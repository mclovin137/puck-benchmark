import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('telemetry',Path(__file__).parents[1]/'scripts/telemetry.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)

class NativeIntegrationTests(unittest.TestCase):
    def test_native_roundtrip_is_idempotent(self):
        import json,sqlite3,tempfile,os
        source=Path(os.environ.get('PUCK_SOURCE','/tmp/puck-benchmark-source'))
        if not source.is_dir():
            self.fail('Fonte Puck obrigatória: executar com PUCK_SOURCE no checkout fixado')
        native=t.load_native(source)
        sid='44444444-4444-4444-4444-444444444444';stamp='2026-11-06T00:00:00Z'
        records=[{'type':'session_meta','payload':{'id':sid}},
            {'type':'turn_context','payload':{'turn_id':'synthetic-turn','model':'gpt-6-luna','effort':'medium'}},
            {'type':'token_usage_record','timestamp':stamp,'payload':{'thread_id':sid,'turn_id':'synthetic-turn','response_id':'synthetic-response','usage':{'input_tokens':100,'cached_input_tokens':80,'output_tokens':10,'reasoning_output_tokens':3}}}]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/f'rollout-{sid}.jsonl';path.write_text(''.join(json.dumps(r)+'\n' for r in records))
            db=sqlite3.connect(':memory:');native.init_db(db)
            count,errors=native.ingest(db,'codex',Path(d),None,False)
            self.assertEqual(errors,0);self.assertEqual(count,1)
            native.ingest(db,'codex',Path(d),None,False)
            self.assertEqual(db.execute('select count(*) from usage').fetchone()[0],1)
            row=db.execute('select input_tokens,cache_read_tokens,output_tokens,reasoning_tokens,model,effort from usage').fetchone()
            self.assertEqual(row,(100,80,10,3,'gpt-6-luna','medium'));db.close()
