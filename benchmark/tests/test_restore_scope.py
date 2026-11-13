import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('restore_scope',Path(__file__).parents[1]/'scripts/restore_probe.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class RestoreScopeTests(unittest.TestCase):
    def test_only_same_scenario_project_is_selected(self):
        for project in ['puck-c1','benchmark-c1-diagnostic','benchmark-eval-c1-abcdef']:
            self.assertTrue(m.owns_project('C1',project))
        for project in ['puck-c2','production','benchmark-c1','puck-c1-other','benchmark-c1-;command']:
            self.assertFalse(m.owns_project('C1',project))

    def test_database_identifier_is_quoted_as_one_identifier(self):
        self.assertEqual(m.quote_identifier('x"; DROP TABLE users;--'),'"x""; DROP TABLE users;--"')
