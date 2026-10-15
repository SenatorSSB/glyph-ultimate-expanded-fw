#include <algorithm>
#include <array>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <vector>
#include <cstdlib>
#include <new>
#include "config.pb.h"
#include "pb_decode.h"
#include "pb_encode.h"
static size_t allocations=0, outstanding=0;
void *operator new(size_t n) { void *p=std::malloc(n?n:1); if(!p)throw std::bad_alloc(); ++allocations; ++outstanding; return p; }
void operator delete(void *p) noexcept { if(p) { --outstanding; std::free(p); } }
void operator delete(void *p,size_t) noexcept { operator delete(p); }
#include "CoordinatedCdcStream.hpp"
#include "cobs/Print.h"
extern "C" {
#include "device/usbd_pvt.h"
void fixture_cdc_init(void);
unsigned fixture_cdc_pending(void);
}
#include "writer.inc"
mutex_t __usb_mutex;
namespace {
uint32_t clock_ms;
bool busy, completion, bus_pending, connected=true, drain=true, drop=false;
bool irq_under_lock=true;
unsigned skips, tasks, releases, slow_ms;
std::array<uint8_t,20000> wire;
size_t wire_size;
uint16_t transferred;
std::array<uint8_t,64> endpoint_bytes;
uint32_t ready_at;
void task() {
 assert(__usb_mutex.held);
 ++tasks;
 if(completion) {
   completion=false; busy=false;
   cdcd_xfer_cb(0,0x81,XFER_RESULT_SUCCESS,transferred);
 }
}
void host_poll() {
 if(!bus_pending || !drain || clock_ms<ready_at)return;
 if(!drop && transferred) {
   assert(wire_size+transferred<wire.size());
   std::memcpy(wire.data()+wire_size,endpoint_bytes.data(),transferred); wire_size+=transferred;
 }
 bus_pending=false; completion=true;
}
void irq() {
 if(mutex_try_enter(&__usb_mutex,nullptr)) { task(); mutex_exit(&__usb_mutex); }
 else ++skips;
}
}
void mutex_init(mutex_t *m) { m->held=false; }
bool mutex_enter_timeout_ms(mutex_t *m,uint32_t) { assert(__usb_mutex.held); assert(!m->held); m->held=true; return true; }
bool mutex_try_enter(mutex_t *m,uint32_t *) { if(m->held)return false; m->held=true; return true; }
void mutex_exit(mutex_t *m) { assert(m->held); m->held=false; ++releases; }
uint32_t millis() { return clock_ms; }
void delay(unsigned long ms) { clock_ms+=ms; if(!irq_under_lock) { host_poll(); irq(); } }
extern "C" void TinyUSB_Device_Task() {
 assert(!__usb_mutex.held); host_poll();
 if(mutex_try_enter(&__usb_mutex,nullptr)) { task(); mutex_exit(&__usb_mutex); }
}
void yield() {
 assert(!__usb_mutex.held); host_poll();
 if(mutex_try_enter(&__usb_mutex,nullptr)) { task(); mutex_exit(&__usb_mutex); }
 if(mutex_try_enter(&__usb_mutex,nullptr)) { tud_cdc_n_write_flush(0); mutex_exit(&__usb_mutex); }
}
extern "C" {
void tud_cdc_line_coding_cb(uint8_t,cdc_line_coding_t const*) {}
void tud_cdc_line_state_cb(uint8_t,bool,bool) {}
void tud_cdc_rx_cb(uint8_t) {}
void tud_cdc_rx_wanted_cb(uint8_t,char) {}
void tud_cdc_send_break_cb(uint8_t,uint16_t) {}
void tud_cdc_tx_complete_cb(uint8_t) {}
bool tud_mounted(void) { return connected; }
bool tud_suspended(void) { return false; }
bool usbd_edpt_claim(uint8_t,uint8_t ep) { if(ep!=0x81)return false; if(busy)return false; busy=true; return true; }
bool usbd_edpt_release(uint8_t,uint8_t ep) { if(ep==0x81)busy=false; return true; }
bool usbd_edpt_xfer(uint8_t,uint8_t ep,uint8_t *p,uint16_t n) {
 assert(__usb_mutex.held); if(ep!=0x81)return false;
 assert(n<=endpoint_bytes.size());
 if(n)std::memcpy(endpoint_bytes.data(),p,n);
 transferred=n; bus_pending=true; completion=false; ready_at=clock_ms+slow_ms;
 if(irq_under_lock) { host_poll(); irq(); }
 return true;
}
bool usbd_edpt_open(uint8_t,tusb_desc_endpoint_t const*) { return true; }
bool usbd_open_edpt_pair(uint8_t,uint8_t const*,uint8_t,uint8_t,uint8_t*,uint8_t*) { return true; }
bool tud_control_xfer(uint8_t,tusb_control_request_t const*,void*,uint16_t) { return true; }
bool tud_control_status(uint8_t,tusb_control_request_t const*) { return true; }
void dcd_int_disable(uint8_t) {}
void dcd_int_enable(uint8_t) {}
}
struct Dummy : Stream { size_t write(uint8_t) override { assert(false); return 0; } } dummy;
void reset() {
 assert(!__usb_mutex.held); __usb_mutex.held=true; fixture_cdc_init(); __usb_mutex.held=false; clock_ms=0; busy=completion=bus_pending=false;
 connected=drain=true; drop=false; wire_size=0; tasks=skips=releases=0; slow_ms=0;
}
void set_dtr(bool on) {
 tusb_control_request_t request{};
 request.bmRequestType=0x21;
 request.bRequest=CDC_REQUEST_SET_CONTROL_LINE_STATE;
 request.wValue=on ? 3 : 0;
 request.wIndex=0;
 assert(mutex_try_enter(&__usb_mutex,nullptr));
 assert(cdcd_control_xfer_cb(0,CONTROL_STAGE_SETUP,&request));
 assert(cdcd_control_xfer_cb(0,CONTROL_STAGE_ACK,&request));
 assert(tud_cdc_n_connected(0)==on);
 mutex_exit(&__usb_mutex);
}
std::vector<uint8_t> decode(const uint8_t *p,size_t n) {
 std::vector<uint8_t> decoded;
 for(size_t i=0;i<n;) {
   unsigned code=p[i++]; assert(code && i+code-1<=n);
   for(unsigned j=1;j<code;++j)decoded.push_back(p[i++]);
   if(code<255 && i<n)decoded.push_back(0);
 }
 return decoded;
}
class ConfiguratorBackend {
 public:
 using Command=uint8_t;
 CoordinatedCdcStream &_base_stream;
 bool &_profile_tx_needs_sync;
 ConfiguratorBackend(CoordinatedCdcStream &stream,bool &sync):_base_stream(stream),_profile_tx_needs_sync(sync){}
#if EXPECT_OLD
 bool WriteProfilePacket(Command,const uint8_t*,size_t);
#else
 bool WriteProfilePacket(Command,const uint8_t*,size_t,size_t *accepted=nullptr,bool *flushRequested=nullptr);
#endif
};
#include "packet.inc"
bool send(const std::vector<uint8_t>& body,bool &resync) {
 CoordinatedCdcStream stream(dummy); ConfiguratorBackend backend(stream,resync);
 size_t before=allocations; bool ok=backend.WriteProfilePacket(9,body.data(),body.size()); assert(allocations==before); return ok;
}
void settle() { for(unsigned i=0;i<500 && (busy||fixture_cdc_pending());++i) { yield(); ++clock_ms; } }
void require_frame(const std::vector<uint8_t>& body,size_t start=0) {
 assert(wire_size>start && wire[wire_size-1]==0);
 size_t begin=wire_size-1; while(begin>start && wire[begin-1]!=0)--begin;
 auto decoded=decode(wire.data()+begin,wire_size-1-begin);
 assert(decoded.size()==body.size()+1 && decoded[0]==9);
 assert(std::equal(body.begin(),body.end(),decoded.begin()+1));
}
int main(int argc,char**argv) {
 std::vector<size_t> sizes={1,63,64,65,255,256,257,512,3079,4096,8191};
 std::vector<std::vector<uint8_t>> payloads;
 for(int i=1;i<argc;++i) { std::ifstream f(argv[i],std::ios::binary); assert(f); payloads.emplace_back(std::istreambuf_iterator<char>(f),std::istreambuf_iterator<char>()); }
 for(const auto &body:payloads) {
   static ProfileStoreResponse response;
   static uint8_t encoded[8192];
   pb_istream_t input=pb_istream_from_buffer(body.data(),body.size());
   assert(pb_decode(&input,ProfileStoreResponse_fields,&response));
   pb_ostream_t output=pb_ostream_from_buffer(encoded,sizeof(encoded));
   assert(pb_encode(&output,ProfileStoreResponse_fields,&response));
   assert(output.bytes_written==body.size() && std::equal(body.begin(),body.end(),encoded));
 }
 // The delimiter may be submitted while its endpoint is still in flight.
 // Success means bounded submission; the host only accepts after completion.
 {
   reset(); slow_ms=5; bool sync=false; std::vector<uint8_t> body(1,0x42);
   assert(send(body,sync));
#if EXPECT_OLD
   assert(wire_size==0 && fixture_cdc_pending()==4);
#else
   assert(bus_pending && fixture_cdc_pending()==0 && wire_size==3 && wire[wire_size-1]!=0);
#endif
   settle(); require_frame(body);
 }
 unsigned failures=0; size_t first=0;
 for(size_t n:sizes) {
   reset(); irq_under_lock=true; bool sync=false;
   std::vector<uint8_t> body(n,0x42); if(n>10)body[n/2]=0;
   bool ok=send(body,sync); settle();
   if(!ok) { ++failures; if(!first)first=n; assert(clock_ms>=2000); }
   else require_frame(body);
   std::printf("payload=%zu ok=%d wire=%zu skipped_irq=%u task_calls=%u\n",n,ok,wire_size,skips,tasks);
 }
 size_t first_sweep_failure=0;
 for(size_t n=1;n<=600;++n) {
   reset(); bool sync=false; std::vector<uint8_t> body(n,0x42);
   bool ok=send(body,sync); settle();
   if(!ok && !first_sweep_failure)first_sweep_failure=n;
#if !EXPECT_OLD
   assert(ok); require_frame(body);
#endif
 }
 std::printf("all_nonzero_payload_sweep_1_to_600_first_failure=%zu\n",first_sweep_failure);
#if EXPECT_OLD
 assert(first_sweep_failure==317);
#else
 assert(first_sweep_failure==0);
#endif
 for(const auto& body:payloads) {
   reset(); bool sync=false; bool ok=send(body,sync); settle();
#if EXPECT_OLD
   assert(ok == (body.size()<320));
#else
   assert(ok); require_frame(body);
#endif
   std::printf("actual_pb_payload=%zu ok=%d wire=%zu\n",body.size(),ok,wire_size);
 }
#if EXPECT_OLD
 assert(failures && first==512);
 std::puts("old_cdc_deferred_completion_negative=PASS first_tested_payload_failure=512");
#else
 assert(!failures);
 for(unsigned mode=0;mode<2;++mode) {
   reset(); bool sync=false; std::vector<uint8_t> body(8191,0);
   if(mode)for(size_t i=0;i<body.size();i+=2)body[i]=0x42;
   assert(send(body,sync)); settle(); require_frame(body);
 }
 // Keep firmware FIFO state across requests; the host consumes completed frames.
 reset(); bool sync=false; size_t heap_before=outstanding;
 for(unsigned i=0;i<1024;++i) {
   const auto &body=payloads[2+i%(payloads.size()-2)];
   wire_size=0; assert(send(body,sync)); settle(); require_frame(body);
   if(i && i%51==0) {
     unsigned pending=fixture_cdc_pending(); bool was_busy=busy;
     set_dtr(false); set_dtr(true);
     assert(fixture_cdc_pending()==pending && busy==was_busy);
     wire_size=0; assert(send(body,sync)); settle(); require_frame(body);
   } // twenty process-style DTR close/open cycles; driver state remains intact
   if(i%7==0) {
     for(const auto &mixed:payloads) { wire_size=0; assert(send(mixed,sync)); settle(); require_frame(mixed); }
   }
   if(i%127==0) { // Complete TX but host application discards one response.
     wire_size=0; drop=true; assert(send(body,sync)); settle(); assert(wire_size==0); drop=false;
     assert(send(payloads[0],sync)); settle(); require_frame(payloads[0]);
   }
   if(i%131==0) { // Host stops draining; recover retained partial frame on same stream.
     wire_size=0; drain=false; uint32_t start=clock_ms;
     assert(!send(body,sync) && sync && clock_ms-start==2000);
     drain=true; settle();
     assert(send(payloads[0],sync)); settle(); require_frame(payloads[0]);
   }
 }
 assert(outstanding==heap_before);
 for(bool adversarial: {false,true}) {
   reset(); irq_under_lock=adversarial; slow_ms=3; sync=false;
   assert(send(payloads[3],sync)); settle(); require_frame(payloads[3]);
 }
 reset(); connected=false; sync=false;
 assert(!send(payloads[2],sync) && clock_ms==2000);
 std::puts("current_cdc_progress=PASS repeated_profile_reads=1024 mixed_rounds=147 dtr_reconnects=20 dropped_responses=9 stalled_host_recovery=8 slow_reader_ms_per_packet=3 disconnected_bound_ms=2000 no_tx_allocations=true no_retained_host_allocation_growth=true actual_nanopb_reencode=true");
#endif
}
