#include <config.pb.h>
#include "glyph_config_validation.hpp"
#include "config_rgb_target_domain.hpp"
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <limits>
static Config c,prior;
static unsigned cases=0;
static void require(bool v,const std::string &s){if(!v)throw std::runtime_error(s);}
static bool target(unsigned n){return (n>=1&&n<=8)||(n>=17&&n<=38)||(n>=41&&n<=45)||n==49;}
static void reset(){c=Config_init_default;c.rgb_configs_count=30;for(auto &rgb:c.rgb_configs){rgb.button_colors_count=60;for(auto &x:rgb.button_colors)x={BTN_LF1,0x12345678};}}
static void raw(Button &b,uint64_t n){using S=std::underlying_type<Button>::type;S s=n;std::memcpy(&b,&s,sizeof b);}
static void check(const std::string &s,bool ok){std::memcpy(&prior,&c,sizeof c);ConfigValidationError e;std::memset(&e,0x5a,sizeof e);require(validate_glyph_config(c,e)==ok,s+" verdict");require(std::memcmp(&prior,&c,sizeof c)==0,s+" Config mutation");if(ok){require(e.length==0,s+" stale error length");for(char b:e.message)require(b==0,s+" stale error bytes");}else require(e.length>0&&e.length<=sizeof(e.message)&&std::memchr(e.message,0,sizeof(e.message)),s+" bounded error");++cases;std::cout<<"validation_case="<<s<<" accepted="<<ok<<" immutable=BYTE_EXACT PASS\n";}
int main(){try{
 unsigned unique=0;bool domain[61]{};for(Button b:pixel_to_button_mappings){unsigned n=b;require(n<=60&&target(n),"actual pixel domain differs");if(!domain[n]){domain[n]=true;++unique;}}require(unique==36,"exact36 actual physical targets");
 for(unsigned n=0;n<256;++n)for(bool last:{false,true}){reset();raw(c.rgb_configs[last?29:0].button_colors[last?59:0].button,n);check("raw/"+std::to_string(n)+(last?"/last":"/first"),target(n));}
 if(sizeof(Button)==4)for(uint64_t n:{uint64_t(256),uint64_t(257),uint64_t(300),uint64_t(65536),uint64_t(UINT32_MAX)}){reset();raw(c.rgb_configs[29].button_colors[59].button,n);check("wide/"+std::to_string(n),false);}
 for(size_t outer:{size_t(0),size_t(30),size_t(31)}){reset();c.rgb_configs_count=outer;check("outer/"+std::to_string(outer),outer<=30);}
 reset();c.rgb_configs[29].button_colors_count=61;{using S=std::underlying_type<Button>::type;S valid=1;auto *bytes=reinterpret_cast<unsigned char*>(&c.rgb_configs[29]);std::memcpy(bytes+offsetof(RgbConfig,button_colors)+sizeof(c.rgb_configs[29].button_colors),&valid,sizeof valid);}require(!validate_glyph_rgb_targets(c),"direct helper rejects nested overflow before target walk");
 reset();c.rgb_configs_count=31;require(!validate_glyph_rgb_targets(c),"direct helper rejects outer overflow before walk");
 for(bool last:{false,true})for(size_t inner:{size_t(0),size_t(60),size_t(61)}){reset();c.rgb_configs[last?29:0].button_colors_count=inner;check("nested/"+std::to_string(last)+"/"+std::to_string(inner),inner<=60);}
 reset();c.rgb_configs_count=0;for(auto &rgb:c.rgb_configs){rgb.button_colors_count=61;for(auto &x:rgb.button_colors)raw(x.button,255);}check("ignored_outer_poison",true);
 reset();for(auto &rgb:c.rgb_configs){rgb.button_colors_count=0;for(auto &x:rgb.button_colors)raw(x.button,255);}check("ignored_nested_poison",true);
 for(unsigned mode:{unsigned(MODE_UNSPECIFIED),unsigned(MODE_ULTIMATE),unsigned(MODE_CUSTOM),unsigned(MODE_KEYBOARD)})for(bool disabled:{false,true}){
  reset();c.game_mode_configs_count=1;c.game_mode_configs[0].mode_id=static_cast<GameModeId>(mode);c.game_mode_configs[0].button_remapping_count=1;c.game_mode_configs[0].button_remapping[0]={BTN_LF1,disabled?BTN_UNSPECIFIED:BTN_MB12};
  check("independent_gameplay/"+std::to_string(mode)+"/"+std::to_string(disabled),true);
 }
 reset();for(auto &rgb:c.rgb_configs)for(size_t i=0;i<60;++i)rgb.button_colors[i]={i%2?BTN_LF1:BTN_MB1,uint32_t(i*1234567)};check("duplicate_order_color_preserved",true);
 reset();c.rgb_configs_count=1;c.rgb_configs[0].button_colors_count=20;for(size_t i=11;i<20;++i)c.rgb_configs[0].button_colors[i]={BTN_UNSPECIFIED,0};check("legacy20_nine_zero",false);c.rgb_configs[0].button_colors_count=11;c.rgb_configs[0].button_colors[0].color=0;check("corrected11_black",true);
 reset();c.default_backend_config=1;c.rgb_configs[0].button_colors[0].button=BTN_UNSPECIFIED;ConfigValidationError base,e;require(!validate_config_semantics(c,base)&&!validate_glyph_config(c,e)&&base.length==e.length&&std::memcmp(base.message,e.message,sizeof e.message)==0,"base errors retain precedence");
 c=Config_init_default;require(validate_config_rgb_targets(c,nullptr,0),"empty domain and absence");require(!validate_config_rgb_targets(c,nullptr,1),"null nonempty domain rejected");c.rgb_configs_count=1;c.rgb_configs[0].button_colors_count=1;c.rgb_configs[0].button_colors[0]={BTN_LF1,0};require(!validate_config_rgb_targets(c,nullptr,0),"empty domain populated rejected");Button zero=BTN_UNSPECIFIED;c.rgb_configs[0].button_colors[0].button=zero;require(!validate_config_rgb_targets(c,&zero,1),"zero never eligible even supplied domain");
 std::cout<<"validation_matrix total="<<cases<<" physical=36 other_named=24 byte_width="<<sizeof(Button)<<" PASS\n";return 0;
 }catch(const std::exception &e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}}
