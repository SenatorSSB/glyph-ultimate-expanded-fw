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
static size_t allocations=0,outstanding=0;
void *operator new(size_t n) {void*p=std::malloc(n?n:1);if(!p)throw std::bad_alloc();++allocations;++outstanding;return p;}
void operator delete(void*p) noexcept {if(p){--outstanding;std::free(p);}}
void operator delete(void*p,size_t) noexcept {operator delete(p);}
#include "CoordinatedCdcStream.hpp"
#include "core/ProfileStoreRxDiagnostics.hpp"
#include "cobs/Stream.h"
#include "cobs/Print.h"
extern "C" {
#include "device/usbd_pvt.h"
void fixture_cdc_init(void);
unsigned fixture_rx_pending(void);
}
mutex_t __usb_mutex;
namespace {
uint32_t clock_ms,ready_at,slow_ms;
bool busy,completion,armed,adversarial,connected=true,prime,separate_delimiter=false;
uint8_t *endpoint;
uint16_t endpoint_capacity,transferred;
const uint8_t *host_bytes;
size_t host_size,host_sent,host_limit,fragment=64;
unsigned skips,tasks,processed,claims,raw_consumed;
void irq();
void host_poll() {
 if(!armed || completion || host_sent>=host_limit || clock_ms<ready_at)return;
 size_t n=std::min({size_t(endpoint_capacity),fragment,host_limit-host_sent});
 if(separate_delimiter && host_sent+n==host_size && n>1)--n; // delimiter arrives separately
 std::memcpy(endpoint,host_bytes+host_sent,n);host_sent+=n;
 transferred=n;armed=false;completion=true;
}
void task() {
 assert(__usb_mutex.held);++tasks;
 // Model usbd's completion dequeue clearing endpoint state before cdcd callback.
 // The event only enters the RX FIFO here, never at host write/USB arrival.
 unsigned bound=0;
 while(completion) {
   assert(++bound<10000);completion=false;busy=false;++processed;
   cdcd_xfer_cb(0,0x02,XFER_RESULT_SUCCESS,transferred);
   if(prime && fixture_rx_pending()<256)host_poll();
 }
}
void irq() {
 if(mutex_try_enter(&__usb_mutex,nullptr)){task();mutex_exit(&__usb_mutex);}
 else ++skips;
}
}
void mutex_init(mutex_t*m){m->held=false;}
bool mutex_enter_timeout_ms(mutex_t*m,uint32_t){assert(__usb_mutex.held);assert(!m->held);m->held=true;return true;}
bool mutex_try_enter(mutex_t*m,uint32_t*){if(m->held)return false;m->held=true;return true;}
void mutex_exit(mutex_t*m){assert(m->held);m->held=false;}
uint32_t millis(){return clock_ms;}
void delay(unsigned long ms){assert(!__usb_mutex.held);clock_ms+=ms;if(!adversarial){host_poll();irq();}}
extern "C" void TinyUSB_Device_Task(){assert(!__usb_mutex.held);host_poll();if(mutex_try_enter(&__usb_mutex,nullptr)){task();mutex_exit(&__usb_mutex);}}
void yield(){TinyUSB_Device_Task();}
extern "C" {
void tud_cdc_line_coding_cb(uint8_t,cdc_line_coding_t const*){}
void tud_cdc_line_state_cb(uint8_t,bool,bool){}
void tud_cdc_rx_cb(uint8_t){}
void tud_cdc_rx_wanted_cb(uint8_t,char){}
void tud_cdc_send_break_cb(uint8_t,uint16_t){}
void tud_cdc_tx_complete_cb(uint8_t){}
bool tud_mounted(void){return connected;}
bool tud_suspended(void){return false;}
bool usbd_edpt_claim(uint8_t,uint8_t ep){assert(__usb_mutex.held);if(ep!=0x02||busy)return false;busy=true;++claims;return true;}
bool usbd_edpt_release(uint8_t,uint8_t ep){if(ep==0x02)busy=false;return true;}
bool usbd_edpt_xfer(uint8_t,uint8_t ep,uint8_t*p,uint16_t n){
 assert(__usb_mutex.held);if(ep!=0x02)return false;assert(n==64);
 endpoint=p;endpoint_capacity=n;armed=true;ready_at=clock_ms+slow_ms;
 if(adversarial&&!prime){host_poll();if(completion)irq();}
 return true;
}
bool usbd_edpt_open(uint8_t,tusb_desc_endpoint_t const*){return true;}
bool usbd_open_edpt_pair(uint8_t,uint8_t const*,uint8_t,uint8_t,uint8_t*,uint8_t*){return true;}
bool tud_control_xfer(uint8_t,tusb_control_request_t const*,void*,uint16_t){return true;}
bool tud_control_status(uint8_t,tusb_control_request_t const*){return true;}
void dcd_int_disable(uint8_t){}
void dcd_int_enable(uint8_t){}
}
struct Dummy:Stream {size_t write(uint8_t)override{assert(false);return 0;}}dummy;
class ConfiguratorBackend {
public:
 CoordinatedCdcStream _coordinated_stream{dummy};
 CoordinatedCdcStream &_base_stream{_coordinated_stream};
 ProfileStoreRxDiagnostics _rx;
 packetio::COBSStream _in{_coordinated_stream};
 bool _packet_timed_out=false;
 size_t ReadPacket(uint8_t*,size_t);
};
#include "reader.inc"
struct Sink:Print {
 std::vector<uint8_t> bytes;
 size_t write(uint8_t b)override{bytes.push_back(b);return 1;}
};
std::vector<uint8_t> encode(const std::vector<uint8_t>&body){
 Sink sink;packetio::COBSPrint out(sink);assert(out.write(uint8_t(9))==1);assert(out.write(body.data(),body.size())==body.size());assert(out.end());return sink.bytes;
}
void reset(const std::vector<uint8_t>&wire,size_t limit=SIZE_MAX,bool initial=true){
 assert(!__usb_mutex.held);host_bytes=wire.data();host_size=wire.size();host_limit=std::min(limit,wire.size());host_sent=0;
 busy=completion=armed=false;clock_ms=ready_at=0;tasks=skips=processed=claims=raw_consumed=0;
 prime=true;__usb_mutex.held=true;fixture_cdc_init();__usb_mutex.held=false;
 if(initial){host_poll();TinyUSB_Device_Task();}prime=false;
}
void set_dtr(bool on){
 tusb_control_request_t r{};r.bmRequestType=0x21;r.bRequest=CDC_REQUEST_SET_CONTROL_LINE_STATE;r.wValue=on?3:0;
 assert(mutex_try_enter(&__usb_mutex,nullptr));assert(cdcd_control_xfer_cb(0,CONTROL_STAGE_SETUP,&r));assert(cdcd_control_xfer_cb(0,CONTROL_STAGE_ACK,&r));assert(tud_cdc_n_connected(0)==on);mutex_exit(&__usb_mutex);
}
std::array<uint8_t,8192> received;
size_t receive(ConfiguratorBackend&backend){
 const uint32_t start=clock_ms;
 int command=-1;
 while(clock_ms-start<5000u){TinyUSB_Device_Task();command=backend._in.read();if(command>=0)break;delay(1);}
 assert(command==9);
 size_t before=allocations;auto n=backend.ReadPacket(received.data(),received.size());assert(allocations==before);return n;
}
bool attempt(const std::vector<uint8_t>&body,bool protobuf=false,bool log=false){
 auto wire=encode(body);ConfiguratorBackend backend;reset(wire);auto n=receive(backend);
 bool ok=!backend._packet_timed_out&&n==body.size()&&std::equal(body.begin(),body.end(),received.begin());
 if(ok){assert(host_sent==wire.size());assert(fixture_rx_pending()==0);}
 if(ok&&protobuf){static ProfileStoreRequest request;request=ProfileStoreRequest_init_default;pb_istream_t in=pb_istream_from_buffer(received.data(),n);assert(pb_decode(&in,ProfileStoreRequest_fields,&request));assert(!in.bytes_left);}
 if(log)std::printf("body=%zu wire=%zu ok=%d timeout=%d ms=%u fifo=%u endpoint_completion=%d endpoint_bytes=%u host_sent=%zu host_pending=%zu raw_consumed=%zu skipped_irq=%u task_passes=%u\n",body.size(),wire.size(),ok,backend._packet_timed_out,clock_ms,fixture_rx_pending(),completion,transferred,host_sent,host_size-host_sent,host_sent-(completion?transferred:0)-fixture_rx_pending(),skips,tasks);
 return ok;
}
void live_receive(ConfiguratorBackend&backend,const std::vector<uint8_t>&body){
 auto wire=encode(body);assert(!completion&&fixture_rx_pending()==0);
 host_bytes=wire.data();host_size=host_limit=wire.size();host_sent=0;
 auto n=receive(backend);assert(!backend._packet_timed_out&&n==body.size());
 assert(std::equal(body.begin(),body.end(),received.begin()));
 static ProfileStoreRequest q;q=ProfileStoreRequest_init_default;pb_istream_t in=pb_istream_from_buffer(received.data(),n);assert(pb_decode(&in,ProfileStoreRequest_fields,&q)&&!in.bytes_left);
 assert(host_sent==wire.size()&&!completion&&fixture_rx_pending()==0);
}
int main(int argc,char**argv){
 std::vector<std::vector<uint8_t>> payloads;
 for(int i=1;i<argc;++i){std::ifstream f(argv[i],std::ios::binary);assert(f);payloads.emplace_back(std::istreambuf_iterator<char>(f),std::istreambuf_iterator<char>());}
 adversarial=true;slow_ms=0;
 size_t first_body=0,first_wire=0;
 for(size_t n=1;n<=600;++n){std::vector<uint8_t>body(n,0x42);bool ok=attempt(body);if(!ok&&!first_body){first_body=n;first_wire=encode(body).size();}}
 std::printf("nonzero_sweep_first_failure_body=%zu wire=%zu\n",first_body,first_wire);
#if EXPECT_OLD
 assert(first_body==253 && first_wire==257);
#else
 assert(first_body==0);
#endif
 for(size_t n:{1u,63u,64u,65u,127u,128u,253u,254u,255u,256u,257u,512u,8191u}){
   std::vector<uint8_t>body(n,0x42);bool ok=attempt(body,false,true);
#if !EXPECT_OLD
   assert(ok);
#endif
 }
 for(const auto&body:payloads){bool ok=attempt(body,true,true);
#if !EXPECT_OLD
 assert(ok);
#else
 if(body.size()>512)assert(!ok);
#endif
 }
#if EXPECT_OLD
 // No lost completion schedule: the exact old parser handles these identical bytes.
 adversarial=false;for(const auto&body:payloads)assert(attempt(body,true));
 std::puts("old_rx_negative=PASS ideal_receiver_control=PASS");
#else
 std::vector<size_t> large;for(size_t i=0;i<payloads.size();++i){static ProfileStoreRequest q;q=ProfileStoreRequest_init_default;pb_istream_t in=pb_istream_from_buffer(payloads[i].data(),payloads[i].size());assert(pb_decode(&in,ProfileStoreRequest_fields,&q));if(payloads[i].size()>512&&(q.operation==PROFILE_STORE_UPDATE||q.operation==PROFILE_STORE_CREATE))large.push_back(i);}assert(!large.empty());
 ConfiguratorBackend live;std::vector<uint8_t> empty;reset(empty);
 const size_t heap_before=outstanding;
 for(unsigned i=0;i<1024;++i){
   if(i&&i%51==0){set_dtr(false);set_dtr(true);}
   const auto&body=payloads[large[i%large.size()]];live_receive(live,body);
   if(i%11==0)for(size_t j=1;j<9;++j)live_receive(live,payloads[j]);
   if(i<84)live_receive(live,payloads[6]);
 }
 assert(outstanding==heap_before);
 for(unsigned mode=0;mode<3;++mode){std::vector<uint8_t>body(8191,0);if(mode)for(size_t i=0;i<body.size();i+=(mode==1?2:254))body[i]=0x42;assert(attempt(body));}
 separate_delimiter=true;for(size_t chunk:{1u,3u,63u,64u}){fragment=chunk;slow_ms=chunk==1?0:3;assert(attempt(payloads[0],true,true));}fragment=1;slow_ms=1;assert(attempt(payloads[0],true,true));
 // Continuous progress cannot extend the whole-frame deadline indefinitely.
 auto too_slow=encode(std::vector<uint8_t>(8191,0));ConfiguratorBackend bounded;reset(too_slow);auto slow_n=receive(bounded);assert(!slow_n&&bounded._packet_timed_out&&bounded._rx.elapsed==5000);
 fragment=64;slow_ms=0;
 // Process reconnects toggle real CDC DTR state; each subsequent wire decodes.
 for(unsigned i=0;i<20;++i){auto wire=encode(payloads[0]);ConfiguratorBackend backend;reset(wire);set_dtr(false);set_dtr(true);auto n=receive(backend);assert(n==payloads[0].size()&&!backend._packet_timed_out);assert(std::equal(payloads[0].begin(),payloads[0].end(),received.begin()));}
 // Adjacent frames can share a64-byte cache; next() must retain the following request.
 {auto joined=encode(payloads[0]);auto tail=encode(payloads[2]);joined.insert(joined.end(),tail.begin(),tail.end());ConfiguratorBackend adjacent;reset(joined);
 auto first=receive(adjacent);assert(first==payloads[0].size()&&!adjacent._packet_timed_out);assert(std::equal(payloads[0].begin(),payloads[0].end(),received.begin()));
 auto second=receive(adjacent);assert(second==payloads[2].size()&&!adjacent._packet_timed_out);assert(std::equal(payloads[2].begin(),payloads[2].end(),received.begin()));assert(host_sent==joined.size());}
 // Truncated frame, total deadline, then delayed remainder+delimiter+next frame.
 auto wire=encode(payloads[0]);auto next=encode(payloads[1]);size_t first_size=wire.size();wire.insert(wire.end(),next.begin(),next.end());
 ConfiguratorBackend backend;reset(wire,200);auto n=receive(backend);assert(n==0&&backend._packet_timed_out&&clock_ms==5000);
 host_limit=wire.size();
 // Normal main loop service while PacketIO's next() skips to old delimiter.
 int command=-1;for(unsigned i=0;i<10000&&command<0;++i){TinyUSB_Device_Task();command=backend._in.read();if(command<0)delay(1);}assert(command==9);
 n=backend.ReadPacket(received.data(),received.size());assert(!backend._packet_timed_out&&n==payloads[1].size());assert(std::equal(payloads[1].begin(),payloads[1].end(),received.begin()));assert(host_sent==wire.size());(void)first_size;
 std::puts("current_rx_progress=PASS mutation_receptions=1024 retained_session_dtr_cycles=20 additional_dtr_cycles=20 read_request_receptions=84 fragmented=1,3,63,64 delimiter_separate=true partial_timeout_resync=true adjacent_frame_cache_ownership=true no_frame_reader_allocations=true no_retained_allocation_growth=true total_deadline_with_continuous_progress=5000");
#endif
}
