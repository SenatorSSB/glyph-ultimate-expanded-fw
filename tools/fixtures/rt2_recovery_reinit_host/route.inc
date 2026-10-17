// Application dependencies are boundary stubs; route body is extracted unchanged.
namespace RecoveryStartupDiagnostics{enum class Phase{RouteEntry,InspectionEntered,InspectionReturned,SerialBeginEntered,SerialBeginReturned,BackendNewEntered,BackendNewReturned,ReadOnlyInstalled,Published};void Mark(Phase){}void HandOffIndicator(){events.push_back("handoff");}}
namespace RecoveryUsbDiagnostics{enum class BootStage{Rt2Route,Published};void BeginRecovery(){}void Stage(BootStage){}}
struct Watchdog{uint32_t scratch[8];};static Watchdog watchdog;static Watchdog*watchdog_hw=&watchdog;
struct RecoveryInitialization{bool config_invalid=false,storage_available=true;};
static int persistence,profile_store,config,inputs,input_sources,input_source_count;
static int&ConfigWriteCandidate(){return config;}
static bool validate_glyph_config(int){return true;}
static RecoveryInitialization initialize_recovery(int,int,int,int,bool(*)(int)){return {};}
struct SerialType{void begin(int){events.push_back("serial");}};static SerialType Serial;
struct ConfiguratorBackend{template<class...T>ConfiguratorBackend(T...){events.push_back("backend");}void SetRecoveryState(bool,bool){readonly_backend=true;events.push_back("readonly");}};
static ConfiguratorBackend*recovery_configurator=nullptr;
enum class BootOutcome{Pending,RecoveryConfigurator,RecoveryTransportFailure};static BootOutcome outcome;
static void publish_boot_state(BootOutcome o,bool){outcome=o;events.push_back("publish");}
#define ARDUINO_ARCH_RP2040 1
#define GLYPH_STRICT_HARDENING_CANDIDATE 1
#include "application_route.inc"
