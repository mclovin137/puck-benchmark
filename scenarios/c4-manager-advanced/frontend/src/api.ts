export type Transaction={id:string;type:'INCOME'|'EXPENSE';description:string;category:string;amount:string;date:string;createdAt:string;updatedAt:string};
export type Summary={income:string;expense:string;balance:string;count:number};
export type Listing={content:Transaction[];totalElements:number;page:number;size:number;totalPages:number};
export type User={id:string;name:string;email:string};
export async function request<T>(path:string,token:string,options:RequestInit={}):Promise<T>{
 const response=await fetch('/api'+path,{...options,headers:{...(options.body?{'Content-Type':'application/json'}:{}),...(token?{Authorization:'Bearer '+token}:{}),...options.headers},cache:'no-store'});
 if(!response.ok){const error=await response.json().catch(()=>({message:'Serviço indisponível. Tente novamente.'}));throw new Error(response.status===401?'Sua sessão não está ativa. Entre novamente.':error.message||'Não foi possível concluir.');}
 if(response.status===204)return undefined as T;return response.json();
}
export function money(value:string){const negative=value.startsWith('-');const [integer,cents='00']=value.replace('-','').split('.');return `${negative?'− ':''}R$ ${BigInt(integer).toLocaleString('pt-BR')},${cents.padEnd(2,'0')}`;}
export function localDate(value:string){return value.split('-').reverse().join('/');}
