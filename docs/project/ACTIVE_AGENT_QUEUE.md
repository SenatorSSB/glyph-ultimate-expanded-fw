# Active Agent Queue

Status label: CURRENT.

This is the only canonical executable work queue for the Glyph repository.
Roadmap entries, Planner packets, branch names, chat recommendations, and old
calibration packets do not authorize implementation. Only a complete work
order recorded here as `READY` authorizes immediate new implementation. A
complete `PREAUTHORIZED` work order may become Ready only through its already
authorized objective mechanical activation conditions.

The former G-series queue in this file is superseded. Its history remains in
Git, but it is not current candidate supply or implementation authority.

## Current Queue State

<!-- queue-state:start -->
```json
{
  "schema_version": 3,
  "canonical_branch": "configurator",
  "audit_base_sha": "b0f8133b10abe11865dc6887f29a2c90f4aaad8a",
  "operating_mode": "MINIMAL_SUPERVISOR_WITH_ON_DEMAND_CONSULTATIVE_PLANNING_AND_HARD_HARDWARE_GATE",
  "curation_obligation": {
    "pending": false,
    "trigger": null,
    "resolution": "Corrected packet glyph-portfolio-20260921-1252 is fully adjudicated. GP-X1-002 has a complete READY order for the exact owner-confirmed sole kX1Table restoration; no packet survivor or pending Curator decision remains.",
    "provenance": {
      "opened_by_role": "Glyph Portfolio Planner",
      "opening_reference": "git-json:525296975bcd6791e8e3a57945b2c47e0fc16ef0:docs/planning/portfolio_20260921_1252.md",
      "subject_ids": [
        "GP-X1-002"
      ],
      "resolved_by_role": "Glyph Work-Order Curator",
      "resolution_reference": "git-json:354ec374f3676e1288e590b09d277729aa94989f:docs/project/ACTIVE_AGENT_QUEUE.md#curator-receipt"
    }
  },
  "planner_packet": {
    "state": "CONSUMED",
    "branch": "planning/portfolio-20260921-1252",
    "base_configurator_sha": "71dc9979a78ae2174a232884e1692f833ea80de3",
    "packet_id": "glyph-portfolio-20260921-1252",
    "packet_path": "docs/planning/portfolio_20260921_1252.md",
    "planning_commit": "525296975bcd6791e8e3a57945b2c47e0fc16ef0",
    "curation_commit": "354ec374f3676e1288e590b09d277729aa94989f",
    "candidate_count": 0,
    "survivors": [],
    "curator_review_required": false,
    "global_wait_proposed": false,
    "material_events_since_packet": [
      "Independent Curator authorized GP-X1-002 as a complete READY H2 order for only the owner-confirmed kX1Table restoration.",
      "The rejected prior packet and unpushed receipt remain non-authoritative; GP-CONFIG-010 stays separately LOCAL_ACCEPTANCE_PENDING and no Senscope binding was selected."
    ],
    "curator_review_provenance": {
      "planning_branch": "planning/portfolio-20260921-1252",
      "planning_commit": "525296975bcd6791e8e3a57945b2c47e0fc16ef0",
      "packet_id": "glyph-portfolio-20260921-1252",
      "packet_base_configurator_sha": "71dc9979a78ae2174a232884e1692f833ea80de3",
      "curation_branch": "curation/portfolio-20260921-1252-review-v2",
      "initial_reviewed_dispositions": [
        {
          "candidate_id": "GP-X1-002",
          "disposition": "READY"
        }
      ],
      "review_date": "2026-09-21",
      "curation_commit": "354ec374f3676e1288e590b09d277729aa94989f"
    }
  },
  "completion_correspondence": {
    "migration_base_configurator_sha": "caf37e10673896b3bf5e2815875a93310b3f3ac1",
    "legacy_done_ids": [
      "GP-CONFIG-001",
      "GP-CONFIG-003",
      "GP-CONFIG-004",
      "GP-CTL-001",
      "GP-HW-001",
      "GP-PROV-001",
      "GP-PROV-002",
      "GP-SRC-001",
      "GP-SRC-002",
      "GP-SRC-003",
      "GP-SRC-004",
      "GP-SRC-005",
      "GP-VAL-001",
      "GP-VAL-002",
      "GP-VAL-003",
      "GP-VAL-004"
    ]
  },
  "runway": {
    "immediate_ready": 1,
    "recorded_preauthorized": 0,
    "mechanically_activatable_preauthorized": 0,
    "invalidated_preauthorized": 0,
    "hardware_pending": 1,
    "effective_authorized_runway": 1,
    "target_effective_authorized_runway": 4,
    "target_provenance": "Initial 4-hour Implementation / 12-hour Curator cadence: three expected opportunities plus one resilience item; target only, never a quota."
  },
  "signals": [
    "RUNWAY_LOW",
    "HARDWARE_TEST_REQUIRED"
  ],
  "global_evidence_wait": {
    "supported": false,
    "planner_broad_audit_provenance": null,
    "curator_acceptance_provenance": null,
    "required_external_evidence": null,
    "resume_event": null
  },
  "items": [
    {
      "id": "GP-X1-002",
      "title": "Restore owner-confirmed prior X1 table",
      "status": "READY",
      "branch": "glyph/gp-x1-002-restore-normal-x1",
      "objective": "Restore the existing Ultimate sole/non-Mode kX1Table to the exact owner-confirmed prior nine-point raw table while preserving every unrelated table, route, mode behavior and publication mechanism.",
      "why_this_matters": "GP-X1-001 intentionally installed a test-oriented offset-41 table. The owner has now selected the prior source-owned table as the desired normal X1 behavior.",
      "hardware_risk": "H2",
      "behavioral_claim": "With the unchanged Ultimate route where LT5 sets x1_active and exactly one effective modifier under non-Mode selection resolves RuntimeTableId::X1, directions 1 through 9 yield raw points (93,51), (128,51), (163,51), (93,128), (128,128), (163,128), (93,205), (128,205), and (163,205). Miniscreen center-relative representation is respectively (-35,-77), (0,-77), (+35,-77), (-35,0), (0,0), (+35,0), (-35,+77), (0,+77), and (+35,+77). The display conversion is raw minus 128 only; no gameplay angle or radius is claimed.",
      "scope": "Add GLYPH-UD-018 and one restoration-specific production-authorized overlay_preserve intake owning only kX1Table; apply directly required source-authority locator/checker and generated source-owned consequences; replace only kX1Table semantic bytes; add candidate-focused source/diff/table checks and GP_X1_002_HW_V1; build and preserve an exact UF2; publish source-free hardware-pending metadata; stop before merge until exact-snapshot physical PASS and normal evidence/integration processing.",
      "explicit_excluded_scope": "No change to the other 27 source-owned tables, kMX1Table, LT5/non-Mode routing, Mode/MX1 behavior, precedence, bindings, active RuntimeConfigView publication, profiles, persistence, USB, WebSerial/device/protobuf/backend write, flashing automation, neutral Profile schema, Senscope data or binding, gameplay semantics, Nunchuk claim, root-cause claim, or GP-CONFIG-010 source, candidate, artifact, protocol, evidence, queue status or correspondence. Do not rewrite either historical X1 intake or reuse GP-X1-001 hardware evidence.",
      "touched_planes": [
        "source-owned configuration",
        "generated tables/artifacts",
        "firmware runtime",
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "GLYPH-UD-018 records the project owner's 2026-09-21 confirmation of every ordered row. Historical source at 045bca0d1450c261c3c60ccf5ef86f7302bd3dbc and docs/runtime_config/intakes/x1_baseline_equivalent_overlay_v1.intake.json independently contain the same raw points. Live configurator 71dc9979a78ae2174a232884e1692f833ea80de3 has the GP-X1-001 offset-41 kX1Table in src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp; src/modes/Ultimate.cpp sets x1_active from inputs.lt5 and selects RuntimeTableId::X1 only for the sole non-Mode X1 path, while Mode+X1 selects RuntimeTableId::MX1. Existing accepted overlay_preserve tooling supplies the single-table realization architecture. Historical agreement is provenance; current owner confirmation is the product decision.",
      "dependencies_prerequisites": [
        "Start from freshly live-verified configurator 71dc9979a78ae2174a232884e1692f833ea80de3 with current generator/intake contracts and active source-owned publication materially unchanged.",
        "Use a new restoration-specific production-authorized intake in overlay_preserve mode owning exactly kX1Table; preserve all other 27 table bytes from the live baseline.",
        "Preserve current LT5 to x1_active routing, sole/non-Mode RuntimeTableId::X1 selection, Mode/MX1 behavior, precedence, profiles, persistence and active RuntimeConfigView publication byte-for-byte outside directly required authority/checker metadata.",
        "Keep GP-CONFIG-010 isolated at candidate f4771e17430fd1ea3f1e3e5339a83dfe648290a3 and artifact 9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a with its current INCONCLUSIVE evidence and gaps unchanged."
      ],
      "substantive_authorization_rationale": "The owner selected all nine behaviorally relevant coordinates, live source supplies the exact bounded X1 route, and the accepted overlay_preserve mechanism supplies a narrow single-table architecture. No semantic value, routing choice, profile behavior or backend capability must be inferred. H2 exact-candidate build, custody, independent review and physical acceptance contain the remaining runtime risk.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any ordered coordinate changes or implementation requires ownership beyond kX1Table.",
        "Any routing, binding, precedence, Mode/MX1, profile, persistence, active-publication or unrelated table delta appears.",
        "Live source, generator/intake contracts, build inputs or GP-CONFIG-010 identity materially drift before candidate implementation.",
        "Implementation requires a Senscope modifier/binding decision, gameplay inference, forbidden runtime/device-write path or rewriting historical X1 authority/evidence."
      ],
      "authorization_snapshot_provenance": "Independent Glyph Work-Order Curator reviewed live configurator 71dc9979a78ae2174a232884e1692f833ea80de3, corrected immutable Planner packet glyph-portfolio-20260921-1252 at 525296975bcd6791e8e3a57945b2c47e0fc16ef0, GLYPH-UD-018, exact live/historical X1 bytes and current LT5/non-Mode selection source on 2026-09-21. Immutable receipt 354ec374f3676e1288e590b09d277729aa94989f records READY; the rejected prior packet and unpushed receipt provide no authority.",
      "automated_validation": [
        "Validate the new production authority identity, exact ordered raw values and raw-minus-128 miniscreen rows; reject current offset-41, mixed, reordered, tampered, stale-baseline, expanded-ownership and unsupported-locator variants.",
        "Prove only kX1Table semantic content changes and all other 27 source-owned table bytes, including kMX1Table, remain exact; prove Ultimate.cpp routing, selection, precedence, active publication, compiled profiles, persistence, USB and GP-CONFIG-010 paths are unchanged.",
        "Run source-authority intake, generator-mode, generated-source contract, current X1 replacement/correspondence consequences, runtime-config aggregate, agent-framework, agentic-sequence, navigation, agent-surface and exact-diff checks.",
        "Commit the complete source candidate before build; run pio run -e glyph_mk6, inspect map/RAM delta, hash and preserve the exact UF2 under the candidate/artifact-addressed custody path, read back and re-hash it, and obtain fresh independent source/diff/firmware-safety review."
      ],
      "canonical_build": "pio run -e glyph_mk6",
      "expected_artifact": ".pio/build/glyph_mk6/firmware.uf2",
      "manual_acceptance": "REQUIRED",
      "manual_acceptance_protocol_reference": "docs/agent_framework/GP_X1_002_HARDWARE_PROTOCOL.md",
      "manual_acceptance_protocol_version": "GP_X1_002_HW_V1",
      "hardware_evidence_contract_reference": "docs/agent_framework/HARDWARE_EVIDENCE.md",
      "hardware_evidence_contract_version": "GLYPH_HARDWARE_EVIDENCE_V2",
      "rollback_recovery": "Before handoff preserve the currently accepted rollback artifact selected through custody records. On FAIL, PARTIAL, INCONCLUSIVE, custody mismatch or source drift, preserve exact evidence and stop; do not patch or rebuild under the same candidate/evidence identity. Never transfer GP-X1-001 or rebuilt/integrated artifact acceptance.",
      "status_documentation_updates": "Record the exact source candidate/base/artifact identity and hardware-pending state without changing GP-CONFIG-010. After exact PASS, use a fresh Hardware Evidence Processor and GP-VAL-015 integration correspondence; preserve GP-X1-001 as historical evidence and the physically tested artifact as the acceptance artifact.",
      "done_evidence": "Exact sole-kX1Table candidate diff, source-authority and negative proofs, canonical build, map/RAM inspection, fresh independent review, preserved UF2 custody, complete GP_X1_002_HW_V1 exact-snapshot physical PASS, independent evidence publication, current-canonical GP-VAL-015 integration correspondence and later strict DONE correspondence.",
      "stop_conditions": [
        "Any value, source authority, route, binding, precedence, Mode/MX1 behavior or physical activation sequence must be invented.",
        "Any table other than kX1Table, profile/configuration behavior, persistence, USB, active publication, GP-CONFIG-010 identity/evidence or Senscope data/binding would change.",
        "Any build, exact diff, review, custody, protocol, hardware or integration-correspondence gate fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-026",
      "title": "Close clean-checkout exact-schema characterization dependencies",
      "status": "DONE",
      "branch": "codex/gp-val-026-clean-schema-closure",
      "objective": "Make the current load-bearing custom-modifier characterization runnable from a clean checkout in the declared Python/C++ sanitizer environment without a firmware build or ignored .pio input.",
      "why_this_matters": "The checker currently reads generated schema/Nanopb files from ignored .pio; CI validation runs before the build and fresh canonical checkout fails missing generated schema header.",
      "hardware_risk": "H1",
      "behavioral_claim": "The exact-production 0/10/11/20 write/read characterization and historical results remain unchanged. A narrow tracked byte-identical host schema fixture supplies its declared inputs and rejects missing, altered, unsafe or wrong-identity dependencies.",
      "scope": "tools/check_glyph_custom_modifier_cache_characterization.py; dedicated tools/fixtures schema directory with config.proto, config.options, generated config.pb.h, Nanopb pb.h, provenance and applicable licenses; narrow .gitattributes entries only for these vendored fixture files to preserve exact bytes (-text) and disable their upstream-only whitespace diagnostics, never normalize CRLF or upstream LICENSE spaces; bounded dependency/adversarial tests and precise use docs; directly coupled runtime manifest, deterministic census and health consequences. Keep original GP-CONFIG-011 evidence and production include unchanged.",
      "explicit_excluded_scope": "No gameplay, routing, source-owned table, neutral Profile schema, runtime-loaded config, active publication, device/WebSerial/protobuf/backend write, persistence, flashing automation, Nunchuk acceptance or root-cause change. GP-VAL-011 remains owner-deferred and nonexecutable. Preserve GP-CONFIG-010 exact candidate f4771e17430fd1ea3f1e3e5339a83dfe648290a3 and UF2 9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a: no edit, rebuild, rebase, integration, or coupling. No production source/build selector/schema ABI change, checker demotion, aggregate isolation change, broad .pio inclusion, fixture regeneration at test time, or firmware build.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "At 4351b951916abbfbcaffec6f4512571a17d15ca5, checker BUILD_HEADER/PROTO/OPTIONS and compile include flags point into .pio; current manifest entry custom_modifier_cache_characterization is current/load-bearing and .github/workflows/build.yml runs validation before build. Nanopb upstream tag0.4.9.1 resolves to cad3c18ef15a663e30e3e43e3a752b66378adec1; pb.h Git blob10249bb651f72e17f2789c435edf0dfd398d2183. GregTurbo/HayBox-proto db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8, unchanged selector GregTurbo/HayBox-proto#db4e2f6 in config/glyph/env.ini. config.proto SHA256 2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b; config.options 6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805; generated config.pb.h 532f7ac324a57895caf82950ee36c6900d883a42188e5d6bbc2d3507318538f3; Nanopb pb.h a2ecdca9fdaeef5f4972ed983540c0d6fb0a5c402a2e0b0349d7e1bc5e188d29. CustomModeConfig.modifiers extent is20. Generated header identifies nanopb0.4.9.1/header40 and observed library metadata0.4.91; observed correspondence, not transitive reproducible-build proof.",
      "dependencies_prerequisites": [
        "Python standard library, existing C++17 compiler with address/undefined/bounds sanitizer support, and verified immutable upstream/local source bytes for intake.",
        "Fixture provenance ambiguity stops intake. Each closure path must be a tracked regular non-symlink file; no network or dependency installation during checker execution."
      ],
      "substantive_authorization_rationale": "Source already fixes both the test behavior and exact schema identity. Tracking the four exact host input files is the smallest closure; per-run generation adds a protoc/generator dependency chain and build bootstrap adds unrelated firmware dependencies. Trusted checker constants bind full upstream commit, Git blobs, selector and SHA256, so mutable manifest labels cannot self-authorize coordinated schema replacement.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Production source, original eight-case corpus, schema bytes, upstream selector or active checker classification changes before execution.",
        "The selected four-file tracked fixture requires an unapproved dependency, fake schema, runtime include replacement, or changes outside its declared closure."
      ],
      "authorization_snapshot_provenance": "Independent Glyph Work-Order Curator reviewed live configurator 4351b951916abbfbcaffec6f4512571a17d15ca5, immutable Planner 4d6f0ed73bff368546c983c6fe2fcf3be7bcef3e, exact production sources and observed dependency hashes on 2026-09-21. Immutable receipt c8d77f0197ae44545c26953c2dca9b160b2f505a records this disposition. Owner campaign explicitly requests these separate bounded cycles; no hardware evidence is supplied.",
      "automated_validation": [
        "Verify intake upstream blob identities and bytes; exact generated extent20; same eight 0/10/11/20 write/read results under sanitizers using exact production source.",
        "Clean checkout direct checker PASS and configurator-category PASS without .pio access. Missing config.pb.h/pb.h/proto/options; symlink; tampered bytes; wrong upstream commit/blob/hash/extent; altered selector and source-hash tamper all FAIL. No skip, demotion or weakened load-bearing gate.",
        "Run clean-checkout direct and affected configurator-category checks; manifest dependency closure, checker census, validation health, framework, agentic sequence, navigation, agent surface, Python compilation and exact diff checks; fresh independent review. Report unrelated aggregate limitations exactly; no aggregate-green claim from category PASS and no GP-VAL-011 redesign."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host/docs/checker-only work; no firmware source or build inputs change.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Keep failed implementation isolated; repair within the contract or return to Curator. Never weaken source correspondence or rewrite historical evidence.",
      "status_documentation_updates": "Update only the selected work order and synchronized current-state mirrors; preserve all other evidence. Publish reviewed implementation first, then strict DONE correspondence in a later canonical metadata snapshot.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "11df2f077466df59b192610a7b03818442d747b4",
        "reviewed_implementation_sha": "597a39545f156bd1e032edaf21085ef44589adcb",
        "prior_canonical_integration_sha": "597a39545f156bd1e032edaf21085ef44589adcb",
        "reviewed_changed_paths": [
          ".gitattributes",
          "docs/AGENT_CONTEXT.md",
          "docs/CURRENT_STATE.md",
          "docs/ROADMAP.md",
          "docs/project/ACTIVE_AGENT_QUEUE.md",
          "docs/runtime_config/custom_modifier_cache_characterization.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "tools/check_glyph_custom_modifier_cache_characterization.py",
          "tools/check_glyph_docs_agent_surface.py",
          "tools/fixtures/custom_modifier_cache_host/schema/LICENSE.nanopb.txt",
          "tools/fixtures/custom_modifier_cache_host/schema/README.md",
          "tools/fixtures/custom_modifier_cache_host/schema/config.options",
          "tools/fixtures/custom_modifier_cache_host/schema/config.pb.h",
          "tools/fixtures/custom_modifier_cache_host/schema/config.proto",
          "tools/fixtures/custom_modifier_cache_host/schema/haybox-proto.library.json",
          "tools/fixtures/custom_modifier_cache_host/schema/pb.h",
          "tools/fixtures/custom_modifier_cache_host/schema/provenance.json"
        ],
        "independent_review_provenance": "Independent reviewer glyph_planner approved exact 597a39545f156bd1e032edaf21085ef44589adcb with no findings after clean-clone direct/configurator/docs checks and exact attribute negative controls. Independent Curator confirmed narrowly guarded six-file gitattributes coupling is within the existing order. Root independently reviewed exact diff and reran framework/sequence/direct characterization.",
        "validation_provenance": "Clean checkout without .pio passes exact-production eight 0/10/11/20 sanitizer cases and missing/tamper/symlink/untracked/wrong upstream/schema/selector/source negative controls; configurator6/6 and docs2/2 PASS with canonical and all isolated proofs MATCH. Manifest closure, census204, health43, framework, sequence, navigation, agent-surface, Python and diff PASS. Firmware, original GP-CONFIG-011 fixture/harness, GP-CONFIG-010 candidate/artifact and GP-VAL-011 unchanged. Exact REVIEW snapshot published and live verified before this completion metadata. No full-aggregate or hardware acceptance claim."
      },
      "stop_conditions": [
        "Any unresolved behavior/source decision or excluded scope is required.",
        "Any exact-source, validation, independent-review or publication gate fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-012",
      "title": "Characterize invalid buttons through exact decoder and mask callers",
      "status": "REVIEW",
      "branch": "codex/gp-config-012-button-mask-characterization",
      "objective": "Finish exact schema/decoder/helper and complete production caller characterization for zero and invalid button values, producing a decision-ready source matrix without selecting firmware policy.",
      "why_this_matters": "Nanopb accepts BTN_UNSPECIFIED=0 and Pico make_button_mask shifts by button-1; the audit observed UBSan negative shift while physical reachability remains untested.",
      "hardware_risk": "H1",
      "behavioral_claim": "Record decode acceptance, enum-read validity, helper behavior and validation paths separately. No invalid-binding repair or reject/no-binding/ignore policy is selected.",
      "scope": "Add exact-production host harness/checker/fixtures and report under tools and docs. Reuse GP-VAL-026 tracked fixture; add exact config.pb.c plus Nanopb pb_decode.c/h and pb_common.c/h with immutable package/source identity, licenses, hashes and declared manifest dependencies. Produce caller matrix and source-census drift checks; no firmware edit.",
      "explicit_excluded_scope": "No gameplay, routing, source-owned table, neutral Profile schema, runtime-loaded config, active publication, device/WebSerial/protobuf/backend write, persistence, flashing automation, Nunchuk acceptance or root-cause change. GP-VAL-011 remains owner-deferred and nonexecutable. Preserve GP-CONFIG-010 exact candidate f4771e17430fd1ea3f1e3e5339a83dfe648290a3 and UF2 9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a: no edit, rebuild, rebase, integration, or coupling. No make_button_mask repair, SetConfig invalid-binding policy, defaults/remaps/binding change, physical crash or exploitability claim. Any subsequent H2/H3 repair needs separate Curator order.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "At 4351b951916abbfbcaffec6f4512571a17d15ca5, HAL/pico/include/util/state_util.hpp make_button_mask lacks zero validation; get_button/set_button exclude BTN_UNSPECIFIED. Callers: CustomControllerMode::SetConfig modifier and combo masks, setup_mode_activation_bindings, backend_config_from_buttons. SetConfig/defaults/persisted/menu paths require explicit characterization; AVR helper is a separate non-Glyph target. Nanopb upstream tag0.4.9.1 resolves to cad3c18ef15a663e30e3e43e3a752b66378adec1; pb.h Git blob10249bb651f72e17f2789c435edf0dfd398d2183. GregTurbo/HayBox-proto db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8, unchanged selector GregTurbo/HayBox-proto#db4e2f6 in config/glyph/env.ini. config.proto SHA256 2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b; config.options 6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805; generated config.pb.h 532f7ac324a57895caf82950ee36c6900d883a42188e5d6bbc2d3507318538f3; Nanopb pb.h a2ecdca9fdaeef5f4972ed983540c0d6fb0a5c402a2e0b0349d7e1bc5e188d29. CustomModeConfig.modifiers extent is20. Generated header identifies nanopb0.4.9.1/header40 and observed library metadata0.4.91; observed correspondence, not transitive reproducible-build proof.",
      "dependencies_prerequisites": [
        "OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017. Do not implement, probe, build, activate or merge this item. The retained contract is historical scope/authority only; resumption requires explicit owner direction followed by fresh Curator reauthorization against live source. REVIEW is a parked TODO, not approval pending for integration.",
        "GP-VAL-026 exact tracked closure integrated; existing source and schema identities preserved.",
        "Decoder fixture extension must have independently verified provenance and share the same pinned Nanopb/schema closure; serialize edits with GP-CONFIG-013."
      ],
      "substantive_authorization_rationale": "OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017. Do not implement, probe, build, activate or merge this item. The retained contract is historical scope/authority only; resumption requires explicit owner direction followed by fresh Curator reauthorization against live source. REVIEW is a parked TODO, not approval pending for integration. Prior authorization rationale retained: This is bounded H1 source/host evidence collection over an already demonstrated undefined operation. The investigation is authorized to resolve reachability facts, not choose externally visible invalid-binding semantics. Ignoring zero from [0,BTN_LF1] may activate behavior; get_button alone is insufficient policy authority.",
      "mechanical_activation_conditions": [
        "GP-VAL-026 is DONE in the freshly live-verified canonical queue with strict completion correspondence, and its current direct checker plus configurator category pass in a clean checkout without .pio.",
        "git diff --quiet 4351b951916abbfbcaffec6f4512571a17d15ca5 HEAD -- include src HAL config platformio.ini builder_scripts succeeds; the exact schema hashes and upstream selector stated in this contract match. These critical production/build inputs must remain byte-identical before activation.",
        "Permitted intervening changes are GP-VAL-026 host fixture/checker/dependency/docs metadata, GP-CONFIG-012/013 exact decoder fixture and characterization/checker/docs metadata, and reviewed queue/receipt/runway metadata only; no product, firmware, schema, dependency selector, protocol or source-policy drift. Shared fixture edits are serialized.",
        "GP-CONFIG-010 remains separately pinned at its existing exact candidate/artifact pair; this activation neither depends on nor changes its hardware result. No other writer is publishing the canonical branch."
      ],
      "invalidation_conditions": [
        "Any critical source/schema/dependency-selector difference from the exact authorization base, or any intervening change outside the named host/docs/control-plane deltas, requires CURATION_REQUIRED before execution.",
        "Any unresolved product, source-authority, architecture or behavior choice appears; missing fixture provenance or failed exact-source correspondence is not permission to infer authority.",
        "The work would change a forbidden boundary, GP-VAL-011, GP-CONFIG-010 source/artifact, or the preserved GP-CONFIG-011 historical observations."
      ],
      "authorization_snapshot_provenance": "Independent Glyph Work-Order Curator reviewed live configurator 4351b951916abbfbcaffec6f4512571a17d15ca5, immutable Planner 4d6f0ed73bff368546c983c6fe2fcf3be7bcef3e, exact production sources and observed dependency hashes on 2026-09-21. Immutable receipt c8d77f0197ae44545c26953c2dca9b160b2f505a records this disposition. Owner campaign explicitly requests these separate bounded cycles; no hardware evidence is supplied. Owner-directed parking recorded by independent Curator on 2026-09-21 against live b0f8133b10abe11865dc6887f29a2c90f4aaad8a; see GLYPH-UD-017 and docs/project/DEFERRED_CONFIG_WORK_2026-09-21.md. Warning source/cause and exact flagged item identities remain UNKNOWN; no observed automatic approval rejection is asserted.",
      "automated_validation": [
        "Exact production helper/caller bodies and actual decoder: empty,zero,first1,last60,61..64,65,max decoder-representable values,negative/overlong/malformed varints,packed/repeated encodings and mixed zero+valid. Separate decoder rejection, numeric storage, enum sanitizer failure, invalid shift and defined completion in independent processes.",
        "Matrix: caller -> input source -> pre-helper validation -> decoded/configured zero reachability -> observed host result -> physical reachability status. Inspect every production caller, HandleSetConfig, compiled defaults, Persistence::LoadConfig, Glyph setup and menu/watchdog/config-producing paths.",
        "Preserve valid mask bit positions. Exact-source/caller-census/fixture tamper and omission FAIL; affected transaction/rebinding/config checks PASS. Physical reachability remains UNKNOWN unless directly proven, hardware NOT_TESTED; host UB is not a physical symptom.",
        "Run clean-checkout direct and affected configurator-category checks; manifest dependency closure, checker census, validation health, framework, agentic sequence, navigation, agent surface, Python compilation and exact diff checks; fresh independent review. Report unrelated aggregate limitations exactly; no aggregate-green claim from category PASS and no GP-VAL-011 redesign."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host/docs/checker-only work; no firmware source or build inputs change.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Keep failed implementation isolated; repair within the contract or return to Curator. Never weaken source correspondence or rewrite historical evidence.",
      "status_documentation_updates": "Keep REVIEW / OWNER_DEFERRED / NONEXECUTABLE until explicit owner resumption and fresh Curator reauthorization. Preserve prior full scope, validation, source and hardware requirements without treating mechanical prerequisite satisfaction as resumption. TODO/custody record: docs/project/DEFERRED_CONFIG_WORK_2026-09-21.md. Prior publication requirements retained: Update only the selected work order and synchronized current-state mirrors; preserve all other evidence. Publish reviewed implementation first, then strict DONE correspondence in a later canonical metadata snapshot.",
      "done_evidence": "Exact reviewed implementation, reproducible host evidence and required checks PASS; prior live canonical integration followed by separate strict completion correspondence.",
      "stop_conditions": [
        "OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017. Do not implement, probe, build, activate or merge this item. The retained contract is historical scope/authority only; resumption requires explicit owner direction followed by fresh Curator reauthorization against live source. REVIEW is a parked TODO, not approval pending for integration.",
        "Any unresolved behavior/source decision or excluded scope is required.",
        "Any exact-source, validation, independent-review or publication gate fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-013",
      "title": "Characterize USB default no-write and downstream selection paths",
      "status": "REVIEW",
      "branch": "codex/gp-config-013-usb-default-characterization",
      "objective": "Finish exact getter/caller/decoder characterization for missing and invalid USB defaults, producing no-write and downstream-read evidence without selecting fallback policy.",
      "why_this_matters": "The default getter writes only for index>0 and <=backend count; its production caller declares usb_backend_config uninitialized and reads backend_id. SetConfig checks a different default index.",
      "hardware_risk": "H1",
      "behavioral_claim": "Sentinel tests prove no-write branches and exact valid copying; uninitialized production reads remain separate source facts unless reliable memory-sanitizer evidence exists. No USB behavior repair or physical symptom is claimed.",
      "scope": "Exact-production getter/caller harnesses bound to current source, decoder fixtures, checker and complete initialization/caller matrix/report. Reuse GP-VAL-026; if GP-CONFIG-012 decoder closure is absent, add the identical pinned config.pb.c and Nanopb pb_decode.c/h,pb_common.c/h with the same provenance/license/hash/dependency rules. Serialize shared fixture edits.",
      "explicit_excluded_scope": "No gameplay, routing, source-owned table, neutral Profile schema, runtime-loaded config, active publication, device/WebSerial/protobuf/backend write, persistence, flashing automation, Nunchuk acceptance or root-cause change. GP-VAL-011 remains owner-deferred and nonexecutable. Preserve GP-CONFIG-010 exact candidate f4771e17430fd1ea3f1e3e5339a83dfe648290a3 and UF2 9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a: no edit, rebuild, rebase, integration, or coupling. No getter/caller initialization fix, USB fallback/reject/retain choice, persisted schema/configuration mutation, or firmware edit. Subsequent H2/H3 repair needs separate Curator order.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "At 4351b951916abbfbcaffec6f4512571a17d15ca5, HAL/pico/src/comms/backend_init.cpp get_usb_backend_config_default has zero/out-of-range no-write paths; initialize_backends reads uninitialized usb_backend_config.backend_id and later may copy default_mode_config. config/glyph/common/src/config.cpp registers the getter; defaults use USB index1; Config.default_usb_backend_config generated uint8 limit is separate from protobuf uint32 wire type. HandleSetConfig validates default_backend_config, not this field. Nanopb upstream tag0.4.9.1 resolves to cad3c18ef15a663e30e3e43e3a752b66378adec1; pb.h Git blob10249bb651f72e17f2789c435edf0dfd398d2183. GregTurbo/HayBox-proto db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8, unchanged selector GregTurbo/HayBox-proto#db4e2f6 in config/glyph/env.ini. config.proto SHA256 2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b; config.options 6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805; generated config.pb.h 532f7ac324a57895caf82950ee36c6900d883a42188e5d6bbc2d3507318538f3; Nanopb pb.h a2ecdca9fdaeef5f4972ed983540c0d6fb0a5c402a2e0b0349d7e1bc5e188d29. CustomModeConfig.modifiers extent is20. Generated header identifies nanopb0.4.9.1/header40 and observed library metadata0.4.91; observed correspondence, not transitive reproducible-build proof.",
      "dependencies_prerequisites": [
        "OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017. Do not implement, probe, build, activate or merge this item. The retained contract is historical scope/authority only; resumption requires explicit owner direction followed by fresh Curator reauthorization against live source. REVIEW is a parked TODO, not approval pending for integration.",
        "GP-VAL-026 integrated exact tracked closure; GP-CONFIG-012 is not a hard prerequisite because the identical decoder closure may be added here.",
        "Source getter/caller bodies must be compiled directly or byte-exact extracted with mechanical current-source equality checks."
      ],
      "substantive_authorization_rationale": "OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017. Do not implement, probe, build, activate or merge this item. The retained contract is historical scope/authority only; resumption requires explicit owner direction followed by fresh Curator reauthorization against live source. REVIEW is a parked TODO, not approval pending for integration. Prior authorization rationale retained: All useful no-write, decode, initialization and propagation facts can be established without hardware or selecting policy. Rejecting config, choosing one fallback backend or retaining prior backend differ externally. Zero-initializing alone is not presumed neutral because COMMS_BACKEND_UNSPECIFIED reaches actual dispatch branches.",
      "mechanical_activation_conditions": [
        "GP-VAL-026 is DONE in the freshly live-verified canonical queue with strict completion correspondence, and its current direct checker plus configurator category pass in a clean checkout without .pio.",
        "git diff --quiet 4351b951916abbfbcaffec6f4512571a17d15ca5 HEAD -- include src HAL config platformio.ini builder_scripts succeeds; the exact schema hashes and upstream selector stated in this contract match. These critical production/build inputs must remain byte-identical before activation.",
        "Permitted intervening changes are GP-VAL-026 host fixture/checker/dependency/docs metadata, GP-CONFIG-012/013 exact decoder fixture and characterization/checker/docs metadata, and reviewed queue/receipt/runway metadata only; no product, firmware, schema, dependency selector, protocol or source-policy drift. Shared fixture edits are serialized.",
        "GP-CONFIG-010 remains separately pinned at its existing exact candidate/artifact pair; this activation neither depends on nor changes its hardware result. No other writer is publishing the canonical branch."
      ],
      "invalidation_conditions": [
        "Any critical source/schema/dependency-selector difference from the exact authorization base, or any intervening change outside the named host/docs/control-plane deltas, requires CURATION_REQUIRED before execution.",
        "Any unresolved product, source-authority, architecture or behavior choice appears; missing fixture provenance or failed exact-source correspondence is not permission to infer authority.",
        "The work would change a forbidden boundary, GP-VAL-011, GP-CONFIG-010 source/artifact, or the preserved GP-CONFIG-011 historical observations."
      ],
      "authorization_snapshot_provenance": "Independent Glyph Work-Order Curator reviewed live configurator 4351b951916abbfbcaffec6f4512571a17d15ca5, immutable Planner 4d6f0ed73bff368546c983c6fe2fcf3be7bcef3e, exact production sources and observed dependency hashes on 2026-09-21. Immutable receipt c8d77f0197ae44545c26953c2dca9b160b2f505a records this disposition. Owner campaign explicitly requests these separate bounded cycles; no hardware evidence is supplied. Owner-directed parking recorded by independent Curator on 2026-09-21 against live b0f8133b10abe11865dc6887f29a2c90f4aaad8a; see GLYPH-UD-017 and docs/project/DEFERRED_CONFIG_WORK_2026-09-21.md. Warning source/cause and exact flagged item identities remain UNKNOWN; no observed automatic approval rejection is asserted.",
      "automated_validation": [
        "Empty list; index0; first1; distinct last/count; count+1; representable extremes; malformed/overflow wire encodings. Sentinel destination stays byte-identical on no-write paths; full CommunicationBackendConfig valid entry copied exactly. Do not manufacture uninitialized reads in harness.",
        "Matrix every getter/callback caller and destination initialization; actual registrations/custom callback API contract; compiled defaults, persisted LoadConfig, SetConfig, menu/default updates and watchdog scratch; downstream backend_id/default_mode_config and other reads.",
        "Exact body, caller census and decoder/schema tamper FAIL. Host results separated from physical UNKNOWN. Record explicit reject/fallback/retain alternatives unless authoritative source unambiguously resolves them.",
        "Run clean-checkout direct and affected configurator-category checks; manifest dependency closure, checker census, validation health, framework, agentic sequence, navigation, agent surface, Python compilation and exact diff checks; fresh independent review. Report unrelated aggregate limitations exactly; no aggregate-green claim from category PASS and no GP-VAL-011 redesign."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host/docs/checker-only work; no firmware source or build inputs change.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Keep failed implementation isolated; repair within the contract or return to Curator. Never weaken source correspondence or rewrite historical evidence.",
      "status_documentation_updates": "Keep REVIEW / OWNER_DEFERRED / NONEXECUTABLE until explicit owner resumption and fresh Curator reauthorization. Preserve prior full scope, validation, source and hardware requirements without treating mechanical prerequisite satisfaction as resumption. TODO/custody record: docs/project/DEFERRED_CONFIG_WORK_2026-09-21.md. Prior publication requirements retained: Update only the selected work order and synchronized current-state mirrors; preserve all other evidence. Publish reviewed implementation first, then strict DONE correspondence in a later canonical metadata snapshot.",
      "done_evidence": "Exact reviewed implementation, reproducible host evidence and required checks PASS; prior live canonical integration followed by separate strict completion correspondence.",
      "stop_conditions": [
        "OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017. Do not implement, probe, build, activate or merge this item. The retained contract is historical scope/authority only; resumption requires explicit owner direction followed by fresh Curator reauthorization against live source. REVIEW is a parked TODO, not approval pending for integration.",
        "Any unresolved behavior/source decision or excluded scope is required.",
        "Any exact-source, validation, independent-review or publication gate fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-014",
      "title": "Repair custom-modifier cache to generated schema capacity",
      "status": "REVIEW",
      "branch": "codex/gp-config-014-modifier-cache-capacity",
      "objective": "Remove schema-valid 11..20 modifier cache overflow while preserving existing masks, ordered modifier interpretation, valid arithmetic, combo/digital behavior and protobuf/persistence ABI.",
      "why_this_matters": "Completed GP-CONFIG-011 proves the ten-entry mask cache is indexed using the generated20-entry modifier count in SetConfig and output processing. This is repair authority, not repeated discovery.",
      "hardware_risk": "H3",
      "behavioral_claim": "Use a named fixed20-mask capacity compile-time equal to the exact generated member extent; initialize the existing config pointer to null. Refuse counts>20 before SetConfig touches accepted base/config/cache state and before processing any custom output or cached modifier read. Preserve existing null no-output path and every valid0..20 ordering/mask/arithmetic result. No truncation, clamp, reordered application, new binding policy or schema ABI change.",
      "scope": "include/modes/CustomControllerMode.hpp, src/modes/CustomControllerMode.cpp, exact-production repair harness/checker, separately identified repair fixture/report, candidate-local hardware protocol and direct source/manifest/census/health correspondence. Review precise RAM/map delta. Existing GP-CONFIG-011 historical fixture and failure observations remain immutable and authenticated; current load-bearing entry enforces explicitly recognized repaired source with passing repair coverage, adding separately named gate if needed.",
      "explicit_excluded_scope": "No gameplay, routing, source-owned table, neutral Profile schema, runtime-loaded config, active publication, device/WebSerial/protobuf/backend write, persistence, flashing automation, Nunchuk acceptance or root-cause change. GP-VAL-011 remains owner-deferred and nonexecutable. Preserve GP-CONFIG-010 exact candidate f4771e17430fd1ea3f1e3e5339a83dfe648290a3 and UF2 9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a: no edit, rebuild, rebase, integration, or coupling. No src/core/mode_selection.cpp change; no combo capacity, schema count reduction, zero-button policy, multiplier/sign/clamp repair, priority, route, or GP-CONFIG-010 coupling. No hardware evidence or merge authorization is supplied by curation.",
      "touched_planes": [
        "firmware runtime",
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At 4351b951916abbfbcaffec6f4512571a17d15ca5, CustomControllerMode.hpp has _modifier_button_masks[10]; SetConfig and UpdateAnalogOutputs index through modifiers_count; generated schema permits20. Existing source fixes order and interpretation. Local impossible-count refusal before mutation/indexing follows already accepted GP-CONFIG-010 safety invariant without changing any schema-valid count. Nanopb upstream tag0.4.9.1 resolves to cad3c18ef15a663e30e3e43e3a752b66378adec1; pb.h Git blob10249bb651f72e17f2789c435edf0dfd398d2183. GregTurbo/HayBox-proto db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8, unchanged selector GregTurbo/HayBox-proto#db4e2f6 in config/glyph/env.ini. config.proto SHA256 2844d8fc8c78c9fbed00a6954a13d9826f4634cac152f8a9a707666f47bb893b; config.options 6a53dc93a79027669a3990c3a785e386e02e063c1f3438744aac49c3ad074805; generated config.pb.h 532f7ac324a57895caf82950ee36c6900d883a42188e5d6bbc2d3507318538f3; Nanopb pb.h a2ecdca9fdaeef5f4972ed983540c0d6fb0a5c402a2e0b0349d7e1bc5e188d29. CustomModeConfig.modifiers extent is20. Generated header identifies nanopb0.4.9.1/header40 and observed library metadata0.4.91; observed correspondence, not transitive reproducible-build proof.",
      "dependencies_prerequisites": [
        "OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017. Do not implement, probe, build, activate or merge this item. The retained contract is historical scope/authority only; resumption requires explicit owner direction followed by fresh Curator reauthorization against live source. REVIEW is a parked TODO, not approval pending for integration.",
        "GP-VAL-026 integrated exact host fixture closure; existing generated member extent20 and production code unchanged before activation.",
        "GP-CONFIG-010 remains separate. Owner campaign explicitly requests an independent modifier candidate despite pending010; its PASS/build cannot transfer.",
        "Use source-authority/firmware-safety specialist plus fresh independent post-implementation reviewer. Preserve unknown zero-binding, override-sign, arithmetic/clamp and USB policies."
      ],
      "substantive_authorization_rationale": "OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017. Do not implement, probe, build, activate or merge this item. The retained contract is historical scope/authority only; resumption requires explicit owner direction followed by fresh Curator reauthorization against live source. REVIEW is a parked TODO, not approval pending for integration. Prior authorization rationale retained: Current schema already permits20 modifiers; internal cache capacity10 contradicts that source contract. Enlarging only internal cache preserves valid configuration and ABI. Out-of-schema count refusal before state mutation/indexing cannot reject any schema-valid count. Explicit null initialization makes the existing null no-output contract deterministic. Guard pointer alias/in-place count changes before processing; this authorizes no fallback or binding semantics. H3 adds exact build/custody/manual acceptance before integration.",
      "mechanical_activation_conditions": [
        "GP-VAL-026 is DONE in the freshly live-verified canonical queue with strict completion correspondence, and its current direct checker plus configurator category pass in a clean checkout without .pio.",
        "git diff --quiet 4351b951916abbfbcaffec6f4512571a17d15ca5 HEAD -- include src HAL config platformio.ini builder_scripts succeeds; the exact schema hashes and upstream selector stated in this contract match. These critical production/build inputs must remain byte-identical before activation.",
        "Permitted intervening changes are GP-VAL-026 host fixture/checker/dependency/docs metadata, GP-CONFIG-012/013 exact decoder fixture and characterization/checker/docs metadata, and reviewed queue/receipt/runway metadata only; no product, firmware, schema, dependency selector, protocol or source-policy drift. Shared fixture edits are serialized.",
        "GP-CONFIG-010 remains separately pinned at its existing exact candidate/artifact pair; this activation neither depends on nor changes its hardware result. No other writer is publishing the canonical branch."
      ],
      "invalidation_conditions": [
        "Any critical source/schema/dependency-selector difference from the exact authorization base, or any intervening change outside the named host/docs/control-plane deltas, requires CURATION_REQUIRED before execution.",
        "Any unresolved product, source-authority, architecture or behavior choice appears; missing fixture provenance or failed exact-source correspondence is not permission to infer authority.",
        "The work would change a forbidden boundary, GP-VAL-011, GP-CONFIG-010 source/artifact, or the preserved GP-CONFIG-011 historical observations."
      ],
      "authorization_snapshot_provenance": "Independent Glyph Work-Order Curator reviewed live configurator 4351b951916abbfbcaffec6f4512571a17d15ca5, immutable Planner 4d6f0ed73bff368546c983c6fe2fcf3be7bcef3e, exact production sources and observed dependency hashes on 2026-09-21. Immutable receipt c8d77f0197ae44545c26953c2dca9b160b2f505a records this disposition. Owner campaign explicitly requests these separate bounded cycles; no hardware evidence is supplied. Owner-directed parking recorded by independent Curator on 2026-09-21 against live b0f8133b10abe11865dc6887f29a2c90f4aaad8a; see GLYPH-UD-017 and docs/project/DEFERRED_CONFIG_WORK_2026-09-21.md. Warning source/cause and exact flagged item identities remain UNKNOWN; no observed automatic approval rejection is asserted.",
      "automated_validation": [
        "Compile exact SetConfig/digital/analog source under address/undefined/bounds sanitizers;0,10,11,20 PASS;21 and maximal injected count rejected before cache writes/reads. Cover fresh/null,valid->invalid->valid,unchanged accepted state after invalid SetConfig,pointer-alias/in-place count mutation,index19,mixed masks and noncommutative order with representable arithmetic.",
        "Demonstrate valid combo/digital/axis semantics unchanged. Exact source hash, generated capacity mismatch and unrecognized-source mutations FAIL. Authenticate original GP-CONFIG-011 record separately; never silently replace historical11/20 FAIL with PASS or demote the current load-bearing checker.",
        "Run affected transaction/rebinding/custom-mode checks and current load-bearing gate; manifest/census/health/framework/sequence/navigation/surface; fresh source-authority and firmware-safety review; exact diff.",
        "Commit exact candidate before pio run -e glyph_mk6; documented quiet fallback only if canonical invocation unavailable. Review RAM/map delta; preserve/readback-hash exact UF2 under candidate-SHA/artifact-SHA custody; publish pinned candidate and separate source-free canonical hardware-pending metadata. STOP before merge until exact candidate/artifact physical PASS."
      ],
      "canonical_build": "pio run -e glyph_mk6",
      "expected_artifact": ".pio/build/glyph_mk6/firmware.uf2",
      "manual_acceptance": "REQUIRED",
      "manual_acceptance_protocol_reference": "docs/agent_framework/GP_CONFIG_014_HARDWARE_PROTOCOL.md",
      "manual_acceptance_protocol_version": "GP_CONFIG_014_HW_V1",
      "hardware_evidence_contract_reference": "docs/agent_framework/HARDWARE_EVIDENCE.md",
      "hardware_evidence_contract_version": "GLYPH_HARDWARE_EVIDENCE_V2",
      "rollback_recovery": "Keep independent candidate unmerged; preserve prior accepted rollback firmware and010 bytes. Manual protocol must bind exact candidate/artifact and verify ordinary layout/connections plus source-derived0/10/11/20 custom cases/order,neutral/release,reconnect/power cycle. Record required owner custom configuration as explicit physical prerequisite, never invent it or automate device write. On anomaly stop and restore accepted artifact; process actual evidence separately.",
      "status_documentation_updates": "Keep REVIEW / OWNER_DEFERRED / NONEXECUTABLE until explicit owner resumption and fresh Curator reauthorization. Preserve prior full scope, validation, source and hardware requirements without treating mechanical prerequisite satisfaction as resumption. TODO/custody record: docs/project/DEFERRED_CONFIG_WORK_2026-09-21.md. Prior publication requirements retained: Publish only exact candidate branch then separate docs-only hardware-pending metadata from fresh configurator; candidate source never enters canonical before exact PASS. Record artifact custody/protocol and precise untested gaps. Keep010 unchanged, Nunchuk NOT_TESTED and root cause unproven.",
      "done_evidence": "Exact-source sanitizer PASS, canonical build and RAM/map proof, independent source/safety review, pinned candidate and preserved exact UF2, candidate-local manual protocol, genuine exact-pair physical PASS, safe exact-candidate integration then separate strict completion correspondence.",
      "stop_conditions": [
        "OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017. Do not implement, probe, build, activate or merge this item. The retained contract is historical scope/authority only; resumption requires explicit owner direction followed by fresh Curator reauthorization against live source. REVIEW is a parked TODO, not approval pending for integration.",
        "Any valid modifier ordering/mask/arithmetic, combo/digital, binding, routing, ABI, schema or persistence behavior would change.",
        "Any need to couple mode_selection.cpp or010, choose zero/USB/override/clamp semantics, weaken historical/current checker correspondence, or cross forbidden publication/write boundaries.",
        "Missing build/review/custody/protocol or physical evidence stops at its exact gate; no merge before exact candidate/artifact physical PASS."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-010",
      "title": "Repair mode-activation capacity correspondence",
      "status": "LOCAL_ACCEPTANCE_PENDING",
      "branch": "glyph/gp-config-010-mode-activation-capacity",
      "objective": "Eliminate the active 13-entry configuration flowing through a 10-slot mode-activation cache while preserving every current default mode, order, binding, and selection behavior.",
      "why_this_matters": "The exact production setup and selection loops index mode_activation_masks through game_mode_configs_count; the current default count is 13 and the cache has 10 slots, creating source-proven out-of-bounds writes and reads.",
      "hardware_risk": "H3",
      "behavioral_claim": "A named fixed activation-mask capacity of 30 is compile-time proven equal to the exact current generated Config.game_mode_configs extent without sizing storage from a Config object; all current 13 entries remain represented in order, and setup/selection refuse counts above capacity before indexing. The persisted Config/protobuf layout and every current valid binding remain unchanged.",
      "scope": "Change mode-selection cache capacity and bounds enforcement, add an exact-production host sanitizer harness and compile-time correspondence checks, add a candidate-local manual protocol, update directly affected source-bound docs/checkers, run the canonical build, and publish only an exact candidate/artifact pair for hardware testing.",
      "explicit_excluded_scope": "No Config/protobuf/schema or persistence-layout change; no new, removed, or reordered mode; no binding, gameplay, routing, runtime-loaded configuration, storage, device-write, Nunchuk, or root-cause change; no merge before exact-snapshot physical PASS.",
      "touched_planes": [
        "firmware runtime",
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At live configurator 37b6d7e5573703f9854674e424b526cf7f5dd1a8, config/glyph/common/include/glyph_overrides.hpp sets game_mode_configs_count to 13, src/core/mode_selection.cpp declares mode_activation_masks[10], and both setup_mode_activation_bindings and select_mode index that cache to the supplied/configured count. The build-resolved generated Config has game_mode_configs[30]. Existing source and defaults own the valid behavior; no new mode semantics are selected.",
      "dependencies_prerequisites": [
        "Preserve all 13 current default entries, order, activation bindings, backend applicability, and selection behavior.",
        "Use a named fixed 30-entry mask capacity with a compile-time equality proof against the generated member extent; do not restore the reverted Config-member sizeof expression or allocate a Config-sized object.",
        "Review the exact RAM/map delta and keep GP-VAL-011 plus all forbidden runtime/device-write paths unchanged."
      ],
      "substantive_authorization_rationale": "The memory-safety defect, valid configured behavior, generated capacity, and ABI-preserving repair architecture are source-proven. Refusing impossible above-capacity counts before indexing is a bounded safety invariant and requires no game-semantic or product choice. H3 governs candidate handling and merge, not whether the exact repair may be implemented.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The current default count, generated Config member extent, or exact setup/selection bodies change materially before implementation.",
        "The repair would require a protobuf/schema/persistence ABI change, a mode/binding semantic change, or a different active publication path.",
        "Exact-production sanitizer coverage, canonical build, independent firmware-safety review, artifact custody, or hardware protocol cannot be completed."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator 37b6d7e5573703f9854674e424b526cf7f5dd1a8 and Planner GP-CONFIG-010 at ebdb7f3d728320c4c6ee229f040cb98a29a8b524. Receipt b2ff798314c9e42f189f280fc1413d6601cef127 records READY after direct source verification of the 13-to-10 mismatch and the generated 30-entry Config extent.",
      "automated_validation": [
        "Compile exact production mode-selection bodies with the named 30-entry capacity and prove equality to the current generated member extent plus fit of the 13-entry default.",
        "Exercise counts 0, 10, 11, 13, 30, and above 30 plus selection indices 0 through 12 under ASan/UBSan or equivalent; prove no out-of-bounds access and no valid-entry ordering/binding drift.",
        "Run focused mode/config checks, RAM/map review, pio run -e glyph_mk6, relevant manifest/census/health gates, framework/navigation/surface gates, exact diff review, a bounded source-authority/firmware-safety specialist, and fresh independent review.",
        "Commit the exact candidate before build; preserve and hash the exact UF2; publish the candidate ref and hardware handoff without merging."
      ],
      "canonical_build": "pio run -e glyph_mk6",
      "expected_artifact": ".pio/build/glyph_mk6/firmware.uf2",
      "manual_acceptance": "REQUIRED",
      "manual_acceptance_protocol_reference": "docs/agent_framework/GP_CONFIG_010_HARDWARE_PROTOCOL.md",
      "manual_acceptance_protocol_version": "GP_CONFIG_010_HW_V1",
      "hardware_evidence_contract_reference": "docs/agent_framework/HARDWARE_EVIDENCE.md",
      "hardware_evidence_contract_version": "GLYPH_HARDWARE_EVIDENCE_V2",
      "rollback_recovery": "Do not merge or substitute rebuilt bytes without exact PASS. On any regression or FAIL, restore the accepted configurator artifact/source and publish the exact failed evidence through the hardware lane.",
      "status_documentation_updates": "Record the source-proven capacity repair, exact candidate/artifact identity, and hardware-pending state; preserve Nunchuk NOT_TESTED, root cause unproven, and all runtime-loaded/device-write non-claims.",
      "done_evidence": "Exact source diff, sanitizer proof, canonical build, independent review, preserved UF2 identity, candidate-local protocol, exact-snapshot hardware PASS, and strict completion correspondence before DONE.",
      "stop_conditions": [
        "Any valid current mode, order, binding, or selection behavior would change.",
        "Any schema/persistence ABI, gameplay semantic, runtime-loaded config, device-write, or forbidden active-publication scope appears.",
        "Any build, review, custody, protocol, or exact-snapshot hardware requirement fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": false,
      "candidate_git_sha": "f4771e17430fd1ea3f1e3e5339a83dfe648290a3",
      "candidate_base_configurator_sha": "28426e4ba4763a99f0ca13491c023af77665c79c",
      "firmware_artifact_build_path": ".pio/build/glyph_mk6/firmware.uf2",
      "preserved_firmware_artifact_locator": "local_backups/hardware-artifacts/f4771e17430fd1ea3f1e3e5339a83dfe648290a3/9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a/firmware.uf2",
      "firmware_artifact_sha256": "9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a",
      "hardware_evidence_record": "git-json:6c858622657b70c8dc964db0cd4ffaac6ca4fb9f:docs/calibration/fixtures/gp_config_010_hardware_evidence_2026-09-21.json",
      "hardware_result": "INCONCLUSIVE",
      "hardware_evidence_gaps": [
        "Run GP_CONFIG_010_HW_V1 with an active test configuration containing all 13 current default mode entries in source order so indices 0 through 12 are physically exercisable.",
        "Record expected and observed mode/backend behavior for mandatory indices 3 through 12; indices 0 through 2 need not be inferred as coverage for the missing rows.",
        "Exercise and record at least one valid entry beyond the historical 10-slot boundary, including indices 10, 11, and 12 as required by the full protocol.",
        "After all 13 mandatory rows pass, execute and record the protocol's final ordinary disconnect, power-cycle/reconnect, default-profile, representative-operation, display/menu, and connection-stability regression checks."
      ]
    },
    {
      "id": "GP-VAL-024",
      "title": "Declare the manifest helper closure",
      "status": "DONE",
      "branch": "glyph/gp-val-024-manifest-helper-closure",
      "objective": "Make the advertised validation manifest runnable from a clean clone by declaring the table-replacement checker's direct extractor helper.",
      "why_this_matters": "The clean-clone manifest preflight currently returns SETUP_FAILURE because table_replacement_contract imports tools/extract_glyph_identity_runtime_tables.py but does not declare it.",
      "hardware_risk": "H0",
      "behavioral_claim": "The table_replacement_contract manifest entry declares its exact current extractor dependency; checker command, applicability, historical classification, load-bearing state, and validation semantics remain unchanged.",
      "scope": "Add only the missing source_dependencies entry and refresh deterministic manifest/census/health consequences and direct contract coverage.",
      "explicit_excluded_scope": "No checker logic, runner/isolation, applicability, classification, workflow, build, firmware/runtime, source-owned value, artifact, device, hardware, or GP-VAL-011 change.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "A clean local clone at 37b6d7e5573703f9854674e424b526cf7f5dd1a8 reproduces SETUP_FAILURE: missing direct helper dependencies for table_replacement_contract: tools/extract_glyph_identity_runtime_tables.py. The checker imports that tracked helper and the manifest currently lists only tools/generate_source_owned_runtime_config.py.",
      "dependencies_prerequisites": [
        "Preserve the current 42-entry manifest and table_replacement_contract command/classification.",
        "Keep the direct-helper closure rule and canonical proof unchanged."
      ],
      "substantive_authorization_rationale": "This is a mechanical declaration of a source-proven existing import, not a validation policy or product change.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The checker removes or changes the direct extractor import before implementation.",
        "The repair would require runner, classification, applicability, checker semantic, or GP-VAL-011 changes."
      ],
      "authorization_snapshot_provenance": "Curator reproduced the clean-clone failure at live base 37b6d7e5573703f9854674e424b526cf7f5dd1a8 and reviewed Planner GP-VAL-024 at ebdb7f3d728320c4c6ee229f040cb98a29a8b524. Receipt b2ff798314c9e42f189f280fc1413d6601cef127 records READY.",
      "automated_validation": [
        "A clean clone passes python3 tools/run_glyph_runtime_config_validation.py --check-manifest --json after the declaration.",
        "Removing or misspelling the extractor dependency fails preflight.",
        "Run manifest, census, health, framework, navigation, agent-surface, syntax, diff, and fresh independent review gates."
      ],
      "canonical_build": "NOT_REQUIRED: H0 manifest metadata only; build and product inputs remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the declaration if it does not exactly match the direct import; do not weaken dependency-closure validation.",
      "status_documentation_updates": "Record clean-clone manifest closure only; make no aggregate-isolation, product, build, or hardware claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "fd6044109ce3af2311c32875979dc37849dd75be",
        "reviewed_implementation_sha": "d8220daee328eae517c5ed10a1a78460b4f46ba7",
        "prior_canonical_integration_sha": "38d57ee2ced51a37475e299fb08a368877a0e507",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer Lorentz PASSed the exact manifest-only diff, confirming the direct extractor import, unchanged command/applicability/classification/load-bearing semantics, and no excluded scope.",
        "validation_provenance": "Manifest preflight, checker census (203 entries), validation health (42 manifest entries and 38 current load-bearing checks), framework, agentic sequence, navigation, agent-surface, Python compilation, and git diff --check PASS. Aggregate runtime validation remains unavailable on the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ preflight defect; no aggregate-green claim is made. No firmware build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "Any checker semantic, applicability, classification, runner, workflow, build, firmware, or GP-VAL-011 change is required.",
        "Clean-clone manifest validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-025",
      "title": "Bind Python validation to the invoking interpreter",
      "status": "DONE",
      "branch": "glyph/gp-val-025-invoking-python",
      "objective": "Prevent ambient PATH resolution from substituting a different program for every manifest Python checker.",
      "why_this_matters": "The aggregate preserves ambient PATH, executes manifest command[0] through execvpe, and accepts zero exit without output correspondence; its own source states interpreter identity is not claimed.",
      "hardware_risk": "H1",
      "behavioral_claim": "Inside the existing isolated launch path, every exact manifest command beginning with portable token python3 executes through the aggregate process's sys.executable; manifest bytes and all non-Python command semantics remain unchanged.",
      "scope": "Change the aggregate runner and its focused adversarial checker/fixtures, documentation, and deterministic manifest/census/health consequences only.",
      "explicit_excluded_scope": "No generic OS, Git, package, or executable trust policy; no manifest checker semantic or command-vector change; no workflow, firmware, artifact, device, hardware, or GP-VAL-011 work.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At 37b6d7e5573703f9854674e424b526cf7f5dd1a8, tools/run_glyph_runtime_config_validation.py base_environment preserves PATH, _exec_checker uses os.execvpe(command[0], command, env), and the source comment explicitly says interpreter identity is not claimed. Manifest entries use exact portable python3 tokens.",
      "dependencies_prerequisites": [
        "Preserve GP-VAL-010 exact manifest vector validation and current isolation/environment normalization.",
        "Preserve direct checker usability and every non-Python command unchanged."
      ],
      "substantive_authorization_rationale": "The trust-boundary gap and the correct identity are source-proven: the already-running aggregate interpreter is the only reviewed Python executable available without inventing a broader trust policy.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Manifest command representation or isolated-launch architecture changes materially.",
        "The implementation would alter checker arguments, outputs, classifications, timeouts, or GP-VAL-011 topology."
      ],
      "authorization_snapshot_provenance": "Curator independently inspected the exact launch path at live base 37b6d7e5573703f9854674e424b526cf7f5dd1a8 and Planner GP-VAL-025 at ebdb7f3d728320c4c6ee229f040cb98a29a8b524. Receipt b2ff798314c9e42f189f280fc1413d6601cef127 records READY.",
      "automated_validation": [
        "Prove every Python manifest entry launches with sys.executable even when PATH resolves python3 elsewhere; fail closed if the invoking interpreter identity is unusable.",
        "Reject substitute success, failure, and forged-output launchers while preserving exact real-checker exit/output behavior and the displayed portable manifest command.",
        "Run focused isolation/aggregate cases, manifest/census/health, framework, navigation, agent-surface, syntax, diff, and fresh independent review. If GP-VAL-024 is not yet DONE, separately report its exact pre-existing clean-clone manifest SETUP_FAILURE without claiming aggregate green."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host validation launcher only; firmware and build inputs remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Retain the existing fail-closed aggregate if invoking-interpreter substitution cannot preserve all current checker behavior; do not change manifest commands to bypass the issue.",
      "status_documentation_updates": "Record invoking-interpreter binding without claiming generic host/toolchain trust.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "5554328c00c43853008b3f82d4744ee08099782b",
        "reviewed_implementation_sha": "6305781ec7b4099e615f772dc979c3a493626a89",
        "prior_canonical_integration_sha": "8d1f49334973429d7b094dbcb3b86d669c465cae",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_runtime_config_validation_aggregate.py",
          "tools/run_glyph_runtime_config_validation.py"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer Linnaeus PASSed the repaired exact diff after the initial reviewer identified missing forged-output, non-invocation, failing-substitute, and unusable-interpreter coverage; the repaired focused corpus closed those findings with no scope drift.",
        "validation_provenance": "Focused aggregate validation PASSed all existing cases plus invoking-interpreter binding, forged-success output, substitute non-invocation, failing substitute, and empty/relative/missing/non-executable interpreter cases. Checker census (203), validation health (42 manifest entries and 38 current load-bearing checks), framework, navigation, agent-surface, Python compilation, and git diff --check PASS. Full aggregate remains unavailable on the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ preflight path; no aggregate-green claim is made. No firmware build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "Any checker command/semantic, workflow, product/runtime, firmware, device, hardware, or GP-VAL-011 change appears.",
        "Any Python manifest entry can still execute through ambient PATH or validation/review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-010",
      "title": "Close residual offline writer bypasses",
      "status": "DONE",
      "branch": "glyph/gp-src-010-offline-writer-closure",
      "objective": "Apply the existing exact-target, containment, symlink/alias, and atomic-replacement invariant to three remaining source-owned output paths.",
      "why_this_matters": "The artifact installer, candidate-preparation writer, and generator-modes prepare CLI still call mkdir/write_text directly and can bypass GP-SRC-005's shared output boundary.",
      "hardware_risk": "H1",
      "behavioral_claim": "The installer and candidate-preparation operations use one high-level atomic API limited to the exact inert repository target; generator-modes prepare uses the existing isolated-system-temporary output validator and atomic writer. The low-level primitive retains a closed call-site census, and accepted output bytes remain identical.",
      "scope": "Change tools/install_generated_source_owned_runtime_config.py, tools/prepare_source_owned_candidate_branch.py, tools/generate_source_owned_generator_modes.py, the shared source_owned_generator_modes output seam, focused filesystem tests, directly affected docs, and deterministic manifest/census/health consequences.",
      "explicit_excluded_scope": "No new output root or install target; no generated value, ownership, authority, active source/table, runtime publication, build, persistence, device-write, or hardware change.",
      "touched_planes": [
        "source-owned configuration",
        "generated tables/artifacts",
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At 37b6d7e5573703f9854674e424b526cf7f5dd1a8 the three named tools directly call Path.mkdir/Path.write_text, while tools/source_owned_generator_modes.py provides validate_offline_output_target and atomic writer helpers already authorized and enforced by GP-SRC-005.",
      "dependencies_prerequisites": [
        "Preserve GP-SRC-005's exact inert install exception separately from its isolated temporary output policy; do not combine them into a wider root policy.",
        "Preserve byte-identical generated content, require the accepted JSON suffix for prepared packets, reject output/input overwrite or observable aliasing, and do not widen authorized roots.",
        "Fresh mkdtemp-only intermediate writes may remain internal only with an explicit non-user-selected rationale; every user-selected final output uses the reviewed high-level policy."
      ],
      "substantive_authorization_rationale": "The bypasses and approved shared policy are source-proven. Reusing the existing invariant requires no new output, source-authority, product, or runtime decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any named writer is removed or its authorized destination/content contract changes materially.",
        "Implementation would require a new durable root, repository install target, active source, or generated semantic change."
      ],
      "authorization_snapshot_provenance": "Curator independently verified the three direct write_text paths against GP-SRC-005 at live base 37b6d7e5573703f9854674e424b526cf7f5dd1a8 and Planner GP-SRC-010 at ebdb7f3d728320c4c6ee229f040cb98a29a8b524. Receipt b2ff798314c9e42f189f280fc1413d6601cef127 records READY.",
      "automated_validation": [
        "Reject repository targets outside the exact inert exception, non-temporary prepare outputs, wrong roots/suffixes, traversal, target and ancestor symlinks, observable hard-link/inode aliases including input overwrite, existing unsafe targets, and partial replacements.",
        "Accept the exact inert repository target only for the first two operations and isolated system-temporary JSON destinations for prepare; prove byte-identical output, failure atomicity, and a closed low-level call-site census.",
        "Run all three wrapper checkers, shared output-boundary tests, manifest/census/health, framework/navigation/surface, syntax, diff, and fresh independent review. If GP-VAL-024 is not yet DONE, report its exact pre-existing clean-clone manifest SETUP_FAILURE without claiming aggregate green."
      ],
      "canonical_build": "NOT_REQUIRED: H1 offline writer hardening only; active source and firmware remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Keep the existing operations unchanged if they cannot reuse the exact shared policy without widening it; never add a direct-write exception.",
      "status_documentation_updates": "Record shared offline writer closure only; retain all active-source/runtime/device/hardware non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "575ed922ffb2812a1838e645e636fe2ac59abae9",
        "reviewed_implementation_sha": "6e616fa8adb78b98865e7bd1db1766ac0f56464f",
        "prior_canonical_integration_sha": "3ca30cc8cd39dc69c94ba4120812fae00735d5d4",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/generated_source_owned_artifact_install.md",
          "docs/runtime_config/generated_source_owned_generator_modes.md",
          "tools/check_glyph_generated_source_owned_artifact_install.py",
          "tools/check_glyph_source_owned_generator_modes.py",
          "tools/generate_source_owned_generator_modes.py",
          "tools/generate_source_owned_runtime_config.py",
          "tools/install_generated_source_owned_runtime_config.py",
          "tools/prepare_source_owned_candidate_branch.py",
          "tools/source_owned_generator_modes.py"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer Pauli PASSed the repaired exact diff, confirming all three named writers and the legacy explicit install route through the reviewed shared APIs, adversarial filesystem coverage, byte preservation, and no excluded scope.",
        "validation_provenance": "Focused generator-modes (6 positive / 16 negative), candidate-generation, and inert-artifact-install checkers PASS; adversarial coverage includes hard links, symlink ancestors, input aliases/overwrite, and injected replacement failure. Checker census 203, validation health 42 manifest entries and 38 current load-bearing checks, source sync, framework, navigation, agent surface, Python compilation, and git diff --check PASS. Aggregate runtime validation remains unavailable on the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ preflight defect; no aggregate-green claim is made. No firmware build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "Any new output root, install exception, generated semantic, active source, runtime, device, or hardware scope is needed.",
        "Any direct bypass remains or focused validation/review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-012",
      "title": "Bind CI build provenance to a clean tracked worktree",
      "status": "DONE",
      "branch": "glyph/gp-prov-012-clean-worktree-gates",
      "objective": "Fail the build workflow when persistent tracked or firmware-relevant untracked divergence exists immediately before the build or after it and before postprocessing.",
      "why_this_matters": "The current checkout gate binds HEAD and glyph_nuker but accepts untracked source; no worktree-integrity proof is adjacent to the build, while the sidecar still records clean GITHUB_SHA.",
      "hardware_risk": "H1",
      "behavioral_claim": "The build workflow performs exact failure-bearing persistent-divergence checks immediately before pio and immediately after build/copy before nuke. Modified/staged/hidden tracked inputs and untracked or ignored critical inputs fail; only the finite reviewed dependency/build-output set is excluded. This does not claim detection of transient changes restored between checks or race freedom during the build.",
      "scope": "Extend the provenance helper/checker and build workflow with pre/post worktree-integrity gates, update both directly affected workflow validators and provenance fixtures/docs, add disposable-repository cases, and refresh deterministic manifest/census/health consequences.",
      "explicit_excluded_scope": "No action/dependency pins, generic reproducibility or race-free claim, artifact custody/store, postprocessor byte change, firmware behavior, device, hardware, or GP-VAL-011 work.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At 37b6d7e5573703f9854674e424b526cf7f5dd1a8, verify_checkout checks only GITHUB_SHA/HEAD and glyph_nuker bytes; .github/workflows/build.yml calls it before Python/dependency setup and has no adjacent worktree check. The existing glyph_tracked_worktree_integrity seam and GP-PROV-009 define tracked/hidden/ignored critical divergence and allowed cache roots.",
      "dependencies_prerequisites": [
        "Preserve GP-PROV-009 divergence semantics, current build command, candidate/HEAD binding, postprocessor identity, and sidecar fields.",
        "Use a finite allowed generated/dependency output model; do not suppress git status or all untracked/ignored paths."
      ],
      "substantive_authorization_rationale": "The provenance gap and reusable integrity model are source-proven. Narrow pre/post persistent-divergence checks strengthen existing CI identity without changing product behavior or claiming impossible continuous monitoring.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The build workflow, provenance helper, or GP-PROV-009 integrity model changes materially.",
        "The implementation requires broad ignored-state suppression, dependency/action pinning, artifact semantics, firmware, or GP-VAL-011 work."
      ],
      "authorization_snapshot_provenance": "Curator independently inspected the live workflow and verify_checkout at 37b6d7e5573703f9854674e424b526cf7f5dd1a8 and Planner GP-PROV-012 at ebdb7f3d728320c4c6ee229f040cb98a29a8b524. Receipt b2ff798314c9e42f189f280fc1413d6601cef127 records READY with the claim narrowed to persistent divergence at the two checks.",
      "automated_validation": [
        "Reject staged/unstaged/hidden tracked source, ordinary and ignored untracked critical inputs, generated inputs, and post-build tracked mutation.",
        "Accept exact clean source plus only the enumerated dependency and build outputs; prove both workflow calls are unique, failure-bearing, and adjacent to the protected build/postprocess boundaries.",
        "Run provenance/prebuild and both workflow checkers, disposable repository cases, manifest/census/health, framework/navigation/surface, syntax, diff, pio run -e glyph_mk6, and fresh independent review."
      ],
      "canonical_build": "pio run -e glyph_mk6",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Do not publish the workflow change if clean dependency/build outputs cannot be finitely distinguished from source divergence; preserve current workflow and report the exact unresolved path class.",
      "status_documentation_updates": "Record pre/post persistent worktree-integrity proof and its transient/race non-claim; make no artifact acceptance or firmware behavior claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "92bad797c3e7e0c32dea2768e1da32870d2aecd8",
        "reviewed_implementation_sha": "244837e424c3369b7b4ba0b836ded29d67d5ba87",
        "prior_canonical_integration_sha": "83b0e69822676381f4ad432cb97907ae438a5517",
        "reviewed_changed_paths": [
          ".github/workflows/build.yml",
          "docs/runtime_config/README.md",
          "docs/runtime_config/artifact_postprocessor_provenance.md",
          "docs/runtime_config/fixtures/build_input_provenance_inventory.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/fixtures/runtime_config_validation_publication_workflow.json",
          "tools/check_glyph_artifact_postprocessor_provenance.py",
          "tools/check_glyph_artifact_postprocessor_workflow.py",
          "tools/glyph_tracked_worktree_integrity.py"
        ],
        "independent_review_provenance": "Fresh independent reviewer Epicurus PASSed the exact diff, confirming pre/post placement, finite tracked/ordinary-untracked/ignored allowlist behavior, adversarial workflow coverage, observed-only sidecar semantics, and excluded-scope preservation.",
        "validation_provenance": "Focused provenance, workflow, publication-route, build-input inventory, prebuild integrity, disposable worktree, census, health, framework, navigation, agent-surface, Python compilation, and git diff checks PASS. Canonical pio was unavailable; documented fallback build passed with RAM 78720/262144 and flash 383792/1568768. Aggregate runtime validation remains unavailable on the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ preflight defect; no aggregate-green claim is made. No firmware behavior, artifact custody, device, or hardware action occurred."
      },
      "stop_conditions": [
        "Any critical divergence can pass either gate or broad suppression is required.",
        "Any transient/race-free, reproducibility, artifact acceptance, firmware, device, hardware, or GP-VAL-011 claim enters scope.",
        "Build or review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-011",
      "title": "Characterize custom-modifier cache capacity",
      "status": "DONE",
      "branch": "glyph/gp-config-011-modifier-cache-characterization",
      "objective": "Establish exact-production host behavior and schema correspondence for the 10-slot modifier mask cache before any repair decision.",
      "why_this_matters": "CustomControllerMode writes and reads _modifier_button_masks through modifiers_count; the cache has 10 slots while the build-resolved schema permits 20 modifiers.",
      "hardware_risk": "H1",
      "behavioral_claim": "An exact-source host sanitizer harness characterizes counts 0, 10, 11, and 20 against the build-resolved generated schema and reports constructor writes and processing reads without changing or selecting firmware behavior, repair policy, modifier semantics, or reachability.",
      "scope": "Add an exact-production host/ASan characterization, bind production source and resolved schema/options identities, add fixtures/docs/checker coverage, and refresh deterministic manifest/census/health consequences.",
      "explicit_excluded_scope": "No cache/schema/count repair, SetConfig policy, modifier/gameplay decision, transport, persistence, device access, active firmware behavior, Nunchuk, root-cause, build artifact, or hardware claim.",
      "touched_planes": [
        "configurator",
        "firmware runtime",
        "docs/checkers"
      ],
      "source_authority": "At 37b6d7e5573703f9854674e424b526cf7f5dd1a8, include/modes/CustomControllerMode.hpp declares _modifier_button_masks[10], and exact production constructor/update loops index it through modifiers_count. The tracked Glyph dependency selector is GregTurbo/HayBox-proto#db4e2f6; the local build-resolved source/options are commit db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8 with CustomModeConfig.modifiers max_count:20. That resolved identity is characterization evidence, not a new durable dependency pin.",
      "dependencies_prerequisites": [
        "Preserve current CustomControllerMode and schema bytes during characterization.",
        "Bind the harness to exact production bodies and the actual build-resolved dependency identity; fail closed on drift.",
        "Route any repair through separate H2/H3 planning and curation."
      ],
      "substantive_authorization_rationale": "The mismatch is source-backed and read-only characterization resolves evidence needed for a later repair without selecting behavior. Exact dependency drift binding avoids upgrading a local cache observation into permanent schema authority.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "CustomControllerMode, the Glyph HayBox-proto selector, resolved schema/options, or current cache/count shapes change materially.",
        "The work would select a repair, SetConfig policy, modifier semantic, active firmware change, or physical reachability claim."
      ],
      "authorization_snapshot_provenance": "Curator independently verified the exact cache and loops plus the local resolved schema/options at live base 37b6d7e5573703f9854674e424b526cf7f5dd1a8 and reviewed Planner GP-CONFIG-011 at ebdb7f3d728320c4c6ee229f040cb98a29a8b524. Receipt b2ff798314c9e42f189f280fc1413d6601cef127 records characterization-only READY.",
      "automated_validation": [
        "Compile exact production CustomControllerMode bodies against the build-resolved generated schema and bind every copied dependency/source byte.",
        "Run isolated sanitizer cases for counts 0, 10, 11, and 20, separating SetConfig mask writes from processing reads while labeling injected-state reachability and physical behavior UNKNOWN.",
        "Run current SetConfig/runtime checks, dependency-resolution/provenance checks, manifest/census/health, framework/navigation/surface, syntax, diff, and fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host characterization only; production source and build inputs remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the characterization if exact production/schema correspondence cannot be maintained; do not patch the cache or schema under this work order.",
      "status_documentation_updates": "Publish bounded host observations and explicit dependency, reachability, firmware, device, and hardware non-claims; route any repair back through planning/curation.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "952e08998c0c0954773cac88d3067f0721912334",
        "reviewed_implementation_sha": "04ea022dd0eb0c6d01771f260aff6bb4af6ae104",
        "prior_canonical_integration_sha": "04ea022dd0eb0c6d01771f260aff6bb4af6ae104",
        "reviewed_changed_paths": [
          "docs/runtime_config/custom_modifier_cache_characterization.md",
          "docs/runtime_config/fixtures/custom_modifier_cache_characterization.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_custom_modifier_cache_characterization.py",
          "tools/fixtures/custom_modifier_cache_host/include/stdlib.hpp",
          "tools/fixtures/custom_modifier_cache_host/modifier_cache_harness.cpp"
        ],
        "independent_review_provenance": "Fresh independent reviewer Linnaeus PASSed the repaired exact diff, confirming the harness SHA and unique literal production include, exact eight-case characterization, schema/source bindings, and excluded-scope preservation.",
        "validation_provenance": "Focused GP-CONFIG-011 (8 cases), SetConfig rebinding (13 cases), build-input provenance, checker census 204, validation health 43 manifest entries and 39 current load-bearing checks, framework, sequence, navigation, agent surface, Python compilation, and git diff checks PASS. Aggregate runtime validation remains unavailable: its existing AGG-11 exclusion adversarial probe fails before the documented ignored .pio/libdeps preflight defect; no aggregate-green claim is made. No firmware source, build, artifact, device, hardware, or physical behavior changed."
      },
      "stop_conditions": [
        "Any cache/schema/SetConfig/runtime behavior changes.",
        "Copied models replace exact production/schema correspondence or injected host state is claimed physically reachable.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-013",
      "title": "Pin reviewed build actions to immutable commits",
      "status": "DONE",
      "branch": "glyph/gp-prov-013-pin-build-actions",
      "objective": "Replace the four current major-tag action references in the top-level firmware build workflow with live-verified immutable commits.",
      "why_this_matters": "The current workflow references two actions/checkout@v4 uses, actions/setup-python@v5, and actions/upload-artifact@v4; those tags can move while current provenance records them as unresolved.",
      "hardware_risk": "H1",
      "behavioral_claim": "Only the four existing .github/workflows/build.yml action references change: both checkout uses pin to checkout v4.4.0 commit 11d5960a326750d5838078e36cf38b85af677262, setup-python pins to v5.6.0 commit a26af69be951a213d495a4c3e4e4022e16d87065, and upload-artifact pins to v4.6.2 commit ea165f8d65b6e75b540449e92b4886f43607fa02, each with a human-readable release annotation. Step configuration and behavior remain otherwise unchanged.",
      "scope": "Change those four top-level workflow uses values, the build-input provenance mapping/fixture/docs, the exact artifact workflow checker and other directly affected workflow hash/contracts, focused tag/commit validation, and deterministic manifest/census/health consequences.",
      "explicit_excluded_scope": "No build-device-config or nested workflow, runner image, pip/PlatformIO, library/toolchain, unresolved build-device/config route, release/store/custody, firmware, device, or hardware change; do not rewrite frozen historical build-input resolution observations.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Curator live-verified official actions repositories after a restricted-path DNS failure and selected the latest patch within each currently declared major line on 2026-09-20: actions/checkout v4.4.0 -> 11d5960a326750d5838078e36cf38b85af677262; actions/setup-python v5.6.0 -> a26af69be951a213d495a4c3e4e4022e16d87065; actions/upload-artifact v4.6.2 -> ea165f8d65b6e75b540449e92b4886f43607fa02. No remembered or stale-local identity is used.",
      "dependencies_prerequisites": [
        "Preserve the exact four current action call sites, with fields/order and major-line behavior unchanged.",
        "Keep unresolved build-device-config, runner, pip, PlatformIO, library, and toolchain provenance explicitly unresolved and out of scope."
      ],
      "substantive_authorization_rationale": "Live upstream evidence closes the Planner gate, and Curator has made the required exact release/commit selection. Pinning reviewed commits strengthens provenance without a product or firmware decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any selected official tag no longer resolves to the recorded commit or upstream repository identity cannot be live verified before implementation publication.",
        "The workflow call sites or required action major lines change materially.",
        "Implementation would expand to excluded dependencies, workflows, releases, artifacts, firmware, or devices."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator 37b6d7e5573703f9854674e424b526cf7f5dd1a8, Planner GP-PROV-013 at ebdb7f3d728320c4c6ee229f040cb98a29a8b524, and live official upstream tag refs. Receipt b2ff798314c9e42f189f280fc1413d6601cef127 records READY with exact selected commits.",
      "automated_validation": [
        "Live-verify all three official tag-to-commit mappings immediately before publication and reject any mismatch.",
        "Require full 40-character pins, exact approved repositories/tags/annotations, exactly two checkout call sites and one setup/upload call site, and no other workflow delta.",
        "Run artifact and validation workflow checkers, build-input provenance inventory, manifest/census/health, framework/navigation/surface, syntax/diff, and fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H1 immutable CI action metadata only; firmware source and build inputs selected by the workflow remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Do not publish if any official tag mapping cannot be reverified or affected workflow checker cannot bind the exact pins; leave current tags and report the exact external mismatch.",
      "status_documentation_updates": "Record only the four top-level immutable action pins and preserve every excluded unresolved provenance item.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "320fd3fcfbcb810c62171a7be90c55929b6d9b9d",
        "reviewed_implementation_sha": "3c4f3a915938ee3eef8e6f7402853bd127cf3f78",
        "prior_canonical_integration_sha": "3c4f3a915938ee3eef8e6f7402853bd127cf3f78",
        "reviewed_changed_paths": [
          ".github/workflows/build.yml",
          "docs/runtime_config/build_input_provenance_inventory.md",
          "docs/runtime_config/fixtures/build_input_provenance_inventory.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_publication_workflow.json",
          "tools/check_glyph_artifact_postprocessor_workflow.py",
          "tools/check_glyph_build_input_provenance_inventory.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASSed the exact workflow/provenance diff after closing duplicate checkout, setup-python, and upload action-count findings; live official tag mappings matched the authorized commits.",
        "validation_provenance": "Artifact workflow, build-input inventory, publication workflow, historical resolution observations, census 204, validation health 43 manifest entries and 39 current load-bearing checks, framework, sequence, navigation, agent-surface, Python compilation, and git diff --check PASS. Aggregate runtime validation remains unavailable on the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ preflight defect; no aggregate-green claim is made. No firmware build, artifact, device, or hardware action occurred."
      },
      "stop_conditions": [
        "Any live upstream mapping differs from the authorized commit.",
        "Any action repository/major, workflow step configuration, excluded dependency, build/product, artifact, device, or hardware scope changes.",
        "Affected validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-009",
      "title": "Fail closed on noncanonical production authority",
      "status": "DONE",
      "branch": "glyph/gp-src-009-canonical-production-authority",
      "objective": "Prevent synthetic or otherwise unreviewed source-authority intake identities and arbitrary locator text from authorizing a production source-owned changeset.",
      "why_this_matters": "The current closed X1 mapping rejects misuse of the canonical identity or locator but returns without a blocker for wholly noncanonical identities, after which generic nonempty approval strings can authorize production emission.",
      "hardware_risk": "H1",
      "behavioral_claim": "For requested_operation production_changeset, only the exact canonical X1 intake/profile pair, GLYPH-UD-010 locator mapping, sole kX1Table ownership, and exact nine reviewed points may pass production emission. Every other identity, locator, ownership set, or production replacement fails closed. Source-equivalence proof and synthetic construction remain explicitly non-production only.",
      "scope": "Change the source-authority intake validator/manager/checker, current closed-corpus fixtures and locator documentation, and deterministic manifest/census/health consequences. Convert current synthetic production-positive cases into fail-closed coverage while preserving non-production review and source-equivalence operations.",
      "explicit_excluded_scope": "No new authority registry, generic anchor grammar, external locator support, human approval, table ownership or value, source install, active firmware, runtime publication, build, artifact, device, or hardware action.",
      "touched_planes": [
        "source-owned configuration",
        "generated tables/artifacts",
        "docs/checkers"
      ],
      "source_authority": "At c4a4ddfb82b2ec7b650202be427ef5797f5092fe, tools/source_owned_source_authority_intake.py::_closed_canonical_x1_mapping returns without a blocker for wholly noncanonical identities unless they reuse the canonical locator. The current checker constructs fixture-intake/fixture-profile with fixture-approval, owns kDefaultTable, receives zero blockers and production_emission_allowed true, and emits an EXPLICIT_OWNED_TABLE_CHANGESET. GP-SRC-008 and source_authority_intake_workflow.md authorize only the exact closed X1/GLYPH-UD-010 corpus mapping.",
      "dependencies_prerequisites": [
        "Preserve the exact current 28-table baseline and canonical X1 intake/profile, GLYPH-UD-010 locator, kX1Table, and nine-point correspondence.",
        "Preserve stale-baseline rejection, overlay/preserve semantics, downstream production gates, and source-equivalence proof as non-production evidence.",
        "Reject rather than infer every production authority outside the closed reviewed mapping."
      ],
      "substantive_authorization_rationale": "The positive gap and the only accepted production authority are directly source-proven. Enforcing the already-recorded closed corpus requires no new product, ownership, coordinate, firmware, or user decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The canonical X1 intake, GLYPH-UD-010 record, or current production operation contract changes materially.",
        "Implementation would require a generic registry, locator grammar, external authority, or newly approved production intake.",
        "The repair would change table ownership, values, active source, runtime behavior, build inputs, or hardware scope."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator c4a4ddfb82b2ec7b650202be427ef5797f5092fe and Planner candidate GP-SRC-009 at 6f7be340568a03069f605503c5ad67dc7f692bda. Receipt 92c3e6b44e66314bde72e99783b22867d3abcf7d records READY after an independent direct probe reproduced production emission from synthetic identity, locator, ownership, and replacement evidence.",
      "automated_validation": [
        "Reject every noncanonical production identity, arbitrary or mismatched locator, ownership expansion, multi-table overlay, full replacement, and changed canonical point through direct API and CLI paths.",
        "Accept the exact canonical X1 record after current-baseline substitution only as its current NO_OP production result; preserve stale-baseline rejection.",
        "Preserve source_equivalence_proof and synthetic helper construction only where they cannot set production_emission_allowed or emit a production changeset.",
        "Run intake, generator, manifest/census/health, framework, navigation, agent-surface, syntax, diff, and fresh independent review gates."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host source-authority enforcement only; active source and build inputs remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave production emission unchanged only if the closed canonical restriction cannot be implemented without broader authority design; emit no noncanonical packet as production-authorized.",
      "status_documentation_updates": "Document the closed production corpus and explicit non-production helper boundary while preserving ownership, runtime, device-write, persistence, Nunchuk, root-cause, and hardware non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "9ac48cd8eb3aa3a673ba85bdc836b664e6b913aa",
        "reviewed_implementation_sha": "70f5d3b119a2881c9cae52c2c3cf91c75b186257",
        "prior_canonical_integration_sha": "70f5d3b119a2881c9cae52c2c3cf91c75b186257",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/source_owned_source_authority_intake.json",
          "docs/runtime_config/source_authority_intake_workflow.md",
          "tools/check_glyph_source_owned_source_authority_intake.py",
          "tools/source_owned_source_authority_intake.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-SRC-009 snapshot. The review confirmed noncanonical production identities fail closed, exact canonical X1/GLYPH-UD-010/kX1Table/nine-point NO_OP remains accepted, source-equivalence helpers remain non-production, and no firmware/runtime/device/hardware scope entered the diff.",
        "validation_provenance": "Focused intake checker (104 negative, 21 positive), checker census (202 entries), validation health (41 manifest entries), framework, navigation, agent-surface, Python syntax, and git diff --check gates PASS. The aggregate runner remains unavailable because its preflight rejects the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ path; no aggregate-green claim is made. No firmware build or hardware action was required."
      },
      "stop_conditions": [
        "Any noncanonical identity or arbitrary locator can still authorize production emission.",
        "Any new authority, table ownership, coordinate, or approval meaning would be inferred.",
        "Active source, runtime, build, artifact, device, or hardware scope appears.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-021",
      "title": "Seal the CI build-to-upload command chain",
      "status": "DONE",
      "branch": "glyph/gp-val-021-ci-build-upload-chain",
      "objective": "Require the current CI build, artifact preparation, sidecar verification, and upload boundary to be exact, unique, unconditional, failure-bearing, and mutation-free after verification.",
      "why_this_matters": "Current workflow checkers accept masked or unreachable build/copy commands, decoy canonical text, post-verification artifact mutation, intervening mutation steps, extra upload actions, and extra upload fields.",
      "hardware_risk": "H0",
      "behavioral_claim": "The exact current build/mkdir/copy step, four-line nuke step, four-line sidecar step, and one current upload-artifact family step with its exact flat field map are required in order. Sidecar verification is the final executable command before the immediately following unique upload step; masking, conditional execution, decoys, duplicates, alternate uploads, extra fields, or intervening/post-verification mutation fail closed.",
      "scope": "Change the artifact workflow checker, bounded workflow-step parser/helper only where required for exact flat upload-with fields, focused in-memory adversarial cases, directly affected documentation, and deterministic manifest/census/health consequences. Preserve the tracked workflow bytes.",
      "explicit_excluded_scope": "No workflow YAML or command change, alternate publication-route claim outside the current build workflow, dependency pin, runner, build input, postprocessor behavior, artifact bytes/store/custody, firmware, device, hardware, or GP-VAL-011 work.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "At c4a4ddfb82b2ec7b650202be427ef5797f5092fe, the artifact checker protects checkout/postprocessor/sidecar operations but discovers build and copy by substring and compares only step indices. Independent mutations with pio or cp followed by || true, an unreachable build, a decoy canonical copy string, post-verify artifact append, an intervening update step, an extra upload-artifact version, and extra nested upload fields are accepted while the exact baseline also passes.",
      "dependencies_prerequisites": [
        "The exact current .github/workflows/build.yml commands, step names, default shell, environment expressions, and upload destination remain unchanged.",
        "Preserve GP-VAL-016 aggregate-command integrity and GP-VAL-019 protected artifact command enforcement.",
        "Keep parser changes limited to the reviewed workflow subset and exact flat upload-with mapping."
      ],
      "substantive_authorization_rationale": "The accepted adversarial mutations and exact current acceptance language are source-proven. This is bounded H0 checker hardening and does not select or alter CI, artifact, product, or firmware behavior.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The tracked workflow legitimately changes any protected command, step order, field map, shell, or upload shape.",
        "The repair would require editing workflow YAML, commands, publication routing, artifact bytes, or custody semantics.",
        "The shared parser cannot preserve the exact current validation and artifact workflow acceptance."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator c4a4ddfb82b2ec7b650202be427ef5797f5092fe and Planner candidate GP-VAL-021 at 6f7be340568a03069f605503c5ad67dc7f692bda. Receipt 92c3e6b44e66314bde72e99783b22867d3abcf7d records READY after independent reproduction of masked, unreachable, decoy, post-verification mutation, intervening-step, alternate-upload, and extra-field acceptance.",
      "automated_validation": [
        "Accept the exact current workflow and require the exact complete build, nuke, sidecar, and upload steps with unique names, order, command lines, supported fields, and exact flat upload-with map.",
        "Reject masking, trailing success, conditionals, functions, subshells, heredocs, duplicates, decoys, wrong source copy, post-verification mutation, intervening steps, alternate upload versions, multiple upload-family steps, and extra or changed upload fields.",
        "Require sidecar verification to be the last executable command of its step and that step to immediately precede the unique upload step.",
        "Run both workflow checkers, parser tests, provenance, manifest/census/health, framework, navigation, agent-surface, syntax, diff, and fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 checker/parser-only work; workflow, build inputs, artifact transformation, and firmware remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave the checker unchanged if the exact tracked workflow cannot pass the bounded contract; do not edit the workflow to satisfy the checker.",
      "status_documentation_updates": "Record exact failure-bearing build-to-upload enforcement only; make no artifact, release, runtime, device, or hardware acceptance claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "db2502dca3b820d8744ed6d567e5173702dc65ed",
        "reviewed_implementation_sha": "a5ec9012684d7c8e45ef4fbd57aa3a4ac755de55",
        "prior_canonical_integration_sha": "b0162560779f10e568de80cff2baf04aae0447a9",
        "reviewed_changed_paths": [
          "docs/runtime_config/artifact_postprocessor_provenance.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_artifact_postprocessor_workflow.py",
          "tools/glyph_workflow_step_contract.py"
        ],
        "independent_review_provenance": "Fresh independent initial review found a job-level continue-on-error masking gap; the repaired-scope re-review PASS confirmed exact command blocks, upload fields, failure-bearing job policy, unchanged workflow bytes, and no scope expansion.",
        "validation_provenance": "Artifact workflow, publication workflow, provenance, checker census (202 entries), framework, navigation, agent-surface, Python compilation, and git diff --check gates PASS. The aggregate runtime runner remains unavailable because preflight rejects the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ path; no aggregate-green claim is made. No firmware build or hardware action was required."
      },
      "stop_conditions": [
        "Any protected operation remains accepted when masked, unreachable, decoyed, duplicated, reordered, or followed by artifact mutation.",
        "Any alternate upload-family action or extra upload field remains accepted in the current workflow.",
        "Workflow YAML, commands, artifact bytes, publication routing, build inputs, firmware, device, hardware, or GP-VAL-011 would change.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-022",
      "title": "Validate every generated adapter mapping",
      "status": "DONE",
      "branch": "glyph/gp-val-022-adapter-mapping-correspondence",
      "objective": "Make current load-bearing source-sync gates prove every active generated table symbol/index and point/axis adapter mapping instead of validating only raw generated rows.",
      "why_this_matters": "The current extractor normalizes raw generated rows by comments and contents without parsing the active adapter macros, so compiled table-symbol correspondence can drift while extracted tables and semantic digest remain unchanged.",
      "hardware_risk": "H1",
      "behavioral_claim": "One exact load-bearing correspondence parser proves all 28 symbol-to-index aliases, the nine point indices 0 through 8, x then y axis expansion, the exact raw-array namespace, and absence of extra, duplicate, missing, or malformed adapter invocations. Active header bytes, table values, runtime publication, and firmware behavior remain unchanged.",
      "scope": "Update the extractor/current source-sync path and one focused checker or bounded host compile probe, reusing or relocating existing historical alias validation rather than creating competing authority. Add adapter fixtures/documentation and deterministic manifest/census/health consequences.",
      "explicit_excluded_scope": "No table value, symbol order, adapter mapping, generated array, active header, runtime publication, build selector, firmware behavior, device, artifact, or hardware change.",
      "touched_planes": [
        "source-owned configuration",
        "generated tables/artifacts",
        "docs/checkers"
      ],
      "source_authority": "At c4a4ddfb82b2ec7b650202be427ef5797f5092fe, extract_glyph_identity_runtime_tables.py parses generated raw rows and embedded row comments but not SOURCE_OWNED_GENERATED_TABLE or SOURCE_OWNED_GENERATED_TABLE_POINT. The current symbol-map checker anchors only kDefaultTable index 0. Mutating the live kX1Table alias from index 2 to 3 leaves extracted tables and digest unchanged. A historical non-load-bearing generator-contract checker already validates the 28 aliases but not point/axis expansion and must be reused or promoted rather than duplicated.",
      "dependencies_prerequisites": [
        "Preserve the exact current 28-symbol order, generated semantic digest, source-owned active publication, and X1/Y2 evidence.",
        "Reuse or relocate the historical alias validation into one current load-bearing authority path.",
        "Treat the gate as correspondence proof only; it must not infer table semantics or change active bytes."
      ],
      "substantive_authorization_rationale": "The blind current extraction path, exact adapter grammar, and expected current mapping are directly source-proven. Making that correspondence load-bearing is bounded H1 host validation and needs no product, table-semantic, runtime, or hardware decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The generated adapter grammar, 28-symbol order, raw-array namespace, or point/axis expansion changes materially.",
        "Implementation would duplicate a second authority source instead of reusing the canonical symbol order and current adapter source.",
        "The repair would change active source bytes, table values, mapping, runtime publication, or firmware behavior."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator c4a4ddfb82b2ec7b650202be427ef5797f5092fe and Planner candidate GP-VAL-022 at 6f7be340568a03069f605503c5ad67dc7f692bda. Receipt 92c3e6b44e66314bde72e99783b22867d3abcf7d records READY after independent kX1 index mutation reproduced unchanged extraction/digest and identified the historical non-load-bearing alias checker overlap.",
      "automated_validation": [
        "Accept the exact current adapter and prove all 28 unique symbol/index mappings plus exact point indices and x/y expansion against the current raw array.",
        "Reject swapped, duplicate, missing, extra, skipped, and out-of-range table indices; wrong point indices; point reorder; x/y inversion; wrong namespace/raw array; and malformed macro expansion.",
        "Retain current source-sync, generator, X1, and generated-baseline results while making adapter correspondence load-bearing and avoiding duplicate authority.",
        "Run focused extractor/checker, manifest/census/health, framework, navigation, agent-surface, syntax, diff, and fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host correspondence validation only; active source and build-input bytes remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave current production gates unchanged if one exact load-bearing adapter proof cannot be established without duplicate authority; do not alter the active adapter to satisfy the checker.",
      "status_documentation_updates": "Record adapter correspondence proof and historical-check reuse only; preserve all table-value, runtime, firmware, device, Nunchuk, root-cause, and hardware non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "79ac6bf1164143d6011a3dad46d047b72352b2a6",
        "reviewed_implementation_sha": "b9a0a20549909a22a1552f216ded7941b7a26a71",
        "prior_canonical_integration_sha": "b9a0a20549909a22a1552f216ded7941b7a26a71",
        "reviewed_changed_paths": [
          "docs/runtime_config/README.md",
          "docs/runtime_config/fixtures/generated_adapter_correspondence.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/generated_adapter_correspondence.md",
          "tools/check_glyph_identity_runtime_table_source_sync.py",
          "tools/check_glyph_source_owned_table_replacement_generator_contract.py",
          "tools/extract_glyph_identity_runtime_tables.py"
        ],
        "independent_review_provenance": "Fresh independent review found and repaired malformed macro-token and namespace-binding gaps; final repaired-scope re-review PASS confirmed exact alias/point grammar, canonical authority reuse, adversarial rejection, unchanged active source, and no scope expansion.",
        "validation_provenance": "Source-sync, source-owned baseline, symbol-map, checker census (202 entries), validation health, docs navigation, agent surface, Python compilation, and git diff --check PASS. Aggregate runtime validation remains unavailable because preflight rejects the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ path; no aggregate-green claim is made. No firmware build or hardware action was required."
      },
      "stop_conditions": [
        "Any current symbol/index or point/axis drift remains invisible to load-bearing source-sync validation.",
        "A competing symbol-order or table-semantic authority is introduced.",
        "Active header bytes, table values, mapping, runtime publication, firmware, device, or hardware behavior would change.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-009",
      "title": "Characterize config-menu invalid states",
      "status": "DONE",
      "branch": "glyph/gp-config-009-config-menu-invalid-state-characterization",
      "objective": "Establish bounded host-sanitizer evidence for the exact production config-menu bodies under source-supported null-mode and empty-page states, without selecting a firmware repair.",
      "why_this_matters": "Current menu source dereferences a possibly null CurrentGameMode, subtracts one from zero item counts, and accepts highlighted index equal to count before indexing, but physical reachability and device consequences are not established.",
      "hardware_risk": "H1",
      "behavioral_claim": "An exact-production host harness records whether isolated null-current-mode, production-filtered empty-page, and injected index-equals-count cases complete or trigger sanitizer/assertion failures. Index-equals-count reachability, dual-core timing, device crash/display/controller effects, and physical behavior remain UNKNOWN; undefined behavior is not relabeled deterministic firmware behavior.",
      "scope": "Literal-include and compile the exact current ConfigMenu.cpp, DefaultConfigMenu.cpp, and GlyphConfigMenu.cpp bodies once with only platform/display/backend dependency doubles, exact source/blob drift binding, ASan/UBSan or equivalent deterministic host assertions, and one subprocess per expected-failure case. Bind construction order from setup source without claiming whole-device setup timing.",
      "explicit_excluded_scope": "No firmware/UI fix, empty-page or no-mode product policy, default selection, SetConfig validation change, setup timing claim, persistence/protocol change, gameplay decision, production source edit, device access, build artifact, physical observation, or hardware claim.",
      "touched_planes": [
        "firmware runtime",
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At c4a4ddfb82b2ec7b650202be427ef5797f5092fe, ConfigMenu::HandleControls uses items_count - 1 without an empty guard, checks highlighted index with > rather than >=, then indexes; UpdateDisplay also subtracts count/offset. DefaultConfigMenu dereferences _backends[0]->CurrentGameMode()->GetConfig() unconditionally. CommunicationBackend initializes mode null, backend boot selects only when default_mode_config > 0, SetConfig accepts zero, setup constructs GlyphConfigMenu, and GlyphConfigMenu filtering can publish a zero-item page. No exact production transition to highlighted==count is proved.",
      "dependencies_prerequisites": [
        "Bind the exact current menu, backend-mode initialization, setup construction, and relevant SetConfig source correspondence.",
        "Use isolated host cases with only dependency doubles; distinguish source-supported state from injected primitive state and unknown physical reachability.",
        "Preserve GP-CONFIG-005 transaction behavior and GP-CONFIG-008 rebinding observations; any desired repair is separate H2/H3 curation."
      ],
      "substantive_authorization_rationale": "The null and empty-page states and unsafe operations are direct source facts. A narrowly bounded exact-body sanitizer characterization records evidence without choosing desired UI behavior, editing firmware, or claiming controller outcomes.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any bound menu, backend-mode, setup, or SetConfig source body changes materially before implementation.",
        "The harness would copy behavioral logic instead of compiling exact production bodies or would require a production source change.",
        "A UI policy, repair, setup-timing guarantee, physical reachability, or device-behavior claim becomes necessary."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator c4a4ddfb82b2ec7b650202be427ef5797f5092fe and Planner candidate GP-CONFIG-009 at 6f7be340568a03069f605503c5ad67dc7f692bda. Receipt 92c3e6b44e66314bde72e99783b22867d3abcf7d records READY after independent source inspection verified null/empty operations and narrowed index-equals-count to an injected case with reachability UNKNOWN.",
      "automated_validation": [
        "Compile exact production menu bodies with source/blob drift binding and isolate every sanitizer/assertion case in its own subprocess.",
        "Cover null CurrentGameMode construction; production-filtered zero game-mode and USB-option pages; fresh up/down/enter/back and UpdateDisplay on empty child pages; and synthetic highlighted==items_count with explicit non-reachability labeling.",
        "Preserve UNKNOWN for dual-core scheduling, physical reachability, performed setup/device timing, display/controller effects, and hardware behavior.",
        "Run existing SetConfig/rebinding checks, focused sanitizer harness, manifest/census/health, framework, navigation, agent-surface, syntax, diff, and fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H1 exact-production host characterization only; production source and build inputs remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the host characterization if exact production-body correspondence or isolated sanitizer evidence cannot be maintained; do not select or implement a menu repair.",
      "status_documentation_updates": "Publish only bounded host observations and explicit reachability/device unknowns; route any desired firmware behavior change through separate H2/H3 planning and curation.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "fb3d96fd8eb2f51081a663a7f729710e74e780f7",
        "reviewed_implementation_sha": "f2fd0892ea9856573c59142ca854fe56585454b8",
        "prior_canonical_integration_sha": "f2fd0892ea9856573c59142ca854fe56585454b8",
        "reviewed_changed_paths": [
          "docs/runtime_config/config_menu_invalid_state_characterization.md",
          "docs/runtime_config/fixtures/config_menu_invalid_state_characterization.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_config_menu_invalid_state_characterization.py",
          "tools/fixtures/config_menu_host/include/comms/IntegratedDisplay.hpp",
          "tools/fixtures/config_menu_host/include/comms/NeoPixelBackend.hpp",
          "tools/fixtures/config_menu_host/include/config.pb.h",
          "tools/fixtures/config_menu_host/include/config/glyph/common/include/LEDTemplates.hpp",
          "tools/fixtures/config_menu_host/include/config/glyph/common/include/display/Font4x7Fixed.h",
          "tools/fixtures/config_menu_host/include/config/glyph/common/include/icons/12x12bitmaps.hpp",
          "tools/fixtures/config_menu_host/include/core/Persistence.hpp",
          "tools/fixtures/config_menu_host/include/core/config_utils.hpp",
          "tools/fixtures/config_menu_host/include/core/mode_selection.hpp",
          "tools/fixtures/config_menu_host/include/display/ConfigMenuAssets/GlyphMenuBitmaps.h",
          "tools/fixtures/config_menu_host/include/display/DisplayMode.hpp",
          "tools/fixtures/config_menu_host/include/img/update.hpp",
          "tools/fixtures/config_menu_host/include/reboot.hpp",
          "tools/fixtures/config_menu_host/menu_harness.cpp"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS confirmed exact production menu bodies, backend/mode/SetConfig source correspondence, null-mode and empty-child sanitizer coverage including enter, explicit injected-index non-reachability labeling, and no firmware/device/hardware scope.",
        "validation_provenance": "Focused exact-production characterization (five cases), checker census (203 entries), validation health (42 manifest entries and 38 current load-bearing checks), framework, navigation, agent surface, Python compilation, and git diff --check PASS. Aggregate runtime validation remains unavailable because preflight rejects the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ path; no aggregate-green claim is made. No firmware build or hardware action was required."
      },
      "stop_conditions": [
        "Any production firmware, UI, setup, protocol, persistence, backend, display, or runtime behavior would change.",
        "Copied behavioral models replace exact production-body correspondence.",
        "Injected host state is claimed reachable or host sanitizer output is claimed as physical controller behavior.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-023",
      "title": "Make trusted comparison-base setup failure-bearing",
      "status": "DONE",
      "branch": "glyph/gp-val-023-trusted-base-command-integrity",
      "objective": "Require the current validation workflow's trusted comparison-base setup and handoff to the aggregate step to be exact, unique, unconditional within each current branch, failure-bearing, and free of intervening ref mutation.",
      "why_this_matters": "The current validator accepts masked or unreachable fetch/assert/resolve operations and an intervening step that mutates origin/configurator after verification but before the aggregate consumes the comparison ref.",
      "hardware_risk": "H0",
      "behavioral_claim": "After GP-VAL-021 integrates the shared workflow parser contract, the one current setup step must contain the exact seven-line PR/configurator conditional fetch, nonempty assertion, and rev-parse sequence; it must immediately precede the exact aggregate step, with no duplicate operations, alternate fields, trailing commands, or intervening ref mutation. The aggregate remains responsible for resolving GLYPH_CHECKER_BASE to a commit; no intrinsic immutable-remote-ref claim is added.",
      "scope": "After GP-VAL-021 is DONE, change the validation-publication checker and fixture, reuse the integrated bounded parser without broadening its supported YAML language, add focused adversarial cases and directly affected documentation, and refresh deterministic manifest/census/health consequences.",
      "explicit_excluded_scope": "No workflow YAML, fetch target, base-expression, Git credential/network behavior, aggregate runner, publication route, build, artifact, firmware, device, hardware, GP-VAL-011, or concurrent parser redesign.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "At c4a4ddfb82b2ec7b650202be427ef5797f5092fe, the validation-publication checker requires substrings for fetch, nonempty GLYPH_CHECKER_BASE, and rev-parse. Independent mutations with || true, unreachable branch operations, duplicate or wrong operations, and an intervening git update-ref step are accepted while the exact workflow passes. The current conditional PR-base versus origin/configurator setup is intentional and must be preserved exactly.",
      "dependencies_prerequisites": [
        "GP-VAL-021 is integrated and DONE with its exact current workflow/parser contract passing.",
        "The exact current trusted-base setup, PR/configurator expressions, aggregate command, default shell, and step order remain unchanged.",
        "GP-VAL-016 aggregate-command integrity remains intact and GP-VAL-011 remains owner-deferred."
      ],
      "substantive_authorization_rationale": "The defect and desired fail-closed current workflow contract are source-proven. The work should be done, but waiting for GP-VAL-021 avoids overlapping shared-parser authority; after that exact integration, activation is objective and mechanical.",
      "mechanical_activation_conditions": [
        "Canonical queue records GP-VAL-021 DONE with strict completion correspondence and its reviewed implementation integrated into live configurator.",
        "The tracked validation workflow's exact seven executable setup lines, environment expressions, aggregate command, default shell, and immediate setup-to-aggregate step order match the c4a4ddfb82b2ec7b650202be427ef5797f5092fe authorization snapshot.",
        "The integrated shared parser and both current workflow checkers accept their exact tracked workflows with no unexpected semantic or supported-shape drift."
      ],
      "invalidation_conditions": [
        "GP-VAL-021 changes the shared parser or workflow contract beyond the exact reviewed delta classes or is not integrated as reviewed.",
        "The trusted-base workflow commands, expressions, fields, shell, step order, aggregate handoff, or remote-selection policy changes materially.",
        "Implementation would require workflow, runner, network, credential, publication, build, artifact, firmware, device, hardware, or GP-VAL-011 changes."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator c4a4ddfb82b2ec7b650202be427ef5797f5092fe and Planner candidate GP-VAL-023 at 6f7be340568a03069f605503c5ad67dc7f692bda. Receipt 92c3e6b44e66314bde72e99783b22867d3abcf7d records PREAUTHORIZED after independent reproduction of masked, unreachable, duplicate, and intervening-ref-mutation acceptance and separation from GP-VAL-021's shared-parser work.",
      "automated_validation": [
        "Accept the exact current conditional setup and aggregate workflow after GP-VAL-021 integration.",
        "Reject masking, trailing success, unreachable or reordered branch operations, duplicate setup operations, wrong refs/fields/shell, functions, subshells, heredocs, continuation/comment disguise, and alternate environment expressions.",
        "Require the exact setup step to end at rev-parse and immediately precede the exact aggregate step; reject intervening or later mutation of the compared refs before aggregate execution.",
        "Run publication/artifact workflow, parser, manifest/census/health, framework, navigation, agent-surface, syntax, diff, and fresh independent review gates."
      ],
      "canonical_build": "NOT_REQUIRED: H0 checker-only work; workflow, runner, build inputs, and firmware remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Remain PREAUTHORIZED/WAITING if GP-VAL-021 is not exactly integrated or any activation condition drifts; do not edit the workflow or aggregate runner to satisfy the checker.",
      "status_documentation_updates": "Record exact failure-bearing trusted-base setup and immediate aggregate handoff only; make no remote immutability, network, credential, runner, artifact, runtime, or hardware claim.",
      "stop_conditions": [
        "Any activation condition is unsatisfied or GP-VAL-021 introduces unexpected parser/workflow drift.",
        "Any setup operation can be masked, skipped, duplicated, reordered, or separated from aggregate execution by ref mutation.",
        "Workflow, runner, network, credential, publication, build, artifact, firmware, device, hardware, or GP-VAL-011 scope appears.",
        "Focused validation or independent review fails."
      ],
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "8d4b69c64316757f1ef23532ee000fa0ac71da5f",
        "reviewed_implementation_sha": "2d95d6ba87843708aea56b98d1cd0bb563309c9d",
        "prior_canonical_integration_sha": "2d95d6ba87843708aea56b98d1cd0bb563309c9d",
        "reviewed_changed_paths": [
          "docs/runtime_config/README.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/fixtures/runtime_config_validation_publication_workflow.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_runtime_config_validation_publication_workflow.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-VAL-023 implementation snapshot. Review confirmed exact and unique jobs.validation.env base expression placement, exact seven-line setup, failure-bearing operations, immediate aggregate adjacency, rejection of masking, unreachable branches, duplicates, ref mutation, continuation splits, block/flow defaults, and no excluded scope.",
        "validation_provenance": "Focused publication-workflow checker PASS with 38 adversarial cases, checker census 203 entries, validation health 42 manifest entries and 38 current load-bearing checks, framework, navigation, agent-surface, Python compilation, and git diff --check PASS. No firmware build, artifact, device, or hardware action was required. Aggregate runtime validation remains unavailable on the pre-existing ignored nested .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ preflight defect; no aggregate-green claim is made."
      },
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-007",
      "title": "Fail closed on non-corresponding coordinate conversion",
      "status": "DONE",
      "branch": "glyph/gp-src-007-fail-closed-conversion",
      "objective": "Stop the coordinate-native bridge from emitting one fixed source-owned layout packet for materially different validated profiles.",
      "why_this_matters": "The current converter labels unrelated inputs as converted output, so review and candidate preparation can carry false input/output provenance into the source-owned generation lane.",
      "hardware_risk": "H1",
      "behavioral_claim": "Every currently generic coordinate-native profile is rejected with a stable fail-closed result instead of receiving the fixed 28-table layout. The directly supplied, already-authorized source-owned layout-spec path remains unchanged; no positive coordinate-to-table mapping is invented.",
      "scope": "Change only tools/convert_coordinate_native_profile_to_source_owned_spec.py, its bridge and candidate-preparation checker coverage, directly affected offline pipeline documentation/fixtures, and deterministic manifest, census, and health consequences. Remove positive expectations that distinct generic profiles equal the fixed fixture and bind explicit rejection.",
      "explicit_excluded_scope": "No inferred coordinate-to-table mapping, table ownership, table values, routing or tie semantics, active source mutation, firmware/runtime publication, runtime-loaded config, persistence, WebSerial/device write, protobuf write, flashing, build, artifact, or hardware action.",
      "touched_planes": [
        "generated tables/artifacts",
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At f1977c1104472d1e58733a14a11acf83fef3139b, convert_profile() validates then unconditionally returns EXPECTED_LAYOUT_SPEC; the minimal, 9-way modifier, and bridge profiles have different tables, coordinates, and routing yet emit the same digest. IMPLEMENTATION_BOUNDARY.md permits only a strict bridge subset and requires explicit full-replacement, overlay/preserve, or rejection semantics. No accepted authority maps those generic profiles to the fixed 28-table packet.",
      "dependencies_prerequisites": [
        "Start from fresh live configurator with the converter and current 28-table source authority materially unchanged.",
        "Preserve the direct authorized source-owned layout-spec generator path and current full/overlay/reject semantics.",
        "Treat every positive profile-to-source mapping as a separate substantive dependency."
      ],
      "substantive_authorization_rationale": "The false-correspondence gap is directly reproduced and the safe behavior is fully determined by existing fail-closed source-authority policy: reject uncorresponded inputs. No product, mapping, ownership, or firmware decision is needed for this bounded correction.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Accepted repository authority supplies an explicit profile-to-table mapping before implementation begins.",
        "The direct source-owned layout-spec path cannot remain accepted without changing its semantics.",
        "The repair would need active source, runtime, device, or hardware behavior."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator f1977c1104472d1e58733a14a11acf83fef3139b and Planner candidate GP-SRC-007 at 4e38028b97ed07e894368564b9f9cdce87ba9c55. Receipt 2d50315600e9528df5daa0db57c9e27b7a710732 records READY after independent reproduction and narrowing to rejection of every currently uncorresponded generic profile.",
      "automated_validation": [
        "Distinct minimal, 9-way modifier, bridge, coordinate, table, and routing inputs fail explicitly instead of emitting the fixed packet.",
        "Direct authorized layout-spec generation, generator modes, artifact-install, candidate-generation, and offline package checks retain their current valid outcomes.",
        "Run affected bridge and candidate-preparation checks, manifest semantic load, census, health, framework, navigation, agent-surface, syntax, and git diff --check.",
        "Fresh independent review confirms no mapping, ownership, active-source, runtime, or device behavior was introduced."
      ],
      "canonical_build": "NOT_REQUIRED: H1 offline converter fail-closed behavior only; firmware source and build inputs remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave the current converter unchanged if rejection cannot be isolated from the direct authorized layout-spec lane; publish no converted packet or candidate from an uncorresponded profile.",
      "status_documentation_updates": "Document that the generic bridge is fail-closed until explicit mapping and ownership authority exists; preserve every runtime, device-write, persistence, Nunchuk, and root-cause non-claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "76f6f12ffa053cbabf55d6be64b41ddb89bc292d",
        "reviewed_implementation_sha": "40e38fcf51acd43a2a2cab085cf9848ad4ee3483",
        "prior_canonical_integration_sha": "f37a0ed72bf1f211cad62a10747f5259ac96fdd5",
        "reviewed_changed_paths": [
          "docs/CURRENT_STATE.md",
          "docs/agent_framework/SUBAGENT_CONTRACTS.md",
          "docs/runtime_config/IMPLEMENTATION_BOUNDARY.md",
          "docs/runtime_config/README.md",
          "docs/runtime_config/coordinate_native_runtime_profile_contract.md",
          "docs/runtime_config/fixtures/generated_source_owned_artifact_install.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/generated_source_owned_artifact_install.md",
          "tools/check_glyph_coordinate_native_runtime_profile_contract.py",
          "tools/check_glyph_generated_source_owned_artifact_install.py",
          "tools/check_glyph_source_owned_candidate_generation.py",
          "tools/convert_coordinate_native_profile_to_source_owned_spec.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-SRC-007 snapshot. The review confirmed generic profiles fail closed with the stable source-authority reason, direct layout-spec generation remains byte-identical, candidate-preparation and artifact-install coverage are aligned, census/health are fresh, and no firmware/runtime/device/persistence/hardware claim entered the diff.",
        "validation_provenance": "Bridge, full coordinate-native contract, offline pipeline/bundle/export, candidate-generation, artifact-install, generator contract, checker census (201 entries), validation health (40 manifest entries), framework, navigation, agent-surface, Python syntax, and git diff --check gates PASS. The aggregate runner remains unavailable because its preflight rejects the pre-existing ignored nested .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ path; no aggregate-green claim is made. No firmware build or hardware action was required."
      },
      "stop_conditions": [
        "Any positive mapping, table ownership, coordinate, routing, or gameplay intent would be inferred.",
        "Any unsupported profile can still emit the fixed source-owned layout packet.",
        "Active firmware, runtime publication, persistence, device-write, or flashing scope appears.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-019",
      "title": "Make artifact provenance commands failure-bearing",
      "status": "DONE",
      "branch": "glyph/gp-val-019-artifact-command-integrity",
      "objective": "Require the checkout, postprocessor, sidecar-write, and sidecar-verification workflow operations to be exact failure-bearing commands before artifact publication.",
      "why_this_matters": "The current artifact workflow validators accept success-masked protected commands, allowing a failing identity or provenance operation to be hidden before upload.",
      "hardware_risk": "H0",
      "behavioral_claim": "The exact four current protected command lines, their order, and their supported step fields are required; masking, wrapping, duplication, conditional execution, or trailing shell content fails closed while the tracked workflow remains unchanged.",
      "scope": "Change the artifact-postprocessor workflow checker, the bounded workflow parser/helper only where useful, focused adversarial cases, and deterministic manifest/census/health consequences. Reuse the GP-VAL-016 exact-command model without broad YAML parsing.",
      "explicit_excluded_scope": "No workflow YAML or command change, runner or publication-route change, postprocessor/artifact bytes, sidecar schema, custody policy, build input, firmware, device, hardware, or GP-VAL-011 work.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "At the authorization snapshot, the four operations in .github/workflows/build.yml are discovered by substring and order checks. Independent in-memory mutations appending || true to each operation were accepted by both workflow validators. Current artifact provenance docs require checkout verification, postprocessing, sidecar writing, and sidecar verification before upload.",
      "dependencies_prerequisites": [
        "The exact current build workflow command lines and default shell contract remain unchanged.",
        "GP-VAL-016 aggregate-command integrity remains intact.",
        "The parser stays limited to the reviewed workflow subset."
      ],
      "substantive_authorization_rationale": "The defect, accepted command bytes, and required fail-closed result are source-proven. This is bounded H0 checker hardening with no product, workflow, artifact, or runtime decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The tracked workflow legitimately changes any protected command or shell/step shape.",
        "The repair would require workflow, runner, publication, artifact, or custody behavior changes.",
        "The shared parser cannot preserve current validation and artifact workflow acceptance."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator f1977c1104472d1e58733a14a11acf83fef3139b and Planner candidate GP-VAL-019 at 4e38028b97ed07e894368564b9f9cdce87ba9c55. Receipt 2d50315600e9528df5daa0db57c9e27b7a710732 records READY after independent masked-command reproduction.",
      "automated_validation": [
        "Accept the exact current workflow and require unique protected commands in exact order and supported fields.",
        "For each protected command reject || true, ; true, exit 0, subshell, function, heredoc, continuation, comment disguise, conditional, duplicate, and field-shape variants.",
        "Run both workflow checkers, manifest semantic load, census, health, framework, navigation, agent-surface, Python syntax, and git diff --check.",
        "Fresh independent review confirms workflow YAML, commands, artifact bytes, and publication behavior are unchanged."
      ],
      "canonical_build": "NOT_REQUIRED: H0 checker-only work; workflow, build inputs, artifact transformation, and firmware remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave the current checker unchanged if the exact tracked workflow cannot pass the bounded contract; do not edit the workflow to satisfy the checker.",
      "status_documentation_updates": "Record exact failure-bearing artifact command enforcement only; make no artifact acceptance or runtime claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "a861964418a9b0e84abb89b2146f8430a5e7c69b",
        "reviewed_implementation_sha": "933456a61269d47603f54b31aea33274a6381f6d",
        "prior_canonical_integration_sha": "933456a61269d47603f54b31aea33274a6381f6d",
        "reviewed_changed_paths": [
          "docs/runtime_config/artifact_postprocessor_provenance.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_artifact_postprocessor_workflow.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-VAL-019 snapshot. The review confirmed exact unique failure-bearing protected commands, rejection of family variants, masking, duplicates, trailing commands, conditionals, loops, subshells, functions, heredocs, set/trap state changes, comments, and unsupported fields, with workflow, artifact, publication, custody, sidecar, and firmware scope unchanged.",
        "validation_provenance": "Artifact workflow, provenance, publication workflow, checker census (201 entries), validation health (40 manifest entries), framework, navigation, agent-surface, Python syntax, and git diff --check gates PASS. The aggregate runner remains unavailable because its preflight rejects the pre-existing ignored nested .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ path; no aggregate-green claim is made. No firmware build or hardware action was required."
      },
      "stop_conditions": [
        "Any protected operation remains accepted with failure masking or non-exact shell content.",
        "Workflow YAML, commands, runner, publication route, artifact bytes, or custody semantics would change.",
        "Parser scope expands beyond the reviewed subset.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-011",
      "title": "Reject ignored files in source-critical paths",
      "status": "DONE",
      "branch": "glyph/gp-prov-011-ignored-critical-paths",
      "objective": "Reject ignored untracked files under the exact audited source and build-control inventory before clean firmware identity or artifact custody is accepted.",
      "why_this_matters": "An ignored source file can currently produce a clean builder identity and pass custody even though it may affect the built artifact.",
      "hardware_risk": "H1",
      "behavioral_claim": "Builder identity reports DIRTY and custody rejects when Git reports ignored untracked entries in the exact hardware-correspondence critical roots, critical files, or workflow inventory. Existing tracked-entry proof is preserved; ignored caches and custody roots outside that finite inventory remain allowed.",
      "scope": "Extend the shared worktree-integrity seam and its builder/custody consumers with the exact source-backed CRITICAL_ROOTS, CRITICAL_FILES, and .github/workflows inventory from hardware correspondence, or one exact shared classifier. Cover .gitignore, .git/info/exclude, and isolated global excludes, with deterministic fail-closed path handling and focused checkers.",
      "explicit_excluded_scope": "No complete ignored-tree fingerprint, nested-repository traversal, GP-VAL-011 isolation, timeout or concurrency redesign, dependency-resolution claim, cache cleanup, custody-root change, artifact acceptance change, firmware behavior, device, or hardware action.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "An isolated repository with ignored src/ghost.cpp yields empty porcelain, a clean builder SHA, and accepted custody. GP-PROV-009 verifies tracked entries only. tools/glyph_hardware_correspondence.py already defines the finite critical roots/files/workflow discovery policy and ignores .pio while rejecting ignored critical source.",
      "dependencies_prerequisites": [
        "Preserve GP-BUILD-001 clean/shortsha-DIRTY output and GP-PROV-009 direct tracked correspondence.",
        "Preserve GP-ART-001 custody identity, path, hash, readback, and pre/post checks.",
        "Use the exact audited finite critical inventory; do not reopen GP-VAL-011."
      ],
      "substantive_authorization_rationale": "The bypass is reproduced and the accepted hardware-correspondence classifier supplies the exact safe inventory. This intentionally supersedes GP-PROV-009 ignored-only acceptance only inside that finite critical scope while retaining its tracked semantics.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The accepted critical-path inventory changes materially before implementation.",
        "A safe implementation requires scanning caches/custody, nested repositories, or the complete ignored tree.",
        "Active/runtime source or firmware behavior would change beyond the expected embedded Git source-identity/version metadata consequence."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator f1977c1104472d1e58733a14a11acf83fef3139b and Planner candidate GP-PROV-011 at 4e38028b97ed07e894368564b9f9cdce87ba9c55. Receipt 2d50315600e9528df5daa0db57c9e27b7a710732 records READY after isolated reproduction and exact-inventory narrowing.",
      "automated_validation": [
        "Reject .gitignore, info-exclude, and isolated global-exclude entries under every exact critical inventory class; fail closed on ambiguous, symlinked, special, unreadable, or drifted discovery.",
        "Allow reviewed .pio, .platformio-home, and local_backups paths outside the critical inventory.",
        "Retain every GP-PROV-009 staged, unstaged, untracked, hidden-tracked, mode, symlink, missing, and unsupported-entry outcome.",
        "Run pre-build identity, custody, hardware-correspondence, provenance, manifest, census, health, framework, navigation, surface, git diff --check, and pio run -e glyph_mk6.",
        "Fresh independent review confirms active/runtime source and firmware behavior are unchanged apart from the expected embedded Git source-identity/version metadata consequence, and artifact policy is unchanged."
      ],
      "canonical_build": "pio run -e glyph_mk6 is required because the build identity hook changes. Cross-commit byte equality is not expected because FIRMWARE_VERSION embeds Git identity; physical hardware acceptance is not required when active/runtime source and firmware behavior are otherwise unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave builder and custody integrity unchanged if exact critical discovery, current clean build, or review fails; do not inspect or mutate ignored owner artifacts.",
      "status_documentation_updates": "Document only the finite ignored-critical-path rejection and the builder-DIRTY versus custody-reject distinction; preserve GP-VAL-011 deferral.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "a63c50d7701480fffaf75b01e2f5f10883e12aa5",
        "reviewed_implementation_sha": "46f71c956f1e6866fb9b4f325d7ca751a0741734",
        "prior_canonical_integration_sha": "d170509476ecb4bd1fa0fc371cd3c73391ad4f55",
        "reviewed_changed_paths": [
          "docs/agent_framework/SUBAGENT_CONTRACTS.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_hardware_artifact_custody.py",
          "tools/check_glyph_prebuild_git_identity.py",
          "tools/glyph_hardware_correspondence.py",
          "tools/glyph_tracked_worktree_integrity.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-PROV-011 snapshot. The review confirmed root and nested .github/workflows coverage, approved .pio/.platformio-home/.venv/local_backups exclusions, repository/info-exclude/global-exclude rejection of ignored critical inputs, preservation of tracked/correspondence behavior, and no GP-VAL-011, runtime, device, or artifact-policy expansion.",
        "validation_provenance": "Pre-build identity, artifact custody, 33 hardware-correspondence tests, build-input provenance, artifact-postprocessor provenance, checker census (201 entries), validation health (40 manifest entries), framework, navigation, agent-surface, Python syntax, git diff --check, and canonical pio run -e glyph_mk6 PASS. The first build attempt hit the host-owned PlatformIO permission boundary before compilation; the permitted repository-local PlatformIO core retry succeeded. No firmware source/runtime behavior, artifact custody, device, or hardware action changed."
      },
      "stop_conditions": [
        "Any ignored entry in the exact critical inventory is silently accepted.",
        "Allowed caches or custody roots are scanned or rejected without separate authority.",
        "GP-VAL-011, dependency resolution, artifact policy, firmware runtime, device, or hardware scope appears.",
        "Canonical build, focused validation, or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-008",
      "title": "Characterize successful SetConfig runtime rebinding",
      "status": "DONE",
      "branch": "glyph/gp-config-008-setconfig-runtime-rebinding",
      "objective": "Establish which successful persisted SetConfig values become visible immediately and which live subsystems remain cached, reselection-dependent, or boot-dependent.",
      "why_this_matters": "The transaction handler publishes the new Config, but activation masks, selected mode state, custom-mode caches, backend selection, and display/LED bindings have separate update boundaries that are not currently characterized.",
      "hardware_risk": "H1",
      "behavioral_claim": "Exact-source host characterization distinguishes in-place Config visibility from activation-mask, same-index selection, mode-object, custom-mode, backend, display, LED, reselection, and boot reconstruction boundaries. Cross-core timing, atomicity, visibility, physical behavior, and performed reboot outcomes remain UNKNOWN.",
      "scope": "Add a bounded docs/fixture/checker characterization using exact production bodies and source/blob drift binding for ConfiguratorBackend, mode_selection, InputMode, CustomControllerMode, backend_init, the setup/core loops, and NeoPixel binding. Reuse the GP-CONFIG-005 stable-address facts and characterize sequential host-visible state only.",
      "explicit_excluded_scope": "No firmware fix or source change, automatic reboot, success-response reinterpretation, backend reinitialization, persistence mechanism, protocol/schema change, game-semantic choice, device access, physical observation, cross-core guarantee, or hardware claim.",
      "touched_planes": [
        "configurator",
        "firmware runtime",
        "persistence",
        "docs/checkers"
      ],
      "source_authority": "HandleSetConfig assigns _config = candidate after successful SaveConfig. GP-CONFIG-005 proves stable embedded addresses and selected pointee visibility but explicitly disclaims successful-update rebinding. Production source separately builds activation masks, suppresses same-index reselection, configures mode singletons only on selection, caches custom masks/pointers, selects backends at boot, and updates display/LED state on distinct pointer or setup paths.",
      "dependencies_prerequisites": [
        "Bind exact production source bodies and preserve GP-CONFIG-005 rejection semantics and GP-PERSIST-002 raw-load characterization.",
        "Use sequential host characterization only; cross-core and physical outcomes remain unknown.",
        "Any desired runtime repair remains a separate H2/H3 authorization."
      ],
      "substantive_authorization_rationale": "This work records current source-derived behavior without selecting a corrective architecture or desired product behavior. The evidence boundary and non-claims are complete, so bounded H1 characterization needs no user or hardware decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any bound production body or existing SetConfig/persistence contract changes materially.",
        "Characterization would require copied behavioral models instead of exact production/source correspondence.",
        "A fix, reboot policy, protocol change, cross-core guarantee, or physical claim becomes necessary."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator f1977c1104472d1e58733a14a11acf83fef3139b and Planner candidate GP-CONFIG-008 at 4e38028b97ed07e894368564b9f9cdce87ba9c55. Receipt 2d50315600e9528df5daa0db57c9e27b7a710732 records READY after independent source-boundary verification.",
      "automated_validation": [
        "Characterize old/new activation chords, same-index suppression, different-index same-mode-object and different-mode-object selection.",
        "Characterize custom-mode reference and cached masks, generic InputMode pointer visibility, backend/default-mode boot binding, RGB pointer/count/color cache, brightness reference, remapper/display paths, and source-path boot reconstruction.",
        "Bind exact source/blob identities and fail on drift; preserve explicit UNKNOWN for cross-core atomicity, timing, visibility, performed reboot, and physical behavior.",
        "Run existing SetConfig and GET_CONFIG checks, focused characterization, manifest/census/health, framework, navigation, surface, syntax, diff, and independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H1 source/host characterization only; production and build-input bytes remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the characterization branch if exact-source correspondence or bounded host proof cannot be maintained; do not select or implement a runtime repair.",
      "status_documentation_updates": "Publish only current rebinding boundaries and explicit UNKNOWN/non-claims; route any desired runtime change back through planning and H2/H3 curation.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "327f442b9df6d0c0a15a6ff8365b3c06071323cc",
        "reviewed_implementation_sha": "7a3c242d5197ffaec3c3a4884cd62da978e955b3",
        "prior_canonical_integration_sha": "7a3c242d5197ffaec3c3a4884cd62da978e955b3",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/fixtures/setconfig_runtime_rebinding_characterization.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "docs/runtime_config/setconfig_runtime_rebinding_characterization.md",
          "tools/check_glyph_setconfig_runtime_rebinding_characterization.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on exact 7a3c242. Exact ordered 8-source list, 13-case corpus, source hashes/anchors, adversarial rejection, manifest/census/health consistency, and forbidden-scope non-claims were verified.",
        "validation_provenance": "GP-CONFIG-008 characterization PASS (13 cases); exact GP-CONFIG-005 SetConfig transaction PASS (9 cases); GP-PERSIST-002 GET_CONFIG/raw-load PASS (11 cases); census 202; health manifest 41/current load-bearing 37; framework, navigation, surface, Python syntax, and diff checks PASS. Aggregate runner stopped at documented pre-existing GP-VAL-011 preflight SETUP_FAILURE on ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/; no aggregate-green claim. No firmware build or hardware action required."
      },
      "stop_conditions": [
        "Any production firmware, protocol, persistence, reboot, backend, display, LED, or runtime behavior is changed.",
        "Copied models replace exact production/source correspondence.",
        "Cross-core, reboot-executed, device, or physical behavior is claimed as proven.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-008",
      "title": "Bind source-authority intake locators",
      "status": "DONE",
      "branch": "glyph/gp-src-008-authority-locator-binding",
      "objective": "Require the canonical production X1 intake's approval, ownership, and replacement evidence locators to resolve to the exact reviewed authority they claim.",
      "why_this_matters": "The intake currently treats arbitrary non-placeholder strings as production authority and carries an unverified approval string into emitted generator metadata.",
      "hardware_risk": "H1",
      "behavioral_claim": "Only the closed current-corpus locator mapping for the accepted X1 intake and GLYPH-UD-010 is accepted, with exact field, kX1Table ownership, and nine-point correspondence. Every unsupported, unrelated, external, compound, absent, ambiguous, or mismatched locator fails closed.",
      "scope": "Change the source-authority intake validator/checker, exact current production intake corpus contract, locator documentation, and deterministic manifest/census/health consequences. Resolve the canonical USER_DIRECTION.md#glyph-ud-010 mapping as a closed reviewed record; defer generic anchor and path:symbol grammars unless separately authorized.",
      "explicit_excluded_scope": "No inference that any existing GLYPH-UD anchor grants production authority, no new human approval, ownership expansion, coordinate change, historical intake reinterpretation, generic external locator, active source mutation, candidate build, device, or hardware action.",
      "touched_planes": [
        "source-owned configuration",
        "generated tables/artifacts",
        "docs/checkers"
      ],
      "source_authority": "review_intake() checks approval_reference, authorization_reference, and source_reference only for non-placeholder text; fake nonexistent values pass and are emitted. The exact accepted current intake uses docs/agent_framework/USER_DIRECTION.md#glyph-ud-010 for all three fields, and GLYPH-UD-010 explicitly owns kX1Table plus the exact nine ordered coordinates. Older compound locator forms are stale/noncanonical and need no reinterpretation.",
      "dependencies_prerequisites": [
        "Limit acceptance to the exact canonical X1 production intake and GLYPH-UD-010 correspondence.",
        "Preserve current 28-table baseline, overlay-preserve ownership, and downstream generator gates.",
        "Reject rather than infer every locator form outside the closed reviewed mapping."
      ],
      "substantive_authorization_rationale": "The authority record and canonical intake already contain the exact approved table and points. Resolving that one closed mapping prevents fabricated locators without interpreting generic user-direction semantics or creating new authority.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The canonical X1 intake or GLYPH-UD-010 record changes materially.",
        "Implementation requires accepting generic anchors, compound path/symbol forms, or external evidence.",
        "The repair would change ownership, coordinates, active source, or candidate behavior."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator f1977c1104472d1e58733a14a11acf83fef3139b and Planner candidate GP-SRC-008 at 4e38028b97ed07e894368564b9f9cdce87ba9c55. Receipt 2d50315600e9528df5daa0db57c9e27b7a710732 records READY after fake-locator reproduction and narrowing to the exact canonical X1/GLYPH-UD-010 mapping.",
      "automated_validation": [
        "Reject missing, duplicate, wrong, inactive, unrelated, unsupported, external, compound, escaping, absent, and ambiguous locator forms.",
        "Reject approval, ownership, table, or point mismatches; require exact kX1Table and ordered nine-point correspondence with GLYPH-UD-010.",
        "Accept the exact current X1 production intake after current-baseline substitution while stale baseline remains independently blocked.",
        "Run intake, generator modes, manifest/census/health, framework, navigation, surface, syntax, diff, and independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host source-authority validation only; active source and build inputs remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave intake emission unchanged if exact closed correspondence cannot be proved; no packet with unresolved locator authority may be emitted as production-authorized.",
      "status_documentation_updates": "Document the closed current-corpus locator contract and fail-closed boundary; preserve all ownership, hardware, runtime, device-write, and historical non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "ccb01a1ac3c8a21f69358bc345242303503ffbde",
        "reviewed_implementation_sha": "d849fbecb9712751284d9540d8c030aa30273fa7",
        "prior_canonical_integration_sha": "220b8a1d27bbd31d00f707303b546fe59b3765dd",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/source_owned_source_authority_intake.json",
          "docs/runtime_config/source_authority_intake_workflow.md",
          "tools/check_glyph_source_owned_source_authority_intake.py",
          "tools/source_owned_source_authority_intake.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on exact d849fbe. Paired identity tampering fails closed, exact GLYPH-UD-010 locator/ownership/point binding holds, stale baseline remains blocked, current-baseline substitution remains a NO_OP, and no active source/build/device/hardware scope entered the diff.",
        "validation_provenance": "Intake checker PASS (22 positive, 104 negative); generator modes PASS; census 202; health 41/current load-bearing 37; framework, navigation, docs-surface, Python syntax, and git diff --check PASS. Aggregate runner remains pre-existing SETUP_FAILURE on ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/; no aggregate-green claim. No firmware build or hardware action required."
      },
      "stop_conditions": [
        "Any unrelated user-direction entry or arbitrary existing anchor can grant authority.",
        "Any table ownership, coordinate, or approval meaning is inferred.",
        "Active source, candidate, build, device, or hardware scope appears.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-020",
      "title": "Classify build and artifact safety checkers",
      "status": "DONE",
      "branch": "glyph/gp-val-020-safety-checker-classification",
      "objective": "Make new CI, build, artifact, custody, and hardware-evidence safety checkers require manifest or explicit-exclusion classification even when they lack runtime-config vocabulary.",
      "why_this_matters": "A new safety checker can currently enter the census with no strong signal and silently fall outside both the validation manifest and exclusion set.",
      "hardware_risk": "H0",
      "behavioral_claim": "A closed source-backed signal inventory classifies checkers referencing canonical CI workflows, build declarations/hooks, artifact custody/provenance, or hardware-evidence contracts. Unclassified strong-signal checkers fail; unrelated general checkers remain census-only.",
      "scope": "Change only the static census generator, aggregate adversarial cases, deterministic census/health artifacts and directly coupled documentation. Add closed exact path/identifier signals and one synthetic unclassified probe per signal class.",
      "explicit_excluded_scope": "No discovered-checker execution expansion, semantic or transitive completeness claim, workflow/command/build input, artifact, custody, hardware-evidence policy, firmware, device, hardware, or GP-VAL-011 change.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "STRONG_RELEVANCE currently contains only runtime/source/profile vocabulary. A synthetic checker referencing only .github/workflows/build.yml receives no strong signal and escapes manifest/exclusion classification after normal census regeneration. Existing CI/build/artifact/hardware checkers are already classified; ROADMAP states census drift and explicit exclusions are load-bearing.",
      "dependencies_prerequisites": [
        "Use a closed signal vocabulary derived from current canonical paths and contract identifiers.",
        "Keep unrelated general-purpose checkers outside mandatory runtime-config classification.",
        "Validate adversarial aggregate behavior in a clean checkout without reopening GP-VAL-011."
      ],
      "substantive_authorization_rationale": "The classification hole is reproduced and the existing manifest/exclusion policy determines the safe result. This is H0 static control-plane hardening with no product, runner, workflow, or firmware judgment.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The census/manifest classification architecture changes materially.",
        "Closed signals cannot avoid classifying unrelated general-purpose checkers.",
        "The repair would execute more checkers or change workflow/build/artifact policy."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator f1977c1104472d1e58733a14a11acf83fef3139b and Planner candidate GP-VAL-020 at 4e38028b97ed07e894368564b9f9cdce87ba9c55. Receipt 2d50315600e9528df5daa0db57c9e27b7a710732 records READY after synthetic escape reproduction.",
      "automated_validation": [
        "One synthetic unclassified checker for each CI workflow, build declaration/hook, artifact custody/provenance, and hardware-evidence signal fails.",
        "Manifest or explicit-exclusion classification succeeds for each signal; an unrelated census-only checker remains allowed.",
        "Run census freshness, manifest semantic load, health, aggregate adversarial checks in a clean checkout, framework, navigation, agent-surface, syntax, diff, and independent review.",
        "Report the known shared-checkout GP-VAL-011 preflight failure truthfully without modifying or reclassifying it."
      ],
      "canonical_build": "NOT_REQUIRED: H0 static census and adversarial validation only; workflows, build inputs, and firmware remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave the current signal set unchanged if closed classification cannot avoid unrelated false positives; do not weaken manifest/exclusion enforcement.",
      "status_documentation_updates": "Document the added safety-checker signal classes only; preserve static-observation and no-completeness claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "f0a1eab7f75c6c037983e4d7290c63f800f2ede6",
        "reviewed_implementation_sha": "2759a37b8908bd68be8fd830ced313e9ec16bed2",
        "prior_canonical_integration_sha": "2759a37b8908bd68be8fd830ced313e9ec16bed2",
        "reviewed_changed_paths": [
          "docs/runtime_config/README.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_runtime_config_validation_aggregate.py",
          "tools/generate_glyph_checker_census.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-VAL-020 snapshot. The review confirmed canonical path/identifier boundaries, near-miss prefix probes, manifest/exclusion correspondence, static-only scope, and no firmware, build, hardware, or policy change.",
        "validation_provenance": "Checker census (202 entries), validation health (41 manifest entries / 42 exclusions), aggregate adversarial suite including AGG-22 safety and near-miss probes, framework, navigation, agent-surface, Python syntax, and git diff --check PASS. The direct manifest command remains a documented pre-existing SETUP_FAILURE because preflight rejects the ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ path; no aggregate-green claim is made. No firmware build or hardware action was required."
      },
      "stop_conditions": [
        "A new safety checker using a reviewed signal can remain unclassified.",
        "Unrelated general-purpose checkers are forced into the manifest without source-backed relevance.",
        "Checker execution, workflow/build/artifact policy, or GP-VAL-011 scope changes.",
        "Focused validation or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-009",
      "title": "Detect hidden-dirty source before build and custody",
      "status": "DONE",
      "branch": "glyph/gp-prov-009-hidden-dirty-source",
      "objective": "Make firmware-version identity and local artifact-custody clean-snapshot checks detect tracked working bytes or modes concealed by Git index flags or stat optimizations.",
      "why_this_matters": "A changed tracked source can currently be hidden by assume-unchanged, skip-worktree, core.filemode=false, or restored stat data, causing a clean firmware identity and allowing custody of an artifact whose checkout is not the recorded candidate.",
      "hardware_risk": "H1",
      "behavioral_claim": "Directly verify tracked HEAD/index/working correspondence. In the builder, detected tracked divergence preserves the existing shortsha-DIRTY contract; unreadable, ambiguous, unmerged, or unsupported entries fail before publish. In custody, any divergence rejects preservation both before and after copying. Clean-source firmware output and runtime behavior remain unchanged.",
      "scope": "Change only builder_scripts/arduino_pico.py, tools/glyph_hardware_artifact_custody.py, their focused isolated checkers, and a small shared helper if useful. Compare tracked entry set, stage, bytes, executable mode, regular-file type, and symlink targets without trusting porcelain optimizations; retain ordinary staged, unstaged, untracked, and ignored-only semantics. Permit only directly required provenance inventory, manifest, census, health, and narrow docs consequences.",
      "explicit_excluded_scope": "No active firmware, HAL, runtime table, build selector/dependency, workflow, artifact bytes, custody root policy, hardware evidence, device write, flashing, GP-VAL-011, GP-VAL-015 classification policy, race-free-build claim, or reproducibility claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At live configurator, builder_scripts/arduino_pico.py::git_identity and tools/glyph_hardware_artifact_custody.py::require_clean_candidate_checkout trust git status porcelain. Independent temporary repositories reproduced empty status plus clean builder identity and accepted custody for assume-unchanged, skip-worktree, core.filemode=false mode changes, and tracked file-to-symlink replacement. tools/glyph_hardware_correspondence.py provides source-backed direct byte/mode comparison precedent. DONE GP-BUILD-001 requires dirty reads to remain shortsha-DIRTY.",
      "dependencies_prerequisites": [
        "Begin from fresh live configurator and preserve GP-BUILD-001 shortsha-DIRTY semantics.",
        "Preserve GP-ART-001 custody path, hash, readback, pre/post-clean checks, and GP-VAL-015 critical-input classification.",
        "Use isolated temporary repositories only; do not mutate the canonical index flags."
      ],
      "substantive_authorization_rationale": "The failure is reproduced and the correct consumer-specific outcomes are already fixed by current contracts: builder divergence is DIRTY, while custody divergence is rejection. The bounded host/build-hook change needs no product, firmware-semantic, hardware, or external decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Current consumers already gain equivalent direct tracked-entry verification.",
        "Implementation would change firmware/runtime bytes for a clean source tree, build selectors, custody identity, or correspondence classification.",
        "A safe implementation cannot preserve ordinary dirty/untracked/ignored behavior or fail closed on unreadable and ambiguous entries."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator 64c9875c53095964ea7a540c7112104ea1a4ab8f and Planner packet glyph-portfolio-20260919-0320 candidate GP-PROV-009 at immutable commit 1c15b71d2d1658c1fde13689f925c7372308dc1d. Direct-child receipt 3a6714cc056960c0d04f69401942b50e58ce4150 records READY disposition. Independent source verification reproduced the gap and refined the bounded contract.",
      "automated_validation": [
        "Synthetic clean, ordinary staged/unstaged/untracked and ignored-only cases preserve current behavior.",
        "Synthetic assume-unchanged, skip-worktree, same-size/restored-mtime, core.filemode=false, symlink target/type, missing, unmerged, and unsupported-entry cases exercise builder DIRTY/failure and custody rejection.",
        "Fake-runner failures remain fail-closed before env.Append; custody rechecks both before and after preservation.",
        "Run focused prebuild identity and artifact custody checkers, affected provenance/manifest/census/health gates, framework/navigation/surface gates, git diff --check, and pio run -e glyph_mk6.",
        "Fresh independent review proves clean-source build output/runtime behavior and artifact bytes are unchanged."
      ],
      "canonical_build": "pio run -e glyph_mk6 is required because the build identity hook changes; no controller acceptance is required when clean-source firmware behavior is unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave the canonical builder and custody tools unchanged if tracked-entry proof, clean build, or review fails; preserve all existing artifacts and evidence.",
      "status_documentation_updates": "Document only the hidden-dirty detection and existing DIRTY-versus-reject distinction; publish DONE only after reviewed build proof and host gates.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "36e9d5f6782011b560a761c9e26b1b4937d1298f",
        "reviewed_implementation_sha": "797113740c2a601e6231642140863b26dac4aa1e",
        "prior_canonical_integration_sha": "7f9b097ba0c840afbc5f4d104dfa1756a3dce97c",
        "reviewed_changed_paths": [
          "builder_scripts/arduino_pico.py",
          "docs/runtime_config/fixtures/build_input_provenance_inventory.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "tools/check_glyph_docs_agent_surface.py",
          "tools/check_glyph_hardware_artifact_custody.py",
          "tools/check_glyph_prebuild_git_identity.py",
          "tools/glyph_hardware_artifact_custody.py",
          "tools/glyph_tracked_worktree_integrity.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-PROV-009 implementation against 36e9d5f6782011b560a761c9e26b1b4937d1298f. The review repaired and rechecked raw non-UTF-8 symlink target bytes, all executable-mode bits, direct HEAD/index/worktree correspondence, fail-closed edge cases, and scope boundaries. No firmware/runtime, build-selector, artifact-policy, hardware, device, correspondence, or reproducibility claim changed.",
        "validation_provenance": "Focused pre-build identity and artifact custody checkers PASS, including staged/unstaged/untracked/ignored-only, assume-unchanged, skip-worktree, same-size/restored-mtime, core.filemode, all executable bits, symlink/type, missing, unmerged, unsupported gitlink, and non-UTF-8 symlink cases. Build-input provenance, manifest, census199, health37, framework, navigation, agent-surface, Python syntax, and diff gates PASS. Canonical .venv/bin/python -m platformio run -e glyph_mk6 SUCCESS with RAM 78720/262144 bytes and flash 383800/1568768 bytes. Full aggregate remains FAIL/UNAVAILABLE in preflight on local ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/; clean 36e9d5f baseline reproduces PASS, so no aggregate-green claim. Feature ref and canonical integration were live-verified before this separate status publication."
      },
      "stop_conditions": [
        "Hidden divergence is silently treated as clean by either consumer.",
        "Builder changes hidden divergence from the existing -DIRTY result to an unconditional failure absent ambiguity.",
        "Custody, artifact identity, build selectors, firmware runtime, hardware evidence, GP-VAL-011, or GP-VAL-015 semantics would change.",
        "Required focused tests, canonical build, or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-016",
      "title": "Reject masked validation commands in workflow parsing",
      "status": "DONE",
      "branch": "glyph/gp-val-016-workflow-command-integrity",
      "objective": "Make validation-before-publication proof require one exact failure-bearing aggregate command instead of accepting a command whose failure can be masked by later shell content.",
      "why_this_matters": "The supported workflow parser currently swallows a same-indent sibling shell field into a block scalar and accepts any run block that merely contains the aggregate command, so a trailing true can erase its failure status.",
      "hardware_risk": "H0",
      "behavioral_claim": "Block-scalar content must be indented beyond the run field, sibling step fields resume normal parsing, malformed indentation fails closed, and the unique validation step contains exactly the aggregate command under the supported default shell contract.",
      "scope": "Change only tools/glyph_workflow_step_contract.py, the runtime-config validation publication checker and fixture, directly affected shared-parser tests, and deterministic manifest/census/health consequences. Add the fixture itself as an exact manifest dependency and exercise the artifact-postprocessor workflow checker that shares the parser.",
      "explicit_excluded_scope": "No workflow YAML, aggregate command, runner, publication route, build input, artifact, firmware, device, GP-VAL-011, or unrelated YAML-parser expansion.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "At live configurator, tools/glyph_workflow_step_contract.py consumes every six-space line after run: | and validate_current_workflow only tests aggregate membership. Independent mutation with aggregate, trailing true, and sibling shell: bash {0} was accepted while the current 15 negative cases remained green.",
      "dependencies_prerequisites": [
        "The exact current workflow and aggregate command remain unchanged.",
        "The accepted subset remains deliberately narrow; unsupported YAML shapes fail closed.",
        "Shared parser consumers must retain their current exact workflows."
      ],
      "substantive_authorization_rationale": "The defect and safe acceptance language are fully source-proven. Tightening a checker/parser without changing workflow behavior or commands is H0 and needs no product or architecture choice.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "A different shell, multi-command validation step, or workflow control-flow shape becomes necessary.",
        "Fixing the gap requires editing workflow YAML, commands, runners, or publication routing.",
        "The shared artifact workflow cannot remain accepted under the same bounded parser."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator 64c9875c53095964ea7a540c7112104ea1a4ab8f and Planner packet glyph-portfolio-20260919-0320 candidate GP-VAL-016 at immutable commit 1c15b71d2d1658c1fde13689f925c7372308dc1d. Direct-child receipt 3a6714cc056960c0d04f69401942b50e58ce4150 records READY disposition. Independent source verification reproduced the gap and refined the bounded contract.",
      "automated_validation": [
        "Accept the exact current validation and artifact-postprocessor workflows.",
        "Reject trailing true/exit 0, swallowed sibling fields, explicit shell/working-directory/env/uses/condition fields, functions, heredocs, multiline control flow, duplicate or conditional aggregate steps, and malformed indentation.",
        "Run publication-workflow and artifact-postprocessor workflow checkers, manifest semantic load, census, health, framework, navigation, surface, Python syntax, and git diff --check.",
        "Fresh independent review confirms no workflow or command bytes changed."
      ],
      "canonical_build": "NOT_REQUIRED: checker/parser-only work; build inputs and runtime code unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave the current parser/checker unchanged if exact current workflows cannot pass under the bounded contract.",
      "status_documentation_updates": "Update only directly affected checker contract prose and deterministic validation inventories; retain GP-VAL-011 deferral.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "8992f1de9c586a29cd102340f8acce49a1a54456",
        "reviewed_implementation_sha": "cccfe43f3b1ffbba82573d3583db8aeb61e2de04",
        "prior_canonical_integration_sha": "1fe57c6885e72c1054be3ae9814e912003a8646c",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/fixtures/runtime_config_validation_publication_workflow.json",
          "tools/glyph_workflow_step_contract.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-VAL-016 implementation. The review verified all requested adversarial mutations, unchanged workflow YAML and commands, shared artifact-postprocessor acceptance, focused scope, and no parser or metadata defects.",
        "validation_provenance": "Publication-workflow checker PASS with 27 negative cases, artifact-postprocessor workflow checker PASS, census199 and health37 PASS, framework/navigation/agent-surface PASS, Python AST syntax and git diff --check PASS. Full aggregate remains FAIL/UNAVAILABLE on the pre-existing ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ unsupported-path setup failure; no aggregate-green claim was made. Feature ref and canonical integration were live-verified before this separate status publication."
      },
      "stop_conditions": [
        "The aggregate can still be followed by a success-masking command.",
        "Sibling fields can still be consumed as shell text or supported-shell restrictions are weakened.",
        "Workflow YAML, commands, runners, publication routes, build inputs, firmware, artifacts, devices, or GP-VAL-011 would change.",
        "Required gates or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-007",
      "title": "Version and continuously gate host transaction stages",
      "status": "DONE",
      "branch": "glyph/gp-config-007-transaction-stage-schema-v2",
      "objective": "Turn GP-CONFIG-006 transaction-stage reporting into a versioned, internally consistent, continuously load-bearing host result contract.",
      "why_this_matters": "GP-CONFIG-006 added stage state while RESULT_SCHEMA_VERSION remained 1; validate_result_schema checks only types and accepts impossible boolean/list combinations, and no current manifest entry makes the host modules and test seam continuously load-bearing.",
      "hardware_risk": "H1",
      "behavioral_claim": "Result schema version becomes integer 2 and versions 1 or unknown are refused for new result validation. The ten named transaction stages form a duplicate-free exact prefix; transaction_stage, every stage boolean, sent, partial-write ambiguity, timestamps, and success outcome must correspond exactly. Historical GP-CONFIG-005 evidence remains historical v1 data and is not rewritten or reinterpreted.",
      "scope": "Change tools/gp_config_005_hw_test.py and focused tests; add a standard-library-only current checker for schema/order/correspondence plus exact existing COBS request bytes and transport callback boundaries; add a current host schema contract and exact manifest dependencies. Treat tools/glyph_serial_config_tool.py as an observed dependency and modify it only if required to expose/test existing boundaries. Permit deterministic census/health/framework docs consequences.",
      "explicit_excluded_scope": "No device access, protobuf schema, wire bytes, command order, automatic retry, persistence guarantee, firmware, build input, artifact, hardware evidence reinterpretation, GP-VAL-011, or compatibility claim for old local results.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At live configurator, tools/gp_config_005_hw_test.py declares RESULT_SCHEMA_VERSION = 1, records ten ordered stages plus derived booleans, and validates only types. Independent mutation with sent and response_decoded true but an empty stage list was accepted. The current validation manifest has no load-bearing entry covering gp_config_005_hw_test.py, glyph_serial_config_tool.py, or its focused suite. tools/glyph_serial_config_tool.py records the existing write/read/decode boundaries.",
      "dependencies_prerequisites": [
        "Preserve GP-CONFIG-005 exact hardware evidence as historical v1 data and GP-CONFIG-006 behavior.",
        "Keep capture and plan schema versions unchanged.",
        "The v2 stage order is prewrite_read_attempted, prewrite_read_completed, prewrite_baseline_matched, write_attempted, full_host_write_completed, awaiting_response, response_received, response_decoded, followup_read_attempted, followup_read_completed.",
        "Use project-venv protobuf tests plus a bare-python checker that does not import protobuf."
      ],
      "substantive_authorization_rationale": "The current source fixes the complete stage vocabulary, order, derived meaning, and transport boundaries. Versioning new results and rejecting impossible combinations is a bounded host evidence-integrity correction requiring no wire, firmware, device, or product decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "GP-CONFIG-006 stage names or operation order materially change before implementation.",
        "A migration/coercion policy for schema-v1 local results is needed.",
        "Implementation requires protocol, firmware, device, retry, persistence, hardware-evidence, or GP-VAL-011 changes."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator 64c9875c53095964ea7a540c7112104ea1a4ab8f and Planner packet glyph-portfolio-20260919-0320 candidate GP-CONFIG-007 at immutable commit 1c15b71d2d1658c1fde13689f925c7372308dc1d. Direct-child receipt 3a6714cc056960c0d04f69401942b50e58ce4150 records READY disposition. Independent source verification reproduced the gap and refined the bounded contract.",
      "automated_validation": [
        "Cover every legal exact prefix and reject unknown, duplicate, skipped, out-of-order, and non-prefix stage lists.",
        "Reject invalid/non-UTC timestamps; transaction_stage/list, named boolean/list, sent/full-write, partial-write ambiguity, outcome, and success/full-prefix mismatches.",
        "Prove exact encoded request bytes, command order, and callback boundaries remain unchanged.",
        "Run the bare-python load-bearing checker, project-venv GP-CONFIG suite, exact manifest/census/health checks, framework/navigation/surface, syntax, and git diff --check.",
        "Fresh independent review confirms no protobuf, wire, firmware, device, persistence, or historical-evidence reinterpretation."
      ],
      "canonical_build": "NOT_REQUIRED: host result-schema and checker work only; firmware/build inputs unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Reject the focused branch if v2 consistency cannot be enforced without wire, firmware, device, or evidence reinterpretation; leave historical records untouched.",
      "status_documentation_updates": "Document v2 as the only accepted new mechanical result schema and v1 as refused historical input; publish DONE only after reviewed continuous-gate coverage.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "01d43af2878a207f20379d46dcee62a842f31810",
        "reviewed_implementation_sha": "bf9affbb4de1fe97b0e80057daf6d95127db4d2c",
        "prior_canonical_integration_sha": "6603249af47f83b7dd4c17214529df7c127011b8",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/gp_config_007_transaction_stage_schema.md",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_gp_config_007_transaction_stage_schema.py",
          "tools/gp_config_005_hw_test.py",
          "tools/test_gp_config_005_hw_test.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-CONFIG-007 implementation. The review verified schema-v2/v1 refusal, every legal stage prefix, exact stage/boolean/write/ambiguity/timestamp correspondence, terminal outcome binding to response/error/follow-up/readback fields, unchanged COBS bytes/order/callback boundaries, adversarial coverage, manifest/census/health wiring, and excluded-scope preservation.",
        "validation_provenance": "Project-venv GP-CONFIG host suite PASS (37/37), stdlib-only GP-CONFIG-007 checker PASS, census200 and health38 PASS, framework/navigation/agent-surface PASS, Python syntax and git diff --check PASS. Publication-workflow and artifact-postprocessor workflow checkers PASS. Full aggregate remains FAIL/UNAVAILABLE on the pre-existing AGG-11 strong-signal adversarial setup defect; no aggregate-green claim was made. Feature ref and canonical integration were live-verified before this separate status publication. No firmware, build, device, artifact, or hardware action occurred."
      },
      "stop_conditions": [
        "Old v1 results are silently accepted, migrated, or reinterpreted.",
        "Any impossible prefix/boolean/final-stage/success combination validates.",
        "Transport bytes/order, protocol, device behavior, firmware, persistence, hardware evidence, or GP-VAL-011 would change.",
        "Required host tests, continuous gate, or review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-017",
      "title": "Bind current design authority to the 28-table baseline",
      "status": "DONE",
      "branch": "glyph/gp-val-017-current-28-table-authority",
      "objective": "Remove present-tense 27-table claims from current/future architecture authority and make source-derived validation reject their recurrence while preserving historical 27-table evidence.",
      "why_this_matters": "UltimateRuntimeConfigInterpreter.hpp defines the current 28-table corpus, but four current design/source-authority documents still call it 27 and existing checkers accept both those contradictions and synthetic 29-table mutations.",
      "hardware_risk": "H1",
      "behavioral_claim": "Current/future authority documents derive the table count and corpus from the canonical 28-table interpreter/extractor. The old 27-table Phase 3, Phase 7A, replacement, pre-Y2, and validation-health material remains explicitly historical or superseded, not rewritten as current evidence.",
      "scope": "Correct runtime_loaded_config_schema_design.md, firmware_interpreter_architecture_spec.md, runtime_config_storage_fallback_architecture.md, and runtime_config_storage_fallback_source_authority.md. Explicitly classify phase3_generated_constants_contract.md and phase7a_runtime_config_parser_offline_and_compiled_scaffold.md as historical/superseded without changing their parser or fixture bytes. Extend semantics and persistence/storage source-authority validation with source-derived numeric/corpus assertions and exact manifest dependencies; permit deterministic census/health/navigation consequences.",
      "explicit_excluded_scope": "No firmware, interpreter/table bytes, GCFG parser or format, runtime-loaded configuration, storage implementation, protobuf, device write, flashing, gameplay semantics, build, hardware, GP-VAL-011, or rewrite of legitimate historical 27-table evidence.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "At live configurator, src/modes/UltimateRuntimeConfigInterpreter.hpp defines kRuntimeTableCount = 28 and the current source-sync checker passes that corpus. Independent review found present-tense 27-table claims in four current docs plus mixed-current Phase 3/7A authority wording. Current semantics and storage checkers still pass after synthetic 27-to-29 mutations, proving the count is not load-bearing.",
      "dependencies_prerequisites": [
        "The canonical interpreter/extractor, 28-table source baseline, table order, and digest remain unchanged.",
        "Persistence research retains its immutable historical base and models edited storage docs as current overlays.",
        "Historical 27-table replacement, parser, pre-Y2, other-27-preserved, and validation-health evidence stays explicitly historical."
      ],
      "substantive_authorization_rationale": "The active source corpus already supplies the numeric authority; correcting stale current prose and binding checkers to it requires no new table values, gameplay semantics, storage behavior, or product decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The current interpreter/extractor corpus or count changes before implementation.",
        "A different active schema corpus, parser/wire format, storage mechanism, or game-semantic decision is proposed.",
        "Historical evidence would need alteration rather than explicit current/historical classification."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator 64c9875c53095964ea7a540c7112104ea1a4ab8f and Planner packet glyph-portfolio-20260919-0320 candidate GP-VAL-017 at immutable commit 1c15b71d2d1658c1fde13689f925c7372308dc1d. Direct-child receipt 3a6714cc056960c0d04f69401942b50e58ce4150 records READY disposition. Independent source verification reproduced the gap and refined the bounded contract.",
      "automated_validation": [
        "Current source-derived 28-table corpus and digest pass across source-sync, semantics, storage/source-authority, and persistence research checks.",
        "Synthetic 27- and 29-table mutations in every current-authority claim fail; allowlisted historical 27-table uses remain accepted and explicitly classified.",
        "Preserve Phase 3/7A parser and fixture bytes and persistence-research immutable base correspondence.",
        "Run manifest/census/health, framework/navigation/surface, Python syntax, git diff --check, and fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: current authority docs/checkers only; firmware and build inputs unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Leave current docs/checkers unchanged if source-derived assertions cannot distinguish current authority from historical 27-table evidence without changing parser or source bytes.",
      "status_documentation_updates": "Publish current 28-table authority and explicit historical classifications only after all source-sync and persistence correspondence gates pass.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "44e7a9e76228dc64f5e1b4b6fc84f26f87e976fe",
        "reviewed_implementation_sha": "58242472fb47d899bc84ab34db06803d4b778c50",
        "prior_canonical_integration_sha": "e96ae3025ccadd91e581295fadd73059b9d2c611",
        "reviewed_changed_paths": [
          "docs/generated_constants/phase3_generated_constants_contract.md",
          "docs/runtime_config/firmware_interpreter_architecture_spec.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/phase7a_runtime_config_parser_offline_and_compiled_scaffold.md",
          "docs/runtime_config/runtime_config_semantics_evaluator_bridge.md",
          "docs/runtime_config/runtime_config_storage_fallback_architecture.md",
          "docs/runtime_config/runtime_config_storage_fallback_source_authority.md",
          "docs/runtime_config/runtime_config_validation_health.md",
          "docs/runtime_config/runtime_loaded_config_schema_design.md",
          "tools/check_glyph_current_config_persistence_recovery_research.py",
          "tools/check_glyph_runtime_config_semantics_evaluator_bridge.py",
          "tools/check_glyph_runtime_config_storage_fallback.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS on the exact GP-VAL-017 implementation. The review verified the semantics bridge design document and four current authority documents bind the current source-derived 28-table corpus, the storage/fallback checker is manifest load-bearing, persistence immutable-base overlays are bounded, historical Phase 3/7A parser and fixture bytes remain unchanged, and no firmware, parser, storage, device, build, or hardware scope entered the diff.",
        "validation_provenance": "Focused source-sync PASS with table_count=28 and unchanged semantic digest b0082f068e0e552d479ec8ed8bf5867737a75a19e5e60aede55bafb72b883874; semantics bridge PASS with 10 invalid cases; storage/fallback PASS; persistence research PASS with 48 ordered steps, 15 immutable upstream blobs, and 56 negative cases; validation health PASS with census200, manifest39, and 35 current load-bearing checks; checker census, framework/navigation/agent-surface, Python syntax, and git diff --check PASS. No firmware build, artifact, device, or hardware action occurred."
      },
      "stop_conditions": [
        "Any current-authority 27/29 claim remains accepted.",
        "Legitimate historical 27-table evidence is rewritten or treated as current.",
        "Firmware, table/parser bytes, schema format, storage behavior, device path, gameplay semantics, or GP-VAL-011 would change.",
        "Required source-sync, persistence, governance gates, or review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PERSIST-002",
      "title": "Characterize CMD_GET_CONFIG raw-load failures",
      "status": "DONE",
      "branch": "glyph/gp-persist-002-get-config-raw-load-characterization",
      "objective": "Complete source-side persistence/readback characterization for HandleGetConfig and LoadConfigRaw without selecting or implementing a firmware correction.",
      "why_this_matters": "GP-CONFIG-005/006 use GET_CONFIG for prewrite and follow-up checks, but current persistence research omits that command path: HandleGetConfig ignores LoadConfigRaw's return and LoadConfigRaw ignores per-byte output-write results.",
      "hardware_risk": "H1",
      "behavioral_claim": "An exact-production host harness and research contract record current invalid-check, raw open, seek, output-write, EOF/read-error, packet ordering, end-result, validate=false, and 0/1 return behavior only. Results are characterization, not a persistence, delivery, integrity, or hardware guarantee.",
      "scope": "Add a dedicated exact-production host characterization harness/checker for HAL/pico/src/comms/ConfiguratorBackend.cpp::HandleGetConfig and HAL/pico/src/core/Persistence.cpp::LoadConfigRaw. Extend current persistence research docs/fixture/checker with exact source correspondence and directly required manifest/census/health consequences. Stubs may model only the called File, Print, PacketIO, and persistence operations.",
      "explicit_excluded_scope": "No firmware fix, protocol/error framing choice, config.bin or device access, retry, persistence guarantee, atomicity/recovery mechanism, hardware claim, device write, GP-VAL-011, or change to GP-CONFIG-005/006 host transaction behavior.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "At live configurator, HandleGetConfig validates the saved file, writes CMD_SET_CONFIG, ignores Persistence::LoadConfigRaw(_out,false), and returns packet end. LoadConfigRaw can fail open or seek, streams until a -1 sentinel, ignores each Print::write result, closes, and returns size_t 0/1. Current 48-step persistence research and fixture contain neither function, while the existing SetConfig harness replaces LoadConfigRaw with a constant stub.",
      "dependencies_prerequisites": [
        "Begin from the exact current production bodies and retain source-blob/body correspondence.",
        "Host stubs must represent only invoked interfaces and cannot claim physical filesystem, transport, or controller semantics.",
        "Any desired firmware outcome or error-framing correction is separate H2/H3 curation and hardware acceptance."
      ],
      "substantive_authorization_rationale": "The missing paths and their observable source control flow are direct facts. Bounded host characterization adds evidence without choosing a correction or changing firmware, protocol, persistence, or device behavior.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Production source or persistence interfaces materially change before implementation.",
        "Exact characterization requires a production firmware change or a choice of desired error outcome.",
        "A harness cannot preserve exact body/source correspondence without inventing hardware semantics."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator 64c9875c53095964ea7a540c7112104ea1a4ab8f and Planner packet glyph-portfolio-20260919-0320 candidate GP-PERSIST-002 at immutable commit 1c15b71d2d1658c1fde13689f925c7372308dc1d. Direct-child receipt 3a6714cc056960c0d04f69401942b50e58ce4150 records READY disposition. Independent source verification reproduced the gap and refined the bounded contract.",
      "automated_validation": [
        "Bind exact HandleGetConfig and LoadConfigRaw production bodies/blobs and fail on source drift.",
        "Cover failed initial validation/error packet/no raw load; valid check followed by raw open or seek failure; zero, partial, and failed output writes; EOF/read-error sentinel non-distinction; success command-byte/raw-payload order; packet-end success/failure propagation; validate=false; and 0/1 size_t return.",
        "Run persistence characterization/research, compiled harness, manifest/census/health, framework/navigation/surface, syntax, and git diff --check.",
        "Fresh independent review confirms no firmware, protocol, device, config.bin, recovery, or hardware claim."
      ],
      "canonical_build": "NOT_REQUIRED: exact-production host characterization only; no production or build-input bytes change.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Remove the host-only harness/research delta if exact source correspondence cannot be proved; leave firmware and current persistence behavior unchanged.",
      "status_documentation_updates": "Extend persistence research with explicit uncertainty and nonclaims; publish DONE only after exact-body and adversarial source-drift gates pass.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "c664d858ad656554d990196f3c46472ca9ebc46e",
        "reviewed_implementation_sha": "b0aa22aff74ae7711dad219330b1490e930b8714",
        "prior_canonical_integration_sha": "b0aa22aff74ae7711dad219330b1490e930b8714",
        "reviewed_changed_paths": [
          "docs/agent_framework/SUBAGENT_CONTRACTS.md",
          "docs/runtime_config/fixtures/getconfig_raw_load_characterization.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/getconfig_raw_load_characterization.md",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_getconfig_raw_load_characterization.py",
          "tools/fixtures/configurator_setconfig_host/handler_harness.cpp",
          "tools/fixtures/configurator_setconfig_host/include/host_stubs.hpp",
          "tools/fixtures/getconfig_raw_host/getconfig_handler_harness.cpp",
          "tools/fixtures/getconfig_raw_host/handler_harness.cpp",
          "tools/fixtures/getconfig_raw_host/include/CRC32.h",
          "tools/fixtures/getconfig_raw_host/include/LittleFS.h",
          "tools/fixtures/getconfig_raw_host/include/config.pb.h",
          "tools/fixtures/getconfig_raw_host/include/host_stubs.hpp",
          "tools/fixtures/getconfig_raw_host/include/pb_arduino.h",
          "tools/fixtures/getconfig_raw_host/include/pb_decode.h",
          "tools/fixtures/getconfig_raw_host/include/pb_encode.h",
          "tools/fixtures/getconfig_raw_host/include/stdlib.hpp"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope review PASS: explicit validate=false and packet-end failure coverage, exact source hashes/literal includes, host-only non-claims, and no firmware/protocol/device/persistence/recovery/hardware behavior change.",
        "validation_provenance": "GP-PERSIST-002 checker PASS with 11 cases; existing SetConfig compiled production-handler regression PASS with 9 cases; GP-PERSIST-001 research PASS; checker census PASS with 201 entries; health PASS with 40 manifest entries and 36 current load-bearing checks; framework/navigation/agent-surface/syntax/diff gates PASS. Canonical firmware build not required; no production or build-input bytes changed."
      },
      "stop_conditions": [
        "Any production firmware, protocol, packet framing, device, config.bin, persistence/recovery, or hardware behavior is changed or prescribed.",
        "Output delivery, integrity, storage recovery, or device acceptance is claimed from the host harness.",
        "Exact source correspondence, focused negative cases, or independent review fails."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-006",
      "title": "Report host serial transaction stages truthfully",
      "status": "DONE",
      "branch": "glyph/gp-config-006-transaction-stage-reporting",
      "objective": "Make the existing GP-CONFIG-005 host operator utility record transaction stages truthfully so a serial response timeout cannot imply that no host write occurred.",
      "why_this_matters": "At canonical 13a0e76, PosixSerialPort.transact completes write_all before waiting for a response, but execute_valid_update sets sent only after transact returns. A timeout after full host write leaves sent false and obscures whether a request may have reached the controller.",
      "hardware_risk": "H1",
      "behavioral_claim": "Report the reached prewrite-read, write-attempt, full host-write, response, and follow-up-read stages. Full host-write completion means the serial write call accepted all encoded bytes, not that the controller received, accepted, published, or persisted the request. Partial or uncertain write and response timeout remain ambiguous; no automatic retry or PASS follows. Existing command bytes, command order, confirmation gate, result outcome classifications, and firmware behavior are unchanged.",
      "scope": "Change only tools/glyph_serial_config_tool.py, tools/gp_config_005_hw_test.py, and tools/test_gp_config_005_hw_test.py for an optional transport stage callback and bounded valid-update result fields. Record prewrite GET_CONFIG attempt/completion and baseline match; valid CMD_SET_CONFIG write attempt before write_all, full host write completion only after write_all returns, awaiting/received/decoded response, and follow-up GET_CONFIG attempt/completion at actual boundaries. Redefine the retained sent key as a full-host-write-completed flag; false means full write was not confirmed, not that zero bytes were written. Stage data must explicitly retain partial-write ambiguity. Permit only directly required GP-CONFIG-005 operator runbook/protocol and deterministic manifest/census consequences. Implement from fresh canonical; use unpublished 8b2c893 only as evidence.",
      "explicit_excluded_scope": "No cherry-pick or wholesale merge of 8b2c893; no firmware, HAL, active tables, build inputs, UF2, protocol/wire command or ordering, new device operation, auto-retry, hardware evidence reinterpretation, persistence/recovery guarantee, runtime-loaded config, WebSerial/device-write expansion, protobuf or wire schema change, flashing automation, GP-VAL-011 repair, modifier/layout semantic choice, Nunchuk or root-cause claim. This order authorizes no device execution.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator 13a0e76: tools/glyph_serial_config_tool.py PosixSerialPort.transact writes encoded bytes before read_packet and decode; tools/gp_config_005_hw_test.py execute_valid_update sets sent only after transact returns. Existing tools/test_gp_config_005_hw_test.py covers current outcomes. Published Planner packet glyph-portfolio-20260919-0155 at 6536b723336a21ee773a4fa6f367887a97e020cc proposed the candidate. Unpublished 8b2c8932304ecf5c56149eb91ec5ddd7511c59e8 is prior-work evidence only. Current GP-CONFIG-005 operator protocol and accepted hardware record retain their exact scope.",
      "dependencies_prerequisites": [
        "Begin from fresh live configurator and confirm the source gap and operator schema still exist.",
        "Keep GP-VAL-011 REVIEW / OWNER_DEFERRED / NONEXECUTABLE and GP-CONFIG-005 exact hardware evidence unchanged.",
        "Use host mocks or isolated transports only; no device connection or write is needed."
      ],
      "substantive_authorization_rationale": "The source-proven gap has a bounded host-only correction at existing write/read operation boundaries. Reporting those boundaries requires no new product, game, firmware, wire, or device behavior decision. The work order resolves the partial-write and response-timeout ambiguity explicitly. H1 risk is correct because firmware and build inputs stay unchanged.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Canonical already provides equivalent reporting or operator/transport architecture changes materially before implementation.",
        "A correction needs wire, device, firmware, protocol/schema, persistence, hardware-evidence, or GP-VAL-011 changes.",
        "The implementation cannot preserve truthful distinction among write attempt, full host write, response, and device acceptance."
      ],
      "authorization_snapshot_provenance": "Curator independently reviewed live configurator 13a0e76e4de39f6fc7e9c80d210315cb19adf316 and Planner branch planning/portfolio-20260919-0155 candidate GP-CONFIG-006 at immutable commit 6536b723336a21ee773a4fa6f367887a97e020cc, packet base 13a0e76e4de39f6fc7e9c80d210315cb19adf316. Direct-child receipt b90bcd9cd1595a87123fccf0d9543c55adc3282c records READY disposition. Independent source verification confirmed the gap and noncanonical status of 8b2c893.",
      "automated_validation": [
        "Host tests cover no-confirmation, prewrite read failure/drift, zero-progress and partial-write failure, completed write then response timeout, response decode failure/error, successful response and matching follow-up, and follow-up timeout. Assert stage order/final state, sent meaning, outcome, and unchanged human-observation fields.",
        "Mock transport tests prove callback timing and unchanged encoded bytes and command order.",
        "Run .venv/bin/python tools/test_gp_config_005_hw_test.py and directly affected serial transport tests.",
        "Run python3 tools/check_glyph_agent_framework_docs.py, python3 tools/check_glyph_docs_navigation.py, python3 tools/check_glyph_docs_agent_surface.py, and required runtime-config manifest/census gates for changed tool bytes.",
        "Review exact diff against fresh configurator; prove no firmware, build input, protocol, artifact, hardware evidence, GP-VAL-011, or unrelated product delta."
      ],
      "canonical_build": "NOT_REQUIRED: host-only reporting; firmware/build inputs unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "On failed stage proof or review, stop and leave the canonical operator utility unchanged; this work changes no device or artifact state.",
      "status_documentation_updates": "Explain stage meaning and uncertainty in the directly affected operator runbook if needed; publish strict DONE correspondence only after reviewed H1 integration. Preserve GP-VAL-011 deferral and H2 source-authority gate.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "e2523d94eb1023f0146cee9fd975453125c67fa2",
        "reviewed_implementation_sha": "1f9e58cd15d5d8df5cb07aeca2e03eaf4c81d953",
        "prior_canonical_integration_sha": "68dd958fe200618399582929c7c1665c941185e0",
        "reviewed_changed_paths": [
          "docs/agent_framework/HARDWARE_CORRESPONDENCE.md",
          "tools/glyph_hardware_correspondence.py",
          "tools/glyph_serial_config_tool.py",
          "tools/gp_config_005_hw_test.py",
          "tools/test_gp_config_005_hw_test.py"
        ],
        "independent_review_provenance": "Fresh independent repaired-scope reviewer PASS on the exact GP-CONFIG-006 implementation against e2523d94eb1023f0146cee9fd975453125c67fa2. The review repaired and rechecked stage order, prewrite/partial-write/decode/follow-up failure coverage, encoded-byte/order preservation, human-observation nonmutation, additive result-schema enforcement, and current-cycle correspondence audit separation from the historical GP-CONFIG-005 inventory. No firmware, wire, device, persistence, hardware, or unrelated scope changed.",
        "validation_provenance": "Focused GP-CONFIG-005 host suite 35/35 PASS; correspondence suite 33/33 PASS; Python syntax, framework, navigation, agent-surface, census 199, health, and diff gates PASS. Full runtime-config aggregate attempted on the exact snapshot and failed/unavailable in preflight with AGG-11 SETUP_FAILURE on ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/; Curator adjudicated this as pre-existing GP-VAL-011 OWNER_DEFERRED/NONEXECUTABLE state, not a GP-CONFIG-006 failure. No full aggregate-green claim, build, artifact, device, or hardware action. Feature ref and canonical integration were live-verified before this separate status publication."
      },
      "stop_conditions": [
        "Any stage or sent value claims controller receipt, SetConfig acceptance, live RAM publication, disk persistence, or hardware PASS without evidence.",
        "Partial write or response timeout is treated as safe no-write or automatically retried.",
        "New device operation, firmware/product behavior, protocol change, evidence reinterpretation, GP-VAL-011 work, or owner/Senscope semantic input is needed.",
        "Focused tests, independent review, or required gates fail."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-015",
      "title": "Bind hardware correspondence to authoritative firmware and build inputs",
      "status": "DONE",
      "branch": "codex/gp-val-015-hardware-correspondence",
      "objective": "Replace GP-VAL-014 whole-candidate-path equality with a general fail-closed distinction between hardware-correspondence-critical inputs and proven host-only repository metadata; retain exact candidate/artifact/PASS identity and reject every unrelated or later critical input delta.",
      "why_this_matters": "The unpushed diagnostic merge 8220bc4c05c5fcb53f0bc5a7a52f0646bea311cd contains the exact tested candidate and handler but fails solely because the checker census legitimately evolved on canonical. GP-VAL-014 introduced all-candidate-path equality as a conservative host implementation rule; physical acceptance protects firmware inputs, not every historical repository blob. Its useful ancestry and protected-source protections must remain.",
      "hardware_risk": "H1",
      "behavioral_claim": "Host-only correspondence validation accepts legitimate evolution of independently classified non-behavioral metadata while preserving exact Git modes and blobs of ALL critical firmware/build inputs in the tested candidate versus the integrated target, including inputs not changed by the candidate. Unknown paths fail closed. Generated active runtime source remains critical. No firmware, build-input, preserved artifact, protocol, hardware PASS, or device behavior changes. The tested artifact stays authoritative: builder_scripts/arduino_pico.py embeds Git HEAD/dirty FIRMWARE_VERSION, so a later merge rebuild is not asserted byte-identical or hardware accepted.",
      "scope": "Repair tools/gp_config_005_hw_test.py and tools/check_glyph_docs_agent_surface.py; add one small shared host correspondence/classification helper under tools/ and focused operator/surface/classification synthetic tests. A finite audited host-only path inventory with source-backed dependency rationale may be encoded in the helper or a directly coupled inert docs/runtime_config fixture. Critical source/build classification takes precedence over metadata classification; reject malformed, ambiguous, unclassified, symlink/gitlink or unsupported entries unless their safe treatment is explicitly proved. Reuse conservative src/, include/, HAL/, lib/ protection and cover config/, builder_scripts/, platformio.ini, build scripts/dependency controls and other proven build inputs; never classify docs/, tools/, fixture, generated, or extension prefixes alone as harmless. Classify every candidate-changed path, every candidate-to-target changed path, and staged/unstaged/untracked paths relevant to correspondence; compare all critical candidate-to-target entries, not only the historical changed set, and reject dirty critical or unknown inputs. Before integration retain the pinned tested-base ancestry check and prove critical candidate-independent baseline inputs have not drifted. Preserve exact candidate SHA/tree/direct parent/ref, artifact hash, protocol/config.proto checks, canonical HARDWARE_VALIDATED PASS evidence correspondence, and narrow exact-source integration applicability. Host-only differences remain subject to normal scope, fixture, census, provenance and governance validators; exemption never skips them. Allow only deterministic direct consequences in validation manifest/census/health fixtures or docs, classification/source-authority documentation, operator runbook or relevant hardware/validation governance wording, and queue/status completion mirrors. No unrelated checker refactor.",
      "explicit_excluded_scope": "No active firmware, HAL, src/include/lib/config source, generated active tables, platformio.ini, builder/build/dependency input, product/runtime semantics, UF2, preserved artifact, candidate commit, protocol, hardware evidence content, persistence, device/write/flashing, runtime-loaded configuration, Nunchuk, root-cause, or game-semantic changes. No GP-VAL-011 repair or unrelated transaction-stage tooling commit 8b2c8932304ecf5c56149eb91ec5ddd7511c59e8. No one-filename census exemption, blanket docs/tools trust, arbitrary branch exemption, weaker candidate/artifact/PASS pins, recreated/rebased/reimplemented candidate substitute, H2 integration or GP-CONFIG-005 DONE within this H1 order.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Live configurator 2f8e93cfe1430a33ef082829d6c9e0340fd66fbf; GP-VAL-014 implementation 0f7f71bfff4b9488d8b148c6eb155ad20cc05589 introduced the broad loops in both host validators. Canonical GP-CONFIG-005 HARDWARE_VALIDATED/PASS binds candidate 437f87e8086a50f0dfbd834176b80d245c1ed307, tree 4b9e2f1eb56add78ff880321730eb15ed22ce72f, direct tested parent 9550a1bf1309383e351f4f9e66663562fc9f13ac, artifact 650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44 and git-json:0bb9e29a2ba8f92483c8a0177997efe32d400030:docs/calibration/fixtures/gp_config_005_hardware_evidence_2026-09-17.json. platformio.ini source filters/include roots and config/glyph/env.ini inheritance compile src/, HAL/pico/src and Glyph config sources/headers, with builder_scripts/arduino_pico.py and declared dependencies as build authority. The candidate has 23 changed paths: only HAL/pico/src/comms/ConfiguratorBackend.cpp contributes to firmware. The other 22 are seven docs/runtime_config research/contract/census/manifest/health files, two host checkers, and thirteen tools/fixtures/configurator_setconfig_host harness/stub files. Production filters exclude these host locations; the host checker explicitly supplies its stub include root to its own c++ invocation, and the harness includes production source rather than production including the harness. The census is consumed by host census/aggregate validation and has no build/runtime input dependency in this audited graph. tools/glyph_checker_context.py supplies conservative protected-source concepts; build_input_provenance_inventory supplies declared build controls, not a complete dependency closure. HARDWARE_EVIDENCE.md, VALIDATION_AND_GATES.md and IMPLEMENTATION_BOUNDARY.md retain exact physical and source authority.",
      "dependencies_prerequisites": [
        "GP-CONFIG-005 remains canonical HARDWARE_VALIDATED/PASS with no evidence gaps for its immutable candidate/artifact pair; preserved artifact readback and live candidate ref must still match.",
        "Begin from fresh live canonical containing GP-VAL-014 DONE; independently trace source filters, include paths, build hooks/dependency declarations and host-only consumers before allowing metadata classification.",
        "Independent review must inspect the general classification and its adversarial tests. Publish reviewed H1 implementation and then separate strict DONE correspondence before fresh GP-CONFIG-005 integration recovery."
      ],
      "substantive_authorization_rationale": "The owner explicitly requested a general H1 governance/model repair and supplied the safety invariant. Independent Curator review and source dependency inspection establish that the census collision is host-only and that exact all-path equivalence was a GP-VAL-014 implementation shortcut, not a firmware acceptance invariant. Replacing it with conservative critical-input exactness across the entire candidate-to-target delta strengthens protection of unchanged-at-candidate inputs while allowing only dependency-proven host metadata evolution. This resolves the substantive model decision without authorizing firmware changes or a new hardware judgment. GP-VAL-014 is already DONE and does not authorize a new implementation cycle; GP-VAL-015 is the next unused VAL identifier.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Live tested identity, candidate ref/direct parent/tree, artifact readback, queue authorization or immutable PASS record differs from the pinned accepted pair.",
        "Dependency tracing reveals a purported host-only exemption can affect the firmware build or runtime, or an unknown path needs judgment beyond conservative rejection.",
        "The proposed model cannot reject unrelated/later critical source/build deltas, unsafe path modes, or active generated source drift without changing active firmware or weakening identity/protected-source authority."
      ],
      "authorization_snapshot_provenance": "Independent Revision-2 Work-Order Curator on 2026-09-19, separate from Implementation Supervisor, inspected current governance, exact candidate diff and live canonical 2f8e93cfe1430a33ef082829d6c9e0340fd66fbf; ordinary read-only GitHub lookup failed DNS, permitted network-enabled retry verified the exact live ref. Parallel independent dependency audit confirmed the 1 critical / 22 host-only candidate split from PlatformIO inheritance and host compiler include paths. Owner architecture/control-plane request authorizes this bounded model decision, not a new Planner packet; immutable consumed Planner receipt and deferred GP-VAL-011 remain unchanged.",
      "automated_validation": [
        "Critical correspondence: exact candidate integration with all critical inputs exact PASS; one-byte tested handler change FAIL; another firmware/build input changed after candidate FAIL even if not candidate-changed; critical additions/deletions/mode changes FAIL. Recreated/reimplemented candidate, moved candidate ref, changed direct parent/base/tree, wrong artifact digest, or PASS belonging to another candidate/artifact FAIL.",
        "Non-behavioral evolution: legitimately regenerated candidate-touched census/inventory and superseded docs/governance paths PASS correspondence only with audited absence from firmware/build dependency inputs and their normal validators passing; deliberately invalid exempt metadata still fails its ordinary validator. Exercise at least two distinct metadata categories so no one-file exception can satisfy the invariant.",
        "Protected source: exact canonically authorized hardware-validated source integration PASS; exact candidate plus unrelated firmware source edit FAIL; dirty staged/unstaged/untracked critical input FAIL; missing canonical HARDWARE_VALIDATED/PASS, stale/mismatched authorization and ordinary H0/H1 HAL edit FAIL. Preserve narrow merge-parent/base checks and existing ordinary scope rules.",
        "Classification: unknown/unclassified candidate or later path FAIL CLOSED; generated active runtime table/header FAIL on drift; path-prefix/extension tricks, unsupported modes and host-harness lookalikes cannot create an exemption. Build hooks, config include/source inputs and dependency control drift fail even outside old protected prefixes. Critical classification takes precedence over any metadata inventory.",
        "Run focused operator, agent-surface and shared-helper synthetic tests; checker context, agent surface, framework, sequence, navigation, source-sync, census, manifest/health and directly affected aggregate gates; Python compilation, git diff --check, exact changed-path and clean-state checks. Report deferred GP-VAL-011 aggregate failures separately without repairing or relabeling them. No H1 firmware build or new hardware test is required because active/build inputs are unchanged.",
        "Fresh independent reviewer must examine later-source bypasses, active generated tables, prefix tricks, unknown paths, exact candidate/artifact/PASS pins, general census-collision resolution and accurate source authority. Fix material findings within this order before publication; return to Curator for expanded scope."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host validation/model work only; any active firmware or build-input delta stops. Canonical firmware command remains pio run -e glyph_mk6 for separate H2 integration verification; a new build is not new physical acceptance.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Keep the H1 repair unmerged on failed classification, identity or independent-review gates; return substantive ambiguity to Curator. Preserve the exact tested artifact and all historical hardware records. After reviewed H1 canonical publication only, separate Implementation Supervisor recovery starts from freshly verified canonical and performs a new conflict-free exact candidate merge; never reuse diagnostic 8220bc4c05c5fcb53f0bc5a7a52f0646bea311cd.",
      "status_documentation_updates": "Publish GP-VAL-015 READY and synchronized runway/status mirrors through independent curation. Implementation may update execution state for this one order and publish strict DONE evidence only in a later canonical publication after reviewed H1 integration. Keep GP-CONFIG-005 HARDWARE_VALIDATED/PASS until its separate exact-candidate integration and post-integration validation. Preserve GP-VAL-014 DONE, GP-VAL-011 OWNER_DEFERRED and INCONCLUSIVE_PERSISTENCE_EVENT history.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "06903092e086e65904be1ae09e6f377fac50728e",
        "reviewed_implementation_sha": "50a7a2c9ab0cfe5d32eea2f3d86146afa6a5c144",
        "prior_canonical_integration_sha": "50a7a2c9ab0cfe5d32eea2f3d86146afa6a5c144",
        "reviewed_changed_paths": [
          "docs/agent_framework/HARDWARE_CORRESPONDENCE.md",
          "docs/agent_framework/README.md",
          "docs/agent_framework/VALIDATION_AND_GATES.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "tools/check_glyph_docs_agent_surface.py",
          "tools/glyph_hardware_correspondence.py",
          "tools/gp_config_005_hw_test.py",
          "tools/test_glyph_docs_agent_surface_integration.py",
          "tools/test_glyph_hardware_correspondence.py",
          "tools/test_gp_config_005_hw_test.py"
        ],
        "independent_review_provenance": "Fresh independent implementation_reviewer approved exact 50a7a2c9ab0cfe5d32eea2f3d86146afa6a5c144 against 06903092e086e65904be1ae09e6f377fac50728e. Hidden dirty-source finding was reproduced and corrected with independent critical worktree byte/mode readback; assume-unchanged and skip-worktree reproductions now reject. No remaining material findings. All seven model/source-authority questions passed; no active/build input changed.",
        "validation_provenance": "33 shared-model tests, 25 operator tests and 12 portable real-Git agent-surface tests PASS. Framework, sequence, navigation/context/surface, source-sync/runtime identity, custody, build-input provenance, census198, health36, manifest semantic load36/37, Python syntax and diff PASS. Canonical H1 implementation live-verified before this separate completion. Main-workspace aggregate preflight remains SETUP_FAILURE on ignored Adafruit_TinyUSB_XInput path. An isolated replay exposed a missing newly tracked helper dependency; the declared docs_agent_surface dependency is corrected in the reviewed final snapshot. Corrected isolated H1 aggregate adversarial PASS. No full aggregate-green claim, no GP-VAL-011 repair, no build or hardware substitution."
      },
      "stop_conditions": [
        "Any active firmware/build input, exact candidate/artifact, protocol or hardware evidence content requires mutation.",
        "Exact tested identity, artifact/PASS correspondence or critical-input equality cannot be proved; any unknown path requires an unrecorded exemption.",
        "Mixed unrelated source/build edits, dirty protected inputs, generated active source or path tricks can pass; a claimed metadata category lacks dependency evidence.",
        "Work expands into GP-VAL-011, excluded transaction-stage tooling, new device/write/persistence/flashing/runtime-config authority, H2 integration or GP-CONFIG-005 DONE before separate reviewed H1 publication.",
        "Live canonical drift changes substantive authority or another canonical writer conflicts; reverify and defer instead of self-authorizing scope."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": true,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-014",
      "title": "Accept exact hardware-validated integration in post-integration host gates",
      "status": "DONE",
      "branch": "glyph/gp-val-014-post-integration-validation",
      "objective": "Repair two host validation false positives so the pinned GP-CONFIG-005 operator identity check and agent-surface checker accept exact authorized post-integration state while retaining candidate, artifact, evidence, and protected-source rejection gates.",
      "why_this_matters": "The correctly ordered local exact-candidate integration 55eaec9bde837e149647627f67e2bf7c34135cca preserves candidate ancestry and all 23 candidate-changed path entries, including the tested HAL blob, and built successfully, but the operator test assumes a pre-integration merge base and the docs agent-surface checker rejects the intentional protected HAL delta. These host gates now reject a valid publication step.",
      "hardware_risk": "H1",
      "behavioral_claim": "Host-only identity and applicability validation accepts either a pre-integration HEAD whose candidate merge base is the pinned tested base, or a post-integration HEAD containing the exact tested candidate. The candidate must retain its pinned direct parent/base, candidate ref and artifact identity, exact tested changed-path content, and corresponding canonical HARDWARE_VALIDATED PASS authorization. Unauthorized protected-source changes remain rejected. No firmware or artifact bytes change.",
      "scope": "Change only tools/gp_config_005_hw_test.py, tools/test_gp_config_005_hw_test.py, tools/check_glyph_docs_agent_surface.py, and focused synthetic tests/fixtures for that checker as needed. In the operator verifier, check the candidate commit direct parent equals 9550a1bf1309383e351f4f9e66663562fc9f13ac independently of HEAD; accept the current pre-integration merge-base relationship or exact candidate ancestry of HEAD. In the post-integration case, prove the exact candidate identity and candidate-changed path modes/blobs are preserved in HEAD, especially HAL/pico/src/comms/ConfiguratorBackend.cpp, and retain pinned protocol, ref, config.proto and artifact checks. In agent-surface applicability, use the existing canonical queue HARDWARE_VALIDATED item and immutable PASS evidence reference, exact candidate Git SHA, tested base, artifact SHA-256, direct candidate ancestry and exact protected-path modes/blobs to grant only the GP-CONFIG-005 candidate integration HAL delta; apply ordinary scope rules to every other path and reject unrelated source edits. Any manifest, census, health, or governance wording edit is allowed only as a deterministic direct consequence of these focused host checker changes.",
      "explicit_excluded_scope": "No active firmware, HAL, config, persistence, platformio.ini, build input, product/runtime test, UF2, preserved artifact, protocol, hardware result, device/write/flashing behavior, runtime-loaded config, Nunchuk, root-cause, or game-semantic change. No H2 integration, no GP-CONFIG-005 DONE publication, no rebased or reimplemented substitute, no broad HAL/src allowlist or arbitrary feature-branch exemption, no weakening of exact candidate/artifact/PASS correspondence, no GP-VAL-011 aggregate repair, and no bundling of independent transaction-stage tooling commit 8b2c8932304ecf5c56149eb91ec5ddd7511c59e8 absent a separately proven direct dependency.",
      "touched_planes": [
        "docs/checkers",
        "build tooling"
      ],
      "source_authority": "Live configurator 0fd9e30f158fa41b06ea193c32a854a36e8cab31 and canonical GP-CONFIG-005 HARDWARE_VALIDATED queue item with git-json:0bb9e29a2ba8f92483c8a0177997efe32d400030:docs/calibration/fixtures/gp_config_005_hardware_evidence_2026-09-17.json. Exact candidate 437f87e8086a50f0dfbd834176b80d245c1ed307 has direct parent 9550a1bf1309383e351f4f9e66663562fc9f13ac; tested UF2 SHA-256 is 650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44. Local noncanonical integration 55eaec9bde837e149647627f67e2bf7c34135cca is diagnostic evidence only; it has canonical and exact-candidate parents and preserves candidate-changed path entries. tools/gp_config_005_hw_test.py verify_repository_identity currently compares candidate-HEAD merge-base only to tested base. tools/check_glyph_docs_agent_surface.py main invokes glyph_checker_context.validate_feature_scope with HAL protected. docs/agent_framework/HARDWARE_EVIDENCE.md defines exact PASS publication recovery and docs/agent_framework/VALIDATION_AND_GATES.md defines protected H2 merge gates.",
      "dependencies_prerequisites": [
        "GP-CONFIG-005 remains canonically HARDWARE_VALIDATED with PASS and no gaps for the exact candidate/artifact pair and immutable evidence reference.",
        "Implementation begins from fresh live configurator with operator pins, queue identity, protected-source defaults, and evidence schema materially unchanged.",
        "The H1 repair is reviewed and canonically integrated before retrying separate GP-CONFIG-005 H2 exact-candidate integration."
      ],
      "substantive_authorization_rationale": "Both failures are host validation applicability defects observed on an exact candidate integration, with source-backed candidate, base, artifact and PASS authority already resolved. Restricting the allowance to candidate direct ancestry, exact candidate path entries and canonical hardware-validated evidence preserves the existing protection. This is deterministic H1 checker work and does not decide or alter firmware behavior.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The live candidate ref, direct parent, exact tested path entries, artifact hash, queue HARDWARE_VALIDATED status, PASS evidence, or hardware authorization differs from the recorded pair.",
        "The repair would require modifying active firmware, accepting a recreated equivalent candidate, or weakening protected-source enforcement.",
        "Live governance provides a different required integration/checker workflow or the observed integration contains a genuine candidate/source mismatch."
      ],
      "authorization_snapshot_provenance": "Independent Revision-2 Curator inspection on 2026-09-18 of live configurator 0fd9e30f158fa41b06ea193c32a854a36e8cab31, canonical queue/evidence, exact candidate and parent, local diagnostic integration 55eaec9bde837e149647627f67e2bf7c34135cca, and current operator/surface checker source. Owner requested this separate H1 curation; no new Planner packet or H2 implementation authority is created.",
      "automated_validation": [
        "Operator identity tests: pre-integration canonical HEAD plus exact candidate PASS; post-integration HEAD containing exact candidate PASS; changed candidate ref FAIL; changed candidate direct parent/base FAIL even when HEAD ancestry would pass; recreated but nonidentical candidate in canonical history FAIL; artifact hash mismatch FAIL; protocol/config.proto checks remain active.",
        "Agent-surface tests: ordinary unauthorized HAL source change FAIL; exact authorized GP-CONFIG-005 hardware-validated candidate integration PASS; different HAL blob/path delta FAIL; exact candidate without corresponding canonical PASS/authorization FAIL; authorized protected-source change mixed with unrelated source change FAIL; docs/tooling-only feature branch follows ordinary rules. Also cover dirty staged/unstaged/untracked protected paths and arbitrary branch names to prevent bypass.",
        "Run focused operator and agent-surface tests, tools/check_glyph_docs_agent_surface.py, tools/check_glyph_checker_context.py, framework, sequence, navigation, manifest/census/health and affected aggregate gates; report the separately deferred GP-VAL-011 aggregate defect without relabeling it. Python compilation and exact diff/clean-state checks pass. No new hardware test or firmware build is needed for this host-only repair."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host checker/governance-only repair with no active firmware or build-input delta; any such delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "If exact evidence or protected-path proof cannot be retained, keep the focused repair unmerged and return to Curator. Preserve the H2 candidate/artifact and canonical HARDWARE_VALIDATED state; retry H2 integration only after reviewed H1 publication.",
      "status_documentation_updates": "Publish GP-VAL-014 DONE only after independently reviewed H1 implementation is integrated and strict completion correspondence is recorded in a later queue publication. Leave GP-CONFIG-005 HARDWARE_VALIDATED until its separate exact-candidate integration, post-integration gates and DONE publication; keep GP-VAL-011 deferred.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "a44b3786b362335801fae32048617d332a9ead85",
        "reviewed_implementation_sha": "0f7f71bfff4b9488d8b148c6eb155ad20cc05589",
        "prior_canonical_integration_sha": "0f7f71bfff4b9488d8b148c6eb155ad20cc05589",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_docs_agent_surface.py",
          "tools/gp_config_005_hw_test.py",
          "tools/test_glyph_docs_agent_surface_integration.py",
          "tools/test_gp_config_005_hw_test.py"
        ],
        "independent_review_provenance": "Fresh independent reviewer PASS on exact GP-VAL-014 implementation 0f7f71bfff4b9488d8b148c6eb155ad20cc05589 against a44b3786b362335801fae32048617d332a9ead85. Prior mixed active-source and recreated-handler findings were fixed; both counterexamples were rerun and rejected. Candidate ref, parent, artifact, PASS evidence, protected HAL, and mixed-source gates remained fail-closed; no firmware or build input changed.",
        "validation_provenance": "Exact reviewed GP-VAL-014 commit: operator 24 tests and agent-surface 6 tests PASS; checker context, agent surface, framework, sequence, navigation, source sync, census 198, validation health 36 entries, Python compilation and diff gates PASS. Firmware glyph_mk6 build SUCCESS: RAM 51928/262144 bytes, flash 383808/1568768 bytes. Aggregate adversarial gate remains failed on its separately deferred GP-VAL-011 defect; aggregate preflight failed on ignored .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/ path. Canonical H1 integration verified before this separate DONE publication."
      },
      "stop_conditions": [
        "Any active firmware/source, build-input, hardware artifact, protocol or PASS record edit is required.",
        "Exact tested candidate ancestry, direct parent, changed path entries, or artifact/evidence correspondence cannot be proven.",
        "Any unrelated protected-source change can pass or a genuine source mismatch is discovered.",
        "A new unrelated tooling/aggregate repair, H2 integration, DONE publication, device action, or prohibited runtime-config boundary enters scope."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": true,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-005",
      "title": "Preserve accepted live Config when SetConfig rejects",
      "status": "DONE",
      "branch": "glyph/gp-config-005-transactional-setconfig",
      "objective": "Make the existing custom Glyph/HayBox SetConfig handler decode, validate, and save a staged candidate while leaving the prior accepted live Config untouched until complete success, then publish the candidate exactly once.",
      "why_this_matters": "Current HandleSetConfig resets and decodes directly into live Config, restores from disk only after decode failure, and leaves rejected candidate state live after later validation or save failure. The approved invariant prevents rejected values from remaining active without claiming storage rollback.",
      "hardware_risk": "H2",
      "behavioral_claim": "Every existing decode, validation/bounds, or SaveConfig rejection leaves the prior live in-memory Config byte-for-byte active; only a candidate whose decode, current validation, and existing SaveConfig call all succeed may be assigned once into existing live Config storage. Existing response text/command and return behavior remain unchanged. This is RAM transaction safety, not disk atomicity or recovery.",
      "scope": "Update HAL/pico/src/comms/ConfiguratorBackend.cpp so HandleSetConfig uses function-static Config candidate storage, resets and decodes only that candidate, runs all current validation only against it, calls persistence.SaveConfig(candidate) while _config remains old, removes decode-failure LoadConfig(_config), and assigns _config = candidate exactly once only after SaveConfig returns true. Preserve existing CMD_ERROR/CMD_SUCCESS strings, packet behavior, and return values. Add a direct production-path host transaction harness without a runtime fault command; renew the GP-PERSIST-001 SetConfig source/step correspondence docs, fixture, checker, manifest, and census consequences without changing persistence conclusions.",
      "explicit_excluded_scope": "No Persistence.cpp/.hpp behavior or config.bin algorithm change; no disk rollback, atomicity, recovery, boot/load/autoformat, power-loss, migration, compatibility, or durability claim; no protobuf/schema/wire-command expansion; no new WebSerial/device-write transport, runtime-loaded config, runtime table, successful-update mode/RGB/display reconfiguration redesign, outer-core-idle change, flashing automation, gameplay semantic, Nunchuk, root-cause, official-configurator, or real-device save-failure fault-injection work.",
      "touched_planes": [
        "configurator",
        "firmware runtime",
        "persistence",
        "docs/checkers"
      ],
      "source_authority": "GLYPH-UD-014 and docs/agent_framework/SUPERVISOR_TRANSITION_CURATOR_ADJUDICATION_20260907.md. At live 8b4babd8ebea7e4f363b694eeb27435a47befbe7, ConfiguratorBackend.cpp:161-273 resets/decodes live _config, validates it, calls SaveConfig(_config), and reports success; ConfiguratorBackend.hpp binds Config by reference. InputMode and custom/keyboard modes retain pointers into fixed embedded Config arrays, so staging preserves failure-state pointees and assignment into existing storage preserves addresses. Persistence.cpp:36-77 does not intentionally mutate its input but can truncate/rewrite config.bin and does not propagate every I/O failure. GP-PERSIST-001 remains disk-limit authority.",
      "dependencies_prerequisites": [
        "Implementation starts from live configurator with the audited handler, Config shape, mode-pointer topology, SaveConfig behavior, and owner direction materially unchanged.",
        "Approved local custody must be canonical before H2 handoff, but its absence does not prevent bounded source/host/build work.",
        "No successful-update runtime rebind or persistence recovery behavior is required for this rejection-only invariant."
      ],
      "substantive_authorization_rationale": "GLYPH-UD-014 approves the exact invariant and source-derived architecture. Current fixed-array copy semantics determine a staged candidate and one post-save live assignment; static storage avoids unsafe automatic-stack allocation and dynamic backend enlargement. Failure/success behavior and storage non-claims are closed, so no product/domain judgment remains before candidate implementation.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Handler order, Config ownership/copy shape, retained pointers, SaveConfig input/return semantics, response behavior, or owner invariant changes materially.",
        "Static staged Config cannot fit safe RAM headroom, or implementation requires new allocation/publication/reconfiguration behavior.",
        "Direct host testing requires a runtime fault command, persistence mechanism, schema, or other excluded change.",
        "The exact candidate cannot satisfy build, review, custody, or physical protocol."
      ],
      "authorization_snapshot_provenance": "Owner decision GLYPH-UD-014 supplied 2026-09-07; independent source-derived Curator adjudication at 8b4babd8ebea7e4f363b694eeb27435a47befbe7; Planner glyph-portfolio-20260907-1359 and its immutable receipt remain initial USER_DECISION_GATED provenance.",
      "automated_validation": [
        "A direct production-path host harness proves malformed decode and every current validation rejection preserve live bytes, live/embedded addresses, cached pointee content, response behavior, and never call SaveConfig before validation.",
        "Save failure proves SaveConfig sees the intended candidate exactly once while live remains old, then existing error/false leaves live unchanged; no disk rollback is asserted.",
        "Success proves SaveConfig sees candidate while live is old, then one assignment activates it and existing success/true occurs once.",
        "Renewed GP-PERSIST-001 bindings describe staged RAM behavior while preserving all config.bin and H3 limitations.",
        "Focused tests, pio run -e glyph_mk6, map/RAM review, all applicable current manifest checks, health/census, framework, sequence, navigation, surface, syntax, and diff gates pass. Run the full aggregate and report its fail-closed result truthfully; the known owner-deferred GP-VAL-011 isolation/setup defect is not reclassified as a product-check failure or repaired through this work order."
      ],
      "canonical_build": "pio run -e glyph_mk6",
      "expected_artifact": ".pio/build/glyph_mk6/firmware.uf2",
      "manual_acceptance": "REQUIRED",
      "manual_acceptance_protocol_reference": "docs/agent_framework/GP_CONFIG_005_HARDWARE_PROTOCOL.md",
      "manual_acceptance_protocol_version": "GP_CONFIG_005_HW_V1",
      "hardware_evidence_contract_reference": "docs/agent_framework/HARDWARE_EVIDENCE.md",
      "hardware_evidence_contract_version": "GLYPH_HARDWARE_EVIDENCE_V2",
      "rollback_recovery": "Before testing retain accepted config and exact prior firmware. On anomaly stop, record the candidate/artifact and failed row, manually restore prior accepted firmware/config through the existing owner path, and record rollback. Do not merge or invent automated flashing/storage recovery.",
      "status_documentation_updates": "After candidate build publish exact identity and HARDWARE_TEST_REQUIRED separately. After exact physical PASS follow publication recovery, then mark DONE. Preserve RAM safety != disk atomicity/recovery and keep official configurator retired.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "9550a1bf1309383e351f4f9e66663562fc9f13ac",
        "reviewed_implementation_sha": "437f87e8086a50f0dfbd834176b80d245c1ed307",
        "prior_canonical_integration_sha": "4e50be81716117022318d8dcdc7aa60c4390b605",
        "reviewed_changed_paths": [
          "HAL/pico/src/comms/ConfiguratorBackend.cpp",
          "docs/runtime_config/current_config_persistence_recovery_research.md",
          "docs/runtime_config/fixtures/configurator_setconfig_transaction.json",
          "docs/runtime_config/fixtures/current_config_persistence_recovery_research.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_configurator_setconfig_transaction.py",
          "tools/check_glyph_current_config_persistence_recovery_research.py",
          "tools/fixtures/configurator_setconfig_host/handler_harness.cpp",
          "tools/fixtures/configurator_setconfig_host/include/arduino/Adafruit_USBD_Device.h",
          "tools/fixtures/configurator_setconfig_host/include/cobs/Print.h",
          "tools/fixtures/configurator_setconfig_host/include/cobs/Stream.h",
          "tools/fixtures/configurator_setconfig_host/include/config.pb.h",
          "tools/fixtures/configurator_setconfig_host/include/core/CommunicationBackend.hpp",
          "tools/fixtures/configurator_setconfig_host/include/core/InputSource.hpp",
          "tools/fixtures/configurator_setconfig_host/include/core/Persistence.hpp",
          "tools/fixtures/configurator_setconfig_host/include/host_stubs.hpp",
          "tools/fixtures/configurator_setconfig_host/include/pb_arduino.h",
          "tools/fixtures/configurator_setconfig_host/include/pb_decode.h",
          "tools/fixtures/configurator_setconfig_host/include/pb_encode.h",
          "tools/fixtures/configurator_setconfig_host/include/reboot.hpp"
        ],
        "independent_review_provenance": "Fresh independent integration reviewer approved exact merge 4e50be81716117022318d8dcdc7aa60c4390b605 with canonical parent 79608f5e4ceb91209ffe5d5581b985bb5fe7c347 and exact tested candidate 437f87e8086a50f0dfbd834176b80d245c1ed307. Independently verified full critical-input equality, candidate tree/direct parent/ref, immutable canonical PASS with no gaps, original preserved UF2 digest, narrow RAM transaction scope, and unchanged prior inconclusive evidence. No remaining material finding. This is integration correspondence review, not new hardware acceptance of the rebuild.",
        "validation_provenance": "Production transaction and persistence correspondence PASS; original operator/artifact custody PASS; 33 shared correspondence +25 operator +12 portable surface tests PASS; surface, framework, sequence, navigation/context, runtime/source identity, source-sync, build-input provenance, census199, health37, manifest semantic load37/37, Python compilation and diff/source checks PASS. Build .venv/bin/python -m platformio run -e glyph_mk6 SUCCESS, RAM78720/262144, flash383792/1568768; original tested UF2 remains unchanged and authoritative. Reviewed H1 GP-VAL-015 completed before fresh exact merge, which was live-verified before this separate DONE publication. Main aggregate remains known GP-VAL-011 preflight SETUP_FAILURE on .pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput/. Extra historical GFW3 binding checker fails identically on unchanged pre-H1 canonical and lies outside current/affected validation scope; no full aggregate/repository-green claim. Consolidated evidence: docs/agent_framework/GP_CONFIG_005_INTEGRATION_RESULT_20260919.md."
      },
      "stop_conditions": [
        "Any rejected path mutates live Config or candidate publishes before SaveConfig true.",
        "Any existing wire behavior changes or success needs a new externally visible reconfiguration semantic.",
        "Any persistence mechanism/disk guarantee, schema/transport expansion, official configurator, flashing, gameplay/runtime-table, or destructive device fault scope appears.",
        "Memory, automated proof, custody, review, or physical PASS is insufficient."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": true,
      "candidate_git_sha": "437f87e8086a50f0dfbd834176b80d245c1ed307",
      "candidate_base_configurator_sha": "9550a1bf1309383e351f4f9e66663562fc9f13ac",
      "firmware_artifact_build_path": ".pio/build/glyph_mk6/firmware.uf2",
      "preserved_firmware_artifact_locator": "local_backups/hardware-artifacts/437f87e8086a50f0dfbd834176b80d245c1ed307/650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44/firmware.uf2",
      "firmware_artifact_sha256": "650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44",
      "hardware_evidence_record": "git-json:0bb9e29a2ba8f92483c8a0177997efe32d400030:docs/calibration/fixtures/gp_config_005_hardware_evidence_2026-09-17.json",
      "hardware_result": "PASS",
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-ART-001",
      "title": "Establish owner-held local content-addressed firmware custody",
      "status": "DONE",
      "branch": "curation/september-supervisor-decisions",
      "objective": "Establish and enforce owner-held local write-once custody for Revision-2 artifacts at local_backups/hardware-artifacts/<candidate SHA>/<artifact SHA>/firmware.uf2, with stable hashing, readback, pre-handoff verification, retention, rebuild, and loss semantics.",
      "why_this_matters": "H2/H3 acceptance is exact-artifact evidence. Mutable .pio output and later rebuilds cannot preserve tested bytes; the approved local contract supplies deterministic custody without cloud infrastructure.",
      "hardware_risk": "H1",
      "behavioral_claim": "Host-only tooling preserves a regular UF2 under its full candidate Git SHA and computed SHA-256 without overwriting an occupied identity, then reopens and re-hashes it. Verification fails closed on missing, malformed, symlinked, escaped, mutated, or mismatched custody. It creates no firmware, upload, device write, flash, hardware result, or runtime behavior.",
      "scope": "Add canonical custody documentation, a fixed-root preserve/verify CLI with no delete command, synthetic adversarial checker, exact queue-locator enforcement, and hardware/workflow/scheduled/work-order/framework/navigation/manifest/health/census integration. Preserve requires a clean exact candidate checkout before and after, stable source hashing, same-filesystem staging, no-clobber publication, read-only permission, and readback hash; pre-handoff verify re-hashes the recorded identity.",
      "explicit_excluded_scope": "No firmware/runtime/product source, build input, real build/artifact creation or modification, cloud/external store, public release, GitHub Release, CI upload/retention, credential, network service, device write, flashing, hardware result, delete/cleanup/garbage collection, reproducible-build claim, persistence, official configurator, Nunchuk, root cause, or gameplay semantics.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "GLYPH-UD-015; HARDWARE_EVIDENCE.md and WORKFLOW.md exact-snapshot requirements; existing ignored X1 layout as historical evidence only; .gitignore local_backups/ rule. Existing provenance sidecars remain distinct observed-only CI provenance without custody claims.",
      "dependencies_prerequisites": [
        "Implementation remains local docs/tools/checker work with synthetic bytes only in temporary directories.",
        "Root, custodian, retention, loss, rebuild, and write-once rules remain exactly GLYPH-UD-015.",
        "No external service, credential, real candidate, or device is required."
      ],
      "substantive_authorization_rationale": "The owner selected exact local identity, custody, retention, readback, rebuild, loss, responsibility, and no-cloud boundaries. Remaining implementation is deterministic H1 path/hash/filesystem enforcement; no service, destructive cleanup, firmware, or hardware judgment remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Owner changes the root, custodian, retention, loss/rebuild, write-once, or external-store policy.",
        "Hardware evidence schema requires a metadata service or destructive lifecycle not authorized by GLYPH-UD-015.",
        "Implementation would touch a real artifact, build, device, upload, credential, or tracked UF2."
      ],
      "authorization_snapshot_provenance": "Owner decision GLYPH-UD-015 supplied 2026-09-07 and independent artifact audit at 8b4babd8ebea7e4f363b694eeb27435a47befbe7; Planner glyph-portfolio-20260907-1359 and immutable receipt remain initial USER_DECISION_GATED provenance.",
      "automated_validation": [
        "Synthetic tests cover exact path, stable hash, positive preserve/readback, wrong candidate/hash, malformed SHA, missing/mutated file, occupied no-overwrite, same-byte idempotence, different-byte rebuild identity, and root/source/component symlink/escape rejection.",
        "Framework tests require the exact approved local locator and reject mutable .pio and wrong-root/extra-segment/wrong-filename shapes while current X1 correspondence remains valid.",
        "Checker uses temporary bytes only; compile, manifest, health, census, framework, sequence, navigation, agent surface, user direction, and diff gates pass. The full aggregate is attempted and any known deferred GP-VAL-011 isolation failure is reported truthfully rather than reclassified as a custody failure."
      ],
      "canonical_build": "NOT_REQUIRED: H1 docs, host utility, synthetic tests, and governance integration only; any firmware/build-input delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the focused implementation before integration if exact local enforcement requires real bytes or destructive/external behavior. Existing ignored artifacts and historical evidence remain untouched.",
      "status_documentation_updates": "After reviewed canonical integration publish GP-ART-001 DONE with structured ancestry and state local custody is sufficient for future H2/H3 handoff after preserve/readback/pre-handoff verification; external backup remains recommendation only.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "8b4babd8ebea7e4f363b694eeb27435a47befbe7",
        "reviewed_implementation_sha": "305557cdcdb9857b54ccae0790f71046ca87a4e1",
        "prior_canonical_integration_sha": "d3e5303f3e0584a279ce4a6c5cd82ed1d0c4e8c0",
        "reviewed_changed_paths": [
          "docs/AGENT_CONTEXT.md",
          "docs/CURRENT_STATE.md",
          "docs/ROADMAP.md",
          "docs/WORKFLOW.md",
          "docs/agent_framework/GP_CONFIG_005_HARDWARE_PROTOCOL.md",
          "docs/agent_framework/GP_VAL_011_RECOVERY_ADJUDICATION.md",
          "docs/agent_framework/HARDWARE_ARTIFACT_CUSTODY.md",
          "docs/agent_framework/HARDWARE_EVIDENCE.md",
          "docs/agent_framework/README.md",
          "docs/agent_framework/SCHEDULED_TASKS.md",
          "docs/agent_framework/SUPERVISOR_TRANSITION_CURATOR_ADJUDICATION_20260907.md",
          "docs/agent_framework/USER_DIRECTION.md",
          "docs/agent_framework/WORK_ORDER_TEMPLATE.md",
          "docs/project/ACTIVE_AGENT_QUEUE.md",
          "docs/runtime_config/artifact_postprocessor_provenance.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_agent_framework_docs.py",
          "tools/check_glyph_artifact_postprocessor_provenance.py",
          "tools/check_glyph_docs_navigation.py",
          "tools/check_glyph_hardware_artifact_custody.py",
          "tools/glyph_hardware_artifact_custody.py"
        ],
        "independent_review_provenance": "Fresh independent Curator review PASS on exact 305557cdcdb9857b54ccae0790f71046ca87a4e1 against base 8b4babd8ebea7e4f363b694eeb27435a47befbe7: exact owner-direction correspondence; truthful GP-VAL-011 owner-deferred state with evidence preserved; fail-closed local content-addressed custody including exact clean-candidate binding and read-only verification; CI provenance separation; source-derived GP-CONFIG-005 H2 contract; synchronized queue mirrors; fresh census; and no firmware/runtime/build-input change. No material findings.",
        "validation_provenance": "Exact reviewed 305557c custody adversarial, framework, sequence, navigation, surface, census198, health manifest36/current32, CI provenance/workflow, Python compilation, diff and clean-status gates PASS. Full runtime-config aggregate was attempted and failed closed in preflight on the preserved GP-VAL-011 ignored .pio nested-repository defect; it was not weakened or repaired. Canonical integration d3e5303f3e0584a279ce4a6c5cd82ed1d0c4e8c0 verified before this separate DONE publication. No real artifact was created or read by custody validation."
      },
      "stop_conditions": [
        "Any overwrite, delete, garbage collection, symlink traversal, escape, mutable locator, mismatch, unverified readback, or rebuild acceptance inheritance can pass.",
        "Any cloud/store, credential, upload/release, real artifact/build/device/flashing/hardware, firmware/runtime, persistence, official-configurator, or gameplay scope appears.",
        "Ignored X1 or owner-held real bytes would be read, modified, deleted, or made a tracked dependency by validation."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-011",
      "title": "Isolate and time-bound aggregate validation",
      "status": "REVIEW",
      "done_evidence": "OWNER_DEFERRED NONEXECUTABLE: GLYPH-UD-013 intentionally defers the incomplete complete-proof isolation optimization. Failed candidate a0373bde823856c4835bb5aed429d0b402eadd48 remains failed/unmerged evidence; prior truthful 9d80/0381/3171837 reviewed completion remains historical. This is not DONE; reopening requires fresh substantive authority and a new complete READY contract.",
      "branch": "codex/gp-val-011-ignored-directory-repair",
      "objective": "Preserve the exact existing aggregate isolation and complete caller mutation proof objective as intentionally OWNER_DEFERRED and NONEXECUTABLE work; the owner has deprioritized further optimization/concurrency architecture.",
      "why_this_matters": "The ignored-directory repair candidate passes 41 focused adversarial groups but fails the required real clean main-checkout aggregate at the 300-second deadline, around checker 10, without final canonical proof. The first full fingerprint alone measured 205.872seconds for existing roughly 4.77GB ignored state. The original directory support bug was corrected in a failed, unmerged candidate; overall GP-VAL-011 remains incomplete.",
      "hardware_risk": "H1",
      "behavioral_claim": "This changes host-side validation execution safety only. A clean exact committed source snapshot that passes today must still run the same current checker command vectors and classifications; checker execution moves to an independent disposable Git repository and timeout or mutation becomes a fail-closed validation result. It changes no checker product semantics, workflow, build input, firmware/runtime behavior, artifact, device, or hardware state.",
      "scope": "OWNER_DEFERRED \u2014 NONEXECUTABLE. GLYPH-UD-013 supersedes the prior repair-required disposition as the current status. Implementation and merge are stopped. The retained contract below is historical closed scope and validation requirements, not current READY authority. No implementation may resume until separate substantive authorization, exact architecture/validation adjudication and a newly complete canonical READY contract. Review here means stopped contract adjudication, not pending approval to merge the failed candidate. Update only tools/run_glyph_runtime_config_validation.py, tools/check_glyph_runtime_config_validation_aggregate.py, docs/runtime_config/README.md, and deterministic docs/runtime_config/fixtures/glyph_checker_census.json consequences. Reject staged, unstaged, and untracked caller paths; permit pre-existing ignored files only as excluded caller-local state. Before execution pin source HEAD, symbolic branch or detached state, comparison base selected by GLYPH_CHECKER_BASE or origin/configurator, caller-supplied GLYPH_CHECKER_EXPECTED_MERGE_BASE when present, and actual merge base to immutable commits; preserve expected-base mismatch as failure rather than replacing caller intent with computed truth. Preserve the exact origin/configurator comparison identity separately when an explicit comparison override differs. Capture canonical fingerprints over HEAD/branch, index, tracked bytes/modes/symlink targets, refs, repository Git config, staged/unstaged/untracked paths, and the complete ignored-path set. Create a TemporaryDirectory git clone --no-local --no-checkout with an independent object database, no caller ignored files or alternates, no canonical-path origin, and the same exact HEAD under the same branch or detached state. Its closed required-ref set is the source symbolic HEAD when present, the exact origin/configurator comparison ref when present or required by default comparison semantics, and, only when the exact existing current_x1_regression_subset entry with unchanged command [python3, tools/check_glyph_current_x1_regression_subset.py] is selected, refs/heads/runtime-config-x1-offset41-hardware-candidate pinned to 74ae24364b84520d4e0e39240beb9867653cc7b9. Require that exact candidate ref to resolve to the pinned SHA in the caller before recreating it, and require the immutable candidate/evidence/integration objects already available locally; never repair caller ref drift or fetch. No unrelated refs/tags are retained. If clone transfer omits a pinned locally available identity, snapshot setup may transfer only the reachable object closure rooted at the exact resolved source HEAD, selected comparison base, caller expected merge-base when present, actual merge-base, original origin/configurator identity when present, and the conditional X1 candidate/evidence/integration identities enumerated above. Use local git pack-objects --revs --stdout with only those deduplicated full object IDs as input and git index-pack --stdin in the clone; never --all, --reflog, arbitrary ref enumeration, thin/shared packs, alternates, hardlinks, fetch, or network/lazy object retrieval. Prove required object closure is locally available, bound both subprocess groups to the setup deadline, verify transferred identities in the clone, and create no additional refs. Missing caller objects, transfer errors, or unverifiable local completeness fail closed. Synthetic adversarial repositories not selecting current_x1_regression_subset need not manufacture the production candidate ref. Every selected unchanged checker command executes only in the clone. Construct environment from ambient PATH only, disposable HOME/TMPDIR/TMP/TEMP/XDG_CONFIG_HOME/XDG_CACHE_HOME/PYTHONPYCACHEPREFIX, PYTHONHASHSEED=0, PYTHONNOUSERSITE=1, LC_ALL=C, LANG=C, TZ=UTC, GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=os.devnull, GIT_OPTIONAL_LOCKS=0, and exact immutable GLYPH_CHECKER_BASE/GLYPH_CHECKER_EXPECTED_MERGE_BASE. For exactly checker_context with command [python3, tools/check_glyph_checker_context.py] and validation_aggregate_adversarial with command [python3, tools/check_glyph_runtime_config_validation_aggregate.py], omit only the two GLYPH comparison variables: these unchanged self-tests create unrelated synthetic repositories and must establish their own context. Do not generalize that exception by category, branch_policy, mutation_risk, arbitrary ID, or ambient state. Preserve census_freshness in structured failure reports whenever census evaluation completed, never invent PASS before evaluation, and retain exact failure phase/kind and checker identity. Fixed production budgets remain 120 seconds per checker, 300 seconds for whole command including preflight/setup/proof, and two seconds TERM-to-KILL grace; only isolated tests may inject shorter budgets. All timed subprocess trees including clone/setup use bounded process groups terminated and reaped on timeout. Attempt bounded final canonical fingerprint proof on every exit path after initial capture, and unchanged clone fingerprint proof after every checker; never return PASS without complete matching proofs. If the whole-command deadline expires before final proof completes, fail closed with explicit final-proof-unavailable status rather than claiming unchanged state. The 300-second operational deadline permits only the separately fixed two-second TERM-to-KILL cleanup grace; no additional unbounded proof or cleanup work is permitted. Timeout, mutation, or inability to prove invariants fails closed and stops later checkers regardless of fail-fast. Second independent recovery curation binds the complete current source-root topology catalog, conditional on each exact current selected entry ID and unchanged command. For generated_baseline_artifact / [python3, tools/check_glyph_generated_source_owned_baseline_artifact.py], preserve the caller refs/heads/configurator at its own exact locally resolved commit; it is distinct from origin/configurator and GLYPH_CHECKER_BASE and must never be synthesized from either. If absent, ambiguous, conflicting with source HEAD, or not locally complete, fail closed. Its current branch-required checker behavior, including detached failure, remains unchanged. For build_input_resolution_observations / [python3, tools/check_glyph_build_input_resolution_observations.py], include exact locally available commit roots 8c04262c66613d46b933b1b739c01c575cb0c580 and ffc007552abc848051841362b0b0ac4c1a7d087b. For nuker_source_lineage / [python3, tools/check_glyph_nuker_source_lineage.py], include a747dd54b02b207483142331d8b5be1113fc951e and d5050847d3f850951b3f47865dc8a91aedea0834; preserve the existing rev-list --all reachability check, do not invent a ref for it (the accepted source lineage already contains these ancestors). For agent_framework / [python3, tools/check_glyph_agent_framework_docs.py], parse only the exact committed HEAD:docs/project/ACTIVE_AGENT_QUEUE.md regular 100644 queue-state JSON block with duplicate-key rejection and enumerate only these source-consumed commit fields: planner_packet.base_configurator_sha, planner_packet.planning_commit, planner_packet.curation_commit for non-ABSENT packet; completion_correspondence.migration_base_configurator_sha; items with status DONE not in completion_correspondence.legacy_done_ids: done_evidence.implementation_base_sha, done_evidence.reviewed_implementation_sha, done_evidence.prior_canonical_integration_sha; and the SHA component of items.hardware_evidence_record only where status HARDWARE_VALIDATED, HARDWARE_FAILED, or LOCAL_ACCEPTANCE_PENDING with a nonnull result causes current validate_evidence_record to read a git-json reference. repo-json evidence uses HEAD. Require the expected source container/field types and full lowercase commit identities, deduplicate, and verify every required object locally before closed local pack transfer. Do not recursively traverse historical queues, scan arbitrary SHA-looking strings, import/run a checker in the caller, select authority from prose, collect unrelated hardware/artifact/upstream hashes, or copy refs named by metadata. Duplicate provenance fields remain independently validated by the unchanged checker, not normalized by the runner. These roots augment the already enumerated HEAD/base/expected/origin and conditional X1 object roots only; all ordinary checker commands, branch/scope rules, classifications, environment exceptions, independent object database, no-network transfer, timeout and fingerprint requirements remain unchanged. No broad automatic dependency discovery runs during validation. Any further substantive source/ref/object-topology requirement exposed after this complete bounded audit stops as non-executable REPAIR_REQUIRED for later authority rather than a third expansion in this recovery. The nested PermissionError remains an unproven execution/test failure: locate the exact operation and repair only within current runner/adversarial scope; do not weaken timeout proof by accepting SETUP_FAILURE or suppressing unexpected signaling errors. Current narrow repair: canonical_fingerprint must handle directory entries emitted by git ls-files --others --ignored --exclude-standard for caller-local ignored nested Git repositories. Recursively enumerate only physical descendants of such IGNORED directory entries in deterministic sorted order and fingerprint each relative path, file type/mode, directory membership (including empty directories), regular-file bytes and symlink target text. Treat nested .git content as opaque caller-local filesystem bytes; never use its refs/objects/config as validation inputs, execute Git there, copy it to the clone, or add it to required-ref/object catalogs. Use lstat and do not follow symlink directories or external targets. Preserve unambiguous length-framed hashing, existing whole-command budget checks during enumeration and byte reads, final proof rules, and fail-closed handling of unsupported special entries, unreadable state, detectable traversal races or unavailable proof. No timestamps are added as mutation semantics. This is support for the already permitted complete ignored-path set, not dirty-state support or new Git topology. Existing original snapshot, exact ref/object catalog, environment, checker commands/applicability, independent object storage and timeouts remain unchanged. The three implementation consequences are runner, aggregate adversarial tests and deterministic census; README may change only to explain this existing ignored-state contract.",
      "explicit_excluded_scope": "No dirty-snapshot overlay support; no copying ignored files; no manifest schema, entry, applicability, category, command, dependency, branch-policy, load-bearing, historical, exclusion, or checker-semantic change; no tools/glyph_checker_context.py or workflow edit; no ambient python3/PATH identity claim; no network sandbox, container, virtual machine, or general malicious-code containment claim; no protection against deliberately detached daemons or arbitrary absolute host writes beyond the exact repository/Git/process-tree contract; no build, firmware/runtime source, artifact, device, persistence, WebSerial/protobuf write, flashing, hardware, Nunchuk, root-cause, or gameplay change or claim.",
      "touched_planes": [
        "docs/checkers",
        "build tooling"
      ],
      "source_authority": "Independent recovery Curator live-verified configurator 2a80462ba2801192154e42ee4bebb9b1b43ca699 on 2026-09-06 after ordinary DNS failure and permitted read-only network retry. tools/glyph_checker_context.py collect_checker_context resolves explicit base but also inherited GLYPH_CHECKER_EXPECTED_MERGE_BASE; tools/check_glyph_checker_context.py creates unrelated synthetic repositories and tests detached missing-base rejection. The aggregate adversarial checker similarly creates unrelated repositories and invokes the runner with module-local ROOT. tools/check_glyph_current_x1_regression_subset.py evidence_correspondence expressly requires candidate_branch to resolve to exact candidate SHA, separately checks immutable evidence blob and integration parent; its current fixture binds runtime-config-x1-offset41-hardware-candidate to 74ae24364b84520d4e0e39240beb9867653cc7b9, evidence commit 6b0061489cb67d345f212f75268455c181ba271f, and integration 1597c01b416b6aa697d73efc7d2c2b3695dc3e5c. All are locally available. Canonical census_freshness is an existing load-bearing result and the adversarial check correctly expects it after census success. Local failed commits ab8e68ede84468c89365b7f5144889c5728e0583 and 34f430886fb808ce70df81e21d926aef05ed7169 are non-authoritative implementation evidence only. Second independent curation inspected failed candidate 95efad7 and /private/tmp/glyph-val011-full-aggregate.json (27/30 PASS; outer canonical proof MATCH), all 30 current commands and manifest Python dependencies, their direct-import closure (42 files), and additional named subprocess/historical references (85-file conservative static surface) with call-path inspection distinguishing current execution from dormant/historical functions. Current generated-baseline main unconditionally validates literal local configurator ancestry; context-migrated generator/artifact/profile/agent-surface mains use glyph_checker_context instead of their obsolete validate_branch functions. Framework reads exactly the enumerated metadata identities, including planning commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb which need not be reachable from clone-advertised local heads. Fixed observation and nuker history roots are locally available and HEAD ancestors. The supervisor temporary source clone itself lacked local configurator at inspection, so recreating it is explicit source-repository preparation, not runner inference. No checker semantic or current applicability change is authorized. Independent Curator reverified live 31bdbbc83f3129ecb9cbf5bc4ad20e073bdd60a4 on 2026-09-07 (ordinary DNS inconclusive; permitted read-only retry PASS). Actual Git ignored enumeration emits the reported directory under .gitignore .pio/; canonical_fingerprint lines617-665 accepts only file/symlink and raises on that directory. Existing test ISO-02 covers ordinary ignored directory files but not nested Git collapse. No checker consumes this caller ignored state. Independent final Curator source review on 2026-09-07 examined failed a0373bde823856c4835bb5aed429d0b402eadd48, actual main aggregate and bounded 60-second profile: 26,104 posix.open calls consumed 54.814 of 60.002 seconds; read 1.694 seconds and hashing 1.004 seconds. Opens provide required byte/anchored-directory access; no demonstrated redundant operation may be removed without weakening proof. A 600-file threaded diagnostic is only possible overlap evidence, not full proof/timeout/cancellation feasibility. Live canonical 4174001e39f23d2dcb438c232bb3b4e498d153a4 verified after permitted network retry; main restored to this canonical snapshot, failed candidate retained separately.",
      "dependencies_prerequisites": [
        "NONEXECUTABLE \u2014 OWNER_DEFERRED. Implementation and merge are stopped. The retained contract is historical scope/evidence, not READY authority. No implementation may resume until fresh substantive authorization and a new complete contract.",
        "A future separately authorized effort must resolve an exact concurrent or other complete-proof architecture, bound ownership/cancellation/resources/deterministic ordering/races, and establish feasibility under the unchanged 300-second budget before a new complete READY work order. A small synthetic latency benchmark supplies no such proof.",
        "Keep original source-independent clone, exact closed ref/object catalog, environment, unchanged current checker commands/applicability, complete ignored-byte proof and fail-closed semantics. Preserve failed candidate a037 and truthful previous reviewed implementation/completion history without merging failed work."
      ],
      "substantive_authorization_rationale": "NONEXECUTABLE \u2014 OWNER_DEFERRED under GLYPH-UD-013. No implementation or merge is authorized. A future concurrent design would require fresh acquisition/ownership/cancellation, resource, aggregation, and race-proof authority. No topology expansion, budget increase, ignored-data omission, cache shortcut, reduced proof, caller cleanup, or semantic weakening is authorized.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The aggregate runner, manifest representation, checker-context base contract, current command set, or required locally resolvable Git-object topology changes materially before implementation.",
        "A current checker requires caller ignored state, network access, a dirty source overlay, a non-POSIX execution platform, or an ambient environment variable outside the exact authorized set.",
        "The implementation would need to change any checker semantic, manifest classification, workflow, tools/glyph_checker_context.py, build input, product/runtime source, artifact, device, or hardware behavior.",
        "Another canonical change supplies equivalent or stronger exact snapshot, environment, mutation, and process-tree timeout enforcement first.",
        "A proposed fix follows caller ignored symlinks, interprets nested Git metadata as validation context, changes the closed required-ref/object catalog, copies ignored bytes into the clone, excludes ignored descendants from proof, changes unsupported special-file behavior to PASS, or needs broader snapshot architecture or checker semantics.",
        "The current READY authorization is withdrawn by demonstrated real-caller whole-command timeout and unproven complete-proof feasibility; no automatic retry, optimization redesign, precursor candidate or merge is authorized by REVIEW."
      ],
      "authorization_snapshot_provenance": "Independent Curator /root/contract_curator adjudication 2026-09-07 against independently live-verified4174001e39f23d2dcb438c232bb3b4e498d153a4 and failed unmerged a0373bde823856c4835bb5aed429d0b402eadd48. Full real-caller aggregate FAIL at 300 seconds supersedes focused PASS as completion authority. This record withdraws immediate executable authorization and selects no future concurrency architecture.",
      "automated_validation": [
        "Test clean canonical, feature, and detached snapshots; explicit comparison override independent from origin/configurator; matching and mismatching caller expected merge base; missing/non-ancestor/unavailable base fail closed; same HEAD/branch/context results inside clone.",
        "Test exact closed environment key/value set; hostile unrelated ambient values never propagate; exact two synthetic-self-test exceptions omit only GLYPH comparison variables; other context-consuming checkers receive immutable context. Run the unchanged checker-context self-test successfully from clone.",
        "Test exact X1 candidate ref presence/identity and immutable object availability, rejection of missing/wrong caller identity, no unrelated ref/tag retention, no alternates/shared database, no ignored caller file copying. Run unchanged current_x1_regression_subset successfully in clone.",
        "Test a comparison/origin object available only through caller remote-tracking topology and absent from ordinary clone transfer; exact local object-closure transfer preserves both identities without network, shared objects, extra refs, or caller mutation. Missing local objects and interrupted transfer fail closed within setup budget.",
        "Test census success plus checker/setup failure preserves truthful structured census status; stale census fails; test clean/staged/unstaged/untracked/multiple ignored states; mutation of HEAD/branch/index/refs/config/tracked modes/bytes/symlinks/status/ignored state causes immediate failure with unchanged caller.",
        "Test per-check and whole-command timeouts including preflight/setup/clone/final proof, TERM-resistant child process groups, no late sentinel, exact checker/phase/budget attribution, bounded final canonical proof attempts on every exit, explicit unavailable proof at exhausted deadline, no PASS without complete matching proof, and no subsequent checker after mutation/timeout.",
        "Pass focused adversarial, checker-context, isolated current X1, census, manifest, health, syntax/compile, full 31-current-check aggregate within production budgets, framework, sequence, navigation, agent-surface, exact diff, and a fresh independent postimplementation reviewer before publication.",
        "Test selected generated-baseline local configurator identity independently from HEAD, origin/configurator and explicit checker-base override; missing caller local ref fails rather than aliasing. Preserve current detached/branch/scope failures unchanged.",
        "Test framework packet commit absent from clone-advertised local heads, exact migration and nonlegacy DIRECT_ANCESTRY/EXACT_PATH_TREE completion roots (including off-head reviewed feature commit), and conditional git-json evidence root. Only schema-enumerated fields become roots; arbitrary hash-like prose, unrelated fields, hardware artifact hashes and foreign upstream identities are ignored. Malformed or missing required local identities fail closed without network or checker import in caller.",
        "Test fixed observation/nuker historical consumers from isolated clone, preserving object availability and existing reachability semantics. Run all 31 current checks on the exact committed candidate, with missing refs/objects negatives and independent full review. Any further substantive topology/semantic gap returns REPAIR_REQUIRED; no third scope expansion in this recovery.",
        "Locate nested PermissionError with exact operation evidence; timeout fixtures must prove actual bounded timeout/group cleanup, not accept unrelated SETUP_FAILURE. Preserve canonical MATCH or truthful UNAVAILABLE proof reporting.",
        "Synthetic clean Git caller with ignored nested Git repository must reproduce directory-form Git enumeration and pass exact isolated aggregate; prove the ignored nested repository and all descendants are absent in clone, caller remains unchanged, and existing source HEAD/context/closed refs are preserved.",
        "Fingerprint negatives inside ignored directory and nested .git must detect changed regular bytes, path addition/removal/rename, empty-directory membership, file/directory type or mode, and symlink target changes. Repeat with whitespace/newline path names. A controlled synthetic caller mutation must produce canonical MISMATCH and stop later checks; mutation created in disposable clone must fail isolated proof.",
        "Symlink-to-directory/outside-root and symlink cycles are hashed as target text without traversal; changing only external target bytes must not cause external file reads. Unsupported special entries and unreadable state fail closed; inject interrupted/stalled traversal to prove the unchanged whole-command deadline and truthful UNAVAILABLE proof, never weakened PASS.",
        "Run focused/adversarial and all existing timeout/context/topology safety tests, census, manifest, health, syntax/compile, full31 isolated aggregate, framework, sequence, navigation, surface and exact diff review on the clean committed candidate. Independently validate the real clean main-checkout ignored layout without copying/deleting/moving/modifying its ignored state; after reviewed integration rerun full31 there and require canonical/clone MATCH before separate renewed DONE and final fresh planning acceptance."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host-side validation isolation and checker/docs consequences only; any build input, compiled source, firmware/runtime, artifact, or device delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Retain canonical fail-closed implementation and all reviewed/failed evidence; main has been restored to live 4174001. Candidate a037 remains on codex/gp-val-011-ignored-directory-failed-evidence and must not merge. Do not delete/move caller ignored data, restore direct canonical checker execution, change budgets or weaken proof. Await new substantive contract adjudication.",
      "status_documentation_updates": "Keep GP-VAL-011 REVIEW with explicit OWNER_DEFERRED/NONEXECUTABLE meaning; preserve prior completion and failed a037 evidence, remove REPAIR_REQUIRED as current liveness, and require fresh substantive authority plus a new READY contract to reopen. GP-PERSIST-001 stays DONE.",
      "stop_conditions": [
        "OWNER_DEFERRED \u2014 NONEXECUTABLE. GLYPH-UD-013 supersedes the prior repair-required disposition as the current status. Implementation and merge are stopped. The retained contract below is historical closed scope and validation requirements, not current READY authority. No implementation may resume until separate substantive authorization, exact architecture/validation adjudication and a newly complete canonical READY contract. Review here means stopped contract adjudication, not pending approval to merge the failed candidate.",
        "Any selected checker executes in or resolves repository state from the canonical worktree.",
        "Any staged, unstaged, or untracked caller state is ignored, any caller ignored file is copied, any canonical HEAD/branch/index/tracked/ref/config/staged/unstaged/untracked/ignored mutation can pass, or any isolated tracked/index/ref/config/status/ignored mutation can pass.",
        "Any timeout can leave the checker process group unreaped, permit later checks to run, or return success.",
        "Any checker semantic, manifest classification, workflow, build input, product/runtime source, artifact, device, persistence, write, flashing, hardware, Nunchuk, root-cause, or gameplay scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PERSIST-001",
      "title": "Research current Config persistence recovery",
      "status": "DONE",
      "branch": "glyph/gp-persist-001-current-config-recovery-research",
      "objective": "Produce an exact source- and upstream-provenance research packet for the existing Pico config.bin SaveConfig, LoadConfig, startup, and SetConfig persistence path, mapping failure windows and future recovery alternatives without selecting or implementing a mechanism.",
      "why_this_matters": "The current SaveConfig path truncates and rewrites the sole config.bin with a placeholder header, protobuf body, CRC pass, and final header, while the repository has no direct persistence fault-injection test or accepted current-device recovery contract. Future H3 repair cannot be responsibly authorized until the exact filesystem guarantees, failure windows, unknowns, and decision gates are recorded.",
      "hardware_risk": "H1",
      "behavioral_claim": "This is evidence-only persistence research and offline correspondence checking. It may describe source-backed current behavior, authoritative dependency guarantees, inferred failure windows labeled as inference, and unknown device facts; it does not choose or authorize a future persistence algorithm, change current config.bin behavior, access a device, or create hardware evidence.",
      "scope": "Add docs/runtime_config/current_config_persistence_recovery_research.md, docs/runtime_config/fixtures/current_config_persistence_recovery_research.json, tools/check_glyph_current_config_persistence_recovery_research.py, one current load-bearing research/provenance manifest entry, and only deterministic census/health consequences. Bind exact current repository blobs and the configured framework-arduinopico 3.6.3 selector, then use permitted read-only live verification to resolve the authoritative Arduino-Pico tag/commit, its LittleFS wrapper source, and the exact upstream littlefs commit and documentation/source/test blobs it incorporates. Record every SaveConfig encode/open/truncate/header/body/seek/read/CRC/header-rewrite/close step; LoadConfig validation/decode behavior; boot load/default-save path; HandleSetConfig save call; checked and ignored return values; and a failure-window/current-consequence matrix with SOURCE_BACKED, INFERRED, or UNKNOWN classification. Compare temp-and-rename, temp-plus-backup, and two-slot/generation alternatives only as non-authoritative design options. Record future fault-injection cut points, exact automated/build/hardware gates, and every unresolved H3 product/device decision. A bounded insufficient-evidence result is valid completion when exact searches and unknowns are preserved.",
      "explicit_excluded_scope": "No edit to HAL/, config/, platformio.ini, dependency selectors, firmware/runtime/product tests, or current storage code; no build, UF2, config.bin read/write, filesystem mount, device access, artifact, controller test, or hardware result; no selection of temp/backup filenames, old-or-new versus prior-good invariant, recovery precedence, cleanup, migration, backward/old-firmware compatibility, autoformat policy, diagnostics, free-space reserve, wear threshold, save cadence, update preservation, fault-injection mechanism, or physical recovery UX; no bundling with GP-CONFIG-005 live-memory transaction work; no runtime-table persistence, runtime-loaded config, WebSerial/device write, protobuf-write expansion, flashing, Nunchuk, root-cause, or gameplay claim.",
      "touched_planes": [
        "docs/checkers",
        "persistence"
      ],
      "source_authority": "Exact clean live configurator 766237660e96189064203c3dc6e00cbdbe0df2c5. HAL/pico/src/core/Persistence.cpp opens config.bin with w+, writes a zero header, streams Config protobuf data, rereads it for CRC, rewrites the header, and closes without a temporary, backup, rename, or generation slot; HAL/pico/include/core/Persistence.hpp defines the filename/header; config/glyph/common/src/config.cpp loads on startup and saves the in-memory default when load fails; HAL/pico/src/comms/ConfiguratorBackend.cpp calls SaveConfig after decode and bounds checks. platformio.ini selects framework-arduinopico at tag 3.6.3. Existing storage/fallback docs explicitly say current persistence is not an atomic rollback architecture and leave recovery policy unresolved; the existing storage simulator excludes config.bin. Planner packet glyph-portfolio-20260901-0909 at 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb proposed GP-PERSIST-001, and bounded specialist verification confirmed exact authoritative upstream provenance is available while later H3 choices remain unresolved.",
      "dependencies_prerequisites": [
        "Implementation starts from a fresh live-configurator descendant of 766237660e96189064203c3dc6e00cbdbe0df2c5 with Persistence.cpp/.hpp, startup config.cpp, ConfiguratorBackend.cpp, platformio.ini selector, and current storage/fallback boundary documents materially unchanged.",
        "Every retained upstream fact resolves through permitted read-only access to an authoritative repository at a full immutable commit and exact regular source/doc/test blob; mutable tags or local installed caches alone are observations, not authority.",
        "The research remains useful with a bounded evidence-insufficient outcome and does not depend on selecting a future recovery mechanism or receiving hardware observations."
      ],
      "substantive_authorization_rationale": "The existing non-atomic application sequence and missing recovery evidence are directly source-proven, and the research question is fully bounded. Exact immutable upstream provenance, a closed current-path/failure-window schema, non-authoritative alternative comparison, explicit unknowns, and future test gates can be completed without deciding any H3 behavior. No user, product, storage-mechanism, migration, runtime-table, device-write, or hardware decision is delegated to the implementer.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any current persistence, boot, SetConfig, filesystem selector, or accepted storage/fallback boundary changes materially before implementation.",
        "Authoritative upstream source cannot be resolved to full immutable commits and exact relevant blobs after every permitted network-capable retry.",
        "The packet would need to choose a recovery invariant, algorithm, filename/layout, migration, compatibility, autoformat, diagnostics, wear/capacity threshold, save cadence, update policy, fault-injection implementation, or hardware procedure rather than record it as a future decision.",
        "Another canonical change supplies equivalent or stronger exact current-path, upstream-guarantee, failure-window, and decision-gate evidence first."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of Planner candidate GP-PERSIST-001 from planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb, packet base 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c, rebound to exact clean live configurator 766237660e96189064203c3dc6e00cbdbe0df2c5 with bounded current-source, upstream-provenance, failure-window, and future-decision specialist verification on curation/portfolio-20260901-final-survivors-20260906.",
      "automated_validation": [
        "The fixture uses an exact closed schema and binds current repository paths, Git blobs, source fragments/order, platform selector, authoritative upstream repository/full commits, exact source/doc/test blob identities, lookup timestamps/methods, and immutable locators; wrong/missing/mutable/abbreviated/duplicate/contradictory provenance fails.",
        "Every current save/load/boot/SetConfig step and return-value handling is represented once in exact order; every failure-window row has a SOURCE_BACKED, INFERRED, or UNKNOWN classification, exact evidence references, current consequence, and no unsupported power-loss or hardware claim.",
        "The three alternative families are descriptive only, select none, and expose exact unresolved decisions for recovery invariant, stale-state cleanup, boot/default and autoformat policy, migration/compatibility, rename replacement, readback/diagnostics, concurrency, capacity/wear/save cadence, update preservation, fault injection, and physical recovery acceptance.",
        "The checker and tests perform no network access, import or execute upstream code, mount a filesystem, read/write config.bin, build firmware, access a device, or create hardware evidence; implementation-time live research is frozen into checked-in immutable provenance for offline validation.",
        "Focused persistence-research and existing storage-transport/source-authority checks, manifest, census, health, full current runtime-config aggregate, framework, sequence, navigation, agent-surface, py_compile, and exact-diff checks pass with fresh independent source-authority review and zero product/build/device delta."
      ],
      "canonical_build": "NOT_REQUIRED: H1 docs, evidence fixture, offline checker, and deterministic validation metadata only; any selector, dependency, firmware/runtime, persistence implementation, or product-source delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the focused research branch if exact current/upstream correspondence cannot be retained without inference; preserve current persistence behavior and explicit UNKNOWN/H3 decision gates rather than selecting a mechanism or fabricating guarantees.",
      "status_documentation_updates": "Publish only exact current-path facts, immutable upstream evidence, labeled inferences, unknowns, option comparisons, and future decision/test gates. Keep runtime-loaded storage and every persistence implementation unapproved.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "3171837fcfe8fa8b9f6ab1d1a8891478c98c76a3",
        "reviewed_implementation_sha": "2b2a48e14e9d621b13038d7a8f29e57713ef462a",
        "prior_canonical_integration_sha": "3a9d41a9927983f1ba5d1e4ff6cf74af57ac634f",
        "reviewed_changed_paths": [
          "docs/runtime_config/current_config_persistence_recovery_research.md",
          "docs/runtime_config/fixtures/current_config_persistence_recovery_research.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_current_config_persistence_recovery_research.py"
        ],
        "independent_review_provenance": "Independent source/provenance and final replay reviewer PASS on exact 2b2a48e: six noncensus blobs equal reviewed 6827f174; nine current source blobs unchanged; closed seven-path authorized delta. H1 evidence only; no mechanism selected.",
        "validation_provenance": "Exact 2b2a48e full isolated aggregate31/31 PASS with canonical and per-check MATCH; 48 ordered operations,15 immutable upstream blobs,52 standard negative cases,159 additional independent record/source negatives; manifest35,census197,health,framework,sequence,navigation,surface,compile,diff and cleanliness PASS. Live integration3a9d41a verified before separate DONE publication."
      },
      "stop_conditions": [
        "Any current or future persistence behavior, storage layout, selector, dependency, boot/default policy, config update behavior, or firmware/product test would be changed.",
        "Any filesystem, rename, power-loss, wear, capacity, update-preservation, or device behavior claim lacks exact authoritative immutable evidence or is not labeled inferred/unknown.",
        "Any future H3 mechanism, migration, compatibility, recovery, diagnostics, fault-injection, or physical acceptance choice would be made or authorized.",
        "Any build, artifact, device/config.bin action, runtime-loaded config, persistence implementation, WebSerial/protobuf write, flashing, hardware, Nunchuk, root-cause, or gameplay scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CTL-003",
      "title": "Bind Planner and Curator packet provenance",
      "status": "DONE",
      "branch": "glyph/gp-ctl-003-packet-provenance-20260902",
      "objective": "Make canonical queue liveness depend on exact locally resolvable Planner and Curator Git-object correspondence plus a unique structured surviving-candidate inventory instead of trusting free-form provenance, prose, and an independent candidate_count integer.",
      "why_this_matters": "The current framework checker accepts bogus planning commits, packet identities, Curator provenance, and arbitrary nonzero candidate counts; GP-X1-001 completion also left the queue claiming nine survivors when only eight existed before this curation.",
      "hardware_risk": "H0",
      "behavioral_claim": "This strengthens offline control-plane provenance and survivor-accounting validation only. It does not change liveness policy, authorize a Planner candidate by inference, edit product/runtime behavior, or perform network access during ordinary validation.",
      "scope": "Upgrade the canonical queue packet representation and tools/check_glyph_agent_framework_docs.py so non-ABSENT packets carry exact packet_id, packet_path, planning_commit, curation_commit, and a unique ordered survivors array of candidate_id plus a closed disposition. Derive candidate_count from survivors. Resolve the immutable planning and curation commits locally, require commit objects and regular non-executable Git 100644 packet/queue blobs, verify planning parent/base and exact packet frontmatter/candidate inventory, verify Curator parent/base and ancestry into current HEAD, and bind the initial reviewed disposition set. Add isolated temporary-Git positive and adversarial cases. Update only canonical queue/status prose and deterministic checker-census, manifest, or validation-health consequences of the authorized checker byte change.",
      "explicit_excluded_scope": "No fetch or network access in the checker; no mutable branch tip as the sole authority; no candidate promotion, new liveness rule, queue target change, implementation execution, tools/glyph_checker_context.py change, workflow, build, product/runtime source, source-authority, hardware result, device, persistence, WebSerial/protobuf write, flashing, Nunchuk, root-cause, or gameplay claim.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Live configurator 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3; Planner packet planning/portfolio-20260901-0909 at 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb with sole packet path docs/planning/portfolio_20260901_0909.md and parent/base 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c; initial reviewed curation commit 7b6601709b6f7780601ff68c0e8d9df1bf63ad8a with the same parent/base and ancestry into current configurator. tools/check_glyph_agent_framework_docs.py currently validates only coarse packet shape and never reads curator_review_provenance or either Git object. Independent adversarial verification confirmed bogus provenance and candidate_count=999 pass today.",
      "dependencies_prerequisites": [
        "Implementation starts from a fresh live-configurator descendant of 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3 with queue schema v2, packet 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb, curation commit 7b6601709b6f7780601ff68c0e8d9df1bf63ad8a, and current completion correspondence locally resolvable.",
        "The implementation repository contains the required immutable planning and curation commit objects; ordinary validation must fail closed rather than fetch when either object is unavailable.",
        "Permitted intervening deltas are reviewed completion/status publication, deterministic census/manifest/health consequences, and the exact Curator-authorized survivor transitions recorded in queue history; any packet identity, initial Curator disposition, or liveness-policy drift requires re-curation."
      ],
      "substantive_authorization_rationale": "The object-required policy is fully resolved by existing immutable Git evidence and is stronger than an unverifiable embedded snapshot. The exact packet, path, base, initial curation object, original thirteen candidate headings, and current dispositions are known. A closed structured survivor list makes candidate_count derived while preserving Planner non-authority. No product, domain, source, hardware, or external-service decision remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Either required planning or curation commit object is unavailable or does not resolve to the exact expected commit/tree shape.",
        "The packet path, frontmatter identity/base/review flag, original candidate inventory, initial Curator disposition, queue schema, liveness policy, or completion correspondence changes materially before implementation.",
        "Implementation would require a fetch, trust a mutable ref, embed unverified prose as correspondence, promote a survivor, or change any product/runtime or hardware state.",
        "Another canonical change supplies equivalent or stronger packet-object and structured-survivor correspondence first."
      ],
      "authorization_snapshot_provenance": "Follow-up Curator review of candidate GP-CTL-003 from planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb, packet base 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c, initial curation commit 7b6601709b6f7780601ff68c0e8d9df1bf63ad8a, and exact live configurator 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3, with independent object/provenance/adversarial verification on curation/portfolio-20260901-survivors-20260902.",
      "automated_validation": [
        "Exact current planning and curation objects, parent/base relationships, packet path/mode/frontmatter, original thirteen unique candidate headings, initial reviewed dispositions, and curation ancestry pass without network access.",
        "Queue candidate_count equals the length of a unique ordered survivors array; every survivor exists in the original packet, uses a closed disposition, and is neither authorized in the current queue nor recorded complete by current material events.",
        "Isolated temporary-Git cases reject missing/wrong object, object type, path, mode, parent/base, packet ID/branch/review flag/candidate inventory, curation object/ancestry, duplicate queue or survivor IDs, count mismatch, unknown disposition, completed survivor, and survivor absent from the packet.",
        "python3 tools/check_glyph_agent_framework_docs.py, tools/check_glyph_agentic_sequence_protocol.py, tools/check_glyph_checker_census.py, tools/run_glyph_runtime_config_validation.py --json, tools/check_glyph_docs_navigation.py, and tools/check_glyph_docs_agent_surface.py pass with focused independent governance review and no applicability reclassification."
      ],
      "canonical_build": "NOT_REQUIRED: H0 queue/schema/governance-checker work only; any workflow, build input, product/runtime source, or firmware delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": [],
      "rollback_recovery": "Drop the focused branch if immutable object correspondence cannot be enforced offline without changing liveness policy; retain current queue authority and never fall back to trusting a shape-valid free-form provenance string or independent count.",
      "status_documentation_updates": "Publish schema/provenance and exact survivor accounting in the canonical queue/status surfaces without changing candidate dispositions beyond already-authorized execution transitions.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "33694f3a67f336c25b3c82008b3511d06a490016",
        "reviewed_implementation_sha": "9dff89d835ccb0bb45dd10c79305b9fef5096263",
        "prior_canonical_integration_sha": "97267efcf5962a6dfa28a551670455aa3bd91c65",
        "reviewed_changed_paths": [
          "docs/project/ACTIVE_AGENT_QUEUE.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_agent_framework_docs.py"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer PASS after frontmatter fail-closed repair and expanded packet/survivor adversarial coverage on the exact integrated source snapshot.",
        "validation_provenance": "Focused framework, packet-object adversarial, census, full current runtime-config aggregate, sequence, navigation, agent-surface, py_compile, and diff checks passed; no firmware, build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "Any required object or exact packet/curation correspondence is missing, ambiguous, mutable-only, or requires network access during validation.",
        "Any candidate is promoted, rejected, or reinterpreted by checker logic instead of an explicit Curator transition.",
        "Any authority, provenance, concurrency, completion, liveness, hardware, or publication invariant would be weakened.",
        "Any file outside the exact control-plane/governance-checker and deterministic consequence surface is required."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null
    },
    {
      "id": "GP-PROV-008",
      "title": "Census canonical local build entrypoints",
      "status": "DONE",
      "branch": "glyph/gp-prov-008-local-build-entrypoints-20260902",
      "objective": "Finish the declared build-input provenance boundary by recording the documented canonical and fallback local glyph_mk6 entrypoints, the exact tracked wrapper chain, and unresolved interpreter selection without executing a build or changing any build input.",
      "why_this_matters": "The accepted GP-PROV-003 inventory omits scripts/build-glyph-mk6-quiet.sh and scripts/pio-local.sh even though AGENTS.md and docs/WORKFLOW.md prescribe that fallback chain, so current declared-input provenance is incomplete.",
      "hardware_risk": "H0",
      "behavioral_claim": "This is static provenance/schema/checker work only. It records command and tracked-wrapper identity while preserving every unresolved executable, dependency, reproducibility, artifact, device, and hardware non-claim.",
      "scope": "Create a schema-v2 current build-input inventory that preserves every existing selector, source-identity, postprocessor, and unresolved-claim record exactly; adds the two tracked 100755 wrappers to declaration_files; and adds one exact local_build_entrypoints contract for canonical [pio, run, -e, glyph_mk6], fallback [./scripts/build-glyph-mk6-quiet.sh], its edge to [./scripts/pio-local.sh, run, -e, glyph_mk6], the exact ordered pio-local interpreter alternatives [.venv/bin/python, ambient python, python3], and the PLATFORMIO_CORE_DIR line. Bind roles, tracked modes/hashes, and AGENTS.md/docs/WORKFLOW.md policy sources. Rework GP-PROV-004 validation to derive its unchanged 44 timestamped observations from the exact historical schema-v1 Git blob at base 8c04262c66613d46b933b1b739c01c575cb0c580 rather than requiring the current inventory bytes to remain frozen. Update focused docs/checkers and deterministic manifest/census/health consequences only.",
      "explicit_excluded_scope": "No wrapper, PlatformIO configuration, builder script, selector, dependency, workflow, postprocessor, build, installation, environment resolution, artifact, upload/store, device, firmware/runtime, table, persistence, WebSerial/protobuf write, flashing, Nunchuk, root-cause, reproducibility, or hardware change or claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "AGENTS.md and docs/WORKFLOW.md name pio run -e glyph_mk6 as canonical and scripts/build-glyph-mk6-quiet.sh as fallback. On exact live configurator 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3, the fallback wrapper is tracked mode 100755, blob e35164eeb512cec678a2f138b2b13f2b52263dc6, SHA-256 328ff73b9f1da1ccad5d7ee0431b664b9c33a70c35959e4a14f6677881844eeb and invokes ./scripts/pio-local.sh run -e glyph_mk6; pio-local is tracked mode 100755, blob deaabc271a8268dcd1f29c473f48beadf979cf7f, SHA-256 3b81e400830b30db0a4a194cdb5ff35df61e4d15f13b8d3891e79f2716ee9714 and selects the three recorded interpreters. The current inventory/checker remains schema v1 with eight declarations. GP-PROV-004 binds historical inventory blob 5e6d2f128cc6baccd98c39369fbd6bc5acc43851 and SHA-256 d783688fdc140ad2a5706b168f24f76093d0a388431ca4b33253257c52dfc455 at base 8c04262c66613d46b933b1b739c01c575cb0c580.",
      "dependencies_prerequisites": [
        "Implementation starts from a fresh live-configurator descendant of 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3 with both wrapper blobs, canonical/fallback policy text, schema-v1 inventory, and GP-PROV-004 historical object materially unchanged.",
        "The exact historical inventory commit/blob required by GP-PROV-004 is locally resolvable; validation fails closed rather than refreshing or fabricating observations.",
        "Every existing schema-v1 selector, source identity, postprocessor identity, unresolved claim, and all 44 GP-PROV-004 observation records/timestamps remain semantically unchanged."
      ],
      "substantive_authorization_rationale": "The documented command chain and exact wrapper bytes resolve the missing representation. Schema v2 can add local entrypoints without promoting ambient pio or Python identity. Loading GP-PROV-004 from its immutable historical object preserves the observation's original source correspondence and avoids false re-observation. No user, product, runtime, external-evidence, or architecture decision remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Either wrapper, its mode/hash/command chain, the canonical/fallback policy, schema-v1 inventory, or GP-PROV-004 historical base/blob changes before implementation.",
        "Any implementation would resolve or infer ambient pio/Python identity, execute a shell/build tool, refresh timestamped observations, or change a selector/build input.",
        "Another canonical change supplies equivalent or stronger local-entrypoint provenance and historical observation preservation first."
      ],
      "authorization_snapshot_provenance": "Follow-up Curator review of the GP-PROV-003 repair from planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb, packet base 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c, rebound under new repair identity GP-PROV-008 against exact live configurator 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3 with independent wrapper/schema/history verification on curation/portfolio-20260901-survivors-20260902.",
      "automated_validation": [
        "Schema v2 preserves all schema-v1 semantic records exactly and requires the two exact tracked executable wrappers plus the complete canonical/fallback command, role, edge, ordered interpreter-selection, core-directory, mode/hash, and policy-source representation.",
        "Missing, changed, duplicated, reordered, extra, escaping, symlinked, untracked, wrong-mode, wrong-hash, wrong-role, wrong-edge, wrong-command, wrong-policy, or promoted executable-identity cases fail without executing any discovered script.",
        "GP-PROV-004 checker resolves and hashes the exact historical schema-v1 inventory object, reproduces all 44 unchanged observations and direct/derived ordering, proves base ancestry, and rejects missing/wrong historical object/blob without rewriting its evidence fixture or timestamps.",
        "Focused provenance inventory and resolution-observation checks, manifest/adversarial checks, checker census, validation health, full runtime-config aggregate, framework, sequence, navigation, agent-surface, py_compile, and diff checks pass with fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 static provenance/schema/checker work; no wrapper or build input changes.",
      "expected_artifact": "NOT_APPLICABLE",
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": [],
      "rollback_recovery": "Drop the focused repair if schema-v2 correspondence or historical-object preservation cannot remain static and fail closed; retain the original GP-PROV-003 and GP-PROV-004 evidence rather than rewriting observations.",
      "status_documentation_updates": "Record the complete local entrypoint chain and historical-object observation boundary without any resolved interpreter, execution, artifact, reproducibility, or hardware claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "d360ff36586133890e9faf07811cc04a806fdbbf",
        "reviewed_implementation_sha": "bc76af250eb61e68daae8b1a91acb6412ecd95a0",
        "prior_canonical_integration_sha": "bc76af250eb61e68daae8b1a91acb6412ecd95a0",
        "reviewed_changed_paths": [
          "docs/runtime_config/build_input_provenance_inventory.md",
          "docs/runtime_config/build_input_resolution_observations.md",
          "docs/runtime_config/fixtures/build_input_provenance_inventory.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "tools/check_glyph_build_input_provenance_inventory.py",
          "tools/check_glyph_build_input_resolution_observations.py"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer PASS after raw historical observation packet pinning and census regeneration on exact integrated implementation snapshot bc76af250eb61e68daae8b1a91acb6412ecd95a0.",
        "validation_provenance": "Focused provenance/observation, manifest, census, health, full runtime-config aggregate, framework, navigation, agent-surface, py_compile, and diff checks passed; no firmware, build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "Any wrapper, build, PlatformIO, dependency, postprocessor, workflow, artifact, network, device, or hardware action would execute.",
        "Any ambient executable identity, dependency closure, reproducibility, purpose/effect, or artifact acceptance would be inferred.",
        "Any GP-PROV-004 observation record, timestamp, external identity, or immutable source locator would be refreshed or weakened.",
        "Any runtime/configurator product source or build input would change."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null
    },
    {
      "id": "GP-VAL-008",
      "title": "Bind the current X1 regression subset",
      "status": "DONE",
      "branch": "glyph/gp-val-008-current-x1-regression-20260902",
      "objective": "Create one current load-bearing offline regression contract for the exact source-backed and Revision-2 hardware-accepted sole/non-mode X1 nine-direction subset without reviving the stale May-28 behavior fixture or claiming a firmware simulation.",
      "why_this_matters": "GP-VAL-008 was evidence-gated when no current accepted behavior subset existed. GP-X1-001 now supplies exact owner intent, current integrated source, an exact candidate/artifact PASS, and bounded sole/non-mode X1 observations for all nine directions.",
      "hardware_risk": "H1",
      "behavioral_claim": "For the already-accepted current source only, SelectRuntimeTableId with mode inactive, X1 active, and every other table modifier inactive selects RuntimeTableId::X1; DirectionIndexFromAxes maps the bounded -1/0/1 axis grid to indices 0..8; ApplyTableAnalogOutput reads the corresponding current kX1Table point; and those nine points are the accepted offset-41 values. The checker is static/offline evidence correspondence, not hardware execution or a general Ultimate behavior oracle.",
      "scope": "Add a dedicated docs/fixture/checker lane that binds exact immutable GLYPH-UD-010/011/012, the Revision-2 evidence record, candidate and integration identities, current source selection/axis-index/lookup structure, and the current extracted kX1Table values. Use only the abstract RoleState boundary mode_active=false, x1_active=true, all other table modifiers=false and axes in {-1,0,1}. Require exact direction/index/raw-coordinate rows and no-disconnect observation classification. Add the checker as one current load-bearing manifest entry and regenerate deterministic census/health consequences.",
      "explicit_excluded_scope": "No physical button-binding assertion, mode+X1/MX1, X2, Y1/Y2, Tilt, layer/flipper, direction-plus-A, RF6/RF7/RF9 or other override, SOCD beyond the supplied normalized axes, digital output, controller/gameplay semantic, stale May-28 case revival, firmware simulation, firmware/runtime source edit, table byte, routing/publication path, build, artifact, device, persistence, WebSerial/protobuf write, flashing, Nunchuk, root-cause, or new hardware claim.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Project-owner authority GLYPH-UD-010/011 and observation GLYPH-UD-012; exact protocol docs/calibration/x1_offset41_hardware_test_protocol_2026-09-02.md; immutable Revision-2 evidence git-json:6b0061489cb67d345f212f75268455c181ba271f:docs/calibration/fixtures/x1_offset41_hardware_evidence_2026-09-02.json; exact candidate 74ae24364b84520d4e0e39240beb9867653cc7b9 and integration 1597c01b416b6aa697d73efc7d2c2b3695dc3e5c; live configurator 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3. Current source defines X1 selection, direction-index mapping, table lookup, and the integrated nine kX1Table points. Existing current checkers bind table/source and intake identity but no current behavior subset; the old identity runtime evaluator remains historical-only and contains obsolete literals.",
      "dependencies_prerequisites": [
        "GP-X1-001 remains DONE with exact candidate/artifact PASS and exact-candidate integration correspondence; GLYPH-UD-010/011/012, protocol, immutable evidence object, intake, and current kX1Table remain exact.",
        "Implementation starts from a fresh live-configurator descendant of 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3 with SelectRuntimeTableId, DirectionIndexFromAxes, ApplyTableAnalogOutput, active source-owned publication, and the X1 table materially unchanged.",
        "The work remains a new bounded current fixture/checker; historical behavior fixtures/evaluators remain excluded and are not copied, edited, or promoted."
      ],
      "substantive_authorization_rationale": "The new owner direction and exact-snapshot PASS resolve the former evidence gate for one narrow subset. Repository source resolves selection, index, lookup, and current bytes without game-semantic inference. Binding only the abstract sole/non-mode X1 role state avoids unsupported physical-button claims, while immutable evidence references prevent a static checker from masquerading as new hardware proof.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any exact user direction, candidate/artifact/evidence identity, integration correspondence, X1 table byte, selection/index/lookup source, or active publication path changes before implementation.",
        "The proposed checker would require a physical binding, unsupported role/override/SOCD/game-semantic assertion, historical fixture promotion, or general firmware-simulator claim.",
        "Another current checker supplies equivalent or stronger exact X1 source-and-evidence behavior correspondence first."
      ],
      "authorization_snapshot_provenance": "Follow-up Curator review of GP-VAL-008 from planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb after material event GP-X1-001 exact PASS and integration, independently rebound to live configurator 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3 on curation/portfolio-20260901-survivors-20260902.",
      "automated_validation": [
        "A new strict fixture contains exactly nine unique normalized-axis cases in canonical index order, exact direction labels and raw points, exact evidence/user/source identities, and bounded non-claims; duplicate/missing/reordered/extra/unknown fields fail.",
        "The checker extracts current kX1Table through the accepted source extractor and structurally binds the sole/non-mode X1 selection, clamped direction-index formula, active-table lookup, and output assignment without importing the historical evaluator or executing firmware.",
        "Wrong mode/modifier state, index, coordinate, evidence commit/path/mode/blob, candidate/artifact/integration identity, source fragment, table byte, active publication, hardware-result classification, or broadened claim fails in isolated adversarial cases.",
        "Focused X1 regression, source-sync, baseline, source-authority intake, symbol-map, activation-alternative, manifest, census, health, full runtime-config aggregate, framework, sequence, navigation, agent-surface, py_compile, and exact-diff checks pass with fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H1 offline current-source/evidence checker and inert fixture only; any compiled source or table-byte delta stops and requires separate H2 authorization.",
      "expected_artifact": "NOT_APPLICABLE",
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": [],
      "rollback_recovery": "Drop the focused checker/fixture branch if exact source/evidence correspondence cannot be expressed without unsupported semantics; retain GP-X1-001 evidence and historical evaluator exclusion unchanged.",
      "status_documentation_updates": "Document the one current X1 regression subset and its immutable evidence limits without broadening physical acceptance or current runtime-config capability claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "84ba70d28629134c92d0b0d25c9d05fb4bd2596c",
        "reviewed_implementation_sha": "63616108477bff72e1cda49572a56601782bac3b",
        "prior_canonical_integration_sha": "63616108477bff72e1cda49572a56601782bac3b",
        "reviewed_changed_paths": [
          "docs/runtime_config/current_x1_regression_subset.md",
          "docs/runtime_config/fixtures/current_x1_regression_subset.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_current_x1_regression_subset.py"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer PASS after strict identity/schema and adversarial-coverage repairs on exact implementation snapshot 63616108477bff72e1cda49572a56601782bac3b.",
        "validation_provenance": "Focused X1 checker, py_compile, manifest, census, health, full 29-check runtime-config aggregate, framework, sequence, navigation, agent-surface, candidate-generation isolation, and exact diff checks passed; no firmware build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "Any expected behavior lacks exact current source plus accepted user/evidence provenance.",
        "Any historical literal, physical binding, mode+X1, additional modifier/override, digital/gameplay, Nunchuk, root-cause, or general simulation claim enters scope.",
        "Any firmware/runtime/table/publication source, build input, artifact, device, persistence, write, flashing, or hardware state changes.",
        "Any hardware PASS is inferred beyond the immutable nine-row sole/non-mode X1 record."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null
    },
    {
      "id": "GP-BUILD-001",
      "title": "Fail closed on pre-build Git identity",
      "status": "DONE",
      "branch": "glyph/gp-build-001-prebuild-git-identity-20260902",
      "objective": "Preserve successful firmware-version stamping while making Git identity and dirtiness failures stop the build and eliminating process-global Git configuration mutation from the PlatformIO pre-build script.",
      "why_this_matters": "builder_scripts/arduino_pico.py performs an unchecked git config --global write and unchecked identity/status reads; command failure can embed an empty or misleading FIRMWARE_VERSION while the build continues.",
      "hardware_risk": "H1",
      "behavioral_claim": "For successful reads, clean source still embeds the existing lowercase abbreviated HEAD and any staged, unstaged, or untracked change appends -DIRTY with the existing escaped CPPDEFINE representation. Missing Git, command failure, empty/multiline/nonhex identity, or unreadable status fails before env.Append and no global Git configuration is written. This changes build-failure safety and version metadata only, not controller runtime behavior.",
      "scope": "After GP-PROV-008 is integrated, update only builder_scripts/arduino_pico.py for an explicit repository root, checked command-local git -c core.longpaths=true rev-parse --short HEAD and git -c core.longpaths=true status --porcelain --untracked-files=normal calls, strict output validation, and failure before env.Append. Factor an injectable/pure identity helper in that file and add a dedicated isolated checker with temporary Git repositories/fake runner. Add the checker as current load-bearing validation and update only the now-complete GP-PROV-008 builder hash plus deterministic manifest/census/health consequences. Build the exact clean committed implementation snapshot.",
      "explicit_excluded_scope": "No selector, dependency, pin, wrapper, PlatformIO configuration, workflow, postprocessor, version-format change on successful reads, firmware logic/table/routing/publication, artifact acceptance/upload/store, device, persistence, WebSerial/protobuf write, flashing, hardware acceptance, Nunchuk, root-cause, or gameplay claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "On live configurator 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3, platformio.ini selects builder_scripts/arduino_pico.py at tracked blob e883cb393ab0ec9b1e499a333cb189cc666cf386 and SHA-256 456a4b7d5582bbeb0244868db28920cd0f276d3db1924b36b401047cdf4569c2. That script runs unchecked git config --global core.longpaths true, unchecked git rev-parse --short HEAD, and unchecked git status --porcelain, then derives FIRMWARE_VERSION. No current checker enforces failure or global-mutation behavior. docs/WORKFLOW.md requires exact build snapshots and forbids unsafe mutation; Planner candidate GP-BUILD-001 and independent verification confirm the surviving gap.",
      "dependencies_prerequisites": [
        "GP-PROV-008 is reviewed, integrated, and recorded DONE on live configurator with schema-v2 local-entrypoint provenance and historical-object GP-PROV-004 validation passing.",
        "builder_scripts/arduino_pico.py, platformio.ini selection, successful FIRMWARE_VERSION abbreviation/-DIRTY/escaping behavior, and the canonical build command remain materially identical to live configurator 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3.",
        "No equivalent fail-closed pre-build identity repair is already integrated, and no legitimate concurrent canonical writer is active."
      ],
      "substantive_authorization_rationale": "The successful and error contracts are fully resolved: preserve existing successful output, classify any ordinary staged/unstaged/untracked porcelain result as dirty, make every identity/status ambiguity fatal before define publication, use command-local longpaths configuration, and never write global Git state. Waiting only prevents the builder hash change from invalidating the old schema-v1 provenance lane before GP-PROV-008 can absorb it; no later judgment is required.",
      "mechanical_activation_conditions": [
        "Live configurator records GP-PROV-008 as DONE with its exact reviewed schema-v2 inventory and historical-object observation preservation integrated and passing.",
        "The current builder script and platformio.ini selector still match the exact source authority recorded here except for deterministic GP-PROV-008 provenance identities.",
        "No equivalent repair exists, the canonical worktree is clean, the live remote is verified, and no legitimate concurrent queue or configurator writer is active."
      ],
      "invalidation_conditions": [
        "GP-PROV-008 completes with a materially different schema, builder-identity update path, or observation-preservation contract.",
        "The builder script, PlatformIO selection, successful version format/quoting, Git dirty semantics, canonical build policy, or build-input topology changes before activation.",
        "Implementation would require a global Git write, best-effort/UNKNOWN identity, selector/pin/workflow/wrapper change, runtime behavior change, or hardware interpretation.",
        "Another canonical change supplies equivalent or stronger pre-build identity failure and no-global-mutation enforcement first."
      ],
      "authorization_snapshot_provenance": "Follow-up Curator substantive review of GP-BUILD-001 from planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb, packet base 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c, against exact live configurator 3a7ed95213d01f2d4ab4cd8e11e2b5376b2980b3 with independent builder/provenance verification; PREAUTHORIZED on curation/portfolio-20260901-survivors-20260902 and waiting only on GP-PROV-008 integration.",
      "automated_validation": [
        "Isolated clean, staged, unstaged, and untracked repositories produce exactly lowercase abbreviated HEAD or that value plus -DIRTY with the existing escaped define representation; ignored-only state does not add -DIRTY.",
        "Missing Git/repository, nonzero rev-parse/status, empty/multiline/nonhex identity, unexpected status failure, wrong cwd/argv/order, absent command-local longpaths, any --global/config write, or env.Append before complete validation fails.",
        "The GP-PROV-008 inventory updates only the exact builder-script tracked hash/blob consequence while all local-entrypoint, wrapper, selector, historical observation, and unresolved identity records remain valid.",
        "Dedicated pre-build identity checker, provenance inventory/observation checks, manifest/adversarial, census, health, full runtime-config aggregate, framework, sequence, navigation, agent-surface, py_compile, exact diff, and canonical pio run -e glyph_mk6 pass on the exact clean committed snapshot with fresh independent review."
      ],
      "canonical_build": "pio run -e glyph_mk6; use the documented fallback only if the canonical executable is unavailable and report it explicitly.",
      "expected_artifact": ".pio/build/glyph_mk6/firmware.uf2",
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": [],
      "rollback_recovery": "Drop the focused builder/checker branch if successful version metadata is not byte/format invariant or any error can still publish a define; never restore a global Git config mutation or fail-open identity result.",
      "status_documentation_updates": "After exact reviewed integration, record fail-closed pre-build identity and preserved successful version semantics without artifact acceptance, reproducibility, runtime, or hardware claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "0fbaebfc4729439f10f5e541e995547e46399e8b",
        "reviewed_implementation_sha": "ecbbf5beecae5a5f8837d4261298c8304e2dec96",
        "prior_canonical_integration_sha": "ecbbf5beecae5a5f8837d4261298c8304e2dec96",
        "reviewed_changed_paths": [
          "builder_scripts/arduino_pico.py",
          "docs/runtime_config/fixtures/build_input_provenance_inventory.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_prebuild_git_identity.py"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer PASS, repaired-scope PASS, and PlatformIO compatibility repaired-scope PASS on the exact implementation snapshot.",
        "validation_provenance": "Focused pre-build identity, provenance, observations, manifest, census, health, full current aggregate, framework, navigation, agent-surface, syntax, diff, and canonical pio run -e glyph_mk6 passed on the exact clean committed snapshot; UF2 build output was not hardware-accepted."
      },
      "stop_conditions": [
        "GP-PROV-008 is not exact DONE and passing, or activation requires interpretation rather than objective checks.",
        "Any successful clean/dirty FIRMWARE_VERSION format or quoting changes, any Git ambiguity remains nonfatal, or any global/repository Git configuration is mutated.",
        "Any selector, dependency, wrapper, workflow, postprocessor, firmware runtime/table/publication, artifact/store, device, persistence, write, flashing, or hardware scope appears.",
        "The exact committed implementation snapshot does not pass the canonical build or documented fallback."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null
    },
    {
      "id": "GP-X1-001",
      "title": "Realize exact X1 offset-41 source-owned hardware candidate",
      "status": "DONE",
      "branch": "runtime-config-x1-offset41-hardware-candidate",
      "objective": "Realize the project-owner-supplied exact raw X1 9-way coordinates at center-relative plus or minus 41 through the existing source-owned overlay-preserve path, preserving every other active table and the current publication/routing path.",
      "why_this_matters": "The project owner requested one bounded behavior-changing X1 candidate for direct controller testing and supplied the exact raw values without asking Glyph to infer gameplay meaning.",
      "hardware_risk": "H2",
      "behavioral_claim": "On the existing sole/non-mode X1 path, kX1Table contains neutral (128,128), cardinals (87,128), (169,128), (128,87), (128,169), and diagonals (87,87), (169,87), (87,169), (169,169). The project owner reported all expected outputs and no disconnects for the exact candidate/artifact pair.",
      "scope": "Candidate-specific overlay_preserve ownership of kX1Table only; exact nine raw coordinates; source-owned generator/intake realization; exact committed candidate build; independent source/diff review; local UF2 handoff; Revision-2 reconciliation of the human hardware PASS; and exact-candidate publication recovery.",
      "explicit_excluded_scope": "No X2, Y1/Y2, Tilt, layer/flipper, routing, button-binding, controller-semantic, gameplay-semantic, other modifier, other source-owned table, alternate publication, runtime-loaded config, persistence, WebSerial/device write, protobuf write, flashing automation, release/upload, Nunchuk, or root-cause claim.",
      "touched_planes": [
        "source-owned configuration",
        "generated tables/artifacts",
        "firmware runtime",
        "docs/checkers"
      ],
      "source_authority": "Project-owner directions GLYPH-UD-010 and GLYPH-UD-011 authorize only the exact candidate-specific X1 raw coordinates and preserve all other tables and publication behavior. Candidate intake docs/runtime_config/intakes/x1_offset41_overlay_hardware_candidate.intake.json records overlay_preserve with owned_tables=[kX1Table].",
      "dependencies_prerequisites": [
        "Exact live base configurator 045bca0d1450c261c3c60ccf5ef86f7302bd3dbc.",
        "Existing generated-source-owned include chain and RuntimeConfigView publication remain unchanged.",
        "Exact candidate/artifact identity and direct human physical report are available before source integration."
      ],
      "substantive_authorization_rationale": "The project owner explicitly supplied the complete nine-value X1 intent, superseded the prior no-op restriction for this candidate only, excluded all other behavior, and later directed processing of the real successful hardware results. No gameplay or cross-table judgment was delegated to the implementer.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The candidate ref no longer resolves exactly to 74ae24364b84520d4e0e39240beb9867653cc7b9.",
        "The preserved UF2 no longer hashes exactly to the recorded SHA-256.",
        "Any non-X1 active table, routing, publication path, or other runtime source differs from the reviewed candidate delta.",
        "The structured PASS evidence does not correspond exactly to the recorded candidate/artifact pair."
      ],
      "authorization_snapshot_provenance": "User Codex task supplied 2026-09-02, recorded as GLYPH-UD-010/011 in exact candidate 74ae24364b84520d4e0e39240beb9867653cc7b9; follow-up direct user reports confirmed expected outputs, no disconnects, successful restoration of the prior UF2, and direction to proceed with the real results.",
      "automated_validation": [
        "Generator classification EXPLICIT_OWNED_TABLE_CHANGESET with changed_table_ids=[2] and preserved_table_count=27.",
        "Independent exact base-to-candidate inspection confirmed only kX1Table semantic contents changed and publication/routing source remained unchanged.",
        "Focused source-owned generator, symbol-map, identity-sync, activation-alternative, framework, navigation, and surface checks passed on the candidate.",
        "Fallback canonical-policy build ./scripts/build-glyph-mk6-quiet.sh passed because the pio executable was unavailable; exact UF2 SHA-256 was recorded."
      ],
      "canonical_build": "pio run -e glyph_mk6 was unavailable in the environment; documented fallback ./scripts/build-glyph-mk6-quiet.sh succeeded for exact candidate 74ae24364b84520d4e0e39240beb9867653cc7b9.",
      "expected_artifact": ".pio/build/glyph_mk6/firmware.uf2",
      "candidate_git_sha": "74ae24364b84520d4e0e39240beb9867653cc7b9",
      "candidate_base_configurator_sha": "045bca0d1450c261c3c60ccf5ef86f7302bd3dbc",
      "firmware_artifact_build_path": ".pio/build/glyph_mk6/firmware.uf2",
      "preserved_firmware_artifact_locator": "local_backups/hardware-artifacts/74ae24364b84520d4e0e39240beb9867653cc7b9/5fadd3d7e82e629fbccd41fac868312b07b01e39d2ef0a0a98a06d649ae28254/firmware.uf2",
      "firmware_artifact_sha256": "5fadd3d7e82e629fbccd41fac868312b07b01e39d2ef0a0a98a06d649ae28254",
      "manual_acceptance": "REQUIRED",
      "manual_acceptance_protocol_reference": "docs/calibration/x1_offset41_hardware_test_protocol_2026-09-02.md",
      "manual_acceptance_protocol_version": "GLYPH_X1_OFFSET41_MANUAL_PROTOCOL_V1",
      "hardware_evidence_contract_reference": "docs/agent_framework/HARDWARE_EVIDENCE.md",
      "hardware_evidence_contract_version": "GLYPH_HARDWARE_EVIDENCE_V2",
      "hardware_evidence_record": "git-json:6b0061489cb67d345f212f75268455c181ba271f:docs/calibration/fixtures/x1_offset41_hardware_evidence_2026-09-02.json",
      "hardware_result": "PASS",
      "hardware_evidence_gaps": [],
      "rollback_recovery": "A prior configurator 045bca0d1450c261c3c60ccf5ef86f7302bd3dbc UF2 was regenerated and supplied with SHA-256 69064a5c1d52772926fe010a593f2a2e04e9675a638737b619b7b0bc4785d001; the project owner confirmed it worked after restoration.",
      "status_documentation_updates": "Exact PASS evidence was published without candidate source; publication recovery reverified identity/evidence, merged only the exact tested candidate, aligned accepted-baseline validators without further firmware-source changes, and published strict DONE correspondence.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "045bca0d1450c261c3c60ccf5ef86f7302bd3dbc",
        "reviewed_implementation_sha": "74ae24364b84520d4e0e39240beb9867653cc7b9",
        "prior_canonical_integration_sha": "1597c01b416b6aa697d73efc7d2c2b3695dc3e5c",
        "reviewed_changed_paths": [
          "docs/agent_framework/USER_DIRECTION.md",
          "docs/runtime_config/intakes/x1_offset41_overlay_hardware_candidate.intake.json",
          "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp"
        ],
        "independent_review_provenance": "Fresh independent candidate reviewer PASS on exact snapshot 74ae24364b84520d4e0e39240beb9867653cc7b9 confirmed only kX1Table changed semantically, exact requested values, 27 preserved tables, unchanged routing/publication, successful fallback build, and artifact identity; fresh evidence reviewer PASS confirmed bounded Revision-2 record correspondence after two precision fixes.",
        "validation_provenance": "Exact candidate/base and remote refs reverified; preserved UF2 rehashed to 5fadd3d7e82e629fbccd41fac868312b07b01e39d2ef0a0a98a06d649ae28254; immutable PASS evidence and protocol validated; pre-integration full runtime-config aggregate passed; merge staged blobs for the active header and intake matched the candidate exactly; post-integration source-sync, intake, census, health, framework, navigation, surface, semantic table, and full aggregate gates passed with no further firmware-source change."
      },
      "stop_conditions": [
        "Any exact candidate Git SHA, base SHA, artifact SHA, protocol, or evidence correspondence mismatch.",
        "Any active change outside kX1Table or any routing/publication delta.",
        "Any need to rebuild or substitute firmware bytes for hardware identity.",
        "Any runtime-loaded, persistence, device-write, flashing, release/upload, Nunchuk, root-cause, or gameplay scope."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": true
    },
    {
      "id": "GP-VAL-010",
      "title": "Bind manifest commands to tracked checkers",
      "status": "DONE",
      "branch": "glyph/gp-val-010-command-contract-20260901",
      "objective": "Make every validation-manifest command an exact execution contract for python3, one normalized stage-0 tracked regular checker path, and the manifest's reviewed required-argument vector before the aggregate can execute it.",
      "why_this_matters": "The aggregate currently accepts any nonempty string-list command, checks only command[1] against the declared path and filesystem existence, rejects all current nonempty required_arguments, and then executes the command directly. A manifest row can therefore name one checker while selecting another executable, wrapper, argument set, untracked regular-file target, or symlink without a complete fail-closed correspondence check; the existing directory rejection is untested regression behavior rather than a current directory-execution gap.",
      "hardware_risk": "H0",
      "behavioral_claim": "This strengthens aggregate-runner validation semantics and the exact aggregate-adversarial checker's isolated coverage only. It does not change the applicability, branch policy, semantic behavior, or source dependencies of any other checker executed from the manifest, nor product/runtime behavior, workflow, build input, firmware artifact, device, or controller behavior.",
      "scope": "Update tools/run_glyph_runtime_config_validation.py so every manifest entry requires path to satisfy the existing normalized tracked_regular_stage_zero policy, required_arguments to be a string list, and command to equal exactly [\"python3\", path, *required_arguments]. Reject malformed command vectors before indexing or execution. Update only tools/check_glyph_runtime_config_validation_aggregate.py isolated temporary-repository adversarial cases for alternate executable, shell/wrapper selection, extra or missing arguments, malformed required_arguments, command/path mismatch, untracked target, executable-mode checker, directory, symlink, absolute/escaping/non-normalized target, and one-element command. Preserve the current manifest schema, all 32 entry records and 37 exclusions, and regenerate only deterministic checker-census/validation-health consequences caused by the two authorized checker-byte changes.",
      "explicit_excluded_scope": "No PATH-resolved python3 binary identity or trust claim; no interpreter pin, wrapper, shell, timeout, aggregate execution isolation, canonical-worktree mutation detection, manifest entry/exclusion/applicability/branch-policy/source-dependency/load-bearing/reason change, semantic edit to any manifest-executed checker other than the exact authorized aggregate-adversarial coverage, or edit to any file beyond the exact aggregate runner/adversarial/census-health consequence surface, tools/glyph_checker_context.py change, workflow, build, product/runtime source, generator, table, artifact, device, persistence, WebSerial/protobuf write, flashing, hardware, Nunchuk, root-cause, or game-semantic change or claim. GP-VAL-011 aggregate isolation remains separate and non-executable.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Live configurator 30f5e348762eafec8ee2845d9d2c002ef5ebe18f. tools/run_glyph_runtime_config_validation.py accepts any nonempty all-string command list, then reads command[1], checks only entry.path equality plus filesystem is_file(), and executes the vector in canonical ROOT; its existing tracked_regular_stage_zero helper is applied to dependencies but not to the checker command target. Current entries incidentally use exactly [python3, path] with empty required_arguments, but tools/check_glyph_runtime_config_validation_aggregate.py has no alternate-executable, wrapper, argument-correspondence, untracked-target, directory, symlink, escaping-target, or one-element-vector adversarial cases. Planner packet glyph-portfolio-20260831-1540 at 896a06c092bfa2f99339c944fceffda957e4478d proposed GP-VAL-010; root and two bounded specialists independently confirmed the gap survives all four preceding repairs and no equivalent current gate exists.",
      "dependencies_prerequisites": [
        "Implementation starts from a fresh live-configurator descendant of 30f5e348762eafec8ee2845d9d2c002ef5ebe18f with manifest schema v4, the current 32 entries/37 exclusions, current command vectors, and the aggregate runner/adversarial checker materially unchanged.",
        "Every current and historical manifest command is mechanically rederived as exactly python3 plus the declared normalized checker path plus required_arguments in recorded order before editing; any noncanonical-argument lane remains excluded rather than silently activated.",
        "GP-SRC-004, GP-VAL-003, GP-VAL-009, and GP-CTL-001 remain canonically DONE with their reviewed correspondence repairs intact."
      ],
      "substantive_authorization_rationale": "The command-correspondence gap is direct and the architecture is fully resolved without product judgment. The manifest already separates path, command, and required_arguments; exact equality to [python3, path, *required_arguments] makes that representation unambiguous, while the existing normalized stage-0 tracked-regular policy prevents filesystem existence from substituting for repository identity. This binds only the declared command vector and explicitly makes no claim about the ambient PATH-resolved python3 executable. No checker applicability, semantic, runtime, external-evidence, or user decision remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The manifest schema, command/required_arguments representation, tracked_regular_stage_zero policy, current checker execution architecture, or aggregate adversarial harness changes materially before implementation.",
        "Another canonical change supplies equivalent or stronger exact interpreter/path/argument and tracked-checker correspondence first.",
        "Any current command requires a non-python3 interpreter, wrapper, extra implicit argument, untracked target, symlink, directory, escaping path, or product-semantic interpretation.",
        "The repair would require aggregate snapshot isolation, timeout policy, environment selection, semantic edits to any manifest-executed checker other than the exact authorized aggregate-adversarial coverage, manifest reclassification, tools/glyph_checker_context.py, workflow, build, product/runtime, artifact, device, or hardware scope."
      ],
      "authorization_snapshot_provenance": "Independent follow-up Curator review of candidate GP-VAL-010 from planning/portfolio-20260831-1540 commit 896a06c092bfa2f99339c944fceffda957e4478d, packet base d94eb6d629f9e8e73e893971a3f47c4485cf17ee, rebound after completion of the first four authorized repairs to live configurator 30f5e348762eafec8ee2845d9d2c002ef5ebe18f with root and bounded specialist source/manifest/adversarial verification on curation/portfolio-20260831-1540-followup.",
      "automated_validation": [
        "All 32 manifest entries pass only when command equals exactly [python3, path, *required_arguments], required_arguments is a list of strings, and path is one normalized stage-0 tracked regular non-symlink file; malformed vectors fail before indexing or execution.",
        "Isolated adversarial cases independently reject an alternate executable, shell/wrapper, extra or missing argument, malformed required_arguments, command/path mismatch, one-element command, absolute/escaping/non-normalized target, untracked file, directory, symlink, and executable-mode confusion without executing an unauthorized target.",
        "A positive isolated case with a reviewed tracked executable-mode Python checker proves Git mode alone is not confused with interpreter selection, while exact current command vectors remain unchanged and pass.",
        "Manifest schema v4 retains exactly 32 entries and 37 exclusions with byte-identical entry applicability, branch policy, required arguments, mutation risk, source dependencies, load-bearing, historical, and reason fields; only deterministic census/health identities caused by authorized checker bytes may change.",
        "Focused aggregate adversarial, manifest check, checker census, validation health, full runtime-config aggregate, agent-framework, sequence, navigation, agent-surface, py_compile, and exact diff checks pass with fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 aggregate manifest-command validation and isolated adversarial coverage only; any workflow, build input, generated/compiled source, or runtime delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused runner/adversarial/census-health branch if exact current command correspondence cannot be enforced without semantic edits to any other manifest-executed checker or without manifest classification changes; never restore acceptance of a command that can select a different executable, target, or argument vector than the reviewed manifest fields.",
      "status_documentation_updates": "Record GP-VAL-010 as Done only after exact reviewed integration and separate structured completion publication. Retain GP-VAL-011 as separately dependency/design gated and every runtime, product, artifact, and hardware non-claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "885daf198be7445bec9fa565eca6d3b2784c7842",
        "reviewed_implementation_sha": "6affdecb526b5571e507cf51d62d3b819b2926bb",
        "prior_canonical_integration_sha": "6affdecb526b5571e507cf51d62d3b819b2926bb",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_runtime_config_validation_aggregate.py",
          "tools/run_glyph_runtime_config_validation.py"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer PASS on exact repaired snapshot 6affdecb526b5571e507cf51d62d3b819b2926bb; command contract, adversarial target coverage, executable-mode coverage, and scope invariants confirmed.",
        "validation_provenance": "Focused aggregate adversarial, manifest, census, health, full current runtime-config aggregate, framework, sequence, navigation, agent-surface, py_compile, and diff checks passed on the exact integrated snapshot; no build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "Any manifest command can select an executable, checker target, or argument vector different from the exact reviewed interpreter/path/required_arguments fields.",
        "Any untracked, directory, symlink, escaping, malformed, or unauthorized target can reach execution.",
        "Any semantic behavior change to a manifest-executed checker other than the exact authorized aggregate-adversarial coverage, applicability, branch policy, source dependency, load-bearing classification, aggregate isolation/timeout architecture, file outside the exact authorized aggregate runner/adversarial/census-health consequence surface, workflow, build, product/runtime source, generator, artifact, device, persistence, WebSerial/protobuf write, flashing, hardware, Nunchuk, root-cause, or game-semantic scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-006",
      "title": "Structurally bind active source-owned publication",
      "status": "DONE",
      "branch": "glyph/gp-src-006-active-publication-structure-20260901",
      "objective": "Make the load-bearing source-owned checker enforce the exact approved active-state initializer and resolver structure instead of accepting required strings inside a materially different publication function.",
      "why_this_matters": "The current checker accepts a synthetic conditional or alternate return when the approved pointer fragment remains present and only the two named forbidden member strings are absent.",
      "hardware_risk": "H0",
      "behavioral_claim": "This strengthens static source-structure validation only. It changes no firmware source, active table byte, routing, runtime behavior, build input, artifact, device, or hardware state.",
      "scope": "Update tools/check_glyph_source_owned_table_symbol_map.py and isolated temporary-source adversarial coverage so GetActiveRuntimeConfigState() has exactly the current static_assert, one static const ActiveRuntimeConfigState initializer containing the approved baseline pointer/source/status members, and one return of that state; ResolveActiveRuntimeConfig() has exactly one return dereferencing GetActiveRuntimeConfigState().active_view. Reject alternate or conditional returns, extra state publication, mismatched enums, parser/load-state reads, wrapper publication, RAM-backed views, and indirect resolver paths. Regenerate only deterministic checker-census or validation-health consequences caused by the checker byte change.",
      "explicit_excluded_scope": "No src/ firmware edit, active table or routing change, RuntimeConfigView replacement, candidate.view or active_storage.view publication, parser/materialization/load integration, runtime-loaded config, persistence, workflow, build input, artifact, device write, protobuf write, flashing, hardware, Nunchuk, root-cause, or gameplay claim. No tools/glyph_checker_context.py change.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Live configurator 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c. src/modes/Ultimate.cpp has the accepted single-state/single-return structure at GetActiveRuntimeConfigState() and ResolveActiveRuntimeConfig(). tools/check_glyph_source_owned_table_symbol_map.py currently requires only pointer/return fragments and rejects candidate.view and active_storage.view tokens, so structurally different alternate returns pass. Planner candidate GP-SRC-006 in planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb and independent specialist inspection confirm no equivalent stronger current gate.",
      "dependencies_prerequisites": [
        "Implementation starts from a fresh live-configurator descendant of 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c with the accepted Ultimate.cpp publication shape and checker materially unchanged.",
        "GP-SRC-001 remains DONE and the approved source-owned publication boundary remains current."
      ],
      "substantive_authorization_rationale": "The accepted source shape and forbidden alternatives are already durably resolved by current source and boundary documents. Structural enforcement is a checker-only H0 repair with no product, gameplay, firmware, or hardware decision left to the implementer.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The accepted active-state or resolver topology changes before implementation.",
        "Another canonical change supplies equivalent or stronger exact structural enforcement first.",
        "The repair would require firmware source, tools/glyph_checker_context.py, product/runtime checker semantics beyond this exact checker, build, artifact, device, or hardware scope."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of Planner candidate GP-SRC-006 from planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb, packet/live base 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c, with root and bounded specialist source/checker verification on curation/portfolio-20260901-0909-review.",
      "automated_validation": [
        "Exact current GetActiveRuntimeConfigState() and ResolveActiveRuntimeConfig() source passes.",
        "Isolated mutations for alternate/conditional pointers, extra returns, mismatched source/status enums, parser/load-state reads, wrapper publication, RAM-backed publication, and indirect resolution fail independently.",
        "Focused symbol-map, source-sync, checker-census, validation-health, full runtime-config aggregate, agent-framework, sequence, navigation, agent-surface, py_compile, and exact-diff checks pass with fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 checker-only structural enforcement; any firmware or build-input delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused checker branch if exact current source cannot be accepted without weakening the source-owned publication boundary.",
      "status_documentation_updates": "Record GP-SRC-006 Done only after reviewed integration and structured completion publication; preserve every current runtime and hardware non-claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "325defbbf7e1cdefe6f7578a924b96073c95dcb6",
        "reviewed_implementation_sha": "bcf5831c00f8ab3a34576e544d9b795eac89e826",
        "prior_canonical_integration_sha": "783334b7476f2c68335d6f312669eac72e78316f",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_source_owned_table_symbol_map.py"
        ],
        "independent_review_provenance": "Fresh independent reviewer PASS on repaired exact snapshot bcf5831c00f8ab3a34576e544d9b795eac89e826; exact publication topology, all required adversarial mutation classes, scope, and non-claims confirmed.",
        "validation_provenance": "Focused source-owned symbol-map, checker census, validation health, full runtime-config aggregate, framework, latest-Y2 source sync, navigation, agent-surface, py_compile, and exact-diff checks passed on the integrated snapshot; no build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "Any active publication, table, routing, firmware, build, artifact, device, or hardware behavior would change.",
        "The checker would accept multiple publication outcomes or rely only on string presence.",
        "Any forbidden runtime-loaded, persistence, device-write, flashing, Nunchuk, root-cause, or gameplay scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-013",
      "title": "Prove executable validation before publication",
      "status": "DONE",
      "branch": "glyph/gp-val-013-executable-publication-gate-20260901",
      "objective": "Repair the accepted GP-VAL-002 outcome by proving that the current aggregate is an executable workflow step and structurally dominates every locally controlled build, postprocess, and upload route.",
      "why_this_matters": "The current static workflow checker scans raw YAML text and accepts the required aggregate command in a comment followed by true, so publication can appear gated without executing validation.",
      "hardware_risk": "H0",
      "behavioral_claim": "This strengthens offline workflow-structure validation only. It changes no workflow YAML, build input, artifact route, product/runtime behavior, device, or hardware state.",
      "scope": "Add tools/glyph_workflow_step_contract.py as the single bounded fail-closed parser for the repository's current workflow job, steps, run, uses, needs, and continue-on-error subset, consume it from tools/check_glyph_runtime_config_validation_publication_workflow.py, and extend isolated adversarial coverage. Prove the exact aggregate command is executable in the validation job and that every CURRENT_GATED local build, glyph_nuker, and upload route depends on successful validation. Reject comments, inert/shadowed commands, unsupported scalar shapes, duplicate ambiguous steps, wrong jobs, permissive failure, missing needs, and alternate unguarded local publication routes. Preserve UNRESOLVED_EXTERNAL nested routes. Update only the existing workflow checker's manifest source_dependencies to add tools/glyph_workflow_step_contract.py and regenerate deterministic census/health consequences.",
      "explicit_excluded_scope": "No .github/workflows YAML edit, trigger, permission, branch-base, upload, artifact, checker-applicability, build, product/runtime, device, or hardware change; no external YAML package; no workflow execution; no claim that UNRESOLVED_EXTERNAL routes are gated; no tools/glyph_checker_context.py change.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Live configurator 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c. .github/workflows/build.yml currently contains a real validation step and build needs validation, but tools/check_glyph_runtime_config_validation_publication_workflow.py uses raw substring and regex scans; a comment-only aggregate command is accepted. Planner GP-VAL-002 repair in packet 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb and independent verification confirm the incomplete executable-step correspondence.",
      "dependencies_prerequisites": [
        "Implementation starts from fresh live configurator with the current workflow and publication census materially unchanged.",
        "GP-VAL-010 command identity remains source-correspondent; implementation may proceed independently because this order parses the exact existing aggregate command without changing runner semantics."
      ],
      "substantive_authorization_rationale": "The original publication-gating intent is accepted, the defect is directly reproducible, and the smallest safe architecture is a fail-closed parser for the finite current YAML subset with no workflow mutation or external dependency. No product, artifact-store, firmware, or hardware decision remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Workflow topology or the exact validation command changes materially before implementation.",
        "A canonical change provides equivalent executable-step and dominance proof first.",
        "The parser would need an external dependency, workflow execution, YAML mutation, checker reclassification, tools/glyph_checker_context.py, or product/runtime scope."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of the GP-VAL-002 repair candidate from planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb against packet/live base 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c. GP-VAL-013 is the executable repair identity while the historical GP-VAL-002 completion record remains immutable.",
      "automated_validation": [
        "Exact current workflow parses and proves one executable validation step dominates every CURRENT_GATED local publication route.",
        "Comment-only, inert, folded/block ambiguity, duplicate/shadowed step, wrong-job, continue-on-error, missing-needs, and alternate-route mutations fail closed; unsupported shapes fail rather than being inferred.",
        "No test executes GitHub Actions, PlatformIO, glyph_nuker, artifact upload, or device access.",
        "Focused workflow checker, publication census, artifact workflow checker where applicable, census, health, full aggregate, framework, sequence, navigation, surface, py_compile, and exact diff checks pass with fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 static checker-only repair; workflow and build inputs remain unchanged.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused checker branch if current workflow syntax cannot be parsed fail closed; never restore acceptance based on comment or raw substring presence.",
      "status_documentation_updates": "Record GP-VAL-013 Done only after reviewed integration; retain historical GP-VAL-002 evidence and all external-route/artifact/hardware non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "b0255a3b8e80cafc65d20526aa42769b1b402316",
        "reviewed_implementation_sha": "dae87ac468f3c9ce6512fc96f855083054668a29",
        "prior_canonical_integration_sha": "dae87ac468f3c9ce6512fc96f855083054668a29",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/fixtures/runtime_config_validation_publication_workflow.json",
          "tools/check_glyph_runtime_config_validation_publication_workflow.py",
          "tools/glyph_workflow_step_contract.py"
        ],
        "independent_review_provenance": "Fresh independent reviewer identified and confirmed repair of conditional-step bypass; repaired-scope PASS on exact snapshot dae87ac468f3c9ce6512fc96f855083054668a29.",
        "validation_provenance": "Focused workflow checker with 15 adversarial cases, aggregate adversarial, checker census, validation health, docs navigation, docs agent surface, agent framework, agentic sequence, and py_compile passed; workflow YAML, firmware, build input, artifact, device, and hardware state unchanged."
      },
      "stop_conditions": [
        "Any workflow YAML, build input, artifact route, product/runtime, device, or hardware state would change.",
        "The checker can pass on comment-only or ambiguous non-executable text.",
        "Any external-route gating or artifact-acceptance claim is inferred."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-007",
      "title": "Bind executable sidecar route and unique JSON identity",
      "status": "DONE",
      "branch": "glyph/gp-prov-007-sidecar-execution-json-identity-20260901",
      "objective": "Repair the accepted GP-PROV-002 outcome by proving its checkout, sidecar generation, and verification commands are executable workflow steps and by rejecting duplicate JSON keys before identity comparison.",
      "why_this_matters": "The workflow checker accepts comment-only command text and ordinary json.loads accepts a bogus first and correct last duplicate identity key.",
      "hardware_risk": "H1",
      "behavioral_claim": "This strengthens static workflow and observed-only sidecar verification only; it changes no workflow, postprocessor, artifact, product/runtime, device, or hardware behavior.",
      "scope": "After GP-VAL-013 lands, reuse its exact reviewed executable-step parser in tools/check_glyph_artifact_postprocessor_workflow.py, add duplicate-key rejection to tools/check_glyph_artifact_postprocessor_provenance.py, extend isolated workflow and JSON adversarial cases, update only the existing artifact workflow checker's manifest source_dependencies to name the shared helper, and regenerate deterministic census/health consequences.",
      "explicit_excluded_scope": "No workflow YAML, sidecar schema, postprocessor bytes/invocation, artifact generation/upload/store, immutable locator, reproducibility, acceptance, firmware/runtime, device, or hardware change or claim.",
      "touched_planes": [
        "docs/checkers",
        "build tooling"
      ],
      "source_authority": "Live configurator c3f3438172c8de977d390c9a2fb2c1037262e2a9; the exact-bound artifact workflow/provenance checkers and sidecar fixture remain byte-identical to the independently reproduced GP-PROV-002 repair gaps in Planner packet 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb. GP-VAL-013 integrated the reviewed shared parser at blob 5c625ff47655acd4ac795cbfc2f0a26fe2d53eb0 without workflow mutation. Independent successor review found the prior Preauthorization literally invalidated only because its predecessor path allowlist omitted the reviewed publication-workflow adversarial fixture; no successor input, artifact behavior, or product/runtime authority changed.",
      "dependencies_prerequisites": [
        "GP-VAL-013 is canonically DONE with tools/glyph_workflow_step_contract.py integrated through strict structured completion evidence and no workflow mutation.",
        "GP-VAL-012 completes first without changing the runtime-config validation manifest, so GP-PROV-007's authorized manifest source-dependency update cannot invalidate the earlier zero-category repair before it executes.",
        "At activation, .github/workflows/build.yml, tools/glyph_workflow_step_contract.py, tools/check_glyph_artifact_postprocessor_workflow.py, tools/check_glyph_artifact_postprocessor_provenance.py, and docs/runtime_config/fixtures/artifact_postprocessor_provenance.json have the exact rebound blob identities recorded in the mechanical activation conditions."
      ],
      "substantive_authorization_rationale": "The substantive decision is complete: once the shared parser exists, reuse it rather than create divergent workflow interpretation, and reject duplicate keys at every JSON load boundary before semantic checks. Remaining work is objective and mechanical.",
      "mechanical_activation_conditions": [
        "Live configurator records GP-VAL-013 as DONE with strict completion evidence whose reviewed implementation is integrated and whose changed paths are exactly docs/runtime_config/fixtures/glyph_checker_census.json, docs/runtime_config/fixtures/runtime_config_validation_manifest.json, docs/runtime_config/fixtures/runtime_config_validation_publication_workflow.json, tools/check_glyph_runtime_config_validation_publication_workflow.py, and tools/glyph_workflow_step_contract.py; workflow YAML remains unchanged.",
        "Live configurator records GP-VAL-012 as DONE with strict reviewed completion evidence, and its implementation changed no runtime-config validation manifest field or blob.",
        "At activation, Git blobs equal exactly .github/workflows/build.yml=d01c382e48bf71bd12ae41430b89d156ad8237e5, tools/glyph_workflow_step_contract.py=5c625ff47655acd4ac795cbfc2f0a26fe2d53eb0, tools/check_glyph_artifact_postprocessor_workflow.py=c228c6afb3c2cd42d8a34dfc437b1638dc96748d, tools/check_glyph_artifact_postprocessor_provenance.py=ded2459117e0ac78c475a289517ddbd69d83683d, and docs/runtime_config/fixtures/artifact_postprocessor_provenance.json=9a3089707fe3544ff5284f790d25ae5f9a89a025.",
        "The runtime-config validation manifest remains blob 82380ccb0205835254a52f3b3edddeedc7ae3124 immediately before GP-PROV-007 activation; implementation may then add only tools/glyph_workflow_step_contract.py to the existing artifact_postprocessor_workflow entry's source_dependencies as already authorized."
      ],
      "invalidation_conditions": [
        "GP-VAL-013 completion evidence, exact five-path set, or tools/glyph_workflow_step_contract.py architecture differs from the rebound authorization snapshot.",
        "GP-VAL-012 does not complete first, changes the runtime-config validation manifest, or broadens beyond its rebound zero-category repair.",
        "Any recorded workflow, shared parser, artifact checker, provenance checker, sidecar fixture, or pre-activation manifest blob differs from the exact rebound identity.",
        "Implementation requires workflow, postprocessor, artifact-store, product/runtime, device, or hardware changes."
      ],
      "authorization_snapshot_provenance": "Independent Curator reauthorization of GP-PROV-007 from planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb, originally reviewed at live base 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c, rebound after explicit path-set invalidation to clean live configurator c3f3438172c8de977d390c9a2fb2c1037262e2a9 on curation/portfolio-20260901-successor-reauthorization. Root and bounded specialists verified exact predecessor ancestry/path correspondence, all successor blobs, unchanged workflow/product inputs, and the sequencing dependency on GP-VAL-012. GP-PROV-007 preserves historical GP-PROV-002 completion.",
      "automated_validation": [
        "Comment-only, inert, reordered, wrong-job, and shadowed sidecar workflow steps fail through the shared parser.",
        "Duplicate top-level and nested JSON keys fail before identity comparison; exact deterministic current sidecar passes.",
        "Focused workflow/provenance, census, health, aggregate, framework, sequence, navigation, surface, py_compile, and diff checks pass with independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host-side CI sidecar validation only; workflow and firmware build-input bytes remain unchanged, so a firmware build is not relevant evidence.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused repair if parser reuse or duplicate-key rejection cannot be preserved without broader artifact semantics.",
      "status_documentation_updates": "Record GP-PROV-007 Done after exact reviewed integration and structured completion publication while retaining all artifact and hardware non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "a1225102179639f06bb00a6735987824b85972ae",
        "reviewed_implementation_sha": "721cd20388c39beefe6b1b85ce25228a7efe6a0e",
        "prior_canonical_integration_sha": "721cd20388c39beefe6b1b85ce25228a7efe6a0e",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "tools/check_glyph_artifact_postprocessor_provenance.py",
          "tools/check_glyph_artifact_postprocessor_workflow.py"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer PASS on exact reviewed snapshot 721cd20388c39beefe6b1b85ce25228a7efe6a0e; focused workflow/provenance, census, health, aggregate, framework, navigation, agent-surface, py_compile, and diff gates passed.",
        "validation_provenance": "Exact integrated H1 host-side checker snapshot passed the authorized focused and full validation gates; no workflow, build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "The activation dependency is absent, drifted, or requires interpretation.",
        "Any workflow, postprocessor, artifact route, product/runtime, device, or hardware state changes.",
        "Duplicate JSON identities can still be accepted."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-012",
      "title": "Reject zero-execution category success",
      "status": "DONE",
      "branch": "glyph/gp-val-012-zero-category-rejection-20260901",
      "objective": "Make every explicit aggregate category request fail when any requested category selects zero current executable checks.",
      "why_this_matters": "The live historical_evidence category request returns PASS with an empty results list because selection filters to current entries and all([]) succeeds.",
      "hardware_risk": "H0",
      "behavioral_claim": "This strengthens aggregate selection validation only and does not promote historical checks, change checker semantics, or affect product/runtime behavior.",
      "scope": "After GP-VAL-010 lands, update tools/run_glyph_runtime_config_validation.py and isolated aggregate adversarial fixtures so each explicitly requested category must select at least one current manifest entry; fail the whole request if any requested category is empty. Preserve unfiltered aggregate behavior and all manifest applicability/category classifications.",
      "explicit_excluded_scope": "No historical or unsafe checker promotion/execution, manifest field or blob edit, manifest reclassification, checker semantic edit, workflow, build, runtime, artifact, device, or hardware change.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Live configurator c3f3438172c8de977d390c9a2fb2c1037262e2a9. python3 tools/run_glyph_runtime_config_validation.py --category historical_evidence --json still returns exit zero, PASS, and results empty. GP-VAL-010's reviewed runner and aggregate-adversarial blobs remain exact. GP-VAL-013 changed only the manifest source_dependencies of validation_publication_workflow; all category/applicability tuples remain unchanged. Independent successor review confirmed the original whole-manifest binding was literally invalidated while the GP-VAL-012 substantive gap and scope remain unchanged.",
      "dependencies_prerequisites": [
        "GP-VAL-010 is canonically DONE with exact command/path/argument correspondence and strict structured completion evidence.",
        "The manifest category/applicability tuples remain byte-identical to authorization base and all runner/adversarial drift is exactly GP-VAL-010's reviewed implementation."
      ],
      "substantive_authorization_rationale": "The desired fail-closed result is fully resolved; GP-VAL-010 is the only mechanical predecessor because both touch runner validation and adversarial coverage. No classification or product judgment remains.",
      "mechanical_activation_conditions": [
        "Live configurator records GP-VAL-010 as DONE with strict completion evidence whose reviewed implementation 6affdecb526b5571e507cf51d62d3b819b2926bb is integrated and whose reviewed changed paths are exactly docs/runtime_config/fixtures/glyph_checker_census.json, tools/check_glyph_runtime_config_validation_aggregate.py, and tools/run_glyph_runtime_config_validation.py.",
        "At activation, docs/runtime_config/fixtures/runtime_config_validation_manifest.json remains exact rebound blob 82380ccb0205835254a52f3b3edddeedc7ae3124, tools/run_glyph_runtime_config_validation.py remains exact reviewed blob 8914130b76c1615cae45169a800b9414d49c9842, and tools/check_glyph_runtime_config_validation_aggregate.py remains exact reviewed blob cc4114546c4eebbe2b87e03a9d619118b9f3f611; no manifest category or applicability field is changed by implementation.",
        "The exact live command python3 tools/run_glyph_runtime_config_validation.py --category historical_evidence --json still returns success with an empty results list immediately before activation, proving the authorized gap remains and has not been superseded."
      ],
      "invalidation_conditions": [
        "GP-VAL-010 completion evidence or reviewed runner/adversarial blobs differ from the exact rebound identities, or the manifest differs from 82380ccb0205835254a52f3b3edddeedc7ae3124 before implementation.",
        "Another canonical change already rejects every requested zero-result category, or the exact historical_evidence probe no longer reproduces the gap.",
        "Implementation would require historical execution, category reclassification, workflow, build, product/runtime, artifact, device, or hardware scope."
      ],
      "authorization_snapshot_provenance": "Independent Curator reauthorization of Planner candidate GP-VAL-012 from planning/portfolio-20260901-0909 commit 3fb785749d8653e91bb8e4b3a73a01be03aaf9cb, originally reviewed at live base 1977ef0d6ec1a65d02947a0b7dae2675c2e8228c, rebound after explicit manifest-blob invalidation to clean live configurator c3f3438172c8de977d390c9a2fb2c1037262e2a9 on curation/portfolio-20260901-successor-reauthorization. Root and bounded specialists verified GP-VAL-010 ancestry and exact path/blob correspondence, the one-field GP-VAL-013 manifest source-dependency delta, unchanged category/applicability tuples, and the still-reproducing zero-result PASS.",
      "automated_validation": [
        "Historical-only, excluded-only, unknown, duplicate, and mixed requests containing any zero-result category fail accurately.",
        "Every requested nonempty current category executes its exact entries, and unfiltered aggregate still runs every current load-bearing check.",
        "The runtime-config validation manifest remains exact blob 82380ccb0205835254a52f3b3edddeedc7ae3124 after implementation; no manifest field, category, applicability, or source dependency changes.",
        "Focused aggregate adversarial, manifest, census, health, full aggregate, framework, sequence, navigation, surface, py_compile, and diff checks pass with independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 aggregate selection validation only.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused repair if valid current category execution regresses; never restore PASS for an explicit empty selection.",
      "status_documentation_updates": "Activate mechanically only after GP-VAL-010 integration and record Done after reviewed publication; preserve all applicability and runtime non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "6d3c2812a45d4d59caab9699cdcd080bf1d7571f",
        "reviewed_implementation_sha": "c91dad6ac3a4a8629e93179d152b882b862a7fd9",
        "prior_canonical_integration_sha": "c91dad6ac3a4a8629e93179d152b882b862a7fd9",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_runtime_config_validation_aggregate.py",
          "tools/run_glyph_runtime_config_validation.py"
        ],
        "independent_review_provenance": "Fresh independent Validator Reviewer PASS on exact reviewed snapshot c91dad6ac3a4a8629e93179d152b882b862a7fd9; focused, manifest, census, health, full aggregate, framework, sequence, navigation, agent-surface, py_compile, and diff gates passed.",
        "validation_provenance": "Exact integrated snapshot c91dad6ac3a4a8629e93179d152b882b862a7fd9 passed all authorized GP-VAL-012 checks; no build, artifact, device, or hardware action was required."
      },
      "stop_conditions": [
        "The activation dependency is absent, drifted, or requires interpretation.",
        "Any historical/unsafe checker is promoted or executed.",
        "Any runtime-config validation manifest byte or field changes.",
        "Any manifest classification, workflow, build, product/runtime, artifact, device, or hardware behavior changes."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-006",
      "title": "Isolate candidate-preparation safety validation",
      "status": "DONE",
      "branch": "glyph/gp-val-006-isolated-candidate-safety-20260831",
      "objective": "Make candidate-preparation branch, target, scope, dirty-tree, and dry-run refusal behavior current and load-bearing without allowing any checker subprocess to mutate or depend on the canonical worktree.",
      "why_this_matters": "The existing candidate-generation checker is excluded as unsafe and currently fails on configurator because it asks the tool to record a synthetic candidate branch while every subprocess still runs in the real repository. The real configurator branch guard therefore preempts the intended active-table-source refusal, and the write-capable tool does not require the requested candidate branch to equal the checked-out branch on non-configurator worktrees.",
      "hardware_risk": "H1",
      "behavioral_claim": "This work strengthens host-side candidate-preparation refusal and validation behavior only. It adds checked-out/requested branch correspondence, confines checker subprocesses and any attempted materialization to copied standalone temporary Git repositories, and makes that safety checker load-bearing. It changes no generated semantic content, active source, active table bytes, firmware/runtime behavior, workflow, artifact, device, or controller behavior.",
      "scope": "Update tools/prepare_source_owned_candidate_branch.py so --write-source fails before generation or mutation unless the checked-out branch exactly equals --candidate-branch and both remain non-configurator. Update tools/check_glyph_source_owned_candidate_generation.py so every tested tool subprocess executes with cwd inside a fresh standalone temporary Git repository copied only from the current tracked stage-0 bytes, initialized with controlled identity and the exact test branch; no subprocess may use canonical REPO_ROOT as its Git or write context. Independently exercise dry-run success, direct-configurator refusal, requested/current branch mismatch, active-table target refusal, unrelated target refusal, dirty-tree refusal, and safe-generation/source-authority refusal before write, and verify canonical repository HEAD, index, tracked bytes, status, and untracked set are unchanged before/after. Reclassify the existing candidate_generation manifest entry in place as current, content_only, temporary_repository_only, load-bearing, with exact direct source dependency tools/prepare_source_owned_candidate_branch.py; keep manifest schema/version and entry count unchanged and regenerate only deterministic checker-census and validation-health consequences.",
      "explicit_excluded_scope": "No successful materialization in the canonical worktree; no new output root, repository install target, generator mode, table ownership, profile intent, coordinate, table byte, active source, RuntimeConfigView path, workflow, build, candidate artifact, publication, merge, hardware action/result, runtime-loaded config, persistence, WebSerial/device write, protobuf write, flashing automation, Nunchuk claim, root-cause claim, or game-semantic claim. No tools/glyph_checker_context.py or product/runtime checker change.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator 0e180e9671b78f8ed3c2a5c9220a4fcafbfae598. tools/check_glyph_source_owned_candidate_generation.py blob 8fde4b1cabf4e36c7f9eb07d5f311476197bb78a (SHA-256 fe15aaa4f26bc1068b9a1530aff9b73f6c00d39bcdc992a8b15b282dbb21468b) fails with 'active table-source refusal must identify active compile-time content' while leaving the canonical worktree clean. It invokes tools/prepare_source_owned_candidate_branch.py from canonical REPO_ROOT for every case. That tool's current blob 84b4d943e73c32d4fe3f956240ba9f63c6c5a4b1 (SHA-256 b12cb3b574a75390c840e760209964b4832578c057f598b691942ec5191af58e) rejects requested and checked-out configurator identities separately but does not require their equality, then writes at its materialization seam after the existing target and production-generation guards. The workflow fixture blob cf4fb1671ab12c86c2ce746eafad18d6902f0530 and manifest-v4 blob 97836fba92e6faf6567351bba360dd77f7fd65d8 retain the exact Planner gap. GP-VAL-003 and GP-VAL-007 are now Done; current validation has 32 manifest entries and 27 current load-bearing checks before this activation.",
      "dependencies_prerequisites": [
        "GP-VAL-003 and GP-VAL-007 remain canonically DONE, with generic validation-health prose correspondence and manifest-v4 bounded dependency metadata intact.",
        "Implementation starts from a fresh live-configurator descendant of 0e180e9671b78f8ed3c2a5c9220a4fcafbfae598 and first reproduces the exact candidate-generation checker failure with a clean before/after canonical status.",
        "The candidate-preparation tool, workflow fixture, active/inert target identities, source-owned generation policy, manifest schema v4, and current 32-entry/27-load-bearing validation state remain materially unchanged.",
        "Every test subprocess and attempted write uses a fresh standalone temporary Git repository; the canonical worktree is observation-only throughout validation."
      ],
      "substantive_authorization_rationale": "The gap and its safety consequence are directly source-proven, GP-VAL-003's recorded wait is satisfied, and the architecture is resolved without product judgment. Exact checked-out/requested branch equality closes the real write-authorization ambiguity. Fresh copied standalone temporary Git repositories make branch, index, dirtiness, target, and source-authority refusal cases deterministic while preventing the current aggregate from depending on or writing the canonical worktree. Reclassifying the existing manifest row in place makes the repaired safety lane load-bearing without changing manifest shape, product semantics, or runtime authority.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The candidate-preparation tool, workflow fixture, active/inert target identity, generator/source-authority policy, manifest schema, or current checker architecture changes materially before implementation.",
        "Another canonical change supplies equivalent or stronger checked-out/requested branch correspondence plus standalone-temporary-repository load-bearing coverage first.",
        "The checker cannot execute every tool subprocess outside canonical REPO_ROOT or cannot prove canonical HEAD, index, tracked bytes, status, and untracked set unchanged.",
        "The implementation would require successful canonical materialization, a new write/output decision, tools/glyph_checker_context.py, product/runtime code, workflow, build, artifact, or hardware scope."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of Planner candidate GP-VAL-006 from planning/portfolio-20260827-1210 commit ae1d15b9a7941934b26d4371b0ea0e10691629cb, packet base 8c04262c66613d46b933b1b739c01c575cb0c580, after GP-VAL-003 and GP-VAL-007 completion. Root and bounded verification specialists independently reproduced the current failure, inspected the write/branch seams, and confirmed the other three survivors remain gated against live configurator 0e180e9671b78f8ed3c2a5c9220a4fcafbfae598 on curation/portfolio-20260831-gp-val-006-review.",
      "automated_validation": [
        "The focused checker runs every candidate-preparation subprocess in a fresh controlled standalone temporary Git repository and passes while the canonical repository's HEAD, index, tracked bytes, status, and untracked set remain exactly unchanged.",
        "Correct non-configurator branch correspondence permits the authorized dry-run path; requested/current branch mismatch and either requested or current configurator identity fail before generation or mutation for their exact reasons.",
        "Active table target, unrelated target, dirty tree, unsafe generation/source authority, and forbidden runtime/device claims fail independently without being preempted by unrelated branch context; rejected cases leave no target or partial write.",
        "The existing fixture policy, allowed inert target, dry-run plan fields, validation command list, forbidden claims, and generated semantic output remain unchanged; no successful materialization is required or performed in the canonical worktree.",
        "Manifest v4 retains 32 entries, reclassifies only candidate_generation to current/content_only/temporary_repository_only/load-bearing with exact direct tool dependency, and raises the current load-bearing count from 27 to 28 without changing another entry's applicability or policy.",
        "Candidate-generation, manifest aggregate adversarial, checker census, validation health, full runtime-config aggregate, agent-framework, sequence, navigation, docs-agent-surface, py_compile, and exact diff checks pass; independent review confirms no write authority, source authority, runtime, publication, or hardware invariant weakened."
      ],
      "canonical_build": "NOT_REQUIRED: H1 host-side branch/write refusal, isolated temporary-repository checker coverage, and validation metadata only; any compiled source, generated semantics, build input, workflow, or runtime delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused host-tool/checker/metadata branch if valid dry-run coverage regresses or canonical non-mutation cannot be proved; keep candidate_generation excluded rather than making an unsafe or context-dependent checker load-bearing.",
      "status_documentation_updates": "Record GP-VAL-006 as Done after exact reviewed integration; retain the remaining evidence/user gates and zero effective runway without creating a product, candidate, artifact, or hardware claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "f8610327da8283c914c0e9b478276e67aea0f4bb",
        "reviewed_implementation_sha": "9d1f6cf3ac064d5df7c63fe0d90a0fae8eca48db",
        "prior_canonical_integration_sha": "f72bff6fd752f6b3643557743058b3a40888c8d8",
        "reviewed_changed_paths": [
          "docs/agent_framework/SUBAGENT_CONTRACTS.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_source_owned_candidate_generation.py",
          "tools/prepare_source_owned_candidate_branch.py"
        ],
        "independent_review_provenance": "Fresh independent reviewer PASS after exact-byte isolation repair; focused, full aggregate, census, health, framework, navigation, agent-surface, syntax, and diff gates passed.",
        "validation_provenance": "Exact feature snapshot 9d1f6cf3ac064d5df7c63fe0d90a0fae8eca48db validated before direct-ancestry integration f72bff6fd752f6b3643557743058b3a40888c8d8."
      },
      "stop_conditions": [
        "Any checker subprocess or attempted write uses the canonical repository as its Git or write context.",
        "Any requested/current branch mismatch, active target, unrelated target, dirty tree, or unsafe source-authority case can reach mutation or pass for the wrong reason.",
        "Any additional manifest entry, other applicability/policy reclassification, successful canonical materialization, write target, generator semantic, product/runtime source, workflow, build, artifact, publication, device, or hardware scope appears.",
        "Any runtime-loaded config, persistence, WebSerial/device write, protobuf write, flashing, Nunchuk, root-cause, or game-semantic claim is introduced."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-003",
      "title": "Inventory declared build-input provenance",
      "status": "DONE",
      "branch": "glyph/gp-prov-003-build-input-provenance-inventory-20260826",
      "objective": "Create one deterministic static inventory of the defined canonical Glyph toolchain, dependency, workflow, source-selection, source-identity, and postprocessor provenance boundary without resolving, changing, installing, or executing any dependency.",
      "why_this_matters": "Current canonical checks prove workflow publication routing and observed source/postprocessor/artifact correspondence, but no load-bearing record covers the selectors that choose the runner, workflow actions, Python line, PlatformIO tool, platform/framework packages, libraries, source tree, local build scripts, nested reusable-workflow caller, or tracked postprocessor. Exact-build and reproducibility claims therefore remain unsupported and selector drift can occur without one complete provenance boundary.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work adds static provenance documentation, a machine-readable inventory, and a read-only checker only. It does not fetch or install dependencies, change selectors or pins, build or postprocess firmware, claim resolved dependency contents or reproducibility, publish an artifact, access a device, or change firmware/configurator product behavior.",
      "scope": "Add docs/runtime_config/build_input_provenance_inventory.md, docs/runtime_config/fixtures/build_input_provenance_inventory.json, and tools/check_glyph_build_input_provenance_inventory.py. The schema has exact top-level fields schema_name, schema_version, status, canonical_environment, declaration_files, selectors, source_identity, postprocessor_identity, and unresolved_claims; schema_name is glyph_build_input_provenance_inventory, schema_version is integer 1, status is declared_input_inventory_only_no_resolution_or_reproducibility, and canonical_environment is glyph_mk6. Discover declaration files with git ls-files across platformio.ini, config/*/env.ini, config/*/meta.yaml, every tracked **/.github/workflows/*.yml or *.yaml caller/reusable workflow, every local extra_scripts or custom_nanopb_options options-file path reached by glyph_mk6 inheritance, and glyph_nuker. declaration_files entries have exact fields path, git_mode, and sha256; ordinary text declarations and scripts are tracked 100644 regular blobs, while glyph_nuker is the separately classified tracked 100755 postprocessor blob. Record every relevant default_envs, src_dir, extra_configs, board, board_build.core, platform, framework, platform_packages, lib_deps, lib_ignore, extra_scripts, build_src_filter, custom_nanopb_protos, custom_nanopb_options --options-file path, runs-on, uses, python-version, pip-install, reusable-workflow ref, and external repo/revision expression reached by the canonical environment or either tracked build workflow. Non-path semantic custom_nanopb_options flags such as --error-on-unmatched are outside this provenance-selector inventory. Selector entries have exact fields id, category, declaring_path, declaration_context, raw_selector, selector_class, and resolution_state. selector_class is one of FULL_GIT_COMMIT, ABBREVIATED_GIT_COMMIT, TAG, COMPATIBLE_VERSION_RANGE, EXACT_VERSION, VERSION_LINE, UNVERSIONED, MOVING_REF, RUNTIME_EXPRESSION, SYMBOLIC_FRAMEWORK, LOCAL_CONFIGURATION_SYMBOL, LOCAL_TRACKED_FILE, LOCAL_SOURCE_SELECTION, or TRACKED_FILE_IDENTITY. Full Git commit means exactly 40 lowercase hexadecimal characters; shorter hexadecimal refs remain ABBREVIATED_GIT_COMMIT. resolution_state is one of STATIC_TRACKED_BYTES, DECLARED_EXACT_NOT_FETCHED, DECLARED_MOVABLE_NOT_RESOLVED, RUNTIME_RESOLVED_ONLY, or UNRESOLVED_EXTERNAL. Map local tracked files and tracked-file identities only to STATIC_TRACKED_BYTES; local configuration symbols such as glyph_mk6, pico, and earlephilhower, local source/glob selections, custom nanopb dependency/options-file paths, workflow expressions, and build-time source SHA to RUNTIME_RESOLVED_ONLY; full commits and exact registry versions to DECLARED_EXACT_NOT_FETCHED; tags, ranges, version lines, unversioned packages, moving refs/runners, and symbolic frameworks to DECLARED_MOVABLE_NOT_RESOLVED; and unresolved external ownership/invocation facts to UNRESOLVED_EXTERNAL. source_identity has exact fields mechanism, required_value_shape, resolution_state, and claim: mechanism is git rev-parse HEAD, required_value_shape is full_lowercase_40_hex, resolution_state is RUNTIME_RESOLVED_ONLY, and claim is exact_source_snapshot_only_not_dependency_closure_or_reproducibility. postprocessor_identity has exact fields path, git_mode, sha256, purpose, byte_transformation, and resolution_state; it binds glyph_nuker mode 100755 and SHA-256 8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae with purpose and byte_transformation UNKNOWN and resolution_state STATIC_TRACKED_BYTES. unresolved_claims is the exact sorted list artifact_acceptance, build_device_config_live_caller_and_ownership, complete_dependency_resolution, immutable_artifact_locator, package_and_action_content_identity, postprocessor_byte_transformation, postprocessor_purpose, reproducible_build, runner_image_identity, and toolchain_resolution. Classify config/glyph/.github/workflows/build.yml@configurator, ubuntu-latest, major action refs, tags, compatible ranges, abbreviated commits, unversioned packages, pip --upgrade selectors, workflow expressions, and the unresolved live use/ownership of build-device-config accurately rather than promoting them to immutable identities. Make the checker a current load-bearing baseline entry in the curated runtime-config validation manifest and regenerate only deterministic census/health consequences.",
      "explicit_excluded_scope": "No network or package-registry resolution; no inspection or trust promotion of local .pio caches; no dependency, action, runner, workflow, platform, library, Python, pip, source, postprocessor, or config pin change; no lockfile design and no complete semantic build-configuration or compiler-flag census. build_flags values, macro meanings, optimization flags, non-path custom_nanopb_options flags, board behavior, and include-path semantics are outside this provenance-selector inventory except that the tracked declaration files and full source snapshot identity remain recorded. No build, glyph_nuker execution, pre/post artifact comparison, sidecar redesign, upload, release, store or retention choice, immutable locator, artifact acceptance, reproducibility or byte-equivalence claim, workflow-owner/caller decision, firmware/runtime source, device/protobuf write, persistence, flashing, hardware result, Nunchuk claim, root-cause claim, or game-semantic claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Fresh live verification pins configurator at 091834bbb35f785cb67212110339af31a8b64e08. Planner packet glyph-portfolio-20260824-2349 at ffba28772d8559df4b356de9b3a3f02248d16c07 proposed GP-PROV-003 as the surviving static provenance candidate. Independent current-source inspection finds no complete provenance inventory spanning PlatformIO selectors, workflow refs/runners/actions, nested callers, source selection, source identity, and the postprocessor; existing workflow checkers bind only selected publication and sidecar-ordering tokens. The declaration-byte SHA-256 values are platformio.ini 99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9, config/glyph/env.ini c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf, config/glyph/meta.yaml 22e3d23a7b596aa99da26fe86cc83e9e24d57b40200f702b9289e94cef2d8655, .github/workflows/build.yml b2da4ecddd42443fa0d19c56b55dfd2df0ee91bd513258983f0887f2ff7ef638, .github/workflows/build-device-config.yml abf612c3f27e9884ad600b1c1b3cd1a864fae45c22c24aa7b2508c8ad98df5a5, config/glyph/.github/workflows/build.yml 85e134a6b98e377db510c468e50a41446c4b62ec486728e1da880f04e531c4a7, builder_scripts/arduino_pico.py 456a4b7d5582bbeb0244868db28920cd0f276d3db1924b36b401047cdf4569c2, and glyph_nuker 8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae. config/glyph/.github/workflows/build.yml invokes GregTurbo/HayBox-Glyph/.github/workflows/build-device-config.yml@configurator, a moving branch ref outside the current top-level publication-route census; this is static caller text, not proof of live invocation or ownership. Existing canonical authority explicitly leaves build-device-config live use/ownership, postprocessor purpose/effect, dependency closure, artifact acceptance, immutable storage, and reproducibility unresolved.",
      "dependencies_prerequisites": [
        "Implementation starts from a fresh live configurator descendant of 091834bbb35f785cb67212110339af31a8b64e08 containing this queue/status publication and first verifies every recorded declaration-file byte hash and the absence of an equivalent complete inventory.",
        "GP-PROV-002 and GP-VAL-002 remain Done, and the prior GP-VAL-003 route census remains canonical while its health-prose correspondence identity is separately reopened; their observed-only sidecar, validation-before-publication, and UNRESOLVED_EXTERNAL build-device-config classifications are preserved exactly.",
        "The implementation uses Python standard-library parsing and Git static discovery only; it must not import workflow code, execute discovered scripts or binaries, inspect dependency caches, or access the network."
      ],
      "substantive_authorization_rationale": "The missing inventory is directly source-proven and the architecture is now closed: complete tracked declaration-file discovery, exact selector records, a finite classification/state vocabulary, exact tracked-byte identities, and explicit unresolved claims. The work records declared provenance rather than attempting resolution or remediation, so it requires no choice of package versions, workflow ownership, artifact store, product behavior, or game semantics. Adding the checker as a current validation prerequisite makes selector drift visible without asserting that current movable selectors are safe or reproducible.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any recorded declaration file, selector, postprocessor byte, canonical build environment, workflow/caller topology, or existing provenance/publication contract changes before implementation.",
        "Another canonical change supplies an equivalent or stronger complete static inventory and fail-closed discovery checker.",
        "Implementation would need network resolution, a new dependency parser package, cache inspection, selector remediation, a pin/lock decision, workflow ownership interpretation, or any claim beyond declared static provenance.",
        "The checker cannot cover the nested config/glyph reusable-workflow caller and every canonical glyph_mk6 inherited selector without executing build tooling or weakening completeness."
      ],
      "authorization_snapshot_provenance": "Curator follow-up review of Planner branch planning/portfolio-20260824-2349, candidate GP-PROV-003, packet commit ffba28772d8559df4b356de9b3a3f02248d16c07, packet base caf37e10673896b3bf5e2815875a93310b3f3ac1, independently rebound to the completed GP-PROV-002/GP-CTL-002 state and live configurator 091834bbb35f785cb67212110339af31a8b64e08 on curation/portfolio-20260826-2350-review.",
      "automated_validation": [
        "The positive inventory contains every tracked top-level and nested workflow declaration; every in-scope glyph_mk6 PlatformIO/environment toolchain, dependency, source-directory/filter, nanopb proto/options, and local-script selector; the dynamic full source identity mechanism; and the exact tracked postprocessor identity with no duplicate IDs or declaration omissions.",
        "Added, removed, renamed, mode-changed, or byte-changed declaration files and added, removed, reordered, or changed selectors fail until the reviewed manifest is updated; unrelated source/docs changes do not fabricate selector drift.",
        "Adversarial fixtures classify 40-hex Git commits separately from abbreviated commits, tags, compatible ranges, exact versions, version lines, bare packages, moving branches/runners, workflow expressions, symbolic frameworks, local configuration symbols, source selections, and tracked files; booleans, malformed records, unknown keys/classes/states, duplicate IDs, escaping paths, symlinks, unexpected executable declaration text, wrong glyph_nuker mode, and untracked paths fail closed.",
        "The current config/glyph nested caller remains MOVING_REF, build-device-config remains UNRESOLVED_EXTERNAL, postprocessor purpose/effect remain UNKNOWN, and the manifest cannot claim complete resolution, reproducibility, artifact acceptance, immutable storage, or hardware evidence.",
        "Tests prove the checker performs no network access, dependency installation, PlatformIO invocation, workflow/script import, glyph_nuker execution, build, artifact read, upload, release, or device action.",
        "The focused provenance checker, publication-route census, artifact-postprocessor provenance/workflow checks, checker census, validation health, full runtime-config aggregate, agent framework, sequence, docs navigation, and agent surface all pass; independent review confirms no selector, workflow, product/runtime, evidence, or authority invariant changed or weakened."
      ],
      "canonical_build": "NOT_REQUIRED: static docs, fixture, read-only checker, and deterministic validation metadata only; any selector, workflow, dependency, compiled source, build input, or product/runtime delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused inventory/checker branch if completeness or classification cannot be enforced without resolution or remediation; retain every existing selector and provenance non-claim rather than inventing resolved identities.",
      "status_documentation_updates": "Document GP-PROV-003 as a declared-input inventory only, add its current validation classification, and retain explicit UNKNOWN/unresolved statements for dependency contents, moving refs, build-device-config ownership/caller, postprocessor semantics, reproducibility, immutable storage, artifact acceptance, and hardware.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "ea5ae10022bc9face69644c5ae9f7ad322940658",
        "reviewed_implementation_sha": "2d468884e5fa812d33886e2520b8251d9ca970be",
        "prior_canonical_integration_sha": "a747dd54b02b207483142331d8b5be1113fc951e",
        "reviewed_changed_paths": [
          "docs/runtime_config/README.md",
          "docs/runtime_config/build_input_provenance_inventory.md",
          "docs/runtime_config/fixtures/build_input_provenance_inventory.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_build_input_provenance_inventory.py"
        ],
        "independent_review_provenance": "Independent validator/reviewer PASS on exact feature tip 2d468884e5fa812d33886e2520b8251d9ca970be after adversarial declaration-discovery, selector-classification, workflow-scope, AST static-safety, census, health, and aggregate repairs.",
        "validation_provenance": "Focused checker PASS with 8 declaration files, 69 selectors, 16 positive cases, 14 negative cases, no network/build/postprocessor execution, plus publication-workflow, postprocessor, census, health, aggregate, framework, sequence, navigation, surface, and diff checks."
      },
      "stop_conditions": [
        "Any selector or tracked build-input byte would change rather than only be inventoried.",
        "Any remote content, package resolution, cache state, action implementation, runner image, dependency closure, postprocessor behavior, artifact equivalence, reproducibility, or external ownership fact would be inferred or promoted without evidence.",
        "Any build, workflow execution, postprocessor execution, artifact publication, device write, flashing, hardware result, runtime-loaded configuration, persistence, Nunchuk, root-cause, or game-semantic scope appears.",
        "Any new load-bearing checker can pass with missing nested workflows, unclassified selectors, stale declaration hashes, or weakened validation applicability."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-004",
      "title": "Record timestamped upstream observations for canonical build-input selectors",
      "status": "DONE",
      "branch": "glyph/gp-prov-004-observation-correspondence-repair-20260829",
      "objective": "Repair and revalidate the GP-PROV-004 observational record so every selector, derived expression, source class, lookup method, locator, immutable identity, base commit, and declared dependency corresponds exactly to current tracked source or remains explicitly unresolved.",
      "why_this_matters": "The accepted checker currently invents two derived workflow expressions, permits heterogeneous records to cite an unrelated registry, accepts arbitrary full-hex identities without proving correspondence to the selector or evidence, treats the base SHA as shape-only, ignores record order, and omits tracked workflow/meta dependencies. The completed objective is therefore not truthfully source-bound.",
      "hardware_risk": "H0",
      "behavioral_claim": "This adds observational provenance docs, a fixture, and an offline checker only. It does not install dependencies, alter selectors or pins, build firmware, execute workflows or glyph_nuker, publish or accept an artifact, access a device, or change runtime/configurator behavior.",
      "scope": "Update docs/runtime_config/build_input_resolution_observations.md, docs/runtime_config/fixtures/build_input_resolution_observations.json, tools/check_glyph_build_input_resolution_observations.py, the existing manifest entry's exact direct source_dependencies, and only mechanically consequent census/health artifacts. Derive the eligible 42 direct records plus workflow.device.external_repo and workflow.device.external_revision from the bound GP-PROV-003 inventory in exact inventory order; never hard-code substitute expressions. Pin source_inventory.base_configurator_sha to 8c04262c66613d46b933b1b739c01c575cb0c580 and require at that commit inventory blob 5e6d2f128cc6baccd98c39369fbd6bc5acc43851, workflow blob 40f8ca91fefc64674c08c03183595983c5054d1f, and meta blob b875b765da097f247823d9550b9d417b0f657656. The exact record policy is: pio.arduino_pico.platform alone may be OBSERVED_FULL_IDENTITY with method git_ls_remote_commit, immutable commit locator https://github.com/maxgerhardt/platform-raspberrypi/commit/5e87ae34ca025274df25b3303e9e9cb6c120123c, and observed identity exactly 5e87ae34ca025274df25b3303e9e9cb6c120123c after permitted live verification; workflow.device.external_repo and workflow.device.external_revision are RUNTIME_DERIVED with method static_tracked_expression_inspection, null identity, and an immutable 8c04262 commit-blob locator for .github/workflows/build-device-config.yml; workflow.nested.reusable_caller is VISIBLE_SOURCE_WITHOUT_INVOCATION only when a permitted lookup records a full upstream commit and immutable commit-tree workflow locator, otherwise BOUNDED_UNRESOLVED; every remaining record is BOUNDED_UNRESOLVED with method tracked_declaration_only, null identity, and the immutable 8c04262 commit-blob locator for its declaring file. No other method/result/identity/locator combination is permitted. Manifest source_dependencies is exactly [docs/runtime_config/fixtures/build_input_provenance_inventory.json, .github/workflows/build-device-config.yml, config/glyph/meta.yaml] and makes no transitive or semantic closure claim.",
      "explicit_excluded_scope": "No new external fact inferred from URL, registry, or 40-hex shape; no package installation, lockfile, cache authority, selector/pin/remediation change, workflow or build-input mutation, compiler/configuration census, build, postprocessor execution, artifact generation/upload/acceptance/storage, reproducibility or byte-equivalence claim, caller/secret/permission inference, firmware/runtime source, device write, protobuf write, persistence, flashing, hardware result, Nunchuk claim, root-cause claim, or gameplay-semantic claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator 8c04262c66613d46b933b1b739c01c575cb0c580. .github/workflows/build-device-config.yml derives HAYBOX_REPO and HAYBOX_REVISION from fromJson(needs.metadata.outputs.meta_json).repo and .revision, while tools/check_glyph_build_input_resolution_observations.py hard-codes ${ inputs.repo } and ${ inputs.revision } equivalents. The repaired checker binds source class, lookup, identity correspondence, exact base/blob closure, record order, and direct manifest dependencies to the reviewed source inventory while retaining unresolved external claims explicitly. Canonical GP-PROV-003 inventory identity remains the declared selector source.",
      "dependencies_prerequisites": [
        "GP-PROV-003 remains canonically DONE and its inventory bytes, eight declaration-file identities, selector set, and declared-only non-claims remain unchanged.",
        "Implementation starts from a fresh live configurator descendant of 8c04262c66613d46b933b1b739c01c575cb0c580 and rechecks inventory blob 5e6d2f128cc6baccd98c39369fbd6bc5acc43851, workflow blob 40f8ca91fefc64674c08c03183595983c5054d1f, and meta blob b875b765da097f247823d9550b9d417b0f657656 at that exact base before editing.",
        "Any live fact retained as authoritative evidence has a reproducible authoritative locator or immutable checked-in correspondence; otherwise it is downgraded to an explicit bounded unresolved observation.",
        "Only read-only upstream lookup mechanisms are used; tests and the final checker remain offline and execute no discovered workflow or build input."
      ],
      "substantive_authorization_rationale": "The defects are directly source-proven and the repair architecture is fully bound by the exact per-record method/result/locator policy, one allowed immutable resolved identity, mechanical reusable-workflow found/not-found rule, explicit unresolved outcome for every other selector, exact base/blob set, inventory order, and three-file direct manifest dependency list. This revalidates the already-authorized observational objective without leaving evidence classification to the implementer or choosing pins, owners, packages, stores, product behavior, or game semantics.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any declaration byte, inventory selector, source-inventory identity, workflow/meta expression, eligible-selector rule, or relevant provenance contract drifts before implementation.",
        "The repair needs a new external fact that cannot be retained as explicitly unresolved, or requires installing/resolving dependencies, changing selectors or pins, inferring workflow ownership/permissions, or asserting reproducibility.",
        "The checker cannot prove asserted immutable identities and exact base/source correspondence from checked-in or reproducibly authoritative evidence without network access at validation time.",
        "A network-capable observation route is wholly unavailable after every permitted retry; do not publish an all-unreachable packet as meaningful completion."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of repair candidate GP-PROV-004 in planning/portfolio-20260827-1210 commit ae1d15b9a7941934b26d4371b0ea0e10691629cb, packet base and live configurator 8c04262c66613d46b933b1b739c01c575cb0c580, with direct current-source/checker/fixture reproduction on curation/portfolio-20260827-1232-review on 2026-08-27.",
      "automated_validation": [
        "The fixture has exact schema and deterministic order with one record for every required direct selector plus exact workflow-derived repo/revision expressions, with no duplicates or omissions.",
        "Every record exactly binds selector ID, raw selector, source class, source inventory identity, observation time, and the one authorized per-record method/result/mutability/locator/identity combination; no unenumerated combination passes.",
        "Any OBSERVED_FULL_IDENTITY requires a full lowercase commit that exactly corresponds to the selector/ref and immutable evidence; tags, branches, runners, version lines, unresolved routes, and syntactic 40-hex substitutes cannot be promoted.",
        "The base configurator commit must exist in the accepted canonical ancestry and bind the exact tracked inventory/workflow/meta blobs on which the packet directly depends; manifest source_dependencies list only those exact direct files and do not claim transitive or semantic closure.",
        "Adversarial fixtures reject the current invented expressions, wrong locator/source class, wrong lookup family, arbitrary or abbreviated identity, wrong base/blob, missing dependency, order drift, omitted selector, stale inventory, duplicate record, unknown field/status, malformed timestamp/URL, and contradictory nullability.",
        "The checker performs no network access, installation, workflow execution, build, postprocessing, upload, artifact read, or device access.",
        "Focused checker, GP-PROV-003 checker, workflow and publication provenance checks, census, validation health, full current aggregate in correct branch context, framework, sequence, navigation, surface, and git diff checks pass; independent review confirms no fact was promoted by inference."
      ],
      "canonical_build": "NOT_REQUIRED: H0 observational docs, fixture, and offline checker only; any build-input or product/runtime delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the focused repair if exact source correspondence cannot be enforced without new external authority; retain the prior packet as historical incomplete evidence and preserve GP-PROV-003 declarations and every unresolved non-claim.",
      "status_documentation_updates": "Record GP-PROV-004 as Done after exact source/identity/base/dependency correspondence repair; publish only directly proved observations and keep all unresolved selector, ownership, reproducibility, artifact, and hardware claims explicit.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "933dd3c93bdce798218e863ac50a5573325a10ef",
        "reviewed_implementation_sha": "ffc007552abc848051841362b0b0ac4c1a7d087b",
        "prior_canonical_integration_sha": "18f451024d8f822cafbf450a80272c2b729c5e7b",
        "reviewed_changed_paths": [
          "docs/runtime_config/build_input_resolution_observations.md",
          "docs/runtime_config/fixtures/build_input_resolution_observations.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "tools/check_glyph_build_input_resolution_observations.py"
        ],
        "independent_review_provenance": "Fresh bounded repaired-scope review passed on the exact feature tip; no selector, source-authority, runtime, product, artifact, hardware, or publication invariant was weakened.",
        "validation_provenance": "Focused correspondence, provenance inventory, publication workflow, checker census, validation health, full runtime-config aggregate, framework, sequence, navigation, surface, and diff gates passed."
      },
      "stop_conditions": [
        "Selector, declaration, workflow/meta expression, or provenance-contract drift.",
        "A required observed identity, source class, locator, or base/blob dependency cannot be represented without inference or trust promotion.",
        "The work needs a pin, version, or workflow-owner decision.",
        "The work would mutate a build input, workflow, product source, artifact, or external account.",
        "All permitted network-capable observation paths fail."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-005",
      "title": "Establish bounded source lineage evidence for glyph_nuker",
      "status": "DONE",
      "branch": "glyph/gp-prov-005-glyph-nuker-source-lineage-20260827",
      "objective": "Search the exact repository history and named authoritative upstream repositories and releases for glyph_nuker source, immutable source commit, documented purpose, and build provenance; record authoritative lineage if found or a bounded searched-not-found result without claiming global absence.",
      "why_this_matters": "The tracked executable participates in the publication route, but canonical evidence establishes only its bytes and invocation. Purpose, byte transformation, source lineage, and build recipe remain UNKNOWN.",
      "hardware_risk": "H0",
      "behavioral_claim": "This is static source-lineage research and deterministic evidence checking only. It does not execute, replace, rebuild, reverse-engineer as authority, or validate glyph_nuker; it does not inspect a real UF2 transformation, build firmware, publish an artifact, access a device, or change runtime/configurator behavior.",
      "scope": "Add docs/runtime_config/glyph_nuker_source_lineage.md, docs/runtime_config/fixtures/glyph_nuker_source_lineage.json, and tools/check_glyph_nuker_source_lineage.py. Bind glyph_nuker Git mode 100755, SHA-256 8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae, blob d0524944a90503a8881281b6673b1f46e36f9383, current workflow invocation, and local history showing binary introduction in squash commit cc57c4fcbcf25c5e33fab21fd5b8312e0543c8dd. Search the live SenatorSSB/glyph-ultimate-expanded-fw history and the source-named GregTurbo/HayBox-Glyph repository's immutable commits, trees, tags, and releases. Each search records exact query or method, time, live locator or ref, outcome, and immutable evidence identity. Result is either AUTHORITATIVE_SOURCE_LINEAGE_FOUND or BOUNDED_SOURCE_LINEAGE_NOT_FOUND. A found result requires exact upstream repository, full source commit, source paths, build-recipe paths, and source-backed purpose or effect references. A not-found result keeps lineage, purpose, effect, and build recipe UNKNOWN and states the bounded search limitations.",
      "explicit_excluded_scope": "No glyph_nuker execution; no real or synthetic UF2 pre or post experiment; no rebuild, binary-equivalence, safety, artifact-acceptance, reproducibility, replacement, workflow, upload, store, release, firmware/runtime, device, persistence, protobuf, flashing, hardware, Nunchuk, root-cause, or gameplay-semantic change or claim. Static strings, file metadata, or disassembly may be observations only and cannot establish source authority; no global proof of source absence.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator a747dd54b02b207483142331d8b5be1113fc951e; canonical binary blob d0524944a90503a8881281b6673b1f46e36f9383, mode 100755, SHA-256 8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae; local path history currently reaches only import commit cc57c4fcbcf25c5e33fab21fd5b8312e0543c8dd. Purpose or effect may become source-backed only through exact authoritative upstream source or docs at immutable identities.",
      "dependencies_prerequisites": [
        "GP-PROV-003 is canonically DONE.",
        "The glyph_nuker blob, mode, workflow invocation, and local path history remain unchanged.",
        "Named upstream sources are checked through permitted read-only network access."
      ],
      "substantive_authorization_rationale": "The unknown lineage is directly source-proven and a bounded evidence search cannot change firmware or product semantics. Both a source-backed positive result and an explicitly bounded not-found result are useful without requiring a product decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "glyph_nuker bytes, mode, workflow invocation, or relevant repository history changes.",
        "The task would execute, rebuild, or replace the binary or inspect a real artifact transformation.",
        "A claimed purpose, byte effect, source, recipe, equivalence, or safety conclusion lacks immutable authoritative evidence.",
        "All permitted network-capable searches fail, preventing a meaningful bounded search."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of planning/portfolio-20260827-0132 commit 174cac2a61b39de543d110fb9319465961501812 against live configurator a747dd54b02b207483142331d8b5be1113fc951e on curation/portfolio-20260827-0148-review on 2026-08-27, including independent path-history and canonical binary/workflow inspection.",
      "automated_validation": [
        "The fixture exactly binds binary mode, SHA-256, Git blob, workflow invocation, import commit, canonical base, and every required search surface.",
        "A positive result requires full immutable upstream commit identities, existing source and build-recipe paths, exact evidence correspondence, and source-backed classification.",
        "A negative result requires complete bounded search records and keeps source lineage, recipe, purpose, and byte transformation UNKNOWN.",
        "Adversarial cases reject fabricated paths, mutable refs presented as immutable, abbreviated SHAs, omitted search surfaces, binary drift, unsupported purpose or effect promotion, and contradictory found or not-found fields.",
        "The checker uses local bytes and checked-in evidence only; it performs no network access or binary or artifact execution.",
        "Focused lineage, build-input provenance, artifact-postprocessor provenance and workflow, census, health, full current aggregate in correct branch context, framework, sequence, navigation, surface, and diff checks pass."
      ],
      "canonical_build": "NOT_REQUIRED: H0 static research, fixture, and checker only; any binary, workflow, build input, product, or runtime delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the focused lineage packet if evidence cannot be bound without inference; leave glyph_nuker, workflow, artifact contracts, and UNKNOWN claims unchanged.",
      "status_documentation_updates": "Link the bounded lineage record from existing artifact and build-input provenance docs. Update current factual status only for claims directly established by immutable source evidence; retain UNKNOWN otherwise.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "d5050847d3f850951b3f47865dc8a91aedea0834",
        "reviewed_implementation_sha": "2982e4aef11b5da01b65fac706cb81d7068835bf",
        "prior_canonical_integration_sha": "def48ddd72a095f4ea150de9eca9164eed6c32e6",
        "reviewed_changed_paths": [
          "docs/runtime_config/README.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/glyph_nuker_source_lineage.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/glyph_nuker_source_lineage.md",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_nuker_source_lineage.py"
        ],
        "independent_review_provenance": "Fresh repaired-scope review PASS on exact feature tip 2982e4aef11b5da01b65fac706cb81d7068835bf; authorized lineage scope, bounded not-found claims, checker safety, manifest/census consequences, and forbidden-path invariants were preserved.",
        "validation_provenance": "Focused lineage, build-input provenance, postprocessor/workflow, 193-entry census, validation health, full current aggregate, framework, sequence, navigation, surface, diff, and compile checks passed; no binary execution, build, artifact, or device action was performed."
      },
      "stop_conditions": [
        "Binary, workflow, or history drift.",
        "Execution, rebuilding, replacement, or real artifact analysis becomes necessary.",
        "Authoritative lineage cannot be distinguished from inference.",
        "A product, safety, artifact-acceptance, or workflow-remediation decision is required.",
        "All permitted network-capable source searches fail."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CTL-002",
      "title": "Prove canonical Done integration correspondence",
      "status": "DONE",
      "branch": "glyph/gp-ctl-002-done-integration-correspondence-20260824",
      "objective": "Prevent canonical work orders from becoming Done unless immutable Git evidence proves that the reviewed authorized implementation, or one exact reviewed replay, is already integrated in the canonical history before the completion publication.",
      "why_this_matters": "GP-SRC-003 was twice published Done while its repaired implementation tree was absent, and GP-PROV-002 has now repeated the same failure: publication commit dfc92adf2910532e24f429f61ea3c1fe7026425a marked it Done on the strength of live feature ref 9c94b5449b8065cb02aa0689ca0564720238b80c, while live configurator caf37e10673896b3bf5e2815875a93310b3f3ac1 does not contain that implementation tree. The current framework checker validates only nonempty prose done_evidence and therefore certifies a false canonical state.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work strengthens agent-framework completion publication and synthetic Git correspondence checks only. It changes no firmware, configurator product, workflow, build, artifact, runtime, table, device, or controller behavior.",
      "scope": "Add a machine-readable completion-correspondence policy to the canonical queue and enforce it in tools/check_glyph_agent_framework_docs.py. The policy must record an immutable full migration-base configurator SHA and a sorted legacy_done_ids list derived exactly from the queue at that Git object; the checker must resolve the object locally, rederive the list, and reject additions, removals, mutable refs, missing objects, or mismatches. Every item first becoming Done after that base must carry strict structured completion evidence with full implementation base, reviewed implementation, and prior canonical integration SHAs, exact reviewed changed paths, independent review/validation provenance, and one mode: DIRECT_ANCESTRY requires the reviewed implementation SHA to be an ancestor of the prior canonical integration SHA; EXACT_PATH_TREE requires a dedicated single-parent integration commit whose changed path set is exactly the reviewed base-to-tip path set and whose Git modes/blob identities for every added, modified, or deleted path exactly equal the reviewed tip. In both modes the integration SHA must be an ancestor of the completion-publication HEAD, must descend from the implementation base, and must precede the status publication so no commit self-identifies. Add isolated temporary-Git positive and adversarial coverage. Keep GP-CTL-002 non-Done on its implementation branch, integrate the checker/docs first, then publish its own Done evidence on a separate descendant control-plane snapshot.",
      "explicit_excluded_scope": "No retroactive fabrication of integration proof; no semantic or patch-equivalence judgment; no whitespace-normalized patch-id substitute; no mutable branch/tag as evidence; no automatic merge/replay/recovery; no queue promotion outside this work order; no tools/glyph_checker_context.py or other checker; no CI/product/runtime test; no workflow, firmware/runtime source, table content, artifact, hardware, device/protobuf write, persistence, flashing, Nunchuk, root-cause, or game-semantic change or claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Planner candidate GP-CTL-002 on planning/portfolio-20260823-2349 identified two false GP-SRC-003 completion publications and required migration-safe direct-integration or exact-equivalence proof. Fresh live verification now establishes a third case on configurator caf37e10673896b3bf5e2815875a93310b3f3ac1: GP-PROV-002 is canonically Done, but git diff and ancestry show reviewed live feature tip 9c94b5449b8065cb02aa0689ca0564720238b80c is not integrated. docs/WORKFLOW.md requires publication to configurator and exact live verification; tools/check_glyph_agent_framework_docs.py currently validates done_evidence only as a nonempty string. Local immutable Git object identity, ancestry, path sets, file modes, and blob OIDs are sufficient to enforce exact correspondence without inventing product semantics or relying on network state.",
      "dependencies_prerequisites": [
        "GP-PROV-002 remains legitimate IN_PROGRESS recovery work and must be canonically integrated before GP-CTL-002 implementation begins; recovery comes first and its implementation commits must not be absorbed into this governance branch.",
        "Implementation starts from a freshly live-verified configurator descendant of caf37e10673896b3bf5e2815875a93310b3f3ac1 after GP-PROV-002 recovery and derives the immutable legacy Done set mechanically from that exact base.",
        "The ordinary Curator governance-checker surface remains tools/check_glyph_agent_framework_docs.py; docs-navigation changes are permitted only for a real navigation consequence."
      ],
      "substantive_authorization_rationale": "The gap is no longer hypothetical and its architecture is fully bounded. A frozen Git-derived legacy set avoids retroactive evidence invention, while all later transitions must prove immutable canonical integration. Direct ancestry covers ordinary merge/fast-forward integration. Exact dedicated path-tree equality covers reviewed squash/cherry-pick replay without treating branch names, prose, patch-id heuristics, or semantic judgment as proof and without allowing extra changed paths. A separate post-integration completion publication avoids impossible self-referential SHAs. No product, domain, runtime, or source-authority choice remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "GP-PROV-002 recovery changes or replays the reviewed implementation rather than integrating exact tip 9c94b5449b8065cb02aa0689ca0564720238b80c, or its implementation/review authority changes before activation.",
        "Another current canonical change already enforces equivalent or stronger Git-object-backed Done correspondence and migration safety.",
        "The proposed checker would need network access, mutable refs, semantic equivalence judgment, automatic Git mutation, or edits outside the authorized governance surface.",
        "The migration base cannot mechanically derive the exact pre-enforcement Done set without inventing or discarding historical evidence."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-2349, candidate GP-CTL-002, packet commit 387a2a7b27d11b81c3c571aaf07cf543af626757, packet base 6b8ebcd404dcbfe9b579eed41fb35b889e9da598, independently reverified against live configurator caf37e10673896b3bf5e2815875a93310b3f3ac1 after the third false Done publication and authorized on curation/done-integration-correspondence-20260824-1921.",
      "automated_validation": [
        "The current false GP-PROV-002 shape fails before correction because its reviewed feature tip is neither directly integrated nor represented by an exact path-tree replay in configurator.",
        "An isolated synthetic direct merge/fast-forward case passes only when the reviewed implementation is an ancestor of the recorded prior canonical integration and that integration is an ancestor of the completion publication.",
        "An isolated synthetic squash/cherry-pick replay passes only for one dedicated single-parent integration commit with exactly the reviewed changed paths and identical Git modes/blob OIDs, including exact deletion correspondence.",
        "Missing/unresolvable/non-commit objects, abbreviated SHAs, mutable refs, wrong base, sibling feature, partial replay, extra path, changed mode/blob, reordered or changed legacy set, retroactive legacy addition, integration after publication, and prose-only evidence fail.",
        "The migration base is resolved from local Git and mechanically rederives the exact legacy Done IDs from that historical queue; no network or checkout mutation is used.",
        "Agent-framework sequence, navigation, docs-agent-surface, checker-census, validation-health, and full runtime-config aggregate gates pass; independent focused governance review confirms no authority, publication, or recovery invariant weakened."
      ],
      "canonical_build": "NOT_REQUIRED: governance docs, the ordinary agent-framework checker, and isolated synthetic Git fixtures only; any workflow, product/runtime checker, compiled source, or build-input delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused governance implementation if valid direct integration or exact dedicated replay cannot be represented. Never restore prose-only Done publication or classify an unintegrated implementation as legacy evidence.",
      "status_documentation_updates": "Document the migration boundary, structured completion evidence, direct-ancestry and exact-path-tree modes, and required two-stage implementation/integration then completion publication. Preserve Planner/Curator/Implementation separation and all runtime/product non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "2fbda7a674555e23cc6d003f2c0bfa02a97fafc8",
        "reviewed_implementation_sha": "afb3121277d12bbd0aa78555f975840f1c8dbb96",
        "prior_canonical_integration_sha": "60e0cc1f784cc5b4638b0b662cd0e4cb6c2001dd",
        "reviewed_changed_paths": [
          "docs/agent_framework/SUPERVISOR_CONTRACT.md",
          "docs/agent_framework/VALIDATION_AND_GATES.md",
          "docs/agent_framework/WORK_ORDER_TEMPLATE.md",
          "docs/project/ACTIVE_AGENT_QUEUE.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_agent_framework_docs.py"
        ],
        "independent_review_provenance": "Fresh bounded governance review and repaired-scope inspection passed; no authority, publication, or runtime invariant was weakened.",
        "validation_provenance": "Focused framework checker, 190-entry census, full runtime-config aggregate, sequence, navigation, and agent-surface gates passed."
      },
      "stop_conditions": [
        "Any historical Done item would need invented integration evidence or GP-PROV-002 would be grandfathered while still unintegrated.",
        "Any completion can pass with prose, a branch/tag, missing Git object, partial/extra replay, semantic judgment, or a status publication that does not descend from prior canonical integration.",
        "Any queue authorization, implementation recovery, Git merge, workflow, firmware/runtime, product checker, artifact, hardware, device-write, persistence, protobuf-write, flashing, Nunchuk, root-cause, or game-semantic scope is added."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-004",
      "title": "Make generator contract validation temp-root portable",
      "status": "DONE",
      "branch": "glyph/gp-val-004-generator-temp-root-portability-20260824",
      "objective": "Restore load-bearing generated-source contract validation on both aliased and canonical system-temporary-root hosts while preserving the shared isolated-output policy exactly.",
      "why_this_matters": "Live configurator fails its current runtime-config aggregate before unrelated GP-PROV-002 publication: the legacy generator-contract checker requires positive file writes on a host where the accepted shared policy deliberately rejects every aliased-root output, and its canonical-root path still expects an isolated temporary src/generated.hpp target to reject even though that target is neither repository source nor an active-publication-like name.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work corrects host-side checker cases and deterministic checker-census/validation-health artifacts only. It must not change the shared output validator, generator output semantics, accepted or rejected target policy, active source, table bytes, firmware/runtime behavior, workflow behavior, or controller behavior.",
      "scope": "Update tools/check_glyph_generated_source_owned_generator_contract.py so semantic generation, layout-spec equivalence, determinism, fixture equality, and malformed-input cases use non-mutating stdout/in-memory paths when file output is not the subject under test. Exercise file-output policy separately and exactly: when abspath(tempfile.gettempdir()) differs from its resolved spelling, normal outputs under that returned lexical root must fail with the aliased-temporary-root classification and create no target; when the spellings are identical, isolated file outputs under that root must succeed atomically. In the identical-root lane, isolated temporary subdirectories named src are ordinary temporary paths and may succeed; replace the stale broad src/generated.hpp rejection with exact negative cases for repository targets, symlink/case/inode aliases, paths outside the returned root, input overwrite, and active-publication-like names already forbidden by the shared policy. Add deterministic two-environment coverage using isolated subprocess temp-root controls so both aliased and identical root behavior are checked on any supported host. Regenerate only deterministic checker-census and validation-health artifacts required by the checker-byte change.",
      "explicit_excluded_scope": "No edit to tools/source_owned_generator_modes.py, tools/generate_source_owned_runtime_config.py, tools/glyph_checker_context.py, any other product/runtime checker, generator policy, accepted output root, atomic writer, active/inert install exception, workflow, firmware/runtime source, table content, production ownership, profile intent, device/protobuf write, persistence, flashing, hardware result, Nunchuk, root-cause, or game-semantic claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Fresh live verification pins configurator at d1ca9abb6dcfbedb7e33cddd96bc54e7da0a6b5e. On that exact snapshot, default macOS tempfile.gettempdir() is /var/folders/_f/25t1m0794kb7ms1vx8tdwgr00000gp/T and resolves to /private/var/folders/_f/25t1m0794kb7ms1vx8tdwgr00000gp/T; tools/check_glyph_generated_source_owned_generator_contract.py fails when its first positive output reaches the accepted aliased-root rejection. Re-running with the canonical resolved temp root gets past those writes and then fails because the checker expects isolated <temp>/src/generated.hpp to reject. GP-SRC-003's canonical work order and tools/check_glyph_source_owned_generator_modes.py explicitly bind aliased-root rejection and identical-root success, while GP-SRC-005 binds remaining writers to that same policy. The GP-PROV-002 range does not change either implicated generator file.",
      "dependencies_prerequisites": [
        "GP-SRC-003 and GP-SRC-005 are DONE on live configurator; their prepared-v2, shared isolated-output, alias/symlink/input-overwrite, active-publication-name, exact inert-example exception, and atomic-write invariants remain authoritative.",
        "Implementation begins from a fresh descendant of d1ca9abb6dcfbedb7e33cddd96bc54e7da0a6b5e and proves the reproduced default-root and canonical-root failures before editing.",
        "GP-PROV-002 is legitimate unfinished work but does not own this generator checker; its workflow/provenance commits remain isolated until this repair is canonically integrated and the fresh aggregate passes."
      ],
      "substantive_authorization_rationale": "Both failures are directly reproducible contradictions between a stale checker and already-canonical target policy, not unresolved generator or product design. The safe resolution is exact: preserve the shared fail-closed validator and move checker semantic assertions to non-writing execution while testing output policy as its own host-portable matrix. Treating a lexical temporary src subdirectory as repository source would invent a restriction absent from the accepted policy; allowing repository or alias targets would weaken it. No product, profile, ownership, architecture, or game-semantic judgment remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The shared isolated-output policy, exact inert install exception, generator CLI/output semantics, or implicated checker changes materially before implementation.",
        "Another current canonical change restores both host lanes with equivalent or stronger coverage before implementation.",
        "The repair would require changing accepted/rejected output policy, generator semantics, product/runtime code, workflow behavior, or tools/glyph_checker_context.py."
      ],
      "authorization_snapshot_provenance": "Direct user priority GLYPH-UD-006 plus fresh Curator reproduction against live configurator d1ca9abb6dcfbedb7e33cddd96bc54e7da0a6b5e, with reviewed packet planning/portfolio-20260823-2349 at 387a2a7b27d11b81c3c571aaf07cf543af626757 now partially consumed and not relied on as authorization; authorized on curation/generator-validation-portability-20260824-1543.",
      "automated_validation": [
        "Default aliased-root and explicit canonical-root subprocess cases both pass the checker on macOS; synthetic alias and identical-root cases cover both branches on hosts whose default root exposes only one branch.",
        "Semantic generator and layout-spec output remain byte-deterministic and equal the checked-in fixture through non-mutating stdout/in-memory execution in both root environments.",
        "Aliased-root normal file output fails with the exact policy classification and leaves no target; identical-root isolated output succeeds atomically, including an ordinary temporary src/generated.hpp subdirectory.",
        "Repository paths, .git, outside-root paths, relative paths, traversal, symlink/case/inode aliases, input overwrite, active baseline aliases, candidate.view, active_storage.view, RuntimeConfigView, and GeneratedRuntimeConfigBaseline-like targets continue to fail for the exact current reasons.",
        "Malformed schema/layout/table/point cases fail for their semantic reason rather than being masked by output-path rejection.",
        "Generated-source contract, generator modes, prepared-v2 preview, source-authority intake, checker census, validation health, full runtime-config aggregate, agent-framework, docs-navigation, and docs-agent-surface checks pass; independent focused validation-policy review confirms no invariant weakening."
      ],
      "canonical_build": "NOT_REQUIRED: checker/test correction and deterministic validation metadata only; any generator, workflow, compiled source, or build-input delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused checker branch if either host lane loses meaningful semantic or output-policy coverage; do not relax the shared validator or hide a current aggregate failure.",
      "status_documentation_updates": "Record only the validation repair and GP-PROV-002 publication dependency; do not create a generator capability, runtime behavior, artifact acceptance, or hardware claim.",
      "done_evidence": "Implementation branch glyph/gp-val-004-generator-temp-root-portability-20260824 from live configurator dfc92adf2910532e24f429f61ea3c1fe7026425a; independent validation-policy review PASS; aliased and identical synthetic temp-root lanes, stdout semantic determinism, fixture equality, malformed-input corpus, exact negative output-policy matrix, generator modes, checker census, validation health, full current aggregate, agent-framework, docs-navigation, and docs-agent-surface checks PASS. Only tools/check_glyph_generated_source_owned_generator_contract.py and deterministic docs/runtime_config/fixtures/glyph_checker_census.json changed; shared output policy, generator semantics, active source/table bytes, firmware/runtime behavior, workflow, hardware, Nunchuk, and root-cause claims remain unchanged.",
      "stop_conditions": [
        "Any accepted/rejected output-policy decision is not already fixed by GP-SRC-003/005 authority.",
        "Any generator semantic, active/inert install, workflow, firmware/runtime, table, product, profile, source-authority, device-write, persistence, protobuf-write, flashing, hardware, Nunchuk, or root-cause scope appears.",
        "The checker can pass only by skipping semantic negative cases, masking their failure reason, weakening alias/path checks, or changing tools/glyph_checker_context.py."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-003",
      "title": "Complete prepared-packet integrity and output guardrails",
      "status": "DONE",
      "branch": "glyph/gp-src-003-v2-cycle-20260824",
      "objective": "Make every reusable generator-v2 preparation and installation path verify exact normalized-input-to-artifact-to-manifest correspondence and fail closed for active, compiled, protected, aliased, or ambiguous output targets.",
      "why_this_matters": "The live installer accepts protected output and stale correspondence, while pushed recovery tip 2b734b26439e9028717becf0010e345cb5efce6c still accepts resealed input-digest, provenance, ownership, generator-version, and primitive-type drift because prepared schema v1 omits the normalized input needed to rederive its claim.",
      "hardware_risk": "H1",
      "behavioral_claim": "This work changes host-side integrity validation and output-path safety only. It must not write or change active source, active table bytes, firmware runtime behavior, RuntimeConfigView publication, or controller behavior.",
      "scope": "Replace prepared schema v1 with strict prepared schema v2 carrying the exact canonical normalized generator input returned by existing validation, including metadata and authority references. One shared validator must regenerate artifact and manifest deterministically from that normalized input and require exact typed object equality, then rederive the authoritative baseline, canonical 28-table order, table/artifact/input/row/manifest/prepared digests, provenance, ownership, actions, counts, classification, generator version, and every primitive type. Preparation, installation, and preview must reject schema v1 and all unknown/missing/duplicate fields. One shared resolved output policy must require every file target to be absolute under the lexical system temporary root returned by tempfile.gettempdir(), resolve under its canonical root, reject repository/other roots, case variants, aliases, symlinks, input overwrite, and active-publication-like names, and write atomically; stdout and dry-run remain non-mutating.",
      "explicit_excluded_scope": "No active or compiled source write; no table-byte, routing, firmware, candidate, build, artifact-publication, workflow, production-ownership, profile-intent, game-semantic, runtime-loading, persistence, WebSerial/device-write, protobuf-write, flashing, Nunchuk, or root-cause change or claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator 6b8ebcd404dcbfe9b579eed41fb35b889e9da598 still lacks strict reusable prepared correspondence and isolated-output enforcement. Fresh Planner packet glyph-portfolio-20260823-2349 and two independent Curator reproductions prove that pushed tip 2b734b26439e9028717becf0010e345cb5efce6c accepts a changed input_semantic_digest after outer resealing because prepared v1 omits the normalized input; independent review also reproduced resealed row provenance, full-replacement ownership, generator-version, boolean/non-finite primitive, and synthetic-to-production drift. tools/source_owned_source_authority_intake.py places intake_id and authorization_reference in normalized metadata, so the exact normalized input is source-authority-bearing and must be carried and regenerated, not discarded or reinterpreted.",
      "dependencies_prerequisites": [
        "GP-SRC-001 and GP-SRC-002 are DONE on configurator; their active-source classification, preview non-claims, and strict preview behavior must remain intact.",
        "Implementation recovery starts from a fresh descendant of 6b8ebcd404dcbfe9b579eed41fb35b889e9da598, may reuse reviewed output-policy and correspondence code from pushed tip 2b734b26439e9028717becf0010e345cb5efce6c, but must amend that branch with the prepared-v2 normalized-input architecture and keep every active table byte unchanged.",
        "The pushed branch is failed recovery evidence, not completion: focused checks and the aggregate passing there do not override the independently reproduced resealed-correspondence failures.",
        "The one permitted non-semantic portability-test delta is exact: when tempfile.gettempdir() and its resolved spelling differ, the resolved-root alias case must reject; when they are identical, the safe returned-root path must pass and remain non-mutating. Real aliases, symlinks, lexical paths outside the returned temporary root, repository paths, and active-publication-like names must still reject.",
        "Other permitted post-snapshot deltas are queue/status publication and deterministic checker-census or validation-health fixture regeneration caused solely by authorized checker bytes; any normalized-input semantics, baseline, table order, generator mode, intake authority fields, preview meaning, output-path policy, table source, or manifest applicability drift outside this exact v2 reauthorization requires fresh curation."
      ],
      "substantive_authorization_rationale": "The failure is directly reproducible without mutation and the source-authority-preserving architecture is now exact: carry the canonical normalized input, regenerate the deterministic artifact and manifest, and require exact typed equality before any preview or install. Rejecting legacy prepared v1 avoids inventing compatibility for packets that cannot prove their input claim. This resolves the material contract decision without choosing production content, ownership, mappings, or game semantics.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Another current change fully closes preparation/install digest recomputation and output-path safety before implementation.",
        "The normalized generator-input contract, prepared-v2 shape, baseline identity, table order, production gate, or preview contract materially changes beyond the exact architecture authorized here.",
        "The implementation would write compiled or active source or choose production table content or ownership."
      ],
      "authorization_snapshot_provenance": "Fresh substantive Curator reauthorization of Planner branch planning/portfolio-20260823-2349, candidate GP-SRC-003, packet commit 387a2a7b27d11b81c3c571aaf07cf543af626757, packet/live base 6b8ebcd404dcbfe9b579eed41fb35b889e9da598, after two independent reproductions against pushed recovery tip 2b734b26439e9028717becf0010e345cb5efce6c; prepared schema v2 and normalized-input deterministic regeneration are bound on curation/portfolio-20260824-0051-review.",
      "automated_validation": [
        "Tampered normalized input, metadata/authority reference, prepared root, artifact, table, point, manifest row/action/ownership/provenance, generator version, counts, classification, baseline, and every declared semantic digest fail closed after adversarial outer resealing, including unknown, missing, duplicate, wrong primitive type, boolean-as-integer, and non-finite values.",
        "Prepared v2 validation deterministically regenerates artifact and manifest from the carried canonical normalized input and requires exact typed equality; prepared v1 and any normalized-input/artifact/manifest mismatch fail closed.",
        "Active header, every repository path, non-temporary absolute root, case-variant, relative, input-overwrite, symlink, path-alias, traversal, and active-publication-like target cases fail for prepare, install, and preview through one shared policy.",
        "Safe isolated absolute offline output is atomic; dry-run and rejected cases leave the repository byte-for-byte unchanged.",
        "The portability corpus passes both distinct raw/resolved temporary-root alias semantics and identical /tmp-style semantics without weakening real alias or symlink rejection; the full current aggregate passes after recovery on the fresh canonical branch context.",
        "Generator-mode, source-authority-intake, C++ preview, candidate-generation safety, table-source-sync, full runtime-config aggregate, agent docs, and docs-navigation checks pass; checker-census and validation-health artifacts are regenerated mechanically with no applicability reclassification.",
        "Before/after semantic digests prove all 28 active table arrays and compiled firmware source are unchanged."
      ],
      "canonical_build": "NOT_REQUIRED when compiled source and all active table bytes remain unchanged; any such delta stops this H1 order and requires fresh H2/H3 authorization.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused host-tool/docs branch if valid offline output or deterministic preparation regresses; do not restore acceptance of unverified packets or protected output targets without renewed curation.",
      "status_documentation_updates": "Correct the generator-v2 integrity and output-boundary docs without creating production authority, a firmware candidate, or a hardware claim.",
      "done_evidence": "Independent repaired-scope review PASS; prepared-v2 normalized-input regeneration and complete resealed tamper/path/row/provenance/type corpus; safe-output rejection and atomicity checks; current aggregate and navigation PASS; exact active-source/table semantic digests unchanged; live feature ref verification and canonical integration pending publication of this snapshot.",
      "stop_conditions": [
        "Any semantic value, ownership, mapping, or production authority must be inferred.",
        "Any active/compiled source, table byte, RuntimeConfigView path, workflow, firmware candidate, or hardware artifact would change.",
        "The reconciled branch cannot pass the full current aggregate under current and Ubuntu-style identical-/tmp semantics without relaxing the returned-temporary-root or real alias/symlink guardrails.",
        "Any runtime-loaded config, persistence, device-write, protobuf-write, flashing, Nunchuk, or root-cause boundary is crossed."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-004",
      "title": "Make active baseline classification machine-true",
      "status": "DONE",
      "branch": "glyph/gp-src-004-active-baseline-manifest-correspondence-20260831",
      "objective": "Complete the accepted active-baseline classification objective by making the current validation-manifest row and its load-bearing checks identify GeneratedRuntimeConfigBaseline.current.hpp as active compile-time table content rather than an inert baseline.",
      "why_this_matters": "The active header, focused checker, fixture, and current docs now correctly distinguish active compile-time table content from unchanged source-owned RuntimeConfigView publication, but the current load-bearing manifest still describes generated_baseline_artifact as 'inert baseline equivalence' and no check rejects that contradiction.",
      "hardware_risk": "H0",
      "behavioral_claim": "This repairs validation classification correspondence only. It changes no generated header, table point, symbol, semantic digest, generator behavior, compiled source, active RuntimeConfigView publication, routing, firmware/runtime behavior, artifact, device, or controller behavior.",
      "scope": "Replace the generated_baseline_artifact manifest reason with exact wording that identifies active compile-time table-content source through UltimateIdentityRuntimeTables.hpp while preserving unchanged source-owned active-view publication. Strengthen the existing baseline/manifest validation seam to reject inert classification for that exact row and retain inert classification for example and review artifacts. Regenerate only deterministic checker-census and validation-health consequences caused by authorized checker bytes.",
      "explicit_excluded_scope": "No generated header or fixture semantic change; no table point, symbol, declaration, order, digest, generator output, source-owned include chain, RuntimeConfigView, GetActiveRuntimeConfigState, ResolveActiveRuntimeConfig, routing, build input, production profile, ownership, candidate, artifact, hardware, runtime-loaded config, persistence, WebSerial/device write, protobuf write, flashing, Nunchuk, root-cause, or game-semantic change or claim.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Live configurator d94eb6d629f9e8e73e893971a3f47c4485cf17ee. src/modes/UltimateIdentityRuntimeTables.hpp includes src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp; tools/check_glyph_generated_source_owned_baseline_artifact.py and docs/runtime_config/generated_source_owned_baseline_artifact.md classify it as active compile-time table-content source while preserving source-owned active-view publication. The exact current manifest row generated_baseline_artifact remains load-bearing with reason 'inert baseline equivalence'. Planner packet glyph-portfolio-20260831-1540 at 896a06c092bfa2f99339c944fceffda957e4478d identified the same incomplete accepted objective, and independent Curator verification confirmed no equivalent manifest correspondence gate exists.",
      "dependencies_prerequisites": [
        "GP-SRC-001 and the prior GP-SRC-004 implementation remain canonically DONE; their active-table-source truth, exact table identity, and source-owned publication distinction remain authoritative.",
        "Implementation starts from a fresh live-configurator descendant of d94eb6d629f9e8e73e893971a3f47c4485cf17ee with the active include chain, focused classification checker, fixture, and generated_baseline_artifact manifest row materially unchanged.",
        "The patch is confined to classification metadata/checking and mechanically consequent census/health bytes; any generated or compiled source delta stops."
      ],
      "substantive_authorization_rationale": "The contradiction is direct and the intended classification is already fixed by accepted source, docs, and focused checks. Reopening GP-SRC-004 preserves the identity of its incomplete classification objective. Exact manifest wording plus a bounded rejection of inert classification closes the remaining gap without choosing product content, profile intent, source ownership, runtime architecture, or gameplay semantics.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The active include chain, focused classification contract, manifest schema/row identity, or source-owned active-view publication changes materially before implementation.",
        "Another canonical change enforces equivalent or stronger active-baseline manifest correspondence first.",
        "The repair would require a generated/compiled source, table, generator, publication, routing, build, artifact, or hardware change."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of reopened candidate GP-SRC-004 from planning/portfolio-20260831-1540 commit 896a06c092bfa2f99339c944fceffda957e4478d, packet/live base d94eb6d629f9e8e73e893971a3f47c4485cf17ee, with bounded source/include/manifest/checker verification on curation/portfolio-20260831-1540-review.",
      "automated_validation": [
        "The generated_baseline_artifact manifest row uses exact active compile-time table-content classification and deliberate reintroduction of inert wording fails.",
        "Example/layout-spec/review artifacts retain their exact inert classifications and deliberate cross-classification drift fails.",
        "Git diff and existing semantic/source-sync checks prove all 28 table values, symbols, declarations, order, digests, include chain, and active publication source remain unchanged.",
        "Generated-baseline, manifest aggregate adversarial, checker census, validation health, full runtime-config aggregate, framework, sequence, navigation, agent-surface, and exact diff checks pass with fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 manifest classification and checker correspondence only; any generated or compiled source, build input, or runtime delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused metadata/checker repair if exact active/inert classification cannot be enforced without semantic source change; never restore inert wording for the active baseline as current truth.",
      "status_documentation_updates": "Record GP-SRC-004 as Done after exact reviewed integration of the final manifest-correspondence repair under the repository's legacy-ID correspondence policy. Retain every runtime, product, artifact, and hardware non-claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "a40e446c09b3f69e699ad697be3eda874a122f62",
        "reviewed_implementation_sha": "aacff861c7958eefee9fad86e271489ec956ad8e",
        "prior_canonical_integration_sha": "aacff861c7958eefee9fad86e271489ec956ad8e",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "tools/check_glyph_generated_source_owned_baseline_artifact.py"
        ],
        "independent_review_provenance": "Fresh independent publication review PASS on exact feature tip aacff861c7958eefee9fad86e271489ec956ad8e; exact ancestry, authorized scope, active/inert classification correspondence, no runtime/product drift, and publication safety were confirmed.",
        "validation_provenance": "Focused baseline checker, manifest adversarial coverage, 194-entry census, validation health, full runtime-config aggregate, framework, navigation, docs-agent-surface, py_compile, and git diff checks passed on the exact integrated snapshot; no build or hardware was required."
      },
      "stop_conditions": [
        "Any table value, symbol, declaration, digest, generated/compiled source, generator behavior, routing, or active-view publication would change.",
        "Any manifest applicability, load-bearing status, or unrelated entry would be reclassified.",
        "Any product/profile/source-ownership judgment, build, artifact, hardware, runtime loading, persistence, WebSerial/device write, protobuf write, flashing, Nunchuk, root-cause, or game-semantic scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-004",
      "title": "Repair reviewed manual-capture correspondence",
      "status": "DONE",
      "branch": "glyph/gp-config-004-capture-correspondence-repair-20260826",
      "objective": "Make every reviewed official-configurator capture status, duplicate artifact field, nested path, precondition, operator/route record, and deterministic comparison describe one exact internally consistent capture packet.",
      "why_this_matters": "GP-CONFIG-004 is recorded Done, but live-byte-identical adversarial reproduction proves its checker still accepts contradictory evidence: the diff row can disagree with metadata and comparison.json, result.md can disagree with metadata overall status, top-level paths and hashes can contradict nested artifact fields, and nested checker/comparison paths can name nonexistent files. A second reviewed-shape construction can substitute unrelated existing precondition files and empty nested operator/route objects. The existing zero-capture and adversarial checks do not exercise those failures.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work strengthens an offline evidence checker and synthetic fixtures only. It performs no app interaction or capture, asserts no official compatibility, and changes no firmware/configurator product behavior.",
      "scope": "Preserve the strict schema-v2 PASS/FAIL/PARTIAL/INCONCLUSIVE matrix and reopen only the offline manual-capture checker, the existing export-candidate-diff checker/helper, synthetic tests, template/docs, and deterministic census/health consequences. Make validate_result_doc return the parsed overall status and require it to equal metadata status and result_status. Require metadata comparison status and comparison-file status to equal the post_capture_json_diff_review row. Require top-level input/output path and SHA-256 fields to equal their nested artifacts fields exactly rather than selecting one with fallback truthiness. Require exact semantic basenames input_candidate.json, output_export.json, metadata.json, notes.md, comparison.json, and rejection_note.md for every applicable field; executed diff checker_output_path and comparison_path must both be comparison.json; resolve every declared capture artifact to that exact capture-local regular non-symlink file. Require preconditions to have exactly the six template keys, capture_id equal the folder name, precondition_status equal PASS, the four canonical tracked paths, and those tracked files to retain the exact authorization-snapshot SHA-256 values; require copied input_candidate.json to be byte-equal to the canonical preview. Require operator_fields and routes to have exactly the template keys; bind top-level operator, app version, import route, and export route to their duplicate nested values. Add one pure capture-local JSON-pointer diff helper to tools/check_glyph_official_configurator_export_candidate_diff.py without changing its current static report: comparison_tool and checker_identity must both equal that tool path, checker_version must equal GLYPH_OFFICIAL_CONFIGURATOR_CAPTURE_DIFF_V1, and structural_diff must exactly equal {schema_name: official_configurator_capture_json_pointer_diff, schema_version: 1, equal: bool, added_paths: sorted RFC6901 JSON-pointer list, removed_paths: sorted RFC6901 JSON-pointer list, changed_paths: sorted RFC6901 JSON-pointer list} recomputed from input_candidate.json and output_export.json. Array indices are pointer segments, object keys use RFC6901 escaping, and type/scalar inequality records one changed path without embedding values. The diff is descriptive only and does not infer compatibility. PASS, accepted FAIL, and rejected FAIL retain no gaps. For PARTIAL and INCONCLUSIVE only, require gaps to equal the sorted row IDs whose status is NOT_TESTED or INCONCLUSIVE. Preserve exact null/non-null combinations for accepted-output, rejected-note, and executed-diff shapes, complete hashes.txt correspondence, the zero-capture scaffold, and full synthetic result matrix.",
      "explicit_excluded_scope": "No official app launch, operator action, new real capture, compatibility/importability/exportability interpretation, production exporter, firmware/runtime source, device write, persistence, WebSerial, protobuf write, flashing, hardware result, or game-semantic claim.",
      "touched_planes": [
        "configurator",
        "docs/checkers"
      ],
      "source_authority": "Fresh live verification pins configurator at caf37e10673896b3bf5e2815875a93310b3f3ac1 and fresh packet glyph-portfolio-20260824-2349 at ffba28772d8559df4b356de9b3a3f02248d16c07. On checker bytes identical to that live base, independent reproduction accepted a synthetic reviewed packet after changing the diff row to FAIL while metadata comparison and comparison.json stayed PASS, changing result.md to PARTIAL while metadata stayed FAIL, contradicting all top-level input/output paths and hashes, and naming nonexistent nested checker/comparison paths. Direct source inspection shows validate_result_doc returns no status, artifact validation chooses nested values with `or`, checker_output_path is not resolved, comparison status is not bound to the diff row, nested object keys are open-ended, preconditions require only existing paths, and comparison identity/output shape are weakly constrained. The template fixes the nested key sets and the existing comparison_tool path. Authorization-snapshot SHA-256 values are manifest 08c8e43218250ad75f187f3fc5d22dd36fc27b112047f9dfdb612cbb232359a5, default fixture 2d24324928f9c0292e3fce74f02083a740272eeb7a271437be10b7b4f6bf025e, back-and-forth fixture 0a782564bd454c50e3fbeccc754acaec6c6ffdc6e0dcff145eef9121b7a3b39b, and canonical preview 7a083bf84bc030e7170739070a9c005527611a457e33db5adaf5342969b3e9ec. The live capture tree contains zero completed captures, so exact schema repair requires no real evidence migration or interpretation.",
      "dependencies_prerequisites": [
        "GP-CONFIG-003 is DONE; its exact regular-file .DS_Store exception and rejection of all other unknown entries, directories, and symlinks must remain intact.",
        "The canonical GP-CONFIG-004 schema-v2 result matrix remains authoritative; this repair binds existing duplicate fields and paths rather than deleting or reinterpreting them.",
        "The official corpus, canonical preview artifact, and current five-check offline lane remain source authority only for their existing bounded claims; the live manual-capture tree remains at zero completed captures.",
        "Implementation begins after legitimate GP-PROV-002 publication recovery or from a fresh live-configurator descendant that has reconciled it. Exact reviewed GP-PROV-002 integration, queue/status publication, and deterministic census/health regeneration are permitted unrelated deltas; any change to this checker, capture schema/docs, official corpus/preview bytes, or result semantics requires fresh curation.",
        "Synthetic fixtures must not be stored or described as operator evidence."
      ],
      "substantive_authorization_rationale": "The fail-open result is mechanically reproduced and every repair decision is fixed by the already-authorized schema-v2 matrix, canonical tracked artifact identities, and capture-local correspondence rules. Exact equality, strict schemas, canonical basenames, resolved regular files, canonical digests, byte equality, and deterministic comparison output require no app, product, compatibility, operator, or gameplay judgment. Reopening the same work-order ID preserves the truth that its prior Done evidence was incomplete.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "A real completed capture arrives before the schema/checker correction and requires evidence-preserving migration judgment.",
        "The official capture artifact layout or primary corpus changes materially before implementation.",
        "The canonical preview, comparison checker identity/version/output contract, or schema-v2 result matrix requires a substantive redesign rather than exact binding.",
        "Implementation would delete duplicate fields, interpret compatibility, automate the app, or fabricate an operator/reviewer result."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260824-2349, repair/revalidation candidate GP-CONFIG-004, packet commit ffba28772d8559df4b356de9b3a3f02248d16c07, packet/live base caf37e10673896b3bf5e2815875a93310b3f3ac1, with independent fail-open reproduction and source audit on curation/portfolio-20260826-2131-review. The earlier completion remains historical implementation evidence but is not sufficient Done evidence.",
      "automated_validation": [
        "Zero-capture scaffold and exact .DS_Store host-metadata cases remain valid without recording evidence.",
        "Complete synthetic PASS, accepted FAIL, rejected FAIL, PARTIAL, and INCONCLUSIVE packets validate only with exact metadata/result-doc/row/comparison status correspondence, exact accepted/rejected nullability, exact gaps, and no positive compatibility claim.",
        "Individually and jointly mutate comparison-vs-row status, comparison-file-vs-row status, result.md-vs-metadata status, top-level-vs-nested path/hash, semantic basename, nested path existence/type/location, capture ID, precondition status/path/snapshot digest, copied-input-versus-preview bytes, operator/route schema and duplicate values, comparison identity/version, JSON-pointer escaping/order/content, nullability, and exact row-ID gaps; every contradiction fails for the intended reason.",
        "Capture diff positive/adversarial cases cover nested objects, arrays, RFC6901 tilde/slash escaping, root scalar/type change, additions, removals, and scalar changes; the recomputed descriptive diff contains no values and makes no compatibility judgment, while the existing static export-candidate-diff report remains byte-identical.",
        "Malformed status syntax, duplicate/missing/unknown rows, status/pass mismatch, stale/missing/extra hashes, symlink, directory, alias, wrong existing file, unknown file, fabricated comparison, and positive-claim cases fail.",
        "Official-configurator manual-capture, five-check validation lane, docs-navigation, docs-agent-surface, and current runtime-config aggregate checks pass."
      ],
      "canonical_build": "NOT_REQUIRED: offline evidence checker, docs, and synthetic fixtures only; any product or compiled source delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused checker/docs repair if a valid schema-v2 packet cannot be represented without ambiguity; preserve all real evidence bytes and never restore fallback-field selection, unbound paths/statuses, or weak nested schemas.",
      "status_documentation_updates": "Record GP-CONFIG-004 as reopened for exact correspondence repair and keep GP-CONFIG-002 substantive-dependency gated until the repair is independently reviewed and canonically integrated; retain zero completed captures and every compatibility/device/runtime non-claim.",
      "done_evidence": "Implementation commit b606244f8810b7457be09de4813dff68d87eb2117 on the named repair branch; independent offline-evidence checker review and repaired-scope re-review PASS; complete positive and adversarial correspondence corpus including exact nullability, duplicate-field binding, capture-local path/hash/status checks, and RFC6901 array/root/type/add/remove/tilde/slash cases; zero-capture, official five-check lane, checker census (190 entries), current aggregate, framework, navigation, sequence, and agent-surface PASS; merged into fresh canonical configurator in publication commit 3a266b2 and live feature ref b606244f8810b7457be09de4813dff68d87eb2117 verified; no real capture and runtime/configurator product code changed: NO.",
      "stop_conditions": [
        "Any app behavior, compatibility outcome, operator action, or reviewer observation must be inferred.",
        "Any duplicate representation, unknown entry, hash/path/status mismatch, weak nested schema, noncanonical comparison output, or output/rejection ambiguity would remain accepted.",
        "The repair requires a schema migration, field deletion, official-app execution, operator evidence, or product/runtime checker change.",
        "Any firmware/runtime, device-write, persistence, protobuf-write, flashing, hardware, Nunchuk, or root-cause scope is required."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-003",
      "title": "Census every CI publication route and claim",
      "status": "DONE",
      "branch": "glyph/gp-val-003-tracked-workflow-census-repair-20260831",
      "objective": "Complete the accepted GP-VAL-003 route-census objective by discovering and classifying every tracked top-level or nested GitHub workflow that builds, publishes, releases, or invokes another build workflow while preserving exact current health correspondence.",
      "why_this_matters": "Git tracks three workflow files, including config/glyph/.github/workflows/build.yml, but the load-bearing census discovers only .github/workflows and records two workflows. The omitted nested caller runs on push/pull_request and invokes a moving external reusable workflow while current health prose still calls the two-file census complete and all checks pass.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work adds static CI route census, explicit classification, and current-claim parity only. It does not edit or invoke a workflow, build firmware, publish bytes, select an owner/caller/store, or change product behavior.",
      "scope": "Update tools/check_glyph_runtime_config_validation_publication_workflow.py so static Git discovery includes every tracked regular .yml/.yaml file whose normalized path is .github/workflows/* or contains /.github/workflows/. Extend the existing workflow-census fixture with config/glyph/.github/workflows/build.yml, its exact bytes, push/pull_request events, reusable-workflow invocation route, and UNRESOLVED_EXTERNAL classification with no gate. Preserve the top-level build.yml CURRENT_GATED validation classification and top-level build-device-config.yml UNRESOLVED_EXTERNAL classification. Update validation-health prose, exact manifest direct dependencies, adversarial fixtures, and only deterministic census/health consequences.",
      "explicit_excluded_scope": "No workflow YAML edit, checker applicability reclassification, manifest expansion, route reinterpretation, caller/owner decision, meta.yaml interpretation, secret/PAT/permission/release change, branch-protection claim, build, glyph_nuker execution, upload, store selection, artifact acceptance, firmware/runtime source, device write, persistence, protobuf write, flashing, or hardware result.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator d94eb6d629f9e8e73e893971a3f47c4485cf17ee. git ls-files finds .github/workflows/build.yml, .github/workflows/build-device-config.yml, and config/glyph/.github/workflows/build.yml. tools/check_glyph_runtime_config_validation_publication_workflow.py uses git ls-files .github/workflows, so its two-entry fixture omits the nested caller; docs/runtime_config/runtime_config_validation_health.md nevertheless says the tracked census records both workflow files. The build-input provenance inventory already records the nested caller and its GregTurbo/HayBox-Glyph/.github/workflows/build-device-config.yml@configurator moving ref as UNRESOLVED_EXTERNAL. Planner packet glyph-portfolio-20260831-1540 and independent Curator inspection confirm no equivalent complete route-census gate exists.",
      "dependencies_prerequisites": [
        "GP-VAL-001 and GP-VAL-002 remain DONE; checker-census freshness, curated applicability authority, and build.yml validation-before-publication remain intact.",
        "The current three-workflow tracked set, current 32-entry/28-load-bearing manifest state, machine health schema, and accepted top-level route classifications remain materially unchanged at implementation start.",
        "Static discovery and route extraction prove tracked declarations only and must not claim live invocation, external caller/owner authority, PAT validity, permissions, or release authority.",
        "Any workflow mutation, route remediation, manifest applicability change, or unresolved external decision remains separate authority."
      ],
      "substantive_authorization_rationale": "The omitted tracked workflow is directly source-proven and GP-VAL-003's accepted objective explicitly promised a complete tracked CI publication-route census, so same-identity reopening is correct. Repository-wide static workflow discovery plus exact existing UNRESOLVED_EXTERNAL treatment closes the gap without editing a workflow or deciding caller, owner, secret, permission, release, product, or runtime semantics.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The tracked workflow set, workflow-census schema, route extractor, current top-level validation dominance, or accepted classifications change materially before implementation.",
        "Authoritative caller/ownership evidence arrives and changes build-device-config.yml classification.",
        "Implementation would edit a workflow, reclassify a current route, infer external authority, or require tools/glyph_checker_context.py or a product/runtime checker."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of reopened candidate GP-VAL-003 from planning/portfolio-20260831-1540 commit 896a06c092bfa2f99339c944fceffda957e4478d, packet/live base d94eb6d629f9e8e73e893971a3f47c4485cf17ee, with bounded tracked-workflow, route, fixture, health, manifest, and provenance verification on curation/portfolio-20260831-1540-review.",
      "automated_validation": [
        "Static discovery finds exactly every tracked top-level or nested workflow regular file, including config/glyph/.github/workflows/build.yml; omitted, added, renamed, untracked, directory, symlink, hash, event, or path-normalization drift fails.",
        "The census records all direct build/postprocess/upload/release and reusable-workflow invocation routes with exact tokens and classifications; moving reusable-workflow ref or workflow_call/event drift fails.",
        "Top-level build.yml remains CURRENT_GATED with validation dominance; both unresolved workflows remain UNRESOLVED_EXTERNAL with no fabricated gate, invocation, caller, owner, PAT, permission, or release claim.",
        "Validation-health prose and manifest direct dependencies name all three tracked workflows and stay correspondent without changing manifest applicability or count; workflow YAML bytes remain unchanged.",
        "Checker census, validation health, publication workflow, full runtime-config aggregate, agent-framework, sequence, docs-navigation, and docs-agent-surface checks pass with no applicability weakening.",
        "Independent repaired-scope review confirms the patch changes correspondence enforcement only and does not reclassify any validation entry or route."
      ],
      "canonical_build": "NOT_REQUIRED: static workflow census/classification and docs/checkers only; no workflow or build input changes.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the focused route-census repair if every tracked workflow cannot be represented without external-authority inference; preserve current validation dominance and unresolved classifications rather than hiding the nested route.",
      "status_documentation_updates": "Record GP-VAL-003 as reopened for complete tracked-workflow route correspondence and later Done only after exact reviewed integration with fresh completion evidence for this repair under the repository's legacy-ID correspondence policy. Its earlier completion evidence must remain historical and must not substitute for new repair correspondence. Retain all external ownership, runtime, artifact, and hardware non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "a7bf7dab6980703fd0003b985d05e0e70b2b7468",
        "reviewed_implementation_sha": "a3c554ab5b8ee266bb8c1f789d8d103c7aef2e86",
        "prior_canonical_integration_sha": "a3c554ab5b8ee266bb8c1f789d8d103c7aef2e86",
        "reviewed_changed_paths": [
          "docs/agent_framework/SUBAGENT_CONTRACTS.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/fixtures/runtime_config_validation_publication_workflow.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_runtime_config_validation_publication_workflow.py"
        ],
        "independent_review_provenance": "Fresh independent reviewer PASS on exact feature tip a3c554ab5b8ee266bb8c1f789d8d103c7aef2e86; route census, unresolved external classification, scope, authority, and required static gates were confirmed.",
        "validation_provenance": "Focused publication-workflow checker, manifest and health checks, full runtime-config aggregate, 194-entry census, framework, sequence, navigation, agent-surface, py_compile, and git diff checks passed on the exact reviewed snapshot; no build or hardware was required."
      },
      "stop_conditions": [
        "Any workflow, manifest applicability, checker classification, permission, secret, trigger, caller, release, or artifact destination must change.",
        "Any unresolved external ownership/caller fact would be inferred.",
        "The complete tracked workflow set cannot be bound without weakening manifest, health, route, or validation-dominance authority.",
        "Any firmware build/input, postprocessor execution, publication, device write, flashing, or hardware claim occurs."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-009",
      "title": "Make validation-health schema exact",
      "status": "DONE",
      "branch": "glyph/gp-val-009-health-schema-exactness-20260831",
      "objective": "Make the validation-health machine record exact by removing its obsolete duplicate strong_signal_exclusions field and rejecting every unknown, missing, mistyped, stale, or contradictory field against current manifest- and census-derived truth.",
      "why_this_matters": "The current health fixture reports explicit_exclusion_count 37 while also carrying an unchecked empty strong_signal_exclusions list. The checker derives the count from the manifest, never reads that duplicate list, and does not enforce an exact top-level health schema, so contradictory or invented health state can pass.",
      "hardware_risk": "H0",
      "behavioral_claim": "This strengthens validation-health schema and source correspondence only. It changes no manifest entry, exclusion, applicability, checker product semantics, workflow, build input, generated source, firmware/runtime behavior, artifact, device, or controller behavior.",
      "scope": "Bump docs/runtime_config/fixtures/runtime_config_validation_health.json to schema_version 3 and remove exactly the obsolete top-level strong_signal_exclusions field. Update tools/check_glyph_runtime_config_validation_health.py to require the exact remaining top-level key set and exact nested key/type shapes, reject duplicate JSON keys, and bind repository checker count, manifest entry/load-bearing/historical/exclusion counts, census freshness identity, current result records, known pre-existing failures, and historical evidence to the current checked-in census and manifest without duplicating the manifest exclusion list. Update validation-health documentation and embedded isolated/adversarial cases, then regenerate only deterministic checker-census consequences.",
      "explicit_excluded_scope": "No manifest schema, entry, exclusion, order, applicability, branch policy, command, dependency, load-bearing, or reason change; no checker product semantic, workflow, build input, source, generator, firmware/runtime, artifact, device, persistence, WebSerial/protobuf write, flashing, hardware, Nunchuk, root-cause, or game-semantic change or claim.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Live configurator d94eb6d629f9e8e73e893971a3f47c4485cf17ee. docs/runtime_config/fixtures/runtime_config_validation_health.json schema v2 reports curated_runtime_config_scope.explicit_exclusion_count 37 and separately stores strong_signal_exclusions as an empty list. tools/check_glyph_runtime_config_validation_health.py derives the count from the manifest and compares curated_runtime_config_scope but never reads the duplicate list or requires an exact top-level key set. Current health and full aggregate pass with checker census 194, manifest entries 32, current load-bearing checks 28, and exclusions 37. Planner packet glyph-portfolio-20260831-1540 at 896a06c092bfa2f99339c944fceffda957e4478d proposed the gap; independent Curator and specialist inspection confirmed no equivalent schema gate exists.",
      "dependencies_prerequisites": [
        "The current health fixture/checker/docs, manifest v4 entry and exclusion sets, 194-entry checker census, and 32-entry/28-load-bearing/37-exclusion derived state remain materially unchanged at implementation start.",
        "Any earlier authorized manifest, checker, census, or health change is integrated first and this work is rebased to its exact deterministic current counts without changing the schema-v3 removal decision.",
        "Implementation uses checked-in JSON, manifest, census, Markdown, and isolated in-memory/adversarial fixtures only; no discovered checker, workflow, build tool, or network route is executed beyond existing authorized validation."
      ],
      "substantive_authorization_rationale": "The contradiction and fail-open schema are directly source-proven. Curator resolves the Planner's representation fork exactly: schema v3 removes the unused duplicate exclusion list and retains the manifest as sole exclusion authority, while exact key/type/source correspondence prevents silent replacement with another contradictory field. No applicability, product, runtime, architecture, external, or user decision remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The health schema, manifest schema or exclusion meaning, census schema, current result/historical record shapes, or derived count meanings change materially before implementation.",
        "Another canonical change supplies equivalent or stronger exact health-schema and duplicate-state rejection first.",
        "The repair would require retaining a second exclusion authority, changing manifest classification, or interpreting checker/product semantics rather than validating current source correspondence."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of candidate GP-VAL-009 from planning/portfolio-20260831-1540 commit 896a06c092bfa2f99339c944fceffda957e4478d, packet/live base d94eb6d629f9e8e73e893971a3f47c4485cf17ee, with bounded health fixture/checker/manifest/census and adversarial-coverage verification on curation/portfolio-20260831-1540-review.",
      "automated_validation": [
        "Schema v3 has exactly the authorized top-level fields, contains no strong_signal_exclusions field, and every nested object/list has exact reviewed keys and primitive types; duplicate, unknown, missing, reordered-authority, null, boolean-as-integer, and malformed fields fail.",
        "Repository checker count, census freshness record, manifest entry/load-bearing/historical/exclusion counts, current checker results, known pre-existing failures, and historical evidence are rederived or cross-checked against exact current source; stale count/content mutations fail independently.",
        "The manifest's 37-entry strong-signal exclusion list remains the sole exclusion authority and is byte-unchanged; no manifest entry, applicability, policy, command, dependency, reason, or load-bearing classification changes.",
        "Validation-health Markdown summary remains exactly correspondent to manifest entries and load-bearing checks and documents schema-v3 duplicate removal without creating a completeness or semantic-audit claim.",
        "Focused health, checker census, manifest check, aggregate adversarial, full runtime-config aggregate, framework, sequence, navigation, agent-surface, py_compile, and exact diff checks pass with fresh independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 validation-health fixture/schema/checker correspondence only; any workflow, build input, generated/compiled source, or runtime delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused health-schema branch if exact current state cannot be represented without duplicate authority or manifest reclassification; never restore acceptance of contradictory or unknown health fields.",
      "status_documentation_updates": "Record GP-VAL-009 as Done only after exact reviewed integration; document schema v3 and retain all manifest completeness, product/runtime, artifact, and hardware non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "9c0324969a2adbe7d13e611e2f636df6fab4d690",
        "reviewed_implementation_sha": "f466ac50e23ff62ecc0825de44501b30a8f0e23b",
        "prior_canonical_integration_sha": "f466ac50e23ff62ecc0825de44501b30a8f0e23b",
        "reviewed_changed_paths": [
          "docs/agent_framework/SUBAGENT_CONTRACTS.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_runtime_config_validation_health.py"
        ],
        "independent_review_provenance": "Fresh independent reviewer initially required repair for current result/census/manifest path correspondence; repaired-scope review PASS confirmed exact schema, source bindings, adversarial coverage, and forbidden-scope invariants on f466ac50e23ff62ecc0825de44501b30a8f0e23b.",
        "validation_provenance": "Focused health, census, manifest, aggregate adversarial, full 28-check runtime-config aggregate, framework, sequence, navigation, docs-agent-surface, py_compile, and diff checks passed on the exact integrated snapshot; no build or hardware was required."
      },
      "stop_conditions": [
        "Any manifest entry, exclusion, applicability, branch policy, command, dependency, reason, load-bearing classification, or checker product semantic must change.",
        "Any second exclusion authority or schema ambiguity remains accepted.",
        "Any workflow, build, product/runtime source, generator, artifact, device, persistence, WebSerial/protobuf write, flashing, hardware, Nunchuk, root-cause, or game-semantic scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-005",
      "title": "Make advertised offline packaging modes load-bearing",
      "status": "DONE",
      "branch": "glyph/gp-val-005-offline-packaging-load-bearing-20260830",
      "objective": "Make the existing offline pipeline, artifact-bundle-manifest, and export-package validators execute through the canonical no-argument coordinate-native checker route and prove that each layer ran.",
      "why_this_matters": "Current docs advertise all three offline packaging modes and each explicit flag passes, but the single current manifest entry invokes only the no-argument checker path, which omits those validators. The aggregate can therefore pass while advertised packaging coverage never runs.",
      "hardware_risk": "H0",
      "behavioral_claim": "This strengthens offline checker coverage only. It changes no coordinate/profile semantics, generated artifact bytes, manifest applicability or count, firmware/runtime source, active publication, device path, or controller behavior.",
      "scope": "Update tools/check_glyph_coordinate_native_runtime_profile_contract.py and only its in-memory or isolated-temporary adversarial coverage plus deterministic checker-census consequences. Preserve every explicit flag route. On the no-argument path, validate the offline pipeline, offline artifact bundle manifest, and offline export package through the existing validators; record an ordered execution trace only after successful validation; require exactly offline_pipeline, offline_artifact_bundle_manifest, offline_export_package; and emit that exact trace as the final aggregate-captured sentinel. Keep the existing single coordinate_native_contract manifest entry, required_arguments empty, runner argument policy, entry count, applicability, and source authority unchanged.",
      "explicit_excluded_scope": "No new manifest entry or fixed-flag runner policy; no general dependency-metadata contract; no fixture semantic redesign; no real artifact, vendor export, runtime-loaded profile, persistent storage, WebSerial/device write, protobuf write, flashing, active source/publication, firmware build, hardware result, Nunchuk claim, root-cause claim, or gameplay-semantic claim.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "Live configurator b81c299e1449fc319788a35763b71d3e73d906f1. tools/check_glyph_coordinate_native_runtime_profile_contract.py blob 7ea68a278c310e8bc9525c82d792947b9ddc95c5 implements all three explicit validators, and each explicit command independently passes. docs/runtime_config/fixtures/runtime_config_validation_manifest.json has one current coordinate_native_contract entry with command python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py and empty required_arguments. Direct source inspection shows the default path validates contract/schema, examples, dry-run fixtures, and layout bridge but does not call the three advertised packaging validators. The checker and runner are unchanged from packet base 8c04262c66613d46b933b1b739c01c575cb0c580.",
      "dependencies_prerequisites": [
        "The three explicit mode commands, their current fixtures, and the single no-argument manifest entry remain present and passing at implementation start.",
        "The implementation keeps the manifest entry count/applicability and tools/run_glyph_runtime_config_validation.py argument policy unchanged, so GP-VAL-003 completion is not a prerequisite.",
        "All tests remain offline and use only checked-in or isolated temporary fixture bytes."
      ],
      "substantive_authorization_rationale": "The coverage gap and all validators are already source-proven. Expanding the existing no-argument contract is the smallest architecture: it avoids a new runner argument policy and count churn while an exact ordered trace plus mode-specific adversarial drift prevents silent early-return or omitted-layer coverage. No product, profile, export, device, or runtime decision remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Any explicit mode, fixture schema, no-argument manifest route, or coordinate-native checker architecture materially changes before implementation.",
        "The implementation would require a new manifest entry, runner required-argument policy, fixture semantic choice, or product/runtime behavior change.",
        "An equivalent or stronger default-route execution trace and adversarial gate becomes canonical first."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of Planner candidate GP-VAL-005 from planning/portfolio-20260827-1210 commit ae1d15b9a7941934b26d4371b0ea0e10691629cb, packet base 8c04262c66613d46b933b1b739c01c575cb0c580, with bounded specialist verification of all explicit modes and the default-route omission against live configurator b81c299e1449fc319788a35763b71d3e73d906f1 on curation/portfolio-20260830-0211-review.",
      "automated_validation": [
        "The no-argument checker succeeds only after the exact ordered trace offline_pipeline, offline_artifact_bundle_manifest, offline_export_package is complete and prints that trace in the final aggregate-captured sentinel.",
        "Removing, reordering, short-circuiting, or falsely pre-recording any layer fails; malformed pipeline input, bundle manifest, and export package each fail independently for their intended reason using in-memory or isolated temporary data.",
        "Every explicit flag route retains its current result and output contract; the current single manifest entry, required_arguments, applicability, and counts are byte-unchanged.",
        "Coordinate-native contract, checker census, validation health, full runtime-config aggregate, framework, sequence, navigation, and agent-surface checks pass with independent repaired-scope review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 offline checker and deterministic census metadata only; any product, generated semantic, compiled source, or build-input delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused checker branch if a valid explicit mode or default contract regresses; never restore aggregate success that omits an advertised packaging layer.",
      "status_documentation_updates": "Record the three existing offline packaging validators as load-bearing through the one default coordinate-native checker route without creating a production export, artifact, runtime, or hardware claim.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "e41e4ea1017b5abde4f17eed1a4bc50404238c75",
        "reviewed_implementation_sha": "7a042fbdd1dc28db8efbd7c59e1730565fe33288",
        "prior_canonical_integration_sha": "7a042fbdd1dc28db8efbd7c59e1730565fe33288",
        "reviewed_changed_paths": [
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_coordinate_native_runtime_profile_contract.py"
        ],
        "independent_review_provenance": "Fresh independent reviewer PASS on exact feature tip 7a042fbdd1dc28db8efbd7c59e1730565fe33288; specialist follow-up repaired explicit pre-recording and short-circuit assertions, followed by repaired-scope review PASS with no findings.",
        "validation_provenance": "Focused explicit/default packaging routes, census freshness, aggregate adversarial checks, validation health, full runtime-config aggregate, framework, sequence, navigation, docs-agent-surface, py_compile, and diff checks passed on the exact integrated snapshot; no build or hardware was required."
      },
      "stop_conditions": [
        "Any profile, package, artifact, export, or active behavior semantics must be chosen or changed.",
        "Any manifest argument-policy or dependency-contract change is required.",
        "Any runtime-loaded config, persistence, device/protobuf write, flashing, build, hardware, Nunchuk, or root-cause scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-006",
      "title": "Census declared effective non-selector build configuration",
      "status": "DONE",
      "branch": "glyph/gp-prov-006-non-selector-config-census-20260830",
      "objective": "Create a deterministic exact-source census of the declared literal non-selector configuration reached by glyph_mk6, including its finite inheritance/reference order, while preserving unresolved runtime interpolation and making no PlatformIO, compiler, or behavior-effect claim.",
      "why_this_matters": "GP-PROV-003 intentionally inventories selectors and excludes build flags, unflags, literal environment settings, non-path nanopb options, and their ordering. No current load-bearing record detects drift in those declared inputs, while complete effective build and reproducibility claims remain unsupported.",
      "hardware_risk": "H0",
      "behavioral_claim": "This adds static provenance documentation, a fixture, and a read-only checker only. It does not change or execute build configuration, resolve PlatformIO/compiler behavior, install dependencies, build firmware, process or accept an artifact, or change runtime/configurator behavior.",
      "scope": "Add docs/runtime_config/build_input_non_selector_configuration.md, docs/runtime_config/fixtures/build_input_non_selector_configuration.json, and tools/check_glyph_build_input_non_selector_configuration.py, then add one current manifest entry with direct dependencies platformio.ini and config/glyph/env.ini and regenerate only deterministic census/health consequences. Use status declared_effective_literal_census_not_platformio_or_compiler_resolution. Bind exactly source blobs 4d56f8630c1b12e84cd12f40ce05a4dc71b9362e and fac4e20461ad632ca1d65826241a4a9c73630f04, the source-declared chain [env], arduino_pico_base, glyph_base, env:glyph_mk6, scalar keys build_type, lib_ldf_mode, debug_tool, monitor_speed, board_build.f_cpu, board_build.filesystem_size, lib_archive, and upload_protocol, ordered-list keys build_flags and build_unflags, and only the non-path custom_nanopb_options token --error-on-unmatched. Preserve declaring path, section, key, raw literal line, order, inheritance/shadow origin, and explicit ${section.option} list-reference expansion order. Preserve ${PIOENV} and ${platformio.name} as unresolved source-labelled runtime interpolation tokens. Record literal token shapes only, never macro, compiler, protocol, board, or behavior effects.",
      "explicit_excluded_scope": "No PlatformIO invocation or claim of exact PlatformIO evaluation; no compiler/preprocessor invocation; no dependency/cache resolution; no source selector, platform, framework, board/core, package, library, ignore, script, source-filter, proto-path, options-file, extends/default-env, workflow, pin, flag, frequency, filesystem, upload, or build-input mutation; no complete configuration/dependency closure, reproducibility, artifact, device, firmware/runtime, Nunchuk, root-cause, or gameplay claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator b81c299e1449fc319788a35763b71d3e73d906f1. platformio.ini has blob 4d56f8630c1b12e84cd12f40ce05a4dc71b9362e and SHA-256 99fc26f84f4cf2c118d08fde7269a13b9b37f6ed1efb2d32291ba9f0b8e780e9; config/glyph/env.ini has blob fac4e20461ad632ca1d65826241a4a9c73630f04 and SHA-256 c754c2f504c8740763d3f65fa114cc61c21fe5d73bd489c728610c1299d1fccf. Their declared chain and values are unchanged from the Planner packet base. Canonical GP-PROV-003 explicitly excludes build_flags values, macro meanings, optimization flags, non-path custom_nanopb_options flags, board behavior, and include-path semantics; repaired GP-PROV-004 is DONE and supplies the accepted exact-source correspondence pattern.",
      "dependencies_prerequisites": [
        "GP-PROV-003 and repaired GP-PROV-004 remain canonically DONE with their selector and correspondence non-claims intact.",
        "The two exact INI blobs, declared section chain, in-scope key set, and GP-PROV-003 selector boundary remain unchanged at implementation start.",
        "Implementation uses Python standard-library static parsing only and does not invoke PlatformIO, a compiler, a build script, a dependency, or the network."
      ],
      "substantive_authorization_rationale": "The remaining provenance gap is directly source-proven and the contract is finite. Exact key lists, source identities, source-declared inheritance/reference order, and explicit unresolved interpolation prevent the implementer from inventing PlatformIO or compiler semantics. The work records declared literals and their provenance without choosing or changing any value, so no product, device, workflow, or gameplay judgment remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Either exact INI blob, in-scope key, declared chain/reference, or GP-PROV-003 selector boundary drifts before implementation.",
        "The census would need PlatformIO/compiler execution, dependency/cache inspection, dynamic environment resolution, or effect interpretation to complete.",
        "Another canonical change supplies an equivalent or stronger exact-source non-selector census first.",
        "A source value, selector, workflow, build input, product/runtime file, or artifact would be changed rather than only inventoried."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of Planner candidate GP-PROV-006 from planning/portfolio-20260827-1210 commit ae1d15b9a7941934b26d4371b0ea0e10691629cb, packet base 8c04262c66613d46b933b1b739c01c575cb0c580, after repaired GP-PROV-004 completion and bounded specialist verification of the exact current INI sources and contract against live configurator b81c299e1449fc319788a35763b71d3e73d906f1 on curation/portfolio-20260830-0211-review.",
      "automated_validation": [
        "The fixture contains every and only authorized scalar, ordered-list, and non-path nanopb literal with exact source path/blob, section/key, raw line, declaration order, inheritance/shadow origin, and explicit reference-expansion order.",
        "Wrong chain/order/source/blob, omitted/invented/duplicate/shadowed key, changed token, selector overlap, unresolved-placeholder promotion, escaping/missing/untracked/symlink dependency, and either INI drift fail closed.",
        "${PIOENV} and ${platformio.name} remain explicit unresolved runtime interpolation tokens and no macro, compiler, board, protocol, device, artifact, or reproducibility effect is asserted.",
        "Focused checker, GP-PROV-003 inventory, GP-PROV-004 observations, checker census, validation health, full runtime-config aggregate, framework, sequence, navigation, and agent-surface checks pass with independent review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 static declaration census and offline checker only; any build-input or product/runtime mutation stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the focused census if exact source/reference correspondence cannot be enforced without evaluating effects; retain every existing build input and all unresolved dependency/reproducibility claims.",
      "status_documentation_updates": "Record only a declared literal non-selector census and its current validation entry; keep complete configuration, PlatformIO/compiler resolution, reproducibility, artifact acceptance, and hardware explicitly unproved.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "0086b388cd230b65e3b9dee0be2e69600b3ae3a0",
        "reviewed_implementation_sha": "26e3ca148df4de6fb9c10806f97204cc17164f52",
        "prior_canonical_integration_sha": "26e3ca148df4de6fb9c10806f97204cc17164f52",
        "reviewed_changed_paths": [
          "docs/agent_framework/SUBAGENT_CONTRACTS.md",
          "docs/runtime_config/build_input_non_selector_configuration.md",
          "docs/runtime_config/fixtures/build_input_non_selector_configuration.json",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_health.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_build_input_non_selector_configuration.py",
          "tools/check_glyph_runtime_config_validation_health.py"
        ],
        "independent_review_provenance": "Fresh repaired-scope independent reviewer PASS on exact feature tip 26e3ca148df4de6fb9c10806f97204cc17164f52 after prior findings were repaired; source reference expansions, chain_references schema, parser-backed correspondence, non-claims, and manifest/census/health consistency passed.",
        "validation_provenance": "Focused census, checker census, validation health, aggregate adversarial, full runtime-config runner, framework, sequence, navigation, docs-agent-surface, py_compile, and diff checks passed; no build or hardware was required."
      },
      "stop_conditions": [
        "Any PlatformIO/compiler behavior, macro effect, source selection, build result, or device meaning would be inferred.",
        "Any dependency, cache, workflow, source, flag, board, frequency, filesystem, upload, or build input would be changed or executed.",
        "Any firmware/runtime, artifact, device-write, persistence, protobuf-write, flashing, hardware, Nunchuk, root-cause, or game-semantic scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-007",
      "title": "Enforce bounded validation-manifest dependency metadata",
      "status": "DONE",
      "branch": "glyph/gp-val-007-manifest-dependency-metadata-20260830",
      "objective": "Define and enforce a bounded truthful contract for validation-manifest source_dependencies and branch_policy without claiming complete transitive or semantic dependency closure.",
      "why_this_matters": "The runner requires both fields but validates neither field's contents. On current source, 19 manifest entries have empty dependency lists and static inspection finds 26 missing direct tracked helper-import edges across 18 entries, so the described dependency graph can drift while the manifest check passes.",
      "hardware_risk": "H0",
      "behavioral_claim": "This strengthens offline validation metadata and adversarial schema checks only. It does not change checker product semantics, execute discovered code during metadata discovery, change branch behavior, build firmware, or alter runtime/configurator behavior.",
      "scope": "Upgrade the runtime-config validation manifest to schema version 4; update tools/run_glyph_runtime_config_validation.py, the existing aggregate adversarial checker, manifest docs, current entry metadata, and only deterministic census/health consequences. Define source_dependencies as an ordered duplicate-free list of normalized repository-relative POSIX paths to existing stage-0 tracked regular non-symlink files inside the repository; the entry checker path is implicit and not repeated. Static AST inspection, without import or execution, must require every direct absolute local single-module Import or level-zero ImportFrom resolving exactly to a tracked tools/<module>.py file to appear. Curated additional direct tracked inputs may remain and receive the same path validation. Explicitly exclude transitive imports, dynamic/importlib imports, subprocess targets, runtime data reads, generated files, external/standard-library modules, and complete semantic closure. Define branch_policy exactly as content_only, content_and_scope, named_evidence_branch, or not_run, with current entries using content_only/content_and_scope, historical_only using named_evidence_branch, and unsafe_or_mutating using not_run. Treat policy as curated classification metadata, not proof of checker-internal branch semantics or a new runner branch gate.",
      "explicit_excluded_scope": "No complete semantic/transitive dependency claim; no dynamic import, subprocess, runtime-data, or generated-file discovery; no arbitrary code execution or import; no branch-policy reclassification; no tools/glyph_checker_context.py change; no current checker applicability change except separately authorized work; no product/runtime checker semantic change, network, workflow, firmware source, build, artifact, device, persistence, protobuf write, flashing, hardware, Nunchuk, root-cause, or gameplay claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator b81c299e1449fc319788a35763b71d3e73d906f1. tools/run_glyph_runtime_config_validation.py blob 8a760901f78e666f862269e62fb36c9cbebf1e93 requires field presence but does not validate source_dependencies contents or branch_policy. Current manifest blob 63c0740f4a298b34b7880b56f7ced37d27cdce3c passes with 31 entries and 37 strong-signal exclusions; 19 entries have empty dependencies. Independent read-only AST census found 26 missing direct tracked helper edges across 18 entries. The current exact policy matrix is 19 current/content_only, 7 current/content_and_scope, 4 historical_only/named_evidence_branch, and 1 unsafe_or_mutating/not_run, with no reclassification required.",
      "dependencies_prerequisites": [
        "The current runner, aggregate adversarial checker, manifest entry set, tracked checker AST set, and four-value branch-policy matrix are freshly inspected before implementation.",
        "Any prior Ready work landing first is permitted only as a separately reviewed mechanical entry/checker/census/health delta that is re-read under this generic contract.",
        "Static discovery never imports or executes a checker, helper, workflow, subprocess target, or generated file."
      ],
      "substantive_authorization_rationale": "The gap is directly reproduced and the exact bounded meaning is now resolved: source_dependencies is a validated set of direct tracked inputs with a mechanically required local-helper lower bound, not a claim of completeness; branch_policy is a finite applicability-consistent classification, not runtime enforcement. This strengthens truthful metadata without choosing product behavior, branch policy, or semantic dependency meaning outside current authority.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The manifest schema, runner topology, tracked checker import shapes, applicability vocabulary, or branch-policy matrix materially changes before implementation.",
        "The work would require complete semantic/transitive dependency truth, dynamic execution, import of discovered code, or branch behavior enforcement.",
        "A current entry cannot be represented truthfully under the bounded direct-helper lower-bound contract without substantive reclassification.",
        "Another canonical change supplies an equivalent or stronger bounded metadata contract first."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of Planner candidate GP-VAL-007 from planning/portfolio-20260827-1210 commit ae1d15b9a7941934b26d4371b0ea0e10691629cb, packet base 8c04262c66613d46b933b1b739c01c575cb0c580, with bounded specialist verification of the 31-entry manifest, direct-helper gaps, and exact policy matrix against live configurator b81c299e1449fc319788a35763b71d3e73d906f1 on curation/portfolio-20260830-0211-review.",
      "automated_validation": [
        "Absolute, empty, dot, dot-dot, backslash, non-normalized, escaping, missing, untracked, directory, duplicate, checker-self, and symlink dependency paths fail; normalized tracked stage-0 regular direct inputs pass in exact order.",
        "Every direct absolute local single-module Import or level-zero ImportFrom resolving to tracked tools/<module>.py is required; missing helper edges fail, while transitive, dynamic/importlib, subprocess, runtime-data, generated, external, and standard-library exclusions remain explicit and tested.",
        "Unknown branch policies and every invalid applicability/policy pair fail; the current matrix passes without reclassification and creates no claim that checker-internal branch semantics were proved.",
        "A zero-import/zero-execution sentinel proves discovery uses AST/static tracked metadata only; manually curated additional direct tracked inputs remain accepted after path validation.",
        "Manifest, aggregate adversarial, checker census, validation health, full runtime-config aggregate, framework, sequence, navigation, and agent-surface checks pass with independent metadata-contract review."
      ],
      "canonical_build": "NOT_REQUIRED: H0 manifest/schema/runner metadata validation only; any checker product semantic, build input, compiled source, or runtime delta stops.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused metadata-contract branch if current valid entries cannot be represented without overclaiming completeness; never restore acceptance of malformed paths, missing direct helper edges, or invalid policy pairs.",
      "status_documentation_updates": "Document manifest v4's bounded direct-input/helper lower bound and branch-policy classification matrix with explicit dynamic, transitive, semantic, and enforcement non-claims.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "a49117062282efc077417143c325cae3c55bff4e",
        "reviewed_implementation_sha": "e8ab9b86408d1c89f3b35a07949782d9e3c414ff",
        "prior_canonical_integration_sha": "e8ab9b86408d1c89f3b35a07949782d9e3c414ff",
        "reviewed_changed_paths": [
          "docs/agent_framework/SUBAGENT_CONTRACTS.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
          "docs/runtime_config/runtime_config_validation_health.md",
          "tools/check_glyph_runtime_config_validation_aggregate.py",
          "tools/run_glyph_runtime_config_validation.py"
        ],
        "independent_review_provenance": "Fresh independent validator review PASS on exact repaired feature tip e8ab9b86408d1c89f3b35a07949782d9e3c414ff; prior policy reclassification finding was repaired and direct dependency path adversarial coverage was expanded.",
        "validation_provenance": "Manifest schema-v4 check, aggregate adversarial suite, 194-entry census, validation health, full 27-check runtime-config aggregate, framework, sequence, navigation, docs-agent-surface, py_compile, and diff checks passed on the exact integrated snapshot; no firmware build or hardware was required."
      },
      "stop_conditions": [
        "Any complete dependency graph, dynamic behavior, or checker branch semantics would be inferred.",
        "Any discovered code must be imported or executed, or tools/glyph_checker_context.py must change.",
        "Any checker applicability, product/runtime semantics, workflow, firmware, build, artifact, device, or hardware behavior would change."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-005",
      "title": "Apply isolated-output policy to remaining writers",
      "status": "DONE",
      "branch": "glyph/gp-src-005-isolated-writers-20260824",
      "objective": "Apply the canonically integrated shared isolated-output policy and shared atomic-write implementation to remaining offline writer paths while preserving stdout and one exact inert example install target.",
      "why_this_matters": "The legacy source-owned generator currently accepts .git/config, AGENTS.md, case/inode aliases of the active baseline, and non-atomic writes; the coordinate-native bridge accepts arbitrary repository or absolute output paths. GP-SRC-003 established the exact isolated-output policy and atomic implementation, which should now govern these writers without broadening repository write authority.",
      "hardware_risk": "H1",
      "behavioral_claim": "This work changes host-side output-path and atomic-write safety only. It must not change generated semantic content, active table bytes, firmware/runtime behavior, profile intent, or the approved publication path.",
      "scope": "Reuse GP-SRC-003's exact shared lexical-system-temp-root, canonical-resolution, case, alias, symlink, input-overwrite, active-publication-name, and atomic-write policy for generic generate_source_owned_runtime_config.py outputs and convert_coordinate_native_profile_to_source_owned_spec.py --output. Preserve stdout as non-mutating. Keep --install-inert-source-artifact only as a separate exact exception for src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigArtifact.example.hpp; reject every other repository target, including the active baseline and case/inode aliases. To make that exact exception atomic without weakening the isolated-output validator, add one internal _atomic_replace_validated_text(target: Path, text: str, *, purpose: str) -> None helper in tools/source_owned_generator_modes.py; existing _atomic_write_text must continue to validate through validate_offline_output_target and then delegate to it, while the inert install path may call it only after exact inert-target validation. A static call-site check must permit the low-level helper only from _atomic_write_text and the exact inert exception. Do not duplicate or weaken target policy or atomic implementation.",
      "explicit_excluded_scope": "No prepared-v2 packet/validation semantic change, source-authority-intake root policy, additional low-level atomic call site, active/compiled source write, table bytes, profile semantics, production ownership, runtime loading, persistence, WebSerial/device write, protobuf write, flashing, Nunchuk, root cause, build, candidate, or hardware action.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "On live configurator 26b939fa3d3664e839cab8076eea60ddb0f67e9f, GP-SRC-003 is DONE and tools/source_owned_generator_modes.py exports the shared validate_offline_output_target(target: Path, *, purpose: str) -> Path and _atomic_write_text(target: Path, text: str, *, purpose: str) -> None policy. Fresh non-mutating follow-up probes still show generate_source_owned_runtime_config.assert_safe_output_path accepts .git/config and AGENTS.md, while a mocked convert_coordinate_native_profile_to_source_owned_spec.convert_profile_file reaches Path.write_text for AGENTS.md. GP-SRC-004 changed only current-baseline classification emission in the legacy generator after the prior snapshot; its independent review, exact table/symbol digests, and build prove that drift did not change either writer's output-path behavior, generated semantic content, or active publication.",
      "dependencies_prerequisites": [
        "GP-SRC-003 is canonically DONE on live configurator with prepared schema v2, one stable shared isolated-output validator, and one atomic writer that currently always applies that validator.",
        "GP-SRC-004 is canonically DONE; its exact reviewed delta to tools/generate_source_owned_runtime_config.py is limited to active-current-baseline versus inert-example classification emission, and all 28 table values/symbols plus active RuntimeConfigView publication remain unchanged.",
        "The exact inert example and active baseline paths remain src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigArtifact.example.hpp and src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp with their current classifications.",
        "Fresh non-mutating probes reproduce acceptance of repository targets in both remaining writer paths before the successor change."
      ],
      "substantive_authorization_rationale": "The prior exact-snapshot Preauthorization invalidated when GP-SRC-004 changed a named writer, so it was not silently activated. Follow-up Curator review resolved that drift from source, independent review, table/symbol digests, and build evidence as classification-only and unrelated to output safety. The unsafe writer behavior remains directly reproducible and the target decision is exact: generic file outputs use the shared isolated temporary policy, while the only repository exception is the established inert example artifact. Because the existing atomic writer always invokes the isolated-output validator and therefore cannot serve that exception, one shared low-level atomic helper with an exact two-call-site invariant resolves atomicity without relaxing either target validator. No product, profile, ownership, game-semantic, or broader repository-write judgment remains.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The two existing shared functions/signatures are absent or their isolated-output, alias, symlink, input-overwrite, active-publication-name, atomicity, or portability semantics change before implementation.",
        "A command-specific durable output requirement or additional repository install target is proposed.",
        "Either named writer differs materially from live authorization base 26b939fa3d3664e839cab8076eea60ddb0f67e9f before implementation, either exact target path/classification changes, or non-mutating probes no longer reproduce the gap.",
        "Implementation would touch compiled/active source, table bytes, profile intent, production ownership, or a forbidden runtime/device boundary."
      ],
      "authorization_snapshot_provenance": "Fresh substantive reauthorization of Planner branch planning/portfolio-20260823-2349 candidate GP-SRC-005, packet commit 387a2a7b27d11b81c3c571aaf07cf543af626757 and packet base 6b8ebcd404dcbfe9b579eed41fb35b889e9da598, after the prior Preauthorization mechanically invalidated. Curator reproduced the gaps and reviewed the exact intervening GP-SRC-004 classification-only delta against live configurator 26b939fa3d3664e839cab8076eea60ddb0f67e9f on curation/portfolio-20260824-1355-followup.",
      "automated_validation": [
        "Generic legacy-generator and coordinate-bridge outputs reject relative paths, every repository path, .git, non-temporary roots, traversal, input overwrite, case/inode aliases, symlinks, active-header aliases, and active-publication-like names.",
        "Safe isolated absolute outputs validate through validate_offline_output_target and use the shared atomic implementation; failure leaves no partial target; stdout remains byte-deterministic and non-mutating.",
        "The exact inert install exception accepts only GeneratedRuntimeConfigArtifact.example.hpp, validates that exact target before invoking the shared low-level atomic helper, and rejects every other repository/source target and alias.",
        "Static call-site census permits _atomic_replace_validated_text only from _atomic_write_text and the exact inert-install branch; direct or additional call sites fail.",
        "Generated semantic output before/after is identical for accepted stdout, isolated output, and inert example cases; repository and active-table digests are unchanged.",
        "Legacy generator, coordinate-native bridge/contract, source sync, checker census, full runtime-config aggregate, and docs-navigation checks pass."
      ],
      "canonical_build": "NOT_REQUIRED when compiled source and active table bytes remain unchanged; any such delta stops and requires fresh risk authorization.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused host-tool branch if valid isolated or exact inert-example output regresses; do not restore arbitrary repository writes or duplicate the shared policy.",
      "status_documentation_updates": "Document shared isolated output plus the one exact inert-example exception without creating production authority, active source, a firmware candidate, or hardware claim.",
      "done_evidence": "Implementation commit a04e995c1fadc1f8d403c88cea147fb8f99f8939; independent writer-safety review PASS; complete path/alias/inode/symlink/atomicity corpus; semantic output and active-source digests unchanged; current aggregate/navigation PASS; canonical integration pending publication.",
      "stop_conditions": [
        "Any new durable output root or repository install target requires judgment.",
        "The shared policy cannot be reused exactly without weakening or duplication.",
        "Any active/compiled source, firmware behavior, profile authority, runtime loading, persistence, device/protobuf write, flashing, or hardware scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-002",
      "title": "Emit observed-only CI artifact sidecar",
      "status": "DONE",
      "branch": "glyph/gp-prov-002-observed-ci-sidecar-20260824",
      "objective": "Make the canonically gated build.yml artifact route emit and verify a sidecar carrying the full source Git identity and exact final postprocessed artifact identity.",
      "why_this_matters": "The current route uploads a postprocessed UF2 named with only a short SHA and no full candidate SHA, final size/SHA-256, or postprocessor identity sidecar, so consumers cannot establish even bounded observed correspondence from the uploaded directory.",
      "hardware_risk": "H1",
      "behavioral_claim": "This work changes CI artifact metadata and fail-closed publication ordering only. It does not change firmware source or build inputs, assign a purpose or byte effect to glyph_nuker, establish immutable storage or artifact acceptance, update a device, flash firmware, or claim hardware PASS.",
      "scope": "Extend the existing observed-only provenance tool and synthetic contract so .github/workflows/build.yml first requires the full lowercase GITHUB_SHA to equal git rev-parse HEAD for the checked-out source before build, and verifies the tracked glyph_nuker bytes equal SHA-256 8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae before its existing postprocessing step. After postprocessing, emit and verify one deterministic JSON sidecar beside each final UF2 before upload. The sidecar must bind that verified full checked-out Git SHA, final artifact filename, byte size and SHA-256, tracked postprocessor path and SHA-256, status observed_only_no_artifact_acceptance, purpose UNKNOWN, byte_transformation UNKNOWN, source classification observed_only, workflow source .github/workflows/build.yml, artifact_store_established false, and immutable_locator null. Build and upload must remain unreachable on source-identity mismatch; upload must remain unreachable when the postprocessor preflight, sidecar generation, or sidecar verification fails; and the verified sidecar must be included in the existing Glyph_FW upload directory.",
      "explicit_excluded_scope": "No change to build-device-config.yml or any unresolved caller/owner/release route; no dependency/action pin, PlatformIO input, firmware source, postprocessor binary, postprocessor invocation semantics, artifact store/retention, release, locator, reproducibility, artifact acceptance, device/protobuf write, persistence, flashing, hardware result, Nunchuk, root-cause, or product/game-semantic change or claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "On live configurator 26b939fa3d3664e839cab8076eea60ddb0f67e9f, .github/workflows/build.yml is the bounded CURRENT_GATED route and still derives only SHA_SHORT, postprocesses the copied UF2 with the tracked glyph_nuker, and uploads the directory without a sidecar. tools/check_glyph_artifact_postprocessor_provenance.py and its fixture already define and pass the synthetic observed-only schema while explicitly leaving purpose, byte transformation, and immutable locator unresolved. The tracked glyph_nuker SHA-256 remains 8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae. GP-VAL-003 separately classifies build-device-config.yml UNRESOLVED_EXTERNAL, so this work cannot overclaim or remediate that route.",
      "dependencies_prerequisites": [
        "GP-PROV-001 and GP-VAL-002 are DONE, and the prior GP-VAL-003 route census remains canonical while its health-prose correspondence identity is reopened; their observed-only non-claims, validation-before-publication gate, and complete tracked-route classification remain intact.",
        "Implementation starts from a fresh descendant of live configurator 26b939fa3d3664e839cab8076eea60ddb0f67e9f and limits workflow mutation to the current build.yml route.",
        "The tracked glyph_nuker path and SHA-256 remain exact; a changed binary stops rather than being reclassified or accepted.",
        "GP-VAL-004 completed as a separate checker repair and was not absorbed into GP-PROV-002."
      ],
      "substantive_authorization_rationale": "The missing correspondence is directly observable and the accepted schema already fixes every sensitive claim: full source identity, exact observed final bytes, exact tracked postprocessor identity, and explicit UNKNOWN/null fields. Adding a pre-execution identity gate plus postprocessing sidecar generation and verification does not select a store, interpret the binary, change firmware inputs, or convert CI output into a hardware-accepted artifact.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The build.yml postprocess/upload route, tracked glyph_nuker bytes, current validation dependency, or observed-only provenance schema materially changes before implementation.",
        "Implementation would touch build-device-config.yml, select an unresolved caller/owner/store/release policy, or claim an immutable locator, reproducibility, artifact acceptance, postprocessor purpose/effect, or hardware evidence.",
        "Any firmware source, dependency, build input, postprocessor binary, device-update, flashing, runtime-loaded config, persistence, or product behavior would change."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-2349 candidate GP-PROV-002, packet commit 387a2a7b27d11b81c3c571aaf07cf543af626757 and packet base 6b8ebcd404dcbfe9b579eed41fb35b889e9da598, independently reproduced against live configurator 26b939fa3d3664e839cab8076eea60ddb0f67e9f and authorized on curation/portfolio-20260824-1355-followup.",
      "automated_validation": [
        "Synthetic generation and verification pass only when the full lowercase workflow SHA equals the exact checked-out Git HEAD and the record carries that identity plus exact final filename/size/SHA-256, exact tracked postprocessor identity, observed-only classification, UNKNOWN purpose/effect, false artifact-store flag, and null immutable locator.",
        "Short/malformed or HEAD-mismatched source SHA, pre-versus-postprocessed hash confusion, missing/changed postprocessor identity, wrong file/size/hash, non-UNKNOWN purpose/effect, non-null locator, false acceptance/store claim, malformed/extra/missing field, and sidecar tampering fail closed.",
        "Focused static workflow cases prove checked-out HEAD equality gates build, postprocessor identity verification occurs before postprocessing, sidecar generation and verification occur after postprocessing and before upload, failure blocks publication, the verified sidecar is included, and no alternate build.yml publication route bypasses the gate.",
        "The exact build.yml validation dependency remains intact; build-device-config.yml bytes and classification remain unchanged.",
        "Artifact-provenance, CI publication-route census, validation-publication workflow, checker census, full runtime-config aggregate, agent-framework, docs-navigation, and docs-agent-surface checks pass; no tool test executes glyph_nuker, builds firmware, uploads bytes, or accesses a device."
      ],
      "canonical_build": "NOT_REQUIRED: workflow metadata generation/static gating and host-side provenance tooling only; no firmware source or build input changes are authorized.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused workflow/provenance branch if valid current artifacts cannot produce a deterministic verified observed-only sidecar; do not bypass failed identity or sidecar checks and do not infer missing provenance.",
      "status_documentation_updates": "Document the bounded build.yml observed-only sidecar and retain explicit non-claims for immutable storage, artifact acceptance, reproducibility, postprocessor purpose/effect, hardware, and every unresolved external route.",
      "done_evidence": "Implementation commits a09ba09d35621b3742ee37f961c012f542ce64c0, 3810732a0daa3d4c771d205da5b76d8f7a63dbf4, and repaired completion commit 9c94b5449b8065cb02aa0689ca0564720238b80c are integrated into configurator by recovery merge 4859c94c038125f42da6771ad5f1a0396df2333c; independent review and the exact sidecar/workflow/tamper/full-validation corpus passed. No firmware/build input, glyph_nuker bytes, build-device-config.yml, upload execution, artifact acceptance, storage, hardware, device, or runtime behavior changed or is claimed.",
      "stop_conditions": [
        "The tracked postprocessor identity differs or its purpose/effect must be interpreted.",
        "A durable locator, store, retention, caller, owner, release, reproducibility, artifact-acceptance, or hardware decision is required.",
        "Any firmware source/build input, postprocessor binary or semantics, build execution, upload execution, device write, flashing, runtime loading, persistence, Nunchuk, or root-cause scope appears."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-HW-001",
      "title": "Enforce hardware evidence-record correspondence",
      "status": "DONE",
      "branch": "agent-framework-hardware-evidence-correspondence",
      "objective": "Make every Revision-2 H2/H3 result-bearing queue state resolve and validate a structured evidence record for the exact candidate, artifact, locator, protocol, result, and evidence gaps.",
      "why_this_matters": "The current framework accepts HARDWARE_VALIDATED and other result states when hardware_evidence_record is any nonempty string, including a nonexistent path, so exact-snapshot acceptance can fail open despite the manual hardware contract.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work strengthens control-plane validation only. It performs no hardware action, creates no PASS, retrieves or executes no firmware artifact, and changes no firmware or configurator product behavior.",
      "scope": "Define an exact flat JSON Revision-2 hardware-result record and cross-validate it from tools/check_glyph_agent_framework_docs.py for HARDWARE_VALIDATED, HARDWARE_FAILED, and result-bearing LOCAL_ACCEPTANCE_PENDING states. Its exact key set is schema_name, schema_version, work_order_id, candidate_branch, candidate_git_sha, candidate_base_configurator_sha, firmware_artifact_filename, firmware_artifact_build_path, firmware_artifact_sha256, preserved_firmware_artifact_locator, pre_update_sha256_verified, controller_model_revision, firmware_profile_state, update_method, host_platform_adapter, evidence_contract_reference, evidence_contract_version, candidate_protocol_reference, candidate_protocol_version, preconditions, steps, negative_regression_checks, power_cycle_reconnect_checks, result, anomalies, rollback_recovery, tester, tested_at, and evidence_gaps. schema_name is exact string glyph_hardware_evidence_record and schema_version is exact integer 2. The identity/context/protocol/result/recovery/tester/time fields are nonblank strings; tested_at is RFC3339; result is PASS, FAIL, PARTIAL, or INCONCLUSIVE. pre_update_sha256_verified is exact boolean true. preconditions and steps are nonempty arrays; negative_regression_checks, power_cycle_reconnect_checks, anomalies, and evidence_gaps are arrays that may be empty but contain only nonblank strings. Each steps entry has exact keys id, instruction, expected, and observed, all nonblank strings. Add manual_acceptance_protocol_version, hardware_evidence_contract_reference, and hardware_evidence_contract_version to every queue work order. H0/H1 use NOT_APPLICABLE for all three new fields. H2/H3 use exact generic contract reference docs/agent_framework/HARDWARE_EVIDENCE.md and version GLYPH_HARDWARE_EVIDENCE_V2, while manual_acceptance_protocol_reference and manual_acceptance_protocol_version remain candidate-local and nonblank. The record evidence-contract and candidate-protocol fields must respectively equal both queue pairs. hardware_evidence_record accepts exactly repo-json:<path> or git-json:<40-lowercase-SHA>:<path>, where path is a normalized POSIX path under docs/ ending in .json with only alphanumeric, dot, underscore, and hyphen path segments. repo-json resolves HEAD:<path>; git-json resolves <SHA>:<path>. Git tree mode must be exactly regular non-executable blob 100644; symlink, executable, submodule/gitlink, tree, missing object, absolute/escaping path, mutable branch/tag, arbitrary external string, and unsupported scheme fail closed. Every record identity/result/gap field must match the queue; PASS requires no gaps, while PARTIAL/INCONCLUSIVE require gaps. Legacy pre-Revision-2 evidence remains historical and is not upgraded.",
      "explicit_excluded_scope": "No controller test, hardware observation, evidence fabrication, firmware build or execution, artifact retrieval/upload/store selection, device update, flashing, legacy evidence reinterpretation, runtime source, product behavior, or weakening of manual acceptance and exact-snapshot rules.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "docs/agent_framework/HARDWARE_EVIDENCE.md requires exact candidate/artifact correspondence and a complete result record; WORK_ORDER_TEMPLATE.md requires a canonical evidence path/ref after processing. On live configurator cf31dfd60b8247a9af19f2c417d8e712d63781ad, validate_work_order() checks only that hardware_evidence_record is nonempty, and its accepted HARDWARE_VALIDATED self-test points to nonexistent docs/evidence/test.md. Curator independently constructed and validated another nonexistent record reference. Planner candidate GP-HW-001 proposes a structured cross-reference gate and distinguishes current-tree from immutable commit-plus-path evidence.",
      "dependencies_prerequisites": [
        "The Revision-2 exact-snapshot contract and current queue result states remain materially unchanged.",
        "Tests use synthetic records and Git objects only; no historical report is relabeled and no hardware result is asserted.",
        "Permitted post-snapshot deltas are queue/status publication, additive non-semantic agent-framework self-tests from GP-CTL-001, and deterministic checker-census or validation-health fixture regeneration; any evidence-reference, exact-snapshot, hardware-result, queue-schema, or manifest-applicability semantic drift requires fresh curation."
      ],
      "substantive_authorization_rationale": "The safety invariant is already canonical, and the representation/protocol architecture is now fully bound: exact flat v2 JSON with grouped types, exact generic evidence-contract fields, separate candidate-local protocol fields, mandatory successful pre-update rehash, exact repo-json/git-json grammars, 100644 Git blobs only, repository-tree records for already-current evidence, and immutable full-commit-plus-path records for separately published evidence. Unsupported external forms fail closed. This resolves the packet's substantive dependency without selecting a store, credentials, retention policy, candidate test procedure, or product behavior.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Canonical hardware evidence publication adopts a different explicit immutable reference representation before implementation.",
        "The queue/result schema or exact-snapshot protocol materially changes.",
        "Implementation would accept an unverifiable external reference, mutable ref, or reinterpret legacy evidence."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-1450, candidate GP-HW-001, packet commit 03d5bea14cc8beaf0be1b58e713c3b2cbc9efcd1, packet base 7688ee287491ff05898038045f5c1918be09f675, reference forms substantively resolved and independently reverified against live configurator cf31dfd60b8247a9af19f2c417d8e712d63781ad on curation/portfolio-20260823-1615-review.",
      "automated_validation": [
        "Complete synthetic repo-json and git-json records pass only when every exact schema key/type, queue identity, generic evidence-contract pair, candidate-local protocol pair, and result field matches.",
        "Missing, escaping, absolute, malformed-segment, mode-not-100644, symlink, executable, tree, gitlink/submodule, mutable branch/tag-only, missing commit/blob/path, malformed/duplicate JSON key, unsupported scheme, and arbitrary external references fail closed.",
        "Candidate/base SHA, work-order/branch, artifact filename/build-path/hash, preserved locator, pre-update verification not exactly true, either protocol pair, PASS/FAIL/PARTIAL/INCONCLUSIVE, tester/RFC3339 time, exact key/type or step shape, and evidence-gap mismatches fail closed; PASS with gaps and partial/inconclusive without gaps fail.",
        "Framework checker self-tests use real synthetic temporary Git objects rather than nonexistent placeholder paths.",
        "Agent-framework, agentic-sequence, checker-census, full runtime-config aggregate, docs-navigation, and docs-agent-surface checks pass with focused independent governance review and no applicability reclassification."
      ],
      "canonical_build": "NOT_REQUIRED: docs/schema/control-plane checker only; no runtime or product source change.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused governance branch if valid immutable evidence cannot be resolved deterministically; never fall back to accepting an arbitrary nonempty string.",
      "status_documentation_updates": "Document the two accepted Revision-2 record-reference forms and the unsupported external-form stop, while preserving legacy UNKNOWN identity and all manual hardware gates.",
      "done_evidence": "Focused independent governance review; structured record and exact cross-reference positive/negative corpus PASS; current framework/navigation gates PASS; no hardware, firmware artifact, workflow, runtime, or product mutation.",
      "stop_conditions": [
        "An accepted reference cannot be resolved to immutable structured bytes.",
        "Any hardware result, legacy identity, artifact equivalence, or controller observation would be inferred or fabricated.",
        "Any artifact store, upload, device update, flashing, runtime source, or product behavior work becomes necessary."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CTL-001",
      "title": "Make queue prose match machine runway",
      "status": "DONE",
      "branch": "glyph/gp-ctl-001-current-prose-parity-repair-20260831",
      "objective": "Complete the accepted GP-CTL-001 parity objective by removing redundant unguarded current Ready, runway, liveness, priority, and validation-count claims and enforcing the four existing machine-derived summary blocks as the sole current runway statements.",
      "why_this_matters": "The four guarded machine summaries correctly track the queue, but current unguarded prose still names completed GP-VAL-006 as Ready, reports runway one and RUNWAY_LOW, denies current PLANNING_REQUIRED, and reports the obsolete 27-check validation state while every framework check passes.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work changes governance consistency checks and duplicated status prose only. It does not create, promote, execute, or invalidate a work order and changes no product, runtime, source-authority, or hardware behavior.",
      "scope": "Remove redundant unguarded current Ready-ID, executable-priority, numeric runway, primary-liveness, and validation-count claims from ACTIVE_AGENT_QUEUE.md, AGENT_CONTEXT.md, CURRENT_STATE.md, and ROADMAP.md. Point validation-count readers to the exact validation-health summary rather than duplicating 32/28. Strengthen tools/check_glyph_agent_framework_docs.py and its synthetic fixtures so each current surface retains exactly one existing machine-derived runway marker and one human-readable summary, and reintroduction of an unguarded current claim in these categories fails without parsing historical work-order or planning evidence as current truth.",
      "explicit_excluded_scope": "No work-order status or authorization change, candidate promotion, Planner ranking, target change, user-direction change, product/runtime checker, firmware/configurator behavior, source authority, hardware result, or weakening of concurrency, publication, activation, and evidence gates.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md makes ACTIVE_AGENT_QUEUE.md machine state canonical and GP-CTL-001's accepted prior scope required removal of redundant unguarded current numeric runway and executable-priority claims. On live configurator d94eb6d629f9e8e73e893971a3f47c4485cf17ee, the queue markers report no Ready item, runway zero, and PLANNING_REQUIRED before curation, while AGENT_CONTEXT.md, CURRENT_STATE.md, ROADMAP.md, and queue interpretation/disposition prose retain contradictory GP-VAL-006/one/RUNWAY_LOW/27-check statements. Canonical validation health reports 32 entries and 28 load-bearing checks. The framework checker reads only the delimited blocks and accepts all contradictions. Planner packet glyph-portfolio-20260831-1540 and independent Curator verification confirm the incomplete same-identity objective.",
      "dependencies_prerequisites": [
        "Implementation starts from a fresh live-configurator descendant of d94eb6d629f9e8e73e893971a3f47c4485cf17ee and treats its then-current machine-readable queue plus validation-health summary, not prose or Planner ranking, as authority.",
        "Any concurrent legitimate queue publication defers this work rather than racing canonical state.",
        "The queue schema, primary liveness derivation, target/provenance, status ownership, and marker contract remain materially unchanged; normal item transitions and deterministic census consequences are permitted only when the checker remains generic."
      ],
      "substantive_authorization_rationale": "The contradictions are directly source-proven regressions in the exact previously accepted objective. Removing redundant current claims is safer and more exact than creating a second prose parser: the delimited blocks and validation-health summary remain the only current numeric/priority authorities, while historical work orders and Planner evidence remain readable. The repair stays on the ordinary Curator governance-checker surface and requires no product, architecture, source, or user decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Another current change adds equivalent generic current-prose and priority parity enforcement before implementation.",
        "Canonical queue ownership, schema, marker format, liveness derivation, or priority semantics changes materially.",
        "The patch would alter authorization state, target, or candidate disposition rather than validate or accurately mirror it.",
        "The checker cannot distinguish current authoritative prose from historical/planning evidence without overreaching into historical packets."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of reopened candidate GP-CTL-001 from planning/portfolio-20260831-1540 commit 896a06c092bfa2f99339c944fceffda957e4478d, packet/live base d94eb6d629f9e8e73e893971a3f47c4485cf17ee, with bounded history, current-prose, validation-health, checker, and clean live-remote verification on curation/portfolio-20260831-1540-review.",
      "automated_validation": [
        "Each of the four current surfaces contains exactly one delimited machine marker and one human-readable summary rendered from queue JSON in the authorized field order; deliberate Ready-ID/count/order, stale completed-item priority, Preauthorization, invalidation, hardware-pending, effective/target runway, or liveness drift fails.",
        "Redundant current Ready-ID, executable-priority, numeric runway, liveness, and validation-count claims outside those blocks are absent; adversarial reintroduction in each surface fails while a queue transition fixture proves the result is not hard-coded.",
        "The current validation count is sourced only from the exact validation-health summary; historical work-order/Planner counts and dispositions remain outside current-truth enforcement.",
        "Historical evidence and Planner packet prose are not misclassified as current authoritative mirrors.",
        "python3 tools/check_glyph_agent_framework_docs.py, tools/check_glyph_agentic_sequence_protocol.py, tools/check_glyph_checker_census.py, tools/run_glyph_runtime_config_validation.py --json, tools/check_glyph_docs_navigation.py, and tools/check_glyph_docs_agent_surface.py pass with no applicability reclassification.",
        "Focused independent review confirms the governance checker invariant is preserved or strengthened."
      ],
      "canonical_build": "NOT_REQUIRED: current governance docs and ordinary Curator control-plane checker only.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Drop the focused repair if it mistakes historical/planning prose for current authority; retain the canonical machine block and never restore a checker that accepts contradictory current guidance.",
      "status_documentation_updates": "Record GP-CTL-001 as Done after exact reviewed integration. Reconcile the four delimited current-runway summaries to the queue-derived state; per-item Done/history prose remains outside the current-truth scan and no product or runtime authority changes.",
      "done_evidence": {
        "schema_name": "glyph_done_completion_evidence",
        "schema_version": 1,
        "mode": "DIRECT_ANCESTRY",
        "implementation_base_sha": "9ea6c4e4aa23587c540bcd1b36ebd0c2b88b8907",
        "reviewed_implementation_sha": "3e668694f1826ff079b6ecb529d6e3706d8184e7",
        "prior_canonical_integration_sha": "3e668694f1826ff079b6ecb529d6e3706d8184e7",
        "reviewed_changed_paths": [
          "docs/project/ACTIVE_AGENT_QUEUE.md",
          "docs/runtime_config/fixtures/glyph_checker_census.json",
          "tools/check_glyph_agent_framework_docs.py"
        ],
        "independent_review_provenance": "Fresh independent reviewer PASS after current-prose coverage repair; repaired-scope review PASS confirmed generic claim detection, historical exclusion, and all required gates.",
        "validation_provenance": "Focused framework, sequence, census, full runtime-config aggregate, navigation, agent-surface, py_compile, and diff checks passed on the exact integrated snapshot; no firmware build or hardware was required."
      },
      "stop_conditions": [
        "The implementation would change queue item status, priority, runway target, user direction, or substantive authority rather than only enforce current mirrors.",
        "Parity cannot be enforced generically without weakening machine-state, provenance, concurrency, liveness, or historical-evidence separation.",
        "Any product/runtime checker, firmware/configurator source, or hardware evidence is touched."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-002",
      "title": "Gate CI artifact publication on current validation",
      "status": "DONE",
      "branch": "ci-runtime-config-validation-publication-gate",
      "objective": "Run the accepted current fail-closed runtime-config validation on pushes and pull requests before any firmware build, postprocessing, or artifact upload can publish bytes.",
      "why_this_matters": "The current build workflow is push-only and builds, postprocesses, and uploads firmware without running the load-bearing checker census and current validation aggregate, so publication is not coupled to the accepted validation lane.",
      "hardware_risk": "H1",
      "behavioral_claim": "This work changes CI validation and publication gating only. It does not change source-built firmware behavior, execute a device update, establish artifact acceptance, or claim hardware PASS.",
      "scope": "Update .github/workflows/build.yml with pull-request and push coverage, full history sufficient for fail-closed Git comparison, least-required read permissions, and an explicit trusted comparison base for detached CI. Run python3 tools/run_glyph_runtime_config_validation.py --json in a validation job before any build, glyph_nuker invocation, or upload; build/publication jobs must depend on validation success and be unreachable on census or aggregate failure. Preserve the current current-vs-historical classifications. Add a focused static workflow checker/fixture that proves event coverage, permissions, ordering/dependency, command parity, and failure-blocks-publication without invoking GitHub Actions, PlatformIO, glyph_nuker, or a firmware artifact; classify that checker explicitly as a current validation/publication-safety entry in the curated manifest and regenerate the deterministic census/health artifacts.",
      "explicit_excluded_scope": "No branch-protection claim, release automation, artifact-retention/store decision, provenance-sidecar integration, glyph_nuker execution or purpose/effect claim, checker weakening, historical-check promotion, firmware/runtime/product source change, device write, persistence, protobuf write, flashing, or hardware acceptance.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "On live configurator cf31dfd60b8247a9af19f2c417d8e712d63781ad, .github/workflows/build.yml uses on: [push], permissions contents: write, then pio build, glyph_nuker, and actions/upload-artifact without the current aggregate. GP-VAL-001 is DONE: tools/run_glyph_runtime_config_validation.py --json now fails on stale checker census and passes all 21 current curated-manifest checks plus the separately load-bearing census-freshness prerequisite, while the curated manifest retains applicability authority. docs/WORKFLOW.md requires repository-native checkers and least-surprise publication; Planner candidate GP-VAL-002 identifies this successor gap.",
      "dependencies_prerequisites": [
        "GP-VAL-001 is DONE on configurator and the census freshness plus current aggregate pass on the implementation base.",
        "The workflow implementation can supply a trusted explicit base for detached pull-request and push contexts without changing glyph_checker_context.py or weakening any scope check.",
        "GP-PROV-001 remains a separate completed observed-only research lane; this work does not select a durable artifact store or integrate a real sidecar.",
        "Permitted post-snapshot deltas are queue/status publication and deterministic census/validation-health updates caused by other authorized checker bytes; any aggregate command, census-freshness, curated-applicability, workflow publication, or Git-context semantic drift requires fresh curation."
      ],
      "substantive_authorization_rationale": "The predecessor is complete, the exact validation entrypoint and fail-closed result are current, and the required sequencing is fixed: validation success must dominate every build/postprocess/upload route. Pull-request coverage and read-only contents permission are bounded CI safety improvements requiring no product behavior or artifact-store decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The build workflow or current validation entrypoint materially changes before implementation.",
        "Another current workflow already guarantees the same validation-before-publication invariant.",
        "Detached CI cannot satisfy existing context checks without editing glyph_checker_context.py or weakening a current invariant."
      ],
      "authorization_snapshot_provenance": "Fresh Curator review of Planner branch planning/portfolio-20260823-1450, candidate GP-VAL-002, packet commit 03d5bea14cc8beaf0be1b58e713c3b2cbc9efcd1, packet base 7688ee287491ff05898038045f5c1918be09f675, after GP-VAL-001 completion and independent reverification against live configurator cf31dfd60b8247a9af19f2c417d8e712d63781ad on curation/portfolio-20260823-1615-review.",
      "automated_validation": [
        "python3 tools/run_glyph_runtime_config_validation.py --json passes locally on the implementation branch with the authorized explicit comparison base.",
        "Focused static workflow tests prove pull_request and push coverage, full-enough checkout history, trusted detached comparison-base wiring, contents: read permissions, exact current validation command, and validation dependency before every build, postprocess, and upload path.",
        "Adversarial workflow fixtures prove a missing/renamed validation command, continue-on-error, permissive dependency, alternate unguarded upload/build route, stale-census success, or write permission fails.",
        "No test executes GitHub Actions, installs PlatformIO, builds firmware, runs glyph_nuker, reads a firmware artifact, uploads, releases, or writes to a device.",
        "Agent-framework, checker-census, runtime-config aggregate, docs-navigation, and workflow syntax/static checks pass with independent review."
      ],
      "canonical_build": "NOT_REQUIRED for this workflow/static-checker change because no firmware or build input changes; CI may continue its existing build only after validation, but a local build is not evidence required by this work order.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused workflow/checker branch if valid CI contexts cannot run the current aggregate; do not restore artifact publication that bypasses known-failing validation without renewed curation.",
      "status_documentation_updates": "Document validation-before-publication and pull-request coverage without claiming branch protection, release integrity, immutable storage, reproducible postprocessing, or hardware acceptance.",
      "done_evidence": "Independent review PASS; exact static workflow positive/adversarial corpus PASS; local current aggregate and census PASS; YAML parse PASS; workflow diff contains no product/runtime source, postprocessor binary, firmware artifact, upload destination, release, device-write, or hardware-result change.",
      "stop_conditions": [
        "Any existing checker or Git-context invariant must be weakened or tools/glyph_checker_context.py must change.",
        "Any firmware source/build input, glyph_nuker binary or execution semantics, upload/store/release architecture, or artifact acceptance must change.",
        "Any runtime-loaded config, persistence, device-write, protobuf-write, flashing, or hardware claim is introduced."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-001",
      "title": "Reconcile active table-source truth and mutation guardrails",
      "status": "DONE",
      "branch": "runtime-config-active-table-source-truth-guardrails",
      "objective": "Make the active compile-time table-content include chain explicit and make every existing write-capable source-owned generator path fail closed around active firmware table content.",
      "why_this_matters": "The current generated baseline header supplies all 28 active table bodies, but multiple docs, markers, and tools call it inert; that mismatch can turn an offline-looking write into unreviewed active firmware source mutation.",
      "hardware_risk": "H1",
      "behavioral_claim": "This work changes classification and host-side mutation safety only. The exact active table bytes, routing logic, RuntimeConfigView publication, and controller behavior remain unchanged.",
      "scope": "Correct current runtime-config docs, fixtures, generator/install/candidate-prep host tools, and their focused checkers so GeneratedRuntimeConfigBaseline.current.hpp is classified as active table-content source through UltimateIdentityRuntimeTables.hpp while the active-view publication path remains source-owned and unchanged. Dry-run and temporary-output paths stay non-mutating. Existing wrappers must not write the active table-source header through legacy/example/layout-spec or generic absolute-target paths; any future active-table-source mutation must enter a separately authorized candidate workflow with explicit production authority, clean non-configurator branch checks, semantic diff evidence, build, and hardware gates.",
      "explicit_excluded_scope": "No table-byte changes; no Ultimate.cpp, UltimateIdentityRuntimeTables.hpp, or UltimateRuntimeConfigInterpreter.hpp behavior changes; no active selection or RuntimeConfigView change; no production profile authorization; no runtime loading, persistence, WebSerial/device write, protobuf write, flashing, Nunchuk claim, or root-cause claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator 6bc34852e1c823fdeda10f42cc370e5cdec8056e: Ultimate.cpp includes UltimateIdentityRuntimeTables.hpp; that header includes GeneratedRuntimeConfigBaseline.current.hpp and materializes all 28 k*Table arrays; UltimateRuntimeConfigInterpreter.hpp binds those arrays into kSourceOwnedCurrentBaselineRuntimeConfig. docs/runtime_config/source_owned_table_symbol_map.md already distinguishes table content from active-view publication. Planner candidate GP-SRC-001 on planning/portfolio-20260823-0152 identified the contradictory docs and write paths.",
      "dependencies_prerequisites": [
        "Live origin/configurator remains descended from 6bc34852e1c823fdeda10f42cc370e5cdec8056e without a material table-source topology change."
      ],
      "substantive_authorization_rationale": "The correctness gap is directly source-proven, no product or game-semantic choice is needed, and the fail-closed outcome is fixed: active table content must never be labeled or mutated as an inert artifact. Restricting legacy/example write paths preserves the current approved source-owned realization boundary and creates no firmware behavior authority.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The active table-content include chain or active RuntimeConfigView publication path changes before implementation.",
        "The proposed patch changes any active table byte or runtime behavior.",
        "The patch would require a production ownership or profile-semantic decision."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-0152, candidate GP-SRC-001, packet commit 6a21c4f442f3de6fe2da42094dbdc32f68c95d2a, packet/live base 6bc34852e1c823fdeda10f42cc370e5cdec8056e, published on curation/portfolio-20260823-0152-review.",
      "automated_validation": [
        "Adversarial tests prove dry-run and temporary outputs do not mutate the repository.",
        "Adversarial tests reject the active table-source header through generic, legacy layout-spec, example, wrong-branch, dirty-tree, unapproved-provenance, and path-alias/symlink target routes.",
        "Source-sync, table-symbol-map, generator-mode, overlay-preserve, artifact-install, candidate-generation safety, and full runtime-config aggregate checks pass.",
        "A before/after semantic digest proves all 28 active table byte arrays are unchanged.",
        "python3 tools/check_glyph_docs_navigation.py passes."
      ],
      "canonical_build": "NOT_REQUIRED when the authorized patch leaves compiled source and active table bytes unchanged; any compiled-source or byte delta stops this H1 order and requires new H2/H3 authorization.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert only the focused host-tool/docs branch before merge if guardrails break supported dry-run behavior; do not restore misleading inert classification or active-source write paths without renewed curation.",
      "status_documentation_updates": "Update the current runtime-config docs and fixtures touched by the contradictory classification; do not claim a new production profile, hardware result, or active publication mechanism.",
      "done_evidence": "Independent review plus focused negative corpus and current aggregate PASS; exact 28-table semantic digest unchanged; git diff contains no firmware/runtime behavior source or table-byte delta.",
      "stop_conditions": [
        "Any active table byte, routing decision, or publication path changes.",
        "Any write path cannot be made fail closed without selecting new production semantics or ownership.",
        "Any runtime-loaded config, storage, device-write, protobuf-write, or flashing boundary is crossed."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-001",
      "title": "Define the current official-configurator validation lane",
      "status": "DONE",
      "branch": "docs-official-configurator-validation-classification",
      "objective": "Create one fail-closed current offline official-configurator validation entrypoint and explicitly separate current primary corpus evidence from superseded compatibility chains.",
      "why_this_matters": "The primary official corpus checks pass, while broad legacy compatibility runners fail on superseded generated-prototype anchors; without explicit classification, historical failure is easily mistaken for current compatibility evidence.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work changes checker classification and documentation only; it makes no official compatibility, production export, firmware behavior, or device-write claim.",
      "scope": "Add or define a current offline aggregate over the existing official export corpus, corpus diff, export target contract, candidate diff, and validation-report checks. Mark older profile/generated-prototype compatibility chains and stale Ultimate source anchors as historical rather than updating them to manufacture a current pass. Add adversarial classification coverage and current documentation navigation.",
      "explicit_excluded_scope": "No official-app automation or capture; no source-coupled runtime anchor rewrite; no production exporter; no firmware/configurator product behavior; no runtime config, device write, persistence, WebSerial, protobuf write, or flashing; no universal official compatibility claim.",
      "touched_planes": [
        "configurator",
        "docs/checkers"
      ],
      "source_authority": "The committed official configurator corpus and manifest are primary source-backed evidence. On live base 6bc34852e1c823fdeda10f42cc370e5cdec8056e, the export-corpus, corpus-diff, export-target, candidate-diff, and validation-report checks pass, while check_glyph_import_export_compatibility.py fails through the historical identity-runtime anchor 'outputs.buttonL = inputs.lt1 || inputs.lt3;' that contradicts current Ultimate.cpp. Planner candidate GP-CONFIG-001 records the same boundary.",
      "dependencies_prerequisites": [
        "The official corpus manifest and its two committed fixtures remain unchanged or any drift is independently source-verified."
      ],
      "substantive_authorization_rationale": "The repo already declares official corpus authority and quarantines superseded lanes. Defining the current aggregate and labeling historical checks resolves classification drift without selecting product semantics or weakening any evidence check.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "A new official configurator corpus or source-backed compatibility decision materially changes the current evidence set.",
        "Implementation proposes rewriting a historical runtime anchor instead of classifying it.",
        "Implementation would assert official compatibility beyond the committed offline evidence."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-0152, candidate GP-CONFIG-001, packet commit 6a21c4f442f3de6fe2da42094dbdc32f68c95d2a, packet/live base 6bc34852e1c823fdeda10f42cc370e5cdec8056e, published on curation/portfolio-20260823-0152-review.",
      "automated_validation": [
        "Current official export corpus, corpus diff, export target, candidate diff, and validation-report checks pass through one aggregate.",
        "Adversarial tests reject promotion of historical/external-remapper/generated-prototype evidence into the current lane.",
        "python3 tools/check_glyph_docs_navigation.py passes.",
        "python3 tools/run_glyph_runtime_config_validation.py --json remains green."
      ],
      "canonical_build": "NOT_REQUIRED: docs/checker classification only.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Remove the new aggregate/classification branch if it obscures a current source-backed failure; preserve all historical evidence files.",
      "status_documentation_updates": "Update the official configurator/export navigation and checker classification only; retain bounded non-claims.",
      "done_evidence": "Independent review PASS, five current checks plus the new aggregate PASS, negative classification coverage PASS, docs navigation PASS, and no product/runtime source change. Canonical implementation commit: 24d18bb666985fedd51d8820971c92ae55db9da7.",
      "stop_conditions": [
        "A source-backed anchor update or product compatibility decision is required.",
        "Any official universal compatibility or production export claim would be introduced.",
        "Any historical evidence would be deleted or weakened."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-CONFIG-003",
      "title": "Make manual-capture validation host-metadata safe",
      "status": "DONE",
      "branch": "codex/gp-config-003-host-metadata",
      "objective": "Ignore only explicitly enumerated operating-system metadata in the manual-capture tree while retaining strict rejection of unknown evidence entries and malformed captures.",
      "why_this_matters": "The current checker reports a false evidence failure solely because docs/export/manual_captures/.DS_Store exists as ignored host metadata.",
      "hardware_risk": "H0",
      "behavioral_claim": "The checker will treat regular files named exactly .DS_Store at the capture root or inside a dated capture folder as non-evidence host metadata; every other unknown file, directory, malformed folder, schema error, and hash mismatch remains rejected.",
      "scope": "Update the manual-capture result checker, focused fixtures/tests, and capture documentation to enumerate the exact ignored metadata basename and prove it is excluded from evidence and hashing.",
      "explicit_excluded_scope": "No capture execution, app automation, compatibility claim, evidence-hash weakening, wildcard hidden-file allowance, firmware change, runtime config, or device write.",
      "touched_planes": [
        "configurator",
        "docs/checkers"
      ],
      "source_authority": "Live execution of tools/check_glyph_official_configurator_manual_capture_result.py on base 6bc34852e1c823fdeda10f42cc370e5cdec8056e fails only on docs/export/manual_captures/.DS_Store. The capture artifact layout defines dated capture folders and strict evidence contents; Planner candidate GP-CONFIG-003 proposes the bounded host-metadata exception.",
      "dependencies_prerequisites": [
        "No completed capture result is reclassified or altered by this change."
      ],
      "substantive_authorization_rationale": "The ignored basename and permitted locations are fully bounded, and preserving rejection for all other unknown entries keeps the evidence lane fail closed without any product decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "A completed capture currently relies on .DS_Store as evidence or hash input.",
        "Implementation broadens the exception beyond the exact regular-file basename .DS_Store at the documented capture root/folder locations.",
        "Unknown-file or malformed-folder rejection would weaken."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-0152, candidate GP-CONFIG-003, packet commit 6a21c4f442f3de6fe2da42094dbdc32f68c95d2a, packet/live base 6bc34852e1c823fdeda10f42cc370e5cdec8056e, published on curation/portfolio-20260823-0152-review.",
      "automated_validation": [
        "Empty capture root passes with and without a regular .DS_Store file.",
        "A valid synthetic capture passes with and without a regular .DS_Store file.",
        "Unknown dotfiles, unknown ordinary files, .DS_Store directories/symlinks, malformed capture folders, schema drift, and hash mismatch all fail.",
        "python3 tools/check_glyph_official_configurator_manual_capture_result.py passes.",
        "python3 tools/check_glyph_docs_navigation.py passes."
      ],
      "canonical_build": "NOT_REQUIRED: docs/checker-only change.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused checker/docs branch if an unknown evidence entry can evade rejection.",
      "status_documentation_updates": "Document the exact ignored host-metadata rule without recording a capture or compatibility result.",
      "done_evidence": "Canonical implementation commit 38d50a3a3785b6b92ac6bac4fdf98dc5c3d890e5, merged into configurator at d740821ad94d7f9adee4dbeb06ead52f9c76bcc6; focused positive/adversarial cases, manual capture plan, docs navigation, and the clean runtime-config validation lane pass; live .DS_Store no longer creates a false failure; unknown evidence, directories, and symlinks still fail; independent review and repaired-scope re-review pass.",
      "stop_conditions": [
        "The implementation needs a wildcard ignore rule.",
        "Any evidence file or hash field would be skipped.",
        "A manual app interaction or compatibility interpretation becomes necessary."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-PROV-001",
      "title": "Characterize firmware artifact postprocessing provenance",
      "status": "DONE",
      "branch": "docs-artifact-postprocessor-provenance-research",
      "objective": "Statically record what the current CI artifact pipeline and tracked glyph_nuker file identity prove, and define an offline sidecar/verifier contract for full Git and artifact identity without claiming an immutable store exists.",
      "why_this_matters": "CI publishes a short-SHA-named, postprocessed UF2 without a full candidate SHA or final SHA-256 sidecar, while exact-snapshot hardware acceptance requires both identity and a durable candidate/artifact-addressed locator.",
      "hardware_risk": "H0",
      "behavioral_claim": "This is static research and inert provenance tooling. It does not execute glyph_nuker, alter or inspect postprocessed firmware behavior, publish, upload, flash, or hardware-accept any firmware bytes, and it does not assign an undocumented purpose to the binary.",
      "scope": "Create a static source-authority/research record for the tracked glyph_nuker file identity and the commands visible in .github/workflows/build.yml. Define a sidecar schema and read-only verifier over synthetic fixture bytes for full Git SHA, final artifact SHA-256, filename, size, postprocessor file SHA-256, observed-only/source-backed classification, and an explicitly nullable unresolved locator. Fail closed on changed/missing identity fields. Record postprocessor purpose and byte transformation as UNKNOWN unless authoritative source is later supplied.",
      "explicit_excluded_scope": "No execution of glyph_nuker; no real UF2 input or pre/post transformation observation; no candidate firmware, release or CI upload, external store selection, workflow integration, postprocessor replacement, output-changing remediation, device write, flashing, hardware PASS, firmware source change, or claim about glyph_nuker's purpose or effect.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "On live base 6bc34852e1c823fdeda10f42cc370e5cdec8056e, .github/workflows/build.yml copies firmware.uf2, runs the tracked stripped static ELF glyph_nuker, and uploads Glyph_FW using only a short SHA in the filename. The tracked binary SHA-256 is 8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae. docs/agent_framework/HARDWARE_EVIDENCE.md requires full candidate SHA, exact artifact SHA-256, and an immutable candidate/artifact-addressed locator. Planner candidate GP-PROV-001 identifies the gap.",
      "dependencies_prerequisites": [
        "Do not execute glyph_nuker or any firmware artifact.",
        "Treat postprocessor purpose and byte transformation as UNKNOWN unless authoritative source is found."
      ],
      "substantive_authorization_rationale": "The identity gap is directly observable and the research outcome is bounded to descriptive evidence plus inert validation. Deferring CI integration and durable-store selection avoids making architecture, publication, or hardware decisions in this work order.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The live CI workflow or tracked glyph_nuker identity changes before implementation.",
        "The work would execute glyph_nuker or inspect a real postprocessed firmware transformation.",
        "The work would infer postprocessor purpose, byte effect, reproducibility, or acceptance from file identity or workflow text alone."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-0152, candidate GP-PROV-001, packet commit 6a21c4f442f3de6fe2da42094dbdc32f68c95d2a, packet/live base 6bc34852e1c823fdeda10f42cc370e5cdec8056e, published on curation/portfolio-20260823-0152-review.",
      "automated_validation": [
        "Schema accepts a complete synthetic record and rejects missing/short Git SHA, missing/changed artifact hash, filename/size mismatch, postprocessor hash mismatch, and false immutable-locator claims.",
        "Verifier tests use synthetic bytes only and prove no tracked repository artifact, workflow, or binary is mutated or executed.",
        "python3 tools/check_glyph_docs_navigation.py passes."
      ],
      "canonical_build": "NOT_REQUIRED: static research and synthetic schema/verifier tests only.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Remove the inert research/schema branch if static identities or validation rules are incorrect; leave CI, glyph_nuker, and all artifacts unchanged.",
      "status_documentation_updates": "Record exact observed identities, UNKNOWN purpose where unresolved, and the durable-store blocker; do not update hardware status.",
      "done_evidence": "Independent review, tools/check_glyph_artifact_postprocessor_provenance.py --check, synthetic tamper/locator negative cases, docs navigation, exact tracked binary hash and workflow commands recorded, UNKNOWN purpose/effect preserved, and git diff shows no workflow, binary, firmware, artifact, or product-code mutation.",
      "stop_conditions": [
        "glyph_nuker or any firmware artifact would be executed.",
        "A candidate artifact, upload, release, device write, or flashing action would occur.",
        "A binary purpose, byte-effect, or artifact equivalence claim lacks authoritative source.",
        "The task expands into CI integration, store selection, or output remediation."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-VAL-001",
      "title": "Make checker census freshness load-bearing",
      "status": "DONE",
      "branch": "runtime-config-checker-census-integration",
      "objective": "Make deterministic repository checker-census freshness a load-bearing prerequisite of the current runtime-config validation aggregate.",
      "why_this_matters": "Live configurator currently reports a passing runtime-config aggregate while the standalone checker census fails on committed checker drift, so the aggregate can certify a stale view of the available checker surface.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work changes validation control-plane behavior only: stale checker discovery metadata will make the current aggregate fail before successful validation publication. It changes no firmware, configurator product behavior, runtime semantics, or hardware claim.",
      "scope": "Regenerate the deterministic static checker census from the live checker surface, add census freshness as a current load-bearing aggregate prerequisite, keep the curated manifest as the authority for checker applicability, update the validation-health record mechanically, and add isolated adversarial coverage proving any discovered checker-set or checker-byte drift fails the aggregate. Census generation remains static inspection only and must not import or execute discovered checkers.",
      "explicit_excluded_scope": "No manual hash editing; no automatic promotion of census relevance signals into current applicability; no checker weakening or historical-lane promotion; no product/runtime test changes beyond the focused validation aggregate/census/health contract; no CI workflow integration, firmware source, runtime config, device write, persistence, protobuf write, flashing, hardware result, Nunchuk claim, or root-cause claim.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "On live configurator 4ce08a163d4e2c18f05f85da1c73e52a16a479a2, python3 tools/check_glyph_checker_census.py fails with committed artifact drift while python3 tools/run_glyph_runtime_config_validation.py --json passes 20 current load-bearing checks. tools/generate_glyph_checker_census.py deterministically discovers tools/check_glyph_*.py and records static hashes/signals without importing or executing them; tools/run_glyph_runtime_config_validation.py consumes the committed census only for strong-signal classification and does not verify census freshness. Planner candidate GP-VAL-001 at commit 6a21c4f442f3de6fe2da42094dbdc32f68c95d2a identified this exact gap.",
      "dependencies_prerequisites": [
        "GP-SRC-001 is DONE on configurator at canonical implementation commit 6152c70e20e00bcb6dda1efb19bf527e341a78fe.",
        "Implementation begins from a fresh live configurator descendant of 4ce08a163d4e2c18f05f85da1c73e52a16a479a2 and regenerates the census only after all authorized checker edits in its branch are final."
      ],
      "substantive_authorization_rationale": "The reproduced contradiction is a fail-closed validation correctness gap with no product or semantic choice. The intended invariant is exact: the current aggregate must not pass when deterministic checker discovery metadata is stale, while census signals remain review prompts and never self-authorize applicability. GP-SRC-001 has completed, so the predecessor-driven checker drift is now concrete and the successor scope can be judged without anticipating further predecessor changes.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The census becomes load-bearing through another current configurator change before implementation.",
        "The implementation would infer current applicability from static census signals or execute discovered checkers during census generation.",
        "The patch would weaken, remove, or reclassify an existing current validation invariant instead of adding freshness enforcement.",
        "The scope expands into CI publication parity, which remains GP-VAL-002 and requires fresh curation after this item is complete."
      ],
      "authorization_snapshot_provenance": "Follow-up Curator review of Planner branch planning/portfolio-20260823-0152, candidate GP-VAL-001, packet commit 6a21c4f442f3de6fe2da42094dbdc32f68c95d2a, packet base 6bc34852e1c823fdeda10f42cc370e5cdec8056e, independently reverified against live configurator 4ce08a163d4e2c18f05f85da1c73e52a16a479a2 and published on curation/portfolio-20260823-0421-followup.",
      "automated_validation": [
        "python3 tools/generate_glyph_checker_census.py --check passes after deterministic regeneration.",
        "python3 tools/check_glyph_checker_census.py passes and reports the discovery-derived count.",
        "An isolated adversarial test proves added, removed, renamed, or byte-changed checkers make the aggregate fail until deterministic census regeneration, without importing or executing discovered checkers.",
        "Adversarial coverage proves static relevance signals cannot automatically add a checker to the current manifest or remove the requirement for explicit curated classification.",
        "python3 tools/check_glyph_runtime_config_validation_health.py passes.",
        "python3 tools/check_glyph_runtime_config_validation_aggregate.py passes.",
        "python3 tools/run_glyph_runtime_config_validation.py --json passes with census freshness recorded as a current load-bearing result.",
        "python3 tools/check_glyph_docs_navigation.py passes."
      ],
      "canonical_build": "NOT_REQUIRED: deterministic static census, validation manifest/health, adversarial checker, and docs only; any compiled or product source delta stops this work order.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused validation-control-plane branch if deterministic regeneration or aggregate freshness enforcement is incorrect; do not restore a passing aggregate over a known-stale census without renewed curation.",
      "status_documentation_updates": "Document that checker-census freshness is load-bearing while the curated manifest remains authoritative for applicability; do not claim broader compatibility or runtime evidence.",
      "done_evidence": "Independent review PASS; census freshness, validation-health, aggregate adversarial (including added/removed/renamed/byte-changed checker drift), full runtime-config aggregate, and docs-navigation PASS; git diff contains no firmware/configurator product code or runtime/product semantic change. Canonical implementation commit: b34ed5b31e8140ef9e0484f8e98e0be942d1169c.",
      "stop_conditions": [
        "Any discovered checker is imported or executed by census generation.",
        "Static signals would become automatic applicability or authorization.",
        "Any current validation gate, evidence classification, or provenance invariant would be weakened.",
        "Any CI workflow, product/runtime source, hardware, device-write, persistence, protobuf-write, or flashing scope is required."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    },
    {
      "id": "GP-SRC-002",
      "title": "Render authorized v2 packets as C++ previews",
      "status": "DONE",
      "branch": "source-owned-v2-cpp-preview-bridge",
      "objective": "Add a deterministic, review-only prepared-packet-to-C++ preview seam for the source-authority intake and generator-v2 pipeline without installing or activating source.",
      "why_this_matters": "The completed authority intake and generator-v2 modes preserve explicit ownership and produce a validated 28-table artifact/manifest, but the current prepared-packet install emits JSON and the older C++ generator consumes a separate legacy layout-spec contract. Reviewers therefore lack one authority-preserving v2-to-C++ preview path.",
      "hardware_risk": "H1",
      "behavioral_claim": "This work adds deterministic host-side rendering of already explicit validated table symbols and coordinates into inert review text only. It performs no source install, branch creation, build, candidate publication, active-table mutation, RuntimeConfigView change, or controller behavior change.",
      "scope": "Add a read-only renderer and focused CLI/checker path that accepts only a complete prepared schema-version-1 packet, revalidates its prepared semantic digest, artifact, 28-row manifest, baseline identity, production/source-equivalence gate, explicit ownership, provenance, table order, per-table/candidate digests, and classification, then renders a deterministic C++ header preview to stdout or an explicitly safe temporary/offline target. The renderer must use only the packet's existing table_symbol and nine exact points in canonical baseline order, carry profile/provenance and artifact/manifest semantic digests in review metadata, and label the output as inactive review material.",
      "explicit_excluded_scope": "No inference of table mapping, ownership, replacement values, profile intent, or game semantics; no generic or active-source install; no writes under src, include, lib, backend, HAL, .git, or active-publication-like paths; no candidate branch preparation, firmware build, hardware artifact, CI integration, runtime loading, active selection, persistence, WebSerial/device write, protobuf write, flashing, production table authorization, Nunchuk claim, or root-cause claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "On live configurator 4ce08a163d4e2c18f05f85da1c73e52a16a479a2, tools/source_owned_source_authority_intake.py emits generator-input v2 only from approved explicit intake and immediately validates the generated artifact/manifest; tools/source_owned_generator_modes.py prepares schema-version-1 packets containing the complete artifact and manifest, but install_prepared writes the artifact as JSON. tools/generate_source_owned_runtime_config.py renders C++ only from the separate schema-version-1 profile/layout-spec path and has no prepared-packet consumer. Current generator-mode and source-authority-intake checks pass, and no production-authorized intake exists. Planner candidate GP-SRC-002 at commit 6a21c4f442f3de6fe2da42094dbdc32f68c95d2a identified this seam.",
      "dependencies_prerequisites": [
        "GP-SRC-001 is DONE on configurator at canonical implementation commit 6152c70e20e00bcb6dda1efb19bf527e341a78fe, so active table-source classification and generic write guardrails are current.",
        "The prepared packet, baseline extractor, v2 schema, table order, production gate, and source-authority intake semantics remain materially unchanged from live configurator 4ce08a163d4e2c18f05f85da1c73e52a16a479a2.",
        "Tests use synthetic production-authorized packets or the current source-baseline-derived no-op only; no real production authority is asserted or created."
      ],
      "substantive_authorization_rationale": "The gap and mapping seam are source-proven, and every rendered semantic input already exists explicitly in the validated prepared packet. Revalidation plus stdout/temporary-only output prevents the renderer from inventing authority or becoming an install path. This is useful engineering integration inside the approved source-owned generator direction and does not consume the missing user/Senscope production-table decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The prepared packet schema, baseline identity, production gate, or authority-intake semantics materially change before implementation.",
        "Another current tool already supplies an equivalent prepared-v2-to-C++ preview with the same authority and mutation guardrails.",
        "Implementation requires inferred symbol mapping, ownership, replacement content, profile intent, or any game-semantic decision.",
        "The output would be written to active or compiled source, used to create a firmware candidate, or treated as production authority."
      ],
      "authorization_snapshot_provenance": "Follow-up Curator review of Planner branch planning/portfolio-20260823-0152, candidate GP-SRC-002, packet commit 6a21c4f442f3de6fe2da42094dbdc32f68c95d2a, packet base 6bc34852e1c823fdeda10f42cc370e5cdec8056e, independently reverified against live configurator 4ce08a163d4e2c18f05f85da1c73e52a16a479a2 and published on curation/portfolio-20260823-0421-followup.",
      "automated_validation": [
        "Synthetic authorized full-replacement and overlay/preserve prepared packets render deterministic C++ previews with exactly 28 ordered table symbols and exact nine-point coordinates.",
        "The current source-baseline-derived no-op renders equivalently to the extracted active table bytes while remaining explicitly inactive review output and not a hardware candidate.",
        "Tampered prepared digest, artifact or manifest digest, baseline identity, row order, table symbol, ownership, provenance, classification, changed/preserved counts, point count, coordinate, and unknown field all fail closed.",
        "Example, synthetic without explicit test mode, unknown, migrated-legacy, unapproved, unsafe-unowned, and ineligible packets cannot be presented as production previews.",
        "Path adversarial tests reject repository source trees, active table-source aliases, case variants, symlinks, and active-publication-like names; stdout and isolated temporary outputs leave the repository byte-for-byte unchanged.",
        "Repeated rendering is byte-deterministic and includes matching artifact and manifest semantic digests in non-semantic review metadata.",
        "python3 tools/check_glyph_source_owned_generator_modes.py passes.",
        "python3 tools/check_glyph_source_owned_source_authority_intake.py passes.",
        "python3 tools/check_glyph_generated_source_owned_generator_contract.py passes.",
        "python3 tools/run_glyph_runtime_config_validation.py --json passes.",
        "python3 tools/check_glyph_docs_navigation.py passes."
      ],
      "canonical_build": "NOT_REQUIRED: inactive host-side renderer, temporary/offline fixtures, docs, and checker coverage only; any compiled source or active table-content delta stops and requires separate H2/H3 authorization.",
      "expected_artifact": "NOT_APPLICABLE",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Remove the focused renderer/docs branch if validation, determinism, or non-mutation cannot be proved; retain the existing v2 artifact/manifest and authority-intake contracts unchanged.",
      "status_documentation_updates": "Document the prepared-v2 C++ preview as offline, review-only, non-installing, and non-authoritative; retain the absence of a production-owned table set and all runtime/device-write non-claims.",
      "done_evidence": "Independent review plus full synthetic/negative corpus, generator-mode, source-authority-intake, generated-source contract, runtime-config aggregate, and docs-navigation PASS; deterministic digest correspondence is proved; git diff contains no firmware/runtime source, active table bytes, production intake, candidate artifact, workflow, or device-write change.",
      "stop_conditions": [
        "Any semantic value, ownership, mapping, or source authority must be inferred rather than read from a valid prepared packet.",
        "Any repository active/compiled source or active publication path would be written or selected.",
        "Any real production profile, firmware candidate, build, artifact publication, hardware, CI, runtime loading, persistence, device-write, protobuf-write, or flashing action is required.",
        "Any forbidden active path, Nunchuk validation, or root-cause claim would be introduced."
      ],
      "activation_state": "NOT_APPLICABLE",
      "activation_requires_new_judgment": false,
      "hardware_evidence_dependency_satisfied": null,
      "candidate_git_sha": null,
      "candidate_base_configurator_sha": null,
      "firmware_artifact_build_path": null,
      "preserved_firmware_artifact_locator": null,
      "firmware_artifact_sha256": null,
      "hardware_evidence_record": null,
      "hardware_result": null,
      "hardware_evidence_gaps": []
    }
  ]
}
```
<!-- queue-state:end -->

## Interpretation

<!-- current-runway:start -->
{"ready_ids":["GP-X1-002"],"immediate_ready":1,"recorded_preauthorized":0,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":1,"effective_authorized_runway":1,"target_effective_authorized_runway":4,"primary_liveness":"RUNWAY_LOW","global_evidence_wait_supported":false}
<!-- current-runway:end -->

<!-- current-runway-summary:start -->
Ready IDs: GP-X1-002; Immediate Ready: 1; Recorded Preauthorized: 0; Mechanically activatable Preauthorized: 0; Invalidated Preauthorized: 0; Hardware-pending: 1; Effective authorized runway: 1; Target effective authorized runway: 4; Primary liveness: RUNWAY_LOW
<!-- current-runway-summary:end -->

The current-runway marker and summary above are the machine-derived
interpretation of
Immediate Ready, Preauthorized, invalidated, hardware-pending, effective and
target runway, primary liveness, and global evidence-wait support.

The preceding packet prose records the authorization snapshot; the current
machine-derived state above supersedes its historical runway wording.

Corrected packet glyph-portfolio-20260921-1252 is independently adjudicated. GP-X1-002 has a complete READY order for the exact owner-confirmed sole kX1Table restoration under GLYPH-UD-018, with all other tables, LT5/non-Mode routing, Mode/MX1 behavior, publication, GP-CONFIG-010 and Senscope binding excluded. GP-CONFIG-010 remains LOCAL_ACCEPTANCE_PENDING with its exact INCONCLUSIVE evidence and gaps. GP-CONFIG-012, GP-CONFIG-013 and GP-CONFIG-014 remain REVIEW / OWNER_DEFERRED / NONEXECUTABLE under GLYPH-UD-017; GP-VAL-011 remains deferred and GP-HW-002 remains research gated. No new hardware PASS is accepted.

## Allowed Statuses

The queue accepts these work-order states:

```text
READY
PREAUTHORIZED
IN_PROGRESS
REVIEW
HARDWARE_TEST_REQUIRED
LOCAL_ACCEPTANCE_PENDING
HARDWARE_VALIDATED
HARDWARE_FAILED
BLOCKED_EXTERNAL
DONE
INVALIDATED_PREAUTHORIZED
```

`READY` is the only immediately executable state. `PREAUTHORIZED` is recorded
authorization, not necessarily effective runway. A Preauthorized item with
unsatisfied conditions, new judgment required, invalidation, or pending
hardware evidence is not mechanically activatable and is excluded from
effective authorized runway.

Hardware-pending items require the supporting signal
`HARDWARE_TEST_REQUIRED`. `HARDWARE_FAILED` items require the supporting signal
`REPAIR_REQUIRED`; newly recorded failure also opens the canonical curation
obligation, which derives primary `CURATION_REQUIRED` at zero runway until the
Curator records its resolution. The preserved failure does not reopen that
resolved obligation. `HARDWARE_TEST_REQUIRED` carries no result yet;
PARTIAL/INCONCLUSIVE stays `LOCAL_ACCEPTANCE_PENDING` with exact gaps.

## Curator Dispositions

The initial review selected exact tracked schema closure and separate button/USB characterizations, plus a distinct hardware-gated modifier-cache repair. GLYPH-UD-017 now parks the three configuration items without erasing that historical authorization. No probe, implementation, build or merge of these parked items is executable. Resumption needs explicit owner direction and fresh Curator reauthorization; button/USB policies remain unresolved and every H3 exact-artifact physical gate remains mandatory. The initial immutable receipt below is historical provenance, not permission to bypass this later deferral.

## Work Orders

The complete machine-readable work orders above are canonical. Array order is
canonical work-order ordering. Only items marked `READY` authorize immediate
execution.
The one-new-work-order-per-Implementation-cycle rule still applies. GP-HW-002 remains historical gated supply and cannot execute without later source-backed planning and curation; it is not a survivor of the new four-candidate packet.

Every future item recorded in the machine-readable `items` list must satisfy
`docs/agent_framework/WORK_ORDER_TEMPLATE.md`. Curator owns substantive
authorization and new work-order creation. The Implementation Supervisor may
update execution and publication state for the one selected item. The Hardware
Evidence Processor may update only exact identity, evidence-reference, result,
gap, and hardware lifecycle state for an already-recorded H2/H3 candidate; it
cannot create, broaden, or authorize work. Array order is canonical priority
order, highest first.

Independent GP-VAL-011 recovery adjudication and the exact rebound contract are
recorded in `docs/agent_framework/GP_VAL_011_RECOVERY_ADJUDICATION.md`.
The prior local implementation remains failed, superseded recovery evidence.

## Immutable Curator Receipt

This record becomes effective only when its actual commit is referenced by
a separately published canonical queue adoption. It contains no self-SHA.

<!-- curator-receipt:start -->
```json
{
  "schema_name": "glyph_curator_packet_receipt",
  "schema_version": 1,
  "planning_branch": "planning/portfolio-20260921-1252",
  "planning_commit": "525296975bcd6791e8e3a57945b2c47e0fc16ef0",
  "packet_id": "glyph-portfolio-20260921-1252",
  "packet_base_configurator_sha": "71dc9979a78ae2174a232884e1692f833ea80de3",
  "curation_branch": "curation/portfolio-20260921-1252-review-v2",
  "initial_reviewed_dispositions": [
    {
      "candidate_id": "GP-X1-002",
      "disposition": "READY"
    }
  ],
  "review_date": "2026-09-21",
  "global_wait_proposed": false,
  "global_wait_accepted": false,
  "planner_broad_audit_provenance": null,
  "curator_acceptance_provenance": null,
  "required_external_evidence": null,
  "resume_event": null
}
```
<!-- curator-receipt:end -->
