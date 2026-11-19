#!/usr/bin/env python3
"""Read-only deterministic aggregate runner for current runtime-config checks."""
from __future__ import annotations

import argparse
from contextvars import ContextVar
from contextlib import ExitStack
import ast
import hashlib
import json
import os
import re
import selectors
import stat
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from pathlib import PurePosixPath
from time import monotonic, sleep

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
from generate_glyph_checker_census import generate as generate_census, rendered as render_census  # noqa: E402

import glyph_ci_package_scope as package_scope

MANIFEST = ROOT / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
CENSUS = ROOT / "docs/runtime_config/fixtures/glyph_checker_census.json"
REQUIRED = {"id", "path", "command", "category", "applicability", "branch_policy", "required_arguments", "mutation_risk", "source_dependencies", "load_bearing", "historical", "reason"}
BRANCH_POLICIES = {"content_only", "content_and_scope", "named_evidence_branch", "not_run"}
APPLICABILITIES = {"current", "historical_only", "unsafe_or_mutating"}
# Retained evidence may name these files; current policy has public owners.
LEGACY_CURRENT_POLICY_DEPENDENCIES = frozenset({
    "docs/AGENT_CONTEXT.md", "docs/WORKFLOW.md",
})
# Owner authority is distinct from policy; historical evidence may retain it.
LEGACY_CURRENT_AUTHORITY_DEPENDENCIES = frozenset({
    "docs/agent_framework/USER_DIRECTION.md",
})
LEGACY_CURRENT_HARDWARE_CONTRACT_DEPENDENCIES = frozenset({
    "docs/agent_framework/HARDWARE_ARTIFACT_CUSTODY.md",
    "docs/agent_framework/HARDWARE_EVIDENCE.md",
})
EXCLUSION_REQUIRED = {"id", "path", "reason", "detail"}
EXCLUSION_REASONS = {"HISTORICAL_BRANCH_EVIDENCE", "HARDWARE_RESULT_EVIDENCE", "SUPERSEDED_CONTRACT", "REQUIRES_NONCANONICAL_ARGUMENT", "UNSAFE_OR_MUTATING", "DUPLICATE_COVERAGE", "NOT_CURRENT_RUNTIME_CONFIG_LANE"}
CHECKER_TIMEOUT_SECONDS = 140.0
ADVERSARIAL_TIMEOUT_SECONDS = 210.0
AGGREGATE_TIMEOUT_SECONDS = 450.0
TERM_GRACE_SECONDS = 2.0
CHILD_SETUP_TIMEOUT_SECONDS = 10.0
CLEANUP_REAP_SECONDS = 2.0


def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


# A single read-only manifest load often refers to the same production input
# hundreds of times. Gather stage-zero metadata once per invocation; live mode
# and regular-file checks still apply, as do the independent clean-tree proofs.
_MANIFEST_INDEX = ContextVar("glyph_manifest_index", default=None)
_C023_RESULT = ContextVar("glyph_manifest_c023_result", default=None)


def regular_index_paths():
    raw = git_value("ls-files", "--stage", "-z")
    rows = {}
    for record in raw.split("\0"):
        if record:
            metadata, path = record.split("\t", 1)
            mode, _, stage = metadata.split()
            rows.setdefault(path, []).append((mode, stage))
    return {path for path, values in rows.items()
            if len(values) == 1 and values[0] in (("100644", "0"), ("100755", "0"))}


def tracked_regular_stage_zero(path: str) -> bool:
    if not path or path.startswith("/") or "\\" in path:
        return False
    pure = PurePosixPath(path)
    if pure.as_posix() != path or any(part in {"", ".", ".."} for part in pure.parts):
        return False
    index = _MANIFEST_INDEX.get()
    if index is not None:
        return path in index and (ROOT / path).is_file() and not (ROOT / path).is_symlink()
    result = git("ls-files", "--stage", "--", path)
    records = [line.split("\t", 1)[0].split() for line in result.stdout.splitlines() if "\t" in line]
    return len(records) == 1 and records[0][0] in {"100644", "100755"} and (ROOT / path).is_file() and not (ROOT / path).is_symlink()


def validate_checker_command(entry: dict[str, object]) -> None:
    checker_id = entry["id"]
    path = entry["path"]
    required_arguments = entry["required_arguments"]
    command = entry["command"]
    if not isinstance(path, str) or not tracked_regular_stage_zero(path):
        raise ValueError(f"invalid checker path: {checker_id}")
    if not isinstance(required_arguments, list) or not all(isinstance(argument, str) for argument in required_arguments):
        raise ValueError(f"invalid required_arguments: {checker_id}")
    expected = ["python3", path, *required_arguments]
    if command != expected:
        raise ValueError(f"command does not match path/required_arguments: {checker_id}")


def campaign_guard_arguments(entry: dict[str, object]) -> bool:
    """The sole current argument contract adopted by GP-VAL-037.

    Either reserved identity claims the entire contract. In particular, an
    empty-argument or renamed variant cannot fall back to ordinary selection.
    """
    checker_id = "campaign_webserial_source_authority"
    path = "tools/check_glyph_runtime_config_webserial_device_write_source_authority.py"
    if entry["id"] != checker_id and entry["path"] != path:
        return False
    expected = {
        "id": checker_id, "path": path,
        "command": ["python3", path, "--campaign-transition"],
        "required_arguments": ["--campaign-transition"],
        "category": "candidate_safety", "applicability": "current",
        "branch_policy": "content_and_scope", "load_bearing": True,
        "historical": False, "mutation_risk": "none",
    }
    if (any(entry[key] != value for key, value in expected.items())
            or type(entry["load_bearing"]) is not bool
            or type(entry["historical"]) is not bool):
        raise ValueError("invalid reserved campaign guard contract")
    indexed = git("ls-files", "--stage", "-z", "--", path)
    records = [record for record in indexed.stdout.split("\0") if record]
    fields = records[0].split("\t", 1)[0].split() if len(records) == 1 else []
    if (indexed.returncode or len(records) != 1 or len(fields) != 3
            or fields[0] != "100644" or fields[2] != "0"
            or records[0].split("\t", 1)[-1] != path
            or not (ROOT / path).is_file() or (ROOT / path).is_symlink()
            or (ROOT / path).stat().st_mode & 0o111
            or any((ROOT / parent).is_symlink() for parent in PurePosixPath(path).parents)):
        raise ValueError("campaign guard requires tracked stage-zero regular 100644 file")
    return True


def c017_replay_arguments(entry: dict[str, object]) -> bool:
    """Two exact035 source replay commands retain actual current load-bearing proof."""
    path = 'tools/check_glyph_neopixel_historical_replay.py'
    identities = {
        'neopixel_null_sendreport_characterization': ('configurator', []),
        'gp_config017_neopixel_repaired_current': ('candidate_safety', ['--repaired-current']),
    }
    if entry['id'] not in identities and entry['path'] != path:
        return False
    if entry['id'] not in identities:
        raise ValueError('unrecognized reserved035 replay identity')
    category, arguments = identities[entry['id']]
    expected = dict(path=path, command=['python3', path, *arguments],
                    required_arguments=arguments, category=category,
                    applicability='current', branch_policy='content_and_scope',
                    load_bearing=True, historical=False, mutation_risk='temporary_file_only')
    if (any(entry[key] != value for key, value in expected.items()) or
            type(entry['load_bearing']) is not bool or type(entry['historical']) is not bool):
        raise ValueError('invalid reserved035 replay command/phase contract')
    indexed = git('ls-files', '--stage', '-z', '--', path)
    expected_stage = '100644 ' + git('rev-parse', ':' + path).stdout.strip() + ' 0\t' + path + '\0'
    if (indexed.returncode or indexed.stdout != expected_stage or
            not (ROOT / path).is_file() or (ROOT / path).is_symlink() or
            (ROOT / path).stat().st_mode & 0o111 or
            any((ROOT / parent).is_symlink() for parent in PurePosixPath(path).parents)):
        raise ValueError('reserved035 replay requires exact stage-zero regular100644 file')
    return True


def c022_replay_arguments(entry: dict[str, object]) -> bool:
    """Only the exact039 replay commands can replace an existing current lane."""
    path = 'tools/check_glyph_c022_proof_replay.py'
    if entry['path'] != path and entry['id'] != 'gp_config022_rgb_target_validation':
        return False
    lanes = {
        'current_config_persistence_recovery_research': 'persistence',
        'getconfig_raw_load_characterization': 'raw_get',
        'configurator_setconfig_transaction': 'transaction005',
        'setconfig_runtime_rebinding_characterization': 'rebind008',
        'config_menu_invalid_state_characterization': 'menu009',
        'gp_config_012_button_mask_characterization': 'button012',
        'gp_config_013_usb_default_characterization': 'usb013',
        'gp_config020_button_validation': 'button020',
        'gp_kbd_001_keyboard_pipeline': 'kbd001',
        'gp_config019_usb_name_selection': 'usb019',
        'neopixel_null_sendreport_characterization': 'neopixel016_017',
        'gp_config017_neopixel_repaired_current': 'neopixel016_017',
        'custom_modifier_cache_characterization': 'modifier011',
        'gp_config014_modifier_capacity': 'modifier014',
        'gp_val035_c017_transition': 'transition035',
        'gp_config021_persisted_recovery': 'recovery021',
        'gp_val038_c021_transition': 'transition038',
    }
    if entry['id'] == 'gp_config022_rgb_target_validation':
        arguments = []
        expected = {'category': 'candidate_safety', 'applicability': 'current',
                    'branch_policy': 'content_and_scope', 'load_bearing': True, 'historical': False}
    elif entry['id'] in lanes:
        from glyph_c022_campaign_transition import B
        document = git('show', B + ':docs/runtime_config/fixtures/runtime_config_validation_manifest.json')
        if document.returncode:
            raise ValueError('039 replay lacks exact accepted predecessor manifest')
        rows = [row for row in json.loads(document.stdout, object_pairs_hook=pairs)['entries']
                if row['id'] == entry['id']]
        if len(rows) != 1:
            raise ValueError('039 replay lacks unique immutable predecessor lane')
        expected = {key: rows[0][key] for key in
                    ('category', 'applicability', 'branch_policy', 'load_bearing', 'historical')}
        arguments = ['--consumer', lanes[entry['id']]]
    else:
        raise ValueError('unknown reserved039 replay identity')
    expected.update(path=path, command=['python3', path, *arguments],
                    required_arguments=arguments, mutation_risk='temporary_file_only')
    if (any(entry[key] != value for key, value in expected.items())
            or type(entry['load_bearing']) is not bool or type(entry['historical']) is not bool):
        raise ValueError('invalid reserved039 replay command/phase contract')
    if (not tracked_regular_stage_zero(path) or (ROOT / path).stat().st_mode & 0o111
            or any((ROOT / parent).is_symlink() for parent in PurePosixPath(path).parents)
            or git('ls-files', '-v', '-z', '--', path).stdout != 'H ' + path + '\0'):
        raise ValueError('039 replay requires tracked regular100644 input without index flags')
    return True


def c023_replay_arguments(entry: dict[str, object]) -> bool:
    """Only the exact GP-VAL-042 replay command binds the C023 source proof."""
    current = 'tools/check_glyph_gp_config023_usb_index_public_current.py'
    if entry['path'] == current:
        expected = {'id': 'gp_config023_usb_index_validation', 'path': current,
                    'command': ['python3', current], 'category': 'candidate_safety',
                    'applicability': 'current', 'branch_policy': 'content_only',
                    'required_arguments': [], 'mutation_risk': 'temporary_file_only',
                    'load_bearing': True, 'historical': False}
        if any(entry.get(key) != value for key, value in expected.items()):
            raise ValueError('invalid exact public C023 current contract')
        package_scope.public_contract(ROOT)
        return False
    path = 'tools/check_glyph_c023_proof_replay.py'
    if entry['path'] != path and entry['id'] != 'gp_config023_usb_index_validation':
        return False
    expected = {'id': 'gp_config023_usb_index_validation', 'path': path,
                'command': ['python3', path], 'category': 'candidate_safety',
                'applicability': 'current', 'branch_policy': 'content_and_scope',
                'required_arguments': [], 'mutation_risk': 'temporary_file_only',
                'load_bearing': True, 'historical': False}
    if any(entry.get(key) != value for key, value in expected.items()):
        raise ValueError('invalid exact GP-VAL-042 replay command/phase contract')
    if (not tracked_regular_stage_zero(path) or (ROOT / path).stat().st_mode & 0o111
            or any((ROOT / parent).is_symlink() for parent in PurePosixPath(path).parents)
            or git('ls-files', '-v', '-z', '--', path).stdout != 'H ' + path + '\0'):
        raise ValueError('GP-VAL-042 replay requires tracked regular100644 input')
    return True


