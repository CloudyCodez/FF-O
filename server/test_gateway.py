import hashlib,json,threading,unittest,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
from main import Gateway
from protocol import encrypt_payload,decrypt_payload,CATALOG
from unittest.mock import patch
class GatewayTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),Gateway);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.url=f'http://127.0.0.1:{cls.server.server_port}'
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
 def test_health_distinguishes_working_login_from_full_gameplay(self):
  data=json.load(urllib.request.urlopen(self.url+'/health'))
  self.assertTrue(data['client_login_ready']);self.assertFalse(data['full_gameplay_ready'])
  self.assertIn('1110203',data['supported_story_missions'])
  self.assertEqual(data['native_cipher'],'cbc-double-padding')
 def test_native_initialize_returns_encrypted_local_guest_identity(self):
  packet={'TEAYk6R1':{'z5hB3P01':'75fYdNxq','ytHoz4E2':'42'},'t7n6cVWf':{'qrVcDe48':encrypt_payload({'fixture':True},'rVG09Xnt','cbc-double-padding')}}
  req=urllib.request.Request(self.url+'/actionSymbol/fSG1eXI9.php',data=json.dumps(packet).encode(),headers={'Content-Type':'application/json'})
  with patch('startup.guest',return_value={'9Tbns0eI':'test-local'}):
   with urllib.request.urlopen(req) as result:
    data=json.load(result);self.assertEqual(result.code,200)
  native=decrypt_payload(data['t7n6cVWf']['qrVcDe48'],'rVG09Xnt','cbc-double-padding')
  self.assertEqual(native['LhVz6aD2'],[{'9Tbns0eI':'test-local'}]);self.assertGreater(len(native['c1qYg84Q']),200)
 def test_unimplemented_gameplay_still_fails_explicitly(self):
  contract=CATALOG['requests']['GachaBoxNextRequest']
  packet={'TEAYk6R1':{'z5hB3P01':contract['getRequestID']['value']},'t7n6cVWf':{'qrVcDe48':encrypt_payload({},contract['getEncodeKey']['value'],'cbc-double-padding')}}
  req=urllib.request.Request(self.url+contract['getUrl']['value'],data=json.dumps(packet).encode())
  with self.assertRaises(urllib.error.HTTPError) as response:urllib.request.urlopen(req)
  with response.exception as result:self.assertEqual(result.code,501)
 def test_invalid_native_request_id_is_rejected(self):
  packet={'TEAYk6R1':{'z5hB3P01':'wrong'},'t7n6cVWf':{'qrVcDe48':encrypt_payload({'fixture':True},'rVG09Xnt','cbc-double-padding')}}
  req=urllib.request.Request(self.url+'/actionSymbol/fSG1eXI9.php',data=json.dumps(packet).encode())
  with self.assertRaises(urllib.error.HTTPError) as response:urllib.request.urlopen(req)
  with response.exception as result:self.assertEqual(result.code,400)
if __name__=='__main__':unittest.main()
