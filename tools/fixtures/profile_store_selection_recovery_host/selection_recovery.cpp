#include <config.pb.h>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include "core/ModeSelectionTransaction.hpp"
#include "core/RecoveryInitialization.hpp"

struct InputState { uint64_t buttons=0; bool lt1=false, lt2=false, mb1=false, mb2=false; };
class InputMode { public: virtual ~InputMode()=default; };
class ControllerMode : public InputMode {};
class KeyboardMode : public InputMode {};
class CommunicationBackend {
 public:
  explicit CommunicationBackend(InputState &i): inputs(i) {}
  InputState &GetInputs(){return inputs;}
  CommunicationBackendId BackendId(){return COMMS_BACKEND_XINPUT;}
  void SetGameMode(InputMode *){++activations;}
  unsigned activations=0; InputState &inputs;
};
#define MODE(name,base) class name:public base {public: template<typename... A> void SetConfig(A&&...) {}};
MODE(Melee20Button,ControllerMode) MODE(ProjectM,ControllerMode) MODE(Ultimate,ControllerMode)
MODE(FgcMode,ControllerMode) MODE(RivalsOfAether,ControllerMode) MODE(Rivals2,ControllerMode)
MODE(CustomKeyboardMode,KeyboardMode) MODE(CustomControllerMode,ControllerMode)
MODE(Smash64,ControllerMode) MODE(SenscopePrototype,ControllerMode)
#undef MODE
namespace senscope::prototype {constexpr bool kEnableSenscopePrototypeManualSelection=false;}
KeyboardMode *current_kb_mode=nullptr;
using ModeDestinationSelector = void (*)(CommunicationBackendId,size_t,const Config &);
void set_mode(CommunicationBackend *,ControllerMode *);
void set_mode(CommunicationBackend *,KeyboardMode *);
void set_mode(CommunicationBackend *,GameModeConfig &,Config &);
void set_mode(CommunicationBackend *,GameModeId,Config &);
uint64_t make_button_mask(const Button *b,size_t n){uint64_t m=0;for(size_t i=0;i<n;++i)m|=uint64_t{1}<<(b[i]-1);return m;}
bool all_buttons_held(uint64_t b,uint64_t m){return m!=0&&(b&m)==m;}
#include MODE_SELECTION_SOURCE
ProfileStore profile_store;
static void require(bool b,const char *s){if(!b)throw std::runtime_error(s);}
struct FakePersistence {
 enum class LoadResult {Loaded,StorageFailure}; enum class SaveResult {Saved,StorageFailure,UnknownOutcome,Conflict};
 Config durable=Config_init_default;
 bool available=true,valid=true,load_ok=true,validator=false; unsigned saves=0,loads=0; SaveResult result=SaveResult::Saved;
 bool SetValidator(ConfigSemanticValidator){validator=true;return true;}
 bool IsAvailable()const{return available;}
 LoadResult LoadConfigChecked(Config &c){++loads;if(!load_ok)return LoadResult::StorageFailure;c=durable;return LoadResult::Loaded;}
 uint32_t ConfigGeneration(const Config &)const{return 17;}
 bool ValidateConfig(const Config &,ConfigValidationError &)const{return valid;}
 SaveResult SaveConfigIfGenerationMatches(Config &c,uint64_t g){require(g==17,"generation fence");++saves;if(result==SaveResult::Saved||result==SaveResult::UnknownOutcome)durable=c;return result;}
} storage;
struct FakeStore {
 static constexpr unsigned kCompactConfigFormat=1;
 unsigned begins=0,normal_begins=0,writes=0; uint32_t expected=0,root_format=0;
 bool BeginRecovery(uint32_t i,uint32_t r){++begins;expected=i;root_format=r;return true;}
};
static Config scratch=Config_init_default;
static unsigned reboots=0;
static void destination(CommunicationBackendId b,size_t i,const Config &){size_t bi=99;if(persist_mode_destination(storage,scratch,b,i,bi)==ModeDestinationResult::Saved)++reboots;}
static Config baseline(){Config c=Config_init_default;c.ultimate_profile_store_format=1;c.ultimate_profile_store_incarnation=41;c.ultimate_profile_root_format=2;c.communication_backend_configs_count=1;c.communication_backend_configs[0].backend_id=COMMS_BACKEND_XINPUT;c.communication_backend_configs[0].default_mode_config=1;c.default_usb_backend_config=1;c.game_mode_configs_count=3;for(size_t i=0;i<3;++i){auto &m=c.game_mode_configs[i];m.mode_id=i==2?MODE_MELEE:MODE_ULTIMATE;m.ultimate_profile_id=i?4:3;m.activation_binding_count=1;m.activation_binding[0]=static_cast<Button>(i+1);}return c;}
static void selection(){
 static Config live=baseline();storage.durable=live;InputState input;CommunicationBackend backend(input);CommunicationBackend *backends[]={&backend};set_mode_destination_selector(destination);setup_mode_activation_bindings(live.game_mode_configs,3,0);
 input.buttons=uint64_t{1}<<0;select_mode(backends,1,live);require(storage.saves==0&&reboots==0&&backend.activations==0,"same destination must not save/reset/activate");
 input.buttons=0;select_mode(backends,1,live);input.buttons=uint64_t{1}<<1;select_mode(backends,1,live);require(storage.saves==1&&reboots==1&&backend.activations==0&&profile_store.activations==0,"different compact profile must persist then reset without activation");require(storage.durable.communication_backend_configs[0].default_mode_config==2&&live.communication_backend_configs[0].default_mode_config==1,"only durable destination changes");require(storage.durable.game_mode_configs[1].ultimate_profile_id==4,"compact stable reference retained");
 for(int n=0;n<8;++n)select_mode(backends,1,live);require(reboots==1&&storage.saves==1,"held chord consumed before reset");
 live=storage.durable;setup_mode_activation_bindings(live.game_mode_configs,3,input.buttons);select_mode(backends,1,live);require(reboots==1&&storage.saves==1,"held chord through boot cannot loop");
 input.buttons=0;select_mode(backends,1,live);input.buttons=uint64_t{1}<<2;storage.result=FakePersistence::SaveResult::StorageFailure;select_mode(backends,1,live);require(reboots==1&&backend.activations==0,"failed save cannot reset or activate");
 for(int n=0;n<8;++n)select_mode(backends,1,live);require(storage.saves==2,"failed save held chord cannot retry writes");
 input.buttons=0;select_mode(backends,1,live);input.buttons=uint64_t{1}<<2;storage.result=FakePersistence::SaveResult::UnknownOutcome;select_mode(backends,1,live);require(reboots==1&&backend.activations==0,"lost save acknowledgement cannot reset or activate");
 // The uncertain result changed durable state in this fault model. A retry
 // resolves to unchanged, rather than resetting or re-executing the save.
 input.buttons=0;select_mode(backends,1,live);input.buttons=uint64_t{1}<<2;select_mode(backends,1,live);require(storage.saves==3&&reboots==1,"same durable non-Ultimate destination cannot loop");
 storage.durable=baseline();storage.result=FakePersistence::SaveResult::Saved;input.buttons=0;select_mode(backends,1,live);input.buttons=uint64_t{1}<<2;select_mode(backends,1,live);require(reboots==2&&storage.durable.communication_backend_configs[0].default_mode_config==3,"non-Ultimate destination reboot-bound");
 require(backend.activations==0&&profile_store.activations==0,"no runtime activation anywhere");
 std::cout<<"selection_same_different_fail_unknown_held_nonultimate_compact=PASS\n";
}
static void committed_boot() {
 static Config durable=baseline();durable.communication_backend_configs[0].default_mode_config=2;
 volatile uint32_t target[3]={1,2,kCommittedModeDestination};CommunicationBackendConfig selected=CommunicationBackendConfig_init_default;
 require(consume_committed_mode_destination(target,true,durable,selected)&&selected.default_mode_config==2,"committed target consumes exact persisted destination");
 require(target[0]==0&&target[1]==0&&target[2]==0&&!consume_committed_mode_destination(target,true,durable,selected),"one-shot target cannot survive consumption");
 target[0]=1;target[1]=3;target[2]=kCommittedModeDestination;require(!consume_committed_mode_destination(target,true,durable,selected)&&target[0]==0,"mismatched target clears before old selector can save it");
 target[0]=1;target[1]=2;target[2]=kCommittedModeDestination;require(!consume_committed_mode_destination(target,false,durable,selected)&&target[2]==0,"cold boot never trusts watchdog target");
 durable.communication_backend_configs[0].backend_id=COMMS_BACKEND_GAMECUBE;durable.default_backend_config=1;target[0]=1;target[1]=2;target[2]=kCommittedModeDestination;require(consume_committed_mode_destination(target,true,durable,selected)&&selected.backend_id==COMMS_BACKEND_GAMECUBE,"non-USB destination preserved without autodetection");
 std::cout<<"committed_boot_consume_validate_nonusb=PASS\n";
}
static bool validator(const Config &,ConfigValidationError &){return true;}
static void recovery(){
 static Config live=baseline();storage.durable=live;FakeStore store;auto state=initialize_recovery(storage,store,live,scratch,validator);require(storage.validator&&!state.config_invalid&&state.storage_available&&store.begins==1&&store.expected==41&&store.root_format==2,"manual RT2 must initialize validator and store inspection");
 storage.load_ok=false;state=initialize_recovery(storage,store,live,scratch,validator);require(state.config_invalid&&state.storage_available&&store.begins==2&&store.expected==0&&store.root_format==0,"automatic invalid Config must retain usable store inspection");
 storage.available=false;state=initialize_recovery(storage,store,live,scratch,validator);require(state.config_invalid&&!state.storage_available&&store.begins==2,"unavailable filesystem cannot inspect store");require(storage.saves==0&&store.writes==0&&store.normal_begins==0,"both recovery routes are nonmutating");std::cout<<"recovery_manual_automatic_unavailable_validator_readonly=PASS\n";
}
int main(int argc,char **argv){try{require(argc==2,"case argument");if(std::strcmp(argv[1],"selection")==0)selection();else if(std::strcmp(argv[1],"boot")==0)committed_boot();else recovery();return 0;}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
