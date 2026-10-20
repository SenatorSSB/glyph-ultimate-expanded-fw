// Reuse the immutable deployed storage harness and actual NOR/LittleFS mount.
#define main native_unused_legacy_store_main
#include "../profile_store_strict_host/strict_harness.cpp"
#undef main
#include "modes/Ultimate.hpp"
#include "modes/UltimateNativeEvaluator.hpp"
#include "core/RuntimeProfileDigest.hpp"
#include "core/RuntimeIdentity.hpp"
namespace {
class NativeBackend : public CommunicationBackend {
 public:
    NativeBackend(InputState &i):CommunicationBackend(i,nullptr,0){}
    CommunicationBackendId BackendId() override { return COMMS_BACKEND_XINPUT; }
    void SendReport() override { UpdateOutputs(); }
};
Bytes incoming_wire;
ultimate_native::PayloadLease incoming_lease;
UltimateProfile incoming;
const UltimateProfile &load_native(const std::string &path) {
    incoming_lease.Release();std::ifstream f(path,std::ios::binary);incoming_wire=Bytes((std::istreambuf_iterator<char>(f)),{});
    require(ultimate_native::DecodeProfile(incoming_wire.data(),incoming_wire.size(),incoming,incoming_lease)&&ultimate_native::ValidProfile(incoming),"native standalone admission");return incoming;
}
void neutral_unavailable(GameModeConfig &mc,const UltimateProfile *p,const ultimate_native::PreparedView *view) {
    Ultimate mode;mode.SetConfig(mc,p,view);require(mode.ActiveEngine()==Ultimate::Engine::NativeUnavailable,"native unavailable engine");
    InputState in{};in.buttons=~uint64_t{0};in.nunchuk_connected=true;in.nunchuk_c=true;in.nunchuk_x=25;in.nunchuk_y=61;OutputState out{};out.buttons=~uint32_t{0};
    mode.UpdateOutputs(in,out,COMMS_BACKEND_XINPUT);require(out.buttons==0&&out.leftStickX==128&&out.leftStickY==128&&out.rightStickX==128&&out.rightStickY==128&&out.triggerLAnalog==0&&out.triggerRAnalog==0,"fully neutral unavailable bypasses Nunchuk/legacy/reserved bits");
}
}
int main(int argc,char **argv) {
 try {
    require(argc==4,"native_store PROFILE_DIRECTORY LEGACY_CONFIG CONTEXT");std::ifstream f(argv[2],std::ios::binary);Bytes raw((std::istreambuf_iterator<char>(f)),{});auto decoder=pb_istream_from_buffer(raw.data(),raw.size());require(pb_decode(&decoder,Config_fields,&legacy),"legacy source decode");
    mounted_cfg.read=ram_read;mounted_cfg.prog=ram_prog;mounted_cfg.erase=ram_erase;mounted_cfg.sync=ram_sync;mounted_cfg.read_size=256;mounted_cfg.prog_size=256;mounted_cfg.block_size=4096;mounted_cfg.block_count=128;mounted_cfg.block_cycles=16;mounted_cfg.cache_size=256;mounted_cfg.lookahead_size=256;
    require(lfs_format(&mounted_fs,&mounted_cfg)==0&&lfs_mount(&mounted_fs,&mounted_cfg)==0,"actual pinned LittleFS mount");
    ProfileStore store;require(store.Begin(),"normal production bootstrap");uint64_t token=1;
    for(unsigned i=1;i<=20;++i) {const auto &p=load_native(std::string(argv[1])+"/"+std::to_string(i)+".pb");auto result=store.Create(p,("native"+std::to_string(i)).c_str(),i,identity(token++));require(result.status==Status::Ok&&result.id==i&&result.revision==1,"twenty independent complete native creates");incoming_lease.Release();}
    require(store.Count()==20,"twenty directory records");const size_t store_bytes=sizeof(store);
    auto capacity=store.Capacity();require(capacity.admissible_profiles>=20&&capacity.free_bytes>=capacity.reserve_bytes+capacity.staging_bytes,"full reserve/staging and native representative admission");
    ProfileStore::Status status;const auto *active=store.Activate(1,&status);require(active&&status==Status::Ok&&store.ActiveNativeView()&&store.ActiveRevision()==1,"native boot publication");
    const auto *view=store.ActiveNativeView();const uint32_t generation=view->generation;uint8_t original[32],after[32];require(runtime_identity::PayloadDigest(*active,original),"actual active wrapper digest");
    static Config observed_config;observed_config=Config_init_default;
    observed_config.ultimate_profile_store_format=1;observed_config.ultimate_profile_store_incarnation=store.Incarnation();
    observed_config.game_mode_configs_count=1;auto &mc=observed_config.game_mode_configs[0];
    std::ifstream context_file(argv[3],std::ios::binary);Bytes context_bytes((std::istreambuf_iterator<char>(context_file)),{});
    auto context_decoder=pb_istream_from_buffer(context_bytes.data(),context_bytes.size());require(pb_decode(&context_decoder,GameModeConfig_fields,&mc),"complete profile exact preprocessing row");
    mc.mode_id=MODE_ULTIMATE;mc.ultimate_profile_id=1;mc.ultimate_profile_engine=1;
    Ultimate mode;mode.SetConfig(mc,active,view);require(mode.ActiveEngine()==Ultimate::Engine::NativeAbi1,"actual active native mode");
    InputState observed_inputs{};NativeBackend backend(observed_inputs);backend.SetGameMode(&mode);
    auto observed=runtime_identity::Observe(&backend,observed_config,store,mode);
    require(observed.status==runtime_identity::Status::Persisted&&observed.schema==5&&observed.id==1&&observed.revision==1&&std::memcmp(observed.digest,original,32)==0,"native actual primary/store/owner/view/context/generation identity");
    auto forged=*view;Ultimate invalid_owner;invalid_owner.SetConfig(mc,active,&forged);
    require(invalid_owner.ActiveEngine()==Ultimate::Engine::NativeUnavailable,"copied view cannot borrow published owner identity");
    auto &mutable_view=const_cast<ultimate_native::PreparedView &>(*view);++mutable_view.generation;
    observed=runtime_identity::Observe(&backend,observed_config,store,mode);
    require(observed.status==runtime_identity::Status::SnapshotUnavailable,"changed active generation invalidates actual snapshot");
    backend.SendReport();require(backend.GetOutputs().buttons==0&&backend.GetOutputs().leftStickX==128,"changed generation produces neutral output");
    mutable_view.generation=generation;
    for(unsigned revision=2;revision<=3;++revision)for(unsigned i=1;i<=20;++i) {const auto &p=load_native(std::string(argv[1])+"/"+std::to_string((i%20)+1)+".pb");auto result=store.Update(i,p,revision-1,identity(token++));require(result.status==Status::Ok&&result.revision==revision,"native revision retention transaction");incoming_lease.Release();}
    require(store.ActiveRevision()==1&&store.ActiveNativeView()==view&&view->generation==generation&&runtime_identity::PayloadDigest(*active,after)&&!std::memcmp(original,after,32),"inactive updates preserve exact active revision/body/view/generation/digest");
    observed=runtime_identity::Observe(&backend,observed_config,store,mode);
    require(observed.status==runtime_identity::Status::Persisted&&observed.revision==1&&std::memcmp(observed.digest,original,32)==0,"native observer reports actual latched r1 after stored r3 update");
    uint8_t response[72];runtime_identity::EncodeResponse(42,observed,response);
    require(response[16]==0&&runtime_identity::ReadLE(response+36,4)==5&&!std::memcmp(response+40,original,32),"native identity unchanged72byte wire");
    require(CheckedStorage::Stat(record_path(1,1).c_str(),nullptr,Kind::Record).outcome==Outcome::Ok,"latched record retained through collection");
    require(store.Update(1,legacy.ultimate_profiles[0],3,identity(token++)).status==Status::Invalid,"cross-kind native to legacy update rejects");
    auto legacy_id=store.Create(legacy.ultimate_profiles[0],"legacy",21,identity(token++));require(legacy_id.status==Status::Ok,"legacy create unchanged");
    require(store.Update(legacy_id.id,load_native(std::string(argv[1])+"/1.pb"),1,identity(token++)).status==Status::Invalid,"cross-kind legacy to native update rejects");incoming_lease.Release();
    auto duplicated=store.Duplicate(2,3,"native duplicate",22,identity(token++));require(duplicated.status==Status::Ok,"native duplicate preserves borrowed record across nested admission reads");
    UltimateProfile readback{};require(store.Read(duplicated.id,readback)==Status::Ok&&readback.schema_version==5,"duplicate native kind");
    require(store.Health(1)==ProfileStore::RecordHealth::Healthy&&store.ActiveRevision()==1&&sizeof(store)==store_bytes,"health doesn't mutate active; inactive count doesn't change state allocation");
    Config persisted=Config_init_default;persisted.ultimate_profile_store_format=1;persisted.ultimate_profile_store_incarnation=store.Incarnation();persisted.game_mode_configs_count=1;persisted.game_mode_configs[0]=mc;
    size_t n=0;require(pb_get_encoded_size(&n,Config_fields,&persisted),"reference Config encoded size");Bytes config_wire(n);auto encoder=pb_ostream_from_buffer(config_wire.data(),config_wire.size());require(pb_encode(&encoder,Config_fields,&persisted),"expected engine persists in Config");Config restored=Config_init_default;decoder=pb_istream_from_buffer(config_wire.data(),config_wire.size());require(pb_decode(&decoder,Config_fields,&restored)&&restored.game_mode_configs[0].ultimate_profile_engine==1,"engine discriminator Config decode");
    const auto incarnation=store.Incarnation();require(lfs_unmount(&mounted_fs)==0&&lfs_mount(&mounted_fs,&mounted_cfg)==0&&store.Begin(incarnation,2)&&store.Count()==22,"actual reboot retained twenty complete profiles, duplicate and legacy");
    active=store.Activate(1,&status);require(active&&store.ActiveRevision()==3&&store.ActiveNativeView(),"reference reboot activates latest selected native revision");mode.SetConfig(mc,active,store.ActiveNativeView());require(mode.ActiveEngine()==Ultimate::Engine::NativeAbi1,"native reinitialization context valid");
    active=store.Activate(2,&status);require(active&&store.ActiveId()==2&&store.ActiveRevision()==3,"second native selection after reboot");
    // Real integrity corruption falls back only to a same-kind previous record.
    auto path=record_path(1,3);size_t size=0;require(CheckedStorage::Stat(path.c_str(),&size,Kind::Record).outcome==Outcome::Ok,"current native record stat");Bytes corrupted(size);{CheckedStorage::File file;require(bool(CheckedStorage::Open(file,path.c_str(),false,Kind::Record)),"record open");auto result=CheckedStorage::Read(file,corrupted.data(),size);require(bool(result)&&result.bytes==size&&bool(CheckedStorage::Close(file)),"record exact read");}
    corrupted.back()^=1;require(bool(CheckedStorage::WriteFile(path.c_str(),corrupted.data(),corrupted.size(),Kind::Record)),"host corrupt current record");
    active=store.Activate(1,&status);require(active&&status==Status::RecoveredPrevious&&store.ActiveRevision()==2&&active->schema_version==5,"corrupt native current recovers same-kind previous");
    GameModeConfig wrong=mc;wrong.button_remapping_count=1;wrong.button_remapping[0]={BTN_RF1,BTN_LF1};neutral_unavailable(wrong,active,store.ActiveNativeView());
    wrong=mc;wrong.ultimate_profile_engine=0;neutral_unavailable(wrong,active,store.ActiveNativeView());
    require(store.Activate(999,&status)==nullptr,"missing native reference");neutral_unavailable(mc,nullptr,nullptr);
    require(store.BeginRecovery(incarnation,2),"read-only recovery inspection");require(store.Activate(2,&status)==nullptr,"read-only native cannot publish");neutral_unavailable(mc,nullptr,nullptr);
    capacity=store.Capacity();std::printf("PASS native actual LittleFS20complete profiles/revisions/staging/reserve/reboot/read/health/duplicate/cross-kind/context/unavailable; sizeof_store=%zu total=%llu used=%llu free=%llu protected=%llu staging=%llu\n",store_bytes,(unsigned long long)capacity.total_bytes,(unsigned long long)capacity.used_bytes,(unsigned long long)capacity.free_bytes,(unsigned long long)capacity.protected_bytes,(unsigned long long)capacity.staging_bytes);
    require(lfs_unmount(&mounted_fs)==0,"native test unmount");return 0;
 } catch(const std::exception &e) {std::fprintf(stderr,"FAIL native store: %s\n",e.what());return 1;}
}
