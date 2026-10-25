import tempfile,unittest,sqlite3
from pathlib import Path
from contextlib import closing
import espers
from battles import begin_mission,finish_tutorial

class EsperTests(unittest.TestCase):
 def test_ifrit_acquisition_and_siren_upgrade_follow_cleared_trials(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'p.db'
   with closing(sqlite3.connect(path)) as db,db:
    db.execute('CREATE TABLE story_switches (id INTEGER PRIMARY KEY)')
    db.executemany('INSERT INTO story_switches VALUES (?)',[(82002100,),(82001200,)])
   owned={r['Iwfx42Wo']:r for r in espers.packets(path)['gP9TW2Bf']}
   self.assertEqual(owned['2']['9fW0TePj'],'1')
   self.assertEqual(owned['1']['9fW0TePj'],'2')
   self.assertEqual(espers.packets(path)['gP9TW2Bf'],list(owned.values()))
 def test_fresh_profile_does_not_receive_siren(self):
  with tempfile.TemporaryDirectory() as folder:
   self.assertEqual(espers.packets(Path(folder)/'p.db'),{'gP9TW2Bf':[]})

 def test_siren_clear_persists_exactly_one_native_record(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'p.db';start={'jQsE54Iz':[{'qo3PECw6':'1110404'}]}
   begin_mission(start,path)
   end={**start,'09HRWXDf':[{'Wdi3MAs2':'25'}]}
   response=finish_tutorial(end,path)
   self.assertEqual(response['gP9TW2Bf'][0]['Iwfx42Wo'],'1')
   self.assertEqual(response['gP9TW2Bf'][0]['fh31sk7B'],'1500')
   self.assertEqual(espers.packets(path)['gP9TW2Bf'],response['gP9TW2Bf'])
   begin_mission(start,path);finish_tutorial(end,path)
   self.assertEqual(len(espers.packets(path)['gP9TW2Bf']),1)

 def test_previous_siren_clear_migrates_without_advancing_story(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'p.db'
   with closing(sqlite3.connect(path)) as db,db:
    db.execute('CREATE TABLE story_switches (id INTEGER PRIMARY KEY)')
    db.execute('INSERT INTO story_switches VALUES (82001100)')
   self.assertEqual(len(espers.packets(path)['gP9TW2Bf']),1)
   with closing(sqlite3.connect(path)) as db:
    self.assertEqual(db.execute('SELECT id FROM story_switches').fetchall(),[(82001100,)])

if __name__=='__main__':unittest.main()
