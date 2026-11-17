# Decisions

These are selected durable decisions and practices, not new implementation or
device-operation authority. Each entry labels its status, type and scope.
Observations, decisions, inferences and practices carry different weight;
unknown rationale is identified rather than reconstructed.
[CURRENT_STATE](../CURRENT_STATE.md) owns present status; [history](HISTORY.md)
records sequence and [evidence](../evidence/README.md) routes to original records.

### Keep generic active publication source-owned

**Status:** Current, within the legacy generic lane.  
**Type:** Decision after historical observations.  
**Decision:** Preserve the generic source-owned active view; realize reviewed
changes through source-owned tables/routing rather than candidate/active-storage
view publication.  
**Rationale/evidence:** Dedicated storage and immutable generated-view attempts
both failed physically. The failure mechanism remains UNPROVEN.  
**Scope:** Generic RuntimeConfigView publication. The separately approved native
Ultimate/ProfileStore lane is a later bounded exception, not evidence that the
old failures passed.  
**Sources:** [Boundary](../runtime_config/IMPLEMENTATION_BOUNDARY.md),
[storage FAIL](../runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md),
[generated-view FAIL](../runtime_config/diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.md).

### Require explicit ownership of generated production contents

**Status:** Current.  
**Type:** Decision / regression practice.  
**Decision:** Generation must declare complete replacement, overlay/preserve,
or rejection; never fill unspecified production tables with example defaults.  
**Rationale/evidence:** The July canonical-grid content failure replaced 26 tables,
while the earlier source-aligned alias mechanism had passed. Matching two tables
alone did not authorize ownership of every other table.  
**Scope:** Offline source-owned generation, with review/build/hardware gates for
active changes; no generic runtime loading authority.  
**Sources:** [Diff diagnosis](../runtime_config/source_owned_candidate_generation_diff_diagnosis.md),
[overlay proof](../runtime_config/generated_source_owned_overlay_preserve_proof_2026-07-19.md).

### Bind behavior claims to measured or explicit source authority

**Status:** Current.  
**Type:** Decision and evidence practice.  
**Decision:** Use source, measurements or explicit domain authority; mark inference
and unknowns. Official Glyph configurator exports are the primary export corpus;
misattributed external-remapper records remain quarantined.  
**Rationale/evidence:** The explicit source-classification correction invalidated
using those exports as evidence of external-remapper execution.  
**Scope:** Firmware/backend/export-shape claims. Glyph does not decide Smash game
thresholds, datasets or solver semantics.  
**Sources:** [Correction](../calibration/glyph_external_remapper_misattribution_correction_2026-06-06.md),
[architecture boundary](../ARCHITECTURE.md).

### Keep native output finite and deterministic

**Status:** Current.  
**Type:** Product/architecture boundary.  
**Decision:** Author finite raw-input/output tables, conditions, bindings and
effects; no scripts, timed sequences, macros, turbo or inferred character facing.  
**Rationale/evidence:** The documented evaluator and authoring contract expose
bounded simultaneous mappings. They carry no game-recognition guarantee.  
**Scope:** Native Ultimate; a character label is annotation, not gameplay authority.  
**Sources:** [Profile system](../PROFILE_SYSTEM.md), [authoring contract](../../profiles/README.md).

### Preserve human authoring source

**Status:** Current.  
**Type:** Decision.  
**Decision:** V1 human JSON is the source of truth; retain requirements and compile
reports rather than treating decoded native bytes as recovered author intent.  
**Rationale/evidence:** Binary native data loses original symbolic names and sparse
declaration intent. V0-shaped recovery cannot recreate those choices.  
**Scope:** Offline native authoring; compilation is not complete-package installation.  
**Sources:** [Authoring](../../profiles/README.md), [profile system](../PROFILE_SYSTEM.md).

### Keep version domains independent

