import os,sys,threading,json
from pathlib import Path
_http=None
_thread=None

def start(directory,external):
 global _http,_thread
 if _thread and _thread.is_alive():return 'Server running on this phone'
 root=Path(directory);cache=Path(external)/'assets/cache'
 if not (cache/'mst').is_dir() or not (cache/'common_lang').is_dir():
  raise RuntimeError('Recovered data is not installed. Complete the USB data transfer first.')
 manifest=Path(external)/'data-manifest.json'
 if not manifest.is_file():raise RuntimeError('USB data transfer is not complete yet.')
 for row in json.loads(manifest.read_text())['files']:
  file=cache/row['path']
  if not file.is_file() or file.stat().st_size!=row['bytes']:
   raise RuntimeError('Missing or incomplete data: '+row['path'])
 (root/'runtime/logs').mkdir(parents=True,exist_ok=True)
 link=root/'assets/cache'
 if not link.exists():link.symlink_to(cache,target_is_directory=True)
 os.environ['FFO_PLAYER_DB']=str(root/'runtime/players.sqlite3')
 sys.path.insert(0,str(root/'server'))
 from main import Gateway
 from http.server import ThreadingHTTPServer
 _http=ThreadingHTTPServer(('127.0.0.1',11880),Gateway)
 _http.daemon_threads=True
 _thread=threading.Thread(target=_http.serve_forever,daemon=True);_thread.start()
 return 'Server running on this phone'

def stop():
 global _http,_thread
 if _http:
  _http.shutdown();_http.server_close();_http=None
 _thread=None
