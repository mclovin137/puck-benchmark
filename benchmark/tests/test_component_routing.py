import importlib.util
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('checks',Path(__file__).parents[1]/'scripts/check_applications.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class RoutingTests(unittest.TestCase):
    def test_each_scenario_is_checked_independently(self):
        paths=['scenarios/c1-specialists-economy/backend/src/App.java','scenarios/c2-specialists-advanced/frontend/package-lock.json']
        self.assertEqual(c.affected_components(paths),{'C1':{'backend'},'C2':{'frontend'}})
    def test_compose_requires_both_boundaries(self):
        self.assertEqual(c.affected_components(['scenarios/c4-manager-advanced/compose.yml']),{'C4':{'backend','frontend'}})
    def test_docs_do_not_claim_application_test_scope(self):
        self.assertEqual(c.affected_components(['docs/rules.md','scenarios/c3-manager-economy/README.md']),{})
