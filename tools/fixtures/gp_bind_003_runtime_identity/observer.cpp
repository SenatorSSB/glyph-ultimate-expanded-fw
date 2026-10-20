#include "core/RuntimeIdentityService.hpp"
#include "core/ProfileStorePaths.hpp"
#include "core/mode_selection.hpp"
#include "util/state_util.hpp"
#include <pb_decode.h>
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
#include <chrono>

// Only unrelated modes and hardware are doubles. The Ultimate, ProfileStore,
// selection function bodies, communication state, viewer and wire are production.
class DummyMode : public ControllerMode {
 public:
  template<class... T> void SetConfig(T&&...) {}
 private:
  void UpdateDigitalOutputs(const InputState &, OutputState &) override {}
  void UpdateAnalogOutputs(const InputState &, OutputState &, CommunicationBackendId) override {}
};
class Melee20Button:public DummyMode{}; class ProjectM:public DummyMode{};
class FgcMode:public DummyMode{}; class RivalsOfAether:public DummyMode{};
class Rivals2:public DummyMode{}; class CustomControllerMode:public DummyMode{};
class Smash64:public DummyMode{}; class SenscopePrototype:public DummyMode{};
class CustomKeyboardMode:public KeyboardMode { public: template<class... T> void SetConfig(T&&...) {} };
KeyboardMode *current_kb_mode = nullptr;
namespace senscope::prototype { constexpr bool kEnableSenscopePrototypeManualSelection = false; }
#include "src/core/mode_selection.cpp"

static void require(bool yes,const char *message) { if(!yes) throw std::runtime_error(message); }
struct Storage final:ProfileStoreStorage {
 std::map<std::string,std::vector<uint8_t>> files; unsigned calls=0;
 bool Geometry(CheckedStorage::Geometry &g) override { ++calls;g.total_bytes=512*1024;g.free_bytes=400*1024;g.used_bytes=112*1024;g.erase_bytes=4096;g.program_bytes=256;return true; }
 bool Enumerate(CheckedStorage::Visitor visitor,void *context) override { ++calls; for(const auto &f:files){CheckedStorage::Entry e{};const char *p=f.first.c_str();if(*p=='/')++p;std::strncpy(e.name,p,sizeof(e.name)-1);e.bytes=f.second.size();if(!visitor(context,e))return false;}return true; }
 bool Write(const char *p,const uint8_t *b,size_t n) override {++calls;files[p]={b,b+n};return true;}
 bool Read(const char *p,uint8_t *b,size_t n) override {++calls;auto it=files.find(p);if(it==files.end()||it->second.size()!=n)return false;std::memcpy(b,it->second.data(),n);return true;}
 bool ReadRange(const char *p,size_t offset,uint8_t *b,size_t n) override {++calls;auto it=files.find(p);if(it==files.end()||offset>it->second.size()||n>it->second.size()-offset)return false;std::memcpy(b,it->second.data()+offset,n);return true;}
 size_t Size(const char *p) override {++calls;auto it=files.find(p);return it==files.end()?0:it->second.size();}
 bool Exists(const char *p) override {++calls;return files.count(p);}
 bool Remove(const char *p) override {++calls;files.erase(p);return true;}
 bool Rename(const char *a,const char *b) override {++calls;auto it=files.find(a);if(it==files.end())return false;files[b]=it->second;files.erase(it);return true;}
} storage;
ProfileStore profile_store(&storage);
class Backend:public CommunicationBackend {
 public:
 Backend(InputState &i):CommunicationBackend(i,nullptr,0){}
 CommunicationBackendId id=COMMS_BACKEND_XINPUT;
 CommunicationBackendId BackendId() override {return id;}
 void SendReport() override { UpdateOutputs(); }
};
struct Wire {
 std::vector<uint8_t> rx,tx;size_t cursor=0;int free=256;unsigned reads=0,writes=0;
 int available(){return int(rx.size()-cursor);} int read(){++reads;return available()?rx[cursor++]:-1;}
 int availableForWrite(){return free;} size_t write(const uint8_t *b,size_t n){require(int(n)<=free,"never partial TX");++writes;tx.insert(tx.end(),b,b+n);free-=int(n);return n;}
 void append(const std::vector<uint8_t>&bytes){rx.insert(rx.end(),bytes.begin(),bytes.end());}
};
static Wire viewer_wire;
namespace serial {
void init(unsigned long){} void close(){} void print(const char*){}
void write(uint8_t b){viewer_wire.write(&b,1);} void write(uint8_t *b,size_t n){viewer_wire.write(b,n);}
int available_for_write(){return viewer_wire.availableForWrite();}
}
#define private public
#include "comms/B0XXInputViewer.hpp"
#undef private

