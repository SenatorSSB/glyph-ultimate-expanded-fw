import json, tarfile, sys
from pathlib import Path
archive, path = map(Path, sys.argv[1:])
with tarfile.open(archive) as t:
    old = json.load(t.extractfile('current/current/functions.json'))
    rows = json.load(t.extractfile('baseline-composed/inherited140-source-ledger.json'))['rows']
row, = [v for v in rows if v['id']=='native.frame']
g = json.loads((path/'graph/functions.json').read_text())
parts = {}
for c,p in zip(row['components'],['main','loop','NintendoSwitchBackend::SendReport()','CommunicationBackend::UpdateOutputs()', 'ControllerMode::UpdateOutputs(','Ultimate::UpdatePreprocessedOutputs(','ultimate_native::Evaluate(','ultimate_native::(anonymous namespace)::Conditions(', 'ultimate_native::(anonymous namespace)::Value('],strict=True):
    n, = [k for k in g if (k==p if p in ('main','loop') else k.startswith(p))]
    f = g[n]['resolved_frame_bytes']
    if c['name'] != 'backendSendMax':
        assert c['current'] == f == old[n]['resolved_frame_bytes'], (n,c['current'],f)
    parts[n]=f
assert sum(parts.values())+row['IRQ']==984
d={'scope':'Retained native.frame selected-input/source/mode predicate only; conservative inherited dispatch reserve and IRQ included. No hardware measurement.', 'predicate':row['frozen_predicate'], 'archive_baseline':row['current_conditional_total'], 'previous_backend_reserve':24, 'new_switch_frame':32,'IRQ':row['IRQ'],'components':parts, 'conditional_total':984, 'margin':2048-984}
(path/'switch-native.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d))
