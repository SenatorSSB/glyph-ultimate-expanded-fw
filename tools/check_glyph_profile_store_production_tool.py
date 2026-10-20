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
      for field in ('resource_diagnostics_enabled','storage_fault_armed','storage_fault_triggered','storage_fault_operation','storage_fault_capable','storage_fault_ticket','storage_fault_pending','fault_control_version','liveness_stage','liveness_value','rx_phase','rx_raw_bytes','rx_decoded_bytes','rx_elapsed_ms','rx_task_passes','rx_last_progress_ms','rx_fetched_bytes','rx_flags'):
        bad=pb.ProfileStoreResponse(); bad.CopyFrom(healthy); setattr(bad,field,True if field.endswith(('enabled','armed','triggered','capable','pending')) else 1)
        try: tool.verify_production_status(a,pb,bad)
        except transport.ToolError: pass
        else: raise AssertionError('retired telemetry accepted '+field)
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
      # Existing protocol operations10/9 have their own explicit fences and no payload.
      for action in ('set-reference','delete'):
        argv=['--port','UNOPENED','--journal-out',str(d/(action+'.jsonl')),action,'--profile-id','99','--token','101','--incarnation','1','--store-generation','166','--request-out',str(d/(action+'.json'))]
        if action=='set-reference':argv+=['--mode-index','0','--config-generation','77']
        args=tool.parse_args(argv); message=tool.build_message(args,pb,jf)
        yes(message.operation==(10 if action=='set-reference' else 9) and message.profile_id==99 and not message.HasField('profile'),'existing bounded operation/no payload')
        status=pb.ProfileStoreResponse();status.CopyFrom(healthy);status.transaction_token_high_water=100;status.config_generation=77
        tool.verify_production_status(args,pb,status)
        if action=='set-reference':
          status.config_generation=78
          try:tool.verify_production_status(args,pb,status)
          except transport.ToolError:pass
          else:raise AssertionError('reference Config fence ignored')
          status.config_generation=77
          for flag in ('--mode-index','--config-generation','--profile-id'):
            missing=argv.copy();i=missing.index(flag);del missing[i:i+2];yes(rejected(missing),'missing explicit reference '+flag)
        yes(rejected([*argv,'--profile-json',str(profile)]),'reference/delete reject body')
        calls=[]
        def checked_request(_port,_pb,m,**kwargs):
          calls.append((m.operation,(d/(action+'.json')).exists()))
          if m.operation==pb.PROFILE_STORE_STATUS:return status
          return pb.ProfileStoreResponse(status=pb.PROFILE_STORE_OK,request_token=101,profile_id=99)
        with patch.object(tool.transport,'PosixSerialPort',Port),patch.object(tool.candidate_transport,'request',checked_request):
          yes(tool.main(argv)==0,'checked existing operation succeeds')
        yes([x for x in calls if isinstance(x,tuple)]==[(pb.PROFILE_STORE_STATUS,False),(message.operation,True)],'checked reference/delete immutable receipt before exactly one mutation')
      # Native/compact context path changes only one existing row's preprocessing.
      # The old legacy fixture binding validator is deliberately still strict.
      from check_glyph_stage_b_ultimate_profiles import make_v3_artifact
      original=pb.Config();jf.ParseDict(make_v3_artifact(),original)
      del original.ultimate_profiles[:]
      original.ultimate_profile_store_format=1;original.ultimate_profile_store_incarnation=1;original.ultimate_profile_root_format=2
      for row in original.game_mode_configs:row.ultimate_profile_config=0
      original.profile_reference_token=11
      raw=original.SerializeToString(deterministic=True)
      packet=ROOT/'docs/runtime_config/profile_native_ultimate/candidate_fixture_packet/forced_wins'
      context=json.loads((packet/'context.json').read_text());native=json.loads((packet/'profile.json').read_text())
      payload=transport.prepare_native_context(raw,0,context,native,pb,jf)
      changed=pb.Config();changed.ParseFromString(payload)
      yes(not changed.game_mode_configs[0].button_remapping and not changed.game_mode_configs[0].socd_pairs,'empty forced native context admitted')
      yes(changed.game_mode_configs[0].ultimate_profile_id==original.game_mode_configs[0].ultimate_profile_id and changed.game_mode_configs[0].ultimate_profile_engine==original.game_mode_configs[0].ultimate_profile_engine,'context does not select ID/engine')
      yes(bool(transport.verify_required_bindings(changed,pb)),'historical legacy binding policy unchanged')
      for bad in ({**context,'ultimateProfileId':99},{**context,'mode_id':'MODE_MELEE'},{**context,'button_remapping':[{'physical_button':61,'activates':1}]}):
        try:transport.prepare_native_context(raw,0,bad,native,pb,jf)
        except Exception:pass
        else:raise AssertionError('native context whitelist/domain/digest negative')
      changed.profile_reference_token=99;changed.profile_reference_result_id=15
      current=changed.SerializeToString(deterministic=True)
      restored=pb.Config();restored.ParseFromString(transport.prepare_native_restore(current,raw,pb))
      yes(restored.profile_reference_token==99 and restored.profile_reference_result_id==15 and list(restored.game_mode_configs[0].button_remapping)==list(original.game_mode_configs[0].button_remapping),'restore original context preserves firmware-owned monotonic receipts')
      import base64,hashlib
      backup=d/'current-backup.json';backup.write_text(json.dumps({'rawConfigPayloadBase64':base64.b64encode(raw).decode()}))
      contextfile=d/'context.json';contextfile.write_text(json.dumps(context));nativefile=d/'native.json';nativefile.write_text(json.dumps(native))
      command=['--expected-current-backup',str(backup),'--expected-current-sha256',hashlib.sha256(raw).hexdigest(),'--session','offline-owned-session','--mode-index','0','--context-json',str(contextfile),'--native-profile-json',str(nativefile)]
      def context_command(name):return [*command,'--receipt-out',str(d/(name+'.receipt')),'--journal-out',str(d/(name+'.journal'))]
      opened=[]
      class NativePort:
        def __init__(self,*x):pass
        def open(self):opened.append(True)
        def flush_input(self):pass
        def close(self):pass
      with patch.object(transport,'PosixSerialPort',NativePort):
        yes(transport.native_packet_main(context_command('dry'))==0 and not opened,'native context dry-run no serial')
        yes(transport.native_packet_main([*context_command('noguard'),'--execute','--port','UNOPENED'])==1 and not opened,'execution requires exclusive Configurator session')
      status=pb.ProfileStoreResponse();status.CopyFrom(healthy);status.store_incarnation=1
      sequence=[]
      def get_config(_):sequence.append('get');return raw if sequence.count('get')==1 else payload
      def set_config(_,body):sequence.append('set');yes(body==payload and (d/'commit.receipt').exists(),'native receipt before exact payload')
      with patch.object(transport,'PosixSerialPort',NativePort),patch.object(tool.candidate_transport,'request',lambda *x,**k:status),patch.object(transport,'request_get_config',get_config),patch.object(transport,'request_set_config',set_config):
        yes(transport.native_packet_main([*context_command('commit'),'--execute','--exclusive-configurator-session','--port','UNOPENED'])==0,'native context actual existing command mock path')
      yes(sequence==['get','set','get'],'one Config write with fresh preflight/readback')
      sequence=[]
      def uncertain_set(*x):sequence.append('set');raise transport.ToolError('lost acknowledgement')
      with patch.object(transport,'PosixSerialPort',NativePort),patch.object(tool.candidate_transport,'request',lambda *x,**k:status),patch.object(transport,'request_get_config',lambda _:raw),patch.object(transport,'request_set_config',uncertain_set):
        yes(transport.native_packet_main([*context_command('uncertain'),'--execute','--exclusive-configurator-session','--port','UNOPENED'])==1,'uncertain Config write stops')
      yes(sequence==['set'],'no Config mutation retry')
      sequence=[]
      with patch.object(transport,'PosixSerialPort',NativePort),patch.object(tool.candidate_transport,'request',lambda *x,**k:status),patch.object(transport,'request_get_config',lambda _:b'changed'),patch.object(transport,'request_set_config',lambda *x:sequence.append('set')):
        yes(transport.native_packet_main([*context_command('stale'),'--execute','--exclusive-configurator-session','--port','UNOPENED'])==1 and not sequence,'stale backup refuses Config write')
      # Restoration uses the original captured backup but preserves current
      # firmware-owned receipts; it never restores a stale transaction token.
      original_backup=d/'original-backup.json';original_backup.write_text(backup.read_text())
      current_backup=d/'after-backup.json';current_backup.write_text(json.dumps({'rawConfigPayloadBase64':base64.b64encode(current).decode()}))
      restore_command=['--expected-current-backup',str(current_backup),'--expected-current-sha256',hashlib.sha256(current).hexdigest(),'--session','offline-restore','--restore-original-backup',str(original_backup),'--original-sha256',hashlib.sha256(raw).hexdigest(),'--receipt-out',str(d/'restore.receipt'),'--journal-out',str(d/'restore.journal')]
      with patch.object(transport,'PosixSerialPort',NativePort):
        yes(transport.native_packet_main(restore_command)==0,'actual restore CLI dry-run')
      yes(json.loads((d/'restore.receipt').read_text())['payload_sha256']==hashlib.sha256(restored.SerializeToString(deterministic=True)).hexdigest(),'restore CLI exact reviewed payload')
      other=pb.Config();other.CopyFrom(original);other.ultimate_profile_store_incarnation=2
      try:transport.prepare_native_restore(current,other.SerializeToString(),pb)
      except transport.ToolError:pass
      else:raise AssertionError('restore accepts another incarnation')
    print('glyph_profile_store_production_tool: PASS offline=true strict_candidate_guard_preserved=true no_serial_opened=true')
    return 0
  except Exception as e: print('glyph_profile_store_production_tool: FAIL: '+str(e)); return 1
def _preflight(module,pb,jf,argv):
    a=module.parse_args(argv); m=module.build_message(a,pb,jf)
    try: module.verify_production_status(a,pb,pb.ProfileStoreResponse(protocol_version=2,status=pb.PROFILE_STORE_OK,mutation_protocol_version=2,store_incarnation=1,store_generation=166,transaction_token_high_water=0xf000000000001d00,mutation_feasible=True)); return True
    except transport.ToolError:return False
if __name__=='__main__': raise SystemExit(main())
