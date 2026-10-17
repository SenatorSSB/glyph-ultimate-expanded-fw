// Actual pinned USBD private-state observation only; appended host probe in C TU.
extern "C" bool glyph_host_addressed();
extern "C" uint8_t glyph_host_configuration();
namespace {
std::string hex_bytes(const Bytes &bytes){static const char h[]="0123456789abcdef";std::string out;for(auto b:bytes){out+=h[b>>4];out+=h[b&15];}return out;}
unsigned le16(const Bytes &bytes,unsigned offset){return bytes[offset]|(unsigned(bytes[offset+1])<<8);}
std::vector<std::string> snapshots;std::vector<unsigned> ids;
void snapshot(const std::string &label,const Bytes &bytes={}){
 std::string j="{\"event\":\""+label+"\",\"bytes_hex\":\""+hex_bytes(bytes)+"\",\"dcd_address_model\":"+std::to_string(dcd_address)+",\"addressed\":"+(glyph_host_addressed()?"true":"false")+",\"configuration\":"+std::to_string(glyph_host_configuration())+",\"mounted\":"+(tud_mounted()?"true":"false")+",\"connected\":"+(tud_connected()?"true":"false")+",\"cdc_endpoint_open_calls\":"+std::to_string(opened);
 if(bytes.size()==18&&bytes[1]==TUSB_DESC_DEVICE){const unsigned vid=le16(bytes,8),pid=le16(bytes,10);ids.push_back((vid<<16)|pid);j+=",\"vid\":"+std::to_string(vid)+",\"pid\":"+std::to_string(pid);}
 else j+=",\"vid\":null,\"pid\":null";
 snapshots.push_back(j+"}");
}
void descriptor(const char *label,unsigned length){control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_DEVICE<<8,length));require(control_rx.size()==std::min(length,18u),"actual device descriptor transfer");snapshot(label,control_rx);}
}
int main(int argc,char**argv){try{
 require(argc==5,"fixture/boundary/initial/length");selected_timing="identity-matrix";
 const char boundary=argv[2][0];const std::string initial=argv[3];const unsigned first_length=unsigned(std::stoul(argv[4]));pre_attach_configurator=initial=="configurator";
 seed(argv[1],&config);require(profile_store.Read(1,config_profile)==ProfileStore::Status::Ok,"fixture profile");require(profile_store.Create(config_profile,"useful3",0,identity(0x60)).id==3&&profile_store.Create(config_profile,"useful4",0,identity(0x61)).id==4,"useful fixture");
 const auto files=storage.files;RecoveryStartupDiagnostics::CapturePrevious();TinyUSBDevice.begin(0);require(tud_inited()&&attached&&Adafruit_USBD_CDC::getInstanceCount()==1,"initialized attached sole CDC");
 const auto live=tud_descriptor_device_cb();require((unsigned(live[8])|(unsigned(live[9])<<8))==0x2e8a,"exact target bootstrap VID");require((unsigned(live[10])|(unsigned(live[11])<<8))==(pre_attach_configurator?0x1092u:0x000au),"exact target bootstrap or pre-attach control PID");
 snapshot("attached");bool injected=false;
 auto inject=[&](char at){if(at!=boundary)return;require(!injected,"one recovery construction");injected=true;snapshot("before-constructor");const uint8_t *same=tud_descriptor_device_cb();enter_recovery_configurator();recovery_loop();
#if EXPECT_DIAGNOSTICS
 const uint32_t expected=tud_mounted()?0x18000000u:(tud_connected()?0x00001800u:0x18180000u);require(last_led_words[0]==expected&&last_led_words[1]==expected&&last_led_words[2]==0&&last_led_words[3]==0,"sticky phase11 downstream state");
 require(led_frames.size()>=11&&std::all_of(led_frames.begin(),led_frames.begin()+10,[](uint32_t color){return color==0x00180000u;}),"early phase frames all red; no transient 13-color sequence or new waits");
#endif
 require(tud_descriptor_device_cb()==same,"live descriptor address remains identical");snapshot("after-constructor");};
 inject('A');dcd_event_bus_reset(0,TUSB_SPEED_FULL,false);task();snapshot("bus-reset");inject('B');
 descriptor("first-device",first_length);inject('C');descriptor("repeat-device",18);
 control(req(0,TUSB_REQ_SET_ADDRESS,5));require(glyph_host_addressed()&&dcd_address==5,"real USBD address state and DCD API");snapshot("set-address");inject('D');descriptor("after-address-device",18);
 control(req(0x80,TUSB_REQ_GET_CONFIGURATION,0,1));snapshot("get-configuration",control_rx);inject('E');
 control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_CONFIGURATION<<8,9));require(control_rx.size()==9,"configuration header");snapshot("config-header",control_rx);
 control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_CONFIGURATION<<8,256));require(control_rx.size()==75&&control_rx[4]==2,"actual CDC configuration");const auto cfg=control_rx;snapshot("config-full",cfg);inject('F');descriptor("after-config-device",18);inject('G');
 control(req(0,TUSB_REQ_SET_CONFIGURATION,1));require(tud_mounted()&&glyph_host_configuration()==1&&opened==3,"actual CDC endpoint activation");snapshot("set-configuration");inject('H');descriptor("configured-device",18);
 require(injected&&boot.outcome==BootOutcome::RecoveryConfigurator,"actual recovery route published");
 require(Bytes(tud_descriptor_configuration_cb(0),tud_descriptor_configuration_cb(0)+75)==cfg,"identity writes never change CDC configuration bytes");
 const bool mixed=std::any_of(ids.begin(),ids.end(),[&](unsigned id){return id!=ids[0];});
 const bool expected_mixed=!EXPECT_DIAGNOSTICS&&!pre_attach_configurator&&((boundary=='C'&&first_length==18)||boundary=='D'||boundary=='E'||boundary=='F'||boundary=='G'||boundary=='H');
 require(mixed==expected_mixed,"source-predicted mixed or stable identity");
