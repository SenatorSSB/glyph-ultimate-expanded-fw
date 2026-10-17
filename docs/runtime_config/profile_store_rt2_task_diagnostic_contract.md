# Version5 independent first-task observer

Both response `recovery_startup_diagnostics_version` and `recovery_task_version`
are5. Retained v4 USB fields remain sequential core0 samples when requested;
they are not the independent LED source. No Config/ProfileStore record schema
or mutation protocol is changed. See [source audit](profile_store_rt2_task_source_audit.md)
and [one-attempt packet](profile_store_rt2_task_hardware_packet.md).

## Identity and asynchronous publication

Route entry enables progress observations. First recovery LoopEntered arms
foreground invocation capture. Only core0, exception-state0, after this arm
qualifies in the `tud_task_ext` wrapper. Each qualified call publishes a monotonic
ID before its real call and publishes return afterward. USB hardware/software
IRQ calls and core1 calls never become a foreground ID. The legacy total task
counters still include all core0 task contexts.

The independent task pixel anchors ID1. RED means no entry recorded; ORANGE
means entry without recorded return and zero DCD reset emissions during that
active interval; MAGENTA means one; BLUE means two or more; GREEN means ID1
returned and remains latched afterward. It does not claim a later invocation
returned, and cannot diagnose later-call stalls without serial telemetry.
Counters observe wrapper boundaries, including small pre-real/post-real
instruction windows, not an atomic hardware instant. Entry publication excludes
resets before active-ID publication; return publication prevents attribution to
a later ID. Mixed bounded reads are rejected without waiting for the writer.

The second MB1 pixel is monotonic progress since observer enable: OFF none;
YELLOW a RESET_OR_UNPLUGGED processing completion during ID1; CYAN DCD SETUP
emitted; GREEN attributable descriptor/address progression; WHITE configuration
completion or supported inspection decoded. Later milestones override earlier
ones on this pixel only. First-call reset count remains independent. YELLOW's
first-call count cannot be advanced by an earlier IRQ task reset; generic reset
completion is also separately reported. A queued event may predate ID1, and the
shared BUS_RESET/UNPLUGGED helper makes exact event identity ambiguous.

Pixels0/1 map to MB1 by source; their geometric order is not established. Report
both colors in either order: the palettes overlap only at GREEN. Unresolvable
blended colors, unavailable indicator, or no visible publisher remain UNKNOWN.
Neither an active marker nor repeated reset emissions prove an infinite hang or
a physical reset storm. Core1 must remain runnable; this is not an independent
hardware watchdog. BLUE can appear even when queue enqueue failed.

## Additive response fields

All fields below use prefix `recovery_task_` and uint32 proto3 scalars; omitted
JSON scalars mean zero when decoded with this exact schema.

| Suffix | Meaning |
| --- | --- |
| version |5 |
| valid |1 only for an accepted bounded foreground/reset-bank snapshot |
| entered / returned | Qualified foreground invocation and return counts |
| active | Current qualified invocation ID,0 outside a call |
| first_returned | ID1 return observed, sticky |
| active_resets | DCD reset emissions tagged to current active ID |
| first_resets | DCD reset emissions tagged to ID1, retained after return |
| reset_completed | Generic after-control-reset completion count since enable |
| first_reset_completed | Completion count while ID1 active |
| event_flags | bit0 DCD reset emitted, bit1 SETUP emitted, bit2 UNPLUGGED emitted |
| task_flags | bit0 control/descriptor progression, bit1 configuration completion |
| pair | Task state in bits4..7; progress state in bits0..3 |

Task-state indices0..4 are RED/ORANGE/MAGENTA/BLUE/GREEN. Progress-state indices
0..4 are OFF/YELLOW/CYAN/GREEN/WHITE. `pair` is computed observed state, not proof
an LED frame physically latched. Inspection can make progress WHITE independently
of configuration bit. Retained generic task/reset counters have their older
scope; do not compare differing scopes as if they were one invocation.

Counts saturate where implemented, while sequence words wrap. This is a bounded
single-attempt diagnostic, not a claim across2^32 transitions or full sequence
wrap during one snapshot. A saturated active ID is rejected to avoid reusing it
as a fresh reset identity. Atomic scalar samples can represent adjacent moments;
valid does not mean a simultaneous electrical/USB snapshot.

Scratch3 after core1 publication has namespace0x5258, task index in bits12..15,
progress index in bits8..11 and indicator-available bit128. It no longer carries
v4 phase/USB flag meanings. Previous0x5257/0x5256/0x5254 values remain recognized
by their own version. No scratch selectors0..2 or SDK scratch4..7 are changed.
Before handoff, the inherited startup indicator/phase behavior remains v4.

The publisher has no USB/MMIO-register sampling dependency on core0 Read. Core0
handoff completes its frame before ownership release; core1 accepts ownership
before accessing the PIO state. Only changed successful states are emitted.
The dedicated PIO remains the existing four-word frame on GPIO11; GPIO15 is
never borrowed. Hardware acceptance is NOT_TESTED and root cause UNPROVEN.
