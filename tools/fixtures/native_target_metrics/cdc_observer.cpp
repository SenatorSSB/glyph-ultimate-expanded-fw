// Actual pinned CDC/FIFO + actual Service/metrics; endpoint/IRQ scheduling only
// is a deterministic host double. No surrogate observer or CDC algorithm.
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>
#include <algorithm>
#include "HAL/pico/src/core/NativeTargetMetrics.cpp"
#include "core/RuntimeIdentityService.hpp"
extern "C" {
#include "device/usbd_pvt.h"
void fixture_cdc_init(void);
unsigned fixture_rx_pending(void);
unsigned fixture_tx_pending(void);
}
mutex_t __usb_mutex;
namespace {
bool rx_busy,tx_busy,rx_event,tx_event,inject;
uint8_t *rx_endpoint;uint16_t rx_length,tx_length;
std::vector<uint8_t> received,pending_input;
unsigned skipped,tasks,reads,raw_calls;
void task() {
    assert(__usb_mutex.held);++tasks;
    if(rx_event) {rx_event=false;rx_busy=false;cdcd_xfer_cb(0,0x02,XFER_RESULT_SUCCESS,rx_length);}
    if(tx_event) {tx_event=false;tx_busy=false;cdcd_xfer_cb(0,0x81,XFER_RESULT_SUCCESS,tx_length);}
}
void irq() {
    if(mutex_try_enter(&__usb_mutex,nullptr)) {task();mutex_exit(&__usb_mutex);}
    else ++skipped;
}
void arrival(const std::vector<uint8_t> &bytes) {
    assert(rx_busy&&!rx_event&&bytes.size()<=64);rx_length=bytes.size();
    std::memcpy(rx_endpoint,bytes.data(),rx_length);rx_event=true;irq();
}
void post_loop_service() {
    // Existing main.cpp loop()->__loop()->yield()->TinyUSB_Device_Task order.
    assert(!__usb_mutex.held);
    if(mutex_try_enter(&__usb_mutex,nullptr)) {task();mutex_exit(&__usb_mutex);}
}
struct PoisonSerial {
    int available(){++raw_calls;assert(false);return 0;}
    int read(){++raw_calls;assert(false);return -1;}
    int availableForWrite(){++raw_calls;assert(false);return 0;}
    size_t write(const uint8_t*,size_t){++raw_calls;assert(false);return 0;}
} serial;
std::vector<uint8_t> request(bool diagnostic) {
    std::vector<uint8_t> r(16);std::memcpy(r.data(),diagnostic?native_metrics::kMagic:runtime_identity::kMagic,4);
    r[4]=1;r[5]=1;r[6]=16;r[8]=42;return r;
}
void poll(runtime_identity::Service &s,uint32_t now=0) {
    CommunicationBackend backend;Config config;ProfileStore store;Ultimate ultimate;
    const unsigned before=reads;s.Poll(serial,&backend,config,store,ultimate,now);
    assert(reads-before<=32&&!__usb_mutex.held&&raw_calls==0);
}
void reset() {
    assert(!__usb_mutex.held);rx_busy=tx_busy=rx_event=tx_event=inject=false;
    received.clear();pending_input.clear();skipped=tasks=reads=raw_calls=0;
    __usb_mutex.held=true;fixture_cdc_init();__usb_mutex.held=false;
    native_metrics::DiscardRequest();native_metrics::capture_sequence=native_metrics::last_tx_ms=0;
}
void settle() {
    for(unsigned i=0;i<8;++i) {
        post_loop_service();assert(mutex_try_enter(&__usb_mutex,nullptr));
        tud_cdc_n_write_flush(0);mutex_exit(&__usb_mutex);
    }
    assert(!tx_event&&fixture_tx_pending()==0);
}
}
void mutex_init(mutex_t *m){m->held=false;}
bool mutex_try_enter(mutex_t *m,uint32_t*){if(m->held)return false;m->held=true;return true;}
void mutex_exit(mutex_t *m){assert(m->held);m->held=false;}
bool mutex_enter_timeout_ms(mutex_t *m,uint32_t) {
    // A task IRQ must never enter a FIFO/endpoint lock owned by this pass.
    assert(__usb_mutex.held&&!m->held);m->held=true;return true;
}
extern "C" {
void tud_cdc_line_coding_cb(uint8_t,cdc_line_coding_t const*){}
void tud_cdc_line_state_cb(uint8_t,bool,bool){}
void tud_cdc_rx_cb(uint8_t){}
void tud_cdc_rx_wanted_cb(uint8_t,char){}
void tud_cdc_send_break_cb(uint8_t,uint16_t){}
void tud_cdc_tx_complete_cb(uint8_t){}
bool tud_mounted(void){return true;}
bool tud_suspended(void){return false;}
bool usbd_edpt_claim(uint8_t,uint8_t ep) {
    assert(__usb_mutex.held);
    if(ep==0x02) {
        ++reads;
        if(inject) {inject=false;arrival(pending_input);} // no new hardware event later
        if(rx_busy)return false;rx_busy=true;return true;
    }
    assert(ep==0x81);irq(); // adversarial preemption while TX locks are live
    if(tx_busy)return false;tx_busy=true;return true;
}
bool usbd_edpt_release(uint8_t,uint8_t ep){if(ep==0x02)rx_busy=false;else tx_busy=false;return true;}
bool usbd_edpt_xfer(uint8_t,uint8_t ep,uint8_t *p,uint16_t n) {
    assert(__usb_mutex.held&&n<=64);
    if(ep==0x02){rx_endpoint=p;return true;}
    assert(ep==0x81&&!tx_event);received.insert(received.end(),p,p+n);tx_length=n;tx_event=true;irq();return true;
}
bool usbd_edpt_open(uint8_t,tusb_desc_endpoint_t const*){return true;}
bool usbd_open_edpt_pair(uint8_t,uint8_t const*,uint8_t,uint8_t,uint8_t*,uint8_t*){return true;}
bool tud_control_xfer(uint8_t,tusb_control_request_t const*,void*,uint16_t){return true;}
bool tud_control_status(uint8_t,tusb_control_request_t const*){return true;}
void dcd_int_disable(uint8_t){}
void dcd_int_enable(uint8_t){}
}
uint32_t NativeMetricHostNow(){return 1;}
bool NativeMetricHostUptime(uint64_t &n){n=100;return true;}
uint32_t NativeMetricHostSaveIrq(){return 0;}
void NativeMetricHostRestoreIrq(uint32_t){}
uint32_t NativeMetricHostSp(){return 0;}
uint32_t NativeMetricHostWord(uint32_t){return 0;}
int main() {
    reset();runtime_identity::Service service;
    // Busy admission consumes nothing and does not wait.
    arrival(request(true));assert(fixture_rx_pending()==16);
    __usb_mutex.held=true;CommunicationBackend backend;Config config;ProfileStore store;Ultimate ultimate;
    service.Poll(serial,&backend,config,store,ultimate,0);__usb_mutex.held=false;
    assert(fixture_rx_pending()==16&&received.empty());
    poll(service);settle();assert(received.size()==160&&received[0]==0xd7&&skipped>0);
    reset();service={};arrival(request(false));poll(service);settle();assert(received.size()==72&&received[0]==0xa5);
    // A malformed pass returns without TX. The OUT completion that arrived
    // under its guard progresses through existing post-loop service alone.
    reset();service={};arrival(std::vector<uint8_t>(16,0));pending_input=request(true);inject=true;
    poll(service);assert(rx_event&&received.empty()&&fixture_rx_pending()==0&&skipped>0);
    const unsigned before=tasks;post_loop_service();assert(tasks==before+1&&!rx_event&&fixture_rx_pending()==16);
    poll(service);settle();assert(received.size()==160);
    // A rate-dropped request likewise cannot strand the next OUT completion.
    arrival(request(true));pending_input=request(false);inject=true;received.clear();poll(service,999);
    assert(rx_event&&received.empty());post_loop_service();poll(service,999);settle();assert(received.size()==72);
    std::puts("PASS actual pinned CDC/FIFO observer: try-only guard, TX preemption defers, busy/no-response/rate-drop RX progresses via existing post-loop task; raw Serial never called");
}
