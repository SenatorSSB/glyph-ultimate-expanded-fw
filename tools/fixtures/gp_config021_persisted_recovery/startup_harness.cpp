#include <Arduino.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_TinyUSB.h>
#include <LittleFS.h>
#include <CRC32.h>
#include <pb_encode.h>
#include <atomic>
#include <thread>
#include <iostream>
#include <stdexcept>
#include <string>
#include <cstdlib>
#include "core/Persistence.hpp"
#include "core/config_validation.hpp"
#include "core/CommunicationBackend.hpp"
#include "host_observation.hpp"
extern void setup(); extern void loop(); extern void setup1(); extern void loop1();
extern Config config; extern InputState inputs;
extern size_t input_source_count, backend_count;
extern CommunicationBackend **backends;
extern Adafruit_SSD1306 display;
static void require(bool v,const char *m) { if (!v) throw std::runtime_error(m); }
static std::vector<uint8_t> encoded(const Config &v) {
 size_t n=0;require(pb_get_encoded_size(&n,Config_fields,&v),"real encoded size");
 std::vector<uint8_t> b(n);auto o=pb_ostream_from_buffer(b.data(),b.size());
 require(pb_encode(&o,Config_fields,&v)&&o.bytes_written==n,"real encode exact");return b;
}
static std::vector<uint8_t> stored(const Config &v) {
 auto b=encoded(v);CRC32 c;c.update(b.data(),b.size());
 Persistence::ConfigHeader h{};h.config_size=b.size();h.config_crc=c.finalize();
 std::vector<uint8_t> r(sizeof(h)+b.size());std::memcpy(r.data(),&h,sizeof(h));
 std::memcpy(r.data()+sizeof(h),b.data(),b.size());return r;
}
static std::thread core1;static std::atomic<bool> core1_finished{false};
static void start_pending_core() {
 unsigned before=__atomic_load_n(&host_observation.sync_acquires,__ATOMIC_RELAXED);
 core1=std::thread([]{setup1();core1_finished.store(true);});
 auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(2);
 while (__atomic_load_n(&host_observation.sync_acquires,__ATOMIC_RELAXED)==before &&
        std::chrono::steady_clock::now()<deadline) std::this_thread::yield();
 require(!core1_finished.load(),"core1 must wait on Pending before publication");
 require(__atomic_load_n(&host_observation.sync_acquires,__ATOMIC_RELAXED)>before,"early core1 actually acquires initialized synchronization");
}
static void during_seek(unsigned n) { if(n==2) start_pending_core(); }
int main(int argc,char **argv) {
 try {
 const char *rgb_offsets=std::getenv("GLYPH_HOST_RGB_CTOR_OFFSETS");
 require(rgb_offsets!=nullptr,"runner supplies actual template constructor addresses");
 char *next=nullptr;host_rgb_ctor_offsets[0]=std::strtoull(rgb_offsets,&next,16);
 require(next&&*next==',',"first template constructor offset");
 host_rgb_ctor_offsets[1]=std::strtoull(next+1,&next,16);
 require(next&&*next==0&&host_rgb_ctor_offsets[0]!=host_rgb_ctor_offsets[1],"two exact distinct template constructor offsets");
 require(argc==4,"case schedule display args");std::string k=argv[1],sched=argv[2];
 bool screen=std::string(argv[3])=="display";display.begin_ok=screen;
 ConfigValidationError e;require(validate_config_semantics(config,e),"literal source defaults validate");
 static Config file_config=config;
 if(k=="rejected") {
  size_t i=0;while(i<file_config.game_mode_configs_count&&file_config.game_mode_configs[i].mode_id!=MODE_ULTIMATE)++i;
  require(i<file_config.game_mode_configs_count,"source Ultimate row");file_config.game_mode_configs[i].custom_mode_config=256;
 }
 if(k=="configurator") {
  size_t i=0;while(i<file_config.communication_backend_configs_count&&file_config.communication_backend_configs[i].backend_id!=COMMS_BACKEND_CONFIGURATOR)++i;
  require(i<file_config.communication_backend_configs_count,"source Configurator row");file_config.default_usb_backend_config=i+1;file_config.communication_backend_configs[i].default_mode_config=1;
 }
 LittleFS.bytes=std::make_shared<std::vector<uint8_t>>(stored(file_config));
 if(k=="missing"||k=="unformatted")LittleFS.bytes->clear();
 if(k=="open")LittleFS.read_open_ok=false;
 if(k=="defaults")config.game_mode_configs_count=31;
 static unsigned char prior[sizeof(config)];std::memcpy(prior,&config,sizeof(config));auto oldfile=*LittleFS.bytes;unsigned writes=LittleFS.write_opens;
 unsigned init=host_observation.sync_initializations;host_observation=HostObservation{};
 host_observation.sync_initializations=init;host_trace_enabled=true;
 // Input seam: the physical matrix is not claimed by these cases.
 input_source_count=0;inputs=InputState{};watchdog_hw->scratch[0]=1;watchdog_hw->scratch[1]=1;host_watchdog_reboot=false;
 if(k=="mb1") {
  inputs.mb1=true;bool escaped=false;try{setup();}catch(const HostBootloaderRequest&){escaped=true;}
  require(escaped,"actual MB1 branch enters bootloader");
  require(LittleFS.read_opens==0&&LittleFS.write_opens==writes,"MB1 precedes load/save");
  require(host_observation.backend_initializations==0&&host_observation.backend_constructions==0,"MB1 no normal construction");
  if(!screen)require(display.display_calls==0&&display.bitmap_calls==0,"failed display guards MB1 splash");
  std::cout<<"case=whole_startup_mb1_before_load_"<<argv[3]<<" PASS\n";return 0;
 }
 if(sched=="early"){start_pending_core();loop();loop1();}
 if(sched=="during")LittleFS.faults.seek_observer=during_seek;
 setup();if(core1.joinable())core1.join();else setup1();
 bool normal=k=="normal"||k=="configurator";
 if(normal) {
  require(backends!=nullptr&&backend_count>0,"valid stored boot constructs backends");
  require(host_observation.backend_initializations>0&&host_observation.backend_constructions>0&&host_observation.mode_binding_setups>0,"positive actual init/constructor/binding traces");
  require(host_observation.menu_constructions>=3&&host_observation.rgb_constructions>0,"positive actual menu/RGB constructor traces");
  require(encoded(config)==encoded(file_config),"valid stored boot decoded Config");
  if(k=="configurator")require(host_observation.configurator_constructions>0,"positive actual Configurator trace");
  loop();loop1();if(k=="normal")require(host_observation.ordinary_reports+host_hid_reports>0,"normal report reaches physical seam");
 }else{
  require(std::memcmp(&config,prior,sizeof(config))==0,"refusal preserves caller bytes");
  require(backends==nullptr&&backend_count==0,"refusal before backend allocation");
  require(host_observation.backend_initializations==0&&host_observation.backend_constructions==0&&host_observation.mode_binding_setups==0&&host_observation.menu_constructions==0&&host_observation.rgb_constructions==0&&host_observation.configurator_constructions==0,"actual normal constructors/init/bindings absent in refusal");
  require(watchdog_hw->scratch[0]==0&&watchdog_hw->scratch[1]==0,"refusal clears watchdog overrides");
  unsigned draws=display.display_calls;
  if(screen){std::string first=k=="rejected"?"Stored Config rejected":k=="defaults"?"Config defaults rejected":"Config storage failure";
   require(display.lines==std::vector<std::string>{first,"Recovery required","Operation refused"},"dedicated recovery text");}
  // Poison the ordinary pointer after proving no construction. The refusal gates
  // must prevent a normal dereference even when a secondary null guard cannot.
  backends=reinterpret_cast<CommunicationBackend **>(static_cast<uintptr_t>(1));backend_count=1;
  for(int i=0;i<8;++i){inputs.buttons=UINT64_MAX;loop();loop1();}
  backends=nullptr;backend_count=0;
  require(host_observation.ordinary_reports+host_hid_reports==0&&Serial.output.empty(),"no reports/transport after refusal menu input");
  require(screen?display.display_calls==draws+8:display.display_calls==0,"unconditional recovery redraw or allocation-failed no draw");
  require(LittleFS.write_opens==writes&&*LittleFS.bytes==oldfile,"refusal preserves stored bytes/no write");
  if(k=="defaults"||k=="mount"||k=="config")require(LittleFS.read_opens==0,"preload refusal invalid defaults/unavailable mount");
 }
 require(LittleFS.format_calls==0&&!LittleFS.saw_auto_format_true,"no format/autoformat");
 require(host_observation.sync_initializations>0&&host_observation.sync_acquires>0&&host_observation.sync_acquires==host_observation.sync_releases,"actual host synchronization closure");
 std::cout<<"case=whole_startup_"<<k<<'_'<<sched<<'_'<<argv[3]<<" PASS init="<<host_observation.backend_initializations<<" backends="<<host_observation.backend_constructions<<" menus="<<host_observation.menu_constructions<<" rgb="<<host_observation.rgb_constructions<<" configurator="<<host_observation.configurator_constructions<<'\n';return 0;
 }catch(const std::exception &e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}
}
