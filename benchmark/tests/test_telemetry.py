import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('telemetry',Path(__file__).parents[1]/'scripts/telemetry.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)

class TelemetryTests(unittest.TestCase):
    def test_missing_is_not_zero_and_cache_is_not_added(self):
        rows=[dict(scenario='C1',run=1,agent='x',model='m',effort='medium',phase='codigo',category='codigo',input_tokens=100,cache_read_tokens=80,output_tokens=10),dict(scenario='C1',run=1,agent='x',model='m',effort='medium',phase='codigo',category='codigo',input_tokens=50,cache_read_tokens=None,output_tokens=5)]
        g=t.aggregate(rows)[0]
        self.assertEqual(g['input_tokens'],150)
        self.assertEqual(g['cache_read_tokens'],80)
        self.assertEqual(g['cache_read_tokens_observations'],1)
        self.assertIsNone(g['reasoning_tokens'])
    def test_read_only_is_not_assumed_search(self):
        self.assertEqual(t.activity_category('sem_escrita',None),'nao_disponivel')
        self.assertEqual(t.activity_category('sem_escrita','busca'),'busca')
        self.assertEqual(t.activity_category('documentacao','planejamento'),'doc')
    def test_categories_are_exclusive_and_phase_separate(self):
        self.assertEqual(t.activity_category('mista','revisao'),'mista')
        self.assertEqual(t.activity_category('codigo','revisao'),'codigo')

if __name__=='__main__':unittest.main()
