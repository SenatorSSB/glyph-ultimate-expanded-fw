#pragma once

#include <cstdint>

// Candidate recovery needs a device-level USB predicate, not a CDC-DTR
// predicate.  Keep the polling policy independent from Arduino/TinyUSB so it
// is host-testable and cannot accidentally wait for a serial client to open.
namespace recovery_usb {

constexpr uint32_t kMountBudgetMs = 2000;
constexpr uint32_t kPollIntervalMs = 10;

class Lifecycle {
  public:
    virtual ~Lifecycle() = default;
    virtual bool mounted() const = 0;
    virtual uint32_t now() const = 0;
    virtual void service() = 0;
    virtual void wait(uint32_t milliseconds) = 0;
};

enum class Outcome : uint8_t { Mounted, TimedOut };

Outcome WaitForMount(Lifecycle &lifecycle);

}  // namespace recovery_usb
