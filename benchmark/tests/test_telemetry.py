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

class NativeIntegrationTests(unittest.TestCase):
    def test_native_roundtrip_is_idempotent(self):
        import json,sqlite3,tempfile,os
        source=Path(os.environ.get('PUCK_SOURCE','/tmp/puck-benchmark-source'))
        if not source.is_dir():
            self.skipTest('Fonte Puck indisponível; executar com PUCK_SOURCE no checkout fixado')
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

class WrapperTests(unittest.TestCase):
    class Native:
        @staticmethod
        def shell_writes(call,command):return [(call,command)]
    def test_json_command_literal_is_decoded_without_eval(self):
        import json
        command='cat > backend/src/Example.java <<\'EOF\'\nclass Example {}\nEOF'
        record={'type':'response_item','payload':{'type':'custom_tool_call','name':'functions.exec','call_id':'synthetic','input':'text(await tools.exec_command({cmd:'+json.dumps(command)+'}));'}}
        writes=t.wrapper_writes(record,self.Native)
        self.assertEqual(len(writes),1);self.assertEqual(writes[0][1],command)
    def test_dynamic_expressions_and_other_tools_are_not_evaluated(self):
        record={'type':'response_item','payload':{'type':'custom_tool_call','name':'functions.exec','input':'tools.exec_command({cmd: dangerousFunction()})'}}
        self.assertEqual(t.wrapper_writes(record,self.Native),[])
        record['payload']['name']='other_tool';record['payload']['input']='cmd: "cat > output"'
        self.assertEqual(t.wrapper_writes(record,self.Native),[])
    def test_native_patch_is_not_double_counted(self):
        record={'type':'response_item','payload':{'type':'custom_tool_call','name':'functions.exec','input':'*** Begin Patch\ncmd: "cat > output"'}}
        self.assertEqual(t.wrapper_writes(record,self.Native),[])

class WrapperRegressionTests(unittest.TestCase):
    def record(self,source):
        return {'type':'response_item','payload':{'type':'custom_tool_call','name':'functions.exec','input':source}}
    def test_comment_is_not_a_call(self):
        for source in ['// cmd: "cat > code.py"','/* tools.exec_command({cmd:"cat > code.py"}) */','const note = "tools.exec_command({cmd: \\"cat > code.py\\"})";']:
            self.assertEqual(t.wrapper_writes(self.record(source),WrapperTests.Native),[])
    def test_dynamic_suffix_is_not_a_literal_command(self):
        self.assertEqual(t.wrapper_writes(self.record('await tools.exec_command({cmd: "cat > code.py" + suffix})'),WrapperTests.Native),[])
    def test_override_or_nested_cmd_is_not_assumed_literal(self):
        for source in ['tools.exec_command({cmd:"cat > code.py",...extra})','tools.exec_command({cmd:"cat > code.py",cmd:dynamic})','tools.exec_command({options:{cmd:"cat > code.py"}})']:
            self.assertEqual(t.wrapper_writes(self.record(source),WrapperTests.Native),[])
