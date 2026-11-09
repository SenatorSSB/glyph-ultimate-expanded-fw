#include "core/ConfigBinReadOnlyDiagnostic.hpp"
#if GLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC
#include <Arduino.h>
#include <cstring>
#ifdef GLYPH_CHECKED_STORAGE_TEST_MOUNT
extern lfs_t *CheckedStorageTestMount();
#else
#include <LittleFS.h>
#include <RP2040Version.h>
#if ARDUINO_PICO_MAJOR != 3 || ARDUINO_PICO_MINOR != 6 || ARDUINO_PICO_REVISION != 3
#error Config.bin diagnostic mount requires the reviewed Arduino-Pico 3.6.3
#endif
#endif

namespace config_bin_diagnostic {
namespace {
int DenyProgram(const lfs_config *, lfs_block_t, lfs_off_t, const void *, lfs_size_t) { return LFS_ERR_IO; }
int DenyErase(const lfs_config *, lfs_block_t) { return LFS_ERR_IO; }
#ifndef GLYPH_CHECKED_STORAGE_TEST_MOUNT
struct FsAccess : fs::FS {
    static fs::FSImplPtr fs::FS::* implementation() { return &FsAccess::_impl; }
};
struct LfsAccess : littlefs_impl::LittleFSImpl {
    static lfs_config littlefs_impl::LittleFSImpl::* configuration() { return &LfsAccess::_lfs_cfg; }
    static lfs_t littlefs_impl::LittleFSImpl::* filesystem() { return &LfsAccess::_lfs; }
    static bool littlefs_impl::LittleFSImpl::* mounted() { return &LfsAccess::_mounted; }
};
littlefs_impl::LittleFSImpl *implementation() {
    auto impl=LittleFS.*FsAccess::implementation();
    return static_cast<littlefs_impl::LittleFSImpl *>(impl.get());
}
#endif
lfs_t *mount() {
#ifdef GLYPH_CHECKED_STORAGE_TEST_MOUNT
    return CheckedStorageTestMount();
#else
    auto *impl=implementation();
    return impl && impl->*LfsAccess::mounted() ? &(impl->*LfsAccess::filesystem()) : nullptr;
#endif
}
void Put16(uint8_t *p,uint16_t v) { p[0]=uint8_t(v);p[1]=uint8_t(v>>8); }
void Put32(uint8_t *p,uint32_t v) { for(unsigned i=0;i<4;++i)p[i]=uint8_t(v>>(8*i)); }
uint32_t Get32(const uint8_t *p) { return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24; }
void Common(Workspace &w,uint8_t type) {
    std::memset(w.wire,0,sizeof(w.wire));
    std::memcpy(w.wire,"GCB1",4);w.wire[4]=1;w.wire[5]=type;
    Put16(w.wire+6,static_cast<uint16_t>(w.status));
    for(unsigned i=0;i<8;++i)w.wire[8+i]=uint8_t(w.nonce>>(8*i));
}
bool Expired(const Workspace &w) { return uint32_t(millis()-w.started)>=kDeadlineMs; }
// SHA compression is a sibling of filesystem work, never its retained caller.
__attribute__((noinline)) void HashChunk(Workspace &w) {
    const auto *p=w.wire+24;w.full_hash.Update(p,w.count);
    for(size_t i=0;i<w.count;++i) {
        if(w.sent+i<8) { w.header[w.sent+i]=p[i];++w.header_count; }
        else {
            w.body_hash.Update(p+i,1);w.body_crc^=p[i];
            for(unsigned j=0;j<8;++j)w.body_crc=(w.body_crc>>1)^(0xedb88320u&(0u-(w.body_crc&1)));
        }
    }
}
__attribute__((always_inline)) inline bool Open(Workspace &w) {
    w.fs=mount();
    if(!w.fs||!w.fs->cfg||w.fs->mlist||w.fs->cfg->prog!=DenyProgram||w.fs->cfg->erase!=DenyErase||w.fs->cfg->cache_size!=sizeof(w.file_cache)) {
        w.status=Status::StorageUnavailable;return false;
    }
    w.file_config.buffer=w.file_cache;
    const int result=lfs_file_opencfg(w.fs,&w.file,"/config.bin",LFS_O_RDONLY,&w.file_config);
    if(result<0) { w.status=result==LFS_ERR_NOENT?Status::NotFound:Status::OpenFailed;return false; }
    w.opened=true;
    const lfs_soff_t size=lfs_file_size(w.fs,&w.file);
    if(size<0) { w.status=Status::ReadFailed;return false; }
    w.file_size=uint32_t(size);
    if(w.file_size>kMaxFileBytes) { w.status=Status::SizeLimit;return false; }
    return true;
}
__attribute__((always_inline)) inline void Close(Workspace &w) {
    if(!w.opened)return;
    const int rc=lfs_file_close(w.fs,&w.file);w.opened=false;w.closed=rc==0;
    if(rc<0)w.status=Status::CloseFailed;
}
__attribute__((always_inline)) inline bool Final(Workspace &w) {
    Common(w,3);
    Put32(w.wire+16,w.file_size);Put32(w.wire+20,w.sent);
    if(w.header_count==8) { Put32(w.wire+24,Get32(w.header));Put32(w.wire+28,Get32(w.header+4)); }
    Put32(w.wire+32,w.sent>8?w.sent-8:0);Put32(w.wire+36,~w.body_crc);
    w.wire[40]=w.header_count;
    if(w.header_count==8) {
        w.wire[41]|=1;
        if(Get32(w.header)==(w.file_size>8?w.file_size-8:0))w.wire[41]|=2;
        if(Get32(w.header+4)==~w.body_crc)w.wire[41]|=4;
    }
    if(w.complete)w.wire[41]|=8;
    if(w.closed)w.wire[41]|=16;
    std::memcpy(w.wire+44,w.header,8);
    if(w.complete&&w.closed) { w.full_hash.Final(w.wire+52);w.body_hash.Final(w.wire+84); }
    return w.send(w.context,w.wire,kFinalBytes);
}
}
bool InstallReadOnlyMount() {
#ifdef GLYPH_CHECKED_STORAGE_TEST_MOUNT
    auto *fs=CheckedStorageTestMount();
    if(!fs||!fs->cfg)return false;
    auto *cfg=const_cast<lfs_config *>(fs->cfg);
#else
    auto *impl=implementation();
    if(!impl||impl->*LfsAccess::mounted())return false;
    auto *cfg=&(impl->*LfsAccess::configuration());
#endif
    cfg->prog=DenyProgram;cfg->erase=DenyErase;
    return true;
}
bool DecodeRequest(const uint8_t *p,size_t n,uint64_t &nonce) {
    if(n!=kRequestBytes||std::memcmp(p,"GCB1",4)||p[4]!=1||p[5]||p[6]||p[7])return false;
    nonce=0;for(unsigned i=0;i<8;++i)nonce|=uint64_t(p[8+i])<<(8*i);
    return nonce!=0;
}
__attribute__((noinline)) void Prepare(Workspace &w,uint64_t nonce,Status status,Send send,void *context) {
    w.nonce=nonce;w.status=status;w.send=send;w.context=context;w.started=millis();
}
__attribute__((noinline)) bool Extract(Workspace &w) {
    if(w.status!=Status::Ok)return Final(w);
    if(!Open(w)) { Close(w);return Final(w); }
    Common(w,1);Put32(w.wire+16,w.file_size);Put32(w.wire+20,kChunkBytes);
    if(!w.send(w.context,w.wire,24)) { Close(w);return false; }
    while(w.sent<w.file_size) {
        if(Expired(w)) { w.status=Status::Deadline;break; }
        Common(w,2);Put32(w.wire+16,w.sent);
        w.count=w.file_size-w.sent<kChunkBytes?w.file_size-w.sent:kChunkBytes;
        Put16(w.wire+20,uint16_t(w.count));
        if(lfs_file_read(w.fs,&w.file,w.wire+24,w.count)!=static_cast<lfs_ssize_t>(w.count)) { w.status=Status::ReadFailed;break; }
        HashChunk(w);
        if(!w.send(w.context,w.wire,24+w.count)) { Close(w);return false; }
        w.sent+=w.count;
    }
    if(w.status==Status::Ok) {
        if(Expired(w))w.status=Status::Deadline;
        else if(lfs_file_read(w.fs,&w.file,w.wire,1)!=0||lfs_file_size(w.fs,&w.file)!=static_cast<lfs_soff_t>(w.file_size))w.status=Status::ReadFailed;
        else w.complete=true;
    }
    Close(w);return Final(w);
}
}
#endif
