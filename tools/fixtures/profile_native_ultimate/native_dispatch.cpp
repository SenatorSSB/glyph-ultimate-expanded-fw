#define main preserved_timeout_fixture_main
#include "../profile_store_timeout_host/timeout_harness.cpp"
#undef main
#include "modes/UltimateNativeProfile.hpp"
namespace {
std::vector<uint8_t> loaded;
ultimate_native::PayloadLease lease;
UltimateProfile &native_file(const char *path) {
    lease.Release();std::ifstream f(path,std::ios::binary);loaded.assign(std::istreambuf_iterator<char>(f),{});
    static UltimateProfile p;require(ultimate_native::DecodeProfile(loaded.data(),loaded.size(),p,lease)&&ultimate_native::ValidProfile(p),"native transport fixture valid");return p;
}
std::vector<uint8_t> response_profile(const DuplexStream &wire) {
    auto framed=wire.tx;while(!framed.empty()&&framed.front()==0)framed.erase(framed.begin());
    auto raw=decode(framed);require(raw[0]==CMD_PROFILE_STORE,"native READ response command");
    auto stream=pb_istream_from_buffer(raw.data()+1,raw.size()-1);
    while(stream.bytes_left) {pb_wire_type_t type;uint32_t tag;bool eof;require(pb_decode_tag(&stream,&type,&tag,&eof),"response profile presence walk");
        if(tag==ProfileStoreResponse_profile_tag){require(type==PB_WT_STRING,"profile response wire");pb_istream_t field;require(pb_make_string_substream(&stream,&field),"response profile field");std::vector<uint8_t> bytes(field.bytes_left);require(pb_read(&field,bytes.data(),bytes.size()),"response profile exact bytes");return bytes;}
        require(pb_skip_field(&stream,type),"response field skip");
    }throw std::runtime_error("native READ body missing");
}
}
int main(int argc,char **argv) {
 try {
    require(argc==4,"native_dispatch LEGACY NATIVE MAXIMUM");static Config config;seed(argv[1],&config);
    InputState inputs;DuplexStream wire;ConfiguratorBackend backend(inputs,nullptr,0,config,wire);
    uint64_t token=profile_store.LastTransactionToken()+100;
    ProfileStoreRequest request=ProfileStoreRequest_init_default;request.protocol_version=2;request.operation=PROFILE_STORE_CREATE;
    request.profile=native_file(argv[2]);request.has_profile=true;request.request_token=token++;
    request.expected_store_incarnation=profile_store.Incarnation();request.expected_store_generation=profile_store.Generation();std::strcpy(request.name,"native transport");
    ProfileStoreTransactionIdentity expected;require(ProfileStoreRequestIdentity(request,expected),"independent native request identity");
    auto created=send(backend,wire,request);require(created.status==PROFILE_STORE_OK&&created.profile_id,"native CREATE through actual COBS/RX/decoder/identity/transaction");
    require(profile_store.QueryTransaction(expected).status==ProfileStore::Status::Ok,"persisted native request identity matches full synchronous payload");
    lease.Release();const auto id=created.profile_id;
    request=ProfileStoreRequest_init_default;request.protocol_version=2;request.operation=PROFILE_STORE_READ;request.profile_id=id;
    for(unsigned i=0;i<100;++i){request.request_token=token++;require(send(backend,wire,request).status==PROFILE_STORE_OK,"native repeated READ dispatch");auto profile=response_profile(wire);std::ifstream original(argv[2],std::ios::binary);std::vector<uint8_t> expected_bytes((std::istreambuf_iterator<char>(original)),{});require(profile==expected_bytes,"READ independent record lease survives shared response frame reuse");}
    request=ProfileStoreRequest_init_default;request.protocol_version=2;request.operation=PROFILE_STORE_SET_MODE_REFERENCE;request.profile_id=id;request.mode_config_index=0;
    request.expected_store_incarnation=profile_store.Incarnation();request.expected_store_generation=profile_store.Generation();request.expected_config_generation=persistence.ConfigGeneration(config);request.request_token=token++;
    require(send(backend,wire,request).status==PROFILE_STORE_OK&&persistence.durable.game_mode_configs[0].ultimate_profile_id==id&&persistence.durable.game_mode_configs[0].ultimate_profile_engine==1,"checked native reference commits expected engine with ID");
    // Maximum profile is precisely3341 bytes; existing native Create/Read
    // envelope/COBS/RX/write-record bounds are exercised without buffer growth.
    request=ProfileStoreRequest_init_default;request.protocol_version=2;request.operation=PROFILE_STORE_CREATE;request.profile=native_file(argv[3]);request.has_profile=true;
    request.expected_store_incarnation=profile_store.Incarnation();request.expected_store_generation=profile_store.Generation();request.request_token=token++;std::strcpy(request.name,"maximum native");
    size_t profile_bytes=0;require(pb_get_encoded_size(&profile_bytes,UltimateProfile_fields,&request.profile)&&profile_bytes==3341,"exact maximum profile wrapper");
    auto maximum=send(backend,wire,request);require(maximum.status==PROFILE_STORE_OK,"maximum native CREATE exact existing admission");lease.Release();
    request=ProfileStoreRequest_init_default;request.protocol_version=2;request.operation=PROFILE_STORE_READ;request.profile_id=maximum.profile_id;request.request_token=token++;
    require(send(backend,wire,request).status==PROFILE_STORE_OK,"maximum native READ");auto maximum_profile=response_profile(wire);require(maximum_profile.size()==3341,"maximum native response preserved full callback bytes");
    // Invalid legacy+tag8 must never reach a transaction, including empty tag8.
    const auto before=storage.files;const auto generation=profile_store.Generation();
    std::vector<uint8_t> mixed={8,1,66,0};
    request=ProfileStoreRequest_init_default;request.protocol_version=2;request.operation=PROFILE_STORE_CREATE;request.request_token=token++;
    size_t encoded=0;require(pb_get_encoded_size(&encoded,ProfileStoreRequest_fields,&request),"malformed request prefix size");std::vector<uint8_t> raw(encoded);auto encoder=pb_ostream_from_buffer(raw.data(),raw.size());require(pb_encode(&encoder,ProfileStoreRequest_fields,&request),"malformed prefix encode");
    const uint32_t key=ProfileStoreRequest_profile_tag*8+2;require(key<128,"bounded test request profile tag");raw.push_back(key);raw.push_back(mixed.size());raw.insert(raw.end(),mixed.begin(),mixed.end());
    wire.clear();packetio::COBSPrint framed(wire);framed.write(uint8_t(CMD_PROFILE_STORE));framed.write(raw.data(),raw.size());require(framed.end(),"mixed frame end");auto packet=wire.tx;wire.clear();wire.append(packet);backend.SendReport();require(decode(wire.tx)[0]==CMD_ERROR&&storage.files==before&&profile_store.Generation()==generation,"mixed callback presence rejects before mutation");
    std::puts("PASS native actual Configurator COBS CREATE/request identity/100READ leases/checked reference engine/MAX3341 wrapper+3373record/response/mixed refusal; no device");return 0;
 }catch(const std::exception &e){std::fprintf(stderr,"FAIL native dispatch: %s\n",e.what());return 1;}
}
