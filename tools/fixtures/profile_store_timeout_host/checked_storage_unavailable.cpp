// The retained backend suite injects MemoryStorage into ProfileStore. Its unused
// production mount construction must link but must never provide fake success.
#include "core/CheckedStorage.hpp"
namespace CheckedStorage {
void SetFaultHook(FaultHook) {}
Result Open(File &,const char *,bool,Kind){return {};}
Result Read(File &,void *,size_t){return {};}
Result Write(File &,const void *,size_t){return {};}
Result Seek(File &,size_t){return {};}
Result Sync(File &){return {};}
Result Close(File &){return {};}
Result Stat(const char *,size_t *,Kind){return {};}
Result Remove(const char *,Kind){return {};}
Result Rename(const char *,const char *,Kind){return {};}
Result Capacity(Geometry &){return {};}
Result Enumerate(const char *,Visitor,void *){return {};}
Result WriteFile(const char *,const uint8_t *,size_t,Kind){return {};}
Result ReadFile(const char *,uint8_t *,size_t,Kind){return {};}
}
