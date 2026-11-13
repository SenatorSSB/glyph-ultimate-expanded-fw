"""Compile candidate sources against the current generated schema and independent host oracles."""
import json
import shutil
from unittest.mock import patch
import tempfile
from pathlib import Path

import check_glyph_gp_config_017_neopixel_repaired_current as leds
import check_glyph_profile_native_ultimate as native
from check_glyph_stage_b_ultimate_profiles import ROOT, make_v3_artifact, run
import glyph_serial_config_tool as codec
import check_glyph_gp_config014_modifier_capacity as modifier
import check_glyph_gp_kbd_001_keyboard_pipeline as keyboard
import check_glyph_gp_config024_usb_profile_identity as usb_menu
from check_glyph_gp_config024_usb_profile_identity import method_body


def current_native(temp, default_abi):
    pb, json_format, _ = codec.load_runtime_proto_modules(ROOT)
    fixture, _ = codec.encode_artifact_payload(make_v3_artifact(), pb, json_format)
    exe, negative, flags, objects = native.compile_runner(temp, default_abi)
    expected = native.HOST / "independent_legacy"
    corpus = [json.loads(row) for row in (expected / "short-expected.jsonl").read_text().splitlines()]
    assert corpus, "missing independently recorded native vectors"
    context = pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    for row in corpus:
        config = pb.Config.FromString((expected / "corpus" / (row["id"] + ".pb")).read_bytes())
        program, _ = native.convert(config.ultimate_profiles[0], context, pb, "historical_compatibility")
        wire = temp / "corpus.pb"
        wire.write_bytes(program.SerializeToString(deterministic=True))
        assert run([str(exe), str(wire), row["input"]]).split() == [row["buttons"], *map(str, row["axes"])], row["id"]
    program, _ = native.convert(fixture.ultimate_profiles[0], context, pb, "historical_compatibility")
    body = temp / "ordinary.body"
    body.write_bytes(program.native_payload)
    print(run([str(negative), str(body), str(ROOT / "docs/runtime_config/profile_native_ultimate/design_evidence/maximum-native.body")]))
    native.host_admission_tests(pb, fixture)
    native.composition_tests(temp, exe, pb, fixture.ultimate_profiles[0])
    native.full_frozen_replay(temp, flags, objects, pb, fixture)
    native.mutation_controls(temp, flags, objects, pb)
    return flags, objects


def config_boundaries(temp, flags, objects):
    # The current compact store rejects unspecified RGB colors. Its legacy input
    # accepts only an explicitly empty no-op, which the production migration drops.
    source = ROOT / "tools/fixtures/gp_config022_rgb_target_validation/validation_harness.cpp"
    text = source.read_text()
    text = text.replace("c=Config_init_default;c.rgb_configs_count=30;",
        "c=Config_init_default;c.communication_backend_configs_count=1;"
        "c.default_usb_backend_config=1;c.rgb_configs_count=30;")
    text = text.replace("c.default_backend_config=1;", "c.default_backend_config=2;")
    anchor = 'check("legacy20_nine_zero",false);'
    assert text.count(anchor) == 1
    text = text.replace(anchor, 'check("legacy20_nine_zero",true);'
        'c.ultimate_profile_store_format=1;c.ultimate_profile_store_incarnation=1;check("compact20_nine_zero",false);'
        'c.ultimate_profile_store_format=0;')
    harness = temp / "current-rgb.cpp"
    harness.write_text(text)
    validator = ["config/glyph/common/src/glyph_config_validation.cpp", "src/core/config_validation.cpp",
                 "src/core/config_rgb_target_validation.cpp", "src/core/config_button_validation.cpp",
                 "src/core/config_usb_default_validation.cpp", "src/modes/UltimateNativeProfile.cpp"]
    binary = temp / "current-rgb"
    run(["c++", "-std=c++17", *flags, "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
         str(harness), *[str(ROOT / p) for p in validator], *objects, "-o", str(binary)])
    report = run([str(binary)])
    assert "physical=36 other_named=24" in report
    print(report.splitlines()[-1])


def neopixel(temp):
    for ndebug in (False, True):
        binary = temp / ("led-release" if ndebug else "led-debug")
        leds.compile_root(ROOT, binary, ndebug)
        for case in leds.NULLS:
            rows = leds.rows(leds.run(binary, case))
            leds.assert_clock(rows)
            assert len(rows) == 4 and all(r["brightness"] == 0 and r["pixels"] == [0]*76 for r in rows), case
        for case in leds.VALID:
            rows = leds.rows(leds.run(binary, case))
            leds.assert_clock(rows)
            assert all(r["brightness"] == 96 and r["show_delta"] == 1 for r in rows), case
            leds.compare_recovery(leds.run(binary, "recovery_"+case), leds.run(binary, "reference_"+case))
    print("NeoPixel current null, valid and recovery source tests passed in both time layouts")


