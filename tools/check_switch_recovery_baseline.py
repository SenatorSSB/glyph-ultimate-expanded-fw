#!/usr/bin/env python3
"""Read retained Stage-H evidence and exercise a production host validator; no devices."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import glyph_switch_recovery as op


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('baseline', 'uf2', 'host-build', 'out'):
        ap.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args()
    pb, jf, _ = op.config_tool.load_runtime_proto_modules(op.ROOT)
    baseline = args.baseline
    op.require(op.sha((baseline/'snapshot.json').read_bytes()) == op.PINS['baselineSnapshotSha256'], 'Stage-H snapshot differs')
    saved = op.read_json(baseline/'snapshot.json')
    op.verify_entries(saved['entries'])
    target = (baseline/'config.pb').read_bytes()
    cfg = pb.Config.FromString(target)
    op.require(len(saved['entries']) == 27 and len(cfg.game_mode_configs) == 4 and not cfg.rgb_configs, 'baseline extent differs')
    op.require(saved['source'] == '84556d904f067bda5a101e6297689239ecd04aae', 'wrong retained source')
    op.require(saved['store']['generation'] == 234 and saved['store']['incarnation'] == 1 and
               saved['store']['token'] == '17293822569102712139', 'Stage-H counters differ')
    for entry in saved['entries']:
        raw = (baseline/entry['wrapperFile']).read_bytes()
        op.require(op.sha(raw) == entry['wrapperSha256'] and len(raw) == entry['wrapperBytes'] and
                   pb.UltimateProfile.FromString(raw).schema_version == entry['wrapperSchema'], 'wrapper differs')
    cfg.default_usb_backend_config = 4
    current = cfg.SerializeToString(deterministic=True)
    op.require(op.exact_payload(current, target, pb) == target, 'selector-only pair failed')
    a, b = jf.MessageToDict(pb.Config.FromString(target)), jf.MessageToDict(cfg)
    op.require({k for k in a.keys() | b.keys() if a.get(k) != b.get(k)} == {'defaultUsbBackendConfig'}, 'unrelated Config change')
    op.verify_ledger(Path(op.PINS['ledger']))
    op.verify_artifact(args.uf2)
    manifest = op.read_json(args.host_build/'source-manifest.json')
    binary = args.host_build/'package-fault-harness'
    op.require(op.sha(binary.read_bytes()) == manifest['binary_sha256'], 'host binary changed')
    for name, digest in manifest['files'].items():
        path = Path(name) if Path(name).is_absolute() else op.ROOT/name
        op.require(op.sha(path.read_bytes()) == digest, 'host source/dependency changed: '+name)
    result = subprocess.run([str(binary), 'observe-configs-facts'],
        input=current.hex().encode()+b'\n'+target.hex().encode()+b'\n', capture_output=True,
        env={**os.environ, 'ASAN_OPTIONS':'detect_leaks=0', 'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
    op.require(result.returncode == 0 and [r.strip() for r in result.stdout.splitlines()] == [b'0 1 0', b'0 1 0'],
               'production parser/semantic validation failed')
    args.out.mkdir()
    (args.out/'production-validator.stdout').write_bytes(result.stdout)
    (args.out/'production-validator.stderr').write_bytes(result.stderr)
    # These payloads remain private; only the non-payload report is published.
    (args.out/'predicted-switch.pb').write_bytes(current)
    (args.out/'target-xinput.pb').write_bytes(target)
    report = dict(result='PASS', source=op.SOURCE, uf2=op.UF2, baselineSnapshotSha256=op.PINS['baselineSnapshotSha256'],
        configBytes=len(target), currentSha256=op.CURRENT, targetSha256=op.TARGET,
        configDifference=dict(field='default_usb_backend_config', xinput=1, switch=4, byteOffset0=263),
        profiles=27, ConfigRows=4, RGBObjects=0, managedSequence=6, storeGeneration=234,
        storeIncarnation=1, transactionHighWater='17293822569102712138',
        originalDirectoryAndWrappersExact=True, originalConfigRowsReferencesSelectorsRGBAndReceiptsExact=True,
        originalLedgerFilesVerified=len(op.PINS['ledgerFiles']), productionExactPairParserAndSemanticValidator='both 0 1 0',
        hostBinarySha256=manifest['binary_sha256'], hostInputs=len(manifest['files']),
        deviceAccess=False, physicalState='Retained Stage-H evidence only; current live state not observed in this invocation')
    (args.out/'result.json').write_bytes(op.json_bytes(report))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
