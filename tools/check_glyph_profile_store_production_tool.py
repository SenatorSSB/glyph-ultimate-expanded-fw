#!/usr/bin/env python3
"""Offline guards for the production acceptance operator; never opens a port."""
import contextlib, io, json, sys, tempfile
from pathlib import Path
from unittest.mock import patch
import glyph_profile_store_production_tool as tool
import glyph_profile_store_candidate_tool as candidate
import glyph_serial_config_tool as transport

ROOT=Path(__file__).resolve().parents[1]
def yes(x,m):
    if not x: raise AssertionError(m)
def rejected(argv):
    with contextlib.redirect_stderr(io.StringIO()):
        try: tool.parse_args(argv)
        except SystemExit: return True
    return False
def main():
  try:
    pb,jf,_=transport.load_runtime_proto_modules(ROOT)
    with tempfile.TemporaryDirectory() as d:
      d=Path(d); profile=d/'p.json'; profile.write_text('{"schemaVersion":1}')
      base=['--port','UNOPENED','--journal-out',str(d/'j.jsonl'),'create','--token','0xf000000000001d01','--incarnation','1','--store-generation','166','--name','01234567890123456789012345678901','--rank','23','--profile-json',str(profile),'--request-out',str(d/'r.json')]
      for x in ('arm','clear','pulse','replay','query','--trace','--fault-ticket','1'):
        yes(rejected([*base,x]),'retired control rejected '+x)
      a=tool.parse_args(base); m=tool.build_message(a,pb,jf)
      healthy=pb.ProfileStoreResponse(protocol_version=2,status=pb.PROFILE_STORE_OK,mutation_protocol_version=2,store_incarnation=1,store_generation=166,transaction_token_high_water=0xf000000000001d00,mutation_feasible=True)
      tool.verify_production_status(a,pb,healthy)
      # This is the old mismatch: production omits strict marker and candidate helper must still refuse it.
      try: candidate.verify_preflight(a,healthy,m)
      except transport.ToolError: pass
      else: raise AssertionError('candidate strict guard weakened')
      for field,value in [('protocol_version',1),('mutation_protocol_version',1),('store_incarnation',2),('store_generation',167),('recovery_flags',1),('mutation_feasible',False)]:
        bad=pb.ProfileStoreResponse(); bad.CopyFrom(healthy); setattr(bad,field,value)
        try: tool.verify_production_status(a,pb,bad)
        except transport.ToolError: pass
        else: raise AssertionError('bad admission accepted '+field)
      for token in ('0','0xf000000000001d00','0xffffffffffffffff'):
        bad=base.copy(); bad[bad.index('--token')+1]=token; yes(rejected(bad) if token=='0' else (not _preflight(tool,pb,jf,bad)),'token gate '+token)
      yes(rejected([*base,'--output',str(d/'j.jsonl')]),'journal/output collision')
      # Result identity failures are explicit, never a retry trigger.
      for r in (pb.ProfileStoreResponse(status=pb.PROFILE_STORE_OK,request_token=1),pb.ProfileStoreResponse(status=pb.PROFILE_STORE_OK,request_token=a.token),pb.ProfileStoreResponse(status=pb.PROFILE_STORE_CONFLICT,request_token=a.token,profile_id=9)):
        try: tool.validate_result(a,pb,r)
        except transport.ToolError: pass
        else: raise AssertionError('bad response accepted')
      good=pb.ProfileStoreResponse(status=pb.PROFILE_STORE_OK,request_token=a.token,profile_id=99); tool.validate_result(a,pb,good)
      # Receipt is created with x before any mutation request; an existing witness blocks before port use.
      (d/'r.json').write_text('existing')
      calls=[]
      class Port:
        def __init__(self,*x): self.timeout_sec=1; self.fd=-1
        def open(self): calls.append('open')
        def close(self): pass
        def flush_input(self): pass
      with patch.object(tool.transport,'PosixSerialPort',Port), patch.object(tool.candidate_transport,'request',lambda *x,**k: healthy):
        yes(tool.main(base)==1,'existing receipt fails'); yes(calls==['open'],'no mutation request after custody refusal')
      # STATUS then exactly one mutation: the immutable receipt exists before
      # the mutation boundary and there is no retry after a malformed/timeout
      # transport exception.
      (d/'r.json').unlink(); (d/'j.jsonl').unlink(); sequence=[]
      def request(_port,_pb,message,**kwargs):
        sequence.append((kwargs.get('phase'), (d/'r.json').exists()))
        if kwargs.get('phase')=='status_preflight': return healthy
        raise transport.ToolError('malformed response after transmission; unresolved')
      directory_sync=[]; original_fsync=tool.os.fsync
      def tracked_fsync(fd): directory_sync.append(fd); return original_fsync(fd)
      with patch.object(tool.transport,'PosixSerialPort',Port), patch.object(tool.candidate_transport,'request',request), patch.object(tool.os,'fsync',tracked_fsync):
        yes(tool.main(base)==1,'post-send malformed response fails')
      yes(sequence==[('status_preflight',False),('create',True)],'receipt precedes one mutation; no retry')
      yes(len(directory_sync)>=3,'receipt file and parent directory are fsynced before mutation')
    print('glyph_profile_store_production_tool: PASS offline=true strict_candidate_guard_preserved=true no_serial_opened=true')
    return 0
  except Exception as e: print('glyph_profile_store_production_tool: FAIL: '+str(e)); return 1
def _preflight(module,pb,jf,argv):
    a=module.parse_args(argv); m=module.build_message(a,pb,jf)
    try: module.verify_production_status(a,pb,pb.ProfileStoreResponse(protocol_version=2,status=pb.PROFILE_STORE_OK,mutation_protocol_version=2,store_incarnation=1,store_generation=166,transaction_token_high_water=0xf000000000001d00,mutation_feasible=True)); return True
    except transport.ToolError:return False
if __name__=='__main__': raise SystemExit(main())
