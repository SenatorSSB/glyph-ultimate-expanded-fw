#define main preserved_selection_recovery_main
#include "../profile_store_selection_recovery_host/selection_recovery.cpp"
#undef main
static size_t requested=SIZE_MAX;
static unsigned calls=0;
static void observe_destination(CommunicationBackendId,size_t index,const Config &){requested=index;++calls;}
int main(){try{
 static Config c;InputState input;CommunicationBackend backend(input);CommunicationBackend *backends[]={&backend};
 set_mode_destination_selector(observe_destination);
 for(size_t count:{0,10,11,13,30,31}){
  c=Config_init_default;c.game_mode_configs_count=count;
  for(size_t i=0;i<30;++i){c.game_mode_configs[i].mode_id=MODE_ULTIMATE;c.game_mode_configs[i].activation_binding_count=1;c.game_mode_configs[i].activation_binding[0]=static_cast<Button>(i+1);}
  setup_mode_activation_bindings(c.game_mode_configs,count,0);calls=0;requested=SIZE_MAX;input.buttons=uint64_t{1}<<29;select_mode(backends,1,c);
  require(calls==(count==30?1u:0u),"current count boundary callback/refusal");
  require(backend.activations==0&&profile_store.activations==0,"current chord never immediately activates a mode");
 }
 c.game_mode_configs_count=13;
 for(size_t i=0;i<13;++i){setup_mode_activation_bindings(c.game_mode_configs,13,0);calls=0;requested=SIZE_MAX;input.buttons=uint64_t{1}<<i;select_mode(backends,1,c);require(calls==1&&requested==i,"all13 actual callback indices");for(int repeat=0;repeat<8;++repeat)select_mode(backends,1,c);require(calls==1,"held chord consumed exactly once");}
 setup_mode_activation_bindings(c.game_mode_configs,13,1);calls=0;input.buttons=1;select_mode(backends,1,c);require(calls==0,"boot-held chord consumed");
 std::cout<<"PASS HOST_COMPONENT_ONLY actual current mode-selection counts0,10,11,13,30,31;13callbackindices/once/refusal/boot-held; historical7unchanged\n";return 0;
}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
