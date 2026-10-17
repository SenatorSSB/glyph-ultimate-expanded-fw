#include <Adafruit_TinyUSB.h>
#include "hardware/structs/usb.h"
#include "hardware/watchdog.h"
#include "hardware/pio.h"
#include "core/RecoveryStartupDiagnostics.hpp"
#include "core/RecoveryInitialization.hpp"
#include "core/ConfigWriteCandidate.hpp"
#define main retained_timeout_main
#include "retained_timeout_harness.inc"
#undef main
using Bytes=std::vector<uint8_t>;
extern "C" {
#include "device/dcd.h"
#include "device/usbd_pvt.h"
}
UsbHw usb_registers;WatchdogHw watchdog_registers;PioHw pios[2];
mutex_t __usb_mutex;
namespace {
bool attached=false,port_initialized=false,pio_available=true,sm_enabled=false;
std::string selected_timing;unsigned boundary_calls=0;
void HostBoundary(const char*);
unsigned tasks=0,opened=0,pio_words=0,led_updates=0,pio_claims=0,dcd_address=0,attach_calls=0,detach_calls=0;bool pre_attach_configurator=false;uint32_t last_led_words[4]={};std::vector<uint32_t> led_frames;bool before_cdc_pending=false;PIO used_pio=nullptr;uint32_t max_led_interval=0;
struct Transfer {uint8_t *buffer=nullptr;uint16_t bytes=0;} endpoints[256];
Bytes control_rx,host_rx;bool capturing=false;
Config config=Config_init_default;UltimateProfile config_profile=UltimateProfile_init_default;InputState inputs;
ProfileStoreTransactionIdentity identity(uint64_t token){ProfileStoreTransactionIdentity t;t.token=token;t.digest[0]=uint8_t(token);return t;}
Bytes outgoing;size_t sent=0;
ConfiguratorBackend *recovery_configurator=nullptr;
enum class BootOutcome{Pending,Normal,RecoveryConfigurator};
struct BootSnapshot{BootOutcome outcome=BootOutcome::Pending;bool display_ready=false;}boot;
void publish_boot_state(BootOutcome o,bool d){require(boot.outcome==BootOutcome::Pending,"single boot decision");boot={o,d};}
BootSnapshot read_boot_state(){return boot;}
bool validate_glyph_config(const Config &,ConfigValidationError &){return true;}
InputSource **input_sources=nullptr;size_t input_source_count=0;
#include "recovery_route.inc"
#include "recovery_loop.inc"
void task(){++tasks;
 if(sent<outgoing.size()&&endpoints[1].buffer){auto transfer=endpoints[1];endpoints[1]={};size_t n=std::min(size_t(transfer.bytes),outgoing.size()-sent);std::memcpy(transfer.buffer,outgoing.data()+sent,n);sent+=n;dcd_event_xfer_complete(0,1,n,XFER_RESULT_SUCCESS,false);}
 tud_task();}
void control(const tusb_control_request_t &request){control_rx.clear();dcd_event_setup_received(0,reinterpret_cast<const uint8_t*>(&request),false);task();}
tusb_control_request_t req(uint8_t type,uint8_t request,uint16_t value=0,uint16_t length=0){tusb_control_request_t r{};r.bmRequestType=type;r.bRequest=request;r.wValue=value;r.wLength=length;return r;}
void host_enumerate(){
 require(attached&&port_initialized,"host cannot enumerate unattached device");
 dcd_event_bus_reset(0,TUSB_SPEED_FULL,false);task();
 control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_DEVICE<<8,18));
 require(control_rx.size()==18,"real GET_DESCRIPTOR device completion");
 control(req(0,TUSB_REQ_SET_ADDRESS,5));
 control(req(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_CONFIGURATION<<8,256));
 require(control_rx.size()==75&&control_rx[4]==2,"real config descriptor includes both CDC interfaces");
 control(req(0,TUSB_REQ_SET_CONFIGURATION,1));require(tud_mounted()&&opened>=3,"actual SET_CONFIG opens CDC endpoints");
 control(req(0x21,CDC_REQUEST_SET_CONTROL_LINE_STATE,3));require(tud_cdc_n_connected(0),"actual CDC DTR/RTS");
}
void HostBoundary(const char *point){
 if(selected_timing!=point)return;
 require(boundary_calls==0,"one exact timing injection");++boundary_calls;
 if(selected_timing=="during-inspection")require(persistence.load_calls>0,"inside Config inspection call");
 if(selected_timing=="after-publication")require(boot.outcome==BootOutcome::RecoveryConfigurator,"publication precedes host event");
 host_enumerate();
}
void host_send(const Bytes &wire){require(sent==outgoing.size(),"prior host bytes consumed");outgoing=wire;sent=0;task();}

