#include "comms/BootJoybusDetection.hpp"
#include <joybus.h>
#include <joybus.pio.h>
#include <hardware/gpio.h>
#include <pico/time.h>

namespace {
class BootJoybusPort {
    joybus_port_t port{};
    bool acquired=false;
public:
    explicit BootJoybusPort(uint32_t pin) {
        // Core0 owns boot detection before publication. Claim once, fail closed
        // on resource exhaustion instead of the vendor constructor's panic.
        const int sm=pio_claim_unused_sm(pio0,false);
        if(sm<0)return;
        if(!pio_can_add_program(pio0,&joybus_program)) {
            pio_sm_unclaim(pio0,sm);
            return;
        }
        port.pin=pin;port.pio=pio0;port.sm=sm;
        port.offset=pio_add_program(pio0,&joybus_program);
        port.config=joybus_program_get_config(port.pio,port.sm,port.offset,pin);
        acquired=true;
        joybus_port_reset(&port);
    }
    ~BootJoybusPort() {
        if(!acquired)return;
        // A timeout may leave a partial TX. Release the line before removing
        // the exact one acquired SM/program or trying the next detector.
        pio_sm_set_enabled(port.pio,port.sm,false);
        pio_sm_set_consecutive_pindirs(port.pio,port.sm,port.pin,1,false);
        joybus_port_terminate(&port);
    }
    BootJoybusPort(const BootJoybusPort &)=delete;
    BootJoybusPort &operator=(const BootJoybusPort &)=delete;
    bool Ready()const{return acquired;}
    absolute_time_t Deadline(uint32_t us){return make_timeout_time_us(us);}
    bool Expired(absolute_time_t deadline){return time_reached(deadline);}
    bool LineHigh(){return gpio_get(port.pin);}
    void Relax(){tight_loop_contents();}
    void BeginSend(){joybus_program_send_init(port.pio,port.sm,port.offset,port.pin,&port.config);}
    bool TxFull(){return pio_sm_is_tx_fifo_full(port.pio,port.sm);}
    void Put(uint32_t value){pio_sm_put(port.pio,port.sm,value);}
    bool Send(const uint8_t *bytes,size_t size,uint32_t timeout){return boot_joybus::SendBounded(*this,bytes,size,timeout);}
    uint Receive(uint8_t *bytes,uint size,uint32_t timeout){return joybus_receive_bytes(&port,bytes,size,timeout,true);}
    void Wait(uint32_t us){busy_wait_us(us);}
    void Reset(){joybus_port_reset(&port);}
};
}

__attribute__((noinline)) bool detect_boot_gamecube(uint32_t pin) {
    BootJoybusPort io(pin);
    return io.Ready()&&boot_joybus::Detect<false>(io);
}
__attribute__((noinline)) bool detect_boot_n64(uint32_t pin) {
    BootJoybusPort io(pin);
    return io.Ready()&&boot_joybus::Detect<true>(io);
}
