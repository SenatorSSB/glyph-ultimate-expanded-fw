#include "glyph_config_validation.hpp"
#include "modes/Ultimate.hpp"
#include "modes/UltimateProfileEvaluator.hpp"
#include <pb_decode.h>
#include <pb_encode.h>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <vector>
#include <initializer_list>
#include <string>
static Config config{};
static UltimateProfile original{};
static size_t cases=0;
static uint64_t bits(std::initializer_list<int> v){uint64_t b=0;for(int n:v)b|=uint64_t{1}<<(n-1);return b;}
static UltimateProfileOutputEffect &effect(UltimateProfile &p,int key){for(size_t i=0;i<p.output_program.effects_count;i++)if(UltimateProfileEvaluator::EffectKey(p.output_program.effects[i])==key)return p.output_program.effects[i];std::abort();}
static void check(const char *id, UltimateProfile p, uint64_t input){
 config.ultimate_profiles[0]=p; ConfigValidationError err{};
 if(!validate_glyph_config(config,err)){std::fprintf(stderr,"INVALID %s: %s\n",id,err.message);std::exit(1);}
 static uint8_t encoded[65536];auto encoder=pb_ostream_from_buffer(encoded,sizeof(encoded));if(!pb_encode(&encoder,Config_fields,&config))std::abort();std::ofstream saved(std::string("corpus/")+id+".pb",std::ios::binary);saved.write(reinterpret_cast<const char*>(encoded),encoder.bytes_written);
 GameModeConfig mc{};mc.mode_id=MODE_ULTIMATE;Ultimate mode;mode.SetConfig(mc,&p);InputState in{};in.buttons=input;OutputState out{};out.buttons=0xa0030000;mode.UpdateOutputs(in,out,COMMS_BACKEND_XINPUT);
 bool roles[32]{};UltimateProfileEvaluator::EvaluateRoles(p,input,roles);
 std::printf("{\"id\":\"%s\",\"input\":\"%016llx\",\"table\":%u,\"role32\":%s,\"buttons\":\"%08x\",\"axes\":[%u,%u,%u,%u,%u,%u]}\n",id,(unsigned long long)input,UltimateProfileEvaluator::SelectTable(&p,input,0),roles[31]?"true":"false",out.buttons,out.leftStickX,out.leftStickY,out.rightStickX,out.rightStickY,out.triggerLAnalog,out.triggerRAnalog);
 ++cases;
}
static void sparse(UltimateProfile &p){p.roles_count=3;p.roles[0]={};p.roles[0].has_condition=true;p.roles[0].role_id=32;p.roles[0].condition.all_tokens_count=1;p.roles[0].condition.all_tokens[0]=71; p.roles[1]={};p.roles[1].has_condition=true;p.roles[1].role_id=7;p.roles[1].condition.all_tokens_count=1;p.roles[1].condition.all_tokens[0]=65; p.roles[2]={};p.roles[2].has_condition=true;p.roles[2].role_id=1;p.roles[2].condition.all_tokens_count=1;p.roles[2].condition.all_tokens[0]=1;p.table_rules_count=2;p.table_rules[0]={};p.table_rules[0].has_condition=true;p.table_rules[0].priority=200;p.table_rules[0].table_id=2;p.table_rules[1]={};p.table_rules[1].has_condition=true;p.table_rules[1].priority=2;p.table_rules[1].table_id=3;p.table_rules[1].condition.all_tokens_count=1;p.table_rules[1].condition.all_tokens[0]=96;}
int main(int argc,char **argv){if(argc!=2)return 2;std::ifstream s(argv[1],std::ios::binary);std::vector<uint8_t>b((std::istreambuf_iterator<char>(s)),{});auto stream=pb_istream_from_buffer(b.data(),b.size());if(!pb_decode(&stream,Config_fields,&config))return 3;original=config.ultimate_profiles[0];
 UltimateProfile p=original;sparse(p);check("SPARSE32-positive",p,bits({1}));check("SPARSE32-negative",p,bits({3})); std::reverse(p.roles,p.roles+p.roles_count);std::reverse(p.table_rules,p.table_rules+p.table_rules_count);check("SPARSE32-reordered",p,bits({1}));
 // Stock V2 routing affects role/table selection but intrinsic legacy RF6/RF7 remains un-routed.
 for(int v=2;v<=3;v++){p=original;p.schema_version=v;if(v==2){p.has_output_program=false;p.output_program={};}for(size_t i=0;i<p.routing_slots_count;i++){auto&r=p.routing_slots[i];if(r.slot_id==22)r.input_token=23;else if(r.slot_id==23)r.input_token=22;}check(("ROUTE-v"+std::to_string(v)+"-RF6").c_str(),p,bits({1,22}));check(("ROUTE-v"+std::to_string(v)+"-RF7").c_str(),p,bits({1,23}));}
 // Arbitrary admitted button and sparse role gates are extra conditions, not replacements for intrinsic phase activation.
 for(int gate:{0,1,96})for(int inv=0;inv<2;inv++){if(!gate&&inv)continue;for(int intrinsic=0;intrinsic<2;intrinsic++){p=original;sparse(p);auto&e=effect(p,5);e.gate_token=gate;e.gate_inverted=inv;e.coordinate_mode=ULTIMATE_COORDINATE_FIXED;e.coordinates_count=0;e.fixed_x=31;e.fixed_y=47;check(("GATE-"+std::to_string(gate)+"-inv"+std::to_string(inv)+"-intrinsic"+std::to_string(intrinsic)).c_str(),p,intrinsic?bits({1,22,23}):bits({1,22}));}}
 for(int source=1;source<=4;source++)for(int coord=1;coord<=4;coord++){p=original;auto&e=effect(p,1);e.direction_source=static_cast<UltimateProfileDirectionSource>(source);e.coordinate_mode=static_cast<UltimateProfileCoordinateMode>(coord);e.table_id=e.mode_table_id=0;e.fixed_x=e.fixed_y=0;e.coordinates_count=0;if(coord==2){e.table_id=2;e.mode_table_id=3;}if(coord==3){e.fixed_x=39;e.fixed_y=61;}if(coord==4){e.coordinates_count=18;for(int i=0;i<18;i++)e.coordinates[i]=10+i*7;}check(("COORD-src"+std::to_string(source)+"-mode"+std::to_string(coord)).c_str(),p,bits({1,2,43,42}));}
 for(int flags=0;flags<8;flags++){p=original;effect(p,11).value=flags;check(("DPAD-"+std::to_string(flags)).c_str(),p,bits({1,29}));}
 for(int key:{4,5,8,9,10}){p=original;effect(p,key).suppress=true;check(("SUPPRESS-"+std::to_string(key)).c_str(),p,(key==4||key==5)?bits({1,22,23}):bits({1,22,23,25,32,33,43,45}));}
 p=original;effect(p,0).digital_clear_mask=0x801;effect(p,0).digital_set_mask=0x406;check("DIGITAL-mask",p,bits({1,17,33,32}));
 p=original;effect(p,9).value=0;effect(p,10).value=255;check("TRIGGERS-0-255",p,bits({32,33}));
 // Full conditions all/any/none across routed slots and sparse higher-ID roles.
 p=original;sparse(p);p.roles[0].condition.any_tokens_count=2;p.roles[0].condition.any_tokens[0]=22;p.roles[0].condition.any_tokens[1]=23;p.roles[0].condition.none_tokens_count=1;p.roles[0].condition.none_tokens[0]=25;for(int n=0;n<4;n++)check(("CONDITION-"+std::to_string(n)).c_str(),p,n==0?bits({1}):n==1?bits({1,22}):n==2?bits({1,23}):bits({1,22,25}));
 p=original;sparse(p);for(size_t i=0;i<p.routing_slots_count;i++){auto&r=p.routing_slots[i];if(r.slot_id==1)r.input_token=3;else if(r.slot_id==3)r.input_token=1;}effect(p,0).gate_token=96;effect(p,0).digital_set_mask=8;check("ROUTED-gate32-physical3",p,bits({3}));check("ROUTED-gate32-physical1",p,bits({1}));
 p=original;auto &ce=effect(p,1);ce.coordinate_mode=ULTIMATE_COORDINATE_TABLE;ce.table_id=2;ce.mode_table_id=3;check("COORD-table-nonMode",p,bits({1,2}));check("COORD-table-Mode",p,bits({1,2,24}));
 for(int version=1;version<=3;version++){p=original;p.schema_version=version;if(version<3){p.has_output_program=false;p.output_program={};}if(version==1){p.roles_count=p.routing_slots_count=p.table_rules_count=0;p.default_table_id=0;}check(("LT6-v"+std::to_string(version)+"-default").c_str(),p,bits({1,38}));check(("LT6-v"+std::to_string(version)+"-ModeX1").c_str(),p,bits({1,24,37,38}));check(("LT6-v"+std::to_string(version)+"-forcedUp").c_str(),p,bits({1,21,38}));}
 const uint64_t conflicts[]={bits({1,2}),bits({1,2,38}),bits({1,2,19}),bits({1,2,19,38}),bits({1,2,19,24}),bits({1,2,18,19,24,38}),bits({1,4,19,20,24,25,34,35,36,37,38,41,42})};for(size_t i=0;i<sizeof(conflicts)/sizeof(*conflicts);i++)check(("CONFLICT-"+std::to_string(i)).c_str(),original,conflicts[i]);
 std::fprintf(stderr,"PASS %zu production-admitted independent legacy outputs\n",cases);
}
