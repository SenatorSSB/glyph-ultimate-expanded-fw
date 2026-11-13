#!/usr/bin/env python3
"""Execute exact f7ba root writer methods, with bounded synthetic host dependencies."""
import argparse,hashlib,json,subprocess,pathlib,struct,zlib
p=argparse.ArgumentParser();p.add_argument('--repo',default=str(pathlib.Path(__file__).resolve().parents[1]));p.add_argument('--output',default='/private/tmp/legacy-writer-replay');a=p.parse_args()
r=pathlib.Path(a.repo);out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True);(out/'include/core').mkdir(parents=True,exist_ok=True)
sha='f7ba82d4cbe79d4353e8d87b7d1b24be3fc15113'
def git(path):return subprocess.check_output(['git','-C',str(r),'show',sha+':'+path],text=True)
source=git('HAL/pico/src/core/ProfileStore.cpp')
def block(signature):
 i=source.index(signature);b=source.index('{',i);j=b+1;depth=1
 while depth:
  depth+=(source[j]=='{')-(source[j]=='}');j+=1
 return source[i:j]
blocks={k:block(k) for k in ['uint32_t Crc32(', 'void Put16(', 'void Put32(', 'uint16_t Get16(', 'uint32_t Get32(', 'struct ProfileStore::Directory {', 'bool EncodeDirectory(', 'bool DecodeDirectory(', 'bool DecodeDirectoryCommit(', 'bool ProfileStore::PublishDirectory(', 'ProfileStore::Status ProfileStore::ImportLegacy(', 'ProfileStore::Status ProfileStore::CompleteMigration(', 'int ProfileStore::Find(', 'ProfileStore::TransactionResult ProfileStore::BeginMutation(', 'void ProfileStore::Finish(', 'ProfileStore::TransactionResult ProfileStore::Reorder(']}
blocks['struct ProfileStore::Directory {']+=';'
manifest={'writer_sha':sha,'source_path':'HAL/pico/src/core/ProfileStore.cpp','blocks':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in blocks.items()},'headers':{},'limitations':['Exact Directory/encoder/decoder/ImportLegacy/CompleteMigration/Reorder/BeginMutation/Find/Finish/PublishDirectory/atomic publication methods are compiled verbatim from Git.','Host Config and UltimateProfile are intentionally synthetic stubs; ValidateProfile and WriteProfile are successful stubs. This proves root publication only, not payload/Config validity, production boot or physical bytes.','Constructor and Begin provide known initial empty ready/incarnation42 storage; neither production initialization nor persistence adapter is exercised.']}
for name in ['ProfileStore.hpp','ProfileStoreStorage.hpp','ProfileStorePaths.hpp','ProfileStoreAtomicCommit.hpp']:
 text=git('include/core/'+name);(out/'include/core'/name).write_text(text);manifest['headers'][name]=hashlib.sha256(text.encode()).hexdigest()
