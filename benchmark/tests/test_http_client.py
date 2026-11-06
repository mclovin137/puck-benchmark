import importlib.util
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import threading
import unittest
s=importlib.util.spec_from_file_location('acceptance',Path(__file__).parents[1]/'scripts/acceptance.py')
a=importlib.util.module_from_spec(s);s.loader.exec_module(a)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path=='/error':
            self.send_response(401);self.send_header('content-type','application/json');self.end_headers();self.wfile.write(b'{"error":"denied"}')
        elif self.path=='/binary':
            self.send_response(200);self.send_header('content-type','application/pdf');self.end_headers();self.wfile.write(b'%PDF-synthetic')
        else:
            self.send_response(200);self.send_header('content-type','application/json');self.end_headers();self.wfile.write(json.dumps({'authorization':self.headers.get('Authorization')}).encode())

class HTTPClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.original=a.BASE;a.BASE='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):
        a.BASE=cls.original;cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def test_http_error_is_a_result_not_success(self):
        status,headers,data=a.Client().request('GET','/error');self.assertEqual(status,401);self.assertEqual(data,{'error':'denied'});self.assertEqual(headers.get('Content-Type'),'application/json')
    def test_binary_is_not_json_decoded(self):
        self.assertEqual(a.Client().request('GET','/binary')[2],b'%PDF-synthetic')
    def test_token_is_sent_only_by_authenticated_client(self):
        self.assertIsNone(a.Client().request('GET','/auth')[2]['authorization']);self.assertEqual(a.Client('synthetic-canary').request('GET','/auth')[2]['authorization'],'Bearer synthetic-canary')
