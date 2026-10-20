#include "core/RuntimeProfileDigest.hpp"
#include <pb_decode.h>
#include <cstdio>
#include <fstream>
#include <vector>
int main(int argc,char **argv) {
 if(argc!=2)return 2;
 static UltimateProfile profile=UltimateProfile_init_default;
 std::ifstream file(argv[1],std::ios::binary);std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(file)),{});
 auto stream=pb_istream_from_buffer(bytes.data(),bytes.size());uint8_t digest[32];
 if(!pb_decode(&stream,UltimateProfile_fields,&profile)||stream.bytes_left||!runtime_identity::PayloadDigest(profile,digest))return 1;
 for(auto byte:digest)std::printf("%02x",byte);std::puts("");return 0;
}
