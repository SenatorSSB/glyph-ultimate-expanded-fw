#include "host_stubs.hpp"
#include "core/Persistence.hpp"
#include "core/ProfileStore.hpp"
#include "core/ProfileStorePaths.hpp"
#include "core/ProfileStoreStorage.hpp"
#include <pb_decode.h>
#include <pb_encode.h>
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
#define private public
#include "comms/ConfiguratorBackend.hpp"
#undef private

uint32_t host_millis = 0;
Persistence persistence;

namespace {
struct MemoryStorage final : ProfileStoreStorage {
  enum class Failure { None, TempOpenWrite, TempWrite, TempRead, TempSize, Verify, DestRemove, Rename };
  std::map<std::string, std::vector<uint8_t>> files;
  std::map<std::string, std::vector<uint8_t>> read_overrides;
  bool strict_absent_remove = false;
  bool enforce_littlefs_component_limit = false;
  Failure failure = Failure::None;
  Failure directory_failure = Failure::None;
  ProfileStoreStorageFailure last_failure = ProfileStoreStorageFailure::None;
  bool PathValid(const char *path) const { for (const char *component=path; component; ) { if (*component=='/') ++component; const char *slash=std::strchr(component,'/'); const size_t length=slash?static_cast<size_t>(slash-component):std::strlen(component); if(length>=32)return false; if(!slash)break; component=slash; } return true; }
  Failure For(const char *p) const { return std::strncmp(p,"/ultimate-dir-",14)==0?directory_failure:failure; }
  bool Write(const char *p, const uint8_t *b, size_t n) override { const Failure active=For(p);last_failure=ProfileStoreStorageFailure::None;if(enforce_littlefs_component_limit&&!PathValid(p)){last_failure=ProfileStoreStorageFailure::TempOpenWrite;return false;}if(active==Failure::TempOpenWrite){last_failure=ProfileStoreStorageFailure::TempOpenWrite;return false;}if(active==Failure::TempWrite){last_failure=ProfileStoreStorageFailure::TempWrite;return false;}files[p] = {b, b + n}; return true; }
  bool Read(const char *p, uint8_t *b, size_t n) override { const Failure active=For(p);last_failure=ProfileStoreStorageFailure::None;if(active==Failure::TempRead){last_failure=ProfileStoreStorageFailure::TempRead;return false;}if(active==Failure::TempSize){last_failure=ProfileStoreStorageFailure::TempSize;return false;}auto i=files.find(p); if(i==files.end()||i->second.size()!=n)return false; auto replacement=read_overrides.find(p);if(replacement!=read_overrides.end()){if(replacement->second.size()!=n)return false;std::memcpy(b,replacement->second.data(),n);}else std::memcpy(b,i->second.data(),n);if(active==Failure::Verify)b[0]^=1;return true; }
  size_t Size(const char *p) override { auto i=files.find(p);return i==files.end()?0:i->second.size(); }
  bool Exists(const char *p) override { return files.find(p)!=files.end(); }
  ProfileStoreStorageFailure LastFailure() const override { return last_failure; }
  bool Remove(const char *p) override { auto i=files.find(p);if(i==files.end())return !strict_absent_remove;if(For(p)==Failure::DestRemove)return false;files.erase(i);return true; }
  bool Rename(const char *a,const char *b) override { if(enforce_littlefs_component_limit&&(!PathValid(a)||!PathValid(b)))return false;if(For(a)==Failure::Rename)return false;auto i=files.find(a);if(i==files.end())return false;files[b]=i->second;files.erase(i);return true; }
};
MemoryStorage storage;
void require(bool ok, const char *m) { if (!ok) throw std::runtime_error(m); }
class DuplexStream final : public Stream {
 public:
  std::vector<uint8_t> rx, tx; size_t pos=0; size_t tx_budget=SIZE_MAX; bool advertise_full_fifo=false;
  int availableForWrite() override { return advertise_full_fifo?64:static_cast<int>(std::min(size_t{64},tx_budget)); }
  int available() override { return static_cast<int>(rx.size()-pos); }
  int read() override { return pos<rx.size()?rx[pos++]:-1; }
  int peek() override { return pos<rx.size()?rx[pos]:-1; }
  void flush() override {}
  size_t write(uint8_t b) override { if(!tx_budget)return 0;--tx_budget;tx.push_back(b);return 1; }
  size_t write(const uint8_t *b,size_t n) override { const size_t accepted=std::min(n,tx_budget);tx_budget-=accepted;tx.insert(tx.end(),b,b+accepted);return accepted; }
  void append(const std::vector<uint8_t>& b){rx.insert(rx.end(),b.begin(),b.end());}
  size_t remaining()const{return rx.size()-pos;} void clear(){tx.clear();}
};
std::vector<uint8_t> decode(const std::vector<uint8_t>& in) {
  require(!in.empty()&&in.back()==0,"COBS delimiter");std::vector<uint8_t> out;
  for(size_t o=0;o+1<in.size();) { uint8_t c=in[o++];require(c&&o+c<=in.size(),"COBS valid");for(size_t i=0;i<c-1;++i)require(in[o+i]!=0,"COBS raw zero");out.insert(out.end(),in.begin()+o,in.begin()+o+c-1);o+=c-1;if(c!=0xff&&o+1<in.size())out.push_back(0); } return out;
}
void malformed_cobs_controls() { bool rejected=false;try{(void)decode({2,0});}catch(const std::exception&){rejected=true;}require(rejected,"COBS 02 00 rejected"); }
std::vector<uint8_t> frame(const ProfileStoreRequest& request) {
  size_t n=0;require(pb_get_encoded_size(&n,ProfileStoreRequest_fields,&request),"request size");std::vector<uint8_t> data(n);pb_ostream_t pb=pb_ostream_from_buffer(data.data(),data.size());require(pb_encode(&pb,ProfileStoreRequest_fields,&request),"request encode");data.resize(pb.bytes_written);
  DuplexStream wire;packetio::COBSPrint out(wire);out.write(static_cast<uint8_t>(CMD_PROFILE_STORE));out.write(data.data(),data.size());require(out.end(),"real COBS end");require(wire.tx.back()==0,"request delimiter");return wire.tx;
}
ProfileStoreResponse response(const DuplexStream& wire) {
  const auto data=decode(wire.tx);require(!data.empty()&&data[0]==CMD_PROFILE_STORE,"response command");ProfileStoreResponse r=ProfileStoreResponse_init_default;pb_istream_t pb=pb_istream_from_buffer(data.data()+1,data.size()-1);require(pb_decode(&pb,ProfileStoreResponse_fields,&r)&&pb.bytes_left==0,"response decode");return r;
}
void seed(const char* path,Config* config) {
  std::ifstream f(path,std::ios::binary);require(bool(f),"fixture open");std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)),{});pb_istream_t pb=pb_istream_from_buffer(bytes.data(),bytes.size());*config=Config_init_default;require(pb_decode(&pb,Config_fields,config)&&pb.bytes_left==0&&config->ultimate_profiles_count==2,"two real fixture profiles");
  require(profile_store.Begin(),"ProfileStore begin");uint32_t ids[2]={};require(profile_store.ImportLegacy(*config,ids,2)==ProfileStore::Status::Ok&&ids[0]&&ids[1],"ProfileStore import");Config compact=*config;for(size_t i=0;i<compact.game_mode_configs_count;++i){auto &mode=compact.game_mode_configs[i];if(mode.mode_id==MODE_ULTIMATE&&mode.ultimate_profile_config){mode.ultimate_profile_id=ids[mode.ultimate_profile_config-1];mode.ultimate_profile_config=0;}}compact.ultimate_profiles_count=0;compact.ultimate_profile_store_format=ProfileStore::kCompactConfigFormat;compact.ultimate_profile_store_incarnation=profile_store.Incarnation();require(profile_store.CompleteMigration(compact)==ProfileStore::Status::Ok&&profile_store.Count()==2,"ProfileStore ready");*config=compact;persistence.Seed(compact);
}
ProfileStoreRequest list() { ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_LIST;r.page_size=8;r.request_token=0x51;return r; }
ProfileStoreRequest status() { ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_STATUS;r.request_token=0x52;return r; }
void expect_list(const DuplexStream& wire) { const auto r=response(wire);require(r.status==PROFILE_STORE_OK&&r.entries_count==2&&r.next_page_cursor==0,"LIST result");require(r.entries[0].profile_id&&r.entries[1].profile_id&&r.entries[0].profile_id!=r.entries[1].profile_id,"two listed profiles"); }
void expect_status(const DuplexStream& wire) { require(response(wire).status==PROFILE_STORE_OK,"STATUS result"); }
ProfileStoreResponse send(ConfiguratorBackend& b,DuplexStream& wire,const ProfileStoreRequest& r) { wire.clear();wire.append(frame(r));b.SendReport();require(wire.remaining()==0,"CRUD request tail");return response(wire); }
std::vector<uint8_t> config_bytes(const Config &config) {
  size_t size=0;require(pb_get_encoded_size(&size,Config_fields,&config),"Config encoded size");
  std::vector<uint8_t> bytes(size);pb_ostream_t pb=pb_ostream_from_buffer(bytes.data(),bytes.size());
  require(pb_encode(&pb,Config_fields,&config),"Config encode");return bytes;
}
void reference_purity(const char *path) {
  Config config=Config_init_default;seed(path,&config);
  UltimateProfile profile=UltimateProfile_init_default;
  require(profile_store.Read(1,profile)==ProfileStore::Status::Ok,"reference fixture source");
  const auto third=profile_store.Create(profile,"Migrated 1",0,0x3001,0x3101);
  const auto fourth=profile_store.Create(profile,"Migrated 2",1,0x3002,0x3102);
  require(third.status==ProfileStore::Status::Ok&&third.id==3&&fourth.status==ProfileStore::Status::Ok&&fourth.id==4,"reference fixture exact IDs 3/4");
  require(config.game_mode_configs_count>=3&&config.communication_backend_configs_count==3,"hardware selector fixture extents");
  require(config.communication_backend_configs[2].backend_id==COMMS_BACKEND_CONFIGURATOR,"USB selector 3 is Configurator");
  config.game_mode_configs[0].mode_id=MODE_MELEE;
  config.game_mode_configs[1].ultimate_profile_id=3;
  config.game_mode_configs[2].ultimate_profile_id=4;
  config.default_backend_config=1;config.default_usb_backend_config=1;
  config.rgb_brightness=81;config.default_dashboard_option=DASHBOARD_MENU_BUTTON_HINTS;
  persistence.Seed(config);
  ConfigValidationError error;require(persistence.ValidateConfig(config,error),"durable reference fixture validates");
  InputState inputs;DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);
  backend._config.default_usb_backend_config=3;
  backend._config.default_backend_config=3;
  backend._config.communication_backend_configs[0].default_mode_config=2;
  backend._config.communication_backend_configs[2].default_mode_config=3;
  backend._config.rgb_brightness=42;backend._config.default_dashboard_option=DASHBOARD_INPUT_VIEWER;
  require(persistence.ValidateConfig(backend._config,error),"live transient fixture validates");
  const Config durable_before=persistence.durable,live_before=backend._config;
  const auto files=storage.files;const auto count=profile_store.Count();const auto store_generation=profile_store.Generation();
  auto request=[&](uint32_t id) {
    ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_SET_MODE_REFERENCE;
    r.expected_store_generation=profile_store.Generation();r.expected_config_generation=persistence.ConfigGeneration(backend._config);
    r.mode_config_index=1;r.profile_id=id;r.request_token=0x4000+persistence.save_calls+persistence.load_calls;return r;
  };
  const uint32_t old_generation=persistence.ConfigGeneration(config);
  const auto changed=send(backend,wire,request(4));
  require(changed.status==PROFILE_STORE_OK,"reference durable save");
  Config expected=durable_before;expected.game_mode_configs[1].ultimate_profile_id=4;expected.game_mode_configs[1].ultimate_profile_config=0;
  require(config_bytes(persistence.durable)==config_bytes(expected),"entire durable encoding changes only requested reference fields");
  require(std::memcmp(&backend._config,&live_before,sizeof(Config))==0,"entire live Config unchanged, including runtime reference");
  require(changed.config_generation==Persistence::GenerationFor(expected)&&changed.config_generation!=old_generation,"response reports saved durable generation");
  require(storage.files==files&&profile_store.Count()==count&&profile_store.Generation()==store_generation,"reference does not mutate ProfileStore");
  Config rebooted=Config_init_default;require(persistence.LoadConfigChecked(rebooted)==Persistence::LoadResult::Loaded,"reboot load");
  require(config_bytes(rebooted)==config_bytes(expected)&&rebooted.default_usb_backend_config==1&&rebooted.game_mode_configs[1].ultimate_profile_id==4,"reboot receives durable selectors and ID4");
  auto deletion=[&](uint32_t id,ProfileStoreStatus wanted) {
    ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_DELETE;r.expected_store_generation=store_generation;r.profile_id=id;r.request_token=0x5000+id;
    require(send(backend,wire,r).status==wanted,"DELETE guards freshly durable and live references");
    require(storage.files==files&&profile_store.Count()==count&&profile_store.Generation()==store_generation,"refused DELETE leaves ProfileStore unchanged");
  };
  deletion(4,PROFILE_STORE_REFERENCED); // Newly durable reference before reboot.
  deletion(3,PROFILE_STORE_REFERENCED); // Still the current live runtime profile.
  persistence.fail_load=true;deletion(1,PROFILE_STORE_IO_FAILURE);persistence.fail_load=false;
  require(config_bytes(persistence.durable)==config_bytes(expected)&&std::memcmp(&backend._config,&live_before,sizeof(Config))==0,"DELETE guards preserve both Configs");
  // Consecutive saves must start from the latest durable body each time. ID0 is
  // the built-in profile selection, and still requires generation protection.
  for(uint32_t id:{0u,4u,3u,0u}){
    const auto saved=send(backend,wire,request(id));require(saved.status==PROFILE_STORE_OK,"consecutive reference save including ID0");
    expected.game_mode_configs[1].ultimate_profile_id=id;
    require(config_bytes(persistence.durable)==config_bytes(expected),"consecutive reference save derives from durable Config");
    require(saved.config_generation==Persistence::GenerationFor(expected)&&std::memcmp(&backend._config,&live_before,sizeof(Config))==0,"consecutive save generation/live boundary");
  }
  enum Failure { StaleConfig, WideConfig, StaleStore, MissingId, NonUltimate, Index, Validation, Load, Save, AfterLoadRace, BeforeSaveRace };
  for(Failure failure:{StaleConfig,WideConfig,StaleStore,MissingId,NonUltimate,Index,Validation,Load,Save,AfterLoadRace,BeforeSaveRace}){
    persistence.Seed(durable_before);auto r=request(4);ProfileStoreStatus wanted=PROFILE_STORE_CONFLICT;
    switch(failure){
      case StaleConfig: ++r.expected_config_generation;break;
      case WideConfig: r.expected_config_generation+=uint64_t{1}<<32;break;
      case StaleStore: --r.expected_store_generation;break;
      case MissingId: r.profile_id=999999;wanted=PROFILE_STORE_NOT_FOUND;break;
      case NonUltimate: r.mode_config_index=0;wanted=PROFILE_STORE_INVALID;break;
      case Index: r.mode_config_index=config.game_mode_configs_count;break;
      case Validation: persistence.fail_validation=true;wanted=PROFILE_STORE_INVALID;break;
      case Load: persistence.fail_load=true;wanted=PROFILE_STORE_IO_FAILURE;break;
      case Save: persistence.fail_save=true;wanted=PROFILE_STORE_IO_FAILURE;break;
      case AfterLoadRace: persistence.advance_after_load=true;break;
      case BeforeSaveRace: persistence.advance_before_save=true;break;
    }
    const auto failed=send(backend,wire,r);
    if(failed.status!=wanted)std::fprintf(stderr,"reference failure case %d returned %d wanted %d\n",failure,failed.status,wanted);
    require(failed.status==wanted,"reference failure status");
    require(config_bytes(persistence.durable)==config_bytes(durable_before)&&std::memcmp(&backend._config,&live_before,sizeof(Config))==0,"failed reference leaves entire durable and live Config unchanged");
    require(storage.files==files&&profile_store.Count()==count&&profile_store.Generation()==store_generation,"failed reference leaves ProfileStore unchanged");
    persistence.fail_validation=false;persistence.fail_load=false;persistence.fail_save=false;persistence.advance_after_load=false;persistence.advance_before_save=false;
  }
  std::puts("profile_store_reference_transactional_purity=PASS");
}

