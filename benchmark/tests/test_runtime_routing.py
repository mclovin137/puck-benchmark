import importlib.util
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('runtime',Path(__file__).parents[1]/'scripts/run_system_evaluation.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
class RuntimeRoutingTests(unittest.TestCase):
    def test_database_is_never_an_http_target(self):
        config={'services':{'db':{'ports':[{'target':5432,'published':'15432'}]},'backend':{'ports':[{'target':8080,'published':'18081'}]},'frontend':{'ports':[{'target':80,'published':'18080'}]}}}
        self.assertEqual(r.published_urls(config),('http://127.0.0.1:18081/api','http://127.0.0.1:18080'))
    def test_missing_boundary_cannot_look_like_passed_startup(self):
        with self.assertRaises(ValueError):r.published_urls({'services':{'db':{'ports':[{'target':5432,'published':'15432'}]}}})
    def test_cleanup_cannot_target_shared_or_external_volumes(self):
        for volume in [{'name':'other-project-data'},{'name':'benchmark-eval-c1-safe_data','external':True},{'name':'benchmark-eval-c1-safe_data','driver_opts':{'device':'/sensitive'}}]:
            with self.assertRaises(ValueError):r.assert_owned_volumes({'volumes':{'data':volume}},'benchmark-eval-c1-safe')
        r.assert_owned_volumes({'volumes':{'data':{'name':'benchmark-eval-c1-safe_data'}}},'benchmark-eval-c1-safe')
