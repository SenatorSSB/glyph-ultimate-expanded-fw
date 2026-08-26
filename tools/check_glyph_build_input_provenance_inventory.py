#!/usr/bin/env python3
"""Validate the declared-only Glyph build-input provenance inventory.

This checker is intentionally static.  It reads tracked declaration bytes and
Git index metadata, but never resolves dependencies, imports workflow code,
executes build scripts or glyph_nuker, invokes PlatformIO, or accesses a
network.
"""
from __future__ import annotations

import copy
import ast
import configparser
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/runtime_config/fixtures/build_input_provenance_inventory.json"
DOC = ROOT / "docs/runtime_config/build_input_provenance_inventory.md"

TOP_LEVEL_FIELDS = {
    "schema_name", "schema_version", "status", "canonical_environment",
    "declaration_files", "selectors", "source_identity",
    "postprocessor_identity", "unresolved_claims",
}
DECLARATION_FIELDS = {"path", "git_mode", "sha256"}
SELECTOR_FIELDS = {
    "id", "category", "declaring_path", "declaration_context",
    "raw_selector", "selector_class", "resolution_state",
}
SELECTOR_CLASSES = {
    "FULL_GIT_COMMIT", "ABBREVIATED_GIT_COMMIT", "TAG",
    "COMPATIBLE_VERSION_RANGE", "EXACT_VERSION", "VERSION_LINE",
    "UNVERSIONED", "MOVING_REF", "RUNTIME_EXPRESSION",
    "SYMBOLIC_FRAMEWORK", "LOCAL_CONFIGURATION_SYMBOL",
    "LOCAL_TRACKED_FILE", "LOCAL_SOURCE_SELECTION", "TRACKED_FILE_IDENTITY",
}
RESOLUTION_STATES = {
    "STATIC_TRACKED_BYTES", "DECLARED_EXACT_NOT_FETCHED",
    "DECLARED_MOVABLE_NOT_RESOLVED", "RUNTIME_RESOLVED_ONLY",
    "UNRESOLVED_EXTERNAL",
}
UNRESOLVED_CLAIMS = sorted([
    "artifact_acceptance",
    "build_device_config_live_caller_and_ownership",
    "complete_dependency_resolution",
    "immutable_artifact_locator",
    "package_and_action_content_identity",
    "postprocessor_byte_transformation",
    "postprocessor_purpose",
    "reproducible_build",
    "runner_image_identity",
    "toolchain_resolution",
])
SHA256_RE = re.compile(r"[0-9a-f]{64}")


