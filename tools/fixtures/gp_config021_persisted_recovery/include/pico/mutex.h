#pragma once
#include <mutex>
#include "../../host_observation.hpp"
struct mutex_t {
    std::mutex lock;
    bool initialized = true;
    mutex_t() { ++host_observation.sync_initializations; }
};
#define auto_init_mutex(name) mutex_t name
inline void mutex_enter_blocking(mutex_t *m) {
    if (!m->initialized) std::terminate();
    m->lock.lock();
    __atomic_fetch_add(&host_observation.sync_acquires,1u,__ATOMIC_RELAXED);
}
inline void mutex_exit(mutex_t *m) {
    __atomic_fetch_add(&host_observation.sync_releases,1u,__ATOMIC_RELAXED);
    m->lock.unlock();
}
