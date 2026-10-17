// The extracted production handler performs its two MMIO loads through this
// host adapter. Schedules act on the modeled register just before the actual
// read; the loaded values still drive the real original vendor body and hooks.
namespace {
std::string late_case;bool inject_late=false,pause_initial=false;
unsigned initial_reads=0,late_reads=0;uint32_t desired_gates=1;
RecoveryPrivateDcdDiagnostics::Snapshot late_read(){
    RecoveryPrivateDcdDiagnostics::Snapshot s;RecoveryUsbDiagnostics::PrivateReadInto(s);
    require(s.valid,"closed actual S0/S1 observer bank readable");return s;
}
}
uint32_t GlyphHostReadInts(bool late){
    if(late){
        ++late_reads;
        if(inject_late){
            inject_late=false;latch_setup();
            const uint32_t mask=1u<<USBCTRL_IRQ;
            if(desired_gates&1u)nvic_hw->iser|=mask;else nvic_hw->iser&=~mask;
            if(desired_gates&2u)nvic_hw->ispr|=mask;else nvic_hw->ispr&=~mask;
            host_primask=(desired_gates&4u)?1u:0u;
        }
    }else ++initial_reads;
    return usb_hw->ints;
}
extern "C" void GlyphHostPrivateStatus(uint32_t s0){
    GlyphDcdPrivateStatus(s0);
    if(pause_initial){pause_initial=false;throw TaskPaused{};}
}
extern "C" void GlyphHostPrivateReturn(uint32_t s0,uint32_t s1){GlyphDcdPrivateReturn(s0,s1);}
int late_main(int argc,char **argv){try{
    using namespace RecoveryPrivateDcdDiagnostics;using namespace RecoveryTaskDiagnostics;
    using Snapshot=RecoveryPrivateDcdDiagnostics::Snapshot;
    require(argc==3,"fixture/scenario");late_case=argv[2];selected_timing="dcd-model";
    seed(argv[1],&config);const auto files=storage.files;
    RecoveryStartupDiagnostics::CapturePrevious();TinyUSBDevice.begin(0);defer_task=true;
    static_assert(sizeof(Snapshot)==64,"actual sixteen-word late observer record");
    static_assert(SetupBit==USB_INTS_SETUP_REQ_BITS&&ResetBit==USB_INTS_BUS_RESET_BITS&&BuffBit==USB_INTS_BUFF_STATUS_BITS,"pinned SDK bit meanings");
    if(late_case=="late-pre-enable"){
        inject_late=true;direct_irq(0);Snapshot pre;RecoveryUsbDiagnostics::PrivateReadInto(pre);
        require(!pre.valid&&pre.entries==1&&pre.late_count==1&&pre.first_late_id==1,"unarmed late boot history retained before enable");
    }
    enter_recovery_configurator();independent();
    uint32_t expected_entries=1,expected_returns=1,expected_setup=0,expected_reset=0,expected_buff=0,expected_late=0,expected_first=0,expected_post=0;
    uint32_t first_s0=0,first_s1=SetupBit;
    if(late_case=="late-no-entry"||late_case=="late-no-entry-raw"){
        expected_entries=expected_returns=0;if(late_case=="late-no-entry-raw")latch_setup();
    }else if(late_case=="late-pre-enable"){
        direct_irq(0);expected_entries=expected_returns=2;expected_late=1;expected_first=1;
    }else if(late_case=="late-none"||late_case=="late-no-raw")direct_irq(0);
    else if(late_case=="late-raw-no-late"){direct_irq(0);latch_setup();}
    else if(late_case=="late-setup-cleared"){direct_irq(SetupBit);expected_setup=1;}
    else if(late_case=="late-setup-still"){
        inject_late=true;direct_irq(SetupBit);expected_setup=1;
    }else{
        if(late_case=="late-older-setup"){direct_irq(SetupBit);expected_entries=expected_returns=2;expected_setup=1;}
        uint32_t s0=0;
        if(late_case=="late-reset"){s0=ResetBit;expected_reset=1;}
        if(late_case=="late-buff"){s0=BuffBit;expected_buff=1;}
        if(late_case=="late-pending")desired_gates=3;
        if(late_case=="late-nvic-off")desired_gates=0;
        if(late_case=="late-masked")desired_gates=5;
        if(late_case=="late-all-gates")desired_gates=7;
        inject_late=true;direct_irq(s0);expected_late=1;expected_first=expected_entries;first_s0=s0;first_s1=SetupBit|(s0&BuffBit);
        if(late_case=="late-later-empty"||late_case=="late-older-setup"||late_case=="late-multiple"){
            if(late_case=="late-multiple"){
                inject_late=true;direct_irq(BuffBit);++expected_entries;++expected_returns;++expected_buff;++expected_late;
            }
            direct_irq(0);++expected_entries;++expected_returns;
        }else if(late_case=="late-later-setup"||late_case=="late-downstream"){
            direct_irq(SetupBit);++expected_entries;++expected_returns;++expected_setup;expected_post=expected_entries;
        }else if(late_case=="late-active-later"||late_case=="late-active-later-setup"){
            pause_initial=true;const bool setup=late_case=="late-active-later-setup";
            try{direct_irq(setup?SetupBit:0);}catch(const TaskPaused&){}
            ++expected_entries;if(setup){++expected_setup;expected_post=expected_entries;}
        }
    }
    host_exception=0;host_primask=0;
    auto s=late_read();
    require(s.entries==expected_entries&&s.returns==expected_returns,"actual exact S0 and normal-return publication counts");
    require(initial_reads==expected_entries&&late_reads==expected_returns,"exactly one S0 per entry and one S1 per normal return");
    require(s.setup_status_count==expected_setup&&s.reset_status_count==expected_reset&&s.buff_status_count==expected_buff,"S0 setup/reset/buffer accounting independent of S1");
    require(s.late_count==expected_late&&s.first_late_id==expected_first&&s.first_post_late_setup_id==expected_post,"first late and strictly post-late S0 identity");
    require(!s.overflow_flags,"ordinary schedules preserve count precision");
    if(expected_first){
        require(s.first_late_s0==first_s0&&s.first_late_s1==first_s1,"first late same-invocation S0/S1 values preserved");
        require(s.first_late_gates==desired_gates,"core0 sequential enabled/pending/PRIMASK samples match exact late return");
    }
    if(late_case=="late-setup-cleared")require(s.latest_s0==SetupBit&&!s.latest_s1,"original SETUP branch clears latch before S1");
    if(late_case=="late-setup-still")require(s.latest_s0==SetupBit&&s.latest_s1==SetupBit&&!s.late_count,"S0 SETUP + S1 SETUP is never late");
    if(late_case=="late-downstream"){
        defer_task=false;recovery_loop();
        const auto task=RecoveryUsbDiagnostics::TaskRead();RecoverySetupIrqDiagnostics::Snapshot setup;RecoveryUsbDiagnostics::SetupReadInto(setup);
        require(setup.setup_emit_entered&&setup.setup_emit_returned&&setup.setup_accepted&&task.setup_consumed&&task.control_began&&!control_rx.empty(),"late then later S0 executes actual external SETUP/queue/task/control path");
    }
    independent();host_clock_us=9999999;independent();Snapshot unavailable;
    require(!RecoveryStartupDiagnostics::CapturedPrivateInto(unavailable)&&!unavailable.valid,"no private freeze before ten-second deadline");
    host_clock_us=10000000;independent();Snapshot captured;
    require(RecoveryStartupDiagnostics::CapturedPrivateInto(captured)&&!memcmp(&captured,&s,sizeof(s)),"independent core1 freezes actual closed late bank while core0 can remain paused");
    const auto task=RecoveryStartupDiagnostics::CapturedTask();
    const bool rawcase=late_case=="late-raw-no-late"||late_case=="late-no-entry-raw";
    if(!expected_setup&&expected_entries)require(task.pixels[2]==((expected_late||rawcase)?Cyan:Blue),"LF4 preserves initial S0 versus historical RAW distinction");
    if(!expected_entries)require(task.pixels[2]==(rawcase?Magenta:Green),"LF4 empty valid history distinguishes RAW and no RAW");
    if(expected_setup)require(task.pixels[2]==Yellow,"LF4 S0 setup positive");
    const unsigned branch=expected_first?(expected_post?White:(expected_entries>expected_first?Cyan:Red)):Off;
    require(task.pixels[4]==branch&&task.pixels[5]==branch,"LF3 only strictly later S0 can select WHITE; older S0 cannot");
    require(task.pixels[0]==Off&&task.pixels[1]==Off,"MB/menu dark");
    for(unsigned i=2;i<8;i+=2)require(task.pixels[i]==task.pixels[i+1],"uniform main button pairs");
    const auto words=led_words;
    // Later real handler publication may change live bank but cannot change core1 capture.
    pause_initial=false;irq_set_enabled(USBCTRL_IRQ,true);direct_irq(0);host_exception=0;host_clock_us=20000000;independent();
    Snapshot still;require(RecoveryStartupDiagnostics::CapturedPrivateInto(still)&&!memcmp(&captured,&still,sizeof(still))&&words==led_words,"captured bank and panel immutable after later private invocation");
    require(storage.files==files,"late diagnostic changes no persistence bytes");
    std::printf("%s=PASS actual_generated_DCD_S0_S1 entries=%u returns=%u late=%u first=%u post=%u physical_irq_redispatch=NOT_MODELED\n",argv[2],s.entries,s.returns,s.late_count,s.first_late_id,s.first_post_late_setup_id);
    delete recovery_configurator;return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
