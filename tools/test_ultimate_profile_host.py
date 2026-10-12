#!/usr/bin/env python3
"""Generate a temporary nanopb schema and exercise production profile validation/lookup."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / ".pio/libdeps/glyph_mk6/Nanopb/generator/nanopb_generator.py"
NANOPB_INCLUDE = ROOT / ".pio/libdeps/glyph_mk6/Nanopb"
PROTO = ROOT / "schema/haybox/config.proto"
OPTIONS = ROOT / "schema/haybox/config.options"
SOURCE = ROOT / "src/modes/Ultimate.cpp"
FIXTURE = ROOT / "tools/fixtures/ultimate_profile_host/profile_harness.cpp"


def production_lookup_definition() -> str:
    source = SOURCE.read_text()
    signature = "StickPoint LookupConfiguredStickPoint("
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 0
    for cursor in range(brace, len(source)):
        if source[cursor] == "{":
            depth += 1
        elif source[cursor] == "}":
            depth -= 1
            if depth == 0:
                return source[start : cursor + 1]
    raise RuntimeError("could not find end of production lookup function")


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print("+", " ".join(str(part) for part in command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    if not GENERATOR.is_file():
        print("ERROR: nanopb generator unavailable; prepare dependencies with PlatformIO first", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="ultimate-profile-host-") as temporary:
        temp = Path(temporary)
        generated = temp / "generated"
        generated.mkdir()
        run([
            sys.executable, str(GENERATOR), "-I", str(PROTO.parent),
            "-f", str(OPTIONS), "--error-on-unmatched", "--no-timestamp",
            "-D", str(generated), str(PROTO),
        ])
        header = generated / "config.pb.h"
        required_schema_tokens = (
            "ultimate_profiles[2]", "tables[28]", "coordinates[9]",
            "ultimate_profile_config",
        )
        generated_text = header.read_text()
        missing = [token for token in required_schema_tokens if token not in generated_text]
        if missing:
            raise RuntimeError("generated schema missing expected Stage-A fields: " + ", ".join(missing))

        harness = FIXTURE.read_text().replace(
            "// ULTIMATE_LOOKUP_DEFINITION", production_lookup_definition()
        )
        harness_path = temp / "profile_harness.cpp"
        harness_path.write_text(harness)
        executable = temp / "ultimate_profile_host"
        run([
            "c++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
            "-I", str(generated), "-I", str(ROOT / "include"),
            "-I", str(NANOPB_INCLUDE), "-I", str(ROOT / "src"),
            str(harness_path), str(ROOT / "src/core/config_validation.cpp"),
            str(ROOT / "src/core/config_button_validation.cpp"),
            str(ROOT / "src/core/config_usb_default_validation.cpp"),
            "-o", str(executable),
        ])
        run([str(executable)])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
