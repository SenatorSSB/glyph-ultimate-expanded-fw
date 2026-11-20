#include "core/RichProfileReadWire.hpp"
#include <cassert>
#include <cstdio>
#include <cstring>
int main(int argc,char **argv) {
    assert(argc==2);
    uint8_t native[3336],metadata[371],sha[32],frame[3816];
    std::memset(native,1,sizeof native);std::memset(metadata,127,sizeof metadata);std::memset(sha,1,sizeof sha);
    glyph_package::BorrowedSpan span{native,sizeof native,sizeof native,true};
    ProfileStoreResponse response=ProfileStoreResponse_init_zero;
    response.protocol_version=2;response.request_token=UINT64_MAX;response.status=ProfileStoreStatus_PROFILE_STORE_OK;
    response.store_generation=response.profile_id=response.profile_revision=response.config_generation=UINT32_MAX;
    response.recovery_flags=UINT32_MAX;response.mutation_protocol_version=2;response.store_incarnation=UINT32_MAX;
    response.has_profile=true;response.profile.schema_version=5;
    response.profile.native_payload.funcs.encode=glyph_package::wire::EncodeSpan;response.profile.native_payload.arg=&span;
    auto output=pb_ostream_from_buffer(frame,sizeof frame);
    assert(pb_encode(&output,ProfileStoreResponse_fields,&response));
    assert(output.bytes_written==3400);
    assert(glyph_package::AppendRichReadTail(output,3,metadata,sizeof metadata,sha));
    assert(output.bytes_written==3816);
    FILE *file=std::fopen(argv[1],"wb");assert(file);assert(std::fwrite(frame,1,sizeof frame,file)==sizeof frame);assert(std::fclose(file)==0);
    output=pb_ostream_from_buffer(frame,sizeof frame-1);
    assert(pb_encode(&output,ProfileStoreResponse_fields,&response));
    assert(!glyph_package::AppendRichReadTail(output,3,metadata,sizeof metadata,sha));
    output=pb_ostream_from_buffer(frame,sizeof frame);
    assert(!glyph_package::AppendRichReadTail(output,3,metadata,372,sha));
    assert(!glyph_package::AppendRichReadTail(output,2,metadata,1,sha));
    assert(!glyph_package::AppendRichReadTail(output,3,nullptr,0,sha));
    assert(!glyph_package::AppendRichReadTail(output,3,metadata,371,nullptr));
    ProfileStoreRequest request=ProfileStoreRequest_init_zero;
    request.protocol_version=2;request.request_token=UINT64_MAX;request.operation=ProfileStoreOperation_PROFILE_STORE_READ;
    request.expected_store_generation=request.profile_id=request.expected_profile_revision=request.expected_config_generation=UINT32_MAX;
    request.expected_store_incarnation=UINT32_MAX;request.include_authoring_metadata=true;
    output=pb_ostream_from_buffer(frame,49);assert(pb_encode(&output,ProfileStoreRequest_fields,&request));
    assert(output.bytes_written==49&&glyph_package::ScanRichRead(frame,49));
    return 0;
}
