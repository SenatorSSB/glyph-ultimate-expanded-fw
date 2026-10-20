// Bodies below are extracted byte-for-byte from the pinned framework by the
// checker. Hardware seams only count FIFO writes and DFU entry; no device IO.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <vector>
static bool ready=true;
struct { uint8_t line_state=0; } _cdcd_itf[1];
struct cdc_line_coding_t { uint32_t bit_rate=115200; } coding;
static std::vector<uint8_t> transmitted;
static unsigned dfu_entries=0;
bool tud_ready(){return ready;}
bool tu_bit_test(uint8_t bits,unsigned bit){return (bits&(1u<<bit))!=0;}
size_t tud_cdc_n_write(uint8_t,const uint8_t *bytes,size_t length){transmitted.insert(transmitted.end(),bytes,bytes+length);return length;}
void tud_cdc_get_line_coding(cdc_line_coding_t *out){*out=coding;}
void TinyUSB_Port_EnterDFU(){++dfu_entries;}
void yield(){}
class Adafruit_USBD_CDC {
 public:
  bool isValid(){return true;}
  size_t write(const uint8_t *,size_t);
 private:
  uint8_t _instance=0;
};
#include "pinned_serial_bodies.inc"
int main(){
 Adafruit_USBD_CDC serial;uint8_t response[72]={};
 coding.bit_rate=115200;_cdcd_itf[0].line_state=0;
 if(tud_cdc_n_connected(0)||serial.write(response,sizeof(response))!=0||!transmitted.empty())return 1;
 _cdcd_itf[0].line_state=1;tud_cdc_line_state_cb(0,true,false);
 if(!tud_cdc_n_connected(0)||serial.write(response,sizeof(response))!=72||transmitted.size()!=72||dfu_entries)return 2;
 _cdcd_itf[0].line_state=0;tud_cdc_line_state_cb(0,false,false);
 if(dfu_entries)return 3;
 // Negative control proves the reset seam is live, solely in this host model.
 coding.bit_rate=1200;tud_cdc_line_state_cb(0,false,false);
 if(dfu_entries!=1)return 4;
 std::puts("runtime_identity_pinned_dtr_write_115200_no_reset_1200_control=PASS");return 0;
}
