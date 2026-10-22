// Actual Configurator/COBS/Nanopb/ProfileStore; named functional Persistence
// boundary is inherited unchanged from the frozen timeout host fixture.
#define main preserved_timeout_fixture_main
#include "../profile_store_timeout_host/timeout_harness.cpp"
#undef main
namespace {
std::string set_digest(const std::vector<uint8_t> &b) {uint8_t d[32];Sha256 h;h.Update(b.data(),b.size());h.Final(d);char out[65];for(unsigned i=0;i<32;++i)std::snprintf(out+i*2,3,"%02x",d[i]);return out;}
}
int main(int argc,char **argv) {
 try {
    require(argc==3,"legacy SET fixture and case");const auto scenario=std::stoul(argv[2]);require(scenario<17,"legacy SET case range");
    static Config live;seed(argv[1],&live);InputState inputs;DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,live,wire);
    Config incoming=live;incoming.rgb_brightness=61;incoming.profile_reference_token=987654321;
    incoming.profile_reference_result_id=999;incoming.profile_reference_result_mode_index=999;
    std::memset(incoming.profile_reference_digest,0x77,32);std::memset(incoming.ultimate_profile_migration_receipt,0x88,32);
    if(scenario==1)backend._recovery_service=true;
    if(scenario==2)persistence.fail_load=true;
    if(scenario==4)incoming.ultimate_profile_store_format=0;
    if(scenario==5)persistence.fail_validation=true;
    if(scenario==6||scenario==16){auto &m=incoming.game_mode_configs[0];m.mode_id=MODE_ULTIMATE;m.ultimate_profile_id=1;m.ultimate_profile_config=0;m.ultimate_profile_engine=1;}
    if(scenario==7)persistence.fail_save=true;
    if(scenario==8)wire.tx_budget=0;
    if(scenario==9){backend._recovery_service=true;wire.tx_budget=0;}
    if(scenario==10)incoming.ultimate_profiles_count=0;
    if(scenario==11){live.ultimate_profile_store_format=0;std::ifstream f(argv[1],std::ios::binary);std::vector<uint8_t> b((std::istreambuf_iterator<char>(f)),{});incoming=Config_init_default;auto pb=pb_istream_from_buffer(b.data(),b.size());require(pb_decode(&pb,Config_fields,&incoming)&&!pb.bytes_left,"valid legacy incoming fixture");incoming.rgb_brightness=61;}
    if(scenario==12)incoming.default_usb_backend_config=255;
    if(scenario==13)backend._reference_unknown=true;
    if(scenario==14){auto &m=incoming.game_mode_configs[0];m.mode_id=MODE_ULTIMATE;m.ultimate_profile_id=9999;m.ultimate_profile_config=0;m.ultimate_profile_engine=1;}
    if(scenario==15){incoming.ultimate_profiles_count=1;auto &p=incoming.ultimate_profiles[0];p=UltimateProfile_init_default;p.schema_version=5;p.native_payload.funcs.encode=[](pb_ostream_t *out,const pb_field_t *field,void *const *){return pb_encode_tag_for_field(out,field)&&pb_encode_string(out,nullptr,0);};}
    if(scenario==16)wire.tx_budget=0;
    auto payload=config_bytes(incoming);if(scenario==3)payload={0xff};
    const auto live_before=config_bytes(live),durable_before=config_bytes(persistence.durable);const auto old_token=persistence.durable.profile_reference_token;
    const auto saves=persistence.save_calls,loads=persistence.load_calls;const auto before_files=storage.files;
    DuplexStream command;packetio::COBSPrint packet(command);packet.write(uint8_t(CMD_SET_CONFIG));packet.write(payload.data(),payload.size());require(packet.end(),"legacy SET COBS request");wire.append(command.tx);
    require(backend.ReadByte()==CMD_SET_CONFIG,"actual command decoder");const bool result=backend.HandleSetConfig();
    const bool saved=persistence.save_calls>saves&&!persistence.fail_save;
    if(!saved){require(config_bytes(live)==live_before,"failed/refused SET never publishes live Config");require(config_bytes(persistence.durable)==durable_before,"failed/refused SET never publishes durable Config");}
    if(saved){require(config_bytes(live)==config_bytes(persistence.durable),"success publishes SAME candidate after save");require(live.profile_reference_token==(scenario==11?0:old_token),"firmware-owned receipt preserved rather than forged");}
    require(storage.files==before_files,"legacy SET does not mutate ProfileStore");
    if(scenario==8)require(saved&&result&&wire.tx.empty(),"success returns true even failed success packet");
    if(scenario==9)require(!result&&!saved,"guard preserves false WritePacket return");
    if(scenario==3||scenario==4||scenario==5||scenario==7||scenario==12||scenario==15||scenario==16)require(!result&&!saved,"legacy false error return preserved");
    if(scenario==1||scenario==2||scenario==6||scenario==13)require(result&&!saved,"legacy guard/reference error returns WritePacket result");
    if(scenario==0||scenario==10||scenario==11||scenario==14)require(result&&saved,"valid legacy SET succeeds");
    std::printf("case=%lu result=%u saves=%u loads=%u live=%s durable=%s generation=%u tx=",scenario,result,persistence.save_calls-saves,persistence.load_calls-loads,set_digest(config_bytes(live)).c_str(),set_digest(config_bytes(persistence.durable)).c_str(),persistence.ConfigGeneration(live));for(auto b:wire.tx)std::printf("%02x",b);std::puts("");
    std::puts("PASS actual legacy SET handler/COBS/validation/receipt/return/publication at named functional Persistence boundary; actual NOR Save differential separate; no device");return 0;
 }catch(const std::exception &e){std::fprintf(stderr,"FAIL legacy SET phases: %s\n",e.what());return 1;}
}
