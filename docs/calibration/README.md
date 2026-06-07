# Calibration Docs

Status label: CURRENT.

`docs/calibration/` is the evidence packet and historical record area for the
Glyph/HayBox-side workflow. It is not the main roadmap.

Canonical current docs live in top-level `docs/`:

- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/WORKFLOW.md`

Many calibration files are dated branch records, one-off blocker packets,
templates, fixtures, or result packets. Preserve them as evidence, but do not
infer the current roadmap by reading every historical packet as equally current.

## Finding Current Evidence

- Current baseline: `glyph_post_gfw3_configurator_baseline_2026-06-06.md`,
  `glyph_roadmap_next_work_index_2026-06-06.md`.
- Hardware results: `glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md`,
  `glyph_ultimate_preservation_hardware_result.md`.
- Official configurator corpus:
  `export_corpus/official_glyph_configurator_2026-06-06/manifest.json` and
  `glyph_external_remapper_misattribution_correction_2026-06-06.md`.
- Generated-config/runtime design:
  `glyph_identity_runtime_generated_config_prototype_2026-05-28.md`,
  `glyph_identity_runtime_generated_cpp_diff_artifact_2026-05-28.md`,
  `glyph_runtime_loaded_config_design_v0_2026-05-28.md`.
- Quarantined external-remapper records: these files are quarantined records;
  files containing
  `external_remapper`, `offline_remapper`, or `clean_room_adapter` remain
  historical/non-authoritative unless independently source-backed.
- Templates: files ending in `_TEMPLATE` or containing `template`.
- Blocker packets: files containing `blocker`, `gate`, `readiness`, or
  `handoff`.

See `docs/calibration/INDEX.md` for grouped key files and
`docs/calibration/archive_policy.md` for preservation policy.
