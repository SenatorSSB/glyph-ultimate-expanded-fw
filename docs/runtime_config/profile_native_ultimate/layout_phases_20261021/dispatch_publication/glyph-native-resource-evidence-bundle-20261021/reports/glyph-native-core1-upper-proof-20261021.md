# Exact bcb9824b core1 stack upper proof, 2026-10-21

**The ordinary source-owned core1 application graph is bounded by 1,152 bytes, including the larger actual core1 IRQ allowance and conservative rounding, within the unchanged 2,048-byte reservation.** The extracted graph gives1,036;1,152 is the retained upper allowance, not a measured peak. This closes the concrete core1 graph left open in section6 of the earlier IRQ/ROM assessment. The earlier partial report remains historical and is not rewritten as whole-firmware PASS. Whole core0/foreground/resource disposition remains the independent source review's responsibility.

Exact ELF: bcb9824bc00c6210babdf00675952deeda7f7c88, SHA-256 `3f43081cec177763abf9f1955f8a3686faa39fa4ca660a5de174a2d70ca62884`. All bounds here apply to this linked firmware, the pinned compile inputs, official B0/B1/B2 ROM images, and ordinary valid internal state. No narrower filesystem admission, arbitrary callback implementation, arbitrary corruption support, resource-cap change, SDK/IRQ change or target observation is introduced. Source label08bdf is production-identical attribution supplied by parent; a future build needs its own exact ELF/source correspondence. Requested model/effort gpt-6.1-sol/high; observed runtime model/effort UNKNOWN.

## Method and retained evidence

`glyph-native-core1-symbol-extents.txt` is pinned ARM nm -S -n -C output from that ELF. `glyph-native-core1-extract.py` uses exact symbol address and byte size, including nested C++ template names, to extract instructions. It never uses the former angle-bracket-header parser as a template extent oracle. The two emitted CPixel show/showColor functions each have size0x462 and allocation inventory128; Clockless showPixels has size0x33c and inventory88. Their distinct emitted bodies remain separate even where the compiler speculates/inlines another virtual implementation.

`glyph-native-core1-exact-functions.json` retains address, end, symbol size, every stack allocation instruction, direct call/tail edge and indirect call site. `glyph-native-core1-vtables.json` decodes actual read-only ELF vtable words. `glyph-native-core1-bound-graph.py/json` adds source-established concrete target sets and certified helper bounds, then computes frame + maximum child over an acyclic over-approximation. It resolves196 non-special functions; unknown targets0; callgraph cycles0. Numeric/time/lock/memory aggregate leaves have their independent bounded derivations below; their bodies are not silently assigned zero.

For ordinary C/C++ functions the allocation inventory sums every PUSH and immediate SUB SP in the exact extent. This is conservative when branches allocate alternatives. The reachable inventory was inspected for other SP mutation, inter-function conditional branches and tail-register targets: the extra SP references only copy SP to argument registers, and the two tail-register sites are resolved stack-neutral veneers. There are no reachable VLA/alloca/unaccounted dynamic SP changes. Veneer temporary4 is conservatively charged even though it is popped before the target. No printf/vfprintf family is in this graph; display text uses Arduino Print. Loop counts affect duration, not frame depth.

The graph deliberately over-approximates: it permits every concrete SSD1306 slot at renderer dispatch, includes both clear/display lambdas at generic display callback sites, allows empty-write I2C probing and timeout reset, charges both endTransmission overload frames even on compiler-inlined paths, and adds the largest core1 IRQ even at masked allocation/time descendants. Some bound-maximizing compositions are source-infeasible; that is safe for an upper. No such composition is represented as an observed or feasible peak.

## Entry and final composition

The default SDK launcher writes three bootstrap words at top-12, core1_trampoline10044818 pops all12 before core1_wrapper1004481a begins. There is no retained extra12-byte bootstrap prefix. core1_wrapper retains8; the metrics entry adapter is stackless and tail-enters main110040f5c, which retains8. Setup and loop execute sequentially and are not added together.

