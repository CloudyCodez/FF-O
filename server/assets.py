"""Read-only local delivery of preserved game files; never account backups."""
from pathlib import Path,PurePosixPath
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]/'assets/cache'
def resolve_asset(url_path,root=ROOT):
 prefix='/dlc_assets_prod/'
 if not url_path.startswith(prefix):return None
 relative=unquote(url_path[len(prefix):]);parts=PurePosixPath(relative).parts
 if not parts or parts[0] not in {'mst','common_lang','en','localized_texts'}:return None
 if '\\' in relative or '\0' in relative or '..' in parts or PurePosixPath(relative).is_absolute():return None
 path=root.joinpath(*parts).resolve()
 if not path.is_relative_to(root.resolve()) or not path.is_file():return None
 if root==ROOT and parts[0] in {'mst','localized_texts'}:
  compat=(ROOT.parent/'client-compat').joinpath(*parts).resolve()
  if compat.is_relative_to((ROOT.parent/'client-compat').resolve()) and compat.is_file():return compat
 return path
