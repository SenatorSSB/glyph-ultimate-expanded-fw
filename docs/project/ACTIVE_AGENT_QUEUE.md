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
  "audit_base_sha": "4ce08a163d4e2c18f05f85da1c73e52a16a479a2",
  "operating_mode": "MINIMAL_SUPERVISOR_WITH_ON_DEMAND_CONSULTATIVE_PLANNING_AND_HARD_HARDWARE_GATE",
  "planner_packet": {
    "state": "PARTIALLY_CONSUMED",
    "branch": "planning/portfolio-20260823-0152",
    "base_configurator_sha": "6bc34852e1c823fdeda10f42cc370e5cdec8056e",
    "candidate_count": 3,
    "curator_review_required": false,
    "global_wait_proposed": false,
    "material_events_since_packet": [
      "Curator independently reviewed all nine candidates: four became READY, three dependency successors remained CURATION_REQUIRED after their predecessors, and two remained external-gated.",
      "GP-SRC-001 and GP-CONFIG-001 completed on configurator without runtime product behavior changes.",
      "Follow-up Curator review on live configurator 4ce08a163d4e2c18f05f85da1c73e52a16a479a2 authorized GP-VAL-001 and GP-SRC-002; GP-VAL-002 remains dependency-gated, GP-AUTH-001 remains user/source-authority gated, and GP-CONFIG-002 remains external-evidence gated."
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
      "status": "READY",
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
      "rollback_recovery": "Revert the focused validation-control-plane branch if deterministic regeneration or aggregate freshness enforcement is incorrect; do not restore a passing aggregate over a known-stale census without renewed curation.",
      "status_documentation_updates": "Document that checker-census freshness is load-bearing while the curated manifest remains authoritative for applicability; do not claim broader compatibility or runtime evidence.",
      "done_evidence": "Independent review plus census, validation-health, aggregate adversarial, full runtime-config aggregate, and docs-navigation PASS; a deliberate temporary checker drift makes the aggregate fail; git diff contains no firmware/configurator product code or runtime/product semantic change.",
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
      "status": "READY",
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

- Immediate Ready runway: `2`.
- Recorded Preauthorized runway: `0`.
- Valid mechanically activatable Preauthorized runway: `0`.
- Invalidated Preauthorized work: `0`.
- Hardware-pending work: `0`.
- Effective authorized runway: `2`.
- Current liveness result: `RUNWAY_LOW` at `2` against the recorded target of `4`; this is a liveness signal, not a quota.
- `GLOBAL_EVIDENCE_WAIT_SUPPORTED`: no.

The two remaining Ready items are independent current H0/H1 opportunities. No
Preauthorization is recorded. `GP-VAL-002` still requires fresh Curator
judgment after `GP-VAL-001`; its future workflow and aggregate assumptions
cannot be activated mechanically. The remaining Planner supply is not a
global wait: `GP-AUTH-001` remains `USER_DECISION_GATED`, and
`GP-CONFIG-002` remains `EVIDENCE_GATED` after `GP-CONFIG-003`.

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

Planner packet `glyph-portfolio-20260823-0152` was initially reviewed against
its exact live `configurator` base
`6bc34852e1c823fdeda10f42cc370e5cdec8056e`. Follow-up review reverified the
surviving dependency candidates against live `configurator`
`4ce08a163d4e2c18f05f85da1c73e52a16a479a2` after `GP-SRC-001` and
`GP-CONFIG-001` completed.

- `GP-SRC-001`: `DONE`; active-table-source truth and mutation guardrails
  shipped without a runtime byte change.
- `GP-VAL-001`: `READY`; the live census/aggregate contradiction remains
  reproduced after `GP-SRC-001`, with curated applicability preserved.
- `GP-VAL-002`: `SUBSTANTIVE_DEPENDENCY_GATED` / `CURATION_REQUIRED` after
  `GP-SRC-001` and `GP-VAL-001`; future aggregate safety and workflow parity
  need fresh judgment.
- `GP-SRC-002`: `READY`; the authority-preserving prepared-v2-to-C++ preview
  seam remains absent after `GP-SRC-001`, with active writes and semantic
  inference excluded.
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
priority order. Only the two remaining `READY` items authorize immediate execution.
No candidate is Preauthorized.

Every future item recorded in the machine-readable `items` list must satisfy
`docs/agent_framework/WORK_ORDER_TEMPLATE.md`. Curator owns substantive
authorization and new work-order creation. The Implementation Supervisor may
update execution and publication state for the one selected item. The Hardware
Evidence Processor may update only exact identity, evidence-reference, result,
gap, and hardware lifecycle state for an already-recorded H2/H3 candidate; it
cannot create, broaden, or authorize work. Array order is canonical priority
order, highest first.
