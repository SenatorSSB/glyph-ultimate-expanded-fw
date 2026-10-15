// Named-file checked primitive double. The separate checked_storage_host suite
// compiles the production primitive against the actual pinned LittleFS engine.
#include <LittleFS.h>
#include "core/CheckedStorage.hpp"
#include <new>
namespace CheckedStorage {
namespace {
FaultHook hook=nullptr;
::File &handle(File &f){return *reinterpret_cast<::File *>(f.native);}
Result pre(Kind k,Operation op,const char *path){if(hook&&hook(k,op,Phase::Before,path)!=Fault::None)return {Outcome::Failed,1,0};return {Outcome::Ok,0,0};}
Result post(Kind k,Operation op,const char *path,Result r){if(hook&&hook(k,op,Phase::After,path)!=Fault::None)return {Outcome::Uncertain,1,r.bytes};return r;}
}
void SetFaultHook(FaultHook f){hook=f;}
Result Open(File &f,const char *p,bool w,Kind k){auto r=pre(k,w?Operation::OpenWrite:Operation::OpenRead,p);if(!r)return r;new(f.native)::File(LittleFS.open(p,w?"w+":"r"));f.opened=bool(handle(f));f.path=p;f.kind=k;return post(k,w?Operation::OpenWrite:Operation::OpenRead,p,{f.opened?Outcome::Ok:Outcome::Failed,0,0});}
Result Read(File &f,void *p,size_t n){auto r=pre(f.kind,Operation::Read,f.path);if(!r)return r;int got=handle(f).read(static_cast<uint8_t *>(p),n);return post(f.kind,Operation::Read,f.path,{got==int(n)?Outcome::Ok:Outcome::Failed,0,got<0?0:size_t(got)});}
Result Write(File &f,const void *p,size_t n){auto r=pre(f.kind,Operation::Write,f.path);if(!r)return r;auto got=handle(f).write(static_cast<const uint8_t *>(p),n);return post(f.kind,Operation::Write,f.path,{got==n?Outcome::Ok:Outcome::Failed,0,got});}
Result Seek(File &f,size_t n){return {handle(f).seek(n)?Outcome::Ok:Outcome::Failed,0,0};}
Result Sync(File &f){auto r=pre(f.kind,Operation::Sync,f.path);if(!r)return r;return post(f.kind,Operation::Sync,f.path,r);}
Result Close(File &f){auto r=pre(f.kind,Operation::Close,f.path);handle(f).~File();f.opened=false;return post(f.kind,Operation::Close,f.path,r);}
Result Stat(const char *p,size_t *s,Kind k){auto r=pre(k,Operation::Stat,p);if(!r)return r;if(!LittleFS.exists(p))return {Outcome::NotFound,0,0};if(s)*s=LittleFS.files.at(p)->size();return post(k,Operation::Stat,p,r);}
Result Remove(const char *p,Kind k){auto r=pre(k,Operation::Remove,p);if(!r)return r;return post(k,Operation::Remove,p,{!LittleFS.exists(p)||LittleFS.remove(p)?Outcome::Ok:Outcome::Failed,0,0});}
Result Rename(const char *a,const char *b,Kind k){auto r=pre(k,Operation::Rename,a);if(!r)return r;return post(k,Operation::Rename,a,{LittleFS.rename(a,b)?Outcome::Ok:Outcome::Failed,0,0});}
Result Capacity(Geometry &g){g.total_bytes=524288;g.used_bytes=8192;for(const auto &entry:LittleFS.files)g.used_bytes+=((entry.second->size()+4095)/4096)*4096;g.free_bytes=g.used_bytes<g.total_bytes?g.total_bytes-g.used_bytes:0;g.erase_bytes=4096;g.program_bytes=256;return {Outcome::Ok,0,0};}

}
