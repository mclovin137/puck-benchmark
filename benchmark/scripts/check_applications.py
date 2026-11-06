#!/usr/bin/env python3
"""Verifica componentes afetados; promoção exige os quatro cenários completos."""
import argparse
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
SCENARIOS={'C1':'c1-specialists-economy','C2':'c2-specialists-advanced','C3':'c3-manager-economy','C4':'c4-manager-advanced'}


def affected_components(paths):
    selected={}
    for path in paths:
        for scenario,directory in SCENARIOS.items():
            prefix='scenarios/'+directory+'/'
            if not path.startswith(prefix):continue
            rel=path[len(prefix):]
            if rel.startswith('backend/'):
                selected.setdefault(scenario,set()).add('backend')
            elif rel.startswith('frontend/'):
                selected.setdefault(scenario,set()).add('frontend')
            elif rel in ('compose.yml','compose.yaml','docker-compose.yml','docker-compose.yaml'):
                selected.setdefault(scenario,set()).update(('backend','frontend'))
    return selected


def run_component(scenario,component):
    cwd=ROOT/'scenarios'/SCENARIOS[scenario]/component
    env=os.environ.copy();env['CI']='true'
    if component=='backend':
        if not (cwd/'pom.xml').is_file():raise RuntimeError(f'{scenario}: backend sem pom.xml')
        commands=[['mvn','-B','--no-transfer-progress','verify']]
    else:
        if not (cwd/'package-lock.json').is_file():raise RuntimeError(f'{scenario}: frontend sem lockfile')
        import json
        scripts=json.loads((cwd/'package.json').read_text()).get('scripts',{})
        if not scripts.get('test') or not scripts.get('build'):raise RuntimeError(f'{scenario}: scripts test/build obrigatórios')
        commands=[['npm','ci','--no-audit','--no-fund'],['npm','test'],['npm','run','build']]
    for command in commands:
        print(scenario,component,command[0],command[-1],flush=True)
        subprocess.run(command,cwd=cwd,env=env,check=True)


def main():
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--all',action='store_true');mode.add_argument('--scenario',choices=SCENARIOS);mode.add_argument('--changed',action='store_true');p.add_argument('--base');p.add_argument('--head');a=p.parse_args()
    if a.changed:
        if not all(isinstance(x,str) and re.fullmatch('[0-9a-f]{40}',x) for x in (a.base,a.head)):p.error('--changed requer base/head SHA completos')
        result=subprocess.run(['git','diff','--name-only',a.base+'...'+a.head],cwd=ROOT,check=True,capture_output=True,text=True)
        selected=affected_components(result.stdout.splitlines())
    else:
        selected={s:{'backend','frontend'} for s in ([a.scenario] if a.scenario else SCENARIOS)}
    for scenario,components in selected.items():
        for component in sorted(components):run_component(scenario,component)
    if not selected:print('Nenhum componente de aplicação alterado; suíte de infraestrutura é o alcance deste PR.')

if __name__=='__main__':main()
