"""Native tutorial encounter reconstruction; historical server stats are unavailable.

The opening uses the recovered Steel Bat model and skill set. Balance values
below are provisional until the original encounter payload is recovered.
"""
from economy import currency_packets
import sqlite3,json,hashlib,time
from contextlib import closing
from accounts import DEFAULT_DB
from switches import switch_packets
from pathlib import Path
from functools import lru_cache
from challenges import packets as challenge_packets
from switches import packets_on_connection as saved_switches
from challenges import packets_on_connection as saved_challenges
import units
import espers
from story_policy import effective_mission
import vortex

# Explicit early-story encounters. Species/resources are recovered native data;
# formation selection and combat balance are provisional offline reconstruction.
# Never use this as an automatic fallback for unknown story/event missions.
ENEMIES={
 'bat':('102001000','1020010','Steel Bat',50,10),
 'goblin':('105001000','1050010','Goblin',156,15),
 'hornet':('109001100','1090011','Hornet',130,15),
 'nuts':('101011000','1010110','Nutkin',143,10),
 'mantis':('209001000','2090010','Killer Mantis',900,30),
 'kochu':('111031000','1110310','Kochu',208,10),
 'ochu':('311001000','3110010','Ochu',2400,30),
}
FORMATIONS={
 '1110201':(('goblin','hornet'),('nuts','hornet'),('goblin','nuts','hornet')),
 '1110202':(('hornet','nuts'),('goblin','hornet'),('mantis',)),
 '1110203':(('goblin','nuts'),('hornet','kochu'),('ochu','kochu','kochu','kochu')),
}
from early_encounters import ENEMIES as MORE_ENEMIES,FORMATIONS as MORE_FORMATIONS
ENEMIES.update(MORE_ENEMIES)
FORMATIONS.update(MORE_FORMATIONS)
from lanzelt_encounters import FORMATIONS as LANZELT_FORMATIONS
FORMATIONS.update(LANZELT_FORMATIONS)
AUTHORED_MISSIONS=frozenset({'1110100','1110101','1110103',*FORMATIONS})
_catalog_path=Path(__file__).resolve().parent/'data/story-battles.json'
if _catalog_path.exists():
    _catalog=json.loads(_catalog_path.read_text(encoding='utf-8'))
    if _catalog.get('mode')!='provisional-test-encounters':
        raise ValueError('Unknown story battle catalog mode')
    for _mission,_entry in _catalog['missions'].items():
        FORMATIONS.setdefault(_mission,tuple(tuple(w) for w in _entry['waves']))

@lru_cache(maxsize=1)
def tutorial_missions():
    path=next((Path(__file__).resolve().parents[1]/'assets/decoded/mst').glob('F_MISSION_MST-*.txt'))
    return {r['qo3PECw6']:effective_mission(r) for r in map(json.loads,path.read_text(encoding='utf-8').splitlines())
            if r['qo3PECw6'] in {'1110100','1110101','1110103',*FORMATIONS}}

@lru_cache(maxsize=1)
def mission_catalog():
    return {**tutorial_missions(),**vortex.missions()}

def start_tutorial(payload):
    rows=payload.get('jQsE54Iz',[])
    if len(rows)!=1 or rows[0].get('qo3PECw6') not in mission_catalog():
        return None
    mission=rows[0]['qo3PECw6'];master=mission_catalog()[mission]
    phases=[];waves=[];groups=[];parts={};names={}
    for wave in range(1,int(master['8xi6Xvyk'])+1):
        phases.append({'qo3PECw6':mission,'6v7y3QcJ':str(wave),'gou39JeI':'2',
                       'DYTx1Is3':master['DYTx1Is3'],'2fY1IomW':str(wave),'T03qgLWA':'1',
                       'i2ar9yXM':'0','5LZN8C9I':'0','J9gafF0t':'0'})
        formation=FORMATIONS.get(mission,(('bat','bat'),)*int(master['8xi6Xvyk']))[wave-1]
        for order,species in enumerate(formation):
            ident,dictionary,name,hp,mp=ENEMIES[species]
            # Explicit compact grid keeps small mobs and the boss within the
            # same native enemy half of the screen.
            x,y=((125,230) if len(formation)==1 else
                 ((85,200),(185,245),(90,290),(185,330),(90,365))[order])
            groups.append({'2fY1IomW':str(wave),'xqartN26':ident,
                           'Z0EN6jSh':str(order),'MxLFKZ13':f'{x},{y}','WJdBp9f0':'1',
                           '3t7pZM5V':'0','m9BvFk2X':'0'})
            waves.append({'qo3PECw6':mission,'6v7y3QcJ':str(wave),'pIHCrf40':str(wave),
                          '2fY1IomW':str(wave),'xqartN26':ident,'Z0EN6jSh':str(order),
                          '6Yc4RkdM':'0'})
            parts[ident]={'xqartN26':ident,'6Yc4RkdM':'0','G4L0YIB2':name,
             'fh31sk7B':str(hp),'PC97pWQj':str(mp),'9NBV1XCS':'5','Pn5w9dfh':'5',
             '84FJM3PD':'5','T8xMDAZ4':'5','B6H34Mea':'0','7UR4J2SE':'5',
             'A5x02C6a':ident,'8a6gAwN9':'1','7wV3QZ80':'1',
             'hn42BL3Q':'0,0,0,0,0,0,0,0','D9Nb7jgd':'0,0,0,0,0,0,0,0'}
            names[ident]={'xqartN26':ident,'V9j8wJcC':dictionary,'G4L0YIB2':name}
    return {**currency_packets(),'an6TB4WS':phases,'y35YvQjZ':waves,'Bi6hVv34':groups,
            'wbet57nF':list(names.values()),'bV34YIJQ':list(parts.values())}

