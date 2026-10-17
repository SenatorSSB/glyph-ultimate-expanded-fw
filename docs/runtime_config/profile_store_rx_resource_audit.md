# RX repair: target resources and allocation lifetime

These are development measurements for the RX repair of failed candidate
`895109eb662a8ad6b6c99889cb37a254dce49998`, not final artifact custody or hardware
acceptance. The integration role must regenerate them from the exact committed
candidate compile database and ELF. No old candidate artifact is rebuilt or
modified by the baseline comparison.

## Reproducible target ABI probes

`tools/measure_glyph_profile_store_resources.py` now appends isolated layout
probes to copies of the actual `ConfiguratorBackend.cpp` compilation unit. It
uses the target compiler and flags from the supplied compile database. The
analysis objects never enter the firmware image. Symbol sizes from target `nm`
measure `sizeof(CoordinatedCdcStream)`, `sizeof(ConfiguratorBackend)`, and
`sizeof(ProfileStoreRxDiagnostics)`.

Use the optional `--baseline-ref 895109eb662a8ad6b6c99889cb37a254dce49998` to compile
an isolated second target object containing the frozen backend translation unit
and both frozen backend/stream headers. `git show` reads those bytes into a
private output-directory include overlay. This does not change a worktree or
invoke a firmware build. Compiler, source/header hashes, exact baseline command,
object path, sizes, and differences are recorded in the resource report.

The baseline ABI comparison shares the pinned target compiler and current common
dependencies. The backend embeds neither `ProfileStoreRequest` nor
`ProfileStoreResponse`, so their added protocol fields do not affect this frozen
backend layout measurement. It is not a frozen whole-program build or a frozen
stack measurement.

| Target object | Frozen895 bytes | RX repair bytes | Difference |
| --- | ---: | ---: | ---: |
| `CoordinatedCdcStream` | 20 | 100 | +80 |
| `ConfiguratorBackend`, including its stream | 376 | 520 | +144 |
| Each `ProfileStoreRxDiagnostics` | absent | 32 | +32 |
| `ProfileStoreRequest` | 2,304 | 2,304 | 0 |
| `ProfileStoreResponse` | 2,992 | 3,024 | +32 |
| `UltimateProfile` | 2,152 | 2,152 | 0 |

The stream growth is its 64-byte RX cache, two cache indices, three 32-bit
counters, and target alignment. The backend's total growth is that embedded
80-byte increase plus two 32-byte RX snapshots. Do not add the stream's 80 bytes
a second time to the backend's 144-byte increase.

The request/response/profile baseline sizes come from the preserved895 resource
evidence; the new frozen-overlay probe independently measures the two backend
classes only. Current `Config`, `ProfileStore`, directory, entry, and transaction
identity sizes are unchanged.

## Static RAM versus heap demand

The RX cache and snapshots are instance members. Both production construction
sites allocate `ConfiguratorBackend` using `new`; these 144 extra bytes therefore
increase the backend allocation payload on the heap. They are not a 144-byte
increase in `.bss` or on the frame-reader stack. Allocator metadata, alignment,
fragmentation, and arena highwater must not be inferred from object payload size.
No request performs a new backend allocation.

The response is a static object in `HandleProfileStore`; its new 32 bytes do
increase static RAM. Development ELF
`5b6b2df9dc59806d8668dd1b0a74df5959db5502d92a730e1f3bb7e9389db997`
contains `.data=20,420` and `.bss=166,976`, totaling 187,396 bytes under the usual
PlatformIO RAM accounting, versus 187,364 for 895: **+32 static bytes**.
The linker arena from `__end__` to `__StackLimit` is 74,552 bytes, versus 74,584.
These section numbers are provisional; final custody must use the final ELF.

Consequently a static-RAM-only report would omit the 144-byte persistent backend
heap increase. Both quantities must be disclosed. The old physical heap peak 9,048
and core0/core1 minimum-free stack measurements 1,936/3,716 describe 895 only.
They are not new-candidate measurements. The target object growth does not itself
predict the exact new heap highwater or minimum free stack.

## Normal and recovery backend lifetime

Source: `HAL/pico/src/comms/backend_init.cpp`,
`config/glyph/common/src/config.cpp`,
`config/glyph/common/include/glyph_overrides.hpp`, and
`src/core/mode_selection.cpp`.

- Normal initialization creates the primary Configurator with `new` and stores
  it through the backend array. When selecting/replacing this primary backend,
  `init_primary_backend` deletes its predecessor before constructing the new
  Configurator. USB detection can therefore construct a temporary backend and
  then replace it, but the source does not keep two Configurator objects alive
  for that replacement.
- Recovery initialization creates one `recovery_configurator`, stores its
  pointer, publishes a permanent recovery boot outcome, and returns from setup.
  The recovery loop repeatedly calls that object's `SendReport`; it does not
  recreate the object. The early recovery routes precede normal backend
  initialization.
- The post-initialization invalid-USB-default guard is also considered.
  `initialize_backends` rejects an invalid default both before selection and
  after the selector, before creating a primary backend. The remaining selected
  default callbacks do not invalidate that default index. This supports one
  persistent Configurator allocation on the current normal/recovery routes,
  rather than adding two backend deltas merely because two `new` sites exist.
- Reconnecting the host or processing another packet does not call either
  construction path. The repaired cache is persistent object state and preserves
  unread bytes across packet ownership transitions. There is no profile-sized
  receive copy added by the repair.

This is a source analysis of the selected callbacks and lifecycle, not a claim
that arbitrary future callback replacements or memory corruption preserve it.

## RX stack evidence and limits

`tools/check_glyph_profile_store_rx_stack.py` composes conservative inventories
from the target `.su` output collected by the resource tool. Current frames:
`ReadPacket=56`, each stream `available/read/peek=24`, each PacketIO
`available/read/peek=16`, `TinyUSB_Device_Task=8`, and `tud_task_ext=112` bytes.
`fillRx` and `serviceRx` are inlined into emitted methods; their local costs are
already included there. The64-byte cache is in the backend object, not an
additional 64-byte automatic frame.

Development enumerations, including the outer foreground callers:

| Enumerated C inventory | Bytes | Remaining to 4,096 |
| --- | ---: | ---: |
| Receive, bulk FIFO read, endpoint rearm | 808 | 3,288 |
| Receive plus USB task and OUT completion | 1,016 | 3,080 |
| Receive plus task/control/descriptor inventory | 1,264 | 2,832 |

These conservative sums include sequential or mutually exclusive helpers. They
are not a full callgraph upper bound. They omit SDK/ROM/libc helper internals,
`snprintf` internals on the timeout path, IRQ nesting, arbitrary indirect
callbacks, and pre-setup startup. A whole-target 4,096-byte safety certificate is
not claimed. Existing READ/encoding/storage stack checks must still pass, and
new exact-candidate physical watermarks remain required.

The RX regression independently checks no allocation occurs during the exact
frame-reader call and no retained modeled-host allocation growth across the
1,024-request sustained sequence. That supports absence of per-request cache
allocation; it does not replace target heap measurements or include every
possible backend/storage operation.
