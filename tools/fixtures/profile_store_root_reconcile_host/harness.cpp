#include "host_stubs.hpp"
#include "core/Persistence.hpp"
#include "core/ProfileStore.hpp"
#include "core/ProfileStoreFaultControls.hpp"
#include "core/ProfileStoreRequestIdentity.hpp"
#include "comms/ConfiguratorBackend.hpp"
#include <lfs.h>
#include <pb_decode.h>
#include <pb_encode.h>
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>
uint32_t host_millis=0;
Persistence persistence;
bool GlyphFaultHookInstalled();
using Bytes=std::vector<uint8_t>;
using Status=ProfileStore::Status;
using Op=CheckedStorage::Operation;
namespace {
lfs_t fs{};lfs_config cfg{};Bytes physical(524288,0xff);
void need(bool v,const char *m){if(!v)throw std::runtime_error(m);}
int rd(const lfs_config*,lfs_block_t b,lfs_off_t o,void*p,lfs_size_t n){std::memcpy(p,physical.data()+4096*b+o,n);return 0;}
int prog(const lfs_config*,lfs_block_t b,lfs_off_t o,const void*p,lfs_size_t n){auto*d=physical.data()+4096*b+o;auto*s=static_cast<const uint8_t*>(p);for(size_t i=0;i<n;++i){if((d[i]&s[i])!=s[i])return LFS_ERR_CORRUPT;d[i]&=s[i];}return 0;}
int erase(const lfs_config*,lfs_block_t b){std::fill_n(physical.data()+4096*b,4096,0xff);return 0;}
int sync(const lfs_config*){return 0;}
class Wire:public Stream {
 public:
 Bytes rx,tx;size_t pos=0;unsigned fail_after_frames=0;
 int availableForWrite()override{return fail_after_frames&&std::count(tx.begin(),tx.end(),0)>=fail_after_frames?0:64;}
 int available()override{return rx.size()-pos;}
 int read()override{return pos<rx.size()?rx[pos++]:-1;}
 int peek()override{return pos<rx.size()?rx[pos]:-1;}
 void flush()override{}
 size_t write(uint8_t b)override{tx.push_back(b);return 1;}
 size_t write(const uint8_t*p,size_t n)override{tx.insert(tx.end(),p,p+n);return n;}
};
Bytes encode(const UltimateProfile &p){size_t n=0;need(pb_get_encoded_size(&n,UltimateProfile_fields,&p),"size");Bytes b(n);auto s=pb_ostream_from_buffer(b.data(),n);need(pb_encode(&s,UltimateProfile_fields,&p),"encode");return b;}
Bytes cobs_decode(const Bytes&b){Bytes out;for(size_t i=0;i<b.size();){unsigned c=b[i++];need(c&&i+c-1<=b.size(),"COBS");out.insert(out.end(),b.begin()+i,b.begin()+i+c-1);i+=c-1;if(c<255&&i<b.size())out.push_back(0);}return out;}
std::vector<unsigned> stages;
ProfileStoreResponse send(ConfiguratorBackend&backend,Wire&wire,const ProfileStoreRequest&r){
 size_t n=0;need(pb_get_encoded_size(&n,ProfileStoreRequest_fields,&r),"request size");Bytes b(n);auto s=pb_ostream_from_buffer(b.data(),n);need(pb_encode(&s,ProfileStoreRequest_fields,&r),"request encode");
 wire.tx.clear();Wire outgoing;packetio::COBSPrint packet(outgoing);packet.write(uint8_t(CMD_PROFILE_STORE));packet.write(b.data(),b.size());need(packet.end(),"frame");wire.rx.insert(wire.rx.end(),outgoing.tx.begin(),outgoing.tx.end());backend.SendReport();need(wire.pos==wire.rx.size(),"request consumed");
 ProfileStoreResponse final=ProfileStoreResponse_init_default;Bytes frame;unsigned finals=0;stages.clear();
 for(auto byte:wire.tx){if(byte){frame.push_back(byte);continue;}if(frame.empty())continue;auto raw=cobs_decode(frame);frame.clear();need(raw[0]==CMD_PROFILE_STORE,"response command");ProfileStoreResponse out=ProfileStoreResponse_init_default;auto input=pb_istream_from_buffer(raw.data()+1,raw.size()-1);need(pb_decode(&input,ProfileStoreResponse_fields,&out)&&!input.bytes_left,"decode response");if(out.liveness_stage){stages.push_back(out.liveness_stage);if(out.liveness_stage>=44)need(!GlyphFaultHookInstalled()&&!ProfileStoreFaultControls::Current().armed,"hook ended before trace/config/encoding");}else{final=out;++finals;}}
 need(finals==(wire.fail_after_frames?0u:1u)&&frame.empty(),"one complete final response, or bounded trace failure");need(!GlyphFaultHookInstalled()&&!ProfileStoreFaultControls::Current().armed,"hook ended at request exit");return final;
}
ProfileStoreRequest query(uint64_t token,uint32_t ticket=0){ProfileStoreRequest r=ProfileStoreRequest_init_default;r.protocol_version=2;r.operation=PROFILE_STORE_QUERY_TRANSACTION;r.request_token=token;r.fault_ticket=ticket;r.liveness_trace=true;return r;}
ProfileStore::TransactionIdentity identity(uint64_t token){ProfileStore::TransactionIdentity t;t.token=token;t.digest[0]=uint8_t(token);return t;}
void arm(unsigned kind,unsigned path,unsigned op,unsigned phase=1,unsigned result=1,unsigned skip=0){
#ifdef EXPECT_PRODUCTION
 ProfileStoreFaultControls::Current()={false,false,true,++ProfileStoreFaultControls::NextTicket(),kind,op,phase,result,path,skip};
#else
 need(ProfileStoreFaultControls::Arm(kind,op,phase,result,path,skip,false),"arm pending");
#endif
 need(!GlyphFaultHookInstalled(),"ARM inert");}
void pending_intent(ConfiguratorBackend&backend,Wire&wire,const UltimateProfile&p,ProfileStoreRequest &update,bool reserve_id=false){
 arm(2,3,unsigned(Op::Rename),2,2);update=ProfileStoreRequest_init_default;update.protocol_version=2;update.operation=PROFILE_STORE_UPDATE;update.profile_id=22;update.request_token=0xf000000000001c00ull;update.expected_store_incarnation=profile_store.Incarnation();update.expected_store_generation=profile_store.Generation();update.expected_profile_revision=1;update.has_profile=true;update.profile=p;update.fault_ticket=ProfileStoreFaultControls::Current().ticket;
#ifdef EXPECT_PRODUCTION
 (void)backend;(void)wire;(void)reserve_id;
 CheckedStorage::SetFaultHook(+[](CheckedStorage::Kind,Op op,CheckedStorage::Phase phase,const char*path){return op==Op::Rename&&phase==CheckedStorage::Phase::After&&std::string(path)=="/ultimate-v2.ctmp"?CheckedStorage::Fault::LostAcknowledgement:CheckedStorage::Fault::None;});
 ProfileStoreTransactionIdentity exact;need(ProfileStoreRequestIdentity(update,exact),"production identity");
 need(profile_store.Update(22,p,1,exact).status==Status::UnknownOutcome,"production pending intent");CheckedStorage::SetFaultHook(nullptr);
#else
 if(reserve_id){update.operation=PROFILE_STORE_CREATE;update.profile_id=0;update.expected_profile_revision=0;std::strcpy(update.name,"reserved");}
 auto r=send(backend,wire,update);need(r.status==PROFILE_STORE_COMMIT_UNKNOWN&&r.storage_fault_triggered&&profile_store.IsTransactionUncertain(),"real control rename lost-ack pending intent");need(std::string(r.diagnostic)=="directory.rename","physical setup diagnostic");
#endif
}
void run(const char*fixture,const std::string&mode){
 cfg.read=rd;cfg.prog=prog;cfg.erase=erase;cfg.sync=sync;cfg.read_size=cfg.prog_size=cfg.cache_size=256;cfg.block_size=4096;cfg.block_count=128;cfg.block_cycles=16;cfg.lookahead_size=256;
 need(lfs_format(&fs,&cfg)==0&&lfs_mount(&fs,&cfg)==0,"mount actual pinned LittleFS");need(profile_store.Begin(),"bootstrap");
 std::ifstream f(fixture,std::ios::binary);Bytes bytes((std::istreambuf_iterator<char>(f)),{});Config config=Config_init_default;auto input=pb_istream_from_buffer(bytes.data(),bytes.size());need(pb_decode(&input,Config_fields,&config)&&config.ultimate_profiles_count==2,"actual fixture");auto original=config.ultimate_profiles[0],intended=config.ultimate_profiles[1];
 for(unsigned id=1;id<=22;++id)need(profile_store.Create(original,"seed",id,identity(id)).id==id,"seed ID22");
 // Exercise both first-root-is-newer and first-root-is-older authority pairs.
 if(mode=="special-even")need(profile_store.Reorder(1,99,profile_store.Generation(),identity(23)).status==Status::Ok,"even generation");
 config.ultimate_profiles_count=0;config.ultimate_profile_root_format=2;config.ultimate_profile_store_format=1;config.ultimate_profile_store_incarnation=profile_store.Incarnation();persistence.Seed(config);
 Wire wire;InputState inputs;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);
 if(mode=="not-uncertain"){
  arm(2,2,unsigned(Op::OpenRead));auto r=send(backend,wire,query(22,ProfileStoreFaultControls::Current().ticket));need(r.status==PROFILE_STORE_INVALID&&r.storage_fault_pending&&!r.storage_fault_triggered,"healthy QUERY ticket rejected");
 }else if(mode=="replay"){
  ProfileStoreRequest create=ProfileStoreRequest_init_default;create.protocol_version=2;create.operation=PROFILE_STORE_CREATE;create.request_token=24;create.expected_store_incarnation=profile_store.Incarnation();create.expected_store_generation=profile_store.Generation();create.has_profile=true;create.profile=original;
  need(send(backend,wire,create).status==PROFILE_STORE_OK,"replay seed");arm(2,2,unsigned(Op::OpenRead));auto before=physical;auto r=send(backend,wire,create);need(r.status==PROFILE_STORE_OK&&r.storage_fault_pending&&!r.storage_fault_triggered&&physical==before,"exact replay never activates pending ticket");
  create.fault_ticket=ProfileStoreFaultControls::Current().ticket;r=send(backend,wire,create);need(r.status==PROFILE_STORE_CONFLICT&&r.storage_fault_pending&&!r.storage_fault_triggered&&physical==before,"changed replay with ticket conflicts without activation");
 }else{
  ProfileStoreRequest update;const auto before_generation=profile_store.Generation();pending_intent(backend,wire,intended,update,mode=="special-create");const auto snapshot=physical;
  unsigned kind=2,path=2,op=unsigned(Op::OpenRead),phase=1,result=1,skip=0;
  if(mode=="record"){kind=1;path=1;}if(mode=="config"){kind=3;path=4;}if(mode=="control")path=3;if(mode=="rename")op=unsigned(Op::Rename);if(mode=="read")op=unsigned(Op::Read);if(mode=="write")op=unsigned(Op::OpenWrite);if(mode=="lost-ack"){phase=2;result=2;}if(mode=="skip")skip=1;
  arm(kind,path,op,phase,result,skip);auto ticket=ProfileStoreFaultControls::Current().ticket;
  need(!ProfileStoreFaultControls::PathMatches(2,"/ultimate-v2.ctrl")&&!ProfileStoreFaultControls::PathMatches(2,"/ultimate-v2.ctmp")&&ProfileStoreFaultControls::PathMatches(2,"/ultimate-v2-0.bin"),"actual-root class excludes control");
  bool ordinary=mode=="ordinary"||mode=="frozen-ordinary";
  if(mode=="status"||mode=="list"||mode=="read-only"){
   auto r=query(0);r.operation=mode=="status"?PROFILE_STORE_STATUS:mode=="list"?PROFILE_STORE_LIST:PROFILE_STORE_READ;r.profile_id=22;r.liveness_trace=false;send(backend,wire,r);need(ProfileStoreFaultControls::Current().pending&&!ProfileStoreFaultControls::Current().triggered&&physical==snapshot,"read operations inert, no reconcile");r.fault_ticket=ticket;need(send(backend,wire,r).status==PROFILE_STORE_INVALID,"read operations reject ticket");
  }else if(mode=="trace-fail42"||mode=="trace-fail43"||mode=="trace-fail44"){
   wire.fail_after_frames=mode=="trace-fail42"?2:mode=="trace-fail43"?3:4;
   send(backend,wire,query(update.request_token,ticket));const auto &state=ProfileStoreFaultControls::Current();
   need(state.pending==(mode=="trace-fail42")&&!state.armed&&state.triggered==(mode=="trace-fail44")&&!GlyphFaultHookInstalled(),"trace failure always ends hook scope");
   need(physical==snapshot&&profile_store.IsTransactionUncertain(),"trace failure never writes checkpoint");
  }else{
   auto request=query(mode=="zero-token"?0:update.request_token,ordinary?0:mode=="wrong-ticket"?ticket+1:ticket);
   if(mode=="v1")request.protocol_version=1;
   if(mode=="wrong-phase")ProfileStoreFaultControls::Current().phase=2;
   auto r=send(backend,wire,request);
#ifdef EXPECT_FROZEN
   bool special=false;
#else
   bool special=kStrictHardeningCandidate&&(mode=="special"||mode=="special-even"||mode=="special-create");
#endif
   if(ordinary){need(r.status==PROFILE_STORE_TRANSACTION_ABORTED&&r.store_generation==before_generation+1&&r.profile_revision==2&&r.storage_fault_pending&&!r.storage_fault_triggered&&!profile_store.IsTransactionUncertain(),"ordinary healthy reconciliation ABORTED; fault inert");}
   else if(special){
    need(r.status==PROFILE_STORE_COMMIT_UNKNOWN&&profile_store.IsTransactionUncertain(),"UnknownOutcome maps COMMIT_UNKNOWN, no second healthy reconciliation");need(r.store_generation<=before_generation&&r.storage_fault_triggered&&!r.storage_fault_pending&&!r.storage_fault_armed&&r.storage_fault_operation==unsigned(Op::OpenRead),"ticket consumed exactly once, generation cannot advance");need((r.recovery_flags&26)==26&&physical==snapshot,"uncertain/read-only/root-invalid; no writes/allocation/deletion");need(stages==std::vector<unsigned>({1,2,42,43,44,45,46,8,9}),"bounded special stage contract");
   }else{need(r.status==PROFILE_STORE_INVALID&&r.storage_fault_pending&&!r.storage_fault_triggered&&physical==snapshot&&profile_store.Generation()==before_generation,"invalid ticket/shape/version rejects before reconciliation");}
   if(special){
    ProfileStoreFaultControls::Arm(0,0,0,0,0,0,true);need(lfs_unmount(&fs)==0&&lfs_mount(&fs,&cfg)==0&&profile_store.Begin(1,2),"healthy simulated reboot/remount");need(!profile_store.IsTransactionUncertain()&&!profile_store.IsReadOnlyRecovery()&&profile_store.Generation()==before_generation+1,"later healthy reconciliation advances exactly once");
    auto receipt=profile_store.QueryTransaction(update.request_token);need(receipt.status==Status::Aborted&&receipt.revision==(mode=="special-create"?1u:2u)&&receipt.id==(mode=="special-create"?23u:22u),"aborted intended revision receipt");UltimateProfile actual;uint32_t revision=0;need(profile_store.Read(22,actual,&revision)==Status::Ok&&revision==1&&encode(actual)==encode(original),"latest healthy prior ID22 authority restored");
    ProfileStoreTransactionIdentity exact;need(ProfileStoreRequestIdentity(update,exact),"update identity");need(profile_store.QueryTransaction(exact).status==Status::Aborted,"exact aborted identity");exact.digest[0]^=1;need(profile_store.QueryTransaction(exact).status==Status::Conflict,"changed token identity conflicts");need(profile_store.LastTransactionToken()==update.request_token,"high water monotonic");auto unchanged=physical;need(profile_store.Update(22,intended,1,exact).status==Status::Conflict&&physical==unchanged,"changed request no execution or revision reuse");
    auto next=identity(update.request_token+1);need(profile_store.Create(original,"next",0,next).id==(mode=="special-create"?24u:23u),"ID allocation stays monotonic");need(lfs_unmount(&fs)==0&&lfs_mount(&fs,&cfg)==0&&profile_store.Begin(1,2)&&profile_store.Generation()==before_generation+2,"second reboot no extra aborted checkpoint");
   }
  }
 }
 need(lfs_unmount(&fs)==0,"unmount");std::printf("root_reconcile_%s=PASS candidate=%d frozen=%d pinned_littlefs=true\n",mode.c_str(),kStrictHardeningCandidate,
#ifdef EXPECT_FROZEN
 1
#else
 0
#endif
 );
}
}
lfs_t *CheckedStorageTestMount(){return &fs;}
int main(int argc,char**argv){try{need(argc==3,"arguments");run(argv[1],argv[2]);return 0;}catch(const std::exception&e){std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}}
