// Synthetic NOR only. No physical device, serial enumeration, or retained data.
#include "core/ConfigBinReadOnlyDiagnostic.hpp"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>
using Bytes=std::vector<uint8_t>;
namespace {
lfs_t fs{};lfs_config cfg{};Bytes nor(524288,0xff);
size_t programs=0,erases=0,allocations=0,read_calls=0,fail_read=0;
size_t size_calls=0,fail_size=0,close_calls=0,fail_close=0;
uint32_t tick=0,tick_step=0;
bool mounted=false,monitor=false;
std::string output;
void need(bool v,const char *why) { if(!v)throw std::runtime_error(why); }
int read_block(const lfs_config *,lfs_block_t b,lfs_off_t off,void *p,lfs_size_t n) {
    if(b>=128||off>4096||n>4096-off)return LFS_ERR_IO;
    std::memcpy(p,nor.data()+size_t(b)*4096+off,n);return 0;
}
int program(const lfs_config *,lfs_block_t b,lfs_off_t off,const void *p,lfs_size_t n) {
    ++programs;if(b>=128||off>4096||n>4096-off)return LFS_ERR_IO;
    const auto *in=static_cast<const uint8_t *>(p);auto *out=nor.data()+size_t(b)*4096+off;
    for(size_t i=0;i<n;++i) { if((out[i]&in[i])!=in[i])return LFS_ERR_CORRUPT;out[i]&=in[i]; }
    return 0;
}
int erase(const lfs_config *,lfs_block_t b) { ++erases;if(b>=128)return LFS_ERR_IO;std::fill_n(nor.data()+size_t(b)*4096,4096,0xff);return 0; }
int sync(const lfs_config *) { return 0; }
void configure() {
    cfg={};cfg.read=read_block;cfg.prog=program;cfg.erase=erase;cfg.sync=sync;
    cfg.read_size=cfg.prog_size=cfg.cache_size=256;
    cfg.block_size=4096;cfg.block_count=128;cfg.lookahead_size=256;cfg.block_cycles=16;
}
void seed(const Bytes *bytes) {
    if(mounted)need(lfs_unmount(&fs)==0,"old unmount");mounted=false;
    std::fill(nor.begin(),nor.end(),0xff);configure();
    need(lfs_format(&fs,&cfg)==0&&lfs_mount(&fs,&cfg)==0,"explicit synthetic seed");mounted=true;
    if(bytes) {
        lfs_file_t f{};need(lfs_file_open(&fs,&f,"/config.bin",LFS_O_CREAT|LFS_O_WRONLY)==0,"seed open");
        need(lfs_file_write(&fs,&f,bytes->data(),bytes->size())==int(bytes->size()),"seed write");
        need(lfs_file_close(&fs,&f)==0,"seed close");
    }
    need(lfs_unmount(&fs)==0,"seed unmount");mounted=false;fs.cfg=&cfg;
    programs=erases=0;
    need(config_bin_diagnostic::InstallReadOnlyMount(),"install pre-mount readonly callbacks");
    const auto snapshot=nor;
    need(lfs_mount(&fs,&cfg)==0,"readonly mount");mounted=true;
    need(nor==snapshot&&programs==0&&erases==0,"mount no mutation");
    uint8_t zero[256]{};
    need(cfg.prog(&cfg,0,0,zero,sizeof(zero))<0&&cfg.erase(&cfg,0)<0,"callbacks deny real flash operations");
    need(nor==snapshot&&programs==0&&erases==0,"deny callbacks preserve NOR");
}
struct Output { std::vector<Bytes> packets;size_t cutoff=SIZE_MAX; };
bool send(void *p,const uint8_t *data,size_t n) {
    auto &out=*static_cast<Output *>(p);if(out.packets.size()==out.cutoff)return false;
    out.packets.emplace_back(data,data+n);return true;
}
void write_output(const std::string &name,const Output &out) {
    std::ofstream file(output+"/"+name+".wire",std::ios::binary);
    for(const auto &p:out.packets) { const uint32_t n=p.size();for(unsigned i=0;i<4;++i)file.put(char(n>>(8*i)));file.write(reinterpret_cast<const char *>(p.data()),p.size()); }
}
void run(const std::string &name,const Bytes *bytes,size_t cutoff=SIZE_MAX,size_t read_fault=0,size_t size_fault=0,size_t close_fault=0,uint32_t clock_step=0) {
    seed(bytes);const auto snapshot=nor;
    read_calls=size_calls=close_calls=0;fail_read=read_fault;fail_size=size_fault;fail_close=close_fault;tick=0;tick_step=clock_step;
    config_bin_diagnostic::Workspace w;Output out;out.cutoff=cutoff;
    allocations=0;monitor=true;
    const bool result=config_bin_diagnostic::Extract(w,0x0102030405060708ULL,send,&out);
    monitor=false;
    need(result==(cutoff==SIZE_MAX),"TX termination");
    need(!w.opened&&!fs.mlist,"all handles released");
    need(nor==snapshot&&programs==0&&erases==0,"extraction no NOR mutation");
    need(allocations==0,"extraction no dynamic allocation");
    write_output(name,out);
    fail_read=fail_size=fail_close=0;tick_step=0;
}
}
extern "C" void *DiagnosticTestMalloc(size_t n) { if(monitor)++allocations;return std::malloc(n); }
extern "C" lfs_ssize_t DiagnosticRealRead(lfs_t *,lfs_file_t *,void *,lfs_size_t);
extern "C" lfs_ssize_t DiagnosticTestRead(lfs_t *f,lfs_file_t *file,void *out,lfs_size_t n) {
    if(monitor&&++read_calls==fail_read)return LFS_ERR_IO;
    return DiagnosticRealRead(f,file,out,n);
}
extern "C" lfs_soff_t DiagnosticRealSize(lfs_t *,lfs_file_t *);
extern "C" lfs_soff_t DiagnosticTestSize(lfs_t *f,lfs_file_t *file) {
    if(monitor&&++size_calls==fail_size)return 524289;
    return DiagnosticRealSize(f,file);
}
extern "C" int DiagnosticRealClose(lfs_t *,lfs_file_t *);
extern "C" int DiagnosticTestClose(lfs_t *f,lfs_file_t *file) {
    const int rc=DiagnosticRealClose(f,file);
    if(monitor&&++close_calls==fail_close)return LFS_ERR_IO;
    return rc;
}
lfs_t *CheckedStorageTestMount() { return &fs; }
unsigned long millis() { const auto result=tick;tick+=tick_step;return result; }
int main(int argc,char **argv) { try {
    need(argc==2,"output directory");output=argv[1];
    uint8_t request[17]={'G','C','B','1',1,0,0,0,1};uint64_t nonce=0;
    need(config_bin_diagnostic::DecodeRequest(request,16,nonce)&&nonce==1,"fixed request");
    for(size_t n=0;n<=17;++n)if(n!=16)need(!config_bin_diagnostic::DecodeRequest(request,n,nonce),"request exact extent");
    for(unsigned i=0;i<8;++i) { const auto old=request[i];request[i]^=0x80;need(!config_bin_diagnostic::DecodeRequest(request,16,nonce),"request header mutations");request[i]=old; }
    request[8]=0;need(!config_bin_diagnostic::DecodeRequest(request,16,nonce),"nonce nonzero");
    Bytes empty,short_header={'b','a','d'},header(8),body(70008);
    for(size_t i=0;i<body.size();++i)body[i]=uint8_t(i*31+7);
    run("missing",nullptr);run("empty",&empty);run("short",&short_header);run("header",&header);run("body",&body);
    run("read-failure",&body,SIZE_MAX,2);run("oversize",&body,SIZE_MAX,0,1);
    run("size-drift",&body,SIZE_MAX,0,2);run("close-failure",&body,SIZE_MAX,0,0,1);
    run("deadline",&body,SIZE_MAX,0,0,0,60000);
    run("tx-start",&body,0);run("tx-chunk",&body,2);
    need(lfs_unmount(&fs)==0,"final unmount");
    std::puts("config_bin_readonly_diagnostic_storage=PASS");return 0;
} catch(const std::exception &e) { std::fprintf(stderr,"%s\n",e.what());return 1; } }
