"""Exact request getters recovered from build9101; no upstream traffic."""
import base64,json
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad,pad
ROOT=Path(__file__).resolve().parents[1]
CATALOG=json.loads((ROOT/'research/native-requests.json').read_text())
BY_PATH={}
for name,contract in CATALOG['requests'].items():BY_PATH.setdefault(contract['getUrl']['value'],[]).append((name,contract))
# Native subclasses can inherit the same wire request (GrandMission and
# SpChallenge entry do). Deduplicate only exact URL/ID/key triples.
for path,entries in BY_PATH.items():
 seen=set();unique=[]
 for name,contract in entries:
  identity=tuple(contract[k]['value'] for k in ('getUrl','getRequestID','getEncodeKey'))
  if identity not in seen:unique.append((name,contract));seen.add(identity)
 BY_PATH[path]=unique
def key_bytes(key):
 raw=key.encode('utf-8')
 if not 0<len(raw)<=16:raise ValueError('Unsupported AES key width')
 return raw.ljust(16,b'\0')
NATIVE_IV=b'dZMjkk8gFDzKHlsx'
def decrypt_payload(encoded,key,mode='ecb'):
 raw=base64.b64decode(encoded,validate=True)
 if not raw or len(raw)%16:raise ValueError('Invalid AES block length')
 if mode not in {'ecb','cbc-double-padding'}:raise ValueError('Unsupported cipher')
 cipher=AES.new(key_bytes(key),AES.MODE_ECB) if mode=='ecb' else AES.new(key_bytes(key),AES.MODE_CBC,NATIVE_IV)
 plain=unpad(cipher.decrypt(raw),16)
 if mode!='ecb':plain=unpad(plain,16)
 return json.loads(plain.decode('utf-8'))
def encrypt_payload(value,key,mode='ecb'):
 raw=json.dumps(value,separators=(',',':'),ensure_ascii=False).encode()
 if mode not in {'ecb','cbc-double-padding'}:raise ValueError('Unsupported cipher')
 cipher=AES.new(key_bytes(key),AES.MODE_ECB) if mode=='ecb' else AES.new(key_bytes(key),AES.MODE_CBC,NATIVE_IV)
 plain=pad(raw,16) if mode=='ecb' else pad(pad(raw,16),16)
 return base64.b64encode(cipher.encrypt(plain)).decode()

def decode_native_request(path,body):
 packet=json.loads(body)
 if not isinstance(packet,dict):raise ValueError('Native envelope must be an object')
 header=packet.get('TEAYk6R1');wrapper=packet.get('t7n6cVWf')
 if not isinstance(header,dict) or not isinstance(wrapper,dict):raise ValueError('Native header/body missing')
 request_id=header.get('z5hB3P01');encoded=wrapper.get('qrVcDe48')
 if not isinstance(request_id,str) or not isinstance(encoded,str):raise ValueError('Native request identity/payload missing')
 entries=[entry for suffix,group in BY_PATH.items() if path==suffix or path.endswith(suffix) for entry in group if entry[1]['getRequestID']['value']==request_id]
 if len(entries)!=1:raise ValueError('Path and native request ID do not identify one request')
 name,contract=entries[0]
 payload=decrypt_payload(encoded,contract['getEncodeKey']['value'],'cbc-double-padding')
 if not isinstance(payload,dict):raise ValueError('Native body must decode to an object')
 return name,contract,payload

def native_response(payload,contract,now):
 # HeaderResponse reads dNrSy63V as an integer timestamp. The encrypted body
 # follows BaseRequest::getSendData / GameResponseParser::parseTag's CBC path.
 return {'TEAYk6R1':{'dNrSy63V':str(int(now))},'t7n6cVWf':{'qrVcDe48':encrypt_payload(payload,contract['getEncodeKey']['value'],'cbc-double-padding')}}
def identify(path):
 # Accept the recovered suffix under a local API prefix, without fuzzy IDs.
 matches=[entry for suffix,entries in BY_PATH.items() if path==suffix or path.endswith(suffix) for entry in entries]
 if len(matches)!=1:raise ValueError('Unknown or ambiguous request path')
 return matches[0]
def inspect_request(path,body):
 entries=[entry for suffix,group in BY_PATH.items() if path==suffix or path.endswith(suffix) for entry in group]
 if not entries:raise ValueError('Unknown request path')
 packet=json.loads(body)
 if not isinstance(packet,dict):raise ValueError('Request envelope must be an object')
 # Older field names are not assumed current. Find exactly one AES payload
 # that decodes with this build's recovered request key; retain only shape.
 candidates=[];strings=[]
 def walk(value):
  if isinstance(value,str) and 16<=len(value)<=2_000_000:
   strings.append(value)
  elif isinstance(value,dict):
   for v in value.values():walk(v)
  elif isinstance(value,list):
   for v in value:walk(v)
 walk(packet)
 for name,contract in entries:
  for value in strings:
   for mode in ['cbc-double-padding','ecb']:
    try:candidates.append((name,contract,decrypt_payload(value,contract['getEncodeKey']['value'],mode),mode))
    except (ValueError,UnicodeError):pass
 if len(candidates)!=1:raise ValueError('Expected one decodable native request payload')
 name,contract,payload,mode=candidates[0]
 return {'request':name,'request_id':contract['getRequestID']['value'],'envelope_keys':sorted(packet),'payload_keys':sorted(payload) if isinstance(payload,dict) else [],'cipher':mode,'decoded':True}
