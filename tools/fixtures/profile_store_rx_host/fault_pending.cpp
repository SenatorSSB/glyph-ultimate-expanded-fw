#include <cassert>
#include "core/ProfileStoreFaultControls.hpp"
namespace CheckedStorage {
static FaultHook installed = nullptr;
void SetFaultHook(FaultHook hook) { installed = hook; }
}
int main() {
    using namespace ProfileStoreFaultControls;
    using namespace CheckedStorage;
    assert(Arm(1, 2, 1, 1, 1, 0, false));
    assert(Current().pending && !Current().armed && Current().ticket == 1);
    assert(installed == nullptr);
    // Even explicit direct hook calls remain inert while only pending.
    for (unsigned i = 0; i != 10000; ++i)
        assert(Hook(Kind::Record, Operation::OpenWrite, Phase::Before,
                    "ultimate-00000016.rec") == Fault::None);
    assert(!Current().triggered && Current().pending && !Current().armed);
    assert(!BeginMutation(2) && installed == nullptr);
    assert(BeginMutation(1) && installed != nullptr);
    assert(!Current().pending && Current().armed);
    assert(installed(Kind::Record, Operation::OpenWrite, Phase::Before,
                     "ultimate-00000016.rec") == Fault::Fail);
    assert(Current().triggered && !Current().armed);
    EndMutation();
    assert(installed == nullptr);
}
