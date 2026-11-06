"""Teste HTTP local isolado: CRUD, autorização, filtros e exportação."""
import json, urllib.request, urllib.error, uuid, io, zipfile
from pypdf import PdfReader
base='http://127.0.0.1:18083/api'
def call(path,method='GET',data=None,token=None):
    headers={}
    if token: headers['Authorization']='Bearer '+token
    if data is not None: headers['Content-Type']='application/json'; data=json.dumps(data).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(base+path,data=data,headers=headers,method=method)) as r: return r.status,r.read()
    except urllib.error.HTTPError as e: return e.code,e.read()
def obj(response): return json.loads(response[1])
suffix=uuid.uuid4().hex
users=[]
for n in ('a','b'):
    creds={'name':n,'email':n+suffix+'@example.com','password':'senha segura 1234'}
    assert call('/auth/register','POST',creds)[0]==201
    status,body=call('/auth/login','POST',creds); assert status==200
    users.append(json.loads(body)['token'])
a,b=users
assert call('/transactions')[0]==401
entry={'type':'INCOME','description':'Salário %_','category':'Trabalho','amount':'123.45','date':'2026-01-20'}
status,body=call('/transactions','POST',entry,a); assert status==201
id=json.loads(body)['id']
assert call('/transactions/'+str(id),token=b)[0]==404
assert call('/transactions/'+str(id),'DELETE',token=b)[0]==404
assert obj(call('/transactions?description=%25_',token=a))['totalElements']==1
assert obj(call('/transactions/summary?category=Trabalho',token=a))=={'income':'123.45','expense':'0.00','balance':'123.45','count':1}
assert obj(call('/transactions/summary',token=b))['count']==0
assert call('/transactions?startDate=2026-02-01&endDate=2026-01-01',token=a)[0]==400
assert call('/transactions','POST',{**entry,'amount':'0'},a)[0]==400
assert call('/transactions','POST',{**entry,'amount':1.25},a)[0]==400
status,pdf=call('/transactions/export.pdf',token=a);assert status==200 and pdf.startswith(b'%PDF'); text=' '.join(p.extract_text() for p in PdfReader(io.BytesIO(pdf)).pages); assert 'Salário' in text and '123.45' in text and 'Saldo:' in text
status,other_pdf=call('/transactions/export.pdf',token=b); assert status==200; other_text=' '.join(p.extract_text() for p in PdfReader(io.BytesIO(other_pdf)).pages); assert 'Salário' not in other_text and '123.45' not in other_text
status,filtered_pdf=call('/transactions/export.pdf?category=Inexistente',token=a); assert status==200; filtered_text=' '.join(p.extract_text() for p in PdfReader(io.BytesIO(filtered_pdf)).pages); assert 'Salário' not in filtered_text and '123.45' not in filtered_text
status,xlsx=call('/transactions/export.xlsx',token=a);assert status==200; archive=zipfile.ZipFile(io.BytesIO(xlsx)); assert 'xl/workbook.xml' in archive.namelist(); strings=archive.read('xl/sharedStrings.xml').decode(); assert 'Salário' in strings and '123.45' in strings and 'Saldo:' in strings
assert call('/transactions/'+str(id),'PUT',{**entry,'amount':'0.01'},a)[0]==200
assert call('/transactions/'+str(id),'DELETE',token=a)[0]==204
assert call('/auth/logout','POST',token=a)[0]==204
assert call('/auth/me',token=a)[0]==401
print('Integração HTTP: cadastro, sessão, isolamento, filtros, resumo, exportações e CRUD passaram.')
