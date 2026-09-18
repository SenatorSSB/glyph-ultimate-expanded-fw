"""Read-only, fail-closed correspondence for already accepted firmware inputs.

Identity, hardware authorization and normal metadata validators remain callers'
responsibility. See docs/agent_framework/HARDWARE_CORRESPONDENCE.md for the
dependency audit behind the deliberately finite metadata inventory.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import re
import stat
import subprocess


class CorrespondenceError(ValueError):
    """An input is unknown, unsafe, or differs from the tested source snapshot."""


CRITICAL_ROOTS = frozenset({
    "src", "include", "hal", "backend", "lib", "active", "storage", "config",
    "builder_scripts", "scripts", "boards", "variants", "patches", "proto",
})
CRITICAL_FILES = frozenset({
    "platformio.ini", "glyph_nuker", ".gitmodules", ".gitignore", ".gitattributes",
    "cmakelists.txt", "makefile", "sconstruct", "sconscript", "library.json",
    "library.properties", "requirements.txt", "platformio.lock",
})
# Exact, reviewed paths only. Membership never overrides a critical input.
NON_BEHAVIORAL_PATHS = frozenset({
    'docs/AGENT_CONTEXT.md',
    'docs/CURRENT_STATE.md',
    'docs/ROADMAP.md',
    'docs/WORKFLOW.md',
    'docs/agent_framework/GP_CONFIG_005_HARDWARE_OPERATOR.md',
    'docs/agent_framework/GP_CONFIG_005_HARDWARE_PROTOCOL.md',
    'docs/agent_framework/GP_CONFIG_005_INTEGRATION_RESULT_20260919.md',
    'docs/agent_framework/HARDWARE_CORRESPONDENCE.md',
    'docs/agent_framework/HARDWARE_EVIDENCE.md',
    'docs/agent_framework/README.md',
    'docs/agent_framework/VALIDATION_AND_GATES.md',
    'docs/calibration/INDEX.md',
    'docs/calibration/fixtures/gp_config_005_hardware_evidence_2026-09-17.json',
    'docs/calibration/gp_config_005_hardware_result_2026-09-17.md',
    'docs/calibration/gp_config_005_prior_inconclusive_persistence_event_2026-09-17.md',
    'docs/project/ACTIVE_AGENT_QUEUE.md',
    'docs/runtime_config/current_config_persistence_recovery_research.md',
    'docs/runtime_config/fixtures/configurator_setconfig_transaction.json',
    'docs/runtime_config/fixtures/current_config_persistence_recovery_research.json',
    'docs/runtime_config/fixtures/glyph_checker_census.json',
    'docs/runtime_config/fixtures/runtime_config_validation_health.json',
    'docs/runtime_config/fixtures/runtime_config_validation_manifest.json',
    'docs/runtime_config/runtime_config_validation_health.md',
    'tools/check_glyph_agent_framework_docs.py',
    'tools/check_glyph_configurator_setconfig_transaction.py',
    'tools/check_glyph_current_config_persistence_recovery_research.py',
    'tools/check_glyph_docs_agent_surface.py',
    'tools/check_glyph_docs_navigation.py',
    'tools/fixtures/configurator_setconfig_host/handler_harness.cpp',
    'tools/fixtures/configurator_setconfig_host/include/arduino/Adafruit_USBD_Device.h',
    'tools/fixtures/configurator_setconfig_host/include/cobs/Print.h',
    'tools/fixtures/configurator_setconfig_host/include/cobs/Stream.h',
    'tools/fixtures/configurator_setconfig_host/include/config.pb.h',
    'tools/fixtures/configurator_setconfig_host/include/core/CommunicationBackend.hpp',
    'tools/fixtures/configurator_setconfig_host/include/core/InputSource.hpp',
    'tools/fixtures/configurator_setconfig_host/include/core/Persistence.hpp',
    'tools/fixtures/configurator_setconfig_host/include/host_stubs.hpp',
    'tools/fixtures/configurator_setconfig_host/include/pb_arduino.h',
    'tools/fixtures/configurator_setconfig_host/include/pb_decode.h',
    'tools/fixtures/configurator_setconfig_host/include/pb_encode.h',
    'tools/fixtures/configurator_setconfig_host/include/reboot.hpp',
    'tools/glyph_hardware_correspondence.py',
    'tools/glyph_serial_config_tool.py',
    'tools/gp_config_005_hw_test.py',
    'tools/test_glyph_docs_agent_surface_integration.py',
    'tools/test_glyph_hardware_correspondence.py',
    'tools/test_gp_config_005_hw_test.py',
})


def classify_path(path: str) -> str:
    """Classify canonical Git paths; never normalize an ambiguous alias."""
    if (not isinstance(path, str) or not path or path.startswith("/")
            or "\\" in path or ":" in path
            or any(ord(char) < 32 or ord(char) == 127 for char in path)
            or any(part in {"", ".", ".."} for part in path.split("/"))):
        raise CorrespondenceError(f"unsafe correspondence path: {path!r}")
    folded = path.casefold()
    if (folded.split("/", 1)[0] in CRITICAL_ROOTS
            or folded in CRITICAL_FILES
            or folded.startswith(".github/workflows/")
            or "/.github/workflows/" in folded):
        return "CRITICAL"
    if path in NON_BEHAVIORAL_PATHS:
        return "NON_BEHAVIORAL"
    raise CorrespondenceError(f"unclassified correspondence path: {path}")


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    if result.returncode:
        raise CorrespondenceError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def _paths(raw: bytes) -> set[str]:
    if raw and not raw.endswith(b"\0"):
        raise CorrespondenceError("unterminated Git path output")
    try:
        return {part.decode("utf-8") for part in raw.split(b"\0") if part}
    except UnicodeDecodeError as exc:
        raise CorrespondenceError("non-UTF-8 Git path") from exc


def _tree(root: Path, revision: str) -> dict[str, tuple[str, str, str]]:
    result = {}
    for record in _git(root, "ls-tree", "-r", "-z", revision).split(b"\0"):
        if record:
            try:
                header, raw_path = record.split(b"\t", 1)
                mode, kind, blob = header.decode("ascii").split()
                result[raw_path.decode("utf-8")] = (mode, kind, blob)
            except (ValueError, UnicodeDecodeError) as exc:
                raise CorrespondenceError("invalid Git tree entry") from exc
    return result


def _entries_safe(path: str, category: str, *entries: tuple[str, str, str] | None) -> None:
    modes = {"100644"} if category == "NON_BEHAVIORAL" else {"100644", "100755"}
    for entry in entries:
        if entry is not None and (entry[0] not in modes or entry[1] != "blob"):
            raise CorrespondenceError(f"unsupported correspondence entry: {path}: {entry[:2]}")


def _working_mode(root: Path, path: str) -> int:
    location = root / path
    for parent in location.parents:
        if parent == root:
            break
        if parent.is_symlink():
            raise CorrespondenceError(f"symlinked correspondence directory: {path}")
    return location.lstat().st_mode


def verify_correspondence(root: Path, candidate: str, tested_base: str,
                          target: str = "HEAD", *, integrated: bool,
                          check_worktree: bool = True) -> dict[str, object]:
    """Require exact critical inputs and audited metadata in both complete deltas.

