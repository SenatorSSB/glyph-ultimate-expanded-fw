#include "host_stubs.hpp"
#include "core/Persistence.hpp"
#include "core/ProfileStore.hpp"
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
  std::map<std::string, std::vector<uint8_t>> files;
  bool Write(const char *p, const uint8_t *b, size_t n) override { files[p] = {b, b + n}; return true; }
  bool Read(const char *p, uint8_t *b, size_t n) override { auto i=files.find(p); if(i==files.end()||i->second.size()!=n)return false; std::memcpy(b,i->second.data(),n);return true; }
  size_t Size(const char *p) override { auto i=files.find(p);return i==files.end()?0:i->second.size(); }
  bool Exists(const char *p) override { return files.find(p)!=files.end(); }
  bool Remove(const char *p) override { files.erase(p);return true; }
  bool Rename(const char *a,const char *b) override { auto i=files.find(a);if(i==files.end())return false;files[b]=i->second;files.erase(i);return true; }
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
} // namespace
ProfileStore profile_store(&storage);
int main(int argc,char**argv) { try { require(argc==2,"usage");InputState inputs;Config config=Config_init_default;seed(argv[1],&config);
#ifndef EXPECT_DUPLICATE_NEXT_DROP
const Config baseline=config;
#endif
DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);consecutive_lists(backend,wire);
#ifndef EXPECT_DUPLICATE_NEXT_DROP
crud_probe(backend,wire);
timeout_and_cap(backend,wire,baseline);
#endif
return 0;}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;} }
