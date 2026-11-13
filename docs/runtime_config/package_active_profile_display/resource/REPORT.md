# Retained exact display ELF: bounded rendering stack impact

Built source **9e69188d857138a3884bcbe243f22188815e9355**; no rebuild.
ELF SHA-256 `30e5c15b61d4e2b1822aa521cf7e53ffbab9cfe568f63f792047069f965929ff`;
map SHA-256 `8b9bb82ec6a6a67e9ff94f241b4bb58e1254bf5ce0b7583aad55a77a034f2f00`.
Use the owner-held retained artifacts in ../VALIDATION.json, never substitute
mutable build output. Extracted ELF identity matches that custody exactly.

## Complete affected paths

| Obligation | Bytes / equation |
| --- | --- |
| Resolver including all descendants | 64 = own32 + max(EntryAt32 + MutationFenced0, Count16, other leaf0 accessors/Lease/IsOwnedView/strnlen) |
| New label path from core1 entry, including IRQ | 292 = wrapper8 + main1 8 + loop1 72 + SendReport24 + renderer48 + resolver subtree64 + IRQ68 |
| Full affected rendering branch, including reused graphics | 948 = wrapper8 + main1 8 + loop1 72 + SendReport24 + renderer subtree768 + IRQ68 |
| Existing exact-graph core1 composition replay | 1060 = outer16 + max(setup1 960, loop1 976) + IRQ68 |
| Retained conservative core1 budget / actual reservation | 1152 / 2048 |

Both dashboard and Input Viewer retain local frame48. The renderer subtree768
includes every supported graphics alternative; it is not a local compiler frame.
The complete new name resolver branch is shallower than existing graphics. Calls
and loop iterations are sequential, so sibling frames are max-composed, not summed.
Count/EntryAt loops add no recursion, allocation, storage or filesystem edge.
Map/ELF retain stack1 reservation2048. Timing and target highwater remain unmeasured.

## Qualified reuse, not a blanket historical bound

The baseline is Senscope canonical resource evidence at commit
`acf22010522ac5b2b17392e977d692195d39e154`, path
`docs/project/goal-runs/fullpkg-b2-storage-fence-repair/evidence/resources/`, for
source b34bd9bc0c19c3bbf060b9914381742727b6ed03 and ELF
`c411c86db3e68c5630b9bd93949c82762ec8521de5fa40cc91536f7faf608443`.
The prior source-bounded equations and current exact linked extraction were replayed
with the unchanged retained core1 oracle. Current setup960/loop976, no unknown
edges and no cycles. All224 prior reachable signatures were compared:222 retain
exact frame/direct-call/tail/indirect forms; the only two changed signatures are
the expected renderers. All43 specially modeled leaves retain those exact shapes.
Relevant SSD1306, IntegratedDisplay, renderer and Ultimate vtable slots retain
named target identity. The new native getters and resolver introduce no dynamic
call target family. Current objdump/nm hashes and retained extractor match baseline.

89 of90 relied lower source pins match. **Adafruit_SSD1306.cpp differs** (current
2.5.16); source equality is not claimed. Its relied linked stack/call/tail/indirect
shapes, class/header and vtable target identities match. This qualifies reuse of
its stack equations only; it transfers no hardware, timing or pixel behavior.
`lower-pin-comparison.json` retains both hashes and the exact exception.

The normal non-RTOS core1 construction, outer wrappers, fixed graphics/backend
class union, IRQ/ROM/time source predicates and no-fault alternatives remain the
baseline conditions. config.cpp and the relied SDK IRQ/ROM sources are unchanged.
SIO IRQ68 = hardware32 + MFIFO16 + max(noInterrupts16, FIFO pop8, interrupts8) +
alignment4. Each relevant veneer releases transient push4 before BX to its target;
those4 bytes are not simultaneously live with the target frame. Their exact
instructions are in retained disassembly. No arbitrary corruption/panic/unsupported
RTOS or new IRQ-family claim is added. No unresolved edge exists within these
explicit supported conditions; outside them this bounded argument supplies none.

This closes the **affected rendering call-chain** stack obligation without changing
limits or rebuilding general resource tooling. It does not renew unrelated core0,
heap, whole-image or hardware proofs. Original compiler-local-frame evidence is
retained, with this post-build proof recorded separately.

## Replay without compiling

`MANIFEST.json` binds every resource evidence file. Gzip files use deterministic
compression and include exact old/current graph inventories and current disassembly.
To replay in a fresh temporary directory, expand functions.json.gz,
vtables.json.gz and disassembly.txt.gz to their original filenames and run:

```sh
python3 retained-core1_bound.py --output-dir /private/tmp/your-display-stack-replay
```

To re-extract from retained custody, use `extract.py --elf <retained ELF>
--output-dir <fresh temporary directory> --toolchain <pinned ARM bin directory>`,
then the same retained oracle. These tools inspect linked bytes; neither compiles
nor opens a device. The map, ELF, source/dependency pins and conditional reuse are
independently reviewed in the follow-up handoff.
