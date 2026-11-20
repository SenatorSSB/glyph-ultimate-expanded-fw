#!/usr/bin/env python3
"""Current source-bound C023 USB-index proof; no historical Git reads or hardware claim."""
from __future__ import annotations

import hashlib
import json
import stat
import shlex
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = "docs/runtime_config/fixtures/gp_config023_usb_index_public_current.v1.json"
REPORT = "docs/runtime_config/gp_config023_usb_index_public_current.md"
HOST = "tools/fixtures/gp_config023_usb_public_current/usb_index_harness.cpp"
STUBS = "tools/fixtures/gp_config023_usb_public_current/host_stubs.hpp"
RECEIPT_SHA256 = '6a45698953a2857c741681215f68c2fd32e8a83b1909b26b699bfcf342e58c3d'
COMPILED_SOURCES = ["src/core/config_usb_default_validation.cpp", "src/core/config_button_validation.cpp", "src/core/config_validation.cpp", "src/modes/UltimateNativeProfile.cpp"]
NANOPB_PATH = "tools/fixtures/gp_config012_button_host/nanopb"
ENCODER_PATH = "tools/fixtures/gp_config021_persisted_recovery/dependencies"
GENERATED_PATH = "tools/fixtures/gp_config023_usb_public_current/generated"


class ProofError(AssertionError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ProofError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def regular(path: str) -> Path:
    file = ROOT / path
    for parent in (file, *file.parents):
        if parent == ROOT:
            break
        require(not parent.is_symlink(), "symlink input: " + path)
    require(file.is_file() and stat.S_ISREG(file.stat().st_mode), "missing/nonregular input: " + path)
    require(stat.S_IMODE(file.stat().st_mode) == 0o644, "fixture input mode is not 100644: " + path)
    return file


def semantic_digest(value):
    return digest(json.dumps(value,sort_keys=True,separators=(",", ":"),ensure_ascii=True).encode())


def load_fixture() -> dict:
    value = json.loads(regular(FIXTURE).read_text(), object_pairs_hook=_unique)
    payload = {key:item for key,item in value.items() if key != "semantic_digest"}
    require(value.get("semantic_digest") == semantic_digest(payload) == RECEIPT_SHA256,
            "sealed current C023 receipt semantic digest mismatch")
    require(value["schema"] == "glyph_gp_config023_usb_index_public_current.v1", "fixture identity")
    for group in ("production_sources", "host_sources"):
        require(value[group] == sorted(value[group],key=lambda row:row["path"]), "unordered source closure")
        require(len({row["path"] for row in value[group]}) == len(value[group]), "duplicate source input")
        for row in value[group]:
            require(digest(regular(row["path"]).read_bytes()) == row["sha256"],
                    group + " bytes mismatch: " + row["path"])
    for name,body in production_fragments().items():
        require(digest(body.encode()) == value["production_fragments"][name], "production fragment changed: " + name)
    report=regular(REPORT).read_text()
    for token in ("GP-CONFIG-023", "4,096", "NOT_CLAIMED", "NOT_TESTED", "UNPROVEN", "host-only"):
        require(token in report,"report nonclaim missing: " + token)
    return value


def _unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def fragment(source: str, start: str, end: str) -> str:
    text = regular(source).read_text()
    require(text.count(start) == 1, "missing/duplicate production body start: " + start)
    begin = text.index(start)
    finish = text.find(end, begin + len(start))
    require(finish >= 0, "production body end missing: " + end)
    return text[begin:finish].rstrip() + "\n"


def production_fragments() -> dict[str,str]:
    return {
        "initialize_backends": fragment("HAL/pico/src/comms/backend_init.cpp", "namespace {\nstruct BackendInputs", "void init_primary_backend("),
        "selectors": fragment("HAL/pico/src/comms/backend_init.cpp", "backend_config_selector_t get_backend_config_default = [](", "// clang-format on"),
        "persistence": fragment("HAL/pico/src/core/Persistence.cpp", "bool Persistence::SetValidator(", "__attribute__((noinline)) Persistence::SaveResult Persistence::VerifyExpectedConfigGeneration(") + fragment("HAL/pico/src/core/Persistence.cpp", "__attribute__((noinline)) Persistence::LoadResult Persistence::CompleteReadConfigCandidate(", "bool Persistence::CheckSavedConfig()"),
        "recovery": fragment("config/glyph/common/src/config.cpp", "void draw_recovery_page(", "// End this display/I2C frame") + fragment("config/glyph/common/src/config.cpp", "void refuse_boot(", "// select_mode consumes"),
    }


def function_body(source: str, start: str, end: str) -> str:
    text = regular(source).read_text()
    require(text.count(start) == 1, "missing/duplicate source-bound consumer: " + start)
    begin = text.index(start)
    finish = text.find(end, begin + len(start))
    require(finish >= 0, "consumer boundary missing: " + end)
    return text[begin:finish]


def ordered(text, *tokens):
    offsets=[text.index(token) for token in tokens]
    require(offsets == sorted(offsets) and len(set(offsets)) == len(offsets), "current consumer ordering: " + repr(tokens))


def check_consumers() -> None:
    source="HAL/pico/src/comms/ConfiguratorBackend.cpp"
    text=regular(source).read_text()
    decode=function_body(source,"__attribute__((noinline)) ConfiguratorBackend::SetConfigPreparation ConfiguratorBackend::DecodeSetConfig()", "__attribute__((noinline)) bool ConfiguratorBackend::ReportDurableLoadError()")
    ordered(decode,"DecodeIncomingSetConfig()", "ValidateSetCandidate()", "return SetConfigPreparation::Ready;")
    incoming=function_body(source,"__attribute__((noinline)) ConfiguratorBackend::SetConfigPreparation ConfiguratorBackend::DecodeIncomingSetConfig()", "__attribute__((noinline)) bool ConfiguratorBackend::ValidateSetCandidate()")
    require("pb_decode(&stream,Config_fields,&ConfigWriteCandidate())" in incoming,"SET actual decoder missing")
    validation=function_body(source,"__attribute__((noinline)) bool ConfiguratorBackend::ValidateSetCandidate()", "__attribute__((noinline)) ConfiguratorBackend::SetConfigPreparation ConfiguratorBackend::PrepareSetConfig()")
    require("persistence.ValidateConfig(ConfigWriteCandidate(),error)" in validation,"SET shared validator missing")
    handle=function_body(source,"bool ConfiguratorBackend::HandleSetConfig()", "#if GLYPH_STRICT_HARDENING_CANDIDATE")
    ordered(handle,"PrepareDecodedSetConfig()", "if(prepared!=SetConfigPreparation::Ready)", "persistence.SaveConfig(ConfigWriteCandidate())", "FinalizeSetConfig(saved)", "if (!saved)", "_config = candidate;")
    prepare=function_body(source,"__attribute__((noinline)) ConfiguratorBackend::SetConfigPreparation ConfiguratorBackend::PrepareDecodedSetConfig()", "__attribute__((noinline)) bool ConfiguratorBackend::FinishSetPhase(")
    ordered(prepare,"DecodeSetConfig()", "if(decoded!=SetConfigPreparation::Ready)", "return SetConfigPreparation::Ready;")
    source="HAL/pico/src/core/Persistence.cpp"
    load=function_body(source,"__attribute__((always_inline)) inline Persistence::LoadResult Persistence::LoadConfigDriver(", "bool Persistence::CheckSavedConfig()")
    ordered(load,"ReadConfigCandidate()", "if(prepared!=LoadResult::Loaded)", "FinishLoadedConfig(config)")
    complete=function_body(source,"__attribute__((noinline)) Persistence::LoadResult Persistence::CompleteReadConfigCandidate(", "__attribute__((noinline)) const char *Persistence::SelectReadConfigCandidate()")
    require("ValidateConfig(loaded_candidate, error)" in complete,"load shared validator missing")
    require("SaveConfig(" not in production_fragments()["persistence"],"load must not write")
    source="config/glyph/common/src/glyph_config_validation.cpp"
    require("validate_config_semantics(config, error)" in regular(source).read_text(),"Glyph shared semantic adapter missing")
    source="config/glyph/common/src/config.cpp"
    setup=function_body(source,"void setup()", "void loop()")
    ordered(setup,"persistence.SetValidator(validate_glyph_config)","persistence.ValidateConfig(config, validation_error)","persistence.LoadConfigChecked(config)","InitializeBootBackends()", "publish_boot_state(BootOutcome::Normal")
    init=function_body(source,"__attribute__((noinline)) bool InitializeBootBackends()", "void setup()")
    ordered(init,"initialize_backends(","if (!is_valid_usb_default_index(config))", "enter_recovery_configurator();", "setup_mode_activation_bindings(", "if(backend_count == 0)")
    require("SaveConfig(" not in init,"backend startup refusal must not save")
    recovery=function_body(source,"void enter_recovery_configurator()", "}  // namespace")
    ordered(recovery,"watchdog_hw->scratch[0] = 0;", "watchdog_hw->scratch[1] = 0;", "initialize_recovery(", "publish_boot_state(BootOutcome::RecoveryConfigurator")
    setup1=function_body(source,"void setup1()", "void dummyloop()")
    ordered(setup1,"while (snapshot.outcome == BootOutcome::Pending)","if (refused(snapshot.outcome))", "static RgbBrightnessMenu")


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=45)
    require(result.returncode == 0, "host command failed: " + " ".join(command) + "\n" + result.stdout + result.stderr)
    return result


