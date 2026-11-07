// This probe executes exact extracted production startup with actual linked
// Persistence/ProfileStore/classifier/NOR. GPIO, display and backend init are
// bounded stubs; no target timing, I2C, USB or physical boot claim follows.
#include "core/RecoveryInitialization.hpp"
#include "core/PackageOwnership.hpp"
namespace boot_probe {
Config config = Config_init_default;
InputState inputs{};
InputSource **input_sources=nullptr;
size_t input_source_count=0;
ConfiguratorBackend *recovery_configurator=nullptr;
enum class BootOutcome {Pending,Normal,StoredConfigRejected,StorageFailure,
    DefaultsRejected,StartupConfigRejected,RecoveryConfigurator};
struct BootSnapshot {BootOutcome outcome=BootOutcome::Pending;bool display_ready=false;} state;
unsigned publications=0,backend_initializations=0;
bool splash=true,recovery_visible=false;
void publish_boot_state(BootOutcome outcome,bool ready) {
    test::need(state.outcome==BootOutcome::Pending,"exactly one terminal publication");
    state={outcome,ready};++publications;
}
bool PrepareBootDisplay(){return true;}
bool InitializeBootBackends(){++backend_initializations;return true;}
#include "extracted_boot.inc"
int run(const char *defaults) {
    const auto raw=test::input(defaults);
    auto stream=pb_istream_from_buffer(raw.data(),raw.size());
    test::need(pb_decode(&stream,Config_fields,&config),"source-valid startup default fixture");
    const auto before=test::nor;const auto programs=test::programs,erases=test::erases;
    setup();
    test::need(state.outcome!=BootOutcome::Pending&&publications==1,"finite terminal startup");
    test::need(test::nor==before&&test::programs==programs&&test::erases==erases,"startup fixture has zero persistent mutation");
    test::no_handles();
    std::ofstream out(test::path("boot.json"));
    out<<"{\"outcome\":"<<unsigned(state.outcome)<<",\"display_ready\":"<<state.display_ready
       <<",\"splash\":"<<splash<<",\"recovery_visible\":"<<recovery_visible
       <<",\"backend_initializations\":"<<backend_initializations<<",\"unchanged\":true}\n";
    delete recovery_configurator;recovery_configurator=nullptr;
    test::shutdown();return 0;
}
}
