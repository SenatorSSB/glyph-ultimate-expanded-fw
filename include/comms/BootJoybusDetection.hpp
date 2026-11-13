#pragma once
#include <cstddef>
#include <cstdint>
#include <gamecube_definitions.h>
#include <n64_definitions.h>

// Only Glyph startup uses these finite detectors. Runtime gameplay IO is unchanged.
namespace boot_joybus {
template<class Io>
bool SendBounded(Io &io,const uint8_t *bytes,size_t size,uint32_t timeout_us) {
    const auto deadline=io.Deadline(timeout_us);
    while(!io.LineHigh()) {
        if(io.Expired(deadline))return false;
        io.Relax();
    }
    io.BeginSend();
    for(size_t i=0;i<size;++i) {
        while(io.TxFull()) {
            if(io.Expired(deadline))return false;
            io.Relax();
        }
        if(io.Expired(deadline))return false;
        io.Put((uint32_t(bytes[i])<<24)|(uint32_t(i+1==size)<<23));
    }
    return true;
}

template<bool N64,class Io>
bool Detect(Io &io) {
    constexpr uint32_t timeout=N64?20000:10000;
    constexpr unsigned budget=N64?60:10;
    for(unsigned attempt=0;attempt<budget;++attempt) {
        uint8_t command=0;
        if(io.Receive(&command,1,timeout)!=1)continue;
        if(command==0x00||command==0xff) {
            io.Wait(4);
            bool sent;
            if constexpr(N64)sent=io.Send(reinterpret_cast<const uint8_t *>(&default_n64_status),sizeof(default_n64_status),timeout);
            else sent=io.Send(reinterpret_cast<const uint8_t *>(&default_gc_status),sizeof(default_gc_status),timeout);
            if(!sent)return false;
        } else if(N64&&command==uint8_t(N64Command::POLL)) {
            io.Wait(4);
            if(!io.Send(reinterpret_cast<const uint8_t *>(&default_n64_report),sizeof(default_n64_report),timeout))return false;
            io.Wait(40*sizeof(n64_report_t));
            return true;
        } else if(!N64&&(command==uint8_t(GamecubeCommand::ORIGIN)||command==uint8_t(GamecubeCommand::RECALIBRATE))) {
            return true;
        } else if(!N64&&command==uint8_t(GamecubeCommand::POLL)) {
            uint8_t tail[2];
            // Original Detect ignores WaitForPollEnd's result after its finite tail read.
            io.Receive(tail,2,50);
            return true;
        } else {
            // (5 us * 8) * (max_command_bytes - 1) + 50 us.
            io.Wait(N64?50:130);
            io.Reset();
        }
    }
    return false;
}
}

bool detect_boot_gamecube(uint32_t pin);
bool detect_boot_n64(uint32_t pin);
