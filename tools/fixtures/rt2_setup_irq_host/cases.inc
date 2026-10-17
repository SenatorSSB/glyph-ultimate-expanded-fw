// Deliberate host-only stalls are injected in pinned source copies, never target
// code. Core0 remains paused with the actual outer USB mutex held while the
// independent core1 branch takes the ten-second dashboard snapshot.
namespace {
struct TaskPaused {};
std::string task_case;
unsigned queue_passes=0,driver_enters=0,driver_returns=0,async_publishes=0;
bool injecting=false,paused=false,capture_response=false;
void independent(){
    std::thread observer([]{host_core=1;recovery_observer_loop();host_core=0;});
    observer.join();++async_publishes;
}
void stop_task(){paused=true;throw TaskPaused{};}
void setup_only(){host_setup_packet(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_DEVICE<<8,18));}
void queue_noops(unsigned n){for(unsigned i=0;i<n;++i)usbd_defer_func(host_noop,nullptr,true);}
bool same_task(const RecoveryTaskDiagnostics::Snapshot&a,const RecoveryTaskDiagnostics::Snapshot&b){
    for(unsigned i=0;i<8;++i)if(a.pixels[i]!=b.pixels[i])return false;
    return a.valid==b.valid&&a.entered==b.entered&&a.returned==b.returned&&a.active==b.active&&a.first_id==b.first_id&&a.latest_returned==b.latest_returned&&a.first_returned==b.first_returned&&a.total_resets==b.total_resets&&a.pre_first_resets==b.pre_first_resets&&a.first_resets==b.first_resets&&a.active_resets==b.active_resets&&a.post_first_resets==b.post_first_resets&&a.reset_completed==b.reset_completed&&a.first_reset_completed==b.first_reset_completed&&a.reset_consumed==b.reset_consumed&&a.reset_continued==b.reset_continued&&a.reset_stage==b.reset_stage&&a.processing_invocation==b.processing_invocation&&a.setup_consumed==b.setup_consumed&&a.control_began==b.control_began&&a.class_entered==b.class_entered&&a.class_returned==b.class_returned&&a.queue_attempted==b.queue_attempted&&a.queue_accepted==b.queue_accepted&&a.queue_failed==b.queue_failed&&a.reset_dropped==b.reset_dropped&&a.setup_dropped==b.setup_dropped&&a.max_occupancy==b.max_occupancy&&a.empty_reads==b.empty_reads&&a.event_flags==b.event_flags&&a.task_flags==b.task_flags&&a.raw_setup_seen==b.raw_setup_seen&&a.pullup==b.pullup&&a.configured_current==b.configured_current&&a.task_pixel==b.task_pixel&&a.progress_pixel==b.progress_pixel&&a.dashboard==b.dashboard;
}
void frame(bool recent=false){
    const auto before=led_updates;
    independent(); // establish current invocation age independently at time0
    RecoveryTaskDiagnostics::Snapshot caller_owned;caller_owned.valid=123;caller_owned.active=123;
    require(!RecoveryStartupDiagnostics::CapturedTaskInto(caller_owned)&&!caller_owned.valid&&!caller_owned.active,"caller-owned capture getter clears unavailable pre-deadline cache");
    host_clock_us=9999999;independent();require(led_updates==before&&!RecoveryStartupDiagnostics::CapturedTask().valid,"no dashboard frame or captured task before ten seconds");
    host_clock_us=10000000;independent();
    const auto snap=RecoveryUsbDiagnostics::TaskRead();require(snap.valid,"final snapshot coherent");
    require(RecoveryStartupDiagnostics::CaptureElapsedUs()==10000000u,"hardware timer capture is exactly ten seconds after handoff in host model");
    require(led_updates==before+1&&led_words.size()>=8,"independent core1 publishes one complete eight-pixel frame at deadline");
    const uint32_t grb[]={0,0x001800,0x061800,0x181800,0x001818,0x000018,0x180018,0x180000,0x181818};
    RecoverySetupIrqDiagnostics::Snapshot setup;RecoveryUsbDiagnostics::SetupReadInto(setup);
    unsigned expected_pixels[8];RecoverySetupIrqDiagnostics::Panel(setup,snap,expected_pixels);
    for(unsigned i=0;i<8;++i)require(led_words[led_words.size()-8+i]==(grb[expected_pixels[i]]<<8),"whole-main-button frame matches captured observer");
    require(expected_pixels[0]==0&&expected_pixels[1]==0,"menu pair remains dark");
    for(unsigned i=2;i<8;i+=2)require(expected_pixels[i]==expected_pixels[i+1],"each main button has one color");
    auto expected=snap;expected.dashboard=0;for(unsigned i=0;i<8;++i){expected.pixels[i]=expected_pixels[i];expected.dashboard|=uint32_t(expected_pixels[i])<<(4*i);}
    const auto captured=RecoveryStartupDiagnostics::CapturedTask();
    require(RecoveryStartupDiagnostics::CapturedTaskInto(caller_owned)&&same_task(caller_owned,captured),"caller-owned capture equals immutable task");
    RecoverySetupIrqDiagnostics::Snapshot captured_setup;require(RecoveryStartupDiagnostics::CapturedSetupInto(captured_setup)&&!std::memcmp(&captured_setup,&setup,sizeof(setup)),"captured SETUP snapshot equals final observer state");
    require(captured.valid&&same_task(captured,expected)&&captured.dashboard==RecoveryStartupDiagnostics::Dashboard(),"captured task and physical panel describe same freeze");
    const auto words=led_words;const auto scratch=watchdog_hw->scratch[3];
    physical_reset(); // IRQ events after capture cannot refresh the frozen panel
    host_clock_us=20000000;for(unsigned i=0;i<1000;++i)independent();
    require(led_words==words&&led_updates==before+1&&watchdog_hw->scratch[3]==scratch,"settled dashboard remains frozen with no refresh");
    caller_owned.entered=123;require(RecoveryStartupDiagnostics::CapturedTaskInto(caller_owned)&&same_task(caller_owned,captured),"caller-owned capture output retains immutable ten-second fields after IRQ");
    require(same_task(captured,RecoveryStartupDiagnostics::CapturedTask())&&captured.dashboard==RecoveryStartupDiagnostics::Dashboard(),"immutable captured task survives later IRQ events and a thousand observer loops");
}
}
void GlyphCaptureResponseBoundary(){if(capture_response){capture_response=false;require(!RecoveryStartupDiagnostics::CapturedTask().valid,"response begins before capture");host_clock_us=10000000;independent();require(RecoveryStartupDiagnostics::CapturedTask().valid,"core1 capture interrupts response at exact safe host-only boundary");}}
extern "C" void GlyphTaskBoundary(const char* point,unsigned index){
    require(host_core==0,"independent observer never invokes TinyUSB task");
    if(task_case.empty()||injecting)return;
    const std::string at=point;
    if(at=="class-enter")++driver_enters;
    if(at=="class-return")++driver_returns;
    if(at=="queue"){
        ++queue_passes;
        if(queue_passes==1){
            const auto s=RecoveryUsbDiagnostics::TaskRead();require(s.valid&&s.active&&__usb_mutex.held,"foreground task has real outer USB mutex");
            injecting=true;
            if(task_case=="soft-irq-locked"){
                const auto before=RecoveryUsbDiagnostics::Read();irq_set_pending(31);interrupt_pass();
                require(RecoveryUsbDiagnostics::Read().task_entered==before.task_entered,"software IRQ try-lock fails without entering task");
            }
            if(task_case=="task-active-zero"||task_case=="later-active"||task_case=="later-recent"||task_case=="core1-active"){injecting=false;stop_task();}
            if(task_case=="setup-consumed"||task_case=="control-began")setup_only();
            else if(task_case=="one-reset"||task_case=="two-resets"||task_case=="continuous-reset"||task_case=="hardware-irq-locked"||task_case=="core1-irqs"||task_case.rfind("stall-",0)==0){
                physical_reset();
                if(task_case=="two-resets")physical_reset();
                if(task_case=="core1-irqs")for(unsigned i=0;i<31;++i)physical_reset();
            }
            injecting=false;
            if(task_case=="hardware-irq-locked"||task_case=="core1-irqs")stop_task();
        }
        if(task_case=="continuous-reset"){
            injecting=true;physical_reset();injecting=false;
            if(queue_passes==128)stop_task();
        }
        if(task_case=="stall-continued"&&queue_passes==2)stop_task();
    }
    if((task_case=="setup-consumed"&&at=="setup-consumed")||(task_case=="control-began"&&at=="control-began"))stop_task();
    std::string target="stall-"+at;
    if(at=="class-enter"||at=="class-body"||at=="class-return")target="stall-class-"+std::to_string(index)+"-"+(at=="class-enter"?"enter":at=="class-body"?"body":"return");
    if(task_case==target)stop_task();
}
int main(int argc,char**argv){try{
    require(argc==3,"fixture/scenario");const std::string scenario=argv[2];
    selected_timing="dcd-model";seed(argv[1],&config);const auto files=storage.files;
    RecoveryStartupDiagnostics::CapturePrevious();TinyUSBDevice.begin(0);
    if(scenario=="pre-enable-reset"){defer_task=true;physical_reset();}
    enter_recovery_configurator();
    const unsigned pre_enable_handler_calls=actual_handler_calls;
    if(scenario=="pre-enable-reset")require(pre_enable_handler_calls==1,"unarmed trampoline invokes original exactly once");
    require(shared_handlers.size()==2&&shared_handlers[0].priority==0xff&&shared_handlers[1].priority==0,"same two pinned handler slots/order preserved");
    TinyUSB_Device_Task();require(RecoveryUsbDiagnostics::TaskRead().entered==0,"pre-loop task excluded from foreground anchor");
    const auto initial_frames=led_updates;independent();require(led_updates==initial_frames,"core1 observes before deadline without publishing");
    if(scenario=="external-context"){
        defer_task=true;
        const auto request=req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_DEVICE<<8,18);
        dcd_event_setup_received(0,reinterpret_cast<const uint8_t*>(&request),false);
    }else if(scenario=="forced"){
        defer_hardware=true;defer_task=true;usb_hw->intf=USB_INTF_SETUP_REQ_BITS;usb_hw->ints=usb_hw->intf;independent();
    }else if(scenario=="nvic-off"||scenario=="global-mask"||scenario=="pending"){
        defer_hardware=true;defer_task=true;
        if(scenario=="nvic-off")irq_set_enabled(USBCTRL_IRQ,false);
        if(scenario=="global-mask")host_primask=1;
        setup_only();RecoveryUsbDiagnostics::LoopEntered();independent();
    }else if(scenario.rfind("timing-",0)==0){
        defer_task=true;timing_point=scenario.back()-'0';
        if(timing_point==2)latch_setup(); // T2 requires an existing SETUP branch
        physical_reset();if(timing_point==6)GlyphTiming(6);
        require(timing_fired,"requested exact source timing boundary executed");
        RecoverySetupIrqDiagnostics::Snapshot before;RecoveryUsbDiagnostics::SetupReadInto(before);
        if(timing_point==0||timing_point==2)require(before.setup_emit_entered==1,"same status snapshot SETUP precedes RESET");
        else require(before.setup_emit_entered==0&&(usb_hw->sie_status&USB_SIE_STATUS_SETUP_REC_BITS),"late SETUP remains latched after reset-only snapshot");
        interrupt_pass();RecoverySetupIrqDiagnostics::Snapshot after;RecoveryUsbDiagnostics::SetupReadInto(after);
        require(after.setup_emit_entered==1&&after.setup_emit_returned==1&&after.setup_hook==1,"one SETUP event is emitted across source-faithful timing matrix");
        require(!(usb_hw->sie_status&USB_SIE_STATUS_SETUP_REC_BITS),"SETUP branch alone clears its latch");
    }else if(scenario=="before-entry"||scenario=="pre-enable-reset"){}
    else if(scenario=="generic-unplug"){defer_task=true;dcd_event_bus_signal(0,DCD_EVENT_UNPLUGGED,true);defer_task=false;recovery_loop();}
    else if(scenario=="pullup-off"){dcd_disconnect(0);independent();}
    else if(scenario=="raw-only"){
        defer_hardware=true;defer_task=true;setup_only();independent();
    }else if(scenario=="dcd-setup"){
        defer_task=true;setup_only();independent();
    }else if(scenario=="queue-partial"||scenario=="queue-full"||scenario=="queue-failed"||scenario=="drop-reset"||scenario=="drop-setup"||scenario=="descriptor-dropped-reset"){
        defer_task=true;
        queue_noops(scenario=="queue-partial"?4:GLYPH_HOST_QUEUE_SIZE);
        if(scenario=="queue-failed"||scenario=="drop-reset"||scenario=="descriptor-dropped-reset")physical_reset();
        if(scenario=="drop-setup")setup_only();
        defer_task=false;recovery_loop();if(scenario=="descriptor-dropped-reset")setup_only();
    }else if(scenario=="pre-first-reset"){
        defer_task=true;physical_reset();defer_task=false;recovery_loop();
    }else if(scenario=="post-first-reset"){
        recovery_loop();defer_task=true;physical_reset();defer_task=false;recovery_loop();
    }else if(scenario=="task-multiple"){
        for(unsigned i=0;i<32;++i)recovery_loop();
    }else if(scenario=="later-active"||scenario=="later-recent"){
        recovery_loop();if(scenario=="later-recent")host_clock_us=9999000;task_case=scenario;try{TinyUSB_Device_Task();}catch(const TaskPaused&){}
    }else if(scenario=="descriptor"||scenario=="address-request"||scenario=="address-applied"||scenario=="capture-during-response"||scenario=="configured"||scenario=="configured-reset"||scenario=="deconfigured"||scenario=="inspection"){
        recovery_loop();physical_reset();setup_only();
        require(control_rx.size()==18,"actual descriptor submission has expected device descriptor bytes");
        if(scenario!="descriptor"){
            hold_address_ack=scenario=="address-request";
            control(req(0,TUSB_REQ_SET_ADDRESS,5));
            if(scenario!="address-request")require(usb_hw->dev_addr_ctrl==5,"actual DCD status completion applies address");
        }
        if(scenario=="capture-during-response"||scenario=="configured"||scenario=="configured-reset"||scenario=="deconfigured"||scenario=="inspection"){
            control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_CONFIGURATION<<8,256));
            control(req(0,TUSB_REQ_SET_CONFIGURATION,1));require(tud_mounted()&&opened>=3,"actual SET_CONFIGURATION opens CDC endpoints");
            if(scenario=="configured-reset")physical_reset();
            if(scenario=="deconfigured")control(req(0,TUSB_REQ_SET_CONFIGURATION,0));
            if(scenario=="capture-during-response"){
                control(req(0x21,CDC_REQUEST_SET_CONTROL_LINE_STATE,3));
                auto pulse=status();pulse.operation=PROFILE_STORE_LIVENESS;capture_response=true;
                const auto crossed=transact(pulse);require(crossed.status==PROFILE_STORE_OK&&crossed.recovery_dashboard==0&&crossed.recovery_dashboard_elapsed_us==0&&crossed.recovery_dashboard_active_age_us==0,"pre-capture response never mixes live fields with a later captured dashboard");
                const auto captured=RecoveryStartupDiagnostics::CapturedTask();const auto frozen=transact(pulse);
                RecoverySetupIrqDiagnostics::Snapshot cs;require(RecoveryStartupDiagnostics::CapturedSetupInto(cs)&&frozen.recovery_setup_irq_valid==cs.valid&&frozen.recovery_setup_irq_irq_entries==cs.irq_entries,"serial SETUP fields share the chosen immutable capture");
                require(frozen.status==PROFILE_STORE_OK&&frozen.recovery_dashboard==captured.dashboard&&frozen.recovery_task_entered==captured.entered&&frozen.recovery_task_returned==captured.returned&&frozen.recovery_task_configured_current==captured.configured_current&&frozen.recovery_dashboard_elapsed_us==10000000u,"post-capture serial fields correspond to immutable dashboard snapshot");
            }
            if(scenario=="inspection"){
                control(req(0x21,CDC_REQUEST_SET_CONTROL_LINE_STATE,3));
                auto pulse=status();pulse.operation=PROFILE_STORE_LIVENESS;
                require(transact(pulse).status==PROFILE_STORE_OK,"supported recovery inspection decoded through actual CDC/backend");
            }
        }
    }else{
        task_case=scenario;
        try{recovery_loop();}catch(const TaskPaused&){}
    }
    const auto s=RecoveryUsbDiagnostics::TaskRead();require(s.valid,"coherent source observer snapshot");
    RecoverySetupIrqDiagnostics::Snapshot setup;RecoveryUsbDiagnostics::SetupReadInto(setup);
    require(actual_handler_calls==pre_enable_handler_calls+setup.irq_entries,"captured original callback executes exactly once per trampoline");
    require(setup.valid&&setup.registration_captured&&!setup.registration_duplicate,"sole exact DCD registration captured");
    if(scenario=="raw-only")require((setup.independent_seen&15u)==15u&&!setup.setup_emit_entered,"independent SIE INTR INTE INTS observed separately");
    if(scenario=="forced")require((setup.independent_seen&24u)==24u&&!(setup.independent_seen&3u),"INTF forced INTS never manufactures raw SIE/INTR");
    if(scenario=="external-context"){unsigned panel[8];RecoverySetupIrqDiagnostics::Panel(setup,s,panel);require(panel[6]==RecoveryTaskDiagnostics::Orange&&panel[7]==RecoveryTaskDiagnostics::Orange,"unfiltered external boundary is visible on whole LF5 button");}
    if(scenario=="external-context")require(setup.external_flags==7&&!setup.setup_emit_entered&&!setup.setup_hook&&!setup.setup_accepted,"unfiltered external SETUP boundary survives old hook context rejection");
    if(scenario=="dcd-setup")require(setup.external_flags==3,"expected IRQ context records independent external call/return");
    if(scenario=="dcd-setup")require(setup.irq_entries==1&&setup.irq_returns==1&&setup.irq_setup_entries==1&&setup.setup_emit_entered==1&&setup.setup_emit_returned==1&&setup.setup_hook==1&&setup.setup_accepted==1&&setup.setup_dropped==0,"exact IRQ/event/queue boundaries remain separate");
    if(scenario=="drop-setup")require(setup.setup_emit_entered==1&&setup.setup_emit_returned==1&&setup.setup_hook==1&&setup.setup_dropped==1&&!setup.setup_accepted,"failed queue still proves DCD emission");
    if(scenario=="nvic-off")require(setup.foreground_conditions&RecoverySetupIrqDiagnostics::IntsNvicOff,"NVIC off paired with actual positive INTS sample");
    if(scenario=="global-mask")require(setup.foreground_conditions&RecoverySetupIrqDiagnostics::IntsGloballyMasked,"PRIMASK paired with actual positive INTS sample");
    if(scenario=="pending")require(setup.foreground_conditions&RecoverySetupIrqDiagnostics::IntsPending,"pending paired with actual positive INTS sample");
    // Scenario-specific semantic assertions follow in checks.inc, kept separate
    // from the host scheduler so no self-fulfilling expected state drives code.
    #include "checks.inc"
    if(scenario!="capture-during-response")frame(scenario=="later-recent");
    require(storage.files==files,"observer changes no persistence bytes");
    std::printf("comprehensive_%s=PASS entered=%u returned=%u active=%u first_resets=%u async=%u physical_macOS=NOT_MODELED\n",scenario.c_str(),s.entered,s.returned,s.active,s.first_resets,async_publishes);
    delete recovery_configurator;return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
