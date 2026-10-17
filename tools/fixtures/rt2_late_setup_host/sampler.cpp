#define GLYPH_RECOVERY_DIAGNOSTICS_HOST 1
#include "core/RecoveryPrivateDcdDiagnostics.hpp"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <thread>
void require(bool x,const char*s){if(!x)throw std::runtime_error(s);}
namespace RecoveryPrivateDcdDiagnostics {
struct StateTestAccess {
 static void Sequence(State&s,uint32_t n){s.seq.store(n,std::memory_order_relaxed);}
 static void Counts(State&s,uint32_t n){
  s.entries.store(n,std::memory_order_relaxed);s.returns.store(n,std::memory_order_relaxed);
  s.setup_status_count.store(n,std::memory_order_relaxed);s.reset_status_count.store(n,std::memory_order_relaxed);
  s.buff_status_count.store(n,std::memory_order_relaxed);s.late_count.store(n,std::memory_order_relaxed);
 }
};
}
using namespace RecoveryPrivateDcdDiagnostics;
int main(){try{
 static_assert(sizeof(State)==68&&sizeof(Snapshot)==64,"fixed bank and sixteen-word snapshot");
 State state;Snapshot s;RecoveryPreSetupDiagnostics::Snapshot pre;pre.valid=1;RecoverySetupIrqDiagnostics::Snapshot setup;setup.valid=1;RecoveryTaskDiagnostics::Snapshot task;task.valid=1;unsigned p[8];
 state.Initial(SetupBit);state.Return(SetupBit,0,1);state.ReadInto(s);
 require(!s.valid&&s.entries==1&&s.returns==1&&s.setup_status_count==1&&s.latest_s0==SetupBit&&s.latest_s1==0&&s.latest_gates==1,"normal boot history retained before publication enable");
 state.Enable();state.ReadInto(s);require(s.valid&&s.entries==1,"enable never resets boot lifetime state");
 state.Initial(ResetBit|BuffBit);state.Return(ResetBit|BuffBit,SetupBit,7);state.ReadInto(s);
 require(s.entries==2&&s.returns==2&&s.latest_s0==(ResetBit|BuffBit)&&s.latest_s1==SetupBit&&s.latest_gates==7&&s.late_count==1&&s.first_late_id==2&&s.first_late_s0==(ResetBit|BuffBit)&&s.first_late_s1==SetupBit&&s.first_late_gates==7,"first authoritative S0/S1 tuple and sequential gates");
 Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Yellow&&p[4]==RecoveryTaskDiagnostics::Red,"older S0 cannot manufacture post-late WHITE");
 state.Initial(0);state.ReadInto(s);require(s.entries==3&&s.returns==2&&s.latest_s0==0&&s.latest_s1==SetupBit,"active S0 readable; S1 remains explicitly previous invocation");
 Panel(s,pre,setup,task,p);require(p[4]==RecoveryTaskDiagnostics::Cyan,"later active entry proves later S0 without claiming return");
 state.Return(0,SetupBit,1);state.ReadInto(s);require(s.late_count==2&&s.first_late_id==2&&s.first_late_gates==7&&s.latest_s0==0&&s.latest_s1==SetupBit&&s.latest_gates==1,"later late return preserves first tuple");
 state.Initial(SetupBit);state.ReadInto(s);require(s.first_post_late_setup_id==4,"strictly later active S0 setup latches exact first post-late ID");
 Panel(s,pre,setup,task,p);require(p[4]==RecoveryTaskDiagnostics::White,"post-late active S0 sufficient for WHITE");
 state.Return(SetupBit,0,0);state.Initial(SetupBit);state.Return(SetupBit,0,0);state.ReadInto(s);require(s.first_post_late_setup_id==4&&s.first_late_id==2,"both selected identities immutable across later SETUP");
 State odd;odd.Enable();StateTestAccess::Sequence(odd,1);s.valid=123;s.entries=123;odd.ReadInto(s);require(!s.valid&&!s.entries,"odd bank clears stale caller snapshot and returns without retry");
 State terminal;terminal.Enable();terminal.Initial(0);terminal.Return(0,SetupBit,3);StateTestAccess::Sequence(terminal,0xfffffffcu);terminal.Initial(0);terminal.ReadInto(s);
 require(s.valid&&(s.overflow_flags&SequenceExhausted)&&s.entries==1&&s.first_late_id==1,"sequence guard final flags-only publication preserves first tuple");
 const auto frozen=s;terminal.Initial(SetupBit);terminal.Return(SetupBit,0,0);terminal.ReadInto(s);
 require(!memcmp(&s,&frozen,sizeof(s)),"sequence terminal stops mutations without wrap");
 Panel(s,pre,setup,task,p);require(p[4]==RecoveryTaskDiagnostics::Magenta,"sequence exhaustion cannot manufacture precision-based LF3");
 State saturated;saturated.Enable();StateTestAccess::Counts(saturated,UINT32_MAX);
 saturated.Initial(SetupBit|ResetBit|BuffBit);saturated.Return(0,SetupBit,1);saturated.ReadInto(s);
 require(s.entries==UINT32_MAX&&s.returns==UINT32_MAX&&s.setup_status_count==UINT32_MAX&&s.reset_status_count==UINT32_MAX&&s.buff_status_count==UINT32_MAX&&s.late_count==UINT32_MAX,"all invocation/event counts saturate rather than wrap");
 require((s.overflow_flags&63u)==63u,"each attempted saturated increment records lost precision");
 Panel(s,pre,setup,task,p);require(p[2]==RecoveryTaskDiagnostics::Yellow&&p[4]==RecoveryTaskDiagnostics::Magenta,"positive S0 survives lost precision; no false relational color");
 for(uint32_t flag=1;flag<=64;flag<<=1){Snapshot x;x.valid=1;x.entries=2;x.first_late_id=1;x.late_count=1;x.overflow_flags=flag;Panel(x,pre,setup,task,p);require(p[4]==RecoveryTaskDiagnostics::Magenta,"every precision flag suppresses LF3 relation");}
 State concurrent;concurrent.Enable();
 std::thread writer([&]{for(unsigned i=0;i<5000;++i){const uint32_t v=(i&1u)?ResetBit:(SetupBit|BuffBit);concurrent.Initial(v);concurrent.Return(v,(i&1u)?SetupBit:0,1);}});
 for(unsigned i=0;i<5000;++i){concurrent.ReadInto(s);if(s.valid){
  require(s.returns<=s.entries&&s.entries-s.returns<=1,"bounded coherent initial/return tuple under real writer interleave");
  require(s.setup_status_count+s.reset_status_count==s.entries&&s.buff_status_count==s.setup_status_count,"all S0 counter words from same publication");
  require(s.late_count==s.returns/2,"late count bound to return publication");
  if(s.entries)require(s.latest_s0==((s.entries&1u)?SetupBit|BuffBit:ResetBit),"latest S0 bound to entries identity");
  if(s.first_late_id)require(s.first_late_id==2&&s.first_late_s0==ResetBit&&s.first_late_s1==SetupBit&&s.first_post_late_setup_id==(s.entries>=3?3u:0u),"immutable late and post-late records never torn");
 }}
 writer.join();concurrent.ReadInto(s);require(s.valid&&s.entries==5000&&s.returns==5000&&s.late_count==2500,"final parallel writer history readable");
 std::puts("late_sampler=PASS odd_bank_saturation_terminal_sequence_older_setup_strict_postlate_concurrent_reader");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
