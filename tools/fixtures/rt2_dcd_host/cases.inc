int main(int argc,char**argv){try{
 require(argc==3,"fixture/scenario");selected_timing="dcd-model";std::string scenario=argv[2];
 seed(argv[1],&config);require(profile_store.Read(1,config_profile)==ProfileStore::Status::Ok,"fixture");require(profile_store.Create(config_profile,"useful3",0,identity(0x60)).id==3&&profile_store.Create(config_profile,"useful4",0,identity(0x61)).id==4,"useful fixtures");const auto files=storage.files;
 require(RecoveryStartupDiagnostics::Valid(0x52540b0f)&&RecoveryStartupDiagnostics::Valid(0x52567d0f)&&!RecoveryStartupDiagnostics::Valid(0x52568d0f),"legacy/new scratch namespace validity");
 RecoveryStartupDiagnostics::CapturePrevious();TinyUSBDevice.begin(0);
 require(tud_inited()&&(usb_hw->main_ctrl&USB_MAIN_CTRL_CONTROLLER_EN_BITS)&&usb_hw->muxing==(USB_USB_MUXING_TO_PHY_BITS|USB_USB_MUXING_SOFTCON_BITS),"actual USBCTRL init reset/mux/controller writes");
 require(usb_hw->sie_ctrl&USB_SIE_CTRL_PULLUP_EN_BITS,"actual DCD connect enables pull-up");
 enter_recovery_configurator();const auto descriptor=tud_descriptor_device_cb();require(descriptor[8]==0x8a&&descriptor[9]==0x2e&&descriptor[10]==0x92&&descriptor[11]==0x10,"ordinary466 recovery identity restored");
 expect(0,"red before repeated loop");
 if(scenario=="pullup-off")dcd_disconnect(0);
 recovery_loop();expect(0,"one completed loop is not repeated-loop proof");recovery_loop();
 if(scenario=="pullup-off"){
  expect(1,"orange exposes post-repeat pull-up OFF");const auto count=led_updates;for(unsigned i=0;i<10000;++i)recovery_loop();require(led_updates==count,"unchanged orange is latched without refresh");
 }else{
  expect(2,"yellow post-repeat pull-up ON, host silent");
  auto s=RecoveryUsbDiagnostics::Read();require((s.irq_state&0x30d)==0x30d,"port complete, stack initialized, both NVIC IRQs enabled and known");
  const auto count=led_updates;for(unsigned i=0;i<10000;++i)recovery_loop();require(led_updates==count,"idle raw task-count changes never refresh LED");
  if(scenario!="silent"){
   if(scenario=="irq-deferred"||scenario=="irq-disabled"||scenario=="global-mask"){defer_hardware=scenario=="irq-deferred";if(scenario=="irq-disabled")dcd_int_disable(0);if(scenario=="global-mask")host_primask=1;physical_reset();expect(2,"no false reset before DCD IRQ");s=RecoveryUsbDiagnostics::Read();require((s.irq_state&2)&&s.ints&USB_INTS_BUS_RESET_BITS&&!(s.milestones&RecoveryUsbDiagnostics::BusReset),"raw pending reset distinct from DCD receipt");defer_hardware=false;host_primask=0;dcd_int_enable(0);interrupt_pass();}
   else physical_reset();
   expect(3,"magenta actual DCD bus reset");require(!tud_connected()&&!tud_mounted(),"reset is not connected/mounted");
   if(scenario!="reset"){
    if(scenario=="task-deferred")defer_task=true;
    control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_DEVICE<<8,18));expect(4,"blue actual DCD SETUP");
    if(defer_task){s=RecoveryUsbDiagnostics::Read();require(!tud_connected()&&!(s.milestones&RecoveryUsbDiagnostics::DeviceDescriptor)&&(s.irq_state&16),"DCD SETUP precedes task/policy and soft IRQ remains pending");defer_task=false;interrupt_pass();sample();}
    require(control_rx.size()==18&&tud_connected()&&(RecoveryUsbDiagnostics::Read().milestones&RecoveryUsbDiagnostics::DeviceDescriptor),"actual descriptor/control processing observed separately");
    if(scenario!="setup"){
     hold_address_ack=scenario=="address-pending";control(req(0,TUSB_REQ_SET_ADDRESS,5));expect(5,"cyan SET_ADDRESS processed");
     if(hold_address_ack){s=RecoveryUsbDiagnostics::Read();require(s.dev_addr==0&&(s.milestones&RecoveryUsbDiagnostics::AddressRequested)&&!(s.milestones&RecoveryUsbDiagnostics::AddressApplied),"requested address distinct from applied");hold_address_ack=false;pending_address_ack=false;dcd_event_xfer_complete(0,0x80,0,XFER_RESULT_SUCCESS,true);irq_set_pending(31);interrupt_pass();}
     require(usb_hw->dev_addr_ctrl==5&&(RecoveryUsbDiagnostics::Read().milestones&RecoveryUsbDiagnostics::AddressApplied),"actual pinned address write after status");
     if(scenario!="address"&&scenario!="address-pending"){
      control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_CONFIGURATION<<8,256));require(control_rx.size()==75,"CDC config descriptor");
      if(scenario=="configured"){control(req(0,TUSB_REQ_SET_CONFIGURATION,0x100));expect(5,"configuration high-byte alone is cfg0, never green");require(!tud_mounted()&&!(RecoveryUsbDiagnostics::Read().milestones&RecoveryUsbDiagnostics::ConfigurationComplete),"observer follows actual uint8 cfg_num");}
      control(req(0,TUSB_REQ_SET_CONFIGURATION,1));expect(6,"green actual configuration/mount");require(tud_mounted()&&opened==3,"actual CDC endpoints open");
      if(scenario=="replug"){
       usb_hw->sie_status|=USB_SIE_STATUS_SUSPENDED_BITS;usb_hw->intr|=USB_INTS_DEV_SUSPEND_BITS;interrupt_pass();expect(6,"forced-VBUS unplug perception is suspend, sticky progress unchanged");physical_reset();expect(6,"replug reset cannot regress sticky green");require(!tud_mounted()&&usb_hw->dev_addr_ctrl==0,"real reset clears current config/address");
       control(req(0,TUSB_REQ_SET_ADDRESS,5));control(req(0,TUSB_REQ_SET_CONFIGURATION,1));
      }
      if(scenario=="inspect"||scenario=="replug"){
       control(req(0x21,CDC_REQUEST_SET_CONTROL_LINE_STATE,3));inspect();expect(7,"white complete inspection decoded");const auto writes=led_updates;for(unsigned i=0;i<1000;++i)recovery_loop();require(led_updates==writes,"white stays latched with no refresh");
      }
     }
    }
   }
  }
 }
 require(storage.files==files,"observer/inspection/refusals never persist");require(led_updates<=8,"at most eight successful monotonic state frames per boot");
 require(led_words.size()==4*led_updates,"exact four pixel words per emitted frame");
 const uint32_t colors[]={0x001800,0x061800,0x181800,0x001818,0x000018,0x180018,0x180000,0x181818};unsigned last=0;
 for(size_t i=0;i<led_words.size();i+=4){require(led_words[i]==led_words[i+1]&&led_words[i+2]==0&&led_words[i+3]==0,"MB1 pair only, LF4 dark");unsigned found=8;for(unsigned j=0;j<8;++j)if(led_words[i]==(colors[j]<<8))found=j;require(found<8&&found>=last,"actual GRB colors never regress");last=found;}
 require(last==state(),"settled emitted MB1 agrees with milestone");
 auto s=RecoveryUsbDiagnostics::Read();require(s.task_entered==s.task_returned,"idle actual task returns; no proven5913-specific block");
 std::printf("dcd_observer_%s=PASS state=%u milestones=%u irq_state=%u LED_frames=%u actual_rp2040_init_irq=true physical_macOS=NOT_MODELED\n",scenario.c_str(),state(),s.milestones,s.irq_state,led_updates);delete recovery_configurator;return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
