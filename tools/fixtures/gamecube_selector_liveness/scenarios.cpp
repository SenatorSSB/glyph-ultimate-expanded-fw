void reset() {
 now_us=0;limit_us=2000;tx_end=0;hw={};bank={};pin_high=true;irq_disabled=false;
 updates=pauses=resumes=resets=starts=0;rx.clear();tx.clear();events.clear();on_disable={};profile_selection::Complete();
 fast_scans=0;on_fast_scan={};
}
void require(bool v,const char *why){if(!v)throw std::runtime_error(why);}
uint32_t pending(){return profile_selection::Pending();}
void request(){require(profile_selection::Request(1001),"mailbox request accepted");}
unsigned counted_services=0;
void count_service(){++counted_services;}
InputState inputs;
GamecubeBackend backend(){return GamecubeBackend(inputs,nullptr,0,0);}
void normal_poll() {
 reset();auto b=backend();event(10,[]{incoming({0x40,0x03,0x01});});b.SendReport();
 require(updates==1&&starts==1,"real POLL runs output update exactly once");
 const uint8_t expected[]={0x15,0xd5,11,22,33,44,55,66};
 require(tx.size()==8,"unchanged eight-byte report");
 for(unsigned i=0;i<8;++i)require(tx[i]==(uint32_t(expected[i])<<24 | (i==7?1u<<23:0)),"exact wire report and final stop marker");
 std::cout<<"normal-poll exact report/update/end PASS\n";
}
void normal_commands() {
 for(uint8_t command:{0u,255u,65u,66u}) {
  reset();GamecubeConsole c(0);event(1,[command]{incoming({command});});
  require(c.WaitForPollStart(),"nonpoll command remains nonpoll");
  const auto *bytes=command==0||command==255?reinterpret_cast<const uint8_t*>(&default_gc_status):reinterpret_cast<const uint8_t*>(&default_gc_origin);
  const auto size=command==0||command==255?sizeof(default_gc_status):sizeof(default_gc_origin);
  require(tx.size()==size,"command response size unchanged");
  for(unsigned i=0;i<size;++i)require(tx[i]==(uint32_t(bytes[i])<<24 | (i+1==size?1u<<23:0)),"probe/reset/origin/recalibrate bytes unchanged");
 }
 reset();GamecubeConsole c(0);event(1,[]{incoming({0x55});});
 require(c.WaitForPollStart()&&tx.empty()&&resets==2&&now_us>=130,"invalid command preserves drain/reset and sends no fake response");
 std::cout<<"normal command response dispatch/bytes/invalid drain PASS\n";
}
int main(){try {
 normal_poll();
 normal_commands();
 reset();auto old_or_new=backend();event(10,request);
#ifdef OLD_SOURCE
 bool blocked=false;try{old_or_new.SendReport();}catch(const Bound&){blocked=true;}
 require(blocked&&pending()==1001&&updates==0&&tx.empty(),"literal failed backend lacks bounded idle progress");
 std::cout<<"old-source actual blocking receive exceeds finite bound PASS\n";
#else
 old_or_new.SendReport();
 require(now_us<=60&&pending()==1001&&!hw.enabled&&updates==0&&tx.empty(),"request after service regains bounded idle application opportunity");
 // Execute the literal application-loop gate. A request already present before
 // SendReport must not reach persistence through the earlier service point.
 reset();auto gated=backend();CommunicationBackend *gated_backends[]={&gated};counted_services=0;
 request();hw.marker=true;application_service_gate(gated_backends,count_service);
 require(counted_services==0,"actual application gate blocks persistence during active partial first byte");
 hw.marker=false;hw.pc=joybus_offset_write;tx_end=100;
 application_service_gate(gated_backends,count_service);
 require(counted_services==0,"actual application gate blocks persistence while prior report TX queued");
 gated.SendReport();application_service_gate(gated_backends,count_service);
 require(counted_services==1&&!hw.enabled,"actual application gate admits only safe paused idle receiver");
 profile_selection::Complete();hw.enabled=true;hw.ctrl=1;application_service_gate(gated_backends,count_service);
 require(counted_services==1,"empty mailbox cannot authorize persistence while receiver running");
 request();application_service_gate(gated_backends,count_service);
 require(counted_services==1,"request after empty-mailbox gate opportunity cannot bypass idle admission");
 // The checker also links this receiver to the existing actual selector service
 // and Persistence harness through the opaque cross-translation-unit bridge.
 for(bool before:{false,true}) {
  reset();auto b=backend();if(before)request();else event(1,request);b.SendReport();
  require(now_us<=60&&!hw.enabled&&tx.empty(),"before/immediately-after-service requests admitted");
  profile_selection::Complete();event(now_us+10,[]{incoming({0x40,3,0});});b.SendReport();
  require(updates==1&&tx.size()==8,"refused selector resumes same receiver for real poll");
 }
 reset();auto b=backend();event(600,[]{incoming({0x40,3,0});});b.SendReport();
 require(now_us>=600&&pauses==0&&updates==1,"repeated idle timeouts without pending never pause/yield/fake command");
 reset();auto menu=backend();on_fast_scan=[]{if(fast_scans==3)request();};menu.SendReport();on_fast_scan={};
 require(fast_scans>=3&&pending()==1001&&!hw.enabled&&tx.empty()&&now_us<200,"absent host still refreshes FAST inputs so menu can produce request");
 reset();auto active=backend();event(1,[]{hw.marker=true;request();});event(140,[]{incoming({0x40,3,0});});active.SendReport();
 require(now_us>=140&&updates==1&&tx.size()==8,"partial first byte protected until real command completes");
 reset();auto stalled=backend();event(1,[]{hw.marker=true;request();});bool protected_stall=false;
 try{stalled.SendReport();}catch(const Bound&){protected_stall=true;}
 require(protected_stall&&hw.enabled&&updates==0&&tx.empty(),"stalled active partial byte never becomes false idle admission");
 reset();auto real=backend();event(1,[]{incoming({0x40});request();});event(20,[]{incoming({3,1});});real.SendReport();
 require(updates==1&&tx.size()==8,"pending selection never aborts active real POLL");
 // Every rejecting snapshot dimension must independently prevent idle admission.
 for(unsigned fault=0;fault<5;++fault) {
  reset();GamecubeConsole c(0);request();unsigned injections=0;
  on_disable=[&]{++injections;if(fault==0)hw.marker=true;if(fault==1)hw.pc=2;
    if(fault==2)pin_high=false;if(fault==3)rx.push_back(0x40);if(fault==4)bank.intr[0]|=GPIO_IRQ_EDGE_FALL;};
  event(120,[&]{on_disable={};pin_high=true;hw.pc=joybus_offset_read_loop;incoming({0x40});});
  auto s=c.WaitForPollStartBounded(pending);
  on_disable={};
  require(s==PollStartStatus::POLL&&injections>0&&hw.enabled,"marker/PC/pin/FIFO/raw FALL reject unsafe admission");
 }
 reset();auto malformed=backend();event(1,[]{incoming({0x40});request();});malformed.SendReport();
 require(tx.empty()&&!hw.marker&&resets==2,"malformed active poll tail drains and resets marker");
 malformed.SendReport();require(!hw.enabled&&now_us<300,"malformed tail cleanup permits next idle admission");
 reset();auto after=backend();event(1,[]{incoming({0x40,3,0});});after.SendReport();
 require(tx_end>now_us,"transmit remains queued on ordinary return");const auto finished_at=tx_end;request();
 after.SendReport();require(!hw.enabled&&now_us>=finished_at&&tx.size()==8,"pending after report waits past queued TX before idle admission");
 // Actual receive/reset/send C-SDK helpers clear sticky marker only while disabled.
 reset();GamecubeConsole c(0);hw.marker=true;c.ResetAfterInvalidPoll();require(!hw.marker,"reset retires activity marker");
 std::cout<<"new-source bounded idle/interleavings/admission races/TX/marker lifecycle PASS\n";
#endif
 return 0;
}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}catch(const Bound&){std::cerr<<"unexpected finite hardware bound\n";return 1;}}
