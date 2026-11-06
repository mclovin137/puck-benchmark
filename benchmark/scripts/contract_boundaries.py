#!/usr/bin/env python3
"""Complementa critérios existentes sem alterar os 16 casos congelados."""
import argparse
from decimal import Decimal,InvalidOperation
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import unittest
import uuid
import zipfile
import xml.etree.ElementTree as ET
spec=importlib.util.spec_from_file_location('shared_acceptance',Path(__file__).with_name('acceptance.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


def compact(text):return re.sub(r'\s+','',text)


def decimal_cell(text):
    value=re.sub(r'\s+','',text).replace('R$','').replace('$','')
    if ',' in value and '.' in value:
        value=value.replace('.','').replace(',','.') if value.rfind(',')>value.rfind('.') else value.replace(',','')
    elif ',' in value:value=value.replace(',','.')
    return Decimal(value)


def xlsx_rows(data):
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    result=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            shared=[''.join(item.itertext()) for item in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
        for path in z.namelist():
            if not path.startswith('xl/worksheets/') or not path.endswith('.xml'):continue
            for row in ET.fromstring(z.read(path)).findall('.//s:row',ns):
                values=[]
                for cell in row.findall('s:c',ns):
                    value=cell.find('s:v',ns)
                    text=value.text if value is not None else ''.join(cell.itertext())
                    values.append(shared[int(text)] if cell.get('t')=='s' else text or '')
                result.append(values)
    return result


class ContractBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anon=a.Client();cls.prefix='boundary-'+uuid.uuid4().hex[:12];cls.password='Boundary-fixture-41!'
        cls.email=cls.prefix+'@example.test'
        status,_,_=cls.anon.request('POST','/auth/register',{'name':'Boundary','email':cls.email,'password':cls.password})
        if status!=201:raise AssertionError('Setup de conta: status '+str(status))
        status,_,login=cls.anon.request('POST','/auth/login',{'email':cls.email,'password':cls.password})
        if status!=200:raise AssertionError('Setup de login: status '+str(status))
        cls.client=a.Client(login['token'])
    def transaction(self,label,amount='10.00'):
        return {'type':'INCOME','description':self.prefix+' '+label,'category':'Educação','amount':amount,'date':'2026-10-10'}
    def create(self,data):
        status,_,body=self.client.request('POST','/transactions',data);self.assertEqual(status,201);return body

    def test_password_upper_boundary_is_valid(self):
        password='aB9!'*32;email=self.prefix+'-128@example.test'
        self.assertEqual(len(password),128)
        self.assertEqual(self.anon.request('POST','/auth/register',{'name':'Limite','email':email,'password':password})[0],201)
        self.assertEqual(self.anon.request('POST','/auth/login',{'email':email,'password':password})[0],200)

    def test_portuguese_export_preserves_text_and_decimal(self):
        from pypdf import PdfReader
        description=self.prefix+' Café e educação';amount='12345678901234.56'
        data=self.transaction('Café e educação',amount);self.create(data)
        params={'description':description}
        status,_,pdf=self.client.request('GET','/transactions/export.pdf',params=params);self.assertEqual(status,200)
        text=compact(' '.join(page.extract_text() for page in PdfReader(io.BytesIO(pdf)).pages))
        self.assertIn(compact(description),text);self.assertIn('Educação',text)
        status,_,xlsx=self.client.request('GET','/transactions/export.xlsx',params=params);self.assertEqual(status,200)
        rows=xlsx_rows(xlsx);found=False
        for row in rows:
            if compact(description) not in compact(' '.join(row)):continue
            for cell in row:
                try:found=found or decimal_cell(cell)==Decimal(amount)
                except InvalidOperation:pass
        self.assertTrue(found,'Linha deve preservar descrição e valor decimal exato')

    def test_rejected_update_preserves_existing_record(self):
        original=self.transaction('rollback');row=self.create(original);invalid=dict(original,amount='0.00')
        path='/transactions/'+str(row['id'])
        self.assertEqual(self.client.request('PUT',path,invalid)[0],400)
        status,_,current=self.client.request('GET',path);self.assertEqual(status,200)
        self.assertEqual(Decimal(current['amount']),Decimal(original['amount']));self.assertEqual(current['description'],original['description'])

    def test_empty_filter_has_zero_summary_and_valid_files(self):
        from pypdf import PdfReader
        params={'description':self.prefix+' never-created'}
        status,_,summary=self.client.request('GET','/transactions/summary',params=params);self.assertEqual(status,200)
        for field in ('income','expense','balance'):self.assertEqual(Decimal(summary[field]),Decimal('0'))
        self.assertEqual(summary['count'],0)
        status,_,pdf=self.client.request('GET','/transactions/export.pdf',params=params);self.assertEqual(status,200)
        self.assertGreaterEqual(len(PdfReader(io.BytesIO(pdf)).pages),1)
        status,_,xlsx=self.client.request('GET','/transactions/export.xlsx',params=params);self.assertEqual(status,200);self.assertTrue(xlsx_rows(xlsx))


def main():
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--scenario',required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();a.BASE=args.base.rstrip('/')
    result=unittest.TextTestRunner(verbosity=2,resultclass=a.JSONResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(ContractBoundaries))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps({'scenario':args.scenario,'tests_run':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'cases':result.cases,'scope':'Complemento comum dos critérios originais: senha128, texto ptBR/decimal em exports, rollback e vazio; os16originais permanecem inalterados'},indent=2,ensure_ascii=False)+'\n')
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':sys.exit(main())
