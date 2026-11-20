#include "core/AuthoringManifest.hpp"
#include "core/PackageStorageFormat.hpp"
#include "core/Sha256.hpp"
extern "C" {
int manifest_valid(const uint8_t *b,size_t n){return glyph_authoring::Validate(b,n);}
int rich_header(uint8_t *h,const uint8_t *p,size_t w,size_t m){
    static const uint8_t digest[32]={1},baseline[32]={2};
    return package_storage::MakeRichRecordHeader(h,p,w,m,{42,1,0,0,2,1,17,digest,baseline});
}
int record_valid(const uint8_t *b,size_t n){return package_storage::RecordValid(b,n);}
size_t wrapper_size(const uint8_t *b,size_t n){package_storage::RecordPayloadView v;return package_storage::SplitRecordPayload(b,n,v)?v.wrapper_bytes:0;}
void record_sha(const uint8_t *b,size_t n,uint8_t *out){Sha256 h;h.Update(b,n);h.Final(out);}
uint64_t charge(size_t n){uint64_t out=0;return package_storage::FileCharge(n,out)?out:0;}
}
