// Tests C++ probe control flow with fake watchdog MMIO; no physical timing proof.
#include "core/ProfileStoreCreateProbe.hpp"
#include <cstdio>
#include <initializer_list>
#include <stdexcept>
namespace Probe=ProfileStoreCreateProbe;
void require(bool ok,const char *message){if(!ok)throw std::runtime_error(message);}
void reset(){host_watchdog={};host_clear_calls=host_enable_calls=host_update_calls=0;host_caused_reboot=false;Probe::active=false;Probe::last_stage=Probe::recovered_stage=0;}
int main(){try{
  reset();Probe::Mark(Probe::Stage::RecordRead);Probe::Finish();
  require(host_update_calls==0&&host_clear_calls==0,"inactive calls are inert");
  for(unsigned i=0;i<8;++i)host_watchdog.scratch[i]=0xa000+i;
  Probe::Begin();require(Probe::active&&host_enable_calls==1&&host_watchdog_deadline==8000&&host_pause_on_debug,"eight-second watchdog arm");
  require(host_magic_at_enable==Probe::kMagic&&host_stage_at_enable==1,"marker established before arm");
  for(uint32_t stage=1;stage<=static_cast<uint32_t>(Probe::Stage::Failed);++stage){
    const unsigned updates=host_update_calls;Probe::Mark(static_cast<Probe::Stage>(stage));
    require(Probe::last_stage==stage&&host_watchdog.scratch[3]==stage&&host_update_calls==updates+1,"stage store and refresh");
  }
  require(host_watchdog.scratch[4]==0x6ab73121,"SDK enable marker modeled");
  for(unsigned i:{0u,1u,5u,6u,7u})require(host_watchdog.scratch[i]==0xa000+i,"scratch outside probe and SDK enable preserved");
  Probe::Finish();require(!Probe::active&&host_watchdog.scratch[2]==0&&!(host_watchdog.ctrl&WATCHDOG_CTRL_ENABLE_BITS)&&host_clear_calls==1,"finish clears marker and disables");
  const uint32_t final_stage=Probe::last_stage;Probe::Mark(Probe::Stage::RequestDecoded);require(Probe::last_stage==final_stage,"finished probe remains inert");
  unsigned cases=0;
  for(bool reboot:{false,true})for(bool magic:{false,true})for(uint32_t stage:{0u,1u,static_cast<uint32_t>(Probe::Stage::Failed),static_cast<uint32_t>(Probe::Stage::Failed)+1,0xffffffffu}){
    reset();host_caused_reboot=reboot;host_watchdog.scratch[2]=magic?Probe::kMagic:0;host_watchdog.scratch[3]=stage;host_watchdog.ctrl=WATCHDOG_CTRL_ENABLE_BITS;
    const bool recovered=Probe::CaptureBoot();require(recovered==(reboot&&magic),"boot requires watchdog plus magic");
    if(recovered){const uint32_t expected=stage==0||stage>static_cast<uint32_t>(Probe::Stage::Failed)?0xffffffffu:stage;require(Probe::recovered_stage==expected&&host_clear_calls==1&&!(host_watchdog.ctrl&WATCHDOG_CTRL_ENABLE_BITS),"valid stage or conservative unknown recovery");}
    else require(Probe::recovered_stage==0&&host_clear_calls==0,"unrelated boot does not enter recovery");
    require(host_watchdog.scratch[2]==(magic?Probe::kMagic:0)&&host_watchdog.scratch[3]==stage,"capture preserves retained evidence");++cases;
  }
  std::printf("profile_store_create_probe_host=PASS watchdog_ms=8000 capture_boot_cases=%u unknown_stage=4294967295 scratch_0_1_5_6_7_preserved=true sdk_scratch4_modeled=true\n",cases);return 0;
}catch(const std::exception &e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
