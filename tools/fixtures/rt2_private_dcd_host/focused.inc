// Fault injections here are host-only conditional schedules. The extracted
// handler and transfer bodies retain their real decisions and panic calls.
namespace {
std::string pre_case;unsigned actual_continue_calls=0;
void GlyphPreSetupBoundary(unsigned point){
    if(point==3)++actual_continue_calls;
    if((pre_case=="pre-active-stall"&&point==3)||(pre_case=="pre-sof-stall"&&point==2)){
        latch_setup(); // assertion after the handler's fixed status snapshot
        throw TaskPaused{};
    }
    if(pre_case=="pre-other-panic"&&point==1)panic("ep %d %s was already available",2,"in");
}
void direct_irq(uint32_t bits){
    usb_hw->intr=bits;usb_hw->inte|=bits;usb_hw->ints=bits;
    host_exception=16+USBCTRL_IRQ;
    shared_handlers[0].fn();
    host_exception=0;
}
void completion(bool active,bool zeroed=false){
    auto *ep=hw_endpoint_get_by_num(2,TUSB_DIR_IN);
    if(!zeroed){hw_endpoint_init(0x82,64,TUSB_XFER_BULK);ep->active=active;ep->remaining_len=0;ep->xferred_len=0;*ep->buffer_control=0;}
    usb_hw->buf_status=1u<<4;
    direct_irq(USB_INTS_BUFF_STATUS_BITS);
}
RecoveryPreSetupDiagnostics::Snapshot pre_read(){RecoveryPreSetupDiagnostics::Snapshot s;RecoveryUsbDiagnostics::PreSetupReadInto(s);require(s.valid,"pre-SETUP read coherent even during original call");return s;}
}
extern "C" void GlyphSofQueueBoundary(){if(pre_case=="pre-sof-queue-stall"){latch_setup();throw TaskPaused{};}}
int focused_main(int argc,char **argv){try{
    require(argc==3,"fixture/scenario");pre_case=argv[2];selected_timing="dcd-model";seed(argv[1],&config);const auto files=storage.files;
    RecoveryStartupDiagnostics::CapturePrevious();TinyUSBDevice.begin(0);
    if(pre_case=="pre-unarmed"){
        direct_irq(0);auto before=RecoveryPreSetupDiagnostics::Snapshot{};RecoveryUsbDiagnostics::PreSetupReadInto(before);
        require(!before.valid&&!before.irq_entered&&actual_handler_calls==1,"unarmed exact once fast forward");
    }
    enter_recovery_configurator();defer_task=true;independent();
    bool panicked=false;
    try {
        if(pre_case=="pre-never"){}
        else if(pre_case=="pre-empty"||pre_case=="pre-unarmed")direct_irq(0);
        else if(pre_case=="pre-active"||pre_case=="pre-no-false-inactive"||pre_case=="pre-active-stall"||pre_case=="pre-other-panic")completion(true);
        else if(pre_case=="pre-inactive")completion(false);
        else if(pre_case=="pre-zeroed-ep")completion(false,true);
        else if(pre_case=="pre-queue-full"){queue_noops(GLYPH_HOST_QUEUE_SIZE);completion(true);}
        else if(pre_case=="pre-unhandled")direct_irq(USB_INTS_HOST_CONN_DIS_BITS);
        else if(pre_case=="pre-sof"||pre_case=="pre-sof-stall")direct_irq(USB_INTS_DEV_SOF_BITS);
        else if(pre_case=="pre-reset-only")physical_reset();
        else if(pre_case=="pre-sof-queue-stall"){
            setup_only();defer_task=false;TinyUSB_Device_Task();defer_task=true;
            dcd_event_bus_signal(0,DCD_EVENT_SUSPEND,true);
            direct_irq(USB_INTS_DEV_SOF_BITS);
        }
        else if(pre_case=="pre-later-irq"||pre_case=="pre-later-setup"||pre_case=="pre-recent"||pre_case=="pre-restarted"){
            direct_irq(USB_INTS_DEV_SOF_BITS);
            if(pre_case=="pre-later-setup"){latch_setup();direct_irq(USB_INTS_SETUP_REQ_BITS);}
            else {if(pre_case=="pre-recent")host_clock_us=9999000;pre_case="pre-active-stall";completion(true);}
        }else require(false,"known focused case");
    }catch(const TaskPaused&){}catch(const std::runtime_error&){panicked=true;latch_setup();}
    const auto s=pre_read();
    require(!s.irq_entered&&!s.irq_returned&&!s.irq_active&&!s.irq_latest_returned&&!s.irq_pre_ints&&!s.irq_post_ints&&!s.panic_irq,"v2 legacy trampoline IRQ association unavailable and zero");
    RecoveryPrivateDcdDiagnostics::Snapshot priv;RecoveryUsbDiagnostics::PrivateReadInto(priv);
    require(priv.valid,"merged private status bank readable in every historical schedule");
    if(pre_case=="pre-never")require(!priv.entries&&!priv.returns&&!priv.active,"private post-read observer never saw a handler");
    else require(priv.entries>=1,"general handler entry independent of raw SETUP");
    if(pre_case=="pre-empty"||pre_case=="pre-unarmed")require(priv.entries==(pre_case=="pre-unarmed"?2u:1u)&&priv.returns==priv.entries&&!priv.active&&priv.latest_id==priv.entries,"empty interrupt returns and latest ID recorded");
    if(pre_case=="pre-active"||pre_case=="pre-no-false-inactive"||pre_case=="pre-queue-full"){
        require(actual_continue_calls==1&&s.ep_entered==1&&s.ep_returned==1&&s.ep_active==1&&s.ep_addr==0x82&&!s.ep_inactive&&s.ep_result==1,"real active endpoint completes once without false inactive");
        require(s.ep_pointer==uint32_t(reinterpret_cast<uintptr_t>(hw_endpoint_get_by_num(2,TUSB_DIR_IN))),"target-width endpoint object identity retained");
        require(s.xfer_entered==1&&s.xfer_returned==1,"actual XFER_COMPLETE external call/return");
        require(pre_case=="pre-queue-full"?s.xfer_dropped==1&&!s.xfer_accepted:s.xfer_accepted==1&&!s.xfer_dropped,"actual nonoverwriting USBD queue outcome");
    }
    if(pre_case=="pre-inactive"||pre_case=="pre-zeroed-ep")require(panicked&&s.panic_kind==RecoveryPreSetupDiagnostics::InactiveEndpoint&&priv.active==priv.latest_id&&s.ep_inactive==1&&s.ep_entered==1&&!s.ep_returned,"real inactive branch enters panic before any sync/deref and never returns");
    if(pre_case=="pre-zeroed-ep")require(s.ep_addr==0&&s.ep_pointer==uint32_t(reinterpret_cast<uintptr_t>(hw_endpoint_get_by_num(2,TUSB_DIR_IN))),"zeroed software address must not be misidentified as EP0");
    if(pre_case=="pre-other-panic")require(panicked&&s.panic_kind==RecoveryPreSetupDiagnostics::OtherUsb&&!s.ep_entered,"general USB panic fallback before continuation");
    if(pre_case=="pre-unhandled")require(panicked&&s.panic_kind==RecoveryPreSetupDiagnostics::UnhandledIrq&&!s.ep_entered,"actual unhandled IRQ enters transparent boundary");
    if(pre_case=="pre-sof")require(s.sof_entered==1&&s.sof_returned==1&&priv.returns==1&&!s.ep_entered,"SOF exact external entry returns before later branches");
    if(pre_case=="pre-sof-queue-stall")require(s.sof_entered==1&&!s.sof_returned&&priv.active,"actual suspended SOF reached RESUME enqueue boundary and never returned");
    if(pre_case=="pre-sof-stall")require(s.sof_entered==1&&s.sof_returned==1&&priv.active&&!priv.returns,"nonreturn after actual SOF external boundary remains valid");
    if(pre_case=="pre-active-stall")require(s.ep_entered==1&&!s.ep_returned&&priv.active&&priv.active>priv.returns,"latest active IRQ cannot hide behind earlier returned invocation");
    if(pre_case=="pre-later-setup")require(priv.entries==2&&priv.returns==2&&priv.latest_id==2,"different later handler may complete SETUP successfully");
    host_exception=0;independent();
    host_clock_us=10000000;independent();
    RecoveryPreSetupDiagnostics::Snapshot captured;require(RecoveryStartupDiagnostics::CapturedPreSetupInto(captured)&&!memcmp(&captured,&s,sizeof(s)),"immutable capture binds complete closed pre-SETUP banks");
    RecoverySetupIrqDiagnostics::Snapshot setup;require(RecoveryStartupDiagnostics::CapturedSetupInto(setup),"same immutable SETUP capture");
    const auto task=RecoveryStartupDiagnostics::CapturedTask();unsigned expected[8];
    const uint32_t age=0; // legacy trampoline ID/age intentionally unavailable in v2
    require(RecoveryStartupDiagnostics::PreSetupCaptureAgeUs()==age,"v2 legacy handler ID age unavailable and zero");
    RecoveryPrivateDcdDiagnostics::Panel(priv,s,setup,task,expected);
    for(unsigned i=0;i<8;++i)require(task.pixels[i]==expected[i],"whole-main-button captured physical frame");
    require(expected[0]==0&&expected[1]==0,"MB1 dark");
    if(s.panic_kind)require(expected[2]==RecoveryTaskDiagnostics::Red,"retained USB panic dominates private status panel");
    if((priv.active||panicked)&&pre_case!="pre-sof-queue-stall")require((setup.independent_seen&11u)==11u&&!setup.setup_emit_entered,"earlier IRQ entered before later SIE INTR INTS assertion with no emitted SETUP");

    require(storage.files==files,"all persistence bytes unchanged");
    const auto words=led_words;host_clock_us=20000000;independent();require(words==led_words,"single immutable preloaded eight-word panel");
    std::printf("%s=PASS actual_DCD_and_endpoint_source physical_sequence=CONDITIONAL_NOT_PROVEN\n",argv[2]);delete recovery_configurator;return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
