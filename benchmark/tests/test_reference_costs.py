import importlib.util
from pathlib import Path
import unittest
import tempfile
import json
import contextlib
import io
from unittest.mock import patch
from decimal import Decimal

spec=importlib.util.spec_from_file_location('reference_costs',Path(__file__).parents[1]/'scripts/reference_costs.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ReferenceCostTests(unittest.TestCase):
    def event(self, **changes):
        result=dict(model='gpt-6.1-sol',input_tokens=100000,cache_read_tokens=80000,cache_write_tokens=0,output_tokens=1000,reasoning_tokens=900)
        result.update(changes)
        return result

    def test_cache_and_reasoning_are_not_billed_twice(self):
        self.assertEqual(m.estimate(self.event()), Decimal('0.058'))

    def test_long_context_multiplier_uses_entire_request(self):
        self.assertEqual(m.estimate(self.event(input_tokens=300000,cache_read_tokens=200000)), Decimal('0.455'))

    def test_threshold_is_strictly_greater(self):
        self.assertEqual(m.estimate(self.event(input_tokens=272000,cache_read_tokens=0)), Decimal('0.554'))

    def test_unknown_or_inconsistent_measurement_stays_unknown(self):
        for patch in [dict(input_tokens=None),dict(cache_read_tokens=100001),dict(model='unknown'),dict(cache_write_tokens=1),dict(output_tokens=-1)]:
            with self.subTest(patch=patch): self.assertIsNone(m.estimate(self.event(**patch)))

    def test_partial_total_cannot_be_presented_as_complete(self):
        result=m.summarize([self.event(),self.event(input_tokens=None)])
        self.assertIsNone(result['reference_standard_api_usd'])
        self.assertEqual(result['known_subtotal_usd'],'0.05800000')
        self.assertEqual(result['unpriced_responses'],1)

    def test_reasoning_cannot_exceed_or_negate_total_output(self):
        self.assertIsNone(m.estimate(self.event(reasoning_tokens=1001)))
        self.assertIsNone(m.estimate(self.event(reasoning_tokens=-1)))
        self.assertEqual(m.estimate(self.event(reasoning_tokens=None)), Decimal('0.058'))

    def test_unknown_model_does_not_stop_mixed_model_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'reports').mkdir()
            (root/'reports/token-events.jsonl').write_text('\n'.join(json.dumps(self.event(scenario='C1',model=model)) for model in [None,'gpt-6.1-sol']))
            with patch.object(m,'ROOT',root),patch.object(m,'PRICE_FILE',root/'prices.json'),contextlib.redirect_stdout(io.StringIO()):
                m.main()
            report=json.loads((root/'reports/cost-estimates.json').read_text())
        self.assertIsNone(report['overall']['reference_standard_api_usd'])
        self.assertEqual({row['value'] for row in report['dimensions']['model']},{'nao_disponivel','gpt-6.1-sol'})