def compile_and_run(temp:Path, fragments:dict[str,str], short_enum:bool) -> tuple[str,set[str]]:
    gen=ROOT/GENERATED_PATH
    nanopb=ROOT/NANOPB_PATH
    encoder=ROOT/ENCODER_PATH
    output_names={"initialize_backends":"backend_init","selectors":"backend_selectors","persistence":"persistence","recovery":"recovery"}
    for name,body in fragments.items():(temp/("production_"+output_names[name]+".inc")).write_text(body)
    includes=[ROOT/Path(HOST).parent,gen,nanopb,encoder,ROOT/"include",ROOT/"HAL/pico/include",ROOT/"config/glyph/common/include",ROOT/"config/glyph/glyph_mk6/include",temp]
    flags=["-O0","-g","-DGLYPH_PACKAGE_V1=1","-fsanitize=address,undefined","-fno-sanitize-recover=all","-fno-omit-frame-pointer"]
    if short_enum:flags.append("-fshort-enums")
    flags += ["-I"+str(p) for p in includes]
    objects=[];closure=set()
    for i,(source,compiler,standard) in enumerate([(ROOT/p,"c++","gnu++20") for p in [*COMPILED_SOURCES,HOST]]+[(nanopb/p,"cc","c99") for p in ["pb_common.c","pb_decode.c"]]+[(encoder/"pb_encode.c","cc","c99"),(gen/"config.pb.c","cc","c99")]):
        obj=temp/f"{i}.o";dep=temp/f"{i}.d"
        run([compiler,"-std="+standard,*flags,"-MMD","-MF",str(dep),"-c",str(source),"-o",str(obj)])
        for name in shlex.split(dep.read_text().replace("\\\n", " ").split(":",1)[1]):
            p=Path(name)
            if p.is_relative_to(ROOT):closure.add(str(p.relative_to(ROOT)))
        objects.append(str(obj))
    binary=temp/"current-c023";run(["c++",*flags,*objects,"-o",str(binary)])
    result=run([str(binary)]);require(not result.stderr,"sanitizer stderr")
    return result.stdout,closure


