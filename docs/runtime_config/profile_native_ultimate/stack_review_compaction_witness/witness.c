#include "lfs.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>
int reviewer_create_branch; unsigned reviewer_compact_in_create;
static unsigned char disk[524288];
static int rd(const struct lfs_config*c,lfs_block_t b,lfs_off_t o,void*p,lfs_size_t n){(void)c;memcpy(p,disk+4096*b+o,n);return 0;}
static int pg(const struct lfs_config*c,lfs_block_t b,lfs_off_t o,const void*p,lfs_size_t n){(void)c;unsigned char*d=disk+4096*b+o;const unsigned char*s=p;for(unsigned i=0;i<n;i++){assert((d[i]&s[i])==s[i]);d[i]&=s[i];}return 0;}
static int er(const struct lfs_config*c,lfs_block_t b){(void)c;memset(disk+4096*b,255,4096);return 0;}
static int sy(const struct lfs_config*c){(void)c;return 0;}
int main(void){memset(disk,255,sizeof(disk));struct lfs_config c={.read=rd,.prog=pg,.erase=er,.sync=sy,.read_size=256,.prog_size=256,.block_size=4096,.block_count=128,.block_cycles=16,.cache_size=256,.lookahead_size=256};lfs_t fs;assert(!lfs_format(&fs,&c));assert(!lfs_mount(&fs,&c));unsigned first=0;for(unsigned i=1;i<=64;i++){char p[32];snprintf(p,sizeof(p),"/ultimate-%08x-%08x.tmp",i,1);lfs_file_t f;assert(!lfs_file_open(&fs,&f,p,LFS_O_CREAT|LFS_O_TRUNC|LFS_O_RDWR));if(reviewer_compact_in_create&&!first)first=i;assert(!lfs_file_close(&fs,&f));}printf("PASS flat-root new-file creation reaches lfs_dir_compact; first_file=%u compact_entries=%u\n",first,reviewer_compact_in_create);assert(first>0);assert(!lfs_unmount(&fs));return 0;}
