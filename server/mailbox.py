"""Persistent one-time NieR parcels using native mail records."""
import sqlite3
from contextlib import closing
from accounts import DEFAULT_DB
from units import initialize,serialize,masters

NIER=((310000107,'2B'),(401001207,'A2'),(310000206,'9S'),
      (310000306,'Adam'),(401001306,'Eve'),(310000405,'21O'),
      (401013807,'2B - Neo Vision'),(401013907,'A2 - Neo Vision'))

def setup(db):
    initialize(db)
    db.execute('CREATE TABLE IF NOT EXISTS gift_parcels (id INTEGER PRIMARY KEY, unit_id INTEGER NOT NULL, name TEXT NOT NULL, claimed_uid INTEGER REFERENCES units(uid))')
    for index,(unit,name) in enumerate(NIER,900100):
        if unit not in masters():raise ValueError('NieR unit absent from recovered master')
        db.execute('INSERT OR IGNORE INTO gift_parcels VALUES (?,?,?,NULL)',(index,unit,name))

def records(db):
    return [{'ynP26rjD':str(ident),'9m5yIkCK':'2','fbcj5Aq9':'NieR collaboration: '+name,
             'Wk1v6upb':'A one-time FF:O character gift. Claim to add this unit to your roster.',
             'u7Z1DYz4':'10','7iJpH5zZ':f'10:{unit}:1:0:0','14Y7jihw':'2' if uid else '0',
             'f5LHNT4v':'2026-01-01 00:00:00','k0qX5yQd':'2026-01-01 00:00:00',
             '0Sba4mZ9':'2026-01-01 00:00:00' if uid else '', 'eGv8Da2s':''}
            for ident,unit,name,uid in db.execute('SELECT * FROM gift_parcels ORDER BY id')]

def packets(database=DEFAULT_DB):
    with closing(sqlite3.connect(database,timeout=10)) as db,db:
        setup(db);rows=records(db)
    received=sum(r['14Y7jihw']=='2' for r in rows)
    return {'qja26wHb':rows,'t8TPs6o2':[{'2BW7YLwg':str(len(rows)),'sC84jvZH':str(len(rows)-received),'mzR39KXj':str(received),'TnZ3J4v8':'0'}]}

def claim(payload,database=DEFAULT_DB):
    rows=payload.get('rStH7od8',[])
    if len(rows)!=1:raise ValueError('Expected one mail claim record')
    ids=[]
    for value in rows[0].get('Qe02W7rX','').split(','):
        if not value:continue
        parts=value.split(':')
        if len(parts)>2 or (len(parts)==2 and parts[1]!='2'):raise ValueError('Invalid mail receipt type')
        ids.append(int(parts[0]))
    if not ids:raise ValueError('Missing mail IDs')
    with closing(sqlite3.connect(database,timeout=10)) as db,db:
        setup(db);db.execute('BEGIN IMMEDIATE') if not db.in_transaction else None
        known={r[0] for r in db.execute('SELECT id FROM gift_parcels')}
        if not set(ids)<=known:raise ValueError('Unknown mail ID')
        granted=[]
        for ident in sorted(set(ids)):
            unit,uid=db.execute('SELECT unit_id,claimed_uid FROM gift_parcels WHERE id=?',(ident,)).fetchone()
            if uid is None:
                uid=db.execute('INSERT INTO units (unit_id) VALUES (?)',(unit,)).lastrowid
                db.execute('UPDATE gift_parcels SET claimed_uid=? WHERE id=?',(uid,ident))
            granted.append(serialize(db.execute('SELECT uid,unit_id,level,exp FROM units WHERE uid=?',(uid,)).fetchone()))
    return {**packets(database),'B71MekS8':granted}
