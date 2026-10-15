// Real pinned LittleFS C engine, RAM NOR model, and production commit primitive.
// Deliberately excludes Arduino FS wrappers, interrupts, multicore and hardware.
#include "core/ProfileStoreAtomicCommit.hpp"
#include "core/ProfileStorePaths.hpp"
extern "C" {
#include "lfs.h"
}
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>

namespace {
void require(bool ok, const char *message) { if (!ok) throw std::runtime_error(message); }
constexpr size_t kBlockSize=4096, kBlocks=128; // production 512 KiB partition
struct RamFlash {
  std::vector<uint8_t> bytes=std::vector<uint8_t>(kBlockSize*kBlocks,0xff);
  static bool valid(lfs_block_t block,lfs_off_t off,lfs_size_t n) { return block<kBlocks&&off<=kBlockSize&&n<=kBlockSize-off; }
  static int read(const lfs_config *c,lfs_block_t b,lfs_off_t o,void *out,lfs_size_t n) {
    if(!valid(b,o,n)||o%256||n%256)return LFS_ERR_IO;
    const auto &self=*static_cast<RamFlash *>(c->context);std::memcpy(out,self.bytes.data()+b*kBlockSize+o,n);return 0;
  }
  static int prog(const lfs_config *c,lfs_block_t b,lfs_off_t o,const void *in,lfs_size_t n) {
    if(!valid(b,o,n)||o%256||n%256)return LFS_ERR_IO;
    auto &self=*static_cast<RamFlash *>(c->context);auto *dst=self.bytes.data()+b*kBlockSize+o;const auto *src=static_cast<const uint8_t *>(in);
    for(size_t i=0;i<n;++i)if((dst[i]&src[i])!=src[i])return LFS_ERR_CORRUPT;
    for(size_t i=0;i<n;++i)dst[i]&=src[i];return 0;
  }
  static int erase(const lfs_config *c,lfs_block_t b) {if(b>=kBlocks)return LFS_ERR_IO;auto &self=*static_cast<RamFlash *>(c->context);std::fill_n(self.bytes.data()+b*kBlockSize,kBlockSize,0xff);return 0;}
  static int sync(const lfs_config *) {return 0;}
};
struct Storage final : ProfileStoreStorage {
  RamFlash flash;lfs_t fs{};lfs_config cfg{};
  bool verified=false;unsigned removes=0,renames=0;bool checking=false;
  Storage(){cfg.context=&flash;cfg.read=RamFlash::read;cfg.prog=RamFlash::prog;cfg.erase=RamFlash::erase;cfg.sync=RamFlash::sync;cfg.read_size=256;cfg.prog_size=256;cfg.block_size=kBlockSize;cfg.block_count=kBlocks;cfg.block_cycles=16;cfg.cache_size=256;cfg.lookahead_size=256;require(lfs_format(&fs,&cfg)==0&&lfs_mount(&fs,&cfg)==0,"format/mount");}
  ~Storage() override {lfs_unmount(&fs);}
  bool Write(const char *p,const uint8_t *bytes,size_t n) override {
    verified=false;lfs_file_t f{};if(lfs_file_open(&fs,&f,p,LFS_O_RDWR|LFS_O_CREAT|LFS_O_TRUNC))return false;
    const auto written=lfs_file_write(&fs,&f,bytes,n);const int closed=lfs_file_close(&fs,&f);return written==static_cast<lfs_ssize_t>(n)&&closed==0;
  }
  bool Read(const char *p,uint8_t *bytes,size_t n) override {
    lfs_file_t f{};if(lfs_file_open(&fs,&f,p,LFS_O_RDONLY))return false;
    const bool sized=lfs_file_size(&fs,&f)==static_cast<lfs_soff_t>(n);const auto got=sized?lfs_file_read(&fs,&f,bytes,n):-1;
    return lfs_file_close(&fs,&f)==0&&got==static_cast<lfs_ssize_t>(n);
  }
  size_t Size(const char *p) override {lfs_info info{};return lfs_stat(&fs,p,&info)==0?info.size:0;}
  bool Exists(const char *p) override {lfs_info info{};return lfs_stat(&fs,p,&info)==0;}
  bool Remove(const char *p) override {if(checking)require(verified,"remove before readback/validation");++removes;return lfs_remove(&fs,p)==0;}
  bool Rename(const char *a,const char *b) override {if(checking)require(verified,"rename before readback/validation");++renames;return lfs_rename(&fs,a,b)==0;}
  void remount(){require(lfs_unmount(&fs)==0,"unmount");fs={};require(lfs_mount(&fs,&cfg)==0,"remount");}
};
struct Expected {Storage *storage;const std::vector<uint8_t> *bytes;bool reject=false;};
bool validate(void *context,const uint8_t *bytes,size_t n){auto &expected=*static_cast<Expected *>(context);const bool ok=!expected.reject&&n==expected.bytes->size()&&std::memcmp(bytes,expected.bytes->data(),n)==0;expected.storage->verified=ok;return ok;}
void exercise(size_t n,bool directory){
  Storage storage;char temporary[64],destination[64];
  if(directory){ProfileStorePaths::DirectoryTemporaryPath(temporary,sizeof(temporary),0);ProfileStorePaths::DirectoryPath(destination,sizeof(destination),0);}
  else{ProfileStorePaths::RecordTemporaryPath(temporary,sizeof(temporary),UINT32_MAX,UINT32_MAX);ProfileStorePaths::RecordPath(destination,sizeof(destination),UINT32_MAX,UINT32_MAX);}
  for(unsigned round=0;round<64;++round){
    std::vector<uint8_t> expected(n);for(size_t i=0;i<n;++i)expected[i]=static_cast<uint8_t>(i*37+round);
    const std::array<uint8_t,3> stale={0xad,0xde,0xff};storage.checking=false;
    require(storage.Write(temporary,stale.data(),stale.size()),"stale temp seed");
    if(round%2==0)require(storage.Write(destination,stale.data(),stale.size()),"orphan/invalid destination seed");
    Expected context{&storage,&expected,false};auto scratch=expected;storage.checking=true;
    const auto kind=directory?ProfileStorePublicationKind::Directory:ProfileStorePublicationKind::Record;
    require(ProfileStoreAtomicCommit::ReplaceVerifiedFile(storage,temporary,destination,scratch.data(),scratch.size(),validate,&context,nullptr,kind),"verified replacement");
    require(!storage.Exists(temporary)&&storage.Size(destination)==n,"rename publishes only destination");
    storage.remount();std::vector<uint8_t> restored(n);require(storage.Read(destination,restored.data(),restored.size())&&restored==expected,"durable remount exact bytes");
    // Validator failure must leave existing destination intact, with no remove/rename.
    context.reject=true;scratch=expected;const auto removes=storage.removes,renames=storage.renames;
    ProfileStoreIoStage stage=ProfileStoreIoStage::None;
    require(!ProfileStoreAtomicCommit::ReplaceVerifiedFile(storage,temporary,destination,scratch.data(),scratch.size(),validate,&context,&stage,kind),"negative validator rejects");
    require(stage==(directory?ProfileStoreIoStage::DirectoryVerify:ProfileStoreIoStage::RecordVerify)&&storage.removes==removes&&storage.renames==renames,"reject has no publication side effect");
    require(storage.Read(destination,restored.data(),restored.size())&&restored==expected,"reject preserves destination");
  }
}
}
int main(){try{exercise(2620,true);exercise(4128,false);std::puts("profile_store_pinned_littlefs_ram=PASS directory_bytes=2620 record_bytes=4128 replacements=128 negative_validations=128 remount_readback=true");return 0;}catch(const std::exception &e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
