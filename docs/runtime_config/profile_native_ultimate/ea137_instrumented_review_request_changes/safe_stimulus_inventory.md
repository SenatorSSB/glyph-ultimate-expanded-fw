# Native packet safe-stimulus inventory

Frozen source: `ea137fc1f61d6acc0f1475c4165263eb661775da`, tree `9000056d2584f65a7ae8b40032c480d5a2250d28`. Recommendation only; five variants and their oracle results remain ungenerated. Requested/observed model: UNKNOWN, not attested.

Use packet-only carrier mapping **49 → LF6=6, 50 → LF7=7, 51 → LF8=8**. These are actual mapped Mk6 ordinary inputs, not assumed spare enum IDs. No references to6/7/8 occur in any token field of any of the13 frozen native bodies (including original/remapped/post domains, conditions, sources, rules, digital bindings, effect gates, header gates and digital post-mask gate), in any of their13 preprocessing contexts, or in any of the495 original stimuli. The JSON records the complete inventory and hashes.

| Old carrier | Proposed carrier | Matrix cell (zero-based) | Row / column GPIO | Existing meaning and explicit proposed addition |
|---|---|---|---|---|
|49 MB1|6 LF6|row2,col3|24 /12|No meaning in these13 native packages; original6=A, plus POST6 Down in complete samples|
|50 MB2|7 LF7|row1,col3|25 /12|No meaning in these13 native packages; original7=A plus priority3/table19 in complete samples|
|51 MB3|8 LF8|row1,col2|25 /13|No meaning in these13 native packages; original8=A+triggerLDigital+triggerRDigital(mask193) in complete samples|

Correction to preliminary transport: LF7/LF8 are **row1**, not row2. Matrix source is decisive. Mk6 matrix is `config/glyph/glyph_mk6/include/matrix_definition.hpp:8-18`; enum identities are `schema/haybox/config.proto:40-47`. Full-layout display coordinates independently name these ordinary buttons at `config/glyph/glyph_mk6/include/button_positions.hpp:42-44`. Source mapping does not confirm the owner unit's revision or physical button accessibility.

## Input and shortcut source evidence

`config/glyph/common/src/config.cpp:47-52,61-64` selects the debounced matrix as the sole input source with COL2ROW. `include/input/SwitchMatrixInput.hpp:29-39,61-78,97-98` drives a row low and reads active-low columns, then restores pullups; `HAL/pico/include/input/DebouncedSwitchMatrixInput.hpp:15,25-34` uses default5ms debounce. GPIO numbers are passed directly to Pico `gpio_get/gpio_put/gpio_init` in `HAL/pico/include/gpio.hpp:16-21` and `HAL/pico/src/gpio.cpp:6-18`. They are GPIO IDs, not physical connector pin numbers.

Original49/50/51 are unsuitable hardware carriers. `config.cpp:170-202` checks raw MB1 at startup and routes to bootloader. `config.cpp:407` maps display back/down/up/enter to49/51/50/52. `src/comms/IntegratedDisplay.cpp:67-80` reads original shared inputs, independently of gameplay remapping. `HAL/pico/src/display/InputDisplay.cpp:20-27` opens the config menu on back; `HAL/pico/src/display/ConfigMenu.cpp:31-83` navigates on up/down and invokes actions on enter. Changing an Ultimate remap cannot remove these paths.

Default Ultimate explicitly disables LF8/LF7/LF6 in `config/glyph/common/include/glyph_overrides.hpp:109-116`. The proposed **packet** contexts must replace those remaps exactly; applying only a profile to an arbitrary existing context is insufficient. `src/core/ControllerMode.cpp:17-24` creates original, remapped and post-SOCD snapshots, `src/core/InputMode.cpp:57-85` preserves unremapped inputs, and `src/modes/UltimateNativeEvaluator.cpp:5-15` defines the three distinct input token domains.

Default backend startup holds are RF3=19(DInput), RF2=18(Switch), LT1=33(NES), LT2=34(SNES), RT2=42(Configurator), per `glyph_overrides.hpp:623-658` and `src/core/config_utils.cpp:8-23` / `HAL/pico/src/comms/backend_init.cpp:271-284`. None is6/7/8. Default game-mode rows contain no activation_binding initializers. **Actual owner Config remains unknown.** Runtime mode switching reads original physical buttons and consumes any nonempty matching mode chord at `src/core/mode_selection.cpp:230-250`; setup builds those masks at253-268. `HAL/pico/include/util/state_util.hpp:26-35` shows a nonempty subset match; empty bindings do not match. For each planned physical set S, the fresh Config must establish that no nonempty game-mode chord C is contained in S. Existing remaps/SOCD cannot neutralize a conflicting raw chord. Release all inputs before any reboot/reconnect, including the original packet's ordinary startup-sensitive stimuli.

