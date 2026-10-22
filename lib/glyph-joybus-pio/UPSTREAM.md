# Joybus source provenance

Vendored from GregTurbo/joybus-pio commit
`f2f59c0aee07aea58cdd03616439bc3c6a8cbd8a`, the dependency pinned by the
failed selector candidate `4898951994bcabcaef2846145de2922a674656f8`.
The retained LICENSE applies.

Local changes add a pending-control-plane-only poll-start admission hook,
a per-state-machine sticky PIO activity flag (IRQ flags 4–7), and the existing
invalid-poll drain/reset at the split poll caller. No CPU PIO IRQ is enabled.
The marker replaces the existing 20-cycle WAIT sampling delay with a one-cycle
WAIT and a 19-cycle nonwaiting IRQ; the input sampling cycle is unchanged.
The generated instruction header must match the accompanying PIO source.

An admitted idle result leaves the receiver paused for the core0 transaction.
The next wait resumes it if the transaction is refused. No-request timeouts
continue receiving without pausing. A partial first byte retains active-command
priority; malformed first-byte traffic is not given a new protocol timeout.
