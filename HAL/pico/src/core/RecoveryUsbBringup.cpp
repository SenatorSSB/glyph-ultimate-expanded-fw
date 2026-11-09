#include "core/RecoveryUsbBringup.hpp"

namespace recovery_usb {

Outcome WaitForMount(Lifecycle &lifecycle) {
    const uint32_t started = lifecycle.now();
    do {
        if (lifecycle.mounted()) return Outcome::Mounted;
        lifecycle.service();
        if (static_cast<uint32_t>(lifecycle.now() - started) >= kMountBudgetMs) break;
        lifecycle.wait(kPollIntervalMs);
    } while (true);
    return lifecycle.mounted() ? Outcome::Mounted : Outcome::TimedOut;
}

}  // namespace recovery_usb
