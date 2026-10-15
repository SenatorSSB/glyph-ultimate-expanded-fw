#!/usr/bin/env python3
"""Offline request/bound/guard proof. Does not open a serial port."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import glyph_profile_store_candidate_tool as candidate
import glyph_serial_config_tool as transport

ROOT=Path(__file__).resolve().parents[1]
def require(ok,message):
    if not ok:raise AssertionError(message)
def rejected(argv):
    with contextlib.redirect_stderr(io.StringIO()):
        try:candidate.parse_args(argv)
        except SystemExit as error:return error.code!=0
    return False

def main():
    try:
        pb,json_format,_=transport.load_runtime_proto_modules(ROOT)
        with tempfile.TemporaryDirectory(prefix='glyph-candidate-cli-') as directory:
            profile=Path(directory)/'profile.json';profile.write_text(json.dumps({'response':{'profile':{'schemaVersion':1}}}))
            base=['--port','UNOPENED','create','--token','0x100000009','--store-generation','8','--incarnation','1','--name','ä'*16,'--rank','0','--profile-json',str(profile),'--request-out',str(Path(directory)/'request.json')]
            args=candidate.parse_args(base);request,host=candidate.build_message(args,pb,json_format)
            require(request.protocol_version==2 and request.request_token==0x100000009 and request.expected_store_generation==8 and request.expected_store_incarnation==1,'explicit mutation fences/full token')
            require(request.HasField('profile') and request.profile.schema_version==1 and len(request.name.encode('utf-8'))==32,'READ export profile and byte bound')
            payload=request.SerializeToString(deterministic=True)
            saved={'receipt_format':1,'incarnation':request.expected_store_incarnation,'request_hex':payload.hex(),'request_sha256':host['transmitted_request_sha256'],'decoded_request':json_format.MessageToDict(request,preserving_proto_field_name=True)}
            receipt=Path(directory)/'receipt.json';receipt.write_text(json.dumps(saved))
            replay_args=candidate.parse_args(['--port','UNOPENED','replay','--replay-request',str(receipt)])
            replay,replay_host=candidate.build_message(replay_args,pb,json_format)
            later=pb.ProfileStoreResponse(strict_hardening_candidate=True,mutation_protocol_version=2,store_incarnation=1,store_generation=99,transaction_token_high_water=0x100000099)
            candidate.verify_preflight(replay_args,later,replay)
            try:candidate.verify_preflight(args,later,request)
            except transport.ToolError:pass
            else:raise AssertionError('ordinary mutation incorrectly bypassed fresh fences')
            require(replay_host['_exact_payload']==payload and replay.request_token==request.request_token and replay.expected_store_generation==8,'exact replay preserves old bytes/token/expectations')
            require(len(host['profile_file_sha256'])==64 and len(host['transmitted_request_sha256'])==64,'source/wire custody hashes')
            require(rejected([*base[:base.index('--name')],'--name','ä'*17,*base[base.index('--rank'):]]),'excess UTF8 bytes refused')
            for option in ('--token','--incarnation','--store-generation'):
                bad=base.copy();bad[bad.index(option)+1]='0' if option!='--store-generation' else '0x100000000'
                require(rejected(bad),'invalid mutation bound refused')
            bad=base.copy();bad.extend(['--profile-sha256','0'*64])
            try:candidate.build_message(candidate.parse_args(bad),pb,json_format)
            except transport.ToolError:pass
            else:raise AssertionError('changed source digest accepted')
            args=candidate.parse_args(['--port','UNOPENED','list','--page','8','--page-size','8']);request,_=candidate.build_message(args,pb,json_format)
            require(request.page_cursor==8 and request.page_size==8,'paged backup request')
            for action in ('update','duplicate'):
                require(rejected(['--port','UNOPENED',action,'--profile-id','1','--token','9','--store-generation','8','--incarnation','1']),'revision/source guards')
            require(rejected(['--port','UNOPENED','query','--token','0']),'zero query token refused')
        print('glyph_profile_store_candidate_tool: PASS offline=true serial_opened=false explicit_fences=true utf8_bound=true source_hash_guard=true paged_backup=true exact_replay_bypasses_fresh_fences=true')
        return 0
    except Exception as error:
        print(f'glyph_profile_store_candidate_tool: FAIL: {error}');return 1
if __name__=='__main__':raise SystemExit(main())
