#pragma once
#include <cstdint>
#include <cstddef>
#include <arduino/Adafruit_USBD_Device.h>
struct hid_keyboard_report_t { uint8_t modifier=0; uint8_t reserved=0; uint8_t keycode[6]{}; };
inline unsigned host_hid_reports=0,host_usb_disconnects=0;
class Adafruit_USBD_HID { public:
 Adafruit_USBD_HID() = default;
 Adafruit_USBD_HID(const uint8_t*,size_t,int,int,bool) {}
 void setReportDescriptor(const uint8_t*,size_t) {}
 bool begin() { return true; }
 bool ready() { return true; }
 bool sendReport(uint8_t,const void*,size_t) { ++host_hid_reports;return true; }
};
inline void tud_disconnect() { ++host_usb_disconnects; }
inline void tight_loop_contents() {}
inline constexpr int HID_ITF_PROTOCOL_NONE=0;
inline constexpr uint8_t HID_KEY_NONE=0;
#define TU_BIT(n) (1u<<(n))
// Host physical-descriptor seam: no wire/USB descriptor compatibility is claimed.
#define HID_COLLECTION_END 0
#define TUD_HID_REPORT_DESC_KEYBOARD(...) 0
#define HID_REPORT_ID(...) 0,
#define HID_USAGE_PAGE(...) 0
#define HID_USAGE_PAGE_N(...) 0
#define HID_USAGE(...) 0
#define HID_USAGE_MIN(...) 0
#define HID_USAGE_MAX(...) 0
#define HID_COLLECTION(...) 0
#define HID_LOGICAL_MIN(...) 0
#define HID_LOGICAL_MAX(...) 0
#define HID_LOGICAL_MAX_N(...) 0
#define HID_PHYSICAL_MIN(...) 0
#define HID_PHYSICAL_MAX(...) 0
#define HID_PHYSICAL_MAX_N(...) 0
#define HID_REPORT_COUNT(...) 0
#define HID_REPORT_SIZE(...) 0
#define HID_INPUT(...) 0
#define HID_OUTPUT(...) 0
#define HID_UNIT(...) 0

#define TU_ATTR_PACKED __attribute__((packed))
enum hid_gamepad_hat_t : uint8_t {
    GAMEPAD_HAT_CENTERED = 0,
    GAMEPAD_HAT_UP, GAMEPAD_HAT_UP_RIGHT, GAMEPAD_HAT_RIGHT,
    GAMEPAD_HAT_DOWN_RIGHT, GAMEPAD_HAT_DOWN, GAMEPAD_HAT_DOWN_LEFT,
    GAMEPAD_HAT_LEFT, GAMEPAD_HAT_UP_LEFT
};
enum : uint8_t {
    HID_KEY_A = 0x04, HID_KEY_B, HID_KEY_C, HID_KEY_D, HID_KEY_E, HID_KEY_F,
    HID_KEY_G, HID_KEY_H, HID_KEY_I, HID_KEY_J, HID_KEY_K, HID_KEY_L,
    HID_KEY_M, HID_KEY_N, HID_KEY_O, HID_KEY_P, HID_KEY_Q, HID_KEY_R,
    HID_KEY_S, HID_KEY_T, HID_KEY_U, HID_KEY_V, HID_KEY_W, HID_KEY_X,
    HID_KEY_Y, HID_KEY_Z,
    HID_KEY_1 = 0x1e, HID_KEY_2, HID_KEY_3, HID_KEY_4, HID_KEY_5,
    HID_KEY_6, HID_KEY_7, HID_KEY_8, HID_KEY_9
};
