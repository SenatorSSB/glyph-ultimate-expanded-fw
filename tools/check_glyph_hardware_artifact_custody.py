#!/usr/bin/env python3
"""Adversarial self-test for local content-addressed hardware artifact custody."""

from __future__ import annotations

import copy
import json
import re
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

from glyph_hardware_artifact_custody import (
    CustodyError,
    FILENAME,
    custody_path,
    preserve,
    require_clean_candidate_checkout,
    verify_preserved,
)


CANDIDATE_A = "a" * 40
CANDIDATE_B = "b" * 40
GOOD_BYTES = b"synthetic glyph hardware artifact\x00v1"
OTHER_BYTES = b"synthetic glyph rebuilt artifact\x00v2"


def expect_failure(label: str, operation) -> None:
    try:
        operation()
    except (CustodyError, OSError):
        return
    raise AssertionError(f"{label} was accepted")


def run_git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


CONTRACT_PATH = "docs/evidence/HARDWARE_EVIDENCE.md"
START = "<!-- hardware-evidence-contract-v1:start -->"
END = "<!-- hardware-evidence-contract-v1:end -->"
EXPECTED_CONTRACT = {'schema_name': 'glyph_public_hardware_evidence_contract',
 'schema_version': 1,
 'contract_id': 'GLYPH_PUBLIC_HARDWARE_EVIDENCE_V1',
 'custody': {'locator_template': 'local_backups/hardware-artifacts/<candidate_git_sha>/<artifact_sha256>/firmware.uf2',
             'write_once': True,
             'pre_handoff_rehash_required': True,
             'reject_symlink_or_nonregular': True,
             'different_rebuild_bytes_are_new_artifact': True},
 'acceptance': {'build_is_hardware_acceptance': False,
                'requires_exact_candidate_git_sha': True,
                'requires_exact_artifact_sha256': True,
                'requires_human_observed_scope': True,
                'acceptance_transfers_to_rebuild': False,
                'results': ['PASS', 'FAIL', 'PARTIAL', 'INCONCLUSIVE']},
 'device_operation': {'document_authorizes_flashing': False,
                      'document_authorizes_device_write': False,
                      'specific_user_authorization_required': True},
 'privacy': {'raw_private_evidence_may_remain_private': True,
             'public_claims_bounded_by_public_record': True},
 'provenance': {'extracted_from_commit': '367785cfe02d883c185327cfface06c37307f2b3',
                'historical_sources': [{'path': 'docs/agent_framework/HARDWARE_ARTIFACT_CUSTODY.md',
                                        'blob': 'd2e9ce8f2f7e0e7efa7f68a9af7f51c3261c0d59'},
                                       {'path': 'docs/agent_framework/HARDWARE_EVIDENCE.md',
                                        'blob': '9846a17d13929f4ad53e12fdc882be5dfcfd22e4'}]}}


def validate_contract(text: str) -> None:
    if text.count(START) != 1 or text.count(END) != 1:
        raise CustodyError("expected exactly one hardware contract marker pair")
    if text.index(START) >= text.index(END):
        raise CustodyError("misordered hardware contract markers")
    block = text.split(START)[1].split(END)[0]
    match = re.fullmatch(r"\s*```json\s*\n(.*?)\n```\s*", block, re.S)
    if not match:
        raise CustodyError("hardware contract must be fenced JSON")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise CustodyError("duplicate contract key: " + key)
            result[key] = value
        return result
    try:
        value = json.loads(match[1], object_pairs_hook=unique)
    except ValueError as exc:
        raise CustodyError("invalid hardware contract JSON") from exc
    def exact(actual, expected):
        if type(actual) is not type(expected):
            return False
        if isinstance(expected, dict):
            return actual.keys() == expected.keys() and all(exact(actual[k], v) for k, v in expected.items())
        if isinstance(expected, list):
            return len(actual) == len(expected) and all(exact(a, b) for a, b in zip(actual, expected))
        return actual == expected
    if not exact(value, EXPECTED_CONTRACT):
        raise CustodyError("hardware contract schema or safety invariant mismatch")


