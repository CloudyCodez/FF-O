"""Permanent offline Vortex schedule with visibly provisional encounters.

Native SpDungeonCondMstResponse field contract; historical rotations, event
currencies, raids and bespoke rewards are not represented as restored.
"""
import json,time
from functools import lru_cache
from pathlib import Path
from story_policy import effective_mission
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def missions():
    path=next((ROOT/'assets/decoded/mst').glob('F_MISSION_MST-*'))
    return {r['qo3PECw6']:effective_mission(r) for r in
            map(json.loads,path.read_text(encoding='utf-8').splitlines()) if r['9Pb24aSy']=='2'}

@lru_cache(maxsize=1)
def condition_rows():
    community=json.loads((ROOT/'research/community/missions.json').read_text(encoding='utf-8'))
    areas={};dungeons={}
    for ident,mission in missions().items():
        name=community.get(ident,{}).get('name','Vortex '+mission['uv60hgDW'])
        areas.setdefault(mission['uv60hgDW'],(name.split(' - ')[0],mission))
        dungeons.setdefault(mission['U9iHsau3'],(name,mission))
    result=[]
    def row(name,mission,dungeon,ident,order):
        lower=name.lower()
        category='2' if any(x in lower for x in ('chamber of experience','chamber of riches','cactuar','gil snapper')) else (
            '4' if any(x in lower for x in ('scorn of','chamber of the fallen','chamber of arms')) else (
            '5' if 'chronicle' in lower else '1'))
        return {'qnUhs32P':category,'uv60hgDW':mission['uv60hgDW'],'U9iHsau3':dungeon,
                'qo3PECw6':ident,'G4L0YIB2':name+' [Offline]','w7VR6ypY':'0','Z0EN6jSh':str(order),
                '4yT7FUqj':'','7JBX0Rsc':'','xm7c08IS':'0','QCLs6SV8':'0','ET8L6iDw':'0',
                'EgW0rXQ9':'0','45wVefcS':'','MrxFQ63W':'','5mouF8P1':'','M1p3ehVU':'',
                'A5efbo71':'','vnhT2EM5':'0','td06MKEX':'0','fSxqkF10':'0','tL6G9egd':'0',
                'C8Qf5bs6':'0','z0ft1PK8':'0','oY0vAuE9':'0','mTHe6pI0':'',
                'VjJQ51uG':'2020-01-01 00:00:00','m8ivD4NX':'2037-01-01 00:00:00',
                'NTXoA6e2':'2020-01-01 00:00:00','7Gvw6J82':'2037-01-01 00:00:00',
                'V48um7Jw':'2037-01-01 00:00:00','0iWgxc1X':'0','B2FW5Qjq':''}
    for order,(area,(name,mission)) in enumerate(sorted(areas.items(),key=lambda x:int(x[0]))):
        result.append(row(name,mission,'0','0',order))
    for order,(dungeon,(name,mission)) in enumerate(sorted(dungeons.items(),key=lambda x:int(x[0]))):
        result.append(row(name,mission,dungeon,'0',order))
    return result

def packets():
    return {'0xkoNP8U':condition_rows(),'8SztQck9':[{'0Zpuzj7E':str(int(time.time())+300)}]}
