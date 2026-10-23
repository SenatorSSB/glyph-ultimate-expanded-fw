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
static void character_menu_policy() {
 // Exact retained topology: source fallback, legacy ID3, native ID28;
 // 22 non-native records, permanent Ultimate and twenty selector fixtures.
 Config config{};config.ultimate_profile_store_format=ProfileStore::kCompactConfigFormat;
 config.game_mode_configs_count=3;
 for(size_t i=0;i<3;++i) {
  auto &m=config.game_mode_configs[i];m.mode_id=MODE_ULTIMATE;
  std::strcpy(m.name,"Ultimate Runtime");m.button_remapping_count=3;
  m.button_remapping[0]={BTN_RF3,BTN_RF3};m.button_remapping[1]={BTN_RF4,BTN_RF4};m.button_remapping[2]={BTN_LT3,BTN_LT3};
 }
 config.game_mode_configs[1].ultimate_profile_id=3;
 auto &native=config.game_mode_configs[2];native.ultimate_profile_engine=1;native.ultimate_profile_id=28;
 native.socd_pairs_count=2;native.socd_pairs[0]={BTN_LF3,BTN_LF1,SOCD_2IP};native.socd_pairs[1]={BTN_LF5,BTN_LF2,SOCD_2IP};
 entries.clear();
 auto add=[](uint32_t id,uint8_t schema,uint32_t rank,const char *name) {
  ProfileStore::Entry e{};e.id=id;e.payload_version=schema;e.rank=rank;
  std::snprintf(e.name,sizeof(e.name),"%s",name);entries.push_back(e);
 };
 add(1,1,0,"retained legacy");
 for(uint32_t id=3;id<=22;++id)add(id,3,0,"retained legacy");
 add(24,3,0,"retained legacy");add(27,5,0,"Ultimate");
 for(uint32_t id=28;id<=47;++id) {
  char name[8];std::snprintf(name,sizeof(name),"SEL%02u",unsigned(id-27));add(id,5,1000+id-27,name);
 }
 check(entries.size()==43,"retained full directory topology");
 const CommunicationBackendId routes[]={COMMS_BACKEND_XINPUT,COMMS_BACKEND_GAMECUBE,COMMS_BACKEND_NINTENDO_SWITCH,COMMS_BACKEND_DINPUT};
 config.communication_backend_configs_count=4;
 for(size_t i=0;i<4;++i){config.communication_backend_configs[i].backend_id=routes[i];config.communication_backend_configs[i].default_mode_config=3;}
 const auto preserved=config;
 profile_selection::Target targets[profile_selection::kMaxTargets]{};
 auto verify=[&](size_t expected) {
  const auto directory=entries;
  for(auto route:routes) {
   check(profile_selection::BuildTargets(config,profile_store,route,targets,profile_selection::kMaxTargets)==expected,"compact character-only count");
   check(targets[0].profile_id==27,"Ultimate first stable ID");
   InputMode current(&native);CommunicationBackend backend(route,&current);CommunicationBackend *backends[]={&backend};
   GlyphConfigMenu menu(config,backends,1);
   check(menu._gamemode_options_page.items_count==expected,"actual menu character count");
   for(size_t i=0;i<expected;++i) {
    const auto *item=menu.ResolveItem(&menu._gamemode_options_page,i);
    check(item&&item->key==i,"stored menu key remains list index");
    const auto *e=profile_selection::FindEntry(profile_store,targets[i].profile_id);
    check(e&&!std::strcmp(item->text,e->name),"actual menu uses stored character label");
    check(targets[i].profile_id!=0,"no compact Ultimate Config target");
   }
  }
  check(!std::memcmp(&config,&preserved,sizeof(config)),"menu keeps exact runtime contexts/defaults");
  check(entries.size()==directory.size(),"enumeration preserves store count");
  for(size_t i=0;i<entries.size();++i)check(entries[i].id==directory[i].id&&entries[i].rank==directory[i].rank&&entries[i].payload_version==directory[i].payload_version&&!std::strcmp(entries[i].name,directory[i].name),"enumeration preserves store metadata");
 };
 verify(21);
 for(size_t i=1;i<21;++i)check(targets[i].profile_id==27+i,"SEL stable IDs/ranks preserved");
 entries.erase(std::remove_if(entries.begin(),entries.end(),[](const auto &e){return e.id>=28&&e.id<=47;}),entries.end());
 check(entries.size()==23,"simulated cleanup retains all non-native records");verify(1);
 add(0x80000030u,5,1,"Kazuya");verify(2);
 check(targets[1].profile_id==0x80000030u,"Kazuya uses actual arbitrary full32 stable ID");
 // Names never designate context visibility. Legacy/noncompact choices stay.
 std::strcpy(config.game_mode_configs[0].name,"Source fallback");
 std::strcpy(config.game_mode_configs[1].name,"Legacy choice");native.name[0]=0;
 check(profile_selection::BuildTargets(config,profile_store,routes[0],targets,94)==2,"semantic predicate independent of names");
 config.ultimate_profile_store_format=0;
 for(size_t i=0;i<3;++i){config.game_mode_configs[i].ultimate_profile_engine=0;config.game_mode_configs[i].ultimate_profile_id=0;}
 check(profile_selection::BuildTargets(config,profile_store,routes[0],targets,94)==3,"noncompact Ultimate choices retained");
 for(size_t i=0;i<3;++i)check(!targets[i].profile_id&&targets[i].mode_index==i,"noncompact ordinary row identity");
 config=preserved;
 // All contexts stay hidden with distinct eligibility/preprocessing. Only an
 // eligible engine1 template admits native choices; never promote engine0.
 config.game_mode_configs_count=5;config.game_mode_configs[3]=native;config.game_mode_configs[4]=native;
 for(size_t i=2;i<5;++i){auto &m=config.game_mode_configs[i];m.applicable_backends_count=1;m.applicable_backends[0]=routes[i-2];}
 config.game_mode_configs[3].button_remapping[0]={BTN_RF1,BTN_LF1};
 for(size_t i=0;i<3;++i)check(profile_selection::BuildTargets(config,profile_store,routes[i],targets,94)==2,"multiple hidden eligible contexts");
 check(profile_selection::BuildTargets(config,profile_store,COMMS_BACKEND_DINPUT,targets,94)==0,"no eligible native template invents no selectable profiles");
 config.game_mode_configs_count=2;
 check(profile_selection::BuildTargets(config,profile_store,routes[0],targets,94)==0,"engine0-only compact rows hidden without promoting legacy templates");
 config=preserved;
 add(501,5,1,"equal-rank later");add(502,5,1,"equal-rank last");
 check(profile_selection::BuildTargets(config,profile_store,routes[0],targets,94)==4,"tie fixture count");
 check(targets[1].profile_id==0x80000030u&&targets[2].profile_id==501&&targets[3].profile_id==502,"equal-rank directory stability");
 check(profile_selection::BuildTargets(config,profile_store,routes[0],targets,1)==1&&targets[0].profile_id==27,"capacity bound retains first native");
 check(!profile_selection::BuildTargets(config,profile_store,routes[0],targets,0),"zero capacity safe");
 check(!profile_selection::BuildTargets(config,profile_store,COMMS_BACKEND_CONFIGURATOR,targets,94),"Configurator does not enumerate profiles");
 std::cout<<"PASS compact character policy:43-record owner topology/Ultimate+20SEL/Ultimate+Kazuya/all4 routes/contexts/read-only/names/noncompact/ties/keys/capacity\n";
}
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
    check(!profile_selection::Request(5),"occupied mailbox rejects second request");
    // Keep the asynchronous request occupied while attempting every top-level
    // action, including immediate Configurator and bootloader resets.
    for(size_t action=0;action<menu._top_level_page->items_count;++action) {
     menu._current_menu_page=menu._top_level_page;menu._highlighted_menu_item=action;
     menu.HandleControls(&display,controls,controls.enter);
     check(menu._current_menu_page==menu._top_level_page&&menu._highlighted_menu_item==action,"pending prevents action/page transition");
     menu.HandleControls(&display,controls,controls.back);
     check(menu._current_menu_page==menu._top_level_page,"pending prevents escape");
    }
    check(!firmware_reboots&&!bootloader_reboots&&!disconnects,"pending prevents all device-side effects");
    profile_selection::Complete();
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
 character_menu_policy();
 std::cout<<"PASS production metadata/menu/mailbox:0/1/11/20/64 ranks names backend Keyboard legacy scrolling empty full32 IDs duplicates\n";
 }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;} }
