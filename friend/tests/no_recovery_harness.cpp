#include "core/Persistence.hpp"
#include <iostream>
#ifdef GLYPH_PRIVATE_FRIEND_STORAGE_RECOVERY
#error Private recovery must be disabled for this control
#endif
int main() {
    LittleFS.reset(); LittleFS.initial_mount_ok=false;
    Persistence store; static Config config;
    if(store.IsAvailable() || store.SaveConfig(config) || LittleFS.format_calls!=0 || LittleFS.auto_format_seen) return 1;
    std::cout<<"MACRO-OFF CONTROL PASS: same Persistence constructor retains no-autoformat/unavailable fail-closed behavior; no private recovery format\n";
}