def c021_replay_arguments(entry: dict[str, object]) -> bool:
    """Exact038 current/replay commands; the old main bodies remain immutable."""
    path = 'tools/check_glyph_c021_proof_replay.py'
    if entry['path'] != path and entry['id'] != 'gp_config021_persisted_recovery':
        return False
    lanes = {'current_config_persistence_recovery_research': 'persistence', 'getconfig_raw_load_characterization': 'raw_get', 'configurator_setconfig_transaction': 'transaction005', 'setconfig_runtime_rebinding_characterization': 'rebind008', 'config_menu_invalid_state_characterization': 'menu009', 'gp_config_012_button_mask_characterization': 'button012', 'gp_config_013_usb_default_characterization': 'usb013', 'gp_config020_button_validation': 'button020', 'gp_kbd_001_keyboard_pipeline': 'kbd001', 'gp_config019_usb_name_selection': 'usb019', 'neopixel_null_sendreport_characterization': 'neopixel016_017', 'gp_config017_neopixel_repaired_current': 'neopixel016_017', 'custom_modifier_cache_characterization': 'modifier011', 'gp_config014_modifier_capacity': 'modifier014', 'gp_val035_c017_transition':'transition035'}
    if entry['id'] == 'gp_config021_persisted_recovery':
        arguments = []
        expected = {'category': 'candidate_safety', 'applicability': 'current',
                    'branch_policy': 'content_and_scope', 'load_bearing': True, 'historical': False}
    elif entry['id'] in lanes:
        from glyph_c021_campaign_transition import B
        document = git('show', B + ':docs/runtime_config/fixtures/runtime_config_validation_manifest.json')
        if document.returncode:
            raise ValueError('038 replay lacks immutable predecessor manifest')
        rows = [row for row in json.loads(document.stdout, object_pairs_hook=pairs)['entries']
                if row['id'] == entry['id']]
        if len(rows) != 1:
            raise ValueError('038 replay lacks exact original lane')
        expected = {key: rows[0][key] for key in
                    ('category', 'applicability', 'branch_policy', 'load_bearing', 'historical')}
        arguments = ['--consumer', lanes[entry['id']]]
    else:
        raise ValueError('unknown reserved038 replay identity')
    expected.update(path=path, command=['python3', path, *arguments],
                    required_arguments=arguments, mutation_risk='temporary_file_only')
    if any(entry[key] != value for key, value in expected.items()) or type(entry['load_bearing']) is not bool or type(entry['historical']) is not bool:
        raise ValueError('invalid reserved038 replay command/phase contract')
    if not tracked_regular_stage_zero(path) or (ROOT / path).stat().st_mode & 0o111 or any((ROOT / parent).is_symlink() for parent in PurePosixPath(path).parents):
        raise ValueError('038 replay requires tracked regular100644 input')
    if git('ls-files', '-v', '-z', '--', path).stdout != 'H ' + path + '\0':
        raise ValueError('038 replay index flag trap')
    return True


def direct_local_helpers(checker_path: str) -> set[str]:
    source = (ROOT / checker_path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=checker_path)
    found: set[str] = set()
    for node in ast.walk(tree):
        module = None
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("tools.") and alias.name.count(".") == 1:
                    candidate = f"{alias.name.replace('.', '/')}.py"
                    if tracked_regular_stage_zero(candidate):
                        found.add(candidate)
                elif "." not in alias.name and tracked_regular_stage_zero(f"tools/{alias.name}.py"):
                    found.add(f"tools/{alias.name}.py")
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            module = node.module
            if module.startswith("tools.") and module.count(".") == 1:
                candidate = f"{module.replace('.', '/')}.py"
                if tracked_regular_stage_zero(candidate):
                    found.add(candidate)
            elif "." not in module and tracked_regular_stage_zero(f"tools/{module}.py"):
                found.add(f"tools/{module}.py")
    return found


def is_legacy_internal_workflow_dependency(path: str) -> bool:
    return (
        path.startswith("docs/agent_framework/")
        or path == "docs/project/ACTIVE_AGENT_QUEUE.md"
    )


def validate_dependencies(entry: dict[str, object]) -> None:
    dependencies = entry["source_dependencies"]
    if not isinstance(dependencies, list) or not all(isinstance(path, str) for path in dependencies):
        raise ValueError(f"invalid source_dependencies: {entry['id']}")
    if len(dependencies) != len(set(dependencies)):
        raise ValueError(f"duplicate source dependency: {entry['id']}")
    for path in dependencies:
        if entry["applicability"] == "current" and path in LEGACY_CURRENT_HARDWARE_CONTRACT_DEPENDENCIES:
            raise ValueError(f"legacy current hardware contract dependency: {entry['id']}: {path}")
        if entry["applicability"] == "current" and path in LEGACY_CURRENT_POLICY_DEPENDENCIES:
            raise ValueError(f"legacy current policy dependency: {entry['id']}: {path}")
        if entry["applicability"] == "current" and path in LEGACY_CURRENT_AUTHORITY_DEPENDENCIES:
            raise ValueError(f"legacy current authority dependency: {entry['id']}: {path}")
        if entry["applicability"] == "current" and is_legacy_internal_workflow_dependency(path):
            raise ValueError(f"legacy current internal workflow dependency: {entry['id']}: {path}")
        if path == entry["path"]:
            raise ValueError(f"checker path repeated as source dependency: {entry['id']}")
        if not tracked_regular_stage_zero(path):
            raise ValueError(f"invalid source dependency path: {entry['id']}: {path}")
    required = direct_local_helpers(str(entry["path"]))
    missing = sorted(required - set(dependencies))
    if missing:
        raise ValueError(f"missing direct helper dependencies for {entry['id']}: {', '.join(missing)}")


def validate_branch_policy(entry: dict[str, object]) -> None:
    applicability, policy = entry["applicability"], entry["branch_policy"]
    if applicability not in APPLICABILITIES or policy not in BRANCH_POLICIES:
        raise ValueError(f"invalid applicability/branch_policy: {entry['id']}")
    expected = {"current": {"content_only", "content_and_scope"}, "historical_only": {"named_evidence_branch"}, "unsafe_or_mutating": {"not_run"}}[applicability]
    if policy not in expected:
        raise ValueError(f"invalid applicability/branch_policy pair: {entry['id']}")


def load() -> tuple[list[dict[str, object]], list[dict[str, object]], set[str]]:
    token = _MANIFEST_INDEX.set(regular_index_paths())
    try:
        return load_indexed_manifest()
    finally:
        _MANIFEST_INDEX.reset(token)


