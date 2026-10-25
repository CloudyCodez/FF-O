import unittest
from startup import dispatch

class StoreRefreshTests(unittest.TestCase):
 def test_optional_store_check_has_explicit_empty_schedule(self):
  self.assertEqual(dispatch('VariableStoreCheckRequest',{}),{'3VS1Bhmf':[]})
 def test_unknown_store_mutation_remains_unimplemented(self):
  self.assertIsNone(dispatch('VariableStorePurchaseUnknown',{}))
