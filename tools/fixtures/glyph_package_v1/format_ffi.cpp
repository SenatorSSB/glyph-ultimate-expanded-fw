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

extern "C" int admission_need(const unsigned long long *wide, const unsigned *small,
                                int rgb, unsigned long long *out) {
 package_storage::AdmissionArithmetic v{};
 v.used=wide[0];v.free=wide[1];v.total=wide[2];v.protected_bytes=wide[3];v.token=wide[4];v.high_token=wide[5];
 v.rows=small[0];v.rgbs=small[1];v.count=small[2];v.high_id=small[3];v.generation=small[4];v.sequence=small[5];
 v.namespace_files=small[6];v.config_bytes=small[7];v.record_bytes=small[8];v.with_rgb=rgb;
 uint64_t needed=0;const bool ok=package_storage::AdmissionNeed(v,needed);*out=needed;return ok;
}
extern "C" int exact_geometry(const unsigned long long *wide,const unsigned *small) {
 CheckedStorage::Geometry g{};g.total_bytes=wide[0];g.used_bytes=wide[1];g.free_bytes=wide[2];
 g.erase_bytes=small[0];g.program_bytes=small[1];g.read_bytes=small[2];g.block_count=small[3];g.cache_bytes=small[4];g.name_max=small[5];
 return package_storage::ExactGeometry(g);
}
