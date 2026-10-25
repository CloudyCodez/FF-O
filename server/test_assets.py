import tempfile,unittest
from pathlib import Path
from assets import resolve_asset
class AssetTests(unittest.TestCase):
 def test_exact_preserved_asset_is_resolved(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);p=root/'mst/Ver1_fixture.dat';p.parent.mkdir();p.write_bytes(b'fixture')
   self.assertEqual(resolve_asset('/dlc_assets_prod/mst/Ver1_fixture.dat',root),p.resolve())
   self.assertIsNone(resolve_asset('/dlc_assets_prod/mst/not-present.dat',root))
 def test_only_game_content_roots_and_contained_paths_are_served(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   for path in ['/dlc_assets_prod/../secret','/dlc_assets_prod/mst/%2e%2e/%2e%2e/secret','/dlc_assets_prod/shared_prefs/auth.xml','/dlc_assets_prod/mst/a%5cb','/dlc_assets_prod//mst/a','/other/mst/a']:
    self.assertIsNone(resolve_asset(path,root),path)
if __name__=='__main__':unittest.main()
