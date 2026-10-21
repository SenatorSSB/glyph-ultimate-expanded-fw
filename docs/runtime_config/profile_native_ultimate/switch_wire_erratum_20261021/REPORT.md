# Exact F Switch axis wire erratum

The frozen F artifact deterministically stores **0 for −14.5 and 14 for 270.5** in the affected axis byte on the supported official RP2040 B0/B1/B2 paths. This closes the eleven selected Switch expectations at the machine-code level. It is not portable C++ behavior, a source repair, target observation, or hardware acceptance. The immutable prior packet and oracle remain unchanged.

F is `334fbd06e4541c120b0db423e5be7e112eb1f6f6`; ELF SHA-256 `a42bd2bf6ab1efd3cac565b27d9e236c0128da3be84a5977e5c739db2697c15d` (5,597,092 bytes). The ELF was independently rehashed. The backend source/header match exact F Git objects. Current worktree/canonical state is not substituted for F.

## Emitted instructions and values

`NintendoSwitchBackend::SendReport` is at `0x1001b924`. Raw axes are loaded with `LDRB`, then integer `SUBS #128`. These are signed inputs −128 through 127 to `__wrap___aeabi_i2d` at `0x100433dc`. That wrapper takes the absolute value, calls the ROM L3/CLZ function through `sf_clz_func` at `0x200303e4`, and constructs the binary64 mantissa, biased exponent and saved sign directly with shifts/ORs; zero has its explicit zero path. `correspond.py` verifies the actual L3 lookup entries and CLZ table paths in all three official ROM ELFs for magnitudes1..128, then replays F's bit-construction equations for both signs. These produce exact binary64 integer values. The SD-table int conversion entries listed below are verified provenance but are not the target of this i2d wrapper.

The actual code uses binary64, not binary32. Each axis calls `dmul` (`0x100432ea`) with low word 0/high word `0x3ff40000` (1.25), then `dadd` (`0x1004329c`) with low word 0/high word `0x40600000` (128). Y additionally calls `dsub` (`0x1004328a`) with first operand low word 0/high word `0x406fe000` (255). These constants were read from actual ELF addresses `0x1001bab4/bab8/babc`, not reconstructed from source alone. The resulting exact values are:

- X: `(5*x − 128)/4`, range −32 through 286.75.
- Y: `(1148 − 5*y)/4`, range −31.75 through 287.

Every integer conversion input, product, sum and subtraction is an integer or quarter integer with at most eleven significant binary digits, far below binary64's 53-bit significand. None is subnormal, infinite or NaN. The pinned `dmul` code accumulates the full mantissa product in four limbs, normalizes and packs with rounding/sticky bits; here all discarded product bits are zero. The pinned add/sub code unpacks signed mantissas, aligns them, adds, normalizes and packs with rounding/sticky bits; the exact quarter-grid sums retain all significant bits. Thus their rounding machinery cannot change these exact results. Integer-to-double is exact for these eight-bit magnitudes. This is a finite arithmetic argument for the actual inputs, not a claim that all ROM math operations always give mathematically exact results.

Conversion calls at `0x1001b9d6`, `0x1001ba02`, `0x1001ba22`, `0x1001ba4e` target `__wrap___aeabi_d2uiz` at `0x10043454`. The wrapper loads table `0x200302ac`, offset 36, and tail-dispatches. Each result is then stored by **STRB r0**, respectively at `0x1001b9dc`, `0x1001ba08`, `0x1001ba28`, `0x1001ba58`. STRB stores the low eight bits of r0; no later axis clamp or replacement intervenes before the report send. The actual backend object retains the same helper relocations and store instructions; its disassembly is retained separately.

## Actual dispatch and conversion semantics

Preinitializer `__aeabi_double_init` at `0x100434f4` reads ROM version byte address 19. For B0/version1 it initializes the table with `double_table_shim_on_use_helper`; the wrapper's embedded offset36/shim pointer is `0x100439f1`. The shim helper resolves and caches that Thumb target without modifying the double arguments. The actual F `double2uint_shim` at `0x100439f0` sets r2=0, adds32, calls `double2ufix64_shim` at `0x10043a1a`, then moves r1 to r0. The signed-high-word test `ASRS r3,r1,#20; BMI` branches to `ret_dzero` (`0x10043a34`), explicitly returning both words zero for negative values. Positive finite values enter `dunpacks`/`d2fix_a`, shifting the exact mantissa to a 32-fraction-bit value; returning its high word yields floor(value). Thus positive270.5 returns r0=270, and negative−14.5 returns r0=0.

