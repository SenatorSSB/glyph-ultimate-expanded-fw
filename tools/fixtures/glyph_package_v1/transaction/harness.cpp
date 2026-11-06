// Host-only harness: every production body is included/linked from --repo.
// Formatting/seeding is confined to mode `seed`. Modes execute/inspect consume
// exactly 512 KiB raw NOR images; neither formats nor recreates namespace files.
#include "ProfileStore.cpp"
#include "glyph_config_validation.hpp"
#include <lfs.h>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace test {
using Bytes=std::vector<uint8_t>;
using Files=std::map<std::string,Bytes>;
constexpr size_t kNorBytes=524288;
lfs_t fs{};lfs_config cfg{};Bytes nor(kNorBytes,0xff),cut;
bool mounted=false, fault_hit=false, trace_enabled=false;
size_t programs=0,erases=0,syncs=0,reads=0,target=SIZE_MAX,reentries=0,hidden_checks=0;
std::string output_dir;
struct Event { size_t index;unsigned kind,operation,when,call_phase,intent_phase;std::string path; };
std::vector<Event> events;
void need(bool value,const std::string &why){if(!value)throw std::runtime_error(why);}
std::string path(const std::string &name){return output_dir+"/"+name;}
Bytes input(const std::string &filename){std::ifstream in(filename,std::ios::binary);need(bool(in),"open input "+filename);return Bytes(std::istreambuf_iterator<char>(in),{});}
void output(const std::string &filename,const Bytes &bytes){std::ofstream out(filename,std::ios::binary);need(bool(out),"open output "+filename);out.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());need(bool(out),"write output "+filename);}
void append_word(Bytes &out,uint32_t value){for(unsigned i=0;i<4;++i)out.push_back(uint8_t(value>>(8*i)));}
uint32_t word(const Bytes &bytes,size_t &at){need(at<=bytes.size()&&bytes.size()-at>=4,"word extent");const auto value=package_storage::Get32(bytes.data()+at);at+=4;return value;}
std::vector<Bytes> requests(const std::string &filename){auto bytes=input(filename);size_t at=0;const auto count=word(bytes,at);std::vector<Bytes> result;
 for(size_t i=0;i<count;++i){const auto n=word(bytes,at);need(n<=bytes.size()-at,"request extent");result.emplace_back(bytes.begin()+at,bytes.begin()+at+n);at+=n;}need(at==bytes.size(),"request trailing bytes");return result;}
Files namespace_input(const std::string &filename){auto bytes=input(filename);size_t at=0;Files files;auto n=word(bytes,at);
 for(size_t i=0;i<n;++i){auto length=word(bytes,at);need(length<=bytes.size()-at,"name extent");std::string name(reinterpret_cast<const char*>(bytes.data()+at),length);at+=length;length=word(bytes,at);need(length<=bytes.size()-at,"file extent");files.emplace(name,Bytes(bytes.begin()+at,bytes.begin()+at+length));at+=length;}need(at==bytes.size(),"namespace trailing bytes");return files;}
int read(const lfs_config*,lfs_block_t block,lfs_off_t offset,void *out,lfs_size_t bytes){++reads;if(block>=128||offset>4096||bytes>4096-offset)return LFS_ERR_INVAL;std::memcpy(out,nor.data()+4096*block+offset,bytes);return 0;}
int program(const lfs_config*,lfs_block_t block,lfs_off_t offset,const void *in,lfs_size_t bytes){++programs;if(block>=128||offset>4096||bytes>4096-offset)return LFS_ERR_INVAL;auto *dest=nor.data()+4096*block+offset;const auto *source=static_cast<const uint8_t*>(in);for(size_t i=0;i<bytes;++i){if((dest[i]&source[i])!=source[i])return LFS_ERR_CORRUPT;dest[i]&=source[i];}return 0;}
int erase(const lfs_config*,lfs_block_t block){++erases;if(block>=128)return LFS_ERR_INVAL;std::fill_n(nor.data()+4096*block,4096,0xff);return 0;}
int sync(const lfs_config*){++syncs;return 0;}
void configure(){cfg.read=read;cfg.prog=program;cfg.erase=erase;cfg.sync=sync;cfg.read_size=cfg.prog_size=cfg.cache_size=256;cfg.block_size=4096;cfg.block_count=128;cfg.lookahead_size=256;cfg.block_cycles=16;}
void mount_image(const std::string &filename){nor=input(filename);need(nor.size()==kNorBytes,"raw NOR extent512KiB");const auto before=nor;const auto p=programs,e=erases;mounted=lfs_mount(&fs,&cfg)==0;need(nor==before&&programs==p&&erases==e,"restart mount must not format/program/erase");}
void no_handles(){need(fs.mlist==nullptr,"no live native file/directory handles");}
Files files(){Files result;if(!mounted)return result;lfs_dir_t directory{};need(lfs_dir_open(&fs,&directory,"/")==0,"dump directory open");lfs_info info{};int rc;
 while((rc=lfs_dir_read(&fs,&directory,&info))>0){if(!std::strcmp(info.name,".")||!std::strcmp(info.name,".."))continue;need(info.type==LFS_TYPE_REG,"unexpected directory");std::string name="/"+std::string(info.name);Bytes bytes(info.size);lfs_file_t file{};need(lfs_file_open(&fs,&file,name.c_str(),LFS_O_RDONLY)==0,"dump file open");const auto read=lfs_file_read(&fs,&file,bytes.data(),bytes.size());const auto closed=lfs_file_close(&fs,&file);need(read==int(bytes.size())&&closed==0,"dump exact read/close");result.emplace(std::move(name),std::move(bytes));}
 const auto closed=lfs_dir_close(&fs,&directory);need(rc==0&&closed==0,"dump directory close");no_handles();return result;}
