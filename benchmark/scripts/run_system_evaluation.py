#!/usr/bin/env python3
"""Sobe somente projeto Compose efêmero próprio e executa aceite compartilhado."""
import argparse
import datetime as dt
import ipaddress
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from urllib.request import build_opener,ProxyHandler
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[2]
SCENARIOS={'C1':'c1-specialists-economy','C2':'c2-specialists-advanced','C3':'c3-manager-economy','C4':'c4-manager-advanced'}
SERVICE_FIELDS=frozenset(('image','build','command','entrypoint','working_dir','environment','env_file',
    'ports','expose','healthcheck','depends_on','volumes','networks','restart','init','user','read_only',
    'tmpfs','stop_signal','stop_grace_period','shm_size','mem_limit','mem_reservation','cpus','pids_limit',
    'logging','labels','platform','container_name','hostname','domainname','cap_drop','security_opt',
    'secrets','configs','profiles','pull_policy','attach','stdin_open','tty','deploy',
    'privileged','devices','device_cgroup_rules','cap_add','volumes_from','external_links','provider',
    'post_start','pre_stop','pid','ipc','network_mode','use_api_socket'))


def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()


def local_url(port):
    address=ipaddress.ip_address(port.get('host_ip','0.0.0.0'))
    if not address.is_loopback:raise ValueError('Publicação fora da interface loopback')
    published=int(port['published'])
    if not 1<=published<=65535:raise ValueError('Porta publicada inválida')
    host='['+str(address)+']' if address.version==6 else str(address)
    return 'http://'+host+':'+str(published)


def published_urls(config):
    api=None;web=None
    services=config.get('services',{})
    for name,service in services.items():
        for port in service.get('ports',[]):
            if not isinstance(port,dict) or not port.get('published'):continue
            target=int(port['target'])
            url=local_url(port)
            if target==5432:continue
            if name in ('backend','api','server') or target==8080:api=url+'/api'
            elif name in ('frontend','web','client') or target in (80,5173,3000):web=url
    if not api or not web:raise ValueError('Compose precisa expor backend e frontend em portas identificáveis')
    return api,web


def assert_owned_volumes(config,project):
    for volume in config.get('volumes',{}).values():
        if volume.get('external') or volume.get('driver_opts') or not str(volume.get('name','')).startswith(project+'_'):
            raise ValueError('Avaliação recusa volume externo, compartilhado ou fora do projeto efêmero')


def assert_owned_resources(config,project,directory):
    assert_owned_volumes(config,project)
    scope=directory.resolve()
    def within_scope(value):
        if '://' in str(value):return False
        path=Path(value)
        return (path if path.is_absolute() else scope/path).resolve().is_relative_to(scope)
    for network in config.get('networks',{}).values():
        if network.get('external') or network.get('driver') not in (None,'bridge') or network.get('driver_opts') or not str(network.get('name','')).startswith(project+'_'):
            raise ValueError('Rede fora do projeto efêmero')
    for section in ('configs','secrets'):
        for resource in config.get(section,{}).values():
            if resource.get('external') or resource.get('environment') or (resource.get('file') and not within_scope(resource['file'])):
                raise ValueError('Configuração ou segredo fora do escopo do cenário')
    for service in config.get('services',{}).values():
        if set(service)-SERVICE_FIELDS:raise ValueError('Campo de serviço fora da política explícita do launcher')
        if any(service.get(k) for k in ('privileged','devices','device_cgroup_rules','cap_add','volumes_from','external_links','provider','post_start','pre_stop','use_api_socket')):
            raise ValueError('Serviço amplia acesso ao host')
        env_files=service.get('env_file',[])
        if isinstance(env_files,str):env_files=[env_files]
        for env_file in env_files:
            path=env_file.get('path') if isinstance(env_file,dict) else env_file
            if not path or not within_scope(path):raise ValueError('env_file fora do cenário')
        deployment=service.get('deploy',{})
        if set(deployment)-{'resources'}:raise ValueError('Deploy fora da política de recursos local')
        resources=deployment.get('resources',{})
        if set(resources)-{'limits','reservations'}:raise ValueError('Recurso de deploy não permitido')
        if any(set(budget)-{'cpus','memory','pids'} for budget in resources.values()):raise ValueError('Reserva de dispositivo não permitida')
        if any(service.get(k) not in (None,'private') for k in ('pid','ipc')) or service.get('network_mode'):
            raise ValueError('Namespace compartilhado fora do modo permitido')
        if any(str(opt).lower() not in ('no-new-privileges','no-new-privileges:true') for opt in service.get('security_opt',[])):
            raise ValueError('Controles do container reduzidos')
        for mount in service.get('volumes',[]):
            kind=mount.get('type')
            if kind=='bind' and (not mount.get('source') or not within_scope(mount['source'])):
                raise ValueError('Bind mount fora do diretório do cenário')
            if kind=='volume' and mount.get('source') and mount['source'] not in config.get('volumes',{}):
                raise ValueError('Volume de serviço não declarado no projeto')
            if kind not in ('bind','volume','tmpfs'):
                raise ValueError('Tipo de montagem não permitido')
        build=service.get('build')
        if build:
            if isinstance(build,str):build={'context':build}
            context=build.get('context',str(scope))
            if not within_scope(context):raise ValueError('Contexto de build fora do cenário')
            dockerfile=build.get('dockerfile')
            if dockerfile:
                context_path=Path(context) if Path(context).is_absolute() else scope/context
                if not within_scope(context_path/dockerfile):raise ValueError('Dockerfile fora do cenário')
            if build.get('additional_contexts') or build.get('ssh'):raise ValueError('Contextos adicionais ou SSH exigem escopo explícito')
        for port in service.get('ports',[]):
            if isinstance(port,dict) and port.get('published'):local_url(port)


