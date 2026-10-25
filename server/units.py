"""Local owned units, serialized with the 9.1.0 native field names."""
import json,sqlite3
from contextlib import closing
from functools import lru_cache
from pathlib import Path
from accounts import DEFAULT_DB

ROOT=Path(__file__).resolve().parents[1]
STATS=('em5hx4FX','L0MX7edB','o7Ynu1XP','6tyb58Kc','Y9H6TWnv','sa8Ewx3H')

@lru_cache(maxsize=1)
def masters():
    path=next((ROOT/'assets/decoded/mst').glob('F_UNIT_MST-*.txt'))
    return {int(r['3HriTp6B']):r for r in map(json.loads,path.read_text(encoding='utf-8').splitlines())}

@lru_cache(maxsize=1)
def growth_tables():
    def rows(name):
        path=next((ROOT/'assets/decoded/mst').glob(name+'-*'))
        return map(json.loads,path.read_text(encoding='utf-8').splitlines())
    growth={(int(r['aU3o2D4t']),int(r['uk6Wh8mw']),int(r['7wV3QZ80'])):
            int(r['UjKF93ok']) for r in rows('F_UNIT_GROW_MST')}
    exp={(int(r['0W7g6YXS']),int(r['7wV3QZ80'])):int(r['93fnYUJG'])
         for r in rows('F_UNIT_EXP_PATTERN_MST')}
    return growth,exp

def growth_rate(master,level):
    if level==1:return 0
    key=(int(master['aU3o2D4t']),int(master['uk6Wh8mw']),level)
    rate=growth_tables()[0].get(key)
    if rate is None:
        raise ValueError(f'Unrecovered unit growth curve: {key}')
    return rate

def gain_exp(row,amount):
    """Native EXP is the remainder within the current level, not lifetime EXP."""
    uid,ident,level,exp=row
    master=masters()[ident];maximum=int(master['aU3o2D4t'])
    exp+=amount
    while level<maximum:
        needed=growth_tables()[1].get((int(master['0W7g6YXS']),level+1))
        if needed is None or needed<=0:raise ValueError('Missing native EXP threshold')
        if exp<needed:break
        exp-=needed;level+=1
    if level==maximum:exp=0
    updated=(uid,ident,level,exp)
    serialize(updated)  # Reject incomplete growth data before touching the save.
    return updated

def level_result(before,after,awarded=0):
    """UserUnitLvInfo::init: uid@before_after, colon fields, four stat parts."""
    def fields(row,earned):
        unit=serialize(row)
        return ':'.join([unit['7wV3QZ80'],'0',
                         unit['B6H34Mea'],*(unit[k] for k in STATS),
                         '0',unit['a71oxzCH'],'0',str(earned),'0','0'])
    # Flattened parameter 30 is the awarded EXP; native
    # MissionResultGetUnitExpScene::getPartyTotalExp (0x237ce44) sums it.
    return f'{before[0]}@{fields(before,0)}_{fields(after,awarded)}'

def battle_party(db):
    initialize(db)
    saved=None
    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='party_decks'").fetchone():
        saved=db.execute('SELECT members FROM party_decks WHERE deck_id=1').fetchone()
    if saved is None:
        return db.execute('SELECT uid,unit_id,level,exp FROM units ORDER BY uid LIMIT 5').fetchall()
    uids=[int(slot.split(':')[2]) for slot in filter(None,saved[0].split(','))]
    return [db.execute('SELECT uid,unit_id,level,exp FROM units WHERE uid=?',(uid,)).fetchone()
            for uid in dict.fromkeys(uids)]

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS units (uid INTEGER PRIMARY KEY AUTOINCREMENT, unit_id INTEGER NOT NULL, level INTEGER NOT NULL DEFAULT 1)')
    if 'exp' not in {r[1] for r in db.execute('PRAGMA table_info(units)')}:
        db.execute('ALTER TABLE units ADD COLUMN exp INTEGER NOT NULL DEFAULT 0')
    if db.execute('SELECT COUNT(*) FROM units').fetchone()[0]==0:
        for ident in (100000102,100000202):
            if ident not in masters():raise ValueError('Starter absent from recovered unit table')
            db.execute('INSERT INTO units (unit_id) VALUES (?)',(ident,))