This does not confer hardware acceptance or authorize metadata mutations.
    Callers must pin the actual candidate/artifact/PASS independently.
    """
    root = root.resolve()
    if not all(re.fullmatch(r"[0-9a-f]{40}", value) for value in (candidate, tested_base)):
        raise CorrespondenceError("candidate and tested base must be full immutable Git identities")
    # Resolve once; subsequent operations do not race against a moving target ref.
    target_sha = _git(root, "rev-parse", "--verify", "--end-of-options", f"{target}^{{commit}}").decode().strip()
    parents = _git(root, "rev-list", "--parents", "-n", "1", candidate).decode().split()
    if parents != [candidate, tested_base]:
        raise CorrespondenceError("candidate tested parent mismatch")
    baseline = candidate if integrated else tested_base
    merge_base = _git(root, "merge-base", candidate, target_sha).decode().strip()
    if merge_base != baseline:
        raise CorrespondenceError("candidate ancestry does not match correspondence phase")
    base_tree, candidate_tree, target_tree = (_tree(root, ref) for ref in (tested_base, candidate, target_sha))
    candidate_paths = _paths(_git(root, "diff", "--no-renames", "--name-only", "-z", tested_base, candidate, "--"))
    candidate_categories = {}
    for path in sorted(candidate_paths):
        category = candidate_categories[path] = classify_path(path)
        _entries_safe(path, category, base_tree.get(path), candidate_tree.get(path))
    target_paths = _paths(_git(root, "diff", "--no-renames", "--name-only", "-z", baseline, target_sha, "--"))
    baseline_tree = candidate_tree if integrated else base_tree
    target_categories = {}
    for path in sorted(target_paths):
        category = target_categories[path] = classify_path(path)
        _entries_safe(path, category, baseline_tree.get(path), target_tree.get(path))
        if category == "CRITICAL":
            raise CorrespondenceError(f"critical input differs from tested snapshot: {path}")
    dirty_categories = {}
    if check_worktree:
        dirty = _paths(_git(root, "diff", "--no-renames", "--name-only", "-z", "--"))
        dirty |= _paths(_git(root, "diff", "--cached", "--no-renames", "--name-only", "-z", "--"))
        dirty |= _paths(_git(root, "ls-files", "--others", "--exclude-standard", "-z"))
        # Git ignores do not exclude source from the firmware compiler. Limit
        # discovery to critical roots/controls so dependency caches under .pio
        # are not mistaken for repository inputs.
        ignored_scope = sorted(CRITICAL_ROOTS | CRITICAL_FILES | {".github/workflows"})
        dirty |= _paths(_git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z",
                             "--", *(f":(icase){path}" for path in ignored_scope)))
        index = {}
        for record in _git(root, "ls-files", "--stage", "-z").split(b"\0"):
            if record:
                header, name = record.split(b"\t", 1)
                mode, blob, stage = header.decode().split()
                path = name.decode("utf-8")
                if stage != "0":
                    raise CorrespondenceError(f"unmerged index: {path}")
                index[path] = (mode, "blob", blob)
        # Git diff can hide assume-unchanged/skip-worktree files and stat-cache
        # collisions. Inspect every indexed critical file's actual mode/bytes,
        # independently of those Git optimizations and without content filters.
        for path, entry in index.items():
            try:
                category = classify_path(path)
            except CorrespondenceError:
                continue  # Unchanged unknown paths are not new exemptions.
            if category != "CRITICAL":
                continue
            _entries_safe(path, category, entry)
            try:
                mode = _working_mode(root, path)
                if not stat.S_ISREG(mode):
                    raise CorrespondenceError(f"non-regular critical working input: {path}")
                raw = (root / path).read_bytes()
            except OSError as exc:
                raise CorrespondenceError(f"unreadable critical working input: {path}") from exc
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != entry[2] or bool(mode & 0o111) != (entry[0] == "100755"):
                raise CorrespondenceError(f"dirty critical working input: {path}")
        for path in sorted(dirty):
            category = dirty_categories[path] = classify_path(path)
            if category == "CRITICAL":
                raise CorrespondenceError(f"dirty critical input: {path}")
            _entries_safe(path, category, index.get(path))
            try:
                mode = _working_mode(root, path)
            except FileNotFoundError:
                continue  # A metadata deletion is left to its normal validator.
            if not stat.S_ISREG(mode) or mode & 0o111:
                raise CorrespondenceError(f"non-regular/non-100644 working metadata: {path}")
    return {"phase": "integrated" if integrated else "pre_integration",
            "candidate": candidate, "tested_base": tested_base, "target": target_sha,
            "candidate_paths": candidate_categories, "target_paths": target_categories,
            "dirty_paths": dirty_categories,
            "normal_metadata_validation_required": True}
