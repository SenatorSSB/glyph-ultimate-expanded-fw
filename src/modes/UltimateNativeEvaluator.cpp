#include "modes/UltimateNativeEvaluator.hpp"

namespace ultimate_native {
namespace {
bool Value(uint16_t t,const ResolvedInputContext &c,const FrameState &f) {
    if(t==0) return false;
    if(t==kTrue) return true;
    const uint16_t id=t&0xfff;
    switch(t&0xf000) {
        case 0: return (c.original.buttons & (uint64_t{1}<<(id-1)))!=0;
        case 0x1000: return (c.remapped.buttons & (uint64_t{1}<<(id-1)))!=0;
        case 0x2000: return (c.post.buttons & (uint64_t{1}<<(id-1)))!=0;
        case 0x3000: return f.roles[id-1];
        case 0x4000: return f.cardinal_activations[id-1];
        case 0x5000: return (f.buttons & (uint32_t{1}<<(id-1)))!=0;
        default: return false; // Preparation rejects this vocabulary.
    }
}
void Conditions(uint8_t first,uint8_t end,const ResolvedInputContext &c,FrameState &f) {
    const auto &v=*f.program;
    for(uint8_t i=first;i<end;++i) {
        const uint8_t *p=v.body+v.condition_token_offsets[i];bool active=true,any=false;
        for(uint8_t j=0;j<v.all_counts[i];++j,p+=2) active=Value(Read16(p),c,f)&&active;
        for(uint8_t j=0;j<v.any_counts[i];++j,p+=2) any=Value(Read16(p),c,f)||any;
        active=active&&(!v.any_counts[i]||any);
        for(uint8_t j=0;j<v.none_counts[i];++j,p+=2) active=!Value(Read16(p),c,f)&&active;
        f.roles[i]=active;
    }
}
void Source(uint8_t id,const ResolvedInputContext &c,const FrameState &f,bool out[4]) {
    const uint8_t *p=f.program->body+f.program->source_offset+(id-1)*9+1;
    for(uint8_t i=0;i<4;++i) out[i]=Value(Read16(p+i*2),c,f);
}
void Axes(uint8_t id,const ResolvedInputContext &c,const FrameState &f,int8_t &x,int8_t &y) {
    bool cardinal[4];Source(id,c,f,cardinal);
    x=cardinal[0]?-1:cardinal[1]?1:0;y=cardinal[2]?-1:cardinal[3]?1:0;
}
bool Filter(uint8_t winner,const FrameState &f) {return winner==255||winner==f.selected_table;}
}
void Neutral(OutputState &o) { o.buttons=0;o.leftStickX=o.leftStickY=o.rightStickX=o.rightStickY=128;o.triggerLAnalog=o.triggerRAnalog=0; }
bool Evaluate(const PreparedView &v,const ResolvedInputContext &c,ControllerMode &mode,OutputState &o) {
    if(!IsOwnedView(v) || !v.published || v.engine_abi!=kEngineAbi) {Neutral(o);return false;}
    FrameState f{};f.program=&v;f.generation=v.generation;f.selected_table=v.default_table;
    Conditions(0,v.early_condition_count,c,f);
    Source(v.ls_source,c,f,f.cardinal_activations);Source(v.rs_source,c,f,f.cardinal_activations+4);
    mode.UpdateDirections(f.cardinal_activations[0],f.cardinal_activations[1],f.cardinal_activations[2],f.cardinal_activations[3],
        f.cardinal_activations[4],f.cardinal_activations[5],f.cardinal_activations[6],f.cardinal_activations[7],28,128,228,o);
    Conditions(v.early_condition_count,v.condition_count,c,f);
    for(uint8_t i=0;i<v.rule_count;++i) {
        const uint8_t *p=v.body+v.rule_offset+i*4;
        if(p[0]<f.table_priority && Value(Read16(p+2),c,f)) {f.table_priority=p[0];f.selected_table=p[1];}
    }
    for(uint8_t i=0;i<v.binding_count;++i) {
        const uint8_t *p=v.body+v.binding_offset+i*6;
        if(Filter(p[4],f)&&Value(Read16(p),c,f)) f.buttons|=Read16(p+2);
    }
    if(Value(Read16(v.body+v.mask_offset),c,f)!=(Read16(v.body+v.mask_offset+6)!=0))
        f.buttons=(f.buttons&~Read16(v.body+v.mask_offset+4))|Read16(v.body+v.mask_offset+2);
    // Legacy leaves only these bits unowned. Every ordinary native-owned bit
    // is assigned once per frame, including clicks/directions/modifiers.
    o.buttons=(o.buttons&0xf0030000u)|f.buttons;
    f.ls_route_bypass=Value(v.dpad_gate,c,f)&&(v.dpad_flags&2);
    if((v.dpad_flags&1)&&Value(v.dpad_gate,c,f)) {
        o.dpadLeft=f.cardinal_activations[0];o.dpadRight=f.cardinal_activations[1];
        o.dpadDown=f.cardinal_activations[2];o.dpadUp=f.cardinal_activations[3];
    }
    if(Value(v.ls_digital_gate,c,f)&&!((v.dpad_flags&4)&&Value(v.dpad_gate,c,f))) {
        o.leftStickLeft=f.cardinal_activations[0];o.leftStickRight=f.cardinal_activations[1];
        o.leftStickDown=f.cardinal_activations[2];o.leftStickUp=f.cardinal_activations[3];
    }
    if(Value(v.rs_digital_gate,c,f)) {
        o.rightStickLeft=f.cardinal_activations[4];o.rightStickRight=f.cardinal_activations[5];
        o.rightStickDown=f.cardinal_activations[6];o.rightStickUp=f.cardinal_activations[7];
    }
    o.triggerLAnalog=o.triggerRAnalog=0;
    for(uint8_t i=0;i<v.effect_count;++i) {
        const uint8_t *p=v.body+v.effect_offset+i*32;const uint8_t target=p[0],priority=p[1];
        if(!Filter(p[28],f) || ((p[29]&2)&&f.ls_route_bypass) || !Value(Read16(p+2),c,f) ||
           Value(Read16(p+4),c,f)==((p[29]&1)!=0)) continue;
        if(target==3) {if(priority<f.left_trigger_priority) {f.left_trigger_priority=priority;o.triggerLAnalog=p[10];}continue;}
        if(target==4) {if(priority<f.right_trigger_priority) {f.right_trigger_priority=priority;o.triggerRAnalog=p[10];}continue;}
        Axes(p[6],c,f,f.x,f.y);const uint8_t index=(f.y+1)*3+f.x+1;
        const uint8_t *point;
        if(p[7]==3) point=p+10;
        else if(p[7]==4) point=p+10+index*2;
        else {
            const uint8_t table=p[7]==1?f.selected_table:Value(v.mode_gate,c,f)?p[9]:p[8];
            point=v.body+v.table_offset+table*18+index*2;
        }
        if((target==1||target==5)&&priority<f.ls_priority) {f.ls_priority=priority;o.leftStickX=point[0];o.leftStickY=point[1];}
        if((target==2||target==5)&&priority<f.rs_priority) {f.rs_priority=priority;o.rightStickX=point[0];o.rightStickY=point[1];}
    }
    // Preserve the source-backed tail after all native effects, using original
    // post-SOCD Nunchuk bytes, and RS activations before opposing-axis reduction.
    if(c.post.nunchuk_c) {
        o.dpadLeft|=f.cardinal_activations[4];o.dpadRight|=f.cardinal_activations[5];
        o.dpadDown|=f.cardinal_activations[6];o.dpadUp|=f.cardinal_activations[7];
        o.rightStickX=o.rightStickY=128;
    }
    if(c.post.nunchuk_connected) {o.leftStickX=c.post.nunchuk_x;o.leftStickY=c.post.nunchuk_y;}
    if(v.generation!=f.generation || !v.valid || f.program!=&v) {Neutral(o);return false;}
    return true;
}
static_assert(sizeof(FrameState)<=144,"native frame budget");
} // namespace ultimate_native
