static usbd_device_t _usbd_dev;
static usbd_control_xfer_t _ctrl_xfer;
static uint8_t _usbd_rhport=0;
static mutex_t mutex_storage;
static osal_mutex_t _usbd_mutex=&mutex_storage;
static uint8_t qbuffer[16*16];
static osal_queue_def_t _usbd_qdef;
static osal_queue_t _usbd_q=&_usbd_qdef;
extern "C" void cdcd_init(void),cdcd_reset(uint8_t),mscd_init(void),mscd_reset(uint8_t),hidd_init(void),hidd_reset(uint8_t),midid_init(void),midid_reset(uint8_t);
// Exact XInput source init/reset bodies are empty; no instance exists at RT2.
static void xinput_init(void){}
static void xinput_reset(uint8_t rhport){(void)rhport;}
static usbd_class_driver_t _usbd_driver[4];
static usbd_class_driver_t app_driver[1];
static const usbd_class_driver_t *_app_driver=app_driver;
static uint8_t _app_driver_count=1;
#define BUILTIN_DRIVER_COUNT 4
#define TOTAL_DRIVER_COUNT (_app_driver_count+BUILTIN_DRIVER_COUNT)
#define DRVID_INVALID 0xff
static usbd_class_driver_t const *get_driver(uint8_t id){return id<_app_driver_count?&_app_driver[id]:&_usbd_driver[id-_app_driver_count];}
