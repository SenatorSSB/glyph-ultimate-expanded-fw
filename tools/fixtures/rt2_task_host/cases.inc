// Host-only fault injection at exact pinned task/class boundaries. The tested
// observer/publisher and route are production code, without foreground Read().
namespace {
struct TaskPaused {};
std::string task_case;
unsigned queue_passes=0,driver_enters=0,driver_returns=0,async_publishes=0;
bool injecting=false,paused=false;
void independent(){
    // Main/core0 is suspended in its task/handler boundary until this independent
    // publisher thread finishes. No foreground diagnostic Read() drives it.
    std::thread observer([]{host_core=1;recovery_observer_loop();host_core=0;});
    observer.join();++async_publishes;
}
void pair(unsigned a,unsigned b,const char* why){
    independent();auto s=RecoveryUsbDiagnostics::TaskRead();
    require(s.valid&&s.task_pixel==a&&s.progress_pixel==b,why);
    const auto word=RecoveryStartupDiagnostics::Current();
    require((word&0xffff0000u)==RecoveryStartupDiagnostics::kTaskPairMagic&&((word>>12)&15u)==a&&((word>>8)&15u)==b,"independent scratch publication");
    const uint32_t ac[]={0x001800,0x061800,0x001818,0x000018,0x180000};
    const uint32_t bc[]={0,0x181800,0x180018,0x180000,0x181818};
    require(led_words.size()>=4&&led_words[led_words.size()-4]==(ac[a]<<8)&&led_words[led_words.size()-3]==(bc[b]<<8)&&led_words[led_words.size()-2]==0&&led_words.back()==0,"physical four-word pair-only GRB frame");
}
void stop_task(){paused=true;throw TaskPaused{};}
void setup_only(){
    const auto request=req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_DEVICE<<8,18);
    host_setup_packet(request);
}
}
extern "C" void GlyphTaskBoundary(const char* point,unsigned index){
    if(task_case.empty()||injecting)return;
    const std::string at=point;
    if(at=="class-enter")++driver_enters;
    if(at=="class-return")++driver_returns;
    if(at=="queue"){
        ++queue_passes;
        if(queue_passes==1){
            const auto active=RecoveryUsbDiagnostics::TaskRead();
            require(active.active!=0&&__usb_mutex.held,"actual foreground task under USB mutex");
            pair(active.first_returned?4:1,0,"active task observed independently before first receive");
            injecting=true;
            if(task_case=="soft-irq-locked"){
                const auto before=RecoveryUsbDiagnostics::Read();irq_set_pending(31);interrupt_pass();
                const auto after=RecoveryUsbDiagnostics::Read();
                require(before.task_entered==after.task_entered,"software IRQ fails try-lock without task entry");
            }
            if(task_case=="setup-active")setup_only();
            else if(task_case!="no-events"&&task_case!="soft-irq-locked"&&task_case!="later-active"){
                physical_reset();
                if(task_case=="two-resets"||task_case=="queue-full")physical_reset();
                if(task_case=="queue-full")for(unsigned i=0;i<GLYPH_HOST_QUEUE_SIZE+8;++i)physical_reset();
                if(task_case=="reset-setup")setup_only();
                if(task_case=="suspend-filter")for(unsigned i=0;i<20;++i){dcd_event_bus_signal(0,DCD_EVENT_SUSPEND,true);dcd_event_bus_signal(0,DCD_EVENT_RESUME,true);}
            }
            injecting=false;
            if(task_case=="setup-active"){pair(1,2,"SETUP independently visible while task active");stop_task();}
            if(task_case=="hardware-irq-locked"){pair(2,0,"hardware DCD IRQ emits reset while foreground holds USB mutex");stop_task();}
            if(task_case=="later-active"){pair(4,0,"first returned remains green while later invocation active");stop_task();}
            if(task_case=="reset-setup")pair(2,2,"reset and SETUP independently visible before consumption");
        }
        if(task_case=="continuous-reset"){
            injecting=true;physical_reset();injecting=false;
            if(queue_passes==128){pair(3,1,"continuing reset replenishment cannot hide blue behind completion");stop_task();}
        }
    }
    std::string target="stall-"+at;
    if(at=="class-enter"||at=="class-return")target="stall-class-"+std::to_string(index)+"-"+(at=="class-enter"?"enter":"return");
    if(task_case==target){pair(2,at=="control-return"?1:0,"single reset blocked at exact processing boundary");stop_task();}
}
int main(int argc,char**argv){try{
    require(argc==3,"fixture/scenario");task_case=argv[2];const std::string scenario=task_case;task_case.clear();
    selected_timing="dcd-model";seed(argv[1],&config);const auto files=storage.files;
    RecoveryStartupDiagnostics::CapturePrevious();TinyUSBDevice.begin(0);enter_recovery_configurator();
    TinyUSB_Device_Task();require(RecoveryUsbDiagnostics::TaskRead().entered==0,"pre-loop foreground task never consumes first recovery-loop identity");
    pair(0,0,"pre-foreground-task RED/dark independent publication");
    // Hardware IRQ runs; software-task IRQ attempts are enabled and independently
    // fail try-lock whenever the actual foreground TinyUSB task owns the mutex.
    if(scenario=="pre-first-reset"){
        physical_reset();pair(0,0,"prior IRQ reset completion cannot claim first-task processing");
        auto prior=RecoveryUsbDiagnostics::TaskRead();require(prior.reset_completed==1&&prior.first_reset_completed==0,"IRQ processing separately tagged");
    }
    if(scenario=="later-active"){
        recovery_loop();pair(4,0,"first task returned");
        const auto frames=led_updates;
        for(unsigned i=0;i<1000;++i){TinyUSB_Device_Task();independent();}
        require(led_updates==frames,"healthy later calls never refresh anchored first-task green");
    }
    if(scenario=="before-entry"){}
    else if(scenario=="configured"||scenario=="inspection"){
        // First foreground invocation returns before normal host control progress.
        recovery_loop();physical_reset();control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_DEVICE<<8,18));
        pair(4,3,"control/device descriptor separate from task return");
        control(req(0,TUSB_REQ_SET_ADDRESS,5));control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_CONFIGURATION<<8,256));control(req(0,TUSB_REQ_SET_CONFIGURATION,1));
        pair(4,4,"actual configured milestone");
        if(scenario=="inspection"){control(req(0x21,CDC_REQUEST_SET_CONTROL_LINE_STATE,3));auto pulse=status();pulse.operation=PROFILE_STORE_LIVENESS;require(transact(pulse).status==PROFILE_STORE_OK,"complete decoded inspection");pair(4,4,"inspection remains white");}
    }else if(scenario=="unplug"){
        defer_task=true;dcd_event_bus_signal(0,DCD_EVENT_UNPLUGGED,true);defer_task=false;
        recovery_loop();pair(4,1,"generic RESET/UNPLUGGED processing marker never claims BUS_RESET receipt");
        auto s=RecoveryUsbDiagnostics::TaskRead();require((s.event_flags&4)&&s.first_resets==0&&s.first_reset_completed==1,"unplug ambiguity explicit");
    }else{
        task_case=scenario=="pre-first-reset"?"stall-control-enter":scenario;
        try{recovery_loop();}catch(const TaskPaused&){}
        if(!paused){
            auto s=RecoveryUsbDiagnostics::TaskRead();
            require(s.first_returned&&s.returned==s.entered,"actual first invocation returned");
            pair(4,scenario=="reset-setup"?3:scenario=="no-events"||scenario=="soft-irq-locked"?0:1,"settled returned pair");
            if(scenario=="one-reset"||scenario=="suspend-filter")require(s.first_resets==1&&s.first_reset_completed==1&&driver_enters==5&&driver_returns==5,"all exact target class callbacks return once; filtered suspend/resume add no resets");
            if(scenario=="two-resets")require(s.first_resets==2&&s.first_reset_completed==2&&driver_enters==10,"every reset repeats all five target callbacks");
            if(scenario=="queue-full")require(s.first_resets==GLYPH_HOST_QUEUE_SIZE+10&&s.first_reset_completed==GLYPH_HOST_QUEUE_SIZE,"bounded queue drops newest reset while event hook counts emissions");
        }else{
            auto s=RecoveryUsbDiagnostics::TaskRead();require(s.active&&__usb_mutex.held,"injected non-return retains actual foreground task ownership");
            if(scenario!="later-active")require(!s.first_returned,"paused first wrapper never returned");
            const auto count=led_updates;for(unsigned i=0;i<1000;++i)independent();require(led_updates==count,"unchanged asynchronous pair stays latched without refresh");
        }
    }
    require(storage.files==files,"diagnostic does not mutate persistence");
    auto s=RecoveryUsbDiagnostics::TaskRead();std::printf("task_observer_%s=PASS first_resets=%u first_completed=%u active=%u pair=%u/%u async=%u physical_macOS=NOT_MODELED\n",scenario.c_str(),s.first_resets,s.first_reset_completed,s.active,s.task_pixel,s.progress_pixel,async_publishes);
    delete recovery_configurator;return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
