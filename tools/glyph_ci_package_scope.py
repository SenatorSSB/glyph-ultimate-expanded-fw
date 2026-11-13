"""Source scope for host proofs whose contracts require a closed historical tree.

The commands still execute and gate validation. Their recorded source SHA
makes a historical replay distinguishable from exercising the current firmware.
"""
import json
from pathlib import Path
import sys
import subprocess

PACKAGE_BASE = "f4146bedebb50559454954b8e20c9b641aeba616"
C023_DONE = "b404453ef22cc994eec54338b8a23c3ba61df808"


def package_lineage(root):
    return subprocess.run(["git", "merge-base", "--is-ancestor", PACKAGE_BASE, "HEAD"],
                          cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


# Explicit maintenance surface. The union of all other tracked paths, types,
# modes and Git object IDs must match the accepted package snapshot exactly.
# No production subtree or executable under docs/ is generally exempt.
MAINTENANCE_INPUTS = frozenset({
    ".github/workflows/build.yml",
    "docs/runtime_config/fixtures/build_input_non_selector_configuration.json",
    "docs/runtime_config/fixtures/build_input_provenance_inventory.json",
    "docs/runtime_config/fixtures/glyph_checker_census.json",
    "docs/runtime_config/fixtures/runtime_config_validation_health.json",
    "docs/runtime_config/fixtures/runtime_config_validation_manifest.json",
    "docs/runtime_config/fixtures/runtime_config_validation_publication_workflow.json",
    "tools/check_glyph_build_input_non_selector_configuration.py",
    "tools/check_glyph_build_input_provenance_inventory.py",
    "tools/check_glyph_runtime_config_validation_publication_workflow.py",
    "tools/generate_glyph_checker_census.py",
    "tools/glyph_ci_build_inputs.py",
    "tools/glyph_ci_package_scope.py",
    "tools/glyph_workflow_step_contract.py",
    "tools/run_glyph_runtime_config_validation.py",
    "tools/test_glyph_ci_build_inputs.py",
})


def verify_current_package(root):
    subprocess.run(["git", "merge-base", "--is-ancestor", PACKAGE_BASE, "HEAD"],
                   cwd=root, check=True)
    changes = subprocess.check_output(
        ["git", "diff", "--name-only", "--no-renames", "-z", PACKAGE_BASE, "HEAD", "--"],
        cwd=root,
    ).split(b"\0")
    unexpected = sorted(p.decode() for p in changes if p and p.decode() not in MAINTENANCE_INPUTS)
    if unexpected:
        raise ValueError("source differs from accepted package outside reviewed CI maintenance: "
                         + ", ".join(unexpected))
    for path in MAINTENANCE_INPUTS:
        entry = subprocess.check_output(["git", "ls-tree", "-z", "HEAD", "--", path], cwd=root)
        if not entry.startswith(b"100644 blob ") or entry.count(b"\0") != 1:
            raise ValueError("reviewed host-only path deleted or changed mode: " + path)


def original_proof(root, parent):
    frozen = materialize(root, C023_DONE, parent)
    # Import the original classifier in the original checkout. It checks C023
    # and authenticates the C022 replay paths using its original predicates.
    code = ("import json,sys;from pathlib import Path;sys.path.insert(0,'tools');"
            "from glyph_c023_campaign_transition import authenticate,replay_covered_checker_paths;"
            "p=authenticate(Path.cwd());print(json.dumps(dict(contract=p['contract'],candidate=p['candidate'],object_roots=sorted(p['object_roots']),covered=sorted(replay_covered_checker_paths(Path.cwd())))))")
    result = subprocess.run([sys.executable, "-I", "-B", "-c", code], cwd=frozen,
                            check=True, capture_output=True, text=True)
    proof = json.loads(result.stdout)
    proof["object_roots"] = frozenset(proof["object_roots"])
    return proof


def materialize(snapshot, revision, parent):
    """Use only objects from the already isolated offline clone."""
    path = parent / ("replay-" + revision)
    if not path.exists():
        subprocess.run(["git", "clone", "--local", "--no-hardlinks", "--no-checkout",
                        str(snapshot), str(path)], check=True, capture_output=True)
        subprocess.run(["git", "remote", "remove", "origin"], cwd=path, check=True)
        subprocess.run(["git", "switch", "-C", "configurator", revision], cwd=path,
                       check=True, capture_output=True)
        subprocess.run(["git", "update-ref", "refs/remotes/origin/configurator", revision],
                       cwd=path, check=True)
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()
    if actual != revision:
        raise ValueError("historical execution checkout identity changed")
    return path