(out/'include/config.pb.h').write_text('#pragma once\n#include <cstdint>\nstruct UltimateProfile { uint32_t test; };\n#define UltimateProfile_init_default {}\nstruct Config { uint32_t ultimate_profiles_count; UltimateProfile ultimate_profiles[2]; uint32_t ultimate_profile_store_format; uint32_t ultimate_profile_store_incarnation; };\n')
text='''#include <cassert>
#include <cstring>
#include <cstdio>
#include <fstream>
#include <map>
#include <string>
#include <vector>
#include "core/ProfileStore.hpp"
#include "core/ProfileStorePaths.hpp"
#include "core/ProfileStoreAtomicCommit.hpp"
constexpr uint32_t kDirectoryMagic=0x31534450u;
constexpr uint16_t kEnvelopeVersion=1;
constexpr size_t kDirectoryWireBytes=2620;
'''+ '\n'.join(blocks.values())+'''
ProfileStore::ProfileStore(ProfileStoreStorage *s): _storage(s) {}
bool ProfileStore::Begin(){static Directory d;d={};d.incarnation=42;_directory=&d;_ready=true;_read_only_recovery=false;return true;}
uint32_t ProfileStore::Incarnation()const{return _directory->incarnation;}
uint32_t ProfileStore::Generation()const{return _directory->generation;}
bool ProfileStore::ValidateProfile(const UltimateProfile&)const{return true;}
bool ProfileStore::WriteProfile(uint32_t,uint32_t,const UltimateProfile&){return true;}
struct Memory:ProfileStoreStorage{
std::map<std::string,std::vector<uint8_t>> files; std::vector<std::string> ops;
bool Write(const char*p,const uint8_t*b,size_t n)override{ops.push_back(std::string("write ")+p);files[p]={b,b+n};return true;}
bool Read(const char*p,uint8_t*b,size_t n)override{ops.push_back(std::string("read ")+p);if(!files.count(p)||files[p].size()!=n)return false;memcpy(b,files[p].data(),n);return true;}
size_t Size(const char*p)override{return files.count(p)?files[p].size():0;}
bool Exists(const char*p)override{return files.count(p);}
bool Remove(const char*p)override{ops.push_back(std::string("remove ")+p);files.erase(p);return true;}
bool Rename(const char*f,const char*t)override{ops.push_back(std::string("rename ")+f+" "+t);if(!files.count(f))return false;files[t]=files[f];files.erase(f);return true;}
};
void dump(const std::string&folder,const char*name,const std::vector<uint8_t>&bytes){std::ofstream file(folder+"/"+name,std::ios::binary);file.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());}
int main(int argc,char**argv){assert(argc==2);std::string output=argv[1];Memory storage;ProfileStore store(&storage);assert(store.Begin());Config legacy{};legacy.ultimate_profiles_count=1;legacy.ultimate_profiles[0].test=1;legacy.ultimate_profiles[1].test=2;uint32_t ids[2]{};
assert(store.ImportLegacy(legacy,ids,2)==ProfileStore::Status::Ok);assert(ids[0]==1&&ids[1]==0);assert(storage.files.size()==1);auto older=storage.files.at("/ultimate-dir-0.bin");assert(Get32(older.data()+8)==1&&Get32(older.data()+24)==1);dump(output,"after-import-slot0.bin",older);
Config compact{};compact.ultimate_profile_store_format=ProfileStore::kCompactConfigFormat;compact.ultimate_profile_store_incarnation=store.Incarnation();assert(store.CompleteMigration(compact)==ProfileStore::Status::Ok);assert(storage.files.size()==2);assert(storage.files.at("/ultimate-dir-0.bin")==older);auto newer=storage.files.at("/ultimate-dir-1.bin");assert(Get32(newer.data()+8)==2&&Get32(newer.data()+24)==2);dump(output,"completed-slot0.bin",older);dump(output,"completed-slot1.bin",newer);
Put32(older.data()+8,2);Put32(older.data()+24,2);Put32(older.data()+2616,Crc32(older.data(),2616));assert(older==newer);
assert(store.Reorder(ids[0],7,2,123,456).status==ProfileStore::Status::Ok);assert(storage.files.size()==2);assert(storage.files.at("/ultimate-dir-1.bin")==newer);auto post=storage.files.at("/ultimate-dir-0.bin");assert(Get32(post.data()+8)==3&&Get32(post.data()+24)==2);assert(Get32(post.data()+32+16)==7);dump(output,"post-update-slot0.bin",post);dump(output,"post-update-slot1.bin",newer);
std::ofstream trace(output+"/operations.txt");for(auto&op:storage.ops)trace<<op<<"\\n";std::puts("source_native_f7ba_publication=PASS state1_generation1_slot0_preserved=true state2_generation2_slot1=true only_generation_state_crc_change=true both_state2_after_reorder=true completed_slot1_preserved=true");}
'''
(out/'replay.cpp').write_text(text)
subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-I',str(out/'include'),str(out/'replay.cpp'),'-o',str(out/'replay')],check=True)
result=subprocess.run([str(out/'replay'),str(out)],check=True,capture_output=True,text=True);manifest['stdout']=result.stdout;manifest['raw_roots']={}
for file in sorted(out.glob('*.bin')):
 b=file.read_bytes();manifest['raw_roots'][file.name]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'generation':struct.unpack_from('<I',b,8)[0],'migration_state':struct.unpack_from('<I',b,24)[0],'crc_valid':zlib.crc32(b[:2616])==struct.unpack_from('<I',b,2616)[0]}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
