# Approval-bound observation scope clarification

This clarification accompanies the grouped packet with technical PINS SHA-256
`427f4aacaa3b933c77caa334f0f3e2cea360a5d8d941653d9cda282d65d20560`
and DEVICE_PACKET SHA-256
`3e271fedee8f57f88803bb389d62ba29dde6673a9e9f9d7a151cffce17f9e70d`.
It changes no command, fixture, expected value, helper, budget or source byte.
The owner approves the packet together with this clarification and the sampling
amendment. No approval or execution has occurred yet.

Family 9's inherited `source_scope` text inventories the original isolated
GameCube L/R/Z capability. The reduced sequence selects N094/N095 visible
analogue-trigger values and the S022 compound XInput case. It never loads or
executes the isolated S039–S045 stress profile. Those isolated physical cases
remain NOT_TESTED.

For S022 the dashboard must show native analogue values 140/140 while the XInput
report must contain 255/255. Preserve both observations and their source-defined
relationship. XInput exposes no separate GameCube digital L/R/Z report bits.
The N060 compound report observes its XInput RB field; GameCube Z and adapter
translation remain separate unobserved route facts.

The frozen selection lists and actual observations define each physical result.
The family inventory text supplies no additional executed case or PASS. All
isolated GameCube fields, WUP adapter translation and USB-Switch report gaps
remain open as stated in the operator packet. Independent HEP must retain them.