def load_indexed_manifest() -> tuple[list[dict[str, object]], list[dict[str, object]], set[str]]:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    version = value.get("schema_version")
    if (ROOT / package_scope.PUBLIC_BASELINE).exists() and version != 5:
        raise ValueError("sealed public current package requires manifest schema 5")
    if version not in (4, 5) or not isinstance(value.get("categories"), list) or not isinstance(value.get("entries"), list) or not isinstance(value.get("strong_signal_exclusions"), list):
        raise ValueError("invalid manifest root")
    categories = set(value["categories"])
    ids: set[str] = set()
    entries: list[dict[str, object]] = []
    current_package = version == 5
    if current_package:
        package_scope.public_contract(ROOT)
    for entry in value["entries"]:
        if not isinstance(entry, dict) or set(entry) != REQUIRED:
            raise ValueError(f"invalid checker entry: {entry!r}")
        checker_id = entry["id"]
        if not isinstance(checker_id, str) or checker_id in ids:
            raise ValueError(f"duplicate checker ID: {checker_id}")
        ids.add(checker_id)
        historical_package_entry = version == 5 and entry["applicability"] == "historical_only"
        campaign_arguments = not historical_package_entry and (c023_replay_arguments(entry) or c022_replay_arguments(entry) or c021_replay_arguments(entry) or campaign_guard_arguments(entry) or c017_replay_arguments(entry))
        if entry["category"] not in categories:
            raise ValueError(f"invalid category: {entry['category']}")
        if not isinstance(entry["command"], list) or not all(isinstance(part, str) for part in entry["command"]):
            raise ValueError(f"invalid command: {checker_id}")
        validate_checker_command(entry)
        # Sealed v5 historical records remain inert evidence. Their original
        # inputs may deliberately be private/excluded; current dependencies
        # always retain full tracked-file and direct-helper validation.
        if not (current_package and entry["applicability"] == "historical_only"):
            validate_dependencies(entry)
        validate_branch_policy(entry)
        if entry["applicability"] == "current" and (entry["historical"] or not entry["load_bearing"] or (entry["required_arguments"] and not campaign_arguments) or entry["mutation_risk"] not in {"none", "temporary_file_only", "temporary_repository_only"}):
            raise ValueError(f"unsafe current aggregate entry: {checker_id}")
        if entry["historical"] and entry["applicability"] != "historical_only":
            raise ValueError(f"historical checker incorrectly current: {checker_id}")
        entries.append(entry)
    #035 reserves both actual native proof lanes. Focused selection may choose a
    #subset after load; the complete current manifest cannot silently omit one.
    c017_markers = ('docs/runtime_config/fixtures/gp_val035_c017_transition.json',
                    'docs/runtime_config/fixtures/gp_val035_accepted_transitions.json',
                    'tools/glyph_c017_campaign_transition.py')
    c017_ready = '9ce55e71eff2be6fee366b52434042985de263e6'
    if version == 4 and (any((ROOT / path).exists() or (ROOT / path).is_symlink() for path in c017_markers) or
            git('merge-base', '--is-ancestor', c017_ready, 'HEAD').returncode == 0):
        for identity in ('neopixel_null_sendreport_characterization',
                         'gp_config017_neopixel_repaired_current'):
            rows = [entry for entry in entries if entry['id'] == identity]
            if len(rows) != 1 or not (c022_replay_arguments(rows[0]) or c021_replay_arguments(rows[0]) or c017_replay_arguments(rows[0])):
                raise ValueError('missing required035 current load-bearing proof: ' + identity)
    c021_markers = ('docs/runtime_config/fixtures/gp_val038_c021_transition.json',
                    'docs/runtime_config/fixtures/gp_val038_accepted_transitions.json',
                    'tools/glyph_c021_campaign_transition.py')
    if version == 4 and any((ROOT / path).exists() or (ROOT / path).is_symlink() for path in c021_markers):
        required038 = ('config_menu_invalid_state_characterization', 'configurator_setconfig_transaction', 'current_config_persistence_recovery_research', 'custom_modifier_cache_characterization', 'getconfig_raw_load_characterization', 'gp_config014_modifier_capacity', 'gp_config017_neopixel_repaired_current', 'gp_config019_usb_name_selection', 'gp_config020_button_validation', 'gp_config_012_button_mask_characterization', 'gp_config_013_usb_default_characterization', 'gp_kbd_001_keyboard_pipeline', 'neopixel_null_sendreport_characterization', 'setconfig_runtime_rebinding_characterization') + ('gp_config021_persisted_recovery',)
        for identity in required038:
            rows = [entry for entry in entries if entry['id'] == identity]
            if len(rows) != 1 or not (c022_replay_arguments(rows[0]) or c021_replay_arguments(rows[0])):
                raise ValueError('missing required038 current historical/source replay: ' + identity)
    c022_markers = ('docs/runtime_config/fixtures/gp_val039_c022_transition.json',
                    'docs/runtime_config/fixtures/gp_val039_accepted_transitions.json',
                    'tools/glyph_c022_campaign_transition.py')
    if version == 4 and any((ROOT / path).exists() or (ROOT / path).is_symlink() for path in c022_markers):
        required039 = (
            'config_menu_invalid_state_characterization', 'configurator_setconfig_transaction',
            'current_config_persistence_recovery_research', 'custom_modifier_cache_characterization',
            'getconfig_raw_load_characterization', 'gp_config014_modifier_capacity',
            'gp_config017_neopixel_repaired_current', 'gp_config019_usb_name_selection',
            'gp_config020_button_validation', 'gp_config_012_button_mask_characterization',
            'gp_config_013_usb_default_characterization', 'gp_kbd_001_keyboard_pipeline',
            'neopixel_null_sendreport_characterization', 'setconfig_runtime_rebinding_characterization',
            'gp_config021_persisted_recovery', 'gp_val035_c017_transition',
            'gp_val038_c021_transition', 'gp_config022_rgb_target_validation',
        )
        for identity in required039:
            rows = [entry for entry in entries if entry['id'] == identity]
            if len(rows) != 1 or not c022_replay_arguments(rows[0]):
                raise ValueError('missing required039 current immutable/current proof: ' + identity)
    c023_markers = ('docs/runtime_config/fixtures/gp_val042_c023_transition.json',
                    'docs/runtime_config/fixtures/gp_val042_accepted_transitions.json',
                    'tools/glyph_c023_campaign_transition.py')
    if version == 4 and any((ROOT / path).exists() or (ROOT / path).is_symlink() for path in c023_markers):
        row = [entry for entry in entries if entry['id'] == 'gp_config023_usb_index_validation']
        if len(row) != 1 or not c023_replay_arguments(row[0]):
            raise ValueError('missing required042 exact C023 candidate replay')
    if version == 5:
        package_scope.verify_manifest_coverage(ROOT, entries)
    exclusions: list[dict[str, object]] = []
    exclusion_ids: set[str] = set()
    exclusion_paths: set[str] = set()
    entry_paths = {str(entry["path"]) for entry in entries}
    for exclusion in value["strong_signal_exclusions"]:
        if not isinstance(exclusion, dict) or set(exclusion) != EXCLUSION_REQUIRED:
            raise ValueError(f"invalid strong-signal exclusion: {exclusion!r}")
        exclusion_id, exclusion_path = exclusion["id"], exclusion["path"]
        if not isinstance(exclusion_id, str) or exclusion_id in exclusion_ids:
            raise ValueError(f"duplicate strong-signal exclusion ID: {exclusion_id}")
        if not isinstance(exclusion_path, str) or exclusion_path in exclusion_paths:
            raise ValueError(f"duplicate strong-signal exclusion path: {exclusion_path}")
        if exclusion_path in entry_paths:
            raise ValueError(f"checker appears in manifest and exclusions: {exclusion_path}")
        if exclusion["reason"] not in EXCLUSION_REASONS:
            raise ValueError(f"invalid strong-signal exclusion reason: {exclusion['reason']}")
        if not isinstance(exclusion["detail"], str) or not exclusion["detail"]:
            raise ValueError(f"invalid strong-signal exclusion detail: {exclusion_id}")
        if not exclusion_path.startswith("tools/check_glyph_") or not exclusion_path.endswith(".py") or not (ROOT / exclusion_path).is_file():
            raise ValueError(f"invalid strong-signal exclusion path: {exclusion_path}")
        exclusion_ids.add(exclusion_id)
        exclusion_paths.add(exclusion_path)
        exclusions.append(exclusion)
    census = json.loads(CENSUS.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    census_entries = census.get("entries")
    if not isinstance(census_entries, list):
        raise ValueError("invalid checker census entries")
    strong_paths: set[str] = set()
    for census_entry in census_entries:
        if not isinstance(census_entry, dict) or not isinstance(census_entry.get("path"), str):
            raise ValueError("invalid checker census entry")
        signals = census_entry.get("runtime_config_relevance_signals")
        if not isinstance(signals, list) or not all(isinstance(signal, str) for signal in signals):
            raise ValueError(f"invalid checker census relevance signals: {census_entry['path']}")
        if signals:
            strong_paths.add(census_entry["path"])
    replay_paths = frozenset()
    if current_package:
        # Extracted classification only. These paths are not replayed and do
        # not provide current safety proof or historical PASS in this mode.
        replay_paths = frozenset(package_scope.public_contract(ROOT)["historical_checker_classification"])
    if any(entry['applicability'] == 'current' and entry['id'] == 'gp_config023_usb_index_validation' and c023_replay_arguments(entry)
           for entry in entries):
        from glyph_c023_campaign_transition import replay_covered_checker_paths
        if package_scope.package_lineage(ROOT):
            with tempfile.TemporaryDirectory(prefix="glyph-c023-classify-") as directory:
                proof = package_scope.original_proof(ROOT, Path(directory))
            _C023_RESULT.set((ROOT, git_value("rev-parse", "HEAD"), proof))
            replay_paths = frozenset(proof["covered"])
        else:
            replay_paths = replay_covered_checker_paths(ROOT)
    elif any(entry['applicability'] == 'current' and entry['id'] == 'gp_config022_rgb_target_validation' and c022_replay_arguments(entry)
           for entry in entries):
        from glyph_c022_campaign_transition import replay_covered_checker_paths
        replay_paths = replay_covered_checker_paths(ROOT)
    elif any(entry['applicability'] == 'current' and entry['id'] == 'gp_config021_persisted_recovery' and c021_replay_arguments(entry)
           for entry in entries):
        from glyph_c021_campaign_transition import replay_covered_checker_paths
        replay_paths = replay_covered_checker_paths(ROOT)
    for path in sorted(strong_paths - entry_paths - exclusion_paths - replay_paths):
        raise ValueError(f"unclassified strong-signal checker: {path}")
    for path in sorted(exclusion_paths - strong_paths):
        raise ValueError(f"strong-signal exclusion lacks census signal: {path}")
    if current_package and package_scope.semantic_digest(value) != package_scope.public_contract(ROOT)["manifest_semantic_digest"]:
        raise ValueError("sealed manifest document identity drift")
    return entries, exclusions, categories



def census_freshness() -> dict[str, object]:
    committed = CENSUS.read_text(encoding="utf-8")
    expected = render_census(generate_census(ROOT))
    require_budget("census evaluation")
    return {
        "id": "checker_census_freshness",
        "path": "tools/check_glyph_checker_census.py",
        "category": "baseline",
        "applicability": "current",
        "load_bearing": True,
        "status": "PASS" if committed == expected else "FAIL",
    }


class AggregateTimeout(RuntimeError):
    pass


class DeadlineAlarm:
    """Own a one-shot operational alarm, including its non-throwing retirement.

    Cleanup has its own bounded TERM/reap clocks. Retiring this alarm never
    grants further operational budget: main checks the absolute deadline too.
    """
    def __init__(self, phase):
        self.phase = phase
        self.interrupt = True
        self.expired = False
        self.previous_handler = None
        self.previous_timer = (0., 0.)
        self.started = monotonic()

    def handler(self, signum, frame):
        self.expired = True
        if self.interrupt:
            self.interrupt = False  # One-shot delivery; retirement cannot raise it twice.
            raise AggregateTimeout("AGGREGATE_TIMEOUT during " + str(self.phase()))

    def start(self, seconds):
        # Install and arm atomically with respect to SIGALRM delivery.
        mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            self.previous_handler = signal.signal(signal.SIGALRM, self.handler)
            self.previous_timer = signal.setitimer(signal.ITIMER_REAL, seconds)
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, mask)

    def stop(self):
        # A one-shot alarm can arrive before the first assignment executes.
        # Catch that boundary once, then make all remaining retirement steps
        # non-throwing for our handler, including an already queued callback.
        try:
            self.interrupt = False
        except AggregateTimeout:
            self.interrupt = False
            self.expired = True
        mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            signal.setitimer(signal.ITIMER_REAL, 0)
            if signal.SIGALRM in signal.sigpending():
                signal.sigwait({signal.SIGALRM})
                self.expired = True
            if self.previous_handler is not None:
                signal.signal(signal.SIGALRM, self.previous_handler)
                if self.previous_timer[0] > 0:
                    remaining = self.previous_timer[0] - (monotonic() - self.started)
                    signal.setitimer(signal.ITIMER_REAL, max(.000001, remaining), self.previous_timer[1])
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, mask)
        return self.expired


# None outside an aggregate invocation; each main owns a fresh lifecycle scope.
_CLEANUP_UNPROVEN = ContextVar("glyph_cleanup_unproven", default=None)


def record_cleanup_failure(failure: str | None) -> None:
    if failure == "PROCESS_CLEANUP_FAILURE" and _CLEANUP_UNPROVEN.get() is not None:
        _CLEANUP_UNPROVEN.set(True)


DEADLINE: float | None = None
EXECUTION_ENV: dict[str, str] | None = None
SELF_TEST_COMMANDS = {
    "checker_context": ["python3", "tools/check_glyph_checker_context.py"],
    "validation_aggregate_adversarial": ["python3", "tools/check_glyph_runtime_config_validation_aggregate.py"],
}
X1_COMMAND = ["python3", "tools/check_glyph_current_x1_regression_subset.py"]
X1_REF = "refs/heads/runtime-config-x1-offset41-hardware-candidate"
X1_CANDIDATE = "74ae24364b84520d4e0e39240beb9867653cc7b9"
X1_OBJECTS = (X1_CANDIDATE, "6b0061489cb67d345f212f75268455c181ba271f", "1597c01b416b6aa697d73efc7d2c2b3695dc3e5c")
GP_CONFIG_010_SEMANTIC_COMMAND = ["python3", "tools/check_glyph_config_010_integration_semantic_correspondence.py"]
GP_CONFIG_010_HISTORICAL_CANDIDATE = "f4771e17430fd1ea3f1e3e5339a83dfe648290a3"


def require_budget(label: str) -> float:
    remaining = 300.0 if DEADLINE is None else DEADLINE - monotonic()
    if remaining <= 0:
        raise AggregateTimeout(f"AGGREGATE_TIMEOUT during {label}")
    return remaining


def restore_operational_alarm(timer, suspended_at: float) -> bool:
    """Restore remaining time, never granting the time spent in cleanup again."""
    if not timer[0]:
        return False
    target = DEADLINE if DEADLINE is not None else suspended_at + timer[0]
    remaining = target - monotonic()
    if remaining <= 0:
        return True
    signal.setitimer(signal.ITIMER_REAL, remaining, timer[1] if DEADLINE is None else 0)
    return False


def base_environment() -> dict[str, str]:
    # PATH is the only ambient execution input. Interpreter identity is not claimed.
    return {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0", "PYTHONNOUSERSITE": "1",
            "LC_ALL": "C", "LANG": "C", "TZ": "UTC", "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_OPTIONAL_LOCKS": "0"}


def isolated_environment(parent: Path, context_data: dict[str, object] | None = None) -> dict[str, str]:
    env = base_environment()
    for key, name in {"HOME": "home", "TMPDIR": "tmp", "TMP": "tmp", "TEMP": "tmp",
                      "XDG_CONFIG_HOME": "config", "XDG_CACHE_HOME": "cache", "PYTHONPYCACHEPREFIX": "pycache"}.items():
        path = parent / "environment" / name
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    if context_data is not None:
        env.update({"GLYPH_CHECKER_BASE": str(context_data["base"]),
                    "GLYPH_CHECKER_EXPECTED_MERGE_BASE": str(context_data["expected_merge_base"])})
    return env


def checker_environment(entry: dict[str, object], env: dict[str, str]) -> dict[str, str]:
    result = dict(env)
    if SELF_TEST_COMMANDS.get(str(entry["id"])) == entry["command"]:
        result.pop("GLYPH_CHECKER_BASE", None)
        result.pop("GLYPH_CHECKER_EXPECTED_MERGE_BASE", None)
    return result


def checker_time_budget(entry: dict[str, object]) -> float:
    # This baseline self-test now includes over 100 controls. Its measured
    # standalone runtime approaches the ordinary 140s cap; isolated aggregate
    # dispatch has exceeded it. Give only this exact suite scheduling margin.
    # Individual deadline/cleanup controls and the aggregate's 450s bound stay
    # unchanged, and dispatch still clips this allowance to remaining time.
    identity = "validation_aggregate_adversarial"
    command = SELF_TEST_COMMANDS[identity]
    if entry["id"] == identity and entry["path"] == command[1] and entry["command"] == command:
        return ADVERSARIAL_TIMEOUT_SECONDS
    return CHECKER_TIMEOUT_SECONDS


def group_exists(pid: int) -> bool:
    try:
        os.killpg(pid, 0)
        return True
    except ProcessLookupError:
        return False


def signal_group(pid: int, signum: int) -> None:
    try:
        os.killpg(pid, signum)
    except ProcessLookupError:
        pass


