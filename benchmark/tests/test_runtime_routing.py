import importlib.util
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('runtime',Path(__file__).parents[1]/'scripts/run_system_evaluation.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
class RuntimeRoutingTests(unittest.TestCase):
    def test_database_is_never_an_http_target(self):
        config={'services':{'db':{'ports':[{'host_ip':'127.0.0.1','target':5432,'published':'15432'}]},'backend':{'ports':[{'host_ip':'127.0.0.1','target':8080,'published':'18081'}]},'frontend':{'ports':[{'host_ip':'127.0.0.1','target':80,'published':'18080'}]}}}
        self.assertEqual(r.published_urls(config),('http://127.0.0.1:18081/api','http://127.0.0.1:18080'))
    def test_missing_boundary_cannot_look_like_passed_startup(self):
        with self.assertRaises(ValueError):r.published_urls({'services':{'db':{'ports':[{'host_ip':'127.0.0.1','target':5432,'published':'15432'}]}}})
    def test_cleanup_cannot_target_shared_or_external_volumes(self):
        for volume in [{'name':'other-project-data'},{'name':'benchmark-eval-c1-safe_data','external':True},{'name':'benchmark-eval-c1-safe_data','driver_opts':{'device':'/sensitive'}}]:
            with self.assertRaises(ValueError):r.assert_owned_volumes({'volumes':{'data':volume}},'benchmark-eval-c1-safe')
        r.assert_owned_volumes({'volumes':{'data':{'name':'benchmark-eval-c1-safe_data'}}},'benchmark-eval-c1-safe')

    def test_ipv6_loopback_url_matches_interface(self):
        self.assertEqual(r.local_url({'host_ip':'::1','published':'18081'}),'http://[::1]:18081')

    def test_explicit_subnet_is_small_private_ipv4_only(self):
        self.assertEqual(r.private_subnet('10.254.244.0/24'),'10.254.244.0/24')
        for value in ('0.0.0.0/0','8.8.8.0/24','127.0.0.0/24','10.0.0.0/8','10.1.1.1/24','::1/128','192.0.2.0/24'):
            with self.subTest(value=value),self.assertRaises(ValueError):r.private_subnet(value)

    def test_override_cannot_reuse_or_add_another_network(self):
        good={'networks':{'default':{'ipam':{'config':[{'subnet':'10.254.244.0/24'}]}}}}
        r.assert_subnet(good,'10.254.244.0/24')
        for bad in ({'networks':{}},{'networks':dict(good['networks'],extra={})},good):
            expected='10.254.245.0/24' if bad is good else '10.254.244.0/24'
            with self.assertRaises(ValueError):r.assert_subnet(bad,expected)
