import hashlib
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
class FrozenContractsTests(unittest.TestCase):
    def test_original_spec_and_config_are_preserved(self):
        freeze=json.loads((ROOT/'experiment/freeze.json').read_text())
        for path,digest in freeze['files'].items():
            with self.subTest(path=path):self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
    def test_shared_acceptance_has_not_drifted(self):
        freeze=json.loads((ROOT/'experiment/evaluation/acceptance-freeze.json').read_text())
        self.assertEqual(hashlib.sha256((ROOT/freeze['file']).read_bytes()).hexdigest(),freeze['sha256'])
        self.assertEqual(freeze['shared_for'],['C1','C2','C3','C4'])
