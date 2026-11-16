"""Fail-closed named-change gate for GOPT's exact finite source families."""
def shape(x):
 return [x['resolved_frame_bytes'],sorted(set(c['name'] for c in x['calls'])),sorted(set(c['name'] for c in x['tail'])), sorted(set(c['instruction'] for c in x['indirect']))]
def edges(x):return {c['name'] for c in x['calls']+x['tail']}
def audit(b,f):
 crc=lambda n:n.startswith(('Persistence::CheckSavedConfig(', 'Persistence::ValidateLegacySource(', 'Persistence::CheckCaptureInput(', 'Persistence::LoadConfigRaw('))
 render=lambda n:n.startswith('MenuButtonHints::UpdateDisplay(')
 helper=lambda n:n.startswith('draw_profile_label(')
 allowed=lambda n:n=='loop' or crc(n) or render(n) or helper(n) or n.startswith('CRC32::update(')
 changed={n:{'old':shape(b[n]),'new':shape(f[n])} for n in sorted(b.keys()&f.keys()) if shape(b[n])!=shape(f[n])}
 added=sorted(f.keys()-b.keys());removed=sorted(b.keys()-f.keys())
 assert not removed and all(allowed(n) for n in changed) and all(helper(n) or n.startswith('CRC32::update(') for n in added), ('Unexpected graph delta',list(changed),added,removed)
 check={n for n in f if n.startswith('Persistence::CheckSavedConfig(CheckedStorageFile&')}
 assert len(check)==1
 for n in changed:
  old,new=b[n],f[n]
  if crc(n):
   assert edges(new)<=edges(old)|check|{k for k in f if k.startswith('CRC32::update(')}, ('Unknown CRC edge',n,edges(new)-edges(old))
   assert len(new['indirect'])<=len(old['indirect']),('New CRC indirect call',n)
  elif n=='loop':
   assert shape(new)[1:]==shape(old)[1:], 'Changed loop call target family'
  elif render(n):
   assert edges(new)<=edges(old)|{k for k in f if helper(k)}, ('Unknown renderer edge',n,edges(new)-edges(old))
 for n in added:
  if helper(n):assert edges(f[n])<={'Adafruit_GFX::write(unsigned char)'},('Unknown label helper edge',n)
  else:
   assert edges(f[n])<={'CRC32::update(unsigned char const&)'} and not f[n]['indirect'] and f[n]['resolved_frame_bytes']<=64,('Unknown CRC helper shape',n)
 return {'changed':changed,'added':added,'removed':removed}
