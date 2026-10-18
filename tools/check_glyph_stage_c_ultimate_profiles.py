#!/usr/bin/env python3
"""Actual Ultimate output path versus frozen Stage-B source, plus strict admission."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from check_glyph_stage_b_ultimate_profiles import ROOT, NANOPB, make_v2_artifact, make_v3_artifact, make_v4_artifact, run, require

HOST = ROOT / "tools/fixtures/stage_c_ultimate_profiles_host"
ARTIFACT = ROOT / "tools/fixtures/stage_c_ultimate_profiles_dry_run.json"

# This gate belongs to the Stage-C fixture handoff only. Generic Config
# validation intentionally continues to accept source-valid Configs that do
# not provide a Configurator recovery binding.
FINAL_GATE_CONFIGURATOR_RECOVERY_REQUIRED = True


def verify_stage_c_recovery_envelope(config, pb) -> None:
    require(FINAL_GATE_CONFIGURATOR_RECOVERY_REQUIRED,
            "Stage-C handoff must require the Configurator recovery envelope")
    backend_count = len(config.communication_backend_configs)
    mode_count = len(config.game_mode_configs)
    require(backend_count == 3, "Stage-C fixture requires exactly XInput, GameCube, and Configurator backends")
    require(1 <= config.default_backend_config <= backend_count,
            "Stage-C default backend index is outside the fixture backend configs")
    require(1 <= config.default_usb_backend_config <= backend_count,
            "Stage-C default USB backend index is outside the fixture backend configs")
    for index, backend in enumerate(config.communication_backend_configs, start=1):
        require(1 <= backend.default_mode_config <= mode_count,
                f"Stage-C backend {index} default mode index is outside fixture game modes")
    backends = list(config.communication_backend_configs)
    require([backend.backend_id for backend in backends] == [
                pb.COMMS_BACKEND_XINPUT,
                pb.COMMS_BACKEND_GAMECUBE,
                pb.COMMS_BACKEND_CONFIGURATOR,
            ], "Stage-C backend envelope drifted from XInput/GameCube/Configurator")
    require(backends[0].default_mode_config == 1,
            "Stage-C XInput default mode must retain legacy Ultimate row 1")
    require(backends[1].default_mode_config == 1,
            "Stage-C GameCube default mode must select legacy Ultimate row 1")
    configurators = [backend for backend in config.communication_backend_configs
                     if backend.backend_id == pb.COMMS_BACKEND_CONFIGURATOR]
    require(len(configurators) == 1,
            "Stage-C fixture requires exactly one Configurator recovery backend")
    require(list(configurators[0].activation_binding) == [pb.BTN_RT2],
            "Stage-C Configurator recovery backend must bind exactly BTN_RT2")

def main() -> int:
    require(sys.argv[1:] in ([],["--default-enum"]),"usage: check_glyph_stage_c_ultimate_profiles.py [--default-enum]")
    sys.path.insert(0, str(ROOT / "tools"))
    import glyph_serial_config_tool as writer
    pb, jf, _ = writer.load_runtime_proto_modules(ROOT)
    stage_a = json.loads((ROOT / "tools/fixtures/stage_a_ultimate_profiles_dry_run.json").read_text(encoding="utf-8"))
    stage_a_message, _ = writer.encode_artifact_payload(stage_a, pb, jf)
    stage_b_message, _ = writer.encode_artifact_payload(make_v2_artifact(), pb, jf)
    require(not writer.verify_required_bindings(stage_a_message, pb),
            "writer rejected the supported schema-v1 artifact")
    require(not writer.verify_required_bindings(stage_b_message, pb),
            "writer rejected the supported schema-v2 artifact")
    artifact=json.loads(ARTIFACT.read_text(encoding="utf-8"))
    require(artifact==make_v3_artifact(),"tracked complete two-v3 writer artifact drift from source fixture")
    _, payload = writer.encode_artifact_payload(artifact, pb, jf)
    _, v4_payload = writer.encode_artifact_payload(make_v4_artifact(), pb, jf)
    valid_message = pb.Config(); valid_message.ParseFromString(payload)
    require(valid_message.SerializeToString() == payload,
            "Stage-C encoded payload did not round-trip exactly through protobuf")
    converted_json = jf.MessageToDict(
        valid_message, preserving_proto_field_name=False, use_integers_for_enums=False)
    converted_message = pb.Config()
    jf.ParseDict(converted_json, converted_message, ignore_unknown_fields=False)
    require(converted_message.SerializeToString() == payload,
            "Stage-C JSON conversion did not preserve the encoded payload")
    verify_stage_c_recovery_envelope(valid_message, pb)
    require(not writer.verify_required_bindings(valid_message, pb),
            "writer rejected the complete schema-v3 artifact")
    v4_message = pb.Config(); v4_message.ParseFromString(v4_payload)
    require(not writer.verify_required_bindings(v4_message, pb),
            "writer rejected the complete schema-v4 artifact")
    require([mode.ultimate_profile_config for mode in valid_message.game_mode_configs] == [0, 1, 2],
            "schema-v3 artifact must retain explicit Ultimate profile references [0, 1, 2]")
    dry_run = subprocess.run(
        [sys.executable, str(ROOT / "tools/glyph_serial_config_tool.py"), "--dry-run", "--artifact", str(ARTIFACT)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    require(dry_run.returncode == 0, f"schema-v3 dry-run failed: {dry_run.stdout} {dry_run.stderr}")
    require("dry_run_serial_opened=false" in dry_run.stdout and "live_device_access=false" in dry_run.stdout,
            "schema-v3 dry-run attempted serial access")

    def writer_rejects(label, mutate):
        invalid = pb.Config(); invalid.CopyFrom(valid_message)
        mutate(invalid)
        require(writer.verify_required_bindings(invalid, pb),
                f"writer accepted malformed schema-v3 artifact: {label}")

    writer_rejects("unsupported_version", lambda value: setattr(value.ultimate_profiles[0], "schema_version", 4))
    writer_rejects("missing_output_program", lambda value: value.ultimate_profiles[0].ClearField("output_program"))
    writer_rejects("incomplete_routing_slots", lambda value: value.ultimate_profiles[0].routing_slots.pop())
    writer_rejects("duplicate_routing_slot", lambda value: setattr(
        value.ultimate_profiles[0].routing_slots[-1], "slot_id",
        value.ultimate_profiles[0].routing_slots[0].slot_id))
    writer_rejects("zero_role_id", lambda value: setattr(value.ultimate_profiles[0].roles[0], "role_id", 0))
    writer_rejects("duplicate_role_id", lambda value: setattr(
        value.ultimate_profiles[0].roles[1], "role_id", value.ultimate_profiles[0].roles[0].role_id))
    writer_rejects("unrouted_role_condition", lambda value: value.ultimate_profiles[0].roles[0].condition.all_tokens.append(60))
    writer_rejects("duplicate_rule_priority", lambda value: setattr(
        value.ultimate_profiles[0].table_rules[1], "priority", value.ultimate_profiles[0].table_rules[0].priority))
    writer_rejects("out_of_range_rule_table", lambda value: setattr(
        value.ultimate_profiles[0].table_rules[0], "table_id", 28))
    writer_rejects("incomplete_output_effects", lambda value: value.ultimate_profiles[0].output_program.effects.pop())
    writer_rejects("duplicate_output_effect_key", lambda value: value.ultimate_profiles[0].output_program.effects[1].CopyFrom(
        value.ultimate_profiles[0].output_program.effects[0]))
    writer_rejects("invalid_output_gate", lambda value: setattr(
        value.ultimate_profiles[0].output_program.effects[0], "gate_token", 61))
    writer_rejects("non_ultimate_reference", lambda value: (
        setattr(value.game_mode_configs[0], "mode_id", pb.MODE_FGC),
        setattr(value.game_mode_configs[0], "ultimate_profile_config", 1),
    ))
    # Fixed custody of the independent oracle: no extraction from changed
    # production source at test time. Headers/tables are frozen alongside it.
    oracle = HOST / "legacy_ultimate.cpp"
    original = oracle.read_bytes().split(b"\n", 2)[2]
    require(hashlib.sha256(original).hexdigest() == "a26c3e05dbc37a49b9cdb50d48a1b749849caa1912f3fa913499f4b456012f8e", "frozen oracle source drift")
    frozen_hashes = {
        "modes/UltimateIdentityRuntimeTables.hpp":"a0563d1c86f48b8e2e4f664b206eee0e11eb330940426998f6ed80d2c5388fdb",
        "modes/UltimateRuntimeConfigInterpreter.hpp":"8354ab72bd8dd9e5b14cebc6658bd08cd70396382d1b7499cfbb940684b76108",
        "modes/UltimateProfileEvaluator.hpp":"f51c89fa57d33ad9da82f30cb795902fd9cdc262bd65334480fb9bb18f1f61e4",
        "modes/UltimateProfileConfig.hpp":"878abcb38dfc94ce3aac7eca466147a4e177d3d6a85dc388640f5bca797daacc",
        "modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp":"e9984660752cecba91a2fbc0fc4cbfe1f940f02389d55a3753dd0022c2f0069d",
    }
    for path, digest in frozen_hashes.items():
        require(hashlib.sha256((HOST / "frozen" / path).read_bytes()).hexdigest()==digest,"frozen oracle dependency drift: "+path)
    # Shared preprocessing/state definitions are independently checked against
    # the frozen Stage-B baseline; changes need deliberate oracle review.
    shared_hashes = {
        "src/core/ControllerMode.cpp":"1278a7e38485458144dd06ecebc034f6694147fd44532da6457afd520b6ebfe8",
        "src/core/InputMode.cpp":"080bcc65bb83b1b896a2b4efa6ea9e9d304071ee30f279fe3386ff2c29cc85c7",
        "src/core/socd.cpp":"5a2bb8e776873d149559e914b07cc4224853e3e3593a46760c38d23ff4d38bb3",
        "include/core/state.hpp":"c46eb5347843ac4574dcffb28faeace608f029c27b94690c02ce06981cc4e6a3",
    }
    for path, digest in shared_hashes.items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest()==digest,"shared Stage-B preprocessing/state drift: "+path)
    with tempfile.TemporaryDirectory(prefix="stage-c-ultimate-") as directory:
        temp = Path(directory)
        generated = temp / "generated"; generated.mkdir()
        schema = ROOT / "schema/haybox"
        run([sys.executable,str(NANOPB / "generator/nanopb_generator.py"),"-I",str(schema),"-f",str(schema / "config.options"),"--error-on-unmatched","--no-timestamp","-D",str(generated),str(schema / "config.proto")])
        includes = ["-I",str(HOST / "include"),"-I",str(generated),"-I",str(NANOPB),"-I",str(ROOT / "include"),"-I",str(ROOT / "HAL/pico/include"),"-I",str(ROOT / "config/glyph/common/include"),"-I",str(ROOT / "config/glyph/glyph_mk6/include"),"-I",str(ROOT / "src")]
        common = ["-O2","-Wall","-Wextra","-Werror","-Wno-unused-function",*includes]
        if "--default-enum" not in sys.argv: common.append("-fshort-enums")
        # Existing anonymous SOCD typedef carries C++ member initializers.
        if sys.platform == "darwin": common.append("-Wno-non-c-typedef-for-linkage")
        objects=[]
        for source in (NANOPB / "pb_common.c",NANOPB / "pb_decode.c",generated / "config.pb.c"):
            target=temp / (source.stem+".o")
            run(["cc","-std=c11",*common,"-c",str(source),"-o",str(target)]); objects.append(str(target))
        frozen=temp / "legacy.o"
        run(["c++","-std=c++17","-DUltimate=LegacyUltimate","-I",str(HOST / "frozen"),*common,"-c",str(oracle),"-o",str(frozen)])
        sources=[ROOT / path for path in ("src/modes/Ultimate.cpp","src/core/ControllerMode.cpp","src/core/InputMode.cpp","src/core/socd.cpp","src/core/config_validation.cpp","src/core/config_button_validation.cpp","src/core/config_usb_default_validation.cpp","src/core/config_rgb_target_validation.cpp","config/glyph/common/src/glyph_config_validation.cpp")]
        executable=temp / "pipeline"
        run(["c++","-std=c++17",*common,str(HOST / "pipeline.cpp"),*[str(p) for p in sources],str(frozen),*objects,"-o",str(executable)])
        binary=temp / "v3.bin"; binary.write_bytes(payload)
        gamecube_default=temp / "gamecube-default"
        run(["c++","-std=c++17",*common,
             str(HOST / "gamecube_default.cpp"), str(ROOT / "src/core/config_utils.cpp"),
             *objects,"-o",str(gamecube_default)])
        print(run([str(gamecube_default), str(binary)]).strip())
        print(run([str(executable),str(binary),"3"]).strip())
        v4_binary=temp / "v4.bin"; v4_binary.write_bytes(v4_payload)
        print(run([str(executable),str(v4_binary),"4"]).strip())
        admission=temp / "admission"
        run(["c++","-std=c++17",*common,str(ROOT / "tools/fixtures/stage_b_ultimate_profiles_host/admission.cpp"),*[str(p) for p in sources],*objects,"-o",str(admission)])
        def reject_config_reference(label, mutate):
            invalid = pb.Config(); invalid.CopyFrom(valid_message)
            mutate(invalid)
            encoded = temp / (label + ".bin"); encoded.write_bytes(invalid.SerializeToString())
            result = subprocess.run([str(admission), str(encoded), "0", "3"],
                                    capture_output=True, text=True, check=False)
            require(result.returncode == 0,
                    f"production validation accepted malformed backend/default reference: {label}: "
                    f"{result.stdout} {result.stderr}")

        reject_config_reference("default_backend_out_of_range",
                                lambda value: setattr(value, "default_backend_config",
                                                      len(value.communication_backend_configs) + 1))
        reject_config_reference("default_usb_backend_out_of_range",
                                lambda value: setattr(value, "default_usb_backend_config",
                                                      len(value.communication_backend_configs) + 1))
        reject_config_reference("backend_default_mode_out_of_range",
                                lambda value: setattr(value.communication_backend_configs[0],
                                                      "default_mode_config",
                                                      len(value.game_mode_configs) + 1))
        decoder_negatives=0
        decoder_required={"excess_effect","digital_wide_mask","table_wide_id","inline_excess","inline_wide_coordinate","fixed_wide_coordinate","trigger_wide_value","wide_gate","wide_condition_token"}
        def reject(label, mutate):
            nonlocal decoder_negatives
            invalid=pb.Config(); invalid.CopyFrom(valid_message)
            mutate(invalid.ultimate_profiles[0])
            encoded=temp / (label+".bin"); encoded.write_bytes(invalid.SerializeToString())
            result=subprocess.run([str(admission),str(encoded),"0","3"],capture_output=True,text=True,check=False)
            require(result.returncode==0,f"negative accepted: {label}: {result.stdout} {result.stderr}")
            decoded="nanopb_decode=" in result.stderr
            if decoded: decoder_negatives+=1
            if label in decoder_required: require(decoded,"expected decoder-stage refusal: "+label)
        mutations = [
            ("missing_program",lambda p:p.ClearField("output_program")),
            ("disabled_program",lambda p:setattr(p.output_program,"enabled",False)),
            ("v1_program",lambda p:(setattr(p,"schema_version",1),p.ClearField("roles"),p.ClearField("routing_slots"),p.ClearField("table_rules"),setattr(p,"default_table_id",0))),
            ("v2_program",lambda p:setattr(p,"schema_version",2)),
            ("unknown_version",lambda p:setattr(p,"schema_version",4)),
            ("missing_effect",lambda p:p.output_program.effects.pop()),
            ("excess_effect",lambda p:p.output_program.effects.add().CopyFrom(p.output_program.effects[0])),
            ("duplicate_key",lambda p:p.output_program.effects[1].CopyFrom(p.output_program.effects[0])),
            ("unknown_phase",lambda p:setattr(p.output_program.effects[0],"phase",11)),
            ("wide_phase",lambda p:setattr(p.output_program.effects[0],"phase",256)),
            ("unknown_target",lambda p:setattr(p.output_program.effects[0],"target",8)),
            ("wide_target",lambda p:setattr(p.output_program.effects[0],"target",256)),
            ("wrong_phase_target",lambda p:setattr(p.output_program.effects[1],"target",4)),
            ("unknown_coordinate_mode",lambda p:setattr(p.output_program.effects[1],"coordinate_mode",5)),
            ("missing_coordinate_mode",lambda p:setattr(p.output_program.effects[1],"coordinate_mode",0)),
            ("selected_table_wrong_phase",lambda p:setattr(p.output_program.effects[2],"coordinate_mode",1)),
            ("invalid_direction_source",lambda p:setattr(p.output_program.effects[1],"direction_source",5)),
            ("missing_direction_source",lambda p:setattr(p.output_program.effects[1],"direction_source",0)),
            ("digital_direction_payload",lambda p:setattr(p.output_program.effects[0],"direction_source",1)),
            ("digital_analogue_payload",lambda p:setattr(p.output_program.effects[0],"fixed_x",128)),
            ("digital_reserved_mask",lambda p:setattr(p.output_program.effects[0],"digital_set_mask",4096)),
            ("digital_wide_mask",lambda p:setattr(p.output_program.effects[0],"digital_clear_mask",65536)),
            ("digital_overlap",lambda p:(setattr(p.output_program.effects[0],"digital_set_mask",1),setattr(p.output_program.effects[0],"digital_clear_mask",1))),
            ("digital_suppress",lambda p:setattr(p.output_program.effects[0],"suppress",True)),
            ("table_unknown_id",lambda p:setattr(p.output_program.effects[3],"table_id",28)),
            ("table_unknown_mode_id",lambda p:setattr(p.output_program.effects[3],"mode_table_id",28)),
            ("table_wide_id",lambda p:setattr(p.output_program.effects[3],"table_id",256)),
            ("table_fixed_payload",lambda p:setattr(p.output_program.effects[3],"fixed_y",128)),
            ("selected_explicit_table",lambda p:setattr(p.output_program.effects[1],"table_id",1)),
            ("inline_short",lambda p:p.output_program.effects[2].coordinates.pop()),
            ("inline_excess",lambda p:p.output_program.effects[2].coordinates.append(128)),
            ("inline_wide_coordinate",lambda p:p.output_program.effects[2].coordinates.__setitem__(0,256)),
            ("inline_fixed_payload",lambda p:setattr(p.output_program.effects[2],"fixed_x",128)),
            ("fixed_table_payload",lambda p:setattr(p.output_program.effects[8],"table_id",1)),
            ("fixed_wide_coordinate",lambda p:setattr(p.output_program.effects[8],"fixed_x",256)),
            ("trigger_coordinate_payload",lambda p:setattr(p.output_program.effects[9],"fixed_y",1)),
            ("trigger_digital_payload",lambda p:setattr(p.output_program.effects[9],"digital_set_mask",1)),
            ("trigger_wide_value",lambda p:setattr(p.output_program.effects[9],"value",256)),
            ("dpad_unknown_flags",lambda p:setattr(p.output_program.effects[11],"value",8)),
            ("dpad_noncenter",lambda p:setattr(p.output_program.effects[11],"direction_source",1)),
            ("unrelated_value",lambda p:setattr(p.output_program.effects[4],"value",1)),
            ("unrelated_digital_mask",lambda p:setattr(p.output_program.effects[4],"digital_clear_mask",1)),
            ("unknown_gate",lambda p:setattr(p.output_program.effects[0],"gate_token",61)),
            ("undefined_role_gate",lambda p:setattr(p.output_program.effects[0],"gate_token",96)),
            ("unrouted_button_gate",lambda p:setattr(p.output_program.effects[0],"gate_token",60)),
            ("wide_gate",lambda p:setattr(p.output_program.effects[0],"gate_token",256)),
            ("inverted_unconditional_gate",lambda p:setattr(p.output_program.effects[0],"gate_inverted",True)),
            ("missing_required_route",lambda p:setattr(p.routing_slots[-1],"slot_id",60)),
            ("duplicate_route_input",lambda p:setattr(p.routing_slots[1],"input_token",1)),
            ("wide_condition_token",lambda p:p.roles[0].condition.all_tokens.append(256)),
        ]
        for label,mutate in mutations: reject(label,mutate)
        print(f"production_decode_validation_negatives={len(mutations)} decoder_refusals={decoder_negatives} semantic_refusals={len(mutations)-decoder_negatives}")
    print(f"writer_fixture_profiles=2 schema_versions=3,3 explicit_refs=0,1,2 payload_bytes={len(payload)} payload_sha256={hashlib.sha256(payload).hexdigest()}")
    print("FINAL_GATE_CONFIGURATOR_RECOVERY_REQUIRED=true backend_envelope=XInput,GameCube,Configurator gamecube_default_mode=1 configurator_backends=1 activation_binding=BTN_RT2 backend_reference_negatives=3")
    print(f"fixture_sha256={hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()} serial_port_opened=false")
    print("glyph_stage_c_ultimate_profiles: PASS")
    return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except (AssertionError,OSError,ValueError,KeyError,TypeError) as error:
        print(f"glyph_stage_c_ultimate_profiles: FAIL: {error}"); raise SystemExit(1)
