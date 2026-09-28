#!/usr/bin/env python3
"""Isolated positive and negative checks for GP-CONFIG-010 proof applicability."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "2fd9a827b90b2079f981d75e836833dc99ec7b10"
CANDIDATE = "1c0ff22646729d26d45eacb4b8322c5baea7de48"
CHECKER = "tools/check_glyph_config_010_integration_semantic_correspondence.py"
CLASSIFIER = "tools/glyph_hardware_correspondence.py"
SELF_HEAD = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def run(root: Path, *command: str, expected: int = 0) -> str:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True)
    if result.returncode != expected:
        raise AssertionError(f"{command!r}: expected {expected}, got {result.returncode}\n{result.stdout}{result.stderr}")
    return result.stdout


def commit_change(root: Path, path: str, text: str, branch: str) -> None:
    run(root, "git", "switch", "--detach", SELF_HEAD)
    run(root, "git", "switch", "-c", branch)
    location = root / path
    location.parent.mkdir(parents=True, exist_ok=True)
    location.write_text(location.read_text() + text if location.exists() else text)
    run(root, "git", "add", "--", path)
    run(root, "git", "commit", "-m", branch)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="gp-val-029-") as directory:
        root = Path(directory) / "repo"
        run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(root))
        run(root, "git", "config", "user.name", "GP-VAL-029 self-test")
        run(root, "git", "config", "user.email", "gp-val-029@example.invalid")
        run(root, "python3", CHECKER)
        commit_change(root, "docs/ROADMAP.md", "\nGP-VAL-029 isolated scope control.\n", "gp-val-029-positive")
        run(root, "python3", CHECKER)
        for label, path, data in (
            ("unknown-doc", "docs/unknown_gp_val_029.md", "unknown\n"),
            ("unknown-tool", "tools/unknown_gp_val_029.py", "# unknown\n"),
            ("critical-build", "platformio.ini", "\n; negative\n"),
            ("mode-source", "src/core/mode_selection.cpp", "\n// negative\n"),
            ("table-source", "src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp", "\n// negative\n"),
        ):
            commit_change(root, path, data, "gp-val-029-" + label)
            run(root, "python3", CHECKER, expected=1)
        run(root, "git", "switch", "--detach", SELF_HEAD)
        with (root / "src/core/mode_selection.cpp").open("a") as stream:
            stream.write("\n// dirty negative\n")
        run(root, "python3", CHECKER, expected=1)
        canonical = Path(directory) / "canonical"
        run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(canonical))
        run(canonical, "git", "switch", "--detach", BASE)
        shutil.copyfile(ROOT / CHECKER, canonical / CHECKER)
        shutil.copyfile(ROOT / CLASSIFIER, canonical / CLASSIFIER)
        run(canonical, "python3", CHECKER)
        # A separate clone keeps the dirty-source case out of historical proof.
        historical = Path(directory) / "historical"
        run(ROOT, "git", "clone", "--quiet", "--no-local", str(ROOT), str(historical))
        run(historical, "git", "switch", "--detach", CANDIDATE)
        run(historical, "git", "switch", "-c", "glyph/gp-config-010-current-canonical-integration")
        shutil.copyfile(ROOT / CHECKER, historical / CHECKER)
        run(historical, "python3", CHECKER, "--historical")
        run(historical, "git", "switch", "-c", "gp-val-029-wrong-branch")
        run(historical, "python3", CHECKER, "--historical", expected=1)
        run(historical, "git", "switch", "glyph/gp-config-010-current-canonical-integration")
        run(historical, "git", "config", "user.name", "GP-VAL-029 self-test")
        run(historical, "git", "config", "user.email", "gp-val-029@example.invalid")
        (historical / "docs/ROADMAP.md").write_text((historical / "docs/ROADMAP.md").read_text() + "\nnegative parent\n")
        run(historical, "git", "add", "docs/ROADMAP.md")
        run(historical, "git", "commit", "-m", "gp-val-029-wrong-parent")
        run(historical, "python3", CHECKER, "--historical", expected=1)
        run(historical, "python3", "-c", "import sys; sys.path.insert(0, 'tools'); import glyph_hardware_correspondence as c; c.NON_BEHAVIORAL_PATHS = c.NON_BEHAVIORAL_PATHS | {'platformio.ini'}; assert c.classify_path('platformio.ini') == 'CRITICAL'")
    print("gp_val_029_semantic_applicability: PASS; canonical, unrelated descendant, historical identity and negatives")


if __name__ == "__main__":
    main()
