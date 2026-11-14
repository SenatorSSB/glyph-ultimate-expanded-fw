#pragma once
#include "hardware/timer.h"

// Descriptor tokens are outside this host fixture. Compare the target ELF descriptor separately.
#define HID_USAGE_PAGE(...) 0
#define HID_USAGE(...) 0
#define HID_COLLECTION(...) 0
#define HID_LOGICAL_MIN(...) 0
#define HID_LOGICAL_MAX(...) 0
#define HID_PHYSICAL_MIN(...) 0
#define HID_PHYSICAL_MAX(...) 0
#define HID_REPORT_SIZE(...) 0
#define HID_REPORT_COUNT(...) 0
#define HID_USAGE_MIN(...) 0
#define HID_USAGE_MAX(...) 0
#define HID_INPUT(...) 0
#define HID_PHYSICAL_MAX_N(...) 0
#define HID_UNIT(...) 0
#define HID_LOGICAL_MAX_N(...) 0
#define HID_USAGE_PAGE_N(...) 0
#define HID_OUTPUT(...) 0
#define HID_COLLECTION_END 0

inline struct {
    void setManufacturerDescriptor(const char *) {}
    void setProductDescriptor(const char *) {}
    void setSerialDescriptor(const char *) {}
    void setID(int, int) {}
} USBDevice;
