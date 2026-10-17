#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <algorithm>
#include <stdexcept>
extern "C" {
#include "tusb.h"
#include "device/usbd_pvt.h"
#include "common/tusb_private.h"
#define CFG_TUD_ENDPPOINT_MAX 16
unsigned class_resets[4];
void host_cdc_seed(void);bool host_cdc_reset_ok(void);
void host_msc_seed(void),host_hid_seed(void),host_midi_seed(void);bool host_msc_reset_ok(void),host_hid_reset_ok(void),host_midi_reset_ok(void);
}
static void require(bool b,const char *why){if(!b)throw std::runtime_error(why);}
#include "usbd.inc"
using Handler=void(*)(void);
static std::vector<std::string> events;
static unsigned core=0,exception=0,primask=0,mutex_allocs=0,reset_count=0,persistent_writes=0;
static unsigned USB_TASK_IRQ=31;
static bool irq_on[32],pending[32],shared=true,descriptor_null=false,queue_fail=false,mutate_during_lock=false,fail_after_dcd=false;
static mutex_t __usb_mutex;
static bool readonly_backend=true;
static void usb_task_irq(void){}
static Handler exclusive=usb_task_irq;
#define USBCTRL_IRQ 5
uint32_t get_core_num(){return core;}
uint32_t __get_current_exception(){return exception;}
uint32_t save_and_disable_interrupts(){auto old=primask;primask=1;events.push_back("mask");return old;}
void restore_interrupts(uint32_t value){primask=value;events.push_back("unmask");}
bool irq_is_enabled(unsigned n){return irq_on[n];}
Handler irq_get_exclusive_handler(unsigned){return exclusive;}
bool irq_has_shared_handler(unsigned){return shared;}
void irq_set_enabled(unsigned n,bool b){irq_on[n]=b;events.push_back(std::string(b?"enable":"disable")+std::to_string(n));}
void irq_clear(unsigned n){pending[n]=false;events.push_back("clear"+std::to_string(n));}
extern "C" void mutex_init(mutex_t*m){++mutex_allocs;m->core.spin_lock=m;m->owner=-1;m->held=false;}
extern "C" bool mutex_try_enter(mutex_t*m,uint32_t*){events.push_back("lock");if(m->held)return false;m->held=true;m->owner=0;if(mutate_during_lock)_app_driver_count=0;return true;}
extern "C" bool mutex_enter_timeout_ms(mutex_t*m,uint32_t){return mutex_try_enter(m,nullptr);}
extern "C" void mutex_exit(mutex_t*m){require(m->held,"balanced mutex");m->held=false;m->owner=-1;events.push_back("unlock");}
extern "C" bool tud_inited(void){return _usbd_rhport!=0xff;}
static uint8_t device[]={18,1,0,2,TUSB_CLASS_MISC,MISC_SUBCLASS_COMMON,MISC_PROTOCOL_IAD,64,0x8a,0x2e,0x92,0x10,0,1,1,2,3,1};
static uint8_t cfg[]={TUD_CONFIG_DESCRIPTOR(1,2,0,75,TUSB_DESC_CONFIG_ATT_REMOTE_WAKEUP|128,100),TUD_CDC_DESCRIPTOR(0,0,0x81,8,0x01,0x82,64)};
extern "C" const uint8_t*tud_descriptor_device_cb(){return descriptor_null?nullptr:device;}
extern "C" const uint8_t*tud_descriptor_configuration_cb(uint8_t){return descriptor_null?nullptr:cfg;}
struct Endpoint{bool active;uint8_t ep_addr;uint32_t bytes;};
using hw_endpoint_t=Endpoint;
#define USB_MAX_ENDPOINTS 16
static Endpoint hw_endpoints[USB_MAX_ENDPOINTS][2];
static bool _sof_enable=true;
struct Pair{uint32_t in,out;};
struct Dpram{Pair ep_ctrl[15];uint8_t epx_data[1024];};
static Dpram dpram;
static Dpram*usb_dpram=&dpram;
static uint8_t*next_buffer_ptr;
struct Registers{uint32_t pwr,main_ctrl,sie_ctrl,inte;};
static Registers registers;
static Registers*usb_hw=&registers;
#define FORCE_VBUS_DETECT 1
#define USB_USB_PWR_VBUS_DETECT_BITS 1
#define USB_USB_PWR_VBUS_DETECT_OVERRIDE_EN_BITS 2
#define USB_MAIN_CTRL_CONTROLLER_EN_BITS 1
#define USB_SIE_CTRL_EP0_INT_1BUF_BITS 4
#define USB_INTS_BUFF_STATUS_BITS 1
#define USB_INTS_BUS_RESET_BITS 2
#define USB_INTS_SETUP_REQ_BITS 4
#define USB_INTS_DEV_SUSPEND_BITS 8
#define USB_INTS_DEV_RESUME_FROM_HOST_BITS 16
#define USB_INTS_DEV_CONN_DIS_BITS 32
#define __tusb_irq_path_func(x) x
static bool attached=true;
static void rp2040_usb_init(){require(primask&&__usb_mutex.held&&!irq_on[5]&&!irq_on[31]&&!attached,"DCD hardware reset quiesced");++reset_count;events.push_back("peripheral-reset");registers={};dpram={};if(fail_after_dcd)_app_driver_count=0;}
// Endpoint-register addressing is modeled; called by the actual helper twice.
static void hw_endpoint_init(uint8_t addr,uint16_t size,uint8_t type){require(size==64&&type==TUSB_XFER_CONTROL,"actual EP0 init parameters");auto&e=hw_endpoints[0][addr>>7];e.ep_addr=addr;e.active=false;e.bytes=64;}
#include "noncontrol.inc"
#include "dcd.inc"
extern "C" void dcd_disconnect(uint8_t){attached=false;events.push_back("detach");}
extern "C" void dcd_connect(uint8_t){require(readonly_backend,"readonly installed before expose");require(irq_on[5]&&irq_on[31]&&!pending[5]&&!pending[31],"clean IRQs before expose");require(host_cdc_reset_ok(),"real CDC reset before expose");attached=true;events.push_back("attach");}
#include "port.inc"
static void fresh(){
 core=exception=primask=0;shared=true;descriptor_null=queue_fail=mutate_during_lock=fail_after_dcd=false;exclusive=usb_task_irq;_app_driver_count=1;_app_driver=app_driver;_usbd_rhport=0;_usbd_q=&_usbd_qdef;
 mutex_init(&__usb_mutex);mutex_init(&mutex_storage);_usbd_qdef.critsec.spin_lock=&_usbd_qdef;_usbd_qdef.critsec.held=0;
 tu_fifo_config(&_usbd_qdef.ff,qbuffer,16,16,false);uint8_t event[16]={1};tu_fifo_write(&_usbd_qdef.ff,event);
 std::memset(&_usbd_dev,0x55,sizeof(_usbd_dev));std::memset(&_ctrl_xfer,0x55,sizeof(_ctrl_xfer));
 _usbd_driver[0].init=cdcd_init;_usbd_driver[0].reset=cdcd_reset;_usbd_driver[1].init=mscd_init;_usbd_driver[1].reset=mscd_reset;_usbd_driver[2].init=hidd_init;_usbd_driver[2].reset=hidd_reset;_usbd_driver[3].init=midid_init;_usbd_driver[3].reset=midid_reset;app_driver[0].init=xinput_init;app_driver[0].reset=xinput_reset;
 cdcd_init();mscd_init();hidd_init();midid_init();host_cdc_seed();host_msc_seed();host_hid_seed();host_midi_seed();std::memset(class_resets,0,sizeof(class_resets));
 std::memset(hw_endpoints,0x55,sizeof(hw_endpoints));std::memset(&dpram,0x55,sizeof(dpram));_sof_enable=true;next_buffer_ptr=nullptr;
 std::fill(std::begin(irq_on),std::end(irq_on),true);std::fill(std::begin(pending),std::end(pending),true);attached=true;glyph_recovery_usb_consumed=false;readonly_backend=true;cfg[25]=4;device[8]=0x8a;cfg[2]=75;events.clear();reset_count=0;
}
static void no_hardware(const char*why){const auto allocs=mutex_allocs;require(!GlyphRecoveryUsbReinitialize(),why);require(reset_count==0&&attached&&irq_on[5]&&irq_on[31]&&persistent_writes==0&&mutex_allocs==allocs,"preflight failure preserves hardware/store/allocs");}
static void success(){const auto allocs=mutex_allocs;require(GlyphRecoveryUsbReinitialize(),"warmreset actual body success");require(reset_count==1&&attached&&!primask&&!__usb_mutex.held,"one reset balanced locks");require(mutex_allocs==allocs,"no duplicate OSAL lock init");require(tu_fifo_empty(&_usbd_qdef.ff),"old queue discarded");require(host_cdc_reset_ok(),"CDC endpoints/FIFOs reset coding retained");require(host_msc_reset_ok()&&host_hid_reset_ok()&&host_midi_reset_ok(),"actual other class state/FIFOs reset");for(auto n:class_resets)require(n==1,"all actual builtin class resets exactly once");for(auto x:_usbd_dev.itf2drv)require(x==0xff,"interface map reset");for(auto&p:_usbd_dev.ep2drv)for(auto x:p)require(x==0xff,"endpoint map reset");require(!_usbd_dev.cfg_num&&!_usbd_dev.connected&&!_ctrl_xfer.buffer&&!_ctrl_xfer.complete_cb,"USBD/control private state clear");require(!_sof_enable&&hw_endpoints[0][0].bytes==64&&hw_endpoints[0][1].bytes==64,"DCD SOF/EP0 reset");for(unsigned n=1;n<16;n++)for(auto&e:hw_endpoints[n])require(!e.active&&!e.bytes,"noncontrol software reset");require(next_buffer_ptr==&usb_dpram->epx_data[0],"DCD allocator rewound");require(events[events.size()-3]=="attach"&&events.back()=="unmask","pullup is final USB mutation");require(!persistent_writes,"zero persistence writes");}
#include "route.inc"
int main(){try{
 unsigned cases=0;fresh();success();++cases;auto prior=events;require(!GlyphRecoveryUsbReinitialize()&&events==prior&&reset_count==1,"repeated one-shot rejected unchanged");++cases;
 for(unsigned fault=0;fault<15;fault++){fresh();switch(fault){case 0:core=1;break;case 1:exception=21;break;case 2:primask=1;break;case 3:descriptor_null=true;break;case 4:device[8]=0;break;case 5:cfg[2]=74;break;case 6:exclusive=nullptr;break;case 7:shared=false;break;case 8:_usbd_rhport=0xff;break;case 9:_usbd_q=nullptr;break;case 10:_usbd_qdef.critsec.spin_lock=nullptr;break;case 11:_usbd_mutex->core.spin_lock=nullptr;break;case 12:_usbd_mutex->owner=0;break;case 13:_app_driver_count=0;break;case 14:__usb_mutex.held=true;break;}no_hardware("preflight discriminator");++cases;}
 for(unsigned n:{5u,31u}){fresh();irq_on[n]=false;const auto a=mutex_allocs;require(!GlyphRecoveryUsbReinitialize()&&reset_count==0&&attached&&mutex_allocs==a,"IRQoff fails without reset");++cases;}
 fresh();mutate_during_lock=true;no_hardware("second preflight protects changed state");require(!__usb_mutex.held&&!primask,"second preflight restores context");++cases;
 fresh();fail_after_dcd=true;require(!GlyphRecoveryUsbReinitialize()&&reset_count==1&&!attached&&!irq_on[5]&&!irq_on[31]&&!primask&&!__usb_mutex.held&&glyph_recovery_usb_consumed,"post-reset failure stays detached/off and consumes attempt");auto failed_events=events;require(!GlyphRecoveryUsbReinitialize()&&events==failed_events,"failed transaction cannot retry");++cases;
 for(unsigned i=9;i<75;i++){fresh();cfg[i]^=1;no_hardware("every malformed CDC byte rejected");cfg[i]^=1;}cases+=66;
 for(unsigned i=0;i<64;i++){fresh();success();}++cases;
 fresh();require(!glyph_recovery_usb_consumed&&reset_count==0,"fresh normal boot unchanged after recovery priorboot");++cases;
 fresh();readonly_backend=false;outcome=BootOutcome::Pending;enter_recovery_configurator(true);require(outcome==BootOutcome::RecoveryConfigurator&&reset_count==1&&readonly_backend&&attached,"actual manual route resets USB only after readonly backend");delete recovery_configurator;++cases;
 fresh();readonly_backend=false;outcome=BootOutcome::Pending;enter_recovery_configurator();require(outcome==BootOutcome::RecoveryConfigurator&&reset_count==0&&!glyph_recovery_usb_consumed,"actual automatic recovery route preserves USB lifecycle");delete recovery_configurator;++cases;
 fresh();core=1;readonly_backend=false;outcome=BootOutcome::Pending;enter_recovery_configurator(true);require(outcome==BootOutcome::RecoveryTransportFailure&&reset_count==0&&readonly_backend,"actual failure route publishes refusal without storage mutations");delete recovery_configurator;++cases;
 std::printf("host_cases=%u PASS real_class_reset=4 real_control_reset=true real_generated_helpers=3 repeated_fresh_boots=64 persistence_writes=%u\n",cases,persistent_writes);return 0;
}catch(const std::exception&e){std::fprintf(stderr,"FAIL %s\n",e.what());return 1;}}