def initialize_runs(db):
    db.execute('CREATE TABLE IF NOT EXISTS battle_runs (id INTEGER PRIMARY KEY, mission TEXT NOT NULL, party TEXT NOT NULL, response TEXT, digest TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS mission_results (mission INTEGER, digest TEXT, result TEXT NOT NULL, completed INTEGER NOT NULL, PRIMARY KEY(mission,digest))')

def begin_mission(payload,database=DEFAULT_DB):
    response=start_tutorial(payload)
    if response is None:return None
    mission=payload['jQsE54Iz'][0]['qo3PECw6']
    with closing(sqlite3.connect(database,timeout=10)) as db,db:
        db.execute('BEGIN IMMEDIATE')
        initialize_runs(db)
        opened=db.execute('SELECT mission FROM battle_runs WHERE response IS NULL').fetchone()
        if opened and opened[0]!=mission:
            # Leaving a battle must not permanently lock the account. No
            # digest or reward is recorded for the abandoned encounter.
            db.execute("UPDATE battle_runs SET response='{}' WHERE response IS NULL")
            opened=None
        if opened is None:
            party=units.battle_party(db)
            db.execute('INSERT INTO battle_runs (mission,party) VALUES (?,?)',
                       (mission,json.dumps([r[0] for r in party])))
    return response

def finish_tutorial(payload,database=DEFAULT_DB):
    rows=payload.get('jQsE54Iz',[])
    if len(rows)!=1 or rows[0].get('qo3PECw6') not in mission_catalog():return None
    mission=rows[0]['qo3PECw6'];master=mission_catalog()[mission]
    result=payload.get('09HRWXDf',[])
    if not isinstance(result,list) or len(result)!=1 or not isinstance(result[0],dict):
        raise ValueError('Missing battle result')
    for stats in payload.get('nSG9Jb1s',[]):
        if stats.get('NYb0Cri6')=='TOTAL_MISSION_BATTLE_WIN':
            if int(stats.get('6gAX1BpC','0'))<int(master['8xi6Xvyk']):
                raise ValueError('Battle did not clear all required waves')
    # Transport counters/credentials can change when the same clear is retried.
    evidence={key:payload[key] for key in ('jQsE54Iz','09HRWXDf','nSG9Jb1s','2urzfX6d') if key in payload}
    digest=hashlib.sha256(json.dumps(evidence,sort_keys=True).encode()).hexdigest()
    with closing(sqlite3.connect(database,timeout=10)) as db,db:
        db.execute('BEGIN IMMEDIATE')
        initialize_runs(db)
        run=db.execute('SELECT id,mission,party FROM battle_runs WHERE response IS NULL').fetchone()
        if run and run[1]!=mission:raise ValueError('Battle result does not match the active mission')
        if run is None:
            cached=db.execute('SELECT response FROM battle_runs WHERE mission=? AND digest=? AND response IS NOT NULL ORDER BY id DESC LIMIT 1',
                              (mission,digest)).fetchone()
            if cached:return json.loads(cached[0])
            # Accept a single in-flight result from clients started before this migration.
            party=units.battle_party(db)
            ident=db.execute('INSERT INTO battle_runs (mission,party) VALUES (?,?)',
                             (mission,json.dumps([r[0] for r in party]))).lastrowid
            run=(ident,mission,json.dumps([r[0] for r in party]))
        units.initialize(db)
        changed=[];growth=[]
        party=json.loads(run[2])
        share,remainder=divmod(int(master['B6H34Mea']),max(1,len(party)))
        for order,uid in enumerate(party):
            amount=share+(order<remainder)
            before=db.execute('SELECT uid,unit_id,level,exp FROM units WHERE uid=?',(uid,)).fetchone()
            if before is None:raise ValueError('Battle party unit no longer exists')
            after=units.gain_exp(before,amount)
            db.execute('UPDATE units SET level=?,exp=? WHERE uid=?',(after[2],after[3],uid))
            changed.append(units.serialize(after));growth.append(units.level_result(before,after,amount))
        db.execute('INSERT OR IGNORE INTO mission_results VALUES (?,?,?,?)',
                   (int(mission),digest,json.dumps(result),int(time.time())))
        switches=saved_switches(db,{'0jqUZuT1':[{'dIPkNn61':master['dIPkNn61']}]})
        espers.sync_story_acquisitions(db)
        response={**currency_packets(),**switches,**saved_challenges(db),'B71MekS8':changed,
                  **espers.packets_on_connection(db),
                  '09HRWXDf':[{'kcb0tsM6':master['B6H34Mea'],'16LQuC5r':master['7UR4J2SE'],
                               'Qic38SuC':','.join(growth)}]}
        db.execute('UPDATE battle_runs SET digest=?,response=? WHERE id=?',(digest,json.dumps(response),run[0]))
        return response
