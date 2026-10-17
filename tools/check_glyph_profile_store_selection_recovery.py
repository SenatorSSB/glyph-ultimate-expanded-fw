#!/usr/bin/env python3
"""Real mode-selection TU and recovery initializer, including old-defect controls."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from check_glyph_stage_b_ultimate_profiles import NANOPB, ROOT

HOST = ROOT / 'tools/fixtures/profile_store_selection_recovery_host'

def run(args: list[str], expected: int = 0) -> str:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                            env={**os.environ, 'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1'}, timeout=60)
    if (result.returncode == 0) != (expected == 0):
        raise AssertionError(' '.join(args) + '\n' + result.stdout + result.stderr)
    return result.stdout + result.stderr

def main() -> int:
    nanopb = Path(os.environ.get('GLYPH_PROFILE_STORE_NANOPB', str(NANOPB)))
    with tempfile.TemporaryDirectory(prefix='glyph-selection-recovery-') as directory:
        temp = Path(directory)
        generated = temp / 'generated'; generated.mkdir()
        schema = ROOT / 'schema/haybox'
        run([sys.executable, str(nanopb/'generator/nanopb_generator.py'), '-I', str(schema),
             '-f', str(schema/'config.options'), '--error-on-unmatched', '--no-timestamp',
             '-D', str(generated), str(schema/'config.proto')])
        # The control restores the exact old loop action while retaining the
        # current declaration/host ABI, so detection is a runtime assertion.
        production = ROOT / 'src/core/mode_selection.cpp'
        old = temp / 'old_selection.cpp'
        source = production.read_text()
        start = source.index('    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {', source.index('void select_mode('))
        end = source.index('\n}', start)
        old.write_text(source[:start] + '''    for (size_t i = 0; i < config.game_mode_configs_count; ++i) {
        if (all_buttons_held(inputs.buttons, mode_activation_masks[i]) && i != current_mode_index) {
            current_mode_index = i;
            for (size_t j = 0; j < backends_count; ++j) set_mode(backends[j], config.game_mode_configs[i], config);
            return;
        }
    }''' + source[end:])
        recovery_control = temp/'old_recovery/core'; recovery_control.mkdir(parents=True)
        header = (ROOT/'include/core/RecoveryInitialization.hpp').read_text()
        assert 'store.BeginRecovery(incarnation, required_root_format);' in header
        (recovery_control/'RecoveryInitialization.hpp').write_text(header.replace('store.BeginRecovery(incarnation, required_root_format);', '(void)store; (void)incarnation; (void)required_root_format; // historical RT2 skipped Begin'))
        def compile_case(name: str, mode_source: Path, old_recovery: bool=False) -> Path:
            exe = temp/(name+'-bin')
            includes = ([temp/'old_recovery'] if old_recovery else []) + [HOST/'include', generated, nanopb,
                 ROOT/'tools/fixtures/mode_selection_host/include', ROOT/'include']
            # The existing mode-only fixture supplies inert hardware headers;
            # its Config stub is intentionally behind the freshly generated ABI.
            run(['c++', '-std=c++17', '-fshort-enums', '-Wall', '-Wextra', '-Werror',
                 '-Wno-missing-field-initializers', '-Wno-unneeded-internal-declaration', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                 '-DMODE_SELECTION_SOURCE="'+str(mode_source)+'"',
                 *sum((['-I',str(p)] for p in includes), []), str(HOST/'selection_recovery.cpp'), '-o', str(exe)])
            return exe
        exe = compile_case('production', production)
        print(run([str(exe),'selection']), end='')
        print(run([str(exe),'recovery']), end='')
        print(run([str(exe),'boot']), end='')
        old_exe = compile_case('old_selection', old)
        failure = run([str(old_exe),'selection'], expected=1)
        assert 'same destination must not save/reset/activate' in failure
        old_recovery_exe = compile_case('old_recovery', production, True)
        failure = run([str(old_recovery_exe),'recovery'], expected=1)
        assert 'manual RT2 must initialize validator and store inspection' in failure
        def function_body(text: str, name: str) -> str:
            start = text.index('void '+name+'(')
            brace = text.index('{',start)
            depth = 1; end = brace + 1
            while depth:
                depth += (text[end] == '{') - (text[end] == '}')
                end += 1
            return text[start:end]
        app = (ROOT/'config/glyph/common/src/config.cpp').read_text()
        recovery = function_body(app,'enter_recovery_configurator')
        setup = function_body(app,'setup')
        loop = function_body(app,'loop')
        def app_case(name: str, old_manual: bool=False, old_auto: bool=False) -> Path:
            directory = temp/name; directory.mkdir()
            rec = recovery
            boot = setup
            if old_manual:
                start = rec.index('    const RecoveryInitialization recovery = initialize_recovery(')
                end = rec.index(';',start)+1
                rec = rec[:start] + '    const RecoveryInitialization recovery{false,true};' + rec[end:]
            if old_auto:
                anchor = 'if (load_result != Persistence::LoadResult::Loaded) {\n        enter_recovery_configurator();'
                assert anchor in boot
                boot = boot.replace(anchor, 'if (load_result != Persistence::LoadResult::Loaded) {\n        refuse_boot(BootOutcome::StorageFailure, display_ready);',1)
            (directory/'extracted_setup.inc').write_text(rec+'\n'+boot+'\n'+loop+'\n')
            exe = directory/'routes'
            run(['c++','-std=c++17','-fshort-enums','-Wall','-Wextra','-Werror','-DGLYPH_RT2_COLD_RECOVERY_CANDIDATE=1',
                 '-Wno-missing-field-initializers','-fsanitize=address,undefined','-fno-omit-frame-pointer',
                 *sum((['-I',str(p)] for p in [directory,generated,nanopb,ROOT/'include']),[]),
                 str(HOST/'setup_routes.cpp'),'-o',str(exe)])
            return exe
        routes = app_case('actual_routes')
        for route in ('manual','automatic','filesystem','mb1','cold','cold-mb1','arm-conflict','reboot-return','prepare-failure','start-failure'):
            print(run([str(routes),route]),end='')
        old_routes = app_case('old_manual_routes',old_manual=True)
        failure = run([str(old_routes),'cold'],expected=1)
        assert 'manual recovery installs validator' in failure
        old_routes = app_case('old_auto_routes',old_auto=True)
        failure = run([str(old_routes),'automatic'],expected=1)
        assert 'both entry routes must run recovery transport' in failure
        print('negative_controls_actual_RT2_skipped_init_automatic_dead_refusal=PASS')
        print('negative_controls_old_immediate_activation_and_uninitialized_RT2=PASS')
    print('glyph_profile_store_selection_recovery=PASS')
    return 0
if __name__ == '__main__':
    try: raise SystemExit(main())
    except (AssertionError,OSError,subprocess.SubprocessError) as error:
        print(f'glyph_profile_store_selection_recovery=FAIL: {error}',file=sys.stderr)
        raise SystemExit(1)
