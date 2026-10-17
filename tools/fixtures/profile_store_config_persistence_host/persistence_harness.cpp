#include <LittleFS.h>
#include <CRC32.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include "core/Persistence.hpp"
#include "core/Sha256.hpp"
#include <iostream>
#include <type_traits>
static_assert(!std::has_virtual_destructor<Print>::value && !std::has_virtual_destructor<Stream>::value, "host fixture matches pinned Arduino Print/Stream destructor contract");
#include <stdexcept>
using Bytes=std::vector<uint8_t>;using Save=Persistence::SaveResult;
static unsigned cases=0;
static CheckedStorage::Operation fault_operation;
static CheckedStorage::Phase fault_phase;
static std::string fault_path;
static CheckedStorage::Fault checked_fault(CheckedStorage::Kind k,CheckedStorage::Operation op,CheckedStorage::Phase p,const char *path){
 if(k==CheckedStorage::Kind::Config&&op==fault_operation&&p==fault_phase&&path==fault_path)return p==CheckedStorage::Phase::Before?CheckedStorage::Fault::Fail:CheckedStorage::Fault::LostAcknowledgement;
 return CheckedStorage::Fault::None;
}
static void checked_inject(CheckedStorage::Operation op,CheckedStorage::Phase phase,const char *path){fault_operation=op;fault_phase=phase;fault_path=path;CheckedStorage::SetFaultHook(checked_fault);}

