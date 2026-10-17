# Official-authority audit: RP2040 SETUP / host evidence

Date: 2026-10-17. Bounded read-only specialist for exact source
`3761b702ea09f50b9c98a55bea91caa337a3f62e`, tree
`43f26381fd2b7b1f701c18aadc839d8f5143eedb`.
Runtime model telemetry: UNKNOWN. No controller I/O, capture, configuration change,
vendor/source edit, Git mutation, workaround enablement or hardware test performed.
Only ignored `local_backups/setup-irq/` evidence was written.

## Official references and custody

- [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040_datasheet.pdf),
  build-date2025-02-20, version3184e62-clean, downloaded as
  `official-references/rp2040-datasheet.pdf`, 5,301,205 bytes,
  SHA256 `be56fbb75ba0ae9e26558a73c93ac3e75c2ad4e6878d3b6703de2a76d886ea8c`.
  Printed pages390 (4.1.2.8.1 SETUP), 403 (SIE_STATUS table404),413–416
  (INTR/INTE/INTF/INTS, tables418–421),630–634 (USB errata).
- [Pico SDK1.5.1 register definitions](https://raw.githubusercontent.com/raspberrypi/pico-sdk/1.5.1/src/rp2040/hardware_regs/include/hardware/regs/usb.h),
  downloaded `official-references/pico-sdk-1.5.1-usb-regs.h`, SHA256
  `8e292ab4eb7ae6c5177f59a7cadcc03605685355b2c789a0cbf262d4968ec313`.
  Relevant lines1001–1007,2924–2930,3102–3108,3280–3286,3426,3458–3464.
- [SDK1.5.1 E5 reference implementation](https://raw.githubusercontent.com/raspberrypi/pico-sdk/1.5.1/src/rp2_common/pico_fix/rp2040_usb_device_enumeration/rp2040_usb_device_enumeration.c),
  downloaded and hashed in `official-references/manifest.json`; reference only.

The dash-spelling datasheet URL and .org variant returned403 on direct download;
the official underscore URL above succeeded. Browser rendering independently
reports the same build identifier. No downloader or firmware package was installed.

## B2 errata adjudication

Official USB errata: E2/E5 fixed on B2; E3/E4 concern host mode. E15 affects B2
under specified VL805/IN-transfer corruption conditions; those conditions are
not established here. E16 affects B2: inadequate clk_usb-to-clk_sys event
synchronization includes SETUP_REC; mitigation requires clk_sys at least10%
faster than clk_usb. Reset/suspend/resume quasi-static states are exempt.
No erratum documents a distinct stable SETUP_REC-to-SETUP_REQ loss stage.
No new workaround is justified. E5 remains physically inapplicable.

Exact target source/dependency inspection, independently reported by the source
specialist, establishes configured clk_sys130MHz and clk_usb48MHz, exceeding
E16 mitigation margin. `platformio.ini:90` sets130000000L; exact3761
`local_backups/comprehensive/compile_commands.json` supplies F_CPU130000000L.
Arduino-Pico `cores/rp2040/main.cpp:82–83` sets the system clock before TinyUSB
initialization at105. SDK `hardware_clocks/clocks.c:171–175` configures USB48MHz.
Source-specialist exactELF audit: only `set_sys_clock_pll` caller is main;
`clock_configure` callers are clocks_init/set_sys_clock_pll; no later target
clock writer found. Therefore E16 is mitigated by the configured source path,
not a supported root cause. Actual clock malfunction is unmeasured.

## Register constraints and observation interpretation

SDK facts: SIE_STATUS.SETUP_REC is bit17 (`0x20000`), write-one-clear;
INTR.SETUP_REQ is bit16 (`0x10000`), read-only, sourced from SETUP_REC.
INTE/INTF bit16 are read-write enable/force. INTS bit16 is read-only status
after masking and forcing. These are not three separately queued SETUP stages.
Reads of these fields do not acknowledge them. Clearing the SIE source removes
the ordinary raw interrupt; do not model writable INTR or read-to-clear INTS.

Normal-register-model inference, with stable state and device mode:
`R=S`, `M=(R & E) | F`, using boolean SETUP bits S/R/E/F/M.
The equation is an inference from official source/mask/force descriptions,
not a disclosed gate-level timing or read-coherency guarantee.

| Proposed observation | Permitted conclusion |
|---|---|
| S1,R0 | Inconsistent as stable normal state; sequential sampling can straddle source clear/change. Cannot establish a separate raw propagation defect. |
| R1,E0,M0,F0 | Valid stable disabled SETUP interrupt; does not prove why the writer/mask state arose. |
| R1,E1,M0 | Inconsistent as stable normal model; independent sequential reads and sticky positives do not prove simultaneity or faulty mask logic. |
| R0,M1 | Force bit can explain this; otherwise consider sample skew. INTS alone requires writer/force audit before attributing receipt. |
| M1 but no DCD event | Positive masked status observation; does not itself prove handler delivery, handler snapshot or branch entry. |

These mismatch patterns can be sampled; calling them a persistent silicon state
requires stronger evidence than non-atomic core1 polling. Retain raw bitset
observations and sampling limits. Avoid turning model-inconsistent rows into
ordinary injected hardware states. Separate synthetic sampler-race tests from
source-faithful hardware model tests.

`R-ever && E-ever` is not evidence of `R && E` in the same read interval.
Even a bundled sequential register sample is not atomic: source clear, mask
write, reset or IRQ service can occur between loads. Bracketed/repeated samples
improve corroboration but cannot prove an unseen negative or historical continuity.
No official exact-cycle synchronization latency is supplied by these references.
Stable mask inference must retain that limit; do not relabel “never sampled” as
“never existed.” NVIC/PRIMASK/IPSR read on core1 concern that core; they do not
prove core0 delivery state unless the observation explicitly belongs to core0.

## Safe native host authority

`HOST_PACKET_TRACE = NOT_AUTHORITATIVE` for this bounded singleRT2 route.

Apple [Console documentation](https://support.apple.com/en-ca/guide/console/cnsl1012/mac)
describes emitted system/device log messages. Native `log help stream` describes
streamed log events and supports predicates/timeout. This is corroborating
software evidence, with no documented guarantee of complete USB SETUP wire
transmission logging. Absence of a log is not absence of a packet. A driver
request/submission message alone is not proof of electrical transmission.

The installed Apple `ioreg(8)` manual says it displays the I/O Kit registry;
its snapshot cannot establish transient bus packets. Preserved copies and hashes:
`official-references/apple-host-ioreg.8` SHA256
`2d214795d791066feb548e872c7884ed9a746e2e20d249f4013a00b4f1b9659a`,
`apple-host-log.1` SHA256
`7f97df791464983bb077819c1aa2e9522e2fa5324da46ce8fb0fe4ae46ae2c92`.

Apple [Recording a Packet Trace](https://developer.apple.com/documentation/Network/recording-a-packet-trace)
covers network interfaces/tcpdump. It supplies no USB-control-transaction
capture authority. USB-flavored network interfaces would still not expose USB
EP0 SETUP tokens through that cited facility.

Host name/help-only discovery: macOS27.0.1 build26A434 arm64; log, ioreg,
system_profiler, tcpdump and fs_usage available. usbdiagnose/usbcfwflasher names
found, neither executed. No USB Prober name found in limited application paths;
this is not a global absence proof. Historical Apple IOUSBFamily/USBProber source
is not proof of safe installed modern capture capability. No SDK/driver
installation, sudo, boot argument, kernel tracing or logging-state change is
within this route.

Optional human-run corroboration only, not executed as capture here:

```sh
/usr/sbin/ioreg -p IOUSB -l -w 0
/usr/bin/log stream --style compact --level info --timeout 30s --predicate 'subsystem CONTAINS[c] "usb" OR senderImagePath CONTAINS[c] "USB"'
```

Neither command supplies HOST_PACKET_TRACE authority or should trigger a retry.
Start an optional log before the same single authorized RT2 only if desired;
failed visibility or permissions must not lead to configuration changes. A
missing predicate match is inconclusive. Prefer retained firmware evidence for
the current narrow boundary and state the remaining below-observability limit.
