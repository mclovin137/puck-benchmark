#!/usr/bin/env python3
"""Publica somente contagens observadas; ausência de execução não vira zero."""
import csv
import datetime as dt
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CATEGORIES=('codigo','doc','testes','planejamento','revisao','busca','configuracao','mista','nao_disponivel')
LABELS={'codigo':'Código','doc':'Documentação','testes':'Testes','planejamento':'Planejamento','revisao':'Revisão','busca':'Busca','configuracao':'Configuração','mista':'Mista','nao_disponivel':'Não disponível'}


def total(groups,field):
    values=[g.get(field) for g in groups if g.get(field) is not None]
    return sum(values) if values else None


def main():
    report=json.loads((ROOT/'reports/token-breakdown.json').read_text())
    state_path=ROOT/'experiment/results/runs.json'
    states=json.loads(state_path.read_text()) if state_path.exists() else {}
    records=[]
    lines=['# Uso de tokens por atividade','',f"Snapshot: {report['generated_at']}.",'',
           'Entrada inclui cache; saída inclui raciocínio. Não somar esses subconjuntos novamente. Categorias indicam associação por resposta, não a causa de cada token de contexto. Fases declaradas são uma dimensão separada da atividade detectada.','',
           'O coletor Puck reconhece escritas diretas e patches. O complemento reconhece chamadas literais tools.exec_command no wrapper functions.exec, ignorando comentários, strings e comandos dinâmicos sem executar o conteúdo; scripts Python dinâmicos e comandos construídos em runtime podem permanecer sem classificação. Revisão, planejamento e busca sem escrita dependem da fase explícita.','',
           'O overhead inclui coordenação, instrumentação e avaliação externas; não é rateado arbitrariamente entre cenários. Custos faturados, tempo ativo e atribuição causal por skill não estão disponíveis neste estágio.','']
    for scenario in ('overhead','C1','C2','C3','C4'):
        groups=[g for g in report['groups'] if g['scenario']==scenario]
        entry={'scenario':scenario,'run':1,'state':states.get(scenario,{}).get('state','nao_iniciado' if not groups else 'em_andamento'),
               'responses':sum(g['responses'] for g in groups),'input_tokens':total(groups,'input_tokens'),'output_tokens':total(groups,'output_tokens'),
               'cache_read_tokens':total(groups,'cache_read_tokens'),'cache_write_tokens':total(groups,'cache_write_tokens'),'reasoning_tokens':total(groups,'reasoning_tokens'),
               'billed_usd':None,'active_seconds':None,'functional_pass_rate':None,'skills_attribution':None,'activity':{},'phase':{},
               'source':'reports/token-breakdown.json','generated_at':report['generated_at']}
        denom=entry['output_tokens']
        lines.extend([f'## {scenario}','', '| Atividade | Respostas | Entrada | Saída | % da saída |','| --- | ---: | ---: | ---: | ---: |'])
        for category in CATEGORIES:
            selected=[g for g in groups if g['category']==category]
            d={'responses':sum(g['responses'] for g in selected),'input_tokens':total(selected,'input_tokens'),'output_tokens':total(selected,'output_tokens')}
            d['output_share_pct']=round(100*d['output_tokens']/denom,2) if denom and d['output_tokens'] is not None else None
            entry['activity'][category]=d
            fmt=lambda v:'n/d' if v is None else str(v)
            lines.append('| '+LABELS[category]+' | '+' | '.join(fmt(d[k]) for k in ('responses','input_tokens','output_tokens','output_share_pct'))+' |')
        for phase in CATEGORIES:
            selected=[g for g in groups if g['phase']==phase]
            entry['phase'][phase]={'responses':sum(g['responses'] for g in selected),'input_tokens':total(selected,'input_tokens'),'output_tokens':total(selected,'output_tokens')}
        lines.append('');records.append(entry)
    (ROOT/'reports/metrics.json').write_text(json.dumps({'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'interim','records':records},indent=2,ensure_ascii=False)+'\n')
    with (ROOT/'reports/metrics.csv').open('w',newline='') as stream:
        fields=['scenario','run','state','responses','input_tokens','output_tokens','cache_read_tokens','cache_write_tokens','reasoning_tokens','billed_usd','active_seconds','functional_pass_rate','source','generated_at']
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore',lineterminator='\n');writer.writeheader();writer.writerows(records)
    (ROOT/'reports/token-usage.md').write_text('\n'.join(lines).rstrip()+'\n')
    print('Métricas intermediárias renderizadas; nenhum resultado de aplicação inferido.')

if __name__=='__main__':main()
