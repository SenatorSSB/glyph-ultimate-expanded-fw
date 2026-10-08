#include <config.pb.h>
#include <pb_decode.h>
#include <pb_common.h>
#include "glyph_config_validation.hpp"
#include <fstream>
#include <iterator>
#include <vector>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <limits>
#include <type_traits>
using Bytes=std::vector<uint8_t>;
extern "C" int gp_config020_abi_probe();
static Config c,prior;
static unsigned cases=0;
static void require(bool b,const std::string&s){if(!b)throw std::runtime_error(s);}
static void append(Bytes&a,const Bytes&b){a.insert(a.end(),b.begin(),b.end());}
static Bytes varint(uint64_t n){Bytes b;do{uint8_t x=n&127;n>>=7;b.push_back(x|(n?128:0));}while(n);return b;}
static Bytes scalar(unsigned t,uint64_t n){Bytes b=varint(uint64_t(t)<<3);append(b,varint(n));return b;}
static Bytes msg(unsigned t,const Bytes&v){Bytes b=varint((uint64_t(t)<<3)|2);append(b,varint(v.size()));append(b,v);return b;}
static bool target(uint64_t n){return (n>=1&&n<=8)||(n>=17&&n<=38)||(n>=41&&n<=45)||n==49;}
static bool decode(const Bytes&b){c=Config_init_default;auto s=pb_istream_from_buffer(b.data(),b.size());return pb_decode(&s,Config_fields,&c)&&s.bytes_left==0;}
static void check(const std::string&label,const Bytes&b,bool decoded,bool accepted){bool d=decode(b);require(d==decoded,label+" decode verdict");if(d){std::memcpy(&prior,&c,sizeof c);ConfigValidationError e;require(validate_glyph_config(c,e)==accepted,label+" validation verdict");require(std::memcmp(&prior,&c,sizeof c)==0,label+" mutation");}++cases;std::cout<<"decoder_case="<<label<<" decoded="<<d<<" accepted="<<(d&&accepted)<<" PASS\n";}
int main(int argc,char**argv){try{
 require(gp_config020_abi_probe()==0,"existing12 binding descriptor ABI");ButtonToColorMapping mapping{};pb_field_iter_t it{};require(pb_field_iter_begin(&it,ButtonToColorMapping_fields,&mapping)&&pb_field_iter_find(&it,1),"real RGB descriptor exists");require(it.data_size==sizeof(Button)&&static_cast<unsigned char*>(it.pField)-reinterpret_cast<unsigned char*>(&mapping)==offsetof(ButtonToColorMapping,button),"real C descriptor RGB width/offset agrees C++");
 if(argc==3&&std::string(argv[1])=="--config-raw") {std::ifstream f(argv[2],std::ios::binary);require(bool(f),"raw input readable");Bytes b((std::istreambuf_iterator<char>(f)),{});bool d=decode(b);ConfigValidationError e{};bool ok=d&&validate_glyph_config(c,e);std::cout<<"{\"accepted\":"<<(ok?"true":"false")<<",\"decoded\":"<<(d?"true":"false")<<",\"error\":\""<<(d?e.message:"Nanopb decode rejected")<<"\"}\n";return ok?0:d?1:2;}

 if(argc==3&&std::string(argv[1])=="--archived-raw-check") {
  std::ifstream f(argv[2],std::ios::binary);require(bool(f),"archive raw readable");Bytes b((std::istreambuf_iterator<char>(f)),{});require(decode(b),"archive real decode");ConfigValidationError e,base;
  require(validate_config_semantics(c,base),"archive base semantics pass");require(!validate_glyph_config(c,e)&&std::string(e.message)=="Config contains an invalid RGB target","archive rejects expected RGB defect only");
  require(c.rgb_configs_count==13,"archive13 RGBblocks");auto &rgb=c.rgb_configs[10];require(rgb.button_colors_count==20,"archive block11 count20");const Button ids[]={BTN_LF1,BTN_LF2,BTN_LF3,BTN_LT1,BTN_RF1,BTN_RF2,BTN_RF5,BTN_RF6,BTN_RT1,BTN_MB1,BTN_LF5};
  for(size_t i=0;i<11;++i)require(rgb.button_colors[i].button==ids[i]&&rgb.button_colors[i].color==2282478,"archive exact11 legacy records");for(size_t i=11;i<20;++i)require(rgb.button_colors[i].button==BTN_UNSPECIFIED&&rgb.button_colors[i].color==0,"archive exactly9 counted empties");
  std::memcpy(&prior,&c,sizeof c);rgb.button_colors_count=11;rgb.button_colors[0].color=0;require(validate_glyph_config(c,e),"minimally corrected archive accepts");rgb.button_colors_count=20;rgb.button_colors[0].color=2282478;require(std::memcmp(&prior,&c,sizeof c)==0,"all unrelated archive fields byte identical after undo two fields");
  std::cout<<"archived_owner_config legacy=EXPECTED_RGB_REJECT corrected=ACCEPTED unrelated=BYTE_EXACT historical_not_fresh=YES PASS\n";return 0;
 }
 require(argc==1,"unknown decoder args");
 for(uint64_t n=0;n<256;++n)for(bool last:{false,true}){Bytes rgb;for(size_t j=0;j<(last?59:0);++j)append(rgb,msg(1,scalar(1,1)));append(rgb,msg(1,scalar(1,n)));Bytes wire;for(size_t i=0;i<(last?29:0);++i)append(wire,msg(5,{}));append(wire,msg(5,rgb));check("raw/"+std::to_string(n)+(last?"/last":"/first"),wire,true,target(n));}
 for(uint64_t n:{uint64_t(256),uint64_t(257),uint64_t(300),uint64_t(65536),uint64_t(UINT32_MAX),uint64_t(UINT32_MAX)+1,std::numeric_limits<uint64_t>::max()})check("overflow/"+std::to_string(n),msg(5,msg(1,scalar(1,n))),sizeof(Button)==4&&n<=UINT32_MAX,false);
 for(size_t outer:{size_t(0),size_t(30),size_t(31)}){Bytes wire;for(size_t i=0;i<outer;++i)append(wire,msg(5,{}));check("outer/"+std::to_string(outer),wire,outer<=30,outer<=30);}
 for(bool last:{false,true})for(size_t n:{size_t(0),size_t(60),size_t(61)}){Bytes rgb,wire;for(size_t j=0;j<n;++j)append(rgb,msg(1,scalar(1,1)));for(size_t i=0;i<(last?29:0);++i)append(wire,msg(5,{}));append(wire,msg(5,rgb));check("nested/"+std::to_string(last)+"/"+std::to_string(n),wire,n<=60,n<=60);}
 for(Bytes bad:{Bytes{0x2a,0x02,0x0a},Bytes{0x2a,0x04,0x0a,0x02,0x08},Bytes{0x2a,0x03,0x0a,0x01,0x80},Bytes{0x2a,0x03,0x0a,0x01,0x0f}})for(bool last:{false,true}){Bytes wire;for(size_t i=0;i<(last?29:0);++i)append(wire,msg(5,{}));append(wire,bad);check("malformed/"+std::to_string(cases)+(last?"/last":"/first"),wire,false,false);}
 Bytes duplicate=scalar(1,0);append(duplicate,scalar(1,1));check("last_singular_valid",msg(5,msg(1,duplicate)),true,true);duplicate=scalar(1,1);append(duplicate,scalar(1,0));check("last_singular_invalid",msg(5,msg(1,duplicate)),true,false);
 std::cout<<"decoder_matrix total="<<cases<<" real_nanopb=YES descriptor_C_CXX=YES byte_width="<<sizeof(Button)<<" PASS\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}}
