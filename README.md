# Glyph Firmware

*Glyph's firmware is based on HayBox, please consider supporting/sponsoring it [here](https://github.com/JonnyHaystack/HayBox)*

This repository is the Glyph/HayBox-side firmware, configurator, and backend
realization workstream for possible Senscope integration. It is used to inspect,
model, document, and cautiously implement controller/backend behavior.

Senscope is a separate browser-first Super Smash Bros. Ultimate Rectangle
Modifier Designer app. This repo may inform future Senscope backend adapters,
realization evaluators, manual-entry guides, or export workflows, but it must
not change Senscope game-semantic source authority.

## Start Here

- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) - current baseline, readiness
  categories, approval gates, and non-claims.
- [docs/ROADMAP.md](docs/ROADMAP.md) - clean long-term Glyph-side roadmap.
- [docs/WORKFLOW.md](docs/WORKFLOW.md) - branch, inspection, test, merge, and
  result-recording workflow.
- [AGENTS.md](AGENTS.md) - standing operating contract for agents.
- [docs/calibration/README.md](docs/calibration/README.md) - guide to detailed
  evidence packets and historical records.

## Current Status

- GFW3 runtime remap work is merged, user hardware-tested, and recorded.
- Phase 3 generated-like C++ constants path is merged, build-gated, user
  hardware-tested for applicable non-nunchuk scope, and recorded.
- Preservation hardware pass is recorded for applicable non-nunchuk scope.
- Step 14 manual firmware-consuming runtime-config load is blocked before implementation.
- Step 15 source-authority research complete.
- Step 16 WebSerial/device-write implementation is blocked before implementation.
- Step 17 flashing automation is forbidden/not approved; safety boundary complete.
- Step 18 public/manual workflow release-candidate hardware result is recorded for
  applicable doable scope in
  `docs/calibration/glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.md`;
  the plan/checklist remain plan-only and no public release or official
  configurator compatibility claim is made.
- Official Glyph configurator corpus records user-provided default and
  back-and-forth JSON fixtures when the correction packet is present.
- Calibration docs remain useful evidence, but the current roadmap should be
  read from `docs/CURRENT_STATE.md`, `docs/ROADMAP.md`, and
  `docs/WORKFLOW.md`.

## Explicit Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Firmware binary/protobuf parser integration is not implemented.
- WebSerial/device write is not implemented.
- Protobuf binary write is not implemented.
- Firmware flashing automation is not implemented.
- No external-remapper adapter output is implemented.
- No public release claim is made.
- No nunchuk validation claim is made.

`docs/calibration/` contains detailed evidence packets, dated blocker records,
historical branch notes, templates, and correction packets. Treat it as an
evidence archive, not the main current roadmap.

## Glyph Links

For remapping your Glyph: [Configurator](https://limitlabs.com/pages/glyph-configurator)

Glyph resources: [Resources](https://limitlabs.com/pages/glyph-resources)

User manual: [Manual](https://cdn.shopify.com/s/files/1/0926/5597/6818/files/Glyph_Manual_v1.0.pdf?v=1775239160)

Order today through [Satisfye.com](https://www.satisfye.com/collections/glyph), our manufacturing and logistics partner for Glyph.

---
This project is licensed under the GNU GPL Version 3 - see the [LICENSE](LICENSE) file for details
