# Glyph capabilities

Implementation, stock exposure, product workflow, managed-package support,
Senscope support and physical qualification are separate claims. The sections
below are scoped inventories, not a promise that every mode/backend combination
works. [Current state](CURRENT_STATE.md) owns exact hardware identities;
[usage](USAGE.md) describes today's limited workflow.

## Mode engines

Nine concrete engines are dispatched in
[mode selection](../src/core/mode_selection.cpp). The
[stock defaults](../config/glyph/common/include/glyph_overrides.hpp) expose 13
rows using eight engines. A stock label is not a mode engine: Brawl uses Project M;
GameCube/N64 use Melee; SNES/NES use FGC.

| Engine | Source implementation | Stock exposure | Product/package/physical scope |
| --- | --- | --- | --- |
| Melee, Project M, FGC | Implemented | Present | Stock rows; no new physical qualification claimed here |
| Rivals of Aether, Rivals 2, Smash64 | Implemented | Present | Stock rows; no new physical qualification claimed here |
| Ultimate | Implemented, including bounded native evaluator | Present | Native authoring and managed Ultimate lane below; selected physical routes only |
| Keyboard | Implemented mode through DInput | Present | Deferred product/physical scope; Keyboard is not a backend |
| Custom / MODE_CUSTOM | Implemented | No stock row | Later product evaluation; no qualification claimed |

## Communication backends

The Mk6 Pico [constructors](../HAL/pico/src/comms/backend_init.cpp) and
[defaults](../config/glyph/common/include/glyph_overrides.hpp) expose eight
backend implementations. These are transports/output paths, not profile kinds.

| Backend | Source/default exposure | Qualification / workflow boundary |
| --- | --- | --- |
| XInput | Implemented / default entry | Selected Windows joy.cpl route PASS |
| DInput | Implemented / default entry; gamepad and keyboard descriptors | Selected packet physical N/A; Keyboard is a mode executed through DInput |
| Nintendo Switch USB | Implemented / default entry | Original Switch/Ultimate selected route PASS; Switch 2 out of scope |
| GameCube | Implemented / default entry | Actual adapter to original Switch/Ultimate selected route PASS |
| N64, NES, SNES | Implemented / default entries | No current first-beta physical qualification claimed |
| Configurator | Implemented / default entry | Firmware configuration/management transport, not a gameplay engine or the retired official website |

PS4/PS5 enum presence in the [schema](../schema/haybox/config.proto) does not
establish a Mk6 backend: those IDs have no constructor in the cited dispatcher.
Browser Gamepad API compatibility is NOT_QUALIFIED, not implied by USB support.

## Native Ultimate profiles

The current [v1 authoring entry point](../profiles/README.md) supports offline
validate/compile/report using profile-owned symbolic tables and finite rules.
Production bounds come from the [native validator](../src/modes/UltimateNativeProfile.cpp)
and [body constants](../include/modes/UltimateNativeProfile.hpp), not older
protobuf role-array capacities.

| Resource | Native capacity |
| --- | ---: |
| Physical coordinate table slots | 28 |
| Declared v1 tables | 1–28 |
| Direction states per table | 9, including 5 / no direction |
| Conditions | 96 |
| Tokens per condition: all / any / none | 2 / 4 / 9 |
| Total condition-token pool | 768 |
| Direction sources | 1–8 |
| Table rules | 32 |
| Digital bindings | 32 |
| Analogue effects | 16 |
| Native body bytes | 3336 |

These bounds apply together; byte, token and graph constraints still govern
admission. The [compiler](../tools/glyph_native_profile_json.py) fills undeclared
wire slots with neutral points. Every declared table supplies all nine absolute
raw `[x,y]` coordinates, components 0..255. Direction 5 can be non-center; input
RIGHT can intentionally select a DOWN-LEFT output.

