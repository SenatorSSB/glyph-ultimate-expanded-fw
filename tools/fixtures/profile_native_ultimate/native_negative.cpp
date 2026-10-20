#include "modes/UltimateNativeProfile.hpp"
#include "modes/UltimateNativeEvaluator.hpp"
#include "core/RuntimeProfileDigest.hpp"
#include "core/ProfileStoreRequestIdentity.hpp"
#include <pb_encode.h>
#include <pb_decode.h>
#include <fstream>
#include <iterator>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
using Bytes=std::vector<uint8_t>;
void require(bool value,const char *label) {if(!value){std::fprintf(stderr,"FAIL %s\n",label);std::exit(1);}}
Bytes read(const char *path) {std::ifstream f(path,std::ios::binary);return {(std::istreambuf_iterator<char>(f)),{}};}
void put16(Bytes &b,size_t o,unsigned v){b[o]=v;b[o+1]=v>>8;}
int main(int argc,char **argv) {
    require(argc==3,"negative ordinary maximum");const auto valid=read(argv[1]),maximum=read(argv[2]);
    ultimate_native::PreparedView view;
    require(ultimate_native::Prepare(valid.data(),valid.size(),1,view),"ordinary native valid");
    require(maximum.size()==3336&&ultimate_native::Prepare(maximum.data(),maximum.size(),1,view),"exact maximum native body valid");
    require(!ultimate_native::Prepare(valid.data(),valid.size()-1,1,view),"truncation rejects");
    auto extra=valid;extra.push_back(0);require(!ultimate_native::Prepare(extra.data(),extra.size(),1,view),"trailing bytes reject");
    auto bad=[&](const char *name,size_t offset,unsigned value,bool wide=false){auto b=valid;if(wide)put16(b,offset,value);else b[offset]=value;require(!ultimate_native::Prepare(b.data(),b.size(),1,view),name);};
    bad("magic",0,0);bad("encoding",4,2);bad("engine ABI",6,2);bad("total length",8,0,true);
    bad("condition capacity",10,97);bad("early condition count",11,97);bad("source capacity",12,9);
    bad("rule capacity",13,33);bad("binding capacity",14,33);bad("effect capacity",15,17);
    bad("default table",16,28);bad("base source missing",17,0);bad("Dpad flags",19,8);
    bad("gate domain",20,0x6001,true);bad("token capacity",92,769,true);bad("reserved header",94,1);
    bad("duplicate/canonical condition ID",600,2);bad("condition count bits",601,0x200,true);
    ultimate_native::Prepare(valid.data(),valid.size(),1,view);
    bad("forward role/cycle",view.condition_token_offsets[0],0x3001,true);
    bad("input domain ID",view.condition_token_offsets[0],0x203d,true);
    bad("early direction read",view.condition_token_offsets[0],0x4001,true);
    bad("condition digital read",view.condition_token_offsets[0],0x5001,true);
    bad("source ID",view.source_offset,2);bad("base source cannot late/direction read",view.source_offset+1,0x4001,true);
    bad("rule priority zero",view.rule_offset,0);bad("rule table",view.rule_offset+1,28);
    auto collision=valid;collision[view.rule_offset+4]=collision[view.rule_offset];require(!ultimate_native::Prepare(collision.data(),collision.size(),1,view),"duplicate table priority");
    ultimate_native::Prepare(valid.data(),valid.size(),1,view);
    bad("binding digital mask",view.binding_offset+2,4096,true);bad("binding winner",view.binding_offset+4,28);bad("binding flags",view.binding_offset+5,1);
    bad("effect target",view.effect_offset,0);bad("effect priority",view.effect_offset+1,0);bad("effect flags",view.effect_offset+29,4);bad("effect reserved",view.effect_offset+30,1);
    bad("effect source",view.effect_offset+6,0);bad("effect mode",view.effect_offset+7,5);bad("mask reserved",view.mask_offset+6,2,true);
    auto overlap=valid;put16(overlap,view.mask_offset+2,1);put16(overlap,view.mask_offset+4,1);require(!ultimate_native::Prepare(overlap.data(),overlap.size(),1,view),"post mask disjoint");
    // Actual production callback transport, duplicate field/presence checks and
    // field-order permutations, including unchanged legacy last-schema-wins.
    static UltimateProfile p;ultimate_native::PayloadLease l;
    auto wire=[&](const Bytes &body){Bytes b={8,5,66};size_t n=body.size();while(n>127){b.push_back((n&127)|128);n>>=7;}b.push_back(n);b.insert(b.end(),body.begin(),body.end());return b;};
    auto native=wire(valid);require(ultimate_native::DecodeProfile(native.data(),native.size(),p,l),"callback decode");
    auto rejected=[&](Bytes b,const char *label){ultimate_native::PayloadLease lease;require(!ultimate_native::DecodeProfile(b.data(),b.size(),p,lease),label);};
    auto b=native;b.insert(b.end(),native.begin()+2,native.end());rejected(b,"duplicate tag8");
    b=native;b.insert(b.begin(),{72,1});rejected(b,"unknown before schema5");b=native;b.insert(b.end(),{72,1});rejected(b,"unknown after schema5");
    b=native;b.insert(b.begin(),{18,0});rejected(b,"mixed legacy preceding schema5");b=native;b.insert(b.end(),{18,0});rejected(b,"mixed legacy trailing schema5");
    b=native;b.insert(b.end(),{8,5});rejected(b,"native duplicate schema");
    b=native;b[1]=1;rejected(b,"tag8 schema1");
    b={8,1,8,2};require(ultimate_native::DecodeProfile(b.data(),b.size(),p,l)&&p.schema_version==2,"legacy duplicate schema last-wins");
    b={8,2,8,1};require(ultimate_native::DecodeProfile(b.data(),b.size(),p,l)&&p.schema_version==1,"legacy reverse duplicate schema last-wins");
    require(ultimate_native::DecodeProfile(native.data(),native.size(),p,l)&&ultimate_native::ValidProfile(p),"lease semantic validation");
    uint8_t digest[32],after[32];require(runtime_identity::PayloadDigest(p,digest),"callback payload digest");
    static ultimate_native::OwnedProgram active;
    require(ultimate_native::CopyProgram(ultimate_native::CandidateView(),active,42),"owned candidate copy");
    ultimate_native::PayloadLease owned;require(ultimate_native::BindOwned(p,active,owned),"owned callback rebind");
    std::fill(native.begin(),native.end(),0xcc);l.Release();require(runtime_identity::PayloadDigest(p,after)&&!std::memcmp(digest,after,32),"incoming poison cannot alter owned program/digest");
    static ProfileStoreRequest request;request=ProfileStoreRequest_init_default;request.has_profile=true;request.profile=p;request.request_token=0x123456789;
    ProfileStoreTransactionIdentity identity;require(ProfileStoreRequestIdentity(request,identity)&&request.request_token==0x123456789,"request identity binds live native callback/restores token");
    owned.Release();require(!runtime_identity::PayloadDigest(p,after),"released lease cannot encode");
    static Config config;config=Config_init_default;ultimate_native::RejectEmbedded(config);
    auto profile=wire(valid);Bytes embedded={0xca,0x0c};size_t n=profile.size();while(n>127){embedded.push_back((n&127)|128);n>>=7;}embedded.push_back(n);embedded.insert(embedded.end(),profile.begin(),profile.end());
    auto stream=pb_istream_from_buffer(embedded.data(),embedded.size());require(!pb_decode(&stream,Config_fields,&config),"actual Config decoder rejects native callback");
    profile[1]=1;embedded.resize(embedded.size()-profile.size());embedded.insert(embedded.end(),profile.begin(),profile.end());
    config=Config_init_default;ultimate_native::RejectEmbedded(config);stream=pb_istream_from_buffer(embedded.data(),embedded.size());require(!pb_decode(&stream,Config_fields,&config),"actual Config decoder rejects schema1 tag8");
    std::puts("PASS native validation negatives, canonical field-order rejection, legacy duplicate-schema compatibility, callback leases/copy poisoning/request identity/embedded rejection");
}
