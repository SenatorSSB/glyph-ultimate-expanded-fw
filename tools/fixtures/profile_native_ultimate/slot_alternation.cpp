// Actual production Save/Capture share one synchronous raw File slot.
#define GLYPH_PERSISTENCE_NOR_NO_MAIN
#include "persistence_nor_lifetimes.cpp"
bool GlyphPersistenceSlotClean();
namespace {
unsigned point;CheckedStorage::Phase cut_phase;CheckedStorage::Fault cut_fault;bool after_remove,hit;
CheckedStorage::Fault cut_copy(Kind,CheckedStorage::Operation op,CheckedStorage::Phase phase,const char *path) {
    if(!path)return CheckedStorage::Fault::None;
    if(op==CheckedStorage::Operation::Remove&&phase==CheckedStorage::Phase::After&&std::strcmp(path,"/ultimate-migration.tmp")==0)after_remove=true;
    const bool input=std::strcmp(path,"config-v2.bin")==0,output=std::strcmp(path,"/ultimate-migration.tmp")==0;
    const auto wanted=point==0?CheckedStorage::Operation::OpenRead:point==1?CheckedStorage::Operation::OpenWrite:point==2?CheckedStorage::Operation::Write:point==3?CheckedStorage::Operation::Sync:CheckedStorage::Operation::Close;
    if(after_remove&&!hit&&phase==cut_phase&&op==wanted&&((point==0||point==4)?input:output)) {hit=true;return cut_fault;}
    return CheckedStorage::Fault::None;
}
void clean() {require(mounted_fs.mlist==nullptr&&GlyphPersistenceSlotClean(),"same raw slot is zero and all native handles retired after each operation");}
}
int main(){try {unsigned cases=0;for(point=0;point<6;++point) { for(auto phase:{CheckedStorage::Phase::Before,CheckedStorage::Phase::After}) { for(auto fault:{CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement}) {
    format_mount();write_record("config-v2.bin",make_config(1));Persistence first;require(first.SetValidator(config_validator),"first validator");after_remove=hit=false;cut_phase=phase;cut_fault=fault;CheckedStorage::SetFaultHook(cut_copy);uint8_t prior[32];(void)first.CaptureLegacySource(prior);CheckedStorage::SetFaultHook(nullptr);require(hit,"target actual copy primitive reached");clean();
    // New boot owner after uncertain/fenced failure; preserve original fence on first.
    Persistence reboot;require(reboot.SetValidator(config_validator),"reboot validator");require(bool(CheckedStorage::Remove("/ultimate-migration.src",Kind::Config)),"isolated test snapshot cleanup");Config candidate=make_config(2);require(reboot.SaveConfig(candidate),"failed Copy then Save succeeds with same slot");clean();uint8_t digest[32];require(reboot.CaptureLegacySource(digest),"Save then Capture exact bytes");clean();require(reboot.SaveConfig(candidate),"Copy then Save succeeds with same slot");clean();require(lfs_unmount(&mounted_fs)==0,"unmount alternation case");++cases;
 } } }
 std::printf("PASS actual Copy/failed-Copy→Save→Capture→Save alternation24 faults; same slot zero/native handles closed cases=%u\n",cases);return 0;
 }catch(const std::exception&e){std::fprintf(stderr,"FAIL slot alternation: %s\n",e.what());return 1;}}