**Status:** Current.  
**Type:** Contract observation and compatibility practice.  
**Decision:** Track authoring format, native schema/encoding/ABI, package body,
package protocol and storage versions independently.  
**Rationale/evidence:** These describe different data/compatibility boundaries;
existing contracts enumerate them separately. No additional original design
rationale was recovered in this extraction.  
**Scope:** Preserve documented compatibility/refusal rules; Stage E changes none.  
**Sources:** [Version contracts](../PROFILE_SYSTEM.md#version-contracts),
[compatibility practice](../DEVELOPMENT.md#compatibility-and-versioning).

### Preserve admitted filesystem compatibility within fixed resource limits

**Status:** Current.  
**Type:** Owner compatibility decision.  
**Decision:** Retain previously admitted filesystem states, including unrelated
directories and applicable orphan/PENDING_MOVE recovery; require no pristine history.  
**Rationale/evidence:** A difficult stack path is an engineering constraint, not
permission to silently refuse, erase or reinterpret supported state. Structural
source/linked-ELF co-liveness proof must cover feasible paths; watermark observations
supplement rather than replace it.  
**Scope:** Existing supported states, excluding arbitrary corruption; unchanged
per-core stacks, memory/storage budgets, recovery and transactional semantics.  
**Sources:** [Filesystem support decision](../runtime_config/profile_native_ultimate/owner_filesystem_support_decision_20261021.md).

### A complete logical profile owns its backing pair

**Status:** Current.  
**Type:** Owner product decision.  
**Decision:** One managed profile owns one dedicated Ultimate Config row and one
dedicated native ProfileStore record, with no sharing even for identical preprocessing.  
**Rationale/evidence:** Editing one package must never mutate another. The shared
30-row Config cap was accepted; compression/deduplication was not a priority.  
**Scope:** Row and record remain distinct objects, jointly owned by the package;
optional owned RGB and plate remain in their source-defined layers. This is not
completed ordinary managed-selection acceptance.  
**Sources:** [November 5 direction](../ROADMAP.md),
[ownership matrix](../PROFILE_SYSTEM.md#ownership-matrix),
[package contract](../runtime_config/glyph_package_v1/README.md).

### Ordinary selection stays eligible and boot-bound

**Status:** Current.  
**Type:** Architecture decision / practice.  
**Decision:** Validate backend eligibility and row/native context, persist a checked
destination, then reboot into execution. Selection does not rewrite package
references or promise arbitrary live hot swapping.  
**Rationale/evidence:** The supported architecture binds execution to validated
storage/context and refuses fenced or conflicting states.  
**Scope:** Source-backed machinery; ordinary managed selection product acceptance
remains outstanding. Configurator is excluded from ordinary enumeration.  
**Sources:** [Selection architecture](../ARCHITECTURE.md#selection--activation-architecture),
[lifecycle](../runtime_config/package_lifecycle_v2/README.md).

### Acceptance belongs to exact bytes and bounded observations

**Status:** Current.  
**Type:** Evidence practice.  
**Decision:** Bind physical PASS to exact candidate SHA, retained artifact SHA-256
and test scope; a successful build or rebuild does not transfer acceptance.  
**Rationale/evidence:** Build proof establishes compilation, not installation,
execution or human physical observations. API-visible Config/profile equality
also does not establish raw-flash equality.  
**Scope:** All acceptance claims; owner reports and machine evidence stay labelled.
Historical evidence does not automatically satisfy current validation.  
**Sources:** [Hardware acceptance](HARDWARE_ACCEPTANCE.md),
[development evidence rules](../DEVELOPMENT.md#firmware-artifact-and-hardware-evidence).

### Separate Configurator transport from the retired website

**Status:** Current.  
**Type:** Architecture distinction.  
**Decision:** Treat firmware Configurator transport/protocol as distinct from the
retired official configurator website.  
**Rationale/evidence:** Current firmware/host management uses the transport;
website retirement does not imply that protocol disappeared. No broader original
website-retirement rationale was recovered.  
**Scope:** Current source/tool relationships, not renewed website support.  
**Sources:** [Protocol architecture](../ARCHITECTURE.md), [capabilities](../CAPABILITIES.md).

### Keep public development independent of personal orchestration

**Status:** Current.  
**Type:** Documentation ownership decision / practice.  
**Decision:** Public contributors use development, architecture and bounded checks;
normal public work does not require personal campaign queues or agent roles.  
**Rationale/evidence:** Stage D established a supported public build/test/review path
and single documentation owners. Coding-agent instructions still apply pending
separate migration.  
**Scope:** Reader navigation; this extracts no authority to delete internal records.  
**Sources:** [Development](../DEVELOPMENT.md), [maintenance audit](../maintenance/README.md).

### Stage a future clean history with explicit original correspondence

**Status:** Current plan, not executed.  
**Type:** Release-preparation decision.  
**Decision:** Build a future public release repository from a reviewed content
snapshot and fresh clean history, retaining upstream attribution and original
source/artifact correspondence.  
**Rationale/evidence:** The audit records incidental personal/history surfaces and
unreviewed export material; review and recoverable private preservation precede
export. Fresh history cannot retroactively become physical test history.  
**Scope:** Future owner-approved export only; Stage E preserves original records.  
**Sources:** [Maintenance privacy/export plan](../maintenance/README.md),
[source lineage](SOURCE_LINEAGE.md).
