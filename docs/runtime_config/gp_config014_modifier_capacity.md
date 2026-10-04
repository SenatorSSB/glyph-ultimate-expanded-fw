# GP-CONFIG-014 repaired-current modifier capacity host proof

This proof binds the exact adopted production header
`9658f5e15f50887caaaf5a71efc0096e9677d144` and implementation
`8cb336f31acd4c324b3ae1f8ef0827c14f15ee85` to canonical base
`8b8e45b17a5670bbf983360faf87bdf9d6b50ce2`. The checker independently pins
source and dependency hashes; editing the JSON fixture cannot authorize changed
production bytes. The four new host/proof paths and four existing validation
metadata paths form a finite candidate inventory with those two production
paths. The committed candidate must be a direct child of that base.

Run `python3 -B tools/check_glyph_gp_config014_modifier_capacity.py`.
It builds host executables from the production CustomControllerMode header and
implementation, included once, plus the real ControllerMode, InputMode and
SOCD sources. It uses the authenticated tracked GP-CONFIG-012 generated header
and Nanopb 0.4.9.2 closure; the historical GP-CONFIG-011 generated header remains
separate, immutable evidence. Both ordinary and short enum layouts compile all
translation units consistently. Address, undefined behavior and bounds
sanitizers stop on the first error. Pattern initialization makes omitted
initializers detectable without zeroing the constructed object's storage.

Each layout runs 30 cases: normal unconfigured construction; fresh accepted
counts 0 through 20, checking every cache mask and active/inactive modifier
outputs; order, combo filtering, direction priorities, trigger priorities and
source-supported compound/override arithmetic; direct counts 21 and pb_size_t
maximum in fresh and seeded instances; poisoned live counts 21 and maximum;
and the historical stale same-session cache observation. Oversize direct calls
preserve the entire object representation, prior InputMode pointer and pointed
GameModeConfig, prior custom config and outputs. Live analog refusal preserves
those values while the modifier cache and modifier/direction/analog arrays are
ASan-poisoned, with the count readable. Digital processing retains its existing
policy. Injected Nunchuk inputs check source arithmetic only.

Disposable negative overlays cover a ten-entry cache, missing direct/live
guards, missing pointer/cache initializers, a one-byte production substitution,
mutable fixture resealing, executable mode, symlink, adjacent inventory path
missing inventory members, wrong/missing/merge parents, candidate host mode
and extra critical source. Generated extents 19 and 21 must fail the production
header's equality assertion in both enum layouts. Real source, schema,
historical assets and the repository index are never modified by these tests.
The checker compares the complete critical tree to the base with exactly the
two adopted substitutions and verifies dependency custody and worktree bytes.

The current campaign guards still reject the two changed production paths
until GP-VAL-034 supplies its separately reviewed exact correspondence. This
standalone proof does not import or bypass that campaign gate. Historical
GP-CONFIG-011 and rebinding fixtures/checkers remain unchanged. The stale cache
observation is preserved; GP-CONFIG-018 coherence remains separate.

Host success does not establish a firmware build, physical reachability or
controller acceptance. Firmware build, exact artifact custody, physical PASS
and integration remain gated. Nunchuk remains NOT_TESTED and root cause remains
UNPROVEN. No configuration, persistence, device write or flashing action is
performed.