def wait_http(url,expected,timeout=120):
    end=time.monotonic()+timeout
    opener=build_opener(ProxyHandler({}))
    while time.monotonic()<end:
        try:
            with opener.open(url,timeout=5) as response:status=response.status
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
    private=ROOT/'.private';private.mkdir(mode=0o700,exist_ok=True);private.chmod(0o700)
    allowed=('PATH','HOME','DOCKER_HOST','DOCKER_CONTEXT','DOCKER_CONFIG','XDG_RUNTIME_DIR','TMPDIR','LANG','LC_ALL','GITHUB_ACTIONS')
    env={key:os.environ[key] for key in allowed if key in os.environ};password=secrets.token_urlsafe(36)
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
            raw=subprocess.run(command+['config','--no-env-resolution','--format','json'],cwd=directory,env=env,check=True,capture_output=True,text=True)
            config=json.loads(raw.stdout)
            assert_owned_resources(config,project,directory)
            api,web=published_urls(config);result.update(api=api,web=web)
            resources_owned=True
            result['stage']='startup'
            subprocess.run(command+['up','--build','-d','--wait','--wait-timeout','180'],cwd=directory,env=env,check=True,stdout=log,stderr=log)
            result['stage']='readiness';wait_http(api+'/transactions',{401});wait_http(web,{200})
            result['stage']='acceptance'
            proc=subprocess.run([sys.executable,str(ROOT/'benchmark/scripts/acceptance.py'),'--base',api,'--scenario',a.scenario,'--output',str(ROOT/'experiment/results'/(a.scenario.lower()+'-acceptance.json'))],cwd=ROOT,env=env,stdout=log,stderr=log)
            boundaries=subprocess.run([sys.executable,str(ROOT/'benchmark/scripts/contract_boundaries.py'),'--base',api,'--scenario',a.scenario,'--output',str(ROOT/'experiment/results'/(a.scenario.lower()+'-boundaries.json'))],cwd=ROOT,env=env,stdout=log,stderr=log)
            code=proc.returncode or boundaries.returncode
            result['commit']=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
            dirty=subprocess.run(['git','status','--porcelain','--untracked-files=all','--',str(directory.relative_to(ROOT))],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
            result['source_clean']=not bool(dirty)
            if dirty:raise ValueError('Fonte do cenário não corresponde a um commit limpo')
            if code==0:result['success']=True;result['stage']='complete'
        except (subprocess.CalledProcessError,ValueError,TimeoutError,OSError) as error:
            code=1;result['success']=False
            result['error_type']=type(error).__name__
        finally:
            cleanup=subprocess.run(command+['down','--volumes','--remove-orphans'],cwd=directory,env=env,stdout=log,stderr=log) if resources_owned else None
            result['cleanup_success']=cleanup.returncode==0 if cleanup else None;result['finished_at']=stamp()
            if cleanup and cleanup.returncode:code=1;result['success']=False
            output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'scenario':a.scenario,'success':result['success'],'stage':result['stage'],'result':str(output.relative_to(ROOT))}))
    return code

if __name__=='__main__':sys.exit(main())
