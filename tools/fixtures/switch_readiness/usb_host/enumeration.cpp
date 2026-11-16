#include "comms/NintendoSwitchBackend.hpp"
#include "TUCompositeHID.hpp"
#include "arduino/Adafruit_TinyUSB_API.h"
#include "device/dcd.h"

#include <array>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

namespace {
bool attached = false;
std::vector<uint8_t> ep0_reply;
std::vector<uint8_t> last_input;
std::vector<uint8_t> opened;

// The host chooses which requests to issue. All setup packets, endpoint claims,
// HID/CDC class opens and report submissions below traverse the pinned USBD.
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

void check_configuration(bool expect_hid) {
    request(0x80, TUSB_REQ_GET_DESCRIPTOR, TUSB_DESC_CONFIGURATION << 8, 128);
    assert(ep0_reply.size() == (expect_hid ? 100 : 75));
    assert(ep0_reply[2] == ep0_reply.size() && ep0_reply[4] == (expect_hid ? 3 : 2));
    if (expect_hid) {
        const std::array<uint8_t, 7> endpoint{7, TUSB_DESC_ENDPOINT, 0x83, TUSB_XFER_INTERRUPT, 64, 0, 1};
        assert(ep0_reply[91] == 86 && ep0_reply[92] == 0);
        assert(ep0_reply[75 + 2] == 2 && ep0_reply[75 + 4] == 1 && ep0_reply[75 + 5] == TUSB_CLASS_HID);
        assert(std::memcmp(ep0_reply.data() + 93, endpoint.data(), endpoint.size()) == 0);
    }
}

void set_configuration() {
    request(0, TUSB_REQ_SET_CONFIGURATION, 1, 0);
    assert(tud_mounted());
}

class NeutralPad : public NintendoSwitchBackend {
    using NintendoSwitchBackend::NintendoSwitchBackend;
    void UpdateOutputs() override {
        _outputs = {};
        _outputs.leftStickX = _outputs.leftStickY = _outputs.rightStickX = _outputs.rightStickY = 128;
        _outputs.a = true;
    }
};
}

// Hardware boundary. RP2040 pull-up changes do not themselves parse configuration
// or open endpoints. The test host must issue its own reset and control requests.
void TinyUSB_Port_InitDevice(uint8_t port) { assert(tud_init(port)); }
uint8_t TinyUSB_Port_GetSerialNumber(uint8_t[16]) { return 0; }
void TinyUSB_Port_EnterDFU() { assert(false); }
void yield() {}
void dcd_init(uint8_t port) { dcd_connect(port); }
void dcd_connect(uint8_t) { attached = true; }
void dcd_disconnect(uint8_t) { attached = false; }
void dcd_int_enable(uint8_t) {}
void dcd_int_disable(uint8_t) {}
void dcd_remote_wakeup(uint8_t) {}
void dcd_sof_enable(uint8_t, bool) {}
void dcd_set_address(uint8_t, uint8_t) {}
void dcd_edpt_close_all(uint8_t) { opened.clear(); }
void dcd_edpt_stall(uint8_t, uint8_t) { assert(false); }
void dcd_edpt_clear_stall(uint8_t, uint8_t) {}
bool dcd_edpt_open(uint8_t, const tusb_desc_endpoint_t *ep) {
    opened.push_back(ep->bEndpointAddress);
    return true;
}
bool dcd_edpt_xfer(uint8_t port, uint8_t ep, uint8_t *buf, uint16_t len) {
    if (ep == 0x80 && len) ep0_reply.insert(ep0_reply.end(), buf, buf + len);
    if (ep == 0x83 && len) last_input.assign(buf, buf + len);
    if (ep == 0x80 || ep == 0 || ep == 0x83)
        dcd_event_xfer_complete(port, ep, len, XFER_RESULT_SUCCESS, false);
    return true;
}

int main(int argc, char **argv) {
    assert(argc == 2);
    const bool early_configured = std::strcmp(argv[1], "early-configured") == 0;
    const bool early = early_configured || std::strcmp(argv[1], "early-descriptor-only") == 0;
    assert(TinyUSBDevice.begin());
    reset_bus();
    const std::vector<uint8_t> hori_id{0x0d, 0x0f, 0x92, 0x00};
    if (early) {
        const auto cached = device_descriptor();
        const std::array<uint8_t, 4> pico_id{0x8a, 0x2e, 0x0a, 0x00};
        assert(std::memcmp(cached.data() + 8, pico_id.data(), 4) == 0);
        check_configuration(false);
        if (early_configured) {
            set_configuration();
            assert((opened == std::vector<uint8_t>{0x81, 0x01, 0x82}));
        }
    }

    NintendoSwitchBackend::RegisterDescriptor();
    InputState inputs{};
    NeutralPad pad(inputs, nullptr, 0);
    if (early) {
        // Repeating the same SET_CONFIGURATION after registration does not reopen for
        // a configured host. An identity-only host has not even selected a config.
        if (early_configured) set_configuration();
        assert(!TUCompositeHID::_usb_hid.ready());
        pad.SendReport();
        assert(last_input.empty());
        assert(tud_disconnect() && !attached);
        assert(tud_connect() && attached);
        reset_bus();  // a co-operating host recognizes the new attachment
    }
    const auto final_device = device_descriptor();
    assert(std::memcmp(final_device.data() + 8, hori_id.data(), 4) == 0);
    check_configuration(true);
    set_configuration();
    assert((opened == std::vector<uint8_t>{0x81, 0x01, 0x82, 0x83}));
    request(0x81, TUSB_REQ_GET_DESCRIPTOR, HID_DESC_TYPE_REPORT << 8, 128, 2);
    // Exact descriptor from the physically tested GOPT binary.
    constexpr char descriptor[] = "05010905a101150025013500450175019510050919012910810205012507463b01"
                                  "7504950165140939814265009501810126ff0046ff000930093109320935750895"
                                  "0481020600ff0920950181020a212695089102c0";
    assert(ep0_reply.size() * 2 == sizeof(descriptor) - 1);
    for (size_t i = 0; i < ep0_reply.size(); ++i) {
        char octet[3];
        std::snprintf(octet, sizeof(octet), "%02x", ep0_reply[i]);
        assert(std::memcmp(octet, descriptor + i * 2, 2) == 0);
    }
    assert(TUCompositeHID::_usb_hid.ready());
    pad.SendReport();
    assert((last_input == std::vector<uint8_t>{4, 0, 8, 128, 127, 128, 127, 0}));
    std::printf("PASS %s: CDC+HID EP83, actual eight-byte report\n", argv[1]);
}

// Optional device/class callbacks normally weak on the RP2040 ELF toolchain.
// Define portable no-op hooks for native linkers that require definitions.
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
const uint8_t *tud_descriptor_bos_cb() { return nullptr; }
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
bool tud_vendor_control_xfer_cb(uint8_t, uint8_t, const tusb_control_request_t *) { return false; }
const usbd_class_driver_t *usbd_app_driver_get_cb(uint8_t *count) { *count = 0; return nullptr; }
