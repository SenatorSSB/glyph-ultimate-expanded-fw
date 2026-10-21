// Actual production Load/Capture differential on pinned NOR/LittleFS.
#define GLYPH_PERSISTENCE_NOR_NO_MAIN
#include "persistence_nor_lifetimes.cpp"
namespace {
std::vector<std::string> run_load_capture(const std::string &label,const std::string &kind,size_t target,CheckedStorage::Fault fault) {
    format_mount(); Persistence p; require(p.SetValidator(config_validator),"actual validator");
    const char *source=kind.find("prior")!=std::string::npos?"config-v2.prev":kind.find("legacy")!=std::string::npos?"config.bin":"config-v2.bin";
    const bool missing=kind=="capture-no-source";
    if(!missing)write_record(source,make_config(1));
    const Bytes foreign{9,8,7};require(lfs_mkdir(&mounted_fs,"/unrelated")==0&&bool(CheckedStorage::WriteFile("/unrelated/keep",foreign.data(),foreign.size(),Kind::Config)),"broader namespace");
    if(kind=="capture-exact"||kind=="capture-mismatch")write_record("/ultimate-migration.src",make_config(kind=="capture-exact"?1:2));
    if(kind=="load-bad-crc"||kind=="capture-bad-crc") {auto bytes=config_record(make_config(1));bytes.back()^=1;require(bool(CheckedStorage::WriteFile(source,bytes.data(),bytes.size(),Kind::Config)),"bad crc source");}
    Config caller=make_config(3);const auto original_caller=config_record(caller);uint8_t identity[32];std::memset(identity,0xa5,sizeof(identity));
    trace.clear();event_index=0;target_event=target;target_fault=fault;fail_readback=false;publication_lost=false;CheckedStorage::SetFaultHook(observe_config);
    const bool capture=kind.rfind("capture",0)==0;unsigned result=capture?unsigned(p.CaptureLegacySource(identity)):unsigned(p.LoadConfigChecked(caller));
    CheckedStorage::SetFaultHook(nullptr);const auto captured=trace;require(mounted_fs.mlist==nullptr,"all actual file handles retire on each fault");
    if(!capture&&result!=unsigned(Persistence::LoadResult::Loaded)) {require(config_record(caller)==original_caller,"failed Load never publishes candidate to caller");require(p.ConfigGeneration(caller)==0,"failed Load never publishes new generation");}
    if(capture)require(config_record(caller)==original_caller,"Capture does not mutate unrelated caller");
    if(target==SIZE_MAX) {if(!capture)require(result==unsigned(kind=="load-bad-crc"?Persistence::LoadResult::Rejected:Persistence::LoadResult::Loaded),"actual selected Load success/rejection");else require(bool(result)==(kind!="capture-mismatch"&&kind!="capture-bad-crc"&&kind!="capture-no-source"),"actual Capture publication/exact-match/refusal");}

    auto body=config_record(caller);auto raw=digest(physical.data(),physical.size());
    std::printf("%s result=%u fence=%u generation=%u caller=%s identity=",label.c_str(),result,p.IsMutationFenced(),p.ConfigGeneration(caller),digest(body.data(),body.size()).c_str());
    for(uint8_t b:identity)std::printf("%02x",b);std::printf(" nor=%s trace=",raw.c_str());for(const auto&e:captured)std::printf("%s;",e.c_str());std::puts("");
    // A fresh checked operation must not borrow stale phase metadata/handles.
    Persistence next;require(next.SetValidator(config_validator),"next validator");Config checked=make_config(2);(void)next.LoadConfigChecked(checked);require(mounted_fs.mlist==nullptr,"next checked load has no stale handle");
    lfs_info info{};require(lfs_stat(&mounted_fs,"/unrelated/keep",&info)==0&&info.size==foreign.size(),"foreign directory untouched");
    require(lfs_unmount(&mounted_fs)==0,"release actual NOR");return captured;
}
}
int main() {try {unsigned faults=0;for(const auto &kind:{"load-current","load-prior","load-legacy","capture-current","capture-prior","capture-legacy","capture-exact","capture-mismatch","load-bad-crc","capture-bad-crc","capture-no-source"}) {
    auto events=run_load_capture(std::string(kind)+"-success",kind,SIZE_MAX,CheckedStorage::Fault::None);
    for(size_t i=0;i<events.size();++i)for(auto f:{CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement}) {run_load_capture(std::string(kind)+"-fault-"+std::to_string(i)+"-"+std::to_string(unsigned(f)),kind,i,f);++faults;}
}std::printf("PASS actual Load/Capture NOR differential faults=%u target=NOT_MEASURED\n",faults);return 0;}catch(const std::exception&e){std::fprintf(stderr,"FAIL Load/Capture: %s\n",e.what());return 1;}}
