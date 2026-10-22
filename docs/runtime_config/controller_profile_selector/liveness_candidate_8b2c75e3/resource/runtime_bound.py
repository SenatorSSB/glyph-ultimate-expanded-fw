import runpy,sys,json
from pathlib import Path
O=Path(sys.argv[1]);sys.argv=['core1_bound.py','--output-dir',str(O)]
g=runpy.run_path('/private/tmp/glyph-selector-resource-audit-20261022/core1_bound.py')
F=g['F'];D=g['D'];calc=g['calc'];find=g['find']
D[find('GamecubeBackend::SendReport(')]=['CommunicationBackend::UpdateOutputs()']
D[find('GamecubeConsole::WaitForPollStartBounded(')]=['profile_selection::Pending()']
D['CommunicationBackend::UpdateOutputs()']=['GamecubeBackend::BackendId()']+[n for n in F if n.startswith(('ControllerMode::UpdateOutputs(', 'KeyboardMode::UpdateOutputs('))]
D['CommunicationBackend::ScanInputs(InputScanSpeed)']=['SwitchMatrixInput<4u, 11u>::ScanSpeed()', 'SwitchMatrixInput<4u, 11u>::UpdateInputs(_InputState&)']
D['SwitchMatrixInput<4u, 11u>::UpdateInputs(_InputState&)']=['DebouncedSwitchMatrixInput<4u, 11u>::UpdateButtonState(_InputState&, unsigned int, unsigned int, bool)']
D[find('ControllerMode::UpdateOutputs(')]=[n for n in F if n.startswith(('ControllerMode::DiagnosticNativeGeneration(', 'Ultimate::DiagnosticNativeGeneration(', 'InputMode::HandleRemap(', 'InputMode::HandleSocd(', 'ProjectM::HandleSocd(', 'Smash64::HandleSocd(', 'FgcMode::HandleSocd(', 'Melee20Button::HandleSocd(', 'ControllerMode::UpdatePreprocessedOutputs(', 'Ultimate::UpdatePreprocessedOutputs('))]
D[find('ControllerMode::UpdatePreprocessedOutputs(')]=[n for n in F if '::UpdateDigitalOutputs(' in n or '::UpdateAnalogOutputs(' in n]
directions=[n for n in F if '::UpdateDirections(' in n]
for n in F:
 if F[n]['indirect'] and ('::UpdateAnalogOutputs(' in n or n.startswith('ultimate_native::Evaluate(')):D[n]=directions
for n in list(g['memo']):g['memo'].pop(n)
for n in list(g['paths']):g['paths'].pop(n)
out={}
for n in ['GamecubeBackend::SendReport()',find('GamecubeConsole::WaitForPollStartBounded('),'GamecubeConsole::PauseAtIdleBoundary()','GamecubeConsole::ResetAfterInvalidPoll()','GamecubeConsole::Detect()','GamecubeConsole::WaitForPollEnd()','GamecubeConsole::SendReport(gc_report_t*)','joybus_port_init','joybus_port_reset','joybus_send_bytes','joybus_receive_bytes','CommunicationBackend::UpdateOutputs()','CommunicationBackend::ScanInputs(InputScanSpeed)']:
 b,p=calc(n);out[n]={'bound':b,'path':p}
res={'bounds':out,'unknown':g['unknown'],'dynamic_targets':D,'all_function_bounds':g['memo'],'special_bounds':g['special'],'special_notes':g['notes'],'edges':g['edges']}
(O/'gc-bound-graph.json').write_text(json.dumps(res,indent=2)+'\n')
print('GC BOUNDS',json.dumps(out,indent=2));print('GC UNKNOWN',g['unknown'])
