#!/usr/bin/env python3
"""Sobe somente projeto Compose efêmero próprio e executa aceite compartilhado."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from urllib.request import urlopen
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[2]
SCENARIOS={'C1':'c1-specialists-economy','C2':'c2-specialists-advanced','C3':'c3-manager-economy','C4':'c4-manager-advanced'}


def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()


def published_urls(config):
    api=None;web=None
    services=config.get('services',{})
    for name,service in services.items():
        for port in service.get('ports',[]):
            if not isinstance(port,dict) or not port.get('published'):continue
            target=int(port['target']);published=int(port['published'])
            if target==5432:continue
            url='http://127.0.0.1:'+str(published)
            if name in ('backend','api','server') or target==8080:api=url+'/api'
            elif name in ('frontend','web','client') or target in (80,5173,3000):web=url
    if not api or not web:raise ValueError('Compose precisa expor backend e frontend em portas identificáveis')
    return api,web


def assert_owned_volumes(config,project):
    for volume in config.get('volumes',{}).values():
        if volume.get('external') or volume.get('driver_opts') or not str(volume.get('name','')).startswith(project+'_'):
            raise ValueError('Avaliação recusa volume externo, compartilhado ou fora do projeto efêmero')


def wait_http(url,expected,timeout=120):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        try:
            with urlopen(url,timeout=5) as response:status=response.status
        except HTTPError as error:status=error.code
        except (URLError,TimeoutError,OSError):status=None
        if status in expected:return
        time.sleep(1)
    raise TimeoutError('HTTP readiness indisponível')


def main():
    p=argparse.ArgumentParser();p.add_argument('--scenario',choices=SCENARIOS,required=True);a=p.parse_args()
    directory=ROOT/'scenarios'/SCENARIOS[a.scenario]
    files=[directory/n for n in ('compose.yml','compose.yaml','docker-compose.yml','docker-compose.yaml') if (directory/n).is_file()]
    if len(files)!=1:raise SystemExit('Exigir exatamente um Compose por cenário')
    project='benchmark-eval-'+a.scenario.lower()+'-'+secrets.token_hex(4)
    command=['docker','compose','-p',project,'-f',str(files[0])]
    private=ROOT/'.private';private.mkdir(mode=0o700,exist_ok=True)
    env=os.environ.copy();password=secrets.token_urlsafe(36)
    for key in ('POSTGRES_PASSWORD','DB_PASSWORD','DATABASE_PASSWORD','SPRING_DATASOURCE_PASSWORD'):env[key]=password
    for key in ('JWT_SECRET','APP_SECRET','TOKEN_SECRET'):env[key]=secrets.token_urlsafe(48)
    if env.get('GITHUB_ACTIONS')=='true':
        for secret in {env[k] for k in ('POSTGRES_PASSWORD','JWT_SECRET','APP_SECRET','TOKEN_SECRET')}:print('::add-mask::'+secret,flush=True)
    output=ROOT/'experiment/results'/('system-'+a.scenario.lower()+'.json');output.parent.mkdir(parents=True,exist_ok=True)
    result={'scenario':a.scenario,'started_at':stamp(),'project':project,'scope':'fresh Compose startup and shared HTTP acceptance; UI and other gates separate','stage':'configuration','success':False}
    code=1
    resources_owned=False
    with (private/('runtime-'+a.scenario.lower()+'.log')).open('w') as log:
        try:
            raw=subprocess.run(command+['config','--format','json'],cwd=directory,env=env,check=True,capture_output=True,text=True)
            config=json.loads(raw.stdout)
            assert_owned_volumes(config,project)
            api,web=published_urls(config);result.update(api=api,web=web)
            resources_owned=True
            result['stage']='startup'
            subprocess.run(command+['up','--build','-d','--wait','--wait-timeout','180'],cwd=directory,env=env,check=True,stdout=log,stderr=log)
            result['stage']='readiness';wait_http(api+'/transactions',{401});wait_http(web,{200})
            result['stage']='acceptance'
            proc=subprocess.run([sys.executable,str(ROOT/'benchmark/scripts/acceptance.py'),'--base',api,'--scenario',a.scenario,'--output',str(ROOT/'experiment/results'/(a.scenario.lower()+'-acceptance.json'))],cwd=ROOT,env=env,stdout=log,stderr=log)
            code=proc.returncode;result['success']=code==0
            result['commit']=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
            if code==0:result['stage']='complete'
        except (subprocess.CalledProcessError,ValueError,TimeoutError,OSError) as error:
            result['error_type']=type(error).__name__
        finally:
            cleanup=subprocess.run(command+['down','--volumes','--remove-orphans'],cwd=directory,env=env,stdout=log,stderr=log) if resources_owned else None
            result['cleanup_success']=cleanup.returncode==0 if cleanup else None;result['finished_at']=stamp()
            if cleanup and cleanup.returncode:code=1;result['success']=False
            output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'scenario':a.scenario,'success':result['success'],'stage':result['stage'],'result':str(output.relative_to(ROOT))}))
    return code

if __name__=='__main__':sys.exit(main())
