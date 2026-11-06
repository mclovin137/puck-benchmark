#!/usr/bin/env python3
"""Coleta metadados com o coletor Puck fixado; nunca publica conversas."""
import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import sqlite3
import sys
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
PIN = 'c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a'
PHASES = ('codigo', 'doc', 'testes', 'planejamento', 'revisao', 'busca', 'configuracao', 'mista', 'nao_disponivel')
TOKENS = ('input_tokens', 'cache_read_tokens', 'cache_write_tokens', 'output_tokens', 'reasoning_tokens')
JS_IDENT = re.compile(r'[A-Za-z_$][A-Za-z0-9_$]*')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_native(source):
    try:
        commit = subprocess.run(['git','-C',str(source),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
        clean = subprocess.run(['git','-C',str(source),'diff','--quiet','HEAD','--'],capture_output=True)
    except (OSError,subprocess.CalledProcessError) as exc:
        raise ValueError('Fonte Puck não verificável') from exc
    if commit != PIN or clean.returncode != 0:
        raise ValueError('Fonte Puck diverge do commit congelado')
    file = Path(source) / 'agents/scripts/monitor-tokens.py'
    spec = importlib.util.spec_from_file_location('puck_token_collector', file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def append_phase(agent, phase, scenario, task):
    if phase not in PHASES:
        raise ValueError('fase inválida')
    if not re.fullmatch(r'/root(?:/[a-z0-9_]{1,40}){0,5}',agent):
        raise ValueError('agente inválido')
    if scenario not in ('C1','C2','C3','C4','overhead') or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}',task):
        raise ValueError('cenário/tarefa inválidos')
    path = ROOT / 'experiment/results/phases.jsonl'
    event = {'timestamp': now(), 'agent': agent, 'phase': phase, 'scenario': scenario,
             'run': 1, 'task': task, 'correlation': hashlib.sha256((agent + now()).encode()).hexdigest()[:16]}
    with path.open('a') as f:
        f.write(json.dumps(event) + '\n')


def activity_category(activity, phase):
    mapping = {'codigo': 'codigo', 'documentacao': 'doc', 'teste': 'testes', 'configuracao': 'configuracao', 'mista': 'mista'}
    if activity in mapping:
        return mapping[activity]
    # Leitura não é busca por inferência: fase explícita é necessária.
    return phase if phase in ('planejamento', 'revisao', 'busca', 'testes') else 'nao_disponivel'


def aggregate(rows):
    groups = {}
    for r in rows:
        key = tuple(r.get(k) for k in ('scenario', 'run', 'agent', 'model', 'effort', 'phase', 'category'))
        g = groups.setdefault(key, dict(zip(('scenario', 'run', 'agent', 'model', 'effort', 'phase', 'category'), key)))
        g['responses'] = g.get('responses', 0) + 1
        for field in TOKENS:
            value = r.get(field)
            g[field + '_observations'] = g.get(field + '_observations', 0) + (value is not None)
            if value is not None:
                g[field] = (g.get(field) or 0) + value
            else:
                g.setdefault(field, None)
    return list(groups.values())


def js_tokens(source):
    """Lexer conservador: comentários e conteúdo de strings não viram código."""
    tokens = []
    i = 0
    while i < len(source):
        char = source[i]
        if char.isspace():
            i += 1
            continue
        if source.startswith('//',i):
            end = source.find('\n',i+2)
            i = len(source) if end < 0 else end+1
            continue
        if source.startswith('/*',i):
            end = source.find('*/',i+2)
            i = len(source) if end < 0 else end+2
            continue
        if char == '/':
            # Regex é dado. Divisões ambíguas podem reduzir cobertura, nunca
            # justificam interpretar seu conteúdo como chamada executada.
            i += 1
            in_class = False
            while i < len(source) and source[i] != '\n':
                if source[i] == '\\':
                    i += 2
                    continue
                if source[i] == '[':
                    in_class = True
                elif source[i] == ']':
                    in_class = False
                elif source[i] == '/' and not in_class:
                    i += 1
                    break
                i += 1
            tokens.append(('opaque',None))
            continue
        if char in ('"',"'",'`'):
            start = i
            i += 1
            while i < len(source):
                if source[i] == '\\':
                    i += 2
                elif source[i] == char:
                    i += 1
                    break
                else:
                    i += 1
            value = None
            if char == '"':
                try:
                    value = json.loads(source[start:i])
                except ValueError:
                    pass
            tokens.append(('string',value))
            continue
        match = JS_IDENT.match(source,i)
        if match:
            tokens.append(('id',match.group(0)))
            i += len(match.group(0))
        else:
            tokens.append(('punct',char))
            i += 1
    return tokens


def wrapper_writes(record, native):
    """Extrai somente literais JSON de cmd no wrapper JS; nunca avalia código."""
    payload = record.get('payload', {})
    if record.get('type') != 'response_item' or payload.get('type') not in ('custom_tool_call','function_call'):
        return []
    name = payload.get('name','')
    if name not in ('exec','functions.exec'):
        return []
    raw = payload.get('input',payload.get('arguments'))
    if not isinstance(raw,str) or len(raw) > 1_000_000 or '*** Begin Patch' in raw:
        return []
    found = []
    tokens = js_tokens(raw)
    prefix = [('id','tools'),('punct','.'),('id','exec_command'),('punct','('),('punct','{')]
    for i in range(len(tokens)-len(prefix)+1):
        if tokens[i:i+len(prefix)] != prefix or (i and tokens[i-1] == ('punct','.')):
            continue
        depth = 1
        j = i + len(prefix)
        commands = []
        ambiguous = False
        while j < len(tokens) and depth:
            kind,value = tokens[j]
            if depth == 1:
                if tokens[j:j+3] == [('punct','.')]*3 or (kind == 'punct' and value == '['):
                    ambiguous = True
                if value == 'cmd' and kind in ('id','string') and tokens[j-1] in (('punct','{'),('punct',',')):
                    tail = tokens[j+1:j+4]
                    literal = len(tail) == 3 and tail[0] == ('punct',':') and tail[1][0] == 'string' and isinstance(tail[1][1],str) and tail[2] in (('punct',','),('punct','}'))
                    commands.append(tail[1][1] if literal else None)
            if kind == 'punct' and value == '{':
                depth += 1
            elif kind == 'punct' and value == '}':
                depth -= 1
            j += 1
        if not depth and not ambiguous and len(commands) == 1 and commands[0] is not None:
            call = str(payload.get('call_id','wrapper')) + ':wrapper:' + str(i)
            found.extend(native.shell_writes(call,commands[0]))
    return found


def enrich_activities(db, metadata, native):
    """Recalcula apenas dimensões de escrita; tokens e identidades são do Puck."""
    count = 0
    for sid,m in metadata.items():
        own = False
        pending = {}
        with m['path'].open() as stream:
            for line in stream:
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                payload = record.get('payload',{})
                if not isinstance(payload,dict):
                    continue
                if record.get('type') == 'session_meta':
                    own = payload.get('id') == sid
                if not own:
                    continue
                pending.update(native.codex_write_paths(record))
                writes = wrapper_writes(record,native)
                pending.update(writes)
                count += bool(writes)
                if record.get('type') == 'token_usage_record' and payload.get('thread_id') == sid:
                    ident = payload.get('response_id') or payload.get('id') or payload.get('request_id') or str(record.get('id') or '')
                    if ident:
                        native.apply_activity(db,'codex',sid+':'+ident,native.counts_of(pending.values()),False)
                        pending.clear()
    db.commit()
    return count


def discover(logs, parent):
    metadata = {}
    for path in Path(logs).rglob('*.jsonl'):
        try:
            match = re.search(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',path.name)
            if not match:
                continue
            own_id = match.group(0)
            with path.open() as f:
                m = None
                for line in f:
                    # Ignore all non-metadata lines, including inherited conversation.
                    if '"session_meta"' not in line:
                        continue
                    record = json.loads(line)
                    payload = record.get('payload',{})
                    if record.get('type') == 'session_meta' and payload.get('id') == own_id:
                        m = payload
                        break
            if m is None:
                continue
            source = m.get('source', {})
            spawn = source.get('subagent', {}).get('thread_spawn', {}) if isinstance(source, dict) else {}
            agent = spawn.get('agent_path', '/root' if m['id'] == parent else None)
            if agent is not None and not re.fullmatch(r'/root(?:/[a-z0-9_]{1,40}){0,5}',agent):
                agent = None
            metadata[m['id']] = {'path': path, 'parent': spawn.get('parent_thread_id'),
                                  'agent': agent,
                                  'role': m.get('agent_role')}
        except (ValueError, OSError, KeyError):
            continue
    keep = {parent}
    while True:
        children = {sid for sid, m in metadata.items() if m['parent'] in keep}
        if children <= keep:
            break
        keep |= children
    return {sid: m for sid, m in metadata.items() if sid in keep}


def collect(args):
    private = ROOT / '.private'
    selected = private / 'sessions'
    selected.mkdir(parents=True, exist_ok=True)
    metadata = discover(args.logs, args.parent)
    for m in metadata.values():
        link = selected / m['path'].name
        if not link.exists():
            link.symlink_to(m['path'])
    native = load_native(args.puck)
    db = sqlite3.connect(private / 'usage.sqlite3', timeout=30)
    native.init_db(db)
    processed, errors = native.ingest(db, 'codex', selected, None, False)
    db.commit()
    wrapper_records = enrich_activities(db,metadata,native)
    db.row_factory = sqlite3.Row
    phases = []
    ledger = ROOT / 'experiment/results/phases.jsonl'
    if ledger.exists():
        phases = [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
    rows = []
    for raw in db.execute('SELECT * FROM usage ORDER BY timestamp,event_id'):
        r = dict(raw)
        m = metadata.get(r['session_id'])
        if not m:
            continue
        agent = m['agent'] or 'nao_disponivel'
        choices = [e for e in phases if e['agent'] == agent and e['timestamp'] <= (r['timestamp'] or '')]
        phase = max(choices, key=lambda e:e['timestamp']) if choices else {}
        row = {k:r.get(k) for k in ('timestamp','model','effort',*TOKENS)}
        scenario_match = re.match(r'^/root/c([1-4])(?:/|$)',agent)
        scenario = 'C' + scenario_match.group(1) if scenario_match else 'overhead'
        row.update(scenario=phase.get('scenario',scenario), run=phase.get('run',1), task=phase.get('task'),
                   agent=agent, phase=phase.get('phase','nao_disponivel'),
                   category=activity_category(r.get('activity'),phase.get('phase')),
                   correlation=hashlib.sha256(r['event_id'].encode()).hexdigest()[:24],
                   source='puck-native-token-usage-record')
        rows.append(row)
    db.close()
    report = {'generated_at':now(), 'puck_commit':PIN, 'measurement':'observed_metadata',
              'new_records':processed,'parse_errors':errors,'observed_sessions':len(metadata),
              'wrapper_records_with_detected_writes':wrapper_records,
              'notes':['Cache is a subset of input; reasoning is a subset of output.',
                       'Categories are response-level associations, not causal allocation of context.',
                       'Unknown tokens are null. Subscription billing and active time unavailable.',
                       'No financial sum across overlapping skill associations.'],
              'groups':aggregate(rows)}
    (ROOT/'reports/token-breakdown.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    with (ROOT/'reports/token-events.jsonl').open('w') as f:
        for row in rows:
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
    groups=report['groups']
    with (ROOT/'reports/token-breakdown.csv').open('w',newline='') as f:
        fields=['scenario','run','agent','model','effort','phase','category','responses']+[x for t in TOKENS for x in (t,t+'_observations')]
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(groups)
    print(json.dumps({'responses':len(rows),'sessions':len(metadata),'new_records':processed,'errors':errors}))


def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    phase=sub.add_parser('phase');phase.add_argument('--agent',required=True);phase.add_argument('--phase',choices=PHASES,required=True);phase.add_argument('--scenario',required=True);phase.add_argument('--task',required=True)
    c=sub.add_parser('collect');c.add_argument('--puck',required=True);c.add_argument('--logs',default=str(Path.home()/'.codex/sessions'));c.add_argument('--parent',required=True);c.add_argument('--watch',type=int,default=0)
    a=p.parse_args()
    if a.cmd=='phase':
        append_phase(a.agent,a.phase,a.scenario,a.task);return
    os.umask(0o077)
    while True:
        collect(a)
        if not a.watch:break
        time.sleep(a.watch)

if __name__=='__main__':main()
