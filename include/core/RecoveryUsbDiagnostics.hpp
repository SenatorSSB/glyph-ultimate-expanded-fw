#pragma once
#include <cstdint>
#include "core/RecoveryTaskDiagnostics.hpp"
#include "core/RecoverySetupIrqDiagnostics.hpp"
#include "core/RecoveryPreSetupDiagnostics.hpp"
namespace RecoveryUsbDiagnostics {
struct Snapshot {
    uint32_t milestones=0, irq_state=0, sie_ctrl=0, inte=0, ints=0, intr=0;
    uint32_t dev_addr=0, main_ctrl=0, task_entered=0, task_returned=0;
    uint32_t sie_status=0, ep0_in=0, ep0_out=0;
    uint32_t seen_sie_status=0, seen_intr=0, seen_ints=0, seen_inte=0, seen_irq=0;
    uint32_t seen_ep0_in=0, seen_ep0_out=0;
    uint32_t bus_reset_count=0, raw_setup_observations=0, setup_event_count=0;
    uint32_t reset_order=0, chip_version=0, rom_version=0, e5_flags=0, observation_valid=0, task_reset_count=0;
};
enum : uint32_t {
    RepeatedLoop=1u, PostLoopPullup=2u, BusReset=4u, Setup=8u,
    DeviceDescriptor=16u, AddressRequested=32u, AddressApplied=64u,
    ConfigurationComplete=128u, Mounted=256u, Inspection=512u,
    IrqTaskEntered=1024u, IrqTaskReturned=2048u, RawSetup=4096u
};
// Boundary is the last completed source marker, not a timestamp.
enum class BootStage : uint8_t { BeforeSetup, Setup, MatrixSampling, MatrixSampled, Rt2Route, Published };
#if defined(GLYPH_STRICT_HARDENING_CANDIDATE) && GLYPH_STRICT_HARDENING_CANDIDATE && (defined(ARDUINO_ARCH_RP2040) || defined(GLYPH_RT2_DCD_HOST))
void ObserveIndependent();
void PreSetupReadInto(RecoveryPreSetupDiagnostics::Snapshot &out);
void SetupReadInto(RecoverySetupIrqDiagnostics::Snapshot &out);
void BeginRecovery();
RecoveryTaskDiagnostics::Snapshot TaskRead();
void TaskReadInto(RecoveryTaskDiagnostics::Snapshot &out);
void Stage(BootStage stage);
void LoopEntered();
void InspectionDecoded();
Snapshot Read();
unsigned Furthest();
#else
inline void ObserveIndependent(){}
inline void PreSetupReadInto(RecoveryPreSetupDiagnostics::Snapshot &out){out={};}
inline void SetupReadInto(RecoverySetupIrqDiagnostics::Snapshot &out){out={};}
inline void BeginRecovery(){}
inline RecoveryTaskDiagnostics::Snapshot TaskRead(){return {};}
inline void TaskReadInto(RecoveryTaskDiagnostics::Snapshot &out){out={};}
inline void Stage(BootStage){}
inline void LoopEntered(){}
inline void InspectionDecoded(){}
inline Snapshot Read(){return {};}
inline unsigned Furthest(){return 0;}
#endif
}
