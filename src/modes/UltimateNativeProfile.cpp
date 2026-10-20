#include "modes/UltimateNativeProfile.hpp"
#include "core/Sha256.hpp"
#include <pb_decode.h>
#include <pb_encode.h>
#include <cstring>

namespace ultimate_native {
uint16_t Read16(const uint8_t *p) { return uint16_t(p[0]) | uint16_t(p[1]) << 8; }
namespace {
CandidateWorkspace candidate;
PayloadLease candidate_lease;
bool Token(uint16_t t, uint8_t roles, bool directions, bool digital) {
    if (t == 0 || t == kTrue) return true;
    const uint16_t kind = t & 0xf000, id = t & 0xfff;
    if (kind <= 0x2000) return id >= 1 && id <= 60;
    if (kind == 0x3000) return id >= 1 && id <= roles;
    if (kind == 0x4000) return directions && id >= 1 && id <= 8;
    return digital && kind == 0x5000 && id >= 1 && id <= 12;
}
bool Zero(const uint8_t *p, size_t n) { for (size_t i = 0; i < n; ++i) if (p[i]) return false; return true; }
bool Winner(uint8_t t) { return t < 28 || t == 255; }
bool Priority(uint32_t seen[8], uint8_t p) {
    if (!p || (seen[p / 32] & (uint32_t{1} << (p % 32)))) return false;
    seen[p / 32] |= uint32_t{1} << (p % 32); return true;
}
bool Encode(pb_ostream_t *stream, const pb_field_t *field, void *const *arg) {
    const auto *lease = static_cast<const PayloadLease *>(*arg);
    return lease && lease->live && lease->bytes && lease->size <= kBodyMax &&
        pb_encode_tag_for_field(stream, field) && pb_encode_string(stream, lease->bytes, lease->size);
}
bool Decode(pb_istream_t *stream, const pb_field_t *, void **arg) {
    auto *lease = static_cast<PayloadLease *>(*arg);
    // The prior presence scan establishes the precise immutable slice. Consume
    // and compare synchronously, without deriving ownership from stream.state.
    if (!lease || !lease->live || stream->bytes_left != lease->size) return false;
    uint8_t bytes[32]; size_t offset = 0;
    while (stream->bytes_left) {
        const size_t n = stream->bytes_left < sizeof(bytes) ? stream->bytes_left : sizeof(bytes);
        if (!pb_read(stream, bytes, n) || std::memcmp(bytes, lease->bytes + offset, n)) return false;
        offset += n;
    }
    return true;
}
struct Cursor {
    const uint8_t *p; size_t n;
    bool Var(uint32_t &v) {
        v = 0;
        for (unsigned i = 0; i < 5; ++i) {
            if (!n) return false;
            uint8_t b = *p++; --n;
            if (i == 4 && b > 15) return false;
            v |= uint32_t(b & 127) << (7*i);
            if (!(b & 128)) return true;
        }
        return false;
    }
    bool Field(uint32_t &tag, uint8_t &wire, const uint8_t *&value, size_t &size, uint32_t &scalar) {
        uint32_t key;
        if (!Var(key) || !(tag = key >> 3)) return false;
        wire = key & 7; value = p; scalar = 0; size = 0;
        if (wire == 0) { // unknown/request uint64 fields remain legal
            for (unsigned i=0; i<10; ++i) {
                if (!n) return false;
                uint8_t b=*p++; --n;
                if (i==9 && b>1) return false;
                if (i<5) scalar |= uint32_t(b&127) << (7*i);
                if (!(b&128)) return true;
            }
            return false;
        }
        if (wire == 2) { uint32_t length; if (!Var(length)) return false; size = length; }
        else if (wire == 1) size = 8;
        else if (wire == 5) size = 4;
        else return false;
        if (size > n) return false;
        value=p; p+=size; n-=size; return true;
    }
};
bool ScanProfile(const uint8_t *bytes, size_t size, PayloadLease &lease) {
    lease.Release(); Cursor c{bytes,size}; uint32_t schema=0; bool seen_schema=false, native=false, legacy=false;
    while(c.n) {
        uint32_t tag,v; uint8_t wire; const uint8_t *data; size_t n;
        if(!c.Field(tag,wire,data,n,v)) return false;
        if(tag==1) { if(wire!=0 || seen_schema) return false; schema=v;seen_schema=true; }
        if(tag>=2 && tag<=7) legacy=true;
        if(tag==8) {
            if(wire!=2 || native || !n || n>kBodyMax) return false;
            lease.bytes=data;lease.size=n;native=true;
        }
        // Schema 5 is closed. Legacy unknown fields retain prior protobuf behavior.
        if(tag>8 && schema==kSchema) return false;
    }
    if(schema==kSchema) { if(!native || legacy) return false; lease.live=true; return true; }
    lease.Release(); return !native;
}
}
bool Prepare(const uint8_t *b, size_t n, uint32_t generation, PreparedView &v) {
    v.valid=false;
    if(!b || n<608 || n>kBodyMax || std::memcmp(b,"GNP5",4) || Read16(b+4)!=kEncoding ||
       Read16(b+6)!=kEngineAbi || Read16(b+8)!=n || Read16(b+94)) return false;
    const uint8_t count=b[10],early=b[11],sources=b[12],rules=b[13],bindings=b[14],effects=b[15];
    if(count>96 || early>count || !sources || sources>8 || rules>32 || bindings>32 || effects>16 ||
       b[16]>=28 || !b[17] || b[17]>sources || !b[18] || b[18]>sources || b[19]>7 || Read16(b+92)>768) return false;
    const size_t expected=608+size_t(count)*3+size_t(Read16(b+92))*2+size_t(sources)*9+
        size_t(rules)*4+size_t(bindings)*6+size_t(effects)*32;
    if(expected!=n) return false;
    uint16_t offset=600+count*3,used=0;
    for(uint8_t i=0;i<count;++i) {
        const uint8_t *p=b+600+i*3; const uint16_t packed=Read16(p+1);
        const uint8_t a=packed&3,any=(packed>>2)&7,none=(packed>>5)&15;
        if(p[0]!=i+1 || (packed>>9) || a>2 || any>4 || none>9) return false;
        const uint16_t total=a+any+none;
        if(used+total>Read16(b+92)) return false;
        v.condition_token_offsets[i]=offset;v.all_counts[i]=a;v.any_counts[i]=any;v.none_counts[i]=none;
        for(uint8_t j=0;j<total;++j) if(!Token(Read16(b+offset+j*2),i,i>=early,false)) return false;
        offset+=total*2;used+=total;
    }
    if(used!=Read16(b+92)) return false;
    v.source_offset=offset;
    for(uint8_t i=0;i<sources;++i,offset+=9) {
        const uint8_t *p=b+offset;
        if(p[0]!=i+1) return false;
        const bool base=i+1==b[17] || i+1==b[18];
        for(uint8_t j=0;j<4;++j) if(!Token(Read16(p+1+j*2),base?early:count,!base,false)) return false;
    }
    // Six compact priority bitsets; no large local matrices or recursion.
    uint32_t priorities[5][8] = {};
    v.rule_offset=offset;
    for(uint8_t i=0;i<rules;++i,offset+=4) {
        const uint8_t *p=b+offset;
        if(!Priority(priorities[0],p[0]) || p[1]>=28 || !Token(Read16(p+2),count,true,false)) return false;
    }
    v.binding_offset=offset;
    for(uint8_t i=0;i<bindings;++i,offset+=6) {
        const uint8_t *p=b+offset;
        if(!Token(Read16(p),count,true,false) || (Read16(p+2)&~0xfff) || !Winner(p[4]) || p[5]) return false;
    }
    v.effect_offset=offset;
    for(uint8_t i=0;i<effects;++i,offset+=32) {
        const uint8_t *p=b+offset; const uint8_t target=p[0],mode=p[7];
        if(target<1 || target>5 || !Token(Read16(p+2),count,true,true) || !Token(Read16(p+4),count,true,true) ||
           !Winner(p[28]) || (p[29]&~3) || Read16(p+30)) return false;
        if(target==5) { if(!Priority(priorities[1],p[1]) || !Priority(priorities[2],p[1])) return false; }
        else if(!Priority(priorities[target],p[1])) return false;
        if(target==3 || target==4) {
            if(p[6] || mode || p[8] || p[9] || !Zero(p+11,17) || (p[29]&2)) return false;
        } else {
            if(!p[6] || p[6]>sources || mode<1 || mode>4) return false;
            if(mode==1 && (p[8] || p[9] || !Zero(p+10,18))) return false;
            if(mode==2 && (p[8]>=28 || p[9]>=28 || !Zero(p+10,18))) return false;
            if(mode==3 && (p[8] || p[9] || !Zero(p+12,16))) return false;
            if(mode==4 && (p[8] || p[9])) return false;
        }
    }
    v.mask_offset=offset;
    if(!Token(Read16(b+offset),count,true,false) || ((Read16(b+offset+2)|Read16(b+offset+4))&~0xfff) ||
       (Read16(b+offset+2)&Read16(b+offset+4)) || Read16(b+offset+6)>1) return false;
    for(uint8_t j=0;j<4;++j) if(!Token(Read16(b+20+j*2),count,true,false)) return false;
    v.body=b;v.body_length=n;v.generation=generation;v.condition_count=count;v.early_condition_count=early;
    v.source_count=sources;v.rule_count=rules;v.binding_count=bindings;v.effect_count=effects;
    v.default_table=b[16];v.ls_source=b[17];v.rs_source=b[18];v.dpad_flags=b[19];
    v.mode_gate=Read16(b+20);v.ls_digital_gate=Read16(b+22);v.rs_digital_gate=Read16(b+24);v.dpad_gate=Read16(b+26);
    v.engine_abi=kEngineAbi;Sha256 hash;hash.Update(b,n);hash.Final(v.body_digest);v.valid=true;return true;
}
bool CopyProgram(const PreparedView &source, OwnedProgram &out, uint32_t generation) {
    if(!source.valid || !source.body || source.body_length>kBodyMax) return false;
    std::memmove(out.body,source.body,source.body_length);out.view=source;
    out.view.body=out.body;out.view.generation=generation;return true;
}
bool ContextDigest(const GameModeConfig &c, uint8_t digest[32]) {
    if(c.mode_id!=MODE_ULTIMATE || c.button_remapping_count>sizeof(c.button_remapping)/sizeof(c.button_remapping[0]) ||
       c.socd_pairs_count>sizeof(c.socd_pairs)/sizeof(c.socd_pairs[0])) return false;
    Sha256 h;static constexpr char domain[]="Glyph.Native.Preprocess.v1";h.Update(domain,sizeof(domain));
    uint8_t v[3]={uint8_t(c.mode_id),uint8_t(uint16_t(c.mode_id)>>8),uint8_t(c.button_remapping_count)};h.Update(v,3);
    for(size_t i=0;i<c.button_remapping_count;++i) {
        const auto &r=c.button_remapping[i];
        if(r.physical_button<1 || r.physical_button>60 || r.activates<1 || r.activates>60) return false;
        v[0]=r.physical_button;v[1]=r.activates;h.Update(v,2);
    }
    v[0]=c.socd_pairs_count;h.Update(v,1);
    for(size_t i=0;i<c.socd_pairs_count;++i) {
        const auto &s=c.socd_pairs[i];
        if(s.button_dir1<1 || s.button_dir1>60 || s.button_dir2<1 || s.button_dir2>60 || s.socd_type>4) return false;
        v[0]=s.button_dir1;v[1]=s.button_dir2;v[2]=s.socd_type;h.Update(v,3);
    }
    h.Final(digest);return true;
}
bool ContextMatches(const PreparedView &v,const GameModeConfig &c) { uint8_t digest[32];return v.valid && ContextDigest(c,digest) && !std::memcmp(digest,v.body+28,32); }
const PayloadLease *Lease(const UltimateProfile &p) { return p.native_payload.funcs.encode==Encode?static_cast<const PayloadLease *>(p.native_payload.arg):nullptr; }
void Bind(UltimateProfile &p,PayloadLease &l) { p.native_payload.funcs.encode=Encode;p.native_payload.arg=&l; }
bool BindOwned(UltimateProfile &p,const OwnedProgram &o,PayloadLease &l) {
    l.Release();if(!o.view.valid || o.view.body!=o.body) return false;
    l.bytes=o.body;l.size=o.view.body_length;l.live=true;Bind(p,l);return true;
}
bool ValidProfile(const UltimateProfile &p) {
    if(p.schema_version!=kSchema || p.tables_count || p.roles_count || p.routing_slots_count || p.default_table_id || p.table_rules_count || p.has_output_program) return false;
    const auto *l=Lease(p);
    if(!l || !l->live || !l->bytes || l->size>kBodyMax || !Prepare(l->bytes,l->size,1,candidate.program.view)) return false;
    return CopyProgram(candidate.program.view,candidate.program,1);
}
const PreparedView &CandidateView() { return candidate.program.view; }
bool PreserveProfile(UltimateProfile &p) {
    if(p.schema_version!=kSchema) return true;
    return ValidProfile(p) && BindOwned(p,candidate.program,candidate_lease);
}
bool DecodeProfile(const uint8_t *bytes,size_t size,UltimateProfile &p,PayloadLease &l) {
    p=UltimateProfile_init_default;if(!ScanProfile(bytes,size,l)) return false;
    if(l.live) { p.native_payload.funcs.decode=Decode;p.native_payload.arg=&l; }
    else p.native_payload.funcs.decode=RejectPayload;
    auto stream=pb_istream_from_buffer(bytes,size);
    if(!pb_decode(&stream,UltimateProfile_fields,&p) || stream.bytes_left) {l.Release();return false;}
    if(l.live) Bind(p,l);else p.native_payload={};
    return true;
}
bool PrepareRequest(const uint8_t *bytes,size_t size,ProfileStoreRequest &request,PayloadLease &l) {
    l.Release();Cursor c{bytes,size};bool seen=false;
    while(c.n) {
        uint32_t tag,v;uint8_t wire;const uint8_t *data;size_t n;
        if(!c.Field(tag,wire,data,n,v)) return false;
        if(tag==ProfileStoreRequest_profile_tag) {
            if(seen || wire!=2 || !ScanProfile(data,n,l)) return false;
            seen=true;
        }
    }
    request.profile.native_payload.funcs.decode=l.live?Decode:RejectPayload;
    request.profile.native_payload.arg=l.live?&l:nullptr;return true;
}
bool RejectPayload(pb_istream_t *,const pb_field_t *,void **) { return false; }
void RejectEmbedded(Config &c) { for(auto &p:c.ultimate_profiles) {p.native_payload.funcs.decode=RejectPayload;p.native_payload.arg=nullptr;} }
void ClearEmbeddedCallbacks(Config &c) { for(auto &p:c.ultimate_profiles) p.native_payload={}; }
} // namespace ultimate_native
