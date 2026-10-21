// Actual production phase3 reconciliation, exact old/new I/O and receipts.
#define GLYPH_STORE_PUBLICATION_NO_MAIN
#include "store_publication_nor.cpp"
namespace {
unsigned recovery_mode=0;bool initial_triggered=false;
CheckedStorage::Fault prepare_phase3(Kind,CheckedStorage::Operation op,CheckedStorage::Phase phase,const char *path) {
    if(initial_triggered||!path)return CheckedStorage::Fault::None;
    const char *root=recovery_mode==2?"/ultimate-v2-0.tmp":"/ultimate-v2-1.tmp";
    if(std::strcmp(path,root))return CheckedStorage::Fault::None;
    if(recovery_mode!=1&&op==CheckedStorage::Operation::OpenWrite&&phase==CheckedStorage::Phase::Before) {initial_triggered=true;return CheckedStorage::Fault::Fail;}
    if(recovery_mode==1&&op==CheckedStorage::Operation::Rename&&phase==CheckedStorage::Phase::After) {initial_triggered=true;return CheckedStorage::Fault::LostAcknowledgement;}
    return CheckedStorage::Fault::None;
}
std::vector<std::string> reconcile_case(unsigned mode,size_t index,CheckedStorage::Fault fault) {
    mount_fresh();ProfileStore store;require(store.Begin(),"initial roots");Config compact=Config_init_default;
    if(mode==2) {
        uint32_t ids[2]{};require(store.ImportLegacy(legacy,ids,2)==Status::Ok,"maintenance migration seed");compact=legacy;compact.ultimate_profiles_count=0;compact.ultimate_profile_store_format=1;compact.ultimate_profile_store_incarnation=store.Incarnation();
        for(size_t i=0;i<compact.game_mode_configs_count;++i){auto &m=compact.game_mode_configs[i];if(m.mode_id==MODE_ULTIMATE&&m.ultimate_profile_config){m.ultimate_profile_id=ids[m.ultimate_profile_config-1];m.ultimate_profile_config=0;}}
        require(store.PrepareCompact(compact),"maintenance actual receipt");
    } else {
        require(store.Create(legacy.ultimate_profiles[0],"one",1,identity(10)).status==Status::Ok&&store.Create(legacy.ultimate_profiles[1],"two",2,identity(11)).status==Status::Ok,"two seed records");
    }
    require(lfs_mkdir(&mounted_fs,"/unrelated")==0,"foreign directory admitted");const uint8_t mark[]{5,4,3};require(bool(CheckedStorage::WriteFile("/unrelated/keep",mark,sizeof(mark),Kind::Record)),"foreign contents");
    recovery_mode=mode;initial_triggered=false;CheckedStorage::SetFaultHook(prepare_phase3);
    if(mode==2)require(store.CompleteMigration(compact)==Status::UnknownOutcome,"maintenance phase3 checkpoint cut");
    else require(store.Create(legacy.ultimate_profiles[1],"attempt",3,identity(20)).status==Status::UnknownOutcome,"actual phase3 pending mutation cut");
    CheckedStorage::SetFaultHook(nullptr);require(initial_triggered&&mounted_fs.mlist==nullptr,"specific durable phase3 state and no handles");
    io_trace.clear();io_index=0;fault_at=index;fault_value=fault;CheckedStorage::SetFaultHook(record_io);
    ProfileStore reboot;const bool began=reboot.Begin(store.Incarnation(),2);
    CheckedStorage::SetFaultHook(nullptr);const auto observed=io_trace;require(mounted_fs.mlist==nullptr,"all reconciliation failure paths close handles");
    const auto before_query=image_digest();auto query=ProfileStore::TransactionResult{Status::Invalid};
    if(began&&!reboot.IsReadOnlyRecovery())query=reboot.QueryTransaction(identity(20));
    if(index==SIZE_MAX){require(began&&!reboot.IsTransactionUncertain()&&!reboot.IsReadOnlyRecovery(),"normal exact reconciliation");if(mode==0)require(query.status==Status::Aborted&&reboot.LastTransactionToken()==20&&reboot.Count()==2,"aborted attempted receipt and reserved highwater retained");if(mode==1)require(query.status==Status::Ok&&query.id==3&&reboot.Count()==3,"published request receipt retained");if(mode==2)require(reboot.LastTransactionToken()==0&&reboot.MigrationPending(),"maintenance checkpoint retains prior receipt/state");}
    std::printf("mode=%u fault=%zu/%u began=%u flags=%u uncertain=%u count=%zu generation=%u token=%llu query=%u,%u,%u,%u nor=%s trace=",mode,index,unsigned(fault),began,reboot.HealthFlags(),reboot.IsTransactionUncertain(),reboot.Count(),reboot.Generation(),(unsigned long long)reboot.LastTransactionToken(),unsigned(query.status),query.id,query.revision,query.generation,before_query.c_str());for(auto &e:observed)std::printf("%s;",e.c_str());std::puts("");
    if(index==SIZE_MAX){if(mode==2)require(reboot.CompleteMigration(compact)==Status::Ok,"maintenance retry after checkpoint");const auto next=reboot.Create(legacy.ultimate_profiles[0],"after",9,identity(1000000));require(next.status==Status::Ok&&next.id==(mode==2?3:4),"reserved ID is never reused after failed request");}
    require(mounted_fs.mlist==nullptr,"subsequent operation clean");lfs_info entry{};require(lfs_stat(&mounted_fs,"/unrelated/keep",&entry)==0&&entry.size==sizeof(mark),"foreign directory untouched");require(lfs_unmount(&mounted_fs)==0,"release recovery mount");return observed;
}
}
int main(int argc,char **argv) {try {
    require(argc==2,"legacy fixture");std::ifstream f(argv[1],std::ios::binary);Bytes b((std::istreambuf_iterator<char>(f)),{});auto pb=pb_istream_from_buffer(b.data(),b.size());require(pb_decode(&pb,Config_fields,&legacy)&&!pb.bytes_left,"actual fixture decode");unsigned faults=0;
    for(unsigned mode=0;mode<3;++mode){auto events=reconcile_case(mode,SIZE_MAX,CheckedStorage::Fault::None);for(size_t i=0;i<events.size();++i)for(auto fault:{CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement}){reconcile_case(mode,i,fault);++faults;}}
    std::printf("PASS actual NOR phase3 aborted/published/maintenance reconciliation and all recovery faults=%u; no device\n",faults);return 0;
 }catch(const std::exception&e){std::fprintf(stderr,"FAIL reconcile phases: %s\n",e.what());return 1;}}
