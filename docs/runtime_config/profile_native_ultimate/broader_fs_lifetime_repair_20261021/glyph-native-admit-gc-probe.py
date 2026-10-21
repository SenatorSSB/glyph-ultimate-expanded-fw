from pathlib import Path
import json,shlex,subprocess,hashlib
root=Path('/private/tmp/glyph-profile-native-20261020');out=Path('/private/tmp/glyph-native-admit-gc-probes-20261021');out.mkdir(exist_ok=True)
source=(root/'HAL/pico/src/core/ProfileStore.cpp').read_text();header=(root/'include/core/ProfileStore.hpp').read_text()
admit_start=source.index('bool ProfileStore::Admit(size_t bytes, size_t records) {');admit_end=source.index('\nProfileStore::TransactionResult ProfileStore::QueryTransaction',admit_start)
admit=source[admit_start:admit_end];prefix='''bool ProfileStore::Admit(size_t bytes, size_t records) {
    if (CollectGarbage() != Status::Ok)
        return false;
''';assert admit.startswith(prefix);calculation=admit[len(prefix):];assert calculation.startswith('    auto c = Capacity();')
replacement='''bool ProfileStore::Admit(size_t bytes, size_t records) {
    if (CollectGarbage() != Status::Ok)
        return false;
    return EvaluateAdmission(bytes, records);
}

__attribute__((noinline)) bool ProfileStore::EvaluateAdmission(size_t bytes, size_t records) {
'''+calculation
phase=source[:admit_start]+replacement+source[admit_end:]
phase_header=header.replace('    bool Admit(size_t staged_record_bytes, size_t records = 1);','    bool Admit(size_t staged_record_bytes, size_t records = 1);\n    bool EvaluateAdmission(size_t staged_record_bytes, size_t records);')
# Fixed output belongs to the same synchronous GC operation. Callback lifetime
# ends at Enumerate return; reset every iteration and all exits after creation.
needle='''    for (unsigned budget = 0; budget < 128; ++budget) {
        Search search{ this, {}, false };
''';assert phase.count(needle)==1
fixed=phase.replace(needle,'''    static Search search{};
    struct SearchReset {
        Search &state;
        ~SearchReset() { std::memset(&state, 0, sizeof(state)); }
    } reset{search};
    for (unsigned budget = 0; budget < 128; ++budget) {
        std::memset(&search, 0, sizeof(search));
        search.store = this;
''')
# Alternative fixed CapacityInfo only, preserves exact admission call order.
static_admit=source.replace('''    auto c = Capacity();
    if (!c.block_size)''','''    static CapacityInfo c;
    ::new (&c) CapacityInfo(Capacity());
    if (!c.block_size)''');assert static_admit!=source
entries=json.loads((root/'docs/runtime_config/profile_native_ultimate/native_production_stack_final/compile_commands.json').read_text());entry=next(e for e in entries if e['file'].endswith('/ProfileStore.cpp'));recipe=shlex.split(entry['command']);compiler=Path(recipe[0]);objdump=compiler.with_name('arm-none-eabi-objdump');nm=compiler.with_name('arm-none-eabi-nm')
results={}
for name,text,decl in [('baseline',source,header),('capacity_phase',phase,phase_header),('capacity_phase_fixed_search',fixed,phase_header),('static_capacity_only',static_admit,header)]:
 folder=out/name;folder.mkdir(exist_ok=True);(folder/'core').mkdir(exist_ok=True);(folder/'core/ProfileStore.hpp').write_text(decl);cpp=folder/'ProfileStore.cpp';cpp.write_text(text);obj=folder/'ProfileStore.o';args=recipe.copy();args[args.index('-o')+1]=str(obj);args[args.index(entry['file'])]=str(cpp);args[1:1]=['-I',str(folder)];args+=['-fstack-usage'];r=subprocess.run(args,cwd=root,capture_output=True,text=True);(folder/'compile.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 dis=subprocess.check_output([str(objdump),'-drC',str(obj)],text=True);(folder/'disassembly.txt').write_text(dis);symbols=subprocess.check_output([str(nm),'-S',str(obj)],text=True);(folder/'symbols.txt').write_text(symbols)
 mutable=0
 for row in symbols.splitlines():
  fields=row.split()
  if len(fields)>=4 and fields[2] in ('b','B','d','D'):mutable+=int(fields[1],16)
 frames={}
 for row in (folder/'ProfileStore.su').read_text().splitlines():
  loc,size,kind=row.rsplit('\t',2)
  if any(n in loc for n in ['ProfileStore::Admit(', 'ProfileStore::EvaluateAdmission(', 'ProfileStore::CollectGarbage()', 'ProfileStore::Create(const UltimateProfile&, const char*, uint32_t, const TransactionIdentity&)', 'ProfileStore::ImportLegacyStream(', 'ProfileStore::Begin(']):frames[loc]=int(size)
 results[name]={'compile_argv':args,'source_sha256':hashlib.sha256(cpp.read_bytes()).hexdigest(),'header_sha256':hashlib.sha256((folder/'core/ProfileStore.hpp').read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'mutable_bytes':mutable,'frames':frames,'no_cxa_guard':'__cxa_guard' not in symbols}
 print(name,'mutable',mutable,'frames',json.dumps(frames))
report={'state':'PRIVATE_PRODUCTION_O3_OBJECT_PROBES_NOT_ADOPTED_NOT_FIRMWARE_BUILD','checkpoint':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'production_source_sha256':hashlib.sha256((root/'HAL/pico/src/core/ProfileStore.cpp').read_bytes()).hexdigest(),'compiler_sha256':hashlib.sha256(compiler.read_bytes()).hexdigest(),'recipe_sha256':hashlib.sha256((root/'docs/runtime_config/profile_native_ultimate/native_production_stack_final/compile_commands.json').read_bytes()).hexdigest(),'results':results,'whole_bound':'PENDING exact branch/IRQ/ROM proof, actual adoption/review/build'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
