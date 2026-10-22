// Test-only entry observer measures both original actual Start calls.
#define GLYPH_STORE_PUBLICATION_NO_MAIN
#include "store_publication_nor.cpp"
extern unsigned glyph_observed_start_calls;
int main(int argc,char **argv) {try {
    require(argc==2,"legacy Config");std::ifstream file(argv[1],std::ios::binary);Bytes raw((std::istreambuf_iterator<char>(file)),{});auto stream=pb_istream_from_buffer(raw.data(),raw.size());require(pb_decode(&stream,Config_fields,&legacy),"fixture decode");mount_fresh();ProfileStore store;require(store.Begin(),"actual Begin");require(store.Create(legacy.ultimate_profiles[0],"one",1,identity(10)).status==Status::Ok,"actual first create");glyph_observed_start_calls=0;require(store.Duplicate(1,1,"two",2,identity(11)).status==Status::Ok,"actual duplicate publication");require(glyph_observed_start_calls==2,"Duplicate preserves both actual Start calls");require(mounted_fs.mlist==nullptr,"duplicate handles close");std::puts("PASS actual Duplicate observes both original Start calls; no device");return 0;
 }catch(const std::exception&e){std::fprintf(stderr,"FAIL Duplicate Start: %s\n",e.what());return 1;}}
