import time,unittest
from home import packets


class HomeContractTests(unittest.TestCase):
    def test_world_entry_has_enabled_native_badge_and_refresh_deadline(self):
        row=packets()['xS3CA5LN'][0]
        self.assertGreater(int(row['0Zpuzj7E']),time.time())
        parts=row['merqbE18'].split(':')
        self.assertEqual(parts[0],'HOME_MAINMENU_WORLD_ICON')
        self.assertTrue(parts[2].endswith('/ffo_world.png'))
        self.assertEqual(parts[3:5],['1','1'])
        self.assertEqual(len(parts),7)
