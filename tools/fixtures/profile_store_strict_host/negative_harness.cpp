// Actual frozen production f7ba82d4 source is compiled separately by the checker.
// These controls intentionally demonstrate the four former acceptance defects.
#include "core/ProfileStore.hpp"
#include <pb_decode.h>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
using Bytes=std::vector<uint8_t>;
namespace {
void require(bool v,const char*m){if(!v)throw std::runtime_error(m);}
struct Memory:ProfileStoreStorage{
 std::map<std::string,Bytes> files;
 uint64_t charge(size_t n)const{return ((n+4*((n+4095)/4096+1)+4095)/4096)*4096;}
 uint64_t used()const{uint64_t total=8192;for(const auto&e:files)total+=charge(e.second.size());return total;}
 bool Write(const char*p,const uint8_t*b,size_t n)override{const auto old=files.count(p)?charge(files.at(p).size()):0;if(used()-old+charge(n)>524288)return false;files[p]=Bytes(b,b+n);return true;}
 bool Read(const char*p,uint8_t*b,size_t n)override{auto i=files.find(p);if(i==files.end()||i->second.size()!=n)return false;std::memcpy(b,i->second.data(),n);return true;}
 size_t Size(const char*p)override{return files.count(p)?files.at(p).size():0;}
 bool Exists(const char*p)override{return files.count(p);}
 bool Remove(const char*p)override{files.erase(p);return true;}
 bool Rename(const char*a,const char*b)override{auto i=files.find(a);if(i==files.end())return false;files[b]=std::move(i->second);files.erase(i);return true;}
};
Config legacy;
}
int main(int argc,char**argv){try{require(argc==2,"fixture");std::ifstream input(argv[1],std::ios::binary);Bytes b((std::istreambuf_iterator<char>(input)),{});auto stream=pb_istream_from_buffer(b.data(),b.size());require(pb_decode(&stream,Config_fields,&legacy)&&legacy.ultimate_profiles_count==2,"fixture decode");
 {Memory m;ProfileStore s(&m);require(s.Begin(),"empty");size_t filler=524288-8192-24576-8;m.files["/foreign"]=Bytes(filler);require(524288-m.used()==20480,"bounded nearreserve geometry");auto result=s.Create(legacy.ultimate_profiles[0],"nearreserve",0,1,1);require(result.status==ProfileStore::Status::Ok&&524288-m.used()<16384,"old countonly destroys reserve");std::puts("frozen_negative_count_only=DETECTED");}
 {Memory m;ProfileStore s(&m);require(s.Begin()&&s.Create(legacy.ultimate_profiles[0],"one",0,1,1).id==1&&s.Create(legacy.ultimate_profiles[0],"two",0,2,2).id==2,"issued1and2");m.files.erase("/ultimate-dir-1.bin");require(s.Begin()&&!s.IsReadOnlyRecovery(),"old lonegen1 accepted");auto result=s.Create(legacy.ultimate_profiles[0],"reissued",0,3,3);require(result.status==ProfileStore::Status::Ok&&result.id==2,"old stableID reissued");std::puts("frozen_negative_lone_generation1_reuse=DETECTED");}
 {Memory m;ProfileStore s(&m);uint32_t mapping[2]{};require(s.Begin()&&s.ImportLegacy(legacy,mapping,2)==ProfileStore::Status::Ok,"old migration");auto generation=s.Generation();Config changed=legacy;changed.rgb_brightness^=1;changed.ultimate_profiles[0]=legacy.ultimate_profiles[1];uint32_t retry[2]{};require(s.ImportLegacy(changed,retry,2)==ProfileStore::Status::MigrationFenced&&mapping[0]==retry[0]&&mapping[1]==retry[1]&&s.Generation()==generation,"old changedsource inheritsreceipt");std::puts("frozen_negative_changed_migration_retry=DETECTED");}
 {Memory m;ProfileStore s(&m);const std::string name(32,'x');require(s.Begin()&&s.Create(legacy.ultimate_profiles[0],name.c_str(),0,1,1).status==ProfileStore::Status::Ok,"old name accepted");require(std::strlen(s.EntryAt(0)->name)==17,"old32byte name silentlytruncated");std::puts("frozen_negative_32byte_name_truncation=DETECTED");}
 std::puts("frozen_production_negative_controls=4 source=f7ba82d4");return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
