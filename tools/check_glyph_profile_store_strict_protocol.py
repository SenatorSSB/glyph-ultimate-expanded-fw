#!/usr/bin/env python3
"""Exercise real backend, nanopb, PacketIO and ProfileStore strict transactions."""
from pathlib import Path
import sys
import tempfile
from check_glyph_profile_store_timeout_resynchronization import build_and_run, ROOT, NANOPB, run, make_v3_artifact

def main():
    try:
        with tempfile.TemporaryDirectory(prefix='glyph-strict-protocol-') as directory:
            temp=Path(directory);generated=temp/'generated';generated.mkdir();schema=ROOT/'schema/haybox'
            run([sys.executable,str(NANOPB/'generator/nanopb_generator.py'),'-I',str(schema),'-f',str(schema/'config.options'),'--error-on-unmatched','--no-timestamp','-D',str(generated),str(schema/'config.proto')])
            import glyph_serial_config_tool as writer
            pb,json,_=writer.load_runtime_proto_modules(ROOT)
            _,payload=writer.encode_artifact_payload(make_v3_artifact(),pb,json)
            fixture=temp/'fixture.pb';fixture.write_bytes(payload)
            build_and_run(temp,generated,fixture,False,strict_only=True)
            build_and_run(temp,generated,fixture,False,strict_only=True,candidate_faults=True)
        print('glyph_profile_store_strict_protocol: PASS')
        return 0
    except Exception as error:
        print(f'glyph_profile_store_strict_protocol: FAIL: {error}')
        return 1
if __name__=='__main__': raise SystemExit(main())
