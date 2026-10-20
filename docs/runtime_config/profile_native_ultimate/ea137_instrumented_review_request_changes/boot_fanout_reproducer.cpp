#include <cassert>
#include <cstdio>
#include <fstream>
#include <cstring>
#include <vector>
#include <deque>
#include <string>
#include <algorithm>
#include <climits>
#include "core/NativeTargetMetrics.hpp"
// Compile the actual implementation in this TU, exposing its fixed internal
// state for boundary injection. No surrogate parser/statistic/scan algorithm.
#include "HAL/pico/src/core/NativeTargetMetrics.cpp"
#include "core/RuntimeIdentityService.hpp"
namespace {
uint32_t clock_now=0, own_core=0, irq_state=0, irq_saves=0, irq_restores=0, word_reads=0;
uint64_t uptime=1000000;bool coherent=true;
uint32_t memory[2][512];
void reset() {
    clock_now=0;uptime=1000000;coherent=true;irq_state=0;irq_saves=irq_restores=word_reads=0;
    std::memset(native_metrics::statistics,0,sizeof(native_metrics::statistics));
    std::memset(native_metrics::overhead,0,sizeof(native_metrics::overhead));
    native_metrics::run_flags=native_metrics::native_generation=native_metrics::capture_sequence=native_metrics::last_tx_ms=0;
    native_metrics::DiscardRequest();
    for(unsigned core=0;core<2;++core) {
        auto &s=glyph_native_metric_scans[core];s={};const uint32_t bottom=0x100000+core*0x1000;
        s.bottom=bottom;s.usable_bottom=bottom+32;s.top=bottom+2048;s.initial_sp=s.minimum_sp=s.top-32;
        s.lowest_changed=s.top;s.cursor=s.usable_bottom;s.flags=25;
        for(auto &word:memory[core])word=0xade175c3;
        for(unsigned i=504;i<512;++i)memory[core][i]=0x12345678;
        auto &m=native_metrics::mailboxes[core];m.version.store(0);m.used_sp.store(0);m.generation.store(0);m.max_chunk.store(0);m.flags.store(0);
    }
}
std::vector<uint8_t> request(bool diagnostic,uint64_t token=42) {
    std::vector<uint8_t> bytes(16);const uint8_t *magic=diagnostic?native_metrics::kMagic:runtime_identity::kMagic;
    std::memcpy(bytes.data(),magic,4);bytes[4]=1;bytes[5]=1;bytes[6]=16;
    runtime_identity::WriteLE(bytes.data()+8,token,8);return bytes;
}
struct Wire {
    std::deque<uint8_t> rx;std::vector<uint8_t> tx;int room=1024;unsigned reads=0,writes=0;
    int available()const{return rx.size();}int availableForWrite()const{return room;}
    int read(){++reads;if(rx.empty())return -1;int b=rx.front();rx.pop_front();return b;}
    size_t write(const uint8_t *p,size_t n){++writes;tx.insert(tx.end(),p,p+n);return n;}
    void add(const std::vector<uint8_t>&v){rx.insert(rx.end(),v.begin(),v.end());}
};
void poll(runtime_identity::Service &service,Wire &wire,uint32_t now=0) {
    CommunicationBackend backend;Config config;ProfileStore store;Ultimate ultimate;
    const unsigned before=wire.reads;service.Poll(wire,&backend,config,store,ultimate,now);assert(wire.reads-before<=32);
}
void complete_measurements() {
    native_metrics::Calibrate();native_metrics::Calibrate();assert(native_metrics::statistics[2].count==16);
    clock_now=100;native_metrics::RecordActivation(70,90,1,true,false);
    clock_now=150;native_metrics::RecordFrame(120,140,1,1);
    for(unsigned core=0;core<2;++core) {own_core=core;for(unsigned i=0;i<32;++i) {const auto before=word_reads;native_metrics::ServiceCore(core);assert(word_reads-before<=16);assert(irq_state==0);}}
    assert(irq_saves==64&&irq_restores==64);
}
void parser_tests() {
    reset();runtime_identity::Service service;Wire wire;wire.add(request(true));poll(service,wire);
    assert(wire.tx.size()==160&&wire.tx[16]==1&&wire.writes==1);
    wire.tx.clear();wire.add(request(true));poll(service,wire,999);assert(wire.tx.empty());
    wire.add(request(true));poll(service,wire,1000);assert(wire.tx.size()==160);
    reset();service={};wire={};wire.add(request(true));wire.add(request(false));poll(service,wire);
    assert(wire.tx.size()==72&&wire.tx[0]==0xa5&&wire.writes==1); // identity priority
    reset();service={};wire={};wire.add(request(true));wire.add(request(true,99));poll(service,wire);assert(wire.tx.empty());
    reset();service={};wire={};wire.rx={0xd7,0x47};wire.add(request(false));poll(service,wire);assert(wire.tx.size()==72);
    reset();service={};wire={};wire.add(request(true));wire.rx.push_back(0xa5);poll(service,wire);assert(wire.tx.empty());
    const auto identity=request(false);wire.add(std::vector<uint8_t>(identity.begin()+1,identity.end()));poll(service,wire);assert(wire.tx.size()==72);
    for(unsigned field:{4u,5u,6u,8u}) {
        reset();service={};wire={};auto bad=request(true);bad[field]=field==8?0:99;wire.add(bad);wire.add(request(false));poll(service,wire);assert(wire.tx.size()==72);
    }
    reset();service={};wire={};const auto diagnostic=request(true);wire.add(std::vector<uint8_t>(diagnostic.begin(),diagnostic.begin()+4));poll(service,wire);
    wire.add(request(false));poll(service,wire,250);assert(wire.tx.size()==72);
    reset();service={};wire={};wire.add(request(false,0x4d4e47d7));poll(service,wire);assert(wire.tx.size()==72); // diagnostic magic opaque in identity token
    reset();service={};wire={};wire.add(request(true,0x495247a5));poll(service,wire);assert(wire.tx.size()==160&&runtime_identity::ReadLE(wire.tx.data()+8,8)==0x495247a5);
    reset();service={};wire={};wire.room=191;wire.add(request(true));poll(service,wire);assert(wire.tx.empty());wire.room=192;wire.add(request(true));poll(service,wire);assert(wire.tx.size()==160);
    reset();service={};wire={};wire.add(request(true));for(unsigned i=0;i<17;++i)wire.rx.push_back(1);poll(service,wire);assert(wire.tx.empty()&&wire.reads==32);poll(service,wire);assert(wire.tx.empty());
}
}
uint32_t NativeMetricHostNow(){return clock_now++;}
bool NativeMetricHostUptime(uint64_t &out){out=uptime;return coherent;}
uint32_t NativeMetricHostSaveIrq(){++irq_saves;uint32_t old=irq_state;irq_state=1;return old;}
void NativeMetricHostRestoreIrq(uint32_t old){++irq_restores;irq_state=old;}
uint32_t NativeMetricHostSp(){return glyph_native_metric_scans[own_core].top-64;}
uint32_t NativeMetricHostWord(uint32_t address){++word_reads;assert(irq_state==1);assert(address>=glyph_native_metric_scans[own_core].usable_bottom&&address<glyph_native_metric_scans[own_core].top);return memory[own_core][(address-glyph_native_metric_scans[own_core].bottom)/4];}
int existing_fixture_main(int argc,char **argv) {
    parser_tests();
    reset();complete_measurements();runtime_identity::Service service;Wire wire;wire.add(request(true));poll(service,wire);
    assert(wire.tx.size()==160&&wire.tx[16]==0&&runtime_identity::ReadLE(wire.tx.data()+18,2)==511);
    assert(runtime_identity::ReadLE(wire.tx.data()+48,4)==1&&runtime_identity::ReadLE(wire.tx.data()+52,4)==20);
    assert(runtime_identity::ReadLE(wire.tx.data()+108,2)>=32&&runtime_identity::ReadLE(wire.tx.data()+112,4)>=1);
    assert(native_metrics::statistics[2].count==16);
    if(argc==2) {std::ofstream output(argv[1],std::ios::binary);output.write(reinterpret_cast<const char *>(wire.tx.data()),wire.tx.size());}
    native_metrics::Statistic saturated{UINT32_MAX,2,3,UINT32_MAX,UINT32_MAX};native_metrics::Accumulate(saturated,10,0);
    assert(saturated.count==UINT32_MAX&&saturated.sum_high==UINT32_MAX&&saturated.sum_low==UINT32_MAX&&(native_metrics::run_flags&3)==3);
    reset();complete_measurements();coherent=false;service={};wire={};wire.add(request(true));poll(service,wire);
    assert(wire.tx[16]==2&&runtime_identity::ReadLE(wire.tx.data()+156,4)==0&&(runtime_identity::ReadLE(wire.tx.data()+154,2)&64));
    reset();complete_measurements();native_metrics::mailboxes[1].version.store(3);service={};wire={};wire.add(request(true));poll(service,wire);
    assert(wire.tx[16]==1&&runtime_identity::ReadLE(wire.tx.data()+124,8)==0&&runtime_identity::ReadLE(wire.tx.data()+132,4)==0&&(runtime_identity::ReadLE(wire.tx.data()+136,2)&128));
    reset();own_core=0;memory[0][8]=1;native_metrics::ServiceCore(0);assert(glyph_native_metric_scans[0].flags&64);
    reset();own_core=0;glyph_native_metric_scans[0].flags=0;native_metrics::ServiceCore(0);assert(glyph_native_metric_scans[0].flags&4);
    reset();own_core=0;irq_state=1;native_metrics::ServiceCore(0);assert(irq_state==1);
    std::puts("PASS actual retained metrics/demux/statistics/finite scans/atomic mailbox rejection/clock invalidation; host observations only");
}

int main() {
 reset();native_metrics::Calibrate();
 clock_now=100;native_metrics::RecordActivation(70,90,1,true,false);
 clock_now=130;native_metrics::RecordActivation(100,120,2,true,false);
 clock_now=160;native_metrics::RecordFrame(130,150,2,2);
 bool complete=false;for(auto b:request(true))native_metrics::ConsumeRequest(b,0,complete);assert(complete);
 const auto *snapshot=native_metrics::Snapshot(0,2);
 assert(snapshot[16]==2);assert(runtime_identity::ReadLE(snapshot+154,2)&256);
 assert(runtime_identity::ReadLE(snapshot+44,4)==1);
 std::puts("REPRODUCED exact production metrics: two actual boot generations leave latch1 and sticky INVALID for actual2; source boot fanout supplies this sequence");
}