void dump_files(const std::string &filename){const auto all=files();Bytes bytes;append_word(bytes,all.size());for(const auto &item:all){append_word(bytes,item.first.size());bytes.insert(bytes.end(),item.first.begin(),item.first.end());append_word(bytes,item.second.size());bytes.insert(bytes.end(),item.second.begin(),item.second.end());}output(filename,bytes);}
std::string quoted(const std::string &s){std::string out="\"";for(char c:s){if(c=='"'||c=='\\')out+='\\';out+=c;}return out+'"';}
void trace(){std::ofstream out(path("trace.json"));out<<"[";bool first=true;for(const auto &e:events){if(!first)out<<",";first=false;out<<"{\"index\":"<<e.index<<",\"kind\":"<<e.kind<<",\"operation\":"<<e.operation<<",\"when\":"<<e.when<<",\"call_phase\":"<<e.call_phase<<",\"intent_phase\":"<<e.intent_phase<<",\"path\":"<<quoted(e.path)<<"}";}out<<"]\n";}
CheckedStorage::Fault hook(CheckedStorage::Kind kind,CheckedStorage::Operation operation,CheckedStorage::Phase when,const char *name){
 if(!trace_enabled||!PackageStorageFence::WriteOwner())return CheckedStorage::Fault::None;
 const auto index=events.size();events.push_back({index,unsigned(kind),unsigned(operation),unsigned(when),unsigned(package_call.phase),package_storage::Get32(initialization_owner.intent+12),name?name:""});
 if(index!=target)return CheckedStorage::Fault::None;
 fault_hit=true;cut=nor;output(path("cut.nor"),cut);
 return when==CheckedStorage::Phase::Before?CheckedStorage::Fault::Fail:CheckedStorage::Fault::LostAcknowledgement;
}
void response(const PackageResponse &r,const std::string &name){size_t bytes=0;need(pb_get_encoded_size(&bytes,PackageResponse_fields,&r),"response size");Bytes out(bytes);auto stream=pb_ostream_from_buffer(out.data(),out.size());need(pb_encode(&stream,PackageResponse_fields,&r),"response encode");output(path(name+".pb"),out);}
bool dispatch(const Bytes &bytes,PackageResponse &response){glyph_package::EnvelopePhase phase{};if(!glyph_package::DecodeCanonicalRequest(bytes.data(),bytes.size(),phase))return false;const bool result=profile_store.DispatchPackage(phase,response);
 need(!phase.package.bytes&&!phase.native.bytes&&!phase.request.package_body.funcs.decode,"dispatch releases borrowed request callbacks");no_handles();return result;}
