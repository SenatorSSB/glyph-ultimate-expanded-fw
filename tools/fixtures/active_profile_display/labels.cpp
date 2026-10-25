#include "display/CurrentProfileLabel.hpp"
#include "display/InputDisplay.hpp"
#include "comms/IntegratedDisplay.hpp"
#include "core/ProfileStore.hpp"
#include "modes/Ultimate.hpp"
#include <cassert>
#include <cstring>
#include <fstream>
#include <iterator>
#include <vector>
// Only persistent directory/active-store ownership is doubled. Actual native
// decode, owned publication, Ultimate::SetConfig and label resolver execute.
Config config{};
Ultimate ultimate_mode;
static ProfileStore::Entry entries[2];
static size_t count=2, reads=0;
static uint32_t active_id=27;
static UltimateProfile profile{};
static bool ready=true,recovery=false;
ProfileStore::ProfileStore(ProfileStoreStorage *) {}
ProfileStore profile_store;
size_t ProfileStore::Count() const {++reads;return count;}
const ProfileStore::Entry *ProfileStore::EntryAt(size_t i) const {++reads;return i<count && i<2?entries+i:nullptr;}
bool ProfileStore::IsReady() const {++reads;return ready;}
bool ProfileStore::IsReadOnlyRecovery() const {++reads;return recovery;}
uint32_t ProfileStore::ActiveId() const {++reads;return active_id;}
const UltimateProfile *ProfileStore::ActiveProfile() const {++reads;return &profile;}
int main(int argc,char **argv) {
 assert(argc==2);
 std::ifstream f(argv[1],std::ios::binary);std::vector<uint8_t> raw{std::istreambuf_iterator<char>(f),{}};
 ultimate_native::PayloadLease lease,owned_lease;static ultimate_native::OwnedProgram owned;
 assert(ultimate_native::DecodeProfile(raw.data(),raw.size(),profile,lease));
 assert(ultimate_native::ValidProfile(profile));
 assert(ultimate_native::CopyProgram(ultimate_native::CandidateView(),owned,7,true));
 assert(ultimate_native::BindOwned(profile,owned,owned_lease));
 config.ultimate_profile_store_format=1;
 auto &mc=config.game_mode_configs[0];mc.mode_id=MODE_ULTIMATE;mc.ultimate_profile_engine=1;mc.ultimate_profile_id=27;
 std::strcpy(mc.name,"Ultimate Runtime");
 entries[0].id=27;entries[1].id=51;entries[0].payload_version=entries[1].payload_version=5;
 std::strcpy(entries[0].name,"Pikachu");std::strcpy(entries[1].name,"Kazuya");
 ultimate_mode.SetConfig(mc,&profile,&owned.view);
 assert(ultimate_mode.ActiveEngine()==Ultimate::Engine::NativeAbi1);
 auto expect=[&](const char *text) {
  for(auto backend:{COMMS_BACKEND_XINPUT,COMMS_BACKEND_GAMECUBE,COMMS_BACKEND_NINTENDO_SWITCH,COMMS_BACKEND_DINPUT})
   assert(!std::strcmp(current_profile_label(&ultimate_mode,backend),text));
 };
 IntegratedDisplay screen;screen.mode=&ultimate_mode;
 InputDisplay viewer(nullptr,0,COMMS_BACKEND_GAMECUBE);Adafruit_GFX pixels;
 auto view=[&](const char *name) {viewer.UpdateDisplay(&screen,pixels);assert(pixels.profile_text==name);};
 expect("Pikachu");view("Pikachu");std::strcpy(entries[0].name,"Fox");expect("Fox");view("Fox");
 mc.ultimate_profile_id=active_id=51;expect("Kazuya");view("Kazuya");
 count=65;expect("Ultimate Runtime");count=2;
 count=1;expect("Ultimate Runtime");view("Ultimate Runtime");count=2;
 active_id=27;expect("Ultimate Runtime");active_id=51;
 entries[1].payload_version=3;expect("Ultimate Runtime");entries[1].payload_version=5;
 entries[1].name[0]=0;expect("Ultimate Runtime");std::memset(entries[1].name,'x',sizeof(entries[1].name));expect("Ultimate Runtime");std::strcpy(entries[1].name,"Kazuya");
 std::memset(entries[1].name,'L',32);entries[1].name[32]=0;expect("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL");std::strcpy(entries[1].name,"Kazuya");
 ready=false;expect("Ultimate Runtime");ready=true;recovery=true;expect("Ultimate Runtime");recovery=false;
 // Failed activation leaves an old store ID but actual native execution fails.
 ultimate_mode.SetConfig(mc,nullptr,nullptr);expect("Ultimate Runtime");
 ultimate_mode.SetConfig(mc,&profile,&owned.view);expect("Kazuya");
 for(auto backend:{COMMS_BACKEND_CONFIGURATOR,COMMS_BACKEND_UNSPECIFIED}) {
  reads=0;assert(!std::strcmp(current_profile_label(&ultimate_mode,backend),"Ultimate Runtime"));assert(!reads);
 }
 config.ultimate_profile_store_format=0;expect("Ultimate Runtime");config.ultimate_profile_store_format=1;
 mc.ultimate_profile_engine=0;expect("Ultimate Runtime");mc.ultimate_profile_engine=1;
 Ultimate other;other.SetConfig(mc,&profile,&owned.view);assert(!std::strcmp(current_profile_label(&other,COMMS_BACKEND_XINPUT),"Ultimate Runtime"));
 mc.mode_id=MODE_MELEE;std::strcpy(mc.name,"Ordinary");expect("Ordinary");mc.name[0]=0;expect("Melee");
 assert(!std::strcmp(current_profile_label(nullptr,COMMS_BACKEND_XINPUT),""));
 assert(!std::strcmp(dashboard_plate_label(LAYOUT_PLATE_UNSPECIFIED),""));
 assert(!std::strcmp(dashboard_plate_label(LAYOUT_PLATE_EVERYTHING),"Full"));
 assert(!std::strcmp(dashboard_plate_label(LAYOUT_PLATE_FGC),"FGC"));
 assert(!std::strcmp(dashboard_plate_label(LAYOUT_PLATE_SPLIT_FGC),"Split FGC"));
 assert(!std::strcmp(dashboard_plate_label(LAYOUT_PLATE_PLATFORM_FIGHTER),"Plat Fighter"));
}
