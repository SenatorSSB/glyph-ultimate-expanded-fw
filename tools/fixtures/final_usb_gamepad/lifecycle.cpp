// Production USB constructors, backend-selection bodies and boot finalization.
// Console wires, storage, mode binding and menu/recovery rendering are boundaries.
#include "comms/NintendoSwitchBackend.hpp"
#include "comms/XInputBackend.hpp"
#include "comms/DInputBackend.hpp"
#include "comms/backend_init.hpp"
#include "core/config_utils.hpp"
#include "core/config_usb_default_validation.hpp"
#include "final_usb_gamepad.hpp"
#include "TUCompositeHID.hpp"
#include "TUGamepad.hpp"
#include "TUKeyboard.hpp"
#include "arduino/Adafruit_TinyUSB_API.h"
#include "device/dcd.h"
#include <array>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace TUCompositeHID { extern size_t _current_descriptor_len; extern uint8_t _hid_report_desc[]; }
namespace {
bool attached = false;
unsigned connects = 0, disconnects = 0, delays = 0, recoveries = 0, detections = 0;
std::vector<uint8_t> ep0_reply, opened;
CommunicationBackendId selected, detected;
bool provisional;
void reset_bus() {
    assert(attached);
    opened.clear();
    dcd_event_bus_reset(0, TUSB_SPEED_FULL, false);
    tud_task();
}
void request(uint8_t type, uint8_t code, uint16_t value, uint16_t count, uint16_t index = 0) {
    const tusb_control_request_t setup{.bmRequestType = type, .bRequest = code, .wValue = value,
                                       .wIndex = index, .wLength = count};
    ep0_reply.clear();
    dcd_event_setup_received(0, reinterpret_cast<const uint8_t *>(&setup), false);
    tud_task();
}
std::vector<uint8_t> device_descriptor() {
    request(0x80, TUSB_REQ_GET_DESCRIPTOR, TUSB_DESC_DEVICE << 8, 18);
    assert(ep0_reply.size() == 18);
    return ep0_reply;
}
void set_configuration() {
    request(0, TUSB_REQ_SET_CONFIGURATION, 1, 0);
    assert(tud_mounted());
}
}
// Non-USB backend constructors intentionally carry identity only. Their report
// protocols are separately covered by unchanged repository fixtures.
struct ConsoleDouble : CommunicationBackend {
    CommunicationBackendId id;
    template<class... T> ConsoleDouble(CommunicationBackendId value, InputState &s, InputSource **p, size_t n, T&&...)
        : CommunicationBackend(s,p,n), id(value) {}
    CommunicationBackendId BackendId() override { return id; }
    void SendReport() override {}
};
#define CONSOLE_DOUBLE(Name, Id) struct Name : ConsoleDouble { \
    template<class... T> Name(InputState &s, InputSource **p, size_t n, T&&... a) \
        : ConsoleDouble(Id,s,p,n,a...) {} };
CONSOLE_DOUBLE(GamecubeBackend, COMMS_BACKEND_GAMECUBE)
CONSOLE_DOUBLE(N64Backend, COMMS_BACKEND_N64)
CONSOLE_DOUBLE(NesBackend, COMMS_BACKEND_NES)
CONSOLE_DOUBLE(SnesBackend, COMMS_BACKEND_SNES)
CONSOLE_DOUBLE(ConfiguratorBackend, COMMS_BACKEND_CONFIGURATOR)
CONSOLE_DOUBLE(B0XXInputViewer, COMMS_BACKEND_UNSPECIFIED)
struct { uint32_t scratch[8]{}; } watchdog_state;
auto *watchdog_hw = &watchdog_state;
bool watchdog_caused_reboot() { return false; }
bool consume_committed_mode_destination(volatile uint32_t *, bool, const Config &, CommunicationBackendConfig &) { return false; }
struct { void SaveConfig(const Config &) { assert(false); } } persistence;
CommunicationBackendConfig backend_config_from_buttons(const InputState &, const CommunicationBackendConfig *, size_t) {
    CommunicationBackendConfig c{}; c.backend_id = provisional ? COMMS_BACKEND_UNSPECIFIED : selected; return c;
}
CommunicationBackendConfig backend_config_from_id(CommunicationBackendId id, const CommunicationBackendConfig *configs, size_t n) {
    for (size_t i=0; i<n; ++i) if (configs[i].backend_id == id) return configs[i];
    return CommunicationBackendConfig_init_zero;
}
CommunicationBackendId detect_console(const Pinout &) {
    ++detections;
    assert(disconnects == 0 && delays == 0); // provisional construction cannot finalize USB
    return detected;
}
CommunicationBackendId detect_console_at_boot(const Pinout &p) { return detect_console(p); }
void set_mode(CommunicationBackend *, GameModeConfig &, Config &) {}
#include "backend_selection.inc"

