import tempfile,unittest
from pathlib import Path
import vortex
from battles import start_tutorial,finish_tutorial

class VortexTests(unittest.TestCase):
 def test_dynamic_listing_covers_every_recovered_event_area_and_dungeon(self):
  missions=vortex.missions();rows=vortex.packets()['0xkoNP8U']
  self.assertEqual(len(missions),14612)
  self.assertEqual({r['uv60hgDW'] for r in rows if r['U9iHsau3']=='0'},
                   {r['uv60hgDW'] for r in missions.values()})
  self.assertEqual({r['U9iHsau3'] for r in rows if r['U9iHsau3']!='0'},
                   {r['U9iHsau3'] for r in missions.values()})
  self.assertTrue(all(r['VjJQ51uG']<'2026' and r['m8ivD4NX']>'2030' for r in rows))

 def test_each_event_has_bounded_placeholder_battle_contract(self):
  for mission,master in vortex.missions().items():
   result=start_tutorial({'jQsE54Iz':[{'qo3PECw6':mission}]})
   self.assertTrue(1<=len(result['an6TB4WS'])<=8)
   self.assertTrue(result['bV34YIJQ'])
   self.assertEqual(master['DYTx1Is3'],'100022')

 def test_event_clear_saves_and_retries_without_duplicate_rewards(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'p.db';mission='2110001'
   payload={'jQsE54Iz':[{'qo3PECw6':mission}],'09HRWXDf':[{}]}
   result=finish_tutorial(payload,path)
   self.assertEqual(result,finish_tutorial(payload,path))
