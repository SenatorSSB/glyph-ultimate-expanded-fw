#!/usr/bin/env python3
"""Exercise the real GP-VAL-035 source-free proof and finite rejectors."""
from __future__ import annotations

import json
from pathlib import Path

import glyph_c017_campaign_transition as proof
from glyph_hardware_correspondence import CorrespondenceError

ROOT = Path(__file__).resolve().parents[1]


def rejected(fn, label: str) -> None:
    try:
        fn()
    except (CorrespondenceError, ValueError, TypeError, KeyError):
        return
    raise AssertionError('accepted invalid 017 contract: ' + label)


def main() -> int:
    before, after = proof.source_contract(ROOT)
    assert len(before) == len(after) == 236
    assert {path for path in before.keys() | after.keys()
            if before.get(path) != after.get(path)} == proof.CRITICAL
    predecessor, integrated = proof.predecessor_contract(ROOT)
    assert predecessor['build'] == 'e5c455637056ac535347c1176dd41c9a9d84d85a'
    assert integrated['integration'] == 'd786c244183343f89287a040055b7eaeae1e41f3'
    current = proof.authenticate(ROOT)
    assert current['contract'] == 'c017_neopixel'
    assert current['phase'] in {'BASELINE', 'CANDIDATE_VALIDATION_ONLY',
                                'SOURCE_FREE_PROCESSOR', 'ACCEPTED_TRANSITION'}
    assert current['predecessor_phase'] == 'ACCEPTED_TRANSITION'
    assert {proof.C, proof.B, proof.ORIGINAL_016_BASE} <= current['object_roots']
    assert current['critical_paths'] >= proof.previous.CRITICAL
    if current['phase'] in {'BASELINE', 'SOURCE_FREE_PROCESSOR'}:
        assert proof.SOURCE not in current['source_candidates']
        assert proof.critical_tree(ROOT, current['target']) == before
    else:
        assert current['source_candidates'][proof.SOURCE] == proof.C
        assert proof.critical_tree(ROOT, current['target']) == after
    rejected(lambda: proof._catalog(b'{}'), 'catalog omission')
    rejected(lambda: proof._catalog(b'{"schema_version":1,"accepted_transitions":[{},{}]}'),
             'extra accepted transitions')
    rejected(lambda: proof._catalog(json.dumps({
        'schema_version': 1, 'accepted_transitions': [{'work_order': 'GP-CONFIG-021'}]
    }).encode()), 'foreign acceptance')
    print('glyph_c017_campaign_transition: PASS; phase=' + current['phase'] +
          '; 236 critical entries; exact 014 predecessor; source-free proof is not hardware PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