control(req(0x21,CDC_REQUEST_SET_CONTROL_LINE_STATE,3));require(tud_cdc_n_connected(0),"real CDC DTR");
#if EXPECT_DIAGNOSTICS
 for(unsigned id:ids)require(id==unsigned(pre_attach_configurator?0x2e8a1092:0x2e8a000a),"candidate recovery retains exactly attached identity");
 recovery_loop();require(last_led_words[0]==0x18000000u&&last_led_words[1]==last_led_words[0]&&last_led_words[2]==0&&last_led_words[3]==0,"single MB1 green mounted state, LF4 dark");
 // Merely seeing a malformed/unsupported command byte must not produce white.
 simple(CMD_UNSPECIFIED);require(last_led_words[0]==0x18000000u,"unknown command cannot claim valid inspection");
#endif
 inspect();
 require(storage.files==files,"all inspection/refusals preserve persistent bytes");require(attach_calls==1&&detach_calls==0,"no detach/reattach from constructor");
#if EXPECT_DIAGNOSTICS
 require(last_led_words[0]==0x18181800u&&last_led_words[1]==last_led_words[0]&&last_led_words[2]==0&&last_led_words[3]==0,"white only after decoded valid inspection");
#endif
 std::printf("{\"result\":\"PASS\",\"frozen\":%s,\"boundary\":\"%c\",\"initial_identity\":\"%s\",\"first_device_length\":%u,\"mixed_identity\":%s,\"configured\":true,\"cdc_endpoints\":3,\"detach_calls\":0,\"physical_host_acceptance\":\"NOT_MODELED\",\"snapshots\":[",EXPECT_DIAGNOSTICS?"false":"true",boundary,initial.c_str(),first_length,mixed?"true":"false");
 for(size_t i=0;i<snapshots.size();++i)std::printf("%s%s",i?",":"",snapshots[i].c_str());std::puts("]}");delete recovery_configurator;return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