For B1/version2 and B2/version3, initialization copies the official ROM SD table. Actual official ELF table contents were independently read (not inferred from function names):

| ROM | SD table | add | sub | multiply | uint conversion at offset36 | int conversion at offset44 |
|---|---:|---:|---:|---:|---:|---:|
| B1 | 0x228 | 0x2e61 | 0x2e55 | 0x2fbd | 0x3573 | 0x36c3 |
| B2 | 0x24c | 0x2e3d | 0x2e31 | 0x2f99 | 0x354f | 0x369f |

Pointers include the Thumb bit. Both unsigned conversion bodies have the same explicit negative→zero test and positive mantissa-shift behavior as F's B0 shim. Fresh official-ELF disassembly exactly matches the retained pinned disassembly. ROM revision is **NOT_OBSERVED**; this result covers the published official B0 shim/B1/B2 alternatives and makes no claim about arbitrary modified or unknown ROM implementations.

`analyze.py` contains a bounded Python replay of the actual disassembled conversion-path instruction subset, including NZCV, stack, calls/returns, shifts, literal/indirect target loads, and integer operations. It is analysis of instructions, not ARM/device execution. It uses packed exact binary64 inputs for both orientations of every uint8 value, follows actual instruction addresses, retains each trace, and checks all **1,536 conversions** (256 inputs × 2 orientations × 3 dispatch implementations) against the independently derived finite equations. No compilation or firmware emulation was performed. Arithmetic helpers are justified by the exact-operand/full-mantissa argument above; the replay is specifically the conversion path and does not pretend to execute those helpers.

Consequently the exact F axis bytes over this finite domain are:

`Xbyte = max(0, floor((5*x−128)/4)) & 255`

`Ybyte = max(0, floor((1148−5*y)/4)) & 255`

This deliberately describes the two actual machine steps. It is not a blanket source-level wrap or clamp rule. In particular −14.5 does **not** become242.

## All334 selected rows

`selected334.json` preserves every old host field and adds exact F wire fields, native input values, rational preconversion values and returned uint32 values. All1,336 axis assignments were checked. Exactly11 axes in11 rows differ; all other1,325 axis assignments agree. `changed11.json` provides the small derivative. Other fields are copied unchanged from the original packet; this investigation changes only axis conversion expectations and is not a renewed proof of native evaluation, buttons, hat, routing or physical observations.

| Rows | Old host lx | Actual returned uint32 | Exact F stored lx byte |
|---|---:|---:|---:|
| O073,O077,O078,O266,N013,N017,N106,N125 | −14 | 0 | 0 |
| O074,O079,O080 | 270 | 270 | 14 |

The selected rows have no additional negative/out-of-range axis assignments. The broader256-input domain includes both X and Y negative and above255 values, so those paths were not silently omitted.

## Portability, provenance and limits

C++ [conv.fpint] discards the fractional part and leaves behavior undefined if the truncated value is not representable in the destination integer type. Here destination fields are uint8_t, so the eleven original −14/270 source-host expectations cannot be defended as portable uint8_t assignments. See the [C++ working draft, floating-integral conversions](https://eel.is/c++draft/conv.fpint). Exact emitted helper dispatch followed by STRB supplies an artifact-specific byte result despite that source-level portability defect; a rebuilt artifact/compiler must be reassessed rather than inheriting this result.

Official ROM source/image custody and URLs are retained in `/private/tmp/glyph-native-irq-rom-upper-proof-20261021-manifest.json`; B1/B2 official release assets are `https://github.com/raspberrypi/pico-bootrom-rp2040/releases/download/b1/b1.elf` and `https://github.com/raspberrypi/pico-bootrom-rp2040/releases/download/b2/b2.elf`. Local ROM sources carry Mark Owen copyright and the Raspberry Pi RP2040-use license (and stated alternate GPLv2 availability); SDK wrappers carry BSD-3-Clause headers. These original copyright/license headers remain in the pinned source files. No source or binary copies were stripped of their headers or relicensed.

`PINS.json` pins inputs and outputs; `correspondence.json` records literal/table verification. Old oracle/review facts, canonical files, F, SDK, build output, device state and limits are unchanged. No firmware build, compilation, library installation, hardware action or acceptance claim occurred. Runtime model/effort remains UNKNOWN.
