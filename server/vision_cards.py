"""Persisted Vision Card rewards required by native Neo Vision reveals."""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def masters():
    path = next((ROOT/'assets/decoded/mst').glob('F_VISION_CARD_MST-*.txt'))
    return {int(row['5giCMUd2']): row for row in
            map(json.loads, path.read_text(encoding='utf-8').splitlines())}


def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS vision_cards '
               '(uid INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER NOT NULL)')


def serialize(row):
    uid, ident = row
    return {'5giCMUd2': str(ident), 'gXb32xzQ': str(uid),
            '7wV3QZ80': '1', 'B6H34Mea': '0', 'X9ABM7En': '0',
            '0W93YZvw': '0', 'uR70J6Lr': '0', '8zE6w9RP': '0'}


def grant_for_unit(db, unit):
    # Native UnitMst::isNeoVision checks this flag, not the displayed rarity.
    if int(unit.get('5Mgpv8hJ', 0)) not in (1, 2):
        return None
    ident = int(unit.get('5giCMUd2', 0))
    # Historical random-card pools are not recovered. Use a real, fixed local
    # starter card when the unit has no assigned card; never omit its NV reward.
    if not ident:
        ident = 100000101
    if ident not in masters():
        raise ValueError(f'Unrecovered Vision Card {ident}')
    initialize(db)
    uid = db.execute('INSERT INTO vision_cards (card_id) VALUES (?)', (ident,)).lastrowid
    return serialize((uid, ident))


def packets(db):
    initialize(db)
    return {'2Xi0wuGA': [serialize(row) for row in
                         db.execute('SELECT uid,card_id FROM vision_cards ORDER BY uid')]}
