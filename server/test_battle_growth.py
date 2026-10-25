from contextlib import closing
import concurrent.futures
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import battles
import units


class BattleGrowthTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/'player.db'
        self.start={'jQsE54Iz':[{'qo3PECw6':'1110401'}]}
        self.end={**self.start,'09HRWXDf':[{'Wdi3MAs2':'35'}]}

    def owned(self):
        return units.inventory(self.path)

    def test_migration_preserves_old_units(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('CREATE TABLE units (uid INTEGER PRIMARY KEY,unit_id INTEGER,level INTEGER)')
            db.execute('INSERT INTO units VALUES (42,100000102,1)')
        self.assertEqual(self.owned()[0]['og2GHy49'],'42')
        self.assertEqual(self.owned()[0]['B6H34Mea'],'0')

    def test_level_up_uses_native_threshold_and_remainder(self):
        result=units.gain_exp((1,100000102,1,0),60)
        self.assertEqual(result,(1,100000102,3,2))
        self.assertGreater(int(units.serialize(result)['em5hx4FX'].split('-')[0]),378)
        self.assertEqual(units.gain_exp((1,100000102,30,0),1000)[2:],(30,0))

    def test_retries_are_exact_and_a_new_run_can_award_again(self):
        battles.begin_mission(self.start,self.path)
        first=battles.finish_tutorial(self.end,self.path)
        growth=first['09HRWXDf'][0]['Qic38SuC'].split(',')
        self.assertEqual(sum(int(r.split('_')[1].split(':')[12]) for r in growth),50)
        self.assertEqual(self.owned()[0]['7wV3QZ80'],'2')
        self.assertEqual(self.owned()[0]['B6H34Mea'],'15')
        self.assertEqual(first,battles.finish_tutorial(self.end,self.path))
        self.assertEqual(first,battles.finish_tutorial({**self.end,'transport_counter':'different'},self.path))
        battles.begin_mission(self.start,self.path)
        battles.finish_tutorial(self.end,self.path)
        self.assertEqual(self.owned()[0]['B6H34Mea'],'40')

    def test_only_party_at_start_is_rewarded(self):
        self.owned()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('CREATE TABLE party_decks (deck_id INTEGER PRIMARY KEY,name TEXT,members TEXT)')
            db.execute("INSERT INTO party_decks VALUES (1,'Rain','1:0:1')")
        battles.begin_mission(self.start,self.path)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE party_decks SET members='1:0:2'")
        response=battles.finish_tutorial(self.end,self.path)
        self.assertEqual([r['og2GHy49'] for r in response['B71MekS8']],['1'])
        self.assertEqual(self.owned()[1]['7wV3QZ80'],'1')

    def test_parallel_retries_do_not_award_twice(self):
        battles.begin_mission(self.start,self.path)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:battles.finish_tutorial(self.end,self.path),range(2)))
        self.assertEqual(*results)
        self.assertEqual(self.owned()[0]['B6H34Mea'],'15')

    def test_failed_switch_save_rolls_back_reward_and_completion(self):
        battles.begin_mission(self.start,self.path)
        before=self.owned()
        with patch('battles.saved_switches',side_effect=ValueError('invalid switch')):
            with self.assertRaises(ValueError):battles.finish_tutorial(self.end,self.path)
        self.assertEqual(before,self.owned())
        with closing(sqlite3.connect(self.path)) as db, db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM mission_results').fetchone()[0],0)
            self.assertIsNone(db.execute('SELECT response FROM battle_runs').fetchone()[0])

    def test_mismatched_result_cannot_complete_active_battle(self):
        battles.begin_mission(self.start,self.path)
        with self.assertRaises(ValueError):
            battles.finish_tutorial({'jQsE54Iz':[{'qo3PECw6':'1110101'}],
                                     '09HRWXDf':[{}]},self.path)

    def test_abandoned_encounter_does_not_lock_new_mission(self):
        battles.begin_mission(self.start,self.path)
        other={'jQsE54Iz':[{'qo3PECw6':'1110101'}]}
        battles.begin_mission(other,self.path)
        result=battles.finish_tutorial({**other,'09HRWXDf':[{}]},self.path)
        self.assertEqual(result['09HRWXDf'][0]['kcb0tsM6'],'10')

    def test_reported_incomplete_waves_cannot_award_clear(self):
        battles.begin_mission(self.start,self.path)
        with self.assertRaises(ValueError):
            battles.finish_tutorial({**self.end,'nSG9Jb1s':[
                {'NYb0Cri6':'TOTAL_MISSION_BATTLE_WIN','6gAX1BpC':'3'}]},self.path)
        self.assertEqual(self.owned()[0]['7wV3QZ80'],'1')

    def test_exp_remainder_is_not_lost(self):
        self.owned()
        with closing(sqlite3.connect(self.path)) as db,db:
            for ident in (100000102,100000202,100000102):
                db.execute('INSERT INTO units (unit_id) VALUES (?)',(ident,))
        start={'jQsE54Iz':[{'qo3PECw6':'1110302'}]}
        battles.begin_mission(start,self.path)
        result=battles.finish_tutorial({**start,'09HRWXDf':[{}]},self.path)
        awards=[int(r.split('_')[1].split(':')[12]) for r in result['09HRWXDf'][0]['Qic38SuC'].split(',')]
        self.assertEqual(awards,[9,9,9,9,8])
        self.assertEqual(sum(awards),44)


if __name__=='__main__':unittest.main()
