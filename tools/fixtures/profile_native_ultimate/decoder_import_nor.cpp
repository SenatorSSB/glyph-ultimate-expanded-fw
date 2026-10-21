// Source-faithful old/current Persistence + Import on actual pinned NOR/LittleFS.
#define GLYPH_PERSISTENCE_NOR_NO_MAIN
#include "persistence_nor_lifetimes.cpp"
#include <map>
#include <set>
#include <type_traits>
bool GlyphPersistenceSlotClean();
bool GlyphPersistenceReadPhaseClean();
namespace {
void varint(Bytes &b,uint64_t n){do{uint8_t v=n&127;n>>=7;b.push_back(v|(n?128:0));}while(n);}
uint64_t take_varint(const Bytes &b,size_t &p){uint64_t v=0;for(unsigned k=0;k<10;++k){require(p<b.size(),"test wire bound");const auto x=b[p++];v|=uint64_t(x&127)<<(7*k);if(!(x&128))return v;}require(false,"test varint bound");return 0;}
Bytes deep_append(const Bytes &wire,const std::vector<unsigned>&path,size_t depth,const Bytes &tail){
    if(depth==path.size()){Bytes b=wire;b.insert(b.end(),tail.begin(),tail.end());return b;}
    Bytes out;size_t p=0;bool changed=false;
    while(p<wire.size()){
        const auto start=p;const auto key=take_varint(wire,p);const unsigned kind=key&7,tag=key>>3;
        if(kind==2){const auto n=take_varint(wire,p);require(n<=wire.size()-p,"test nested bound");const auto stop=p+n;
            if(!changed&&tag==path[depth]){Bytes child(wire.begin()+p,wire.begin()+stop);child=deep_append(child,path,depth+1,tail);varint(out,key);varint(out,child.size());out.insert(out.end(),child.begin(),child.end());changed=true;}
            else out.insert(out.end(),wire.begin()+start,wire.begin()+stop);p=stop;
        }else{if(kind==0)(void)take_varint(wire,p);else if(kind==1)p+=8;else if(kind==5)p+=4;else require(false,"test wire kind");require(p<=wire.size(),"test scalar bound");out.insert(out.end(),wire.begin()+start,wire.begin()+p);}
    }
    require(changed,"actual generated D4 path present");return out;
}
Bytes wrap_payload(const Bytes &payload){Persistence::ConfigHeader h{};h.config_size=payload.size();CRC32 crc;crc.update(payload.data(),payload.size());h.config_crc=crc.finalize();Bytes out(sizeof(h));std::memcpy(out.data(),&h,sizeof(h));out.insert(out.end(),payload.begin(),payload.end());return out;}
void foreign(){require(lfs_mkdir(&mounted_fs,"/unrelated")==0,"foreign directory");const uint8_t b[]{4,8,15};require(bool(CheckedStorage::WriteFile("/unrelated/keep",b,sizeof(b),Kind::Record)),"foreign file");}
void clean(){require(mounted_fs.mlist==nullptr,"all actual native handles retire");require(GlyphPersistenceSlotClean(),"one shared File slot all zero");require(GlyphPersistenceReadPhaseClean(),"new read phase pointers/stream all clear");}
std::vector<size_t> selected_cuts(const std::vector<std::string>&events){std::set<size_t> chosen;if(!events.empty()){chosen.insert(0);chosen.insert(events.size()/2);chosen.insert(events.size()-1);}std::map<std::string,std::vector<size_t>> groups;for(size_t i=0;i<events.size();++i)groups[events[i]].push_back(i);for(const auto &g:groups){chosen.insert(g.second.front());chosen.insert(g.second[g.second.size()/2]);chosen.insert(g.second.back());}return {chosen.begin(),chosen.end()};}
std::vector<std::string> load_deep(unsigned variant,size_t cut,CheckedStorage::Fault fault){
    format_mount();Persistence p;require(p.SetValidator(config_validator),"actual validation callback");Config source=legacy;source.ultimate_profile_store_format=0;source.ultimate_profile_root_format=0;source.ultimate_profile_store_incarnation=0;
    if(variant==8||variant==9){auto &condition=source.ultimate_profiles[0].roles[0].condition;condition.all_tokens_count=1;condition.all_tokens[0]=variant==8?255:96;condition.any_tokens_count=condition.none_tokens_count=0;}
    auto bytes=config_record(source);Bytes payload(bytes.begin()+sizeof(Persistence::ConfigHeader),bytes.end());
    if(variant>=1&&variant<=7){const size_t n=variant==1?0:variant==2?1:variant==3?31:variant==4?32:variant==5?33:variant==6?65:5;Bytes extra;varint(extra,(199u<<3)|2);varint(extra,n);extra.insert(extra.end(),n,0x45);if(variant==7)extra.pop_back();payload=deep_append(payload,{Config_ultimate_profiles_tag,UltimateProfile_tables_tag,UltimateProfileTable_coordinates_tag},0,extra);bytes=wrap_payload(payload);}
    require(bool(CheckedStorage::WriteFile("config-v2.bin",bytes.data(),bytes.size(),Kind::Config)),"D4 raw record");foreign();Config caller=make_config(3);const auto before=config_record(caller);
    trace.clear();event_index=0;target_event=cut;target_fault=fault;fail_readback=publication_lost=false;CheckedStorage::SetFaultHook(observe_config);const auto result=p.LoadConfigChecked(caller);CheckedStorage::SetFaultHook(nullptr);auto events=trace;clean();
    if(cut==SIZE_MAX)require(result==(variant>=7?Persistence::LoadResult::Rejected:Persistence::LoadResult::Loaded),"D4 admission/rejection");if(result!=Persistence::LoadResult::Loaded)require(config_record(caller)==before,"failed deep Load leaves caller untouched");
    const auto record=config_record(caller);std::printf("D4=%u cut=%zu/%u result=%u generation=%u caller=%s nor=%s trace=",variant,cut,unsigned(fault),unsigned(result),p.ConfigGeneration(caller),digest(record.data(),record.size()).c_str(),digest(physical.data(),physical.size()).c_str());for(const auto &e:events)std::printf("%s;",e.c_str());std::puts("");
    // A fresh call must not use stale shared File/stream metadata after any read failure.
    Persistence next;require(next.SetValidator(config_validator),"next validator");Config again=make_config(2);(void)next.LoadConfigChecked(again);clean();require(lfs_unmount(&mounted_fs)==0,"D4 unmount");return events;
}
std::vector<std::string> save_deep(unsigned variant,size_t cut,CheckedStorage::Fault fault) {
    format_mount();Persistence p;require(p.SetValidator(config_validator),"deep Save validator");Config source=legacy;
    if(variant==1){source=Config_init_default;source.communication_backend_configs_count=1;source.communication_backend_configs[0].backend_id=COMMS_BACKEND_CONFIGURATOR;source.default_usb_backend_config=1;source.ultimate_profiles_count=1;auto &profile=source.ultimate_profiles[0];profile.schema_version=1;profile.tables_count=28;for(unsigned t=0;t<28;++t){auto &table=profile.tables[t];table.table_id=t;table.coordinates_count=9;for(auto &coords:table.coordinates){coords.x=coords.y=1;}}}
    source.ultimate_profile_store_format=0;source.ultimate_profile_root_format=2;source.ultimate_profile_store_incarnation=0;ConfigValidationError error;require(config_validator(source,error),"actual admitted noncompact D4 Save input");Config initial=source;initial.ultimate_profiles_count=0;write_record("config-v2.bin",initial);foreign();require(lfs_unmount(&mounted_fs)==0&&lfs_mount(&mounted_fs,&mounted_cfg)==0,"fresh lookahead after valid read-only seed");
    trace.clear();event_index=0;target_event=cut;target_fault=fault;fail_readback=publication_lost=false;CheckedStorage::SetFaultHook(observe_config);const bool saved=p.SaveConfig(source);CheckedStorage::SetFaultHook(nullptr);const auto events=trace;clean();if(cut==SIZE_MAX)require(saved,"actual D4 legacy Config Save");
    std::printf("SAVE-D4=%u cut=%zu/%u saved=%u fence=%u generation=%u files=%s nor=%s trace=",variant,cut,unsigned(fault),saved,p.IsMutationFenced(),p.ConfigGeneration(source),canonical_files().c_str(),digest(physical.data(),physical.size()).c_str());for(const auto&e:events)std::printf("%s;",e.c_str());std::puts("");require(lfs_unmount(&mounted_fs)==0,"deep Save unmount");return events;
}
void actual_read_result(size_t count,CheckedStorage::Phase phase,CheckedStorage::Fault fault) {
    format_mount();const uint8_t bytes[]{1,2,3,4,5,6,7,8};require(bool(CheckedStorage::WriteFile("read-result.bin",bytes,sizeof(bytes),Kind::Config)),"read result seed");
    CheckedStorageFile file("read-result.bin","r");require(bool(file),"actual read constructor");uint8_t output[12]{};trace.clear();event_index=0;target_event=phase==CheckedStorage::Phase::Before?0:1;target_fault=fault;fail_readback=publication_lost=false;CheckedStorage::SetFaultHook(observe_config);
    const int n=file.read(output,count);const auto result=file.last_result();const auto position=file.position(),size=file.size();const bool failed=file.failed(),uncertain=file.uncertain();CheckedStorage::SetFaultHook(nullptr);
    const int following=file.read(output+10,1);const auto after=file.last_result();const auto next_position=file.position();const bool closed=file.close();require(mounted_fs.mlist==nullptr,"actual read explicit close releases once");
    std::printf("READRESULT count=%zu phase=%u fault=%u n=%d result=%u,%d,%zu,%u state=%zu,%zu,%u,%u next=%d,%u,%d,%zu,%u,%zu close=%u bytes=",count,unsigned(phase),unsigned(fault),n,unsigned(result.outcome),result.error,result.bytes,unsigned(result.operation),position,size,failed,uncertain,following,unsigned(after.outcome),after.error,after.bytes,unsigned(after.operation),next_position,closed);for(uint8_t b:output)std::printf("%02x",b);std::printf(" trace=");for(const auto &e:trace)std::printf("%s;",e.c_str());std::puts("");require(lfs_unmount(&mounted_fs)==0,"read result unmount");
}
std::vector<std::string> import_stream(size_t cut,CheckedStorage::Fault fault){
    format_mount();ProfileStore store;require(store.Begin(),"actual store bootstrap");Persistence p;require(p.SetValidator(config_validator),"import validator");Config source=legacy;source.ultimate_profile_store_format=0;source.ultimate_profile_root_format=0;source.ultimate_profile_store_incarnation=0;write_record("config.bin",source);write_record("/ultimate-migration.src",source);foreign();const uint8_t garbage=42;require(bool(CheckedStorage::WriteFile("/ultimate-00000100-00000001.tmp",&garbage,1,Kind::Record)),"recognized unprotected GC file");
    uint8_t captured[32];require(p.CaptureLegacySource(captured),"ExistingExact snapshot route");uint32_t mapping[2]={0,0};const auto original=config_record(source);
    trace.clear();event_index=0;target_event=cut;target_fault=fault;fail_readback=publication_lost=false;CheckedStorage::SetFaultHook(observe_config);
    // Record ALL kinds for Import: GC/record/root/control as well as actual streamed Config reads.
    CheckedStorage::SetFaultHook([](Kind,CheckedStorage::Operation op,CheckedStorage::Phase ph,const char *path){return observe_config(Kind::Config,op,ph,path);});
    const auto status=store.ImportLegacyStream(source,captured,[](void *context,size_t index,UltimateProfile &profile){return static_cast<Persistence*>(context)->ReadLegacyProfile(index,profile)==Persistence::LoadResult::Loaded;},&p,mapping,2);CheckedStorage::SetFaultHook(nullptr);auto events=trace;clean();require(config_record(source)==original,"Import immutable source");
    if(cut==SIZE_MAX){require(status==Status::Ok&&store.Count()==2&&mapping[0]&&mapping[1]&&mapping[0]!=mapping[1],"actual streamed complete migration");require(store.MigrationPending(),"pending compact publication retained");for(size_t i=0;i<2;++i)check_profile(store,mapping[i],source.ultimate_profiles[i]);}
    std::printf("IMPORT cut=%zu/%u status=%u generation=%u count=%zu flags=%u uncertain=%u mapping=%u,%u diag=%s nor=%s trace=",cut,unsigned(fault),unsigned(status),store.Generation(),store.Count(),store.HealthFlags(),store.IsTransactionUncertain(),mapping[0],mapping[1],store.LastDiagnostic(),digest(physical.data(),physical.size()).c_str());for(const auto &e:events)std::printf("%s;",e.c_str());std::puts("");
    if(status==Status::Ok){uint32_t replay[2]{};require(store.ImportLegacyStream(source,captured,[](void *context,size_t index,UltimateProfile &profile){return static_cast<Persistence*>(context)->ReadLegacyProfile(index,profile)==Persistence::LoadResult::Loaded;},&p,replay,2)==Status::MigrationFenced&&replay[0]==mapping[0]&&replay[1]==mapping[1],"pending same source replay/fence/mapping");clean();Config compact=source;require(store.PrepareCompact(compact)&&p.SaveConfig(compact),"actual compact Save after Import reader");clean();UltimateProfile streamed{};require(p.ReadLegacyProfile(1,streamed)==Persistence::LoadResult::Loaded,"Save then real legacy reader reuses slot");clean();require(p.SaveConfig(compact),"ReadLegacy then Save reuses slot/union");clean();require(store.CompleteMigration(compact)==Status::Ok,"same completed migration publication");}
    require(lfs_unmount(&mounted_fs)==0,"Import unmount");return events;
}
}
int main(int argc,char **argv){try{
    require(argc==2,"complete legacy fixture");std::ifstream file(argv[1],std::ios::binary);Bytes raw((std::istreambuf_iterator<char>(file)),{});auto stream=pb_istream_from_buffer(raw.data(),raw.size());require(pb_decode(&stream,Config_fields,&legacy)&&!stream.bytes_left&&legacy.ultimate_profiles_count==2,"complete legacy Config decode");ConfigValidationError error;require(config_validator(legacy,error),"production-admitted legacy data");
#ifdef GLYPH_TEST_DEFAULT_ENUM
    static_assert(sizeof(CommunicationBackendId)==4&&sizeof(GameModeId)==4,"actual default enum ABI");
#else
    static_assert(sizeof(CommunicationBackendId)==1&&sizeof(GameModeId)==1,"actual short enum ABI");
#endif
    for(size_t count:{0,1,3,9})for(auto phase:{CheckedStorage::Phase::Before,CheckedStorage::Phase::After})for(auto fault:{CheckedStorage::Fault::None,CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement})actual_read_result(count,phase,fault);
    unsigned loads=0,imports=0;for(unsigned v=0;v<10;++v){auto events=load_deep(v,SIZE_MAX,CheckedStorage::Fault::None);for(auto cut:selected_cuts(events))for(auto fault:{CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement}){load_deep(v,cut,fault);++loads;}}
    for(unsigned v=0;v<2;++v){const auto events=save_deep(v,SIZE_MAX,CheckedStorage::Fault::None);for(auto cut:selected_cuts(events))for(auto fault:{CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement})save_deep(v,cut,fault);}
    const auto events=import_stream(SIZE_MAX,CheckedStorage::Fault::None);for(auto cut:selected_cuts(events))for(auto fault:{CheckedStorage::Fault::Fail,CheckedStorage::Fault::LostAcknowledgement}){import_stream(cut,fault);++imports;}
    std::printf("PASS actual NOR deepD4=10 selectedLoadFaults=%u streamedImportFaults=%u enum=%zu target=NOT_MEASURED\n",loads,imports,sizeof(CommunicationBackendId));return 0;
}catch(const std::exception&e){CheckedStorage::SetFaultHook(nullptr);std::fprintf(stderr,"FAIL decoder/import actual NOR: %s\n",e.what());return 1;}}
