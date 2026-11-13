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

class RegressionTests(unittest.TestCase):
    def test_null_then_number(self):
        for field in t.TOKENS:
            rows=[{field:None},{field:10},{field:None}]
            result=t.aggregate(rows)[0]
            self.assertEqual(result[field],10)
            self.assertEqual(result[field+'_observations'],1)

    def test_fork_own_metadata_keeps_parent_child_grandchild(self):
        import tempfile,json
        parent='11111111-1111-1111-1111-111111111111'
        child='22222222-2222-2222-2222-222222222222'
        grand='33333333-3333-3333-3333-333333333333'
        def meta(sid,up=None,agent='/root'):
            return {'type':'session_meta','payload':{'id':sid,'source':{'subagent':{'thread_spawn':{'parent_thread_id':up,'agent_path':agent}}}}}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/f'rollout-{parent}.jsonl').write_text(json.dumps(meta(parent))+'\n')
            (p/f'rollout-{child}.jsonl').write_text('\n'.join(map(json.dumps,[meta(parent),{'type':'response_item','payload':{'content':'untrusted data'}},meta(child,parent,'/root/c1')]))+'\n')
            (p/f'rollout-{grand}.jsonl').write_text('\n'.join(map(json.dumps,[meta(parent),meta(child,parent,'/root/c1'),meta(grand,child,'/root/c1/yoda')]))+'\n')
            found=t.discover(p,parent)
            self.assertEqual(set(found),{parent,child,grand})
            self.assertEqual(found[parent]['path'].name,f'rollout-{parent}.jsonl')
            self.assertEqual(found[grand]['agent'],'/root/c1/yoda')

    def test_source_without_pin_fails_closed(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises((ValueError,RuntimeError)):
                t.load_native(d)

    def test_continuation_keeps_both_trees_without_unrelated_sessions(self):
        import tempfile,json
        ids=[f'{n:08d}-1111-1111-1111-111111111111' for n in range(1,6)]
        with tempfile.TemporaryDirectory() as d:
            for sid,up,agent,start in [
                (ids[0],None,None,'2026-11-06T00:00:00Z'),
                (ids[1],ids[0],'/root/c1','2026-11-06T01:00:00Z'),
                (ids[2],None,None,'2026-11-11T00:00:00Z'),
                (ids[3],ids[2],'/root/c4_qa_recovery','2026-11-11T01:00:00Z'),
                (ids[4],None,None,'2026-11-11T00:00:00Z')]:
                source={'subagent':{'thread_spawn':{'parent_thread_id':up,'agent_path':agent}}} if up else 'vscode'
                Path(d,f'rollout-{sid}.jsonl').write_text(json.dumps({'type':'session_meta','payload':{'id':sid,'source':source,'timestamp':start}})+'\n')
            found=t.discover(d,ids[0],continuations=[ids[2],ids[0]])
            self.assertEqual(set(found),set(ids[:4]))
            self.assertEqual(found[ids[2]]['agent'],'/root')
            self.assertEqual(found[ids[3]]['root_started_at'],'2026-11-11T00:00:00Z')
            self.assertEqual(found[ids[1]]['root_started_at'],'2026-11-06T00:00:00Z')

    def test_continuation_cannot_inherit_phase_from_old_session(self):
        ledger=[{'agent':'/root','timestamp':'2026-11-06T10:00:00Z','phase':'codigo'},
                {'agent':'/root','timestamp':'2026-11-11T10:00:00Z','phase':'planejamento'}]
        self.assertEqual(t.phase_at(ledger,'/root','2026-11-11T09:00:00Z','2026-11-11T00:00:00Z'),{})
        self.assertEqual(t.phase_at(ledger,'/root','2026-11-11T11:00:00Z','2026-11-11T00:00:00Z')['phase'],'planejamento')
        self.assertEqual(t.phase_at(ledger,'/root','2026-11-06T11:00:00Z','2026-11-06T00:00:00Z')['phase'],'codigo')

    def test_continuation_requires_a_valid_timezone_aware_start(self):
        import tempfile,json
        sid='55555555-1111-1111-1111-111111111111'
        with tempfile.TemporaryDirectory() as d:
            for start in (None,'','invalid','2026-11-11T00:00:00',17):
                with self.subTest(start=start):
                    Path(d,f'rollout-{sid}.jsonl').write_text(json.dumps({'type':'session_meta','payload':{'id':sid,'timestamp':start}})+'\n')
                    with self.assertRaises(ValueError):
                        t.discover(d,sid,continuations=[sid])
            with self.assertRaises(ValueError):
                t.discover(d,sid,continuations=['66666666-1111-1111-1111-111111111111'])

    def test_phase_times_compare_instants_across_timezone_offsets(self):
        ledger=[{'agent':'/root','timestamp':'2026-11-11T10:00:00-03:00','phase':'codigo'},
                {'agent':'/root','timestamp':'2026-11-11T12:00:00+00:00','phase':'busca'}]
        self.assertEqual(t.phase_at(ledger,'/root','2026-11-11T14:00:00Z','2026-11-11T12:30:00Z')['phase'],'codigo')