Config config{};
InputState inputs{};
InputSource **input_sources = nullptr;
size_t input_source_count = 0, backend_count = 0;
CommunicationBackend **backends = nullptr;
Pinout pinout{};
bool failed_detection = false;
namespace native_metrics { void Calibrate() {} }
void enter_recovery_configurator() { ++recoveries; }
void request_mode_destination(CommunicationBackendId, size_t, const Config &) {}
void set_mode_destination_selector(void (*)(CommunicationBackendId, size_t, const Config &)) {}
void setup_mode_activation_bindings(const GameModeConfig *, size_t, uint64_t) {}
size_t init_secondary_backends_glyph(CommunicationBackend **&b, CommunicationBackend *&p, CommunicationBackendId id,
    InputState &s, InputSource **i, size_t n, Config &c, const Pinout &pins) {
    return init_secondary_backends(b,p,id,s,i,n,c,pins);
}
#include "boot_finalization.inc"

void TinyUSB_Port_InitDevice(uint8_t port) { assert(tud_init(port)); }
uint8_t TinyUSB_Port_GetSerialNumber(uint8_t[16]) { return 0; }
void TinyUSB_Port_EnterDFU() { assert(false); }
void yield() {}
void delay(unsigned long ms) { assert(!attached && ms == 10); ++delays; }
void dcd_init(uint8_t port) { dcd_connect(port); }
void dcd_connect(uint8_t) { attached = true; ++connects; }
void dcd_disconnect(uint8_t) {
    assert(attached && backends && !failed_detection);
    const auto final_id=backends[0]->BackendId();
    // The publication must occur after constructors registered final descriptors,
    // but before a host has reset/opened their new class endpoints.
    const auto *device=reinterpret_cast<const tusb_desc_device_t *>(tud_descriptor_device_cb());
    const auto *configuration=tud_descriptor_configuration_cb(0);
    assert(configuration[4]==3);
    if (final_id==COMMS_BACKEND_XINPUT) {
        assert(device->idVendor==0x0738 && device->idProduct==0x4726);
        assert(!tud_xinput_ready());
    } else {
        assert(final_id==COMMS_BACKEND_DINPUT || final_id==COMMS_BACKEND_NINTENDO_SWITCH);
        assert(TUCompositeHID::_current_descriptor_len>0 && !TUCompositeHID::_usb_hid.ready());
        if(final_id==COMMS_BACKEND_NINTENDO_SWITCH)
            assert(device->idVendor==0x0f0d && device->idProduct==0x0092);
    }
    attached = false; ++disconnects;
}
void dcd_int_enable(uint8_t) {}
void dcd_int_disable(uint8_t) {}
void dcd_remote_wakeup(uint8_t) {}
void dcd_sof_enable(uint8_t, bool) {}
void dcd_set_address(uint8_t, uint8_t) {}
void dcd_edpt_close_all(uint8_t) { opened.clear(); }
void dcd_edpt_stall(uint8_t, uint8_t) { assert(false); }
void dcd_edpt_clear_stall(uint8_t, uint8_t) {}
bool dcd_edpt_open(uint8_t, const tusb_desc_endpoint_t *ep) { opened.push_back(ep->bEndpointAddress); return true; }
bool dcd_edpt_xfer(uint8_t port, uint8_t ep, uint8_t *buf, uint16_t len) {
    if (ep == 0x80 && len) ep0_reply.insert(ep0_reply.end(), buf, buf + len);
    if (ep == 0x80 || ep == 0)
        dcd_event_xfer_complete(port, ep, len, XFER_RESULT_SUCCESS, false);
    return true;
}