Bytes encoded_envelope(const PackageEnvelope &request){size_t n=0;need(pb_get_encoded_size(&n,PackageEnvelope_fields,&request),"request encode size");Bytes out(n);auto stream=pb_ostream_from_buffer(out.data(),out.size());need(pb_encode(&stream,PackageEnvelope_fields,&request),"request encode");return out;}
void hidden_id(uint32_t id){if(!id)return;for(size_t i=0;i<profile_store.Count();++i)need(profile_store.EntryAt(i)->id!=id,"pending absent from LIST");UltimateProfile scratch=UltimateProfile_init_default;need(profile_store.Read(id,scratch)!=ProfileStore::Status::Ok,"pending absent from READ");ProfileStore::Status state;need(!profile_store.Activate(id,&state),"pending cannot activate");++hidden_checks;}
// Geometry contradiction injection at the existing ProfileStoreStorage seam.
// Namespace/config/native reads still bind the real mounted production adapter.
class UnderreportedStorage final : public ProfileStoreStorage {
 MountedStorage source;
 public:
 bool Write(const char *p,const uint8_t *b,size_t n)override{return source.Write(p,b,n);}
 bool Read(const char *p,uint8_t *b,size_t n)override{return source.Read(p,b,n);}
 size_t Size(const char *p)override{return source.Size(p);}
 bool Exists(const char *p)override{return source.Exists(p);}
 bool Remove(const char *p)override{return source.Remove(p);}
 bool Rename(const char *a,const char *b)override{return source.Rename(a,b);}
 Result CheckedWrite(const char *p,const uint8_t *b,size_t n,CheckedStorage::Kind k)override{return source.CheckedWrite(p,b,n,k);}
 Result CheckedRead(const char *p,uint8_t *b,size_t n,CheckedStorage::Kind k)override{return source.CheckedRead(p,b,n,k);}
 Result Probe(const char *p,size_t *n=nullptr)override{return source.Probe(p,n);}
 Result CheckedRename(const char *a,const char *b,CheckedStorage::Kind k)override{return source.CheckedRename(a,b,k);}
 Result CheckedRemove(const char *p)override{return source.CheckedRemove(p);}
 bool ReadRange(const char *p,size_t o,uint8_t *b,size_t n)override{return source.ReadRange(p,o,b,n);}
 bool Enumerate(CheckedStorage::Visitor v,void *c)override{return source.Enumerate(v,c);}
 bool Geometry(CheckedStorage::Geometry &g)override{if(!source.Geometry(g))return false;g.used_bytes=0;g.free_bytes=g.total_bytes;return true;}
};
class FallbackBacking final : public ProfileStoreStorage {
 public:
 Files items;unsigned writes=0,removes=0,renames=0;bool revoke_after_write=false;
 bool Write(const char *p,const uint8_t *b,size_t n)override{++writes;items[p]=Bytes(b,b+n);if(revoke_after_write)PackageStorageFence::Fence();return true;}
 bool Read(const char *p,uint8_t *b,size_t n)override{auto it=items.find(p);if(it==items.end()||it->second.size()!=n)return false;std::memcpy(b,it->second.data(),n);return true;}
 size_t Size(const char *p)override{return items.count(p)?items.at(p).size():0;}
 bool Exists(const char *p)override{return items.count(p);}
 bool Remove(const char *p)override{++removes;items.erase(p);return true;}
 bool Rename(const char *a,const char *b)override{++renames;if(!items.count(a))return false;items[b]=items.at(a);items.erase(a);return true;}
};
bool fallback_authorize(void*,PackageStorageFence::WriteKind,uint64_t token,CheckedStorage::Operation operation,const char *p,const char *dest){
 if(token!=7)return false;
 if(operation==CheckedStorage::Operation::OpenWrite)return p&&!std::strcmp(p,"/t");
 if(operation==CheckedStorage::Operation::Remove)return p&&!std::strcmp(p,"/d");
 if(operation==CheckedStorage::Operation::Rename)return p&&dest&&!std::strcmp(p,"/t")&&!std::strcmp(dest,"/d");
 return false;
}
void owner_aliases(){need(sizeof(package_storage::ClassificationWorkspace)<=sizeof(publication_readback),"classifier existing readback owner");need(sizeof(initialization_owner)<=((3908+alignof(decltype(initialization_owner))-1)/alignof(decltype(initialization_owner)))*alignof(decltype(initialization_owner)),"initialization owner extent");need(reinterpret_cast<void*>(&initialization_owner.v2)==reinterpret_cast<void*>(&initialization_owner.body)&&reinterpret_cast<void*>(&initialization_owner.body)==reinterpret_cast<void*>(&initialization_owner.intent),"real initialization aliases");need(reinterpret_cast<void*>(&publication_owner.legacy)==reinterpret_cast<void*>(&publication_owner.package),"publication owner alias");need(reinterpret_cast<void*>(&prepared_create_owner.legacy)==reinterpret_cast<void*>(&prepared_create_owner.package),"request preparation owner alias");}
void summary(bool unchanged,bool hidden,size_t inspected){std::ofstream out(path("summary.json"));out<<"{\"mounted\":"<<(mounted?"true":"false")<<",\"fault_hit\":"<<(fault_hit?"true":"false")<<",\"trace_events\":"<<events.size()<<",\"programs\":"<<programs<<",\"erases\":"<<erases<<",\"syncs\":"<<syncs<<",\"unchanged\":"<<(unchanged?"true":"false")<<",\"no_handles\":true,\"pending_hidden\":"<<(hidden?"true":"false")<<",\"inspected\":"<<inspected<<",\"reentries\":"<<reentries<<",\"hidden_checks\":"<<hidden_checks<<"}\n";}
void shutdown(){if(mounted){const auto before=nor;need(lfs_unmount(&fs)==0,"unmount");need(nor==before,"unmount must preserve NOR");mounted=false;}}
}
lfs_t *CheckedStorageTestMount(){return test::mounted?&test::fs:nullptr;}

