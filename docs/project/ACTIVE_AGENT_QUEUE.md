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
  "schema_version": 2,
  "canonical_branch": "configurator",
  "audit_base_sha": "cf31dfd60b8247a9af19f2c417d8e712d63781ad",
  "operating_mode": "MINIMAL_SUPERVISOR_WITH_ON_DEMAND_CONSULTATIVE_PLANNING_AND_HARD_HARDWARE_GATE",
  "planner_packet": {
    "state": "PARTIALLY_CONSUMED",
    "branch": "planning/portfolio-20260823-1450",
    "base_configurator_sha": "7688ee287491ff05898038045f5c1918be09f675",
    "candidate_count": 6,
    "curator_review_required": false,
    "global_wait_proposed": false,
    "material_events_since_packet": [
      "The packet was published after GP-SRC-001, GP-CONFIG-001, and GP-CONFIG-003 completed, and before GP-PROV-001, GP-VAL-001, and GP-SRC-002 completed on configurator.",
      "Curator independently reproduced the surviving GP-SRC-003, GP-HW-001, GP-CTL-001, and GP-VAL-002 gaps against live configurator cf31dfd60b8247a9af19f2c417d8e712d63781ad and authorized four bounded H0/H1 work orders.",
      "GP-AUTH-001 remains user/source-authority gated and GP-CONFIG-002 remains external-evidence gated; no global evidence wait is supported."
    ],
    "curator_review_provenance": {
      "planning_branch": "planning/portfolio-20260823-1450",
      "planning_commit": "03d5bea14cc8beaf0be1b58e713c3b2cbc9efcd1",
      "packet_id": "glyph-portfolio-20260823-1450",
      "packet_base_configurator_sha": "7688ee287491ff05898038045f5c1918be09f675",
      "curation_branch": "curation/portfolio-20260823-1615-review",
      "review_date": "2026-08-23"
    }
  },
  "runway": {
    "immediate_ready": 0,
    "recorded_preauthorized": 0,
    "mechanically_activatable_preauthorized": 0,
    "invalidated_preauthorized": 0,
    "hardware_pending": 0,
    "effective_authorized_runway": 0,
    "target_effective_authorized_runway": 4,
    "target_provenance": "Initial 4-hour Implementation / 12-hour Curator cadence: three expected opportunities plus one resilience item; target only, never a quota."
  },
    "signals": [
    "CURATION_REQUIRED"
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
      "id": "GP-SRC-003",
      "title": "Complete prepared-packet integrity and output guardrails",
      "status": "DONE",
      "branch": "source-owned-v2-prepared-packet-guardrails",
      "objective": "Make every reusable generator-v2 preparation and installation path verify exact prepared-packet correspondence and fail closed for active, compiled, protected, aliased, or ambiguous output targets.",
      "why_this_matters": "The current installer accepts the active compile-time table header and accepts artifact or manifest payloads changed after preparation while their declared digests remain stale, contradicting the documented inert and integrity-gated boundary.",
      "hardware_risk": "H1",
      "behavioral_claim": "This work changes host-side integrity validation and output-path safety only. It must not write or change active source, active table bytes, firmware runtime behavior, RuntimeConfigView publication, or controller behavior.",
      "scope": "Refactor one strict prepared-packet validator and one resolved offline-output policy into the reusable generator-v2 lane, using the already-shipped preview validator as source-backed input rather than maintaining divergent integrity implementations. Preparation, installation, and preview must enforce exact object schemas; rederive the authoritative baseline, canonical 28-table order, table and artifact digests, manifest rows/counts/actions/classification/digest, and prepared digest. Every file output must be absolute and resolve under the system isolated temporary root returned by tempfile.gettempdir(); repository targets, other filesystem roots, relative paths, case variants, aliases, symlinks, input overwrite, and active-publication-like names fail closed. Accepted writes remain atomic; stdout and dry-run remain non-mutating.",
      "explicit_excluded_scope": "No active or compiled source write; no table-byte, routing, firmware, candidate, build, artifact-publication, workflow, production-ownership, profile-intent, game-semantic, runtime-loading, persistence, WebSerial/device-write, protobuf-write, flashing, Nunchuk, or root-cause change or claim.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator cf31dfd60b8247a9af19f2c417d8e712d63781ad: tools/source_owned_generator_modes.py validate_manifest() does not recompute the table, artifact, row, manifest, or prepared digests; install_prepared() accepts any absolute path except three case-sensitive substrings; tools/generate_source_owned_generator_modes.py prepare --output writes directly; tools/source_owned_cpp_preview.py contains a stricter but preview-local validator/path policy. Curator read-only reproductions accepted the exact active GeneratedRuntimeConfigBaseline.current.hpp path, a changed artifact coordinate with stale digests, and an arbitrary changed manifest action. Planner candidate GP-SRC-003 records the same gap.",
      "dependencies_prerequisites": [
        "GP-SRC-001 and GP-SRC-002 are DONE on configurator; their active-source classification, preview non-claims, and strict preview behavior must remain intact.",
        "Implementation starts from a fresh descendant of cf31dfd60b8247a9af19f2c417d8e712d63781ad and keeps all repository active table bytes unchanged.",
        "Permitted post-snapshot deltas are queue/status publication and deterministic checker-census or validation-health fixture regeneration caused solely by other authorized checker bytes; any prepared-packet, baseline, generator, intake, preview, path-policy, table-source, or manifest-applicability semantic drift requires fresh curation."
      ],
      "substantive_authorization_rationale": "The failure is directly reproducible without mutation, the intended fail-closed correspondence is fixed by existing v2 digests and the shipped preview validator, and the protected output boundary already exists in the source-authority intake path. Sharing and strengthening those invariants requires no product, ownership, mapping, or game-semantic decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Another current change fully closes preparation/install digest recomputation and output-path safety before implementation.",
        "The prepared packet schema, baseline identity, table order, production gate, or preview contract materially changes.",
        "The implementation would write compiled or active source or choose production table content or ownership."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-1450, candidate GP-SRC-003, packet commit 03d5bea14cc8beaf0be1b58e713c3b2cbc9efcd1, packet base 7688ee287491ff05898038045f5c1918be09f675, independently reverified against live configurator cf31dfd60b8247a9af19f2c417d8e712d63781ad and published on curation/portfolio-20260823-1615-review.",
      "automated_validation": [
        "Tampered prepared root, artifact, table, point, manifest row/action/ownership/provenance, counts, classification, baseline, and every declared semantic digest fail closed, including unknown, missing, duplicate, boolean-as-integer, and non-finite fields.",
        "Active header, every repository path, non-temporary absolute root, case-variant, relative, input-overwrite, symlink, path-alias, traversal, and active-publication-like target cases fail for prepare, install, and preview through one shared policy.",
        "Safe isolated absolute offline output is atomic; dry-run and rejected cases leave the repository byte-for-byte unchanged.",
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
      "done_evidence": "Independent review, complete tamper/path negative corpus, safe-output atomicity and non-mutation proof, shared-validator proof, current aggregate and navigation PASS, and exact active-source/table semantic digests unchanged.",
      "stop_conditions": [
        "Any semantic value, ownership, mapping, or production authority must be inferred.",
        "Any active/compiled source, table byte, RuntimeConfigView path, workflow, firmware candidate, or hardware artifact would change.",
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
      "branch": "agent-framework-machine-prose-runway-parity",
      "objective": "Make every current queue and status prose mirror agree mechanically with the canonical machine-readable work-order counts, runway, and liveness state.",
      "why_this_matters": "The framework checker validates queue JSON while stale prose can still tell an operator that a different number of Ready items authorizes execution; the current queue still says two Ready items although machine state is zero before this curation and four after it.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work changes governance consistency checks and duplicated status prose only. It does not create, promote, execute, or invalidate a work order and changes no product, runtime, source-authority, or hardware behavior.",
      "scope": "Strengthen tools/check_glyph_agent_framework_docs.py so the canonical queue interpretation and the current agent-context, current-state, and roadmap operating summaries cannot disagree with the queue JSON on Ready IDs/count, recorded or activatable Preauthorization, invalidated Preauthorization, hardware-pending count, effective/target runway, and primary liveness. Prefer stable machine-derived markers or removal of redundant exact numeric prose where that preserves readable status; keep human-readable candidate dispositions consistent with item statuses. The canonical machine block remains the sole authority.",
      "explicit_excluded_scope": "No work-order status or authorization change, candidate promotion, Planner ranking, target change, user-direction change, product/runtime checker, firmware/configurator behavior, source authority, hardware result, or weakening of concurrency, publication, activation, and evidence gates.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md makes ACTIVE_AGENT_QUEUE.md machine state canonical and tools/check_glyph_agent_framework_docs.py already derives exact runway and liveness from it. On live configurator cf31dfd60b8247a9af19f2c417d8e712d63781ad, the machine block and current summaries report zero Ready while ACTIVE_AGENT_QUEUE.md says 'Only the two remaining READY items'; the framework checker still passes. Planner candidate GP-CTL-001 identified the same recurring parity gap on its earlier base.",
      "dependencies_prerequisites": [
        "Implementation starts from the then-current queue snapshot and treats its machine-readable block, not historical Planner prose, as authority.",
        "Any concurrent legitimate queue publication defers this work rather than racing canonical state.",
        "Permitted post-snapshot deltas are normal queue/status transitions, additive non-semantic hardware-record checker tests from GP-HW-001, and deterministic checker-census or validation-health fixture regeneration; any queue-schema, liveness, authority, provenance, or manifest-applicability semantic drift requires fresh curation."
      ],
      "substantive_authorization_rationale": "The machine block is already canonical and the intended invariant is exact: readable current mirrors must not contradict it. This is a narrow Curator-owned control-plane checker surface and requires no new product, architecture, source, or user decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Another current change adds equivalent generic parity enforcement before implementation.",
        "Canonical queue ownership or the machine-readable state format changes materially.",
        "The patch would alter authorization state rather than validate or accurately mirror it."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-1450, candidate GP-CTL-001, packet commit 03d5bea14cc8beaf0be1b58e713c3b2cbc9efcd1, packet base 7688ee287491ff05898038045f5c1918be09f675, independently reverified against live configurator cf31dfd60b8247a9af19f2c417d8e712d63781ad and published on curation/portfolio-20260823-1615-review.",
      "automated_validation": [
        "Deliberate Ready-ID/count, DONE-ID/count, Preauthorization, invalidation, hardware-pending, effective/target runway, and liveness drift in each current mirrored surface fails.",
        "A queue transition fixture proves parity derives from machine state rather than hard-coded current counts.",
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
      "rollback_recovery": "Revert the focused parity branch if it mistakes historical prose for current state; retain the canonical machine block and do not restore contradictory current guidance.",
      "status_documentation_updates": "Reconcile only current queue/status mirrors and document generic parity ownership; do not change work authorization while performing this item.",
      "done_evidence": "Focused independent governance review, adversarial generic parity corpus PASS, current framework/sequence/navigation/surface gates PASS, and exact queue authorization JSON unchanged by the implementation branch.",
      "stop_conditions": [
        "The implementation would change queue item status, runway target, user direction, or substantive authority.",
        "Parity cannot be enforced without weakening machine-state, provenance, concurrency, or liveness validation.",
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
{"ready_ids":[],"immediate_ready":0,"recorded_preauthorized":0,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":0,"target_effective_authorized_runway":4,"primary_liveness":"CURATION_REQUIRED","global_evidence_wait_supported":false}
<!-- current-runway:end -->

The current-runway marker above is the machine-derived interpretation of
Immediate Ready, Preauthorized, invalidated, hardware-pending, effective and
target runway, primary liveness, and global evidence-wait support.

Ready work remains executable according to the marker above. No
Preauthorization or hardware-pending work is recorded. The remaining
external-gated Planner supply is not a global wait:
`GP-AUTH-001` remains `USER_DECISION_GATED`, and `GP-CONFIG-002` remains
`EVIDENCE_GATED` after `GP-CONFIG-003`.

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
`REPAIR_REQUIRED`; with zero effective runway they also derive the primary
`CURATION_REQUIRED` state. `HARDWARE_TEST_REQUIRED` carries no result yet;
PARTIAL/INCONCLUSIVE stays `LOCAL_ACCEPTANCE_PENDING` with exact gaps.

## Curator Dispositions

Planner packet `glyph-portfolio-20260823-1450` was independently reviewed
after its six carried-forward predecessors completed. Its four surviving
internal candidates were reverified against exact live `configurator`
`cf31dfd60b8247a9af19f2c417d8e712d63781ad`; its two external-gated
candidates remain non-executable.

- `GP-SRC-003`: `DONE`; prepared-packet correspondence, shared isolated-output
  guardrails, atomic writes, and adversarial tamper/path coverage shipped in
  `6cdc25363f1446dea8436cc874992e5adec158ad` without active-source change.
- `GP-HW-001`: `DONE`; Revision-2 result references are limited to a
  current-tree structured record or immutable full-commit-plus-path record and
  must match the exact queue identity/result fields. The exact flat schema,
  Git-object resolution, queue correspondence, and adversarial self-tests
  shipped in this cycle.
- `GP-CTL-001`: `DONE`; generic machine/prose runway parity enforcement is
  authorized on the ordinary Curator governance-checker surface.
- `GP-VAL-002`: `DONE`; current validation now gates every CI
  build/postprocess/upload route with pull-request coverage and existing
  Git-context invariants preserved.

- `GP-SRC-001`: `DONE`; active-table-source truth and mutation guardrails
  shipped without a runtime byte change.
- `GP-VAL-001`: `DONE`; checker-census freshness is load-bearing, curated
  applicability remains authoritative, and the exact drift corpus passes.
- `GP-VAL-002`: `DONE`; its validation-before-publication workflow gate and
  static adversarial corpus are complete.
- `GP-SRC-002`: `DONE`; the authority-preserving prepared-v2-to-C++ preview
  seam is implemented as inactive, deterministic host-side review output with
  fail-closed packet and temporary-path validation.
- `GP-CONFIG-001`: `DONE`; current-vs-historical official-configurator checker
  classification shipped without product behavior change.
- `GP-CONFIG-003`: `DONE`; exact `.DS_Store` regular-file exception only, merged from `codex/gp-config-003-host-metadata`.
- `GP-PROV-001`: `DONE`; observed-only research and inert provenance schema
  record the tracked identity and synthetic verifier; CI integration and store
  selection remain excluded.
- `GP-AUTH-001`: `USER_DECISION_GATED`; no production-authorized owned-table
  set or replacement content exists, so Curator cannot authorize it.
- `GP-CONFIG-002`: `EVIDENCE_GATED`; requires an external operator and first
  depends on `GP-CONFIG-003`.

## Work Orders

The complete machine-readable work orders above are canonical. Array order is
priority order. Only items marked `READY` in the machine-readable block
authorize immediate execution. No candidate is Preauthorized.

Every future item recorded in the machine-readable `items` list must satisfy
`docs/agent_framework/WORK_ORDER_TEMPLATE.md`. Curator owns substantive
authorization and new work-order creation. The Implementation Supervisor may
update execution and publication state for the one selected item. The Hardware
Evidence Processor may update only exact identity, evidence-reference, result,
gap, and hardware lifecycle state for an already-recorded H2/H3 candidate; it
cannot create, broaden, or authorize work. Array order is canonical priority
order, highest first.