| Complete branch | Graph below setup1/loop1 entry | wrapper8 + main1 8 + conservative SIO IRQ68 | Retained allowance |
|---|---:|---:|---:|
| setup1 startup, including constructors/remap screen |936|1,020|<=1,152|
| loop1, including display controls/recovery/RGB |952|**1,036**|<=1,152|
| new metrics ServiceCore -> Publish |72+48+20=140|224|<=1,152|

Normal core1 enables only exclusive SIO and exclusive FastLED DMA_IRQ0, both0x80. No SysTick/USB/alarm handler is enabled on this core. Their established upper costs are SIO68 and DMA52, each including first exception alignment, and they cannot mutually preempt. Therefore adding68 once dominates either. Earlier SDK trampoline12 and registerCore initialization are smaller separate branches. The1,152 allowance leaves896 bytes below2,048 (and864 above the diagnostic bottom32 exclusion); no4-KiB scratch-bank envelope is used. ROM's pre-application core1 waiting protocol is not relabeled a measured application startup observation.

## Actual display and bus targets

The only display is `Adafruit_SSD1306 display(128,64,&OLED_WIRE_INSTANCE)` with Mk6 OLED_WIRE_INSTANCE Wire1. Its constructor stores a non-null Wire pointer and spi=NULL. No source assigns another display implementation or replaces that pointer. SPI/bitbang paths, SPI interrupt-registration/tree-allocation logic and Wire slave callbacks are unreachable for this display. SSD1306 frame-buffer GFX operations and its I2C display/command methods are the concrete targets.

Exact SSD1306 vptr slots (offsets after the two ABI header words):0 GFX::write(char);4 Print::write(buffer);8 availableForWrite;12 flush;16 SSD1306::drawPixel;20 startWrite;24 writePixel;28 writeFillRect;32 writeFastVLine;36 writeFastHLine;40 writeLine;44 endWrite (same zero-body address as startWrite);48 setRotation;52 SSD1306::invertDisplay;56 SSD1306::drawFastVLine;60 SSD1306::drawFastHLine;64 GFX::fillRect;68 fillScreen;72 drawLine;76 drawRect. All pointer words/addresses are retained in the vtable JSON.

The concrete graphics DAG is finite: writePixel -> SSD pixel; writeFastV/H -> SSD line -> internal leaf; writeLine -> writePixel; writeFillRect -> fillRect -> writeFastVLine; fillScreen -> fillRect. drawChar/drawBitmap/circle/rectangle paths descend into those primitives; none re-enters text rendering or an application callback. GFX::drawChar bound336 includes its136-byte frame and the conservative writeFillRect56 -> fillRect56 -> writeFastVLine24 -> SSD line32 -> internal32 chain. Print::printNumber bound480 adds72 + Print buffer24 + GFX write48 to that336. Virtual alternatives eliminated by the concrete SSD object are not mistaken for recursive base-class cycles.

The seven constructed modes are exactly MenuButtonHints, InputDisplay, GlyphConfigMenu (inherits ConfigMenu UpdateDisplay/HandleControls), RgbBrightnessMenu, AboutMenu, OopsieMenu and RemapMenu. Configurator/remapper loop returns early, but setup1 construction/remap rendering remains included. Their ordinary controls choose from the source static page/action tables, the actual DefaultConfigMenu lambdas1–6 and named SetDefaultMode/SetUsbBackend/SetSocdType functions, plus inherited dashboard return. They update display/RGB/scratch/reboot or ordinary in-memory settings. There is no core1 ProfileStore/Persistence call, CDC/HID report writer, TinyUSB task, __loop or yield. `tud_disconnect` is included and reaches DCD without endpoint mutex ownership.

| Renderer callback including descendants (conservative union) | Bytes |
|---|---:|
| ConfigMenu::UpdateDisplay |784|
| InputDisplay::UpdateDisplay |768|
| RemapMenu::UpdateDisplay |124|
| RgbBrightnessMenu::UpdateDisplay |752|
| AboutMenu::UpdateDisplay |464|
| MenuButtonHints::UpdateDisplay |768|
| OopsieMenu::UpdateDisplay |776|
| IntegratedDisplay::SendReport, including subsequent controls |880|

