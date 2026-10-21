import datetime, hashlib, json, os, pathlib, subprocess, sys, time
out=pathlib.Path(__file__).resolve().parent
report_path=out/'report.json'
report=json.loads(report_path.read_text())
clone=pathlib.Path(report['snapshot'])
env={**os.environ, **report['environment']}
for relative in report['inspection']['checkers']:
    name=pathlib.Path(relative).stem
    if any(c['name']==name for c in report['checks']):
        continue
    argv=[sys.executable,relative]
    if name=='check_glyph_profile_store_read_storage':
        argv += ['--output-dir',str(out/'read-storage')]
    started=datetime.datetime.now(datetime.timezone.utc).isoformat(); tick=time.monotonic()
    print('START '+name,flush=True)
    with (out/('logs/'+name+'.log')).open('w') as log:
        try:
            child=subprocess.run(argv,cwd=clone,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=480)
            code=child.returncode
        except subprocess.TimeoutExpired:
            code=None
            log.write('\nOUTER_TIMEOUT_SECONDS=480\n')
    item={'name':name,'argv':argv,'cwd':str(clone),'environment':report['environment'],'started_utc':started,'elapsed_seconds':round(time.monotonic()-tick,3),'exit_code':code,'result':'PASS' if code==0 else ('TIMEOUT' if code is None else 'FAIL'),'log':str(out/('logs/'+name+'.log')),'log_sha256':hashlib.sha256((out/('logs/'+name+'.log')).read_bytes()).hexdigest()}
    report['checks'].append(item)
    report['commands'].append({k:item[k] for k in ['argv','cwd','environment','log','exit_code']})
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print(item['result']+' '+name+' elapsed_seconds='+str(item['elapsed_seconds']),flush=True)
    if code != 0:
        print((out/('logs/'+name+'.log')).read_text()[-12000:],flush=True)
        break
report['result']='PASS' if len(report['checks'])==len(report['inspection']['checkers']) and all(c['result']=='PASS' for c in report['checks']) else 'STOPPED_ON_FAILURE'
report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
report_path.write_text(json.dumps(report,indent=2)+'\n')
