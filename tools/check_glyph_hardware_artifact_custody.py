#!/usr/bin/env python3
"""Adversarial self-test for local content-addressed hardware artifact custody."""

from __future__ import annotations

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


def main() -> int:
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
