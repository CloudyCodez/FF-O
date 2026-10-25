"""FF:O local gateway with bounded native gameplay restoration."""
import argparse,hashlib,json,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from protocol import inspect_request,decode_native_request,native_response,CATALOG
from startup import dispatch
from assets import resolve_asset
from battles import tutorial_missions,AUTHORED_MISSIONS
import vortex
ROOT=Path(__file__).resolve().parents[1]
LOCK=threading.Lock()
class Gateway(BaseHTTPRequestHandler):
 server_version='FFO/0.0.1'
 def reply(self,status,data):
  raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  if urlsplit(self.path).path.endswith('/probability/sg_summons_list.php'):
   return self.rate_page(parse_qs(urlsplit(self.path).query))
  if '/content/userpolicysin/' in self.path:
   raw=b'<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#102448;color:#fff;font:20px sans-serif;line-height:1.6;padding:24px}h1{color:#94ddff}</style><h1>FF:O</h1><h2>Local test session</h2><p>This client connects to the FF:O server on this computer. Your test profile and progress are saved locally.</p><p>Summons, battles and other gameplay systems are being restored. Continue below to use the local test profile.</p>'
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
  if urlsplit(self.path).path=='/health':return self.reply(200,{'project':'FF:O','gateway_revision':5,'phase':'early-game-restoration','native_request_classes':len(CATALOG['requests']),'native_cipher':'cbc-double-padding','asset_delivery':True,'client_login_ready':True,'full_gameplay_ready':False,'placeholder_story_battles':len(set(tutorial_missions())-AUTHORED_MISSIONS),'vortex_missions':len(vortex.missions()),'vortex_encounter_mode':'offline-placeholder-battles','story_encounter_mode':'provisional-placeholders','supported_story_missions':sorted(tutorial_missions())})
  path=resolve_asset(urlsplit(self.path).path)
  if path is not None:
   with path.open('rb') as stream:
    import os,shutil
    size=os.fstat(stream.fileno()).st_size
    self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(size));self.end_headers();shutil.copyfileobj(stream,self.wfile,1024*1024)
   return
  if urlsplit(self.path).path.startswith('/dlc_assets_prod/'):
   folder=ROOT/'runtime/logs';folder.mkdir(parents=True,exist_ok=True)
   with LOCK,(folder/'missing-assets.jsonl').open('a',encoding='utf-8') as stream:
    stream.write(json.dumps({'time':time.time(),'path':urlsplit(self.path).path})+'\n')
  self.reply(404,{'error':'unimplemented_route'})
 def do_POST(self):
  try:length=int(self.headers.get('Content-Length','0'))
  except ValueError:return self.reply(400,{'error':'invalid_length'})
  if not 0<length<=2_000_000:return self.reply(413,{'error':'invalid_body_size'})
  raw=self.rfile.read(length);record={'time':time.time(),'path':urlsplit(self.path).path,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
  if record['path'].endswith('/probability/sg_summons_list.php'):
   return self.rate_page(parse_qs(raw.decode('utf-8')))
  try:
   record.update(inspect_request(record['path'],raw))
   name,contract,payload=decode_native_request(record['path'],raw)
   record['native_envelope_valid']=True
   if name in {'MissionWaveStartRequest','MissionStartRequest','MissionEndRequest','GachaExeRequest','UnitEquipRequest','PartyDeckEditRequest','MailReceiptRequest','MailListRequest','TownInRequest','TownUpdateRequest','TownOutRequest'}:
    record['gameplay']={key:payload[key] for key in ('jQsE54Iz','5yLD4dYI','09HRWXDf','Er92Kdhm','49rQB3fP','5Eb0Rig6','CN92arJK','nSG9Jb1s','nE7pV2wr','2urzfX6d','rStH7od8','t8TPs6o2','JcxS6A8N','1sGiqV9T') if key in payload}
   response=dispatch(name,payload)
   status=200 if response is not None else 501;error='native_response_not_restored'
  except (ValueError,UnicodeError,RecursionError) as exc:record['decode_error']=str(exc);status=400;error='unrecognized_native_request'
  folder=ROOT/'runtime/logs';folder.mkdir(parents=True,exist_ok=True)
  with LOCK,(folder/'requests.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
  if status==200:return self.reply(200,native_response(response,contract,time.time()))
  # Unimplemented requests still fail explicitly, never fake login success.
  self.reply(status,{'error':error,'request':record.get('request')})
 def rate_page(self,params):
  from rates import page
  try:raw=page(params.get('gacha_id',['1'])[0])
  except ValueError:return self.reply(400,{'error':'unknown_banner'})
  self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--port',type=int,default=11880);args=parser.parse_args()
 print(f'FF:O local gateway http://{args.host}:{args.port}; early-game restoration build',flush=True)
 ThreadingHTTPServer((args.host,args.port),Gateway).serve_forever()