int main(int argc, char **argv) {
    assert(argc == 5);
    // Closed protocol classification includes future/unknown IDs fail-closed.
    for (unsigned id=0;id<=255;++id) {
        const auto backend=static_cast<CommunicationBackendId>(id);
        const bool expected=backend==COMMS_BACKEND_XINPUT || backend==COMMS_BACKEND_DINPUT || backend==COMMS_BACKEND_NINTENDO_SWITCH;
        assert(requires_final_usb_gamepad_reenumeration(backend)==expected);
    }
    selected = static_cast<CommunicationBackendId>(std::atoi(argv[1]));
    provisional = std::atoi(argv[2]);
    detected = static_cast<CommunicationBackendId>(std::atoi(argv[3]));
    const bool invalid = std::atoi(argv[4]);
    // Arduino-Pico attaches CDC before setup or any backend construction.
    assert(TinyUSBDevice.begin());
    reset_bus();
    const auto cached = device_descriptor();
    const std::array<uint8_t, 4> pico{0x8a,0x2e,0x0a,0x00};
    assert(std::memcmp(cached.data()+8,pico.data(),4)==0);
    request(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_CONFIGURATION<<8,255);
    assert(ep0_reply.size()==75 && ep0_reply[4]==2);
    set_configuration();
    assert((opened == std::vector<uint8_t>{0x81,0x01,0x82}));
    connects = disconnects = delays = 0;
    const CommunicationBackendId ids[] = {COMMS_BACKEND_XINPUT,COMMS_BACKEND_DINPUT,COMMS_BACKEND_NINTENDO_SWITCH,
        COMMS_BACKEND_CONFIGURATOR,COMMS_BACKEND_GAMECUBE,COMMS_BACKEND_N64,COMMS_BACKEND_NES,COMMS_BACKEND_SNES};
    config.communication_backend_configs_count = 8;
    config.default_usb_backend_config = invalid ? 9 : 1;
    for (size_t i=0; i<8; ++i) config.communication_backend_configs[i].backend_id=ids[i];
    // For a USB detection path, selected denotes the saved default USB backend.
    if (provisional && !invalid) {
        for (size_t i=0;i<8;++i) if (ids[i]==selected) config.default_usb_backend_config=i+1;
    }
    const bool ok = InitializeBootBackends();
    if (invalid) {
        assert(!ok && recoveries==1 && detections==0 && disconnects==0 && connects==0 && delays==0);
        std::puts("PASS invalid startup: recovery boundary, no normal USB reconnect"); return 0;
    }
    assert(ok && recoveries==0);
    if (provisional && detected==COMMS_BACKEND_UNSPECIFIED) {
        assert(failed_detection && disconnects==0 && connects==0 && delays==0);
        std::puts("PASS failed detection: no normal USB reconnect"); return 0;
    }
    const auto final_id=backends[0]->BackendId();
    const bool usb_gamepad = final_id==COMMS_BACKEND_XINPUT || final_id==COMMS_BACKEND_DINPUT || final_id==COMMS_BACKEND_NINTENDO_SWITCH;
    assert(disconnects==unsigned(usb_gamepad) && connects==unsigned(usb_gamepad) && delays==unsigned(usb_gamepad));
    assert(final_id == (provisional && detected>=COMMS_BACKEND_GAMECUBE && detected<=COMMS_BACKEND_SNES ? detected : selected));
    if (!usb_gamepad) {
        std::printf("PASS backend %u provisional=%u: no final USB gamepad reconnect\n",unsigned(final_id),unsigned(provisional));
        return 0;
    }
    // Co-operating host observes changed pull-up and enumerates from scratch.
    reset_bus();
    const auto final_device=device_descriptor();
    if (final_id==COMMS_BACKEND_XINPUT) {
        const std::array<uint8_t,4> id{0x38,0x07,0x26,0x47};
        assert(std::memcmp(final_device.data()+8,id.data(),4)==0);
    } else if (final_id==COMMS_BACKEND_NINTENDO_SWITCH) {
        const std::array<uint8_t,4> id{0x0d,0x0f,0x92,0x00};
        assert(std::memcmp(final_device.data()+8,id.data(),4)==0);
    }
    request(0x80,TUSB_REQ_GET_DESCRIPTOR,TUSB_DESC_CONFIGURATION<<8,255);
    const auto configuration=ep0_reply;
    assert(configuration.size()>75 && configuration[4]==3);
    set_configuration();
    if (final_id==COMMS_BACKEND_XINPUT) {
        // XInput is first after Serial.end resets the configuration; CDC follows.
        assert(configuration[9+5]==TUSB_CLASS_VENDOR_SPECIFIC && configuration[9+6]==0x5d);
        assert(tud_xinput_ready());
    } else {
        assert(configuration[75+5]==TUSB_CLASS_HID);
        assert(TUCompositeHID::_usb_hid.ready());
        request(0x81,TUSB_REQ_GET_DESCRIPTOR,HID_DESC_TYPE_REPORT<<8,1024,2);
        assert(ep0_reply.size()==TUCompositeHID::_current_descriptor_len);
        assert(std::memcmp(ep0_reply.data(),TUCompositeHID::_hid_report_desc,ep0_reply.size())==0);
        if (final_id==COMMS_BACKEND_DINPUT) {
            // Both Gamepad(usage05/reportID1) and Keyboard(usage06/reportID2)
            // descriptors, not merely any HID endpoint.
            const uint8_t gamepad[]{0x05,0x01,0x09,0x05,0xa1,0x01,0x85,0x01};
            const uint8_t keyboard[]{0x05,0x01,0x09,0x06,0xa1,0x01,0x85,0x02};
            assert(ep0_reply.size()>sizeof(gamepad)+sizeof(keyboard));
            assert(std::memcmp(ep0_reply.data(),gamepad,sizeof(gamepad))==0);
            bool found=false;
            for(size_t i=0;i+sizeof(keyboard)<=ep0_reply.size();++i)
                if(!std::memcmp(ep0_reply.data()+i,keyboard,sizeof(keyboard)))found=true;
            assert(found);
        }
    }
    std::printf("PASS backend %u: early CDC -> final identity/interface -> exactly one 10ms reconnect\n",unsigned(final_id));
}
// Optional weak target callbacks: portable native linker definitions.
#include "device/usbd_pvt.h"
void dcd_edpt0_status_complete(uint8_t, const tusb_control_request_t *) {}
void dcd_edpt_close(uint8_t, uint8_t) {}
bool dcd_edpt_iso_activate(uint8_t, const tusb_desc_endpoint_t *) { return false; }
bool dcd_edpt_iso_alloc(uint8_t, uint8_t, uint16_t) { return false; }
bool dcd_edpt_xfer_fifo(uint8_t, uint8_t, tu_fifo_t *, uint16_t) { return false; }
void tud_cdc_line_coding_cb(uint8_t, const cdc_line_coding_t *) {}
void tud_cdc_rx_cb(uint8_t) {}
void tud_cdc_rx_wanted_cb(uint8_t, char) {}
void tud_cdc_send_break_cb(uint8_t, uint16_t) {}
void tud_cdc_tx_complete_cb(uint8_t) {}
const uint8_t *tud_descriptor_device_qualifier_cb() { return nullptr; }
const uint8_t *tud_descriptor_other_speed_configuration_cb(uint8_t) { return nullptr; }
void tud_event_hook_cb(uint8_t, uint32_t, bool) {}
void tud_hid_report_complete_cb(uint8_t, const uint8_t *, uint16_t) {}
bool tud_hid_set_idle_cb(uint8_t, uint8_t) { return true; }
void tud_hid_set_protocol_cb(uint8_t, uint8_t) {}
void tud_mount_cb() {}
void tud_resume_cb() {}
void tud_suspend_cb(bool) {}
void tud_umount_cb() {}
