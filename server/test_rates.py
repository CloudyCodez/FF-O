import unittest,re
from rates import page
from summons import summon_pool
from banners import COLLAB_BANNER_ID

class RatesTests(unittest.TestCase):
 def test_each_banner_lists_exact_draw_pool(self):
  for banner in (1,2,COLLAB_BANNER_ID):
   html=page(banner).decode()
   ids={int(x) for x in re.findall(r'<tr><td>(\d+)</td><td>',html)}
   self.assertEqual(ids,set(summon_pool(banner)))
   self.assertIn(f'{100/len(ids):.8f}%',html)
 def test_unknown_banner_rejected(self):
  with self.assertRaises(ValueError):page(98765)