The renderer bounds can select SSD invert/command/I2C helpers even when a particular source callback only draws pixels; this is an intentional finite over-approximation, not an assertion those callbacks invert the display.

TwoWire display dispatch is confined to setClock, beginTransmission, write(byte/buffer), endTransmission and the same concrete master end/begin/setClock on timeout. No onReceive/onRequest callbacks or slave begin(addr) are included. check_single_timeout_us10044cc8 is the sole I2C timeout-function target initialized by init_single_timeout_until; it retains8 and returns without recursion. i2c_write_blocking_until64 -> internal48 -> check8 totals120. Timeout reset graph is <=160; byte-buffer write40 -> byte write8 totals48. For conservatism, endTransmission()56 -> endTransmission(bool)64 -> _probe40 -> sleep_us512 is allowed, giving672, even though real SSD writes include command/data bytes. SSD display40 -> commandList40 -> endTransmission672 gives752. Clock/restoration/probe transactions are sequential.

## Actual LED controller targets

The only source-created FastLED controller type is NEOPIXEL<11>. Its read-only vtable points to CPixelLEDController<GRB>::showColor/show, ClocklessController<11,...>::init/showPixels, CLEDController::clearLeds/size, lanes, and getMaxRefreshRate. The configured power callback is calculate_max_brightness_for_power_mW, installed by setMaxPowerInVoltsAndMilliamps; null before installation is the other possibility. There is no user-provided callback or controller type in Config data.

| LED subtree | Upper bytes |
|---|---:|
| Clockless init (72 own, numeric/hardware children included) |136|
| Clockless showPixels (88 own, allocation included) |264|
| CPixel show and showColor (128 own + fallback showPixels subtree) |392 each|
| CFastLED::show (56 own) |448|
| Power limiter64 + conservative integer child64 |128|

The PIO/DMA state-machine and buffer loops do not recursively call show. When the compiler has inlined the expected target but keeps a virtual fallback, counting128 + actual showPixels88 + allocator176 overbounds it safely. The current emitted bodies use PIO/DMA; no unaccounted blocking-M0 assembly frame appears in their extents. DMA IRQ callback is handler8 -> micros8 -> timer leaf0, already included through the larger SIO68 allowance. A pending DMA transfer does not allocate a second C stack.

## Allocator/lock proof

The exact no-RTOS firmware has no initFreeRTOS implementation. main's weak test takes the non-RTOS path; __freeRTOSinitted20030405 is zero-initialized and no linked setter enables it. Thus retarget locks use SDK mutexes, not the otherwise allocation-recursive FreeRTOS map helper. Each lock/unlock aggregate24 conservatively adds own8 + veneer temporary4 + recursive-mutex frame12. The hardware wait loops are fixed-depth even under cross-core contention. No callback or reentrant allocation occurs while waiting.

Exact retained allocator graph: `_malloc_r`10061854 own40 may call `_free_r`10060d08 own24, which may call `_malloc_trim_r`10060c6c own24. Trim calls lock/unlock or `_sbrk_r`10063238 own16 -> `_sbrk`100449f8 leaf0. It does not call malloc/free again. `__malloc_lock`/unlock each own8 plus the24 lock aggregate. Therefore trim56, free80, malloc_r120, malloc128, wrapper malloc136, operator new/new[]144. calloc16 -> calloc_r24 -> malloc_r120 gives160; wrapper calloc16 gives176. Zero fill adds at most ROM memset8 as an alternative after allocation. Allocation failure returns in these actual new wrappers; no exception unwinder or stdio path is hidden in this graph. Dynamic allocation changes heap occupancy, not automatic stack size; heap-capacity validation remains a separate existing obligation.

The noInterrupts wrapper panic on nesting15 is excluded by the ordinary state invariant: core1 reaches at most a bounded outer allocation critical section and the SIO pre-mask critical entry, not fifteen nested masking calls. Resource-claim panic/assert calls are likewise outside the admitted successful setup path: DMA/PIO claims use required=false, PIO program insertion follows can-add with all core0 backend claims complete before Normal publication, and the DMA handler is installed once into an unused core1 vector. Master Wire's impossible slave IRQ removal branch is over-approximated for stack but is not treated as a reachable conflicting IRQ installation. These exclusions and call sites are retained in graph JSON; no arbitrary-corruption/fatal-assert certificate is claimed.

