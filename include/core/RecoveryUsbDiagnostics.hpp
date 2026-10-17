#pragma once
#include <cstdint>
namespace RecoveryUsbDiagnostics {
struct Snapshot {
    uint32_t milestones=0, irq_state=0, sie_ctrl=0, inte=0, ints=0, intr=0;
    uint32_t dev_addr=0, main_ctrl=0, task_entered=0, task_returned=0;
};
enum : uint32_t {
    RepeatedLoop=1u, PostLoopPullup=2u, BusReset=4u, Setup=8u,
    DeviceDescriptor=16u, AddressRequested=32u, AddressApplied=64u,
    ConfigurationComplete=128u, Mounted=256u, Inspection=512u,
    IrqTaskEntered=1024u, IrqTaskReturned=2048u
};
#if defined(GLYPH_STRICT_HARDENING_CANDIDATE) && GLYPH_STRICT_HARDENING_CANDIDATE && (defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_RT2_DCD_HOST))
void LoopEntered();
void InspectionDecoded();
Snapshot Read();
unsigned Furthest();
#else
inline void LoopEntered(){}
inline void InspectionDecoded(){}
inline Snapshot Read(){return {};}
inline unsigned Furthest(){return 0;}
#endif
}
