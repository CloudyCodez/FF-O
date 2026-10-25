import unittest,tempfile,sqlite3
from pathlib import Path
from challenges import packets
from battles import finish_tutorial

class CompletionChallengesTests(unittest.TestCase):
 def test_completion_persists_without_claiming_other_achievements(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'test.db'
   self.assertEqual(packets(path),{'TQ5AJd2K':[]})
   payload={'jQsE54Iz':[{'qo3PECw6':'1110201'}],'09HRWXDf':[{'Wdi3MAs2':'35'}]}
   result=finish_tutorial(payload,path)
   expected=[{'qo3PECw6':'1110201','qdhWF7z9':'11102010','wf5Toh4k':''}]
   self.assertEqual(result['TQ5AJd2K'],expected)
   self.assertEqual(packets(path)['TQ5AJd2K'],expected)
   self.assertEqual(finish_tutorial(payload,path)['TQ5AJd2K'],expected)
