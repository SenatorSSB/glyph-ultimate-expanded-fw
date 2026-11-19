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

def replace_once(source: str, anchor: str, replacement: str) -> str:
    if source.count(anchor) != 1:
        raise AssertionError(f'expected one mutation anchor: {anchor.splitlines()[0]}')
    return source.replace(anchor, replacement, 1)

def without_final_usb(phases: str) -> str:
    guard = '#if defined(GLYPH_MK6_FINAL_USB_GAMEPAD_REENUMERATION) && GLYPH_MK6_FINAL_USB_GAMEPAD_REENUMERATION\n'
    if phases.count(guard) != 1:
        raise AssertionError('expected one final USB re-enumeration guard in boot phases')
    block, end, _ = phases.split(guard, 1)[1].partition('\n#endif\n')
    sequence = '        tud_disconnect();\n        delay(10);\n        tud_connect();'
    if not end or '\n#' in block or block.count(sequence) != 1:
        raise AssertionError('expected one guarded final USB detach/wait/attach sequence')
    return replace_once(phases, guard + block + end + '\n', '')

def with_two_boot_reads(loop: str) -> str:
    loop = replace_once(loop,
        '    BootOutcome outcome = read_boot_state().outcome;\n'
        '    if (outcome == BootOutcome::RecoveryConfigurator) {',
        '    if (read_boot_state().outcome == BootOutcome::RecoveryConfigurator) {')
    return replace_once(loop,
        '    // Only Pending can change between the recovery and normal-service gates.\n'
        '    if (outcome == BootOutcome::Pending) outcome = read_boot_state().outcome;\n'
        '    if (outcome != BootOutcome::Normal) return;',
        '    if (read_boot_state().outcome != BootOutcome::Normal) return;')

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
        # The immutable selection double models only activation counts. Add
        # the new read-only native-view query in scratch without editing it.
        compat=temp/'native-interface/core';compat.mkdir(parents=True)
        double=(HOST/'include/core/ProfileStore.hpp').read_text()
        (compat/'ProfileStore.hpp').write_text(double.replace('  unsigned activations=',
            '  const void *ActiveNativeView() const { return nullptr; }\n  unsigned activations='))
        def compile_case(name: str, mode_source: Path, old_recovery: bool=False) -> Path:
            exe = temp/(name+'-bin')
            includes = ([temp/'old_recovery'] if old_recovery else []) + [temp/'native-interface', HOST/'include', generated, nanopb,
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
        def function_body(text: str, name: str, result_type: str='void') -> str:
            start = text.index(result_type+' '+name+'(')
            brace = text.index('{',start)
            depth = 1; end = brace + 1
            while depth:
                depth += (text[end] == '{') - (text[end] == '}')
                end += 1
            return text[start:end]
        app = (ROOT/'config/glyph/common/src/config.cpp').read_text()
        recovery = function_body(app,'enter_recovery_configurator')
        setup = function_body(app,'setup')
        # Keep the original route assertions and doubles. The same actual
        # setup body now calls returned lifetime phases; include their exact
        # bodies in scratch rather than modeling or flattening their logic.
        def boot_phases(source: str) -> str:
            return '\n'.join(function_body(source, name, 'bool') for name in (
                'PrepareBootDisplay', 'MigrateBootLegacyConfiguration', 'InitializeBootBackends'))
        loop = function_body(app,'loop')
        phases = boot_phases(app)
        def app_case(name: str, old_manual: bool=False, old_auto: bool=False, loop_source: str=loop, phase_source: str=phases) -> Path:
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
            ownership = (ROOT/'include/core/PackageOwnership.hpp').read_text()
            supported = function_body(ownership, 'SupportedLayout', 'inline bool')
            (directory/'extracted_boot_state.inc').write_text(
                function_body(app, 'read_boot_state', 'BootSnapshot') + '\n' +
                function_body(app, 'publish_boot_state') + '\n')
            (directory/'extracted_setup.inc').write_text('namespace package_ownership {\n'+supported+'\n}\n'+rec+'\n'+phase_source+'\n'+boot+'\n'+loop_source+'\n')
            exe = directory/'routes'
            run(['c++','-std=c++17','-DGLYPH_MK6_SWITCH_USB_REENUMERATION=1','-DGLYPH_MK6_FINAL_USB_GAMEPAD_REENUMERATION=1','-fshort-enums','-Wall','-Wextra','-Werror',
                 '-Wno-missing-field-initializers','-fsanitize=address,undefined','-fno-omit-frame-pointer',
                 *sum((['-I',str(p)] for p in [directory,generated,nanopb,ROOT/'include',ROOT/'config/glyph/common/include']),[]),
                 '-include',str(ROOT/'include/core/NativeTargetMetrics.hpp'),
                 '-include',str(ROOT/'config/glyph/common/include/final_usb_gamepad.hpp'),
                 str(HOST/'setup_routes.cpp'),'-o',str(exe)])
            return exe
        routes = app_case('actual_routes')
        for route in ('ordinary','rt2_deferred','automatic','filesystem','mb1','loop_gate','usb_enumeration'):
            print(run([str(routes),route]),end='')
        # Recreate startup before final USB gamepad publication, then run the
        # route harness against the real boot phases with that block removed.
        original_usb = app_case('missing_final_usb', phase_source=without_final_usb(phases))
        assert 'USB gamepad enumeration sequence' in run([str(original_usb), 'usb_enumeration'], expected=1)
        print('negative_control_missing_final_usb=PASS')
        # The old loop reads the boot state at both gates even after a terminal
        # outcome. It still services the same routes, but takes an extra lock.
        old_loop = app_case('two_boot_reads', loop_source=with_two_boot_reads(loop))
        print(run([str(old_loop), 'baseline_loop_gate']), end='')
        assert 'boot snapshot lock count' in run([str(old_loop), 'loop_gate'], expected=1)
        pending = 'if (outcome == BootOutcome::Pending) outcome = read_boot_state().outcome;'
        missed_transition = app_case('missed_transition', loop_source=replace_once(loop, pending, ''))
        assert 'boot gate service trace' in run([str(missed_transition), 'loop_gate'], expected=1)
        print('negative_controls_extra_boot_lock_and_missed_pending_transition=PASS')
        old_routes = app_case('old_auto_routes',old_auto=True)
        failure = run([str(old_routes),'automatic'],expected=1)
        assert 'automatic failures must run recovery transport' in failure
        # Restore the removed physical branch as an executable negative control.
        matrix = '    matrix_input.UpdateInputs(inputs);'
        retired_manual = replace_once(phases, matrix,
            matrix + '\n    if(inputs.rt2&&!inputs.mb1){enter_recovery_configurator();return false;}')
        retired_routes = app_case('retired_manual_route', phase_source=retired_manual)
        failure = run([str(retired_routes),'rt2_deferred'],expected=1)
        assert 'ordinary startup including RT2 alone' in failure
        print('negative_controls_retired_manual_route_automatic_dead_refusal=PASS')
        print('negative_controls_old_immediate_activation_and_uninitialized_RT2=PASS')
    print('glyph_profile_store_selection_recovery=PASS')
    return 0
if __name__ == '__main__':
    try: raise SystemExit(main())
    except (AssertionError,OSError,subprocess.SubprocessError) as error:
        print(f'glyph_profile_store_selection_recovery=FAIL: {error}',file=sys.stderr)
        raise SystemExit(1)
