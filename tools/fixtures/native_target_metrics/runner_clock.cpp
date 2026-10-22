// Actual instrumentation host clock for native/legacy output correspondence.
// Scans and coherent/incoherent time snapshots have their own actual-source
// finite fixture. This clock supplies no target timing evidence.
#include <cstdint>
uint32_t NativeMetricHostNow(){static uint32_t tick=0;return ++tick;}
bool NativeMetricHostUptime(uint64_t &out){out=1000000;return true;}
uint32_t NativeMetricHostSaveIrq(){return 0;}
void NativeMetricHostRestoreIrq(uint32_t){}
uint32_t NativeMetricHostSp(){return 0;}
uint32_t NativeMetricHostWord(uint32_t){return 0;}
