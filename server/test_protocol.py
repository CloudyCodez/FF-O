import json,unittest
from protocol import *
class ProtocolTests(unittest.TestCase):
 def test_native_catalog_has_complete_unique_routes(self):
  wire_routes={tuple(c[k]['value'] for k in ('getUrl','getRequestID','getEncodeKey')) for c in CATALOG['requests'].values()}
  self.assertEqual(sum(map(len,BY_PATH.values())),len(wire_routes))
  self.assertEqual(len(CATALOG['requests']),222)
  self.assertTrue(any(len(entries)>1 for entries in BY_PATH.values()))
  self.assertEqual(identify('/lapisProd/app/php/gme/actionSymbol/fSG1eXI9.php')[0],'InitializeRequest')
 def test_recovered_initialize_key_decodes_local_fixture(self):
  body={'fixture_header':{},'fixture_wrapper':{'fixture_data':encrypt_payload({'fixture':'Cloud'},'rVG09Xnt')}}
  result=inspect_request('/actionSymbol/fSG1eXI9.php',json.dumps(body))
  self.assertEqual(result['request'],'InitializeRequest');self.assertEqual(result['payload_keys'],['fixture']);self.assertNotIn('Cloud',json.dumps(result))
 def test_malformed_and_ambiguous_packets_are_rejected(self):
  encrypted=encrypt_payload({'fixture':1},'rVG09Xnt')
  for body in ['[]','{}',json.dumps({'a':encrypted,'b':encrypted}),json.dumps({'a':'invalid-base64'})]:
   with self.assertRaises(ValueError):inspect_request('/actionSymbol/fSG1eXI9.php',body)
  with self.assertRaises(ValueError):identify('/actionSymbol/unknown.php')
 def test_cipher_rejects_bad_padding_and_wrong_key(self):
  data=encrypt_payload({'test':True},'rVG09Xnt');self.assertEqual(decrypt_payload(data,'rVG09Xnt'),{'test':True})
  with self.assertRaises(ValueError):decrypt_payload(data,'wrong')
 def test_native_request_uses_cbc_and_validates_path_and_header_identity(self):
  body={'TEAYk6R1':{'z5hB3P01':'75fYdNxq','ytHoz4E2':'12'},'t7n6cVWf':{'qrVcDe48':encrypt_payload({'fixture':1},'rVG09Xnt','cbc-double-padding')}}
  name,contract,payload=decode_native_request('/actionSymbol/fSG1eXI9.php',json.dumps(body));self.assertEqual(name,'InitializeRequest');self.assertEqual(payload,{'fixture':1})
  self.assertEqual(inspect_request('/actionSymbol/fSG1eXI9.php',json.dumps(body))['cipher'],'cbc-double-padding')
  body['TEAYk6R1']['z5hB3P01']='wrong'
  with self.assertRaises(ValueError):decode_native_request('/actionSymbol/fSG1eXI9.php',json.dumps(body))
 def test_native_response_encrypts_body_with_the_same_request_contract(self):
  _,contract=identify('/actionSymbol/fSG1eXI9.php');r=native_response({'fixture':[{'value':'text'}]},contract,123456)
  self.assertEqual(r['TEAYk6R1']['dNrSy63V'],'123456')
  self.assertEqual(decrypt_payload(r['t7n6cVWf']['qrVcDe48'],'rVG09Xnt','cbc-double-padding'),{'fixture':[{'value':'text'}]})
 def test_identical_inherited_wire_requests_decode_once(self):
  contract=CATALOG['requests']['GrandMissionEntryRequest']
  alias=CATALOG['requests']['SpChallengeEntryRequest']
  for field in ('getUrl','getRequestID','getEncodeKey'):
   self.assertEqual(contract[field]['value'],alias[field]['value'])
  path=contract['getUrl']['value']
  body={'TEAYk6R1':{'z5hB3P01':contract['getRequestID']['value']},'t7n6cVWf':{'qrVcDe48':encrypt_payload({'fixture':1},contract['getEncodeKey']['value'],'cbc-double-padding')}}
  self.assertEqual(decode_native_request(path,json.dumps(body))[2],{'fixture':1})
  self.assertTrue(inspect_request(path,json.dumps(body))['decoded'])
  body['TEAYk6R1']['z5hB3P01']='wrong'
  with self.assertRaises(ValueError):decode_native_request(path,json.dumps(body))
if __name__=='__main__':unittest.main()
