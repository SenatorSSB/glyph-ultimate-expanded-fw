#include <config.pb.h>
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include "core/ModeSelectionTransaction.hpp"
#include "core/RecoveryInitialization.hpp"
#include "core/RecoveryStartupDiagnostics.hpp"
#include "core/ConfigWriteCandidate.hpp"
#include "core/ResourceDiagnostics.hpp"
static void require(bool b,const char *m){if(!b)throw std::runtime_error(m);}
struct InputState {uint64_t buttons=0;bool rt2=false,mb1=false;};
InputState inputs;
struct Matrix {void UpdateInputs(InputState &) {}} matrix_input;
struct InputSource {};InputSource **input_sources=nullptr;size_t input_source_count=0;
struct Watchdog {uint32_t scratch[8]={};} watchdog;Watchdog *watchdog_hw=&watchdog;
static unsigned bootloader=0,normal_initializations=0,ordinary_reports=0,serial_reports=0,store_begins=0,recovery_begins=0;
struct SerialStub {void begin(unsigned){}} Serial;
struct WireStub {void setSDA(unsigned){}void setSCL(unsigned){}void setClock(unsigned){}void begin(){}} Wire1;
struct Display {bool begin(unsigned,unsigned,bool,bool){return false;}void clearDisplay(){}void drawBitmap(unsigned,unsigned,const uint8_t *,unsigned,unsigned,unsigned){}void display(){throw std::runtime_error("headless display use");}} display;
struct Led {template<unsigned,unsigned>void addLeds(unsigned *,unsigned){}void setMaxPowerInVoltsAndMilliamps(unsigned,unsigned){}void setMaxRefreshRate(unsigned){}void setBrightness(unsigned){}void show(){}}FastLED;
constexpr unsigned OLED_SDA=0,OLED_SCL=1,SSD1306_SWITCHCAPVCC=1,NEOPIXEL=1,LED_PIN=2,LED_COUNT=1;unsigned bootloaderRGB[1]={};const uint8_t Bitmap_Update[1]={},Bitmap_Glyph_Splashscreen[1]={};
struct BootloaderRequest{};
void reboot_bootloader(){++bootloader;throw BootloaderRequest{};}
enum class BootOutcome {Pending,Normal,StorageFailure,DefaultsRejected,StartupConfigRejected,RecoveryConfigurator};
struct BootSnapshot {BootOutcome outcome=BootOutcome::Pending;bool display_ready=false;}boot_state;
void publish_boot_state(BootOutcome o,bool d){boot_state={o,d};}
BootSnapshot read_boot_state(){return boot_state;}
void refuse_boot(BootOutcome o,bool d){publish_boot_state(o,d);}
struct Backend {void SendReport(){++ordinary_reports;}InputState &GetInputs(){return inputs;}};
Backend **backends=nullptr;size_t backend_count=0;bool failed_detection=false;
struct Keyboard {void SendReport(InputState &){++ordinary_reports;}};Keyboard *current_kb_mode=nullptr;
Config config=Config_init_default;
struct Persistence {
 enum class LoadResult {Loaded,Rejected,StorageFailure};enum class SaveResult {Saved,Conflict,StorageFailure,UnknownOutcome};
 bool available=true,load_ok=true,validator=false;unsigned saves=0,loads=0;
 bool SetValidator(ConfigSemanticValidator){validator=true;return true;}
 bool IsAvailable(){return available;}
 bool ValidateConfig(const Config &,ConfigValidationError &){return validator;}
 LoadResult LoadConfigChecked(Config &c){++loads;if(!available)return LoadResult::StorageFailure;if(!load_ok)return LoadResult::Rejected;c=config;return LoadResult::Loaded;}
 uint32_t ConfigGeneration(const Config &){return 1;}
 SaveResult SaveConfigIfGenerationMatches(Config &,uint64_t){++saves;return SaveResult::Saved;}
 bool SaveConfig(Config &){++saves;return true;}
 bool CaptureLegacySource(uint8_t *){return true;}
 LoadResult ReadLegacyProfile(size_t,UltimateProfile &){return LoadResult::Loaded;}
}persistence;
struct ProfileStore {
 static constexpr unsigned kCompactConfigFormat=1;
 enum class Status {Ok,MigrationFenced};
 bool Begin(uint32_t=0,uint32_t=0){++store_begins;return true;}
 bool BeginRecovery(uint32_t=0,uint32_t=0){++recovery_begins;return true;}
 bool IsReadOnlyRecovery(){return false;}
 uint32_t Incarnation(){return 41;}
 bool MigrationPending(){return false;}
 Status CompleteMigration(const Config &){return Status::Ok;}
 Status ImportLegacy(const Config &,uint32_t *,size_t){return Status::Ok;}
 template<typename... Args>Status ImportLegacyStream(Args&&...){return Status::Ok;}
 bool PrepareCompact(Config &){return true;}
 bool ValidateCompactReceipt(const Config &){return true;}
}profile_store;
struct ConfiguratorBackend {
 ConfiguratorBackend(InputState &,InputSource **,size_t,Config &,SerialStub &){++constructions;}
 void SetRecoveryState(bool invalid,bool available){config_invalid=invalid;storage_available=available;readonly=true;}
 void SendReport(){++serial_reports;}
 bool config_invalid=false,storage_available=false,readonly=false;static unsigned constructions;
};unsigned ConfiguratorBackend::constructions=0;ConfiguratorBackend *recovery_configurator=nullptr;
bool validate_glyph_config(const Config &,ConfigValidationError &){return true;}
void normalize_legacy_glyph_rgb_noops(Config &){}
void request_mode_destination(CommunicationBackendId,size_t,const Config &){}
void set_mode_destination_selector(void(*)(CommunicationBackendId,size_t,const Config &)){}
void setup_mode_activation_bindings(GameModeConfig *,size_t,uint64_t){}
void select_mode(Backend **,size_t,Config &){++ordinary_reports;}
bool is_valid_usb_default_index(const Config &){return true;}
unsigned pinout=0,get_backend_config_default=0,get_usb_backend_config_default=0;
void detect_console(){}void init_secondary_backends_glyph(){}
template<typename... Args>size_t initialize_backends(Args&&...){++normal_initializations;return 0;}
#include "extracted_setup.inc"
int main(int argc,char **argv){try{require(argc==2,"case arg");config.ultimate_profile_store_format=1;config.ultimate_profile_store_incarnation=41;
 const bool manual=std::strcmp(argv[1],"manual")==0;const bool mb1=std::strcmp(argv[1],"mb1")==0;const bool fs=std::strcmp(argv[1],"filesystem")==0;
 inputs.rt2=manual||mb1;inputs.mb1=mb1;persistence.load_ok=manual||mb1;persistence.available=!fs;
 if(mb1){bool entered=false;try{setup();}catch(const BootloaderRequest &){entered=true;}require(entered&&bootloader==1&&persistence.loads==0&&recovery_begins==0&&ConfiguratorBackend::constructions==0,"MB1 has priority over RT2 and storage");}
 else {setup();require(boot_state.outcome==BootOutcome::RecoveryConfigurator&&ConfiguratorBackend::constructions==1,"both entry routes must run recovery transport");require(persistence.validator,"manual recovery installs validator");require(recovery_begins==(fs?0u:1u),"RT2/automatic recovery initializes available store inspection");require(recovery_configurator->readonly&&recovery_configurator->config_invalid==!manual&&recovery_configurator->storage_available==!fs,"recovery policy reflects Config and filesystem health");for(unsigned i=0;i<8;++i)loop();require(serial_reports==8&&ordinary_reports==0,"recovery loop remains responsive without gameplay");}
 require(persistence.saves==0&&store_begins==0&&normal_initializations==0&&backends==nullptr,"recovery and MB1 do not write or initialize gameplay");delete recovery_configurator;
 std::cout<<"actual_setup_route_"<<argv[1]<<"=PASS\n";return 0;}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
