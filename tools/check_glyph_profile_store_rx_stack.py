#!/usr/bin/env python3
"""Enumerate target RX/task C frames; never a whole-target stack certificate."""
import argparse, hashlib, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--resources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    data=json.loads(a.resources.read_text());rows={x['function']:x for x in data['frames']}
    def frames(needle):
        found=[row for name,row in rows.items() if (name.endswith(needle) or needle+'.' in name if needle.startswith(':') else needle in name) and '::<lambda' not in name]
        if not found:raise AssertionError('missing actual target frame '+needle)
        coords={':'.join(row['function'].split(':',3)[:3]) for row in found}
        # Include optimizer-split implementations emitted at the same source coordinate.
        selected={name:row for name,row in rows.items() if ':'.join(name.split(':',3)[:3]) in coords}
        return sum(row['bytes'] for row in selected.values())
    def group(names):return {name:frames(name) for name in names}
    callers=group([':int main()',':void loop()','ConfiguratorBackend::SendReport()','ConfiguratorBackend::HandleProfileStore()','ConfiguratorBackend::ReadPacket('])
    packet=group(['COBSStream::available()','COBSStream::read()','COBSStream::peek()','CoordinatedCdcStream::available()','CoordinatedCdcStream::read()','CoordinatedCdcStream::peek()'])
    native=group([':tud_cdc_n_read',':tu_fifo_read_n',':usbd_edpt_claim',':usbd_edpt_xfer',':dcd_edpt_xfer',':hw_endpoint_xfer_start',':hw_endpoint_start_next_buffer',':_hw_endpoint_buffer_control_update32'])
    task=group(['TinyUSB_Device_Task()',':tud_task_ext',':cdcd_xfer_cb',':tu_fifo_write_n'])
    control=group([':cdcd_control_xfer_cb',':tud_control_xfer',':tud_control_status',':usbd_control_xfer_cb','tud_cdc_line_state_cb('])
    descriptor=group(['Adafruit_USBD_Device::descriptor_string_cb','Adafruit_USBD_Device::getSerialDescriptor','strcpy_utf16('])
    common=sum(callers.values())+sum(packet.values())
    chains={'receive_bulk_fifo_endpoint_inventory':common+sum(native.values()),
            'receive_task_out_completion_inventory':common+sum(native.values())+sum(task.values()),
            'receive_task_control_descriptor_inventory':common+sum(native.values())+sum(task.values())+sum(control.values())+sum(descriptor.values())}
    for name,size in chains.items():assert size<4096,(name,size)
    abi=data['abi_sizes'];assert abi['ProfileStoreRxDiagnostics']==32
    baseline=data.get('baseline_backend_abi')
    result={'status':'PASS_ENUMERATED_RX_C_PATHS','candidate_elf_sha256':data['candidate_elf_sha256'],
            'resource_report_sha256':hashlib.sha256(a.resources.read_bytes()).hexdigest(),
            'caller_frames':callers,'packet_adapter_frames':packet,'fifo_endpoint_frames':native,
            'task_completion_frames':task,'control_frames':control,'descriptor_frames':descriptor,
            'enumerated_bytes':chains,'margin_to_scratch4096':{name:4096-size for name,size in chains.items()},
            'backend_abi':{name:abi[name]for name in ('ConfiguratorBackend','CoordinatedCdcStream','ProfileStoreRxDiagnostics')},
            'baseline_backend_abi':baseline,
            'limitations':'Conservative inventories include sequential/mutually exclusive helpers. Not a callgraph or whole-target bound; exclude ROM/SDK/libc helpers, snprintf internals, IRQ nesting, arbitrary callbacks and pre-setup startup. Hardware watermarks required.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
