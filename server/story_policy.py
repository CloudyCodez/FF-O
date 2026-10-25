"""Explicit temporary battle stand-ins for unavailable zero-wave story content."""
import json
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def story_worlds():
    path=next((ROOT/'assets/decoded/mst').glob('F_WORLD_MST-*'))
    return {r['9Pb24aSy'] for r in map(json.loads,path.read_text(encoding='utf-8').splitlines()) if r['dw2nvP3r']=='1'}

@lru_cache(maxsize=1)
def unavailable_missions():
    path=Path(__file__).resolve().parent/'data/story-resource-fallbacks.json'
    return json.loads(path.read_text(encoding='utf-8'))['missions'] if path.exists() else {}

def effective_mission(row):
    if row['9Pb24aSy']=='2':
        patched=dict(row)
        patched.update({'Y4VoF8yu':'1','0VkYZx1a':'0','8xi6Xvyk':str(max(1,min(8,int(row['8xi6Xvyk'])))),
                        'DYTx1Is3':'100022','q4f9IdMs':'','bs60p4LC':'','6w4xiIsS':'',
                        'juA0Z4m7':'0','1C7GDEv4':'','gQR24kST':'0','IpyB85ab':'0'})
        return patched
    if row['9Pb24aSy'] not in story_worlds():return dict(row)
    if int(row['8xi6Xvyk'])!=0 and row['qo3PECw6'] not in unavailable_missions():return dict(row)
    patched=dict(row)
    patched.update({'Y4VoF8yu':'1','0VkYZx1a':'0','8xi6Xvyk':str(max(1,int(row['8xi6Xvyk']))),
                    'DYTx1Is3':'100022','q4f9IdMs':'','bs60p4LC':'','6w4xiIsS':''})
    return patched
