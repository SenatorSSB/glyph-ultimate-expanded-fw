#!/usr/bin/env python3
"""Offline candidate-fixture preparation only; no serial/device/write operation."""
from pathlib import Path
import sys,json,hashlib,tempfile,subprocess,re,itertools
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
import glyph_serial_config_tool as writer
import check_glyph_profile_native_ultimate as check
from convert_glyph_native_ultimate_profile import convert
OUT=Path(__file__).parent/'candidate_fixture_packet'

def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data if isinstance(data,bytes) else (json.dumps(data,indent=2,sort_keys=True)+'\n').encode())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=True);pb,jf,_=writer.load_runtime_proto_modules(ROOT)
    config,_=writer.encode_artifact_payload(check.make_v3_artifact(),pb,jf);source=config.ultimate_profiles[0]
    names={v.number:v.name for v in pb.Button.DESCRIPTOR.values}
    packages=[];observations=[]
    with tempfile.TemporaryDirectory(prefix='native-packet-') as directory:
        temp=Path(directory);exe,_,flags,objects=check.compile_runner(temp)
        # Packet observations initialize actual OutputState buttons tozero.
        text=(check.HOST/'native_runner.cpp').read_text().replace('0xa0030000','0')
        path=temp/'packet_runner.cpp';path.write_text(text);exe=temp/'packet-runner'
        sources=['src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp','src/core/config_button_validation.cpp']
        check.run(['c++','-std=c++17',*flags,str(path),*[str(ROOT/s) for s in sources],str(temp/'legacy.o'),*objects,'-o',str(exe)])
        # Compile literal production serializer assignments and literal report
        # types. SDK/USB/poll transport is deliberately absent in this host proof.
        switch=(ROOT/'HAL/pico/include/comms/NintendoSwitchBackend.hpp').read_text();switch=switch[switch.index('typedef enum'):switch.index('class NintendoSwitchBackend')]
        xi=(ROOT/'.pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/include/Adafruit_USBD_XInput.hpp').read_text();xi=xi[xi.index('typedef struct __attribute((packed, aligned(1)))'):xi.index('} xinput_report_t;')+len('} xinput_report_t;')]
        gc=(ROOT/'.pio/libdeps/glyph_mk6/joybus-pio/include/gamecube_definitions.h').read_text();gc=gc[gc.index('typedef struct __attribute__((packed))'):gc.index('} gc_report_t;')+len('} gc_report_t;')]
        snippets=[];backend_sources={}
        for label,relative,kind,end in [('XInput','HAL/pico/src/comms/XInputBackend.cpp','xinput_report_t','    if(timeout)'),('Switch','HAL/pico/src/comms/NintendoSwitchBackend.cpp','switch_gamepad_report_t','    TUCompositeHID::_usb_hid.sendReport'),('Gamecube','HAL/pico/src/comms/GamecubeBackend.cpp','gc_report_t','    // Send outputs')]:
            text=(ROOT/relative).read_text();body=text[text.index('    // Digital outputs'):text.index(end)]
            fields=list(dict.fromkeys(re.findall(r'_report\.(\w+)\s*=',body)))
            body=body.replace('_report.','r.').replace('_outputs.','o.')
            snippets.append('void '+label+'(const OutputState &o){'+kind+' r{};'+body+'std::printf("{\\"backend\\":\\"'+label+'\\",\\"fields\\":{");'+''.join('std::printf("'+(',' if i else '')+'\\"'+f+'\\":%d",int(r.'+f+'));' for i,f in enumerate(fields))+'std::puts("}}");}\n')
            backend_sources[relative]=sha(ROOT/relative)
        text=(ROOT/'HAL/pico/src/comms/NintendoSwitchBackend.cpp').read_text();hat=text[text.index('switch_gamepad_hat_t NintendoSwitchBackend::GetHatPosition'):].replace('NintendoSwitchBackend::GetHatPosition','GetHatPosition')
        serializer=temp/'serializer.cpp';serializer.write_text('#include "core/state.hpp"\n#include <cstdio>\n#include <cstdlib>\n'+switch+xi+gc+hat+'\n'+''.join(snippets)+'int main(int n,char **v){if(n!=8)return 1;OutputState o;o.buttons=std::strtoul(v[1],nullptr,16);for(int i=0;i<6;++i)o.analog_axes[i]=std::atoi(v[i+2]);XInput(o);Switch(o);Gamecube(o);}')
        serializer_exe=temp/'serializer';check.run(['c++','-std=c++17',*flags,str(serializer),'-o',str(serializer_exe)])
        # Complete baseline/rebound packages, six explicit clean SOCD packages,
        # forcedtable win/lose/filter and twocomplete physical capacity samples.
        def package(name,profile,context,policy='historical_compatibility',options=None,complete=None):
            native,report=convert(profile,context,pb,policy,options=options)
            if complete is not None:native=check.complete_profile(native,pb,complete)
            folder=OUT/name;wire=folder/'profile.pb';save(wire,native.SerializeToString(deterministic=True));save(folder/'profile.json',jf.MessageToDict(native,preserving_proto_field_name=True));save(folder/'context.pb',context.SerializeToString());save(folder/'context.json',jf.MessageToDict(context,preserving_proto_field_name=True));save(folder/'conversion.json',report)
            record={'name':name,'profile_sha256':sha(wire),'body_sha256':hashlib.sha256(native.native_payload).hexdigest(),'wrapper_bytes':wire.stat().st_size,'policy':policy,'context_sha256':sha(folder/'context.pb'),'complete_sample':complete};packages.append(record)
            return name
        context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
        package('compatibility',source,context)
        rebound=pb.UltimateProfile();rebound.CopyFrom(source)
        carriers=[18,19,20,24,25,34,35,36,37,41,42,43,44,45];mapping=dict(zip(carriers,carriers[3:]+carriers[:3]))
        for slot in rebound.routing_slots:slot.input_token=mapping.get(slot.input_token,slot.input_token)
        package('rebound',rebound,context);save(OUT/'rebound/explicit_routing_change.json',mapping)
        for policy in range(6):
            c=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE);c.button_remapping.add(physical_button=38,activates=5);c.button_remapping.add(physical_button=27,activates=5);c.socd_pairs.add(button_dir1=5,button_dir2=2,socd_type=policy)
            package('clean_socd_'+str(policy),source,c,'clean_down_a',{'physical_input':38,'down_input':5,'up_input':2})
        for name,priority,filtered in [('forced_wins',5,False),('forced_loses',254,False),('forced_filter',254,True)]:
            options={'physical_input':49,'table_id':3,'table_priority':priority,'forced_x':79,'forced_y':81}
            if filtered:options['a_winner_table']=3
            package(name,source,context,'forced_table_down_a',options)
        for variant in (1,2):
            c=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE);c.socd_pairs.add(button_dir1=49,button_dir2=2,socd_type=1)
            package('complete_sample_'+str(variant),source,c,complete=variant)
        def sequence(name,row,stimuli):
            folder=OUT/name;frames=temp/'frames.txt';frames.write_text(''.join(f'{sum(1<<(i-1) for i in set(ids)):x}\n' for ids in stimuli))
            rows=check.run([str(exe),str(folder/'profile.pb'),'sequence',str(folder/'context.pb'),str(frames)]).splitlines()
            for step,(ids,output) in enumerate(zip(stimuli,rows)):
                values=output.split();raw={'buttons_hex':values[0],'leftStickX':int(values[1]),'leftStickY':int(values[2]),'rightStickX':int(values[3]),'rightStickY':int(values[4]),'triggerLAnalog':int(values[5]),'triggerRAnalog':int(values[6])}
                reports=[json.loads(x) for x in check.run([str(serializer_exe),*values]).splitlines()]
                observations.append({'row':row,'package':name,'sequence_step':step,'original_input_ids':ids,'original_inputs':[names[i] for i in ids],'expected_output_state':raw,'expected_backend_assignment_fields':reports,'observed':None,'result':'NOT_TESTED'})
        directions=[[],[3],[1],[5],[2],[3,5],[3,2],[1,5],[1,2]]
        modifiers=[[],[37],[36],[34],[35],[20],[41],[20,41],[24],[35,19],[35,20],[37,36],[37,35],[20,41,24],[22],[23],[25],[29],[38],[21],[19,42,43]]
        for name in ('compatibility','rebound'):
            for m in modifiers:
                for d in directions:
                    ids=m+d
                    if name=='rebound':ids=[mapping.get(i,i) for i in ids]
                    sequence(name,'H2/H3/H7' if name=='compatibility' else 'H8',[ids])
        for policy in range(6):sequence('clean_socd_'+str(policy),'H4',[[],[38],[38,2],[2],[],[2],[38,2],[38],[],[27],[27,38],[27,38,2],[]])
        for name in ('forced_wins','forced_loses','forced_filter'):sequence(name,'H5',[[],[49],[49,24],[49,5],[49,2],[24],[]])
        for name in ('complete_sample_1','complete_sample_2'):sequence(name,'H6/H9',[[],[51],[49],[49,2],[50],[49,50],[49,50,51],[2],[]])
        # Actual serializer distinctions, independently asserted from source
        # assignments: L/Rdigital are not shoulderL/Z; rawaxes remain distinct.
        reports=[json.loads(x) for x in check.run([str(serializer_exe),'000000e0','79','81','128','128','17','23']).splitlines()]
        by={r['backend']:r['fields'] for r in reports}
        assert by['Gamecube']['l']==by['Gamecube']['r']==by['Gamecube']['z']==1
        assert by['Gamecube']['l_analog']==17 and by['Gamecube']['r_analog']==23
        assert by['XInput']['lt']==by['XInput']['rt']==255 and by['XInput']['rb']==1
        assert by['Switch']['zl']==by['Switch']['zr']==by['Switch']['r']==1
        save(OUT/'backend_LR_Z_source_assertions.json',{'status':'PASS_HOST_SOURCE_ASSIGNMENTS_ONLY','reports':reports,'backend_source_hashes':backend_sources})
        save(OUT/'profiles.json',packages);save(OUT/'expected_observations.json',observations)
        save(OUT/'manifest.json',{'state':'OFFLINE_PREPARATION_NOT_APPROVED_FOR_DEVICE','source_checkpoint':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'runtime_route_context':{'available_owner_report':['XInput','Switch','Gamecube'],'controller_revision':None,'host_details':None,'adapter_details':None},'target_timing':'NOT_MEASURED','target_whole_stack_peak':'NOT_MEASURED','files':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'},'limitations':['Exact reviewed candidate/tree/UF2/custody and packet approval pending.','Expected rawoutputs use production native decoder/evaluator with initial buttons0; eachsequence starts from fresh mode history.','Backend fields are actual source assignments/types executed on host; USB/PIO timing and targetwirelayout are not hardware proof.','Nunchuk NOT_TESTED. No targettiming/highwater facility is implemented.','H1/H10/H11/H12 need actual session/backup/reference/negative/restoration evidence; no unsafe corrupting fixture is proposed.']})
        print(f'PASS offline fixtures packages={len(packages)} fulloutputobservations={len(observations)}; actual3backend assignments/LR/Z assertions; no device')
if __name__=='__main__':main()
