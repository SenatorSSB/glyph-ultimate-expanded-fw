#!/usr/bin/env python3
"""Private source/custody proof supplementing actual-source runtime tests."""
import json, pathlib, subprocess
root=pathlib.Path(__file__).resolve().parents[1]
base='28ba39da5f517baa40f3dee8d868c9bb583dde4a'
def baseline(path): return subprocess.check_output(['git','show',base+':'+path],cwd=root).decode()
untouched=['src/core/config_validation.cpp','src/core/config_button_validation.cpp',
           'src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp',
           'src/core/config_usb_default_validation.cpp','HAL/pico/src/comms/backend_init.cpp','HAL/pico/src/comms/ConfiguratorBackend.cpp',
           'src/core/InputMode.cpp','src/core/ControllerMode.cpp','src/core/socd.cpp']
for path in untouched: assert (root/path).read_text()==baseline(path),path
import re
for path in ['HAL/pico/src/core/Persistence.cpp','HAL/pico/include/core/Persistence.hpp']:
    private=(root/path).read_text()
    stripped=re.sub(r'\n#if defined\(GLYPH_PRIVATE_FRIEND_STORAGE_RECOVERY\)\n.*?\n#endif\n','\n',private,flags=re.S)
    assert ''.join(stripped.split())==''.join(baseline(path).split()),'canonical Persistence semantics changed: '+path
failed='8b8d829d79810d5b4597255aabce036c6970d208'
for path in ['src/modes/Ultimate.cpp','src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp','config/glyph/common/include/glyph_overrides.hpp']:
    assert (root/path).read_bytes()==subprocess.check_output(['git','show',failed+':'+path],cwd=root),'friend gameplay changed: '+path
env=(root/'config/glyph/env.ini').read_text()
old=baseline('config/glyph/env.ini')
addition='build_flags =\n    ${glyph_base.build_flags}\n    -D GLYPH_PRIVATE_FRIEND_STORAGE_RECOVERY=1\n'
assert env.replace('[env:glyph_mk6]\nextends = glyph_base\n'+addition,'[env:glyph_mk6]\nextends = glyph_base\n')==old
path='config/glyph/common/src/config.cpp'
current=(root/path).read_text()
stripped=current.replace('#include "friend_profile_provisioning.hpp"\n','').replace('    if (!friend_profile::provision_once(config)) {\n        refuse_boot(BootOutcome::StorageFailure, display_ready);\n        return;\n    }\n','')
assert stripped==baseline(path),'only bounded provisioning hook allowed in boot path'
assert current.index('persistence.SetValidator(')<current.index('friend_profile::provision_once(config)')<current.index('persistence.LoadConfigChecked(config)')<current.index('publish_boot_state(BootOutcome::Normal')
helper=(root/'config/glyph/common/include/friend_profile_provisioning.hpp').read_text()
assert 'static Config readback;' in helper and 'readback = Config_init_default;' in helper
assert 'static uint8_t encoded_expected[16384];' in helper
assert helper.index('if (marker_valid()) return true;')<helper.index('static Config readback;')
assert 'LittleFS.exists' not in helper and 'memcmp(&' not in helper
assert helper.index('store.ValidateConfig(defaults, error)')<helper.index('store.PrivateFriendRecoverUnmountableStorage()')<helper.index('store.SaveConfig(defaults)')
spec=json.loads((root/'friend/profile_spec.json').read_text())
assert len(spec['buttons'])==34 and len(set(spec['buttons']))==34
for name,points in spec['offsets'].items():
    assert len(points)==9
    for x,y in points: assert 0<=128+x<=255 and 0<=128+y<=255
import re
test=(root/'friend/tests/harness.cpp').read_text().split('tables[9][9] = {',1)[1].split('\n};',1)[0]
pairs=[list(map(int,p)) for p in re.findall(r'\{(\d+),(\d+)\}',test)]
assert len(pairs)==81
for i,name in enumerate(['Default','X1','Y1','Y2','Tilt1','Tilt2','Tilt3','Mode','Up-smash']):
    assert pairs[i*9:(i+1)*9]==[[128+x,128+y] for x,y in spec['offsets'][name]],name
# Verify all unrelated profiles/RGB configs match the base literal initializer.
def blocks(text,start,key,end):
    section=text.split(start,1)[1].split(end,1)[0]
    return section.split(key)[1:]
path='config/glyph/common/include/glyph_overrides.hpp'
for start,key,end in [('.game_mode_configs = {','GameModeConfig {','.communication_backend_configs_count'),('.rgb_configs = {','RgbConfig {','.default_backend_config')]:
    old=blocks(baseline(path),start,key,end); new=blocks((root/path).read_text(),start,key,end)
    assert len(old)==len(new)==13
    for i in range(13):
        if i==2:continue
        # Comments/whitespace between RGB entries are not Config content.
        import re
        clean=lambda s: re.sub(r'\s+','',re.sub(r'//[^\n]*','',s))
        assert clean(old[i])==clean(new[i]),('unrelated profile/RGB changed',i)
print('SOURCE PASS: current validators/backend/refusal gates retained; Persistence canonical bodies unchanged after removing private macro block; recovery enabled only in private glyph_mk6')
print('SOURCE PASS: all gameplay/routing/table/default/RGB source byte-identical to failed snapshot; defaults validate before format; mounted bypass; no generic autoformat')
print('SOURCE PASS: static reset/readback/equality buffer; marker-present short path; no exists-only marker; no raw Config memcmp')
print('SOURCE PASS: all 34 normalized bindings, all coordinate ranges; 12 unrelated profiles and RGB configs unchanged')
