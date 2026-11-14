"""Operation-count regression for a 27-profile library on real, host-mounted LittleFS."""
import argparse
import functools
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile

from run import dump_namespace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--corpus", required=True, type=Path)
    args = parser.parse_args()
    corpus = args.corpus.resolve()
    sys.path[:0] = [str(corpus / "proof"), str(corpus / "wire"), str(corpus.parents[1] / "tools/research")]
    import glyph_package_fixtures as fixtures
    import glyph_package_storage as model

    model.config_wire = functools.lru_cache(maxsize=1)(model.config_wire)
    disk = fixtures.package_plan(fixtures.baseline(4, ultimate=True, backend=True), True, 100)[0]["COMMITTED"]
    for i in range(26):
        disk = fixtures.later_raw_create(disk, 101 + i)
    assert len(disk) == 32
    env = {**os.environ, "ASAN_OPTIONS": "detect_leaks=0", "UBSAN_OPTIONS": "halt_on_error=1"}
    with tempfile.TemporaryDirectory() as temporary:
        dest = Path(temporary)
        namespace, nor = dest / "library.namespace", dest / "library.nor"
        dump_namespace(disk, namespace)
        subprocess.run([args.binary, "seed", namespace, nor], check=True, env=env)
        samples = [json.loads(subprocess.check_output(
            [args.binary, "startup-work", nor, "-", dest], env=env
        )) for _ in range(5)]
        counts = {k: v for k, v in samples[0].items() if k != "host_us"}
        assert all(all(sample[k] == v for k, v in counts.items()) for sample in samples)
        # Bounds are specific to these 32 files, pinned LittleFS and geometry.
        # Wall time is reported only. It is neither a target claim nor a gate.
        limits = dict(enumerations=30, opens=120, seeks=250, reads=1900, nor_reads=15000)
        for key, limit in limits.items():
            if counts[key] > limit:
                raise AssertionError(f"{key} {counts[key]} exceeds fixture budget {limit}")
        print(json.dumps({
            **counts, "host_median_us": statistics.median(s["host_us"] for s in samples),
            "fixture_sha256": hashlib.sha256(namespace.read_bytes()).hexdigest()
        }))


if __name__ == "__main__":
    main()
