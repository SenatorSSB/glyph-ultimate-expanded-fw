from pathlib import Path
import sys
sys.path.insert(0,"/private/tmp/glyph-profile-native-20261020/tools")
import check_glyph_profile_native_ultimate as c
import glyph_serial_config_tool as w
pb,jf,_=w.load_runtime_proto_modules(c.ROOT)
config,_=w.encode_artifact_payload(c.make_v3_artifact(),pb,jf)
for default in (False,True):
    out=Path('/private/tmp/glyph-native-gc-invalidated-'+('default' if default else 'short'));out.mkdir(exist_ok=True)
    exe,negative,flags,objects=c.compile_runner(out,default,True)
    c.store_tests(out,flags,objects,pb,config)
    print('PASS invalidated actual native store bothABI component='+str(default),flush=True)
    if not default:c.dispatch_tests(out,pb,config)