# These are reviewed selector records, not resolved package identities.  Each
# literal is also required to remain present in its declaring tracked file;
# declaration byte hashes bind ordering and all surrounding declaration text.
SELECTOR_SPECS = [
    ("meta.build.glyph_mk6.bin_ext", "environment", "config/glyph/meta.yaml", "build[1].bin_ext", "uf2", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("meta.build.glyph_mk6.env", "environment", "config/glyph/meta.yaml", "build[1].env", "glyph_mk6", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("meta.build.glyph_protoA.bin_ext", "environment", "config/glyph/meta.yaml", "build[0].bin_ext", "uf2", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("meta.build.glyph_protoA.env", "environment", "config/glyph/meta.yaml", "build[0].env", "glyph_protoA", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("meta.external_repo", "source_selection", "config/glyph/meta.yaml", "repo", "GregTurbo/Haybox-Glyph", "UNVERSIONED", "UNRESOLVED_EXTERNAL"),
    ("meta.external_revision", "source_identity", "config/glyph/meta.yaml", "revision", "05a7d2b", "ABBREVIATED_GIT_COMMIT", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.arduino_pico.board", "environment", "platformio.ini", "arduino_pico_base.board", "pico", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("pio.arduino_pico.core", "environment", "platformio.ini", "arduino_pico_base.board_build.core", "earlephilhower", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("pio.arduino_pico.extra_script", "local_script", "platformio.ini", "arduino_pico_base.extra_scripts", "pre:builder_scripts/arduino_pico.py", "LOCAL_TRACKED_FILE", "STATIC_TRACKED_BYTES"),
    ("pio.arduino_pico.framework", "toolchain", "platformio.ini", "arduino_pico_base.framework", "arduino", "SYMBOLIC_FRAMEWORK", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.arduino_pico.platform", "toolchain", "platformio.ini", "arduino_pico_base.platform", "https://github.com/maxgerhardt/platform-raspberrypi.git#5e87ae34ca025274df25b3303e9e9cb6c120123c", "FULL_GIT_COMMIT", "DECLARED_EXACT_NOT_FETCHED"),
    ("pio.arduino_pico.platform_package", "toolchain", "platformio.ini", "arduino_pico_base.platform_packages", "framework-arduinopico@https://github.com/earlephilhower/arduino-pico.git#3.6.3", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.default_environment", "environment", "platformio.ini", "platformio.default_envs", "glyph_mk6", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("pio.env.lib.haybox_proto", "dependency", "platformio.ini", "env.lib_deps", "https://github.com/JonnyHaystack/HayBox-proto#5b2bb5d", "ABBREVIATED_GIT_COMMIT", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.env.lib.nanopb", "dependency", "platformio.ini", "env.lib_deps", "nanopb/Nanopb@^0.4.8", "COMPATIBLE_VERSION_RANGE", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.env.nanopb_proto", "source_selection", "platformio.ini", "env.custom_nanopb_protos", "+<.pio/libdeps/${PIOENV}/HayBox-proto/config.proto>", "LOCAL_SOURCE_SELECTION", "RUNTIME_RESOLVED_ONLY"),
    ("pio.env.source_filter", "source_selection", "platformio.ini", "env.build_src_filter", "+<src/>", "LOCAL_SOURCE_SELECTION", "RUNTIME_RESOLVED_ONLY"),
    ("pio.extra_configs", "environment", "platformio.ini", "platformio.extra_configs", "config/*/env.ini", "LOCAL_SOURCE_SELECTION", "RUNTIME_RESOLVED_ONLY"),
    ("pio.glyph.extends", "environment", "config/glyph/env.ini", "glyph_base.extends", "arduino_pico_base", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("pio.glyph.lib.haybox_proto", "dependency", "config/glyph/env.ini", "glyph_base.lib_deps", "https://github.com/GregTurbo/HayBox-proto#db4e2f6", "ABBREVIATED_GIT_COMMIT", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.glyph.lib_ignore.haybox_proto", "dependency", "config/glyph/env.ini", "glyph_base.lib_ignore", "https://github.com/JonnyHaystack/HayBox-proto", "UNVERSIONED", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.glyph.source_common", "source_selection", "config/glyph/env.ini", "glyph_base.build_src_filter", "+<config/glyph/common/src>", "LOCAL_SOURCE_SELECTION", "RUNTIME_RESOLVED_ONLY"),
    ("pio.glyph.source_environment", "source_selection", "config/glyph/env.ini", "glyph_base.build_src_filter", "+<config/glyph/${PIOENV}>", "LOCAL_SOURCE_SELECTION", "RUNTIME_RESOLVED_ONLY"),
    ("pio.glyph_mk6.extends", "environment", "config/glyph/env.ini", "env:glyph_mk6.extends", "glyph_base", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("pio.lib.adafruit_gfx", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "adafruit/Adafruit GFX Library@^1.11.9", "COMPATIBLE_VERSION_RANGE", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.adafruit_ssd1306", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "adafruit/Adafruit SSD1306@^2.5.9", "COMPATIBLE_VERSION_RANGE", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.arduino_nunchuk", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "https://github.com/JonnyHaystack/arduino-nunchuk/archive/refs/tags/v1.0.1.zip", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.crc32", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "bakercp/CRC32@^2.0.0", "COMPATIBLE_VERSION_RANGE", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.fastled", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "https://github.com/FastLED/FastLED#6daa782", "ABBREVIATED_GIT_COMMIT", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.joybus_pio", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "https://github.com/GregTurbo/joybus-pio#f2f59c0", "ABBREVIATED_GIT_COMMIT", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.nanopb_arduino", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "https://github.com/JonnyHaystack/nanopb-arduino/archive/refs/tags/v1.1.1.zip", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.nes_pio", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "https://github.com/GregTurbo/nes-pio#422f16f", "ABBREVIATED_GIT_COMMIT", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.packetio", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "eric-wieser/PacketIO@^0.3.0", "COMPATIBLE_VERSION_RANGE", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.pcf8575", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "robtillaart/PCF8575@^0.2.2", "COMPATIBLE_VERSION_RANGE", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.tu_composite_hid", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "TUCompositeHID", "UNVERSIONED", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.lib.xinput", "dependency", "platformio.ini", "arduino_pico_base.lib_deps", "https://github.com/JonnyHaystack/Adafruit_TinyUSB_XInput#4b5617b", "ABBREVIATED_GIT_COMMIT", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("pio.source_filter.pico", "source_selection", "platformio.ini", "arduino_pico_base.build_src_filter", "+<HAL/pico/src>", "LOCAL_SOURCE_SELECTION", "RUNTIME_RESOLVED_ONLY"),
    ("pio.src_dir", "source_selection", "platformio.ini", "platformio.src_dir", "./", "LOCAL_SOURCE_SELECTION", "RUNTIME_RESOLVED_ONLY"),
    ("workflow.device.build_matrix", "workflow_expression", ".github/workflows/build-device-config.yml", "jobs.build.strategy.matrix.include", "${{ fromJson(needs.metadata.outputs.meta_json).build }}", "RUNTIME_EXPRESSION", "RUNTIME_RESOLVED_ONLY"),
    ("workflow.device.checkout_action", "workflow_action", ".github/workflows/build-device-config.yml", "jobs.metadata.steps.Checkout.uses", "actions/checkout@v4", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.config_checkout_action", "workflow_action", ".github/workflows/build-device-config.yml", "jobs.build.steps.Check out config repo.uses", "actions/checkout@v4", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.device_config_revision", "workflow_expression", ".github/workflows/build-device-config.yml", "jobs.build.env.DEVICE_CONFIG_REVISION", "${{ github.ref_type == 'tag' && github.ref_name || github.sha }}", "RUNTIME_EXPRESSION", "RUNTIME_RESOLVED_ONLY"),
    ("workflow.device.external_repo", "workflow_expression", ".github/workflows/build-device-config.yml", "jobs.build.env.HAYBOX_REPO", "${{ fromJson(needs.metadata.outputs.meta_json).repo }}", "RUNTIME_EXPRESSION", "UNRESOLVED_EXTERNAL"),
    ("workflow.device.external_revision", "workflow_expression", ".github/workflows/build-device-config.yml", "jobs.build.env.HAYBOX_REVISION", "${{ fromJson(needs.metadata.outputs.meta_json).revision }}", "RUNTIME_EXPRESSION", "UNRESOLVED_EXTERNAL"),
    ("workflow.device.metadata_path", "source_selection", ".github/workflows/build-device-config.yml", "jobs.metadata.steps.Read metadata from yaml file.run", "meta.yaml", "LOCAL_TRACKED_FILE", "STATIC_TRACKED_BYTES"),
    ("workflow.device.pip", "dependency", ".github/workflows/build-device-config.yml", "jobs.build.steps.Install PlatformIO.run", "python -m pip install --upgrade pip", "UNVERSIONED", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.platformio", "dependency", ".github/workflows/build-device-config.yml", "jobs.build.steps.Install PlatformIO.run", "pip install --upgrade platformio", "UNVERSIONED", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.python", "toolchain", ".github/workflows/build-device-config.yml", "jobs.build.steps.Set up Python.with.python-version", "3.10", "VERSION_LINE", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.remarshal", "dependency", ".github/workflows/build-device-config.yml", "jobs.metadata.steps.Install yaml2json.run", "python3 -m pip install remarshal", "UNVERSIONED", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.release_action", "workflow_action", ".github/workflows/build-device-config.yml", "jobs.build.steps.Upload binaries to release.uses", "softprops/action-gh-release@v1", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.runner.build", "workflow_runner", ".github/workflows/build-device-config.yml", "jobs.build.runs-on", "ubuntu-latest", "MOVING_REF", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.runner.metadata", "workflow_runner", ".github/workflows/build-device-config.yml", "jobs.metadata.runs-on", "ubuntu-latest", "MOVING_REF", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.setup_python_action", "workflow_action", ".github/workflows/build-device-config.yml", "jobs.build.steps.Set up Python.uses", "actions/setup-python@v5", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.device.upload_action", "workflow_action", ".github/workflows/build-device-config.yml", "jobs.build.steps.Publish ${{ matrix.env }} artifacts.uses", "actions/upload-artifact@v4", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.nested.reusable_caller", "reusable_workflow", "config/glyph/.github/workflows/build.yml", "jobs.build.uses", "GregTurbo/HayBox-Glyph/.github/workflows/build-device-config.yml@configurator", "MOVING_REF", "UNRESOLVED_EXTERNAL"),
    ("workflow.top.build_environment", "environment", ".github/workflows/build.yml", "jobs.build.strategy.matrix.include.env", "glyph_mk6", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("workflow.top.build_extension", "environment", ".github/workflows/build.yml", "jobs.build.strategy.matrix.include.bin_ext", "uf2", "LOCAL_CONFIGURATION_SYMBOL", "RUNTIME_RESOLVED_ONLY"),
    ("workflow.top.checkout_build", "workflow_action", ".github/workflows/build.yml", "jobs.build.steps.Check out source code.uses", "actions/checkout@v4", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.top.checkout_validation", "workflow_action", ".github/workflows/build.yml", "jobs.validation.steps.Check out source code.uses", "actions/checkout@v4", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.top.comparison_base", "source_selection", ".github/workflows/build.yml", "jobs.validation.env.GLYPH_CHECKER_BASE", "${{ github.event_name == 'pull_request' && format('origin/{0}', github.base_ref) || 'origin/configurator' }}", "RUNTIME_EXPRESSION", "RUNTIME_RESOLVED_ONLY"),
    ("workflow.top.glyph_nuker", "postprocessor", ".github/workflows/build.yml", "jobs.build.steps.nuke.run", "glyph_nuker", "TRACKED_FILE_IDENTITY", "STATIC_TRACKED_BYTES"),
    ("workflow.top.pip", "dependency", ".github/workflows/build.yml", "jobs.build.steps.Install PlatformIO.run", "python -m pip install --upgrade pip", "UNVERSIONED", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.top.platformio", "dependency", ".github/workflows/build.yml", "jobs.build.steps.Install PlatformIO.run", "pip install --upgrade platformio", "UNVERSIONED", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.top.python", "toolchain", ".github/workflows/build.yml", "jobs.build.steps.Set up Python.with.python-version", "3.10", "VERSION_LINE", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.top.runner.build", "workflow_runner", ".github/workflows/build.yml", "jobs.build.runs-on", "ubuntu-latest", "MOVING_REF", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.top.runner.validation", "workflow_runner", ".github/workflows/build.yml", "jobs.validation.runs-on", "ubuntu-latest", "MOVING_REF", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.top.setup_python_action", "workflow_action", ".github/workflows/build.yml", "jobs.build.steps.Set up Python.uses", "actions/setup-python@v5", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
    ("workflow.top.source_sha", "source_identity", ".github/workflows/build.yml", "jobs.build.steps.Verify checked-out source and postprocessor identity.run", "$GITHUB_SHA", "RUNTIME_EXPRESSION", "RUNTIME_RESOLVED_ONLY"),
    ("workflow.top.upload_action", "workflow_action", ".github/workflows/build.yml", "jobs.build.steps.Publish ${{ matrix.env }} artifacts.uses", "actions/upload-artifact@v4", "TAG", "DECLARED_MOVABLE_NOT_RESOLVED"),
]


def duplicate_guard(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def tracked_index(root: Path = ROOT) -> dict[str, tuple[str, str]]:
    completed = subprocess.run(
        ["git", "ls-files", "-s"], cwd=root, text=True,
        capture_output=True, check=True,
    )
    result: dict[str, tuple[str, str]] = {}
    for line in completed.stdout.splitlines():
        header, path = line.split("\t", 1)
        mode, oid, stage = header.split()
        if stage == "0":
            result[path] = (mode, oid)
    return result


def declaration_paths(index: dict[str, tuple[str, str]]) -> list[str]:
    paths = {
        path for path in index
        if path == "platformio.ini"
        or (path.startswith("config/") and (path.endswith("/env.ini") or path.endswith("/meta.yaml")))
        or (path.endswith((".yml", ".yaml")) and (path.startswith(".github/workflows/") or "/.github/workflows/" in path))
    }
    paths.update({"builder_scripts/arduino_pico.py", "glyph_nuker"})
    return sorted(paths)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_selector(raw: str, category: str) -> str:
    """Classify the reviewed raw selector without resolving its target."""
    suffix = raw.rsplit("#", 1)[-1] if "#" in raw else raw
    if re.fullmatch(r"[0-9a-f]{40}", suffix):
        return "FULL_GIT_COMMIT"
    if re.fullmatch(r"[0-9a-f]{7,39}", suffix):
        return "ABBREVIATED_GIT_COMMIT"
    if "/refs/tags/" in raw or re.search(r"@v\d+(?:\.\d+){0,2}$", raw) or re.search(r"#v?\d+(?:\.\d+){0,2}$", raw):
        return "TAG"
    if re.search(r"@\^[0-9]", raw):
        return "COMPATIBLE_VERSION_RANGE"
    if re.search(r"@\d+\.\d+\.\d+$", raw):
        return "EXACT_VERSION"
    if re.fullmatch(r"\d+\.\d+", raw):
        return "VERSION_LINE"
    if raw == "ubuntu-latest" or raw.endswith("@configurator"):
        return "MOVING_REF"
    if "${{" in raw or raw == "$GITHUB_SHA":
        return "RUNTIME_EXPRESSION"
    if raw == "arduino":
        return "SYMBOLIC_FRAMEWORK"
    if raw.startswith(("+<", "./", "config/")):
        return "LOCAL_SOURCE_SELECTION"
    if category == "environment":
        return "LOCAL_CONFIGURATION_SYMBOL"
    if category == "local_script" or raw == "meta.yaml":
        return "LOCAL_TRACKED_FILE"
    if category == "postprocessor" and raw == "glyph_nuker":
        return "TRACKED_FILE_IDENTITY"
    return "UNVERSIONED"


def selector_records() -> list[dict[str, str]]:
    return [
        {
            "id": item[0], "category": item[1], "declaring_path": item[2],
            "declaration_context": item[3], "raw_selector": item[4],
            "selector_class": item[5], "resolution_state": item[6],
        }
        for item in sorted(SELECTOR_SPECS)
    ]


def ini_context_contains(path: Path, context: str, raw: str) -> bool:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    parser.read(path, encoding="utf-8")
    section, key = context.split(".", 1)
    if not parser.has_section(section) or not parser.has_option(section, key):
        return False
    tokens = [line.strip() for line in parser.get(section, key).splitlines() if line.strip()]
    return raw in tokens


def yaml_job_block(text: str, job: str) -> str:
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if line == f"  {job}:"), None)
    if start is None:
        return ""
    end = next((index for index in range(start + 1, len(lines)) if re.match(r"^  [A-Za-z0-9_-]+:\s*$", lines[index])), len(lines))
    return "\n".join(lines[start:end])


def yaml_step_block(job_block: str, step_name: str) -> str:
    lines = job_block.splitlines()
    marker = f"- name: {step_name}"
    start = next((index for index, line in enumerate(lines) if line.strip() == marker), None)
    if start is None:
        return ""
    indentation = len(lines[start]) - len(lines[start].lstrip())
    end = next((index for index in range(start + 1, len(lines)) if lines[index].lstrip().startswith("- name:") and len(lines[index]) - len(lines[index].lstrip()) == indentation), len(lines))
    return "\n".join(lines[start:end])


def workflow_step_field_contains(step_block: str, field: str, raw: str) -> bool:
    first_line = step_block.splitlines()[0] if step_block else ""
    step_indent = len(first_line) - len(first_line.lstrip())
    field_indent = " " * (step_indent + 2)
    if field == "uses":
        return bool(re.search(rf"^{field_indent}uses:\s*{re.escape(raw)}\s*$", step_block, re.MULTILINE))
    if field == "with.python-version":
        child_indent = " " * (step_indent + 4)
        return bool(re.search(rf"^{child_indent}python-version:\s*['\"]?{re.escape(raw)}['\"]?\s*$", step_block, re.MULTILINE))
    if field != "run":
        return False
    lines = step_block.splitlines()
    start = next((index for index, line in enumerate(lines) if re.match(rf"^{field_indent}run:\s*", line)), None)
    if start is None:
        return False
    indentation = len(lines[start]) - len(lines[start].lstrip())
    first = lines[start].split("run:", 1)[1].strip()
    commands = [] if first in {"", "|", ">"} else [first]
    for line in lines[start + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= indentation:
            break
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            commands.append(stripped)
    return any(raw in command for command in commands)


def meta_context_contains(text: str, context: str, raw: str) -> bool:
    if context in {"repo", "revision"}:
        return bool(re.search(rf"^{re.escape(context)}:\s*{re.escape(raw)}\s*$", text, re.MULTILINE))
    match = re.fullmatch(r"build\[(\d+)\]\.(env|bin_ext)", context)
    if not match:
        return False
    rows = re.findall(r"^\s*- env:\s*(\S+)\s*\n\s+bin_ext:\s*(\S+)\s*$", text, re.MULTILINE)
    index, field = int(match.group(1)), match.group(2)
    if index >= len(rows):
        return False
    return rows[index][0 if field == "env" else 1] == raw


def workflow_context_contains(text: str, context: str, raw: str) -> bool:
    match = re.match(r"^jobs\.([^.]+)\.(.+)$", context)
    if not match:
        return False
    job, remainder = match.groups()
    block = yaml_job_block(text, job)
    if not block:
        return False
    if ".steps." in context:
        before, after = context.split(".steps.", 1)
        if after.endswith(".with.python-version"):
            step_name = after.removesuffix(".with.python-version")
            field = "with.python-version"
        else:
            step_name, field = after.rsplit(".", 1)
        step = yaml_step_block(yaml_job_block(text, before.split(".")[1]), step_name)
        return workflow_step_field_contains(step, field, raw)
    if remainder == "runs-on":
        return bool(re.search(rf"^    runs-on:\s*{re.escape(raw)}\s*$", block, re.MULTILINE))
    if remainder.startswith("env."):
        key = remainder.removeprefix("env.")
        return bool(re.search(rf"^      {re.escape(key)}:\s*{re.escape(raw)}\s*$", block, re.MULTILINE))
    if remainder == "strategy.matrix.include":
        return bool(re.search(rf"^        include:\s*{re.escape(raw)}\s*$", block, re.MULTILINE))
    if remainder.startswith("strategy.matrix.include."):
        key = remainder.rsplit(".", 1)[-1]
        return bool(re.search(rf"^          (?:-\s+)?{re.escape(key)}:\s*{re.escape(raw)}\s*$|^            {re.escape(key)}:\s*{re.escape(raw)}\s*$", block, re.MULTILINE))
    if remainder == "uses":
        return bool(re.search(rf"^    uses:\s*{re.escape(raw)}\s*$", block, re.MULTILINE))
    return False


def assert_selector_contexts(root: Path = ROOT) -> None:
    cache: dict[str, str] = {}
    for item in selector_records():
        path = item["declaring_path"]
        cache.setdefault(path, (root / path).read_text(encoding="utf-8"))
        context = item["declaration_context"]
        raw = item["raw_selector"]
        if path.endswith(".ini"):
            found = ini_context_contains(root / path, context, raw)
        elif path.endswith("meta.yaml"):
            found = meta_context_contains(cache[path], context, raw)
        else:
            found = workflow_context_contains(cache[path], context, raw)
        if not found:
            raise ValueError(f"selector missing from exact declaration context: {item['id']}")
        actual_class = classify_selector(raw, item["category"])
        if actual_class != item["selector_class"]:
            raise ValueError(f"selector classification drift for {item['id']}: {actual_class}")


def expected_inventory(root: Path = ROOT) -> dict[str, object]:
    index = tracked_index(root)
    declarations = []
    for relative in declaration_paths(index):
        path = root / relative
        if relative not in index or not path.is_file() or path.is_symlink():
            raise ValueError(f"missing or unsafe tracked declaration: {relative}")
        declarations.append({"path": relative, "git_mode": index[relative][0], "sha256": sha256(path)})
    return {
        "schema_name": "glyph_build_input_provenance_inventory",
        "schema_version": 1,
        "status": "declared_input_inventory_only_no_resolution_or_reproducibility",
        "canonical_environment": "glyph_mk6",
        "declaration_files": declarations,
        "selectors": selector_records(),
        "source_identity": {
            "mechanism": "git rev-parse HEAD",
            "required_value_shape": "full_lowercase_40_hex",
            "resolution_state": "RUNTIME_RESOLVED_ONLY",
            "claim": "exact_source_snapshot_only_not_dependency_closure_or_reproducibility",
        },
        "postprocessor_identity": {
            "path": "glyph_nuker", "git_mode": "100755",
            "sha256": "8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae",
            "purpose": "UNKNOWN", "byte_transformation": "UNKNOWN",
            "resolution_state": "STATIC_TRACKED_BYTES",
        },
        "unresolved_claims": UNRESOLVED_CLAIMS,
    }


def validate_shape(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != TOP_LEVEL_FIELDS:
        raise ValueError("inventory top-level fields do not match the contract")
    if value["schema_name"] != "glyph_build_input_provenance_inventory" or type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("inventory schema identity is invalid")
    declarations = value.get("declaration_files")
    selectors = value.get("selectors")
    if not isinstance(declarations, list) or not isinstance(selectors, list):
        raise ValueError("declaration_files and selectors must be arrays")
    if any(not isinstance(item, dict) or set(item) != DECLARATION_FIELDS for item in declarations):
        raise ValueError("invalid declaration record shape")
    if any(not isinstance(item, dict) or set(item) != SELECTOR_FIELDS for item in selectors):
        raise ValueError("invalid selector record shape")
    paths = [item["path"] for item in declarations]
    ids = [item["id"] for item in selectors]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ValueError("declaration paths must be unique and sorted")
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise ValueError("selector IDs must be unique and sorted")
    for item in declarations:
        path = item["path"]
        if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts:
            raise ValueError("declaration path escapes repository")
        if item["git_mode"] not in {"100644", "100755"} or not isinstance(item["sha256"], str) or not SHA256_RE.fullmatch(item["sha256"]):
            raise ValueError("invalid declaration identity")
        if path != "glyph_nuker" and item["git_mode"] != "100644":
            raise ValueError("unexpected executable declaration")
    for item in selectors:
        if item["selector_class"] not in SELECTOR_CLASSES or item["resolution_state"] not in RESOLUTION_STATES:
            raise ValueError("unknown selector classification")
        if not all(isinstance(item[field], str) and item[field] for field in SELECTOR_FIELDS):
            raise ValueError("selector values must be nonempty strings")
    return value


def validate_declaration_files(
    declarations: list[dict[str, str]], root: Path,
    index: dict[str, tuple[str, str]],
) -> None:
    for item in declarations:
        relative = item["path"]
        path = root / relative
        if relative not in index:
            raise ValueError(f"untracked declaration: {relative}")
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"unsafe declaration path: {relative}")
        actual_mode = index[relative][0]
        if actual_mode != item["git_mode"]:
            raise ValueError(f"declaration mode drift: {relative}")
        if relative != "glyph_nuker" and actual_mode != "100644":
            raise ValueError(f"unexpected executable declaration: {relative}")
        if sha256(path) != item["sha256"]:
            raise ValueError(f"declaration byte drift: {relative}")


def assert_checker_safety() -> None:
    """Fail if this checker gains a non-static execution or network seam."""
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=__file__)
    forbidden_imports = {"socket", "urllib", "http", "requests", "platformio"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = {alias.name.split(".", 1)[0] for alias in node.names}
            if names & forbidden_imports:
                raise ValueError("checker imports a forbidden network/build module")
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".", 1)[0] in forbidden_imports:
            raise ValueError("checker imports a forbidden network/build module")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
            if node.func.attr != "run" or not node.args or not isinstance(node.args[0], ast.List):
                raise ValueError("checker gained an unreviewed subprocess seam")
            command = [element.value for element in node.args[0].elts if isinstance(element, ast.Constant) and isinstance(element.value, str)]
            if command != ["git", "ls-files", "-s"]:
                raise ValueError(f"checker subprocess is not static Git discovery: {command}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "__import__"}:
            raise ValueError("checker gained a dynamic execution seam")


def adversarial_tests(current: dict[str, object]) -> tuple[int, int]:
    positive = 0
    negative = 0
    validate_shape(copy.deepcopy(current)); positive += 1
    for mutation in (
        lambda value: value.__setitem__("schema_version", True),
        lambda value: value.__setitem__("unknown", True),
        lambda value: value["declaration_files"][0].__setitem__("path", "../escape"),
        lambda value: value["declaration_files"][0].__setitem__("git_mode", "100755"),
        lambda value: value["selectors"].append(copy.deepcopy(value["selectors"][0])),
        lambda value: value["selectors"][0].__setitem__("selector_class", "INVENTED"),
        lambda value: value["selectors"][0].__setitem__("resolution_state", "RESOLVED_BY_ASSERTION"),
    ):
        candidate = copy.deepcopy(current)
        mutation(candidate)
        try:
            validate_shape(candidate)
        except ValueError:
            negative += 1
        else:
            raise AssertionError("adversarial inventory mutation passed")
    with tempfile.TemporaryDirectory(prefix="glyph-provenance-inventory-") as directory:
        root = Path(directory)
        regular = root / "regular"
        regular.write_text("tracked", encoding="utf-8")
        regular_record = [{"path": "regular", "git_mode": "100644", "sha256": sha256(regular)}]
        validate_declaration_files(regular_record, root, {"regular": ("100644", "synthetic")})
        positive += 1
        symlink = root / "alias"
        symlink.symlink_to(regular.name)
        cases = [
            ([{"path": "alias", "git_mode": "100644", "sha256": sha256(regular)}], {"alias": ("100644", "synthetic")}),
            ([{"path": "untracked", "git_mode": "100644", "sha256": "0" * 64}], {"regular": ("100644", "synthetic")}),
            ([{"path": "regular", "git_mode": "100755", "sha256": sha256(regular)}], {"regular": ("100755", "synthetic")}),
        ]
        for declarations, index in cases:
            try:
                validate_declaration_files(declarations, root, index)
            except ValueError:
                negative += 1
            else:
                raise AssertionError("unsafe declaration adversarial case passed")
        ini_path = root / "context.ini"
        ini_path.write_text("[test]\nboard = pico_w\n[other]\nboard = pico\n", encoding="utf-8")
        if ini_context_contains(ini_path, "test.board", "pico"):
            raise AssertionError("INI substring context drift passed")
        negative += 1
        wrong_field = """  build:
    steps:
    - name: Checkout
      # uses: actions/checkout@v4
      with:
        note: actions/checkout@v4
"""
        if workflow_context_contains(wrong_field, "jobs.build.steps.Checkout.uses", "actions/checkout@v4"):
            raise AssertionError("workflow step field drift passed")
        negative += 1
        wrong_job_scope = """  build:
    steps:
    - name: Nested
      uses: GregTurbo/HayBox-Glyph/.github/workflows/build-device-config.yml@configurator
      env:
        HAYBOX_REPO: stale
"""
        if workflow_context_contains(wrong_job_scope, "jobs.build.uses", "GregTurbo/HayBox-Glyph/.github/workflows/build-device-config.yml@configurator"):
            raise AssertionError("job-level reusable workflow scope drift passed")
        if workflow_context_contains(wrong_job_scope, "jobs.build.env.HAYBOX_REPO", "stale"):
            raise AssertionError("job-level environment scope drift passed")
        negative += 2
    classification_cases = {
        "a" * 40: "FULL_GIT_COMMIT",
        "05a7d2b": "ABBREVIATED_GIT_COMMIT",
        "actions/checkout@v4": "TAG",
        "nanopb/Nanopb@^0.4.8": "COMPATIBLE_VERSION_RANGE",
        "pkg@1.2.3": "EXACT_VERSION",
        "3.10": "VERSION_LINE",
        "ubuntu-latest": "MOVING_REF",
        "${{ github.sha }}": "RUNTIME_EXPRESSION",
        "arduino": "SYMBOLIC_FRAMEWORK",
        "glyph_mk6": "LOCAL_CONFIGURATION_SYMBOL",
        "builder_scripts/arduino_pico.py": "LOCAL_TRACKED_FILE",
        "+<src/>": "LOCAL_SOURCE_SELECTION",
        "glyph_nuker": "TRACKED_FILE_IDENTITY",
        "TUCompositeHID": "UNVERSIONED",
    }
    for raw, selector_class in classification_cases.items():
        categories = {
            "arduino": "toolchain", "glyph_mk6": "environment",
            "builder_scripts/arduino_pico.py": "local_script",
            "+<src/>": "source_selection", "glyph_nuker": "postprocessor",
        }
        actual = classify_selector(raw, categories.get(raw, "dependency"))
        if actual != selector_class:
            raise AssertionError(f"classification case {raw!r}: {actual} != {selector_class}")
        positive += 1
    return positive, negative


def main() -> int:
    try:
        raw = INVENTORY.read_text(encoding="utf-8")
        committed = json.loads(raw, object_pairs_hook=duplicate_guard)
        validate_shape(committed)
        index = tracked_index()
        validate_declaration_files(committed["declaration_files"], ROOT, index)
        expected = expected_inventory()
        if committed != expected:
            raise ValueError("inventory drift; regenerate through reviewed static inventory update")
        assert_selector_contexts()
        assert_checker_safety()
        if "declared-input inventory" not in DOC.read_text(encoding="utf-8"):
            raise ValueError("inventory documentation classification is missing")
        positive, negative = adversarial_tests(committed)
    except (OSError, ValueError, TypeError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"glyph_build_input_provenance_inventory: FAIL: {exc}")
        return 1
    print(json.dumps({
        "status": "PASS", "declaration_files": len(committed["declaration_files"]),
        "selectors": len(committed["selectors"]), "unresolved_claims": len(UNRESOLVED_CLAIMS),
        "positive_tests": positive, "negative_tests": negative,
        "network_access": False, "dependency_resolution": False,
        "platformio_invoked": False, "glyph_nuker_executed": False,
        "firmware_artifact_published": False, "runtime_behavior_changed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