def child_exec(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    """Called only after the parent owns the forked child; tests may delay exec."""
    os.chdir(cwd)
    os.execvpe(command[0], command, env)


def execution_command(command: list[str]) -> list[str]:
    """Bind portable manifest Python commands to this runner's interpreter."""
    if not command or command[0] != "python3":
        return command
    executable = Path(sys.executable)
    if not executable.is_absolute():
        raise ValueError("invoking Python executable must be an absolute path")
    try:
        mode = executable.stat().st_mode
    except OSError as exc:
        raise ValueError(f"invoking Python executable is unusable: {executable}") from exc
    if not stat.S_ISREG(mode) or not os.access(executable, os.X_OK):
        raise ValueError(f"invoking Python executable is unusable: {executable}")
    return [str(executable), *command[1:]]


def child_setup_status(fd: int, message: dict[str, object]) -> None:
    """One bounded setup record; this descriptor closes atomically on exec."""
    data = (json.dumps(message, sort_keys=True) + "\n").encode()
    if len(data) > 4096 or os.write(fd, data) != len(data):
        raise ValueError("child setup status write incomplete")


def run_process(command: list[str], cwd: Path, env: dict[str, str], timeout: float,
                *, input_text: str | None = None, input_file=None, output_file=None) -> tuple[int | None, bytes, bytes, str | None, float]:
    """Return raw byte streams; acquire before exec and finish bounded cleanup.

    Until the parent validates READY and releases the gate, only the owned
    direct child may run. EOF after release proves the trusted exec path closed
    its CLOEXEC status pipe; errors before exec carry their phase and errno.
    Descendants that deliberately leave the managed group are outside this
    POSIX group contract, as before. No session-less fallback is permitted.
    """
    if _CLEANUP_UNPROVEN.get():
        return None, b"", b"managed lifecycle closure unproved; dispatch refused", "PROCESS_CLEANUP_FAILURE", 0.
    started = monotonic()
    pid = None
    exit_code = None
    failure = None
    phase = "pipes"
    ready = False
    acquired = False
    cleaned = False
    cleanup_finished = False
    completed = False
    cleanup_errors = []
    group_denials = []
    streams = {"stdout": bytearray(), "stderr": bytearray()}
    status_bytes = bytearray()
    descriptors: set[int] = set()
    selector = None
    input_bytes = (input_text or "").encode()
    input_offset = 0

    def diagnostic(kind, where, exc=None, **details):
        row = dict(kind=kind, phase=where, pid=pid, managed_pgid=pid if ready else None, **details)
        if exc is not None:
            row.update(error=str(exc), errno=getattr(exc, "errno", None))
        streams["stderr"].extend((json.dumps(row, sort_keys=True) + "\n").encode())

    def pipe():
        pair = os.pipe()  # Python's pipes are non-inheritable (CLOEXEC).
        descriptors.update(pair)
        return pair

    def close(fd):
        if fd in descriptors:
            descriptors.remove(fd)
            os.close(fd)

    def reap() -> bool:
        nonlocal exit_code
        if exit_code is None:
            mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
            try:
                found, status = os.waitpid(pid, os.WNOHANG)
                if found:
                    exit_code = os.waitstatus_to_exitcode(status)
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, mask)
        return exit_code is not None

    def setup_record(record):
        nonlocal ready, failure
        try:
            message = json.loads(record)
        except (ValueError, UnicodeError):
            raise ValueError("malformed child setup record") from None
        if not isinstance(message, dict):
            raise ValueError("child setup record must be an object")
        if message.get("status") == "ERROR":
            if set(message) != {"status", "phase", "errno", "error"}:
                raise ValueError("malformed child setup error")
            failure = "CHILD_SETUP_FAILURE"
            diagnostic(failure, "child:" + str(message["phase"]),
                       reported_errno=message["errno"], error=message["error"])
        elif (not ready and message == {"status": "READY", "pid": pid, "pgid": pid, "sid": pid}
              and os.getpgid(pid) == pid and os.getsid(pid) == pid):
            ready = True
            if cleaned:
                close(release_write)
                return
            if os.write(release_write, b"G") != 1:
                raise ValueError("child release incomplete")
            close(release_write)
        else:
            raise ValueError("invalid child setup identity or sequence")

    def drain(duration: float) -> None:
        nonlocal input_offset, acquired, failure
        wait = max(0, duration)
        if not selector.get_map():
            # EOF can precede waitpid readiness by a scheduler tick. Do not
            # impose a full I/O poll on every already-closed Git process.
            wait = min(wait, .001)
        for key, _ in selector.select(wait):
            fd, label = key.fd, key.data
            if label == "stdin":
                try:
                    input_offset += os.write(fd, input_bytes[input_offset:input_offset + 65536])
                except BrokenPipeError:
                    input_offset = len(input_bytes)
                if input_offset == len(input_bytes):
                    selector.unregister(fd)
                    close(fd)
            else:
                block = os.read(fd, 65536)
                if label == "setup" and not cleaned:
                    status_bytes.extend(block)
                    if len(status_bytes) > 4096:
                        raise ValueError("child setup record exceeds bound")
                    while b"\n" in status_bytes:
                        record, _, rest = status_bytes.partition(b"\n")
                        status_bytes[:] = rest
                        setup_record(record)
                    if not block:
                        if status_bytes or not ready:
                            raise ValueError("child setup EOF before success")
                        acquired = failure is None
                elif block and label != "setup":
                    streams[label].extend(block)
                if not block:
                    selector.unregister(fd)
                    close(fd)

    def managed_group(signum: int = 0) -> bool:
        # Darwin can return EPERM for a group containing only an unreaped
        # zombie leader. Reap our child first. Resolve a racing EPERM only by
        # proving group absence afterwards; an extant/denied group fails closed.
        reap()
        try:
            os.killpg(pid, signum)
            return True
        except ProcessLookupError:
            return False
        except PermissionError as exc:
            reap()
            if not group_exists(pid):
                diagnostic("GROUP_ABSENT_AFTER_REAP", "killpg", exc, signal=signum)
                return False
            raise

    def terminate() -> None:
        nonlocal cleaned, cleanup_finished, failure
        if cleanup_finished or pid is None:
            return
        suspended_at = monotonic()
        timer = signal.setitimer(signal.ITIMER_REAL, 0)
        cleaned = True
        def attempt(where, action):
            try:
                return action()
            except (OSError, ValueError) as exc:
                if isinstance(exc, PermissionError) and ("killpg" in where or "group_probe" in where):
                    if where not in group_denials:
                        group_denials.append(where)
                        diagnostic("GROUP_OPERATION_DENIED", where, exc)
                    return None
                if where not in cleanup_errors:
                    cleanup_errors.append(where)
                    diagnostic("PROCESS_CLEANUP_FAILURE", where, exc)
                return None
        def send(signum):
            # A failed group operation must never skip direct-child escalation.
            attempt("cleanup.waitpid", reap)
            attempt("cleanup.killpg." + signal.Signals(signum).name,
                    lambda: signal_group(pid, signum))
            if exit_code is None:  # Never signal a reaped/reusable numeric PID.
                def direct():
                    try: os.kill(pid, signum)
                    except ProcessLookupError: pass
                attempt("cleanup.kill." + signal.Signals(signum).name, direct)
        try:
            send(signal.SIGTERM)
            grace_end = monotonic() + TERM_GRACE_SECONDS
            while monotonic() < grace_end:
                if selector is not None:
                    attempt("cleanup.drain", lambda: drain(min(.01, max(0, grace_end - monotonic()))))
                else:
                    sleep(.005)
                done = attempt("cleanup.waitpid", reap)
                exists = attempt("cleanup.group_probe", lambda: managed_group())
                if done and exists is False:
                    if group_denials:
                        diagnostic("GROUP_ABSENT_AFTER_REAP", "cleanup.proof",
                                   resolved_group_denials=group_denials, leader_reaped=True)
                    cleanup_finished = True
                    return
            # Always try KILL, including when group probes were denied.
            send(signal.SIGKILL)
            reap_end = monotonic() + CLEANUP_REAP_SECONDS
            while monotonic() < reap_end:
                done = attempt("cleanup.waitpid", reap)
                exists = attempt("cleanup.group_probe", lambda: managed_group())
                if done and exists is False:
                    if group_denials:
                        diagnostic("GROUP_ABSENT_AFTER_REAP", "cleanup.proof",
                                   resolved_group_denials=group_denials, leader_reaped=True)
                    cleanup_finished = True
                    return
                if selector is not None:
                    attempt("cleanup.drain", lambda: drain(min(.01, max(0, reap_end - monotonic()))))
                else:
                    sleep(.005)
            cleanup_errors.append("cleanup.proof")
            diagnostic("PROCESS_CLEANUP_FAILURE", "cleanup.proof",
                       leader_reaped=exit_code is not None, group_absence_proven=False)
            cleanup_finished = True
        finally:
            if restore_operational_alarm(timer, suspended_at):
                failure = failure or "AGGREGATE_TIMEOUT"
                diagnostic("AGGREGATE_TIMEOUT", "cleanup.suspended_alarm")

    try:
        try:
            selector = selectors.DefaultSelector()
            stdout_read, stdout_write = pipe() if output_file is None else (None, output_file.fileno())
            stderr_read, stderr_write = pipe()
            setup_read, setup_write = pipe()
            release_read, release_write = pipe()
            if input_file is not None:
                stdin_read, stdin_write = input_file.fileno(), None
            elif input_text is not None:
                stdin_read, stdin_write = pipe()
            else:
                stdin_read, stdin_write = os.open(os.devnull, os.O_RDONLY), None
                descriptors.add(stdin_read)
            phase = "fork"
            old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
            try:
                pid = os.fork()
            finally:
                if pid != 0:
                    signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)
            if pid == 0:
                child_phase = "setsid"
                try:
                    os.setsid()
                    child_phase = "stdio"
                    os.dup2(stdin_read, 0)
                    os.dup2(stdout_write, 1)
                    os.dup2(stderr_write, 2)
                    child_phase = "descriptors"
                    # Retain only the two setup channels in addition to stdio.
                    try:
                        inherited_fds = [int(name) for name in os.listdir("/dev/fd")]
                    except OSError:
                        for low, high in zip([3, *[fd + 1 for fd in sorted((setup_write, release_read))]],
                                             [*sorted((setup_write, release_read)), os.sysconf("SC_OPEN_MAX")]):
                            os.closerange(low, high)
                    else:
                        for descriptor in inherited_fds:
                            if descriptor > 2 and descriptor not in (setup_write, release_read):
                                try: os.close(descriptor)
                                except OSError: pass
                    child_phase = "signals"
                    signal.signal(signal.SIGALRM, signal.SIG_DFL)
                    signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)
                    child_phase = "ready"
                    child_setup_status(setup_write, dict(status="READY", pid=os.getpid(), pgid=os.getpgrp(), sid=os.getsid(0)))
                    child_phase = "release"
                    if os.read(release_read, 1) != b"G":
                        raise ValueError("parent did not release child")
                    os.close(release_read)
                    child_phase = "exec"
                    child_exec(command, cwd, env)
                    raise ValueError("child exec returned")
                except BaseException as exc:
                    try:
                        child_setup_status(setup_write, dict(status="ERROR", phase=child_phase,
                            errno=getattr(exc, "errno", None), error=str(exc)[:250]))
                    except BaseException:
                        pass  # EOF without READY is a protocol failure, never success.
                os._exit(127)
            phase = "parent_descriptors"
            for fd in (stdin_read, stdout_write, stderr_write, setup_write, release_read):
                close(fd)
            for fd, label, event in ((stdout_read, "stdout", selectors.EVENT_READ), (stderr_read, "stderr", selectors.EVENT_READ),
                                     (setup_read, "setup", selectors.EVENT_READ), (stdin_write, "stdin", selectors.EVENT_WRITE)):
                if fd is not None:
                    os.set_blocking(fd, False)
                    selector.register(fd, event, label)
            end = started + timeout
            setup_end = min(end, started + CHILD_SETUP_TIMEOUT_SECONDS)
            while selector.get_map() or exit_code is None:
                phase = "checker_execution" if acquired else "child_setup"
                remaining = (end if acquired else setup_end) - monotonic()
                if remaining <= 0:
                    failure = "CHECKER_TIMEOUT" if acquired else "CHILD_SETUP_TIMEOUT"
                    diagnostic(failure, phase)
                    break
                drain(min(.01, remaining))
                if failure:
                    break
                reap()
            if failure is None and exit_code == 127:
                # A failed exec-error report must still stop aggregate dispatch.
                # A real checker may also return 127; keep that ambiguity honest.
                failure = "UNREPORTED_LAUNCH_OR_EXIT_127"
                diagnostic(failure, "exec_or_checker_exit")
            if failure is None:
                if managed_group():
                    failure = "PROCESS_GROUP_REMAINS"
                else:
                    completed = True
        except AggregateTimeout as exc:
            failure = failure or "AGGREGATE_TIMEOUT"
            diagnostic("AGGREGATE_TIMEOUT", phase, exc)
        except (OSError, ValueError) as exc:
            failure = failure or ("CHILD_SETUP_PROTOCOL_FAILURE" if phase == "child_setup" else "PROCESS_CONTROL_FAILURE")
            diagnostic(failure, phase, exc)
        finally:
            if pid not in (None, 0) and not completed:
                terminate()
    except AggregateTimeout as exc:
        # A one-shot operational alarm can arrive just as cleanup begins.
        # Resume the unfinished bounded cleanup, never discard child ownership.
        if failure in (None, "CHECKER_TIMEOUT", "CHILD_SETUP_TIMEOUT"):
            failure = "AGGREGATE_TIMEOUT"
        diagnostic("AGGREGATE_TIMEOUT", "cleanup_entry", exc)
        if pid not in (None, 0) and not cleanup_finished:
            terminate()
    finally:
        if selector is not None:
            selector.close()
        for fd in list(descriptors):
            close(fd)
    if cleanup_errors:
        diagnostic("PROCESS_CLEANUP_FAILURE", "cleanup", primary_failure=failure, failed_operations=cleanup_errors)
        failure = "PROCESS_CLEANUP_FAILURE"
    record_cleanup_failure(failure)
    return exit_code, bytes(streams["stdout"]), bytes(streams["stderr"]), failure, monotonic() - started


