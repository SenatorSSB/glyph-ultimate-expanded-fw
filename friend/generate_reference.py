#!/usr/bin/env python3
"""Generate reference artifacts from the actual tested complete baked Config.
This is host-only artifact generation, not a Config push/device writer.
"""
import json, pathlib, sys
from google.protobuf import json_format
root=pathlib.Path(__file__).resolve().parents[1]
out=root.parent/'config-refresh-v3-20261012'/'verification'; profile=root.parent/'config-refresh-v3-20261012'/'profile'; profile.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(out/'protobuf'))
import config_pb2
raw=(out/'baked-short.pb').read_bytes()
assert raw==(out/'baked-ordinary.pb').read_bytes()
config=config_pb2.Config(); config.ParseFromString(raw)
text=json_format.MessageToJson(config,preserving_proto_field_name=True,always_print_fields_with_no_presence=True)
roundtrip=config_pb2.Config(); json_format.Parse(text,roundtrip)
assert roundtrip.SerializeToString(deterministic=True)==raw
assert len(config.game_mode_configs)==13 and len(config.rgb_configs)==13
assert config.game_mode_configs[2].mode_id==config_pb2.MODE_ULTIMATE
assert config.game_mode_configs[2].rgb_config==3
assert len(config.rgb_configs[2].button_colors)==0
for backend in ['XINPUT','DINPUT','NINTENDO_SWITCH','GAMECUBE']:
    matches=[c for c in config.communication_backend_configs if c.backend_id==config_pb2.CommunicationBackendId.Value('COMMS_BACKEND_'+backend)]
    assert len(matches)==1 and matches[0].default_mode_config==3
spec=json.loads((root/'friend/profile_spec.json').read_text())
spec['raw_coordinates']={name:[[128+x,128+y] for x,y in points] for name,points in spec['offsets'].items()}
spec['physical_ids']={name:config_pb2.Button.Value('BTN_'+name) for name in spec['buttons']}
expected=[(config_pb2.Button.Value('BTN_'+physical),0 if logical=='UNSPECIFIED' else config_pb2.Button.Value('BTN_'+logical)) for physical,logical in spec['physical_to_logical_remaps'].items()]
assert [(r.physical_button,r.activates) for r in config.game_mode_configs[2].button_remapping]==expected
(profile/'friend-config.json').write_text(text+'\n')
(profile/'friend_profile_normalized.json').write_text(json.dumps(spec,indent=2)+'\n')
(profile/'FRIEND_PROFILE_NORMALIZED.md').write_text((root/'FriendProfile.md').read_text())
print('REFERENCE PASS: exact target schema; full Config binary -> JSON -> binary equality; short/ordinary encoded bytes identical; length='+str(len(raw)))
print('REFERENCE PASS: normalized physical numeric IDs/remaps, source-owned raw grid, backend defaults, counts and RGB reference')