void crud_probe(ConfiguratorBackend& b,DuplexStream& wire) {
  const auto durable_before=config_bytes(persistence.durable);const auto saves_before=persistence.save_calls;
  UltimateProfile profile=UltimateProfile_init_default;require(profile_store.Read(profile_store.EntryAt(0)->id,profile)==ProfileStore::Status::Ok,"read seeded profile");
  ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_CREATE;r.expected_store_generation=profile_store.Generation();r.has_profile=true;r.profile=profile;std::strcpy(r.name,"Config create");r.display_rank=9;r.request_token=0x101;const auto made=send(b,wire,r);require(made.status==PROFILE_STORE_OK&&made.profile_id!=0,"CREATE");const uint32_t id=made.profile_id;
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_READ;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.request_token=0x102;const auto read=send(b,wire,r);require(read.status==PROFILE_STORE_OK&&read.profile_id==id&&read.has_profile,"READ persisted CREATE");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_UPDATE;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.expected_profile_revision=read.profile_revision;r.has_profile=true;r.profile=profile;r.request_token=0x103;const auto updated=send(b,wire,r);require(updated.status==PROFILE_STORE_OK&&updated.profile_id==id&&updated.profile_revision==read.profile_revision+1,"UPDATE stable identity");
  const uint32_t stale=profile_store.Generation();r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_RENAME;r.expected_store_generation=stale;r.profile_id=id;std::strcpy(r.name,"Renamed");r.request_token=0x104;require(send(b,wire,r).status==PROFILE_STORE_OK,"RENAME");r.expected_store_generation=stale;r.request_token=0x105;require(send(b,wire,r).status==PROFILE_STORE_CONFLICT,"generation CONFLICT");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_REORDER;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.display_rank=44;r.request_token=0x106;require(send(b,wire,r).status==PROFILE_STORE_OK,"REORDER");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_DUPLICATE;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.expected_profile_revision=updated.profile_revision;std::strcpy(r.name,"Copy");r.display_rank=45;r.request_token=0x107;const auto copy=send(b,wire,r);require(copy.status==PROFILE_STORE_OK&&copy.profile_id!=id,"DUPLICATE");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_READ;r.expected_store_generation=profile_store.Generation();r.profile_id=999999;r.request_token=0x108;require(send(b,wire,r).status==PROFILE_STORE_NOT_FOUND,"READ missing ID");
  require(persistence.save_calls==saves_before&&config_bytes(persistence.durable)==durable_before,"non-reference CRUD never saves Config");
  size_t ultimate=0;while(ultimate<b._config.game_mode_configs_count&&b._config.game_mode_configs[ultimate].mode_id!=MODE_ULTIMATE)++ultimate;require(ultimate<b._config.game_mode_configs_count,"Ultimate mode for reference");r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_SET_MODE_REFERENCE;r.expected_store_generation=profile_store.Generation();r.expected_config_generation=persistence.ConfigGeneration(b._config);r.mode_config_index=ultimate;r.profile_id=id;r.request_token=0x109;require(send(b,wire,r).status==PROFILE_STORE_OK,"SET_MODE_REFERENCE");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_DELETE;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.request_token=0x10a;require(send(b,wire,r).status==PROFILE_STORE_REFERENCED,"DELETE referenced refusal");
  r.expected_store_generation=profile_store.Generation();r.profile_id=copy.profile_id;r.request_token=0x10b;require(send(b,wire,r).status==PROFILE_STORE_OK,"DELETE legal duplicate");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_QUERY_TRANSACTION;r.expected_store_generation=profile_store.Generation();r.request_token=0x10b;require(send(b,wire,r).status==PROFILE_STORE_OK,"QUERY_TRANSACTION");
  require(persistence.save_calls==saves_before+1,"only SET_MODE_REFERENCE saves Config across CRUD/delete/query");
  r=ProfileStoreRequest_init_default;r.protocol_version=2;r.operation=PROFILE_STORE_STATUS;wire.clear();wire.append(frame(r));b.SendReport();const auto invalid=decode(wire.tx);require(invalid[0]==CMD_ERROR,"malformed protocol rejected");wire.clear();wire.append(frame(status()));b.SendReport();expect_status(wire);
}
void consecutive_lists(ConfiguratorBackend& b,DuplexStream& wire) {
  const auto request=frame(list());for(int i=0;i<3;++i){wire.clear();wire.append(request);b.SendReport();
#ifdef EXPECT_DUPLICATE_NEXT_DROP
    if(i==1)require(wire.tx.empty(),"original duplicate-next drops second LIST");else expect_list(wire);
#else
    expect_list(wire);
#endif
    require(wire.remaining()==0,"no unexplained RX tail");}
}
void timeout_and_cap(ConfiguratorBackend& b,DuplexStream& wire,const Config& baseline) {
  const uint32_t generation=profile_store.Generation();const size_t count=profile_store.Count();const auto files=storage.files;const unsigned saves=persistence.save_calls;wire.clear();wire.append({3,static_cast<uint8_t>(CMD_PROFILE_STORE),0x08});b.SendReport();const auto timeout=decode(wire.tx);require(timeout.size()==1+std::strlen("Profile store frame timeout")&&timeout[0]==CMD_ERROR,"timeout error");require(host_millis>=5000&&std::memcmp(&baseline,&b._config,sizeof(Config))==0&&profile_store.Generation()==generation&&profile_store.Count()==count&&storage.files==files&&persistence.save_calls==saves,"timeout state preserved");
  const auto valid=frame(status());wire.clear();wire.append(valid);b.SendReport();require(wire.tx.empty(),"no delimiter rejects following STATUS");wire.clear();wire.append(valid);b.SendReport();expect_status(wire);
  DuplexStream oversized;packetio::COBSPrint out(oversized);out.write(static_cast<uint8_t>(CMD_PROFILE_STORE));std::vector<uint8_t> body(8192,0x55);out.write(body.data(),body.size());require(out.end(),"oversized COBS end");wire.clear();wire.append(oversized.tx);b.SendReport();const auto cap=decode(wire.tx);require(cap.size()==30&&cap[0]==CMD_ERROR&&std::memcmp(&baseline,&b._config,sizeof(Config))==0&&profile_store.Generation()==generation&&profile_store.Count()==count&&storage.files==files&&persistence.save_calls==saves,"8192 cap bounded failure");wire.clear();wire.append(valid);b.SendReport();expect_status(wire);
}
void path_component_limits() {
  char record[64], temporary[64], directory[32], directory_temporary[32];
  ProfileStorePaths::RecordPath(record,sizeof(record),UINT32_MAX,UINT32_MAX);
  ProfileStorePaths::RecordTemporaryPath(temporary,sizeof(temporary),UINT32_MAX,UINT32_MAX);
  require(std::strlen(record+1)==ProfileStorePaths::kRecordComponentLength&&std::strlen(record+1)<=ProfileStorePaths::kMaxFsComponent,"record max component");
  require(std::strlen(temporary+1)==ProfileStorePaths::kRecordTemporaryComponentLength&&std::strlen(temporary+1)<=ProfileStorePaths::kMaxFsComponent,"record temporary max component");
  for(uint8_t slot=0;slot<2;++slot){ProfileStorePaths::DirectoryPath(directory,sizeof(directory),slot);ProfileStorePaths::DirectoryTemporaryPath(directory_temporary,sizeof(directory_temporary),slot);require(std::strlen(directory+1)==ProfileStorePaths::kDirectoryComponentLength&&std::strlen(directory+1)<=ProfileStorePaths::kMaxFsComponent,"directory component");require(std::strlen(directory_temporary+1)==ProfileStorePaths::kDirectoryTemporaryComponentLength&&std::strlen(directory_temporary+1)<=ProfileStorePaths::kMaxFsComponent,"directory temporary component");}
}
void first_create_from_empty(const char *path, const char *mode) {
  std::ifstream f(path,std::ios::binary);require(bool(f),"fixture open");std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)),{});pb_istream_t pb=pb_istream_from_buffer(bytes.data(),bytes.size());Config config=Config_init_default;require(pb_decode(&pb,Config_fields,&config)&&pb.bytes_left==0&&config.ultimate_profiles_count==2,"two real fixture profiles");
  const UltimateProfile profile=config.ultimate_profiles[0];config.ultimate_profiles_count=0;config.ultimate_profile_store_format=ProfileStore::kCompactConfigFormat;config.ultimate_profile_store_incarnation=1;
  storage.strict_absent_remove=true;storage.failure=MemoryStorage::Failure::None;storage.enforce_littlefs_component_limit=std::strcmp(mode,"--path-limit-create")==0;
  const char *expected="";
  if(std::strcmp(mode,"--io-temp-open-write")==0){storage.failure=MemoryStorage::Failure::TempOpenWrite;expected="record.temp_open_write";}
  else if(std::strcmp(mode,"--io-temp-write")==0){storage.failure=MemoryStorage::Failure::TempWrite;expected="record.temp_write";}
  else if(std::strcmp(mode,"--io-temp-read")==0){storage.failure=MemoryStorage::Failure::TempRead;expected="record.temp_read";}
  else if(std::strcmp(mode,"--io-verify")==0){storage.failure=MemoryStorage::Failure::Verify;expected="record.verify";}
  else if(std::strcmp(mode,"--io-dest-remove")==0){storage.failure=MemoryStorage::Failure::DestRemove;expected="record.dest_remove";storage.files["/ultimate-00000001-00000001.bin"]={0x5a};}
  else if(std::strcmp(mode,"--io-rename")==0){storage.failure=MemoryStorage::Failure::Rename;expected="record.rename";}
  else require(std::strcmp(mode,"--empty-create")==0||std::strcmp(mode,"--io-stale-reset")==0||std::strcmp(mode,"--path-limit-create")==0,"empty create mode");
  path_component_limits();
  for(size_t i=0;i<config.game_mode_configs_count;++i)config.game_mode_configs[i].ultimate_profile_config=0;
  persistence.Seed(config);
  require(profile_store.Begin()&&profile_store.Count()==0,"empty ProfileStore begin");
  InputState inputs;DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);
  ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_CREATE;r.expected_store_generation=profile_store.Generation();r.has_profile=true;r.profile=profile;std::strcpy(r.name,"First create");r.display_rank=1;r.request_token=0x401;const auto made=send(backend,wire,r);
  if(expected[0]){require(made.status==PROFILE_STORE_IO_FAILURE&&std::strcmp(made.diagnostic,expected)==0,"empty-store CREATE diagnostic");std::puts("profile_store_full_stream_create_diagnostic=PASS");return;}