def contract_cases() -> None:
    text = (Path(__file__).resolve().parents[1] / CONTRACT_PATH).read_text()
    validate_contract(text)
    def rendered(value):
        return START + "\n```json\n" + json.dumps(value) + "\n```\n" + END
    # Independently reverse/remove every leaf and add unknown keys at every object.
    def mutations(value, path=()):
        if isinstance(value, dict):
            yield path + ("unexpected",), True, False
            for key, child in value.items():
                yield path + (key,), None, True
                yield from mutations(child, path + (key,))
        elif isinstance(value, list):
            yield path, [], False
            for i, child in enumerate(value):
                yield from mutations(child, path + (i,))
        else:
            replacement = not value if type(value) is bool else (0 if type(value) is int else "wrong")
            yield path, replacement, False
            if type(value) is bool:
                yield path, int(value), False
    count = 0
    for path, replacement, remove in mutations(EXPECTED_CONTRACT):
        bad = copy.deepcopy(EXPECTED_CONTRACT)
        parent = bad
        for key in path[:-1]:
            parent = parent[key]
        if remove:
            del parent[path[-1]]
        else:
            parent[path[-1]] = replacement
        expect_failure("contract mutation " + str(path), lambda: validate_contract(rendered(bad)))
        count += 1
    for bad in (text + START, text + END, text.replace(START, ""),
                text.replace("```json", "```text"), END + START,
                START + '\n```json\n{"schema_version":1,"schema_version":1}\n```\n' + END):
        expect_failure("contract framing", lambda: validate_contract(bad))
    print(f"public_hardware_contract=PASS; negative_controls={count + 6}")


