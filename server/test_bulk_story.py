import json,tempfile,unittest
from pathlib import Path
from battles import tutorial_missions,start_tutorial,finish_tutorial,AUTHORED_MISSIONS,FORMATIONS
import sqlite3
from contextlib import closing

class BulkStoryTests(unittest.TestCase):
 def test_all_ordinary_story_battles_have_complete_native_wave_contracts(self):
  missions=tutorial_missions()
  self.assertEqual(len(missions),2732)
  worlds=set()
  for mission,master in missions.items():
   with self.subTest(mission=mission):
    worlds.add(master['9Pb24aSy'])
    result=start_tutorial({'jQsE54Iz':[{'qo3PECw6':mission}]})
    self.assertEqual(len(result['an6TB4WS']),int(master['8xi6Xvyk']))
    self.assertTrue(result['y35YvQjZ'])
    self.assertEqual(len(result['y35YvQjZ']),len(result['Bi6hVv34']))
    parts={r['xqartN26'] for r in result['bV34YIJQ']}
    self.assertTrue(all(r['xqartN26'] in parts for r in result['y35YvQjZ']))
    self.assertTrue(all(r['DYTx1Is3']==master['DYTx1Is3'] for r in result['an6TB4WS']))
  self.assertEqual(worlds,{'1','3','4','5','6'})

 def test_authored_encounters_override_placeholder_catalog(self):
  self.assertEqual(len(AUTHORED_MISSIONS),77)
  self.assertEqual(FORMATIONS['1110404'],(('siren',),))
  self.assertEqual(FORMATIONS['1120204'][-1],('ochu','kochu','kochu'))

 def test_later_world_clear_rewards_and_receipts(self):
  missions=tutorial_missions()
  selected=[max((m for m,r in missions.items() if r['9Pb24aSy']==world),key=int)
            for world in ('1','3','4','5','6')]
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'p.db'
   for mission in selected:
    payload={'jQsE54Iz':[{'qo3PECw6':mission}],'09HRWXDf':[{}]}
    response=finish_tutorial(payload,path)
    self.assertEqual(response['09HRWXDf'][0]['kcb0tsM6'],missions[mission]['B6H34Mea'])
    self.assertEqual(response,finish_tutorial(payload,path))

 def test_explorations_events_and_unknown_stages_are_not_misclassified(self):
  for mission in ('99999999','6110101'):
   self.assertIsNone(start_tutorial({'jQsE54Iz':[{'qo3PECw6':mission}]}))

 def test_every_supported_story_clear_saves_without_contract_failure(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'all-story.db'
   for mission,master in tutorial_missions().items():
    with self.subTest(mission=mission):
     payload={'jQsE54Iz':[{'qo3PECw6':mission}],'09HRWXDf':[{}]}
     result=finish_tutorial(payload,path)
     self.assertEqual(result['09HRWXDf'][0]['kcb0tsM6'],master['B6H34Mea'])
   with closing(sqlite3.connect(path)) as db:
    self.assertEqual(db.execute('SELECT COUNT(DISTINCT mission) FROM mission_results').fetchone()[0],2732)

if __name__=='__main__':unittest.main()
