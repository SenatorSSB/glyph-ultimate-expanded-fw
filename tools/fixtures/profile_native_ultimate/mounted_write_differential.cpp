// Exact original/repaired DEFAULT MountedStorage primitive outcomes on real NOR.
#define GLYPH_STORE_PUBLICATION_NO_MAIN
#include "store_publication_nor.cpp"
CheckedStorage::Result GlyphMountedOutcome(const uint8_t *,size_t,unsigned &);
namespace {
CheckedStorage::Operation selected;CheckedStorage::Phase selected_phase;CheckedStorage::Fault selected_fault;bool dual;
CheckedStorage::Fault cut_mounted(Kind kind,CheckedStorage::Operation op,CheckedStorage::Phase phase,const char *path) {
    (void)record_io(kind,op,phase,path);
    if(dual&&op==CheckedStorage::Operation::Close&&phase==CheckedStorage::Phase::After)return CheckedStorage::Fault::LostAcknowledgement;
    return op==selected&&phase==selected_phase?selected_fault:CheckedStorage::Fault::None;
}
void one(unsigned number) {
    mount_fresh();io_trace.clear();io_index=0;fault_at=SIZE_MAX;unsigned diagnostic=999;const uint8_t bytes[]{11,22,33};CheckedStorage::SetFaultHook(cut_mounted);const auto result=GlyphMountedOutcome(bytes,sizeof(bytes),diagnostic);CheckedStorage::SetFaultHook(nullptr);require(mounted_fs.mlist==nullptr,"default Mounted closes all real handles");
    std::printf("case=%u result=%u,%u,%zu diagnostic=%u nor=%s trace=",number,unsigned(result.outcome),unsigned(result.operation),result.bytes,diagnostic,image_digest().c_str());for(auto&e:io_trace)std::printf("%s;",e.c_str());std::puts("");require(lfs_unmount(&mounted_fs)==0,"release direct mount");
}
}
int main(){try {unsigned cases=0;using namespace CheckedStorage;dual=false;selected=Operation::OpenWrite;selected_phase=Phase::Before;selected_fault=Fault::None;one(cases++);
    for(auto op:{Operation::OpenWrite,Operation::Write,Operation::Sync,Operation::Close}) {for(auto phase:{Phase::Before,Phase::After}) {for(auto fault:{Fault::Fail,Fault::LostAcknowledgement}) {selected=op;selected_phase=phase;selected_fault=fault;one(cases++);}}}
    dual=true;selected_phase=Phase::Before;selected_fault=Fault::Fail;for(auto op:{Operation::Write,Operation::Sync}){selected=op;one(cases++);}std::printf("PASS exact DEFAULT Mounted primitive Result/outcome/bytes/Remember/fullNOR traces cases=%u\n",cases);return 0;
 }catch(const std::exception&e){std::fprintf(stderr,"FAIL Mounted differential: %s\n",e.what());return 1;}}