static void require(bool value,const std::string &why){if(!value)throw std::runtime_error(why);}
static bool validator(const Config &c,ConfigValidationError &e){return validate_config_semantics(c,e);}
// Persistence's bounded extent validator remains an independent production input.
static Bytes encode(const Config &c){size_t n=0;require(pb_get_encoded_size(&n,Config_fields,&c),"size");Bytes b(n);auto s=pb_ostream_from_buffer(b.data(),b.size());require(pb_encode(&s,Config_fields,&c),"encode");return b;}
static Bytes record(const Config &c){auto b=encode(c);CRC32 crc;crc.update(b.data(),b.size());Persistence::ConfigHeader h{};h.config_size=b.size();h.config_crc=crc.finalize();Bytes r(sizeof(h)+b.size());std::memcpy(r.data(),&h,sizeof(h));std::memcpy(r.data()+sizeof(h),b.data(),b.size());return r;}
static Bytes get(const char *p){return *LittleFS.files.at(p);}
static bool same_record(const Bytes &a,const Bytes &b){if(a.size()!=b.size()||a.size()<sizeof(Persistence::ConfigHeader))return false;Persistence::ConfigHeader x,y;std::memcpy(&x,a.data(),sizeof(x));std::memcpy(&y,b.data(),sizeof(y));return x.config_size==y.config_size&&x.config_crc==y.config_crc&&std::equal(a.begin()+sizeof(x),a.end(),b.begin()+sizeof(y));}
static void put(const char *p,const Bytes &b){LittleFS.files[p]=std::make_shared<Bytes>(b);}
static Config config(uint8_t selector){Config c=Config_init_default;c.default_usb_backend_config=selector;c.communication_backend_configs_count=3;for(auto &b:c.communication_backend_configs){b.backend_id=COMMS_BACKEND_XINPUT;b.default_mode_config=1;}c.ultimate_profile_store_format=1;c.ultimate_profile_store_incarnation=7;c.game_mode_configs_count=1;c.game_mode_configs[0].mode_id=MODE_ULTIMATE;c.game_mode_configs[0].ultimate_profile_id=3;return c;}
static void pass(const std::string &name){++cases;std::cout<<name<<"=PASS\n";}
int main(){try{
 const Config old=config(1),next=config(3);const Bytes initial=record(old),legacy={0x31,0x32};
 auto seed=[&](Persistence &p){LittleFS.reset();put("config-v2.bin",initial);put("config.bin",legacy);require(p.SetValidator(validator),"validator");Config loaded;require(p.LoadConfigChecked(loaded)==Persistence::LoadResult::Loaded,"seed load");return p.ConfigGeneration(loaded);};
 {Persistence p;auto gen=seed(p);auto candidate=next;unsigned m=LittleFS.mutations;require(p.SaveConfigIfGenerationMatches(candidate,uint64_t(gen)+1)==Save::Conflict,"stale cache");require(LittleFS.mutations==m&&get("config-v2.bin")==initial,"stale cache no mutation");pass("stale_cache");}
 {Persistence p;auto gen=seed(p);auto candidate=next;LittleFS.files.erase("config-v2.bin");LittleFS.files.erase("config.bin");auto m=LittleFS.mutations;require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::StorageFailure,"missing durable guard");require(LittleFS.mutations==m,"missing durable no writes");Config caller=old;require(p.LoadConfigChecked(caller)==Persistence::LoadResult::StorageFailure&&encode(caller)==encode(old),"missing load preserves caller");pass("missing_durable_load_and_save");}
 {Persistence p;auto gen=seed(p);auto candidate=next;put("config-v2.bin",record(config(2)));auto before=get("config-v2.bin");unsigned m=LittleFS.mutations;require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::Conflict,"durable changed");require(get("config-v2.bin")==before&&LittleFS.mutations==m,"durable race no mutation");pass("durable_generation_changed");}
 for(const std::string fault:{"open:config-v2.bin","read:config-v2.bin","open:config-v2.tmp","write:config-v2.tmp","read:config-v2.tmp","rename:config-v2.bin","rename:config-v2.tmp"}){
  Persistence p;auto gen=seed(p);auto candidate=next;LittleFS.fault=fault;
  require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::StorageFailure,fault+": result");
  require(get("config-v2.bin")==initial,fault+": durable preserved");require(get("config.bin")==legacy,fault+": legacy preserved");require(p.ConfigGeneration(candidate)==gen,fault+": generation preserved");require(encode(candidate)==encode(next),fault+": caller preserved");pass(fault);
 }
 {Persistence p;auto gen=seed(p);put("config-v2.prev",record(config(2)));auto previous=get("config-v2.prev");auto candidate=next;LittleFS.fault="remove:config-v2.prev";require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::StorageFailure,"prior removal refused");require(get("config-v2.bin")==initial&&get("config-v2.prev")==previous&&get("config.bin")==legacy,"prior removal refusal preserves anchors");pass("prior_remove_failure");}
 for(unsigned at:{2u,3u}){Persistence p;auto gen=seed(p);auto candidate=next;LittleFS.fail_write_call=at;require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::StorageFailure,"partial-write failure");require(get("config-v2.bin")==initial&&get("config.bin")==legacy,"partial-write durable exact");require(p.ConfigGeneration(candidate)==gen,"partial-write generation unchanged");pass("partial_write_call_"+std::to_string(at));}
 {Persistence p;auto gen=seed(p);auto candidate=next;auto corrupt=initial;corrupt.back()^=1;put("config-v2.bin",corrupt);auto m=LittleFS.mutations;require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::StorageFailure,"CRC mismatch guard");require(get("config-v2.bin")==corrupt&&LittleFS.mutations==m,"CRC mismatch no writes");pass("durable_crc_mismatch");}
 {Persistence p;auto gen=seed(p);auto candidate=next;put("config-v2.bin",Bytes{1,2});unsigned m=LittleFS.mutations;require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::StorageFailure,"malformed result");require(get("config-v2.bin")==Bytes({1,2})&&LittleFS.mutations==m,"malformed unchanged");pass("malformed_durable");}
 {Persistence p;seed(p);put("config-v2.bin",record(config(99)));Config caller=old;require(p.LoadConfigChecked(caller)==Persistence::LoadResult::Rejected,"semantic load reject");require(encode(caller)==encode(old),"failed load caller unchanged");pass("load_rejected_preserves_caller");}
 {Persistence p;auto gen=seed(p);auto candidate=next;LittleFS.fault="postpublish-open";require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::Saved,"rename publication success");require(same_record(get("config-v2.bin"),record(next))&&get("config-v2.prev")==initial,"published and prior exact");require(get("config.bin")==legacy,"legacy immutable");Persistence::ConfigHeader h;auto bytes=get("config-v2.bin");std::memcpy(&h,bytes.data(),sizeof(h));require(p.ConfigGeneration(candidate)==h.config_crc,"generation published");LittleFS.fault.clear();Config reboot;require(p.LoadConfigChecked(reboot)==Persistence::LoadResult::Loaded&&encode(reboot)==encode(next),"reboot current");pass("successful_publish_no_postcommit_false");}
 for(bool fail:{false,true}){Persistence p;auto gen=seed(p);require(LittleFS.rename("config-v2.bin","config-v2.prev"),"prior-only seed");auto candidate=next;LittleFS.fault=fail?"rename:config-v2.tmp":"";require(p.SaveConfigIfGenerationMatches(candidate,gen)==(fail?Save::StorageFailure:Save::Saved),"prior-only save result");require(get("config-v2.prev")==initial,"prior-only durable anchor preserved");require(get("config.bin")==legacy,"prior-only legacy preserved");if(!fail)require(same_record(get("config-v2.bin"),record(next)),"prior-only published");pass(fail?"prior_only_publish_failure":"prior_only_publish_success");}
 {Persistence p;seed(p);require(LittleFS.rename("config-v2.bin","config-v2.prev"),"interrupt rotation");put("config-v2.tmp",record(next));Config reboot;require(p.LoadConfigChecked(reboot)==Persistence::LoadResult::Loaded,"prior recovery");require(encode(reboot)==encode(old)&&get("config-v2.bin")==initial,"prior restored");require(get("config.bin")==legacy,"legacy preserved recovery");pass("interrupted_rotation_prior_recovery");}

 for(auto op:{CheckedStorage::Operation::Sync,CheckedStorage::Operation::Close})for(auto phase:{CheckedStorage::Phase::Before,CheckedStorage::Phase::After}){
  Persistence p;auto gen=seed(p);auto candidate=next;checked_inject(op,phase,"config-v2.tmp");
  const bool uncertain=phase==CheckedStorage::Phase::After;
  require(p.SaveConfigIfGenerationMatches(candidate,gen)==(uncertain?Save::Uncertain:Save::StorageFailure),"checked staging boundary refuses");
  require(get("config-v2.bin")==initial&&get("config.bin")==legacy&&p.IsMutationFenced()==uncertain,"staging uncertainty preserved through close");
  auto mutations=LittleFS.mutations;if(uncertain)require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::Uncertain&&LittleFS.mutations==mutations,"uncertain stage fences next writer");
  CheckedStorage::SetFaultHook(nullptr);if(uncertain){Config reconciled;require(p.ReconcileConfig(reconciled)==Save::Saved&&!p.IsMutationFenced()&&encode(reconciled)==encode(old),"staging reconciliation proves old authority");}pass("checked_config_staging_sync_close");
 }
 {Persistence p;auto gen=seed(p);auto candidate=next;checked_inject(CheckedStorage::Operation::Rename,CheckedStorage::Phase::After,"config-v2.tmp");
  require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::Saved&&!p.IsMutationFenced(),"lost rename resolved by exact bytes");
  require(same_record(get("config-v2.bin"),record(next)),"lost ack committed exact");CheckedStorage::SetFaultHook(nullptr);pass("lost_ack_resolved_exact");}
 {Persistence p;auto gen=seed(p);auto candidate=next;checked_inject(CheckedStorage::Operation::Rename,CheckedStorage::Phase::After,"config-v2.tmp");LittleFS.fault="postpublish-open";
  require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::Uncertain&&p.IsMutationFenced(),"unknown publication fenced");
  auto mutations=LittleFS.mutations;require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::Uncertain&&LittleFS.mutations==mutations,"unknown cannot admit next writer");
  Config authoritative;require(p.ReconcileConfig(authoritative)==Save::Uncertain&&p.IsMutationFenced(),"unreadable unresolved retained");
  LittleFS.fault.clear();CheckedStorage::SetFaultHook(nullptr);require(p.ReconcileConfig(authoritative)==Save::Saved&&!p.IsMutationFenced()&&encode(authoritative)==encode(next),"readback reconciliation updates generation and Config");pass("unknown_fence_and_reconcile");}
 {Persistence p;seed(p);Config source=old;source.ultimate_profile_store_format=0;source.ultimate_profiles_count=2;source.ultimate_profiles[0].schema_version=1;source.ultimate_profiles[1].schema_version=3;
  const auto raw=record(source);put("config-v2.bin",raw);uint8_t digest[32],expected[32];Sha256 sha;sha.Update(raw.data(),raw.size());sha.Final(expected);
  require(p.CaptureLegacySource(digest)&&!std::memcmp(digest,expected,32)&&get("/ultimate-migration.src")==raw,"exact persisted source captured");
  UltimateProfile profile;require(p.ReadLegacyProfile(0,profile)==Persistence::LoadResult::Loaded&&profile.schema_version==1,"stream first source profile");require(p.ReadLegacyProfile(1,profile)==Persistence::LoadResult::Loaded&&profile.schema_version==3,"stream second source profile");require(p.ReadLegacyProfile(2,profile)==Persistence::LoadResult::StorageFailure,"stream count bound");
  require(p.CaptureLegacySource(digest),"same source capture retry");source.rgb_brightness=9;put("config-v2.bin",record(source));require(!p.CaptureLegacySource(digest)&&get("/ultimate-migration.src")==raw,"changed source refuses unrelated receipt");
  put("config-v2.bin",record(next));require(p.LegacySourceIdentity(digest)&&!std::memcmp(digest,expected,32),"immutable source survives compact replacement");
  (*LittleFS.files.at("/ultimate-migration.src")).back()^=1;require(!p.LegacySourceIdentity(digest),"corrupt dependency rejected");pass("bounded_immutable_legacy_source");}

 {Persistence p;seed(p);Config source=old;source.ultimate_profile_store_format=0;source.ultimate_profiles_count=1;source.ultimate_profiles[0].schema_version=1;put("config-v2.bin",record(source));CheckedStorage::Geometry geometry;require(bool(CheckedStorage::Capacity(geometry)),"source reserve geometry");const size_t foreign=geometry.free_bytes-32768;put("/foreign",Bytes(foreign));auto mutations=LittleFS.mutations;uint8_t digest[32];require(!p.CaptureLegacySource(digest)&&LittleFS.mutations==mutations&&!LittleFS.exists("/ultimate-migration.src"),"source capture refuses before destroying reserve");pass("legacy_snapshot_reserve_preflight");}
 for(auto op:{CheckedStorage::Operation::Sync,CheckedStorage::Operation::Close,CheckedStorage::Operation::Rename})for(auto phase:{CheckedStorage::Phase::Before,CheckedStorage::Phase::After}){
  Persistence p;seed(p);Config source=old;source.ultimate_profile_store_format=0;source.ultimate_profile_store_incarnation=0;source.game_mode_configs[0].ultimate_profile_id=0;source.ultimate_profiles_count=0;put("config-v2.bin",record(source));const auto original=get("config-v2.bin");checked_inject(op,phase,"/ultimate-migration.tmp");uint8_t digest[32];const bool captured=p.CaptureLegacySource(digest);const bool published=op==CheckedStorage::Operation::Rename&&phase==CheckedStorage::Phase::After;
  require(captured==published&&get("config-v2.bin")==original&&get("config.bin")==legacy,"snapshot fault preserves sources");CheckedStorage::SetFaultHook(nullptr);if(p.IsMutationFenced()){Config authoritative;require(p.ReconcileConfig(authoritative)==Save::Saved&&!p.IsMutationFenced(),"snapshot stageunknown reconciled");}require(p.CaptureLegacySource(digest)&&get("/ultimate-migration.src")==original,"snapshot fault retry exact");pass("legacy_snapshot_checked_fault_retry");
 }

 for(auto op:{CheckedStorage::Operation::OpenWrite,CheckedStorage::Operation::Write,CheckedStorage::Operation::Read}){
  Persistence p;auto gen=seed(p);auto candidate=next;checked_inject(op,CheckedStorage::Phase::After,"config-v2.tmp");
  require(p.SaveConfigIfGenerationMatches(candidate,gen)==Save::Uncertain&&p.IsMutationFenced()&&get("config-v2.bin")==initial,"early unknown persists through cleanup close");
  CheckedStorage::SetFaultHook(nullptr);Config authoritative;require(p.ReconcileConfig(authoritative)==Save::Saved&&!p.IsMutationFenced()&&encode(authoritative)==encode(old),"earlyunknown reconciles authority");pass("config_staging_open_write_read_unknown");
 }
 std::cout<<"current_persistence_cases="<<cases<<" target_FS_power_loss=NOT_EMULATED\n";return 0;
}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