## Numeric and time helper aggregates

`glyph-native-core1-cfg-probe.py` explores exact direct conditional branches, call/return edges and stack instructions by machine address across internal labels; loops are visited by `(PC, depth, return context)` until fixed point. ROM numeric CFG result files show no unresolved transfer or unbalanced return for the listed ROM operations. They were also source/readback inspected. This is static analysis of the official release instructions, not recompilation or target execution.

| Numeric helper | B0 | B1/B2 | Linked wrapper addition |
|---|---:|---:|---:|
| ROM fadd/fsub |16|16|0|
| ROM fmul |20|8|0|
| ROM fdiv |16|16|possible hardware-divider save20|
| ROM float2uint |8|8|0|
| ROM uint642float |SDK shim12|12|B0 first-use dispatch16, released before shim|
| ROM uint2float/fix2float |12|12|0|
| ROM clz32 and packx |0|0|i2f/ui2f wrapper8; B0 shim fixed packx0x29ef|
| SDK unsigned64 divide |48|48|veneer temporary4, conservatively additive|
| SDK signed/unsigned32 divide |28|28|veneer temporary4|
| SDK lmul |4|4|0|

The generic **64-byte numeric child** used in the core1 graph dominates every actual integer/single-float wrapper reached by LED setup/RGB/display/power calculations, including state-save, B0 table patch, fixed packx call and veneer. B0 uint64 shim's BLX at1004479e is resolved to fixed ROM packx29ee, leaf0; i2f's BLX10044680 resolves to initialized ROM CLZ32, leaf0. They are the two intentionally external transfers in the SDK numeric CFG output, explicitly closed by ROM leaf results and pinned float_init_rom/float_v1_rom_shim source. The first-use dispatcher16 pops its entire frame into the shim target; it does not remain co-live with shim12. RGB arithmetic children execute sequentially, so divide, conversion, multiplication and output conversion are alternatives under the retained loop frame.

The conservative sleep_us512 aggregate bounds sleep_us16 -> sleep_until40 -> alarm_pool_add_alarm_at72 -> add_alarm_under_lock40 -> remove/free16 -> remove_head16 -> remove_any_head32 -> fixed16-node merge140 =472. The critical phase is masked. Callback is stackless sleep notifier returning0 and no user/repeating callback is installed. Other target/clock/cancel/return branches are smaller. sleep_ms520 additionally bounds its own8 and preceding multiplication. There is no recursive sleep callback. This reuses the independently established finite16-node heap proof, with exact72-byte alarm-add allocation inventory rather than a prior informal64 estimate. Adding SIO68 even to masked sleep/allocator descendants is deliberately conservative.

## Additional core0 XInput activation applicability

The earlier348 IRQ certificate was for Configurator/recovery FS. For boot activation after XInput+CDC descriptor registration, it extends to348 using the same no-owner-at-FS and no-core1-endpoint-writer invariants. Actual xinput control1000b998/init/reset callbacks are stackless; xinput transfer1000b99c8 -> usbd_edpt_xfer16 -> DCD8 -> hardware start24 -> ROM memcpy12 totals68 below the CDC child. xinput open1000b9c032 -> endpoint open16 -> DCD open24 totals72. Vendor1000bb4416 -> control32 -> endpoint16 -> DCD8 -> start24 -> ROM12 totals108, plus task120 + exception32 + SysTick44 + alignment8 =312. Configured serial remains340 including padding. No XInput callback adds another producer or callback into application FS. This does not yet certify NES/non-Configurator mode-destination persistence; its priority0 GPIO alternative is a separate extension.

All original resource limits and all NOT_MEASURED/NOT_TESTED/hardware acceptance boundaries remain unchanged. The result closes the named exact core1 application graph; it does not authorize handoff, firmware integration, device action or whole-resource PASS by itself.