The [evaluator](../src/modes/UltimateNativeEvaluator.cpp) separately resolves
conditions, table selection, digital bindings and analogue activation/gates.
One input can participate in several mechanisms. In ordinary remapping, each physical input maps to one destination; multiple
physical inputs may share a destination, as documented in
[Config's schema](../schema/haybox/config.proto).
“Subsystem/sublayer” means coordinated rules sharing conditions, not a separate
native collection type or arbitrary nesting. No timers, persistent toggles,
scripts or automated sequences are supplied by this finite native program.
There is no automatic character-facing awareness or game-move guarantee.

These native capabilities are implemented, exposed by offline authoring and used
by the managed Ultimate lane. They do not establish finished Senscope support or
physical coverage of every authored program. Keep the human v1 source: wire
bytes cannot recover its names/declaration intent. The historical v0 golden is
retained evidence, not the current authoring starting point.

## Profile and package management

| Scope | Implemented / exposed | Limits and acceptance boundary |
| --- | --- | --- |
| Config profile rows | Row preprocessing, bindings, layout, backend applicability and references | Maximum **30 profile rows total**, a shared 30-row budget including retained stock/other modes; [schema options](../schema/haybox/config.options) |
| ProfileStore | Persistent record/directory storage, revisions, read/management primitives and boot-bound native activation | [Directory maximum 64](../include/core/ProfileStore.hpp), separate from row budget and available storage; not 64 complete selectable packages |
| Complete managed package | Dedicated Ultimate row + dedicated native record, metadata/plate and optional RGB; CREATE/QUERY and lifecycle source | [Package schema](../schema/haybox/package.proto), [Mk6 feature flags](../platformio.ini), [storage implementation](../HAL/pico/src/core/ProfileStore.cpp); source existence is not complete user UX or physical lifecycle qualification |
| Offline authoring | Native v1 JSON validate/compile/report | Does not install a complete package |
| Existing production store tool | [Protocol-2 ProfileStore tool](../tools/glyph_profile_store_production_tool.py) | A record-management tool, not a complete package installer or finished Senscope Builder path |
| Ordinary managed selection | Existing menu/reference primitives; target package workflow outstanding | Boot-bound activation, no arbitrary live hot-swap; stored labels alone do not prove execution |
| Senscope | Separate accepted read/store/reference episodes exist | Complete Builder/package/install/readback/execution acceptance against eventual frozen firmware remains separate |

Profile-owned remaps/SOCD and native rules coexist with device-global backend
destinations, overall RGB brightness and some mode options. The row and native
record are different objects; one logical managed profile owns both without
sharing. See [Config](../schema/haybox/config.proto) and [usage](USAGE.md).

## Display, menu, RGB and optional subsystems

Display/menu and NeoPixel code exists in the
[Glyph configuration](../config/glyph/common/src/config.cpp), separately from
engines and backends. The accepted dashboard observation was KazTest5 / Unknown
Plate / XInput with executing native identity proof. Input Viewer naming remains
NOT_VISIBLE / NOT_VERIFIED, and managed activation/display and known-plate cases
retain separate NOT_TESTED scope in the
[accepted display record](runtime_config/package_active_profile_display/integration_20261113/README.md).
This is not blanket UI/RGB qualification.

[Nunchuk input](../HAL/pico/src/input/NunchukInput.cpp) is an optional subsystem,
not a mode. Mk6 [pin defaults](../config/glyph/glyph_mk6/include/glyph_pinout.hpp)
set detect/SDA/SCL to `-1`; source existence does not establish out-of-box Mk6
availability. Nunchuk remains **NOT_TESTED**.

## Physical qualification and open capabilities

Only the [selected exact firmware packet](CURRENT_STATE.md) has the recorded
first-beta physical PASS. DInput was N/A; browser/JoyCheck NOT_QUALIFIED;
Keyboard deferred; Switch 2 out of scope/not tested; Nunchuk NOT_TESTED;
Fresh Install/recovery deferred/unqualified. API-visible preservation is not
raw-flash equality. No general backend cross-product, adapter, macro, gameplay
or tournament-approval claim follows.

[Roadmap](ROADMAP.md) distinguishes near-term preparation from conditional
Keyboard, Custom, recovery, browser, boot-time, Switch 2 and other-family work.
The [implementation boundary](runtime_config/IMPLEMENTATION_BOUNDARY.md)
preserves the accepted bounded native lane and restrictions on generic expansion.
