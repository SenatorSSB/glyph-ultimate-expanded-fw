#include "core/CheckedStorage.hpp"
#include <lfs.h>
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
using namespace CheckedStorage;
namespace {
lfs_t fs{}; lfs_config cfg{};
std::vector<uint8_t> flash(4096*128,0xff);
Kind selected_kind; Operation selected_operation; Phase selected_phase; Fault selected_fault; bool enabled=false;
unsigned calls=0; bool native_sync_failure=false;
Fault hook(Kind k,Operation o,Phase p,const char *) { if(enabled&&k==selected_kind&&o==selected_operation&&p==selected_phase){++calls;return selected_fault;}return Fault::None; }
void require(bool v,const char *m){if(!v)throw std::runtime_error(m);}
int rd(const lfs_config *,lfs_block_t b,lfs_off_t o,void *p,lfs_size_t n){std::memcpy(p,flash.data()+b*4096+o,n);return 0;}
int pg(const lfs_config *,lfs_block_t b,lfs_off_t o,const void *p,lfs_size_t n){auto *d=flash.data()+b*4096+o;auto *s=static_cast<const uint8_t *>(p);for(size_t i=0;i<n;++i){if((d[i]&s[i])!=s[i])return LFS_ERR_CORRUPT;d[i]&=s[i];}return 0;}
int er(const lfs_config *,lfs_block_t b){std::fill_n(flash.data()+b*4096,4096,0xff);return 0;}
int sy(const lfs_config *){return native_sync_failure?LFS_ERR_IO:0;}
void inject(Kind k,Operation o,Phase p,Fault f){selected_kind=k;selected_operation=o;selected_phase=p;selected_fault=f;enabled=true;calls=0;}
bool old_unchecked(const char *path,const uint8_t *bytes,size_t n,Kind kind){File f;auto o=Open(f,path,true,kind);if(!o)return false;bool wrote=bool(Write(f,bytes,n));Close(f);return wrote;}
}
lfs_t *CheckedStorageTestMount(){return &fs;}
int main(){try{
 cfg.read=rd;cfg.prog=pg;cfg.erase=er;cfg.sync=sy;cfg.read_size=256;cfg.prog_size=256;cfg.block_size=4096;cfg.block_count=128;cfg.cache_size=256;cfg.lookahead_size=256;cfg.block_cycles=16;
 require(lfs_format(&fs,&cfg)==0&&lfs_mount(&fs,&cfg)==0,"mount");
 SetFaultHook(hook);std::array<uint8_t,4097> bytes{},readback{};for(size_t i=0;i<bytes.size();++i)bytes[i]=i*37;
 unsigned faults=0,negative_controls=0;
 for(auto kind:{Kind::Record,Kind::Root,Kind::Config}){
  for(auto op:{Operation::OpenWrite,Operation::Write,Operation::Sync,Operation::Close})for(auto phase:{Phase::Before,Phase::After}){
   inject(kind,op,phase,phase==Phase::Before?Fault::Fail:Fault::LostAcknowledgement);
   auto r=WriteFile("/stage",bytes.data(),bytes.size(),kind);
   require(!r&&calls==1,"checked write catches every named boundary");++faults;
   enabled=false;require(bool(Remove("/stage",kind)),"cleanup");
  }
  for(auto phase:{Phase::Before,Phase::After}){
   enabled=false;require(bool(WriteFile("/stage",bytes.data(),bytes.size(),kind)),"write stage");
   inject(kind,Operation::Rename,phase,Fault::LostAcknowledgement);auto r=Rename("/stage","/published",kind);
   require(r.outcome==Outcome::Uncertain,"rename unknown never clean failure");enabled=false;
   if(phase==Phase::After)require(bool(ReadFile("/published",readback.data(),readback.size(),kind))&&bytes==readback,"lost rename ack really committed");
   else require(Stat("/published",nullptr,kind).outcome==Outcome::NotFound,"pre rename no publication");
   Remove("/published",kind);Remove("/stage",kind);++faults;
  }
  enabled=false;require(bool(WriteFile("/stable",bytes.data(),bytes.size(),kind)),"stable seed");
  for(auto op:{Operation::OpenRead,Operation::Stat,Operation::Read,Operation::Close})for(auto phase:{Phase::Before,Phase::After}){
   inject(kind,op,phase,Fault::Fail);require(!ReadFile("/stable",readback.data(),readback.size(),kind)&&calls==1,"checked read boundaries");++faults;
  }
  enabled=false;require(bool(ReadFile("/stable",readback.data(),readback.size(),kind))&&bytes==readback,"exact read");
  inject(kind,Operation::Close,Phase::After,Fault::Fail);require(old_unchecked("/old",bytes.data(),bytes.size(),kind),"old wrapper negative control incorrectly succeeds");++negative_controls;
  require(!WriteFile("/new",bytes.data(),bytes.size(),kind),"checked equivalent refuses close failure");
  enabled=false;Remove("/stable",kind);Remove("/old",kind);Remove("/new",kind);
 }
 enabled=false;require(bool(WriteFile("/native-new",bytes.data(),bytes.size(),Kind::Config))&&bool(WriteFile("/native-old",bytes.data(),bytes.size(),Kind::Config)),"native sync seeds");
 native_sync_failure=true;
 auto native=WriteFile("/native-new",bytes.data(),bytes.size(),Kind::Config);
 require(!native&&native.error==LFS_ERR_IO,"native LittleFS sync error surfaced");
 require(old_unchecked("/native-old",bytes.data(),bytes.size(),Kind::Config),"actual old wrapper drops native close sync error");++negative_controls;
 native_sync_failure=false;Remove("/native-new");Remove("/native-old");
 Geometry geometry{};require(bool(Capacity(geometry))&&geometry.total_bytes==524288&&geometry.erase_bytes==4096&&geometry.program_bytes==256&&geometry.used_bytes+geometry.free_bytes==geometry.total_bytes,"measured geometry");
 inject(Kind::Root,Operation::Capacity,Phase::Before,Fault::Fail);require(!Capacity(geometry),"capacity error observable");enabled=false;
 require(bool(WriteFile("/enumerated",bytes.data(),10,Kind::Record)),"enum seed");
 unsigned count=0;require(bool(Enumerate("/",[](void *p,const Entry&e){++*static_cast<unsigned *>(p);return std::strcmp(e.name,"enumerated")==0&&e.bytes==10;},&count))&&count==1,"enumerate bounded checked callback");
 inject(Kind::Root,Operation::Enumerate,Phase::After,Fault::Fail);require(!Enumerate("/",[](void*,const Entry&){return true;},nullptr),"enumeration failure checked");enabled=false;
 inject(Kind::Record,Operation::Remove,Phase::After,Fault::LostAcknowledgement);require(Remove("/enumerated").outcome==Outcome::Uncertain,"remove lost ack uncertain");enabled=false;
 require(Stat("/enumerated").outcome==Outcome::NotFound&&bool(Remove("/enumerated")),"checked absence/idempotent removal");
 require(lfs_unmount(&fs)==0&&lfs_mount(&fs,&cfg)==0,"remount");require(bool(Capacity(geometry)),"geometry after remount");require(lfs_unmount(&fs)==0,"end");
 std::printf("checked_storage_production_primitive=PASS fault_cases=%u old_unchecked_negative_controls=%u same_engine=true ram_only=true\n",faults,negative_controls);return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
