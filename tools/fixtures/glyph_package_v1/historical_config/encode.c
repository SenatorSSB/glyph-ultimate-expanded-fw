#include "config.pb.h"
#include <pb_encode.h>
#include <stdio.h>
#include <string.h>
static Config config=Config_init_zero;
static unsigned char out[65536];
int main(void) {
 config.game_mode_configs_count=1;
 config.game_mode_configs[0].mode_id=3;
 strcpy(config.game_mode_configs[0].name,"Historical");
 config.communication_backend_configs_count=1;
 config.communication_backend_configs[0].backend_id=7;
 config.communication_backend_configs[0].default_mode_config=1;
 config.default_backend_config=1;config.default_usb_backend_config=1;
 pb_ostream_t stream=pb_ostream_from_buffer(out,sizeof out);
 if(!pb_encode(&stream,Config_fields,&config))return 1;
 return fwrite(out,1,stream.bytes_written,stdout)==stream.bytes_written?0:2;
}