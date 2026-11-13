"""Regressão: preparar fixtures não pode substituir TestCase.run."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('acceptance_execution',Path(__file__).parents[1]/'scripts/acceptance.py')
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class ExecutionTests(unittest.TestCase):
    def test_setup_preserves_unittest_execution_method(self):
        class SyntheticClient:
            def __init__(self, token=None): pass
            def request(self, method, path, data=None):
                return (201, {}, {}) if path.endswith('register') else (200, {}, {'token':'fixture-token'})
        with patch.object(a,'Client',SyntheticClient):
            a.Acceptance.setUpClass()
        self.assertTrue(callable(a.Acceptance('test_01_private_routes_deny_anonymous').run))

    def test_pdf_ligatures_have_equivalent_text(self):
        self.assertEqual(a.normalized_pdf_text("pdﬁncluded Café"), "pdfincluded Café")
        self.assertNotEqual(a.normalized_pdf_text("pdfexcluded"), "pdfincluded")
