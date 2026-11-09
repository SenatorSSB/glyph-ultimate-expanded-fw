#include "core/PackageNamespaceClassifier.hpp"
#include "core/ProfileStoreName.hpp"
#include <cstring>
#include <cstdio>
#include <new>
#include <initializer_list>

namespace package_storage {
namespace {
constexpr const char *kRoots[3] = {"/ultimate-v2-0.bin", "/ultimate-v2-1.bin", "/ultimate-v2.ctrl"};
constexpr const char *kCurrent = "/config-v2.bin", *kPrior = "/config-v2.prev";
bool Eq(const uint8_t *a,const uint8_t *b,size_t n=32){return !std::memcmp(a,b,n);}
bool Zero(const uint8_t *a,size_t n){while(n--)if(*a++)return false;return true;}
bool Is(const char *a,const char *b){return !std::strcmp(a,b);}
bool Starts(const char *a,const char *b){return !std::strncmp(a,b,std::strlen(b));}
bool Ends(const char *a,const char *b){const auto n=std::strlen(a),m=std::strlen(b);return n>=m&&Is(a+n-m,b);}
bool ConfigPath(const char *p){return Is(p,kCurrent)||Is(p,kPrior)||Is(p,"/config-v2.tmp")||Is(p,"/config.bin")||Is(p,"/ultimate-migration.src")||Is(p,"/ultimate-migration.tmp");}
bool RootPath(const char *p){return Is(p,kRoots[0])||Is(p,kRoots[1])||Is(p,"/ultimate-v2-0.tmp")||Is(p,"/ultimate-v2-1.tmp")||Is(p,"/ultimate-dir-0.bin")||Is(p,"/ultimate-dir-1.bin")||Is(p,"/ultimate-dir-0.tmp")||Is(p,"/ultimate-dir-1.tmp");}
bool ControlPath(const char *p){return Is(p,kRoots[2])||Is(p,"/ultimate-v2.ctmp");}
bool TempPath(const char *p){return (Ends(p,".tmp")||Ends(p,".ctmp"))&&(ConfigPath(p)||RootPath(p)||ControlPath(p)||Starts(p,"/ultpkg-"));}
uint32_t Generation(const RootFacts &r){return Get32(r.prefix+8);}
uint32_t Incarnation(const RootFacts &r){return Get32(r.prefix+12);}
uint32_t HighId(const RootFacts &r){return Get32(r.prefix+16);}
uint64_t Token(const RootFacts &r){return Get64(r.prefix+24);}
uint32_t Sequence(const RootFacts &r){return r.format==3?Get32(r.prefix+300):0;}
size_t Count(const RootFacts &r){return Get16(r.prefix+6);}
const uint8_t *Entry(const RootFacts &r,size_t i){return r.prefix+320+i*56;}
bool Marked(const ConfigFacts &c){return c.root_format==3||c.managed_format||c.sequence||c.any_row_marker;}
void ReadIntentFacts(const uint8_t *p,IntentFacts &i){
#define U(name,offset) i.name=Get32(p+offset)
 U(operation,8);U(phase,12);U(terminal,16);U(flags,20);U(incarnation,64);U(id,68);U(revision,72);U(baseline_generation,76);U(generation,80);U(sequence,84);U(baseline_crc,88);U(final_crc,92);U(row,96);U(rgb,100);U(record_bytes,360);U(config_bytes,364);U(baseline_sequence,368);U(baseline_rows,372);U(final_rows,376);U(baseline_rgbs,380);U(final_rgbs,384);U(baseline_high_id,396);
#undef U
 i.token=Get64(p+24);i.baseline_token=Get64(p+388);
#define H(name,offset) std::memcpy(i.name,p+offset,32)
 H(digest,32);H(baseline_config,104);H(final_config,136);H(record,168);H(row_sha,200);H(rgb_sha,232);H(baseline_root,264);H(aggregate,296);H(receipt,328);
#undef H
 Sha256 h;h.Update(p,12);h.Update(p+20,492);h.Final(i.immutable);
}
class Classifier {
 NamespaceReader &reader;const ClassifierOwners &owners;ClassificationWorkspace &w;
 const char *why="namespace uncertainty";
 bool Fail(const char *message){why=message;return false;}
 void Corrupt(const char *message){if(!w.corrupt)why=message;w.corrupt=true;}
 __attribute__((noinline)) bool Hash(const uint8_t *p,size_t n,uint8_t out[32]){
  w.hash.~Sha256();::new(&w.hash)Sha256;w.hash.Update(p,n);w.hash.Final(out);return true;
 }
 bool ReadObject(const char *path,uint8_t *out,size_t cap,size_t &n){
  if(reader.Extent(path,n)!=Probe::Present||n>cap)return false;
  return reader.Read(path,0,out,n);
 }
 __attribute__((noinline)) bool RawHash(const char *path,uint8_t out[32]){
  size_t n=0;if(reader.Extent(path,n)!=Probe::Present)return false;
  w.hash.~Sha256();::new(&w.hash)Sha256;
  for(size_t o=0;o<n;){size_t take=n-o;if(take>sizeof(w.read_chunk))take=sizeof(w.read_chunk);if(!reader.Read(path,o,w.read_chunk,take))return false;w.hash.Update(w.read_chunk,take);o+=take;}
  w.hash.Final(out);return true;
 }
 __attribute__((noinline)) bool HistoricalRetained(){
  if(reader.ObservationFailed())return false;
  // Current compact authority must independently pass. Historical bytes supply
  // no facts and cannot repair a missing/invalid current or another predicate.
  w.scan_config={};
  const bool current=reader.Config(kCurrent,8191,w.scan_config)&&w.scan_config.source_valid;
  w.scan_config={};
  return current&&!reader.ObservationFailed()&&reader.HistoricalRetainedConfig();
 }
 bool Scan(){
  if(!reader.MountedAndConfigured())return Fail("mount/configuration uncertainty");
  // Read every byte before considering future-format markers; unreadable wins.
  for(size_t i=0;;++i){bool eof=false;if(!reader.ObjectAt(i,w.object,eof))return false;if(eof)break;
   if(w.object.directory)return Fail("unsupported namespace directory");
   size_t observed=0;if(reader.Extent(w.object.path,observed)!=Probe::Present||observed!=w.object.bytes)return Fail("namespace/probe disagreement");
   ++w.namespace_files;if(w.logical_bytes>UINT64_MAX-w.object.bytes)return false;w.logical_bytes+=w.object.bytes;
   for(size_t o=0;o<w.object.bytes;){size_t take=w.object.bytes-o;if(take>sizeof(w.read_chunk))take=sizeof(w.read_chunk);if(!reader.Read(w.object.path,o,w.read_chunk,take))return Fail("probe/read uncertainty");o+=take;}
  }
  for(size_t i=0;i<w.namespace_files;++i){bool eof=false;if(!reader.ObjectAt(i,w.object,eof)||eof)return false;
   auto *p=owners.root0;const auto n=w.object.bytes;const size_t head=n<320?n:320;
   if(head&&!reader.Read(w.object.path,0,p,head))return false;
   if(ConfigPath(w.object.path)){
    w.scan_config={};if(!reader.Config(w.object.path,65536,w.scan_config)){
     if(Is(w.object.path,"/config.bin")&&HistoricalRetained())continue;
     Corrupt(Is(w.object.path,kCurrent)?"current Config invalid":Is(w.object.path,kPrior)?"prior Config invalid":Is(w.object.path,"/config.bin")?"config.bin: retained input invalid":"retained migration/staged Config invalid");continue;}
    const auto &c=w.scan_config;w.unsupported|=c.root_format>3||c.managed_format>1||c.newer_row_marker;
    w.managed_observed|=Marked(c);
    if(Marked(c)&&!Is(w.object.path,kCurrent)&&!Is(w.object.path,kPrior)&&!Is(w.object.path,"/config-v2.tmp"))Corrupt("retained Config ownership marker");
   }
   if(RootPath(w.object.path)){
    if(n<6){Corrupt("truncated root");continue;}const auto magic=Get32(p);const auto v=Get16(p+4);
    const bool old=Starts(w.object.path,"/ultimate-dir-");if(magic!=(old?0x31534450u:0x32534450u))Corrupt("root magic");
    if(magic==0x31534450u){w.unsupported|=v>1;if(v<=1&&!LegacyRoot(w.object.path,false))Corrupt("legacy root invalid");}
    if(magic==0x32534450u){w.unsupported|=v>3||(v==3&&n>=300&&Get32(p+296)>1);w.managed_observed|=v==3;if(v<2)Corrupt("compact root version");
     if(v==2){size_t z=0;if(!ReadObject(w.object.path,owners.record,4128,z)||z!=3908||!ValidV2(owners.record))Corrupt("compact root invalid");}
     if(v==3&&!old){if(!LoadRoot(w.object.path,w.roots[0],owners.root0,false))Corrupt("managed root invalid");}
    }
   }
   if(ControlPath(w.object.path)){
    if(n<22||Get32(p)!=0x32435350u||Get32(p+16)!=0x32534450u)Corrupt("control header invalid");
    else {const auto v=Get16(p+20);w.unsupported|=v>3||(v==3&&n>=316&&Get32(p+312)>1);w.managed_observed|=v==3;}
   }
   if(Starts(w.object.path,"/ultpkg-"))w.managed_observed=true;
   if((Starts(w.object.path,"/ultpkg-")||(Starts(w.object.path,"/ultimate-")&&(Ends(w.object.path,".bin")||Ends(w.object.path,".tmp"))))&&n>=8&&Get32(p)==0x31525055u){
    const auto v=Get16(p+4);w.unsupported|=v>2||(v==2&&n>=120&&Get32(p+116)>1);
    if(v==2){w.managed_observed=true;if(!Starts(w.object.path,"/ultpkg-"))Corrupt("managed record namespace");}
   }
  }
  return true;
 }
 bool ValidV2(const uint8_t *p){
  if(!SourcePrefixValid(p)||Get16(p+4)!=2||Crc32(p,3904)!=Get32(p+3904)||!Zero(p+264,56))return false;
  for(size_t i=0;i<Get16(p+6);++i)if(!Zero(p+320+i*56+53,3))return false;
  return true;
 }
 __attribute__((noinline)) bool LegacyRoot(const char *path,bool migration){
  size_t n=0;auto *p=owners.record;if(!ReadObject(path,p,4128,n)||n!=2620||Get32(p)!=0x31534450u||Get16(p+4)!=1||Crc32(p,2616)!=Get32(p+2616)||Get16(p+6)>64||!Get32(p+8)||!Get32(p+12)||Get32(p+24)>2)return false;
  if(migration&&Get32(p+24)!=2)return false;
  for(size_t i=0;i<Get16(p+6);++i){const auto *e=p+32+i*40;
   if(!Get32(e)||Get32(e)>Get32(p+16)||!Get32(e+4)||Get32(e+8)>=Get32(e+4))return false;
   for(size_t j=0;j<i;++j)if(Get32(p+32+j*40)==Get32(e))return false;
   std::memcpy(w.read_chunk,e+20,17);w.read_chunk[17]=0;if(!ProfileStoreNameValid(reinterpret_cast<const char*>(w.read_chunk),18))return false;
  }
  if(Get32(p+24)&&!Get32(p+2608)&&!Get32(p+2612))return false;
  for(unsigned i=0;i<2;++i)if(Get32(p+2608+i*4)>Get32(p+16))return false;
  return true;
 }
 bool LoadRoot(const char *path,RootFacts &r,uint8_t *owner,bool control){
  size_t n=0;if(reader.Extent(path,n)!=Probe::Present)return false;
  const size_t lead=control?16:0;r.prefix=owner+lead;
  if(n<lead+8||!reader.Read(path,0,owner,lead+8))return false;
  r.format=Get16(r.prefix+4);if(r.format!=2&&r.format!=3)return false;
  if(n!=lead+(r.format==3?kRootBytes:3908))return false;
  if(!reader.Read(path,lead,r.prefix,kRootPrefixBytes))return false;
  if(!reader.Read(path,n-4,r.prefix+3904,4))return false;
  if(r.format==3){
   if(!reader.Read(path,lead+3904,owners.intent,512))return false;
   RootView view{r.prefix,owners.intent,r.prefix+3904};if(!RootValid(view))return false;
   if(control&&(!ControlValid(owner,view)||!ControlPhaseValid(owner,owners.intent)))return false;
   HashRoot(view,r.sha);ReadIntentFacts(owners.intent,r.intent);
  }else{
   if(!ValidV2(r.prefix))return false;
   Hash(r.prefix,3908,r.sha);r.intent={};
   if(control&&(Get32(owner)!=0x32435350u||Get32(owner+4)!=2||Get32(owner+8)!=3908||Get32(owner+12)!=(Crc32(owner,12)^Crc32(r.prefix,3908))))return false;
  }
  if(control)r.control_phase=Get32(owner+4);
  r.present=true;return true;
 }
 bool Slots(){
  auto &a=w.roots[0];auto &b=w.roots[1];
  if(Incarnation(a)!=Incarnation(b))return false;
  const auto ga=Generation(a),gb=Generation(b);const auto &newer=ga>=gb?a:b;const auto &older=ga>=gb?b:a;
  if(ga==gb&&!Eq(a.sha,b.sha))return false;
  if(Generation(newer)-Generation(older)>1||HighId(newer)<HighId(older)||Token(newer)<Token(older))return false;
  if(ga!=gb&&((ga&1u)!=0||(gb&1u)!=1))return false;
  if(a.format==3&&b.format==3){
   if(Sequence(newer)<Sequence(older))return false;
   for(size_t i=0;i<Count(older);++i){const auto *e=Entry(older,i);if(!e[53])continue;bool found=false;for(size_t j=0;j<Count(newer);++j)if(Eq(e,Entry(newer,j),56))found=true;if(!found)return false;}
  }
  return true;
 }
 bool LoadConfigs(){
  w.current={};w.prior={};size_t n=0;const auto c=reader.Extent(kCurrent,n);if(c==Probe::Error)return false;
  if(c==Probe::Present&&!reader.Config(kCurrent,8191,w.current))return false;
  const auto p=reader.Extent(kPrior,n);if(p==Probe::Error)return false;
  return p!=Probe::Present||reader.Config(kPrior,8191,w.prior);
 }
 bool NoTemps(){
  for(size_t i=0;i<w.namespace_files;++i){bool eof=false;if(!reader.ObjectAt(i,w.object,eof)||eof||TempPath(w.object.path))return false;}return true;
 }
 bool RootAppend(const RootFacts &base,const RootFacts &next,const IntentFacts &intent){
  return Count(next)==Count(base)+1&&Eq(base.prefix+320,next.prefix+320,56*Count(base))&&Eq(base.prefix+20,next.prefix+20,4)&&Eq(base.prefix+80,next.prefix+80,184)&&Generation(next)==intent.generation&&Incarnation(next)==Incarnation(base);
 }
 bool StoreReceiptEqual(const uint8_t *prefix,const uint8_t *record){
  return Eq(prefix+32,record+40)&&Get32(prefix+68)==Get32(record+12)&&Get32(prefix+72)==Get32(record+16)&&Get32(prefix+64)==0&&Get32(prefix+76)==Get32(record+120);
 }
 bool SharedReceipts(){
  const auto &selected=Generation(w.roots[0])>=Generation(w.roots[1])?w.roots[0]:w.roots[1];
  for(unsigned i=0;i<3;++i){const auto &a=w.roots[i];
   for(unsigned j=0;j<i;++j){const auto &b=w.roots[j];if(Token(a)&&Token(a)==Token(b)&&(!Eq(a.prefix+32,b.prefix+32)||!Eq(a.prefix+64,b.prefix+64,16)))return false;}
   for(const auto *c:{&w.current,&w.prior})if(c->reference_token&&c->reference_token==Token(a))return false;
  }
  for(const auto *c:{&w.current,&w.prior}){
   if(!c->body_bytes)continue;
   if(c->reference_token){
    if(c->store_format!=1||c->incarnation!=Incarnation(selected)||!c->reference_digest_valid||!c->reference_generation||c->reference_generation>Generation(selected)||c->reference_id>HighId(selected)||c->reference_row>=30)return false;
    for(unsigned i=0;i<2;++i)if(Generation(w.roots[i])==c->reference_generation&&c->reference_id>HighId(w.roots[i]))return false;
   }else if(!Zero(c->reference_digest,32)||c->reference_id||c->reference_generation||c->reference_row)return false;
  }
  if(w.current.reference_token&&w.current.reference_token==w.prior.reference_token&&(!Eq(w.current.reference_digest,w.prior.reference_digest)||w.current.reference_id!=w.prior.reference_id||w.current.reference_generation!=w.prior.reference_generation||w.current.reference_row!=w.prior.reference_row))return false;
  for(size_t i=0;i<w.namespace_files;++i){bool eof=false;if(!reader.ObjectAt(i,w.object,eof)||eof)return false;
   if(!Starts(w.object.path,"/ultpkg-")||!Ends(w.object.path,".bin"))continue;
   size_t n=0;if(!ReadObject(w.object.path,owners.record,4128,n)||!RecordValid(owners.record,n))return false;const auto token=Get64(owners.record+32);
   for(unsigned j=0;j<3;++j)if(Token(w.roots[j])==token&&!StoreReceiptEqual(w.roots[j].prefix,owners.record))return false;
   for(const auto *c:{&w.current,&w.prior})if(c->reference_token==token)return false;
   // Scan earlier namespace records without another record owner: retain only
   // checked semantic receipt identity, then reread this file after each compare.
   const uint32_t id=Get32(owners.record+12),rev=Get32(owners.record+16),gen=Get32(owners.record+120);std::memcpy(w.record_sha,owners.record+40,32);
   for(size_t k=0;k<i;++k){if(!reader.ObjectAt(k,w.object,eof)||eof)return false;if(!Starts(w.object.path,"/ultpkg-")||!Ends(w.object.path,".bin"))continue;
    if(!ReadObject(w.object.path,owners.record,4128,n)||!RecordValid(owners.record,n))return false;
    if(Get64(owners.record+32)==token&&(!Eq(w.record_sha,owners.record+40)||Get32(owners.record+12)!=id||Get32(owners.record+16)!=rev||Get32(owners.record+120)!=gen))return false;
   }
  }
  return true;
 }
 __attribute__((noinline)) bool MigrationReceipt(const RootFacts &root,const ConfigFacts &config){
  const auto *p=root.prefix;
  static constexpr char domain[]="Glyph.ProfileStore.Migration.v2";
  w.hash.~Sha256();::new(&w.hash)Sha256;w.hash.Update(domain,sizeof(domain));
  uint8_t words[16];Put32(words,Get32(p+80));Put32(words+4,Incarnation(root));Put32(words+8,Get32(p+84));Put32(words+12,0);w.hash.Update(words,16);w.hash.Update(p+88,32);
  for(size_t i=0;i<Get32(p+84);++i){Put32(words,Get32(p+120+i*4));Put32(words+4,Get32(p+128+i*4));w.hash.Update(words,8);w.hash.Update(p+136+i*32,32);}
  w.hash.Final(w.digest);return Eq(w.digest,p+200)&&Eq(w.digest,config.migration_receipt);
 }
 bool Migration(const RootFacts &root,const ConfigFacts &config){
  const auto *p=root.prefix;const auto state=Get32(p+20);if(!state)return true;if(state!=2)return false;
  if(!MigrationReceipt(root,config))return false;
  if(Get32(p+80)==2){if(!RawHash("/ultimate-migration.src",w.digest)||!Eq(w.digest,p+88))return false;}
  if(Get32(p+80)==3){
   uint32_t generations[2]{};bool present[2]{};const char *paths[2]={"/ultimate-dir-0.bin","/ultimate-dir-1.bin"};
   for(unsigned i=0;i<2;++i){size_t n=0;const auto pr=reader.Extent(paths[i],n);if(pr==Probe::Error)return false;if(pr==Probe::Absent)continue;
    if(!LegacyRoot(paths[i],true)||Get32(owners.record+12)!=Incarnation(root)||Get32(owners.record+8)>Generation(root))return false;
    present[i]=true;generations[i]=Get32(owners.record+8);if(!RawHash(paths[i],i?w.row_sha:w.rgb_sha))return false;
   }
   if(present[0]||present[1]){
    const unsigned newest=present[1]&&(!present[0]||generations[1]>generations[0])?1:0;
    if(present[0]&&present[1]&&((generations[newest]-generations[newest^1])>1||(generations[0]==generations[1]&&!Eq(w.row_sha,w.rgb_sha))))return false;
    if(!Eq(newest?w.row_sha:w.rgb_sha,p+88)||!LegacyRoot(paths[newest],true))return false;
    unsigned count=0;for(unsigned i=0;i<2;++i){const auto id=Get32(owners.record+2608+i*4);if(!id)continue;
     if(count>=Get32(p+84)||id!=Get32(p+120+count*4)||Get32(p+128+count*4)!=1)return false;
     ++count;
    }if(count!=Get32(p+84))return false;
   }
  }
  for(size_t i=0;i<Get32(p+84);++i){auto *path=reinterpret_cast<char*>(w.read_chunk);std::snprintf(path,32,"/ultimate-%08x-%08x.bin",unsigned(Get32(p+120+i*4)),unsigned(Get32(p+128+i*4)));
   size_t n=0;if(!ReadObject(path,owners.record,4128,n)||n<=32||Get32(owners.record)!=0x31525055u||Get16(owners.record+4)!=1||Get16(owners.record+6)!=1||Get32(owners.record+8)!=Incarnation(root)||Get32(owners.record+12)!=Get32(p+120+i*4)||Get32(owners.record+16)!=Get32(p+128+i*4)||Get32(owners.record+20)!=n-32||Crc32(owners.record,24)!=Get32(owners.record+24)||Crc32(owners.record+32,n-32)!=Get32(owners.record+28)||!reader.LegacyProfile(owners.record+32,n-32))return false;
   Hash(owners.record+32,n-32,w.digest);if(!Eq(w.digest,p+136+i*32))return false;
  }return true;
 }
 bool OwnedSet(const RootFacts &root,const char *config_path,const ConfigFacts &config,bool all_extra=false,uint32_t extra_id=0){
  auto &scratch=w.owned; scratch={};
  scratch.root=&root; scratch.config=&config; scratch.config_path=config_path;
  scratch.all_extra=all_extra; scratch.extra_id=extra_id;
  if((*scratch.root).format!=3||!(*scratch.config).source_valid||(*scratch.config).embedded_profiles||(*scratch.config).store_format!=1||(*scratch.config).incarnation!=Incarnation((*scratch.root))||(*scratch.config).root_format!=3||(*scratch.config).managed_format!=1||(*scratch.config).sequence!=Sequence((*scratch.root)))return false;
  for(size_t i=0;i<Count((*scratch.root));++i)if(Entry((*scratch.root),i)[53])++scratch.managed_count;

  for(size_t i=0;i<(*scratch.config).rows;++i){if(!reader.Row(scratch.config_path,i,w.row))return false;
   const uint8_t *owned=nullptr;for(size_t j=0;j<Count((*scratch.root));++j)if(Entry((*scratch.root),j)[53]&&Get32(Entry((*scratch.root),j))==w.row.id)owned=Entry((*scratch.root),j);
   if(owned){if(w.row.marker!=1||unsigned(owned[54]-1)!=i)return false;++scratch.mapped;}else if(w.row.marker)return false;
  }if(scratch.mapped!=scratch.managed_count)return false;
  static constexpr char domain[]="Glyph.Package.Set.v1";
  w.aggregate_hash.~Sha256();::new(&w.aggregate_hash)Sha256;w.aggregate_hash.Update(domain,sizeof(domain));
Put32(scratch.word,Incarnation((*scratch.root)));Put32(scratch.word+4,scratch.managed_count);w.aggregate_hash.Update(scratch.word,8);

  for(scratch.item=0;scratch.item<scratch.managed_count;++scratch.item){
   scratch.e=nullptr;for(size_t j=0;j<Count((*scratch.root));++j){const auto *candidate=Entry((*scratch.root),j);if(candidate[53]&&Get32(candidate)>scratch.previous_id&&(!scratch.e||Get32(candidate)<Get32(scratch.e)))scratch.e=candidate;}
   if(!scratch.e)return false;
   scratch.id=Get32(scratch.e);scratch.previous_id=scratch.id;
   if(!reader.Row(scratch.config_path,scratch.e[54]-1,w.row)||w.row.mode!=3||w.row.legacy||w.row.engine!=1||w.row.rgb!=scratch.e[55])return false;
   std::memcpy(w.row_sha,w.row.sha,32);
   Hash(nullptr,0,w.rgb_sha);
   if(scratch.e[55]){
    if(scratch.e[55]>(*scratch.config).rgbs||!reader.Rgb(scratch.config_path,scratch.e[55]-1,w.rgb_sha))return false;
    unsigned shares=0;for(size_t j=0;j<(*scratch.config).rows;++j){if(!reader.Row(scratch.config_path,j,w.other_row))return false;if(w.other_row.rgb==scratch.e[55])++shares;}if(shares!=1)return false;
   }
   auto *path=reinterpret_cast<char*>(w.read_chunk);if(!RecordPath(path,32,scratch.id,Get32(scratch.e+4),false))return false;
   scratch.n=0;if(!ReadObject(path,owners.record,4128,scratch.n)||!RecordValid(owners.record,scratch.n))return false;
   const auto *r=owners.record;scratch.token=Get64(r+32);scratch.sequence=Get32(r+124);
   if(Get32(r+8)!=Incarnation((*scratch.root))||Get32(r+12)!=scratch.id||Get32(r+16)!=Get32(scratch.e+4)||Get32(r+72)!=unsigned(scratch.e[54]-1)||Get32(r+76)!=scratch.e[55]||Get32(r+120)>Generation((*scratch.root))||scratch.sequence>Sequence((*scratch.root))||scratch.token>Token((*scratch.root))||scratch.token==(*scratch.config).reference_token||!reader.Native(scratch.config_path,scratch.e[54]-1,r,scratch.n))return false;
   Hash(r,scratch.n,w.record_sha);Hash(scratch.e,56,w.entry_sha);
   const auto &intent=(*scratch.root).intent;
   if(intent.operation&&scratch.id==intent.id){
    Hash(r,128,w.digest);
    if(scratch.n!=intent.record_bytes||!Eq(w.record_sha,intent.record)||!Eq(w.digest,intent.receipt)||scratch.token!=intent.token||!Eq(r+40,intent.digest)||!Eq(r+80,intent.baseline_config)||Get32(r+120)!=intent.generation||scratch.sequence!=intent.sequence||!Eq(w.row_sha,intent.row_sha)||(intent.flags?!Eq(w.rgb_sha,intent.rgb_sha):!Zero(intent.rgb_sha,32)))return false;
   }
   Put32(scratch.word,scratch.id);Put32(scratch.word+4,Get32(scratch.e+4));Put32(scratch.word+8,scratch.e[54]);Put32(scratch.word+12,scratch.e[55]);w.aggregate_hash.Update(scratch.word,16);w.aggregate_hash.Update(w.row_sha,32);w.aggregate_hash.Update(w.rgb_sha,32);w.aggregate_hash.Update(w.record_sha,32);w.aggregate_hash.Update(w.entry_sha,32);
   for(size_t j=0;j<Count((*scratch.root));++j){const auto *old=Entry((*scratch.root),j);if(!old[53]||Get32(old)>=scratch.id)continue;
    if(!RecordPath(path,32,Get32(old),Get32(old+4),false)||!ReadObject(path,owners.record,4128,scratch.n)||!RecordValid(owners.record,scratch.n))return false;
    if(Get64(owners.record+32)==scratch.token||Get32(owners.record+124)==scratch.sequence)return false;
   }
  }
  w.aggregate_hash.Final(w.digest);if(!Eq(w.digest,(*scratch.root).prefix+264))return false;
  if(scratch.all_extra)return true;
  for(size_t i=0;i<w.namespace_files;++i){bool eof=false;if(!reader.ObjectAt(i,w.object,eof)||eof)return false;if(!Starts(w.object.path,"/ultpkg-"))continue;
   bool known=false;auto *path=reinterpret_cast<char*>(w.read_chunk);
   for(size_t j=0;j<Count((*scratch.root));++j){scratch.e=Entry((*scratch.root),j);if(scratch.e[53]&&RecordPath(path,32,Get32(scratch.e),Get32(scratch.e+4),false)&&Is(path,w.object.path))known=true;}
   if(scratch.extra_id&&RecordPath(path,32,scratch.extra_id,1,false)&&Is(path,w.object.path))known=true;
   if(!known)return false;
  }return true;
 }
 bool Legacy(){
  const auto &a=w.roots[0],&b=w.roots[1],&ctrl=w.roots[2];const auto &selected=Generation(a)>=Generation(b)?a:b;
  if(a.format!=2||b.format!=2||ctrl.format!=2)return Fail("legacy: root format");
  if(!Eq(ctrl.sha,selected.sha))return Fail("legacy: control differs");
  if(Get32(selected.prefix+20)==1)return Fail("legacy: migration pending");
  if(!w.current.source_valid)return Fail("legacy: Config source invalid");
  if(w.current.managed_format||w.current.any_row_marker)return Fail("legacy: Config ownership");
  if(w.current.embedded_profiles)return Fail("legacy: embedded profiles");
  if(w.current.store_format!=1||w.current.incarnation!=Incarnation(selected)||w.current.root_format!=2)return Fail("legacy: Config/store mismatch");
  if(!NoTemps())return Fail("legacy: temporary present");
  if(!Migration(selected,w.current))return Fail("legacy: migration proof");
  if(!SharedReceipts())return Fail("legacy: shared receipts");
  return true;
 }
 bool HistoricalPrior(const IntentFacts &intent){
  if(!w.prior.body_bytes||!Marked(w.prior))return true;
  for(unsigned i=0;i<2;++i)if(w.roots[i].format==3&&OwnedSet(w.roots[i],kPrior,w.prior,true))return true;
  if(!w.current.body_bytes)return false;
  for(unsigned i=0;i<2;++i){const auto &r=w.roots[i];const auto &h=r.intent;
   if(r.format!=3||h.phase!=5||h.terminal!=3||!OwnedSet(r,kCurrent,w.current,true))continue;
   if(Eq(w.prior.sha,h.baseline_config)&&w.prior.crc==h.baseline_crc&&w.prior.rows==h.baseline_rows&&w.prior.rgbs==h.baseline_rgbs&&w.prior.store_format==1&&w.prior.incarnation==Incarnation(r)&&w.prior.root_format==(h.baseline_sequence?3u:2u)&&w.prior.managed_format==(h.baseline_sequence?1u:0u)&&w.prior.sequence==h.baseline_sequence&&w.prior.source_valid)return true;
  }(void)intent;return false;
 }
 public:
 Classifier(NamespaceReader &r,const ClassifierOwners &o):reader(r),owners(o),w(o.work){}
 __attribute__((noinline)) Classification &Run(){
  w.classification={}; auto &result=w.classification; w.run={}; auto &run_state=w.run;
  if(!Scan()){result.diagnostic=why;return result;}
  if(reader.ObservationFailed()){result.diagnostic="checked I/O uncertainty";return result;}
  if(w.unsupported){result.floor=Floor::Unsupported;result.diagnostic="recognized newer storage";return result;}
  if(w.corrupt){result.diagnostic=why;return result;}
  if(!w.namespace_files){result.floor=Floor::NoManaged;result.logical=Logical::None;result.write_fenced=false;result.diagnostic="mounted empty namespace";return result;}
  run_state.next_phase=1; return result;
 }
 __attribute__((noinline)) Classification &RunRoots(){
  auto &result=w.classification;
  auto &run_state=w.run; run_state.next_phase=0;
  if(!LoadRoot(kRoots[0],w.roots[0],owners.root0,false)){result.diagnostic="root0: absent/invalid";return result;}
  if(!LoadRoot(kRoots[1],w.roots[1],owners.root1,false)){result.diagnostic="root1: absent/invalid";return result;}
  if(!LoadRoot(kRoots[2],w.roots[2],owners.control,true)){result.diagnostic="control: absent/invalid";return result;}
  if(!Slots()){result.diagnostic="root slots disagree";return result;}
  if(!LoadConfigs()){result.diagnostic="Config observation invalid";return result;}
  const auto &control=w.roots[2];const auto &intent=control.intent;
  if(!w.managed_observed){
   if(!Legacy()){result.diagnostic=why;return result;}
   result.floor=Floor::NoManaged;result.logical=Logical::None;result.write_fenced=false;result.diagnostic="validated no-managed legacy";
   const auto &selected=Generation(w.roots[0])>=Generation(w.roots[1])?w.roots[0]:w.roots[1];
   result.incarnation=Incarnation(selected);result.generation=Generation(selected);return result;
  }
  if(control.format!=3||intent.operation!=15||Incarnation(control)!=intent.incarnation||HighId(control)<intent.id||Token(control)<intent.token){result.diagnostic="invalid package reservation";return result;}

  for(unsigned i=0;i<2;++i){const auto &r=w.roots[i];
   if(Eq(r.sha,intent.baseline_root))run_state.baseline_root_found=true;
   if(r.format==2){++run_state.v2;if(Incarnation(r)!=intent.incarnation||Generation(r)>intent.baseline_generation){result.diagnostic="invalid V2 transition baseline";return result;}}
   else if(!run_state.selected||Generation(r)>Generation(*run_state.selected))run_state.selected=&r;
  }
  if(run_state.v2){
   bool first=false,next=false;
   if(!intent.baseline_sequence)for(unsigned i=0;i<2;++i)if(w.roots[i].format==2&&Eq(w.roots[i].sha,intent.baseline_root))first=true;
   if(run_state.selected&&Eq(run_state.selected->sha,intent.baseline_root)){next=true;for(unsigned i=0;i<2;++i)if(w.roots[i].format==2&&Generation(w.roots[i])+1!=intent.baseline_generation)next=false;}
   if(!first&&!next){result.diagnostic="unproven mixed-root transition";return result;}
  }
  if(run_state.selected&&Get32(run_state.selected->prefix+20)==1){result.diagnostic="migration pending";return result;}
  run_state.baseline_selected=run_state.selected&&Generation(*run_state.selected)==intent.baseline_generation;
  run_state.store_published=run_state.selected&&(Generation(*run_state.selected)==intent.generation||(intent.terminal==3&&Generation(*run_state.selected)>intent.generation));
  if((run_state.baseline_selected&&(!Eq(run_state.selected->sha,intent.baseline_root)||Sequence(*run_state.selected)!=intent.baseline_sequence))||(run_state.selected&&!run_state.baseline_selected&&!run_state.store_published)||!NoTemps()){result.diagnostic="selected root/temp disagreement";return result;}
  run_state.baseline_current=w.current.body_bytes&&Eq(w.current.sha,intent.baseline_config);
  run_state.baseline_prior=w.prior.body_bytes&&Eq(w.prior.sha,intent.baseline_config);
  for(unsigned i=0;i<2;++i){const auto &r=w.roots[i];
   if(Generation(r)==intent.baseline_generation){
    if(!Eq(r.sha,intent.baseline_root)||HighId(r)!=intent.baseline_high_id||Token(r)>intent.baseline_token||Sequence(r)!=intent.baseline_sequence){result.diagnostic="retained baseline differs";return result;}
    for(unsigned j=0;j<3;++j)if(w.roots[j].format==3&&Generation(w.roots[j])==intent.generation&&!RootAppend(r,w.roots[j],intent)){result.diagnostic="changed preceding root entries/provenance";return result;}
   }
   if(r.format==3){
    if(r.intent.token==intent.token&&Sequence(r)==intent.sequence&&!Eq(r.intent.immutable,intent.immutable)){result.diagnostic="immutable intent mismatch";return result;}
    if(r.intent.phase!=3&&r.intent.phase!=5){result.diagnostic="unreachable visible root phase";return result;}
   }
  }
  if(run_state.selected)for(unsigned i=0;i<3;++i)if(!Eq(w.roots[i].prefix+20,run_state.selected->prefix+20,4)||!Eq(w.roots[i].prefix+80,run_state.selected->prefix+80,184)){result.diagnostic="migration provenance changed";return result;}
  run_state.next_phase=2; return result;
 }
 __attribute__((noinline)) Classification &RunBaseline(){
  auto &result=w.classification;
  auto &run_state=w.run; run_state.next_phase=0;
  const auto &control=w.roots[2];
  const auto &intent=control.intent;
  if(run_state.baseline_current&&intent.terminal!=3){
   uint64_t high=0;for(unsigned i=0;i<2;++i)if(Generation(w.roots[i])<=intent.baseline_generation&&Token(w.roots[i])>high)high=Token(w.roots[i]);
   for(const auto *c:{&w.current,&w.prior})if(c->body_bytes&&c->store_format==1&&c->incarnation==intent.incarnation&&c->reference_token>high)high=c->reference_token;
   for(size_t i=0;i<w.namespace_files;++i){bool eof=false;if(!reader.ObjectAt(i,w.object,eof)||eof)return result;
    if(!Starts(w.object.path,"/ultpkg-")||!Ends(w.object.path,".bin"))continue;
    size_t n=0;if(!ReadObject(w.object.path,owners.record,4128,n)||!RecordValid(owners.record,n))return result;
    if(Get32(owners.record+12)!=intent.id&&Get64(owners.record+32)>high)high=Get64(owners.record+32);
   }
   if(high!=intent.baseline_token){result.diagnostic="baseline omitted shared high-water";return result;}
  }
  if(run_state.baseline_current||run_state.baseline_prior){
   const auto &base=run_state.baseline_current?w.current:w.prior;const char *base_path=run_state.baseline_current?kCurrent:kPrior;
   if(!base.source_valid||base.store_format!=1||base.incarnation!=intent.incarnation||base.root_format!=(intent.baseline_sequence?3u:2u)||base.managed_format!=(intent.baseline_sequence?1u:0u)||base.sequence!=intent.baseline_sequence||base.crc!=intent.baseline_crc||base.rows!=intent.baseline_rows||base.rgbs!=intent.baseline_rgbs||(!run_state.baseline_root_found&&intent.terminal!=3)){result.diagnostic="baseline Config mismatch";return result;}
   const RootFacts *baseline=nullptr;for(unsigned i=0;i<2;++i)if(Eq(w.roots[i].sha,intent.baseline_root))baseline=&w.roots[i];
   if(!baseline){if(intent.baseline_token<base.reference_token)return result;}
   else{
    if(Token(*baseline)>intent.baseline_token||base.reference_token>intent.baseline_token||HighId(*baseline)!=intent.baseline_high_id||Generation(*baseline)!=intent.baseline_generation||!Migration(*baseline,base))return result;
    if(baseline->format==3){if(!OwnedSet(*baseline,base_path,base,false,intent.id)){result.diagnostic="baseline managed set mismatch";return result;}}
    else{
     if(base.managed_format||base.any_row_marker)return result;
     for(size_t i=0;i<w.namespace_files;++i){bool eof=false;if(!reader.ObjectAt(i,w.object,eof)||eof)return result;if(!Starts(w.object.path,"/ultpkg-"))continue;auto *path=reinterpret_cast<char*>(w.read_chunk);if(!RecordPath(path,32,intent.id,1,false)||!Is(path,w.object.path))return result;}
    }
   }
  }
  run_state.next_phase=3; return result;
 }
 __attribute__((noinline)) Classification &RunFinal(){
  auto &result=w.classification;
  auto &run_state=w.run; run_state.next_phase=0;
  const auto &control=w.roots[2];
  const auto &intent=control.intent;
  if(intent.terminal!=3&&!HistoricalPrior(intent)){result.diagnostic="marked prior unproven";return result;}
  if(!SharedReceipts()){result.diagnostic="shared transaction receipt conflict";return result;}
  auto *path=reinterpret_cast<char*>(w.read_chunk);if(!RecordPath(path,32,intent.id,1,false))return result;
  size_t n=0;const auto probe=reader.Extent(path,n);
  if(probe==Probe::Error)return result;
  if(probe==Probe::Absent){
   if(run_state.store_published||!run_state.baseline_current||(run_state.v2!=2&&!run_state.baseline_selected)||control.control_phase!=1)return result;
   result.logical=Logical::ProvenAborted;result.diagnostic="reserved identity; expected record absent";return result;
  }
  if(n>4128||!reader.Read(path,0,owners.record,n)||!RecordValid(owners.record,n)){result.diagnostic="managed record invalid";return result;}
  const auto *record=owners.record;
  Hash(record,n,w.record_sha);Hash(record,128,w.digest);
  if(n!=intent.record_bytes||!Eq(w.record_sha,intent.record)||!Eq(w.digest,intent.receipt)||Get32(record+8)!=intent.incarnation||Get32(record+12)!=intent.id||Get64(record+32)!=intent.token||!Eq(record+40,intent.digest)||Get32(record+72)!=intent.row||Get32(record+76)!=intent.rgb||!Eq(record+80,intent.baseline_config)||Get32(record+120)!=intent.generation||Get32(record+124)!=intent.sequence||record[128]!=8||record[129]!=5||!reader.LegacyProfile(record+128,n-128)){result.diagnostic="managed receipt/native mismatch";return result;}
  if(!run_state.store_published){
   if(!run_state.baseline_current||(control.control_phase!=1&&control.control_phase!=2)||(intent.phase!=1&&intent.phase!=2))return result;
   result.logical=Logical::Incomplete;result.diagnostic="record published; store absent";return result;
  }
  if(Generation(*run_state.selected)<intent.generation||Sequence(*run_state.selected)!=intent.sequence||!Eq(run_state.selected->intent.immutable,intent.immutable)||run_state.selected->intent.phase<intent.phase)return result;
  if(run_state.baseline_current||(!w.current.body_bytes&&run_state.baseline_prior)){
   if(intent.terminal==3||run_state.selected->intent.terminal==3||intent.phase>=4)return result;
   result.logical=Logical::Incomplete;result.diagnostic="store published; Config uninstalled";return result;
  }
  if(!w.current.body_bytes||!Migration(*run_state.selected,w.current)||w.current.reference_token==Token(*run_state.selected))return result;
  if((intent.terminal!=3||run_state.baseline_prior)&&(!Eq(w.current.sha,intent.final_config)||w.current.crc!=intent.final_crc||w.current.body_bytes!=intent.config_bytes))return result;
  if(run_state.baseline_prior&&!reader.AppendConfig(kPrior,kCurrent))return result;
  if(!OwnedSet(*run_state.selected,kCurrent,w.current)||!Eq(run_state.selected->prefix+264,intent.aggregate))return result;
  if(!reader.Row(kCurrent,intent.row,w.row)||!Eq(w.row.sha,intent.row_sha))return result;
  if(intent.flags){if(!reader.Rgb(kCurrent,intent.rgb-1,w.rgb_sha)||!Eq(w.rgb_sha,intent.rgb_sha))return result;}else if(!Zero(intent.rgb_sha,32))return result;
  if(w.current.reference_token==intent.token)return result;
  if(w.prior.body_bytes&&!run_state.baseline_prior){
   if(w.prior.managed_format){bool matched=false;for(unsigned i=0;i<2;++i)if(w.roots[i].format==3&&OwnedSet(w.roots[i],kPrior,w.prior,true))matched=true;if(!matched)return result;}
   else return result;
  }
  if(w.prior.body_bytes&&w.current.store_format==1&&w.prior.store_format==1&&w.current.incarnation==intent.incarnation&&w.prior.incarnation==intent.incarnation&&w.current.root_format==3&&w.prior.root_format==3&&w.current.managed_format==1&&w.prior.managed_format==1&&w.current.reference_token<w.prior.reference_token)return result;
  const bool terminal=control.control_phase==3&&intent.phase==5&&intent.terminal==3&&run_state.selected->intent.phase==5&&run_state.selected->intent.terminal==3;
  if(terminal&&!Eq(control.sha,run_state.selected->sha))return result;
  result.logical=Logical::Committed;result.write_fenced=!terminal;result.floor=terminal?Floor::Supported:Floor::Unresolved;result.diagnostic=terminal?"exact installed pair and terminal metadata":"exact installed pair; terminal metadata incomplete";
  result.incarnation=Incarnation(*run_state.selected);result.generation=Generation(*run_state.selected);result.package_sequence=Sequence(*run_state.selected);
  result.high_token=Token(control);for(unsigned i=0;i<2;++i)if(Token(w.roots[i])>result.high_token)result.high_token=Token(w.roots[i]);
  if(w.current.reference_token>result.high_token)result.high_token=w.current.reference_token;
  if(w.prior.reference_token>result.high_token)result.high_token=w.prior.reference_token;
  return result;
 }
};
}
static __attribute__((noinline)) void FinishClassification(NamespaceReader &reader,const ClassifierOwners &owners){
 auto &classified=owners.work.classification;
 if(reader.ObservationFailed()){classified=Classification{};classified.diagnostic="checked I/O uncertainty";return;}
 if(classified.logical!=Logical::Unresolved){
  const RootFacts *selected=nullptr;
  for(unsigned i=0;i<3;++i){const auto &r=owners.work.roots[i];if(!r.present)continue;
   if(Token(r)>classified.high_token)classified.high_token=Token(r);
   if(i<2&&(!selected||Generation(r)>Generation(*selected)))selected=&r;
  }
  if(selected){classified.incarnation=Incarnation(*selected);classified.generation=Generation(*selected);classified.package_sequence=Sequence(*selected);}
  if(owners.work.current.reference_token>classified.high_token)classified.high_token=owners.work.current.reference_token;
  if(owners.work.prior.reference_token>classified.high_token)classified.high_token=owners.work.prior.reference_token;
 }
}
void ClassifyNamespaceInto(NamespaceReader &reader,const ClassifierOwners &owners){
 // Placement construction never materializes a 4KiB automatic temporary.
 owners.work.~ClassificationWorkspace();::new(&owners.work)ClassificationWorkspace;
 Classifier classifier(reader,owners);
 classifier.Run();
 if(owners.work.run.next_phase==1)classifier.RunRoots();
 if(owners.work.run.next_phase==2)classifier.RunBaseline();
 if(owners.work.run.next_phase==3)classifier.RunFinal();
 FinishClassification(reader,owners);
}
Classification ClassifyNamespace(NamespaceReader &reader,const ClassifierOwners &owners){
 ClassifyNamespaceInto(reader,owners);
 return owners.work.classification;
}

}
