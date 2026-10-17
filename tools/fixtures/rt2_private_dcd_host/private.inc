// Host-only stop scheduler surrounds the real marker call. No target hook is
// replaced by a fake handler or a second status read. Exceptions model a pause,
// not a physical CPU fault. BEFORE and AFTER outcomes are checked separately.
namespace {
std::string private_case;int private_stop=-1;bool private_after=false;
std::vector<unsigned> private_calls;bool private_armed=false;
RecoveryPrivateDcdDiagnostics::Snapshot private_read(){RecoveryPrivateDcdDiagnostics::Snapshot s;RecoveryUsbDiagnostics::PrivateReadInto(s);require(s.valid,"closed private bank readable while later vendor execution paused");return s;}
}
extern "C" void GlyphHostPrivateMarker(uint32_t marker,uint32_t value){
    if(!private_armed){GlyphDcdPrivateMarker(marker,value);return;}
    private_calls.push_back(marker);
    if(private_case=="private-raw-active"&&marker==GLYPH_DCD_PRIVATE_STATUS){
        GlyphDcdPrivateMarker(marker,value);latch_setup();throw TaskPaused{};
    }
    if(private_stop==int(marker)&&!private_after)throw TaskPaused{};
    GlyphDcdPrivateMarker(marker,value);
    if(private_stop==int(marker)&&private_after)throw TaskPaused{};
}
int private_main(int argc,char **argv){try{
    require(argc==3,"fixture/scenario");private_case=argv[2];selected_timing="dcd-model";
    seed(argv[1],&config);const auto files=storage.files;
    RecoveryStartupDiagnostics::CapturePrevious();TinyUSBDevice.begin(0);
    RecoveryPrivateDcdDiagnostics::Snapshot unavailable;unavailable.valid=123;
    require(!RecoveryStartupDiagnostics::CapturedPrivateInto(unavailable)&&!unavailable.valid,"caller-owned private cache unavailable until same release publication");
    RecoveryUsbDiagnostics::PrivateReadInto(unavailable);
    require(!unavailable.valid&&!unavailable.entries,"publication unavailable before enable; no invocation yet");
    if(private_case=="private-pre-enable-setup"||private_case=="private-pre-enable-reset"||private_case=="private-pre-enable-then-enabled"){
        direct_irq(USB_INTS_SETUP_REQ_BITS);RecoveryUsbDiagnostics::PrivateReadInto(unavailable);
        require(!unavailable.valid&&unavailable.entries==1&&unavailable.returns==1&&unavailable.setup_status_count==1&&unavailable.first_setup_id==1,"actual pre-enable private SETUP history captured before publication eligibility");
        const auto early=unavailable;enter_recovery_configurator();private_armed=true;defer_task=true;
        auto retained=private_read();require(retained.entries==early.entries&&retained.first_setup_status==early.first_setup_status&&retained.first_setup_markers==early.first_setup_markers,"BeginRecovery enables validity without resetting boot-lifetime history");
        if(private_case=="private-pre-enable-reset")physical_reset();
        if(private_case=="private-pre-enable-then-enabled"){private_stop=8;private_after=false;try{direct_irq(USB_INTS_SETUP_REQ_BITS);}catch(const TaskPaused&){}private_stop=-1;}
        else direct_irq(0);host_exception=0;independent();host_clock_us=10000000;independent();
        RecoveryPrivateDcdDiagnostics::Snapshot captured;require(RecoveryStartupDiagnostics::CapturedPrivateInto(captured),"pre-enable history available at frozen publication");
        require(captured.entries==(private_case=="private-pre-enable-reset"?3u:2u)&&captured.setup_status_count==(private_case=="private-pre-enable-then-enabled"?2u:1u)&&captured.first_setup_id==1&&captured.first_setup_status==USB_INTS_SETUP_REQ_BITS&&captured.first_setup_markers==early.first_setup_markers,"later empty and BUS_RESET preserve pre-enable ANY SETUP witness");
        require(captured.reset_status_count==(private_case=="private-pre-enable-reset"?1u:0u),"later reset counted without reset of history");
        RecoveryTaskDiagnostics::Snapshot task;require(RecoveryStartupDiagnostics::CapturedTaskInto(task),"task frozen with private history");
        if(private_case=="private-pre-enable-then-enabled"){
            require(captured.enabled_setup_count==1&&captured.first_enabled_setup_id==2&&captured.first_enabled_setup_status==USB_INTS_SETUP_REQ_BITS&&captured.first_enabled_setup_markers!=captured.first_setup_markers,"pre-enable and enabled first records remain independently associated");
            require(task.pixels[2]==RecoveryTaskDiagnostics::Yellow&&task.pixels[4]==RecoveryTaskDiagnostics::Yellow&&task.pixels[6]==RecoveryTaskDiagnostics::Off,"enabled SETUP selects enabled PID-only progress over historical pre-enable full return");
        }else require(!captured.enabled_setup_count&&!captured.first_enabled_setup_id&&task.pixels[2]==RecoveryTaskDiagnostics::Orange&&task.pixels[4]==RecoveryTaskDiagnostics::White&&task.pixels[6]==RecoveryTaskDiagnostics::Off,"pre-enable-only SETUP is ORANGE/WHITE/OFF, never compared against enabled-window downstream absence");
        require(storage.files==files,"boot-lifetime private history changes no persistence bytes");
        std::printf("%s=PASS actual_pre_enable_PRIVATE_SETUP_retained_boot_lifetime\n",argv[2]);delete recovery_configurator;return 0;
    }
    private_calls.clear();
    enter_recovery_configurator();private_armed=true;defer_task=true;independent();
    static_assert(sizeof(RecoveryPrivateDcdDiagnostics::Snapshot)==96,"fixed tiny history");
    static_assert(RecoveryPrivateDcdDiagnostics::SetupBit==USB_INTS_SETUP_REQ_BITS,"pinned setup mask");
    static_assert(RecoveryPrivateDcdDiagnostics::ResetBit==USB_INTS_BUS_RESET_BITS,"pinned reset mask");
    static_assert(RecoveryPrivateDcdDiagnostics::BuffBit==USB_INTS_BUFF_STATUS_BITS,"pinned buffer mask");
    uint32_t status=USB_INTS_SETUP_REQ_BITS;
    if(private_case.rfind("private-stop-",0)==0){
        private_stop=std::stoi(private_case.substr(13));private_after=private_case.find("-after")!=std::string::npos;
        status|=USB_INTS_DEV_SOF_BITS|USB_INTS_BUFF_STATUS_BITS;
    }
    if(private_case=="private-none"||private_case=="private-no-raw"||private_case=="private-raw-between"||private_case=="private-no-entry"||private_case=="private-no-entry-raw")status=0;
    if(private_case=="private-raw-active")status=USB_INTS_DEV_SOF_BITS;
    if(private_case=="private-setup-reset")status|=USB_INTS_BUS_RESET_BITS;
    if(private_case=="private-setup-buff")status|=USB_INTS_BUFF_STATUS_BITS;
    if(private_case=="private-setup-sof")status|=USB_INTS_DEV_SOF_BITS;
    if(private_case=="private-normal")status|=USB_INTS_DEV_SOF_BITS|USB_INTS_BUFF_STATUS_BITS;
    if(private_case=="private-later"||private_case=="private-raw-between")direct_irq(0);
    if(private_case=="private-raw-between"||private_case=="private-no-entry-raw")latch_setup();
    if(private_case=="private-reset-setup")physical_reset();
    if(private_case=="private-queue-drop")queue_noops(GLYPH_HOST_QUEUE_SIZE);
    try{if(private_case!="private-no-entry"&&private_case!="private-no-entry-raw")direct_irq(status);}catch(const TaskPaused&){}
    host_exception=0;
    const auto s=private_read();
    uint32_t expected_entries=(private_stop==0&&!private_after)?0u:1u;
    if(private_case=="private-later"||private_case=="private-raw-between"||private_case=="private-reset-setup")++expected_entries;
    if(private_case=="private-no-entry"||private_case=="private-no-entry-raw")expected_entries=0;
    require(s.entries==expected_entries&&s.latest_id==expected_entries,"exact monotonic private invocation ID");
    if(private_stop>=0){
        const unsigned completed=unsigned(private_stop)+(private_after?1u:0u);
        uint32_t mask=completed?((1u<<completed)-1u):0;
        if(completed>GLYPH_DCD_PRIVATE_SETUP_TEST)mask|=RecoveryPrivateDcdDiagnostics::SetupTestTrue;
        require(s.marker_calls==completed&&s.latest_markers==mask,"each exact patched marker retained with BEFORE/AFTER ordering");
        require(s.returns==(completed==13?1u:0u)&&s.active==(completed&&completed<13?1u:0u),"normal return distinguished from each artificial stop");
        const bool loaded=completed>GLYPH_DCD_PRIVATE_STATUS;
        require(s.latest_status==(loaded?status:0u)&&s.setup_status_count==(loaded?1u:0u),"actual private local status stored exactly once at H1");
        if(loaded)require(s.first_setup_id==1&&s.first_setup_status==status&&s.first_setup_markers==mask,"first exact SETUP history remains readable at stop");
    }else{
        require(s.latest_status==status,"exact handler-local word preserved, no later hardware reread");
        const bool local=(status&USB_INTS_SETUP_REQ_BITS)!=0;
        require(s.setup_status_count==(local?1u:0u)&&s.first_setup_id==(local?expected_entries:0u),"any SETUP private snapshot and exact first invocation selected");
        require(s.reset_status_count==((status&USB_INTS_BUS_RESET_BITS)?1u:0u)+(private_case=="private-reset-setup"?1u:0u),"exact private BUS_RESET history");
        require(s.buff_status_count==((status&USB_INTS_BUFF_STATUS_BITS)?1u:0u),"exact private BUFF_STATUS history");
        require(s.multi_status_count==((status&&(status&(status-1u)))?1u:0u),"all local multibit statuses retained");
        if(private_case=="private-raw-active")require(s.active==1&&!s.returns&&!s.setup_status_count,"raw assertion during earlier active status does not manufacture local SETUP");
        else require(s.returns==s.entries&&!s.active,"actual patched normal handler returns");
        if(local){
            require(s.first_setup_status==status&&s.latest_setup_status==status&&s.latest_setup_id==expected_entries,"selected status records refer to exact invocation");
            require((s.first_setup_markers&0x1ff3u)==0x1ff3u&&(s.first_setup_markers&RecoveryPrivateDcdDiagnostics::SetupTestTrue),"normal exact private SETUP path includes all setup markers and TRUE predicate");
        }else if(private_case!="private-raw-active")require((!s.entries||(s.latest_markers&RecoveryPrivateDcdDiagnostics::SetupTestFalse))&&s.setup_test_false_count==s.entries,"actual false predicate explicitly retained");
        if(private_case=="private-normal")require(s.marker_calls==13&&s.latest_markers==(0x1fffu|RecoveryPrivateDcdDiagnostics::SetupTestTrue),"all thirteen private source markers required individually");
    }
    require(s.enabled_setup_count==s.setup_status_count&&s.first_enabled_setup_id==s.first_setup_id&&s.first_enabled_setup_status==s.first_setup_status&&s.first_enabled_setup_markers==s.first_setup_markers,"all post-enable-only scenarios bind separate enabled first record exactly");
    independent();host_clock_us=9999999;independent();
    require(!RecoveryStartupDiagnostics::CapturedPrivateInto(unavailable)&&!unavailable.valid,"private capture not published before ten seconds");
    host_clock_us=10000000;independent();
    RecoveryPrivateDcdDiagnostics::Snapshot captured;
    require(RecoveryStartupDiagnostics::CapturedPrivateInto(captured)&&!memcmp(&captured,&s,sizeof(s)),"same frozen private history published with task/setup/pre banks");
    RecoverySetupIrqDiagnostics::Snapshot setup;RecoveryPreSetupDiagnostics::Snapshot pre;RecoveryTaskDiagnostics::Snapshot task;
    require(RecoveryStartupDiagnostics::CapturedSetupInto(setup)&&RecoveryStartupDiagnostics::CapturedPreSetupInto(pre)&&RecoveryStartupDiagnostics::CapturedTaskInto(task),"all frozen observer banks share one release boundary");
    unsigned expected[8];RecoveryPrivateDcdDiagnostics::Panel(s,pre,setup,task,expected);
    for(unsigned i=0;i<8;++i)require(expected[i]==task.pixels[i],"frozen current whole-button panel matches private record");
    require(expected[0]==0&&expected[1]==0,"menu pair dark");for(unsigned i=2;i<8;i+=2)require(expected[i]==expected[i+1],"both LEDs of each main button same");
    if(private_case=="private-raw-between"||private_case=="private-raw-active")require(expected[2]==RecoveryTaskDiagnostics::Cyan&&expected[4]==0,"no-serial RAW positive without any handler-local SETUP unambiguous");
    if(private_case=="private-no-raw"||private_case=="private-none")require(expected[2]==RecoveryTaskDiagnostics::Blue&&expected[4]==0,"no RAW reproduction and no local SETUP remain non-diagnostic");
    if(private_stop>=0){
        const unsigned completed=unsigned(private_stop)+(private_after?1u:0u);
        using namespace RecoveryTaskDiagnostics;
        unsigned branch=completed>1?Red:Off;
        if(completed>5)branch=Orange;if(completed>7)branch=Yellow;if(completed>8)branch=Cyan;if(completed>9)branch=Green;if(completed>11)branch=White;
        require(expected[4]==branch,"independent physical branch color follows exact completed source marker, prebranch residual remains RED");
        require(expected[2]==(completed>1?Yellow:completed?Cyan:Magenta),"independent physical local-status color at each artificial stop");
    }
    if(private_case=="private-no-entry")require(expected[2]==RecoveryTaskDiagnostics::Green&&expected[4]==0,"valid frozen noentry/noRAW distinct from all-dark unknown");
    if(private_case=="private-no-entry-raw")require(expected[2]==RecoveryTaskDiagnostics::Magenta&&expected[4]==0,"valid frozen noentry/RAW positive unambiguous");
    if(private_case=="private-queue-drop")require(setup.setup_dropped==1&&expected[6]==RecoveryTaskDiagnostics::Red,"actual full queue reports drop independently of private normal return");
    if(private_case=="private-queue-accept")require(setup.setup_accepted==1&&expected[6]==RecoveryTaskDiagnostics::Cyan,"actual FIFO SETUP acceptance retained downstream");
    const auto words=led_words;private_stop=-1;private_case="private-post-freeze";direct_irq(USB_INTS_SETUP_REQ_BITS);host_exception=0;
    host_clock_us=20000000;independent();RecoveryPrivateDcdDiagnostics::Snapshot unchanged;
    require(RecoveryStartupDiagnostics::CapturedPrivateInto(unchanged)&&!memcmp(&unchanged,&captured,sizeof(captured))&&words==led_words,"later private history cannot mutate frozen telemetry or settled panel");
    require(storage.files==files,"private observer changes no persistence bytes");
    std::printf("%s=PASS patched_private_handler_SOURCE_FAITHFUL physical_cpu_fault=NOT_MODELED\n",argv[2]);delete recovery_configurator;return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
