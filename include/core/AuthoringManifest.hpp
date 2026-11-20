#pragma once
#include <cstddef>
#include <cstdint>

// Inert authoring bytes. No allocation, normalization or runtime dependencies.
namespace glyph_authoring {
constexpr size_t kMaximumBytes = 371;
inline bool Utf8(const uint8_t *b, size_t size) {
    for (size_t i = 0; i < size;) {
        const uint8_t c = b[i++];
        if (!c) return false;
        if (c < 0x80) continue;
        unsigned n; uint32_t v, minimum;
        if (c >= 0xc2 && c <= 0xdf) { n=1; v=c&31; minimum=0x80; }
        else if (c >= 0xe0 && c <= 0xef) { n=2; v=c&15; minimum=0x800; }
        else if (c >= 0xf0 && c <= 0xf4) { n=3; v=c&7; minimum=0x10000; }
        else return false;
        if (n > size-i) return false;
        while (n--) { const uint8_t d=b[i++]; if ((d&0xc0)!=0x80) return false; v=(v<<6)|(d&63); }
        if (v<minimum || v>0x10ffff || (v>=0xd800 && v<=0xdfff)) return false;
    }
    return true;
}
inline bool Validate(const uint8_t *b, size_t size) {
    if (!b || size<7 || size>kMaximumBytes || b[0]!=1) return false;
    uint32_t mask=uint32_t(b[1])|(uint32_t(b[2])<<8)|(uint32_t(b[3])<<16)|(uint32_t(b[4])<<24);
    if (!mask || (mask&0xf0000000u)) return false;
    size_t at=5;
    for (unsigned slot=0; slot<28; ++slot) if (mask&(uint32_t(1)<<slot)) {
        if (at==size) return false;
        const size_t n=b[at++];
        if (!n || n>64 || n>size-at || !Utf8(b+at,n)) return false;
        at+=n;
    }
    return at==size;
}
// Stored future versions are bounded opaque custody; only new writes use Validate.
inline bool StoredEnvelope(const uint8_t *b, size_t size) {
    return b && size && size<=kMaximumBytes && (b[0]!=1 || size>=7);
}
}
