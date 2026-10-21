// Differential actual production ProfileStore publication on pinned NOR/LFS.
#define main unused_legacy_publication_fixture
#include "../profile_store_strict_host/strict_harness.cpp"
#undef main
namespace {
std::vector<std::string> io_trace;
size_t fault_at=SIZE_MAX,io_index=0;
CheckedStorage::Fault fault_value=CheckedStorage::Fault::None;
CheckedStorage::Fault record_io(Kind kind,CheckedStorage::Operation op,CheckedStorage::Phase phase,const char *path) {
    io_trace.push_back(std::to_string(unsigned(kind))+":"+std::to_string(unsigned(op))+":"+std::to_string(unsigned(phase))+":"+(path?path:""));
    return io_index++==fault_at?fault_value:CheckedStorage::Fault::None;
}
std::string image_digest() {uint8_t d[32];Sha256 h;h.Update(physical.data(),physical.size());h.Final(d);char result[65];for(unsigned i=0;i<32;++i)std::snprintf(result+i*2,3,"%02x",d[i]);return result;}
void mount_fresh() {
    CheckedStorage::SetFaultHook(nullptr);std::fill(physical.begin(),physical.end(),0xff);mounted_fs={};mounted_cfg={};
    mounted_cfg.read=ram_read;mounted_cfg.prog=ram_prog;mounted_cfg.erase=ram_erase;mounted_cfg.sync=ram_sync;
    mounted_cfg.read_size=mounted_cfg.prog_size=mounted_cfg.cache_size=256;mounted_cfg.block_size=4096;mounted_cfg.block_count=128;mounted_cfg.block_cycles=16;mounted_cfg.lookahead_size=256;
    require(lfs_format(&mounted_fs,&mounted_cfg)==0&&lfs_mount(&mounted_fs,&mounted_cfg)==0,"actual publication NOR mount");
}
std::vector<std::string> publication_case(unsigned op,size_t index,CheckedStorage::Fault fault) {
    mount_fresh();ProfileStore store;require(store.Begin(),"seed portable roots");
    auto one=store.Create(legacy.ultimate_profiles[0],"one",1,identity(10));auto two=store.Create(legacy.ultimate_profiles[1],"two",2,identity(11));
    require(one.status==Status::Ok&&two.status==Status::Ok,"seed exact profiles");Status active;require(store.Activate(one.id,&active)&&active==Status::Ok,"retain active immutable previous revision");
    require(lfs_mkdir(&mounted_fs,"/unrelated")==0,"admitted foreign directory");uint8_t keep[]{4,8,15};require(bool(CheckedStorage::WriteFile("/unrelated/keep",keep,sizeof(keep),Kind::Record)),"foreign bytes seed");
    io_trace.clear();io_index=0;fault_at=index;fault_value=fault;CheckedStorage::SetFaultHook(record_io);
    ProfileStore::TransactionResult result;
    switch(op) {
        case 0:result=store.Create(legacy.ultimate_profiles[1],"created",7,identity(20));break;
        case 1:result=store.Update(one.id,legacy.ultimate_profiles[1],1,identity(20));break;
        case 2:result=store.Duplicate(one.id,1,"duplicated",7,identity(20));break;
        case 3:result=store.Rename(one.id,"renamed",store.Generation(),identity(20));break;
        case 4:result=store.Reorder(one.id,7,store.Generation(),identity(20));break;
        case 5:result=store.Delete(two.id,store.Generation(),0,identity(20));break;
        default:require(false,"operation range");
    }
    CheckedStorage::SetFaultHook(nullptr);const auto observed=io_trace;
    require(mounted_fs.mlist==nullptr,"publication/fault leaves no file or directory handle");
    if(index==SIZE_MAX)require(result.status==Status::Ok,"normal publication succeeds");
    std::printf("op=%u fault=%zu/%u result=%u,%u,%u,%u store=%u,%zu,%llu flags=%u uncertain=%u active=%u,%u diag=%s nor=%s trace=",op,index,unsigned(fault),unsigned(result.status),result.id,result.revision,result.generation,store.Generation(),store.Count(),(unsigned long long)store.LastTransactionToken(),store.HealthFlags(),store.IsTransactionUncertain(),store.ActiveId(),store.ActiveRevision(),store.LastDiagnostic(),image_digest().c_str());
    for(const auto &e:observed)std::printf("%s;",e.c_str());std::puts("");
    const auto incarnation=store.Incarnation();ProfileStore reboot;require(reboot.Begin(incarnation,2),"reboot retains checked current/previous authority");
    if(!reboot.IsReadOnlyRecovery()&&!reboot.IsTransactionUncertain()) {
        const auto next=reboot.Create(legacy.ultimate_profiles[0],"next",9,identity(1000000));require(next.status==Status::Ok,"fresh next operation after failure has no stale phase metadata");
    }
    require(mounted_fs.mlist==nullptr,"reboot/next operation closes every handle");lfs_info info{};require(lfs_stat(&mounted_fs,"/unrelated/keep",&info)==0&&info.size==sizeof(keep),"foreign namespace retained");
    require(lfs_unmount(&mounted_fs)==0,"actual publication unmount");return observed;
}
}
#ifdef GLYPH_STORE_PUBLICATION_NO_MAIN
int unused_store_publication_main(int argc,char **argv) {
#else
int main(int argc,char **argv) {
#endif
    try {
        require(argc>=2&&argc<=3,"publication fixture path and optional smoke");std::ifstream file(argv[1],std::ios::binary);Bytes b((std::istreambuf_iterator<char>(file)),{});auto input=pb_istream_from_buffer(b.data(),b.size());require(pb_decode(&input,Config_fields,&legacy)&&!input.bytes_left&&legacy.ultimate_profiles_count==2,"production-admitted fixture decode");
        unsigned count=0;for(unsigned op=0;op<6;++op) {
            const auto success=publication_case(op,SIZE_MAX,CheckedStorage::Fault::None);
            if(argc==2)for(size_t i=0;i<success.size();++i)for(auto fault:{CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement}){publication_case(op,i,fault);++count;}
        }
        std::printf("PASS actual portable Store publication traces/results/generations/fences/receipts/reboot/reset all6operations faults=%u hardware=NOT_CLAIMED\n",count);return 0;
    }catch(const std::exception&e){CheckedStorage::SetFaultHook(nullptr);std::fprintf(stderr,"FAIL actual Store publication NOR: %s\n",e.what());return 1;}
}