#ifdef EXPECT_LEGACY_RECORD_TEMP_PATH
  if(std::strcmp(mode,"--path-limit-create")==0){require(made.status==PROFILE_STORE_IO_FAILURE&&std::strcmp(made.diagnostic,"record.temp_open_write")==0,"legacy temporary path rejected");std::puts("profile_store_full_stream_legacy_path_rejected=PASS");return;}
#endif
  if(std::strcmp(mode,"--io-stale-reset")==0){
    storage.failure=MemoryStorage::Failure::TempWrite;
    r.expected_store_generation=profile_store.Generation();
    r.request_token=0x404;
    const auto record_failure=send(backend,wire,r);
    require(record_failure.status==PROFILE_STORE_IO_FAILURE&&std::strcmp(record_failure.diagnostic,"record.temp_write")==0,"record diagnostic before reset");
    storage.failure=MemoryStorage::Failure::None;
    size_t ultimate=0;while(ultimate<backend._config.game_mode_configs_count&&backend._config.game_mode_configs[ultimate].mode_id!=MODE_ULTIMATE)++ultimate;
    require(ultimate<backend._config.game_mode_configs_count,"Ultimate mode for stale diagnostic reset");
    persistence.fail_save=true;
    r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_SET_MODE_REFERENCE;r.expected_store_generation=profile_store.Generation();r.expected_config_generation=persistence.ConfigGeneration(backend._config);r.mode_config_index=ultimate;r.profile_id=0;r.request_token=0x405;
    const auto persistence_failure=send(backend,wire,r);
    persistence.fail_save=false;
    require(persistence_failure.status==PROFILE_STORE_IO_FAILURE&&persistence_failure.diagnostic[0]==0,"request-bound diagnostic reset");
    std::puts("profile_store_full_stream_diagnostic_reset=PASS");return;
  }
  require(made.status==PROFILE_STORE_OK&&made.diagnostic[0]==0&&made.profile_id==1&&made.profile_revision==1,"empty-store CREATE");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_LIST;r.expected_store_generation=profile_store.Generation();r.page_size=8;r.request_token=0x402;const auto listed=send(backend,wire,r);require(listed.status==PROFILE_STORE_OK&&listed.entries_count==1&&listed.entries[0].profile_id==made.profile_id,"empty-store LIST");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_READ;r.expected_store_generation=profile_store.Generation();r.profile_id=made.profile_id;r.request_token=0x403;const auto read=send(backend,wire,r);require(read.status==PROFILE_STORE_OK&&read.has_profile&&read.profile_id==made.profile_id,"empty-store READ");
  if(std::strcmp(mode,"--path-limit-create")==0){ProfileStore reboot(&storage);require(reboot.Begin()&&reboot.Count()==1,"path-limited reboot");UltimateProfile restored=UltimateProfile_init_default;require(reboot.Read(made.profile_id,restored)==ProfileStore::Status::Ok&&std::memcmp(&restored,&profile,sizeof(profile))==0,"path-limited reboot record");std::puts("profile_store_full_stream_path_limited_create=PASS");return;}
  std::puts("profile_store_full_stream_empty_create=PASS");
}
void path_limited_import(const char *path) {
  storage.enforce_littlefs_component_limit=true;storage.strict_absent_remove=true;Config config=Config_init_default;seed(path,&config);require(profile_store.Count()==2,"path-limited import count");ProfileStore reboot(&storage);require(reboot.Begin()&&reboot.Count()==2,"path-limited import reboot");UltimateProfile profile=UltimateProfile_init_default;require(reboot.Read(reboot.EntryAt(0)->id,profile)==ProfileStore::Status::Ok,"path-limited imported record");std::puts("profile_store_strict_path_import=PASS");
}
void directory_failure_from_empty(const char *path, const char *mode) {
  std::ifstream f(path,std::ios::binary);require(bool(f),"fixture open");std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)),{});pb_istream_t pb=pb_istream_from_buffer(bytes.data(),bytes.size());Config config=Config_init_default;require(pb_decode(&pb,Config_fields,&config)&&pb.bytes_left==0,"fixture decode");UltimateProfile profile=config.ultimate_profiles[0];config.ultimate_profiles_count=0;config.ultimate_profile_store_format=ProfileStore::kCompactConfigFormat;config.ultimate_profile_store_incarnation=1;
  storage.strict_absent_remove=true;storage.enforce_littlefs_component_limit=true;storage.failure=MemoryStorage::Failure::None;storage.directory_failure=MemoryStorage::Failure::None;const char *expected="";
  if(std::strcmp(mode,"--directory-temp-open")==0){storage.directory_failure=MemoryStorage::Failure::TempOpenWrite;expected="directory.temp_open_write";}else if(std::strcmp(mode,"--directory-temp-write")==0){storage.directory_failure=MemoryStorage::Failure::TempWrite;expected="directory.temp_write";}else if(std::strcmp(mode,"--directory-temp-read")==0){storage.directory_failure=MemoryStorage::Failure::TempRead;expected="directory.temp_read";}else if(std::strcmp(mode,"--directory-temp-size")==0){storage.directory_failure=MemoryStorage::Failure::TempSize;expected="directory.temp_size";}else if(std::strcmp(mode,"--directory-verify")==0){storage.directory_failure=MemoryStorage::Failure::Verify;expected="directory.verify";}else if(std::strcmp(mode,"--directory-dest-remove")==0){storage.directory_failure=MemoryStorage::Failure::DestRemove;expected="directory.dest_remove";}else if(std::strcmp(mode,"--directory-rename")==0){storage.directory_failure=MemoryStorage::Failure::Rename;expected="directory.rename";}else require(false,"directory failure mode");
  require(profile_store.Begin()&&profile_store.Generation()==0,"empty directory store");if(std::strcmp(mode,"--directory-dest-remove")==0)storage.files["/ultimate-dir-0.bin"]={0x5a};InputState inputs;DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_CREATE;r.expected_store_generation=0;r.has_profile=true;r.profile=profile;std::strcpy(r.name,"Directory failure");r.display_rank=1;r.request_token=0x501;const auto made=send(backend,wire,r);require(made.status==PROFILE_STORE_COMMIT_UNKNOWN&&made.profile_id==1&&made.profile_revision==1&&std::strcmp(made.diagnostic,expected)==0,"directory failure response");storage.directory_failure=MemoryStorage::Failure::None;if(std::strcmp(mode,"--directory-dest-remove")==0){require(!profile_store.Begin()&&profile_store.IsReadOnlyRecovery()&&!profile_store.IsReady(),"injected invalid destination remains recovery-only after failed removal");}else require(profile_store.Begin()&&profile_store.Generation()==0&&profile_store.Count()==0,"directory failure reboot empty");r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_QUERY_TRANSACTION;r.expected_store_generation=0;r.request_token=0x501;require(send(backend,wire,r).status==PROFILE_STORE_NOT_FOUND,"directory failure query not committed");std::puts("profile_store_full_stream_directory_diagnostic=PASS");
}



