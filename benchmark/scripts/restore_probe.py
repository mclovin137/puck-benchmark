#!/usr/bin/env python3
"""Confere backup/restore em banco novo, sem substituir o banco de origem."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import secrets
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def quote_identifier(value):
    return '"'+value.replace('"','""')+'"'


def owns_project(scenario,project):
    key=scenario.lower()
    return project=='puck-'+key or bool(re.fullmatch(r'benchmark-(?:eval-)?'+key+r'-[a-z0-9-]+',project))


def main():
    p=argparse.ArgumentParser();p.add_argument('--scenario',choices=['C1','C2','C3','C4'],required=True);p.add_argument('--project',required=True);p.add_argument('--database',default='finance');p.add_argument('--user',default='finance');a=p.parse_args()
    if not owns_project(a.scenario,a.project):p.error('Projeto fora do namespace de benchmark do cenário')
    if not all(re.fullmatch('[a-zA-Z_][a-zA-Z0-9_]*',x) for x in (a.database,a.user)):p.error('Identificador de banco/usuário inválido')
    service='database' if a.scenario=='C1' else 'db'
    clone='benchmark_restore_'+secrets.token_hex(12)
    private=ROOT/'.private/restores'/clone;private.mkdir(parents=True,mode=0o700)
    result={'scenario':a.scenario,'project':a.project,'started_at':dt.datetime.now(dt.timezone.utc).isoformat(),'success':False,'scope':'snapshot de dados públicos do banco sintético, pg_dump/pg_restore em banco novo; não mede recuperação de desastre ou tempo de produção'}
    created=False;container=None
    with (private/'commands.log').open('wb') as log:
        def run(args,**kwargs):
            return subprocess.run(args,check=True,stderr=log,timeout=120,**kwargs)
        def execute(args,**kwargs):return run(['docker','exec',container,*args],**kwargs)
        def sql(db,query):return execute(['psql','-X','-v','ON_ERROR_STOP=1','-A','-t','-U',a.user,'-d',db,'-c',query],capture_output=False,stdout=subprocess.PIPE).stdout
        def snapshot(db):
            tables=sql(db,"SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename").decode().splitlines()
            stats={}
            for table in tables:
                rows=sql(db,'SELECT row_to_json(t)::text FROM public.'+quote_identifier(table)+' t ORDER BY row_to_json(t)::text')
                stats[table]={'rows':len(rows.splitlines()),'rows_sha256':hashlib.sha256(rows).hexdigest()}
            return stats
        try:
            result['stage']='identity'
            containers=run(['docker','ps','-q','--no-trunc','--filter','label=com.docker.compose.project='+a.project,'--filter','label=com.docker.compose.service='+service],stdout=subprocess.PIPE).stdout.decode().splitlines()
            if len(containers)!=1 or not re.fullmatch('[a-f0-9]{64}',containers[0]):raise ValueError('Identidade de container ambígua')
            container=containers[0]
            result['stage']='snapshot';before=snapshot(a.database)
            result['stage']='backup'
            with (private/'backup.dump').open('wb') as backup:execute(['pg_dump','-U',a.user,'-d',a.database,'--format=custom','--no-owner'],stdout=backup)
            execute(['createdb','-U',a.user,clone],stdout=log);created=True
            result['stage']='restore'
            with (private/'backup.dump').open('rb') as backup:run(['docker','exec','-i',container,'pg_restore','--exit-on-error','--no-owner','-U',a.user,'-d',clone],stdin=backup,stdout=log)
            restored=snapshot(clone);after=snapshot(a.database)
            result.update(tables=restored,source_unchanged=before==after,restored_matches=before==restored,backup_sha256=hashlib.sha256((private/'backup.dump').read_bytes()).hexdigest())
            result['success']=bool(before) and before==after==restored;result['stage']='complete' if result['success'] else 'mismatch'
        except (subprocess.SubprocessError,OSError,ValueError) as e:result['error_type']=type(e).__name__
        finally:
            result['cleanup_success']=None
            if created:
                try:
                    cleanup=subprocess.run(['docker','exec',container,'dropdb','-U',a.user,clone],stdout=log,stderr=log,timeout=120)
                    result['cleanup_success']=cleanup.returncode==0
                except (subprocess.SubprocessError,OSError) as e:
                    result['cleanup_success']=False;result['cleanup_error_type']=type(e).__name__
                if not result['cleanup_success']:result['success']=False
            result['finished_at']=dt.datetime.now(dt.timezone.utc).isoformat()
            output=ROOT/'experiment/results'/('restore-'+a.scenario.lower()+'.json');output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'scenario':a.scenario,'success':result['success'],'stage':result['stage']}))
    return 0 if result['success'] else 1


if __name__=='__main__':raise SystemExit(main())
