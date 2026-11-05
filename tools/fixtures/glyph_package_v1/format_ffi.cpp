#include "core/PackageStorageFormat.hpp"
extern "C" {
int root_valid(const unsigned char *b) { return package_storage::RootValid({b,b+3904,b+4416}); }
int control_valid(const unsigned char *b) { return package_storage::ControlValid(b,{b+16,b+3920,b+4432}) && package_storage::ControlPhaseValid(b,b+3920); }
int record_valid(const unsigned char *b, size_t n) { return package_storage::RecordValid(b,n); }
int intent_valid(const unsigned char *b) { return package_storage::IntentValid(b); }
int charge(unsigned long long n, unsigned long long *out) { uint64_t v; bool ok=package_storage::FileCharge(n,v);if(ok)*out=v;return ok; }
}
extern "C" int make_record(unsigned char *header,const unsigned char *body,size_t n,unsigned inc,unsigned id,unsigned row,unsigned rgb,unsigned gen,unsigned seq,unsigned long long token,const unsigned char *digest,const unsigned char *baseline) {
 return package_storage::MakeRecordHeader(header,body,n,{inc,id,row,rgb,gen,seq,token,digest,baseline});
}
