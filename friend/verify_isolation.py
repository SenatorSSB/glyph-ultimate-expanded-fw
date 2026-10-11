#!/usr/bin/env python3
"""Read-only canonical isolation audit against this task's recorded baseline."""
import hashlib, json, pathlib, subprocess
root=pathlib.Path(__file__).resolve().parents[1]; main=root.parents[3]
base='28ba39da5f517baa40f3dee8d868c9bb583dde4a'
expected={
 'tools/glyph_serial_config_tool.py':'4de5753855eb42b9d462e2ab2c1a59b2c47d5a8cb43a31ab588e471d2cbc7368',
 'docs/agent_framework/FUTURE_DAEMON_BOOTSTRAP.md':'0ada724783607dd2cb9d7231049883816171f311f87a7ec08b3881e6e3f84f0e',
 'docs/project/DAEMON_RETROSPECTIVE_2026-10-10.md':'f24c87fb4da6120e68a1a173a9296048e91b92613ca4a71be9034e7e18622f4e',
 'docs/project/ACTIVE_AGENT_QUEUE.md':'1ca9d7272b2d4ef6dcf732fd560204a9c94b8f9ad1e91ae8f46311c68223c6e2',
 'docs/ROADMAP.md':'18138f1dde2711b08192f3b4075f1fe95dfdb13cc04b4940fda0edf94d5be817',
 'docs/CURRENT_STATE.md':'d1321856d2fb6f96959f662ec4deab11ff784ab60ea6c0269c1100be290f71ab'}
actual={p:hashlib.sha256((main/p).read_bytes()).hexdigest() for p in expected}
assert actual==expected,'canonical dirty/authority file changed'
def git(*args): return subprocess.check_output(['git',*args],cwd=main).decode().rstrip('\n')
status=git('status','--short')
assert status==' M tools/glyph_serial_config_tool.py\n?? docs/agent_framework/FUTURE_DAEMON_BOOTSTRAP.md\n?? docs/project/DAEMON_RETROSPECTIVE_2026-10-10.md',status
assert git('rev-parse','HEAD')=='98c2ca04e61e095fc1bb3cedadb6211bbe453a8a'
assert git('branch','--show-current')=='codex/c024-exact-duplicate-writer'
assert git('rev-parse','configurator')==base
live=git('ls-remote','origin','refs/heads/configurator').split()[0]
assert live==base,'live configurator changed externally; refresh package baseline'
report={'result':'PASS','canonical':str(main),'main_head':git('rev-parse','HEAD'),
 'main_branch':git('branch','--show-current'),'main_status_unchanged':status,
 'canonical_configurator_local_and_live':live,'dirty_and_authority_hashes_unchanged':actual,
 'queue_roadmap_current_state_unchanged':True,'no_main_product_order_created':True,
 'runtime_loaded_coordinate_architecture_started':False,'hardware_flashing_performed':False}
(root.parent/'storage-recovery-v2/verification/ISOLATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
