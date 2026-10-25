import unittest,tempfile,sqlite3
from pathlib import Path
from contextlib import closing
from battles import start_tutorial,finish_tutorial

class TutorialContractTests(unittest.TestCase):
 def test_latius_stages_have_distinct_species_and_native_resource_references(self):
  import json
  from battles import FORMATIONS,ENEMIES,tutorial_missions
  root=Path(__file__).resolve().parents[1]
  dictionaries={r['V9j8wJcC'] for r in map(json.loads,next((root/'assets/decoded/mst').glob('F_MONSTER_DICTIONARY_MST-*')).read_text(encoding='utf-8').splitlines())}
  skills={r['A5x02C6a'] for r in map(json.loads,next((root/'assets/decoded/mst').glob('F_MONSTER_SKILL_SET_MST-*')).read_text(encoding='utf-8').splitlines())}
  for mission in ('1110201','1110202','1110203'):
   formations=FORMATIONS[mission]
   result=start_tutorial({'jQsE54Iz':[{'qo3PECw6':mission}]})
   self.assertEqual(len(result['an6TB4WS']),int(tutorial_missions()[mission]['8xi6Xvyk']))
   self.assertEqual(len(result['y35YvQjZ']),sum(map(len,formations)))
   self.assertTrue(all(r['DYTx1Is3']=='100031' for r in result['an6TB4WS']))
   for row in result['wbet57nF']:self.assertIn(row['V9j8wJcC'],dictionaries)
   for row in result['bV34YIJQ']:self.assertTrue(row['A5x02C6a'] in skills,row['A5x02C6a'])
  south=start_tutorial({'jQsE54Iz':[{'qo3PECw6':'1110203'}]})
  final=[r for r in south['y35YvQjZ'] if r['6v7y3QcJ']=='3']
  self.assertEqual([r['xqartN26'] for r in final],['311001000','111031000','111031000','111031000'])
 def test_opening_has_two_battles_and_matching_monster_parts(self):
  data=start_tutorial({'jQsE54Iz':[{'qo3PECw6':'1110100'}]})
  self.assertEqual([r['6v7y3QcJ'] for r in data['an6TB4WS']],['1','2'])
  parts={(r['xqartN26'],r['6Yc4RkdM']) for r in data['bV34YIJQ']}
  for row in data['y35YvQjZ']:
   self.assertIn((row['xqartN26'],row['6Yc4RkdM']),parts)
  self.assertEqual(len(data['y35YvQjZ']),4)
  self.assertEqual(len(data['Bi6hVv34']),4)
  self.assertTrue(all(r['MxLFKZ13']!='0,0' for r in data['Bi6hVv34']))
 def test_other_missions_remain_explicitly_unimplemented(self):
  self.assertIsNone(start_tutorial({'jQsE54Iz':[{'qo3PECw6':'9999999'}]}))
 def test_earth_shrine_uses_recovered_wave_counts_and_background(self):
  for mission,count in [('1110101',2),('1110103',3)]:
   data=start_tutorial({'jQsE54Iz':[{'qo3PECw6':mission}]})
   self.assertEqual(len(data['an6TB4WS']),count)
   self.assertTrue(all(r['qo3PECw6']==mission and r['DYTx1Is3']=='100022'
                       for r in data['an6TB4WS']))
 def test_earth_shrine_clear_sets_its_own_flag_and_rewards(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'p.db'
   result=finish_tutorial({'jQsE54Iz':[{'qo3PECw6':'1110101'}],
                           '09HRWXDf':[{'Wdi3MAs2':'20'}]},path)
   self.assertEqual(result['09HRWXDf'][0]['kcb0tsM6'],'10')
   self.assertEqual(result['09HRWXDf'][0]['16LQuC5r'],'12')
   self.assertIn('Qic38SuC',result['09HRWXDf'][0])
   with closing(sqlite3.connect(path)) as db:
    self.assertIsNotNone(db.execute('SELECT id FROM story_switches WHERE id=10002100').fetchone())
    self.assertIsNone(db.execute('SELECT id FROM story_switches WHERE id=10002200').fetchone())
 def test_completion_retry_does_not_duplicate_result(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'p.db'
   payload={'jQsE54Iz':[{'qo3PECw6':'1110100'}],'09HRWXDf':[{'Wdi3MAs2':'20'}]}
   self.assertEqual(finish_tutorial(payload,path),finish_tutorial(payload,path))
   db=sqlite3.connect(path)
   try:
    self.assertEqual(db.execute('SELECT COUNT(*) FROM mission_results').fetchone()[0],1)
    self.assertIsNone(db.execute('SELECT id FROM story_switches WHERE id=10003001').fetchone())
   finally:db.close()

if __name__=='__main__':unittest.main()
