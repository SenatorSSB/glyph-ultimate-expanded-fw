from pathlib import Path
import json,subprocess,hashlib,argparse
root=Path('/private/tmp/glyph-profile-native-20261020');p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('sources',nargs='+');args=p.parse_args();out=args.out;out.mkdir(exist_ok=True)
r=json.loads(Path('/private/tmp/glyph-native-admit-gc-probes-20261021/report.json').read_text());base=r['results']['capacity_phase_fixed_search']['compile_argv'];report={}
for source in args.sources:
 name=Path(source).stem;obj=out/(name+'.o');a=list(base);a[a.index('-o')+1]=str(obj)
 a=[str(root/source) if x.endswith('/capacity_phase_fixed_search/ProfileStore.cpp') else x for x in a];i=a.index('-I');a[i+1]=str(root/'include')
 p=subprocess.run(a,cwd=root,capture_output=True,text=True);(out/(name+'.log')).write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 tools=Path(a[0]).parent
 for suffix,argv in [('disassembly.txt',[tools/'arm-none-eabi-objdump','-drC',obj]),('symbols.txt',[tools/'arm-none-eabi-nm','-SC',obj])]:
  q=subprocess.run(list(map(str,argv)),capture_output=True,text=True);assert q.returncode==0;(out/(name+'.'+suffix)).write_text(q.stdout)
 report[source]={'argv':a,'source_sha256':hashlib.sha256((root/source).read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest()}
report['status']='CURRENT_SOURCE_PRODUCTION_O3_OBJECT_NOT_FINAL_FIRMWARE';report['head']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();report['compiler_sha256']=hashlib.sha256(Path(base[0]).read_bytes()).hexdigest()
(out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