void direct_create_replay(const char *path) {
  Config config=Config_init_default;seed(path,&config);UltimateProfile profile=UltimateProfile_init_default;
  require(profile_store.Read(profile_store.EntryAt(0)->id,profile)==ProfileStore::Status::Ok,"direct replay source profile");
  const auto made=profile_store.Create(profile,"Direct replay",7,0xabc,0xdef);
  require(made.status==ProfileStore::Status::Ok,"direct CREATE committed");
  const auto files=storage.files;const auto count=profile_store.Count();const auto generation=profile_store.Generation();
  for(unsigned reboot=0;reboot<2;++reboot){
    if(reboot)require(profile_store.Begin(),"direct replay boot");
    const auto replay=profile_store.Create(profile,"Direct replay",7,0xabc,0xdef);
    require(replay.status==made.status&&replay.id==made.id&&replay.revision==made.revision&&replay.generation==made.generation,"direct CREATE returns cached identity");
    const auto conflict=profile_store.Create(profile,"Direct replay",7,0xabc,0xdf0);
    require(conflict.status==ProfileStore::Status::Conflict,"direct CREATE token/digest collision refused");
    require(storage.files==files&&profile_store.Count()==count&&profile_store.Generation()==generation,"direct CREATE replay and collision do not mutate");
  }
  std::puts("profile_store_direct_create_replay=PASS");
}
void stale_valid_readback(const char *path, bool directory) {
  std::ifstream f(path,std::ios::binary);require(bool(f),"fixture open");std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)),{});
  pb_istream_t pb=pb_istream_from_buffer(bytes.data(),bytes.size());Config config=Config_init_default;
  require(pb_decode(&pb,Config_fields,&config)&&pb.bytes_left==0,"fixture decode");
  const UltimateProfile first=config.ultimate_profiles[0];
  config.ultimate_profiles_count=0;config.ultimate_profile_store_format=ProfileStore::kCompactConfigFormat;config.ultimate_profile_store_incarnation=1;
  storage.strict_absent_remove=true;storage.enforce_littlefs_component_limit=true;require(profile_store.Begin(),"stale proof begin");
  InputState inputs;DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);
  ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_CREATE;r.has_profile=true;r.profile=first;r.request_token=0x901;std::strcpy(r.name,"Original payload");
  // An interrupted root publication leaves a real internally valid record and
  // root temporary, both for the exact same next identity/generation.
  storage.directory_failure=MemoryStorage::Failure::Rename;
  const auto interrupted=send(backend,wire,r);require(interrupted.status==PROFILE_STORE_COMMIT_UNKNOWN,"seed valid uncommitted envelopes");
  storage.directory_failure=MemoryStorage::Failure::None;
  const std::string record="/ultimate-00000001-00000001.bin", root="/ultimate-dir-0.tmp";
  const auto old_record=storage.files.at(record),old_root=storage.files.at(root);
  if(directory){storage.read_overrides[root]=old_root;std::strcpy(r.name,"Changed payload");}
  else{
    // Change one in-range coordinate without changing protobuf varint length.
    bool changed=false;
    for(size_t table=0;table<r.profile.tables_count&&!changed;++table)
      for(size_t coordinate=0;coordinate<r.profile.tables[table].coordinates_count&&!changed;++coordinate){
        auto &x=r.profile.tables[table].coordinates[coordinate].x;
        if(x>1&&x<=255){x^=1;changed=true;}
      }
    require(changed,"profile coordinate available for same-size mutation");
    storage.read_overrides["/ultimate-00000001-00000001.tmp"]=old_record;
  }
  r.request_token=0x902;const auto rejected=send(backend,wire,r);
  require(rejected.status==(directory?PROFILE_STORE_COMMIT_UNKNOWN:PROFILE_STORE_IO_FAILURE)&&
          std::strcmp(rejected.diagnostic,directory?"directory.verify":"record.verify")==0,"old valid envelope rejected as unintended bytes");
  require(profile_store.Count()==0&&profile_store.Generation()==0,"old valid readback cannot publish logical state");
  if(!directory)require(storage.files.at(record)==old_record,"old record destination preserved before verification");
  storage.read_overrides.clear();require(profile_store.Begin()&&profile_store.Count()==0&&profile_store.Generation()==0,"old valid rejection reload remains empty");
  const auto made=send(backend,wire,r);require(made.status==PROFILE_STORE_OK&&made.profile_id==1,"retry exact intended image succeeds");
  UltimateProfile restored=UltimateProfile_init_default;require(profile_store.Read(1,restored)==ProfileStore::Status::Ok&&std::memcmp(&restored,&r.profile,sizeof(restored))==0,"retry committed payload is intended profile");
  std::puts("profile_store_old_valid_readback_rejected=PASS");
}
void root_fault_recovery(const char *path) {
  std::ifstream file(path,std::ios::binary);require(bool(file),"root fault fixture");
  std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(file)),{});pb_istream_t pb=pb_istream_from_buffer(bytes.data(),bytes.size());
  Config config=Config_init_default;require(pb_decode(&pb,Config_fields,&config)&&config.ultimate_profiles_count==2,"root fault decode");
  const UltimateProfile profile=config.ultimate_profiles[0];config.ultimate_profiles_count=0;config.ultimate_profile_store_format=1;config.ultimate_profile_store_incarnation=1;
  for(size_t i=0;i<config.game_mode_configs_count;++i)config.game_mode_configs[i].ultimate_profile_config=0;
  persistence.Seed(config);require(profile_store.Begin(),"genuine empty root boot");
  const auto first=profile_store.Create(profile,"One",0,0x9001,1);
  require(first.status==ProfileStore::Status::Ok&&first.id==1,"first root commit");
  require(profile_store.Begin()&&!profile_store.IsReadOnlyRecovery()&&profile_store.Generation()==1,"one valid generation-one root is writable");
  require(profile_store.Create(profile,"Two",0,0x9002,2).id==2&&profile_store.Create(profile,"Three",0,0x9003,3).id==3,"three exact IDs committed");
  const auto committed=storage.files;
  const std::string newest="/ultimate-dir-0.bin",older="/ultimate-dir-1.bin";
  auto repair_crc=[](std::vector<uint8_t>& image) {
    uint32_t crc=UINT32_MAX;for(size_t i=0;i<image.size()-4;++i){crc^=image[i];for(unsigned bit=0;bit<8;++bit)crc=(crc>>1)^(0xedb88320u&(0u-(crc&1u)));}crc=~crc;
    for(unsigned i=0;i<4;++i)image[image.size()-4+i]=static_cast<uint8_t>(crc>>(8*i));
  };
  auto frozen=[&]() {
    const auto fault_files=storage.files;const auto durable=config_bytes(persistence.durable);const auto saves=persistence.save_calls;
    const auto generation=profile_store.Generation();const auto count=profile_store.Count();
    require(profile_store.Create(profile,"Forbidden reuse",0,0x9100,1).status!=ProfileStore::Status::Ok,"damaged roots cannot reuse ID3");
    require(profile_store.Update(1,profile,1,0x9101,1).status!=ProfileStore::Status::Ok,"recovery UPDATE refused");
    require(profile_store.Duplicate(1,1,"Forbidden",0,0x9102,1).status!=ProfileStore::Status::Ok,"recovery DUPLICATE refused");
    require(profile_store.Rename(1,"Forbidden",generation,0x9103,1).status!=ProfileStore::Status::Ok,"recovery RENAME refused");
    require(profile_store.Reorder(1,99,generation,0x9104,1).status!=ProfileStore::Status::Ok,"recovery REORDER refused");
    require(profile_store.Delete(1,generation,0,0x9105,1).status!=ProfileStore::Status::Ok,"recovery DELETE refused");
    InputState inputs;DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);
    const auto diagnostic=send(backend,wire,status());
    require(diagnostic.status==PROFILE_STORE_IO_FAILURE&&std::strcmp(diagnostic.diagnostic,"directory.recovery")==0,"STATUS identifies directory recovery");
    require(send(backend,wire,list()).status==(profile_store.IsReady()?PROFILE_STORE_OK:PROFILE_STORE_IO_FAILURE),"LIST exposes only validated recovery directory");
    ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_SET_MODE_REFERENCE;r.expected_store_generation=generation;r.expected_config_generation=persistence.ConfigGeneration(config);r.mode_config_index=1;r.profile_id=0;r.request_token=0x9200;
    require(send(backend,wire,r).status!=PROFILE_STORE_OK,"recovery reference save refused");
    require(storage.files==fault_files&&profile_store.Generation()==generation&&profile_store.Count()==count,"recovery mutations preserve exact files and high water state");
    require(persistence.save_calls==saves&&config_bytes(persistence.durable)==durable&&std::memcmp(&backend._config,&config,sizeof(Config))==0,"recovery reference leaves durable/live Config unchanged");
  };
  storage.files[newest][0]^=1;
  require(profile_store.Begin()&&profile_store.IsReady()&&profile_store.IsReadOnlyRecovery()&&profile_store.Generation()==2&&profile_store.Count()==2,"corrupt newest root permits read-only older generation");
  UltimateProfile readable=UltimateProfile_init_default;require(profile_store.Read(1,readable)==ProfileStore::Status::Ok&&profile_store.Read(3,readable)==ProfileStore::Status::NotFound,"older root remains readable without exposing orphan ID3");frozen();
  storage.files[older][0]^=1;
  require(!profile_store.Begin()&&!profile_store.IsReady()&&profile_store.IsReadOnlyRecovery(),"both present invalid roots fail closed");frozen();
  storage.files=committed;storage.files[older][12]^=2;repair_crc(storage.files[older]);
  require(!profile_store.Begin()&&!profile_store.IsReady()&&profile_store.IsReadOnlyRecovery(),"valid roots with unequal incarnations fail closed");frozen();
  storage.files=committed;storage.files[older]=storage.files[newest];storage.files[older][48]^=1;repair_crc(storage.files[older]);
  require(!profile_store.Begin()&&!profile_store.IsReady()&&profile_store.IsReadOnlyRecovery(),"equal-generation unequal-content valid roots fail closed");frozen();
  storage.files=committed;storage.files.erase(older);
  require(profile_store.Begin()&&profile_store.Generation()==3&&profile_store.IsReadOnlyRecovery(),"single generation-above-one root is conservatively read only");frozen();
  storage.files=committed;require(profile_store.Begin()&&profile_store.Count()==3,"restore committed fixture before absent roots");
  storage.files.clear();require(profile_store.Begin()&&profile_store.IsReady()&&!profile_store.IsReadOnlyRecovery()&&profile_store.Generation()==0&&profile_store.Count()==0&&profile_store.EntryAt(0)==nullptr&&profile_store.ActiveId()==0,"both absent roots clear stale in-memory directory");
  const auto fresh=profile_store.Create(profile,"Genuine empty",0,0x9300,1);require(fresh.status==ProfileStore::Status::Ok&&fresh.id==1,"genuine empty store remains writable");
  std::puts("profile_store_root_corruption_fail_closed=PASS");
}

