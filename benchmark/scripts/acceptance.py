#!/usr/bin/env python3
"""Aceite HTTP externo idêntico aos quatro cenários, com dados sintéticos."""
import argparse
from decimal import Decimal
import io
import json
from pathlib import Path
import sys
import unittest
import unicodedata
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
import uuid
import zipfile
import xml.etree.ElementTree as ET

BASE='http://127.0.0.1:8080/api'

def normalized_pdf_text(text):
    return unicodedata.normalize('NFKC', text)


class Client:
    def __init__(self, token=None): self.token=token
    def request(self,method,path,data=None,params=None):
        url=BASE+path+('?' + urlencode(params) if params else '')
        headers={'Accept':'application/json'}
        if self.token:headers['Authorization']='Bearer '+self.token
        body=json.dumps(data).encode() if data is not None else None
        if body is not None:headers['Content-Type']='application/json'
        try:
            r=urlopen(Request(url,data=body,headers=headers,method=method),timeout=30)
        except HTTPError as e:r=e
        with r:
            content=r.read(); kind=r.headers.get('Content-Type','')
            value=json.loads(content) if content and 'json' in kind else content
            return r.status,r.headers,value

class Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anon=Client();cls.fixture_prefix=uuid.uuid4().hex[:12];cls.password='Bench-only-passphrase-93!'
        cls.email='owner-'+cls.fixture_prefix+'@example.test';cls.other_email='other-'+cls.fixture_prefix+'@example.test'
        for email in (cls.email,cls.other_email):
            status,_,_=cls.anon.request('POST','/auth/register',{'name':'Benchmark','email':email,'password':cls.password})
            if status!=201:raise AssertionError('Cadastro inicial esperado 201; recebido '+str(status))
        cls.owner=cls.login(cls.email);cls.other=cls.login(cls.other_email)

    @classmethod
    def login(cls,email):
        status,_,data=cls.anon.request('POST','/auth/login',{'email':email,'password':cls.password})
        if status!=200 or not isinstance(data,dict) or not isinstance(data.get('token'),str):raise AssertionError('Login não atende contrato')
        return Client(data['token'])

    def fixture(self,tag,**extra):
        d={'type':'INCOME','description':self.fixture_prefix+'-'+tag,'category':'Trabalho','amount':'100.00','date':'2026-10-10'};d.update(extra);return d
    def create(self,tag,client=None,**extra):
        status,_,data=(client or self.owner).request('POST','/transactions',self.fixture(tag,**extra))
        self.assertEqual(status,201);self.assertIsInstance(data,dict);self.assertIn('id',data);return data
    def query(self,tag,**extra):
        d={'description':self.fixture_prefix+'-'+tag};d.update(extra);return d

    def test_01_private_routes_deny_anonymous(self):
        for method,path in [('GET','/auth/me'),('GET','/transactions'),('GET','/transactions/summary'),('GET','/transactions/export.pdf'),('GET','/transactions/export.xlsx')]:
            with self.subTest(path=path):self.assertEqual(self.anon.request(method,path)[0],401)

    def test_02_registration_and_login_validation(self):
        for patch in [{'name':''},{'email':'invalid'},{'password':'short'},{'password':'x'*129}]:
            d={'name':'Valid','email':'v-'+uuid.uuid4().hex+'@example.test','password':self.password};d.update(patch)
            with self.subTest(field=next(iter(patch))):self.assertEqual(self.anon.request('POST','/auth/register',d)[0],400)
        self.assertEqual(self.anon.request('POST','/auth/register',{'name':'Dup','email':self.email.upper(),'password':self.password})[0],409)
        self.assertEqual(self.anon.request('POST','/auth/login',{'email':self.email,'password':'wrong'})[0],401)

    def test_03_logout_revokes_token_and_me_hides_secrets(self):
        c=self.login(self.email);status,_,me=c.request('GET','/auth/me');self.assertEqual(status,200)
        self.assertNotIn('password',json.dumps(me).lower());self.assertNotIn('token',json.dumps(me).lower())
        self.assertEqual(c.request('POST','/auth/logout')[0],204)
        self.assertEqual(c.request('GET','/transactions')[0],401)

    def test_04_crud_and_decimal_contract(self):
        row=self.create('crud',amount='12.34')
        self.assertEqual(row['amount'],'12.34')
        for f in ['createdAt','updatedAt','date','type','category','description']:self.assertIn(f,row)
        path='/transactions/'+str(row['id'])
        self.assertEqual(self.owner.request('GET',path)[0],200)
        updated=self.fixture('crud-edited',type='EXPENSE',amount='7.89')
        status,_,data=self.owner.request('PUT',path,updated);self.assertEqual(status,200);self.assertEqual(data['amount'],'7.89');self.assertEqual(data['type'],'EXPENSE')
        self.assertEqual(self.owner.request('DELETE',path)[0],204)
        self.assertEqual(self.owner.request('GET',path)[0],404)

    def test_05_resource_isolation_read_write_delete(self):
        row=self.create('private');path='/transactions/'+str(row['id'])
        for method,data in [('GET',None),('PUT',self.fixture('stolen')),('DELETE',None)]:
            with self.subTest(method=method):self.assertEqual(self.other.request(method,path,data)[0],404)
        self.assertEqual(self.owner.request('GET',path)[0],200)
        status,_,data=self.other.request('GET','/transactions',params=self.query('private'));self.assertEqual(status,200);self.assertEqual(data['totalElements'],0)
        status,_,data=self.other.request('GET','/transactions/summary',params=self.query('private'));self.assertEqual(status,200);self.assertEqual(Decimal(str(data['balance'])),0)

    def test_06_financial_exactness_and_single_balance(self):
        for value in ['0.10','0.20']:self.create('exact',amount=value)
        self.create('exact',type='EXPENSE',amount='0.05')
        status,_,d=self.owner.request('GET','/transactions/summary',params=self.query('exact'));self.assertEqual(status,200)
        self.assertEqual(d['income'],'0.30');self.assertEqual(d['expense'],'0.05');self.assertEqual(d['balance'],'0.25');self.assertEqual(d['count'],3)

    def test_07_invalid_transaction_inputs(self):
        for patch in [{'amount':'0'},{'amount':'-1'},{'amount':'1.001'},{'amount':'100000000000000.00'},{'date':'2026-02-30'},{'category':''},{'description':' '},{'type':'OTHER'},{'category':'x'*81},{'description':'x'*256}]:
            with self.subTest(field=next(iter(patch)),value=str(next(iter(patch.values())))[:20]):self.assertEqual(self.owner.request('POST','/transactions',self.fixture('invalid',**patch))[0],400)

    def test_08_combined_filters_summary_and_order(self):
        a=self.create('filters',amount='10.00',date='2026-10-01',category='Casa')
        b=self.create('filters',amount='20.00',date='2026-10-02',category='Casa')
        self.create('filters',amount='30.00',date='2026-10-03',category='Casa')
        self.create('filters',type='EXPENSE',amount='15.00',date='2026-10-02',category='Casa')
        self.create('filters',amount='15.00',date='2026-10-02',category='Outro')
        params=self.query('filters',type='INCOME',category='Casa',startDate='2026-10-01',endDate='2026-10-02',minAmount='10.00',maxAmount='20.00',sort='amount,asc')
        status,_,d=self.owner.request('GET','/transactions',params=params);self.assertEqual(status,200);self.assertEqual([str(r['id']) for r in d['content']],[str(a['id']),str(b['id'])]);self.assertEqual(d['totalElements'],2)
        status,_,s=self.owner.request('GET','/transactions/summary',params=params);self.assertEqual(status,200);self.assertEqual(s['income'],'30.00');self.assertEqual(s['balance'],'30.00');self.assertEqual(s['count'],2)

    def test_09_pagination_and_stable_sort(self):
        for amount in ['3.00','1.00','2.00']:self.create('pages',amount=amount)
        status,_,a=self.owner.request('GET','/transactions',params=self.query('pages',page=0,size=2,sort='amount,asc'));self.assertEqual(status,200);self.assertEqual(a['totalElements'],3);self.assertEqual(a['totalPages'],2);self.assertEqual([r['amount'] for r in a['content']],['1.00','2.00'])
        status,_,b=self.owner.request('GET','/transactions',params=self.query('pages',page=1,size=2,sort='amount,asc'));self.assertEqual(status,200);self.assertEqual([r['amount'] for r in b['content']],['3.00'])
        self.assertEqual(self.owner.request('GET','/transactions',params=self.query('pages',page=0,size=2,sort='amount,asc'))[2],a)

    def test_10_filter_validation(self):
        for params in [{'page':-1},{'size':0},{'size':101},{'startDate':'2026-12-01','endDate':'2026-01-01'},{'minAmount':'20','maxAmount':'10'},{'sort':'owner,asc'},{'type':'INVALID'}]:
            with self.subTest(params=params):self.assertEqual(self.owner.request('GET','/transactions',params=params)[0],400)

    def test_11_description_search_is_literal(self):
        self.create('literal-percent-%',amount='4.00');self.create('literal-ordinary',amount='5.00')
        status,_,d=self.owner.request('GET','/transactions',params=self.query('literal-percent-%'));self.assertEqual(status,200);self.assertEqual(d['totalElements'],1)
        status,_,d=self.owner.request('GET','/transactions',params={'description':(self.fixture_prefix+'-LITERAL-ORDINARY').upper()});self.assertEqual(status,200);self.assertEqual(d['totalElements'],1)

    def test_12_pdf_filters_totals_and_user_isolation(self):
        from pypdf import PdfReader
        self.create('pdfincluded',amount='123.45');self.create('pdfexcluded',amount='900.00');self.create('pdfincluded-private',client=self.other,amount='888.00')
        status,h,data=self.owner.request('GET','/transactions/export.pdf',params=self.query('pdfincluded'))
        self.assertEqual(status,200);self.assertIn('application/pdf',h.get('Content-Type',''));self.assertTrue(data.startswith(b'%PDF-'));self.assertIn('attachment',h.get('Content-Disposition','').lower())
        text=normalized_pdf_text('\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages))
        self.assertIn(self.fixture_prefix+'-pdfincluded',text);self.assertNotIn('pdfexcluded',text);self.assertNotIn('private',text)
        self.assertRegex(text,r'123[,.]45')

    def test_13_xlsx_filters_totals_and_formula_injection(self):
        self.create('xlsxincluded',amount='45.67',category='=1+1');self.create('xlsxexcluded',amount='900.00');self.create('xlsxincluded-private',client=self.other,amount='888.00')
        status,h,data=self.owner.request('GET','/transactions/export.xlsx',params=self.query('xlsxincluded'))
        self.assertEqual(status,200);self.assertIn('spreadsheetml.sheet',h.get('Content-Type',''));self.assertIn('attachment',h.get('Content-Disposition','').lower())
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            texts=[];ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for path in z.namelist():
                if path.startswith('xl/worksheets/') or path=='xl/sharedStrings.xml':
                    tree=ET.fromstring(z.read(path));texts.extend(tree.itertext());self.assertFalse(tree.findall('.//s:f',ns),'Dados do usuário viraram fórmula XLSX')
        text=' '.join(texts);self.assertIn(self.fixture_prefix+'-xlsxincluded',text);self.assertNotIn('xlsxexcluded',text);self.assertNotIn('private',text);self.assertIn('45.67',text);self.assertIn('=1+1',text)

    def test_14_exports_ignore_pagination(self):
        from pypdf import PdfReader
        for i in range(3):self.create('exportpages-'+str(i),amount='1.00')
        params=self.query('exportpages',page=0,size=1)
        status,_,data=self.owner.request('GET','/transactions/export.pdf',params=params);self.assertEqual(status,200)
        text=normalized_pdf_text('\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages))
        for i in range(3):self.assertIn('exportpages-'+str(i),text)

    def test_15_exports_apply_combined_filters(self):
        from pypdf import PdfReader
        self.create('exportcombined-included',amount='17.21',category='Filtro',date='2026-09-01')
        self.create('exportcombined-wrongtype',type='EXPENSE',amount='17.21',category='Filtro',date='2026-09-01')
        self.create('exportcombined-wrongcategory',amount='17.21',category='Outra',date='2026-09-01')
        self.create('exportcombined-wrongamount',amount='99.00',category='Filtro',date='2026-09-01')
        self.create('exportcombined-wrongdate',amount='17.21',category='Filtro',date='2026-08-31')
        params=self.query('exportcombined',type='INCOME',category='Filtro',startDate='2026-09-01',endDate='2026-09-01',minAmount='17.21',maxAmount='17.21')
        for extension in ('pdf','xlsx'):
            with self.subTest(format=extension):
                status,_,data=self.owner.request('GET','/transactions/export.'+extension,params=params)
                self.assertEqual(status,200)
                if extension=='pdf':text=normalized_pdf_text(' '.join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages))
                else:
                    with zipfile.ZipFile(io.BytesIO(data)) as z:
                        text=' '.join(' '.join(ET.fromstring(z.read(path)).itertext()) for path in z.namelist() if path.startswith('xl/worksheets/') or path=='xl/sharedStrings.xml')
                self.assertIn('exportcombined-included',text)
                for suffix in ('wrongtype','wrongcategory','wrongamount','wrongdate'):self.assertNotIn('exportcombined-'+suffix,text)

    def test_16_anonymous_cannot_mutate_and_invalid_token_rejected(self):
        row=self.create('anonymous-private');path='/transactions/'+str(row['id'])
        for method,endpoint,body in [('POST','/transactions',self.fixture('anonymous')),('GET',path,None),('PUT',path,self.fixture('overwritten')),('DELETE',path,None)]:
            with self.subTest(method=method):self.assertEqual(self.anon.request(method,endpoint,body)[0],401)
        self.assertEqual(Client('not-a-valid-token').request('GET','/transactions')[0],401)
        self.assertEqual(self.owner.request('GET',path)[0],200)

class JSONResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.cases=[]
    def addSuccess(self,test):super().addSuccess(test);self.cases.append({'case':test.id(),'status':'aprovado'})
    def addFailure(self,test,err):super().addFailure(test,err);self.cases.append({'case':test.id(),'status':'reprovado','reason':type(err[1]).__name__})
    def addError(self,test,err):super().addError(test,err);self.cases.append({'case':test.id(),'status':'erro','reason':type(err[1]).__name__})
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        if err:self.cases.append({'case':test.id(),'subcase':str(subtest),'status':'reprovado','reason':type(err[1]).__name__})

def main():
    global BASE
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--scenario',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();BASE=a.base.rstrip('/')
    result=unittest.TextTestRunner(verbosity=2,resultclass=JSONResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(Acceptance))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({'scenario':a.scenario,'tests_run':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'cases':result.cases,'scope':'HTTP API only; UI, static security and CI are separate gates'},indent=2,ensure_ascii=False)+'\n')
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':sys.exit(main())
