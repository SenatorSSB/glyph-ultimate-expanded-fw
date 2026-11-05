#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include "core/ConfigWireValidator.hpp"
struct Source { const uint8_t *bytes; size_t size; size_t fail_at; };
bool Read(void *raw,size_t offset,uint8_t *into,size_t count) {
 auto &s=*static_cast<Source *>(raw);
 if(offset>=s.fail_at||offset>s.size||count>s.size-offset)return false;
 std::memcpy(into,s.bytes+offset,count);return true;
}
int main(){
 char input[140000];while(std::fgets(input,sizeof input,stdin)) {
  size_t n=std::strcspn(input,"\n");if(n%2)return 2;
  std::vector<uint8_t> bytes(n/2);for(size_t i=0;i<bytes.size();++i){char pair[3]={input[2*i],input[2*i+1],0};bytes[i]=std::strtoul(pair,nullptr,16);}
  config_wire::Workspace workspace;uint8_t borrowed[256];
  const auto span=config_wire::ValidateSpan(workspace,bytes.data(),bytes.size());
  Source source{bytes.data(),bytes.size(),SIZE_MAX};
  for(size_t chunk:{size_t(1),size_t(2),size_t(3),size_t(7),size_t(31),size_t(32),size_t(255),size_t(256)}) {
   const auto actual=config_wire::ValidateReader(workspace,Read,&source,bytes.size(),borrowed,chunk);
   if(actual!=span){std::fprintf(stderr,"chunk disagreement %zu\n",chunk);return 3;}
  }
  if(span==config_wire::Result::Valid&&!bytes.empty()) {
   source.fail_at=0;
   if(config_wire::ValidateReader(workspace,Read,&source,bytes.size(),borrowed,32)!=config_wire::Result::StorageFailure)return 4;
   if(bytes.size()>32) {
    source.fail_at=32;
    if(config_wire::ValidateReader(workspace,Read,&source,bytes.size(),borrowed,32)!=config_wire::Result::StorageFailure)return 5;
   }
  }
  std::printf("%u\n",unsigned(span));
 }
}
