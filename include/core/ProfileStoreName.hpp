#pragma once
#include <cstddef>
#include <cstdint>
// String bound is bytes, never Unicode code points. Reject malformed UTF-8,
// overlong encodings, surrogates and values outside Unicode before persistence.
inline bool ProfileStoreNameValid(const char *name, size_t capacity = 33) {
    if (!name) return false;
    size_t n=0;while(n<capacity&&name[n])++n;
    if(n==capacity)return false;
    for(size_t i=0;i<n;){
        const uint8_t c=static_cast<uint8_t>(name[i++]);
        if(c<0x80)continue;
        unsigned rest=0;uint32_t value=0, minimum=0;
        if(c>=0xc2&&c<=0xdf){rest=1;value=c&0x1f;minimum=0x80;}
        else if(c>=0xe0&&c<=0xef){rest=2;value=c&0x0f;minimum=0x800;}
        else if(c>=0xf0&&c<=0xf4){rest=3;value=c&7;minimum=0x10000;}
        else return false;
        if(rest>n-i)return false;
        while(rest--){const uint8_t b=static_cast<uint8_t>(name[i++]);if((b&0xc0)!=0x80)return false;value=(value<<6)|(b&0x3f);}
        if(value<minimum||value>0x10ffff||(value>=0xd800&&value<=0xdfff))return false;
    }
    return true;
}
