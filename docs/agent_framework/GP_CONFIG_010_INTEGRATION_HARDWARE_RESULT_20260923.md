# GP-CONFIG-010 current-canonical integration hardware result

Status: `HARDWARE_VALIDATED / PASS`.

The project owner physically tested exact integration candidate
`1c0ff22646729d26d45eacb4b8322c5baea7de48` and exact preserved 791552-byte
UF2 `4312f6a64fd1009e231aab2015e3ce67f862abd88a8ea31cd545db0e91e27476`
under `GP_CONFIG_010_INTEGRATION_HW_V1`. The structured Revision-2 result is
`repo-json:docs/calibration/fixtures/gp_config_010_integration_hardware_evidence_2026-09-23.json`.

The run passed the clean first startup, exact Ult01-through-Ult13 menu
visibility, required activation indices 0, 9, 10, 11, and 12, post-reconnect
visibility and LT4-to-Ult13 selection, representative controls, exact owner
Config restoration, all nine accepted GP-X1-002 raw/miniscreen rows with
neutral return, and the final normal reconnect. No repeated frozen-logo event,
stuck input, or disconnect was reported. Evidence gaps are empty.

The owner-original Config was restored with exact immediate and post-reboot
identity: 4201 bytes, SHA-256
`f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`.
Nunchuk remains `NOT_TESTED`; no gameplay-angle/radius or root-cause claim is
made.

This PASS applies only to the integration candidate/artifact pair above. The
original historical GP-CONFIG-010 candidate
`f4771e17430fd1ea3f1e3e5339a83dfe648290a3`, 791040-byte UF2
`9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a`, and
its immutable PASS evidence remain distinct and unchanged. This publication
does not integrate firmware or mark GP-CONFIG-010 `DONE`; a fresh
Implementation Supervisor must perform strict tested-candidate integration and
completion publication.