void deep_create_paths(const char *path, bool drop_response, unsigned scenario) {
  std::ifstream f(path,std::ios::binary);require(bool(f),"fixture open");
  std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)),{});
  pb_istream_t pb=pb_istream_from_buffer(bytes.data(),bytes.size());
  Config config=Config_init_default;require(pb_decode(&pb,Config_fields,&config)&&pb.bytes_left==0,"fixture decode");
  const UltimateProfile profile=config.ultimate_profiles[0];config.ultimate_profiles_count=0;
  config.ultimate_profile_store_format=ProfileStore::kCompactConfigFormat;config.ultimate_profile_store_incarnation=1;
  storage.strict_absent_remove=true;storage.enforce_littlefs_component_limit=true;
  // Cartesian stale-file controls: record temp, orphan destination, root temp,
  // and an invalid inactive root, individually and in every combination.
  for(unsigned mask=scenario;mask==scenario;++mask){
    storage.files.clear();storage.failure=MemoryStorage::Failure::None;storage.directory_failure=MemoryStorage::Failure::None;
    if(!drop_response){
      if(mask&1)storage.files["/ultimate-00000001-00000001.tmp"]={0xde,0xad};
      if(mask&2)storage.files["/ultimate-00000001-00000001.bin"]={0xba,0xd0};
      if(mask&4)storage.files["/ultimate-dir-0.tmp"]={0xfa};
      if(mask&8)storage.files["/ultimate-dir-0.bin"]={0xff};
    }
    if(!drop_response&&(mask&8)){
      const auto corrupt_files=storage.files;
      require(!profile_store.Begin()&&!profile_store.IsReady()&&profile_store.IsReadOnlyRecovery(),"invalid root is corruption, not empty writable store");
      require(profile_store.Create(profile,"Forbidden stale root",0,0xf000+mask,1).status!=ProfileStore::Status::Ok&&storage.files==corrupt_files,"invalid-root stale combinations refuse mutation");
      storage.files.erase("/ultimate-dir-0.bin"); // Remove only injected corruption, retaining orphan/temp controls.
    }
    require(profile_store.Begin()&&profile_store.Count()==0&&profile_store.Generation()==0&&!profile_store.IsReadOnlyRecovery(),"stale non-root files are not a committed root");
    InputState inputs;DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);
    const unsigned operations=drop_response?1:32;
    for(unsigned step=0;step<operations;++step){
      ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_CREATE;
      r.expected_store_generation=profile_store.Generation();r.has_profile=true;r.profile=profile;
      std::snprintf(r.name,sizeof(r.name),"Create %u",step);r.display_rank=step;r.request_token=0x8000+step;
      const uint32_t before=profile_store.Generation();
      if(!drop_response&&mask==0&&step>1&&step<9){
        const auto active_slot=std::string("/ultimate-dir-")+std::to_string((profile_store.Generation()+1)&1u)+".bin";
        const auto active_bytes=storage.files.at(active_slot);
        const auto before_failure_files=storage.files;
        storage.directory_failure=static_cast<MemoryStorage::Failure>(step-1);
        const auto failed=send(backend,wire,r);
        require(failed.status==PROFILE_STORE_COMMIT_UNKNOWN&&failed.profile_id==step+1,"rotating inactive-root publication failure");
        require(storage.files.at(active_slot)==active_bytes,"failed publication preserves exact active root");
        storage.directory_failure=MemoryStorage::Failure::None;
        require(profile_store.Begin()&&profile_store.Generation()==before&&profile_store.Count()==step,"failed inactive publication reloads active root");
        UltimateProfile orphan=UltimateProfile_init_default;require(profile_store.Read(step+1,orphan)==ProfileStore::Status::NotFound,"orphan record is invisible");
        if(profile_store.IsReadOnlyRecovery()){
          const auto fault_files=storage.files;
          require(profile_store.Create(profile,"Forbidden incomplete roots",0,0xf100+step,1).status!=ProfileStore::Status::Ok&&storage.files==fault_files,"ambiguous missing root refuses new IDs");
          // Restore exact pre-fault fixture roots so later independent injected
          // failure cases continue from an authenticated two-root snapshot.
          for(const auto &name:{std::string("/ultimate-dir-0.bin"),std::string("/ultimate-dir-1.bin")}){
            const auto found=before_failure_files.find(name);if(found==before_failure_files.end())storage.files.erase(name);else storage.files[name]=found->second;
          }
          require(profile_store.Begin()&&!profile_store.IsReadOnlyRecovery()&&profile_store.Generation()==before&&profile_store.Count()==step,"fixture root restoration preserves committed state");
        }
      }
      if(drop_response){wire.tx_budget=mask==0?0:(mask==1?1:7);wire.advertise_full_fifo=mask==3;const uint32_t started=host_millis;wire.append(frame(r));backend.SendReport();require(wire.remaining()==0,"bounded TX request consumed");require(wire.tx.size()<=7,"bounded response sink");require(host_millis-started==2000,"TX deadline bounded at 2000 ms");}
      else{const auto made=send(backend,wire,r);require(made.status==PROFILE_STORE_OK&&made.profile_id==step+1&&made.request_token==r.request_token&&made.store_generation==before+1,"successful CREATE response");}
      require(profile_store.Count()==step+1&&profile_store.Generation()==before+1,"CREATE commits before response");
      const std::string active=std::string("/ultimate-dir-")+std::to_string((profile_store.Generation()+1)&1u)+".bin";
      require(storage.files.at(active).size()==2620,"complete root wire size");
      // Begin rereads committed roots; it must select the newest alternating slot.
      require(profile_store.Begin()&&profile_store.Count()==step+1&&profile_store.Generation()==before+1,"rotating roots survive reload");
      UltimateProfile restored=UltimateProfile_init_default;
      require(profile_store.Read(step+1,restored)==ProfileStore::Status::Ok&&std::memcmp(&restored,&profile,sizeof(profile))==0,"committed profile readback");
      if(drop_response){
        DuplexStream recovery;ConfiguratorBackend reboot(inputs,nullptr,0,config,recovery);
        ProfileStoreRequest query=ProfileStoreRequest_init_default;query.protocol_version=1;query.operation=PROFILE_STORE_QUERY_TRANSACTION;
        query.expected_store_generation=profile_store.Generation();query.request_token=r.request_token;
        const auto result=send(reboot,recovery,query);require(result.status==PROFILE_STORE_OK&&result.profile_id==1&&result.profile_revision==1,"lost successful response recovered by transaction query");
        wire.tx_budget=SIZE_MAX;wire.clear();
        if(scenario%2==0){
          DuplexStream command_wire;packetio::COBSPrint command_packet(command_wire);
          command_packet.write(static_cast<uint8_t>(CMD_GET_DEVICE_INFO));require(command_packet.end(),"device info command frame");
          wire.append(command_wire.tx);
        }else wire.append(frame(status()));
        backend.SendReport();
        // Legacy GET_DEVICE_INFO retains its lazy EOP drain lifecycle.
        if(scenario%2==0&&wire.remaining()!=0)backend.SendReport();
        require(wire.remaining()==0&&!wire.tx.empty()&&wire.tx[0]==0,"same-transport recovery delimits failed response prefix");
        wire.tx.erase(wire.tx.begin());
        if(scenario%2==0){const auto info=decode(wire.tx);require(!info.empty()&&info[0]==CMD_SET_DEVICE_INFO,"legacy device-info response resynchronizes after partial CREATE TX");}
        else require(response(wire).status==PROFILE_STORE_OK,"profile response resynchronizes after partial CREATE TX");
        const auto observed=send(backend,wire,status());
        require(observed.status==PROFILE_STORE_OK&&observed.store_generation==before+1&&observed.diagnostic[0]==0,"STATUS retains actual generation after bounded TX failure");
        const auto repeated=send(backend,wire,query);
        require(repeated.status==PROFILE_STORE_OK&&repeated.profile_id==1&&profile_store.Count()==1,"same-transport QUERY_TRANSACTION recovers without duplicate commit");
        r.expected_store_generation=profile_store.Generation();++r.request_token;
        const auto next=send(backend,wire,r);
        require(next.status==PROFILE_STORE_OK&&next.profile_id==2,"later CREATE completes after failed response");
        const auto complete=send(backend,wire,status());
        require(complete.status==PROFILE_STORE_OK&&complete.diagnostic[0]==0,"completed CREATE leaves clean STATUS");
      }
    }
  }
  std::puts(drop_response?"profile_store_successful_commit_tx_failure=PASS":"profile_store_stale_files_root_rotation=PASS");
}
} // namespace
ProfileStore profile_store(&storage);
int main(int argc,char**argv) { try { require(argc==2||argc==3,"usage");malformed_cobs_controls();if(argc==3){if(std::strcmp(argv[2],"--root-faults")==0){root_fault_recovery(argv[1]);return 0;}if(std::strcmp(argv[2],"--reference-purity")==0){reference_purity(argv[1]);return 0;}if(std::strcmp(argv[2],"--direct-create-replay")==0){direct_create_replay(argv[1]);return 0;}if(std::strcmp(argv[2],"--old-valid-record")==0){stale_valid_readback(argv[1],false);return 0;}if(std::strcmp(argv[2],"--old-valid-directory")==0){stale_valid_readback(argv[1],true);return 0;}if(std::strncmp(argv[2],"--deep-create-",14)==0){deep_create_paths(argv[1],false,static_cast<unsigned>(std::stoul(argv[2]+14)));return 0;}if(std::strncmp(argv[2],"--drop-create-response-",22)==0){deep_create_paths(argv[1],true,static_cast<unsigned>(std::stoul(argv[2]+22)));return 0;}if(std::strcmp(argv[2],"--path-limit-import")==0)path_limited_import(argv[1]);else if(std::strncmp(argv[2],"--directory-",12)==0)directory_failure_from_empty(argv[1],argv[2]);else first_create_from_empty(argv[1],argv[2]);return 0;}InputState inputs;Config config=Config_init_default;seed(argv[1],&config);
#ifndef EXPECT_DUPLICATE_NEXT_DROP
const Config baseline=config;
#endif
DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);consecutive_lists(backend,wire);
#ifndef EXPECT_DUPLICATE_NEXT_DROP
crud_probe(backend,wire);
timeout_and_cap(backend,wire,baseline);
#endif
return 0;}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;} }
