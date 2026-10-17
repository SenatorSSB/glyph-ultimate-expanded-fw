// The lifecycle injects its bounded storage adapter. The unused production
// default adapter must fail closed if a test accidentally invokes it.
#include "core/CheckedStorage.hpp"
namespace CheckedStorage {
Result unavailable(){return {Outcome::Failed};}
Result Open(File&,const char*,bool,Kind){return unavailable();}
Result Read(File&,void*,size_t){return unavailable();}
Result Seek(File&,size_t){return unavailable();}
Result Close(File&){return unavailable();}
Result WriteFile(const char*,const uint8_t*,size_t,Kind){return unavailable();}
Result ReadFile(const char*,uint8_t*,size_t,Kind){return unavailable();}
Result Stat(const char*,size_t*,Kind){return unavailable();}
Result Rename(const char*,const char*,Kind){return unavailable();}
Result Remove(const char*,Kind){return unavailable();}
Result Capacity(Geometry&){return unavailable();}
Result Enumerate(const char*,Visitor,void*){return unavailable();}
}
