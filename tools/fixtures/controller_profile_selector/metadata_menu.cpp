#include <algorithm>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <vector>
template<class A,class B> constexpr auto min(A a,B b) { return a<b?a:b; }
template<class A,class B> constexpr auto max(A a,B b) { return a>b?a:b; }
#define protected public
#define private public
#include "display/GlyphConfigMenu.hpp"
#undef private
#undef protected
#include "core/ProfileSelection.hpp"
// Only directory metadata is doubled. Menu population, item resolution,
// controls, rendering and request mailbox are the literal production code.
static std::vector<ProfileStore::Entry> entries;
ProfileStore::ProfileStore(ProfileStoreStorage *) {}
size_t ProfileStore::Count() const { return entries.size(); }
const ProfileStore::Entry *ProfileStore::EntryAt(size_t i) const { return i<entries.size()?&entries[i]:nullptr; }
bool ProfileStore::IsReady() const { return true; }
ProfileStore profile_store;
#include "HAL/pico/src/display/ConfigMenu.cpp"
#include "HAL/pico/src/display/DefaultConfigMenu.cpp"
#include "config/glyph/common/src/display/GlyphConfigMenu.cpp"
static void check(bool ok,const char *why) { if(!ok) throw std::runtime_error(why); }
int main() { try {
 Config config{};config.ultimate_profile_store_format=1;
 config.communication_backend_configs_count=4;
 const CommunicationBackendId routes[]={COMMS_BACKEND_XINPUT,COMMS_BACKEND_NINTENDO_SWITCH,COMMS_BACKEND_DINPUT,COMMS_BACKEND_GAMECUBE};
 for(size_t i=0;i<4;++i)config.communication_backend_configs[i].backend_id=routes[i];
 config.game_mode_configs_count=3;
 auto &native=config.game_mode_configs[0];native.mode_id=MODE_ULTIMATE;native.ultimate_profile_engine=1;
 native.applicable_backends_count=2;native.applicable_backends[0]=COMMS_BACKEND_XINPUT;native.applicable_backends[1]=COMMS_BACKEND_GAMECUBE;
 auto &ordinary=config.game_mode_configs[1];ordinary.mode_id=MODE_MELEE;std::strcpy(ordinary.name,"Legacy");
 auto &keyboard=config.game_mode_configs[2];keyboard.mode_id=MODE_KEYBOARD;keyboard.keyboard_mode_config=1;keyboard.applicable_backends_count=1;keyboard.applicable_backends[0]=COMMS_BACKEND_DINPUT;
 const DisplayControls controls{BTN_MB1,BTN_MB3,BTN_MB2,BTN_MB4};
 for(size_t count:{0u,1u,11u,20u,64u}) {
  entries.clear();
  for(size_t i=0;i<count;++i) {ProfileStore::Entry e{};e.id=0x80000100u+i;e.payload_version=5;e.rank=count-i;std::snprintf(e.name,sizeof(e.name),"Profile%02zu",i);entries.push_back(e);}
  if(count)std::memset(entries[0].name,'x',sizeof(entries[0].name)); // independently bounded source extent
  for(auto route:routes) {
   InputMode current(&native);CommunicationBackend backend(route,&current);CommunicationBackend *backends[]={&backend};
   GlyphConfigMenu menu(config,backends,1);IntegratedDisplay display;
   const bool admitted=route==COMMS_BACKEND_XINPUT||route==COMMS_BACKEND_GAMECUBE;
   const size_t legacy=profile_selection::IsUsb(route)?2:1;
   check(menu._gamemode_options_page.items_count==legacy+(admitted?count:0),"backend/native/legacy count");
   menu._current_menu_page=&menu._gamemode_options_page;
   const auto n=menu._current_menu_page->items_count;
   for(size_t i=0;i<n;++i) {
    const auto *item=menu.ResolveItem(menu._current_menu_page,i);check(item,"virtual item");check(std::memchr(item->text,0,sizeof(item->text)),"label terminated");
    if(i>=legacy)check(menu._profile_targets[i].profile_id==entries[count-1-(i-legacy)].id,"rank stable full32bit ID");
   }
   for(size_t i=0;i<2*n+5;++i){menu.HandleControls(&display,controls,controls.down);menu.UpdateDisplay(&display,display._display);check(menu._highlighted_menu_item<n,"bounded down/scroll");}
   for(size_t i=0;i<2*n+5;++i){menu.HandleControls(&display,controls,controls.up);menu.UpdateDisplay(&display,display._display);}
   check(menu._highlighted_menu_item==0,"bounded up");
   if(admitted&&count) {
    const size_t index=legacy;menu._highlighted_menu_item=index;
    menu.HandleControls(&display,controls,controls.enter);
    check(profile_selection::Pending()==entries.back().id,"menu confirms stable ID");
    check(!profile_selection::Request(5),"occupied mailbox rejects second request");profile_selection::Complete();
   }
  }
 }
 // Equal names do not alias identity; duplicate directory identities never
 // create duplicate choices. Non-native metadata remains hidden and untouched.
 entries.resize(4);for(size_t i=0;i<4;++i){entries[i]={};entries[i].id=1000+i;entries[i].payload_version=5;std::strcpy(entries[i].name,"same");}
 entries[1].id=entries[0].id;entries[2].payload_version=3;
 profile_selection::Target targets[94]{};
 check(profile_selection::BuildTargets(config,profile_store,COMMS_BACKEND_XINPUT,targets,94)==4,"duplicate ID/schema filtering");
 native.applicable_backends_count=0;check(profile_selection::Eligible(native,COMMS_BACKEND_NINTENDO_SWITCH),"empty applicability unrestricted");
 check(!profile_selection::Eligible(keyboard,COMMS_BACKEND_GAMECUBE)&&profile_selection::Eligible(keyboard,COMMS_BACKEND_XINPUT),"Keyboard USB exception");
 config.game_mode_configs_count=1;entries.clear();
 InputMode current(&native);CommunicationBackend backend(COMMS_BACKEND_XINPUT,&current);CommunicationBackend *backends[]={&backend};
 GlyphConfigMenu empty(config,backends,1);IntegratedDisplay display;empty._current_menu_page=&empty._gamemode_options_page;
 for(auto b:{controls.up,controls.down,controls.enter}){empty.HandleControls(&display,controls,b);empty.UpdateDisplay(&display,display._display);}
 check(empty._highlighted_menu_item==0&&!empty.ResolveItem(empty._current_menu_page,0),"empty list safe");
 empty.HandleControls(&display,controls,controls.back);check(empty._current_menu_page==empty._top_level_page,"empty back");
 check(profile_selection::Request(UINT32_MAX)&&profile_selection::Pending()==UINT32_MAX,"maximum ID no sentinel/truncation");profile_selection::Complete();check(!profile_selection::Request(0),"zero ID refuses");
 std::cout<<"PASS production metadata/menu/mailbox:0/1/11/20/64 ranks names backend Keyboard legacy scrolling empty full32 IDs duplicates\n";
 }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;} }