def run_checker(command: list[str], cwd: Path, env: dict[str, str], timeout: float,
                *, input_text: str | None = None, input_file=None, output_file=None) -> tuple[int | None, str, str, str | None, float]:
    """Strict text boundary. Malformed checker text is a dispatch-stopping failure."""
    code, stdout, stderr, failure, duration = run_process(command, cwd, env, timeout,
        input_text=input_text, input_file=input_file, output_file=output_file)
    record_cleanup_failure(failure)
    decoded = []
    errors = []
    for label, raw in (("stdout", stdout), ("stderr", stderr)):
        try:
            decoded.append(raw.decode("utf-8", errors="strict"))
        except UnicodeDecodeError as exc:
            decoded.append("")
            errors.append(json.dumps(dict(kind="MALFORMED_TEXT_OUTPUT", stream=label,
                encoding="utf-8", start=exc.start, end=exc.end, prefix_hex=raw[:128].hex()), sort_keys=True))
    if errors:
        failure = failure or "MALFORMED_TEXT_OUTPUT"
        decoded[1] += "\n".join(errors) + "\n"
    return code, decoded[0], decoded[1], failure, duration


def git_bytes(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None,
              timeout: float | None = None) -> subprocess.CompletedProcess[bytes]:
    """Git transport for byte-oriented evidence. Never decode a successful probe."""
    remaining = require_budget("git " + " ".join(args[:2]))
    command = ["git", "-c", "protocol.allow=never", *args]
    code, stdout, stderr, failure, _ = run_process(command, cwd or ROOT,
        env if env is not None else EXECUTION_ENV or base_environment(), min(remaining, timeout) if timeout is not None else remaining)
    record_cleanup_failure(failure)
    if failure:
        if failure in {"CHECKER_TIMEOUT", "AGGREGATE_TIMEOUT"}:
            raise AggregateTimeout("AGGREGATE_TIMEOUT during git " + " ".join(args[:2]))
        raise ValueError(f"Git process control failed: {failure}: {stderr!r}")
    return subprocess.CompletedProcess(command, code, stdout, stderr)


def git(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None,
        timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    """Explicit strict UTF-8 contract for textual Git consumers."""
    result = git_bytes(*args, cwd=cwd, env=env, timeout=timeout)
    try:
        stdout = result.stdout.decode("utf-8", errors="strict")
        stderr = result.stderr.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"MALFORMED_GIT_TEXT_OUTPUT: git {args!r}: {exc}") from exc
    return subprocess.CompletedProcess(result.args, result.returncode, stdout, stderr)


def repository_path(root: Path, relative: bytes) -> bytes:
    """Keep raw Git path identity through POSIX filesystem access."""
    if (not relative or os.path.isabs(relative) or b"\0" in relative
            or b".." in relative.split(b"/")):
        raise ValueError(f"invalid raw repository path: {relative!r}")
    return os.path.join(os.fsencode(root), relative)


def nul_paths(raw: bytes) -> list[bytes]:
    """NUL framing and raw-byte ordering, without stripping any path bytes."""
    if not raw:
        return []
    if not raw.endswith(b"\0") or any(not path for path in raw[:-1].split(b"\0")):
        raise ValueError("malformed NUL-separated repository path enumeration")
    return sorted(raw[:-1].split(b"\0"))


def git_value(*args: str, cwd: Path | None = None) -> str:
    result = git(*args, cwd=cwd)
    if result.returncode:
        raise ValueError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def reject_partial_repository() -> None:
    values = git("config", "--local", "--get-regexp", r"^(extensions\.partialclone|remote\..*\.promisor)$")
    if values.returncode not in (0, 1):
        raise ValueError("could not inspect local object topology")
    if values.stdout.strip():
        raise ValueError("partial/promisor repository cannot prove offline local object completeness")


def require_clean_source() -> None:
    status = git_bytes("status", "--porcelain=v1", "--untracked-files=all", "-z").stdout
    if status:
        raise ValueError("source worktree must be clean; staged, unstaged, and untracked paths are refused")
    # Index stat shortcuts (assume-unchanged/skip-worktree/core.filemode) may
    # suppress git status. Compare the physical committed content directly.
    tree = git_bytes("ls-tree", "-r", "-z", "HEAD")
    if tree.returncode:
        raise ValueError("could not enumerate committed source tree")
    for record in tree.stdout.split(b"\0"):
        if not record: continue
        header, relative = record.split(b"\t", 1)
        mode, kind, identity = header.split()
        path = repository_path(ROOT, relative)
        try:
            physical = os.lstat(path)
            if mode == b"120000" and stat.S_ISLNK(physical.st_mode):
                data = os.readlink(path)
            elif mode in {b"100644", b"100755"} and stat.S_ISREG(physical.st_mode):
                actual_mode = b"100755" if physical.st_mode & stat.S_IXUSR else b"100644"
                if actual_mode != mode: raise ValueError("tracked executable mode differs")
                with open(path, "rb") as stream:
                    data = stream.read()
            else:
                raise ValueError("tracked path type differs or is unsupported")
            digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if kind != b"blob" or digest.encode("ascii") != identity:
                raise ValueError("tracked bytes or symlink target differ")
        except (OSError, ValueError) as exc:
            raise ValueError(f"source worktree must be clean: {relative!r}: {exc}") from exc
        require_budget("direct committed-source correspondence")


def required_catalog(selected: list[dict[str, object]]) -> tuple[dict[str, str], set[str]]:
    """Only current source-consumed identities authorized by the closed catalog."""
    refs: dict[str, str] = {}
    roots: set[str] = set()
    def has(checker_id: str, filename: str) -> bool:
        return any(entry["id"] == checker_id and entry["command"] == ["python3", "tools/" + filename] for entry in selected)
    if has("generated_baseline_artifact", "check_glyph_generated_source_owned_baseline_artifact.py"):
        identity = git_value("rev-parse", "--verify", "refs/heads/configurator^{commit}")
        refs["refs/heads/configurator"] = identity
        roots.add(identity)
    for checker_id, filename, identities in (
        ("build_input_resolution_observations", "check_glyph_build_input_resolution_observations.py", ("8c04262c66613d46b933b1b739c01c575cb0c580", "ffc007552abc848051841362b0b0ac4c1a7d087b")),
        ("nuker_source_lineage", "check_glyph_nuker_source_lineage.py", ("a747dd54b02b207483142331d8b5be1113fc951e", "d5050847d3f850951b3f47865dc8a91aedea0834")),
    ):
        if has(checker_id, filename):
            if package_scope.package_lineage(ROOT):
                # These two exact current commands now authenticate sealed
                # receipts instead of replaying historical Git observations.
                # Require their exact checked-in manifest records, not object
                # absence, before using the history-independent current proof.
                current_entries = json.loads((ROOT / "docs/runtime_config/fixtures/runtime_config_validation_manifest.json").read_text())["entries"]
                package_scope.verify_manifest_coverage(ROOT, current_entries)
                expected = next(row for row in current_entries if row["id"] == checker_id)
                if any(row != expected for row in selected if row["id"] == checker_id):
                    raise ValueError("invalid sealed current receipt command: " + checker_id)
            else:
                roots.update(identities)
    if any(entry["id"] == "gp_config_010_integration_semantic_correspondence"
           and entry["command"] == GP_CONFIG_010_SEMANTIC_COMMAND for entry in selected):
        roots.add(GP_CONFIG_010_HISTORICAL_CANDIDATE)
    # GP-VAL-037 finite proof roots, selected independently of framework execution.
    campaign_consumers = [('gp_config_012_button_mask_characterization', ['python3', 'tools/check_glyph_gp_config012_button_mask_characterization.py']), ('gp_config_013_usb_default_characterization', ['python3', 'tools/check_glyph_gp_config013_usb_default_characterization.py']), ('gp_config_010_integration_semantic_correspondence', ['python3', 'tools/check_glyph_config_010_integration_semantic_correspondence.py']), ('configurator_setconfig_transaction', ['python3', 'tools/check_glyph_configurator_setconfig_transaction.py']), ('current_config_persistence_recovery_research', ['python3', 'tools/check_glyph_current_config_persistence_recovery_research.py']), ('getconfig_raw_load_characterization', ['python3', 'tools/check_glyph_getconfig_raw_load_characterization.py']), ('setconfig_runtime_rebinding_characterization', ['python3', 'tools/check_glyph_setconfig_runtime_rebinding_characterization.py']), ('config_menu_invalid_state_characterization', ['python3', 'tools/check_glyph_config_menu_invalid_state_characterization.py']), ('checker_context', ['python3', 'tools/check_glyph_checker_context.py']), ('generated_source_contract', ['python3', 'tools/check_glyph_generated_source_owned_generator_contract.py']), ('generated_baseline_artifact', ['python3', 'tools/check_glyph_generated_source_owned_baseline_artifact.py']), ('artifact_install', ['python3', 'tools/check_glyph_generated_source_owned_artifact_install.py']), ('coordinate_native_contract', ['python3', 'tools/check_glyph_coordinate_native_runtime_profile_contract.py']), ('docs_agent_surface', ['python3', 'tools/check_glyph_docs_agent_surface.py']), ('campaign_webserial_source_authority', ['python3', 'tools/check_glyph_runtime_config_webserial_device_write_source_authority.py', '--campaign-transition'])]
    campaign_consumers.extend([
        ('custom_modifier_cache_characterization', ['python3', 'tools/check_glyph_custom_modifier_cache_characterization.py']),
        ('gp_config014_modifier_capacity', ['python3', 'tools/check_glyph_gp_config014_modifier_capacity.py']),
        ('gp_val034_c014_transition', ['python3', 'tools/test_glyph_c014_campaign_transition.py']),
        ('gp_val035_c017_transition', ['python3', 'tools/test_glyph_c017_campaign_transition.py']),
        ('neopixel_null_sendreport_characterization', ['python3', 'tools/check_glyph_neopixel_historical_replay.py']),
        ('gp_config017_neopixel_repaired_current', ['python3', 'tools/check_glyph_neopixel_historical_replay.py', '--repaired-current']),
        ('gp_config019_usb_name_selection', ['python3', 'tools/check_glyph_gp_config019_usb_name_selection.py']),
    ])
    campaign_consumers.extend([('gp_config021_persisted_recovery', ['python3', 'tools/check_glyph_c021_proof_replay.py']),
                               ('gp_val038_c021_transition', ['python3', 'tools/test_glyph_c021_campaign_transition.py'])])
    campaign_consumers.extend((identity, ['python3', 'tools/check_glyph_c021_proof_replay.py', '--consumer', lane])
                              for identity, lane in {'current_config_persistence_recovery_research': 'persistence', 'getconfig_raw_load_characterization': 'raw_get', 'configurator_setconfig_transaction': 'transaction005', 'setconfig_runtime_rebinding_characterization': 'rebind008', 'config_menu_invalid_state_characterization': 'menu009', 'gp_config_012_button_mask_characterization': 'button012', 'gp_config_013_usb_default_characterization': 'usb013', 'gp_config020_button_validation': 'button020', 'gp_kbd_001_keyboard_pipeline': 'kbd001', 'gp_config019_usb_name_selection': 'usb019', 'neopixel_null_sendreport_characterization': 'neopixel016_017', 'gp_config017_neopixel_repaired_current': 'neopixel016_017', 'custom_modifier_cache_characterization': 'modifier011', 'gp_config014_modifier_capacity': 'modifier014', 'gp_val035_c017_transition':'transition035'}.items())
    campaign_consumers.extend((identity, ['python3', 'tools/check_glyph_c022_proof_replay.py', '--consumer', lane])
        for identity, lane in {
            'current_config_persistence_recovery_research': 'persistence',
            'getconfig_raw_load_characterization': 'raw_get',
            'configurator_setconfig_transaction': 'transaction005',
            'setconfig_runtime_rebinding_characterization': 'rebind008',
            'config_menu_invalid_state_characterization': 'menu009',
            'gp_config_012_button_mask_characterization': 'button012',
            'gp_config_013_usb_default_characterization': 'usb013',
            'gp_config020_button_validation': 'button020',
            'gp_kbd_001_keyboard_pipeline': 'kbd001',
            'gp_config019_usb_name_selection': 'usb019',
            'neopixel_null_sendreport_characterization': 'neopixel016_017',
            'gp_config017_neopixel_repaired_current': 'neopixel016_017',
            'custom_modifier_cache_characterization': 'modifier011',
            'gp_config014_modifier_capacity': 'modifier014',
            'gp_val035_c017_transition': 'transition035',
            'gp_config021_persisted_recovery': 'recovery021',
            'gp_val038_c021_transition': 'transition038',
        }.items())
    campaign_consumers.extend((
        ('gp_config022_rgb_target_validation', ['python3', 'tools/check_glyph_c022_proof_replay.py']),
        ('gp_config023_usb_index_validation', ['python3', 'tools/check_glyph_c023_proof_replay.py']),
        ('gp_val039_c022_transition', ['python3', 'tools/test_glyph_c022_campaign_transition.py']),
    ))
    if package_scope.package_lineage(ROOT):
        # Current checker_context exercises synthetic branch scope and source
        # guardrails. Its package path never consumes C020/C024 replay roots.
        campaign_consumers = [(identity, command) for identity, command in campaign_consumers
                              if identity != "checker_context"]
    if any(entry['applicability'] == 'current'
           and entry['id'] == identity and entry['command'] == command
           for entry in selected for identity, command in campaign_consumers):
        from glyph_campaign_transition import ROOTS, TRANSITIONS, authenticate
        c023_selected = any(entry['applicability'] == 'current'
                            and entry['id'] == 'gp_config023_usb_index_validation'
                            and entry['command'] == ['python3', 'tools/check_glyph_c023_proof_replay.py']
                            for entry in selected)
        # The exact C023 replay command needs the candidate commit even while
        # GP-VAL-042 is still source-free. Authenticate that bounded source
        # contract whenever the command is selected; source overlay is only a
        # phase fact inside the authenticator, not a reason to fall back to
        # the predecessor's smaller object-root catalog.
        if c023_selected:
            from glyph_c023_campaign_transition import authenticate as authenticate_c023
            if package_scope.package_lineage(ROOT):
                classified = _C023_RESULT.get()
                if classified is not None and classified[:2] == (ROOT, git_value("rev-parse", "HEAD")):
                    proof = classified[2]
                else:
                    with tempfile.TemporaryDirectory(prefix="glyph-c023-catalog-") as directory:
                        proof = package_scope.original_proof(ROOT, Path(directory))
                roots.add(package_scope.C023_DONE)
            else:
                proof = authenticate_c023(ROOT)
        else:
            proof = authenticate(ROOT)
        roots.update(ROOTS)
        if proof.get('contract') in {'c020_abi_repair', 'c014_capacity', 'c017_neopixel', 'c021_persisted_recovery', 'c022_rgb_targets', 'c023_usb_index'}:
            # GP-VAL-043 exports only roots whose finite candidate, authority and
            # accepted-transition contracts passed the actual phase proof. The
            # mutable mapping/catalog never supplies runner authority by itself.
            repaired_roots = proof.get('object_roots')
            if (type(repaired_roots) is not frozenset or not repaired_roots
                    or any(not isinstance(identity, str) or re.fullmatch(r'[0-9a-f]{40}', identity) is None
                           for identity in repaired_roots)):
                raise ValueError('invalid authenticated campaign object roots')
            roots.update(repaired_roots)
        else:
            # Original037 keeps its authenticated historical catalog contract.
            catalog_path = ROOT / TRANSITIONS
            if catalog_path.exists():
                catalog = json.loads(catalog_path.read_text(), object_pairs_hook=pairs)
                for record in catalog['accepted_transitions']:
                    roots.update(record[k] for k in ('build', 'parent', 'review_commit', 'evidence_commit', 'integration'))
    return refs, roots


