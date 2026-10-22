#include "core/ProfileSelection.hpp"
// The directory/Read/Activate/NOR/LittleFS are real production implementations.
// A checked Config publisher double isolates store immutability here; the
// separate selection_persistence fixture exercises actual Persistence.cpp.
struct NativeSelectorPersistence {
 enum class LoadResult {Loaded};enum class SaveResult {Saved,Conflict};
 Config durable{};uint32_t generation=1;
 bool IsAvailable()const{return true;}bool IsMutationFenced()const{return false;}
 LoadResult LoadConfigChecked(Config &into){into=durable;return LoadResult::Loaded;}
 uint32_t ConfigGeneration(const Config &)const{return generation;}
 bool ValidateConfig(const Config &c,ConfigValidationError &e){return validate_config_semantics(c,e);}
 SaveResult SaveConfigIfGenerationMatches(Config &c,uint32_t expected){if(expected!=generation)return SaveResult::Conflict;durable=c;++generation;return SaveResult::Saved;}
};
void test_actual_store_selector(ProfileStore &store,const GameModeConfig &context) {
 NativeSelectorPersistence storage;auto &config=storage.durable;
 config.ultimate_profile_store_format=1;config.ultimate_profile_store_incarnation=store.Incarnation();
 config.game_mode_configs_count=1;config.game_mode_configs[0]=context;
 config.communication_backend_configs_count=1;config.communication_backend_configs[0].backend_id=COMMS_BACKEND_XINPUT;
 config.communication_backend_configs[0].default_mode_config=1;config.default_usb_backend_config=1;config.default_backend_config=1;
 profile_selection::Target targets[94]{};
 require(profile_selection::BuildTargets(config,store,COMMS_BACKEND_XINPUT,targets,94)==21,"actual native directory21choices with duplicate+legacy hidden");
 const uint32_t generation=store.Generation();const size_t count=store.Count();
 std::vector<ProfileStore::Entry> metadata;for(size_t i=0;i<count;++i)metadata.push_back(*store.EntryAt(i));
 static Config candidate;
 for(uint32_t id:{1u,2u,1u}) {
  size_t mode=99,backend=99;
  require(profile_selection::Persist(storage,store,candidate,COMMS_BACKEND_XINPUT,id,0,mode,backend)==ModeDestinationResult::Saved,"actual store native selector A B A");
  require(candidate.game_mode_configs[mode].ultimate_profile_id==id&&store.Generation()==generation&&store.Count()==count,"select reference only no store transaction");
  ProfileStore::Status status;const auto *profile=store.Activate(candidate.game_mode_configs[mode].ultimate_profile_id,&status);
  require(profile&&status==ProfileStore::Status::Ok&&store.ActiveId()==id,"actual initialization activates selected record");
  Ultimate runtime;runtime.SetConfig(candidate.game_mode_configs[mode],profile,store.ActiveNativeView());
  require(runtime.ActiveEngine()==Ultimate::Engine::NativeAbi1,"selected exact context activates native evaluator");
 }
 for(size_t i=0;i<count;++i)require(!std::memcmp(&metadata[i],store.EntryAt(i),sizeof(ProfileStore::Entry)),"all directory/revisions/names/ranks untouched");
 std::puts("PASS selector actual NOR/LittleFS metadata21 native choices and A->B->A validated reference/boot activation; no store mutation");
}
