import React from 'react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, render, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../src/App';

type Call = {url:string, method:string, authorization:string | undefined, body?:string};
const calls: Call[] = [];
let loggedOut = false;
let deleted = false;
let failLogin = false;
const response = (status:number, value:unknown = {}) => ({ok:status >= 200 && status < 300, status, json:async()=>value});
beforeEach(()=>{
 calls.length=0; loggedOut=false; deleted=false; failLogin=false;
 vi.stubGlobal('fetch',vi.fn(async (path:string, init:RequestInit={})=>{
  const method=init.method ?? 'GET'; const headers=init.headers as Record<string,string> | undefined;
  calls.push({url:path,method,authorization:headers?.Authorization,body:init.body as string | undefined});
  if(path==='/api/auth/login') return failLogin ? response(401) : response(200,{token:'teste-opaco'});
  if(path==='/api/auth/logout'){loggedOut=true;return response(204);}
  if(path==='/api/transactions/7' && method==='DELETE'){deleted=true;return response(204);}
  if(path.startsWith('/api/transactions/summary')) return response(200,{income:'0.00',expense:deleted?'0.00':'25.50',balance:deleted?'0.00':'-25.50',count:deleted?0:1});
  if(path.startsWith('/api/transactions?')) return response(200,{content:deleted?[]:[{id:7,type:'EXPENSE',description:'Almoço',category:'Casa',amount:'25.50',date:'2026-01-20'}],totalElements:deleted?0:1,page:0,size:20,totalPages:deleted?0:1});
  throw new Error('Requisição inesperada: '+path);
 }));
});
afterEach(()=>{cleanup();vi.restoreAllMocks();vi.unstubAllGlobals();localStorage.clear();sessionStorage.clear();});
async function login(user:ReturnType<typeof userEvent.setup>){
 await user.type(screen.getByLabelText('E-mail'),'pessoa@example.com');
 await user.type(screen.getByLabelText('Senha'),'senha segura 123');
 await user.click(screen.getByRole('button',{name:'Entrar'}));
}
describe('fluxos financeiros',()=>{
 it('apresenta erro de credenciais e permite nova tentativa',async()=>{
  failLogin=true;const user=userEvent.setup();render(<App/>);await login(user);
  await waitFor(()=>expect(screen.getByRole('status').textContent).toContain('credenciais incorretas'));
  expect(screen.queryByRole('heading',{name:'Seu painel'})).toBeNull();
 });
 it('usa a sessão nos filtros e a revoga ao sair sem persistir o token',async()=>{
  const user=userEvent.setup();render(<App/>);await login(user);await screen.findByText('Almoço');
  expect(screen.getByText('R$ -25.50')).toBeTruthy();
  const area=screen.getByRole('heading',{name:'Movimentações'}).closest('section')!;
  await user.type(within(area).getByLabelText('Categoria'),'Casa');
  await waitFor(()=>expect(calls.some(c=>c.url.startsWith('/api/transactions?') && new URL(c.url,'http://localhost').searchParams.get('category')==='Casa')).toBe(true));
  const filtered=calls.filter(c=>c.url.includes('category=Casa'));
  expect(filtered.some(c=>c.url.includes('/summary?'))).toBe(true);
  expect(filtered.every(c=>c.authorization==='Bearer teste-opaco')).toBe(true);
  expect(JSON.stringify(localStorage)).not.toContain('teste-opaco');expect(JSON.stringify(sessionStorage)).not.toContain('teste-opaco');
  await user.click(screen.getByRole('button',{name:'Sair'}));await screen.findByRole('heading',{name:'Entrar'});
  expect(loggedOut).toBe(true);expect(calls.find(c=>c.url==='/api/auth/logout')?.authorization).toBe('Bearer teste-opaco');
 });
 it('não exclui ao cancelar e atualiza a lista após confirmação',async()=>{
  const user=userEvent.setup();render(<App/>);await login(user);await screen.findByText('Almoço');
  const confirm=vi.spyOn(window,'confirm').mockReturnValueOnce(false).mockReturnValueOnce(true);
  await user.click(screen.getByRole('button',{name:'Excluir'}));expect(deleted).toBe(false);expect(calls.some(c=>c.method==='DELETE')).toBe(false);
  await user.click(screen.getByRole('button',{name:'Excluir'}));await screen.findByText('Nenhuma movimentação encontrada.');
  expect(confirm).toHaveBeenCalledTimes(2);expect(calls.find(c=>c.method==='DELETE')?.authorization).toBe('Bearer teste-opaco');
 });
});
