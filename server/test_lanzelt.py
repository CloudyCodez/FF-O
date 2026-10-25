import unittest,tempfile,sqlite3
from pathlib import Path
from contextlib import closing
from battles import tutorial_missions,start_tutorial,finish_tutorial,ENEMIES
from lanzelt_encounters import FORMATIONS

class LanzeltTests(unittest.TestCase):
 def test_every_stage_uses_native_wave_count_and_existing_species(self):
  self.assertEqual(len(FORMATIONS),52)
  for mission,waves in FORMATIONS.items():
   with self.subTest(mission=mission):
    master=tutorial_missions()[mission]
    self.assertEqual(master['uv60hgDW'],'112')
    self.assertEqual(master['0VkYZx1a'],'0')
    self.assertEqual(len(waves),int(master['8xi6Xvyk']))
    result=start_tutorial({'jQsE54Iz':[{'qo3PECw6':mission}]})
    self.assertEqual(len(result['y35YvQjZ']),sum(map(len,waves)))
    self.assertTrue(all(r['DYTx1Is3']==master['DYTx1Is3'] for r in result['an6TB4WS']))
    self.assertTrue(all(s in ENEMIES for wave in waves for s in wave))

 def test_every_clear_persists_its_exact_switches_and_retry_receipt(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'test.db'
   for mission in FORMATIONS:
    payload={'jQsE54Iz':[{'qo3PECw6':mission}],'09HRWXDf':[{}]}
    result=finish_tutorial(payload,path)
    self.assertEqual(result,finish_tutorial(payload,path))
    with closing(sqlite3.connect(path)) as db:
     saved={str(r[0]) for r in db.execute('SELECT id FROM story_switches')}
    self.assertTrue(set(tutorial_missions()[mission]['dIPkNn61'].split(','))<=saved)

if __name__=='__main__':unittest.main()
