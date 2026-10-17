using namespace RecoveryTaskDiagnostics;
if(scenario=="before-entry")require(s.entered==0&&s.active==0&&s.pixels[0]==Red,"first foreground task never entered remains distinct");
if(scenario=="no-events"||scenario=="queue-empty"||scenario=="soft-irq-locked")require(s.first_returned&&s.entered==s.returned&&s.empty_reads&&s.queue_attempted==0&&s.pixels[0]==Green,"actual empty queue returns without manufacturing event progress");
if(scenario=="task-active-zero"||scenario=="core1-active")require(s.active==1&&!s.first_returned&&!s.total_resets&&s.pixels[0]==Orange&&s.pixels[1]==Off,"first active zero-reset task independently identifiable");
if(scenario=="later-active"||scenario=="later-recent")require(s.first_returned&&s.active>1&&s.latest_returned<s.active&&s.pixels[0]==White,"later active invocation cannot hide behind first return");
if(scenario=="task-multiple")require(s.first_returned&&s.entered>32&&s.entered==s.returned&&s.latest_returned==s.entered&&s.pixels[0]==Green,"multiple normal invocations preserve first anchor and latest return");
if(scenario=="pre-first-reset")require(s.total_resets==1&&s.pre_first_resets==1&&s.first_resets==0&&s.reset_completed==1&&s.reset_continued==1,"pre-entry reset never attributed to active first invocation");
if(scenario=="post-first-reset")require(s.total_resets==1&&s.pre_first_resets==0&&s.first_resets==0&&s.post_first_resets==1&&s.reset_completed==1,"post-first-return reset independently attributed");
if(scenario=="one-reset")require(s.first_resets==1&&s.total_resets==1&&s.reset_consumed==1&&s.first_reset_completed==1&&s.reset_completed==1&&s.reset_continued==1&&s.class_entered==15&&s.class_returned==15&&driver_enters==5&&driver_returns==5,"one reset completes exact XInput CDC MSC HID MIDI reset paths and task continues");
if(scenario=="two-resets")require(s.first_resets==2&&s.total_resets==2&&s.reset_consumed==2&&s.reset_completed==2&&driver_enters==10&&driver_returns==10,"two reset emissions preserve invocation attribution and two complete reset passes");
if(scenario=="continuous-reset")require(s.active==1&&s.first_resets>=128&&s.active_resets==s.first_resets&&s.reset_completed>=126&&s.pixels[1]==Magenta,"replenished real queue leaves first task active with multiple attributed emissions");
if(scenario=="hardware-irq-locked")require(s.active==1&&__usb_mutex.held&&s.first_resets==1&&s.queue_accepted==1&&s.reset_consumed==0&&s.pixels[1]==Blue,"hardware IRQ queues RESET independently of outer foreground mutex");
if(scenario=="core1-irqs")require(s.active==1&&s.first_resets==32&&s.active_resets==32&&s.queue_failed==16&&s.reset_dropped==16&&s.pixels[1]==Magenta,"independent observer sees ongoing IRQ emissions even with foreground paused");
if(scenario=="queue-partial")require(s.queue_attempted==4&&s.queue_accepted==4&&s.queue_failed==0&&s.max_occupancy==4&&s.empty_reads,"partial queue drains all actual FIFO events");
if(scenario=="queue-full")require(s.queue_attempted==16&&s.queue_accepted==16&&s.queue_failed==0&&s.max_occupancy==16&&s.pixels[5]==Magenta,"full non-overwriting Pico queue pressure is distinct from loss");
if(scenario=="queue-failed"||scenario=="drop-reset")require(s.queue_attempted==17&&s.queue_accepted==16&&s.queue_failed==1&&s.reset_dropped==1&&s.total_resets==1&&s.reset_consumed==0&&s.pixels[5]==Red,"dropped RESET emission never masquerades as accepted or consumed reset");
if(scenario=="drop-setup")require(s.queue_attempted==17&&s.queue_accepted==16&&s.queue_failed==1&&s.setup_dropped==1&&(s.event_flags&2u)&&s.setup_consumed==0&&s.control_began==0&&s.pixels[5]==Orange,"dropped SETUP emission never masquerades as accepted control processing");
if(scenario=="raw-only")require(s.raw_setup_seen&&!(s.event_flags&2u)&&s.setup_consumed==0&&s.pixels[4]==Blue,"raw hardware SETUP without DCD event is an independent distinction");
if(scenario=="dcd-setup")require((s.event_flags&2u)&&s.setup_consumed==0&&s.control_began==0&&s.pixels[4]==Cyan,"DCD emitted SETUP without task consumption remains explicit");
if(scenario=="setup-consumed")require(s.setup_consumed==1&&s.control_began==0&&s.pixels[4]==Green,"accepted consumed SETUP before control entry is distinct");
if(scenario=="control-began")require(s.setup_consumed==1&&s.control_began==1&&s.task_flags==0&&s.pixels[4]==White&&s.pixels[6]==Off,"control request begins before descriptor submission");
if(scenario=="descriptor")require(s.control_began&&s.pixels[6]==Yellow&&!(s.task_flags&6u),"device descriptor submission remains distinct from address and host receipt");
if(scenario=="address-request")require(s.pixels[6]==Cyan&&(s.task_flags&2u)&&!(s.task_flags&4u)&&usb_hw->dev_addr_ctrl==0,"SET_ADDRESS request precedes EP0 status completion address application");
if(scenario=="address-applied")require(s.pixels[6]==Blue&&(s.task_flags&4u)&&usb_hw->dev_addr_ctrl==5,"actual DCD status applies address without configured claim");
if(scenario=="configured")require(s.pixels[6]==Green&&(s.task_flags&8u)&&tud_mounted(),"configured device state independent of host serial node existence");
if(scenario=="inspection")require(s.pixels[6]==White&&(s.task_flags&16u),"complete supported decoded recovery command distinct from configuration");
if(scenario.rfind("stall-",0)==0){
    require(s.active==1&&__usb_mutex.held&&s.first_resets==1&&s.reset_consumed==1&&!s.first_returned,"injected reset processing non-return preserves real foreground owner");
    unsigned expected=0;
    if(scenario=="stall-configuration-enter"||scenario=="stall-class-0-enter"||scenario=="stall-class-0-body"||scenario=="stall-class-0-return"||scenario=="stall-class-1-enter")expected=1;
    if(scenario=="stall-class-1-body")expected=2;
    if(scenario=="stall-class-1-return"||scenario=="stall-class-2-enter"||scenario=="stall-class-2-body"||scenario=="stall-class-2-return"||scenario=="stall-class-3-enter"||scenario=="stall-class-3-body"||scenario=="stall-class-3-return"||scenario=="stall-class-4-enter")expected=3;
    if(scenario=="stall-class-4-body")expected=4;
    if(scenario=="stall-class-4-return"||scenario=="stall-configuration-return"||scenario=="stall-control-enter")expected=5;
    if(scenario=="stall-control-return"||scenario=="stall-continued")expected=6;
    if(scenario=="stall-empty-return")expected=7;
    require(expected&&s.reset_stage==expected,"exact last observable class/reset completion boundary preserved");
    if(scenario.rfind("stall-class-",0)==0){
        unsigned i=unsigned(scenario[12]-'0');const std::string side=scenario.substr(14);
        const unsigned before=i?((1u<<(i-1))-1u):0u,bit=i?(1u<<(i-1)):0u;
        require(s.class_entered==(before|((side=="body"||side=="return")?bit:0u))&&s.class_returned==(before|(side=="return"?bit:0u)),"all exact linked class wrapper entry/return masks distinguish hidden MSC/HID stage");
    }
    require(s.reset_completed==(expected>=6?1u:0u),"reset processing completion never inferred from emission/consumption alone");
}

if(scenario=="pullup-off")require(s.pullup==1&&s.pixels[7]==Red,"current pullup OFF is explicit and independent of historical milestones");

if(scenario=="descriptor-dropped-reset")require(s.reset_dropped==1&&s.reset_completed==0&&s.setup_consumed&&s.control_began&&(s.task_flags&1u)&&s.pixels[6]==Yellow,"actual descriptor progress remains visible after dropped RESET despite legacy epoch mismatch");
if(scenario=="configured-reset"||scenario=="deconfigured")require((s.task_flags&8u)&&!s.configured_current&&s.pixels[6]==Magenta,"retired configuration never masquerades as current configured device");
