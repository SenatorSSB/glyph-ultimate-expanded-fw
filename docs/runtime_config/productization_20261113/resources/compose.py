#!/usr/bin/env python3
"""Recompose affected Mk6 core0 routes from exact linked ELF inventory and accepted source predicates."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shape(row):
    return [row['resolved_frame_bytes'], sorted(set(x['name'] for x in row['calls'])),
            sorted(set(x['instruction'] for x in row['indirect'])), sorted(set(x['name'] for x in row['tail']))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resource', type=Path, required=True)
    parser.add_argument('--baseline-archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    graph = json.loads((args.resource / 'functions.json').read_bytes())
    with tarfile.open(args.baseline_archive) as archive:
        previous = json.load(archive.extractfile('current/current/functions.json'))
        ledger = json.load(archive.extractfile('baseline-composed/resource-source-predicate-ledger.json'))
    names = set(graph) | set(previous)
    reused = ('lfs_', 'pb_', 'encode_', 'decode_', 'CheckedStorage::', 'config_wire::', 'flash_', '__wrap_mem')
    lower = sorted(name for name in names if name.startswith(reused))
    changed = [name for name in lower if name not in previous or name not in graph or shape(graph[name]) != shape(previous[name])]
    assert not changed, ('Review changed lower storage/codec graph', changed)

    def sym(part):
        if part in graph:
            return part
        matches = [n for n in graph if part in n and ('::{lambda' in part or '::{lambda' not in n)]
        assert len(matches) == 1, (part, matches)
        return matches[0]

    def frame(part):
        return graph[sym(part)]['resolved_frame_bytes']

    def edge(caller, callee):
        row = graph[sym(caller)]
        assert sym(callee) in {c['name'] for c in row['calls'] + row['tail']}, (caller, callee)

    def blocked_edge(caller, callee):
        row = graph[sym(caller)]
        assert sym(callee) not in {c['name'] for c in row['calls'] + row['tail']}, (caller, callee)

    def total(*parts):
        return sum(x if isinstance(x, int) else frame(x) for x in parts)

    def val(label, number):
        return [label, number]

    routes = {}
    def route(name, *parts):
        components = [x if isinstance(x, list) else val(sym(x), frame(x)) for x in parts]
        routes[name] = {'parts': components, 'total': sum(x[1] for x in components)}
        return routes[name]['total']

    pre = 'ProfileStore::PreparePackageDispatch()'
    prep = 'ProfileStore::PrepareLifecycleTransaction('
    create = 'ProfileStore::PreparePackageTransaction('
    publish = 'ProfileStore::PublishPackageTransaction() [clone'
    describe = 'GlyphPackageSourceReader::DescribeConfig('
    encode = '::EncodeConfigFacts('
    callback = 'EncodeConfigFacts(_Config const&, package_storage::ConfigFacts&)::{lambda'
    project = 'Classifier::RunProjection()'
    installed = 'Classifier::RunInstalled()'
    classifier = '::ClassifyNamespaceInto('
    baseline = 'Classifier::RunBaseline()'
    roots = 'Classifier::RunRoots()'
    owned = 'Classifier::OwnedSet('
    reader = 'GlyphPackageSourceReader::'
    material = reader + 'MaterializeProjection('
    cget = reader + 'Config('
    load = reader + 'LoadNamedConfig('
    parse = 'Persistence::ObservePackageConfig('
    parsed = 'Persistence::RunObservedPackageConfig()'
    for a, b in [(pre, prep), (pre, create), (prep, describe), (create, describe), (describe, encode),
                 (roots, 'Classifier::LoadRoot('), ('Classifier::LoadRoot(', '::ReadIntentFacts('),
                 (classifier, baseline), (classifier, project), (classifier, installed), (baseline, owned),
                 (reader + 'Native(', material), (material, load), (load, parse), (parse, parsed),
                 (publish, '::RetirePreviousPackageRecord()'), ('::RetirePreviousPackageRecord()', 'CheckedStorage::Remove('),
                 ('loop', '::persist_ordinary_chord('), ('loop','::persist_managed_chord('), ('loop', '::mark_first_mode_ready()')]:
        edge(a,b)
    blocked_edge(create, prep)
    blocked_edge(roots, '::ReadIntentFacts(')
    blocked_edge('::request_mode_destination(', 'Persistence::LoadConfigChecked(')
    # The calibrating lower bounds are the current source-bounded values in the archived ledger.
    led = {r['id']:r for r in ledger['new_routes']}
    def historical(route_id, component):
        c, = [x for x in led[route_id]['components'] if x['name']==component]
        return val(component,c['bytes'])
    cap = 2048
    base168 = val('packet foreground + max(admission observation, publication) caller reserve', 168)
    irq = val('configurator IRQ',348)
    # Explicit current stack through Prepare and Publish both fit the historical 168 prefix.
    foreground = total('main','loop','ConfiguratorBackend::SendReport()','ConfiguratorBackend::HandlePackageRequest(', 'ProfileStore::DispatchPackage(')
    assert foreground+frame(pre) <=168 and foreground <=168
    assert frame('loop') <=32
    generic_io = historical('package.segment.generic_rename','generic_Rename_U')
    for owner, title in [(create,'create'),(prep,'lifecycle')]:
        route(title+'.compact_description',base168,owner,describe,encode,
              historical('package_prepare.description','original_PB_encode'),callback,
              '::UpdateConfigEncodingHash(',val('ROM copy',12),irq)
    route('publish.root_rename',base168,publish,'::SegmentRename()',generic_io,irq)
    route('publish.config_rotation',base168,publish,'ProfileStore::PublishPackageConfigStage()',
          'Persistence::PublishPreparedPackageConfig()', 'Persistence::PublishPackageStaged()',
          val('rotate helper maximum',8),generic_io,irq)
    route('publish.retire_remove',base168,publish,'::RetirePreviousPackageRecord()',val('generic Remove upper',1376),irq)
    route('publish.retire_checked_read',base168,publish,'::RetirePreviousPackageRecord()', '::MountedStorage::CheckedRead(',
          'CheckedStorage::ReadFile(',val('checked read-only open/stat/read/close max',540),irq)
    route('publish.segment_open',base168,publish,val('segment open',40),historical('package.segment.generic_open','generic_open_U_adjusted'),irq)
    route('publish.record_open',base168,publish,val('record Open wrapper from predecessor',56),historical('package.record.generic_open','generic_open_U_adjusted'),irq)
    # Boot import + IRQ, physical service + IRQ, and recovery/terminal remount bound.
    # Baseline boot/import maximum344+336, physical parent comparison described in accompanying report.
    boot_irq = val('boot import ancestors plus IRQ',680)
    physical_irq = total('main','loop','::service_profile_selection()', 'profile_selection::Persist<',
                         'Persistence::SaveConfigIfGenerationMatches(', 'Persistence::InitializeOrdinarySaveContext(',
                         'ProfileStore::BeginOrdinaryConfigWrite(',408)
    assert physical_irq <=680
    max_owner=val('max of boot/ordinary physical/recovery/configurator classifier contexts including IRQ',680)
    general_tail = val('full historical Config semantic check + rejected alternatives',1000)
    defaults = val('iterative descriptor defaults + fixed 4-depth leaf',total('Persistence::DecodeObservedPackageConfig()',
            'DecodeObservedConfigFields(', 'DecodeObservedField(', 'InitializeObservedMessage(', 'pb_decode', 'pb_decode_inner',416,208))
    scalar = val('NOINIT scalar read through CheckedStorage without submessage recursion',total('Persistence::DecodeObservedPackageConfig()',
            'DecodeObservedConfigFields(', 'DecodeObservedField(',472,'::read_config_file(',308))
    canonical = val('canonical child sizing + 3-level child PB upper',total('Persistence::FinishObservedPackageConfig()',
            'CompareObservedConfigBytes(', 'EncodeObservedField(', 'pb_get_encoded_size',712))
    compact_semantic = val('compact Config validation with format1 and zero embedded profiles',752)
    for moment, root, adapter in [('roots',roots,'Classifier::LoadConfigs()'),('scan_recheck','Classifier::Run()','Classifier::HistoricalRetained()')]:
        for tail in (general_tail,defaults,scalar,canonical):
            route('classify.'+moment+'.'+tail[0],max_owner,classifier,root,adapter,cget,load,parse,parsed,tail)
    # Every observation inside OwnedSet already rejected embedded profile arrays.
    # The inclusive compact semantic envelope is 64+152+16+56+464: the last
    # component covers 448-byte legacy formatter upper plus its bridge, versus
    # the smaller extents/button/RGB helpers. Full historical mode retains1000.
    assert total('Persistence::FinishObservedPackageConfig()', 'Persistence::ValidateObservedPackageConfig(',
                 'validate_glyph_config(', 'validate_config_semantics(',464) <= compact_semantic[1]
    phase = val('max baseline/terminal/installed frame for OwnedSet',max(frame(baseline),frame('Classifier::RunFinal()'),frame(installed)))
    for suffix,branch in [('native',[reader+'Native(',material]),('row',[reader+'Row(']),('rgb',[reader+'Rgb('])]:
        for tail in (defaults,scalar,canonical,compact_semantic):
            route('classify.owned.'+suffix+'.'+tail[0],max_owner,classifier,phase,owned,*branch,load,parse,parsed,tail)
    for suffix, owner in [('lifecycle',prep),('create',create)]:
        for tail in (general_tail,defaults,scalar,canonical):
            route(suffix+'.aggregate.'+tail[0],base168,owner,'::ComputePackageAggregate(',reader+'Row(',load,parse,parsed,tail,irq)
    route('classify.append_stat',max_owner,classifier,project,reader+'AppendConfig(', '::CompareAppendFiles(', '::NextAppendField(',val('checked Stat upper',532))
    route('classify.lifecycle_projection.full_config_hash',max_owner,classifier,project, reader+'LifecycleConfig(', '::HashMessage(',
          historical('package_prepare.description','original_PB_encode'), val('SHA callback max',184),val('ROM copy',12))
    route('classify.lifecycle_projection.reload',max_owner,classifier,project,reader+'LifecycleConfig(',load,parse,parsed,general_tail)
    route('classify.root_object_read',max_owner,classifier,roots,'Classifier::LoadRoot(',reader+'Read(',val('checked read-only open/stat/read/close max',540))
    route('classify.intent_hash',max_owner,classifier,roots,'Classifier::LoadRoot(','::ReadIntentFacts(',val('SHA final/compression upper',240))
    route('legacy.full_config_description', 'main','loop','ConfiguratorBackend::SendReport()',val('conservative legacy SET handler',8),
          'Persistence::SaveConfig(', 'Persistence::InitializeOrdinarySaveContext(', 'ProfileStore::BeginOrdinaryConfigWrite(',
          describe,encode,historical('legacy_SET_full_Config.description','original_PB_encode'),callback,
          '::UpdateConfigEncodingHash(',val('ROM copy',12),irq)
    route('ordinary.chord_configurator_full_depth', 'main','loop','::persist_ordinary_chord(',
          'Persistence::LoadConfigChecked(',val('validated published D4 decoder',1208),'::read_config_file(',val('noninline legacy read',300),irq)
    route('managed.chord_physical_full_depth_unknown_field', 'main','loop','::persist_managed_chord(','profile_selection::Persist<',
          'Persistence::LoadConfigChecked(',val('D4 unknown skip',1112),'::read_config_file(',val('readonly lower',308),val('physical IRQ',408))
    # Retain full legacy stage-write baseline with actual loop32; all validator/callback/FS functions are unchanged below that entry.
    route('legacy.SET_stage_write',val('prior accepted non-IRQ foreground, write/flash/masked branch under same or smaller loop frame',1700),irq)
    route('classify.directory_scan',max_owner,classifier,'Classifier::Run()',reader+'ObjectAt(',
          'CheckedStorage::Enumerate(', 'lfs_dir_open','lfs_dir_find','lfs_dir_fetchmatch',
          'lfs_dir_find_match',val('block read',64),val('read or unsigned divide leaf',20))
    route('lifecycle.geometry',base168,prep,'::MountedStorage::Geometry(', 'CheckedStorage::Capacity(',
          'lfs_fs_size','lfs_fs_rawtraverse.constprop.0','lfs_dir_fetchmatch','lfs_dir_find_match',
          val('block read',64),val('read or unsigned divide leaf',20),irq)
    route('lifecycle.protected_root_enumeration',base168,prep,'::PackageProtectedBytes(',reader+'ObjectAt(',
          'CheckedStorage::Enumerate(', 'lfs_dir_open','lfs_dir_find','lfs_dir_fetchmatch',
          'lfs_dir_find_match',val('block read',64),val('read or unsigned divide leaf',20),irq)
    route('lifecycle.stale_root_reread',base168,prep,'::RecheckPackageBaselineRoots(',reader+'Read(',
          val('max checked RO open/stat/read/close',540),irq)
    if 'profile_selection::GamecubeSelectionPending()' in graph:
        edge('profile_selection::GamecubeSelectionPending()','managed_chord_held(')
        predicate=total('profile_selection::GamecubeSelectionPending()','managed_chord_held(')
        route('gamecube.chord_idle_predicate','main','loop','GamecubeBackend::SendReport()',
              'GamecubeConsole::WaitForPollStartBounded(',val('actual predicate + sample',predicate),val('physical IRQ',408))
    assert all(r['total'] <= cap for r in routes.values()), {k:r for k,r in routes.items() if r['total']>cap}
    receipt={'source':args.resource.parent.name,'elf_sha256':digest(args.resource.parent/'firmware.elf'),
             'baseline_archive_sha256':digest(args.baseline_archive),'functions_sha256':digest(args.resource/'functions.json'),
             'lower_graph_functions_compared':len(lower),'equivalence':'resolved frame, set of direct callees, indirect instruction union and tail destinations',
             'routes':routes,'stack_ceiling_each_core':2048,'maximum_affected_route':max(r['total'] for r in routes.values()),
             'new_lifecycle_maximum':max(r['total'] for k,r in routes.items() if k.startswith(('publish.','classify.','lifecycle.'))),
             'measured_hardware_highwater':False}
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(f"{len(routes)} route compositions, maximum {receipt['maximum_affected_route']}, lifecycle {receipt['new_lifecycle_maximum']}")


if __name__=='__main__':
    main()