def immutable_source_context(selected: list[dict[str, object]]) -> dict[str, object]:
    require_clean_source()
    head = git_value("rev-parse", "--verify", "HEAD^{commit}")
    branch_result = git("symbolic-ref", "--quiet", "HEAD")
    if branch_result.returncode not in (0, 1):
        raise ValueError("source symbolic HEAD could not be resolved")
    branch_ref = branch_result.stdout.strip() if branch_result.returncode == 0 else None
    if branch_ref is not None and not branch_ref.startswith("refs/heads/"):
        raise ValueError("source HEAD must name a full local branch ref")
    branch = branch_ref.removeprefix("refs/heads/") if branch_ref else None
    remote = git("rev-parse", "--verify", "refs/remotes/origin/configurator^{commit}")
    comparison_ref = remote.stdout.strip() if remote.returncode == 0 else None
    override = os.environ.get("GLYPH_CHECKER_BASE")
    base = git_value("rev-parse", "--verify", f"{override}^{{commit}}") if override else comparison_ref
    if not base:
        if package_scope.package_lineage(ROOT):
            # Public current proof authenticates a source snapshot, not the
            # development fork's branch topology. This base is visible data.
            base = head
        else:
            raise ValueError("origin/configurator must resolve to an immutable commit without GLYPH_CHECKER_BASE")
    merge_base = git_value("merge-base", head, base)
    expected_input = os.environ.get("GLYPH_CHECKER_EXPECTED_MERGE_BASE")
    expected = git_value("rev-parse", "--verify", f"{expected_input}^{{commit}}") if expected_input else merge_base
    if expected != merge_base:
        raise ValueError("unexpected feature merge base: supplied GLYPH_CHECKER_EXPECTED_MERGE_BASE differs")
    if git("merge-base", "--is-ancestor", base, head).returncode:
        raise ValueError("comparison base is not an ancestor of HEAD")
    required_refs = {}
    roots = {head, base, merge_base, expected}
    if comparison_ref:
        roots.add(comparison_ref)
    catalog_refs, catalog_roots = required_catalog(selected)
    required_refs.update(catalog_refs)
    roots.update(catalog_roots)
    if any(entry["id"] == "current_x1_regression_subset" and entry["command"] == X1_COMMAND for entry in selected):
        if git_value("rev-parse", "--verify", f"{X1_REF}^{{commit}}") != X1_CANDIDATE:
            raise ValueError("required historical X1 candidate ref does not match its immutable identity")
        required_refs[X1_REF] = X1_CANDIDATE
        roots.update(X1_OBJECTS)
    for identity in sorted(roots):
        if git_value("rev-parse", "--verify", f"{identity}^{{commit}}") != identity:
            raise ValueError("required local commit identity unavailable")
    objects = git_value("rev-list", "--objects", "--missing=print", *sorted(roots))
    if any(line.startswith("?") for line in objects.splitlines()):
        raise ValueError("required immutable Git object closure is unavailable locally")
    return {"head": head, "branch": branch, "branch_ref": branch_ref, "detached": branch is None, "base": base,
            "merge_base": merge_base, "expected_merge_base": expected,
            "comparison_ref": comparison_ref, "required_refs": required_refs, "object_roots": sorted(roots)}


LOCATOR_LIMIT = 4096


def admitted_regular(path: bytes, *, optional: bool = False) -> os.stat_result | None:
    """Safety admission only: never open a nonregular fixed Git control file."""
    require_budget("Git-free metadata admission")
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        if optional:
            return None
        raise ValueError(f"MISSING_REQUIRED_GIT_CONTROL: {path!r}") from None
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"UNSAFE_GIT_CONTROL: {path!r} mode={info.st_mode:o}")
    return info


def locator_bytes(path: bytes, info: os.stat_result) -> bytes:
    """Bounded regular locator read, separately from payload serialization."""
    if info.st_size > LOCATOR_LIMIT:
        raise ValueError(f"OVERSIZED_GIT_LOCATOR: {path!r}")
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        actual = os.fstat(stream.fileno())
        if (not stat.S_ISREG(actual.st_mode) or
                (actual.st_dev, actual.st_ino, actual.st_mode) != (info.st_dev, info.st_ino, info.st_mode)):
            raise ValueError(f"GIT_LOCATOR_CHANGED_DURING_OPEN: {path!r}")
        raw = stream.read(LOCATOR_LIMIT + 1)
    if len(raw) > LOCATOR_LIMIT:
        raise ValueError(f"OVERSIZED_GIT_LOCATOR: {path!r}")
    return raw


def locator_record(raw: bytes, *, gitfile: bool) -> bytes:
    record = raw[:-1] if raw.endswith(b"\n") else raw
    if gitfile:
        if not record.startswith(b"gitdir: "):
            raise ValueError("MALFORMED_GITFILE: expected gitdir locator")
        record = record[len(b"gitdir: "):]
    if not record or any(value in record for value in (b"\0", b"\n", b"\r")):
        raise ValueError("MALFORMED_GIT_LOCATOR: empty, NUL or multiple records")
    return record


def directory_identity(info: os.stat_result) -> tuple[int, int, int]:
    # Transient acquisition evidence only; never part of the persistent digest.
    return info.st_dev, info.st_ino, info.st_mode


def walk_directory(raw: bytes, *, base_fd: int | None = None,
                   base_path: bytes | None = None) -> tuple[int, bytes]:
    """Open every raw component with kernel no-follow directory traversal.

    Dot is an explicit no-op. Dot-dot is opened against the currently owned
    directory FD BEFORE deriving its display spelling. Empty internal/trailing
    components refuse. Neither lexical normalization nor realpath has admission
    authority. The caller owns the returned descriptor, including on root /.
    """
    if not raw or b"\0" in raw:
        raise ValueError("MALFORMED_LOCATOR_TOPOLOGY")
    absolute = raw.startswith(b"/")
    components = raw.split(b"/")[1:] if absolute else raw.split(b"/")
    if raw == b"/":
        components = []
    if any(not part for part in components):
        raise ValueError("MALFORMED_LOCATOR_TOPOLOGY: empty component")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK
    if absolute:
        fd, path = os.open(b"/", flags), b"/"
    elif base_fd is not None and base_path is not None:
        fd, path = os.dup(base_fd), base_path
    else:
        raise ValueError("RELATIVE_LOCATOR_WITHOUT_ADMITTED_BASE")
    try:
        for component in components:
            require_budget("descriptor locator traversal")
            if component == b".":
                continue
            try:
                next_fd = os.open(component, flags, dir_fd=fd)
            except OSError as exc:
                raise ValueError(f"UNSAFE_LOCATOR_TOPOLOGY: component={component!r} errno={exc.errno}") from exc
            os.close(fd)
            fd = next_fd
            if not stat.S_ISDIR(os.fstat(fd).st_mode):
                raise ValueError("UNSAFE_LOCATOR_TOPOLOGY: nondirectory")
            # This spelling is derived only AFTER successful physical traversal.
            path = os.path.dirname(path) if component == b".." else os.path.join(path, component)
        if directory_identity(os.lstat(path)) != directory_identity(os.fstat(fd)):
            raise ValueError("LOCATOR_DIRECTORY_CHANGED_DURING_TRAVERSAL")
        return fd, path
    except BaseException:
        os.close(fd)
        raise


def admitted_directory(path: bytes, *, optional: bool = False) -> None:
    require_budget("Git-free directory admission")
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        if optional:
            return
        raise ValueError(f"MISSING_GIT_DIRECTORY: {path!r}") from None
    if not stat.S_ISDIR(info.st_mode):
        raise ValueError(f"UNSAFE_GIT_DIRECTORY: {path!r} mode={info.st_mode:o}")