def mismatch_negatives(value):
    """Exercise every protected current production and host byte binding."""
    import shutil
    global ROOT
    original=ROOT
    count=0
    with tempfile.TemporaryDirectory(prefix="glyph-c023-negative-") as directory:
        root=Path(directory)
        paths=[FIXTURE,REPORT]+[row["path"] for group in ("production_sources","host_sources") for row in value[group]]
        for path in paths:
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(original/path,target)
        try:
            ROOT=root
            for group in ("production_sources","host_sources"):
                for row in value[group]:
                    target=root/row["path"];raw=target.read_bytes()
                    target.write_bytes(raw+b"\n// deliberate host-only mismatch\n")
                    try:load_fixture()
                    except ProofError:count+=1
                    else:raise ProofError("source/host byte mismatch accepted: "+row["path"])
                    finally:target.write_bytes(raw)
            target=root/FIXTURE;raw=target.read_bytes();target.write_bytes(raw+b" ")
            # Formatting is not semantic receipt drift. A changed semantic field is.
            changed=json.loads(raw);changed["hardware_acceptance"]="PASS"
            target.write_text(json.dumps(changed))
            try:load_fixture()
            except ProofError:count+=1
            else:raise ProofError("receipt semantic drift accepted")
            finally:target.write_bytes(raw)
            target=root/value["host_sources"][0]["path"];target.unlink()
            try:load_fixture()
            except ProofError:count+=1
            else:raise ProofError("missing current host input accepted")
        finally:ROOT=original
    return count


def main() -> int:
    try:
        value = load_fixture()
        negatives=mismatch_negatives(value)
        check_consumers()
        parts = production_fragments()
        with tempfile.TemporaryDirectory(prefix="glyph-config023-usb-index-") as folder:
            outputs = []
            for short_enum in (False, True):
                output,closure=compile_and_run(Path(folder), parts, short_enum)
                require(closure <= {row["path"] for group in ("production_sources","host_sources") for row in value[group]}, "undeclared compiled source dependency: " + repr(sorted(closure-{row["path"] for group in ("production_sources","host_sources") for row in value[group]})))
                outputs.append(output)
        require(outputs[0] == outputs[1] == value["expected_host_output"], "ABI/receipt observations differ")
        lines = outputs[0].splitlines()
        require(len(lines) == 15 and lines[-1] == "gp_config023_usb_index_public_current: PASS (host-only; no hardware claim)",
                "unexpected bounded proof output:\n" + outputs[0])
        require(lines[0].startswith("index_matrix counts=0..15 indices=0..255 cases=4096 accepted=120 actual_extent=15"),
                "index/count matrix result")
        require(all(any(line.startswith("decoder_case " + name + " ") for line in lines) for name in
                    ("omitted", "zero", "out_of_range_2", "out_of_range_255", "varint_256", "valid_1")),
                "actual decoder/persisted refusal cases missing")
        require(any(line.startswith("startup_recovery executable_display=PASS") for line in lines),
                "executable startup recovery proof missing")
        print(outputs[0], end="")
        print(f"ABIs=default,short-enum ASan_UBSan=PASS source_host_mismatch_negatives={negatives} current_production_fragments=4 hardware=NOT_CLAIMED")
        return 0
    except (OSError, subprocess.SubprocessError, ProofError, KeyError, TypeError, ValueError) as error:
        print("gp_config023_usb_index_public_current: FAIL: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
