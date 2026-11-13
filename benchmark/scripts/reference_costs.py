#!/usr/bin/env python3
"""Referência API determinística, sem chamadas a modelos nem cobrança inferida."""
from collections import defaultdict
from decimal import Decimal
import datetime as dt
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PRICE_FILE=ROOT/'experiment/evaluation/api-reference-prices.json'
PRICES=json.loads(PRICE_FILE.read_text())


def estimate(event):
    prices=PRICES['models'].get(event.get('model'))
    counters=[event.get(k) for k in ('input_tokens','cache_read_tokens','cache_write_tokens','output_tokens')]
    if not prices or any(type(x) is not int or x<0 for x in counters):return None
    incoming,cached,written,outgoing=counters
    reasoning=event.get('reasoning_tokens')
    if reasoning is not None and (type(reasoning) is not int or not 0<=reasoning<=outgoing):return None
    if cached>incoming or written:return None
    long=incoming>PRICES['long_context']['threshold_exclusive']
    input_multiplier=Decimal(PRICES['long_context']['input_and_cache_multiplier']) if long else Decimal(1)
    output_multiplier=Decimal(PRICES['long_context']['output_multiplier']) if long else Decimal(1)
    return ((Decimal(incoming-cached)*Decimal(prices['input'])+Decimal(cached)*Decimal(prices['cached_input']))*input_multiplier+Decimal(outgoing)*Decimal(prices['output'])*output_multiplier)/Decimal(1000000)


def summarize(events):
    estimates=[estimate(e) for e in events]
    known=[v for v in estimates if v is not None]
    subtotal=format(sum(known,Decimal(0)),'.8f') if known else None
    times=[]
    for e in events:
        try:
            stamp=dt.datetime.fromisoformat(e['timestamp'].replace('Z','+00:00'))
            if stamp.tzinfo is not None:times.append(stamp)
        except (KeyError,ValueError,AttributeError):pass
    return {'responses':len(events),'priced_responses':len(known),'unpriced_responses':len(events)-len(known),
            'reference_standard_api_usd':subtotal if events and len(known)==len(events) else None,
            'known_subtotal_usd':subtotal,'billed_usd':None,
            'first_observed_response':min(times).isoformat() if times else None,
            'last_observed_response':max(times).isoformat() if times else None,
            'observed_response_span_seconds':(max(times)-min(times)).total_seconds() if times and len(times)==len(events) else None,
            'active_seconds':None}


def main():
    events=[json.loads(s) for s in (ROOT/'reports/token-events.jsonl').read_text().splitlines() if s.strip()]
    report={'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'interim','price_source':str(PRICE_FILE.relative_to(ROOT)),
            'measurement':'API Standard reference estimate; not observed charges','overall':summarize(events),
            'notes':['Cache is a subset of input; reasoning is a subset of output.',
                     'Each dimension is an alternative grouping, not an additional cost.',
                     'Subscription billing, service tier, regional premiums and tool fees are unavailable; Standard API is a stated counterfactual.',
                     'Response span includes preparation, interruption and idle gaps; it is not active time or complete project duration.'],
            'dimensions':{}}
    for dimension in ('scenario','model','agent','phase'):
        groups=defaultdict(list)
        for event in events:
            values=[event.get('scenario'),event.get(dimension)]
            key=tuple(value if isinstance(value,str) and value else 'nao_disponivel' for value in values)
            groups[key].append(event)
        report['dimensions'][dimension]=[dict(scenario=s,value=v,**summarize(rows)) for (s,v),rows in sorted(groups.items())]
    (ROOT/'reports/cost-estimates.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print('Referência API calculada; cobrança real permanece não disponível.')


if __name__=='__main__':main()
