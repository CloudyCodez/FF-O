"""Native challenge state derived from recorded, supported mission clears.

Only the unconditional completion challenge (condition 68) is restored here.
Conditional achievements and mail reward delivery are not inferred.
"""
import json,sqlite3
from pathlib import Path
from functools import lru_cache
from contextlib import closing
from accounts import DEFAULT_DB

@lru_cache(maxsize=1)
def completion_ids():
    path=next((Path(__file__).resolve().parents[1]/'assets/decoded/mst').glob('F_CHALLENGE_MST-*'))
    return {r['qo3PECw6']:r['V36ygRYs']
            for r in map(json.loads,path.read_text(encoding='utf-8').splitlines())
            if r['Pzn5h0Ga']=='68'}

def packets(database=DEFAULT_DB):
    with closing(sqlite3.connect(database,timeout=10)) as db:
        return packets_on_connection(db)

def packets_on_connection(db):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='mission_results'").fetchone():
        return {'TQ5AJd2K':[]}
    missions=[str(r[0]) for r in db.execute('SELECT DISTINCT mission FROM mission_results ORDER BY mission')]
    ids=completion_ids()
    return {'TQ5AJd2K':[{'qo3PECw6':mission,'qdhWF7z9':ids[mission],'wf5Toh4k':''}
                         for mission in missions if mission in ids]}
