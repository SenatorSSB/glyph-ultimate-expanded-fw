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
        load = json.loads(subprocess.check_output(
            [args.binary, "config-load-work", nor, "-", dest], env=env
        ))
        assert load["checked_reads"] <= 150, load
        faults = json.loads(subprocess.check_output(
            [args.binary, "config-load-faults", nor, "-", dest], env=env
        ))
        assert faults["failed"] == faults["seams"] == load["checked_reads"]
        assert faults["short_failed"] > 0
        # A corrupt body, a mismatched header and truncation remain rejections.
        # Remove any prior so recovery cannot mask the damaged current file.
        for damage in ("crc", "size", "truncated"):
            damaged = dict(disk)
            damaged.pop("/config-v2.prev", None)
            current = bytearray(damaged["/config-v2.bin"])
            if damage == "crc":
                current[-1] ^= 1
            elif damage == "size":
                current[0] ^= 1
            else:
                del current[-4:]
            damaged["/config-v2.bin"] = bytes(current)
            damaged_namespace, damaged_nor = dest / "damaged.namespace", dest / "damaged.nor"
            dump_namespace(damaged, damaged_namespace)
            subprocess.run([args.binary, "seed", damaged_namespace, damaged_nor], check=True, env=env)
            outcome = subprocess.check_output(
                [args.binary, "config-load-outcome", damaged_nor, "-", dest], env=env, text=True
            ).strip()
            assert outcome == "2", (damage, outcome)  # LoadResult::Rejected
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
            **counts, "config_load": load, "config_faults": faults, "host_median_us": statistics.median(s["host_us"] for s in samples),
            "fixture_sha256": hashlib.sha256(namespace.read_bytes()).hexdigest()
        }))


if __name__ == "__main__":
    main()
