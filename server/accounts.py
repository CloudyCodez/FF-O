"""Local guest identities. Never import identities from the preserved archive."""
import os,secrets,sqlite3,time
from contextlib import closing
from pathlib import Path
DEFAULT_DB=Path(os.environ.get('FFO_PLAYER_DB') or Path(__file__).resolve().parents[1]/'runtime/players.sqlite3').resolve()
def guest(database=DEFAULT_DB):
 database=Path(database);database.parent.mkdir(parents=True,exist_ok=True)
 with closing(sqlite3.connect(database,timeout=10)) as db,db:
  db.execute('CREATE TABLE IF NOT EXISTS guests (id INTEGER PRIMARY KEY, name TEXT NOT NULL, password TEXT NOT NULL, created INTEGER NOT NULL)')
  row=db.execute('SELECT id,name,password,created FROM guests WHERE id=100000001').fetchone()
  if row is None:
   row=(100000001,'Player',secrets.token_urlsafe(24),int(time.time()))
   db.execute('INSERT INTO guests VALUES (?,?,?,?)',row)
 return {'9Tbns0eI':str(row[0]),'9qh17ZUf':row[1],'JC61TPqS':row[2],
         'm3Wghr1j':'100000001','6Nf5risL':'0','e8Si6TGh':'FFO-LOCAL',
         'F0bCxp5m':time.strftime('%Y%m%d',time.gmtime(row[3]))}
