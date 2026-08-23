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
  "audit_base_sha": "6bc34852e1c823fdeda10f42cc370e5cdec8056e",
  "operating_mode": "MINIMAL_SUPERVISOR_WITH_ON_DEMAND_CONSULTATIVE_PLANNING_AND_HARD_HARDWARE_GATE",
  "planner_packet": {
    "state": "PARTIALLY_CONSUMED",
    "branch": "planning/portfolio-20260823-0152",
    "base_configurator_sha": "6bc34852e1c823fdeda10f42cc370e5cdec8056e",
    "candidate_count": 5,
    "curator_review_required": false,
    "global_wait_proposed": false,
    "material_events_since_packet": [
      "Curator independently reviewed all nine candidates: four became READY, three dependency successors remain CURATION_REQUIRED after their predecessors, and two remain external-gated."
    ],
    "curator_review_provenance": {
      "planning_branch": "planning/portfolio-20260823-0152",
      "planning_commit": "6a21c4f442f3de6fe2da42094dbdc32f68c95d2a",
      "packet_id": "glyph-portfolio-20260823-0152",
      "packet_base_configurator_sha": "6bc34852e1c823fdeda10f42cc370e5cdec8056e",
      "curation_branch": "curation/portfolio-20260823-0152-review",
      "review_date": "2026-08-23"
    }
  },
  "runway": {
    "immediate_ready": 2,
    "recorded_preauthorized": 0,
    "mechanically_activatable_preauthorized": 0,
    "invalidated_preauthorized": 0,
    "hardware_pending": 0,
    "effective_authorized_runway": 2,
    "target_effective_authorized_runway": 4,
    "target_provenance": "Initial 4-hour Implementation / 12-hour Curator cadence: three expected opportunities plus one resilience item; target only, never a quota."
  },
  "signals": [
    "RUNWAY_LOW"
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
      "status": "READY",
      "branch": "official-configurator-manual-capture-host-metadata",
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
      "rollback_recovery": "Revert the focused checker/docs branch if an unknown evidence entry can evade rejection.",
      "status_documentation_updates": "Document the exact ignored host-metadata rule without recording a capture or compatibility result.",
      "done_evidence": "Focused positive and adversarial cases pass, the live .DS_Store no longer creates a false failure, unknown evidence still fails, and independent review confirms no evidence weakening.",
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
      "status": "READY",
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
      "rollback_recovery": "Remove the inert research/schema branch if static identities or validation rules are incorrect; leave CI, glyph_nuker, and all artifacts unchanged.",
      "status_documentation_updates": "Record exact observed identities, UNKNOWN purpose where unresolved, and the durable-store blocker; do not update hardware status.",
      "done_evidence": "Independent review, synthetic schema negative corpus PASS, exact tracked binary hash and workflow commands recorded, UNKNOWN purpose/effect preserved, and git diff shows no workflow, binary, firmware, artifact, or product-code mutation.",
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
    }
  ]
}
```
<!-- queue-state:end -->

## Interpretation

- Immediate Ready runway: `2`.
- Recorded Preauthorized runway: `0`.
- Valid mechanically activatable Preauthorized runway: `0`.
- Invalidated Preauthorized work: `0`.
- Hardware-pending work: `0`.
- Effective authorized runway: `2`.
- Current liveness result: `RUNWAY_LOW` below the recorded target of `4`.
- `GLOBAL_EVIDENCE_WAIT_SUPPORTED`: no.

The two remaining Ready items are independent current H0/H1 opportunities. No
Preauthorization is recorded: the three dependency successors require a fresh
Curator judgment after their predecessors because semantic and applicability
drift cannot be reduced to the current objective mechanical evidence. The
remaining Planner supply is not a global wait: `GP-AUTH-001` remains
`USER_DECISION_GATED`, and `GP-CONFIG-002` remains `EVIDENCE_GATED` after
`GP-CONFIG-003`.

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

Planner packet `glyph-portfolio-20260823-0152` was independently reviewed
against live `configurator` base
`6bc34852e1c823fdeda10f42cc370e5cdec8056e`.

- `GP-SRC-001`: `READY`; source-proven correctness/safety gap, H1, no runtime
  byte change authorized.
- `GP-VAL-001`: `SUBSTANTIVE_DEPENDENCY_GATED` / `CURATION_REQUIRED` after
  `GP-SRC-001`; successor checker/applicability drift needs fresh judgment.
- `GP-VAL-002`: `SUBSTANTIVE_DEPENDENCY_GATED` / `CURATION_REQUIRED` after
  `GP-SRC-001` and `GP-VAL-001`; future aggregate safety and workflow parity
  need fresh judgment.
- `GP-SRC-002`: `SUBSTANTIVE_DEPENDENCY_GATED` / `CURATION_REQUIRED` after
  `GP-SRC-001`; generator-v2 semantics and duplicate-work checks need fresh
  judgment.
- `GP-CONFIG-001`: `READY`; current-vs-historical checker classification only.
- `GP-CONFIG-003`: `READY`; exact `.DS_Store` regular-file exception only.
- `GP-PROV-001`: `READY`; observed-only research and inert provenance schema,
  with CI integration and store selection excluded.
- `GP-AUTH-001`: `USER_DECISION_GATED`; no production-authorized owned-table
  set or replacement content exists, so Curator cannot authorize it.
- `GP-CONFIG-002`: `EVIDENCE_GATED`; requires an external operator and first
  depends on `GP-CONFIG-003`.

## Work Orders

The complete machine-readable work orders above are canonical. Array order is
priority order. Only the four `READY` items authorize immediate execution.
No candidate is Preauthorized.

Every future item recorded in the machine-readable `items` list must satisfy
`docs/agent_framework/WORK_ORDER_TEMPLATE.md`. Curator owns substantive
authorization and new work-order creation. The Implementation Supervisor may
update execution and publication state for the one selected item. The Hardware
Evidence Processor may update only exact identity, evidence-reference, result,
gap, and hardware lifecycle state for an already-recorded H2/H3 candidate; it
cannot create, broaden, or authorize work. Array order is canonical priority
order, highest first.
