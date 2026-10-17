# Timing-corrected private DCD observer source audit

Direct parent7e9e2ea0e3ac8c018dfa3088ef65af6b6c8cc820 is rejected for physical
installation by owner correction52ec706f-e12c-4b47-9aa1-92678981065d. Its ENTRY
cost90instructions/36DMB before local status and its per-invocation external
trampoline are removed. Source/build/custody architecture is retained.

Pristine installed and repository source remain18095bytes SHA256
92a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12.
Deterministically patched source SHA256
44feae8932391bee16ab9aa567716d1f00195fc4e0398f6531cad908895aa00a.
Removing one include and12post-read publications restores exact pristine bytes.
No installed package mutation, upgrade, workaround, USB repair or private status
reread. The registration wrapper passes original callback/same priority once.

Original local INTS assignment is the first source statement; dedicated one-arg
GlyphDcdPrivateStatus(status) follows immediately. It merges entry/ID/active/local
status and enabled-window classification. Later SOFdone/BUFFdone/actualSETUPtest/
branch/pointer/PID/event/clear/return boundaries retain exact insertion positions.
Bit0 means merged post-read entry, with no target H0 callback. Return is the source
normal-return boundary, not independent proof of completed machine return.

The single non-reentrant USBCTRL writer and atomic32 payload preserve race freedom.
Writer: relaxed odd sequence, release fence, relaxed payload, release even sequence.
Reader: acquire initial sequence, relaxed payload, acquire fence, relaxed final
sequence; matching even only, one bounded try, later ordinary loop retries invalid.
Initial acquire excludes old payload. Any newer payload read bridges writer release
fence to reader acquire fence, forcing final sequence beyond old even via coherence.
Both fences, final release and initial acquire are necessary for this proof. Enable
is separate monotonic release/acquire. No seq wrap during one reader attempt is an
explicit assumption. Invocation saturation likewise limits unbounded identity.
Primary normative rules: C++17 N4659 atomics.fences paragraph2 and intro.races
write-read coherence. The finite RF checker illustrates225assignments and order-edge
negative witnesses; it is not a universal C++ formal verifier or physical proof.

Both C ABI hooks inline State::Marker. Final target disassembly must prove no nested
hook/helper, inline aligned32 accesses and no atomic RMW/library support. Separate
source and assembly gates forbid pre-read diagnostics/DMB/helper/atomicstore/reread/
wrongvalue/movedmarker. Sole candidate-owned object selection and exact-only-output
command replay bind assembly proof to actual final object and final ELF. Final
instruction/barrier counts, compiler prologue differences, resource deltas and
fresh review are recorded with exact final identity in sealed HANDOFF.

Response-only version2: setup_irq/pre_setup legacy trampoline entry/return/pre/post/
age fields stay unsupported zero; private post-read entry/active/source-return
history remains valid. Snapshot96B/State100B, Config/Profile/Request/persistent
schema unchanged. Global first/latest and first-enabled selected history retained;
all normal-boot IRQs incur post-read diagnostics. LF4/LF3/LF5 whole-button mapping
and menu darkness retained, no new pre-status visual state.

Post-read publication and larger compiler register saves can still affect timing,
subsequent interrupts and IRQ return. Zero intentional diagnostic instructions/
barriers before the original load is not zero perturbation or cycle equivalence.
No root-cause inference before physical evidence. Controller still stopped88a36e.
Separate stopped88a36e read-only adjudication prerequisite and one-attempt future
owner packet remain prepared/unexecuted. No source-agent controller action, new
RT2, canonical merge, endpoint repair, panic suppression or persistent mutation.
Hardware NOT_TESTED; root cause UNPROVEN. Earlier source-review/coverage receipts
are historical evidence for prior rejected artifact, not current acceptance.