ProfileStoreResponse transact(const ProfileStoreRequest&r){host_rx.clear();capturing=true;host_send(frame(r));if(selected_timing=="normal-configurator")recovery_configurator->SendReport();else recovery_loop();task();capturing=false;DuplexStream result;result.tx=host_rx;return response(result);}
void simple(Command command,const Bytes &body={}){host_rx.clear();capturing=true;DuplexStream wire;packetio::COBSPrint packet(wire);packet.write(uint8_t(command));packet.write(body.data(),body.size());require(packet.end(),"simple frame");host_send(wire.tx);if(selected_timing=="normal-configurator")recovery_configurator->SendReport();else recovery_loop();task();capturing=false;}
void inspect(){
 auto pulse=status();pulse.operation=PROFILE_STORE_LIVENESS;require(transact(pulse).status==PROFILE_STORE_OK,"recovery PULSE actual CDC/backend");
 auto health=transact(status());require(health.recovery_flags&(1u<<19),"read-only service flag");
 require(transact(list()).entries_count==4,"recovery LIST");
 for(unsigned id:{1u,3u,4u}){auto r=status();r.operation=PROFILE_STORE_READ;r.profile_id=id;auto out=transact(r);require(out.status==PROFILE_STORE_OK&&out.has_profile,"full recovery READ real CDC");r.operation=PROFILE_STORE_INSPECT_HEALTH;require(transact(r).status==PROFILE_STORE_OK,"recovery HEALTH");}
 simple(CMD_GET_DEVICE_INFO);require(!host_rx.empty()&&decode(host_rx)[0]==CMD_SET_DEVICE_INFO,"recovery device info");
 const auto files=storage.files;const auto generation=profile_store.Generation();const unsigned saves=persistence.save_calls;
 for(unsigned op=PROFILE_STORE_CREATE;op<=PROFILE_STORE_SET_MODE_REFERENCE;++op){auto r=status();r.operation=decltype(r.operation)(op);r.request_token=0x8000+op;r.expected_store_generation=generation;r.expected_store_incarnation=profile_store.Incarnation();r.profile_id=1;r.expected_profile_revision=1;r.has_profile=true;r.profile=config_profile;r.expected_config_generation=persistence.ConfigGeneration(config);auto out=transact(r);require(out.status==PROFILE_STORE_IO_FAILURE,"all new mutations refused in recovery");}
 simple(CMD_SET_CONFIG,config_bytes(config));require(!host_rx.empty()&&decode(host_rx)[0]==CMD_ERROR,"whole Config SET refused");require(storage.files==files&&profile_store.Generation()==generation&&persistence.save_calls==saves,"inspection and refusals make no persistent changes");
}
}
void mutex_init(mutex_t*m){m->held=false;}
bool mutex_try_enter(mutex_t*m,uint32_t*){if(m->held)return false;m->held=true;return true;}
bool mutex_enter_timeout_ms(mutex_t*m,uint32_t){return mutex_try_enter(m,nullptr);}
void mutex_exit(mutex_t*m){require(m->held,"balanced USB mutex");m->held=false;}
void TinyUSB_Port_InitDevice(uint8_t port){mutex_init(&__usb_mutex);port_initialized=true;require(Adafruit_USBD_CDC::getInstanceCount()==1,"CDC installed BEFORE tud_init/attach");require(tud_init(port),"real tud_init");if(before_cdc_pending){require(attached,"queued host request waits for attach");host_enumerate();}}
void TinyUSB_Port_EnterDFU(){throw std::runtime_error("DFU prohibited");}
uint8_t TinyUSB_Port_GetSerialNumber(uint8_t id[16]){std::memset(id,0x42,8);return 8;}
extern "C" {
void TinyUSB_Device_Task(){if(mutex_try_enter(&__usb_mutex,nullptr)){task();mutex_exit(&__usb_mutex);}}
void TinyUSB_Device_FlushCDC(){tud_cdc_n_write_flush(0);}
void dcd_init(uint8_t){++attach_calls;attached=true;usb_registers.sie_ctrl|=1;}
void dcd_int_enable(uint8_t){}void dcd_int_disable(uint8_t){}
void dcd_connect(uint8_t){++attach_calls;attached=true;usb_registers.sie_ctrl|=1;}
void dcd_disconnect(uint8_t){++detach_calls;attached=false;usb_registers.sie_ctrl&=~1u;}
void dcd_set_address(uint8_t port,uint8_t address){dcd_address=address;dcd_edpt_xfer(port,0x80,nullptr,0);}
void dcd_remote_wakeup(uint8_t){}
void dcd_sof_enable(uint8_t,bool){}
bool dcd_edpt_open(uint8_t,const tusb_desc_endpoint_t*){++opened;return true;}
void dcd_edpt_close_all(uint8_t){}
void dcd_edpt_stall(uint8_t,uint8_t){throw std::runtime_error("unexpected endpoint stall");}
void dcd_edpt_clear_stall(uint8_t,uint8_t){}
bool dcd_edpt_xfer(uint8_t port,uint8_t ep,uint8_t*buffer,uint16_t n){
 if(ep&0x80){if(n){auto &out=ep==0x80?control_rx:host_rx;out.insert(out.end(),buffer,buffer+n);}dcd_event_xfer_complete(port,ep,n,XFER_RESULT_SUCCESS,false);}
 else if(ep==0&&n==0)dcd_event_xfer_complete(port,ep,0,XFER_RESULT_SUCCESS,false);
 else endpoints[ep]={buffer,n};
 return true;
}
// Mach-O does not resolve ELF-style weak-undefined callbacks to null.
// These optional callbacks model null/no-op defaults, not device I/O.
// Target XInput app-driver/BOS/vendor overrides are omitted; this exercises
// pure CDC and does not claim complete linked production callback closure.
void dcd_edpt0_status_complete(uint8_t,const tusb_control_request_t*){}
void dcd_edpt_close(uint8_t,uint8_t){}
bool dcd_edpt_iso_alloc(uint8_t,uint8_t,uint16_t){return false;}
bool dcd_edpt_iso_activate(uint8_t,const tusb_desc_endpoint_t*){return false;}
bool dcd_edpt_xfer_fifo(uint8_t,uint8_t,tu_fifo_t*,uint16_t){return false;}
void tud_cdc_line_coding_cb(uint8_t,const cdc_line_coding_t*){}
void tud_cdc_rx_cb(uint8_t){}void tud_cdc_rx_wanted_cb(uint8_t,char){}
void tud_cdc_send_break_cb(uint8_t,uint16_t){}void tud_cdc_tx_complete_cb(uint8_t){}
const uint8_t* tud_descriptor_bos_cb(){return nullptr;}
const uint8_t* tud_descriptor_device_qualifier_cb(){return nullptr;}
const uint8_t* tud_descriptor_other_speed_configuration_cb(uint8_t){return nullptr;}
void tud_event_hook_cb(uint8_t,uint32_t,bool){}
const uint8_t* tud_hid_descriptor_report_cb(uint8_t){return nullptr;}
void tud_hid_report_complete_cb(uint8_t,const uint8_t*,uint16_t){}
bool tud_hid_set_idle_cb(uint8_t,uint8_t){return true;}
void tud_hid_set_protocol_cb(uint8_t,uint8_t){}void tud_midi_rx_cb(uint8_t){}
void tud_mount_cb(){}void tud_umount_cb(){}void tud_resume_cb(){}void tud_suspend_cb(bool){}
bool tud_vendor_control_xfer_cb(uint8_t,uint8_t,const tusb_control_request_t*){return false;}
const usbd_class_driver_t* usbd_app_driver_get_cb(uint8_t* count){*count=0;return nullptr;}
uint8_t tud_msc_get_maxlun_cb(){return 0;}
bool tud_msc_is_writable_cb(uint8_t){return false;}
void tud_msc_read10_complete_cb(uint8_t){}void tud_msc_write10_complete_cb(uint8_t){}
int32_t tud_msc_request_sense_cb(uint8_t,void*,uint16_t){return -1;}
void tud_msc_scsi_complete_cb(uint8_t,const uint8_t*){}
bool tud_msc_start_stop_cb(uint8_t,uint8_t,bool,bool){return false;}
// Unexercised optional MSC/MIDI callbacks link real class drivers, never success.
int32_t tud_msc_read10_cb(uint8_t,uint32_t,uint32_t,void*,uint32_t){return -1;}
int32_t tud_msc_write10_cb(uint8_t,uint32_t,uint32_t,uint8_t*,uint32_t){return -1;}
void tud_msc_inquiry_cb(uint8_t,uint8_t*,uint8_t*,uint8_t*){}
bool tud_msc_test_unit_ready_cb(uint8_t){return false;}
void tud_msc_capacity_cb(uint8_t,uint32_t *count,uint16_t *size){*count=0;*size=0;}
int32_t tud_msc_scsi_cb(uint8_t,const uint8_t*,void*,uint16_t){return -1;}
uint16_t tud_hid_get_report_cb(uint8_t,uint8_t,hid_report_type_t,uint8_t*,uint16_t){return 0;}
void tud_hid_set_report_cb(uint8_t,uint8_t,hid_report_type_t,const uint8_t*,uint16_t){}
}
bool USBTestAllowAutoCDC(){return selected_timing!="no-auto-cdc";}
void USBTestCoreBeforeCDC(){if(pre_attach_configurator){require(!tud_inited()&&!attached,"pre-attach identity control");TinyUSBDevice.setID(0x2e8a,0x1092);}if(selected_timing=="core-before-cdc"){require(!tud_inited()&&!attached&&Adafruit_USBD_CDC::getInstanceCount()==0,"before actual initial CDC registration is not enumerable");++boundary_calls;before_cdc_pending=true;}}
void USBTestDuringInspection(){if(boot.outcome==BootOutcome::Pending)HostBoundary("during-inspection");}
void yield(){TinyUSB_Device_Task();TinyUSB_Device_FlushCDC();}
bool pio_can_add_program(PIO p,const pio_program*){return pio_available&&!(selected_timing=="pio1-fallback"&&p==pio0);}
int pio_claim_unused_sm(PIO,bool required){require(!required,"diagnostic claim cannot panic");return pio_available&&selected_timing!="pio-no-sm"?0:-1;}
unsigned pio_add_program(PIO unit,const pio_program*p){++pio_claims;used_pio=unit;require(p->length==4&&p->instructions[0]==0x6021&&p->instructions[1]==0xe101&&p->instructions[2]==0xa401&&p->instructions[3]==0xe100,"exact pinned four-instruction LED program");return 0;}
void sm_config_set_wrap(pio_sm_config*,unsigned a,unsigned b){require(a==0&&b==3,"PIO wrap");}
void sm_config_set_set_pins(pio_sm_config*,unsigned p,unsigned n){require(p==11&&n==1,"safe established Mk6 LED pin");}
void sm_config_set_out_pins(pio_sm_config*,unsigned p,unsigned n){require(p==11&&n==1,"same output pin");}
void sm_config_set_out_shift(pio_sm_config*,bool right,bool autopull,unsigned n){require(!right&&autopull&&n==24,"GRB24 autopull");}
void sm_config_set_clkdiv(pio_sm_config*,float n){require(n==16.25f,"8MHz LED clock at130MHz");}
void pio_gpio_init(PIO,unsigned p){require(p==11,"no other GPIO");}
void pio_sm_set_consecutive_pindirs(PIO,int,unsigned,unsigned,bool){}
void pio_sm_init(PIO,int,unsigned,const pio_sm_config*){}void pio_sm_set_pins(PIO,int,unsigned){}void pio_sm_set_enabled(PIO,int,bool value){sm_enabled=value;}
bool pio_sm_is_tx_fifo_empty(PIO,int){return pio_words==0&&selected_timing!="pio-fifo-busy";}
void pio_sm_put(PIO,int,uint32_t word){require(!sm_enabled&&pio_words<4,"SM disabled throughout frame preload, USB IRQ may interleave");last_led_words[pio_words++]=word;}
void busy_wait_us_32(uint32_t n){require(n==200&&pio_words==4,"bounded LED protocol interval");max_led_interval=std::max(max_led_interval,n);++led_updates;led_frames.push_back(last_led_words[0]);pio_words=0;}
#ifdef GLYPH_IDENTITY_MATRIX
#include "identity_matrix.inc"
#define main retained_startup_main
#endif
int main(int argc,char**argv){try{
 require(argc==3,"fixture/timing args");std::string timing=argv[2];selected_timing=timing;pio_available=timing!="pio-unavailable";
 seed(argv[1],&config);require(profile_store.Read(1,config_profile)==ProfileStore::Status::Ok,"profile fixture");require(profile_store.Create(config_profile,"useful3",0,identity(0x60)).id==3&&profile_store.Create(config_profile,"useful4",0,identity(0x61)).id==4,"useful3/4");
 // Diagnostic namespace is disjoint and only register3 may change.
 for(unsigned i=0;i<8;++i)watchdog_registers.scratch[i]=0x100+i;
 #if EXPECT_DIAGNOSTICS
 require(!RecoveryStartupDiagnostics::Valid(0x4d445354)&&!RecoveryStartupDiagnostics::Valid(RecoveryStartupDiagnostics::kMagic|(14u<<8))&&!RecoveryStartupDiagnostics::Valid(RecoveryStartupDiagnostics::kMagic),"selector magic and invalid phases rejected");
 RecoveryStartupDiagnostics::CapturePrevious();require(RecoveryStartupDiagnostics::Previous()==0&&watchdog_registers.scratch[3]==0&&pio_claims==0,"foreign namespace cleared without hardware claim");
 watchdog_registers.scratch[3]=RecoveryStartupDiagnostics::kMagic|(5u<<8)|3;RecoveryStartupDiagnostics::CapturePrevious();require(RecoveryStartupDiagnostics::Previous()!=0,"retained warm marker capture");
#endif
 TinyUSBDevice.begin(0);require(tud_inited()&&attached&&Adafruit_USBD_CDC::getInstanceCount()==1,"core USB initialized before recovery");

 const auto before=storage.files;
#if !GLYPH_STRICT_HARDENING_CANDIDATE
 if(timing=="production-retain-policy"){
  auto *backend=new ConfiguratorBackend(inputs,input_sources,input_source_count,config,Serial,ConfiguratorBackend::UsbIdentityPolicy::RetainAttachedForRecoveryDiagnostic);
  const auto descriptor=tud_descriptor_device_cb();require(descriptor[8]==0x8a&&descriptor[9]==0x2e&&descriptor[10]==0x92&&descriptor[11]==0x10,"noncandidate cannot opt into diagnostic identity");
  require(RecoveryStartupDiagnostics::Current()==0&&pio_claims==0&&storage.files==before,"noncandidate diagnostics inactive");host_enumerate();delete backend;std::puts("production_identity_guard=PASS");return 0;
 }
#endif
 if(timing=="normal-configurator"){
  Serial.begin(115200);recovery_configurator=new ConfiguratorBackend(inputs,input_sources,input_source_count,config,Serial);const auto descriptor=tud_descriptor_device_cb();require(descriptor[8]==0x8a&&descriptor[9]==0x2e&&descriptor[10]==0x92&&descriptor[11]==0x10,"normal Configurator identity remains2e8a:1092");host_enumerate();
  auto h=transact(status());require(h.status==PROFILE_STORE_OK&&!(h.recovery_flags&(1u<<19)),"normal Configurator status is not recovery");
  simple(CMD_GET_DEVICE_INFO);require(!host_rx.empty()&&decode(host_rx)[0]==CMD_SET_DEVICE_INFO,"normal Configurator device info");
  require(RecoveryStartupDiagnostics::Current()==0&&pio_claims==0&&storage.files==before,"normal Configurator never claims diagnostic PIO/writes files");
  delete recovery_configurator;std::puts("normal_configurator=PASS actual_usb=true diagnostics_inactive=true");return 0;
 }
 enter_recovery_configurator();HostBoundary("after-publication");
 const bool named=timing=="before-inspection"||timing=="during-inspection"||timing=="before-serial"||timing=="after-serial"||timing=="after-publication"||timing=="core-before-cdc";
 require(boundary_calls==(named?1u:0u),"exact named timing boundary exercised");
 if(!tud_mounted())host_enumerate();
 const auto desc=tud_descriptor_configuration_cb(0);require(desc[4]==2&&desc[2]==75,"idempotent Serial.begin retains CDC descriptors");
 for(unsigned i=0;i<8;++i)if(i!=0&&i!=1&&i!=2&&i!=3)require(watchdog_registers.scratch[i]==0x100+i,"SDK scratch preserved");
 require(watchdog_registers.scratch[0]==0&&watchdog_registers.scratch[1]==0&&watchdog_registers.scratch[2]==0,"recovery selector clearing retained");
 require(storage.files==before&&boot.outcome==BootOutcome::RecoveryConfigurator,"source recovery inspection and publication");inspect();
 require(tasks>0&&tud_mounted(),"real USB device task progressed");
#if EXPECT_DIAGNOSTICS
 if(timing=="pio1-fallback")require(used_pio==pio1,"second PIO fallback");
 const auto marker=RecoveryStartupDiagnostics::Current();require(((marker>>8)&255u)==13&&(marker&127u)==127u,"all USB/route observations and request byte seen");require(watchdog_registers.scratch[3]==marker,"stable flags remain in scratch");require(bool(marker&128u)==(pio_available&&timing!="pio-no-sm"),"indicator availability is honest");require(pio_available&&timing!="pio-no-sm"&&timing!="pio-fifo-busy"?(led_updates>0&&max_led_interval==200):led_updates==0,"bounded indicator or graceful unavailable");
#else
 require(RecoveryStartupDiagnostics::Current()==0,"frozen source has no diagnostic marker");
#endif
 delete recovery_configurator;std::printf("rt2_startup_%s=PASS frozen=%d actual_usb_descriptors=true actual_usbd_events=true actual_cdc=true actual_backend=true read_only=true task_passes=%u LED_updates=%u physical_macOS=NOT_MODELED\n",timing.c_str(),!EXPECT_DIAGNOSTICS,tasks,led_updates);return 0;
 }catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
