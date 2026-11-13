"""Source scope for host proofs whose contracts require a closed historical tree.

The commands still execute and gate validation. Their recorded source SHA
makes a historical replay distinguishable from exercising the current firmware.
"""
import json
import os
from pathlib import Path
import sys
import subprocess

PACKAGE_BASE = "f4146bedebb50559454954b8e20c9b641aeba616"
C023_DONE = "b404453ef22cc994eec54338b8a23c3ba61df808"
MAINTENANCE_BRANCH = "codex/ci-productization-20261113"


def package_lineage(root):
    return subprocess.run(["git", "merge-base", "--is-ancestor", PACKAGE_BASE, "HEAD"],
                          cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


# Explicit maintenance surface. The union of all other tracked paths, types,
# modes and Git object IDs must match the accepted package snapshot exactly.
# No production subtree or executable under docs/ is generally exempt.
MAINTENANCE_INPUTS = frozenset({
    ".github/workflows/build.yml",
    "tools/glyph_ci_current_firmware.py",
    "tools/check_glyph_docs_agent_surface.py",
    "tools/glyph_ci_current_package_tests.py",
    "tools/check_glyph_checker_context.py",
    "tools/check_glyph_runtime_config_validation_aggregate.py",
    "tools/check_glyph_runtime_config_validation_health.py",
    "tools/check_glyph_source_owned_candidate_generation.py",
    "docs/runtime_config/runtime_config_validation_health.md",
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


RETIRED_PACKAGE_CHECKS = frozenset({
    'artifact_install',
    'campaign_webserial_source_authority',
    'config_menu_invalid_state_characterization',
    'configurator_setconfig_transaction',
    'coordinate_native_contract',
    'current_config_persistence_recovery_research',
    'custom_modifier_cache_characterization',
    'docs_agent_surface',
    'generated_baseline_artifact',
    'generated_source_contract',
    'getconfig_raw_load_characterization',
    'gp_config014_modifier_capacity',
    'gp_config017_neopixel_repaired_current',
    'gp_config019_usb_name_selection',
    'gp_config020_button_validation',
    'gp_config021_persisted_recovery',
    'gp_config022_rgb_target_validation',
    'gp_config024_usb_profile_identity',
    'gp_config_010_integration_semantic_correspondence',
    'gp_config_010_mode_activation_capacity',
    'gp_config_012_button_mask_characterization',
    'gp_config_013_usb_default_characterization',
    'gp_kbd_001_keyboard_pipeline',
    'gp_prov_014_decoder_closure',
    'gp_val034_c014_transition',
    'gp_val035_c017_transition',
    'gp_val038_c021_transition',
    'gp_val039_c022_transition',
    'identity_table_source_sync',
    'neopixel_null_sendreport_characterization',
    'runtime_semantics_evaluator_bridge',
    'setconfig_runtime_rebinding_characterization',
    'table_symbol_map',
})


def verify_manifest_coverage(root, entries):
    path = "docs/runtime_config/fixtures/runtime_config_validation_manifest.json"
    baseline = json.loads(subprocess.check_output(["git", "show", PACKAGE_BASE + ":" + path], cwd=root))
    current = {row["id"]: row for row in entries}
    for original in baseline["entries"]:
        identity = original["id"]
        candidate = current.get(identity)
        if candidate is None or candidate["command"] != original["command"]:
            raise ValueError("missing or substituted required command: " + identity)
        expected = "historical_only" if identity in RETIRED_PACKAGE_CHECKS else original["applicability"]
        if candidate["applicability"] != expected:
            raise ValueError("invalid required current or historical classification: " + identity)


def current_package_comparison(root):
    subprocess.run(["git", "merge-base", "--is-ancestor", PACKAGE_BASE, "HEAD"],
                   cwd=root, check=True)
    changes = subprocess.check_output(
        ["git", "diff", "--name-only", "--no-renames", "-z", PACKAGE_BASE, "HEAD", "--"],
        cwd=root,
    ).split(b"\0")
    unexpected = sorted(p.decode() for p in changes if p and p.decode() not in MAINTENANCE_INPUTS)
    entries = subprocess.check_output(["git", "ls-tree", "-z", "HEAD", "--",
                                       *sorted(MAINTENANCE_INPUTS)], cwd=root)
    regular = {row.split(b"\t", 1)[1].decode() for row in entries.split(b"\0")
               if row.startswith(b"100644 blob ")}
    invalid = sorted(MAINTENANCE_INPUTS - regular)
    return {"accepted_source": PACKAGE_BASE,
            "candidate_source": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
            "outside_maintenance_paths": unexpected, "missing_or_changed_ci_modes": invalid,
            "status": ("CHANGED_INPUTS_HARDWARE_PENDING" if unexpected or invalid else
                       "EXACT_INPUTS_OUTSIDE_CI_MAINTENANCE"),
            "new_hardware_acceptance": False}


def verify_current_package(root):
    comparison = current_package_comparison(root)
    if comparison["outside_maintenance_paths"]:
        raise ValueError("source differs from accepted package outside reviewed CI maintenance: "
                         + ", ".join(comparison["outside_maintenance_paths"]))
    if comparison["missing_or_changed_ci_modes"]:
        raise ValueError("reviewed host-only path deleted or changed mode: "
                         + ", ".join(comparison["missing_or_changed_ci_modes"]))
    return comparison


def package_evidence(root, parent, strict=False):
    # The accepted proof script reads files and checks Git trees/ancestry. Run
    # its original bytes with its original worktree at the accepted commit.
    accepted = materialize(root, PACKAGE_BASE, parent)
    verifier = accepted / "docs/runtime_config/package_active_profile_display/integration_20261113/verify_correspondence.py"
    proof = subprocess.run([sys.executable, "-I", "-B", str(verifier)], cwd=accepted,
                           check=True, capture_output=True, text=True)
    strict = strict or os.environ.get("GITHUB_REF") == "refs/heads/" + MAINTENANCE_BRANCH or (
        os.environ.get("GITHUB_HEAD_REF") == MAINTENANCE_BRANCH)
    comparison = verify_current_package(root) if strict else current_package_comparison(root)
    comparison.update(historical_correspondence=proof.stdout.strip(),
                      maintenance_only_required=strict)
    return comparison


def original_proof(root, parent):
    frozen = materialize(root, C023_DONE, parent)
    # Import the original classifier in the original checkout. It checks C023
    # and authenticates the C022 replay paths using its original predicates.
    result = subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).resolve()),
                             "--historical-classifier"], cwd=frozen,
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError("C023 historical classifier failed: " + result.stderr.strip())
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


def run_historical_classifier():
    # Keep the original per-invocation memoization of immutable Git object
    # reads active across the proof and coverage calls. Neither result is
    # computed from the current checkout's campaign classifier.
    root = Path.cwd()
    if subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() != C023_DONE:
        raise ValueError("historical classifier invoked outside its exact source")
    sys.path.insert(0, str(root / "tools"))
    from glyph_campaign_transition import _proof_invocation
    from glyph_c023_campaign_transition import authenticate, replay_covered_checker_paths

    @_proof_invocation
    def classify():
        proof = authenticate(root)
        return {"contract": proof["contract"], "candidate": proof["candidate"],
                "object_roots": sorted(proof["object_roots"]),
                "covered": sorted(replay_covered_checker_paths(root))}

    print(json.dumps(classify()))


if __name__ == "__main__":
    if sys.argv[1:] != ["--historical-classifier"]:
        raise SystemExit("expected --historical-classifier")
    run_historical_classifier()
