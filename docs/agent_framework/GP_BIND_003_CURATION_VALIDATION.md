# GP-BIND-003 curation validation

Classification: `DOCS_CHECKER_ONLY`. Base
`941affbdbb7e54563e4c58a3830c49f39ea0f449`; Planner
`9af3ce8b6c6076ca96cc8c7ee60850537c8ddfad`; immutable same-base receipt
`9a822a5afc4709d35ed9919814e5088a3c8c555e`. No firmware/build/device mutation.

Executed on 2026-10-19 against the descendant adoption:

- `python3 tools/check_glyph_agent_framework_docs.py`: PASS, including queue,
  complete work-order shape, exact Planner/receipt same-base Git correspondence,
  append-only/legacy receipt negatives, event receipt, all runway/status mirrors,
  hardware merge gate, role and current authority contracts.
- `python3 tools/check_glyph_docs_navigation.py`: PASS.
- `python3 tools/check_glyph_agentic_sequence_protocol.py`: PASS.
- `git diff --check`: PASS.
- Focused snapshot assertions: PASS; all 101 prior queue items, the resolved
  GP-BIND-001/002 post-event obligation/receipt, completion policy and global-wait
  fields are object-equal to the base. Exactly one new complete order is appended.
  Copied Planner packet/capability bytes equal their immutable published blobs.
  Planner and first receipt are direct children of the exact same base; receipt
  is regular `100644` and unchanged in adoption. No active firmware/config/schema,
  build inputs, old receipts or historical physical evidence changed.

`python3 tools/check_glyph_docs_agent_surface.py`: actual FAIL, not waived to
PASS. It fails at `C024 post-integration change outside validation/evidence paths`.
The exact command also fails identically in the clean unchanged base worktree
`/private/tmp/gp-bind-002-activation-observation-review` whose HEAD was verified
as `941affbdbb7e54563e4c58a3830c49f39ea0f449`. The old finite C024 consumer is
incompatible with already-existing later canonical chapters, before this pass.

Direct calls to that checker's unchanged actual content functions establish:
AGENT_CONTEXT and ROADMAP PASS on base and adoption. CURRENT_STATE fails its
120-line ceiling on both (base already 217 lines); unchanged implementation
boundary fails the old exact phrase `Runtime-loaded profile claims are forbidden
without separate design` on both. These are retained baseline framework debt,
not false PASS and not a new implementation-boundary contradiction. The current
boundary explicitly preserves separate approval and accepted bounded chapter
authority. This pass edits no checker or scope-authentication code to bypass it.

Revision 3 permits this docs-only authorization to progress on the required
actual framework/sequence/navigation, source-boundary and frozen-record proof:
no concrete Tier-1 or directly affected Tier-2 safety contradiction was found.
No full aggregate PASS is claimed, and no firmware test, build, artifact,
controller acceptance or X1 root-cause result is implied by these checks.
