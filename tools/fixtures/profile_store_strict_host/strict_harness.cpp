#include "core/ProfileStore.hpp"
#include "core/ProfileStorePaths.hpp"
#include "core/Sha256.hpp"
#include <pb_encode.h>
#include <pb_decode.h>
#include <lfs.h>
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
bool GlyphMountedReadRangeProbe(const char *,size_t,uint8_t *,size_t);
using Bytes=std::vector<uint8_t>;using Files=std::map<std::string,Bytes>;
using Status=ProfileStore::Status;using Kind=CheckedStorage::Kind;using Outcome=CheckedStorage::Outcome;using Result=CheckedStorage::Result;
namespace {
unsigned cases=0;
void require(bool v,const std::string&m){if(!v)throw std::runtime_error(m);}
void pass(const char*m){++cases;std::printf("%s=PASS\n",m);}
uint32_t crc(const uint8_t*p,size_t n){uint32_t c=~0u;while(n--){c^=*p++;for(unsigned j=0;j<8;++j)c=(c>>1)^(0xedb88320u&(0u-(c&1)));}return ~c;}
void put16(uint8_t*p,uint16_t v){p[0]=v;p[1]=v>>8;}
void put32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;++i)p[i]=v>>(i*8);}
[[maybe_unused]] uint32_t get32(const uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;++i)v|=uint32_t(p[i])<<(i*8);return v;}
Bytes encode(const UltimateProfile&p){size_t n=0;require(pb_get_encoded_size(&n,UltimateProfile_fields,&p),"profile size");Bytes b(n);auto s=pb_ostream_from_buffer(b.data(),b.size());require(pb_encode(&s,UltimateProfile_fields,&p),"profile encode");return b;}
ProfileStore::TransactionIdentity identity(uint64_t token,const char*text="request"){ProfileStore::TransactionIdentity t;t.token=token;Sha256 sha;sha.Update(text,std::strlen(text));sha.Final(t.digest);return t;}
std::string record_path(uint32_t id,uint32_t rev){char p[32];ProfileStorePaths::RecordPath(p,sizeof(p),id,rev);return p;}
struct MemoryStorage:ProfileStoreStorage{
 Files files; uint64_t total=524288;bool available=true;
 unsigned removes=0,fail_remove=0;bool remove_after=false;
 std::string fault_path;enum class Action {None,Write,Read,Probe,Rename,Enumerate};Action action=Action::None;bool after=false;
 uint64_t charge(size_t n)const{return ((n+4*((n+4095)/4096+1)+4095)/4096)*4096;}
 uint64_t used()const{uint64_t n=8192;for(const auto&e:files)n+=charge(e.second.size());return n;}
 bool Write(const char*p,const uint8_t*b,size_t n)override{uint64_t before=files.count(p)?charge(files.at(p).size()):0;if(used()-before+charge(n)>total)return false;files[p]=Bytes(b,b+n);return true;}
 bool Read(const char*p,uint8_t*b,size_t n)override{auto i=files.find(p);if(i==files.end()||i->second.size()!=n)return false;std::memcpy(b,i->second.data(),n);return true;}
 size_t Size(const char*p)override{return files.count(p)?files.at(p).size():0;}
 bool Exists(const char*p)override{return files.count(p);}
 bool Remove(const char*p)override{files.erase(p);return true;}
 bool Rename(const char*a,const char*b)override{auto i=files.find(a);if(i==files.end())return false;files[b]=std::move(i->second);files.erase(i);return true;}
 bool inject(Action op,const char*p)const{return action==op&&(fault_path.empty()||fault_path==p);}
 Result CheckedWrite(const char*p,const uint8_t*b,size_t n,Kind)override{if(inject(Action::Write,p)&&!after)return {Outcome::Failed};bool ok=Write(p,b,n);if(inject(Action::Write,p)&&after)return {Outcome::Uncertain};return {ok?Outcome::Ok:Outcome::Failed,0,n};}
 Result CheckedRead(const char*p,uint8_t*b,size_t n,Kind)override{if(inject(Action::Read,p))return {Outcome::Failed};return {Read(p,b,n)?Outcome::Ok:Outcome::Failed,0,n};}
 Result Probe(const char*p,size_t*n=nullptr)override{if(!available||inject(Action::Probe,p))return {Outcome::Failed};if(!Exists(p))return {Outcome::NotFound};if(n)*n=Size(p);return {Outcome::Ok};}
 Result CheckedRename(const char*a,const char*b,Kind)override{if(inject(Action::Rename,a)&&!after)return {Outcome::Failed};bool ok=Rename(a,b);if(inject(Action::Rename,a)&&after)return {Outcome::Uncertain};return {ok?Outcome::Ok:Outcome::Failed};}
 Result CheckedRemove(const char*p)override{++removes;if(fail_remove==removes&&!remove_after)return {Outcome::Failed};Remove(p);if(fail_remove==removes&&remove_after)return {Outcome::Uncertain};return {Outcome::Ok};}
 bool Geometry(CheckedStorage::Geometry&g)override{if(!available)return false;g.total_bytes=total;g.used_bytes=used();g.free_bytes=used()<total?total-used():0;g.erase_bytes=4096;g.program_bytes=256;g.read_bytes=256;g.block_count=total/4096;g.cache_bytes=256;g.name_max=31;return true;}
 bool Enumerate(CheckedStorage::Visitor visitor,void*c)override{if(action==Action::Enumerate)return false;for(const auto&e:files){CheckedStorage::Entry item{};auto p=e.first[0]=='/'?e.first.c_str()+1:e.first.c_str();require(std::strlen(p)<sizeof(item.name),"enumeration name bound");std::strcpy(item.name,p);item.bytes=e.second.size();if(!visitor(c,item))return false;}return true;}
 bool ReadRange(const char*p,size_t offset,uint8_t*b,size_t n)override{auto i=files.find(p);if(i==files.end()||offset>i->second.size()||n>i->second.size()-offset)return false;std::memcpy(b,i->second.data()+offset,n);return true;}
 void fill_to_free(uint64_t free){files.erase("/foreign");require(total>=used()+free,"fill bound");size_t n=total-used()-free;if(n)files["/foreign"]=Bytes(n>8?n-8:1);require(total-used()<=free,"filled free");}
};
Config legacy;
bool legacy_reader(void *p,size_t i,UltimateProfile&out){auto&c=*static_cast<Config*>(p);if(i>=c.ultimate_profiles_count)return false;out=c.ultimate_profiles[i];return true;}
[[maybe_unused]] void source_hash(const Config &c,uint8_t digest[32]){size_t n=0;require(pb_get_encoded_size(&n,Config_fields,&c),"source size");Bytes b(n);auto s=pb_ostream_from_buffer(b.data(),b.size());require(pb_encode(&s,Config_fields,&c),"source encode");Sha256 sha;sha.Update(b.data(),b.size());sha.Final(digest);}
void check_profile(ProfileStore&s,uint32_t id,const UltimateProfile&p){UltimateProfile out;require(s.Read(id,out)==Status::Ok&&encode(out)==encode(p),"profile exact bytes");}
ProfileStore::TransactionResult create(ProfileStore&s,uint64_t token,const char*name="profile"){return s.Create(legacy.ultimate_profiles[token&1],name,token,identity(token));}
void fix_root_crc(Bytes&b){put32(b.data()+b.size()-4,crc(b.data(),b.size()-4));}
// Actual deployed portable v1 root/envelope: no native layout bytes in fixtures.
Bytes v1root(uint32_t generation,const std::vector<ProfileStore::Entry>&entries){Bytes b(2620);put32(b.data(),0x31534450);put16(b.data()+4,1);put16(b.data()+6,entries.size());put32(b.data()+8,generation);put32(b.data()+12,7);put32(b.data()+16,4);put32(b.data()+20,0x12345678);put32(b.data()+24,generation==7?1:2);put32(b.data()+2592+16,3);put32(b.data()+2592+20,4);size_t off=32;for(const auto&e:entries){put32(b.data()+off,e.id);put32(b.data()+off+4,e.revision);put32(b.data()+off+8,e.previous_revision);put32(b.data()+off+12,e.payload_version);put32(b.data()+off+16,e.rank);std::strncpy(reinterpret_cast<char*>(b.data()+off+20),e.name,17);off+=40;}put32(b.data()+2616,crc(b.data(),2616));return b;}
Bytes v1record(uint32_t id,uint32_t rev,const UltimateProfile&p){auto payload=encode(p);Bytes b(32+payload.size());put32(b.data(),0x31525055);put16(b.data()+4,1);put16(b.data()+6,1);put32(b.data()+8,7);put32(b.data()+12,id);put32(b.data()+16,rev);put32(b.data()+20,payload.size());put32(b.data()+24,crc(b.data(),24));std::copy(payload.begin(),payload.end(),b.begin()+32);put32(b.data()+28,crc(b.data()+32,payload.size()));return b;}
MemoryStorage exact_upgrade(){MemoryStorage m;std::vector<ProfileStore::Entry> e(3);for(unsigned i=0;i<3;++i){e[i].id=i==0?1:i+2;e[i].revision=i==0?2:1;e[i].previous_revision=i==0?1:0;e[i].payload_version=legacy.ultimate_profiles[i==0?1:i-1].schema_version;e[i].rank=i==0?20:i-1;std::strcpy(e[i].name,i==0?"CRUD Primary":i==1?"Migrated 1":"Migrated 2");}m.files["/ultimate-dir-1.bin"]=v1root(8,e);m.files["/ultimate-dir-0.bin"]=v1root(7,e);m.files[record_path(1,1)]=v1record(1,1,legacy.ultimate_profiles[0]);m.files[record_path(1,2)]=v1record(1,2,legacy.ultimate_profiles[1]);m.files[record_path(3,1)]=v1record(3,1,legacy.ultimate_profiles[0]);m.files[record_path(4,1)]=v1record(4,1,legacy.ultimate_profiles[1]);return m;}
}
namespace {
unsigned failures=0;
template<class Work>void test(const char*name,Work work){try{work();pass(name);}catch(const std::exception&e){++failures;std::fprintf(stderr,"%s=FAIL: %s\n",name,e.what());}}
void prepare_source(MemoryStorage&m,const Config&c,uint8_t digest[32]){size_t n=0;require(pb_get_encoded_size(&n,Config_fields,&c),"source encode size");auto&b=m.files["/ultimate-migration.src"];b.resize(n);auto s=pb_ostream_from_buffer(b.data(),b.size());require(pb_encode(&s,Config_fields,&c),"source encoding");Sha256 sha;sha.Update(b.data(),b.size());sha.Final(digest);}
void root_tests(){
 test("all_mutation_unknown_query_replay_reset",[]{
  for(unsigned operation=0;operation<6;++operation)for(bool after:{false,true})for(bool reset:{false,true}){
   MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).status==Status::Ok&&create(s,2).status==Status::Ok,"mutation seed");
   auto token=identity(10);const uint32_t generation=s.Generation();
   auto mutate=[&](const ProfileStore::TransactionIdentity&t){switch(operation){case 0:return s.Create(legacy.ultimate_profiles[0],"created",44,t);case 1:return s.Update(1,legacy.ultimate_profiles[0],1,t);case 2:return s.Duplicate(1,1,"duplicated",45,t);case 3:return s.Rename(1,"renamed",generation,t);case 4:return s.Reorder(1,46,generation,t);default:return s.Delete(2,generation,0,t);}};
   m.action=MemoryStorage::Action::Rename;m.fault_path="/ultimate-v2-1.tmp";m.after=after;
   auto result=mutate(token);require(result.status==Status::UnknownOutcome&&s.IsTransactionUncertain(),"unknown rootpublication fenced");
   require(create(s,11).status==Status::UnknownOutcome,"unknown cannotadmit anothermutation");
   if(!after)require(s.QueryTransaction(token).status==Status::UnknownOutcome,"query retains unresolved evidence");
   m.action=MemoryStorage::Action::None;
   if(reset)require(s.Begin(1),"unknown reset reconciliation");
   auto query=s.QueryTransaction(token);require(query.status==(after?Status::Ok:Status::Aborted)&&!s.IsTransactionUncertain(),"query authoritative result");
   if(after){auto before=m.files;auto replay=mutate(token);require(replay.status==Status::Ok&&m.files==before,"completedtoken neverexecutes twice");require(mutate(identity(10,"changedrequest")).status==Status::Conflict,"same token changedrequest");require(s.Begin(1)&&mutate(token).status==Status::Ok,"durable replay afterreload");}
   else {
    require(s.Count()==2,"aborted checkpoint hasno newauthority");
    auto before=m.files;
    require(mutate(token).status==Status::Aborted&&m.files==before,"exact aborted retry neverexecutes");
    require(mutate(identity(10,"changedrequest")).status==Status::Conflict&&s.QueryTransaction(identity(10,"changedrequest")).status==Status::Conflict&&m.files==before,"changed aborted request conflicts before reboot");
    require(s.Begin(1,2)&&s.QueryTransaction(token).status==Status::Aborted&&mutate(token).status==Status::Aborted,"aborted identity durable afterreboot");
    require(mutate(identity(10,"changedrequest")).status==Status::Conflict&&s.QueryTransaction(identity(10,"changedrequest")).status==Status::Conflict,"changed aborted request conflicts afterreboot");
    require(create(s,11).status==Status::Ok,"later receipt consumption");before=m.files;
    require(mutate(token).status==Status::Conflict&&mutate(identity(10,"changedrequest")).status==Status::Conflict&&m.files==before,"consumed aborted token cannotexecute again");
    require(s.Begin(1,2)&&mutate(identity(10,"changedrequest")).status==Status::Conflict,"consumed aborted token remains rejected afterreboot");
   }
  }
 });
 test("discarded_abort_receipt_negative_control",[]{
  MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).status==Status::Ok&&create(s,2).status==Status::Ok,"abort negative seed");
  const Bytes previous=m.files.at("/ultimate-v2-0.bin");
  m.action=MemoryStorage::Action::Rename;m.fault_path="/ultimate-v2-1.tmp";m.after=false;
  require(create(s,10).status==Status::UnknownOutcome,"abort negative acceptedintent");m.action=MemoryStorage::Action::None;
  require(s.QueryTransaction(identity(10)).status==Status::Aborted&&s.Count()==2,"positive abort retainsidentity");
  // Reconstruct exactly the previous reconciliation state: preserve its new
  // generation/reserved high-water but copy the prior token/digest/result.
  // This is an explicit bad-state negative control, not a production repair.
  auto&checkpoint=m.files.at("/ultimate-v2-1.bin");
  std::copy(previous.begin()+24,previous.begin()+80,checkpoint.begin()+24);fix_root_crc(checkpoint);
  auto&control=m.files.at("/ultimate-v2.ctrl");std::copy(checkpoint.begin(),checkpoint.end(),control.begin()+16);
  put32(control.data()+12,crc(control.data(),12)^crc(control.data()+16,control.size()-16));
  require(s.Begin(1,2)&&s.QueryTransaction(identity(10)).status==Status::NotFound,"previous discard state loses acceptedtoken");
  auto changed=s.Create(legacy.ultimate_profiles[0],"changed aborted request",99,identity(10,"changedrequest"));
  require(changed.status==Status::Ok&&changed.id==4&&s.Count()==3,"discarded receipt admitschanged reusedtoken defect");
  std::puts("previous_abort_discard_negative_control=DETECTED reserved_id3_preserved=true changed_token10_executes=true");
 });
 test("migration_abort_preserves_existing_success_receipt",[]{
  MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,5).status==Status::Ok,"maintenance receipt seed");
  const auto successful=s.QueryTransaction(identity(5));uint8_t digest[32];prepare_source(m,legacy,digest);uint32_t ids[2]{};
  m.action=MemoryStorage::Action::Rename;m.fault_path="/ultimate-v2-0.tmp";m.after=false;
  require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2)==Status::UnknownOutcome,"migration maintenance unknown");m.action=MemoryStorage::Action::None;
  require(s.ReconcileTransaction()&&s.Count()==1&&!s.MigrationPending(),"migration maintenance abort checkpoint");
  auto retained=s.QueryTransaction(identity(5));require(retained.status==Status::Ok&&retained.id==successful.id&&retained.revision==successful.revision&&retained.generation==successful.generation,"maintenance cannot falselyabort successfulreceipt");
  require(s.Begin(1,2)&&s.QueryTransaction(identity(5)).status==Status::Ok,"successful receipt survives maintenance reboot");
  require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2)==Status::Ok&&ids[0]==4&&ids[1]==5,"maintenance retry preserves reserved IDs");
  Config compact=legacy;require(s.PrepareCompact(compact)&&s.CompleteMigration(compact)==Status::Ok&&s.QueryTransaction(identity(5)).status==Status::Ok,"maintenance completion retains successfulreceipt");
 });
 test("completed_older_token_cannot_execute_again",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).status==Status::Ok&&create(s,2).status==Status::Ok,"seed");auto before=m.files;require(create(s,1).status==Status::Conflict&&s.Count()==2&&m.files==before,"retiredtoken rejects");require(s.Begin(1)&&create(s,1).status==Status::Conflict,"retiredtoken reboot rejects");});
 test("migration_each_record_and_root_publication_fault",[]{
  for(const char*path:{"/ultimate-00000001-00000001.tmp","/ultimate-00000002-00000001.tmp","/ultimate-v2.ctmp","/ultimate-v2-1.tmp"})for(bool after:{false,true}){
   MemoryStorage m;ProfileStore s(&m);require(s.Begin(),"migrationfault seed");uint8_t digest[32];prepare_source(m,legacy,digest);uint32_t ids[2]{};
   m.action=MemoryStorage::Action::Rename;m.fault_path=path;m.after=after;
   auto failed=s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2);
   require(failed==Status::IoFailure||failed==Status::UnknownOutcome,"migrationfault explicitfailure");
   if(failed==Status::UnknownOutcome)require(create(s,10).status==Status::UnknownOutcome,"migrationunknown fences");
   m.action=MemoryStorage::Action::None;require(s.Begin(1),"migrationfault reset reconciles");
   auto retry=s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2);require(retry==Status::Ok||retry==Status::MigrationFenced,"migrationfault retry bounded");
   require(s.Count()==2&&s.MigrationPending(),"migrationfault no duplicateauthority");check_profile(s,ids[0],legacy.ultimate_profiles[0]);check_profile(s,ids[1],legacy.ultimate_profiles[1]);
   Config compact=legacy;require(s.PrepareCompact(compact)&&s.CompleteMigration(compact)==Status::Ok,"migrationfault complete");
  }
 });
 test("migration_completion_publication_fault_and_replay",[]{
  for(const char*path:{"/ultimate-v2.ctmp","/ultimate-v2-0.tmp"})for(bool after:{false,true}){
   MemoryStorage m;ProfileStore s(&m);require(s.Begin(),"completionfault seed");uint8_t digest[32];prepare_source(m,legacy,digest);uint32_t ids[2]{};
   require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2)==Status::Ok,"completionfault import");Config compact=legacy;require(s.PrepareCompact(compact),"completionfault compact");
   m.action=MemoryStorage::Action::Rename;m.fault_path=path;m.after=after;
   require(s.CompleteMigration(compact)==Status::UnknownOutcome&&s.IsTransactionUncertain(),"completionfault uncertain");
   m.action=MemoryStorage::Action::None;require(s.Begin(1)&&s.CompleteMigration(compact)==Status::Ok&&!s.MigrationPending()&&s.Count()==2,"completionfault reset idempotent");
  }
 });
 test("unsupported_envelope_schema_and_prior_fallback",[]{
  for(bool schema:{false,true}){
   MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).status==Status::Ok&&s.Update(1,legacy.ultimate_profiles[0],1,identity(2)).status==Status::Ok,"health seed");
   auto corrupt=[&](Bytes&record){if(schema){require(record.size()>34&&record[32]==8,"protobuf schema field");record[33]=99;put32(record.data()+28,crc(record.data()+32,record.size()-32));}else{put16(record.data()+4,99);put32(record.data()+24,crc(record.data(),24));}};
   corrupt(m.files.at(record_path(1,2)));require(s.Health(1)==ProfileStore::RecordHealth::RecoveredPrevious,"unsupported current falls back prior");
   corrupt(m.files.at(record_path(1,1)));require(s.Health(1)==ProfileStore::RecordHealth::Unsupported&&s.Count()==1,"unsupported distinguished from corruption");
  }
 });
 test("bootstrap_near_reserve_refuses_without_writes",[]{
  MemoryStorage m;m.fill_to_free(32768);const auto before=m.files;ProfileStore s(&m);require(!s.Begin()&&s.IsReadOnlyRecovery()&&m.files==before,"bootstrap reserves metadata before anypublication");
  auto upgrade=exact_upgrade();upgrade.fill_to_free(32768);const auto older=upgrade.files;ProfileStore u(&upgrade);require(!u.Begin(7)&&u.IsReadOnlyRecovery()&&upgrade.files==older,"upgrade refuses before irreversible marker");
 });
 test("compact_format_marker_prevents_erased_v2_downgrade",[]{
  auto m=exact_upgrade();ProfileStore s(&m);require(s.Begin(7)&&create(s,9).id==5,"upgraded issued5");
  for(auto file=m.files.begin();file!=m.files.end();){if(file->first.find("/ultimate-v2")==0)file=m.files.erase(file);else ++file;}
  require(m.files.count("/ultimate-dir-0.bin")&&m.files.count("/ultimate-dir-1.bin"),"v1 rollback evidence remains");
  require(!s.Begin(7,2)&&s.IsReadOnlyRecovery()&&create(s,10).status!=Status::Ok,"compact marker rejects completev2 loss");
  require(!s.Begin(7,2)&&create(s,11).status!=Status::Ok,"marker remains failclosed afterrestart");
 });
 test("twenty_block_charged_profiles",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin(),"bootstrap");require(s.Capacity().admissible_profiles>=20,"measured capacity meets20");for(unsigned i=1;i<=20;++i)require(create(s,i).status==Status::Ok,"admit each20");require(s.Count()==20&&m.used()<m.total-16384,"twenty preserve reserve");for(unsigned i=1;i<=20;++i)check_profile(s,i,legacy.ultimate_profiles[i&1]);auto c=s.Capacity();std::printf("measured_model total=%llu used=%llu free=%llu protected=%llu staging=%llu admissible=%u\n",(unsigned long long)c.total_bytes,(unsigned long long)c.used_bytes,(unsigned long long)c.free_bytes,(unsigned long long)c.protected_bytes,(unsigned long long)c.staging_bytes,c.admissible_profiles);require(s.Begin(1)&&s.Count()==20,"twenty reboot");});
 test("near_reserve_create_update_duplicate_refusal",[]{for(unsigned op=0;op<3;++op){MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).status==Status::Ok,"seed");m.fill_to_free(45056);auto before=m.files;auto generation=s.Generation();auto t=identity(2);auto r=op==0?create(s,2):op==1?s.Update(1,legacy.ultimate_profiles[0],1,t):s.Duplicate(1,1,"duplicate",2,t);require(r.status==Status::Full&&s.Generation()==generation&&m.files==before,"reserve fail before authority/staging");}});
 test("update_duplicate_staging_and_previous_union",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).status==Status::Ok,"seed");require(s.Update(1,legacy.ultimate_profiles[0],1,identity(2)).status==Status::Ok,"update");require(m.files.count(record_path(1,1))&&m.files.count(record_path(1,2)),"previous protected");auto duplicated=s.Duplicate(1,2,"duplicate",9,identity(3));require(duplicated.status==Status::Ok&&duplicated.id==2,"duplicate newidentity");check_profile(s,2,legacy.ultimate_profiles[0]);require(s.EntryAt(0)->revision==2&&s.EntryAt(0)->previous_revision==1,"update metadata");require(s.Capacity().protected_bytes>=3*4096,"protected union charge");});
 test("gc_protected_revisions_deletion_and_interruptions",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).status==Status::Ok,"seed");for(unsigned rev=1;rev<4;++rev)require(s.Update(1,legacy.ultimate_profiles[rev&1],rev,identity(rev+1)).status==Status::Ok,"rev update");require(m.files.count(record_path(1,1)),"thirdprior retained until rootadvance");require(s.CollectGarbage()==Status::Ok&&!m.files.count(record_path(1,1)),"superseded reclaim");for(unsigned rev=2;rev<=4;++rev)require(m.files.count(record_path(1,rev)),"protected previous union");require(create(s,5).status==Status::Ok,"delete seed");require(s.Delete(2,s.Generation(),0,identity(6)).status==Status::Ok,"delete");require(s.CollectGarbage()==Status::Ok&&m.files.count(record_path(2,1)),"previous root stillprotects deleted");require(s.Reorder(1,88,s.Generation(),identity(7)).status==Status::Ok&&s.CollectGarbage()==Status::Ok&&!m.files.count(record_path(2,1)),"deleted reclaim after boundary");for(unsigned i=100;i<106;++i)m.files[record_path(i,1)]=Bytes(100,0x55);auto snapshot=m.files;
  for(unsigned boundary=1;boundary<=6;++boundary)for(bool after:{false,true}){m.files=snapshot;m.removes=0;m.fail_remove=boundary;m.remove_after=after;require(s.Begin(1),"gc retry reboot");auto generation=s.Generation();require(s.CollectGarbage()==Status::IoFailure&&s.Generation()==generation,"gc interrupted no authoritychange");for(unsigned rev=3;rev<=4;++rev)require(m.files.count(record_path(1,rev)),"gc cannotdelete protected revisions");m.fail_remove=0;require(s.CollectGarbage()==Status::Ok,"gc retry succeeds");for(unsigned i=100;i<106;++i)require(!m.files.count(record_path(i,1)),"gc boundedgarbage absent");}
 });
 test("all_accepted_name_lengths_reboot_duplicate",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin(),"seed");unsigned token=0;for(size_t n:{0u,1u,17u,18u,31u,32u}){std::string name(n,'a'+n%20);auto r=create(s,++token,name.c_str());require(r.status==Status::Ok&&std::string(s.EntryAt(token-1)->name)==name,"name exact");}std::string maximum(32,'z');require(s.Rename(1,maximum.c_str(),s.Generation(),identity(++token)).status==Status::Ok,"maximum rename");auto r=s.Duplicate(1,1,maximum.c_str(),0,identity(++token));require(r.status==Status::Ok&&std::string(s.EntryAt(s.Count()-1)->name)==maximum,"maximum duplicate");require(s.Begin(1)&&std::string(s.EntryAt(0)->name)==maximum,"maximum survives reboot");std::string rejected(33,'x');require(create(s,++token,rejected.c_str()).status==Status::Invalid,"overbound reject");});
 test("lazy_health_corruption_fallback_missing",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).status==Status::Ok&&s.Update(1,legacy.ultimate_profiles[0],1,identity(2)).status==Status::Ok&&create(s,3).status==Status::Ok,"seed");auto active=s.Activate(2);require(active,"active seed");Bytes active_before=encode(*active);require(s.Health(1)==ProfileStore::RecordHealth::Healthy,"healthy");m.files.at(record_path(1,2)).back()^=1;require(s.Health(1)==ProfileStore::RecordHealth::RecoveredPrevious&&s.Count()==2,"current corrupt previous usable/list healthy");require(s.ActiveId()==2&&encode(*s.ActiveProfile())==active_before,"health never activates");m.files.at(record_path(1,1)).back()^=1;require(s.Health(1)==ProfileStore::RecordHealth::Corrupt,"both corrupt");m.files.erase(record_path(1,2));m.files.erase(record_path(1,1));require(s.Health(1)==ProfileStore::RecordHealth::Missing&&s.EntryAt(1)->id==2,"missing isolated");});
 test("firstuse_and_exact_lost_generation2_no_reuse",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).id==1,"legitimate firstmutation");require(s.Begin(1)&&!s.IsReadOnlyRecovery(),"healthy firstuse");require(create(s,2).id==2,"issued2");m.files.erase("/ultimate-v2-0.bin");s.Begin(1);require(s.IsReadOnlyRecovery()&&s.Count()==1&&(s.HealthFlags()&ProfileStore::RootInvalid),"lonegen1 readonly rootinvalid");require(create(s,3).status!=Status::Ok,"never reissue2");s.Begin(1);require(create(s,3).status!=Status::Ok&&s.IsReadOnlyRecovery(),"restart remains readonly");});
 test("root_absence_invalid_conflict_and_compact_identity",[]{MemoryStorage m;ProfileStore s(&m);require(!s.Begin(7)&&s.IsReadOnlyRecovery(),"compactidentity rootabsence");m={};require(s.Begin()&&create(s,1).status==Status::Ok,"seed");auto healthy=m.files;m.files.erase("/ultimate-v2-0.bin");m.files.erase("/ultimate-v2-1.bin");require(!s.Begin(1)&&s.IsReadOnlyRecovery(),"both absent closed");m.files=healthy;m.files.at("/ultimate-v2-0.bin").back()^=1;require(s.Begin(1)&&s.IsReadOnlyRecovery(),"invalid companion readonly");m.files=healthy;auto&conflict=m.files.at("/ultimate-v2-0.bin");put32(conflict.data()+12,77);fix_root_crc(conflict);require(!s.Begin(1)&&s.IsReadOnlyRecovery(),"conflicting incarnations rejected");m.files=healthy;m.files.erase("/ultimate-v2.ctrl");require(!s.Begin(1)&&s.IsReadOnlyRecovery(),"missing marker cannotdowngrade");});
 test("rollback_older_valid_pair_cannot_reissue",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin()&&create(s,1).id==1,"initial");const Bytes prior0=m.files.at("/ultimate-v2-0.bin"),prior1=m.files.at("/ultimate-v2-1.bin");require(create(s,2).id==2,"issued2");m.files["/ultimate-v2-0.bin"]=prior0;m.files["/ultimate-v2-1.bin"]=prior1;const bool begun=s.Begin(1);require((!begun||s.IsReadOnlyRecovery())&&(s.HealthFlags()&ProfileStore::RootInvalid),"rolledback validpair must readonly rootinvalid");require(create(s,3).status!=Status::Ok,"rolledbackpair neverreallocates");});
 test("exact_f7_compact_v1_upgrade",[]{auto m=exact_upgrade();const Files before=m.files;ProfileStore s(&m);require(s.Begin(7)&&!s.IsReadOnlyRecovery()&&s.Generation()==8&&s.Count()==3,"upgrade identity");require(s.EntryAt(0)->id==1&&s.EntryAt(0)->revision==2&&s.EntryAt(0)->rank==20&&std::string(s.EntryAt(0)->name)=="CRUD Primary"&&s.EntryAt(1)->id==3&&s.EntryAt(2)->id==4,"upgrade metadata");for(const auto&e:before)require(m.files.at(e.first)==e.second,"v1 dependency immutable");check_profile(s,1,legacy.ultimate_profiles[1]);check_profile(s,3,legacy.ultimate_profiles[0]);check_profile(s,4,legacy.ultimate_profiles[1]);Config compact=legacy;compact.ultimate_profiles_count=0;compact.ultimate_profile_store_format=1;compact.ultimate_profile_store_incarnation=7;
 for(size_t i=0;i<compact.game_mode_configs_count;++i){auto &mode=compact.game_mode_configs[i];if(mode.mode_id==MODE_ULTIMATE){const auto old=mode.ultimate_profile_config;mode.ultimate_profile_id=old==1?3:old==2?4:0;mode.ultimate_profile_config=0;}}
 require(compact.game_mode_configs_count>2&&compact.game_mode_configs[1].ultimate_profile_id==3&&compact.game_mode_configs[2].ultimate_profile_id==4,"exact compactmode1to3 mode2to4");
 require(s.PrepareCompact(compact)&&s.ValidateCompactReceipt(compact)&&compact.game_mode_configs[1].ultimate_profile_id==3&&compact.game_mode_configs[2].ultimate_profile_id==4,"receipt promotion preservescompact references");
 require(s.CompleteMigration(compact)==Status::Ok&&s.Generation()==8,"completed v1 receipt upgrade stayscomplete");
 require(s.Begin(7)&&s.ValidateCompactReceipt(compact)&&create(s,9).id==5,"deleted2 nonreuse andreceipt through upgrade reboot");});
 test("upgrade_interruption_no_writable_downgrade",[]{for(const char*p:{"/ultimate-v2.ctmp","/ultimate-v2-0.tmp","/ultimate-v2-1.tmp"})for(bool after:{false,true}){auto m=exact_upgrade();m.action=MemoryStorage::Action::Rename;m.fault_path=p;m.after=after;ProfileStore s(&m);s.Begin(7);require(!s.IsReady()||s.IsReadOnlyRecovery()||s.IsTransactionUncertain(),std::string("interruption fences write path=")+p+" after="+std::to_string(after));m.action=MemoryStorage::Action::None;require(s.Begin(7)&&s.Count()==3&&!s.IsReadOnlyRecovery(),"mechanical upgrade resume");require(create(s,9).id==5,"upgrade neverreuse deleted2");}});
 test("full_store_and_migration_count_highwater_preflight",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin(),"seed");for(unsigned i=1;i<=64;++i)require(create(s,i).status==Status::Ok,"fill64");require(create(s,65).status==Status::Full&&s.Count()==64,"fullcount");uint8_t digest[32];prepare_source(m,legacy,digest);uint32_t map[2]{};require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,map,2)==Status::Full&&s.Count()==64,"64 plus2 refused");require(s.Delete(64,s.Generation(),0,identity(66)).status==Status::Ok,"reduce63");require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,map,2)==Status::Full&&s.Count()==63,"63 plus2 refused");m={};require(s.Begin(),"highwater seed");for(const char*p:{"/ultimate-v2-0.bin","/ultimate-v2-1.bin"}){auto&b=m.files.at(p);put32(b.data()+16,UINT32_MAX-1);fix_root_crc(b);}auto&control=m.files.at("/ultimate-v2.ctrl");put32(control.data()+32,UINT32_MAX-1);put32(control.data()+control.size()-4,crc(control.data()+16,control.size()-20));put32(control.data()+12,crc(control.data(),12)^crc(control.data()+16,control.size()-16));require(s.Begin(1),"highwater validroots");prepare_source(m,legacy,digest);require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,map,2)==Status::Full&&s.Count()==0,"highwater plus2 overflow refused");});
 test("authenticated_streamed_migration_retry_completion",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin(),"seed");uint8_t digest[32];prepare_source(m,legacy,digest);uint32_t ids[2]{};require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2)==Status::Ok&&s.MigrationPending(),"stream import");const auto generation=s.Generation();check_profile(s,ids[0],legacy.ultimate_profiles[0]);check_profile(s,ids[1],legacy.ultimate_profiles[1]);require(s.Begin(1)&&s.MigrationPending(),"reset after receipt");uint32_t retry[2]{};require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,retry,2)==Status::MigrationFenced&&retry[0]==ids[0]&&retry[1]==ids[1]&&s.Generation()==generation,"same source retry stable");Config compact=legacy;require(s.PrepareCompact(compact)&&s.ValidateCompactReceipt(compact),"compact bound receipt");Config wrong=compact;wrong.ultimate_profile_store_incarnation=99;require(s.CompleteMigration(wrong)==Status::Invalid,"wrong incarnation");wrong=compact;for(size_t i=0;i<wrong.game_mode_configs_count;++i)if(wrong.game_mode_configs[i].mode_id==MODE_ULTIMATE&&wrong.game_mode_configs[i].ultimate_profile_id){wrong.game_mode_configs[i].ultimate_profile_id=99;break;}require(s.CompleteMigration(wrong)==Status::Invalid,"wrong reference mapping");require(s.Begin(1)&&s.MigrationPending()&&s.CompleteMigration(compact)==Status::Ok&&!s.MigrationPending(),"reset after compact beforecomplete");require(s.Begin(1)&&s.CompleteMigration(compact)==Status::Ok&&s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,retry,2)==Status::Ok&&s.Count()==2,"completion replay stable");});
 test("migration_changedsource_corrupt_missing_capacity",[]{MemoryStorage m;ProfileStore s(&m);require(s.Begin(),"seed");uint8_t digest[32];prepare_source(m,legacy,digest);uint32_t ids[2]{};require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2)==Status::Ok,"import");auto original=m.files;auto&source=m.files.at("/ultimate-migration.src");source.back()^=1;uint8_t changed[32];Sha256 h;h.Update(source.data(),source.size());h.Final(changed);require(s.ImportLegacyStream(legacy,changed,legacy_reader,&legacy,ids,2)==Status::Conflict,"changed source receipt refused");m.files=original;m.files.at(record_path(ids[0],1)).back()^=1;require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2)==Status::Invalid,"corrupt imported record");Config compact=legacy;require(s.PrepareCompact(compact)&&s.CompleteMigration(compact)==Status::Invalid,"corrupt completion dependency");m.files=original;m.files.erase(record_path(ids[0],1));require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2)==Status::Invalid,"missing imported record");m={};require(s.Begin(),"capacity seed");prepare_source(m,legacy,digest);m.fill_to_free(45056);auto before=m.files;require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2)==Status::Full&&m.files==before,"migration reserve preflight");});
}
}
namespace {
lfs_t mounted_fs{};lfs_config mounted_cfg{};std::vector<uint8_t> physical(524288,0xff);
int ram_read(const lfs_config*,lfs_block_t b,lfs_off_t o,void*p,lfs_size_t n){std::memcpy(p,physical.data()+4096*b+o,n);return 0;}
int ram_prog(const lfs_config*,lfs_block_t b,lfs_off_t o,const void*p,lfs_size_t n){auto*d=physical.data()+4096*b+o;auto*s=static_cast<const uint8_t*>(p);for(size_t i=0;i<n;++i){if((d[i]&s[i])!=s[i])return LFS_ERR_CORRUPT;d[i]&=s[i];}return 0;}
int ram_erase(const lfs_config*,lfs_block_t b){std::fill_n(physical.data()+b*4096,4096,0xff);return 0;}
int ram_sync(const lfs_config*){return 0;}
void pinned_test(){test("pinned_littlefs_actual_twenty_admission",[]{mounted_cfg.read=ram_read;mounted_cfg.prog=ram_prog;mounted_cfg.erase=ram_erase;mounted_cfg.sync=ram_sync;mounted_cfg.read_size=256;mounted_cfg.prog_size=256;mounted_cfg.block_size=4096;mounted_cfg.block_count=128;mounted_cfg.block_cycles=16;mounted_cfg.cache_size=256;mounted_cfg.lookahead_size=256;require(lfs_format(&mounted_fs,&mounted_cfg)==0&&lfs_mount(&mounted_fs,&mounted_cfg)==0,"actual mountedengine");
 const uint8_t range_bytes[]={0x31,0x42,0x53};uint8_t range_out[8]{};
 require(bool(CheckedStorage::WriteFile("/range-probe",range_bytes,sizeof(range_bytes),Kind::Record)),"range probe seed");
 require(GlyphMountedReadRangeProbe("/range-probe",0,range_out,3)&&std::memcmp(range_out,range_bytes,3)==0,"real mountedadapter exact range");
 require(!GlyphMountedReadRangeProbe("/range-probe",0,range_out,4)&&!GlyphMountedReadRangeProbe("/range-probe",1,range_out,3)&&!GlyphMountedReadRangeProbe("/range-probe",3,range_out,1),"real mountedadapter rejects shortreads andEOF");
 CheckedStorage::File old_file;require(bool(CheckedStorage::Open(old_file,"/range-probe",false,Kind::Record))&&bool(CheckedStorage::Seek(old_file,0)),"old range control open");
 auto short_read=CheckedStorage::Read(old_file,range_out,4);auto old_closed=CheckedStorage::Close(old_file);
 require(bool(short_read)&&short_read.bytes==3&&bool(old_closed),"previous boolResult control wrongly accepts shortread");
 std::puts("mounted_read_range_shortread=PASS previous_bool_result_negative_control=DETECTED");
 require(bool(CheckedStorage::Remove("/range-probe",Kind::Record)),"range probe cleanup");
 ProfileStore s;require(s.Begin(),"production mountedadapter");for(unsigned i=1;i<=20;++i)require(create(s,i).status==Status::Ok,"actual20admission");auto c=s.Capacity();require(s.Count()==20&&c.admissible_profiles>=20&&c.free_bytes>=c.reserve_bytes+c.staging_bytes,"actualgeometry preserves fullreserve");std::printf("pinned_littlefs total=%llu used=%llu free=%llu protected=%llu staging=%llu admissible=%u\n",(unsigned long long)c.total_bytes,(unsigned long long)c.used_bytes,(unsigned long long)c.free_bytes,(unsigned long long)c.protected_bytes,(unsigned long long)c.staging_bytes,c.admissible_profiles);require(lfs_unmount(&mounted_fs)==0&&lfs_mount(&mounted_fs,&mounted_cfg)==0&&s.Begin(1)&&s.Count()==20,"actual reboot twenty");for(unsigned i=1;i<=20;++i)check_profile(s,i,legacy.ultimate_profiles[i&1]);require(lfs_unmount(&mounted_fs)==0,"actualunmount");});}
}
lfs_t *CheckedStorageTestMount(){return &mounted_fs;}
int main(int argc,char**argv){try{require(argc==2,"fixture argument");std::ifstream input(argv[1],std::ios::binary);Bytes b((std::istreambuf_iterator<char>(input)),{});require(!b.empty(),"fixture exists");auto stream=pb_istream_from_buffer(b.data(),b.size());legacy=Config_init_default;require(pb_decode(&stream,Config_fields,&legacy)&&!stream.bytes_left&&legacy.ultimate_profiles_count==2,"accepted Runtime A/B source");root_tests();pinned_test();std::printf("strict_profile_store_cases=%u failures=%u ASAN_UBSAN=true physical_hardware=NOT_CLAIMED\n",cases,failures);return failures?1:0;}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
