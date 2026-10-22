// Actual production Persistence + CheckedStorage over pinned 512KiB NOR/LittleFS.
// The included immutable harness supplies the mount only; no storage model is copied.
#define main unused_storage_fixture_main
#include "../profile_store_strict_host/strict_harness.cpp"
#undef main
#include "core/Persistence.hpp"
#include <CRC32.h>
namespace {
std::vector<std::string> trace;
size_t target_event=SIZE_MAX,event_index=0;
CheckedStorage::Fault target_fault=CheckedStorage::Fault::None;
bool fail_readback=false,publication_lost=false;
CheckedStorage::Fault observe_config(Kind kind,CheckedStorage::Operation op,CheckedStorage::Phase phase,const char *path) {
    if(kind!=Kind::Config)return CheckedStorage::Fault::None;
    std::string name=path?path:"";
    trace.push_back(std::to_string(unsigned(op))+":"+std::to_string(unsigned(phase))+":"+name);
    if(fail_readback && publication_lost && op==CheckedStorage::Operation::OpenRead && phase==CheckedStorage::Phase::Before && name=="config-v2.bin")return CheckedStorage::Fault::Fail;
    if(event_index++==target_event) {
        if(op==CheckedStorage::Operation::Rename&&phase==CheckedStorage::Phase::After&&name=="config-v2.tmp")publication_lost=true;
        return target_fault;
    }
    return CheckedStorage::Fault::None;
}
bool config_validator(const Config &c,ConfigValidationError &e) {return validate_config_semantics(c,e);}
Config make_config(unsigned selector) {
    Config c=Config_init_default;c.default_usb_backend_config=selector;c.communication_backend_configs_count=3;
    for(auto &b:c.communication_backend_configs){b.backend_id=COMMS_BACKEND_XINPUT;b.default_mode_config=1;}
    c.ultimate_profile_store_format=1;c.ultimate_profile_store_incarnation=7;c.game_mode_configs_count=1;
    c.game_mode_configs[0].mode_id=MODE_ULTIMATE;c.game_mode_configs[0].ultimate_profile_id=3;return c;
}
Bytes config_record(const Config &c) {
    size_t n=0;require(pb_get_encoded_size(&n,Config_fields,&c),"config encoded size");Bytes b(sizeof(Persistence::ConfigHeader)+n);
    auto out=pb_ostream_from_buffer(b.data()+sizeof(Persistence::ConfigHeader),n);require(pb_encode(&out,Config_fields,&c),"config encode");
    CRC32 crc;crc.update(b.data()+sizeof(Persistence::ConfigHeader),n);Persistence::ConfigHeader h;std::memset(&h,0,sizeof(h));h.config_size=n;h.config_crc=crc.finalize();std::memcpy(b.data(),&h,sizeof(h));return b;
}
std::string digest(const uint8_t *p,size_t n) {uint8_t d[32];Sha256 sha;sha.Update(p,n);sha.Final(d);char hex[65];for(unsigned i=0;i<32;++i)std::snprintf(hex+2*i,3,"%02x",d[i]);return hex;}
std::string canonical_files() {
    lfs_dir_t dir{};require(lfs_dir_open(&mounted_fs,&dir,"/")==0,"snapshot directory open");lfs_info entry{};std::vector<std::string> names;
    int rc;while((rc=lfs_dir_read(&mounted_fs,&dir,&entry))>0)if(entry.type==LFS_TYPE_REG)names.emplace_back(entry.name);
    require(rc==0&&lfs_dir_close(&mounted_fs,&dir)==0,"snapshot directory closed");std::sort(names.begin(),names.end());Sha256 sha;
    for(const auto &name:names) {
        size_t n=0;require(bool(CheckedStorage::Stat(name.c_str(),&n,Kind::Config)),"snapshot file size");Bytes b(n);require(bool(CheckedStorage::ReadFile(name.c_str(),b.data(),n,Kind::Config)),"snapshot exact file bytes");
        // ARM ConfigHeader is8 bytes with no padding. This 64-bit host has
        // four trailing padding bytes which C++ does not specify on the old
        // automatic header. Compare all fields/body bytes, excluding only
        // those host-only padding bytes, never CRC/data or target bytes.
        if(name.rfind("config",0)==0&&n>=sizeof(Persistence::ConfigHeader))
            for(size_t i=offsetof(Persistence::ConfigHeader,config_crc)+sizeof(uint32_t);i<sizeof(Persistence::ConfigHeader);++i)b[i]=0;
        sha.Update(reinterpret_cast<const uint8_t*>(name.c_str()),name.size()+1);sha.Update(b.data(),b.size());
    }
    uint8_t d[32];sha.Final(d);char hex[65];for(unsigned i=0;i<32;++i)std::snprintf(hex+2*i,3,"%02x",d[i]);return hex;
}
void format_mount() {
    CheckedStorage::SetFaultHook(nullptr);std::fill(physical.begin(),physical.end(),0xff);mounted_fs={};mounted_cfg={};
    mounted_cfg.read=ram_read;mounted_cfg.prog=ram_prog;mounted_cfg.erase=ram_erase;mounted_cfg.sync=ram_sync;
    mounted_cfg.read_size=mounted_cfg.prog_size=mounted_cfg.cache_size=256;mounted_cfg.block_size=4096;mounted_cfg.block_count=128;mounted_cfg.block_cycles=16;mounted_cfg.lookahead_size=256;
    require(lfs_format(&mounted_fs,&mounted_cfg)==0&&lfs_mount(&mounted_fs,&mounted_cfg)==0,"actual NOR mount");
}
void write_record(const char *name,const Config &c) {auto b=config_record(c);require(bool(CheckedStorage::WriteFile(name,b.data(),b.size(),Kind::Config)),"seed exact record");}
std::vector<std::string> run_case(const std::string &label,size_t target,CheckedStorage::Fault fault,bool readback_failure=false,bool stale=false,bool changed=false) {
    format_mount();Persistence p;require(p.SetValidator(config_validator),"production validator");write_record("config-v2.bin",make_config(1));write_record("config-v2.prev",make_config(2));
    const Bytes foreign{9,8,7};require(lfs_mkdir(&mounted_fs,"/unrelated")==0&&bool(CheckedStorage::WriteFile("/unrelated/keep",foreign.data(),foreign.size(),Kind::Config)),"broader namespace retained");
    Config loaded;require(p.LoadConfigChecked(loaded)==Persistence::LoadResult::Loaded,"normal durable generation seed");auto generation=p.ConfigGeneration(loaded);
    if(changed)write_record("config-v2.bin",make_config(2));
    auto candidate=make_config(3);trace.clear();event_index=0;target_event=target;target_fault=fault;fail_readback=readback_failure;publication_lost=false;CheckedStorage::SetFaultHook(observe_config);
    const auto result=p.SaveConfigIfGenerationMatches(candidate,uint64_t(generation)+(stale?1:0));CheckedStorage::SetFaultHook(nullptr);const auto captured=trace;
    require(mounted_fs.mlist==nullptr,"all constructor/explicit-close/destructor paths release actual handles");
    if(stale)require(result==Persistence::SaveResult::Conflict&&captured.empty(),"stale RAM generation performs no operation");
    if(changed)require(result==Persistence::SaveResult::Conflict,"fresh durable CRC compared before save");
    if(target==SIZE_MAX&&!stale&&!changed)require(result==Persistence::SaveResult::Saved&&!p.IsMutationFenced(),"normal exact publication");
    const auto raw_nor=digest(physical.data(),physical.size());const auto files=canonical_files();
    std::printf("%s result=%u fence=%u generation=%u nor=%s files=%s trace=",label.c_str(),unsigned(result),p.IsMutationFenced(),p.ConfigGeneration(candidate),raw_nor.c_str(),files.c_str());
    for(const auto &e:captured)std::printf("%s;",e.c_str());std::puts("");
    Config authoritative;require(p.ReconcileConfig(authoritative)==Persistence::SaveResult::Saved&&!p.IsMutationFenced(),"actual current/prior authority reconciles after injected boundary");
    require(p.SaveConfigIfGenerationMatches(candidate,p.ConfigGeneration(authoritative))==Persistence::SaveResult::Saved,"fresh next operation has reset slot/state and publishes once");
    require(mounted_fs.mlist==nullptr,"next operation owns no leftover handle");
    lfs_info info{};require(lfs_stat(&mounted_fs,"/unrelated/keep",&info)==0&&info.size==foreign.size(),"foreign directory untouched");
    require(lfs_unmount(&mounted_fs)==0&&lfs_mount(&mounted_fs,&mounted_cfg)==0,"reboot mount");Persistence reboot;require(reboot.SetValidator(config_validator)&&reboot.LoadConfigChecked(authoritative)==Persistence::LoadResult::Loaded&&authoritative.default_usb_backend_config==3,"checked durable publication survives reboot");
    require(lfs_unmount(&mounted_fs)==0,"release actual NOR mount");return captured;
}
}
#ifdef GLYPH_PERSISTENCE_NOR_NO_MAIN
int unused_persistence_save_main() {
#else
int main() {
#endif
    try {
        const auto success=run_case("success",SIZE_MAX,CheckedStorage::Fault::None);unsigned faults=0;
        for(size_t i=0;i<success.size();++i)for(auto fault:{CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement}) {
            run_case("fault-"+std::to_string(i)+"-"+std::to_string(unsigned(fault)),i,fault);++faults;
        }
        const std::string marker=std::to_string(unsigned(CheckedStorage::Operation::Rename))+":1:config-v2.tmp";
        const auto where=std::find(success.begin(),success.end(),marker);require(where!=success.end(),"actual publication trace found");
        run_case("lost-publication-unreadable",where-success.begin(),CheckedStorage::Fault::LostAcknowledgement,true);
        run_case("stale-memory",SIZE_MAX,CheckedStorage::Fault::None,false,true);
        run_case("changed-durable",SIZE_MAX,CheckedStorage::Fault::None,false,false,true);
        std::printf("PASS actual Persistence NOR/LittleFS trace/fault/reset/reconcile/reboot faults=%u events=%zu hardware=NOT_CLAIMED\n",faults,success.size());return 0;
    } catch(const std::exception&e){CheckedStorage::SetFaultHook(nullptr);std::fprintf(stderr,"FAIL actual Persistence NOR lifetimes: %s\n",e.what());return 1;}
}