def preflight_repository_safety(root: Path) -> dict[str, object]:
    """Git-free, fresh admission; never a token reusable across checker code.

    FIXED_PRECHECK_REQUIRED: .git/gitfile, commondir, HEAD, index, config.worktree,
    config, packed-refs, info/exclude and their final directory containers.
    ALREADY_COVERED: these raw objects/topology plus worktree bytes/modes/links
    and Git semantic index/ref/config/status outputs enter the fingerprint.
    BOUNDED_GIT_FAILURE_ACCEPTABLE: loose refs/ref-backend storage, object and
    worktree administration internals, config include targets and configuration-
    selected helpers. These dynamic Git-owned graphs are not recursively modeled.
    Fingerprint Git probes remain owned, deadline-bounded and fail closed on failure;
    success fingerprints semantic output. This is not an OS access sandbox or
    protection against concurrent malicious replacement during an admitted Git
    call. Arbitrary checker execution always requires a new admission afterward.
    """
    # The root itself is traversed without aliases too. Callers using macOS
    # /var aliases must supply the physical path; no-follow is never relaxed.
    raw_root = os.fsencode(root)
    if not raw_root.startswith(b"/"):
        raw_root = os.getcwdb() + b"/" + raw_root
    with ExitStack() as owned:
        root_fd, root_bytes = walk_directory(raw_root)
        owned.callback(os.close, root_fd)
        dot_git = os.path.join(root_bytes, b".git")
        try:
            dot_info = os.stat(b".git", dir_fd=root_fd, follow_symlinks=False)
        except FileNotFoundError:
            raise ValueError("MISSING_DOT_GIT") from None
        gitfile_raw = b""
        if stat.S_ISDIR(dot_info.st_mode):
            git_fd, git_dir = walk_directory(b".git", base_fd=root_fd, base_path=root_bytes)
            kind = b"DIRECTORY"
        elif stat.S_ISREG(dot_info.st_mode):
            gitfile_raw = locator_bytes(dot_git, dot_info)
            git_fd, git_dir = walk_directory(locator_record(gitfile_raw, gitfile=True),
                                            base_fd=root_fd, base_path=root_bytes)
            kind = b"GITFILE"
        else:
            raise ValueError(f"UNSAFE_DOT_GIT: mode={dot_info.st_mode:o}")
        owned.callback(os.close, git_fd)
        common_record = os.path.join(git_dir, b"commondir")
        common_info = admitted_regular(common_record, optional=True)
        common_raw = locator_bytes(common_record, common_info) if common_info is not None else b""
        if common_info is not None:
            common_fd, common = walk_directory(locator_record(common_raw, gitfile=False),
                                               base_fd=git_fd, base_path=git_dir)
        else:
            common_fd, common = os.dup(git_fd), git_dir
        owned.callback(os.close, common_fd)
        for directory in (os.path.join(common, b"info"), os.path.join(common, b"refs"),
                          os.path.join(common, b"objects")):
            admitted_directory(directory, optional=True)
        metadata = [(b"WORKTREE/" + name, os.path.join(git_dir, name))
                    for name in (b"HEAD", b"index", b"config.worktree")]
        metadata.extend((b"COMMON/" + name, os.path.join(common, name))
                        for name in (b"config", b"packed-refs", b"info/exclude"))
        for role, path in metadata:
            admitted_regular(path, optional=role != b"WORKTREE/HEAD")
        identities = tuple(directory_identity(os.fstat(fd)) for fd in (root_fd, git_fd, common_fd))
        for path, identity in zip((root_bytes, git_dir, common), identities):
            if directory_identity(os.lstat(path)) != identity:
                raise ValueError("GIT_LAYOUT_CHANGED_DURING_ADMISSION")
        return {"root": root_bytes, "dot_git": dot_git, "kind": kind,
                "gitfile_raw": gitfile_raw, "git_dir": git_dir, "common_dir": common,
                "commondir": common_record, "commondir_raw": common_raw, "metadata": metadata,
                "transient_directory_identities": identities}


def verify_layout_unchanged(root: Path, layout: dict[str, object]) -> None:
    # A fresh admission immediately before Git detects changed locators/targets.
    # This is not a defense against a privileged unrelated syscall-level racer.
    if preflight_repository_safety(root) != layout:
        raise ValueError("GIT_LAYOUT_CHANGED_BEFORE_PROBE")


def metadata_object(path: bytes) -> tuple[bytes, ...]:
    """Serialize one selected Git entry without following its final symlink.

    Only ENOENT at lstat means ABSENT. Nonblocking/no-follow open plus fstat
    prevents a regular-file inspection racing into a blocking FIFO/link read.
    Inode identity is checked for acquisition races, never fingerprinted.
    """
    require_budget("repository metadata object")
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return (b"ABSENT",)
    mode = str(info.st_mode).encode("ascii")
    if stat.S_ISLNK(info.st_mode):
        target = os.readlink(path)
        if not isinstance(target, bytes):
            raise ValueError("METADATA_TARGET_NOT_BYTES")
        return (b"PRESENT", mode, b"SYMLINK", target)
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"UNSUPPORTED_METADATA_OBJECT: {path!r} mode={info.st_mode:o}")
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (not stat.S_ISREG(opened.st_mode) or
                (opened.st_dev, opened.st_ino, opened.st_mode) != (info.st_dev, info.st_ino, info.st_mode)):
            raise ValueError(f"METADATA_OBJECT_CHANGED_DURING_OPEN: {path!r}")
        contents = stream.read()
    return (b"PRESENT", mode, b"REGULAR", contents)


def metadata_topology(path: bytes) -> tuple[bytes, ...]:
    """Prove lexical directory/link topology, without inode/time identity.

    Git may canonicalize directory discovery through a symlink. Include lexical
    components (also the source .git locator) so that an equal-byte directory
    replacement cannot hide behind the same resolved Git discovery output.
    Ordinary directory contents are covered by selected entries/Git probes;
    unrelated parent inode or permission changes are not repository evidence.
    """
    parts = []
    current = os.path.abspath(path)
    while current != os.path.dirname(current):
        parts.append(current)
        current = os.path.dirname(current)
    result = []
    for component in reversed(parts):
        require_budget("repository metadata topology")
        info = os.lstat(component)
        result.extend((component,))
        if stat.S_ISDIR(info.st_mode):
            result.append(b"DIRECTORY")
        elif stat.S_ISLNK(info.st_mode):
            result.extend(metadata_object(component))
        elif component == os.path.abspath(path) and stat.S_ISREG(info.st_mode):
            # Linked worktrees use a regular .git locator file.
            result.extend(metadata_object(component))
        else:
            raise ValueError(f"UNSUPPORTED_METADATA_TOPOLOGY: {component!r}")
    return tuple(result)


def canonical_fingerprint(root: Path | None = None) -> str:
    """Byte-exact files, paths, symlink targets and Git/index/ref/config evidence.

    Git paths and readlink targets never cross a Unicode text boundary. Text
    APIs elsewhere either decode strictly or refuse; they cannot normalize this
    proof. Explicit presence/type tags also distinguish missing metadata files
    from files whose literal contents happen to spell the absence marker.
    """
    if _CLEANUP_UNPROVEN.get():
        raise ValueError("PROCESS_CLEANUP_FAILURE: repository proof refused while lifecycle closure is unproved")
    root = root or ROOT
    layout = preflight_repository_safety(root)
    root_bytes = layout["root"]
    digest = hashlib.sha256()
    def add(value: bytes) -> None:
        digest.update(len(value).to_bytes(8, "big"))
        digest.update(value)
    def probe(*args: str):
        verify_layout_unchanged(root, layout)
        result = git_bytes(*args, cwd=root)
        if result.returncode and not (args[0] == "symbolic-ref" and result.returncode == 1):
            raise ValueError(f"canonical fingerprint probe failed: git {args!r}")
        add(b"GIT")
        add(str(len(args)).encode("ascii"))
        for argument in args:
            add(os.fsencode(argument))
        add(str(result.returncode).encode("ascii"))
        add(result.stdout)
        add(result.stderr)
        return result.stdout
    def git_path(*args: str) -> bytes:
        raw = probe(*args)
        # Git appends exactly one LF. Preserve any whitespace in the path itself.
        if not raw.endswith(b"\n") or not raw[:-1] or b"\0" in raw:
            raise ValueError("malformed Git metadata directory path")
        return raw[:-1]
    # Serialize admitted topology and raw fixed objects BEFORE invoking Git.
    git_dir, common = layout["git_dir"], layout["common_dir"]
    add(b"GIT_LAYOUT")
    add(layout["kind"])
    add(layout["gitfile_raw"])
    add(layout["commondir_raw"])
    for locator in sorted({layout["dot_git"], git_dir, common}):
        add(b"METADATA_TOPOLOGY")
        for value in metadata_topology(locator):
            add(value)
    metadata = [*layout["metadata"], (b"LOCATOR/commondir", layout["commondir"])]
    for role, path in metadata:
        add(b"METADATA_OBJECT")
        add(role)
        add(path)
        for value in metadata_object(path):
            add(value)
    # No admission is reused across arbitrary checker code. Git remains the
    # semantic authority; equivalent lexical spellings compare by safe admitted
    # filesystem topology, while original locator bytes remain hash evidence.
    discovered_git = git_path("rev-parse", "--absolute-git-dir")
    discovered_common = git_path("rev-parse", "--git-common-dir")
    if not os.path.isabs(discovered_git):
        raise ValueError("Git metadata directory must be absolute")
    if not os.path.isabs(discovered_common):
        discovered_common = os.path.join(root_bytes, discovered_common)
    # Git output is also traversed physically; no normalization decides identity.
    git_fd = common_fd = None
    try:
        git_fd, git_path_proof = walk_directory(discovered_git)
        common_fd, common_path_proof = walk_directory(discovered_common)
        if (git_path_proof != git_dir or common_path_proof != common
                or directory_identity(os.fstat(git_fd)) != layout["transient_directory_identities"][1]
                or directory_identity(os.fstat(common_fd)) != layout["transient_directory_identities"][2]):
            raise ValueError("GIT_LAYOUT_DISAGREEMENT: preflight versus Git discovery")
    finally:
        if git_fd is not None: os.close(git_fd)
        if common_fd is not None: os.close(common_fd)
    for args in (("rev-parse", "HEAD"), ("symbolic-ref", "--quiet", "HEAD"),
                 ("ls-files", "--stage", "-z"), ("for-each-ref", "--format=%(refname) %(objectname)"),
                 ("config", "--local", "--null", "--list"),
                 ("status", "--porcelain=v2", "--ignored=matching", "--untracked-files=all", "-z")):
        probe(*args)
    for label, args in ((b"TRACKED", ("ls-files", "-z")),
                        (b"UNTRACKED", ("ls-files", "--others", "--exclude-standard", "-z")),
                        (b"IGNORED", ("ls-files", "--others", "--ignored", "--exclude-standard", "-z"))):
        for relative in nul_paths(probe(*args)):
            require_budget("repository file fingerprint")
            path = repository_path(root, relative)
            add(label)
            add(relative)
            try:
                info = os.lstat(path)
                add(str(info.st_mode).encode("ascii"))
                if stat.S_ISLNK(info.st_mode):
                    target = os.readlink(path)  # bytes input gives bytes on POSIX.
                    if not isinstance(target, bytes):
                        raise ValueError("symlink target lost its byte representation")
                    add(b"SYMLINK")
                    add(target)
                elif stat.S_ISREG(info.st_mode):
                    add(b"REGULAR")
                    with open(path, "rb") as stream:
                        while block := stream.read(1024 * 1024):
                            require_budget("repository file bytes fingerprint")
                            add(block)
                else:
                    raise ValueError(f"unsupported repository path type: {relative!r}")
            except FileNotFoundError:
                add(b"MISSING")
    require_budget("completed repository fingerprint")
    return digest.hexdigest()


def clone_snapshot(context_data: dict[str, object], parent: Path) -> Path:
    clone = parent / "snapshot"
    completed = git("-c", "protocol.file.allow=always", "clone", "--no-local", "--no-checkout", str(ROOT), str(clone))
    if completed.returncode:
        raise ValueError(f"isolated clone failed: {completed.stderr.strip()}")
    if (clone / ".git/objects/info/alternates").exists():
        raise ValueError("isolated clone must not use object alternates")
    git_value("remote", "remove", "origin", cwd=clone)
    # Clone initially discovers refs locally; retain only the closed authorized set.
    for ref in git_value("for-each-ref", "--format=%(refname)", cwd=clone).splitlines():
        git_value("update-ref", "-d", ref, cwd=clone)
    roots = context_data["object_roots"]
    missing = any(git("cat-file", "-e", f"{identity}^{{commit}}", cwd=clone).returncode for identity in roots)
    if missing:
        pack = parent / "required-objects.pack"
        with pack.open("wb") as output:
            code, _, error, failure, _ = run_checker(["git", "-c", "protocol.allow=never", "pack-objects", "--revs", "--stdout"],
                ROOT, EXECUTION_ENV or base_environment(), require_budget("local immutable object packing"),
                input_text="\n".join(roots) + "\n", output_file=output)
        if failure:
            if failure in {"CHECKER_TIMEOUT", "AGGREGATE_TIMEOUT"}:
                raise AggregateTimeout("AGGREGATE_TIMEOUT during local immutable object packing")
            raise ValueError("local immutable object packing: " + failure + ": " + error.strip())
        if code:
            raise ValueError("local immutable object packing failed: " + error.strip())
        with pack.open("rb") as source:
            code, _, error, failure, _ = run_checker(["git", "-c", "protocol.allow=never", "index-pack", "--stdin"],
                clone, EXECUTION_ENV or base_environment(), require_budget("local immutable object import"), input_file=source)
        if failure:
            if failure in {"CHECKER_TIMEOUT", "AGGREGATE_TIMEOUT"}:
                raise AggregateTimeout("AGGREGATE_TIMEOUT during local immutable object import")
            raise ValueError("local immutable object import: " + failure + ": " + error.strip())
        if code:
            raise ValueError("local immutable object import failed: " + error.strip())
    for identity in roots:
        if git_value("rev-parse", "--verify", f"{identity}^{{commit}}", cwd=clone) != identity:
            raise ValueError("isolated required object identity differs")
    objects = git_value("rev-list", "--objects", "--missing=print", *roots, cwd=clone)
    if any(line.startswith("?") for line in objects.splitlines()):
        raise ValueError("isolated required object closure incomplete")
    if context_data["comparison_ref"]:
        git_value("update-ref", "refs/remotes/origin/configurator", str(context_data["comparison_ref"]), cwd=clone)
    for ref, identity in context_data["required_refs"].items():
        git_value("update-ref", ref, identity, cwd=clone)
    branch = context_data["branch"]
    if branch is None:
        git_value("checkout", "--detach", str(context_data["head"]), cwd=clone)
    else:
        git_value("checkout", "-B", str(branch), str(context_data["head"]), cwd=clone)
    expected_refs = dict(context_data["required_refs"])
    if branch:
        expected_refs["refs/heads/" + str(branch)] = context_data["head"]
    if context_data["comparison_ref"]:
        expected_refs["refs/remotes/origin/configurator"] = context_data["comparison_ref"]
    refs = dict(line.split(" ", 1) for line in git_value("for-each-ref", "--format=%(refname) %(objectname)", cwd=clone).splitlines())
    actual_branch = git("symbolic-ref", "--quiet", "HEAD", cwd=clone)
    if actual_branch.returncode not in (0, 1) or (actual_branch.stdout.strip() or None) != context_data["branch_ref"]:
        raise ValueError("isolated full symbolic HEAD correspondence failed")
    if refs != expected_refs or git_value("rev-parse", "HEAD", cwd=clone) != context_data["head"]:
        raise ValueError("isolated HEAD/ref correspondence failed")
    return clone


