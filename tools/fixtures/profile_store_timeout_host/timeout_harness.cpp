#include "host_stubs.hpp"
#include "core/Persistence.hpp"
#include "core/ProfileStore.hpp"
#include "core/ProfileStorePaths.hpp"
#include "core/ProfileStoreStorage.hpp"
#include <pb_decode.h>
#include <pb_encode.h>
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
  enum class Failure { None, TempOpenWrite, TempWrite, TempRead, Verify, DestRemove, Rename };
  std::map<std::string, std::vector<uint8_t>> files;
  bool strict_absent_remove = false;
  bool enforce_littlefs_component_limit = false;
  Failure failure = Failure::None;
  ProfileStoreIoStage last_failure = ProfileStoreIoStage::None;
  bool PathValid(const char *path) const { for (const char *component=path; component; ) { if (*component=='/') ++component; const char *slash=std::strchr(component,'/'); const size_t length=slash?static_cast<size_t>(slash-component):std::strlen(component); if(length>=32)return false; if(!slash)break; component=slash; } return true; }
  bool Write(const char *p, const uint8_t *b, size_t n) override { last_failure=ProfileStoreIoStage::None;if(enforce_littlefs_component_limit&&!PathValid(p)){last_failure=ProfileStoreIoStage::RecordTempOpenWrite;return false;}if(failure==Failure::TempOpenWrite){last_failure=ProfileStoreIoStage::RecordTempOpenWrite;return false;}if(failure==Failure::TempWrite){last_failure=ProfileStoreIoStage::RecordTempWrite;return false;}files[p] = {b, b + n}; return true; }
  bool Read(const char *p, uint8_t *b, size_t n) override { last_failure=ProfileStoreIoStage::None;if(failure==Failure::TempRead){last_failure=ProfileStoreIoStage::RecordTempRead;return false;}auto i=files.find(p); if(i==files.end()||i->second.size()!=n)return false; std::memcpy(b,i->second.data(),n);if(failure==Failure::Verify)b[0]^=1;return true; }
  size_t Size(const char *p) override { auto i=files.find(p);return i==files.end()?0:i->second.size(); }
  bool Exists(const char *p) override { return files.find(p)!=files.end(); }
  ProfileStoreIoStage LastFailureStage() const override { return last_failure; }
  bool Remove(const char *p) override { auto i=files.find(p);if(i==files.end())return !strict_absent_remove;if(failure==Failure::DestRemove)return false;files.erase(i);return true; }
  bool Rename(const char *a,const char *b) override { if(enforce_littlefs_component_limit&&(!PathValid(a)||!PathValid(b)))return false;if(failure==Failure::Rename)return false;auto i=files.find(a);if(i==files.end())return false;files[b]=i->second;files.erase(i);return true; }
};
MemoryStorage storage;
void require(bool ok, const char *m) { if (!ok) throw std::runtime_error(m); }
class DuplexStream final : public Stream {
 public:
  std::vector<uint8_t> rx, tx; size_t pos=0;
  int available() override { return static_cast<int>(rx.size()-pos); }
  int read() override { return pos<rx.size()?rx[pos++]:-1; }
  int peek() override { return pos<rx.size()?rx[pos]:-1; }
  void flush() override {}
  size_t write(uint8_t b) override { tx.push_back(b);return 1; }
  size_t write(const uint8_t *b,size_t n) override { tx.insert(tx.end(),b,b+n);return n; }
  void append(const std::vector<uint8_t>& b){rx.insert(rx.end(),b.begin(),b.end());}
  size_t remaining()const{return rx.size()-pos;} void clear(){tx.clear();}
};
std::vector<uint8_t> decode(const std::vector<uint8_t>& in) {
  require(!in.empty()&&in.back()==0,"COBS delimiter");std::vector<uint8_t> out;
  for(size_t o=0;o+1<in.size();) { uint8_t c=in[o++];require(c&&o+c-1<=in.size(),"COBS valid");out.insert(out.end(),in.begin()+o,in.begin()+o+c-1);o+=c-1;if(c!=0xff&&o+1<in.size())out.push_back(0); } return out;
}
std::vector<uint8_t> frame(const ProfileStoreRequest& request) {
  size_t n=0;require(pb_get_encoded_size(&n,ProfileStoreRequest_fields,&request),"request size");std::vector<uint8_t> data(n);pb_ostream_t pb=pb_ostream_from_buffer(data.data(),data.size());require(pb_encode(&pb,ProfileStoreRequest_fields,&request),"request encode");data.resize(pb.bytes_written);
  DuplexStream wire;packetio::COBSPrint out(wire);out.write(static_cast<uint8_t>(CMD_PROFILE_STORE));out.write(data.data(),data.size());require(out.end(),"real COBS end");require(wire.tx.back()==0,"request delimiter");return wire.tx;
}
ProfileStoreResponse response(const DuplexStream& wire) {
  const auto data=decode(wire.tx);require(!data.empty()&&data[0]==CMD_PROFILE_STORE,"response command");ProfileStoreResponse r=ProfileStoreResponse_init_default;pb_istream_t pb=pb_istream_from_buffer(data.data()+1,data.size()-1);require(pb_decode(&pb,ProfileStoreResponse_fields,&r)&&pb.bytes_left==0,"response decode");return r;
}
void seed(const char* path,Config* config) {
  std::ifstream f(path,std::ios::binary);require(bool(f),"fixture open");std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)),{});pb_istream_t pb=pb_istream_from_buffer(bytes.data(),bytes.size());*config=Config_init_default;require(pb_decode(&pb,Config_fields,config)&&pb.bytes_left==0&&config->ultimate_profiles_count==2,"two real fixture profiles");
  require(profile_store.Begin(),"ProfileStore begin");uint32_t ids[2]={};require(profile_store.ImportLegacy(*config,ids,2)==ProfileStore::Status::Ok&&ids[0]&&ids[1],"ProfileStore import");Config compact=*config;compact.ultimate_profiles_count=0;compact.ultimate_profile_store_format=ProfileStore::kCompactConfigFormat;compact.ultimate_profile_store_incarnation=profile_store.Incarnation();require(profile_store.CompleteMigration(compact)==ProfileStore::Status::Ok&&profile_store.Count()==2,"ProfileStore ready");*config=compact;
}
ProfileStoreRequest list() { ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_LIST;r.page_size=8;r.request_token=0x51;return r; }
ProfileStoreRequest status() { ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_STATUS;r.request_token=0x52;return r; }
void expect_list(const DuplexStream& wire) { const auto r=response(wire);require(r.status==PROFILE_STORE_OK&&r.entries_count==2&&r.next_page_cursor==0,"LIST result");require(r.entries[0].profile_id&&r.entries[1].profile_id&&r.entries[0].profile_id!=r.entries[1].profile_id,"two listed profiles"); }
void expect_status(const DuplexStream& wire) { require(response(wire).status==PROFILE_STORE_OK,"STATUS result"); }
ProfileStoreResponse send(ConfiguratorBackend& b,DuplexStream& wire,const ProfileStoreRequest& r) { wire.clear();wire.append(frame(r));b.SendReport();require(wire.remaining()==0,"CRUD request tail");return response(wire); }
void crud_probe(ConfiguratorBackend& b,DuplexStream& wire) {
  UltimateProfile profile=UltimateProfile_init_default;require(profile_store.Read(profile_store.EntryAt(0)->id,profile)==ProfileStore::Status::Ok,"read seeded profile");
  ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_CREATE;r.expected_store_generation=profile_store.Generation();r.has_profile=true;r.profile=profile;std::strcpy(r.name,"Config create");r.display_rank=9;r.request_token=0x101;const auto made=send(b,wire,r);require(made.status==PROFILE_STORE_OK&&made.profile_id!=0,"CREATE");const uint32_t id=made.profile_id;
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_READ;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.request_token=0x102;const auto read=send(b,wire,r);require(read.status==PROFILE_STORE_OK&&read.profile_id==id&&read.has_profile,"READ persisted CREATE");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_UPDATE;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.expected_profile_revision=read.profile_revision;r.has_profile=true;r.profile=profile;r.request_token=0x103;const auto updated=send(b,wire,r);require(updated.status==PROFILE_STORE_OK&&updated.profile_id==id&&updated.profile_revision==read.profile_revision+1,"UPDATE stable identity");
  const uint32_t stale=profile_store.Generation();r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_RENAME;r.expected_store_generation=stale;r.profile_id=id;std::strcpy(r.name,"Renamed");r.request_token=0x104;require(send(b,wire,r).status==PROFILE_STORE_OK,"RENAME");r.expected_store_generation=stale;r.request_token=0x105;require(send(b,wire,r).status==PROFILE_STORE_CONFLICT,"generation CONFLICT");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_REORDER;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.display_rank=44;r.request_token=0x106;require(send(b,wire,r).status==PROFILE_STORE_OK,"REORDER");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_DUPLICATE;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.expected_profile_revision=updated.profile_revision;std::strcpy(r.name,"Copy");r.display_rank=45;r.request_token=0x107;const auto copy=send(b,wire,r);require(copy.status==PROFILE_STORE_OK&&copy.profile_id!=id,"DUPLICATE");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_READ;r.expected_store_generation=profile_store.Generation();r.profile_id=999999;r.request_token=0x108;require(send(b,wire,r).status==PROFILE_STORE_NOT_FOUND,"READ missing ID");
  size_t ultimate=0;while(ultimate<b._config.game_mode_configs_count&&b._config.game_mode_configs[ultimate].mode_id!=MODE_ULTIMATE)++ultimate;require(ultimate<b._config.game_mode_configs_count,"Ultimate mode for reference");r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_SET_MODE_REFERENCE;r.expected_store_generation=profile_store.Generation();r.expected_config_generation=persistence.ConfigGeneration(b._config);r.mode_config_index=ultimate;r.profile_id=id;r.request_token=0x109;require(send(b,wire,r).status==PROFILE_STORE_OK,"SET_MODE_REFERENCE");
  b._config.game_mode_configs[ultimate].ultimate_profile_id=id;r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_DELETE;r.expected_store_generation=profile_store.Generation();r.profile_id=id;r.request_token=0x10a;require(send(b,wire,r).status==PROFILE_STORE_REFERENCED,"DELETE referenced refusal");b._config.game_mode_configs[ultimate].ultimate_profile_id=0;
  r.expected_store_generation=profile_store.Generation();r.profile_id=copy.profile_id;r.request_token=0x10b;require(send(b,wire,r).status==PROFILE_STORE_OK,"DELETE legal duplicate");
  r=ProfileStoreRequest_init_default;r.protocol_version=1;r.operation=PROFILE_STORE_QUERY_TRANSACTION;r.expected_store_generation=profile_store.Generation();r.request_token=0x10b;require(send(b,wire,r).status==PROFILE_STORE_OK,"QUERY_TRANSACTION");
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
  const uint32_t generation=profile_store.Generation();wire.clear();wire.append({3,static_cast<uint8_t>(CMD_PROFILE_STORE),0x08});b.SendReport();const auto timeout=decode(wire.tx);require(timeout.size()==1+std::strlen("Profile store frame timeout")&&timeout[0]==CMD_ERROR,"timeout error");require(host_millis>=5000&&std::memcmp(&baseline,&b._config,sizeof(Config))==0&&profile_store.Generation()==generation,"timeout state preserved");
  const auto valid=frame(status());wire.clear();wire.append(valid);b.SendReport();require(wire.tx.empty(),"no delimiter rejects following STATUS");wire.clear();wire.append(valid);b.SendReport();expect_status(wire);
  DuplexStream oversized;packetio::COBSPrint out(oversized);out.write(static_cast<uint8_t>(CMD_PROFILE_STORE));std::vector<uint8_t> body(8192,0x55);out.write(body.data(),body.size());require(out.end(),"oversized COBS end");wire.clear();wire.append(oversized.tx);b.SendReport();const auto cap=decode(wire.tx);require(cap.size()==30&&cap[0]==CMD_ERROR&&profile_store.Generation()==generation,"8192 cap bounded failure");wire.clear();wire.append(valid);b.SendReport();expect_status(wire);
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
} // namespace
ProfileStore profile_store(&storage);
int main(int argc,char**argv) { try { require(argc==2||argc==3,"usage");if(argc==3){if(std::strcmp(argv[2],"--path-limit-import")==0)path_limited_import(argv[1]);else first_create_from_empty(argv[1],argv[2]);return 0;}InputState inputs;Config config=Config_init_default;seed(argv[1],&config);
#ifndef EXPECT_DUPLICATE_NEXT_DROP
const Config baseline=config;
#endif
DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);consecutive_lists(backend,wire);
#ifndef EXPECT_DUPLICATE_NEXT_DROP
crud_probe(backend,wire);
timeout_and_cap(backend,wire,baseline);
#endif
return 0;}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;} }
