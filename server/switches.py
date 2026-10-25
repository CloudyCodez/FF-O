"""Persist client-managed story switches using the recovered master types."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from accounts import DEFAULT_DB
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def switch_types():
    masters = next((ROOT/'assets/decoded/mst').glob('F_SWITCH_MST-*.txt'))
    types = {}
    for line in masters.read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        types[int(row['8vAYn3IX'])] = (int(row['5opcUT9t']), int(row['QLfe23bu']))
    return types

def packets_on_connection(db, payload=None):
    types=switch_types()
    incoming = None
    if payload is not None:
        rows = payload.get('0jqUZuT1', [])
        if not isinstance(rows, list) or len(rows) != 1:
            raise ValueError('Expected one switch snapshot')
        value = rows[0].get('dIPkNn61', '')
        incoming = {int(x) for x in value.split(',') if x}
        if not incoming.issubset(types):
            raise ValueError('Unknown client switch')
    db.execute('CREATE TABLE IF NOT EXISTS story_switches (id INTEGER PRIMARY KEY)')
    if incoming is not None:
        db.executemany('INSERT OR IGNORE INTO story_switches VALUES (?)', [(x,) for x in incoming])
    saved = [r[0] for r in db.execute('SELECT id FROM story_switches ORDER BY id')]
    grouped = {}
    for ident in saved:
        kind, index = types[ident]
        grouped.setdefault(kind, []).append(index)
    result=[]
    # Native bit reader 0x1a8a638: four switches per hex character, MSB first.
    for kind, indexes in sorted(grouped.items()):
        digits=[0] * (max(indexes)//4+1)
        for index in indexes:
            digits[index//4] |= 8 >> (index%4)
        result.append({'5opcUT9t':str(kind), 'juA0Z4m7':''.join(format(x,'x') for x in digits)})
    return {'8J1R5PXG': result}


def switch_packets(payload=None, database=DEFAULT_DB):
    with closing(sqlite3.connect(database, timeout=10)) as db, db:
        return packets_on_connection(db,payload)