def serialize(row):
    uid,ident,level=row[:3]
    exp=row[3] if len(row)>3 else 0
    master=masters()[ident]
    result={'og2GHy49':str(uid),'9Tbns0eI':'100000001','3HriTp6B':str(ident),
            '7wV3QZ80':str(level),'B6H34Mea':str(exp),'X9ABM7En':'0','a71oxzCH':'1',
            'EXf5G3Mk':'0','xojJ2w0S':'0','f17L8wuX':'0'}
    for key in STATS:
        low,high,*_=map(int,master[key].split(','))
        percent=growth_rate(master,level)
        base=low+(high-low)*percent//100
        result[key]=f'{base}-0-0-0'
    return result

def inventory(database=DEFAULT_DB):
    with closing(sqlite3.connect(database,timeout=10)) as db,db:
        initialize(db)
        rows=db.execute('SELECT uid,unit_id,level,exp FROM units ORDER BY uid').fetchall()
    return [serialize(r) for r in rows]

def player_packets(database=DEFAULT_DB):
    owned=inventory(database)
    # Member type 1 = owned unit; display order follows the native party record.
    members=','.join(f"1:{i}:{r['og2GHy49']}" for i,r in enumerate(owned[:5]))
    # Native UnitPartyCommon renders every deck from 0 through the recovered
    # MAX_PARTY_DECK_CNT. Missing empty decks are dereferenced by the party UI.
    defines=next((ROOT/'assets/decoded/mst').glob('F_DEFINE_MST-*.txt'))
    count=next(int(r['YjIUDJ97']) for r in map(json.loads,defines.read_text(encoding='utf-8').splitlines())
               if r['AK8Nn7ta']=='MAX_PARTY_DECK_CNT')
    decks=[{'r21y0YzS':str(i),'G4L0YIB2':'FF:O' if i==1 else f'Party {i+1}',
            '2A6fYiEC':members if i==1 else ''} for i in range(count)]
    with closing(sqlite3.connect(database,timeout=10)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS party_decks (deck_id INTEGER PRIMARY KEY, name TEXT NOT NULL, members TEXT NOT NULL)')
        for index,name,saved_members in db.execute('SELECT deck_id,name,members FROM party_decks'):
            if 0<=index<count:
                decks[index].update({'G4L0YIB2':name,'2A6fYiEC':saved_members})
        import vision_cards
        cards=vision_cards.packets(db)
        db.commit()
    return {**cards,'B71MekS8':owned,
            '5Eb0Rig6':decks,
            '8PEB5o7G':[{'r21y0YzS':'1','DYTx1Is3':'100021'}]}


def edit_party(payload,database=DEFAULT_DB):
    rows=payload.get('5Eb0Rig6')
    if not isinstance(rows,list) or len(rows)!=10:return None
    with closing(sqlite3.connect(database,timeout=10)) as db,db:
        initialize(db)
        known={str(row[0]) for row in db.execute('SELECT uid FROM units')}
        ids=set()
        for row in rows:
            ident=int(row['r21y0YzS'])
            if ident in ids or not 0<=ident<10:return None
            ids.add(ident)
            for slot in filter(None,row.get('2A6fYiEC','').split(',')):
                pieces=slot.split(':')
                if len(pieces)!=3 or pieces[0]!='1' or pieces[2] not in known:return None
        db.execute('CREATE TABLE IF NOT EXISTS party_decks (deck_id INTEGER PRIMARY KEY, name TEXT NOT NULL, members TEXT NOT NULL)')
        for row in rows:
            db.execute('INSERT OR REPLACE INTO party_decks VALUES (?,?,?)',
                       (int(row['r21y0YzS']),row.get('G4L0YIB2',''),row.get('2A6fYiEC','')))
    return {'5Eb0Rig6':player_packets(database)['5Eb0Rig6']}
