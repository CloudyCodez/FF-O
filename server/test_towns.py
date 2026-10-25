import tempfile,unittest,sqlite3
from pathlib import Path
from contextlib import closing
from towns import handle
from towns import supported_towns

class TownTests(unittest.TestCase):
 def test_available_town_routes_are_native_master_ids(self):
  import json
  root=Path(__file__).resolve().parents[1]
  known={r['Gh92V3Tx'] for r in map(json.loads,next((root/'assets/decoded/mst').glob('F_TOWN_MST-*')).read_text(encoding='utf-8').splitlines())}
  self.assertTrue(supported_towns().issubset(known))
  self.assertTrue({'1101','1102','9001'}.issubset(supported_towns()))
 def test_entry_and_story_update_persist_without_completing_sidequests(self):
  with tempfile.TemporaryDirectory() as folder:
   database=Path(folder)/'p.db'
   self.assertEqual(handle('TownInRequest',{'JcxS6A8N':[{'Gh92V3Tx':'1101'}]},database)['8J1R5PXG'],[])
   result=handle('TownUpdateRequest',{'JcxS6A8N':[{'Gh92V3Tx':'1101','dIPkNn61':'10004003'}]},database)
   self.assertTrue(result['8J1R5PXG'])
   self.assertEqual(handle('TownOutRequest',{'JcxS6A8N':[{'Gh92V3Tx':'1101'}]},database),result)
   with closing(sqlite3.connect(database)) as db:self.assertEqual(db.execute('SELECT id FROM story_switches').fetchall(),[(10004003,)])
 def test_unrestored_towns_and_reward_mutations_are_not_silently_acknowledged(self):
  for payload in [{'JcxS6A8N':[{'Gh92V3Tx':'9999'}]}, {'JcxS6A8N':[{'Gh92V3Tx':'1101','NiG2wL3A':'1:1'}]}]:
   self.assertIsNone(handle('TownUpdateRequest',payload))

 def test_grandshelt_entry_does_not_complete_its_story(self):
  with tempfile.TemporaryDirectory() as folder:
   database=Path(folder)/'p.db'
   result=handle('TownInRequest',{'JcxS6A8N':[{'Gh92V3Tx':'1102'}]},database)
   self.assertEqual(result['8J1R5PXG'],[])
   with self.assertRaises(ValueError):
    handle('TownInRequest',{'JcxS6A8N':[{'Gh92V3Tx':'1102','dIPkNn61':'10011001'}]},database)
   result=handle('TownUpdateRequest',{'JcxS6A8N':[{'Gh92V3Tx':'1102','dIPkNn61':'10011001'}]},database)
   self.assertTrue(result['8J1R5PXG'])
