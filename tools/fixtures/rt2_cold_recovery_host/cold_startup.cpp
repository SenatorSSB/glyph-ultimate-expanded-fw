// Include the retained actual CDC/USBD/backend fixture in this translation unit.
// The build driver renames only hardware boundary definitions, then appends the
// exact pinned port/DCD initialization bodies with boundary doubles.
#include "retained_startup.cpp"
#include "core/ColdRecoveryBoot.h"
#include "cold_port_dcd.inc"

bool cold_readonly_ready=false;
void USBColdDeviceBegin(){++descriptor_preparations;}
void USBColdDescriptorClear(){++descriptor_clears;}
void USBColdReadOnlyReady(){cold_readonly_ready=true;if(selected_timing=="start-failure")TinyUSBDevice.setID(0x2e8a,0xffff);}

extern "C" void TinyUSB_Device_Init(uint8_t);
bool GlyphRecoveryUsbReinitialize(){throw std::runtime_error("forbidden same-boot warm reset");}
void TinyUSB_Port_InitDevice(uint8_t p) { GlyphWrapPortInit(p); }
extern "C" void TinyUSB_Device_Task() { __wrap_TinyUSB_Device_Task(); }
extern "C" void TinyUSB_Device_FlushCDC() { __wrap_TinyUSB_Device_FlushCDC(); }

int main(int argc,char **argv) { try {
 require(argc==3,"fixture/cold case args");
 const std::string mode=argv[2]; selected_timing=mode;
 seed(argv[1],&config);
 require(profile_store.Read(1,config_profile)==ProfileStore::Status::Ok,"profile fixture");
 require(profile_store.Create(config_profile,"useful3",0,identity(0x60)).id==3&&profile_store.Create(config_profile,"useful4",0,identity(0x61)).id==4,"useful fixture");
 for(unsigned i=0;i<8;++i)watchdog_registers.scratch[i]=0;
 for(unsigned i=3;i<8;++i)watchdog_registers.scratch[i]=0x100+i;
 const auto before=storage.files;
 if(mode=="ordinary"||mode=="random"||mode=="mode-marker"||mode=="diag-marker"||mode=="wrong-reason"||mode=="bad-selectors"||mode=="arm") {
  if(mode=="random")watchdog_registers.scratch[2]=0x12345678;
  if(mode=="mode-marker")watchdog_registers.scratch[2]=0x4d445354;
  if(mode=="diag-marker")watchdog_registers.scratch[2]=0x525d0a00;
  if(mode=="wrong-reason"){watchdog_registers.scratch[2]=0x43525432;watchdog_registers.reason=2;}
  if(mode=="bad-selectors"){watchdog_registers.scratch[2]=0x43525432;watchdog_registers.scratch[0]=1;watchdog_registers.reason=1;}
  TinyUSB_Device_Init(0);
  require(!GlyphColdRecoveryBoot(),"ordinary init does not authorize recovery");
  require(port_calls==1&&attached&&tud_inited(),"ordinary startup point initializes port once");
  Serial.begin(115200);
  recovery_configurator=new ConfiguratorBackend(inputs,input_sources,input_source_count,config,Serial);
  selected_timing="normal-configurator";host_enumerate();
  auto result=transact(status());require(result.status==PROFILE_STORE_OK&&!(result.recovery_flags&(1u<<19)),"ordinary backend normal response");
  if(mode=="arm")require(GlyphColdRecoveryArm()&&!GlyphColdRecoveryArm()&&watchdog_registers.scratch[2]==0x43525432u,"production arm exactly once");
 } else {
  watchdog_registers.scratch[2]=0x43525432u;
  watchdog_registers.reason=1;
  TinyUSB_Device_Init(0);
  require(GlyphColdRecoveryBoot()&&watchdog_registers.scratch[2]==0,"early strong symbol consumes one-shot marker");
  require(port_calls==0&&!tud_inited()&&!attached,"cold early init never starts ordinary USB");
  for(unsigned i=0;i<8;++i){TinyUSB_Device_Task();TinyUSB_Device_FlushCDC();}
  require(port_calls==0&&!attached&&tasks==0,"early task/flush cannot initialize or service deferred stack");
  if(mode=="prepare-failure") {
   TinyUSBDevice.begin(0); // A foreign premature preparation poisons clean state.
  }
  enter_recovery_configurator(true);
  if(mode=="prepare-failure"||mode=="start-failure") {
   require(boot.outcome==BootOutcome::RecoveryTransportFailure&&!attached,"preparation failure remains refused");
   require(!GlyphColdRecoveryStart()&&!attached,"failed start never retries/falls back");
   require(storage.files==before,"failed preparation does not mutate persistent files");
   std::printf("cold_case=%s PASS\n",mode.c_str());return 0;
  }
  require(boot.outcome==BootOutcome::RecoveryConfigurator&&recovery_configurator,"cold recovery backend ready and published");
  require(port_calls==1&&attached&&tud_inited()&&GlyphColdRecoveryUsbReady(),"one deferred port start makes USB ready");
  host_enumerate();inspect();
  simple(CMD_GET_CONFIG);require(!host_rx.empty()&&decode(host_rx)[0]==CMD_SET_CONFIG,"actual bounded cold GET_CONFIG response");
  require(!GlyphColdRecoveryStart()&&port_calls==1,"second start refused without duplicate resources");
  require(storage.files==before,"cold inspection and all mutation refusals preserve file bytes");
 }
 std::printf("counts port=%u mutex=%u critical=%u task=%u exclusive=%u trigger=%u dcd=%u\n",port_calls,mutex_initializations,critical_initializations,task_claims,task_registrations,trigger_registrations,dcd_registrations);
 require(port_calls==1&&mutex_initializations==1&&critical_initializations==1,"one port/mutex/queue critical section");
 require(descriptor_preparations==1&&descriptor_clears==1,"descriptor/CDC preparation and clear exactly once");
 require(task_claims==1&&task_registrations==1&&trigger_registrations==1&&dcd_registrations==1,"one task IRQ/exclusive/shared trigger/DCD registration");
 for(unsigned i=4;i<8;++i)require(watchdog_registers.scratch[i]==0x100+i,"boot ROM routing scratch4-7 untouched");
 delete recovery_configurator;
 std::printf("cold_case=%s PASS actual_descriptor_builder=true actual_cdc=true actual_usbd=true actual_backend=true actual_port_init=true actual_dcd_init=true resource_counts=1\n",mode.c_str());
 return 0;
 } catch(const std::exception &e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