## Minimal separate packet variants

Preserve the existing13 packages and original495-row host catalog byte-for-byte. Add five distinctly named packet-only variants (three forced, two complete), with39 separately identified sequence rows. Original source locations are `prepare_hardware_fixtures.py:60-66,82-84`; the helper at `tools/check_glyph_profile_native_ultimate.py:150-174` hardcodes49/50/51 and therefore needs an explicit packet-only carrier choice instead of silently changing the original host capacity proof.

For forced_wins/loses/filter, keep the exact empty-remap/empty-SOCD context, use `physical_input=6`, retain table3/coordinates/priorities/winner-filter semantics, and bind both the original-domain A gate and forced-table gate to6. The converter source defines these at `tools/convert_glyph_native_ultimate_profile.py:220-226,265-267`. Proposed sequence: `[],[6],[6,24],[6,5],[6,2],[24],[]`.

For complete_sample_1/2, use exact empty remaps plus SOCD_NEUTRAL pair(6,2). Re-convert the same immutable legacy source with that context, add POST6 to the Down OR condition, use original7 for priority3/table19, and use original6/7/8 digital masks1/1/193. Preserve table19 values `(78,84)` / `(79,85)` and all other source-family/effect data. Proposed sequence: `[],[8],[6],[6,2],[7],[6,7],[6,7,8],[2],[]`. Recompute the ordered preprocessing digest and derivation identity, body/wrapper hashes, context bytes, conversion metadata and manifest; a bare text substitution does not establish an admitted package (`convert...py:120-132,183-184,270`; `complete_profile:162-171`). No remap to old MB IDs is needed.

The proposed renaming has no intrinsic native carrier conflict in this frozen packet. Output equivalence is a source-backed inference until root/writer executes the production evaluator and serializer on the generated variants. This probe generated no profile, context, observed output or candidate file. It does not replace the original495 host cases or the20-profile host storage proof.

Mask193 means A plus the two digital trigger bits (`include/core/state.hpp:112-119`), with existing trigger effects. XInput serializes those digital triggers as255 (`HAL/pico/src/comms/XInputBackend.cpp:49-56`); native Switch uses zl/zr (`NintendoSwitchBackend.cpp:127-140`); GameCube uses l/r (`GamecubeBackend.cpp:45-65`). These are source assignments, not host/adapter observations or gameplay semantics.

## Exact unverified remainder

- Owner reports tentative Mk6. Physical revision, present/accessible LF6/LF7/LF8 and actual row/column wiring are unverified on that unit.
- Fresh owner Config mode chords, startup backend bindings and full packet context/reference readback are unverified. A raw mode-chord collision is an irreducible Config-dependent conflict for any chosen carrier; choose another sourced carrier or obtain separately scoped packet authority rather than silently edit owner chords.
- Five variant artifacts, context digests, manifests and39 production evaluator/serializer oracle rows are not generated or executed here. Root/writer must finish those checks and rebind findings to its final exact source candidate; concurrent source changes are outside this frozen inventory.
- Exact candidate/UF2/custody, concrete owner packet approval, original/current backups, device operations and restoration remain outside this probe.
- Available reported routes: USB XInput, USB Switch, GameCube adapter→Switch. Adapter model, downstream translation and raw-output observer are unknown. B0XXInputViewer physical-input feedback cannot establish native/backend outputs. No physical PASS, timing/stack measurements, or GameCube→Switch report equivalence is claimed. Nunchuk NOT_TESTED; root cause UNPROVEN.

## Source pins

All pins, all42 mapped cells, all13 package/body/context hashes and decoded carrier-reference locations are in `/private/tmp/glyph-native-safe-stimulus-inventory.json`. Primary SHA-256 values:

- `config/glyph/glyph_mk6/include/matrix_definition.hpp`: `c7782c507912c45b1c282027f3ba24ab43f526e653ef2dd426fa8159973fc0f1`
- `config/glyph/glyph_mk6/include/glyph_pinout.hpp`: `1ac5e4278fb72b8c918a6bb307521927afb8d27142aba278bd0f7bfb219e4ab6`
- `config/glyph/glyph_mk6/include/button_positions.hpp`: `73b84b62bec59650ed5a027b0d6100bb09109618c65611ca6bf37b8877736e2f`
- `include/input/SwitchMatrixInput.hpp`: `9f7fa65db078877d53cc851c8a906ac6c37ddbbb615f28266fc35bcd301f88f6`
- `HAL/pico/include/input/DebouncedSwitchMatrixInput.hpp`: `45c3dfd010eebbcce79329df30f71f3d25a33759b30ecbe9fe2cc95fa1e5df30`
- `HAL/pico/include/gpio.hpp`: `0a1bf79395451be05260e928a2c5197e2804f04e9d375f43d35378f1bc406553`
- `HAL/pico/src/gpio.cpp`: `141d0d3ce6bfa98ea2883086963a0517967f74629617510a9f8f7918abc2973c`
- `HAL/pico/include/util/state_util.hpp`: `db4b4ee7dcfe462dd00097a5109e028787e11d7868b012f447c9fee84e68ea81`
- `config/glyph/common/src/config.cpp`: `5b407ecb9283ea311cd1c033abcc6a5baff2a8a42ad3ffacbbf4974e683177bc`
- `config/glyph/common/include/glyph_overrides.hpp`: `7a1bc4b09745767d7a34d4b2495edfe22af5d3b4b960eb822c361ac16590803c`
- `src/comms/IntegratedDisplay.cpp`: `37213732b17e8d911ecdb22908a005cc792540f4f4cd67b3c986ecfcdeed006e`
- `HAL/pico/src/display/InputDisplay.cpp`: `761f3a5bb6357a278042356e25c691ef82bb45030ee6588cd6571a08e2e6480b`
- `HAL/pico/src/display/ConfigMenu.cpp`: `5772d5accd688ffe176d968146c02c17682512c9551348438d6a7a76e94a57be`
- `src/core/mode_selection.cpp`: `f395110a5d1df8a762bccee9c977e6cbd13374ba2c5c12222969207a0c47acb6`
- `src/core/config_utils.cpp`: `b97af928bff72103f90b0155e4e63fd44a3cfcb84e46ac93cf74f6f3227e02ab`
- `HAL/pico/src/comms/backend_init.cpp`: `057e4eb529fd9d9fbe94872ee73f0a64799ce77cdfc7f32c367775c9293c27d0`
- `src/core/ControllerMode.cpp`: `501de8537c8274e6cf42d1f182e9daba14e951261476b3b9642e73eda895f8a0`
- `src/core/InputMode.cpp`: `080bcc65bb83b1b896a2b4efa6ea9e9d304071ee30f279fe3386ff2c29cc85c7`
- `src/modes/UltimateNativeEvaluator.cpp`: `e35ca0ee79dc5add52205361a8954da8d11e24680400c505b7b1c9a19de13f08`
- `include/core/state.hpp`: `c46eb5347843ac4574dcffb28faeace608f029c27b94690c02ce06981cc4e6a3`
- `schema/haybox/config.proto`: `1e65f3f62f8a7f220c480217722f0e96ad2d48f9c274b462e5494a68ef15edec`
- `config/glyph/env.ini`: `ab5aff0bb43b47a18f460bd9504ce327e0c5db04568672c26b50de54fd396d36`
- `tools/convert_glyph_native_ultimate_profile.py`: `d6a84657308ee957172185de2393205cf849465416c2f7e250a91e27774d293f`
- `tools/check_glyph_profile_native_ultimate.py`: `b3c30c4810d85091a6b7e40356194a0b364f00864f25f5560c56a49120b85163`
- `tools/check_glyph_stage_b_ultimate_profiles.py`: `b9c8d1afd6f84f075a496fad75d49ba7fc7f877fbec38049e343e00b11722769`
- `tools/fixtures/stage_c_ultimate_profiles_fixture.json`: `8cb2b68d4d99c162d543077e8f7b8f30f646401c7d9710c34fd92cdadd5d64d1`
- `docs/runtime_config/profile_native_ultimate/prepare_hardware_fixtures.py`: `cc2746f83ae17da1841f4e940ec48956511cb0d852e359f5dab4280415c07551`
- `docs/runtime_config/profile_native_ultimate/native_context_operator.md`: `aa82cfd39ef3fe83f106c50e8174b96d475179deb77bf0a02099d46b66db06c6`
- `docs/runtime_config/profile_native_ultimate/candidate_fixture_packet/profiles.json`: `5c62f51ff3c5dc2d61f25991384b0c777a4dcb10a1c0b1b1305a0855b55af163`
- `docs/runtime_config/profile_native_ultimate/candidate_fixture_packet/manifest.json`: `f58a0bd36b668a3b70408c48235bc06869a6b7c4e518530aff2a00d6978e7cf1`
- `docs/runtime_config/profile_native_ultimate/candidate_fixture_packet/expected_observations.json`: `e2cf3540b28519c06dc66a9f11a17a19fb08536cecfc4808e1dd2d3d533481bd`

Scope: exact git archive plus read-only inspection; only this report and its JSON written. No source/device/network/publication work.
