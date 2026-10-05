#!/usr/bin/env python3
"""Exact C017 repaired-current host proof; no device or firmware build action."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile, time
ROOT=Path(__file__).resolve().parents[1]
BASE='a6b7750e271324972c51915563fe0dc22f941f95'
FIXTURE='docs/runtime_config/fixtures/gp_config_017_neopixel_repaired_current.json'
FIXTURE_SHA256='8b097e9df6d0d7807e469f8ed18b362b67a6b5eb2322ad5550dd33c3204510db'
ORIGINAL_BASE_PINS={'HAL/pico/include/comms/NeoPixelBackend.hpp': {'mode': '100644', 'blob': '843eb9b937ccebc616679b0ced24b805d8a6290d', 'sha256': 'a3a83278a2f13464f6fa15de7f611ec4189f40fcf14f0ce44ce0b8e6cc890dbc'}, 'HAL/pico/include/rgb/ButtonLocations.hpp': {'mode': '100644', 'blob': 'a291b9ff6ed8482a2caa7452362eafa3077b13f1', 'sha256': '4b1a0aa989c2c162e0700b0d30c22f0f1653dc27708ad8cc51f27c97cdb6cb05'}, 'HAL/pico/src/rgb/ButtonLocations.cpp': {'mode': '100644', 'blob': 'd59b490890477b359c98c9a8c09e7f3f42e8a883', 'sha256': '348fe34ea848a08a5d03b078caf3bb2b0008f816734c53241eaa7db527ed9a6f'}, 'config/glyph/common/src/config.cpp': {'mode': '100644', 'blob': '701e4ac8c0a635b77ef4282f29109f7bb0bea726', 'sha256': 'bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5'}, 'config/glyph/env.ini': {'mode': '100644', 'blob': 'fac4e20461ad632ca1d65826241a4a9c73630f04', 'sha256': 'c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf'}, 'config/glyph/glyph_mk6/include/neopixel_definitions.hpp': {'mode': '100644', 'blob': '252c624733f2aee65be51b363f46957658957a78', 'sha256': 'f6fa43c14db9394bdc409bb63978b58a27aff340f4ba125bf27dcaedc7be6a32'}, 'docs/runtime_config/fixtures/neopixel_null_sendreport_characterization.json': {'mode': '100644', 'blob': '6646c82f303cbc9d89c91a44bd8fe6d1494f00fe', 'sha256': '92d9f40b6b548037532bc2974dd2eeaa1699f8696c9637f273e9e7d54cdf016b'}, 'platformio.ini': {'mode': '100644', 'blob': '4d56f8630c1b12e84cd12f40ce05a4dc71b9362e', 'sha256': '99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9'}, 'tools/check_glyph_neopixel_null_sendreport_characterization.py': {'mode': '100644', 'blob': '7f1ecd243c190c703d031c8376458bfccbec14d0', 'sha256': 'a6204924f1d94b4e87abc9535fe67af8e6387302f2aa98e2c48c9170c63712e8'}, 'tools/fixtures/custom_modifier_cache_host/schema/config.pb.h': {'mode': '100644', 'blob': '9b8d8eb9e771e3a791356a94681cb5c89ce93e74', 'sha256': '532f7ac324a57895caf82950ee36c6900d883a42188e5d6bbc2d3507318538f3'}, 'tools/fixtures/gp_config012_button_host/generated/config.pb.h': {'mode': '100644', 'blob': '01d0dda2ae768dd0f18c0f338a74c55e613bb199', 'sha256': 'bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323'}, 'tools/fixtures/neopixel_null_host/include/FastLED.h': {'mode': '100644', 'blob': 'e60dd96418f1def42a2b2ac4dd760873a127db09', 'sha256': '01a4ad9d08b879495c0115f2ea167704949e3bcf690d427ab4a9b21b70625f9e'}, 'tools/fixtures/neopixel_null_host/include/config.pb.h': {'mode': '100644', 'blob': '2ebb970f544622a4452410cea1822cae79c0fb46', 'sha256': '8e96d2814f29b04889c6bc25ae38faae492ede8f94631355891d7f63f5e7aa53'}, 'tools/fixtures/neopixel_null_host/include/core/CommunicationBackend.hpp': {'mode': '100644', 'blob': 'a0cad046c3fb51dd7c06006f09b90b465f7c9e76', 'sha256': '71c30c37faee0c7653d2150215c5abff49aba43454c5e436e6e95c008d858ff9'}, 'tools/fixtures/neopixel_null_host/neo_harness.cpp': {'mode': '100644', 'blob': 'c9a0ec576c7126798b9ef908cdd0b0a047baf322', 'sha256': '85f6d0922c20a20da2258cf2e871b9c35b644508a1b3b1f13b7e28529dd62c0e'}}
CURRENT_PINS={'HAL/pico/include/comms/NeoPixelBackend.hpp': {'mode': '100644', 'blob': '4724544d5989fdf403c5e6e0accab721371bc9d3', 'sha256': '71108cbd6ac17f78fd2698be5236854c292a599077f8e74f002493565953b10b'}, 'HAL/pico/include/rgb/ButtonLocations.hpp': {'mode': '100644', 'blob': 'a291b9ff6ed8482a2caa7452362eafa3077b13f1', 'sha256': '4b1a0aa989c2c162e0700b0d30c22f0f1653dc27708ad8cc51f27c97cdb6cb05'}, 'HAL/pico/src/rgb/ButtonLocations.cpp': {'mode': '100644', 'blob': 'd59b490890477b359c98c9a8c09e7f3f42e8a883', 'sha256': '348fe34ea848a08a5d03b078caf3bb2b0008f816734c53241eaa7db527ed9a6f'}, 'config/glyph/common/src/config.cpp': {'mode': '100644', 'blob': '701e4ac8c0a635b77ef4282f29109f7bb0bea726', 'sha256': 'bde443c7eceb417494ae71191a2076c0ab251e987706f30a757b14aaf16ad0e5'}, 'config/glyph/env.ini': {'mode': '100644', 'blob': 'fac4e20461ad632ca1d65826241a4a9c73630f04', 'sha256': 'c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf'}, 'config/glyph/glyph_mk6/include/neopixel_definitions.hpp': {'mode': '100644', 'blob': '252c624733f2aee65be51b363f46957658957a78', 'sha256': 'f6fa43c14db9394bdc409bb63978b58a27aff340f4ba125bf27dcaedc7be6a32'}, 'docs/runtime_config/fixtures/neopixel_null_sendreport_characterization.json': {'mode': '100644', 'blob': '6646c82f303cbc9d89c91a44bd8fe6d1494f00fe', 'sha256': '92d9f40b6b548037532bc2974dd2eeaa1699f8696c9637f273e9e7d54cdf016b'}, 'platformio.ini': {'mode': '100644', 'blob': '4d56f8630c1b12e84cd12f40ce05a4dc71b9362e', 'sha256': '99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9'}, 'tools/check_glyph_neopixel_null_sendreport_characterization.py': {'mode': '100644', 'blob': '7f1ecd243c190c703d031c8376458bfccbec14d0', 'sha256': 'a6204924f1d94b4e87abc9535fe67af8e6387302f2aa98e2c48c9170c63712e8'}, 'tools/fixtures/custom_modifier_cache_host/schema/config.pb.h': {'mode': '100644', 'blob': '9b8d8eb9e771e3a791356a94681cb5c89ce93e74', 'sha256': '532f7ac324a57895caf82950ee36c6900d883a42188e5d6bbc2d3507318538f3'}, 'tools/fixtures/gp_config012_button_host/generated/config.pb.h': {'mode': '100644', 'blob': '01d0dda2ae768dd0f18c0f338a74c55e613bb199', 'sha256': 'bdd72a220126911d7f6d2558ec5517be96189af92242979e3af43d1076550323'}, 'tools/fixtures/neopixel_null_host/include/FastLED.h': {'mode': '100644', 'blob': 'e60dd96418f1def42a2b2ac4dd760873a127db09', 'sha256': '01a4ad9d08b879495c0115f2ea167704949e3bcf690d427ab4a9b21b70625f9e'}, 'tools/fixtures/neopixel_null_host/include/config.pb.h': {'mode': '100644', 'blob': '2ebb970f544622a4452410cea1822cae79c0fb46', 'sha256': '8e96d2814f29b04889c6bc25ae38faae492ede8f94631355891d7f63f5e7aa53'}, 'tools/fixtures/neopixel_null_host/include/core/CommunicationBackend.hpp': {'mode': '100644', 'blob': 'a0cad046c3fb51dd7c06006f09b90b465f7c9e76', 'sha256': '71c30c37faee0c7653d2150215c5abff49aba43454c5e436e6e95c008d858ff9'}, 'tools/fixtures/neopixel_null_host/neo_harness.cpp': {'mode': '100644', 'blob': 'c9a0ec576c7126798b9ef908cdd0b0a047baf322', 'sha256': '85f6d0922c20a20da2258cf2e871b9c35b644508a1b3b1f13b7e28529dd62c0e'}, 'tools/fixtures/gp_config017_neopixel_repaired_current/neo_harness.cpp': {'mode': '100644', 'blob': '5c150f5c725be18f97720032c80585c9d250bb86', 'sha256': '872855d12e5d3b6dd4404403a963988da3295339c5497b9a6d6501ec33abcad7'}, 'tools/fixtures/gp_config017_neopixel_repaired_current/include/FastLED.h': {'mode': '100644', 'blob': '1b77f0d75f96c409612bce13463b47ea73b7ac6a', 'sha256': 'ab8265928fbd359362aa70dd5547ac1876d001515a79764159513ada960388db'}}
NEW_HOST=Path('tools/fixtures/gp_config017_neopixel_repaired_current')
HEADER='HAL/pico/include/comms/NeoPixelBackend.hpp'
OLD_HEADER_SHA='a3a83278a2f13464f6fa15de7f611ec4189f40fcf14f0ce44ce0b8e6cc890dbc'
REPAIRED_SHA='71108cbd6ac17f78fd2698be5236854c292a599077f8e74f002493565953b10b'
REPAIRED_BLOB='4724544d5989fdf403c5e6e0accab721371bc9d3'
NULLS=['startup_null','no_mode','no_config','zero_rgb_index','out_of_range_rgb_index','unsupported_animation','unknown_animation_enum']
VALID=['static','shift','xwave']
BRANCH='''if(_config == nullptr) {
            for (int i = 0; i < led_count; i++) {
                Button button = this->_button_mappings[i];
                _leds[i] = 0;
            }
            FastLED.setBrightness(0);
            FastLED.show();
            return;
        }'''
SPEED='uint8_t deltaHue = (diff/1000) * (interval * _config->speed);'
FROZEN=['docs/runtime_config/fixtures/neopixel_null_sendreport_characterization.json','tools/check_glyph_neopixel_null_sendreport_characterization.py','tools/fixtures/neopixel_null_host/neo_harness.cpp','tools/fixtures/neopixel_null_host/include/FastLED.h','tools/fixtures/neopixel_null_host/include/config.pb.h','tools/fixtures/neopixel_null_host/include/core/CommunicationBackend.hpp','tools/fixtures/custom_modifier_cache_host/schema/config.pb.h','tools/fixtures/gp_config012_button_host/generated/config.pb.h']
SOURCE=[HEADER,'HAL/pico/include/rgb/ButtonLocations.hpp','HAL/pico/src/rgb/ButtonLocations.cpp','config/glyph/glyph_mk6/include/neopixel_definitions.hpp','config/glyph/common/src/config.cpp']
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def require(ok,text):
    if not ok:raise AssertionError(text)
def output(path,body):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
def validate_closure(root,pins):
    for p,hashv in pins.items():
        target=root/p
        require(target.is_file() and not target.is_symlink() and not target.stat().st_mode&0o111,'input mode/type: '+p)
        require(all(not x.is_symlink() for x in target.parents),'input parent symlink: '+p)
        require(sha(target.read_bytes())==hashv,'exact input bytes: '+p)
def compile_root(root,out,ndebug=False):
    command=['c++','-std=c++20','-O1','-g','-Wall','-Wextra','-fno-omit-frame-pointer','-fsanitize=address,undefined,bounds','-fno-sanitize-recover=all','-I'+str(root/NEW_HOST/'include'),'-I'+str(root/'tools/fixtures/neopixel_null_host/include'),'-I'+str(root/'HAL/pico/include'),str(root/NEW_HOST/'neo_harness.cpp'),'-o',str(out)]
    if ndebug:command.insert(1,'-DNDEBUG')
    r=subprocess.run(command,text=True,capture_output=True)
    require(r.returncode==0,'host compile: '+r.stdout+r.stderr)
    return command
def run(binary,name):return subprocess.run([str(binary),name],text=True,capture_output=True)
def rows(result):
    require(result.returncode==0,'runtime failure: '+result.stdout+result.stderr)
    parsed=[]
    for line in result.stdout.splitlines():
        require(line.startswith('sample '),'invalid trace line')
        r=dict(x.split('=',1) for x in line.split()[1:])
        for k in ['step','from','to','diff','show_delta','brightness_delta','brightness']:r[k]=int(r[k])
        r['pixels']=[int(x,16) for x in r['pixels'].split(',')]
        r['hues']=[int(x) for x in r['hues'].split(',')]
        require(len(r['pixels'])==len(r['hues'])==76,'actual mapped pixel trace extent')
        parsed.append(r)
    require(parsed,'no traces')
    return parsed
def assert_clock(rs):
    for i,r in enumerate(rs):require((r['from'],r['to'],r['diff'])==[(1000,101000,100000),(101000,351000,250000),(351000,851000,500000),(851000,1876000,1025000)][i],'time/diff/prevTime trace')
def compare_recovery(current,reference):
    rs=rows(current); assert_clock(rs)
    require(len(rs)==3,'null-null-valid sequence extent')
    for r in rs[:2]:require(r['brightness']==0 and r['pixels']==[0]*76,'null blank/brightness behavior')
    expected=rows(reference)[0];actual=rs[-1]
    require({k:v for k,v in actual.items() if k!='step'}=={k:v for k,v in expected.items() if k!='step'},'valid-after-null exact old nonnull result/timing')
    return rs

def regular(path):
    target=ROOT/path
    require(target.is_file() and not target.is_symlink() and not target.stat().st_mode&0o111,'regular100644 input: '+path)
    require(all(not p.is_symlink() for p in target.parents),'parent symlink input: '+path)
    return target.read_bytes()
def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)
def authenticate_inputs():
    current_head=git('rev-parse','--verify','HEAD^{commit}').decode().strip()
    raw_fixture=regular(FIXTURE)
    require(sha(raw_fixture)==FIXTURE_SHA256,'immutable current fixture changed; checksum reseal is not authority')
    require(git('ls-tree',current_head,'--',FIXTURE).decode().strip()=='100644 blob '+blob(raw_fixture)+'\t'+FIXTURE,'current fixture committed HEAD mode/blob custody')
    require(git('ls-files','--stage','--',FIXTURE).decode().strip()=='100644 '+blob(raw_fixture)+' 0\t'+FIXTURE,'current fixture stage-zero custody')
    require(git('ls-files','-v','--',FIXTURE).decode().strip().startswith('H '),'fixture skip/assume custody')
    value=json.loads(raw_fixture)
    require(value['base']==BASE and value['current_pins']==CURRENT_PINS and value['original_base_pins']==ORIGINAL_BASE_PINS,'finite fixture source contract changed')
    require(git('cat-file','-t',BASE).decode().strip()=='commit','missing immutable B017 commit')
    for path,identity in ORIGINAL_BASE_PINS.items():
        entry=git('ls-tree',BASE,'--',path).decode().strip()
        require(entry=='100644 blob '+identity['blob']+'\t'+path,'immutable B017 mode/blob: '+path)
        data=git('show',BASE+':'+path)
        require(sha(data)==identity['sha256'],'immutable B017 source bytes: '+path)
    for path,identity in CURRENT_PINS.items():
        data=regular(path)
        require(sha(data)==identity['sha256'] and blob(data)==identity['blob'],'current byte/blob drift: '+path)
        require(git('ls-tree',current_head,'--',path).decode().strip()=='100644 blob '+identity['blob']+'\t'+path,'current committed HEAD mode/blob custody: '+path)
        stage=git('ls-files','--stage','--',path).decode().strip()
        require(stage=='100644 '+identity['blob']+' 0\t'+path,'current tracked stage-zero custody: '+path)
        flag=git('ls-files','-v','--',path).decode().strip()
        require(flag.startswith('H '),'skip-worktree/assume-unchanged input: '+path)
    historical=git('show',BASE+':'+HEADER)
    require(sha(historical)==OLD_HEADER_SHA,'old NeoPixel header authority')
    needle=(SPEED+'\n\n        '+BRANCH).encode()
    require(historical.count(needle)==1,'unique immutable old ordering')
    expected=historical.replace(needle,(BRANCH+'\n\n        '+SPEED).encode(),1)
    require(regular(HEADER)==expected and sha(expected)==REPAIRED_SHA and blob(expected)==REPAIRED_BLOB,'only exact null-block movement permitted')
    harness=regular(str(NEW_HOST/'neo_harness.cpp')).decode()
    require(harness.count('#include "../../../HAL/pico/include/comms/NeoPixelBackend.hpp"')==1,'literal production header include exactly once')
    require('SendReport() {' not in harness and 'NeoPixelBackend::SendReport' not in harness,'copied production method body forbidden')
    require(harness.count('#include "../../../config/glyph/glyph_mk6/include/neopixel_definitions.hpp"')==1 and harness.count('#include "../../../HAL/pico/src/rgb/ButtonLocations.cpp"')==1,'literal authenticated physical mapping/animation source')
    schema=regular('tools/fixtures/gp_config012_button_host/generated/config.pb.h').decode()
    ids=re.findall(r'\b(BTN_\w+)\s*=\s*(\d+)',schema)
    constants='\n'.join('constexpr Button '+n+' = '+v+';' for n,v in ids)
    require(len(ids)==61 and [int(v) for _,v in ids]==list(range(61)) and '// BEGIN_AUTHENTICATED_BUTTON_IDS\n'+constants+'\n// END_AUTHENTICATED_BUTTON_IDS' in harness,'host Button constants differ from immutable schema')
    require(git('rev-parse','--verify','HEAD^{commit}').decode().strip()==current_head,'HEAD changed during input authentication')
    return historical,value

def prove(temp,historical,value):
    global DRAFT
    DRAFT=temp
    old=temp/'original-root';current=temp/'repaired-root'
    pins={p:v['sha256'] for p,v in CURRENT_PINS.items()}
    pins[FIXTURE]=FIXTURE_SHA256
    oldpins=dict(pins,**{HEADER:OLD_HEADER_SHA})
    for path in pins:
        data=regular(path)
        output(current/path,data)
        output(old/path,historical if path==HEADER else data)
    validate_closure(old,oldpins);validate_closure(current,pins)
    repaired=regular(HEADER)
    report={'classification':'CURRENT_SOURCE_HOST_PROOF_ONLY','candidate_identity':'external035contract','firmware_build':'NOT_RUN','hardware_acceptance':'NOT_CLAIMED','actual_source_cases':{},'negative_controls':[]}
    commands=[]
    for ndebug in (False,True):
        label='NDEBUG-scalar-time' if ndebug else 'debug-struct-time'
        oldbin=DRAFT/('original-'+label);currentbin=DRAFT/('repaired-'+label)
        commands += [compile_root(old,oldbin,ndebug),compile_root(current,currentbin,ndebug)]
        evidence={'nine_case_categories':NULLS+['valid_static','valid_dynamic'],'valid_dynamic_actual_subcases':['RAINBOW_SHIFT','RAINBOW_XWAVE_LEFT'],'null_cases':{},'valid_multiupdate':{},'null_bookkeeping_then_valid':{}}
        for case in NULLS:
            original=run(oldbin,case)
            require(original.returncode!=0 and 'runtime error: member access within null pointer' in original.stderr and 'NeoPixelBackend.hpp' in original.stderr,'original seven-null failure preservation:'+case)
            output(DRAFT/'logs'/('original-'+label+'-'+case+'.log'),(original.stdout+original.stderr).encode())
            rs=rows(run(currentbin,case));assert_clock(rs)
            require(len(rs)==4 and all(r['pixels']==[0]*76 and r['brightness']==0 for r in rs),'repaired null blank/zero:'+case)
            evidence['null_cases'][case]={'old':'EXPECTED_SANITIZER_FAILURE','repaired':'4updates PASS','time_diff_us':[r['diff'] for r in rs]}
        for case in VALID:
            baseline=rows(run(oldbin,case));actual=rows(run(currentbin,case))
            assert_clock(actual);require(actual==baseline,'actualold/new fulltrace equality:'+case)
            require(all(r['brightness']==96 and r['show_delta']==1 and r['brightness_delta']==1 for r in actual),'valid brightness/show')
            if case=='shift':require([r['hues'][0] for r in actual]==[8,28,68,150],'nonzero SHIFT hue trajectory')
            if case=='xwave':require([r['hues'][0] for r in actual]==[32,72,152,60],'nonzero XWAVE hue trajectory/wrap')
            evidence['valid_multiupdate'][case]={'old_repaired_fulltrace':'IDENTICAL','updates':4,'time_diff_us':[r['diff'] for r in actual],'first_pixel':[r['pixels'][0] for r in actual],'first_target_hues':[r['hues'][0] for r in actual]}
            rs=compare_recovery(run(currentbin,'recovery_'+case),run(oldbin,'reference_'+case))
            evidence['null_bookkeeping_then_valid'][case]={'two_null_then_valid':'PASS','timers':[[r['from'],r['to'],r['diff']] for r in rs],'postnull_valid_fulltrace':'EXACT_OLD500ms_REFERENCE'}
        report['actual_source_cases'][label]=evidence
    report['compile_commands']=commands
    # Real filesystem substitutions/omissions against independently fixed closure.
    scratch=DRAFT/'negative-root';shutil.copytree(current,scratch,dirs_exist_ok=True)
    for p in [HEADER,str(NEW_HOST/'neo_harness.cpp'),str(NEW_HOST/'include/FastLED.h'),'tools/fixtures/neopixel_null_host/include/config.pb.h','tools/fixtures/custom_modifier_cache_host/schema/config.pb.h',FIXTURE]:
        path=scratch/p;data=path.read_bytes(); altered=bytes([data[0]^1])+data[1:]; require(len(altered)==len(data) and sum(a!=b for a,b in zip(altered,data))==1,'one-byte substitution'); path.write_bytes(altered)
        try:validate_closure(scratch,pins)
        except AssertionError:report['negative_controls'].append({'test':'substitute:'+p,'result':'REJECTED'})
        else:raise AssertionError('substituted closure accepted:'+p)
        path.write_bytes(data);path.unlink()
        try:validate_closure(scratch,pins)
        except AssertionError:report['negative_controls'].append({'test':'omit:'+p,'result':'REJECTED'})
        else:raise AssertionError('omitted closure accepted:'+p)
        path.write_bytes(data)
    mutants=[
     ('omitted_null_branch',repaired.decode().replace(BRANCH+'\n\n        ','',1),'startup_null'),
     ('omitted_null_return',repaired.decode().replace('            return;\n        }\n\n        '+SPEED,'        }\n\n        '+SPEED,1),'startup_null'),
     ('null_brightness',repaired.decode().replace('FastLED.setBrightness(0);','FastLED.setBrightness(1);',1),'startup_null'),
     ('null_blank_omitted',repaired.decode().replace('                _leds[i] = 0;','                /* omitted */',1),'startup_null'),
     ('prevTime_removed',repaired.decode().replace('        prevTime = time;','        /* removed prevTime */',1),'recovery_shift'),
     ('prevTime_after_guard',repaired.decode().replace('        prevTime = time;\n','',1).replace('        '+SPEED,'        prevTime = time;\n        '+SPEED,1),'recovery_shift'),
     ('nonnull_interval',repaired.decode().replace('float interval = 0.08;','float interval = 0.09;',1),'shift'),
     ('shift_divisor',repaired.decode().replace('_ledsHSV[i].hue += deltaHue / 2;','_ledsHSV[i].hue += deltaHue;',1),'shift'),
     ('xwave_delta',repaired.decode().replace('_ledsHSV[i].hue += deltaHue;','_ledsHSV[i].hue += deltaHue / 2;',1),'xwave'),
     ('nonnull_brightness',repaired.decode().replace('FastLED.setBrightness(_brightness);','FastLED.setBrightness(0);',1),'static'),
    ]
    for label,source,case in mutants:
        require(source.encode()!=repaired,'mutation did not apply:'+label)
        output(scratch/HEADER,source.encode())
        for ndebug in (False,True):
            binary=DRAFT/('mutant-'+label+str(ndebug));compile_root(scratch,binary,ndebug)
            r=run(binary,case);rejected=False
            try:
                rs=rows(r)
                if case.startswith('recovery_'):
                    reference=run(DRAFT/('original-'+('NDEBUG-scalar-time' if ndebug else 'debug-struct-time')),'reference_'+case[9:]);compare_recovery(r,reference)
                elif case in NULLS:
                    assert_clock(rs);require(all(x['brightness']==0 and x['pixels']==[0]*76 for x in rs),'null result mutation')
                else:
                    baseline=rows(run(DRAFT/('original-'+('NDEBUG-scalar-time' if ndebug else 'debug-struct-time')),case));require(rs==baseline,'nonnull original/repaired equality mutation')
            except AssertionError:rejected=True
            require(rejected,'runtime mutant survived:'+label+str(ndebug))
            report['negative_controls'].append({'test':label,'time_layout':'NDEBUG' if ndebug else 'debug','result':'REJECTED_ACTUAL_SOURCE_RUNTIME'})
    output(scratch/HEADER,repaired)
    # Stub behavior substitution is separately reached by the actual source caller.
    stub=scratch/NEW_HOST/'include/FastLED.h';saved=stub.read_bytes();stub.write_bytes(saved.replace(b'++show_count;',b'/* omitted show */',1))
    binary=DRAFT/'mutant-show-stub';compile_root(scratch,binary);r=run(binary,'static');require(r.returncode!=0 and 'one show per update' in r.stderr,'show stub mutation survived')
    report['negative_controls'].append({'test':'show_stub_no_increment','result':'REJECTED_ACTUAL_CALLER'});stub.write_bytes(saved)
    # Historical original closure stays byte-exact throughout preparatory tests.
    validate_closure(old,oldpins);validate_closure(current,pins)
    # Pin fixtures and harness independently of their own mutable identity fields.
    # Coordinated fixture and source reseal still fails the reviewed literal hash.
    forged=json.loads((scratch/FIXTURE).read_text())
    forged['current_pins'][HEADER]['sha256']='0'*64
    output(scratch/FIXTURE,(json.dumps(forged,indent=2)+'\n').encode())
    try: validate_closure(scratch,pins)
    except AssertionError: report['negative_controls'].append({'test':'coordinated mutable fixture reseal','result':'REJECTED'})
    else: raise AssertionError('mutable fixture reseal accepted')
    output(scratch/FIXTURE,regular(FIXTURE))
    # A copied body or missing literal include cannot stand in for actual source.
    target=scratch/NEW_HOST/'neo_harness.cpp';saved=target.read_bytes()
    for label,bad in [('copied_SendReport_body',saved+b'\nvoid NeoPixelBackend::SendReport() {}\n'),('missing_literal_include',saved.replace(b'#include "../../../HAL/pico/include/comms/NeoPixelBackend.hpp"',b'/* omitted production header */',1))]:
        require(bad!=saved,'harness mutation failed:'+label);target.write_bytes(bad)
        try: validate_closure(scratch,pins)
        except AssertionError: report['negative_controls'].append({'test':label,'result':'REJECTED'})
        else: raise AssertionError('harness source substitution accepted:'+label)
    target.write_bytes(saved)
    validate_closure(old,oldpins);validate_closure(current,pins)
    report['negative_count']=len(report['negative_controls'])
    return report

def main():
    try:
        historical,value=authenticate_inputs()
        with tempfile.TemporaryDirectory(prefix='glyph-config017-host-') as directory:
            report=prove(Path(directory),historical,value)
        for label in ('debug-struct-time','NDEBUG-scalar-time'):
            print('layout='+label+' cases=9 PASS; static+SHIFT+XWAVE fourupdates; null-null-valid timing PASS')
        print('negative_controls='+str(report['negative_count'])+' PASS; source/harness/schema/fixture omissions and single-byte substitutions; guard/bookkeeping/nonnull mutants; literal include/copied body/reseal')
        print('glyph_gp_config_017_neopixel_repaired_current: PASS; exact source/header/caller/host/dependencies; base='+BASE)
        print('physical_null_reachability=UNKNOWN FastLED_color_conversion=SYNTHETIC firmware_build=NOT_RUN hardware_acceptance=NOT_CLAIMED Nunchuk=NOT_TESTED root_cause=UNPROVEN')
        return 0
    except (AssertionError,OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as exc:
        print('glyph_gp_config_017_neopixel_repaired_current: FAIL: '+str(exc));return 1
if __name__=='__main__':raise SystemExit(main())
