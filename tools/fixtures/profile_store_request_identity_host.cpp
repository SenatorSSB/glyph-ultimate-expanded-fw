#include "core/ProfileStoreRequestIdentity.hpp"
#include "core/ProfileStoreName.hpp"
#include <pb_decode.h>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>

static ProfileStoreTransactionIdentity identity(ProfileStoreRequest request) {
    ProfileStoreTransactionIdentity result;
    assert(ProfileStoreRequestIdentity(request, result));
    assert(request.request_token == result.token);
    return result;
}
static std::string hex(const uint8_t *bytes, size_t size) {
    static const char digits[] = "0123456789abcdef";
    std::string text;
    for (size_t i=0;i<size;++i) { text += digits[bytes[i]>>4]; text += digits[bytes[i]&15]; }
    return text;
}
int main() {
    uint8_t digest[32]; Sha256 empty; empty.Final(digest);
    assert(hex(digest,32)=="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    Sha256 abc; abc.Update("a",1); abc.Update("bc",2); abc.Final(digest);
    assert(hex(digest,32)=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    Sha256 million; for(unsigned i=0;i<1000000;++i) million.Update("a",1); million.Final(digest);
    assert(hex(digest,32)=="cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");
    for(size_t n:{size_t{0},size_t{1},size_t{17},size_t{18},size_t{31},size_t{32}}) {
        const std::string name(n,'x'); assert(ProfileStoreNameValid(name.c_str()));
        if(n>17) { char old_name[18]{};std::strncpy(old_name,name.c_str(),17);assert(std::strlen(old_name)!=n); }
    }
    assert(!ProfileStoreNameValid(std::string(33,'x').c_str()));
    assert(ProfileStoreNameValid("\xc3\xa4\xf0\x9f\x90\xb1"));
    assert(!ProfileStoreNameValid("\xc0\x80"));
    assert(!ProfileStoreNameValid("\xed\xa0\x80"));
    assert(!ProfileStoreNameValid("\xf4\x90\x80\x80"));
    ProfileStoreRequest request=ProfileStoreRequest_init_default;
    request.protocol_version=1; request.request_token=0x123456789abcdef0ull;
    request.operation=PROFILE_STORE_CREATE; request.expected_store_generation=7;
    request.has_profile=true; request.profile.schema_version=3; std::strcpy(request.name,"01234567890123456789012345678901");
    const auto original=identity(request);
    auto changed=[&](ProfileStoreRequest other) { assert(!original.SameRequest(identity(other))); };
    auto copy=request; copy.operation=PROFILE_STORE_UPDATE; changed(copy);
    copy=request; ++copy.profile_id; changed(copy);
    copy=request; ++copy.expected_profile_revision; changed(copy);
    copy=request; ++copy.expected_store_generation; changed(copy);
    copy=request; ++copy.expected_config_generation; changed(copy);
    copy=request; ++copy.mode_config_index; changed(copy);
    copy=request; ++copy.display_rank; changed(copy);
    copy=request; copy.name[31]='X'; changed(copy);
    copy=request; ++copy.profile.default_table_id; changed(copy);
    copy=request; copy.has_profile=false; changed(copy);
    copy=request; copy.request_token^=uint64_t{1}<<40;
    const auto token_changed=identity(copy);
    assert(!original.SameRequest(token_changed));
    assert(std::memcmp(original.digest,token_changed.digest,32)==0);
    // Old convention trusted the high32 caller digest even when payload and
    // operation changed. This negative control deliberately aliases them.
    copy=request; copy.operation=PROFILE_STORE_DELETE; ++copy.profile_id;
    assert(uint32_t(copy.request_token>>32)==uint32_t(request.request_token>>32));
    assert(uint32_t(copy.request_token)==uint32_t(request.request_token));
    changed(copy);
    // Frozen legacy v1 STATUS frame is still accepted with additive schema.
    const uint8_t old_status[]={0x08,0x01,0x10,0x52,0x18,0x01};
    ProfileStoreRequest legacy=ProfileStoreRequest_init_default;
    pb_istream_t in=pb_istream_from_buffer(old_status,sizeof(old_status));
    assert(pb_decode(&in,ProfileStoreRequest_fields,&legacy));
    assert(legacy.protocol_version==1&&legacy.request_token==0x52&&legacy.operation==PROFILE_STORE_STATUS);
    static_assert(PROFILE_STORE_STATUS==1&&PROFILE_STORE_LIST==2&&PROFILE_STORE_READ==3&&PROFILE_STORE_CREATE==4&&PROFILE_STORE_UPDATE==5&&PROFILE_STORE_DUPLICATE==6&&PROFILE_STORE_RENAME==7&&PROFILE_STORE_REORDER==8&&PROFILE_STORE_DELETE==9&&PROFILE_STORE_SET_MODE_REFERENCE==10&&PROFILE_STORE_QUERY_TRANSACTION==11,"frozen operations unchanged");
    static_assert(sizeof(request.name)==33,"32 UTF-8 bytes plus terminator");
    static_assert(sizeof(Config{}.profile_reference_digest)==32,"full request digest persisted");
    std::puts("sha256_vectors=PASS authenticated_request_identity=PASS caller_digest_negative_control=PASS old_protocol_fixture=PASS full_name_bound=PASS");
}
