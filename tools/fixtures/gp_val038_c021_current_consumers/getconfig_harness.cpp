// Literal GET method is supplied by authenticated Git C, equal to Git B.
// Print/end are external transport observations; this is not a COBS wire test.
#include <Arduino.h>
#include <LittleFS.h>
#include <config.pb.h>
#include <pb_encode.h>
#include <CRC32.h>
#include "core/Persistence.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>
#include <cstring>
using Bytes=std::vector<uint8_t>;
static void require(bool x,const char *s){if(!x)throw std::runtime_error(s);}
struct FrameOutput:Print {
    Bytes bytes;size_t limit=std::numeric_limits<size_t>::max(),attempts=0;bool end_result=true;
    using Print::write;
    size_t write(uint8_t b)override{++attempts;if(bytes.size()>=limit)return 0;bytes.push_back(b);return 1;}
    size_t write(const uint8_t *p,size_t n)override{size_t sent=0;for(size_t i=0;i<n;++i)sent+=write(p[i]);return sent;}
    bool end(){return end_result;}
};
class ConfiguratorBackend {
public:
    FrameOutput &_out;explicit ConfiguratorBackend(FrameOutput &out):_out(out){}
    bool HandleGetConfig();
    void WritePacket(Command command,uint8_t *data,size_t length){_out.write(uint8_t(command));_out.write(data,length);_out.end();}
};
#include "getconfig_body.inc"
static void reset(){LittleFS.faults=HostFileFaults{};LittleFS.read_open_ok=true;LittleFS.write_open_ok=true;}
static Config config;
static Bytes saved,payload;
static void seed(){reset();*LittleFS.bytes=saved;}
static void pass(const char *label){std::cout<<"raw_get_case="<<label<<" PASS\n";}
static void second_open_failure(unsigned call){if(call==1)LittleFS.read_open_ok=false;}
static Bytes error_packet(){const char text[]="Config file is invalid";Bytes out{uint8_t(CMD_ERROR)};out.insert(out.end(),text,text+sizeof(text));return out;}
int main(int argc,char **){try{
    require(!LittleFS.saw_auto_format_true&&LittleFS.format_calls==0,"no autoformat");
    if(argc>1){require(!persistence.IsAvailable(),"fresh unavailable");const unsigned opens=LittleFS.read_opens,writes=LittleFS.write_opens;FrameOutput out;require(!persistence.LoadConfigRaw(out,false)&&out.bytes.empty(),"unavailable raw guard");ConfiguratorBackend get(out);require(!get.HandleGetConfig()&&out.bytes==error_packet(),"bounded unavailable GET error with NUL");require(LittleFS.read_opens==opens&&LittleFS.write_opens==writes,"unavailable FS access");pass("unavailable_error_no_raw_payload");return 0;}
    require(persistence.IsAvailable(),"available");config=Config_init_default;config.game_mode_configs_count=1;config.game_mode_configs[0].mode_id=MODE_ULTIMATE;std::strcpy(config.game_mode_configs[0].name,"raw-payload");require(persistence.SaveConfig(config),"real save");saved=*LittleFS.bytes;payload=Bytes(saved.begin()+Persistence::config_offset,saved.end());require(!payload.empty(),"nonempty real payload");
    {seed();(*LittleFS.bytes)[Persistence::config_offset]^=1;FrameOutput out;ConfiguratorBackend get(out);const unsigned opens=LittleFS.read_opens;require(!get.HandleGetConfig()&&out.bytes==error_packet()&&LittleFS.read_opens==opens+1,"invalid check prevents raw load");pass("invalid_check_no_raw_load");}
    {seed();LittleFS.read_open_ok=false;FrameOutput out;require(!persistence.LoadConfigRaw(out,false)&&out.bytes.empty(),"raw open failure");pass("open_failure");}
    {seed();LittleFS.faults.fail_seek=true;FrameOutput out;require(!persistence.LoadConfigRaw(out,false)&&out.bytes.empty(),"raw seek failure");pass("seek_failure");}
    {seed();LittleFS.bytes->resize(Persistence::config_offset);FrameOutput out;require(persistence.LoadConfigRaw(out,false)&&out.bytes.empty(),"raw empty EOF");pass("empty_eof");}
    {seed();FrameOutput out;ConfiguratorBackend get(out);Bytes wanted{uint8_t(CMD_SET_CONFIG)};wanted.insert(wanted.end(),payload.begin(),payload.end());require(get.HandleGetConfig()&&out.bytes==wanted,"GET payload order");pass("payload_order");}
    {seed();(*LittleFS.bytes)[0]^=1;FrameOutput out;require(persistence.LoadConfigRaw(out,false)&&out.bytes==payload,"raw unchecked CRC");pass("validate_false");}
    {seed();FrameOutput out;out.limit=0;require(persistence.LoadConfigRaw(out,false)&&out.bytes.empty()&&out.attempts==payload.size(),"raw ignores zero output writes");pass("zero_output_write");}
    {seed();FrameOutput out;out.limit=2;require(persistence.LoadConfigRaw(out,false)&&out.bytes==Bytes(payload.begin(),payload.begin()+2)&&out.attempts==payload.size(),"raw ignores partial output writes");pass("partial_output_write");}
    {seed();LittleFS.faults.read_cutoff=Persistence::config_offset+2;FrameOutput out;require(persistence.LoadConfigRaw(out,false)&&out.bytes==Bytes(payload.begin(),payload.begin()+2),"raw EOF/read-error sentinel");pass("read_error_sentinel");}
    {seed();LittleFS.faults.seek_observer=second_open_failure;FrameOutput out;ConfiguratorBackend get(out);require(get.HandleGetConfig()&&out.bytes==Bytes{uint8_t(CMD_SET_CONFIG)},"GET ignores raw failure, end wins");pass("raw_result_ignored_packet_end_wins");}
    {seed();FrameOutput out;out.end_result=false;ConfiguratorBackend get(out);Bytes wanted{uint8_t(CMD_SET_CONFIG)};wanted.insert(wanted.end(),payload.begin(),payload.end());require(!get.HandleGetConfig()&&out.bytes==wanted,"GET packet end failure");pass("packet_end_failure_propagates");}
    require(!LittleFS.saw_auto_format_true&&LittleFS.format_calls==0,"no format after cases");std::cout<<"raw_get_matrix cases=11 PASS\n";return 0;
}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