def main() -> int:
    contract_cases()
    with tempfile.TemporaryDirectory(prefix="glyph-artifact-custody-") as temp:
        base = Path(temp).resolve()
        root = base / "local_backups" / "hardware-artifacts"
        absent_root = base / "absent" / "hardware-artifacts"
        source = base / "firmware.uf2"
        source.write_bytes(GOOD_BYTES)
        digest = hashlib.sha256(GOOD_BYTES).hexdigest()

        repo = base / "candidate-repo"
        repo.mkdir()
        run_git(repo, "init", "-q")
        run_git(repo, "config", "user.name", "Glyph Custody Self-Test")
        run_git(repo, "config", "user.email", "custody-self-test@example.invalid")
        tracked = repo / "tracked.txt"
        tracked.write_text("candidate A\n", encoding="utf-8")
        run_git(repo, "add", "tracked.txt")
        run_git(repo, "commit", "-q", "-m", "candidate A")
        candidate_a = run_git(repo, "rev-parse", "HEAD")
        require_clean_candidate_checkout(candidate_a, repo)
        tracked.write_text("candidate B\n", encoding="utf-8")
        run_git(repo, "commit", "-q", "-am", "candidate B")
        candidate_b = run_git(repo, "rev-parse", "HEAD")
        assert candidate_a != candidate_b
        expect_failure(
            "candidate SHA not equal to checked-out HEAD",
            lambda: require_clean_candidate_checkout(candidate_a, repo),
        )
        require_clean_candidate_checkout(candidate_b, repo)
        tracked.write_text("dirty\n", encoding="utf-8")
        expect_failure(
            "dirty candidate checkout",
            lambda: require_clean_candidate_checkout(candidate_b, repo),
        )
        run_git(repo, "restore", "tracked.txt")

        run_git(repo, "update-index", "--assume-unchanged", "tracked.txt")
        tracked.write_text("hidden change\n", encoding="utf-8")
        expect_failure(
            "assume-unchanged tracked divergence",
            lambda: require_clean_candidate_checkout(candidate_b, repo),
        )
        run_git(repo, "update-index", "--no-assume-unchanged", "tracked.txt")
        tracked.write_text("candidate B\n", encoding="utf-8")
        run_git(repo, "update-index", "--skip-worktree", "tracked.txt")
        tracked.write_text("hidden skip-worktree change\n", encoding="utf-8")
        expect_failure(
            "skip-worktree tracked divergence",
            lambda: require_clean_candidate_checkout(candidate_b, repo),
        )
        run_git(repo, "update-index", "--no-skip-worktree", "tracked.txt")
        tracked.write_text("candidate B\n", encoding="utf-8")
        run_git(repo, "config", "core.filemode", "false")
        tracked.chmod(0o755)
        expect_failure(
            "core.filemode tracked mode divergence",
            lambda: require_clean_candidate_checkout(candidate_b, repo),
        )
        tracked.chmod(0o644)

        (repo / ".gitignore").write_text("src/ignored.cpp\n.pio/\n", encoding="utf-8")
        run_git(repo, "add", ".gitignore")
        run_git(repo, "commit", "-q", "-m", "ignore policy")
        (repo / "src").mkdir()
        (repo / "src/ignored.cpp").write_text("compiler input\n", encoding="utf-8")
        expect_failure(
            "ignored critical source",
            lambda: require_clean_candidate_checkout(run_git(repo, "rev-parse", "HEAD"), repo),
        )
        (repo / "src/ignored.cpp").unlink()
        (repo / ".pio").mkdir()
        (repo / ".pio/cache.bin").write_text("dependency cache\n", encoding="utf-8")
        require_clean_candidate_checkout(run_git(repo, "rev-parse", "HEAD"), repo)

        expect_failure(
            "missing custody root",
            lambda: verify_preserved(absent_root, CANDIDATE_A, digest),
        )
        assert not absent_root.exists()

        target, observed, size, status = preserve(source, CANDIDATE_A, root)
        assert status == "PRESERVED_AND_VERIFIED"
        assert observed == digest and size == len(GOOD_BYTES)
        assert target == custody_path(root, CANDIDATE_A, digest)
        assert target.relative_to(root).as_posix() == f"{CANDIDATE_A}/{digest}/{FILENAME}"
        readback, readback_size = verify_preserved(root, CANDIDATE_A, digest)
        assert readback == target and readback_size == len(GOOD_BYTES)

        inode = target.stat().st_ino
        mtime_ns = target.stat().st_mtime_ns
        _, _, _, second_status = preserve(source, CANDIDATE_A, root)
        assert second_status == "ALREADY_PRESENT_VERIFIED"
        assert target.stat().st_ino == inode
        assert target.stat().st_mtime_ns == mtime_ns

        expect_failure(
            "wrong candidate identity",
            lambda: verify_preserved(root, CANDIDATE_B, digest),
        )
        expect_failure(
            "wrong artifact hash",
            lambda: verify_preserved(root, CANDIDATE_A, "0" * 64),
        )
        expect_failure(
            "malformed candidate SHA",
            lambda: custody_path(root, "A" * 40, digest),
        )
        expect_failure(
            "malformed artifact SHA",
            lambda: custody_path(root, CANDIDATE_A, "../escape"),
        )

        rebuilt = base / "rebuilt.uf2"
        rebuilt.write_bytes(OTHER_BYTES)
        rebuilt_target, rebuilt_digest, _, rebuilt_status = preserve(
            rebuilt, CANDIDATE_A, root
        )
        assert rebuilt_status == "PRESERVED_AND_VERIFIED"
        assert rebuilt_digest != digest and rebuilt_target != target
        assert target.read_bytes() == GOOD_BYTES

        os.chmod(target, 0o644)
        target.write_bytes(b"mutated")
        expect_failure(
            "mutated preserved artifact",
            lambda: verify_preserved(root, CANDIDATE_A, digest),
        )
        expect_failure(
            "overwrite of occupied content identity",
            lambda: preserve(source, CANDIDATE_A, root),
        )
        assert target.read_bytes() == b"mutated"

        target.unlink()
        expect_failure(
            "missing preserved artifact",
            lambda: verify_preserved(root, CANDIDATE_A, digest),
        )

        outside = base / "outside"
        outside.mkdir()
        symlink_root = base / "symlink-root"
        symlink_root.symlink_to(outside, target_is_directory=True)
        expect_failure(
            "symlink custody root",
            lambda: preserve(source, CANDIDATE_A, symlink_root),
        )

        source_link = base / "source-link.uf2"
        source_link.symlink_to(source)
        expect_failure(
            "symlink source artifact",
            lambda: preserve(source_link, CANDIDATE_A, root),
        )

        escaped_root = base / "escape-test"
        escaped_root.mkdir()
        candidate_link = escaped_root / CANDIDATE_A
        candidate_link.symlink_to(outside, target_is_directory=True)
        expect_failure(
            "symlink candidate component",
            lambda: preserve(source, CANDIDATE_A, escaped_root),
        )

    print("hardware_artifact_custody=PASS")
    print("synthetic_correct_path=PASS")
    print("synthetic_write_once=PASS")
    print("synthetic_readback_rehash=PASS")
    print("synthetic_wrong_identity_hash_missing_mutation=REJECTED")
    print("synthetic_rebuild_different_bytes=new_identity")
    print("synthetic_malformed_escape_symlink=REJECTED")
    print("real_firmware_artifact=NOT_CREATED_OR_READ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
