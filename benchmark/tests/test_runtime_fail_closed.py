import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('runtime_guard',Path(__file__).parents[1]/'scripts/run_system_evaluation.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
VALID={'services':{'backend':{'ports':[{'host_ip':'127.0.0.1','target':8080,'published':'18081'}]},'frontend':{'ports':[{'host_ip':'127.0.0.1','target':80,'published':'18080'}]}}}

class RuntimeFailClosedTests(unittest.TestCase):
    def exercise(self,config=None,git_fail=False,dirty=False):
        calls=[]
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);scenario=root/'scenarios'/r.SCENARIOS['C1'];scenario.mkdir(parents=True);(scenario/'compose.yaml').write_text('services: {}\n')
            cfg=config(scenario) if callable(config) else (config or copy.deepcopy(VALID))
            def run(command,**kwargs):
                calls.append(command)
                if command[0]=='git':
                    if git_fail:raise subprocess.CalledProcessError(128,command)
                    output=(' M scoped-source.java\n' if dirty else '') if 'status' in command else 'a'*40+'\n'
                    return subprocess.CompletedProcess(command,0,stdout=output)
                if 'config' in command:return subprocess.CompletedProcess(command,0,stdout=json.dumps(cfg))
                return subprocess.CompletedProcess(command,0,stdout='')
            with patch.object(r,'ROOT',root),patch.object(sys,'argv',['runtime','--scenario','C1']),patch.object(r.subprocess,'run',side_effect=run),patch.object(r,'wait_http'),patch.dict(os.environ,{'PATH':os.environ.get('PATH','')},clear=True),contextlib.redirect_stdout(io.StringIO()):
                code=r.main()
            result=json.loads((root/'experiment/results/system-c1.json').read_text())
        return code,result,calls

    def assert_rejected_before_up(self,config):
        code,result,calls=self.exercise(config)
        self.assertNotEqual(code,0);self.assertFalse(result['success']);self.assertFalse(any('up' in x for x in calls));self.assertFalse(any('down' in x for x in calls))

    def test_external_service_bind_is_rejected_before_start(self):
        cfg=copy.deepcopy(VALID);cfg['services']['backend']['volumes']=[{'type':'bind','source':'/synthetic-host-data','target':'/data'}];self.assert_rejected_before_up(cfg)
    def test_public_bind_is_rejected_before_start(self):
        cfg=copy.deepcopy(VALID);cfg['services']['backend']['ports'][0]['host_ip']='0.0.0.0';self.assert_rejected_before_up(cfg)
    def test_privileged_service_is_rejected_before_start(self):
        cfg=copy.deepcopy(VALID);cfg['services']['backend']['privileged']=True;self.assert_rejected_before_up(cfg)
    def test_external_build_context_is_rejected_before_start(self):
        cfg=copy.deepcopy(VALID);cfg['services']['backend']['build']={'context':'/synthetic-external-code'};self.assert_rejected_before_up(cfg)
    def test_external_network_is_rejected_before_start(self):
        cfg=copy.deepcopy(VALID);cfg['networks']={'default':{'external':True,'name':'outside'}};self.assert_rejected_before_up(cfg)
    def test_secret_file_outside_scope_is_rejected(self):
        cfg=copy.deepcopy(VALID);cfg['secrets']={'db':{'file':'/synthetic-host-secret'}};self.assert_rejected_before_up(cfg)
    def test_remote_build_context_is_rejected(self):
        cfg=copy.deepcopy(VALID);cfg['services']['backend']['build']={'context':'https://example.invalid/repo.git'};self.assert_rejected_before_up(cfg)
    def test_engine_api_socket_is_rejected_before_start(self):
        cfg=copy.deepcopy(VALID);cfg['services']['backend']['use_api_socket']=True;self.assert_rejected_before_up(cfg)
    def test_unknown_service_resource_is_fail_closed(self):
        cfg=copy.deepcopy(VALID);cfg['services']['backend']['future_engine_access']=True;self.assert_rejected_before_up(cfg)
    def test_external_env_file_is_not_resolved_before_guard(self):
        cfg=copy.deepcopy(VALID);cfg['services']['backend']['env_file']=[{'path':'/synthetic-outside/host.env','required':True}]
        code,result,calls=self.exercise(cfg)
        self.assertNotEqual(code,0);self.assertFalse(result['success']);self.assertFalse(any('up' in x for x in calls))
        self.assertTrue(any('config' in x and '--no-env-resolution' in x for x in calls))
    def test_commit_error_after_green_acceptance_fails_and_cleans(self):
        code,result,calls=self.exercise(git_fail=True)
        self.assertNotEqual(code,0);self.assertFalse(result['success']);self.assertEqual(result['error_type'],'CalledProcessError');self.assertTrue(any('down' in x for x in calls))
    def test_dirty_source_cannot_claim_tested_commit(self):
        code,result,_=self.exercise(dirty=True);self.assertNotEqual(code,0);self.assertFalse(result['success'])
    def test_owned_bind_and_complete_legitimate_run(self):
        def config(scope):
            cfg=copy.deepcopy(VALID);cfg['services']['frontend']['volumes']=[{'type':'bind','source':str(scope/'nginx.conf'),'target':'/etc/nginx/conf.d/default.conf','read_only':True}];return cfg
        code,result,calls=self.exercise(config)
        self.assertEqual(code,0);self.assertTrue(result['success']);self.assertEqual(result['stage'],'complete');self.assertEqual(result['commit'],'a'*40);self.assertTrue(any('up' in x for x in calls));self.assertTrue(any('down' in x for x in calls))
