#!/usr/bin/env python3
"""Focused self-test for the fail-closed Glyph checker-context helper."""

from __future__ import annotations

import subprocess
import tempfile
import importlib.util
import contextlib
import io
import os
import shutil
import sys
from unittest.mock import patch
from pathlib import Path

from glyph_checker_context import ScopeValidationError, collect_checker_context, validate_feature_scope


def run(root: Path, *args: str) -> None:
    completed = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")


def output(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def expect_scope_failure(root: Path, base: str | None, needle: str) -> None:
    context = collect_checker_context(repo_root=root, base=base)
    try:
        validate_feature_scope(context, allowed_paths=("docs/",))
    except ScopeValidationError as exc:
        if needle not in str(exc):
            raise AssertionError(f"expected {needle!r}, got {exc!s}") from exc
    else:
        raise AssertionError(f"scope unexpectedly accepted case containing {needle!r}")


def fresh_repo(parent: Path) -> Path:
    root = parent / "repo"
    root.mkdir()
    run(root, "init", "-b", "configurator")
    run(root, "config", "user.name", "Glyph checker context test")
    run(root, "config", "user.email", "checker-context@example.invalid")
    write(root, "docs/baseline.md", "baseline\n")
    run(root, "add", "docs/baseline.md")
    run(root, "commit", "-m", "baseline")
    return root


GUARD = "tools/check_glyph_runtime_config_webserial_device_write_source_authority.py"
AUTHORITY_DOC = "docs/runtime_config/runtime_config_webserial_device_write_source_authority.md"


def guard_main(root: Path, campaign: bool, expected: str | None = None) -> None:
    """Exercise the real entry point, including argument handling and all guards."""
    env = dict(os.environ)
    env.pop("GLYPH_CHECKER_BASE", None)
    result = subprocess.run([sys.executable, str(root / GUARD)] +
                            (["--campaign-transition"] if campaign else []),
                            cwd=root, env=env, capture_output=True, text=True, check=False)
    combined = result.stdout + result.stderr
    if expected is None:
        if result.returncode or "status=PASS" not in result.stdout:
            raise AssertionError("actual guard main positive failed: " + combined)
    else:
        reasons = [expected]
        if campaign and expected in {"critical", "unclassified"}:
            reasons.append("dirty path outside reviewed governance inventory")
        if result.returncode == 0 or not any(reason in combined for reason in reasons):
            raise AssertionError("actual guard main negative lost " + repr(expected) + ": " + combined)


def campaign_guard_tests() -> None:
    from glyph_campaign_transition import ADOPTION, B, C
    source = Path(__file__).resolve().parents[1]
    # These clones borrow objects read-only. Their index, branches and mutations
    # are private; never update canonical refs or manufacture hardware evidence.
    with tempfile.TemporaryDirectory(prefix="glyph-campaign-guard-") as directory:
        root = Path(directory) / "baseline"
        run(source, "clone", "--shared", "--no-checkout", str(source), str(root))
        run(root, "checkout", "--detach", ADOPTION)
        run(root, "config", "user.name", "Glyph guard negative control")
        run(root, "config", "user.email", "guard-control@example.invalid")
        run(root, "branch", "-f", "configurator", ADOPTION)
        guard_main(root, False)
        for relative in (GUARD, "tools/glyph_campaign_transition.py", "tools/glyph_hardware_correspondence.py"):
            shutil.copyfile(source / relative, root / relative)
        # This disposable control is the pre-transition baseline, even when the
        # test itself runs from an accepted-phase repository. Never transplant
        # that repository's nonempty accepted catalog onto baseline source.
        write(root, "docs/runtime_config/fixtures/gp_val037_accepted_transitions.json",
              '{"schema_version":1,"accepted_transitions":[]}\n')
        guard_main(root, False)
        guard_main(root, True)
        spec = importlib.util.spec_from_file_location("campaign_guard_under_test", root / GUARD)
        if spec is None or spec.loader is None:
            raise AssertionError("guard import unavailable")
        guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard)
        doc = root / AUTHORITY_DOC
        original = doc.read_text()
        for phrase in guard.REQUIRED_PHRASES:
            doc.write_text(original.replace(phrase, "removed-required-phrase"))
            guard_main(root, True, "missing required phrase")
        for reference in guard.REQUIRED_REFERENCES:
            doc.write_text(original.replace(reference, "removed-required-reference"))
            guard_main(root, True, "missing required reference")
        doc.write_text(original + "\nDEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=true\n")
        guard_main(root, True, "flag must not be true")
        for claim in ("WebSerial/device write is implemented", "WebSerial implementation is implemented",
                      "device-write implementation is implemented", "Runtime-loaded config is implemented",
                      "Firmware flashing automation is implemented", "Hardware validation is claimed",
                      "Nunchuk validation is claimed"):
            doc.write_text(original + "\n" + claim + "\n")
            guard_main(root, True, "positive implementation claim")
        doc.write_text(original)
        # Authenticated campaign main rejects an additional protected input.
        marker_path = "src/gp_val037_guard_negative.cpp"
        write(root, marker_path, "// " + guard.FORBIDDEN_SOURCE_MARKERS[0] + "\n")
        guard_main(root, True, "critical")
        (root / marker_path).unlink()
        write(root, "tools/gp_val037_unknown_negative.txt", "unknown metadata\n")
        guard_main(root, True, "unclassified")
        (root / "tools/gp_val037_unknown_negative.txt").unlink()

        # Legacy source scans run against content on the private configurator
        # tip so scope rejection cannot mask a missing marker scan.
        for marker in guard.FORBIDDEN_SOURCE_MARKERS:
            write(root, marker_path, "// " + marker + "\n")
            run(root, "add", marker_path)
            run(root, "commit", "-m", "isolated source marker negative")
            run(root, "branch", "-f", "configurator", "HEAD")
            guard_main(root, False, "blocked runtime/device-write marker")
        (root / marker_path).unlink()
        run(root, "add", marker_path)
        run(root, "commit", "-m", "remove isolated source marker")
        run(root, "branch", "-f", "configurator", "HEAD")
        for marker in guard.FLASHING_MARKERS:
            write(root, "tools/gp_val037_flashing_negative.txt", marker + "\n")
            guard_main(root, False, "potential flashing automation marker")
        (root / "tools/gp_val037_flashing_negative.txt").unlink()

        # Instrument only the already independently tested authentication seam
        # to prove main passes its unfiltered inventory to the real flashing scan.
        # This is a wiring negative, never an authenticated campaign positive.
        import glyph_campaign_transition
        removed = "HAL/pico/src/comms/ConfiguratorBackend.cpp"
        target = root / removed
        original_source = target.read_bytes()
        for marker in guard.FLASHING_MARKERS:
            target.write_text(marker + "\n")
            proof = {"critical_paths": frozenset({removed}), "changed_paths": frozenset({removed})}
            captured = io.StringIO()
            with patch.object(glyph_campaign_transition, "authenticate", return_value=proof), \
                 patch.object(sys, "argv", [str(root / GUARD), "--campaign-transition"]), \
                 contextlib.redirect_stdout(captured):
                result = guard.main()
            if result != 1 or "potential flashing automation marker" not in captured.getvalue():
                raise AssertionError("campaign main filtered flashing input: " + marker)
        target.write_bytes(original_source)

        candidate = Path(directory) / "candidate"
        run(source, "clone", "--shared", "--no-checkout", str(source), str(candidate))
        run(candidate, "checkout", "--detach", C)
        run(candidate, "branch", "-f", "configurator", B)
        shutil.copyfile(source / GUARD, candidate / GUARD)
        guard_main(candidate, False, "firmware/source/device paths changed")
    print("campaign_guard_actual_main: PASS; legacy/campaign baseline, C020 legacy rejection, "
          "all phrases/references/claims/source/flashing markers and unfiltered campaign wiring")



