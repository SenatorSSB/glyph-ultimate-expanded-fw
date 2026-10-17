#include <config.pb.h>
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include "core/ModeSelectionTransaction.hpp"
#include "core/RecoveryInitialization.hpp"
#include "core/RecoveryStartupDiagnostics.hpp"
#include "core/RecoveryUsbDiagnostics.hpp"
#include "core/ConfigWriteCandidate.hpp"
#include "core/ResourceDiagnostics.hpp"
#include "core/ColdRecoveryBoot.h"
#include "core/ColdRecoveryIntent.hpp"
static void require(bool b,const char *m){if(!b)throw std::runtime_error(m);}
struct InputState {uint64_t buttons=0;bool rt2=false,mb1=false;};
InputState inputs;
static unsigned matrix_samples=0;
struct Matrix {void UpdateInputs(InputState &) {++matrix_samples;}} matrix_input;
struct InputSource {};InputSource **input_sources=nullptr;size_t input_source_count=0;
struct Watchdog {uint32_t scratch[8]={};} watchdog;Watchdog *watchdog_hw=&watchdog;
static unsigned bootloader=0,normal_initializations=0,ordinary_reports=0,serial_reports=0,store_begins=0,recovery_begins=0;
static unsigned cold_prepares=0,cold_starts=0,reboots=0;
static bool cold_boot=false,reboot_returns=false,prepare_fails=false,start_fails=false;
struct FirmwareReboot {};
void reboot_firmware(){++reboots;if(!reboot_returns)throw FirmwareReboot{};}
extern "C" bool GlyphColdRecoveryBoot(){return cold_boot;}
extern "C" bool GlyphColdRecoveryArm(){return !cold_boot&&ColdRecoveryIntent::Arm(watchdog_hw->scratch);}
extern "C" bool GlyphColdRecoveryPrepare(){++cold_prepares;return !prepare_fails;}
extern "C" bool GlyphColdRecoveryStart(){++cold_starts;return !start_fails;}
struct SerialStub {void begin(unsigned){}} Serial;
struct WireStub {void setSDA(unsigned){}void setSCL(unsigned){}void setClock(unsigned){}void begin(){}} Wire1;
struct Display {bool begin(unsigned,unsigned,bool,bool){return false;}void clearDisplay(){}void drawBitmap(unsigned,unsigned,const uint8_t *,unsigned,unsigned,unsigned){}void display(){throw std::runtime_error("headless display use");}} display;
struct Led {template<unsigned,unsigned>void addLeds(unsigned *,unsigned){}void setMaxPowerInVoltsAndMilliamps(unsigned,unsigned){}void setMaxRefreshRate(unsigned){}void setBrightness(unsigned){}void show(){}}FastLED;
constexpr unsigned OLED_SDA=0,OLED_SCL=1,SSD1306_SWITCHCAPVCC=1,NEOPIXEL=1,LED_PIN=2,LED_COUNT=1;unsigned bootloaderRGB[1]={};const uint8_t Bitmap_Update[1]={},Bitmap_Glyph_Splashscreen[1]={};
struct BootloaderRequest{};
void reboot_bootloader(){++bootloader;throw BootloaderRequest{};}
enum class BootOutcome {Pending,Normal,StorageFailure,DefaultsRejected,StartupConfigRejected,RecoveryConfigurator,RecoveryTransportFailure};
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
 const std::string mode=argv[1];const bool manual=mode=="manual"||mode=="arm-conflict"||mode=="reboot-return";const bool mb1=mode=="mb1";const bool fs=mode=="filesystem";
 cold_boot=mode=="cold"||mode=="cold-mb1"||mode=="prepare-failure"||mode=="start-failure";
 prepare_fails=mode=="prepare-failure";start_fails=mode=="start-failure";reboot_returns=mode=="reboot-return";
 inputs.rt2=manual||mb1;inputs.mb1=mb1||mode=="cold-mb1";persistence.load_ok=manual||mb1||cold_boot;persistence.available=!fs;
 if(mode=="arm-conflict")watchdog.scratch[2]=0x4d445354;
 if(mb1){bool entered=false;try{setup();}catch(const BootloaderRequest &){entered=true;}require(entered&&bootloader==1&&persistence.loads==0&&recovery_begins==0&&ConfiguratorBackend::constructions==0,"MB1 has priority over RT2 and storage");}
 else if(manual){bool rebooted=false;try{setup();}catch(const FirmwareReboot&){rebooted=true;}require(reboots==(mode=="arm-conflict"?0u:1u)&&rebooted==(mode=="manual"),"Boot A arms one watchdog reboot or refuses conflict/return");require(persistence.loads==0&&recovery_begins==0&&ConfiguratorBackend::constructions==0,"Boot A never inspects or constructs backend");if(mode=="arm-conflict")require(watchdog.scratch[2]==0x4d445354,"conflict marker preserved");else require(watchdog.scratch[2]==ColdRecoveryIntent::kMagic,"Boot A exact ephemeral marker");if(mode!="manual")require(boot_state.outcome==BootOutcome::RecoveryTransportFailure,"conflict/returned reboot permanently refused");}
 else {setup();if(prepare_fails||start_fails){require(boot_state.outcome==BootOutcome::RecoveryTransportFailure,"cold USB failure permanently refused");require(cold_prepares==1&&cold_starts==(start_fails?1u:0u),"failed cold preparation/start never retries");}else{require(boot_state.outcome==BootOutcome::RecoveryConfigurator&&ConfiguratorBackend::constructions==1,"both entry routes must run recovery transport");require(persistence.validator,"manual recovery installs validator");require(recovery_begins==(fs?0u:1u),"RT2/automatic recovery initializes available store inspection");require(recovery_configurator->readonly&&recovery_configurator->config_invalid==!cold_boot&&recovery_configurator->storage_available==!fs,"recovery policy reflects Config and filesystem health");for(unsigned i=0;i<8;++i)loop();require(serial_reports==8&&ordinary_reports==0,"recovery loop remains responsive without gameplay");}if(cold_boot)require(matrix_samples==0&&reboots==0&&bootloader==0,"Boot B bypasses physical resampling/MB1 and never reboots");else require(reboots==0&&cold_prepares==0&&cold_starts==0&&watchdog.scratch[2]==0,"automatic recovery does not authorize cold reboot");}
 require(persistence.saves==0&&store_begins==0&&normal_initializations==0&&backends==nullptr,"recovery and MB1 do not write or initialize gameplay");delete recovery_configurator;
 std::cout<<"actual_setup_route_"<<argv[1]<<"=PASS\n";return 0;}catch(const FirmwareReboot &){std::cerr<<"unexpected cold watchdog reboot"<<'\n';return 1;}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