int main(int argc,char **argv){using namespace test;try{
 need(argc>=2,"mode required");configure();owner_aliases();
 if(!std::strcmp(argv[1],"observe-configs")||!std::strcmp(argv[1],"observe-configs-faults")){
  const bool inject=!std::strcmp(argv[1],"observe-configs-faults");
  // Synthetic NOR setup only; production observation itself must never write.
  need(lfs_format(&fs,&cfg)==0&&lfs_mount(&fs,&cfg)==0,"observation fixture mount");mounted=true;
  need(persistence.SetValidator(validate_glyph_config),"source Config validator");
  std::string hex;
  while(std::getline(std::cin,hex)){
   need(hex.size()%2==0,"Config hex extent");Bytes body(hex.size()/2);
   for(size_t i=0;i<body.size();++i){const auto pair=hex.substr(2*i,2);body[i]=std::strtoul(pair.c_str(),nullptr,16);}
   Bytes wrapped;append_word(wrapped,body.size());append_word(wrapped,package_storage::Crc32(body.data(),body.size()));wrapped.insert(wrapped.end(),body.begin(),body.end());
   lfs_file_t seed{};need(lfs_file_open(&fs,&seed,"/config-v2.bin",LFS_O_WRONLY|LFS_O_CREAT|LFS_O_TRUNC)==0,"Config seed open");
   need(lfs_file_write(&fs,&seed,wrapped.data(),wrapped.size())==int(wrapped.size()),"Config seed write");need(lfs_file_close(&fs,&seed)==0,"Config seed close");
   const auto before=nor;const auto p=programs,e=erases;Persistence::PackageConfigFacts facts{};bool source=false;
   const auto result=persistence.ObservePackageConfig(Persistence::PackageConfigFile::Current,persistence.PackageConfigScratch(),facts,source,65536);
   no_handles();need(nor==before&&programs==p&&erases==e,"Config observation write-free");
   if(result==Persistence::LoadResult::Loaded){
    need(facts.bytes==body.size()&&facts.crc==package_storage::Crc32(body.data(),body.size()),"exact observed extent/CRC");
    Sha256 hash;hash.Update(body.data(),body.size());uint8_t digest[32];hash.Final(digest);need(!std::memcmp(digest,facts.sha,32),"exact observed SHA");
   }
   if(inject&&result==Persistence::LoadResult::Loaded){
    // Enumerate this actual observation's read/seek seams, then independently
    // fail each one before/after. No fault selection changes production code.
    static size_t seen,fail_at;seen=0;fail_at=SIZE_MAX;
    const auto fault=[](CheckedStorage::Kind,CheckedStorage::Operation op,CheckedStorage::Phase,const char*){
     if(op!=CheckedStorage::Operation::Read&&op!=CheckedStorage::Operation::Seek)return CheckedStorage::Fault::None;
     const auto index=seen++;return index==fail_at?CheckedStorage::Fault::Fail:CheckedStorage::Fault::None;
    };
    CheckedStorage::SetFaultHook(fault);
    Persistence::PackageConfigFacts observed{};bool valid=false;
    need(persistence.ObservePackageConfig(Persistence::PackageConfigFile::Current,persistence.PackageConfigScratch(),observed,valid,65536)==Persistence::LoadResult::Loaded,"fault census positive");
    const auto seams=seen;
    const size_t count=body.size()>8191?32:seams;
    for(size_t selected=0;selected<count;++selected){
     const size_t i=count==seams?selected:selected*(seams-1)/(count-1);
     seen=0;fail_at=i;
     need(persistence.ObservePackageConfig(Persistence::PackageConfigFile::Current,persistence.PackageConfigScratch(),observed,valid,65536)!=Persistence::LoadResult::Loaded,"Config read/seek failure closed");
     need(seen>i,"Config fault reached");no_handles();need(nor==before&&programs==p&&erases==e,"faulted Config observation write-free");
    }
    CheckedStorage::SetFaultHook(nullptr);
    std::cerr<<"observation fault seams "<<count<<" of "<<seams<<" bytes "<<body.size()<<"\n";
   }
   std::cout<<(result==Persistence::LoadResult::Loaded?0:1)<<"\n";
  }
  shutdown();return 0;
 }
 if(!std::strcmp(argv[1],"seed")){
  need(argc==4,"seed NAMESPACE NOR");const auto all=namespace_input(argv[2]);need(lfs_format(&fs,&cfg)==0&&lfs_mount(&fs,&cfg)==0,"explicit test seed format/mount");mounted=true;
  for(const auto &item:all){lfs_file_t file{};need(lfs_file_open(&fs,&file,item.first.c_str(),LFS_O_WRONLY|LFS_O_CREAT|LFS_O_TRUNC)==0,"seed open");need(lfs_file_write(&fs,&file,item.second.data(),item.second.size())==int(item.second.size()),"seed transfer");need(lfs_file_close(&fs,&file)==0,"seed close");}
  need(files()==all,"seed exact namespace");no_handles();output(argv[3],nor);shutdown();return 0;
 }
 need(argc>=5,"execute|inspect NOR REQUESTS OUTDIR");output_dir=argv[4];mount_image(argv[2]);need(persistence.SetValidator(validate_glyph_config),"configured actual source validator");
 if(!std::strcmp(argv[1],"execute")){
  need(argc==6,"execute NOR CREATE OUTDIR FAULT_INDEX(-1none)");target=std::strtoll(argv[5],nullptr,10);const auto bytes=input(argv[3]);
  glyph_package::EnvelopePhase header{};need(glyph_package::DecodeCanonicalRequest(bytes.data(),bytes.size(),header),"canonical CREATE fixture");const auto inc=header.request.expected_store_incarnation;const auto token=header.request.request_token;uint8_t semantic[32];need(PackageCreateDigest(header,semantic),"independent query identity preparation");header.Release();
  const auto boot=nor;profile_store.Begin(inc,0);need(nor==boot,"ordinary creation boot readonly");
  CheckedStorage::SetFaultHook(hook);trace_enabled=true;PackageResponse result{};need(dispatch(bytes,result),"CREATE dispatch");trace_enabled=false;CheckedStorage::SetFaultHook(nullptr);response(result,"response");
  if(fault_hit){const auto after_error=nor;const auto p=programs,e=erases;
   need(PackageStorageFence::MutationFenced(),"every admitted publication failure remains same-boot fenced");
   PackageEnvelope query=PackageEnvelope_init_zero;query.protocol_version=3;query.request_token=token;query.operation=PackageOperation_QUERY_PACKAGE;query.expected_store_incarnation=inc;query.has_expected_digest=true;std::memcpy(query.expected_digest,semantic,32);PackageResponse observed{};need(dispatch(encoded_envelope(query),observed),"sameboot QUERY after failure");need(observed.write_fenced&&observed.storage_floor==PackageStorageFloor_FLOOR_UNRESOLVED,"sameboot QUERY cannot clear a sticky fence");response(observed,"sameboot-query");
   PackageEnvelope status=PackageEnvelope_init_zero;status.protocol_version=3;status.request_token=1;status.operation=PackageOperation_PACKAGE_STATUS;need(dispatch(encoded_envelope(status),observed),"sameboot STATUS after failure");need(observed.status==ProfileStoreStatus_PROFILE_STORE_COMMIT_UNKNOWN&&observed.logical==PackageLogicalDisposition_LOGICAL_NONE&&observed.write_fenced&&observed.storage_floor==PackageStorageFloor_FLOOR_UNRESOLVED,"sameboot STATUS cannot clear sticky fence");response(observed,"sameboot-status");
   need(nor==after_error&&programs==p&&erases==e,"sameboot failure inspection is write-free");}
  trace();output(path("unwound.nor"),nor);dump_files(path("namespace.bin"));
  const bool unchanged=!fault_hit||cut==nor;summary(unchanged,false,0);shutdown();return 0;
 }
 if(!std::strcmp(argv[1],"underreported")){
  const auto baseline=nor;UnderreportedStorage storage;ProfileStore observed(&storage);auto bytes=input(argv[3]);glyph_package::EnvelopePhase phase{};need(glyph_package::DecodeCanonicalRequest(bytes.data(),bytes.size(),phase),"underreported input");observed.BeginRecovery(phase.request.expected_store_incarnation,0);PackageResponse result{};trace_enabled=true;CheckedStorage::SetFaultHook(hook);need(observed.DispatchPackage(phase,result),"underreported source dispatch");trace_enabled=false;CheckedStorage::SetFaultHook(nullptr);response(result,"response");trace();dump_files(path("namespace.bin"));output(path("unwound.nor"),nor);need(nor==baseline&&programs==0&&erases==0&&events.empty(),"used below observed logical byte sum refuses before any publication");summary(true,true,0);shutdown();return 0;
 }
 if(!std::strcmp(argv[1],"digest")){
  auto bytes=input(argv[3]);glyph_package::EnvelopePhase phase{};need(glyph_package::DecodeCanonicalRequest(bytes.data(),bytes.size(),phase),"canonical digest input");uint8_t digest[32];need(PackageCreateDigest(phase,digest),"source token-zero digest");output(path("digest.bin"),Bytes(digest,digest+32));phase.Release();summary(true,true,0);shutdown();return 0;
 }
 if(!std::strcmp(argv[1],"fallback")){
  const std::string kind=argv[3];const auto baseline=nor;FallbackBacking backing;backing.items["/d"]={2};uint8_t value=1;
  profile_store.BeginRecovery(0,0);
  if(kind=="unresolved")PackageStorageFence::Classify(PackageStorageFence::Classification::Unresolved);
  else if(kind=="unsupported")PackageStorageFence::Classify(PackageStorageFence::Classification::Unsupported);
  else if(kind!="unscoped")need(PackageStorageFence::BeginWrite(&backing,kind=="package-helper"?PackageStorageFence::WriteKind::Package:PackageStorageFence::WriteKind::Legacy,kind=="wrong-token"?8:7,fallback_authorize,nullptr),"test bounded scope");
  if(kind=="package-helper"||kind=="revoked-helper"){
   backing.revoke_after_write=kind=="revoked-helper";
   need(!ProfileStoreAtomicCommit::ReplaceInactiveRoot(backing,"/t","/d",&value,1,[](void*,const uint8_t*,size_t){return true;},nullptr),"historical delete helper must fail closed");
   need(backing.writes==(kind=="revoked-helper"?1u:0u)&&backing.removes==0&&backing.renames==0&&backing.items.at("/d")==Bytes{2},"helper denies package scope/rechecks revoked authority before destructive destination mutation");
  }else{
   const char *temporary=kind=="wrong-path"?"/foreign":"/t";
   need(!backing.CheckedWrite(temporary,&value,1,CheckedStorage::Kind::Record)&&!backing.CheckedRename(temporary,"/d",CheckedStorage::Kind::Record)&&!backing.CheckedRemove(kind=="wrong-path"?"/foreign":"/d"),"fallback adapters require matching exact scope");
   need(!ProfileStoreAtomicCommit::ReplaceInactiveRoot(backing,temporary,"/d",&value,1,[](void*,const uint8_t*,size_t){return true;},nullptr),"atomic helper requires matching legacy scope");
   need(backing.writes==0&&backing.removes==0&&backing.renames==0,"denied lower fallback has zero effects");}
  need(nor==baseline&&programs==0&&erases==0,"fallback negatives cannot reach NOR");summary(true,true,0);shutdown();return 0;
 }
 if(!std::strcmp(argv[1],"probe-save")){
  const std::string kind=argv[3];const auto baseline=nor;need(profile_store.Begin(42,3),"managed proposal boot");auto &proposal=ConfigWriteCandidate();need(persistence.LoadConfigChecked(proposal)==Persistence::LoadResult::Loaded,"managed proposal load");
  if(kind=="migration")proposal.ultimate_profile_migration_receipt[0]^=1;
  else {proposal.profile_reference_token=700;Sha256 hash;hash.Update("invalidG6",9);hash.Final(proposal.profile_reference_digest);proposal.profile_reference_result_id=UINT32_MAX;proposal.profile_reference_result_store_generation=UINT32_MAX;proposal.profile_reference_result_mode_index=0;}
  need(!persistence.SaveConfig(proposal),"public Config save rejects invalid managed receipt tuple");need(nor==baseline&&programs==0&&erases==0,"invalid receipt proposal zero-write");dump_files(path("namespace.bin"));output(path("after.nor"),nor);summary(true,true,0);shutdown();return 0;
 }
 if(!std::strcmp(argv[1],"regress")){
  need(argc==5,"regress NOR NATIVE_CREATE OUTDIR");auto source=input(argv[3]);glyph_package::EnvelopePhase request{};need(glyph_package::DecodeCanonicalRequest(source.data(),source.size(),request),"native regression input");need(profile_store.Begin(request.request.expected_store_incarnation,3),"healthy managed regression boot");
  uint32_t raw_id=0,raw_revision=0;for(size_t i=0;i<profile_store.Count();++i){const auto &entry=*profile_store.EntryAt(i);if(!entry.managed_format){raw_id=entry.id;raw_revision=entry.revision;}}
  need(raw_id&&raw_revision,"existing unmanaged raw regression record");
  UltimateProfile profile=UltimateProfile_init_default;profile.schema_version=5;ultimate_native::PayloadLease lease;lease.bytes=request.native.bytes;lease.size=request.native.size;lease.live=true;ultimate_native::Bind(profile,lease);
  auto identity=[](uint64_t token,const char *label){ProfileStore::TransactionIdentity id;id.token=token;Sha256 hash;hash.Update(label,std::strlen(label));hash.Final(id.digest);return id;};
  auto check=[&](const ProfileStore::TransactionResult &result,const char *label){need(result.status==ProfileStore::Status::Ok,std::string("raw ")+label);need(!PackageStorageFence::MutationFenced(),"allowed raw mutation keeps managed namespace healthy");no_handles();dump_files(path(std::string(label)+".namespace.bin"));};
  check(profile_store.Update(raw_id,profile,raw_revision,identity(600,"update")),"update");++raw_revision;
  auto duplicated=profile_store.Duplicate(raw_id,raw_revision,"Raw duplicate",1,identity(601,"duplicate"));check(duplicated,"duplicate");
  check(profile_store.Rename(raw_id,"Renamed raw",profile_store.Generation(),identity(602,"rename")),"rename");
  check(profile_store.Reorder(raw_id,123,profile_store.Generation(),identity(603,"reorder")),"reorder");
  check(profile_store.Delete(duplicated.id,profile_store.Generation(),0,identity(604,"delete")),"delete");
  check(profile_store.Rename(raw_id,"Final raw",profile_store.Generation(),identity(605,"advance")),"advance");
  need(profile_store.CollectGarbage()==ProfileStore::Status::Ok,"allowed raw GC");dump_files(path("gc.namespace.bin"));
  lease.Release();profile.native_payload={};request.Release();
  auto &proposal=ConfigWriteCandidate();need(persistence.LoadConfigChecked(proposal)==Persistence::LoadResult::Loaded,"actual ordinary Config load");const auto generation=persistence.ConfigGeneration(proposal);
  proposal.game_mode_configs[0].ultimate_profile_id=raw_id;proposal.game_mode_configs[0].ultimate_profile_engine=1;proposal.profile_reference_token=700;auto receipt=identity(700,"G6 reference");std::memcpy(proposal.profile_reference_digest,receipt.digest,32);proposal.profile_reference_result_id=raw_id;proposal.profile_reference_result_store_generation=profile_store.Generation();proposal.profile_reference_result_mode_index=0;
  const auto before=nor;
  need(persistence.SaveConfigIfGenerationMatches(proposal,generation^1)==Persistence::SaveResult::Conflict,"stale ordinary generation guard");
  const char original=proposal.game_mode_configs[1].name[0];proposal.game_mode_configs[1].name[0]='X';need(!profile_store.BeginOrdinaryConfigWrite(proposal),"managed row exact bytes guarded");proposal.game_mode_configs[1].name[0]=original;
  if(proposal.rgb_configs_count){proposal.rgb_configs[0].default_color^=1;need(!profile_store.BeginOrdinaryConfigWrite(proposal),"owned RGB exact bytes guarded");proposal.rgb_configs[0].default_color^=1;}
  proposal.game_mode_configs[0].ultimate_profile_id=1;need(!profile_store.BeginOrdinaryConfigWrite(proposal),"G6 cannot point foreign row at managed record");proposal.game_mode_configs[0].ultimate_profile_id=raw_id;
  proposal.profile_reference_token=100;need(!profile_store.BeginOrdinaryConfigWrite(proposal),"G6 cannot reuse package token");proposal.profile_reference_token=700;
  proposal.profile_reference_result_id=UINT32_MAX;proposal.profile_reference_result_store_generation=UINT32_MAX;need(!persistence.SaveConfig(proposal),"public SaveConfig denies impossible G6 ID/generation");proposal.profile_reference_result_id=raw_id;proposal.profile_reference_result_store_generation=profile_store.Generation();
  proposal.game_mode_configs[0].ultimate_profile_id=UINT32_MAX;proposal.profile_reference_result_id=UINT32_MAX;need(!persistence.SaveConfig(proposal),"public SaveConfig denies nonexistent unmanaged G6 ID");proposal.game_mode_configs[0].ultimate_profile_id=raw_id;proposal.profile_reference_result_id=raw_id;
  need(nor==before,"all ordinary candidate guard refusals zero-write");
  need(persistence.SaveConfigIfGenerationMatches(proposal,generation)==Persistence::SaveResult::Saved,"actual allowed G6 save");need(profile_store.ValidateCompactReceipt(proposal),"managed receipt survives ordinary G6 publication");dump_files(path("g6.namespace.bin"));output(path("after.nor"),nor);summary(false,true,0);shutdown();return 0;
 }
 if(!std::strcmp(argv[1],"inspect")){
  const auto baseline=nor;const auto p=programs,e=erases;profile_store.BeginRecovery(0,0);need(nor==baseline&&programs==p&&erases==e,"reboot must not mutate NOR");
  const auto all=requests(argv[3]);bool hidden=true;size_t count=0;PackageResponse target_result{};
  for(const auto &bytes:all){PackageResponse result{};const bool admitted=dispatch(bytes,result);need(admitted,"inspection request canonical");if(!count)target_result=result;response(result,"query-"+std::to_string(count++));
   if(result.has_row_index&&(result.logical==PackageLogicalDisposition_INCOMPLETE||result.logical==PackageLogicalDisposition_PROVEN_ABORTED||result.write_fenced)){
    hidden_id(result.profile_id);
   }
   need(nor==baseline&&programs==p&&erases==e,"every reboot/query/re-entry has zero persistent writes");
  }
  if(argc>=6&&(target_result.write_fenced||target_result.profile_id)){
   auto original=input(argv[5]);PackageResponse result{};need(dispatch(original,result),"explicit exact CREATE re-entry");response(result,"reentry-0");++reentries;
   need(nor==baseline&&programs==p&&erases==e,"accepted/uncertain CREATE cannot repeat publication after restart");
   glyph_package::EnvelopePhase candidate{};need(glyph_package::DecodeCanonicalRequest(original.data(),original.size(),candidate),"re-entry fixture");
   candidate.request.request_token+=1;need(candidate.request.request_token,"test token overflow");
   auto fresh=encoded_envelope(candidate.request);need(dispatch(fresh,result),"fresh token against retained reservation/stale guards");response(result,"reentry-1");++reentries;
   need(nor==baseline&&programs==p&&erases==e,"new token cannot reuse pending ID or bypass stale guards");
   if(target_result.write_fenced){
    if(argc>=7)hidden_id(std::strtoul(argv[6],nullptr,10));
    UltimateProfile proposed=UltimateProfile_init_default;proposed.schema_version=5;ultimate_native::PayloadLease lease;lease.bytes=candidate.native.bytes;lease.size=candidate.native.size;lease.live=true;ultimate_native::Bind(proposed,lease);
    ProfileStore::TransactionIdentity identity;identity.token=candidate.request.request_token+1;identity.digest[0]=1;
    need(profile_store.Create(proposed,"forbidden raw",0,identity).status!=ProfileStore::Status::Ok,"raw writer cannot bypass pending package fence");lease.Release();proposed.native_payload={};
    need(nor==baseline&&programs==p&&erases==e,"raw refusal consumes no ID/token/storage");
   }
   candidate.Release();}
  {const uint8_t byte=1;need(!CheckedStorage::WriteFile("/intruder.tmp",&byte,1,CheckedStorage::Kind::Record),"direct checked writer needs exact admitted scope");need(nor==baseline&&programs==p&&erases==e,"unscoped writer has zero program/erase");}
  dump_files(path("namespace.bin"));output(path("after.nor"),nor);summary(true,hidden,count);shutdown();return 0;
 }
 throw std::runtime_error("unknown mode");
 }catch(const std::exception &e){std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;}}
