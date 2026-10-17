#define GLYPH_RECOVERY_DIAGNOSTICS_HOST 1
#include "core/RecoveryPrivateDcdDiagnostics.hpp"
#include <cstdio>
#include <stdexcept>
#include <thread>
void require(bool x,const char*s){if(!x)throw std::runtime_error(s);}
namespace RecoveryPrivateDcdDiagnostics {
struct StateTestAccess {
 static void Sequence(State &s,uint32_t n){s.seq.store(n,std::memory_order_relaxed);}
};
}
using namespace RecoveryPrivateDcdDiagnostics;
int main(){try{
 static_assert(sizeof(State)==100&&sizeof(Snapshot)==96,"fixed bank and 24-word wire record");
 State state;Snapshot s;RecoveryPreSetupDiagnostics::Snapshot pre;pre.valid=1;RecoverySetupIrqDiagnostics::Snapshot setup;setup.valid=1;RecoveryTaskDiagnostics::Snapshot task;task.valid=1;unsigned p[8];
 state.Marker(GLYPH_DCD_PRIVATE_ENTRY,0);state.ReadInto(s);require(!s.entries&&!s.marker_calls,"obsolete ENTRY ignored rather than pre-status telemetry");
 state.ReadInto(s);Panel(s,pre,setup,task,p);for(auto c:p)require(!c,"unknown means all dark");
 state.Marker(1,0);state.Marker(4,0);state.Marker(12,0);state.ReadInto(s);require(!s.valid&&s.entries==1&&s.returns==1,"unarmed boot-lifetime history retained but invalid publication");
 State odd;odd.Enable();StateTestAccess::Sequence(odd,1);s.valid=42;s.entries=42;odd.ReadInto(s);
 require(!s.valid&&!s.entries,"odd writer bank is invalid with cleared caller output and no retry");
 StateTestAccess::Sequence(odd,2);odd.ReadInto(s);require(s.valid&&!s.entries,"closed empty bank readable after odd publication completes");
 State empty;empty.Enable();empty.ReadInto(s);Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Green&&p[4]==0,"valid noentry/noRAW distinct from unknown");
 setup.independent_seen=RecoverySetupIrqDiagnostics::Sie;Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Magenta,"one raw sticky bit enough for raw positive, not simultaneity");
 state.Enable();
 state.Marker(GLYPH_DCD_PRIVATE_STATUS,SetupBit|BuffBit);state.ReadInto(s);require(s.first_setup_id==2&&s.first_setup_markers==3&&s.active==2,"first status readable before earlier BUFF completion");
 Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Yellow&&p[4]==RecoveryTaskDiagnostics::Red,"prebranch residual never proof branch code failed");
 for(unsigned marker=3;marker<=12;marker++)state.Marker(marker,marker==4?1:0);
 Snapshot first;state.ReadInto(first);require((first.first_setup_markers&SetupTestTrue)&&first.first_enabled_setup_id==first.first_setup_id&&first.first_enabled_setup_markers==first.first_setup_markers,"actual true predicate and independently selected enabled first retained");
 state.Marker(1,0);state.Marker(4,0);state.Marker(12,0);state.ReadInto(s);require(s.first_setup_markers==first.first_setup_markers&&s.first_setup_status==first.first_setup_status&&s.latest_status==0&&(s.latest_markers&SetupTestFalse),"later nonSETUP invocation cannot overwrite first setup witness");
 state.Marker(1,SetupBit);state.Marker(4,1);state.Marker(5,0);state.ReadInto(s);require(s.latest_setup_id==4&&s.first_setup_id==2&&s.latest_setup_markers!=s.first_setup_markers,"latest selected SETUP separate from immutable first progress");
 pre.panic_kind=1;Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Red,"external panic retained");
 // A real parallel writer can invalidate this single bounded read; valid
 // snapshots still retain invocation tuples. No retry loop in production API.
 State concurrent;concurrent.Enable();
 std::thread writer([&]{for(unsigned i=0;i<5000;i++){
   const uint32_t value=(i&1u)?ResetBit:(SetupBit|BuffBit);
   concurrent.Marker(1,value);concurrent.Marker(4,(value&SetupBit)?1u:0u);concurrent.Marker(12,0);
 }});
 for(unsigned i=0;i<5000;i++){
   concurrent.ReadInto(s);
   if(s.valid){
     require(s.returns<=s.entries&&s.entries-s.returns<=1&&s.latest_id==s.entries,"coherent bounded invocation tuple under writer interleave");
     require(s.setup_status_count+s.reset_status_count==s.entries&&s.buff_status_count==s.setup_status_count&&s.multi_status_count==s.setup_status_count,"counts belong to the same closed transaction");
     if(s.entries)require(s.latest_status==((s.entries&1u)?SetupBit|BuffBit:ResetBit)&&s.first_setup_id==1,"mixed alternating ID/status and immutable first setup rejected");
   }
 }
 writer.join();concurrent.ReadInto(s);require(s.valid&&s.entries==5000&&s.returns==5000,"final closed concurrent history readable without retry");
 std::puts("private_sampler_panel_first_latest_bounded_concurrent_read=PASS");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
