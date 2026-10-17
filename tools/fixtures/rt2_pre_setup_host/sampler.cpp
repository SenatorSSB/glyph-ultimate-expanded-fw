#include "core/RecoveryPreSetupDiagnostics.hpp"
#include <cstdio>
#include <stdexcept>
using namespace RecoveryPreSetupDiagnostics;
void require(bool ok,const char *why){if(!ok)throw std::runtime_error(why);}
int main(){try{
 State state;Snapshot s;state.ReadInto(s);require(!s.valid,"unarmed invalid");state.Enable();state.ReadInto(s);require(s.valid&&!s.irq_entered,"armed before any handler");
 RecoverySetupIrqDiagnostics::Snapshot setup;setup.valid=1;RecoveryTaskDiagnostics::Snapshot task;task.valid=1;unsigned pixels[8];
 Panel(s,setup,task,0,pixels);require(pixels[2]==RecoveryTaskDiagnostics::Blue&&pixels[4]==0,"valid never-entered visible");
 state.IrqEnter(0x1234);state.EndpointEnter(0x82,true,0x44,0x20000024);state.ReadInto(s);
 require(s.irq_entered==1&&s.irq_active==1&&s.irq_pre_ints==0x1234&&!s.irq_returned&&s.ep_entered==1&&s.ep_irq==1&&s.ep_addr==0x82&&s.ep_active==1&&s.ep_buf_status==0x44&&s.ep_pointer==0x20000024&&!s.ep_inactive&&!s.ep_returned,"closed entry banks readable before original return");
 Panel(s,setup,task,999999,pixels);require(pixels[2]==RecoveryTaskDiagnostics::Orange&&pixels[4]==RecoveryTaskDiagnostics::Blue,"recent IRQ and active endpoint");Panel(s,setup,task,1000000,pixels);require(pixels[2]==RecoveryTaskDiagnostics::Red,"one-second same handler lower-bound age");
 state.EndpointReturn(true);state.Event(false,false);state.Event(false,true);state.Queue(true);state.Queue(false);state.Event(true,false);state.ReadInto(s);
 require(s.ep_returned==1&&s.ep_result==1&&s.xfer_entered==1&&s.xfer_returned==1&&s.xfer_accepted==1&&s.xfer_dropped==1&&s.sof_entered==1&&!s.sof_returned,"all endpoint and event return/queue counters");
 Panel(s,setup,task,0,pixels);require(pixels[4]==RecoveryTaskDiagnostics::Orange,"current SOF dominates old completed endpoint");state.Event(true,true);state.ReadInto(s);Panel(s,setup,task,0,pixels);require(s.sof_returned==1&&pixels[4]==RecoveryTaskDiagnostics::Cyan,"completed endpoint preserved after SOF returns");
 state.IrqReturn(0x66);state.ReadInto(s);require(s.irq_returned==1&&s.irq_latest_returned==1&&!s.irq_active&&s.irq_post_ints==0x66,"exact latest return ID and post bits");
 state.IrqEnter(0x77);state.EndpointEnter(0,false,0x88,0x20000048);state.ReadInto(s);Panel(s,setup,task,1000000,pixels);require(s.irq_active==2&&s.irq_latest_returned==1&&s.ep_inactive==1&&pixels[4]==RecoveryTaskDiagnostics::Magenta,"new active handler and inactive entry dominate old returns");
 const unsigned panic_colors[]={0,RecoveryTaskDiagnostics::White,RecoveryTaskDiagnostics::Red,RecoveryTaskDiagnostics::Green};
 for(unsigned kind=1;kind<=3;++kind){state.PanicEntered(kind);state.ReadInto(s);Panel(s,setup,task,0,pixels);require(s.panic_kind==kind&&s.panic_irq==2&&pixels[2]==RecoveryTaskDiagnostics::White&&pixels[4]==panic_colors[kind],"panic identity visible without serial");}
 std::puts("pre_setup_sampler_closed_banks_age_precedence=PASS");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
