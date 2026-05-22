# G4 - G1/G2/G3 Review and Next Queue

Status: complete (workflow normalization only)  
Date: 2026-05-23  
Branch inspected: `docs/senscope-glyph-baseline`  
Scope: review and queue normalization only; no firmware/source/runtime implementation

## 1. Scope

Reviewed:
- `docs/project/G1_GLYPH_REPO_INVENTORY_AND_ARCHITECTURE_MAP.md`
- `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`
- `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
- the standing workflow and boundary docs that frame those three milestones

Intentionally not changed:
- firmware behavior
- backend runtime behavior
- neutral profile schema
- Senscope game-semantic source authority
- export/push workflows
- runtime adapter implementation

This was a documentation and queue-normalization pass only. No firmware/source/runtime implementation was performed.

## 2. G1 summary

G1 established the repo inventory and architecture map in [docs/project/G1_GLYPH_REPO_INVENTORY_AND_ARCHITECTURE_MAP.md](./G1_GLYPH_REPO_INVENTORY_AND_ARCHITECTURE_MAP.md).

Key knowns:
- the repo is split across firmware core, mode logic, HAL/backend layers, glyph config overlays, and docs/research/reference material;
- the source-backed areas to watch are `include/core`, `src/core`, `include/modes`, `src/modes`, `config/glyph`, `HAL/pico`, and the staged reference material under `docs/sources/raw`;
- the wrapper command policy is explicit: verify `./scripts/pio-local.sh` and `./scripts/build-glyph-mk6-quiet.sh` before relying on them;
- the main unknowns were deeper mode coverage, display/RGB significance, and how far existing reference artifacts can be treated as current runtime authority.

## 3. G2 summary

G2 extracted the controller capability surface in [docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md](./G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md).

Key knowns:
- input/output surfaces are source-backed at the bitfield and byte-output level;
- SOCD, remap, layer/mode, and chord behavior are present, but scope matters;
- Ultimate mode is a hardcoded mode-specific realization path, while `CustomControllerMode` is the data-driven/configurable path;
- capability claims are explicitly separated into source-backed, inferred, unknown, and unsupported-by-current-source;
- generic full 9-way directional support and a first-class neutral `5` were not proven as universal backend capabilities.

## 4. G3 summary

G3 defined the neutral-profile integration boundary in [docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md](./G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md).

Key boundaries:
- the Senscope neutral profile remains app-owned;
- the backend capability model is source-referenced for every claim;
- the realization evaluator is conservative and keeps unknowns distinct from unsupported cases;
- evaluation stays at Level 0/1 near term;
- export, push, and runtime adapter work are deferred and require explicit approval plus source authority.

## 5. Consistency check

| Topic | G1/G2/G3 state | Consistency result | Notes |
|---|---|---|---|
| game semantics boundary | explicitly out of scope / must not be invented | consistent | All three docs keep Smash semantics out of the Glyph repo authority boundary. |
| neutral profile schema boundary | owned by Senscope / not changed here | consistent | G3 makes this explicit and G1/G2 stay inside backend-only analysis. |
| runtime adapter boundary | deferred until review/approval | consistent | G3 defers it; queue now stops after G4. |
| firmware behavior boundary | no undocumented behavior claims | consistent | G1/G2 rely on inspected source, and G3 keeps inference conservative. |
| export/push boundary | unsupported unless source-backed and approved | consistent | G2 and G3 both keep export/push separate from runtime realization. |
| mode-specific vs generic capability boundary | mode-specific behavior must not become generic support automatically | consistent | This is a central G2/G3 rule, especially for Ultimate and `CustomControllerMode`. |
| source-reference requirements | every claim must be source-refed or marked unknown/inferred | consistent | G2 and G3 both preserve the source-reference discipline. |
| active queue state | initial sequence complete, stop before runtime work | consistent | This is the G4 normalization target. |

## 6. Issues found

- Non-blocking wording risk: `docs/sources/README.md` was already identified in G1 as stale relative to staged reference artifacts now present under `docs/sources/raw/`. This does not block G4, but it is worth cleaning up later if the docs inventory is revisited.
- Non-blocking ambiguity: some G2/G3 phrases around export and push remain deliberately conservative, which is correct, but future readers may still want a short reminder that device-side config handlers are not the same as an approved host-side workflow.

No blocking contradictions were found between G1, G2, and G3.

## 7. Decisions preserved

- no gameplay semantic changes in the Glyph repo
- no runtime adapter until the review boundary is complete
- no export/push without explicit source authority and approval
- mode-specific behavior must not become generic support automatically
- unknown stays unknown

## 8. Recommended next phase options

| Option | Purpose | Allowed scope | Stop conditions | Recommended model | User approval required |
|---|---|---|---|---|---|
| G5 - Non-runtime capability model schema draft | sketch the source-refed capability model shape | docs/design only; no runtime code | stop if it drifts into schema commitment or runtime behavior | conservative, source-referenced, mode-scoped | no, unless the draft would change schema authority |
| G6 - Evaluator contract tests using mock capabilities | define evaluator behavior against mocked capability inputs | code/test scaffold only | stop if it depends on undecided backend behavior or Senscope semantics | source-backed, mock-driven, conservative classification | yes, after G5 and before any code scaffold |
| G7 - Firmware custom mode design spike | explore a custom mode design path | design only; no implementation | stop if it requires firmware behavior commitments or schema changes | mode-specific, source-backed, explicitly bounded | yes |
| G8 - Realization evaluator prototype | prototype evaluator logic for backend realization | prototype only, no runtime adapter or export/push | stop if it becomes runtime adapter work or broadens scope into game semantics | conservative, level 0/1 first, source-refed | yes |
| G9 - Source inventory expansion | fill remaining evidence gaps | docs/source inspection only | stop if it turns into implementation or unsupported inference | source-first, gap-driven, non-committal | no unless new source-authority questions appear |

## 9. Recommended immediate next action

Stop for human review of G1-G3. The queue had already been framed to stop after G3, and G4 should serve as the normalization point before any runtime implementation work is considered.

Proceed to G5 only if the user explicitly asks for a docs/schema draft.

## 10. Verification

Commands run:
- `git status --short --branch`: branch is `docs/senscope-glyph-baseline` tracking `origin/docs/senscope-glyph-baseline`
- `git branch --show-current`: `docs/senscope-glyph-baseline`
- `git remote -v`: `origin` points to `https://github.com/SenatorSSB/glyph-ultimate-expanded-fw.git`; `upstream` points to `https://github.com/LimitLabs/FW-Glyph.git`
- `git diff --stat`: clean before edits
- `sed -n '1,260p'` and `sed -n '261,520p'` on the required workflow docs and the G1/G2/G3 milestone docs

Build was not run because this was a docs-only task.
