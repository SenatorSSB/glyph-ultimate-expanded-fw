#pragma once
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
void *liveness_lfs_malloc(size_t size);
void liveness_lfs_free(void *pointer);
#ifdef __cplusplus
}
#endif
