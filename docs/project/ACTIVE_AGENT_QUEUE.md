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
  "audit_base_sha": "0e180e9671b78f8ed3c2a5c9220a4fcafbfae598",
  "operating_mode": "MINIMAL_SUPERVISOR_WITH_ON_DEMAND_CONSULTATIVE_PLANNING_AND_HARD_HARDWARE_GATE",
  "planner_packet": {
    "state": "CONSUMED",
    "branch": "planning/portfolio-20260827-1210",
    "base_configurator_sha": "8c04262c66613d46b933b1b739c01c575cb0c580",
    "candidate_count": 3,
    "curator_review_required": false,
    "global_wait_proposed": false,
      "material_events_since_packet": [
      "Curator independently reviewed fresh packet glyph-portfolio-20260827-1210 at commit ae1d15b9a7941934b26d4371b0ea0e10691629cb against live configurator 8c04262c66613d46b933b1b739c01c575cb0c580.",
      "Direct current-source inspection confirmed incomplete accepted correspondence in GP-PROV-004, GP-CTL-001, and GP-VAL-003; the same identities are reopened as complete H0 READY repair/revalidation work orders rather than duplicated.",
      "Subsequent implementation completed GP-PROV-004, GP-PROV-005, and GP-CTL-001; GP-VAL-003 remained Ready but its 30/25 authorization snapshot drifted mechanically to the current 31/26 manifest state and required same-identity reauthorization.",
      "Curator reverified the surviving packet against live configurator b81c299e1449fc319788a35763b71d3e73d906f1, reauthorized GP-VAL-003, and authorized GP-VAL-005, GP-PROV-006, and GP-VAL-007 as complete H0 READY work orders.",
      "GP-VAL-006 remains non-executable after independent verification: the gap persists, but the responsible design adds H1 host-side branch-correspondence refusal and must wait until GP-VAL-003 completes before its manifest/count consequence can activate.",
      "GP-VAL-008 remains EVIDENCE_GATED, while GP-ART-001 and GP-X1-001 remain USER_DECISION_GATED; none is executable or hardware-pending.",
      "No global evidence wait is proposed or supported.",
      "GP-PROV-004, GP-PROV-005, and GP-CTL-001 are repaired or completed, independently reviewed, integrated, and canonically published Done.",
      "Runtime/configurator product code, active table bytes, workflows, firmware artifacts, and hardware state were unchanged by this curation.",
      "All four work orders authorized on 2026-08-30 are now Done on live configurator 0e180e9671b78f8ed3c2a5c9220a4fcafbfae598, reducing effective authorized runway to zero before this curation.",
      "GP-VAL-006 was independently reverified against live configurator: its checker still fails because canonical branch context preempts the intended active-target refusal, while GP-VAL-003 is Done and the exact H1 isolated-temporary-repository design is now recorded as Ready.",
      "The packet is now consumed for independently executable supply; GP-VAL-008 remains EVIDENCE_GATED and GP-ART-001 plus GP-X1-001 remain USER_DECISION_GATED, so a fresh broad Planner audit is requested without treating those gates as a global wait."
    ],
    "curator_review_provenance": {
      "planning_branch": "planning/portfolio-20260827-1210",
      "planning_commit": "ae1d15b9a7941934b26d4371b0ea0e10691629cb",
      "packet_id": "glyph-portfolio-20260827-1210",
      "packet_base_configurator_sha": "8c04262c66613d46b933b1b739c01c575cb0c580",
      "curation_branch": "curation/portfolio-20260831-gp-val-006-review",
      "review_date": "2026-08-31"
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
      "PLANNING_REQUIRED",
      "RUNWAY_SHORTFALL_CANDIDATE_SUPPLY",
      "RUNWAY_SHORTFALL_EVIDENCE_GATED",
      "RUNWAY_SHORTFALL_USER_DECISION_GATED",
      "PLANNER_REFRESH_REQUIRED"
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
        "reviewed_changed_paths": ["docs/agent_framework/SUBAGENT_CONTRACTS.md", "docs/runtime_config/fixtures/glyph_checker_census.json", "docs/runtime_config/fixtures/runtime_config_validation_health.json", "docs/runtime_config/fixtures/runtime_config_validation_manifest.json", "docs/runtime_config/runtime_config_validation_health.md", "tools/check_glyph_source_owned_candidate_generation.py", "tools/prepare_source_owned_candidate_branch.py"],
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
      "done_evidence": {"schema_name":"glyph_done_completion_evidence","schema_version":1,"mode":"DIRECT_ANCESTRY","implementation_base_sha":"d5050847d3f850951b3f47865dc8a91aedea0834","reviewed_implementation_sha":"2982e4aef11b5da01b65fac706cb81d7068835bf","prior_canonical_integration_sha":"def48ddd72a095f4ea150de9eca9164eed6c32e6","reviewed_changed_paths":["docs/runtime_config/README.md","docs/runtime_config/fixtures/glyph_checker_census.json","docs/runtime_config/fixtures/glyph_nuker_source_lineage.json","docs/runtime_config/fixtures/runtime_config_validation_health.json","docs/runtime_config/fixtures/runtime_config_validation_manifest.json","docs/runtime_config/glyph_nuker_source_lineage.md","docs/runtime_config/runtime_config_validation_health.md","tools/check_glyph_nuker_source_lineage.py"],"independent_review_provenance":"Fresh repaired-scope review PASS on exact feature tip 2982e4aef11b5da01b65fac706cb81d7068835bf; authorized lineage scope, bounded not-found claims, checker safety, manifest/census consequences, and forbidden-path invariants were preserved.","validation_provenance":"Focused lineage, build-input provenance, postprocessor/workflow, 193-entry census, validation health, full current aggregate, framework, sequence, navigation, surface, diff, and compile checks passed; no binary execution, build, artifact, or device action was performed."},
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
      "branch": "runtime-config-active-baseline-classification-truth",
      "objective": "Replace machine-enforced inert claims on the active generated baseline header with exact active-table-content and unchanged-publication classification.",
      "why_this_matters": "The compiled source include chain consumes all 28 table arrays from GeneratedRuntimeConfigBaseline.current.hpp, while that header, its fixture, and its current checker still require the contradictory claims 'inert generated-table placeholder' and 'not wired into runtime selection'.",
      "hardware_risk": "H1",
      "behavioral_claim": "This work changes classification comments, metadata, generator emission classification, docs, and checks only. All 28 table values and symbols, routing, active RuntimeConfigView publication, and controller behavior remain byte-for-byte and semantically unchanged.",
      "scope": "Give the current-baseline output its own exact classification as active compile-time table-content source through UltimateIdentityRuntimeTables.hpp while separately stating that active RuntimeConfigView publication remains source-owned and unchanged. Keep inert example/layout-spec outputs classified as inactive. Update only classification comments/metadata, the current-baseline generator emission seam, fixture, docs, and focused/current validation checks; do not rename or reorder compiled symbols or arrays.",
      "explicit_excluded_scope": "No table point, symbol, routing, RuntimeConfigView, GetActiveRuntimeConfigState, ResolveActiveRuntimeConfig, production profile, ownership, runtime-loaded config, persistence, device/protobuf write, flashing, Nunchuk, root-cause, or hardware-result change or claim.",
      "touched_planes": [
        "source-owned configuration",
        "generated tables/artifacts",
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "On live configurator 6b8ebcd404dcbfe9b579eed41fb35b889e9da598, src/modes/UltimateIdentityRuntimeTables.hpp directly includes src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp and materializes its 28 arrays, while the header and tools/check_glyph_generated_source_owned_baseline_artifact.py require inert/not-wired markers. docs/CURRENT_STATE.md and docs/runtime_config/generated_source_owned_baseline_artifact.md already classify the header as active compile-time table content and distinguish it from unchanged source-owned active-view publication. Fresh Planner candidate GP-SRC-004 records the same contradiction; the classification is now corrected without changing compiled table content or publication.",
      "dependencies_prerequisites": [
        "GP-SRC-001 is DONE and its active-table-source truth, mutation guardrails, and source-owned publication distinction remain authoritative.",
        "Implementation starts from a fresh descendant of 6b8ebcd404dcbfe9b579eed41fb35b889e9da598 and records before/after table, symbol, and active-publication evidence.",
        "Any current-baseline generator change is limited to classification metadata/comments; generated array values and declarations must remain exact."
      ],
      "substantive_authorization_rationale": "The include-chain fact and contradictory machine claims are directly source-proven, and the correction is already resolved by canonical current docs: active compile-time table content is not the same as replacing active RuntimeConfigView publication. No product, profile, ownership, or game-semantic judgment is needed.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The active table-content include chain or active RuntimeConfigView publication changes before implementation.",
        "The correction would change a table value, symbol, declaration, routing decision, or emitted compiled semantics.",
        "Another current change fully corrects the machine-enforced classification before implementation."
      ],
      "authorization_snapshot_provenance": "Curator review of Planner branch planning/portfolio-20260823-2349, candidate GP-SRC-004, packet commit 387a2a7b27d11b81c3c571aaf07cf543af626757, packet/live base 6b8ebcd404dcbfe9b579eed41fb35b889e9da598, independently reproduced and authorized on curation/portfolio-20260824-0051-review.",
      "automated_validation": [
        "Before/after exact values, order, names, symbols, declarations, and semantic digest for all 28 tables are identical.",
        "The include-chain checker proves the current header is active compile-time table content while active RuntimeConfigView selection and publication source remain unchanged.",
        "Current-baseline output uses the active-table-content classification; every example/layout-spec/review output retains its inert classification.",
        "pio run -e glyph_mk6 passes because a compiled header is touched, even though only comments/classification are authorized.",
        "Generated-baseline, source-sync, table-symbol-map, full runtime-config aggregate, docs-navigation, and docs-agent-surface checks pass."
      ],
      "canonical_build": "pio run -e glyph_mk6",
      "expected_artifact": ".pio/build/glyph_mk6/firmware.uf2",
      "manual_acceptance": "NOT_REQUIRED",
      "manual_acceptance_protocol_reference": "NOT_APPLICABLE",
      "manual_acceptance_protocol_version": "NOT_APPLICABLE",
      "hardware_evidence_contract_reference": "NOT_APPLICABLE",
      "hardware_evidence_contract_version": "NOT_APPLICABLE",
      "rollback_recovery": "Revert the focused classification branch if compiled content or active-publication evidence drifts; retain the current source-owned baseline and do not restore a known-false inert claim as current truth.",
      "status_documentation_updates": "Reconcile current baseline docs, fixture, and checker language around active table-content inclusion versus unchanged source-owned active-view publication; make no new compatibility, profile, or hardware claim.",
      "done_evidence": "Implementation commit efda608f9f2af61a44a96f1e5866f2ae57dcc688; independent source-classification review PASS; exact 28-table/symbol/declaration digests unchanged; canonical command unavailable, documented fallback build PASS; source-sync, current aggregate, and navigation PASS; live feature ref verified; runtime product behavior changed: NO.",
      "stop_conditions": [
        "Any compiled table value, symbol, declaration, routing, or active-view publication would change.",
        "Any production profile, source ownership, game semantic, or hardware interpretation is needed.",
        "Any runtime loading, persistence, device/protobuf write, flashing, Nunchuk, or root-cause boundary is crossed."
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
      "branch": "glyph/gp-val-003-health-prose-correspondence-repair-20260830",
      "objective": "Repair and revalidate GP-VAL-003 so the validation-health Markdown manifest-entry count and current load-bearing count mechanically agree with the machine fixture and manifest-derived state while preserving the complete tracked CI publication-route census.",
      "why_this_matters": "Later provenance work mechanically refreshed the Markdown and machine fixture from 30/25 to the current 31 manifest entries and 26 current load-bearing checks, but tools/check_glyph_runtime_config_validation_health.py still never reads the Markdown claims. The values happen to agree while the completed correspondence objective remains fail-open, and the prior exact-count authorization snapshot is invalidated.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work adds static CI route census, explicit classification, and current-claim parity only. It does not edit or invoke a workflow, build firmware, publish bytes, select an owner/caller/store, or change product behavior.",
      "scope": "Update docs/runtime_config/runtime_config_validation_health.md and tools/check_glyph_runtime_config_validation_health.py, plus only synthetic/adversarial test data and mechanically consequent census metadata. Give the Markdown exactly one current-summary sentence or delimited block whose manifest-entry count and current load-bearing count are parsed and required to equal both docs/runtime_config/fixtures/runtime_config_validation_health.json and values derived from docs/runtime_config/fixtures/runtime_config_validation_manifest.json. Preserve all other prose, the existing workflow census, CURRENT_GATED build.yml classification, UNRESOLVED_EXTERNAL build-device-config.yml classification, and every current manifest applicability decision exactly.",
      "explicit_excluded_scope": "No workflow YAML edit, checker applicability reclassification, manifest expansion, route reinterpretation, caller/owner decision, meta.yaml interpretation, secret/PAT/permission/release change, branch-protection claim, build, glyph_nuker execution, upload, store selection, artifact acceptance, firmware/runtime source, device write, persistence, protobuf write, flashing, or hardware result.",
      "touched_planes": [
        "build tooling",
        "docs/checkers"
      ],
      "source_authority": "Live configurator b81c299e1449fc319788a35763b71d3e73d906f1. docs/runtime_config/fixtures/runtime_config_validation_health.json and docs/runtime_config/runtime_config_validation_health.md currently report 31 manifest entries and 26 current load-bearing checks, and tools/run_glyph_runtime_config_validation.py --json passes. tools/check_glyph_runtime_config_validation_health.py derives and verifies the JSON counts against the manifest but does not read or bind the Markdown claims, so a deliberate prose-only drift still passes. Existing workflow census source still classifies build.yml CURRENT_GATED and build-device-config.yml UNRESOLVED_EXTERNAL. Prior GP-VAL-003 completion remains historical evidence of the incomplete prose-correspondence gate.",
      "dependencies_prerequisites": [
        "GP-VAL-001 and GP-VAL-002 remain DONE; checker-census freshness, curated applicability authority, and build.yml validation-before-publication remain intact.",
        "The current 31-entry manifest, 26 current load-bearing entries, machine health schema, and complete tracked workflow census remain the fresh starting state; implementation derives the values mechanically rather than hard-coding either count.",
        "Static discovery proves tracked routes only and must not claim that an external caller invokes build-device-config.yml.",
        "Any manifest/applicability or unresolved-route remediation remains separate authority and is not coupled into this repair."
      ],
      "substantive_authorization_rationale": "The stale 30/25 authorization snapshot was independently detected and not silently reused. Current 31/26 prose is accurate only by convention; the fail-open checker gap remains directly source-proven. Binding one exact current summary generically to the fixture and manifest completes the original GP-VAL-003 parity promise without choosing a checker classification, changing a route, or making a product or external decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "The validation-health machine schema, meaning of either count, tracked workflow census, or publication classification materially changes before implementation; ordinary separately reviewed checker additions and their deterministic manifest/census/health consequences are permitted only when the generic parity invariant remains exact.",
        "Authoritative caller/ownership evidence arrives and changes build-device-config.yml classification.",
        "Implementation would edit/reclassify the manifest or a workflow rather than bind already-current machine state to prose.",
        "Current Markdown cannot be parsed deterministically without replacing prose with one explicit machine-derived marker or equivalent stronger invariant."
      ],
      "authorization_snapshot_provenance": "Same-identity substantive reauthorization of repair candidate GP-VAL-003 from planning/portfolio-20260827-1210 commit ae1d15b9a7941934b26d4371b0ea0e10691629cb, packet base 8c04262c66613d46b933b1b739c01c575cb0c580, independently rebound after the old 30/25 snapshot invalidated to live configurator b81c299e1449fc319788a35763b71d3e73d906f1 on curation/portfolio-20260830-0211-review on 2026-08-30.",
      "automated_validation": [
        "Validation-health Markdown contains exactly one parseable current summary whose manifest-entry count and current load-bearing count agree mechanically with the machine fixture and manifest-derived state.",
        "Adversarially drifting either Markdown count independently, duplicating/removing the summary, or mismatching JSON versus manifest fails while historical records remain excluded from current counts.",
        "Static workflow census still records both workflow files, exact hashes, all build/postprocess/upload/release routes, and explicit CURRENT_GATED or UNRESOLVED_EXTERNAL classification; build.yml and build-device-config.yml bytes remain unchanged.",
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
      "rollback_recovery": "Drop the focused repair if readable current health prose cannot be bound without weakening machine authority; retain the complete route census and unresolved external classification, and never restore a checker that accepts stale current counts.",
      "status_documentation_updates": "Record GP-VAL-003 as reauthorized against current 31/26 machine state for generic machine/prose correspondence enforcement while preserving the route census and every unresolved external, runtime, artifact, and hardware non-claim.",
      "done_evidence": {"schema_name":"glyph_done_completion_evidence","schema_version":1,"mode":"DIRECT_ANCESTRY","implementation_base_sha":"d4d68a1e708674c04a0d81846183cb74918ae241","reviewed_implementation_sha":"7987251866da58575a2a6a0dc7556f9d0cc60d3d","prior_canonical_integration_sha":"00c2b9aa91633ee877186052d4f1c5d93cdc8f45","reviewed_changed_paths":["docs/runtime_config/fixtures/glyph_checker_census.json","docs/runtime_config/runtime_config_validation_health.md","tools/check_glyph_runtime_config_validation_health.py"],"independent_review_provenance":"Fresh independent reviewer found one fail-open unmatched-marker case; root repaired it by requiring exactly one marker pair and added adversarial coverage, followed by fresh repaired-scope re-review PASS on the exact feature tip 7987251866da58575a2a6a0dc7556f9d0cc60d3d.","validation_provenance":"Focused health checker, 193-entry census, full runtime-config aggregate, publication workflow, full runtime-config validation, agent-framework, sequence, docs-navigation, docs-agent-surface, py_compile, and diff checks passed on the integrated snapshot; no build or hardware was required."},
      "stop_conditions": [
        "Any workflow, manifest applicability, checker classification, permission, secret, trigger, caller, release, or artifact destination must change.",
        "Any unresolved external ownership/caller fact would be inferred.",
        "The current machine/prose state cannot be bound without weakening manifest or health authority.",
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
      "done_evidence": {"schema_name":"glyph_done_completion_evidence","schema_version":1,"mode":"DIRECT_ANCESTRY","implementation_base_sha":"e41e4ea1017b5abde4f17eed1a4bc50404238c75","reviewed_implementation_sha":"7a042fbdd1dc28db8efbd7c59e1730565fe33288","prior_canonical_integration_sha":"7a042fbdd1dc28db8efbd7c59e1730565fe33288","reviewed_changed_paths":["docs/runtime_config/fixtures/glyph_checker_census.json","tools/check_glyph_coordinate_native_runtime_profile_contract.py"],"independent_review_provenance":"Fresh independent reviewer PASS on exact feature tip 7a042fbdd1dc28db8efbd7c59e1730565fe33288; specialist follow-up repaired explicit pre-recording and short-circuit assertions, followed by repaired-scope review PASS with no findings.","validation_provenance":"Focused explicit/default packaging routes, census freshness, aggregate adversarial checks, validation health, full runtime-config aggregate, framework, sequence, navigation, docs-agent-surface, py_compile, and diff checks passed on the exact integrated snapshot; no build or hardware was required."},
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
      "done_evidence": {"schema_name":"glyph_done_completion_evidence","schema_version":1,"mode":"DIRECT_ANCESTRY","implementation_base_sha":"0086b388cd230b65e3b9dee0be2e69600b3ae3a0","reviewed_implementation_sha":"26e3ca148df4de6fb9c10806f97204cc17164f52","prior_canonical_integration_sha":"26e3ca148df4de6fb9c10806f97204cc17164f52","reviewed_changed_paths":["docs/agent_framework/SUBAGENT_CONTRACTS.md","docs/runtime_config/build_input_non_selector_configuration.md","docs/runtime_config/fixtures/build_input_non_selector_configuration.json","docs/runtime_config/fixtures/glyph_checker_census.json","docs/runtime_config/fixtures/runtime_config_validation_health.json","docs/runtime_config/fixtures/runtime_config_validation_manifest.json","docs/runtime_config/runtime_config_validation_health.md","tools/check_glyph_build_input_non_selector_configuration.py","tools/check_glyph_runtime_config_validation_health.py"],"independent_review_provenance":"Fresh repaired-scope independent reviewer PASS on exact feature tip 26e3ca148df4de6fb9c10806f97204cc17164f52 after prior findings were repaired; source reference expansions, chain_references schema, parser-backed correspondence, non-claims, and manifest/census/health consistency passed.","validation_provenance":"Focused census, checker census, validation health, aggregate adversarial, full runtime-config runner, framework, sequence, navigation, docs-agent-surface, py_compile, and diff checks passed; no build or hardware was required."},
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
      "done_evidence": {"schema_name":"glyph_done_completion_evidence","schema_version":1,"mode":"DIRECT_ANCESTRY","implementation_base_sha":"a49117062282efc077417143c325cae3c55bff4e","reviewed_implementation_sha":"e8ab9b86408d1c89f3b35a07949782d9e3c414ff","prior_canonical_integration_sha":"e8ab9b86408d1c89f3b35a07949782d9e3c414ff","reviewed_changed_paths":["docs/agent_framework/SUBAGENT_CONTRACTS.md","docs/runtime_config/fixtures/glyph_checker_census.json","docs/runtime_config/fixtures/runtime_config_validation_manifest.json","docs/runtime_config/runtime_config_validation_health.md","tools/check_glyph_runtime_config_validation_aggregate.py","tools/run_glyph_runtime_config_validation.py"],"independent_review_provenance":"Fresh independent validator review PASS on exact repaired feature tip e8ab9b86408d1c89f3b35a07949782d9e3c414ff; prior policy reclassification finding was repaired and direct dependency path adversarial coverage was expanded.","validation_provenance":"Manifest schema-v4 check, aggregate adversarial suite, 194-entry census, validation health, full 27-check runtime-config aggregate, framework, sequence, navigation, docs-agent-surface, py_compile, and diff checks passed on the exact integrated snapshot; no firmware build or hardware was required."},
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
      "branch": "glyph/gp-ctl-001-current-prose-parity-repair-20260827",
      "objective": "Repair and revalidate GP-CTL-001 so the four current executable-runway summaries mechanically agree with canonical Ready order, authorization counts, effective/target runway, and primary liveness.",
      "why_this_matters": "The framework's current-runway JSON markers agree, but docs/AGENT_CONTEXT.md and docs/ROADMAP.md still say effective runway is two while the canonical markers report one, and the queue's closing priority prose still places completed GP-PROV-004 before the sole Ready GP-PROV-005. The completed parity objective therefore remains fail-open for human-readable claims.",
      "hardware_risk": "H0",
      "behavioral_claim": "This work changes governance consistency checks and duplicated status prose only. It does not create, promote, execute, or invalidate a work order and changes no product, runtime, source-authority, or hardware behavior.",
      "scope": "Strengthen tools/check_glyph_agent_framework_docs.py and its synthetic fixtures by adding one exact delimited human-readable current-runway summary block to ACTIVE_AGENT_QUEUE.md, AGENT_CONTEXT.md, CURRENT_STATE.md, and ROADMAP.md. The checker deterministically renders the block from queue JSON in this exact field order: Ready IDs in queue priority order; immediate Ready; recorded Preauthorized; mechanically activatable Preauthorized; invalidated Preauthorized; hardware-pending; effective/target runway; primary liveness. Each file must contain exactly one matching block. Remove other unguarded current numeric runway and executable-priority claims from those four current surfaces, while historical/planning evidence remains outside the block and ungated. Update only the ordinary Curator checker, its synthetic fixtures, and current control-plane prose; the queue JSON remains sole authority.",
      "explicit_excluded_scope": "No work-order status or authorization change, candidate promotion, Planner ranking, target change, user-direction change, product/runtime checker, firmware/configurator behavior, source authority, hardware result, or weakening of concurrency, publication, activation, and evidence gates.",
      "touched_planes": [
        "docs/checkers"
      ],
      "source_authority": "docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md makes ACTIVE_AGENT_QUEUE.md machine state canonical. On live configurator 8c04262c66613d46b933b1b739c01c575cb0c580, the queue and all current-runway markers report ready_ids [GP-PROV-005] and effective runway one, while docs/AGENT_CONTEXT.md and docs/ROADMAP.md say two and the queue closing work-order prose orders completed GP-PROV-004 before Ready GP-PROV-005. tools/check_glyph_agent_framework_docs.py validates marker equality but accepts these prose contradictions. Prior GP-CTL-001 completion remains historical evidence of the incomplete parity gate.",
      "dependencies_prerequisites": [
        "Implementation starts from a fresh live configurator descendant of 8c04262c66613d46b933b1b739c01c575cb0c580 and treats its machine-readable queue block, not prose or Planner ranking, as authority.",
        "Any concurrent legitimate queue publication defers this work rather than racing canonical state.",
        "The queue schema, primary liveness derivation, target/provenance, status ownership, and marker contract remain materially unchanged; normal item transitions and deterministic census consequences are permitted only when the checker remains generic."
      ],
      "substantive_authorization_rationale": "The contradictions are directly source-proven and the intended invariant is already canonical: readable current mirrors and priority prose must not contradict machine authorization. The repair stays on the ordinary Curator governance-checker surface, derives from existing state, and requires no queue promotion, target change, product, architecture, source, or user decision.",
      "mechanical_activation_conditions": [],
      "invalidation_conditions": [
        "Another current change adds equivalent generic current-prose and priority parity enforcement before implementation.",
        "Canonical queue ownership, schema, marker format, liveness derivation, or priority semantics changes materially.",
        "The patch would alter authorization state, target, or candidate disposition rather than validate or accurately mirror it.",
        "The checker cannot distinguish current authoritative prose from historical/planning evidence without overreaching into historical packets."
      ],
      "authorization_snapshot_provenance": "Independent Curator review of repair candidate GP-CTL-001 in planning/portfolio-20260827-1210 commit ae1d15b9a7941934b26d4371b0ea0e10691629cb, packet base and live configurator 8c04262c66613d46b933b1b739c01c575cb0c580, with direct current marker/prose/checker reproduction on curation/portfolio-20260827-1232-review on 2026-08-27.",
      "automated_validation": [
        "Each of the four current surfaces contains exactly one delimited human-readable summary block rendered from queue JSON in the authorized field order; deliberate Ready-ID/count/order, stale completed-item priority, Preauthorization, invalidation, hardware-pending, effective/target runway, or liveness drift fails.",
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
      "rollback_recovery": "Drop the focused repair if it mistakes historical/planning prose for current authority; retain the canonical machine block and never restore a checker that accepts contradictory current guidance.",
      "status_documentation_updates": "Record GP-CTL-001 as reopened for current executable-runway summary parity repair. Reconcile only the four delimited current-runway summaries and remove redundant unguarded executable priority/count prose; per-item Done/history prose remains outside this objective, and work authorization must not change during implementation.",
      "done_evidence": {"schema_name":"glyph_done_completion_evidence","schema_version":1,"mode":"DIRECT_ANCESTRY","implementation_base_sha":"b901d10360402e98953eac539d3a681971e72e20","reviewed_implementation_sha":"8909e50594a4443a4ee2d5cd16a2e78c22ef960f","prior_canonical_integration_sha":"b901d10360402e98953eac539d3a681971e72e20","reviewed_changed_paths":["docs/AGENT_CONTEXT.md","docs/CURRENT_STATE.md","docs/ROADMAP.md","docs/project/ACTIVE_AGENT_QUEUE.md","docs/runtime_config/fixtures/glyph_checker_census.json","tools/check_glyph_agent_framework_docs.py"],"independent_review_provenance":"Fresh independent reviewer PASS on the exact feature tip, followed by repaired-scope re-review PASS confirming removal of unguarded Ready-order prose, fail-closed reversed-marker handling, and no queue, authorization, product, runtime, firmware, or hardware drift.","validation_provenance":"Framework, sequence, 193-entry census, full current runtime-config aggregate, navigation, agent-surface, health, publication-workflow, and diff checks passed on the exact integrated snapshot; no build or hardware was required."},
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
{"ready_ids":[],"immediate_ready":0,"recorded_preauthorized":0,"mechanically_activatable_preauthorized":0,"invalidated_preauthorized":0,"hardware_pending":0,"effective_authorized_runway":0,"target_effective_authorized_runway":4,"primary_liveness":"PLANNING_REQUIRED","global_evidence_wait_supported":false}
<!-- current-runway:end -->

<!-- current-runway-summary:start -->
Ready IDs: none; Immediate Ready: 0; Recorded Preauthorized: 0; Mechanically activatable Preauthorized: 0; Invalidated Preauthorized: 0; Hardware-pending: 0; Effective authorized runway: 0; Target effective authorized runway: 4; Primary liveness: PLANNING_REQUIRED
<!-- current-runway-summary:end -->

The current-runway marker and summary above are the machine-derived
interpretation of
Immediate Ready, Preauthorized, invalidated, hardware-pending, effective and
target runway, primary liveness, and global evidence-wait support.

`GP-SRC-003` and `GP-SRC-004` are DONE on validated implementation branches.
`GP-SRC-005` and `GP-VAL-004` are DONE; `GP-VAL-003` is DONE after exact
generic health-prose correspondence repair, with current validation now at 32
manifest entries and 27 load-bearing checks before GP-VAL-006 implementation.
`GP-CONFIG-004` is `DONE`; its exact reviewed H0 checker repair is merged and
live-verified in canonical configurator.
`GP-PROV-002` is `DONE`; its reviewed feature tip is integrated into
configurator and its exact recovery publication is live-verified.
`GP-CTL-002` is `DONE`; its exact integration and separate completion
publication are canonical. `GP-PROV-003` is `DONE` after exact reviewed
implementation ancestry and separate structured completion publication.
`GP-PROV-004` is `DONE` after exact source/identity/base/dependency
correspondence repair, independent review, canonical integration, and
structured completion publication. `GP-CTL-001` is `DONE` after exact
machine/prose runway parity enforcement and separate completion publication.
`GP-PROV-006` and `GP-VAL-007` are `DONE` after exact reviewed implementation
ancestry and separate completion publication. `GP-VAL-003` is `DONE` after
exact reviewed health-prose correspondence repair and canonical integration.
`GP-PROV-005` is `DONE` after bounded
source-lineage research; source lineage, purpose, byte transformation, build
recipe, reproducibility, safety, artifact acceptance, and hardware remain
`UNKNOWN`.
No invalidated Preauthorization or hardware-pending work exists.
The current-runway summary above is authoritative for the human-readable
runway state.
`GP-VAL-006` is DONE after exact reviewed branch-correspondence and
standalone-temporary-repository safety validation; no executable Ready item
remains.
`GP-AUTH-001` is resolved by the baseline-equivalent sole-X1 production intake;
`GP-CONFIG-002` is invalidated by user direction. Remaining non-executable
Planner survivors are `GP-VAL-008`, `GP-ART-001`, and `GP-X1-001`; none
establishes a portfolio-global wait. The packet is consumed for further
executable supply and a fresh Planner audit is requested.

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

Planner packet `glyph-portfolio-20260827-1210` at
`ae1d15b9a7941934b26d4371b0ea0e10691629cb` was independently reviewed
against exact live `configurator` `8c04262c66613d46b933b1b739c01c575cb0c580`
and its surviving candidates were independently reverified against live
`configurator` `b81c299e1449fc319788a35763b71d3e73d906f1`, with the final
actionable survivor reverified again against live `configurator`
`0e180e9671b78f8ed3c2a5c9220a4fcafbfae598`. It is
`CONSUMED`: all previously authorized H0 candidates are now Done. Independent
reverification authorized the final actionable survivor, `GP-VAL-006`, as one
H1 Ready work order; three non-executable survivors remain, effective runway is
one against target four, and fresh Planner supply is requested.
Historical Done items not named below remain Done.

- `GP-PROV-004`: `DONE`; exact workflow expressions, source classes,
  lookup/locator rules, immutable identity correspondence, base/blob closure,
  record order, and exact direct manifest dependencies were repaired without
  adding, promoting, or claiming complete dependency closure for external facts.
- `GP-CTL-001`: `DONE`; current human-readable runway and priority prose are
  machine-bound and canonically published.
- `GP-VAL-003`: `DONE`; its checker now enforces exactly one Markdown summary
  marker pair and generic Markdown/fixture/manifest correspondence without
  reclassifying any checker or workflow route.
- `GP-PROV-005`: `DONE`; bounded `glyph_nuker` source-lineage research recorded
  research without executing, rebuilding, replacing, or promoting inference
  into authority.
- `GP-VAL-005`: `DONE`; the existing no-argument coordinate-native checker now
  runs all three advertised offline packaging validators with an exact trace.
- `GP-VAL-006`: `DONE`; exact checked-out/requested branch equality, isolated
  standalone temporary repositories, canonical immutability snapshots, and
  the existing manifest-v4 row's 28th current load-bearing classification are
  reviewed and canonically integrated.
- `GP-PROV-006`: `DONE`; its exact two-source, finite-key, literal-only census
  preserves runtime interpolation and PlatformIO/compiler effects as unresolved.
- `GP-VAL-007`: `DONE`; manifest v4 now enforces its bounded normalized tracked-
  file dependency contract, static direct-local-helper lower bound, explicit
  exclusions, and applicability-consistent branch-policy matrix.
- `GP-VAL-008`: `EVIDENCE_GATED`; current source/evidence does not yet define a
  safe runtime-behavior regression subset without historical or semantic
  inference.
- `GP-ART-001` and `GP-X1-001`: remain `USER_DECISION_GATED`; no store/custody
  decision or different X1 bytes exist.
- `GP-AUTH-001` remains resolved by the baseline-equivalent sole-`kX1Table`
  no-op intake. `GP-CONFIG-002` remains invalidated by user direction. No
  global evidence wait is proposed or supported.

## Work Orders

The complete machine-readable work orders above are canonical. Array order is
priority order. Only items marked `READY` authorize immediate execution.
No Ready work order remains; the one-new-work-order-per-Implementation-cycle
rule still applies. Remaining Planner survivors are
non-executable under the dispositions above.

Every future item recorded in the machine-readable `items` list must satisfy
`docs/agent_framework/WORK_ORDER_TEMPLATE.md`. Curator owns substantive
authorization and new work-order creation. The Implementation Supervisor may
update execution and publication state for the one selected item. The Hardware
Evidence Processor may update only exact identity, evidence-reference, result,
gap, and hardware lifecycle state for an already-recorded H2/H3 candidate; it
cannot create, broaden, or authorize work. Array order is canonical priority
order, highest first.
