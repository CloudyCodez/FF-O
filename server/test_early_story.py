import json,tempfile,unittest,sqlite3
from pathlib import Path
from contextlib import closing
from battles import start_tutorial,finish_tutorial,tutorial_missions,ENEMIES
from early_encounters import FORMATIONS
ROOT=Path(__file__).resolve().parents[1]

class EarlyStoryTests(unittest.TestCase):
 def test_all_new_stages_have_native_resources_and_exact_master_wave_counts(self):
  def records(name):
   return map(json.loads,next((ROOT/'assets/decoded/mst').glob(name+'-*')).read_text(encoding='utf-8').splitlines())
  dictionaries={r['V9j8wJcC'] for r in records('F_MONSTER_DICTIONARY_MST')}
  skills={r['A5x02C6a'] for r in records('F_MONSTER_SKILL_SET_MST')}
  self.assertEqual(len(tutorial_missions()),2732)
  for mission,formations in FORMATIONS.items():
   with self.subTest(mission=mission):
    master=tutorial_missions()[mission];result=start_tutorial({'jQsE54Iz':[{'qo3PECw6':mission}]})
    self.assertEqual(len(formations),int(master['8xi6Xvyk']))
    self.assertEqual(len(result['an6TB4WS']),len(formations))
    self.assertTrue(all(r['DYTx1Is3']==master['DYTx1Is3'] for r in result['an6TB4WS']))
    for species in set(s for wave in formations for s in wave):
     enemy=ENEMIES[species];self.assertIn(enemy[0],skills);self.assertIn(enemy[1],dictionaries)
    self.assertEqual(len(result['y35YvQjZ']),sum(map(len,formations)))
    keys=[(r['2fY1IomW'],r['Z0EN6jSh']) for r in result['Bi6hVv34']]
    self.assertEqual(len(keys),len(set(keys)))
 def test_stage_completion_rewards_and_switches_stay_mission_specific(self):
  with tempfile.TemporaryDirectory() as folder:
   database=Path(folder)/'p.db'
   for mission in FORMATIONS:
    master=tutorial_missions()[mission]
    payload={'jQsE54Iz':[{'qo3PECw6':mission}],'09HRWXDf':[{'Wdi3MAs2':'20'}]}
    result=finish_tutorial(payload,database)
    self.assertEqual(result['09HRWXDf'][0]['kcb0tsM6'],master['B6H34Mea'])
    self.assertEqual(result['09HRWXDf'][0]['16LQuC5r'],master['7UR4J2SE'])
    self.assertEqual(result,finish_tutorial(payload,database))
    with closing(sqlite3.connect(database)) as db:
     for flag in master['dIPkNn61'].split(','):
      self.assertIsNotNone(db.execute('SELECT id FROM story_switches WHERE id=?',(int(flag),)).fetchone())
   with closing(sqlite3.connect(database)) as db:
    self.assertEqual(db.execute('SELECT COUNT(*) FROM mission_results').fetchone()[0],19)

 def test_siren_boss_is_separate_from_tower_floors_and_optional_trials(self):
  self.assertEqual(FORMATIONS['1110404'],(('siren',),))
  master=tutorial_missions()['1110404']
  self.assertEqual(master['juA0Z4m7'],'10007300')
  self.assertEqual(set(master['dIPkNn61'].split(',')),{'10007400','82001100'})
  self.assertIn('1110405',tutorial_missions())
  result=start_tutorial({'jQsE54Iz':[{'qo3PECw6':'1110404'}]})
  self.assertEqual(len(result['y35YvQjZ']),1)
  self.assertEqual(result['wbet57nF'][0]['G4L0YIB2'],'Siren')
