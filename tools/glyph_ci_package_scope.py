"""Source scope for host proofs whose contracts require a closed historical tree.

The commands still execute and gate validation. Their recorded source SHA
makes a historical replay distinguishable from exercising the current firmware.
"""
import json
import hashlib
import stat
import os
from pathlib import Path
import sys
import subprocess

PACKAGE_BASE = "f4146bedebb50559454954b8e20c9b641aeba616"
C023_DONE = "b404453ef22cc994eec54338b8a23c3ba61df808"
MAINTENANCE_BRANCH = "codex/ci-productization-20261113"


PUBLIC_BASELINE = "docs/runtime_config/fixtures/public_package_baseline.v1.json"
# Reviewed extraction digest; updated only with a reviewed contract migration.
PUBLIC_BASELINE_SHA256 = "65bed35090fa2091bdc591f7c46e0b94f8cd1760d02dd50649775aa05f7406e3"
PROTECTED_PREFIXES = ("HAL/", "include/", "src/", "config/", "schema/", "lib/", "builder_scripts/", "scripts/")
PROTECTED_FILES = ("platformio.ini",)


def semantic_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _pairs(items):
    out = {}
    for key, value in items:
        if key in out:
            raise ValueError("duplicate public contract key: " + key)
        out[key] = value
    return out


def public_contract(root):
    """Authenticate current bytes. Historical object availability grants no authority."""
    root = Path(root)
    path = root / PUBLIC_BASELINE
    if path.is_symlink() or not path.is_file():
        raise ValueError("required sealed public package baseline missing")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PUBLIC_BASELINE_SHA256:
        raise ValueError("sealed public package baseline digest mismatch")
    value = json.loads(raw, object_pairs_hook=_pairs)
    if (value["schema"] != "glyph_public_package_baseline.v1"
            or value["protected_prefixes"] != list(PROTECTED_PREFIXES)
            or value["protected_files"] != list(PROTECTED_FILES)):
        raise ValueError("invalid closed public package boundary")
    inventory = value["protected_inputs"]
    indexed = {}
    for row in subprocess.check_output(["git", "ls-files", "-s", "-z"], cwd=root).split(b"\0"):
        if not row:
            continue
        meta, name = row.split(b"\t", 1)
        mode, oid, stage = meta.decode().split()
        name = name.decode()
        if name.startswith(PROTECTED_PREFIXES) or name in PROTECTED_FILES:
            if stage != "0" or name in indexed:
                raise ValueError("unmerged/duplicate protected source: " + name)
            indexed[name] = (mode, oid)
    disk = set()
    for prefix in PROTECTED_PREFIXES:
        base = root / prefix
        if base.is_symlink():
            raise ValueError("symlink protected directory: " + prefix)
        if base.exists():
            disk.update(p.relative_to(root).as_posix() for p in base.rglob("*") if p.is_file() or p.is_symlink())
    disk.update(p for p in PROTECTED_FILES if (root / p).exists())
    expected = {row["path"]: row for row in inventory}
    if len(expected) != len(inventory) or set(indexed) != set(expected) or disk != set(expected):
        raise ValueError("protected source closure mismatch")
    for name, record in expected.items():
        source = root / name
        if any(part.is_symlink() for part in (source, *source.parents) if part != root and root in part.parents):
            raise ValueError("symlink protected input: " + name)
        mode = "100755" if source.stat().st_mode & 0o111 else "100644"
        if (not stat.S_ISREG(source.stat().st_mode) or mode != record["git_mode"]
                or indexed[name][0] != mode or hashlib.sha256(source.read_bytes()).hexdigest() != record["sha256"]
                or indexed[name][1] != hashlib.sha1(b"blob " + str(len(source.read_bytes())).encode() + b"\0" + source.read_bytes()).hexdigest()):
            raise ValueError("protected current source mismatch: " + name)
    sealed = dict(value)
    recorded = sealed.pop("receipt_semantic_digest")
    if semantic_digest(sealed) != recorded:
        raise ValueError("public receipt semantic digest mismatch")
    manifest = root / value["manifest_path"]
    if manifest.is_symlink() or not manifest.is_file():
        raise ValueError("required current manifest missing/nonregular")
    document = json.loads(manifest.read_text(), object_pairs_hook=_pairs)
    if document.get("schema_version") != 5 or semantic_digest(document) != value["manifest_semantic_digest"]:
        raise ValueError("sealed current manifest schema/semantic identity drift")
    return value


def package_lineage(root):
    # A missing historical commit never selects or weakens current validation.
    if not (Path(root) / PUBLIC_BASELINE).exists():
        return False
    public_contract(root)
    return True


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
    'agent_framework',
    'agentic_sequence',
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
    contract = public_contract(root)
    if semantic_digest(entries) != contract["manifest_entries_semantic_digest"]:
        raise ValueError("missing or substituted required command/classification/dependency contract")



def current_package_comparison(root):
    contract = public_contract(root)
    return {"accepted_source_contract": contract["accepted_source_contract"],
            "candidate_source": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
            "outside_maintenance_paths": [], "missing_or_changed_ci_modes": [],
            "status": "EXACT_PROTECTED_CURRENT_PUBLIC_INPUTS", "new_hardware_acceptance": False}


def verify_current_package(root):
    return current_package_comparison(root)


def package_evidence(root, parent, strict=False):
    # Current proof is sealed source correspondence, never historical replay.
    comparison = current_package_comparison(root)
    comparison.update(historical_correspondence="SEPARATE_EXPLICIT_HISTORICAL_PROOF",
                      maintenance_only_required=strict)
    return comparison


def historical_package_evidence(root, parent):
    accepted = materialize(root, PACKAGE_BASE, parent)
    verifier = accepted / "docs/runtime_config/package_active_profile_display/integration_20261113/verify_correspondence.py"
    return subprocess.run([sys.executable, "-I", "-B", str(verifier)], cwd=accepted,
                          check=True, capture_output=True, text=True).stdout.strip()



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
