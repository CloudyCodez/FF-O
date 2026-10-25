import sqlite3,tempfile,unittest
from pathlib import Path
from switches import switch_packets
from units import inventory,player_packets
from economy import TEST_BALANCE,currency_packets,debit_for_test

class PlayerStateTests(unittest.TestCase):
 def test_switch_snapshot_survives_restart_and_uses_native_hex_bits(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'player.sqlite3'
   expected=switch_packets({'0jqUZuT1':[{'dIPkNn61':'10000140,90001838'}]},path)
   self.assertEqual(expected,switch_packets(database=path))
   rows={int(r['5opcUT9t']):r['juA0Z4m7'] for r in expected['8J1R5PXG']}
   self.assertEqual(rows[10][96//4],'8')
   self.assertEqual(rows[9000][9842//4],'2')
   self.assertEqual(set(rows[10]),{'0','8'})
 def test_unknown_switch_does_not_modify_save(self):
  with tempfile.TemporaryDirectory() as folder:
   with self.assertRaises(ValueError):switch_packets({'0jqUZuT1':[{'dIPkNn61':'-1'}]},Path(folder)/'p.db')
 def test_owned_starters_are_stable_across_reloads(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'p.db'
   first=inventory(path)
   self.assertEqual(first,inventory(path))
   self.assertEqual([r['3HriTp6B'] for r in first],['100000102','100000202'])
   self.assertEqual(len({r['og2GHy49'] for r in first}),2)
 def test_test_spending_refills_without_overflow(self):
  self.assertEqual(debit_for_test(TEST_BALANCE,5000),TEST_BALANCE)
  self.assertLess(TEST_BALANCE,2**31)
  with self.assertRaises(ValueError):debit_for_test(TEST_BALANCE,-1)
  self.assertEqual(currency_packets()['J3pAG0I5'][0]['cb3WmiD0'],str(TEST_BALANCE))
 def test_party_pages_have_records_even_when_empty(self):
  with tempfile.TemporaryDirectory() as folder:
   packets=player_packets(Path(folder)/'p.db')
   decks=packets['5Eb0Rig6']
   self.assertEqual([int(r['r21y0YzS']) for r in decks],list(range(10)))
   self.assertEqual(decks[0]['2A6fYiEC'],'')
   self.assertEqual(decks[1]['2A6fYiEC'],'1:0:1,1:1:2')

if __name__=='__main__':unittest.main()
