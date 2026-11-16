"""Observe existing Mk6 boot stage marks in the checked LittleFS host fixture."""
import argparse
import functools
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def replace_once(path, old, new):
    source = path.read_text()
    if source.count(old) != 1:
        raise ValueError(f"unexpected host fixture at {path.name}")
    path.write_text(source.replace(old, new))


def main():
    args = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "corpus", "out"):
        args.add_argument("--" + name, type=Path, required=True)
    opts = args.parse_args()
    repo, corpus, out = (path.resolve() for path in (opts.repo, opts.corpus, opts.out))
    out.mkdir(parents=True, exist_ok=False)
    fixture = out / "fixture"
    shutil.copytree(repo / "tools/fixtures/glyph_package_v1/transaction", fixture,
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(Path(__file__).with_name("observe_boot.inc"), fixture)
    probe = fixture / "boot_probe.hpp"
    replace_once(probe, '#include "extracted_boot.inc"',
                 '#include "observe_boot.inc"\n#include "extracted_boot.inc"')
    replace_once(probe, "    setup();", "    start_observing();\n    setup();\n    finish_observing();")
    extract = fixture / "boot_probe.py"
    replace_once(extract, "function(text,n,t) for n,t in names",
                 "function(text,n,t).replace('time_boot_stage(stage);', "
                 "'observe_stage(stage); time_boot_stage(stage);') for n,t in names")
    sys.path[:0] = [str(fixture), str(corpus / "proof"), str(corpus / "wire"),
                    str(corpus.parents[1] / "tools/research")]
    from build import build
    from run import dump_namespace
    import glyph_package_fixtures as fixtures
    import glyph_package_storage as model

    binary = build(repo, out / "build", sanitize=False, boot_probe=True)
    model.config_wire = functools.lru_cache(maxsize=1)(model.config_wire)
    base = fixtures.baseline(4, ultimate=True, backend=True)
    disk = fixtures.package_plan(base, True, 100)[0]["COMMITTED"]
    for token in range(101, 127):
        disk = fixtures.later_raw_create(disk, token)
    namespace, nor, defaults = (out / name for name in ("library.namespace", "library.nor", "defaults.pb"))
    dump_namespace(disk, namespace)
    fixture_digest = hashlib.sha256(namespace.read_bytes()).hexdigest()
    assert fixture_digest == "251a9a7cc1c1c3242be170605e651074e198e12d9c02a9ca5da3336d53a99580"
    defaults.write_bytes(base["/config-v2.bin"][8:])
    subprocess.run([binary, "seed", namespace, nor], check=True)
    fields = "stage elapsed_us nor_reads enumerations opens seeks reads".split()
    runs = []
    for trial, fault_stage in enumerate([0] * 10 + [6, 8]):
        case = out / f"trial-{trial:02}"
        case.mkdir()
        env = dict(os.environ, BETA_PROBE_FAULT_STAGE=str(fault_stage))
        subprocess.run([binary, "boot", nor, defaults, case], check=True, env=env)
        hits, *lines = (case / "stages.txt").read_text().splitlines()
        stages = [dict(zip(fields, map(int, line.split()), strict=True)) for line in lines]
        result = json.loads((case / "boot.json").read_text())
        assert result["unchanged"]
        if fault_stage:
            assert int(hits) > 0 and result["outcome"] == 6 and result["recovery_visible"]
            assert result["backend_initializations"] == 0
            assert (7 in [s["stage"] for s in stages]) == (fault_stage == 8)
        else:
            assert int(hits) == 0 and result["outcome"] == 1 and result["backend_initializations"] == 1
            assert [s["stage"] for s in stages] == list(range(1, 17)) + [0]
        runs.append(dict(fault_stage=fault_stage, read_fault_hits=int(hits), result=result, stages=stages))
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    report = dict(source=sha, fixture_sha256=fixture_digest, runs=runs)
    (out / "observations.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
