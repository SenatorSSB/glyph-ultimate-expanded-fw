#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>

// Portable streaming FIPS 180-4 SHA-256. No heap, native-layout serialization,
// framework crypto dependency, or whole-message staging buffer.
class Sha256 {
  public:
    Sha256() : _h{0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19} {}
    void Update(const void *data, size_t size) {
        const auto *p = static_cast<const uint8_t *>(data);
        _bytes += size;
        while (size) {
            const size_t n = size < 64 - _used ? size : 64 - _used;
            std::memcpy(_buffer + _used, p, n); _used += n; p += n; size -= n;
            if (_used == 64) { Transform(); _used = 0; }
        }
    }
    void Final(uint8_t digest[32]) {
        const uint64_t bits = _bytes * 8;
        const uint8_t one = 0x80, zero = 0;
        Update(&one, 1);
        while (_used != 56) Update(&zero, 1);
        uint8_t length[8];
        for (unsigned i = 0; i < 8; ++i) length[7-i] = static_cast<uint8_t>(bits >> (8*i));
        Update(length, sizeof(length));
        for (unsigned i = 0; i < 8; ++i)
            for (unsigned j = 0; j < 4; ++j) digest[4*i+j] = static_cast<uint8_t>(_h[i] >> (24-8*j));
    }
  private:
    static uint32_t R(uint32_t x, unsigned n) { return (x >> n) | (x << (32-n)); }
    void Transform() {
        static constexpr uint32_t k[64] = {
            0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
            0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
            0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
            0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
            0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
            0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
            0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
            0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
        uint32_t w[16];
        for (unsigned i = 0; i < 16; ++i) w[i] = (uint32_t(_buffer[4*i])<<24)|(uint32_t(_buffer[4*i+1])<<16)|(uint32_t(_buffer[4*i+2])<<8)|_buffer[4*i+3];
        uint32_t a=_h[0], b=_h[1], c=_h[2], d=_h[3], e=_h[4], f=_h[5], g=_h[6], h=_h[7];
        for (unsigned i = 0; i < 64; ++i) {
            if (i >= 16) { const uint32_t x=w[(i+1)%16], y=w[(i+14)%16]; w[i%16] += (R(x,7)^R(x,18)^(x>>3)) + w[(i+9)%16] + (R(y,17)^R(y,19)^(y>>10)); }
            const uint32_t t1 = h+(R(e,6)^R(e,11)^R(e,25))+((e&f)^(~e&g))+k[i]+w[i%16];
            const uint32_t t2 = (R(a,2)^R(a,13)^R(a,22))+((a&b)^(a&c)^(b&c));
            h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
        }
        _h[0]+=a; _h[1]+=b; _h[2]+=c; _h[3]+=d; _h[4]+=e; _h[5]+=f; _h[6]+=g; _h[7]+=h;
    }
    uint32_t _h[8];
    uint64_t _bytes = 0;
    uint8_t _buffer[64] = {};
    size_t _used = 0;
};