def main() -> int:
    global DEADLINE, EXECUTION_ENV
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", action="append")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    parser.add_argument("--require-ci-maintenance", action="store_true",
                        help="require exact accepted package inputs outside reviewed CI files")
    args = parser.parse_args()
    proof_context = _C023_RESULT.set(None)
    cleanup_context = _CLEANUP_UNPROVEN.set(False)
    previous_deadline, previous_env = DEADLINE, EXECUTION_ENV
    started = monotonic()
    DEADLINE = started + AGGREGATE_TIMEOUT_SECONDS
    before = None
    output = {"status": "FAIL", "failure_kind": None, "phase": "preflight", "message": None,
              "aggregate_timeout_seconds": AGGREGATE_TIMEOUT_SECONDS,
              "canonical_proof": "UNAVAILABLE", "results": [], "excluded": []}
    parent = None
    alarm = DeadlineAlarm(lambda: output["phase"])
    def refuse_unclosed_proofs():
        output["status"] = "FAIL"
        if output["failure_kind"] not in (None, "PROCESS_CLEANUP_FAILURE"):
            output["failure_before_cleanup"] = output["failure_kind"]
        output["failure_kind"] = "PROCESS_CLEANUP_FAILURE"
        if output["canonical_proof"] != "MISMATCH":
            output["canonical_proof"] = "UNAVAILABLE"
        reason = "managed lifecycle closure unproved; repository proof withheld"
        output["final_proof_error"] = reason
        for row in output["results"]:
            if row["isolated_proof"] != "MISMATCH":
                row["isolated_proof"] = "UNAVAILABLE"
                row["proof_error"] = reason
    try:
        try:
            alarm.start(AGGREGATE_TIMEOUT_SECONDS)
            parent = Path(tempfile.mkdtemp(prefix="glyph-runtime-config-validation-")).resolve()
            EXECUTION_ENV = isolated_environment(parent)
            try:
                preflight_repository_safety(ROOT)
                before = canonical_fingerprint()
                reject_partial_repository()
                freshness = census_freshness()
                output["census_freshness"] = freshness
                if freshness["status"] != "PASS":
                    raise ValueError("checker census is stale; run tools/generate_glyph_checker_census.py")
                entries, exclusions, categories = load()
                output["excluded"] = [{"id": entry["id"], "applicability": entry["applicability"], "reason": entry["reason"]} for entry in entries if entry["applicability"] != "current"] + [{"id": exclusion["id"], "applicability": "excluded", "reason": exclusion["reason"]} for exclusion in exclusions]
                output["manifest_entries"] = len(entries)
                output["strong_signal_exclusions"] = len(exclusions)
                if args.category and any(category not in categories for category in args.category):
                    raise ValueError("unknown category: " + ", ".join(sorted(set(args.category) - categories)))
                selected = [entry for entry in entries if entry["applicability"] == "current" and (not args.category or entry["category"] in args.category)]
                if args.category:
                    empty = sorted(set(args.category) - {str(entry["category"]) for entry in selected})
                    if empty:
                        raise ValueError("requested category selects zero current checks: " + ", ".join(empty))
                require_clean_source()
                if package_scope.package_lineage(ROOT):
                    output["phase"] = "accepted_and_current_package_comparison"
                    output["package_evidence"] = package_scope.package_evidence(
                        ROOT, parent, strict=args.require_ci_maintenance)
                elif args.require_ci_maintenance:
                    raise ValueError("CI maintenance requires the accepted package baseline ancestry")
                if not args.check_manifest:
                    output["phase"] = "source_context"
                    context_data = immutable_source_context(selected)
                    output["context"] = context_data
                    output["phase"] = "snapshot_setup"
                    clone = clone_snapshot(context_data, parent)
                    env = isolated_environment(parent, context_data)
                    isolated_before = canonical_fingerprint(clone)
                    for entry in selected:
                        output["phase"] = "checker:" + str(entry["id"])
                        remaining = require_budget(output["phase"])
                        configured_timeout = checker_time_budget(entry)
                        timeout = min(configured_timeout, remaining)
                        active = clone
                        checker_env = checker_environment(entry, env)
                        is_c023 = (entry["id"] == "gp_config023_usb_index_validation"
                                   and entry["path"] == "tools/check_glyph_c023_proof_replay.py"
                                   and package_scope.package_lineage(ROOT))
                        if is_c023:
                            active = package_scope.materialize(clone, package_scope.C023_DONE, parent)
                            checker_env.update(GLYPH_CHECKER_BASE=package_scope.C023_DONE,
                                               GLYPH_CHECKER_EXPECTED_MERGE_BASE=package_scope.C023_DONE)
                            replay_before = canonical_fingerprint(active)
                        code, stdout, stderr, failure, duration = run_checker(
                            execution_command(entry["command"]), active, checker_env, timeout
                        )
                        if failure == "CHECKER_TIMEOUT" and remaining <= configured_timeout:
                            failure = "AGGREGATE_TIMEOUT"
                        result = {"id": entry["id"], "command": entry["command"], "category": entry["category"],
                                  "applicability": entry["applicability"], "exit_code": code, "status": "FAIL",
                                  "failure_kind": failure, "timeout_seconds": timeout,
                                  "stdout_summary": stdout.strip().splitlines()[-1:], "stderr_summary": stderr.strip().splitlines()[-1:],
                                  "duration_seconds": round(duration, 3), "isolated_proof": "UNAVAILABLE"}
                        if is_c023:
                            result["historical_execution_source"] = package_scope.C023_DONE
                        output["results"].append(result)
                        record_cleanup_failure(failure)
                        if _CLEANUP_UNPROVEN.get():
                            refuse_unclosed_proofs()
                        else:
                            try:
                                if canonical_fingerprint(clone) != isolated_before or (is_c023 and canonical_fingerprint(active) != replay_before):
                                    result["isolated_proof"] = "MISMATCH"
                                    failure = failure or "ISOLATED_REPOSITORY_MUTATION"
                                else:
                                    result["isolated_proof"] = "MATCH"
                            except (AggregateTimeout, OSError, ValueError, subprocess.SubprocessError) as exc:
                                failure = failure or ("AGGREGATE_TIMEOUT" if isinstance(exc, AggregateTimeout) else "ISOLATED_PROOF_FAILURE")
                                result["proof_error"] = str(exc)
                        result["failure_kind"] = failure
                        result["status"] = "PASS" if code == 0 and not failure else "FAIL"
                        if failure:
                            output["failure_kind"] = failure
                            break
                        if code and args.fail_fast:
                            break
                output["status"] = "PASS" if not output["failure_kind"] and all(result["status"] == "PASS" for result in output["results"]) else "FAIL"
            except (AggregateTimeout, OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
                output["failure_kind"] = "AGGREGATE_TIMEOUT" if isinstance(exc, AggregateTimeout) else "SETUP_FAILURE"
                output["message"] = str(exc)
                output["status"] = "FAIL"
            finally:
                if _CLEANUP_UNPROVEN.get():
                    refuse_unclosed_proofs()
                elif before is not None:
                    try:
                        if canonical_fingerprint() == before:
                            output["canonical_proof"] = "MATCH"
                        else:
                            output["canonical_proof"] = "MISMATCH"
                            output["failure_kind"] = "CANONICAL_REPOSITORY_MUTATION"
                            output["status"] = "FAIL"
                    except (AggregateTimeout, OSError, ValueError, subprocess.SubprocessError) as exc:
                        output["canonical_proof"] = "UNAVAILABLE"
                        output["final_proof_error"] = str(exc)
                        output["failure_kind"] = output["failure_kind"] or ("AGGREGATE_TIMEOUT" if isinstance(exc, AggregateTimeout) else "FINAL_PROOF_FAILURE")
                        output["status"] = "FAIL"
                else:
                    output["status"] = "FAIL"
        except (AggregateTimeout, OSError, ValueError, subprocess.SubprocessError) as exc:
            output["status"] = "FAIL"
            output["failure_kind"] = "AGGREGATE_TIMEOUT" if isinstance(exc, AggregateTimeout) else "SETUP_FAILURE"
            output["message"] = str(exc)
        finally:
            # No atexit/context-manager recursive deletion may overrun the deadline.
            # A timed-out run can retain only its disposable scratch tree, reported explicitly.
            try:
                if _CLEANUP_UNPROVEN.get():
                    refuse_unclosed_proofs()
                    output["retained_temporary_directory"] = str(parent) if parent is not None else None
                elif parent is not None:
                    output["phase_before_cleanup"] = output["phase"]
                    code, _, error, failure, _ = run_checker(["rm", "-rf", str(parent)], parent.parent,
                        EXECUTION_ENV or base_environment(), require_budget("disposable cleanup"))
                    record_cleanup_failure(failure)
                    if _CLEANUP_UNPROVEN.get():
                        refuse_unclosed_proofs()
                    if failure in {"CHECKER_TIMEOUT", "AGGREGATE_TIMEOUT"}:
                        raise AggregateTimeout("disposable cleanup did not finish within the operational deadline")
                    if code or failure:
                        raise ValueError("disposable cleanup failed: " + str(failure or code) + ": " + error.strip())
            except (AggregateTimeout, OSError, ValueError, subprocess.SubprocessError) as exc:
                output["status"] = "FAIL"
                output["failure_kind"] = output["failure_kind"] or ("AGGREGATE_TIMEOUT" if isinstance(exc, AggregateTimeout) else "DISPOSABLE_CLEANUP_FAILURE")
                output["cleanup_error"] = str(exc)
                output["retained_temporary_directory"] = str(parent) if parent is not None else None
            finally:
                expired = alarm.stop()
                if _CLEANUP_UNPROVEN.get():
                    refuse_unclosed_proofs()
                if expired or monotonic() >= DEADLINE:
                    output["status"] = "FAIL"
                    output["failure_kind"] = output["failure_kind"] or "AGGREGATE_TIMEOUT"
                    output["message"] = output["message"] or "AGGREGATE_TIMEOUT during timer finalization"
                DEADLINE, EXECUTION_ENV = previous_deadline, previous_env
                _C023_RESULT.reset(proof_context)
                _CLEANUP_UNPROVEN.reset(cleanup_context)
    except AggregateTimeout as exc:
        # Covers delivery at the boundary of the inner finalizer itself. The
        # one-shot handler retires its raising mode before throwing, so this
        # recovery cannot be interrupted by the same operational deadline.
        output["status"] = "FAIL"
        output["failure_kind"] = output["failure_kind"] or "AGGREGATE_TIMEOUT"
        output["message"] = str(exc)
        alarm.stop()
        if _CLEANUP_UNPROVEN.get():
            refuse_unclosed_proofs()
        DEADLINE, EXECUTION_ENV = previous_deadline, previous_env
        _C023_RESULT.reset(proof_context)
        _CLEANUP_UNPROVEN.reset(cleanup_context)
    if args.json:
        print(json.dumps(output, sort_keys=True))
    elif args.check_manifest and output["status"] == "PASS":
        print(f"glyph_runtime_config_validation_manifest: PASS; entries={output['manifest_entries']}; strong_signal_exclusions={output['strong_signal_exclusions']}")
    else:
        print(f"glyph_runtime_config_validation: {output['status']}" + (": " + str(output["message"]) if output["message"] else ""))
        for result in output["results"]:
            print(f"- {result['id']}: {result['status']}")
        if output["failure_kind"]:
            print(f"failure_kind={output['failure_kind']}; phase={output['phase']}; canonical_proof={output['canonical_proof']}")
        print("excluded=" + ",".join(item["id"] for item in output["excluded"]))
    return 0 if output["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
