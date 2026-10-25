import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from summons import summon,summon_pool,is_collaboration
from units import inventory,masters
import sqlite3
from contextlib import closing
from banners import COLLAB_BANNER_ID
import vision_cards


class SummonPersistenceTests(unittest.TestCase):
    def test_tutorial_retry_does_not_duplicate_fina(self):
        with tempfile.TemporaryDirectory() as folder:
            database=Path(folder)/'player.db'
            payload={'5yLD4dYI':[{'X1IuZnj2':'0','nqzG3b2v':'0'}]}
            first=summon(payload,database)
            second=summon(payload,database)
            self.assertEqual(first,second)
            self.assertEqual(len(inventory(database)),3)

    def test_ten_pull_grants_ten_distinct_owned_ids_and_survives_reload(self):
        with tempfile.TemporaryDirectory() as folder:
            database=Path(folder)/'player.db'
            with patch('summons.secrets.choice',return_value=213000105):
                result=summon({'5yLD4dYI':[{'X1IuZnj2':'1','nqzG3b2v':'20','2RtVPS3b':'10'}]},database)
            granted=result['B71MekS8']
            self.assertEqual(len(granted),10)
            self.assertEqual(len({r['og2GHy49'] for r in granted}),10)
            self.assertEqual(inventory(database)[2:],granted)
            self.assertEqual(len(result['5yLD4dYI'][0]['UJz5QED2'].split(',')),10)

    def test_unknown_offer_and_invalid_count_do_not_grant_units(self):
        with tempfile.TemporaryDirectory() as folder:
            database=Path(folder)/'player.db'
            self.assertIsNone(summon({'5yLD4dYI':[{'X1IuZnj2':'999','nqzG3b2v':'1'}]},database))
            with self.assertRaises(ValueError):
                summon({'5yLD4dYI':[{'X1IuZnj2':'1','nqzG3b2v':'11','2RtVPS3b':'10'}]},database)
            self.assertEqual(len(inventory(database)),2)

    def test_local_pool_only_contains_recovered_base_summon_units(self):
        pool=summon_pool()
        self.assertTrue(pool)
        for ident in pool:
            row=masters()[ident]
            self.assertEqual(row['UbSL8C7i'],'2')
            self.assertEqual(row['woghJa61'],str(ident))
            self.assertGreaterEqual(int(row['9fW0TePj']),3)

    def test_collaboration_pool_is_separate_from_both_other_offers(self):
        collab=set(summon_pool(COLLAB_BANNER_ID))
        self.assertTrue(collab)
        self.assertTrue(all(is_collaboration(masters()[i]) for i in collab))
        self.assertFalse(collab.intersection(summon_pool('1')))
        self.assertFalse(collab.intersection(summon_pool('2')))
        self.assertEqual(collab.union(summon_pool('2')),set(summon_pool()))
        self.assertTrue(all(int(masters()[i]['9fW0TePj'])>=5 for i in summon_pool('1')))

    def test_collaboration_purchase_draws_from_its_own_pool(self):
        with tempfile.TemporaryDirectory() as folder:
            database=Path(folder)/'player.db'
            with patch('summons.secrets.choice',return_value=313000205) as draw:
                result=summon({'5yLD4dYI':[{'X1IuZnj2':str(COLLAB_BANNER_ID),'nqzG3b2v':str(COLLAB_BANNER_ID*10+1),'2RtVPS3b':'1'}]},database)
            self.assertEqual(draw.call_args.args[0],summon_pool(COLLAB_BANNER_ID))
            self.assertEqual(result['B71MekS8'][0]['3HriTp6B'],'313000205')
            self.assertEqual(result['5yLD4dYI'][0]['X1IuZnj2'],str(COLLAB_BANNER_ID))

    def test_nv_rewards_include_persistent_cards_for_each_reveal(self):
        with tempfile.TemporaryDirectory() as folder:
            database=Path(folder)/'player.db'
            with patch('summons.secrets.choice',return_value=100040007):
                result=summon({'5yLD4dYI':[{'X1IuZnj2':'1','nqzG3b2v':'20','2RtVPS3b':'10'}]},database)
            cards=result['2Xi0wuGA']
            self.assertEqual(len(cards),10)
            self.assertEqual(len({card['gXb32xzQ'] for card in cards}),10)
            rewards=result['5yLD4dYI'][0]['eb2ANT1m'].split(',')
            self.assertEqual(result['5yLD4dYI'][0]['zoU5J3Kq'],'35')
            self.assertEqual(result['5yLD4dYI'][0]['8schfem9'],
                             ','.join(f"{c['gXb32xzQ']}:39" for c in cards))
            self.assertEqual(rewards,[f"27:{c['5giCMUd2']}:{c['gXb32xzQ']}:1" for c in cards])
            for card in cards:self.assertIn(int(card['5giCMUd2']),vision_cards.masters())
            with closing(sqlite3.connect(database)) as db:
                self.assertEqual(vision_cards.packets(db)['2Xi0wuGA'],cards)
