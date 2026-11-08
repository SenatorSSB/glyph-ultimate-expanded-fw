// This probe executes exact extracted production startup with actual linked
// Persistence/ProfileStore/classifier/NOR. GPIO, display and backend init are
// bounded stubs; no target timing, I2C, USB or physical boot claim follows.
#include "core/RecoveryInitialization.hpp"
#include "core/PackageOwnership.hpp"
#include "core/BootDiagnostics.hpp"
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
bool boot_display_ready=false;
constexpr unsigned SSD1306_WHITE=1;
struct Display {
    std::string text;
    void clearDisplay(){splash=false;text.clear();}
    void setFont(const void*){} void setTextSize(unsigned){} void setTextColor(unsigned){}
    void setCursor(unsigned,unsigned){}
    void print(const char *s){text+=s;}
    void println(const char *s){text+=s;text+='\n';}
    void println(unsigned n){text+=std::to_string(n);text+='\n';}
    void display(){
        recovery_visible=text.find("Startup recovery")!=std::string::npos;
    }
}display;
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
    // Exercise actual recovery/ordinary protocol2 STATUS after production setup.
    // This also verifies that the selected prior is never restored by STATUS.
    const uint8_t status_request[]={8,2,16,1,24,1};
    packetio::COBSPrint framed(Serial);
    test::need(framed.write(uint8_t(CMD_PROFILE_STORE))==1 &&
        framed.write(status_request,sizeof(status_request))==sizeof(status_request) && framed.end(),"STATUS frame");
    Serial.input=std::move(Serial.output);Serial.output.clear();
    auto *backend=recovery_configurator;
    if(!backend)backend=new ConfiguratorBackend(inputs,nullptr,0,config,Serial);
    for(size_t guard=0;Serial.position<Serial.input.size();++guard) {
        test::need(guard<Serial.input.size()+8,"finite recovery STATUS");backend->SendReport();
    }
    test::output(test::path("status.cobs"),Serial.output);
    if(backend!=recovery_configurator)delete backend;
    test::need(test::nor==before&&test::programs==programs&&test::erases==erases,"recovery/STATUS never writes");
    test::no_handles();
    std::ofstream out(test::path("boot.json"));
    out<<"{\"outcome\":"<<unsigned(state.outcome)<<",\"display_ready\":"<<state.display_ready
       <<",\"splash\":"<<splash<<",\"recovery_visible\":"<<recovery_visible
       <<",\"backend_initializations\":"<<backend_initializations<<",\"unchanged\":true}\n";
    delete recovery_configurator;recovery_configurator=nullptr;
    test::shutdown();return 0;
}
}