static std::vector<uint8_t> request(uint64_t token=42) {
 std::vector<uint8_t> b={0xa5,'G','R','I',1,1,16,0}; b.resize(16);runtime_identity::WriteLE(b.data()+8,token,8);return b;
}
static runtime_identity::Snapshot observe(Backend &b,const Config &c) {return runtime_identity::Observe(&b,c,profile_store,ultimate_mode);}
static void neutral(Backend &b,const Config &c,runtime_identity::Status expected) {
 const auto s=observe(b,c); require(s.status==expected,"expected explicit neutral status");
 uint8_t out[72];runtime_identity::EncodeResponse(42,s,out);
 require(std::all_of(out+24,out+72,[](uint8_t v){return v==0;}),"neutral never persistent");
}
static void digest_line(const runtime_identity::Snapshot &s) {
 std::printf("digest=");for(auto b:s.digest)std::printf("%02x",b);std::printf("\n");
}

int main(int argc,char **argv) {
 try {
  require(argc==2,"fixture argument"); static Config config=Config_init_default;
  std::ifstream file(argv[1],std::ios::binary);std::vector<uint8_t> raw((std::istreambuf_iterator<char>(file)),{});
  auto input=pb_istream_from_buffer(raw.data(),raw.size());require(pb_decode(&input,Config_fields,&config)&&input.bytes_left==0,"fixture decode");
  static UltimateProfile original=UltimateProfile_init_default;original=config.ultimate_profiles[0];
  require(profile_store.Begin(),"real store Begin");uint32_t ids[2]={};
  require(profile_store.ImportLegacy(config,ids,2)==ProfileStore::Status::Ok,"real V1-V3 admission");
  for(size_t i=0;i<config.game_mode_configs_count;++i){auto &m=config.game_mode_configs[i];if(m.mode_id==MODE_ULTIMATE&&m.ultimate_profile_config){m.ultimate_profile_id=ids[m.ultimate_profile_config-1];m.ultimate_profile_config=0;}}
  config.ultimate_profiles_count=0;config.ultimate_profile_store_format=1;config.ultimate_profile_store_incarnation=profile_store.Incarnation();
  require(profile_store.PrepareCompact(config)&&profile_store.CompleteMigration(config)==ProfileStore::Status::Ok,"production compact migration");
  InputState buttons{};Backend backend(buttons);const size_t row=1;
  set_mode(&backend,config.game_mode_configs[row],config);
  auto s=observe(backend,config);
  require(s.status==runtime_identity::Status::Persisted&&s.id==ids[0]&&s.row==row+1&&s.requested==ids[0]&&s.revision==1&&s.incarnation==profile_store.Incarnation()&&s.schema==original.schema_version,"actual selected persisted identity");
  digest_line(s);const auto initial=s;
  static UltimateProfile updated=UltimateProfile_init_default;updated=original;updated.tables[0].coordinates[0].x^=1;
  require(profile_store.Update(ids[0],updated,1,100,1000).status==ProfileStore::Status::Ok,"real stored r+1 Update");
  const auto files=storage.files;const unsigned calls=storage.calls;const auto generation=profile_store.Generation();
  const auto transaction=profile_store.LastTransactionToken();const auto active=profile_store.ActiveProfile();
  const bool recovery=profile_store.IsReadOnlyRecovery();
  static Config before=Config_init_default;before=config;
  for(int i=0;i<100;++i){s=observe(backend,config);require(s.revision==1&&std::memcmp(initial.digest,s.digest,32)==0,"stored r+1 must not appear running");}
  require(storage.calls==calls&&storage.files==files&&profile_store.Generation()==generation&&profile_store.LastTransactionToken()==transaction&&profile_store.ActiveProfile()==active&&profile_store.IsReadOnlyRecovery()==recovery&&std::memcmp(&before,&config,sizeof(config))==0,"queries zero storage/mutation/activation");
  // Context remains separately labeled even if the requested reference changes.
  config.game_mode_configs[row].ultimate_profile_id=ids[1];s=observe(backend,config);
  require(s.id==ids[0]&&s.requested==ids[1]&&s.revision==1,"requested ID is not active ID");
  config.game_mode_configs[row].ultimate_profile_id=ids[0];set_mode(&backend,config.game_mode_configs[row],config);
  s=observe(backend,config);require(s.revision==2&&std::memcmp(initial.digest,s.digest,32)!=0,"only real activation loads r+1");
  char path[64];ProfileStorePaths::RecordPath(path,sizeof(path),ids[0],2);const auto newest=storage.files[path];storage.files[path][12]^=1;
  set_mode(&backend,config.game_mode_configs[row],config);s=observe(backend,config);
  require(s.status==runtime_identity::Status::Persisted&&s.revision==1&&std::memcmp(initial.digest,s.digest,32)==0,"recovered previous exact latched revision");storage.files[path]=newest;
  config.game_mode_configs[row].ultimate_profile_id=999;set_mode(&backend,config.game_mode_configs[row],config);
  require(profile_store.ActiveId()==ids[0],"failed Activate preserves stale store ActiveId");
  neutral(backend,config,runtime_identity::Status::SourceFallback);
  config.game_mode_configs[row].ultimate_profile_id=ids[0];set_mode(&backend,config.game_mode_configs[row],config);
  ultimate_mode.SetConfig(config.game_mode_configs[row],&original);neutral(backend,config,runtime_identity::Status::ObjectMismatch);
  config.ultimate_profile_store_format=0;neutral(backend,config,runtime_identity::Status::ObjectMismatch);
  config.ultimate_profiles_count=1;config.ultimate_profiles[0]=original;ultimate_mode.SetConfig(config.game_mode_configs[row],&config.ultimate_profiles[0]);
  neutral(backend,config,runtime_identity::Status::EmbeddedLegacy);config.ultimate_profile_store_format=1;config.ultimate_profiles_count=0;
  GameModeConfig foreign=config.game_mode_configs[row];ultimate_mode.SetConfig(foreign,profile_store.ActiveProfile());neutral(backend,config,runtime_identity::Status::ContextUnavailable);
  set_mode(&backend,config.game_mode_configs[row],config);backend.SetGameMode(nullptr);neutral(backend,config,runtime_identity::Status::NoMode);
  DummyMode other;backend.SetGameMode(&other);neutral(backend,config,runtime_identity::Status::NonUltimate);
  backend.id=COMMS_BACKEND_CONFIGURATOR;neutral(backend,config,runtime_identity::Status::Configurator);backend.id=COMMS_BACKEND_XINPUT;
  require(runtime_identity::Observe(nullptr,config,profile_store,ultimate_mode).status==runtime_identity::Status::NoPrimary,"no primary neutral");
  set_mode(&backend,config.game_mode_configs[row],config);
  ProfileStore unavailable(&storage);
  require(runtime_identity::Observe(&backend,config,unavailable,ultimate_mode).status==runtime_identity::Status::StoreUnavailable,"uninitialized store unavailable");
  auto *active_for_fault=const_cast<UltimateProfile *>(profile_store.ActiveProfile());
  const auto saved_count=active_for_fault->tables_count;active_for_fault->tables_count=UINT16_MAX;
  neutral(backend,config,runtime_identity::Status::DigestFailure);active_for_fault->tables_count=saved_count;
  Ultimate oracle;oracle.SetConfig(config.game_mode_configs[row],profile_store.ActiveProfile());
  runtime_identity::Service service;Wire wire;
  const auto query=request();const unsigned no_io=storage.calls;
  for(unsigned i=0;i<512;++i){buttons.buttons=uint64_t(i)*0x1001001u;OutputState expected{};oracle.UpdateOutputs(buttons,expected,COMMS_BACKEND_XINPUT);wire.rx=query;wire.cursor=0;wire.tx.clear();wire.free=256;service.Poll(wire,&backend,config,profile_store,ultimate_mode,i);OutputState actual{};ultimate_mode.UpdateOutputs(buttons,actual,COMMS_BACKEND_XINPUT);require(actual.buttons==expected.buttons&&std::equal(actual.analog_axes,actual.analog_axes+6,expected.analog_axes),"same-input output noninterference");require(wire.tx.size()==72,"one complete response");}
  require(storage.calls==no_io,"adapter never reads/reconciles/writes store");
  for(unsigned free:{0u,71u,72u,103u}){wire=Wire{};wire.free=int(free);wire.rx=query;service.Poll(wire,&backend,config,profile_store,ultimate_mode,1000);require(wire.tx.empty(),"full TX drops identity without waits/partial data");}
  for(unsigned index:{0u,4u,5u,6u,7u,8u}){wire=Wire{};wire.rx=query;wire.rx[index]=index==8?0:uint8_t(wire.rx[index]^1);service.Poll(wire,&backend,config,profile_store,ultimate_mode,1001);require(wire.tx.empty(),"malformed/zero token rejected");}
  wire=Wire{};wire.rx.assign(query.begin(),query.begin()+8);service.Poll(wire,&backend,config,profile_store,ultimate_mode,2000);wire.append(std::vector<uint8_t>(query.begin()+8,query.end()));service.Poll(wire,&backend,config,profile_store,ultimate_mode,2250);require(wire.tx.empty(),"timeout partial cannot succeed");wire.append(query);service.Poll(wire,&backend,config,profile_store,ultimate_mode,2251);require(wire.tx.size()==72,"resynchronizes fresh magic");
  wire=Wire{};wire.rx.assign(8192,0x55);service.Poll(wire,&backend,config,profile_store,ultimate_mode,3000);require(wire.reads==32&&wire.tx.empty(),"oversized garbage bounded at 32 reads");
  wire=Wire{};wire.rx=query;backend.id=COMMS_BACKEND_DINPUT;service.Poll(wire,&backend,config,profile_store,ultimate_mode,4000);require(wire.reads==0&&wire.tx.empty(),"only primary XInput reader");backend.id=COMMS_BACKEND_XINPUT;
  B0XXInputViewer viewer(buttons,nullptr,0);viewer._clock=0;
  runtime_identity::Service mixed;
  for(unsigned i=0;i<60;++i){viewer_wire.free=256;viewer.SendReport();viewer_wire.rx=query;viewer_wire.cursor=0;mixed.Poll(viewer_wire,&backend,config,profile_store,ultimate_mode,i);}
  size_t viewers=0,responses=0;for(size_t i=0;i<viewer_wire.tx.size();){if(viewer_wire.tx[i]=='0'||viewer_wire.tx[i]=='1'){require(i+25<=viewer_wire.tx.size()&&viewer_wire.tx[i+24]=='\n',"complete viewer record");for(unsigned j=0;j<24;++j)require(viewer_wire.tx[i+j]=='0'||viewer_wire.tx[i+j]=='1',"viewer bytes intact");i+=25;++viewers;}else{require(i+72<=viewer_wire.tx.size()&&viewer_wire.tx[i]==0xa5,"complete identity between viewer records");i+=72;++responses;}}
  require(viewers==10&&responses==60,"viewer pacing remains five increments plus report");
  uint8_t digest[32];const auto started=std::chrono::steady_clock::now();for(unsigned i=0;i<100;++i)require(runtime_identity::PayloadDigest(original,digest),"streaming digest");
  std::printf("sizeof_service=%zu sizeof_snapshot=%zu encoded_profile_bound=%u\n",sizeof(runtime_identity::Service),sizeof(runtime_identity::Snapshot),unsigned(4096));
  std::printf("host_digest_100_us=%lld\n",static_cast<long long>(std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-started).count()));
  std::puts("runtime_identity_actual_selection_store_ultimate_viewer_wire_output=PASS");return 0;
 }catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}
}
