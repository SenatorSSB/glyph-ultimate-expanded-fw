#define main preserved_persistence_regression_main
#include "../profile_store_config_persistence_host/persistence_harness.cpp"
#undef main
#include "core/ProfileSelection.hpp"
#include "core/ModeSelectionTransaction.hpp"
#include <fstream>
#ifdef GLYPH_GC_LIVENESS_BRIDGE
extern "C" void run_gc_idle_then(void (*service)());
#endif
// Metadata methods are not exercised by this persistence-only fixture.
size_t ProfileStore::Count() const { return 0; }
const ProfileStore::Entry *ProfileStore::EntryAt(size_t) const { return nullptr; }
bool ProfileStore::IsReady() const { return false; }
struct Store {
 Bytes wire[2]; bool ready=true,ro=false,uncertain=false,missing=false,corrupt=false,race=false;
 ultimate_native::PayloadLease lease;
 bool MigrationPending()const{return false;}
 bool IsReady()const{return ready;}bool IsReadOnlyRecovery()const{return ro;}
 bool IsTransactionUncertain()const{return uncertain;}uint32_t Incarnation()const{return 7;}
 ProfileStore::Status Read(uint32_t id,UltimateProfile &out){
  if(missing||id<1000||id>1001)return ProfileStore::Status::NotFound;
  const auto &b=wire[id-1000];lease.Release();
  if(corrupt||!ultimate_native::DecodeProfile(b.data(),b.size(),out,lease)||!ultimate_native::ValidProfile(out))return ProfileStore::Status::Invalid;
  if(race){auto changed=config(11);put("config-v2.bin",record(changed));}
  return ProfileStore::Status::Ok;
 }
};
#include "core/ConfigWriteCandidate.hpp"
static Store selected_store;
static Persistence selected_persistence;
static unsigned reboots=0;
static void reboot_firmware(){++reboots;}
struct Backend { CommunicationBackendId id=COMMS_BACKEND_XINPUT; CommunicationBackendId BackendId(){return id;} } backend_instance;
static Backend *backends[]={&backend_instance};
static size_t current_mode_index=0;
#define profile_store selected_store
#define persistence selected_persistence
#include "selector_service.inc"
#undef persistence
#undef profile_store
int main(int argc,char **argv){try{
 require(argc==3,"two source-faithful native wrappers");Store store;
 for(unsigned i=0;i<2;++i){std::ifstream f(argv[i+1],std::ios::binary);store.wire[i]=Bytes((std::istreambuf_iterator<char>(f)),{});}
 const auto bodies=store.wire[0];
 static Config durable,candidate;
 auto seed=[&](Persistence &storage,CommunicationBackendId backend){
  LittleFS.reset();durable=Config_init_default;durable.rgb_brightness=19;
  durable.ultimate_profile_store_format=1;durable.ultimate_profile_store_incarnation=7;
  durable.communication_backend_configs_count=1;durable.communication_backend_configs[0].backend_id=backend;durable.communication_backend_configs[0].default_mode_config=1;
  durable.default_backend_config=1;durable.default_usb_backend_config=1;
  durable.game_mode_configs_count=1;auto &m=durable.game_mode_configs[0];m.mode_id=MODE_ULTIMATE;m.ultimate_profile_id=1000;m.ultimate_profile_engine=1;
  put("config-v2.bin",record(durable));require(storage.SetValidator(validator),"validator installed");
  require(storage.LoadConfigChecked(candidate)==Persistence::LoadResult::Loaded,"seed load");
 };
 for(auto backend:{COMMS_BACKEND_XINPUT,COMMS_BACKEND_NINTENDO_SWITCH,COMMS_BACKEND_DINPUT,COMMS_BACKEND_GAMECUBE}) {
  Persistence storage;seed(storage,backend);
  for(auto id:{1000u,1001u,1000u}) {
   size_t mode=99,route=99;
   require(profile_selection::Persist(storage,store,candidate,backend,id,0,mode,route)==ModeDestinationResult::Saved,"A B A checked save");
   Config expected=durable;expected.game_mode_configs[0].ultimate_profile_id=id;
   require(mode==0&&route==0&&encode(expected)==encode(candidate),"only reference/default changes; backend unrelated fields preserved");
   Persistence reboot;require(reboot.SetValidator(validator),"reboot validator");static Config loaded;
   require(reboot.LoadConfigChecked(loaded)==Persistence::LoadResult::Loaded&&encode(loaded)==encode(expected),"ordinary power/reboot durable selection");
   volatile uint32_t scratch[3]={1,1,kCommittedModeDestination};CommunicationBackendConfig destination{};
   require(consume_committed_mode_destination(scratch,true,loaded,destination)&&destination.backend_id==backend,"committed reboot keeps exact route and consumes once");
  }
 }
 for(unsigned failure=0;failure<9;++failure) {
  Persistence storage;seed(storage,COMMS_BACKEND_XINPUT);const auto original=get("config-v2.bin");const auto mutations=LittleFS.mutations;
  store.ro=failure==0;store.uncertain=failure==1;store.ready=failure!=2;store.missing=failure==3;store.corrupt=failure==4;
  if(failure==5){durable.game_mode_configs[0].button_remapping_count=1;durable.game_mode_configs[0].button_remapping[0]={BTN_RF1,BTN_LF1};put("config-v2.bin",record(durable));}
  if(failure==6){durable.game_mode_configs[0].applicable_backends_count=1;durable.game_mode_configs[0].applicable_backends[0]=COMMS_BACKEND_GAMECUBE;put("config-v2.bin",record(durable));}
  if(failure==7){durable.ultimate_profile_store_incarnation=8;put("config-v2.bin",record(durable));}
  if(failure==8){durable.game_mode_configs[0].ultimate_profile_engine=0;put("config-v2.bin",record(durable));}
  const auto before=get("config-v2.bin");const auto writes=LittleFS.mutations;size_t mode=0,route=0;
  require(profile_selection::Persist(storage,store,candidate,COMMS_BACKEND_XINPUT,1001,0,mode,route)==ModeDestinationResult::Refused,"invalid/context/ineligible/recovery refuses");
  require(get("config-v2.bin")==before&&LittleFS.mutations==writes,"refusal has no persistence mutation");
  if(failure<5)require(before==original&&writes==mutations,"original known-good exact");
  store.ro=store.uncertain=store.missing=store.corrupt=false;store.ready=true;
 }
 {Persistence storage;seed(storage,COMMS_BACKEND_XINPUT);store.race=true;size_t m=0,b=0;require(profile_selection::Persist(storage,store,candidate,COMMS_BACKEND_XINPUT,1001,0,m,b)==ModeDestinationResult::Refused,"fresh durable generation conflict");store.race=false;}
 {Persistence storage;seed(storage,COMMS_BACKEND_XINPUT);const auto before=get("config-v2.bin");checked_inject(CheckedStorage::Operation::Close,CheckedStorage::Phase::After,"config-v2.tmp");size_t m=0,b=0;
  require(profile_selection::Persist(storage,store,candidate,COMMS_BACKEND_XINPUT,1001,0,m,b)==ModeDestinationResult::Refused&&storage.IsMutationFenced(),"uncertain selection refuses and fences");
  require(get("config-v2.bin")==before,"uncertain stage preserves durable original");CheckedStorage::SetFaultHook(nullptr);
 }
 {Persistence storage;seed(storage,COMMS_BACKEND_XINPUT);durable.game_mode_configs_count=2;durable.game_mode_configs[1]=durable.game_mode_configs[0];durable.game_mode_configs[0].button_remapping_count=1;durable.game_mode_configs[0].button_remapping[0]={BTN_RF1,BTN_LF1};put("config-v2.bin",record(durable));size_t m=0,b=0;
  require(profile_selection::Persist(storage,store,candidate,COMMS_BACKEND_XINPUT,1001,0,m,b)==ModeDestinationResult::Saved&&m==1,"multiple existing contexts resolve matching eligible row");
 }
 selected_store.wire[0]=store.wire[0];selected_store.wire[1]=store.wire[1];
 for(unsigned failure=0;failure<4;++failure) {
  const bool fail=failure!=0;
#ifdef GLYPH_GC_LIVENESS_BRIDGE
  seed(selected_persistence,COMMS_BACKEND_GAMECUBE);backend_instance.id=COMMS_BACKEND_GAMECUBE;
#else
  seed(selected_persistence,COMMS_BACKEND_XINPUT);
#endif
  host_watchdog={};reboots=0;selected_store.ro=failure==1;selected_store.race=failure==3;
  if(failure==2)checked_inject(CheckedStorage::Operation::Close,CheckedStorage::Phase::After,"config-v2.tmp");
#ifdef GLYPH_GC_LIVENESS_BRIDGE
  run_gc_idle_then(service_profile_selection);
#else
  require(profile_selection::Request(1001),"service request accepted");
  service_profile_selection();
#endif
  CheckedStorage::SetFaultHook(nullptr);
  selected_store.race=false;
  require(!profile_selection::Pending(),"service releases request after returned attempt");
  require(reboots==(fail?0u:1u),"exact service reboot only after Saved");
  require(host_watchdog.scratch[2]==(fail?0u:kCommittedModeDestination),"failed service never publishes destination");
  if(!fail)require(ConfigWriteCandidate().game_mode_configs[0].ultimate_profile_id==1001,"service saved requested native ID");
 }
 selected_store.ro=false;
 require(store.wire[0]==bodies,"selection never mutates record body");
 std::cout<<"PASS actual Persistence selector A->B->A/all4 routes/committed boot/context/fences/conflict/uncertain/multiple-context preservation\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
