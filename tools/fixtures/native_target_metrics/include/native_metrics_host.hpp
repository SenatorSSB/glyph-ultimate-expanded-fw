#pragma once
#include <cstdint>
constexpr uint8_t kNativeTargetSourceSha[20]={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20};
constexpr uint16_t kNativeTargetSourceFlags=3;
uint32_t NativeMetricHostNow();
bool NativeMetricHostUptime(uint64_t &);
uint32_t NativeMetricHostSaveIrq();
void NativeMetricHostRestoreIrq(uint32_t);
uint32_t NativeMetricHostSp();
uint32_t NativeMetricHostWord(uint32_t);
