#!/usr/bin/env python3
"""Owner-directed visual evidence correction; no transport or device operations."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ADAPTER=HERE.parent/'hardware_continuation_v2'
spec=importlib.util.spec_from_file_location('reviewed_admission_adapter',ADAPTER/'executor.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
need,load,save,digest=e.need,e.load,e.save,e.digest


def verify():
    manifest=load(HERE/'MANIFEST.json')
    for name,expected in manifest['files'].items():
        p=HERE/name
        need(p.is_file() and not p.is_symlink() and digest(p.read_bytes())==expected,'visual evidence preparation changed')
    need(digest((ADAPTER/'MANIFEST.json').read_bytes())==manifest['adapter_manifest_sha256'],'admission adapter seal changed')
    need(digest((ADAPTER/'executor.py').read_bytes())==manifest['adapter_executor_sha256'],'admission adapter changed')
    return e.verify()


def authorize(receipt):
    need(receipt.get('owner_scope_correction') is True and bool(receipt.get('owner_message_reference')),
         'actual owner visual-scope correction required')
    need(receipt.get('scope_manifest_sha256')==digest((HERE/'MANIFEST.json').read_bytes()),'scope receipt seal mismatch')
    need(receipt.get('continuation_id')==e.ID and receipt.get('viewer_name_result')=='NOT_VISIBLE_NOT_VERIFIED',
         'visual scope differs')


def apply(packet,pb,package,episode,stage,event,receipt):
    """Only display/finish evidence; unchanged adapter owns all controller requests."""
    root=Path(episode)
    try:
        need(stage in ('display','finish') and not (root/'terminal.json').exists(),'visual stage or terminal')
        runner=e.Runner(packet,root,pb,package,None)
        runner.prior('install')
        runner.prior('first_xinput_boot' if stage=='display' else 'final_xinput_boot')
        target=root/stage
        target.mkdir(mode=0o700,exist_ok=False)
        save(target,'claim.json',{'stage':stage,'executor_sha256':digest(Path(__file__).read_bytes()),
             'scope':'OWNER_CORRECTED_VISUAL_EVIDENCE_ONLY','controller_exchanges':0})
        save(target,'owner-scope-correction.json',receipt)
        save(target,'owner-event.json',event)
        need(event.get('owner_present') is True and bool(event.get('owner_message_reference')),'actual owner observation required')
        need((event.get('dashboard_name'),event.get('plate'),event.get('backend'))==('KazTest5','Unknown Plate','XInput')
             and event.get('responsive') is True,'dashboard observation mismatch/uncertainty')
        if stage=='display':
            need(event.get('viewer_opened') is True and event.get('returned_dashboard') is True and
                 event.get('viewer_name_result')=='NOT_VISIBLE_NOT_VERIFIED','actual viewer navigation/visibility report required')
            result={'result':'PASS','controller_exchanges':0,'scope':'DASHBOARD_AND_VIEWER_NAVIGATION',
                    'viewer_name_result':'NOT_VISIBLE_NOT_VERIFIED','visible_viewer_name_PASS':False,
                    'basis':'Actual owner dashboard/navigation report and explicit visual-scope correction.'}
        else:
            count=sum(load(root/s/'result.json').get('controller_exchanges',0) for s in e.STAGES[:-1])
            need(count==36 and load(root/'pre_snapshot/result.json')['controller_exchanges']==34,'combined operation count differs')
            need(load(root/'display/result.json')['viewer_name_result']=='NOT_VISIBLE_NOT_VERIFIED','viewer limitation lost')
            result={'result':'PASS','controller_exchanges':0,'new_controller_exchanges':36,'inherited_controller_exchanges':34,
                    'packet_result':'PASS_DASHBOARD_IDENTITY_AND_API_PRESERVATION_WITH_VIEWER_NAME_UNVERIFIED',
                    'viewer_name_result':'NOT_VISIBLE_NOT_VERIFIED','visible_viewer_name_PASS':False,
                    'installation_basis':'OWNER_REPORTED_SINGLE_EXACT_INSTALL; NO_MACHINE_BUILD_ATTESTATION'}
        save(target,'result.json',result)
        return result
    except BaseException as error:
        if root.is_dir() and not (root/'terminal.json').exists():
            save(root,'terminal.json',{'result':'INCONCLUSIVE_TERMINAL_STOP','stage':stage,'reason':repr(error),
                 'controller_exchanges':0,'no_retry':True})
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('check','display','finish'))
    parser.add_argument('--authority',type=Path)
    parser.add_argument('--scope-directive',type=Path)
    parser.add_argument('--owner-event',type=Path)
    args=parser.parse_args()
    try:
        if e.established():need(not (e.EPISODE/'terminal.json').exists(),'continuation terminal; no retry')
        packet,pb,package=verify()
        if args.stage=='check':
            print('PASS_OFFLINE_VISUAL_SCOPE_PREPARATION; no device access')
            return
        need(args.authority and args.scope_directive and args.owner_event,'bound authority/correction/actual observation required')
        authority=load(args.authority);e.authorize(authority)
        need(load(e.EPISODE/'authority.json')==authority,'continuation authority changed')
        receipt=load(args.scope_directive);authorize(receipt)
        print(json.dumps(apply(packet,pb,package,e.EPISODE,args.stage,load(args.owner_event),receipt),indent=2))
    except BaseException as error:
        owned=e.established()
        if owned and not (owned/'terminal.json').exists():
            save(owned,'terminal.json',{'result':'INCONCLUSIVE_TERMINAL_STOP','stage':args.stage,'reason':repr(error),'no_retry':True})
        raise


if __name__=='__main__':main()