def chord_capacity(temp, flags):
    source = (ROOT / "src/core/mode_selection.cpp").read_text()
    utilities = (ROOT / "HAL/pico/include/util/state_util.hpp").read_text()
    body = method_body
    start = source.index("constexpr size_t kModeActivationMaskCapacity")
    end = source.index("} // namespace", start)
    globals_start = source.index("uint64_t mode_activation_masks[", end)
    callback_end = source.index("void set_mode_destination_selector", globals_start)
    test = temp / "current-mode-chords.cpp"
    test.write_text("""
#include <cassert>
#include <cstdint>
#include <cstddef>
#include <type_traits>
#include <config.pb.h>
struct InputState { uint64_t buttons = 0; };
struct CommunicationBackend {
    InputState inputs;
    InputState &GetInputs() {return inputs;}
    CommunicationBackendId BackendId() {return COMMS_BACKEND_XINPUT;}
};
namespace senscope::prototype { constexpr bool kEnableSenscopePrototypeManualSelection = false; }
bool TrySelectSenscopePrototypeManualDebugMode(CommunicationBackend **, size_t, const InputState &) { return false; }
using ModeDestinationSelector = void (*)(CommunicationBackendId,size_t,const Config &);
""" + source[start:end] + source[globals_start:callback_end] +
        body(utilities, "inline uint64_t make_button_mask(") +
        body(utilities, "inline bool all_buttons_held(") +
        body(source, "void set_mode_destination_selector(") +
        body(source, "void setup_mode_activation_bindings(") +
        body(source, "void select_mode(") + """
static size_t chosen, calls;
void destination(CommunicationBackendId backend, size_t index, const Config &) {
    assert(backend == COMMS_BACKEND_XINPUT); chosen=index; ++calls;
}
int main() {
    static Config config;
    CommunicationBackend backend, *backends[] = {&backend};
    set_mode_destination_selector(destination);
    for (size_t n : {0u, 10u, 11u, 13u, 30u, 31u}) {
        config.game_mode_configs_count = n;
        for (size_t i=0; i<30; ++i) {
            mode_activation_masks[i]=0xdead;
            config.game_mode_configs[i].activation_binding_count=1;
            config.game_mode_configs[i].activation_binding[0]=static_cast<Button>(i+1);
        }
        setup_mode_activation_bindings(config.game_mode_configs,n,0);
        const auto before=calls;
        for(size_t i=0; i<30; ++i) {
            assert(mode_activation_masks[i] == (i<n && n<=30 ? (uint64_t(1)<<i) : 0xdead));
            backend.inputs.buttons=0; select_mode(backends,1,config);
            backend.inputs.buttons=uint64_t(1)<<i;
            const auto previous=calls; select_mode(backends,1,config); select_mode(backends,1,config);
            if(i<n && n<=30) {assert(calls==previous+1 && chosen==i);}
            else {assert(calls==previous);}
        }
        assert(calls-before == (n<=30?n:0));
    }
}
""")
    exe = temp / "current-mode-chords"
    run(["c++", "-std=c++17", "-include", "initializer_list", *flags, "-fsanitize=address,undefined",
         "-fno-sanitize-recover=all", str(test), "-o", str(exe)])
    run([str(exe)])


def modifiers(temp, short):
    binary = temp / "modifiers"
    compiled = modifier.compile_host(ROOT, binary, short, temp/"generated")
    assert compiled.returncode == 0, compiled.stderr
    for case in modifier.CASES:
        result = modifier.run(binary, case)
        assert result.returncode == 0 and "case="+case+" PASS" in result.stdout, (case, result.stderr)


def keyboard_pipeline(temp):
    for name in (*keyboard.SOURCES, *keyboard.HOST_PATHS):
        target = temp / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    expected = json.loads((ROOT / keyboard.FIXTURE).read_text())["observations"]
    assert keyboard.run_host(temp, sanitize=True) == expected
    assert keyboard.behavioral_negatives(temp) == 5
    print("Keyboard pipeline, held keys, release and report behavior matched 104 rows; five source mutants rejected")


def current_usb_menu(tmp):
    root = ROOT
    for name in (usb_menu.INPUT_MODE, usb_menu.MODE_SETUP, usb_menu.PRODUCTION):
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, tmp / name)
    shutil.copytree(root / usb_menu.HOST, tmp / usb_menu.HOST)
    stubs = tmp / usb_menu.HOST / 'include/host_stubs.hpp'
    text = stubs.read_text().replace('struct GameModeConfig {', '''
struct UltimateProfile {};
struct ProfileStore {
    static constexpr unsigned kCompactConfigFormat = 1;
    enum class Status { Ok, RecoveredPrevious };
    const UltimateProfile* Activate(unsigned, Status *status) { *status = Status::Ok; return nullptr; }
    std::nullptr_t ActiveNativeView() { return nullptr; }
};
inline ProfileStore profile_store;
struct GameModeConfig {
    unsigned ultimate_profile_id = 0, ultimate_profile_config = 0;''').replace('struct Config {', '''struct Config {
    unsigned ultimate_profiles_count = 0, ultimate_profile_store_format = 0;
    UltimateProfile ultimate_profiles[1]{};''').replace('class StubMode : public ControllerMode {','''class StubMode : public ControllerMode {
  public:
    void SetConfig(GameModeConfig& row, const UltimateProfile*, std::nullptr_t = nullptr) { InputMode::SetConfig(row); }''')
    stubs.write_text(text)
    main = tmp / usb_menu.HOST / 'main.cpp'
    text = main.read_text().replace('CHECK(current_mode_index == SIZE_MAX);','CHECK(current_mode_index == static_cast<size_t>(&row - config.game_mode_configs));')
    main.write_text(text)
    expected = json.loads((root/usb_menu.FIXTURE).read_text())['expected_host_output']
    for mode in ('default-enum', 'short-enum'):
        with patch.object(usb_menu, "ROOT", tmp):
            output = usb_menu.compile_and_run(mode)
        assert output == expected, (mode, output, expected)
        print(mode, output)



def main():
    for default_abi in (False, True):
        with tempfile.TemporaryDirectory(prefix="glyph-firmware-regressions-") as directory:
            temp = Path(directory)
            flags, objects = current_native(temp, default_abi)
            config_boundaries(temp, flags, objects)
            modifiers(temp, not default_abi)
            chord_capacity(temp, flags)
            if default_abi:
                neopixel(temp)
                keyboard_pipeline(temp / "keyboard")
                current_usb_menu(temp / "usb-menu")
    print("Current two-ABI configuration and native runtime checks passed")


if __name__ == "__main__":
    main()
