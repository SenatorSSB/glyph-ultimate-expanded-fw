import pathlib,json,shlex,subprocess
r=pathlib.Path('/private/tmp/glyph-profile-native-20261020');out=pathlib.Path('/private/tmp/glyph-native-workspace-probes/finite-next');out.mkdir(exist_ok=True)
db=json.loads((r/'docs/runtime_config/profile_native_ultimate/native_production_stack_final/compile_commands.json').read_text())
def compile(name,relative,s,h):
 p=out/(name+'.cpp');p.write_text(s);inc=out/name/'core';inc.mkdir(parents=True,exist_ok=True);(inc/'ProfileStore.hpp').write_text(h)
 e=next(e for e in db if e['file'].endswith(relative));args=shlex.split(e['command']);args[args.index('-o')+1]=str(p.with_suffix('.o'));args[args.index(e['file'])]=str(p);args[1:1]=['-I',str(inc.parent)];args+=['-fstack-usage'];c=subprocess.run(args,cwd=r,capture_output=True,text=True);print(c.returncode,c.stderr)
 if not c.returncode:
  for x in p.with_suffix('.su').read_text().splitlines():
   if any(n in x for n in ['Create(const UltimateProfile&, const char*, uint32_t, const TransactionIdentity&)', 'Duplicate(uint32_t, uint32_t, const char*, uint32_t, const TransactionIdentity&)']):print(x)
s=(r/'HAL/pico/src/core/ProfileStore.cpp').read_text();h=(r/'include/core/ProfileStore.hpp').read_text();a=s.index('ProfileStore::TransactionResult ProfileStore::Create(\n    const UltimateProfile &p,');s=s[:a]+s[a:].replace('ProfileStore::TransactionResult ProfileStore::Create(', '__attribute__((always_inline)) inline ProfileStore::TransactionResult ProfileStore::ExecuteCreate(',1);a=s.index('\nProfileStore::TransactionResult ProfileStore::Update(',a);s=s[:a]+'''
ProfileStore::TransactionResult ProfileStore::Create(
    const UltimateProfile &p, const char *name, uint32_t rank, const TransactionIdentity &t
) { return ExecuteCreate(p, name, rank, t); }
'''+s[a:];s=s.replace('    return Create(_candidate_profile, name, rank, t);','    return ExecuteCreate(_candidate_profile, name, rank, t);');h=h.replace('    void PrepareCreate();','    TransactionResult ExecuteCreate(const UltimateProfile &, const char *, uint32_t, const TransactionIdentity &);\n    void PrepareCreate();');compile('single-create-body','HAL/pico/src/core/ProfileStore.cpp',s,h)
# Store inputs before Duplicate preparation, then consume the same inline body;
# no dangling input pointer remains after the synchronous operation.
s2=s.replace('    duplicate_prepared = false;\n    static TransactionResult r;', '    prepared_create.input_name = name; prepared_create.rank = rank; prepared_create.identity = t;\n    duplicate_prepared = false;\n    static TransactionResult r;').replace('    return ExecuteCreate(_candidate_profile, name, rank, t);', '    return ExecuteCreate(_candidate_profile, prepared_create.input_name, prepared_create.rank, prepared_create.identity);')
compile('single-create-snapshotted','HAL/pico/src/core/ProfileStore.cpp',s2,h)
