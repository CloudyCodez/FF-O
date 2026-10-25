import unittest,tempfile,sqlite3
from pathlib import Path
from contextlib import closing
from mailbox import packets,claim,NIER

class MailTests(unittest.TestCase):
 def test_claim_all_is_persistent_and_retry_safe(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'player.db';before=packets(path)
   self.assertEqual(len(before['qja26wHb']),8)
   request={'rStH7od8':[{'Qe02W7rX':','.join(r['ynP26rjD']+':2' for r in before['qja26wHb'])}]}
   first=claim(request,path);second=claim(request,path)
   self.assertEqual(first,second)
   self.assertEqual({int(u['3HriTp6B']) for u in first['B71MekS8']},{u for u,_ in NIER})
   with closing(sqlite3.connect(path)) as db:self.assertEqual(db.execute('SELECT count(*) FROM units').fetchone()[0],10)
   self.assertTrue(all(r['14Y7jihw']=='2' for r in packets(path)['qja26wHb']))
 def test_unknown_id_does_not_partially_grant(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'player.db';packets(path)
   with self.assertRaises(ValueError):claim({'rStH7od8':[{'Qe02W7rX':'900100,1'}]},path)
   self.assertTrue(all(r['14Y7jihw']=='0' for r in packets(path)['qja26wHb']))
