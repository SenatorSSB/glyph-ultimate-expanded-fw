// Actual pinned NOR/LittleFS, CheckedStorage and ProfileStore; no GC model.
// Foreign directories are host-seeded admitted filesystem states, not a claim
// that firmware exposes mkdir. Positive-orphan/power-loss images are separate.
#define main gc_unused_legacy_store_main
#include "../profile_store_strict_host/strict_harness.cpp"
#undef main
#include <set>
namespace {
struct Event { CheckedStorage::Operation op;CheckedStorage::Phase phase;std::string path; };
std::vector<Event> events;
CheckedStorage::Operation injected_op=CheckedStorage::Operation::None;
CheckedStorage::Phase injected_phase=CheckedStorage::Phase::Before;
CheckedStorage::Fault injected_fault=CheckedStorage::Fault::None;
unsigned injection_hits;
CheckedStorage::Fault observe(CheckedStorage::Kind,CheckedStorage::Operation op,CheckedStorage::Phase phase,const char *path) {
    events.push_back({op,phase,path?path:""});
    if(op==injected_op&&phase==injected_phase&&injection_hits++==0)return injected_fault;
    return CheckedStorage::Fault::None;
}
void observe_only() {injected_op=CheckedStorage::Operation::None;injection_hits=0;events.clear();CheckedStorage::SetFaultHook(observe);}
void stop_observing() {CheckedStorage::SetFaultHook(nullptr);}
bool exists(const std::string &p) {lfs_info info{};return lfs_stat(&mounted_fs,p.c_str(),&info)==0;}
void write_bytes(const std::string &p,const Bytes &b) {require(bool(CheckedStorage::WriteFile(p.c_str(),b.data(),b.size(),Kind::Record)),"host seed file "+p);}
Bytes read_bytes(const std::string &p) {
    size_t n=0;require(bool(CheckedStorage::Stat(p.c_str(),&n)),"readback stat "+p);Bytes b(n);
    require(bool(CheckedStorage::ReadFile(p.c_str(),b.data(),n,Kind::Record)),"readback bytes "+p);return b;
}
std::vector<std::string> before_removes() {
    std::vector<std::string> out;for(const auto &e:events)if(e.op==CheckedStorage::Operation::Remove&&e.phase==CheckedStorage::Phase::Before)out.push_back(e.path);return out;
}
std::vector<std::string> root_order(const std::set<std::string> &known) {
    lfs_dir_t dir{};require(lfs_dir_open(&mounted_fs,&dir,"/")==0,"independent root scan open");lfs_info entry{};std::vector<std::string> ordered;
    int rc;while((rc=lfs_dir_read(&mounted_fs,&dir,&entry))>0) {std::string p="/"+std::string(entry.name);if(entry.type==LFS_TYPE_REG&&known.count(p))ordered.push_back(p);}
    require(rc==0&&lfs_dir_close(&mounted_fs,&dir)==0,"independent root scan close");return ordered;
}
void verify_enumeration_before_removal() {
    bool enumerating=false,complete=false;
    for(const auto &e:events) {
        if(e.op==CheckedStorage::Operation::Enumerate&&e.phase==CheckedStorage::Phase::Before) {require(!enumerating,"enumeration never recursive");enumerating=true;complete=false;}
        if(e.op==CheckedStorage::Operation::Enumerate&&e.phase==CheckedStorage::Phase::After) {require(enumerating,"enumeration after matching before");enumerating=false;complete=true;}
        if(e.op==CheckedStorage::Operation::Remove&&e.phase==CheckedStorage::Phase::Before) {require(!enumerating&&complete,"directory callback/handle finishes before remove");complete=false;}
    }
}
void fresh_mount() {
    stop_observing();std::fill(physical.begin(),physical.end(),0xff);
    mounted_fs={};mounted_cfg={};mounted_cfg.read=ram_read;mounted_cfg.prog=ram_prog;mounted_cfg.erase=ram_erase;mounted_cfg.sync=ram_sync;
    mounted_cfg.read_size=mounted_cfg.prog_size=mounted_cfg.cache_size=256;mounted_cfg.block_size=4096;mounted_cfg.block_count=128;mounted_cfg.block_cycles=16;mounted_cfg.lookahead_size=256;
    require(lfs_format(&mounted_fs,&mounted_cfg)==0&&lfs_mount(&mounted_fs,&mounted_cfg)==0,"real NOR/LittleFS fresh mount");
}
struct Seed {
    uint32_t generation,active,revision;uint64_t token;size_t count;std::map<std::string,Bytes> retained;
};
Seed seed(ProfileStore &s) {
    require(s.Begin(),"normal production roots");uint8_t digest[32];source_hash(legacy,digest);
    size_t n=0;require(pb_get_encoded_size(&n,Config_fields,&legacy),"migration source size");Bytes wire(n);auto out=pb_ostream_from_buffer(wire.data(),wire.size());require(pb_encode(&out,Config_fields,&legacy),"migration source encoding");
    write_bytes("/ultimate-migration.src",wire);uint32_t ids[2]{};
    require(s.ImportLegacyStream(legacy,digest,legacy_reader,&legacy,ids,2)==Status::Ok,"real migration seed");Config compact=legacy;
    require(s.PrepareCompact(compact)&&s.CompleteMigration(compact)==Status::Ok,"real migration dependency protection");
    auto created=s.Create(legacy.ultimate_profiles[0],"active",3,identity(10));require(created.status==Status::Ok,"active profile seed");
    Status activated;require(s.Activate(created.id,&activated)&&activated==Status::Ok,"active r1 before updates");
    require(s.Update(created.id,legacy.ultimate_profiles[1],1,identity(11)).status==Status::Ok&&s.Update(created.id,legacy.ultimate_profiles[0],2,identity(12)).status==Status::Ok,"current/previous/active distinct revisions");
    require(lfs_mkdir(&mounted_fs,"/foreign")==0&&lfs_mkdir(&mounted_fs,"/foreign/nested")==0&&lfs_mkdir(&mounted_fs,"/ultimate-0000dddd-00000001.bin")==0,"admitted unrelated physical directories");
    write_bytes("/foreign/nested/ultimate-0000eeee-00000001.tmp",{7,8,9});write_bytes("/foreign.txt",{3,1,4});write_bytes("/ultimate-malformed.bin",{2,7,1});write_bytes("/ultimate-0000aaaa-00000001.bak",{8,2,8});
    Seed state{s.Generation(),s.ActiveId(),s.ActiveRevision(),s.LastTransactionToken(),s.Count(),{}};
    for(const auto &p:{record_path(ids[0],1),record_path(ids[1],1),record_path(created.id,1),record_path(created.id,2),record_path(created.id,3),std::string("/ultimate-migration.src"),std::string("/foreign/nested/ultimate-0000eeee-00000001.tmp"),std::string("/foreign.txt"),std::string("/ultimate-malformed.bin"),std::string("/ultimate-0000aaaa-00000001.bak")})state.retained[p]=read_bytes(p);
    return state;
}
void verify_retained(ProfileStore &s,const Seed &seeded) {
    require(s.Generation()==seeded.generation&&s.LastTransactionToken()==seeded.token&&s.Count()==seeded.count&&s.ActiveId()==seeded.active&&s.ActiveRevision()==seeded.revision,"GC never publishes authority/receipt/active changes");
    require(exists("/foreign")&&exists("/foreign/nested")&&exists("/ultimate-0000dddd-00000001.bin"),"unrelated and matching-name physical directories retained");
    for(const auto &entry:seeded.retained)require(read_bytes(entry.first)==entry.second,"protected/unrelated bytes retained "+entry.first);
}
std::set<std::string> garbage(unsigned count,unsigned start=0x10000) {
    std::set<std::string> result;for(unsigned i=0;i<count;++i) {auto p=record_path(start+i,1);if(i&1)p.replace(p.size()-3,3,"tmp");write_bytes(p,{uint8_t(i),99});result.insert(p);}return result;
}
void clean_unmount() {stop_observing();require(mounted_fs.mlist==nullptr,"all actual file/directory handles released");require(lfs_unmount(&mounted_fs)==0,"real mount closes");}
void clean_and_repeated() {
    fresh_mount();ProfileStore s;const auto saved=seed(s);observe_only();require(s.CollectGarbage()==Status::Ok,"no candidates");require(before_removes().empty(),"no deletion invented on empty root");stop_observing();verify_retained(s,saved);
    auto stale=garbage(3);const auto expected=root_order(stale);observe_only();require(s.CollectGarbage()==Status::Ok,"three genuine unprotected records collected");require(before_removes()==expected,"first-match real enumeration order");verify_enumeration_before_removal();stop_observing();verify_retained(s,saved);
    observe_only();require(s.CollectGarbage()==Status::Ok&&before_removes().empty(),"completed prior candidate cannot survive into fresh call");stop_observing();
    auto fresh=garbage(1,0x20000);observe_only();require(s.CollectGarbage()==Status::Ok&&before_removes()==std::vector<std::string>(fresh.begin(),fresh.end()),"new call removes only its actual new candidate");stop_observing();verify_retained(s,saved);clean_unmount();pass("actual_gc_foreign_dirs_protected_migration_active_repeated_reset");
}
void fault_reset() {
    for(auto op:{CheckedStorage::Operation::Enumerate,CheckedStorage::Operation::Remove})for(auto phase:{CheckedStorage::Phase::Before,CheckedStorage::Phase::After})for(auto fault:{CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement}) {
        fresh_mount();ProfileStore s;const auto saved=seed(s);auto candidates=garbage(2);const auto order=root_order(candidates);observe_only();injected_op=op;injected_phase=phase;injected_fault=fault;
        require(s.CollectGarbage()==Status::IoFailure&&injection_hits==1,"real injected enumeration/remove failure returned once");
        if(op==CheckedStorage::Operation::Enumerate)require(before_removes().empty(),"enumeration failure never removes selected/old output");
        else {require(before_removes()==std::vector<std::string>{order.front()},"remove failure stops after first selected candidate");require(exists(order.front())==(phase==CheckedStorage::Phase::Before),"actual before/after remove outcome preserved");}
        stop_observing();verify_retained(s,saved);require(!s.IsTransactionUncertain(),"GC retains existing failure/fence policy");
        observe_only();require(s.CollectGarbage()==Status::Ok,"fresh call recovers actual remaining candidates");verify_enumeration_before_removal();stop_observing();
        for(const auto &p:candidates)require(!exists(p),"all remaining candidates collected after fault");verify_retained(s,saved);clean_unmount();
    }
    pass("actual_gc_16_faults_reset_handles_next_operation");
}
void budget_and_admission() {
    for(unsigned count:{128u,129u}) {
        fresh_mount();ProfileStore s;const auto saved=seed(s);auto candidates=garbage(count);const auto ordered=root_order(candidates);observe_only();
        const auto failed=s.Create(legacy.ultimate_profiles[0],"after-budget",9,identity(30));
        require(failed.status==Status::Full,"128 removal budget returns Full even exactly emptied");const auto removed=before_removes();require(removed.size()==128&&std::equal(removed.begin(),removed.end(),ordered.begin()),"exact 128 first-match removals, no reordered batch");
        require(std::none_of(events.begin(),events.end(),[](const Event &e){return e.op==CheckedStorage::Operation::Capacity;}),"Capacity phase never runs after GC Full");verify_enumeration_before_removal();stop_observing();verify_retained(s,saved);
        unsigned remaining=0;for(const auto &p:candidates)remaining+=exists(p);require(remaining==count-128,"exact bounded leftovers");
        observe_only();const auto next=s.Create(legacy.ultimate_profiles[0],"after-budget",9,identity(30));require(next.status==Status::Ok,"same unconsumed receipt retries after GC budget");
        require(before_removes().size()==count-128,"retry starts with fresh remaining search");stop_observing();require(s.Count()==saved.count+1&&s.LastTransactionToken()==30,"only successful retry publishes profile and receipt");clean_unmount();
    }
    pass("actual_gc_128_129_budget_capacity_order_same_token_retry");
}
}
int main(int argc,char **argv) {
    try {
        require(argc==2,"gc-lifetime LEGACY_CONFIG");std::ifstream input(argv[1],std::ios::binary);Bytes b((std::istreambuf_iterator<char>(input)),{});auto stream=pb_istream_from_buffer(b.data(),b.size());
        require(pb_decode(&stream,Config_fields,&legacy)&&!stream.bytes_left&&legacy.ultimate_profiles_count==2,"real admitted legacy source");
        clean_and_repeated();fault_reset();budget_and_admission();
        std::puts("PASS actual broader-namespace GC lifetime/reset/fault/128budget; positive-orphan and PENDING_MOVE compaction witness separately pending; target stack/timing NOT_MEASURED");return 0;
    } catch(const std::exception &e) {std::fprintf(stderr,"FAIL native GC lifetime: %s\n",e.what());return 1;}
}
