/* Independent exact old descriptor, never firmware or current Config oracle. */
#include "config.pb.h"
#include <pb_encode.h>
#include <pb_decode.h>
#include <stdio.h>
#include <string.h>
static Config config;
static unsigned char input[65537], output[65536];
int main(void) {
 size_t n=fread(input,1,sizeof input,stdin);
 if(n>sizeof output)return 1;
 pb_istream_t in=pb_istream_from_buffer(input,n);
 if(!pb_decode(&in,Config_fields,&config))return 2;
 pb_ostream_t out=pb_ostream_from_buffer(output,sizeof output);
 if(!pb_encode(&out,Config_fields,&config))return 3;
 return out.bytes_written==n&&!memcmp(input,output,n)?0:4;
}
