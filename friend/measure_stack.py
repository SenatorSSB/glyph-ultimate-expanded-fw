#!/usr/bin/env python3
"""Recompile only selected literal TUs with exact PIO flags plus -fstack-usage.
Outputs go to private verification, never replace firmware build objects.
"""
import json, pathlib, shlex, subprocess
root=pathlib.Path(__file__).resolve().parents[1]
out=root.parent/'config-refresh-v3-20261012'/'verification'
path=root/'compile_commands.json'
if not path.exists(): path=out/'compile_commands.json'
if not path.exists(): path=root.parent/'default2-fix-20261012'/'verification'/'compile_commands.json'
database=json.loads(path.read_text())
for suffix in ['config/glyph/common/src/config.cpp','HAL/pico/src/core/Persistence.cpp','src/modes/Ultimate.cpp']:
    entry=next(e for e in database if e['file']==suffix)
    command=shlex.split(entry['command'])
    destination=out/(suffix.replace('/','_')+'.o')
    command[command.index('-o')+1]=str(destination)
    command+=['-fstack-usage']
    result=subprocess.run(command,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/(destination.stem+'.command.json')).write_text(json.dumps(command,indent=2))
    (out/(destination.stem+'.compile.log')).write_text(result.stdout)
    if result.returncode: raise RuntimeError(result.stdout)
    print(destination.with_suffix('.su').read_text())
