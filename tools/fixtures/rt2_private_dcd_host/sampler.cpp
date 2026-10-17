#include "core/RecoveryPrivateDcdDiagnostics.hpp"
#include <cstdio>
#include <stdexcept>
#include <thread>
void require(bool x,const char*s){if(!x)throw std::runtime_error(s);}
using namespace RecoveryPrivateDcdDiagnostics;
int main(){try{
 State state;Snapshot s;RecoveryPreSetupDiagnostics::Snapshot pre;pre.valid=1;RecoverySetupIrqDiagnostics::Snapshot setup;setup.valid=1;RecoveryTaskDiagnostics::Snapshot task;task.valid=1;unsigned p[8];
 state.ReadInto(s);Panel(s,pre,setup,task,p);for(auto c:p)require(!c,"unknown means all dark");
 state.Marker(0,0);state.Marker(1,0);state.Marker(4,0);state.Marker(12,0);state.ReadInto(s);require(!s.valid&&s.entries==1&&s.returns==1,"unarmed boot-lifetime history retained but invalid publication");
 State empty;empty.Enable();empty.ReadInto(s);Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Green&&p[4]==0,"valid noentry/noRAW distinct from unknown");
 setup.independent_seen=RecoverySetupIrqDiagnostics::Sie;Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Magenta,"one raw sticky bit enough for raw positive, not simultaneity");
 state.Enable();
 state.Marker(GLYPH_DCD_PRIVATE_ENTRY,0);state.Marker(GLYPH_DCD_PRIVATE_STATUS,SetupBit|BuffBit);state.ReadInto(s);require(s.first_setup_id==2&&s.first_setup_markers==3&&s.active==2,"first status readable before earlier BUFF completion");
 Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Yellow&&p[4]==RecoveryTaskDiagnostics::Red,"prebranch residual never proof branch code failed");
 for(unsigned marker=3;marker<=12;marker++)state.Marker(marker,marker==4?1:0);
 Snapshot first;state.ReadInto(first);require((first.first_setup_markers&SetupTestTrue)&&first.first_enabled_setup_id==first.first_setup_id&&first.first_enabled_setup_markers==first.first_setup_markers,"actual true predicate and independently selected enabled first retained");
 state.Marker(0,0);state.Marker(1,0);state.Marker(4,0);state.Marker(12,0);state.ReadInto(s);require(s.first_setup_markers==first.first_setup_markers&&s.first_setup_status==first.first_setup_status&&s.latest_status==0&&(s.latest_markers&SetupTestFalse),"later nonSETUP invocation cannot overwrite first setup witness");
 state.Marker(0,0);state.Marker(1,SetupBit);state.Marker(4,1);state.Marker(5,0);state.ReadInto(s);require(s.latest_setup_id==4&&s.first_setup_id==2&&s.latest_setup_markers!=s.first_setup_markers,"latest selected SETUP separate from immutable first progress");
 pre.panic_kind=1;Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Red,"external panic retained");
 // A real parallel writer can invalidate this single bounded read; valid
 // snapshots still retain invocation tuples. No retry loop in production API.
 std::thread writer([&]{for(unsigned i=0;i<5000;i++){state.Marker(12,0);state.Marker(0,0);state.Marker(1,SetupBit);state.Marker(4,1);}});
 for(unsigned i=0;i<5000;i++){state.ReadInto(s);if(s.valid)require(s.returns<=s.entries&&s.latest_id==s.entries&&s.first_setup_id==2,"coherent bounded snapshot under writer interleave");}writer.join();
 std::puts("private_sampler_panel_first_latest_bounded_concurrent_read=PASS");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
