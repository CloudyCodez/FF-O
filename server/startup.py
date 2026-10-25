"""Recovered startup responses, implemented independently for the local client."""
import json
import time
from pathlib import Path
from accounts import guest
from economy import currency_packets
from switches import switch_packets
from units import player_packets,edit_party
from battles import begin_mission,finish_tutorial
from summons import summon
from banners import entry_packets
from home import packets as home_packets
from challenges import packets as challenge_packets
import mailbox as local_mail
import espers
import vortex
from towns import handle as town_request
def dispatch(name,payload):
 if name=='VariableStoreCheckRequest':
  # Native VariableStoreScheduleInfoResponse tag. No rotating paid/local
  # stores are scheduled; return the explicit empty schedule on refresh.
  return {'3VS1Bhmf':[]}
 if name=='GrandMissionEntryRequest':
  rows=payload.get('Dtw7GU1j',[])
  if len(rows)!=1 or rows[0].get('Y4VoF8yu')!='1':return None
  # Recovered GrandMissionStatusResponse fields; no active local campaign.
  return {'9mt5LBsu':[],'uPW93tHB':[{'oz5Vt6AR':'0','w24kLvE6':'0','es0Yun3Z':'0'}]}
 if name in {'TownInRequest','TownUpdateRequest','TownOutRequest'}:return town_request(name,payload)
 if name=='MailListRequest':return local_mail.packets()
 if name=='MailReceiptRequest':return local_mail.claim(payload)
 if name in {'GachaEntryRequest','GachaInfoRequest','RoutineGachaUpdateRequest'}:
  return {**entry_packets(),**currency_packets()}
 if name in {'NoticeUpdateRequest','ResourceAllDownloadRequest','sgOfferwallInfoRequest'}:
  # All recovered client resources are already staged in the isolated install.
  return {}
 if name=='sgPanelQuestEntryRequest':
  # No campaign-panel state on a fresh local account yet.  Keep the panel
  # navigable while its reward and mission contracts are reconstructed.
  return {}
 if name=='UnitEquipRequest':
  # The starter guidance sends a zero-filled equipment loadout for the newly
  # granted unit.  There are no equipment instances to transfer yet.
  records=payload.get('Er92Kdhm',[])
  if len(records)!=1 or records[0].get('r21y0YzS')!='1':return None
  return {'B71MekS8':player_packets()['B71MekS8']}
 if name=='PartyDeckEditRequest':return edit_party(payload)
 if name=='GachaExeRequest':return summon(payload)
 if name in {'RoutineWorldUpdateRequest','RoutineEventUpdateRequest'}:
  if name=='RoutineEventUpdateRequest':return vortex.packets()
  # Native UpdateInfo refresh deadline, not gameplay completion or progression.
  tag='3yXTA9Se' if name=='RoutineWorldUpdateRequest' else '8SztQck9'
  return {tag:[{'0Zpuzj7E':str(int(time.time())+300)}]}
 if name=='MissionEndRequest':
  return finish_tutorial(payload)
 if name=='DungeonResourceLoadMstListRequest':
  # Recovered packs are preinstalled in the local client, no CDN jobs required.
  return {'1IfDqR4n':[]}
 if name=='MissionWaveStartRequest':
  return begin_mission(payload)
 if name=='UpdateSwitchInfoRequest':
  return switch_packets(payload)
 if name=='RoutineHomeUpdateRequest':
  # Factory handles this tag in a separate branch. Inspect native response map.
  return home_packets()
 if name in {'GetUserInfo2Request','GetUserInfo3Request','GetReinforcementInfoRequest','FriendListRequest','sgHomeMarqueeInfoRequest','UpdateDeviceIdRequest'}:
  # Fresh local guest has no secondary inventories or event records yet.
  return {}
 if name=='InitializeRequest':
  catalog=json.loads((Path(__file__).resolve().parents[1]/'research/local-version-catalog.json').read_text())
  text_catalog=json.loads((Path(__file__).resolve().parents[1]/'research/local-text-catalog.json').read_text())
  registry=json.loads((Path(__file__).resolve().parents[1]/'research/registry-master-catalog.json').read_text())
  return {'LhVz6aD2':[guest()], 'c1qYg84Q':catalog['native_master_rows']+registry['native_version_rows']+text_catalog['native_version_rows']}
 if name=='GetUserInfoRequest':
  return {'LhVz6aD2':[guest()], **currency_packets(), **switch_packets(), **player_packets(), **challenge_packets(), **espers.packets()}
 if name=='GetBackgroundDownloadInfoRequest':
  # No background jobs: recovered content is staged by the local installer.
  return {}
 if name=='GameSettingRequest':
  # GameSettingResponse::readParam 0x1986258; native factory tag PJm9d197.
  return {'PJm9d197':[{
   'P_GS_CDN_PATH':'http://127.0.0.1:11880/dlc_assets_prod/',
   'P_GS_EVENT_PATH':'http://127.0.0.1:11880/events/',
   'P_GS_NOTICE_HOST_SERVER':'http://127.0.0.1:11880/',
   'P_GS_BANNER_PATH':'http://127.0.0.1:11880/banners/',
   'P_GS_ACTIVE_LANGUAGES':'en',
   'P_GS_FEATURE_FRESVII_COMMUNITY':'0',
   'P_GS_FEATURE_FRESVII_VIDEO':'0',
   'P_GS_FEATURE_HOME_MARQUEE':'0',
   'P_GS_NOTICE_STATIC':'0',
  }]}
 return None
