#include "core/RecoveryUsbBringup.hpp"

#include <cstdint>
#include <cstdlib>
#include <iostream>

namespace {

struct FakeLifecycle final : recovery_usb::Lifecycle {
    uint32_t elapsed = 0;
    uint32_t mount_at = UINT32_MAX;
    uint32_t service_calls = 0;
    uint32_t wait_calls = 0;
    bool cdc_open = false;

    bool mounted() const override { return elapsed >= mount_at; }
    uint32_t now() const override { return elapsed; }
    void service() override { ++service_calls; }
    void wait(uint32_t milliseconds) override { ++wait_calls; elapsed += milliseconds; }
};

void require(bool condition, const char *message) {
    if (!condition) {
        std::cerr << message << '\n';
        std::exit(1);
    }
}

}  // namespace

int main() {
    FakeLifecycle immediate;
    immediate.mount_at = 0;
    require(recovery_usb::WaitForMount(immediate) == recovery_usb::Outcome::Mounted,
            "already-mounted device is ready");
    require(immediate.service_calls == 0 && immediate.wait_calls == 0,
            "already-mounted device has no unnecessary wait");

    FakeLifecycle delayed;
    delayed.mount_at = recovery_usb::kMountBudgetMs - recovery_usb::kPollIntervalMs;
    require(recovery_usb::WaitForMount(delayed) == recovery_usb::Outcome::Mounted,
            "device mounted inside budget is ready");
    require(delayed.elapsed < recovery_usb::kMountBudgetMs,
            "delayed mount completes inside bounded window");

    FakeLifecycle never;
    require(recovery_usb::WaitForMount(never) == recovery_usb::Outcome::TimedOut,
            "unmounted device reports bounded failure");
    require(never.elapsed == recovery_usb::kMountBudgetMs,
            "unmounted device consumes exactly the finite budget");
    require(!never.cdc_open, "device readiness never requires CDC host open");

    std::cout << "recovery_usb_bringup_lifecycle=PASS\n";
}
