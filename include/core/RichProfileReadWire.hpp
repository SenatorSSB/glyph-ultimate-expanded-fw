#pragma once
#include "core/PackageRequestWire.hpp"

namespace glyph_package {
// Presence probe preserves ordinary legacy parsing. Any outer24, even with a
// malformed value, selects strict rich grammar; it can never become normal READ.
inline bool HasRichReadField(const uint8_t *b, size_t size) {
    size_t at=0;
    auto raw=[&](uint64_t &v) {
        v=0;
        for(unsigned shift=0;shift<70;shift+=7) {
            if(at==size)return false;
            uint8_t c=b[at++]; if(shift==63&&c>1)return false;
            v|=uint64_t(c&127)<<shift; if(!(c&128))return true;
        } return false;
    };
    while(at<size) {
        uint64_t key,n;
        if(!raw(key))return false;
        if((key>>3)==24)return true;
        if((key&7)==0) { if(!raw(n))return false; continue; }
        if((key&7)==2) { if(!raw(n))return false; }
        else if((key&7)==1)n=8;
        else if((key&7)==5)n=4;
        else return false;
        if(n>size-at)return false;
        at+=size_t(n);
    } return false;
}
inline bool ScanRichRead(const uint8_t *b,size_t size) {
    if(!b||!size||size>49)return false;
    size_t at=0; unsigned previous=0; uint32_t seen=0;
    while(at<size) {
        uint64_t key,v;
        if(!wire::Varint(b,size,at,key)||key>UINT32_MAX||(key&7))return false;
        const unsigned tag=unsigned(key>>3);
        if(tag<=previous || (tag!=1&&tag!=2&&tag!=3&&tag!=4&&tag!=5&&tag!=6&&tag!=13&&tag!=21&&tag!=24))return false;
        previous=tag;seen|=uint32_t(1)<<tag;
        if(!wire::Varint(b,size,at,v)||!v||(tag!=2&&v>UINT32_MAX))return false;
        if((tag==1&&v!=2)||(tag==3&&v!=3)||(tag==24&&v!=1))return false;
    }
    constexpr uint32_t required=(1u<<1)|(1u<<2)|(1u<<3)|(1u<<4)|(1u<<5)|(1u<<6)|(1u<<21)|(1u<<24);
    return (seen&required)==required;
}
inline bool AppendRichReadTail(pb_ostream_t &out,uint32_t format,const uint8_t *metadata,
                               size_t metadata_bytes,const uint8_t *sha) {
    if(!sha||(format!=2&&format!=3)||(format==2&&(metadata||metadata_bytes))||
       (format==3&&(!metadata||!metadata_bytes||metadata_bytes>371)))return false;
    if(!pb_encode_tag(&out,PB_WT_VARINT,218)||!pb_encode_varint(&out,format==2?1:2))return false;
    if(format==3&&(!pb_encode_tag(&out,PB_WT_STRING,219)||!pb_encode_string(&out,metadata,metadata_bytes)))return false;
    return pb_encode_tag(&out,PB_WT_STRING,220)&&pb_encode_string(&out,sha,32)&&
        pb_encode_tag(&out,PB_WT_VARINT,221)&&pb_encode_varint(&out,format);
}
}
