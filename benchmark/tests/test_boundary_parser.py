import importlib.util
from pathlib import Path
from decimal import Decimal,InvalidOperation
import unittest
spec=importlib.util.spec_from_file_location('boundaries',Path(__file__).parents[1]/'scripts/contract_boundaries.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DecimalParserTests(unittest.TestCase):
    def test_numeric_representations_preserve_cents(self):
        for text in ['12345678901234.56','R$ 12.345.678.901.234,56','1.234567890123456E13']:
            self.assertEqual(m.decimal_cell(text),Decimal('12345678901234.56'))
    def test_description_is_not_a_number(self):
        with self.assertRaises(InvalidOperation):m.decimal_cell('educação')
