import json,unittest
from pathlib import Path
from story_policy import effective_mission,story_worlds
from battles import start_tutorial,tutorial_missions

class StoryPlaceholderTests(unittest.TestCase):
 def test_every_zero_wave_story_row_has_consistent_reversible_standin(self):
  root=Path(__file__).resolve().parents[1]
  rows=list(map(json.loads,next((root/'assets/decoded/mst').glob('F_MISSION_MST-*')).read_text(encoding='utf-8').splitlines()))
  changed=[]
  for row in rows:
   if row['9Pb24aSy'] not in story_worlds() or row['8xi6Xvyk']!='0':continue
   before=dict(row);patched=effective_mission(row);changed.append(row['qo3PECw6'])
   self.assertEqual(row,before)
   self.assertEqual(patched['dIPkNn61'],row['dIPkNn61'])
   self.assertEqual(patched['juA0Z4m7'],row['juA0Z4m7'])
   self.assertEqual(patched['Y4VoF8yu'],'1')
   self.assertEqual(patched['8xi6Xvyk'],'1')
   result=start_tutorial({'jQsE54Iz':[{'qo3PECw6':row['qo3PECw6']}]})
   self.assertEqual(len(result['an6TB4WS']),1)
   self.assertEqual(result['an6TB4WS'][0]['DYTx1Is3'],'100022')
  self.assertEqual(len(changed),132)
  self.assertEqual(len(tutorial_missions()),2732)

if __name__=='__main__':unittest.main()
