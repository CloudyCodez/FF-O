"""Owned esper records using Global 9.1.0's UserBeastInfoResponse contract.

Story acquisitions and rarity upgrades use a documented offline clear-flag
policy. Training and deck assignment remain separate, unrestored contracts.
"""
import json
import sqlite3
from contextlib import closing
from functools import lru_cache
from pathlib import Path
from accounts import DEFAULT_DB

@lru_cache(maxsize=1)
def statuses():
    path=next((Path(__file__).resolve().parents[1]/'assets/decoded/mst').glob('F_BEAST_STATUS_MST-*'))
    return {(r['Iwfx42Wo'],r['9fW0TePj']):r
            for r in map(json.loads,path.read_text(encoding='utf-8').splitlines())}

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS espers (beast_id INTEGER PRIMARY KEY, rarity INTEGER NOT NULL DEFAULT 1, level INTEGER NOT NULL DEFAULT 1, exp INTEGER NOT NULL DEFAULT 0)')

def grant_siren(db):
    initialize(db)
    db.execute('INSERT OR IGNORE INTO espers (beast_id) VALUES (1)')

def sync_story_acquisitions(db):
    """Offline acquisition policy: native trial-clear flag precedes level gate.

    Native status level gates end in 110; the matching mission clear ends in
    100. Require that exact clear to exist in both a mission row and this save.
    This provisional mapping replaces the previous Siren-only special case.
    """
    initialize(db)
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='story_switches'").fetchone():return
    saved={str(r[0]) for r in db.execute('SELECT id FROM story_switches')}
    for (ident,rarity),master in statuses().items():
        clear=str(int(master['W2hq4UaG'])-10)
        if clear not in acquisition_flags() or clear not in saved:continue
        db.execute('INSERT OR IGNORE INTO espers (beast_id,rarity) VALUES (?,?)',(int(ident),int(rarity)))
        db.execute('UPDATE espers SET rarity=?,level=1,exp=0 WHERE beast_id=? AND rarity<?',
                   (int(rarity),int(ident),int(rarity)))

@lru_cache(maxsize=1)
def acquisition_flags():
    path=next((Path(__file__).resolve().parents[1]/'assets/decoded/mst').glob('F_MISSION_MST-*'))
    return {flag for row in map(json.loads,path.read_text(encoding='utf-8').splitlines())
            for flag in row['dIPkNn61'].split(',') if flag.startswith('820')}

def packets_on_connection(db):
    initialize(db)
    owned=[]
    fields=('fh31sk7B','PC97pWQj','9NBV1XCS','Pn5w9dfh','84FJM3PD','41fbhtj2')
    stats=('em5hx4FX','L0MX7edB','o7Ynu1XP','6tyb58Kc','Y9H6TWnv','sa8Ewx3H')
    for ident,rarity,level,exp in db.execute('SELECT beast_id,rarity,level,exp FROM espers ORDER BY beast_id'):
        if level!=1:raise ValueError('Esper growth is not restored')
        master=statuses()[(str(ident),str(rarity))]
        row={'Iwfx42Wo':str(ident),'9fW0TePj':str(rarity),'7wV3QZ80':str(level),
             'B6H34Mea':str(exp),'X9ABM7En':'0','0A1BkNWb':'0','HXc84WT2':'0'}
        row.update({out:master[source].split(',')[0] for out,source in zip(fields,stats)})
        owned.append(row)
    return {'gP9TW2Bf':owned}

def packets(database=DEFAULT_DB):
    with closing(sqlite3.connect(database,timeout=10)) as db,db:
        # Migrate saves which cleared the native Siren acquisition before
        # esper inventory existed; do not grant it on fresh profiles.
        sync_story_acquisitions(db)
        return packets_on_connection(db)