PROTECTED_SCOPE_MAINS = (
    "check_glyph_generated_source_owned_generator_contract.py",
    "check_glyph_generated_source_owned_artifact_install.py",
    "check_glyph_coordinate_native_runtime_profile_contract.py",
    "check_glyph_generated_source_owned_baseline_artifact.py",
    "check_glyph_docs_agent_surface.py",
)


def campaign_protected_scope_tests() -> None:
    """Exercise all five real mains on an ancestry-preserving private composition."""
    from concurrent.futures import ThreadPoolExecutor
    from glyph_campaign_transition import ADOPTION, C, GOVERNANCE_PATHS, authenticate
    source = Path(__file__).resolve().parents[1]
    source_proof = authenticate(source)
    if source_proof['contract'] == 'c020_abi_repair':
        from glyph_c020_abi_repair_transition import B_R, GOVERNANCE_PATHS
        base, candidate = B_R, source_proof['candidate']
    else:
        base, candidate = ADOPTION, C
    with tempfile.TemporaryDirectory(prefix="glyph-five-campaign-scopes-") as directory:
        root = Path(directory) / "composed"
        run(source, "clone", "--shared", "--no-checkout", str(source), str(root))
        run(root, "checkout", "-b", "scope-test-composition", output(source, "rev-parse", "HEAD"))
        run(root, "config", "user.name", "Glyph scope test")
        run(root, "config", "user.email", "scope-test@example.invalid")
        # Development runs may exercise pending governance edits. In the final
        # clean aggregate this set is empty, so only committed inputs are used.
        pending = set(output(source, "diff", "HEAD", "--name-only").splitlines())
        pending.update(output(source, "ls-files", "--others", "--exclude-standard").splitlines())
        if not pending <= GOVERNANCE_PATHS:
            raise AssertionError("scope test refuses non-governance development edits")
        for relative in pending:
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, root / relative)
        if pending:
            run(root, "add", "--", *sorted(pending))
            run(root, "commit", "-m", "private pending governance test snapshot")
        run(root, "branch", "-f", "configurator", base)
        processor_phase = source_proof['phase'] == 'SOURCE_FREE_PROCESSOR'
        if processor_phase:
            # E must exercise the real scope mains before any F/C_R integration.
            # Its evidence removal conveys no protected-source exemption.
            proof = authenticate(root)
            if proof['critical_paths'] or not proof['accepted_metadata_paths']:
                raise AssertionError('source-free processor context has source authority')
        else:
            run(root, "merge", "--no-ff", "--no-edit", candidate)
        for ancestor in ((base,) if processor_phase else (base, candidate)):
            run(root, "merge-base", "--is-ancestor", ancestor, "HEAD")
        env = dict(os.environ, GLYPH_CHECKER_BASE=base, PYTHONDONTWRITEBYTECODE="1")

        def actual_main(filename: str, rejection: str | None) -> None:
            result = subprocess.run([sys.executable, str(root / "tools" / filename)],
                                    cwd=root, env=env, capture_output=True, text=True,
                                    check=False, timeout=60)
            combined = result.stdout + result.stderr
            if rejection is None:
                if result.returncode or ": PASS" not in result.stdout:
                    raise AssertionError(filename + " composed positive failed: " + combined)
            else:
                # Accepted proofs can reject unknown/critical dirty paths at
                # the finite dirty-inventory gate before the final live scan.
                expected = [rejection]
                if rejection in {"critical", "unclassified"}:
                    expected.append("dirty path outside reviewed governance inventory")
                if result.returncode == 0 or not any(message in combined for message in expected):
                    raise AssertionError(filename + " negative lost " + rejection + ": " + combined)

        def all_mains(rejection: str | None = None) -> None:
            with ThreadPoolExecutor(max_workers=5) as pool:
                futures = [pool.submit(actual_main, filename, rejection)
                           for filename in PROTECTED_SCOPE_MAINS]
                for future in futures:
                    future.result()
            guard_main(root, True, rejection)

        all_mains()
        # Changes are confined to the private checkout. Each main must reject
        # through its real authentication path, without mocking the proof.
        protected = root / "src/gp_val037_scope_negative.cpp"
        protected.write_text("// unexpected protected source\n")
        all_mains("critical")
        protected.unlink()
        header = root / ("HAL/pico/src/comms/ConfiguratorBackend.cpp" if processor_phase
                         else "include/core/config_button_validation.hpp")
        mode = header.stat().st_mode
        header.chmod(mode | 0o111)
        all_mains("critical")
        header.chmod(mode)
        for relative in ("tools/gp_val037_unknown_negative.txt",
                         "docs/project/ACTIVE_AGENT_QUEUE.md.bak"):
            path = root / relative
            path.write_text("unexpected metadata alias\n")
            all_mains("unclassified")
            path.unlink()
        # Accepted phase must prove each exact result path before scope removal.
        from glyph_campaign_transition import authenticate
        metadata = authenticate(root)['accepted_metadata_paths']
        for relative in sorted(metadata):
            path = root / relative
            original, mode = path.read_bytes(), path.stat().st_mode
            try:
                path.write_bytes(original + b"\nsubstituted accepted metadata\n")
                all_mains("substitution")
            finally:
                path.write_bytes(original)
            try:
                path.chmod(mode | 0o111)
                all_mains("regular")
            finally:
                path.chmod(mode)
            alias = root / (relative + ".bak")
            try:
                alias.write_bytes(original)
                all_mains("unclassified")
            finally:
                alias.unlink()
        if output(root, "status", "--porcelain", "--untracked-files=all"):
            raise AssertionError("five-scope tests left dirty composition")
    print("campaign_five_scope_actual_mains: PASS; five scope mains plus WebSerial authenticated composed-phase positives; "
          "protected source, executable mode, unknown metadata and alias negatives per main")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "renamed-feature-branch")
        write(root, "docs/allowed.md", "allowed\n")
        run(root, "add", "docs/allowed.md")
        run(root, "commit", "-m", "docs only")
        context = collect_checker_context(repo_root=root, base="configurator")
        validate_feature_scope(context, allowed_paths=("docs/",))

        write(root, "src/committed.cpp", "x\n")
        run(root, "add", "src/committed.cpp")
        run(root, "commit", "-m", "protected committed")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/committed.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-include")
        write(root, "include/committed.hpp", "x\n")
        run(root, "add", "include/committed.hpp")
        run(root, "commit", "-m", "protected include")
        expect_scope_failure(root, "configurator", "protected prefix changed: include/committed.hpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-staged")
        write(root, "src/staged.cpp", "x\n")
        run(root, "add", "src/staged.cpp")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/staged.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-unstaged")
        write(root, "src/unstaged.cpp", "x\n")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/unstaged.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-mixed")
        write(root, "docs/allowed.md", "allowed\n")
        write(root, "src/protected.cpp", "x\n")
        run(root, "add", "docs/allowed.md", "src/protected.cpp")
        run(root, "commit", "-m", "mixed paths")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/protected.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-case-variant")
        write(root, "SRC/case_variant.cpp", "x\n")
        run(root, "add", "SRC/case_variant.cpp")
        run(root, "commit", "-m", "case variant protected")
        expect_scope_failure(root, "configurator", "protected prefix changed: SRC/case_variant.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-renamed-path")
        write(root, "docs/rename-me.md", "x\n")
        run(root, "add", "docs/rename-me.md")
        run(root, "commit", "-m", "docs file")
        (root / "src").mkdir()
        run(root, "mv", "docs/rename-me.md", "src/renamed.cpp")
        expect_scope_failure(root, "configurator", "protected prefix changed: src/renamed.cpp")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        original_base = output(root, "rev-parse", "HEAD")
        run(root, "switch", "-c", "feature-wrong-merge-base")
        write(root, "docs/feature.md", "feature\n")
        run(root, "add", "docs/feature.md")
        run(root, "commit", "-m", "feature")
        run(root, "switch", "configurator")
        write(root, "docs/base-advance.md", "base\n")
        run(root, "add", "docs/base-advance.md")
        run(root, "commit", "-m", "advance base")
        run(root, "switch", "feature-wrong-merge-base")
        run(root, "merge", "--no-edit", "configurator")
        context = collect_checker_context(
            repo_root=root, base="configurator", expected_merge_base=original_base
        )
        try:
            validate_feature_scope(context, allowed_paths=("docs/",))
        except ScopeValidationError as exc:
            if "unexpected feature merge base" not in str(exc):
                raise AssertionError(f"unexpected wrong-merge-base result: {exc!s}") from exc
        else:
            raise AssertionError("wrong expected merge base was accepted")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-base-not-ancestor")
        write(root, "docs/feature.md", "feature\n")
        run(root, "add", "docs/feature.md")
        run(root, "commit", "-m", "feature")
        run(root, "switch", "configurator")
        write(root, "docs/base.md", "base\n")
        run(root, "add", "docs/base.md")
        run(root, "commit", "-m", "advance base")
        run(root, "switch", "feature-base-not-ancestor")
        expect_scope_failure(root, "configurator", "is not an ancestor of HEAD")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-detached")
        run(root, "switch", "--detach")
        expect_scope_failure(root, None, "detached HEAD requires an explicit comparison base")
        context = collect_checker_context(repo_root=root, environ={"GLYPH_CHECKER_BASE": "configurator"})
        validate_feature_scope(context, allowed_paths=("docs/",))

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        write(root, "src/configurator_only.cpp", "x\n")
        context = collect_checker_context(repo_root=root, base="configurator")
        validate_feature_scope(context, allowed_paths=("docs/",))

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-outside-allowlist")
        write(root, "tools/not_allowed.py", "x\n")
        run(root, "add", "tools/not_allowed.py")
        run(root, "commit", "-m", "outside checker allowlist")
        expect_scope_failure(root, "configurator", "out-of-scope changed path: tools/not_allowed.py")

    for path in (
        "AGENTS.md",
        "docs/WORKFLOW.md",
        "docs/project/ACTIVE_AGENT_QUEUE.md",
    ):
        with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
            root = fresh_repo(Path(directory))
            run(root, "switch", "-c", "feature-unauthorized-control-plane")
            write(root, path, "unauthorized authority change\n")
            run(root, "add", path)
            run(root, "commit", "-m", "unauthorized control plane")
            context = collect_checker_context(repo_root=root, base="configurator")
            try:
                validate_feature_scope(context, allowed_paths=("docs/runtime_config/",))
            except ScopeValidationError as exc:
                if f"out-of-scope changed path: {path}" not in str(exc):
                    raise AssertionError(
                        f"unexpected unauthorized control-plane result: {exc!s}"
                    ) from exc
            else:
                raise AssertionError(f"unauthorized control-plane path was accepted: {path}")

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "curation-authorized-queue")
        write(root, "docs/project/ACTIVE_AGENT_QUEUE.md", "queue\n")
        run(root, "add", "docs/project/ACTIVE_AGENT_QUEUE.md")
        run(root, "commit", "-m", "authorized queue")
        context = collect_checker_context(repo_root=root, base="configurator")
        validate_feature_scope(
            context, allowed_paths=("docs/project/ACTIVE_AGENT_QUEUE.md",)
        )

    with tempfile.TemporaryDirectory(prefix="glyph-checker-context-") as directory:
        root = fresh_repo(Path(directory))
        run(root, "switch", "-c", "feature-control-plane-near-match")
        write(root, "docs/project/ACTIVE_AGENT_QUEUE.md.bak", "not canonical\n")
        run(root, "add", "docs/project/ACTIVE_AGENT_QUEUE.md.bak")
        run(root, "commit", "-m", "control plane near match")
        context = collect_checker_context(repo_root=root, base="configurator")
        try:
            validate_feature_scope(context, allowed_paths=("docs/runtime_config/",))
        except ScopeValidationError as exc:
            if "out-of-scope changed path" not in str(exc):
                raise AssertionError(f"unexpected control-plane near-match result: {exc!s}") from exc
        else:
            raise AssertionError("near-match control-plane path was accepted")

    historical = Path(__file__).with_name("check_glyph_source_owned_table_replacement_generator_contract.py")
    spec = importlib.util.spec_from_file_location("historical_branch_policy", historical)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load historical branch-policy checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_git_lines = module.git_lines
    try:
        module.git_lines = lambda args, preserve_status=False: ["unrelated-feature-branch"]
        try:
            module.validate_branch()
        except module.SourceOwnedTableReplacementGeneratorContractError as exc:
            if "checker must run on" not in str(exc):
                raise AssertionError(f"unexpected historical-branch result: {exc!s}") from exc
        else:
            raise AssertionError("historical exact-branch checker unexpectedly lost branch-specific policy")
    finally:
        module.git_lines = original_git_lines

    campaign_guard_tests()
    campaign_protected_scope_tests()

    case_ids = (
        "CTX-01-valid-feature-branch",
        "CTX-02-renamed-feature-branch",
        "CTX-03-committed-src-rejected",
        "CTX-04-staged-src-rejected",
        "CTX-05-unstaged-src-rejected",
        "CTX-06-committed-include-rejected",
        "CTX-07-mixed-safe-protected-rejected",
        "CTX-08-case-variant-protected-rejected",
        "CTX-09-wrong-merge-base-rejected",
        "CTX-10-base-not-ancestor-rejected",
        "CTX-11-detached-explicit-base-accepted",
        "CTX-12-detached-missing-base-rejected",
        "CTX-13-configurator-content-accepted",
        "CTX-14-checker-allowlist-rejected",
        "CTX-15-unauthorized-authority-paths-rejected",
        "CTX-16-exact-role-scoped-queue-path-accepted",
        "CTX-17-control-plane-near-match-rejected",
        "CTX-18-historical-exact-branch-remains-specific",
    )
    print("glyph_checker_context: PASS; cases=" + ",".join(case_ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
