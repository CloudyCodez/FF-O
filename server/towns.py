"""Bounded native first-island town entry and story switch persistence."""
from accounts import DEFAULT_DB
from economy import currency_packets
from switches import switch_packets
import json
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def supported_towns():
    root=Path(__file__).resolve().parents[1]
    def rows(name):
        path=next((root/'assets/decoded/mst').glob(name+'-*'))
        return map(json.loads,path.read_text(encoding='utf-8').splitlines())
    worlds={r['9Pb24aSy'] for r in rows('F_WORLD_MST') if r['dw2nvP3r']=='1'}
    resources={r['Nnb20keZ']:r for r in rows('F_RESOURCE_MAP_MST')}
    supported={'1101','1102','9001'}
    def valid_pack(path):
        with path.open('rb') as stream:return stream.read(4)==b'CPK '
    for town in rows('F_TOWN_MST'):
        if town['9Pb24aSy'] not in worlds:continue
        primary=[resources.get(ident) for ident in town['q4f9IdMs'].split(',') if ident]
        if not primary or any(r is None for r in primary):continue
        if all(any(valid_pack(p) for p in
                   (root/'assets/cache/common_lang/sd'/r['3LHdc6Qa']).glob('Ver*_'+r['pJ56sAEo']))
               for r in primary):supported.add(town['Gh92V3Tx'])
    return supported

def handle(name,payload,database=DEFAULT_DB):
    records=payload.get('JcxS6A8N',[])
    if len(records)!=1 or records[0].get('Gh92V3Tx') not in supported_towns():return None
    town=records[0]
    # Treasure, consumables and side-quest rewards need their own inventories.
    # Never acknowledge them without granting/consuming the corresponding item.
    if any(town.get(k,'') for k in ('NiG2wL3A','0VBQ7AhT')) or payload.get('1sGiqV9T'):return None
    flags=town.get('dIPkNn61','')
    if name=='TownInRequest' and flags:raise ValueError('Town entry cannot complete story flags')
    return {**currency_packets(),**switch_packets({'0jqUZuT1':[{'dIPkNn61':flags}]},database)}
