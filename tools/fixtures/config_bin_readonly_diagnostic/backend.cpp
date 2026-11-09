// Actual ConfiguratorBackend/PacketIO with synthetic NOR; no physical access.
#define main HistoricalPackageFixtureMain
#include "../glyph_package_v1/transaction/harness.cpp"
#undef main
#include "core/ConfigBinReadOnlyDiagnostic.hpp"

namespace {
void fresh(const test::Bytes &bytes) {
    using namespace test;
    shutdown();configure();std::fill(nor.begin(),nor.end(),0xff);
    need(lfs_format(&fs,&cfg)==0&&lfs_mount(&fs,&cfg)==0,"explicit synthetic seed");mounted=true;
    lfs_file_t file{};need(lfs_file_open(&fs,&file,"/config.bin",LFS_O_CREAT|LFS_O_WRONLY)==0,"seed fixed file");
    need(lfs_file_write(&fs,&file,bytes.data(),bytes.size())==int(bytes.size()),"seed fixed bytes");
    need(lfs_file_close(&fs,&file)==0,"seed close");shutdown();
    // The host mount seam supplies the same configuration before initial mount.
    fs.cfg=&cfg;mounted=true;need(config_bin_diagnostic::InstallReadOnlyMount(),"pre-mount denial");
    programs=erases=0;const auto before=nor;
    need(lfs_mount(&fs,&cfg)==0,"readonly initial mount");
    need(nor==before&&programs==0&&erases==0,"initial mount zero program erase");
}
test::Bytes query(uint64_t nonce=42) {
    test::Bytes bytes={'G','C','B','1',1,0,0,0};
    for(unsigned i=0;i<8;++i)bytes.push_back(uint8_t(nonce>>(i*8)));
    return bytes;
}
void append(VectorStream &wire,uint8_t command,const test::Bytes &bytes) {
    packetio::COBSPrint packet(wire);
    test::need(packet.write(command)==1&&packet.write(bytes.data(),bytes.size())==bytes.size()&&packet.end(),"COBS request");
    wire.input.insert(wire.input.end(),wire.output.begin(),wire.output.end());wire.output.clear();
}
void pump(ConfiguratorBackend &backend,VectorStream &wire) {
    for(size_t guard=0;wire.position<wire.input.size();++guard) {
        test::need(guard<wire.input.size()+8,"finite transport pump");backend.SendReport();
    }
}
void scenario(const char *name,const test::Bytes &body,bool recovery,bool available,unsigned request_count,bool malformed=false) {
    using namespace test;fresh(body);VectorStream wire;
    static Config config=Config_init_default;const Config saved=config;
    const auto before=nor;const auto generation=profile_store.Generation();const auto active=profile_store.ActiveId();
    InputState inputs{};ConfiguratorBackend backend(inputs,nullptr,0,config,wire);
    if(recovery)backend.SetRecoveryState(true,available);
    if(malformed) { auto bad=query();bad[0]='X';append(wire,config_bin_diagnostic::kCommand,bad); }
    for(unsigned i=0;i<request_count;++i)append(wire,config_bin_diagnostic::kCommand,query(42+i));
    // A subsequent ordinary Identity must survive frame/union ownership.
    append(wire,CMD_RUNTIME_IDENTITY,{0xa5,'G','R','I',1,1,16,0,99,0,0,0,0,0,0,0});
    pump(backend,wire);
    need(!std::memcmp(&config,&saved,sizeof(Config)),"no live Config adoption or mutation");
    need(profile_store.Generation()==generation&&profile_store.ActiveId()==active,"no store mutation or activation");
    need(nor==before&&programs==0&&erases==0,"transport zero NOR mutation");no_handles();
    output(output_dir+"/"+name+".cobs",wire.output);
}
}
int main(int argc,char **argv) { try {
    using namespace test;need(argc==2,"output directory");output_dir=argv[1];
    Bytes bytes(70008);for(size_t i=0;i<bytes.size();++i)bytes[i]=uint8_t(i*31+7);
    scenario("recovery-once",bytes,true,true,2);
    scenario("not-recovery",bytes,false,true,1);
    scenario("no-storage",bytes,true,false,2);
    scenario("malformed-then-valid",bytes,true,true,1,true);
    // Negative raw-library calls prove mounted callbacks cannot reach the
    // actual NOR mutators. They are test controls, not diagnostic API options.
    fresh(bytes);const auto before=nor;
    need(lfs_remove(&fs,"/config.bin")<0,"readonly remove denial");
    need(nor==before&&programs==0&&erases==0,"remove preserved NOR");
    fresh(bytes);need(lfs_rename(&fs,"/config.bin","/renamed.bin")<0,"readonly rename denial");
    need(nor==before&&programs==0&&erases==0,"rename preserved NOR");
    fresh(bytes);lfs_file_t file{};uint8_t cache[256]{};lfs_file_config options{};options.buffer=cache;
    const int opened=lfs_file_opencfg(&fs,&file,"/config.bin",LFS_O_RDWR,&options);
    if(opened==0) {
        uint8_t value=7;const auto wrote=lfs_file_write(&fs,&file,&value,1);
        const int synced=lfs_file_sync(&fs,&file);need(wrote<0||synced<0,"readonly dirty handle denial");
        lfs_file_close(&fs,&file);
    }
    need(nor==before&&programs==0&&erases==0,"writable handle preserved NOR");no_handles();shutdown();
    std::puts("config_bin_readonly_backend_cobs_oneshot_identity_nonmutation=PASS");return 0;
} catch(const std::exception &e) { std::fprintf(stderr,"%s\n",e.what());return 1; } }
