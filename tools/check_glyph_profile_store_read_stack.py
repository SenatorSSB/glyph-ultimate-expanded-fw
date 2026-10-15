#!/usr/bin/env python3
"""Compose enumerated READ C frames from actual target resource collection.

Not an IRQ/ROM/SDK or arbitrary callback whole-target stack certificate.
"""
import argparse,json,hashlib
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--resources',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 data=json.loads(a.resources.read_text());rows={x['function']:x for x in data['frames']}
 def matching(needle):
  if needle.startswith(':') and not needle.startswith('::'):
   found=[x for k,x in rows.items() if k.endswith(needle) or (needle+'.') in k]
  else:
   found=[x for k,x in rows.items() if needle in k and ('::<lambda' not in k or '::<lambda' in needle)]
  if not found:raise AssertionError('missing actual target frame '+needle)
  return found
 def frame(needle):return max(x['bytes'] for x in matching(needle))
 def split(needle):
  coords={x['function'].split(':',3)[0]+':'+':'.join(x['function'].split(':',3)[1:3])+':' for x in matching(needle)}
  return sum(x['bytes'] for k,x in rows.items() if any(k.startswith(c) for c in coords))
 def group(names):return {n:split(n) for n in names}
 caller=group([':int main()',':void loop()','ConfiguratorBackend::SendReport()','ConfiguratorBackend::HandleProfileStore()'])
 storage=group(['ProfileStore::Read(uint32_t','ProfileStore::ReadProfile(','MountedStorage::CheckedRead(','CheckedStorage::ReadFile('])
 # Conservative aggregate includes both single-byte and buffer COBS/writer
 # entry points, though optimizer paths need not keep all live simultaneously.
 trace=group(['ProfileStoreReadTrace.hpp:9:','::<lambda(void*, uint32_t, uint32_t)>::_FUN','ConfiguratorBackend::TraceProfileStage(','ConfiguratorBackend::WriteProfilePacket(','COBSPrint::write(uint8_t)','COBSPrint::write(const uint8_t*','COBSPrint::end()','ProfilePacketWriter::write(uint8_t)','ProfilePacketWriter::write(const uint8_t*'])
 task=group(['TinyUSB_Device_Task()',':tud_task_ext'])
 completion=group([':cdcd_xfer_cb',':tud_cdc_n_write_flush',':tu_fifo_read_n',':usbd_edpt_claim',':usbd_edpt_xfer',':dcd_edpt_xfer',':hw_endpoint_xfer_start',':hw_endpoint_start_next_buffer',':_hw_endpoint_buffer_control_update32'])
 control=group([':cdcd_control_xfer_cb',':tud_control_xfer',':tud_control_status',':usbd_control_xfer_cb','tud_cdc_line_state_cb('])
 descriptor=group(['Adafruit_USBD_Device::descriptor_string_cb','Adafruit_USBD_Device::getSerialDescriptor','strcpy_utf16('])
 common=sum(caller.values())+sum(storage.values())+sum(trace.values())+sum(task.values())
 chains={'traced_checked_read_cdc_completion':common+sum(completion.values()),
         'traced_checked_read_control_and_descriptor_inventory':common+sum(completion.values())+sum(control.values())+sum(descriptor.values())}
 encode=group([':pb_encode',':encode_field',':encode_basic_field',':pb_encode_submessage',':pb_encode_tag_for_field',':pb_write',':pb_encode_varint',':pb_encode_tag',':pb_get_encoded_size',':pb_check_proto3_default_value',':pb_field_iter_begin_const',':pb_field_iter_begin',':pb_field_iter_next',':load_descriptor_values'])
 # Four schema levels; count even mutually exclusive helpers at every level.
 chains['response_encode_four_schema_levels']=sum(caller.values())+4*sum(encode.values())
 for name,size in chains.items():assert size<4096,(name,size)
 usb_files=['usbd.c','usbd_control.c','cdc_device.c','tusb_fifo.c','tusb.c','dcd_rp2040.c','rp2040_usb.c','Adafruit_TinyUSB_rp2040.cpp','Adafruit_TinyUSB_API.cpp','Adafruit_USBD_CDC.cpp','Adafruit_USBD_Device.cpp']
 inventory={f:sum(x['bytes'] for k,x in rows.items() if '/'+f+':' in k) for f in usb_files}
 result={'status':'PASS_ENUMERATED_C_PATHS','resource_report_sha256':hashlib.sha256(a.resources.read_bytes()).hexdigest(),'candidate_elf_sha256':data['candidate_elf_sha256'],'caller_frames':caller,'storage_frames':storage,'trace_frames':trace,'task_frames':task,'cdc_completion_frames':completion,'control_frames':control,'descriptor_frames':descriptor,'encode_frames':encode,'enumerated_bytes':chains,'margin_to_scratch4096':{n:4096-v for n,v in chains.items()},'all_usb_emitted_frames_inventory':inventory,'inventory_is_not_callgraph_bound':True,'limitations':'No whole-target upper bound: excludes ROM/SDK helpers, IRQ nesting, arbitrary indirect callbacks and pre-setup startup. Inventory overcounts mutually exclusive functions; not a proof each function occurs once. Exact hardware watermarks required.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
