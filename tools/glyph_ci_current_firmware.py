"""Compile candidate sources against the current generated schema and independent host oracles."""
import json
import tempfile
from pathlib import Path

import check_glyph_gp_config_017_neopixel_repaired_current as leds
import check_glyph_profile_native_ultimate as native
from check_glyph_stage_b_ultimate_profiles import ROOT, make_v3_artifact, run
import glyph_serial_config_tool as codec


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


def main():
    for default_abi in (False, True):
        with tempfile.TemporaryDirectory(prefix="glyph-firmware-regressions-") as directory:
            temp = Path(directory)
            flags, objects = current_native(temp, default_abi)
            config_boundaries(temp, flags, objects)
            if default_abi:
                neopixel(temp)
    print("Current two-ABI configuration and native runtime checks passed")


if __name__ == "__main__":
    main()
