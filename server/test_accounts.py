import tempfile,unittest
from pathlib import Path
from accounts import guest
class AccountTests(unittest.TestCase):
 def test_guest_survives_restart_and_has_local_credentials(self):
  with tempfile.TemporaryDirectory() as directory:
   db=Path(directory)/'players.sqlite3';first=guest(db);second=guest(db)
   self.assertEqual(first,second);self.assertEqual(first['9Tbns0eI'],'100000001')
   self.assertGreater(len(first['JC61TPqS']),20)
 def test_separate_installations_do_not_share_passwords(self):
  with tempfile.TemporaryDirectory() as directory:
   a=guest(Path(directory)/'a.db');b=guest(Path(directory)/'b.db')
   self.assertNotEqual(a['JC61TPqS'],b['JC61TPqS'])
