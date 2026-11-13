#!/usr/bin/env python3
"""Owner-authorized installed-candidate continuation. No installation entry point."""
import argparse
import importlib.util
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
V2 = HERE.parent / 'hardware_v2'
spec = importlib.util.spec_from_file_location('sealed_display_v2', V2 / 'executor.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
need, load, save, digest = v2.need, v2.load, v2.save, v2.digest
ID = 'GLYPH-DISPLAY-9E69188D-CONT-v1'
EPISODE = Path('/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/display-hardware-results/GLYPH-DISPLAY-9E69188D-CONT-v1-20261113')
INHERITED = v2.EPISODE_PATH
STAGES = ('first_xinput_boot', 'display', 'post_snapshot', 'final_xinput_boot', 'finish')


def verify_inherited():
    binding = load(HERE / 'INHERITED.json')
    for absolute, expected in binding['files'].items():
        path = Path(absolute)
        need(path.is_file() and not any(p.is_symlink() for p in (path, *path.parents)), 'inherited file unavailable')
        need(digest(path.read_bytes()) == expected, 'inherited evidence changed: ' + absolute)
    before = load(INHERITED / 'pre_snapshot/result.json')
    terminal = load(INHERITED / 'terminal.json')
    install = load(INHERITED / 'install/owner-event.json')
    need(before['result'] == 'PASS' and before['controller_exchanges'] == 34 and
         len(before['profiles']) == 27 and load(INHERITED / 'pre_snapshot/settlement.json')['port_closed'],
         'incomplete/unsettled inherited baseline')
    need(terminal['stage'] == 'install' and terminal['request_invocations'] == 0 and
         terminal['reason'] == "ValueError('manual install/copy outcome uncertain')" and
         not (INHERITED / 'install/result.json').exists(), 'closed v2 evidence differs')
    need(install['manual_install_count'] == 1 and install['one_same_unit_bootloader'] is True and
         install['copy_result'] == 'confirmed_success' and install['reenumeration'] == 'unambiguous' and
         install['source_sha'] == binding['built_source_sha'] and install['uf2_sha256'] == binding['uf2_sha256'] and
         install['uf2_bytes'] == 1296896, 'owner-reported installation evidence differs')
    # Volume path is optional metadata. Do not read it as an admission condition.
    return binding


def verify():
    manifest = load(HERE / 'MANIFEST.json')
    for relative, expected in manifest['files'].items():
        path = HERE / relative
        need(path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == expected,
             'continuation preparation changed: ' + relative)
    need(digest((V2 / 'packet.json').read_bytes()) == manifest['sealed_v2_packet_sha256'], 'sealed v2 packet changed')
    need(digest((V2 / 'PREPARATION_MANIFEST.json').read_bytes()) == manifest['sealed_v2_preparation_sha256'], 'sealed v2 preparation changed')
    packet, pb, package = v2.verify_preparation()
    verify_inherited()
    return packet, pb, package


def authorize(receipt):
    need(receipt.get('owner_directive') is True and bool(receipt.get('owner_message_reference')),
         'explicit owner continuation directive required')
    binding = load(HERE / 'INHERITED.json')
    expected = {'continuation_id': ID, 'manifest_sha256': digest((HERE / 'MANIFEST.json').read_bytes()),
                'v2_terminal_commit': binding['v2_terminal_commit'],
                'built_source_sha': binding['built_source_sha'], 'uf2_sha256': binding['uf2_sha256']}
    need(all(receipt.get(k) == value for k, value in expected.items()), 'continuation authority binding differs')


def copy_baseline(destination):
    verify_inherited()
    shutil.copytree(INHERITED / 'pre_snapshot', destination / 'pre_snapshot')
    save(destination, 'inherited-baseline.json', {'source': str(INHERITED / 'pre_snapshot'),
         'classification': 'INHERITED_V2_BEFORE_NOT_A_NEW_SESSION',
         'v2_terminal_commit': load(HERE / 'INHERITED.json')['v2_terminal_commit'],
         'installation': 'OWNER_REPORTED_SINGLE_EXACT_INSTALL; NO_MACHINE_BUILD_ATTESTATION',
         'v2_install_stage': 'REMAINS_TERMINAL_NO_PASS', 'new_installations_authorized': 0})


class Runner(v2.Runner):
    def prior(self, stage):
        if stage == 'install':
            # Prospective owner correction, never a fabricated v2 install PASS.
            need(not (self.c / 'terminal.json').exists(), 'continuation terminal')
            need(load(self.c / 'inherited-baseline.json')['v2_install_stage'] == 'REMAINS_TERMINAL_NO_PASS',
                 'missing inherited evidence binding')
            verify_inherited()
            for path in (INHERITED / 'pre_snapshot').iterdir():
                if path.is_file():
                    need((self.c / 'pre_snapshot' / path.name).read_bytes() == path.read_bytes(),
                         'inherited baseline copy changed')
            return
        super().prior(stage)

    def snapshot(self, stage, port, post):
        need(post is True, 'no new pre-install snapshot allowed')
        return super().snapshot(stage, port, post)

    def execute(self, name, event):
        need(name in STAGES, 'only remaining read-only/visual stages allowed')
        self.prior('install')  # Recheck inherited copy at every remaining stage.
        # V2 finish verifies 70 combined exchanges: exactly 34 inherited + 36 new.
        if name == 'finish':
            count = sum(load(self.c / s / 'result.json').get('controller_exchanges', 0) for s in STAGES[:-1])
            need(count == 36, 'remaining exchange count must be exactly 36')
        return super().execute(name, event)


def established():
    if not EPISODE.is_dir() or any(p.is_symlink() for p in (EPISODE, *EPISODE.parents)):
        return None
    marker = EPISODE / 'begin-claim.json'
    return EPISODE if marker.is_file() and not marker.is_symlink() else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('check', 'begin', *STAGES))
    parser.add_argument('--authority', type=Path)
    parser.add_argument('--owner-event', type=Path)
    args = parser.parse_args()
    try:
        owned = established()
        if owned:
            need(not (owned / 'terminal.json').exists(), 'continuation terminal; no retry')
        packet, pb, package = verify()
        if args.stage == 'check':
            print('PASS_OFFLINE_CONTINUATION_PREPARATION; no device access')
            return
        need(args.authority, 'owner directive receipt required')
        receipt = load(args.authority)
        authorize(receipt)
        if args.stage == 'begin':
            EPISODE.mkdir(mode=0o700, parents=True, exist_ok=False)
            save(EPISODE, 'begin-claim.json', {'continuation_id': ID, 'one_episode_only': True})
            save(EPISODE, 'authority.json', receipt)
            copy_baseline(EPISODE)
            print('Continuation claimed; inherited baseline copied; no device access')
            return
        need(load(EPISODE / 'authority.json') == receipt, 'authority receipt changed')
        need(args.owner_event, 'actual fresh owner event required')
        result = Runner(packet, EPISODE, pb, package, v2.LiveIO()).execute(args.stage, load(args.owner_event))
        print(json.dumps(result, indent=2))
    except BaseException as error:
        owned = established()
        if owned and not (owned / 'terminal.json').exists():
            save(owned, 'terminal.json', {'result': 'INCONCLUSIVE_TERMINAL_STOP', 'stage': args.stage,
                 'reason': repr(error), 'no_retry': True})
        raise


if __name__ == '__main__':
    main()
