// Actual selected LittleFS C implementation on simulated 512KiB flash.
// Also calls the literal pathValid body extracted from the selected wrapper.
// No flash device, host filesystem mount or hardware is accessed.
#include <lfs.h>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>
#include "actual_path_valid.hpp"
static uint8_t flash[512*1024];
static lfs_t fs;
static lfs_config cfg;
static unsigned checks;
static void require(bool ok,const char *name) { ++checks; if(!ok){std::cerr<<"FAIL "<<name<<'\n';std::exit(1);} }
static bool bounds(lfs_block_t block,lfs_off_t off,lfs_size_t size) { return block<128 && off<=4096 && size<=4096-off; }
static int read_flash(const lfs_config*,lfs_block_t block,lfs_off_t off,void *dst,lfs_size_t size) {
    if(!bounds(block,off,size)) return LFS_ERR_IO; std::memcpy(dst,flash+block*4096+off,size);return 0;
}
static int prog_flash(const lfs_config*,lfs_block_t block,lfs_off_t off,const void *src,lfs_size_t size) {
    if(!bounds(block,off,size))return LFS_ERR_IO;
    auto data=static_cast<const uint8_t*>(src);auto dest=flash+block*4096+off;
    for(size_t i=0;i<size;++i){if((dest[i]&data[i])!=data[i])return LFS_ERR_IO;dest[i]&=data[i];}return 0;
}
static int erase_flash(const lfs_config*,lfs_block_t block) { if(block>=128)return LFS_ERR_IO;std::memset(flash+block*4096,255,4096);return 0; }
static int sync_flash(const lfs_config*) { return 0; }
int main(int argc,char **argv) {
    require(argc==4,"probe arguments");const char *old=argv[1],*current=argv[2];
    std::ifstream file(argv[3],std::ios::binary);std::vector<uint8_t> config((std::istreambuf_iterator<char>(file)),{});
    require(config.size()==3779,"actual tested baked Config blob");
    cfg.read=read_flash;cfg.prog=prog_flash;cfg.erase=erase_flash;cfg.sync=sync_flash;
    cfg.read_size=256;cfg.prog_size=256;cfg.block_size=4096;cfg.block_count=128;
    cfg.block_cycles=16;cfg.cache_size=256;cfg.lookahead_size=256;
    std::memset(flash,255,sizeof(flash));
    require(lfs_mount(&fs,&cfg)!=0,"erased partition initially unmountable");
    require(lfs_format(&fs,&cfg)==0,"explicit format actual library");
    require(lfs_mount(&fs,&cfg)==0,"actual remount after format");
    require(fs.name_max==32,"exact target LFS_NAME_MAX");
    require(!pathValid(old),"old marker rejected by literal Arduino wrapper pathValid");
    lfs_file_t marker{};int old_rc=lfs_file_open(&fs,&marker,old,LFS_O_WRONLY|LFS_O_CREAT|LFS_O_TRUNC);
    require(old_rc==LFS_ERR_NAMETOOLONG,"old marker also rejected by actual littlefs C");
    require(pathValid(current),"new versioned marker accepted by literal pathValid");
    require(!pathValid("/12345678901234567890123456789012"),"wrapper 32-byte boundary rejects");
    require(pathValid("/1234567890123456789012345678901"),"wrapper 31-byte boundary accepts");
    lfs_file_t config_file{};
    require(lfs_file_open(&fs,&config_file,"config.bin",LFS_O_WRONLY|LFS_O_CREAT|LFS_O_TRUNC)==0,"real Config file open");
    require(lfs_file_write(&fs,&config_file,config.data(),config.size())==int(config.size()),"real Config write");
    require(lfs_file_close(&fs,&config_file)==0,"real Config close/sync");
    constexpr char payload[]="friend_ultimate_20261011_applied_v2\n";
    require(lfs_file_open(&fs,&marker,current,LFS_O_WRONLY|LFS_O_CREAT|LFS_O_TRUNC)==0,"real v2 marker create");
    require(lfs_file_write(&fs,&marker,payload,sizeof(payload)-1)==sizeof(payload)-1,"real v2 marker write");
    require(lfs_file_sync(&fs,&marker)==0 && lfs_file_close(&fs,&marker)==0,"real marker sync/close");
    require(lfs_unmount(&fs)==0 && lfs_mount(&fs,&cfg)==0,"real later remount, no format");
    require(lfs_file_open(&fs,&marker,current,LFS_O_RDONLY)==0,"real marker reopen");
    char readback[sizeof(payload)]{};
    require(lfs_file_size(&fs,&marker)==sizeof(payload)-1 && lfs_file_read(&fs,&marker,readback,sizeof(readback))==sizeof(payload)-1 && std::memcmp(payload,readback,sizeof(payload)-1)==0,"real exact marker readback after remount");
    require(lfs_file_close(&fs,&marker)==0,"real marker close");
    require(lfs_file_open(&fs,&config_file,"config.bin",LFS_O_RDONLY)==0,"real persisted Config reopen");
    std::vector<uint8_t> read_config(config.size());
    require(lfs_file_read(&fs,&config_file,read_config.data(),read_config.size())==int(config.size()) && read_config==config,"real full Config bytes roundtrip after remount");
    require(lfs_file_close(&fs,&config_file)==0 && lfs_unmount(&fs)==0,"real close/unmount");
    std::cout<<"ACTUAL LITTLEFS PASS: erased partition mount FAIL -> explicit format -> remount -> Config + marker persisted -> later remount exact readback\n"
             <<"OLD MARKER PROVEN DEFECT: basename="<<std::strlen(old+1)<<" wrapper pathValid=false; real lfs_file_open="<<old_rc<<" (LFS_ERR_NAMETOOLONG); selected LFS_NAME_MAX=32\n"
             <<"NEW MARKER: basename="<<std::strlen(current+1)<<" pathValid=true; Config3779 bytes and marker36 bytes exact; checks="<<checks<<" PASS; hardware NOT_TESTED\n";
}
