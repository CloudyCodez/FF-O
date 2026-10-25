"""Native summon grants. Tutorial summon is a persistent, one-time grant."""
import sqlite3,secrets
from contextlib import closing
from accounts import DEFAULT_DB
from economy import currency_packets
from switches import switch_packets
from units import initialize,serialize,masters
from banners import entry_packets,COLLAB_BANNER_ID
import vision_cards


def is_collaboration(unit):
    # Recovered series IDs distinguish non-FF collaborations (200xx), guest
    # performers (900xx), and the separate War of the Visions series (11010).
    # Unit-number ranges cannot do this: global-exclusive IDs mix all series.
    series=int(unit['taQ69cIx'])
    return series==11010 or 20000<=series<30000 or 90000<=series<100000


def summon_pool(banner_id=None):
    """Recovered base-form summon units for the explicitly local test pool.

    Historical banner rates and pools are not represented by this catalog yet.
    """
    candidates=tuple(ident for ident, row in masters().items()
                 if row['UbSL8C7i'] == '2' and row['woghJa61'] == str(ident)
                 and int(row['9fW0TePj']) >= 3)
    if banner_id is None:return candidates
    if str(banner_id)==str(COLLAB_BANNER_ID):
        return tuple(i for i in candidates if is_collaboration(masters()[i]))
    return tuple(i for i in candidates if not is_collaboration(masters()[i])
                 and (str(banner_id)!='1' or int(masters()[i]['9fW0TePj'])>=5))


def regular_summon(row,database):
    detail=next((item for item in entry_packets()['IC0ueV5s']
                 if item['X1IuZnj2']==str(row.get('X1IuZnj2'))
                 and item['nqzG3b2v']==str(row.get('nqzG3b2v'))),None)
    if detail is None:return None
    count=int(row.get('2RtVPS3b',1))
    maximum=int(detail['0GgK6ytT'].split(':')[3])
    if count not in (1,10) or count>maximum:raise ValueError('Invalid summon count')
    pool=summon_pool(detail['X1IuZnj2'])
    if not pool:raise ValueError('Recovered summon pool is empty')
    with closing(sqlite3.connect(database,timeout=10)) as db,db:
        initialize(db)
        granted=[]
        cards=[]
        for _ in range(count):
            ident=secrets.choice(pool)
            uid=db.execute('INSERT INTO units (unit_id) VALUES (?)',(ident,)).lastrowid
            granted.append(serialize((uid,ident,1)))
            card=vision_cards.grant_for_unit(db,masters()[ident])
            if card:cards.append(card)
    maximum_rare=max(int(masters()[int(u['3HriTp6B'])]['9fW0TePj']) for u in granted)
    # This field is an animation-pattern ID, not a rarity. These recovered
    # patterns use direct blue/gold/rainbow/NV reveals without a fake upgrade.
    pattern='35' if cards else ('32' if maximum_rare>=5 else '30' if maximum_rare==4 else '29')
    result={'X1IuZnj2':detail['X1IuZnj2'],'nqzG3b2v':detail['nqzG3b2v'],
            '2RtVPS3b':str(count),'zJ1A6HXm':'0',
            '3HriTp6B':granted[0]['3HriTp6B'],
            'UJz5QED2':','.join(f"10:{unit['3HriTp6B']}:{unit['og2GHy49']}:1" for unit in granted),
            'zoU5J3Kq':pattern,
            'uR70J6Lr':'','yV45kbjw':'',
            'eb2ANT1m':','.join(f"27:{card['5giCMUd2']}:{card['gXb32xzQ']}:1" for card in cards),
            '8schfem9':','.join(f"{card['gXb32xzQ']}:39" for card in cards),
            'oY0vAuE9':'9999'}
    return {**currency_packets(),'B71MekS8':granted,'2Xi0wuGA':cards,'5yLD4dYI':[result]}

def summon(payload,database=DEFAULT_DB):
    rows=payload.get('5yLD4dYI',[])
    if len(rows)!=1:raise ValueError('Expected one summon request')
    row=rows[0]
    if (str(row.get('X1IuZnj2')),str(row.get('nqzG3b2v')))!=('0','0'):
        return regular_summon(row,database)
    with closing(sqlite3.connect(database,timeout=10)) as db,db:
        initialize(db)
        db.execute('CREATE TABLE IF NOT EXISTS tutorial_summon (id INTEGER PRIMARY KEY CHECK(id=1), uid INTEGER NOT NULL REFERENCES units(uid))')
        found=db.execute('SELECT uid FROM tutorial_summon WHERE id=1').fetchone()
        if found:uid=found[0]
        else:
            uid=db.execute('INSERT INTO units (unit_id) VALUES (100000303)').lastrowid
            db.execute('INSERT INTO tutorial_summon VALUES (1,?)',(uid,))
        unit=serialize(db.execute('SELECT uid,unit_id,level,exp FROM units WHERE uid=?',(uid,)).fetchone())
    # Native UserGachaResult uses comma-separated type:master:owned-uid entries.
    # Type 10 identifies a unit; 1 is a different reward category.
    result={'X1IuZnj2':'0','nqzG3b2v':'0','2RtVPS3b':'1','zJ1A6HXm':'0',
            '3HriTp6B':unit['3HriTp6B'],'UJz5QED2':f"10:{unit['3HriTp6B']}:{uid}:1",
            'zoU5J3Kq':'4','uR70J6Lr':'','yV45kbjw':'','eb2ANT1m':'',
            '8schfem9':'','oY0vAuE9':'9999'}
    # Owner requested removal of guided menu gates after the tutorial battles.
    switches=switch_packets({'0jqUZuT1':[{'dIPkNn61':'10003001'}]},database)
    return {**currency_packets(),**switches,'B71MekS8':[unit],'5yLD4dYI':[result]}
