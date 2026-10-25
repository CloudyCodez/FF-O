import unittest
import struct
from banners import entry_packets, ROOT, COLLAB_BANNER_ID


class BannerContractTests(unittest.TestCase):
    def test_collaboration_offer_is_immediately_below_premium(self):
        schedules={row['X1IuZnj2']:row for row in entry_packets()['4D5k8dpI']}
        collab=str(COLLAB_BANNER_ID)
        self.assertNotEqual(collab,'3')
        self.assertEqual(schedules['1']['w2A76noc'],schedules[collab]['w2A76noc'])
        # The native list sorts display priority descending.
        self.assertEqual(int(schedules[collab]['Z0EN6jSh']),int(schedules['1']['Z0EN6jSh'])-1)
        banners={row['X1IuZnj2']:row for row in entry_packets()['PcUrGH13']}
        self.assertEqual(banners['1']['sx4kyW0i'],banners[collab]['sx4kyW0i'])

    def test_every_banner_has_native_single_and_multi_details(self):
        packets = entry_packets()
        for banner in packets['PcUrGH13']:
            self.assertEqual(banner['7xBNR2MH'], '1')
            self.assertEqual(banner['g38Pjk10'], 'gacha_animation')
            self.assertEqual(banner['JDFMe3A7'], 'mog_rare/anime')
            details = [row for row in packets['IC0ueV5s']
                       if row['X1IuZnj2'] == banner['X1IuZnj2']]
            self.assertEqual({row['ijEey5f7'] for row in details}, {'1', '2'})
            self.assertEqual(len({row['nqzG3b2v'] for row in details}), 2)
            for detail in details:
                self.assertIn({'X1IuZnj2': detail['X1IuZnj2'],
                               'nqzG3b2v': detail['nqzG3b2v'],
                               '08MuyfqD': '0', 'L4QmV0Nz': '0'}, packets['80nGg32w'])
                self.assertTrue(detail['t6aQ1voV'])
                cost = list(map(int, detail['0GgK6ytT'].split(':')))
                self.assertEqual(cost[0], 50)
                self.assertGreater(cost[2], 0)  # Native multi-count divides by this.
                self.assertIn(cost[3], (1, 10))
                self.assertEqual(len(detail['1ovyP04j'].split(':')), 2)

    def test_visible_schedules_have_banner_images(self):
        packets = entry_packets()
        self.assertEqual({r['X1IuZnj2'] for r in packets['PcUrGH13']},
                         {r['X1IuZnj2'] for r in packets['4D5k8dpI']})
        for schedule in packets['4D5k8dpI']:
            main, *sub = schedule['4yT7FUqj'].split(',')
            self.assertTrue(main.endswith('.png'))
            self.assertTrue(sub)
            self.assertTrue(all(':' in item for item in sub))
            for item in sub:
                data = (ROOT/'assets/cache/en/sd/static_banner/gacha/sub'/item.split(':', 1)[1]).read_bytes()
                self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
                self.assertEqual(struct.unpack('>II', data[16:24]), (640, 190))
