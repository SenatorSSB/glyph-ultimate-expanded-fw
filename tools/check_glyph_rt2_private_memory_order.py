#!/usr/bin/env python3
"""Finite read-from illustration of the separately reviewed C++ fence proof.

This is a two-word/two-transaction derived-axiom model, not a C++ model checker
or physical RP2040 proof. Each data read names the transaction it reads from.
Sequence modification order is 0, odd1, even2, odd3, even4; a bounded reader
cannot span a full sequence wrap. Axioms derive from atomic coherence and the
release/acquire fence/publication edges documented in the timing audit.
"""
import itertools
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def outcomes(begin_acquire=True, final_release=True, writer_fence=True, reader_fence=True):
    accepted=[]
    for begin,end,x,y in itertools.product(range(5),range(5),range(3),range(3)):
        if begin&1 or begin!=end or end<begin:
            continue
        # Reading a closed release publication with acquire prevents older data.
        if begin_acquire and final_release and min(x,y)<begin//2:
            continue
        # A data store/read bridges release/acquire fences, making its preceding
        # odd seq store happen-before the ending seq load (write-read coherence).
        if writer_fence and reader_fence and any(end<2*v-1 for v in (x,y) if v):
            continue
        accepted.append((begin,end,x,y))
    bad=[v for v in accepted if v[2]!=v[0]//2 or v[3]!=v[0]//2]
    return accepted,bad

def main():
    source=(ROOT/'include/core/RecoveryPrivateDcdDiagnostics.hpp').read_text()
    writer=source[source.index('inline void Marker('):source.index('    void ReadInto(')]
    reader=source[source.index('    void ReadInto('):source.index('\n};',source.index('    void ReadInto('))]
    assert writer.index('seq.store(sequence+1u,std::memory_order_relaxed);')<writer.index('std::atomic_thread_fence(std::memory_order_release);')<writer.index('bump(calls);')<writer.index('seq.store(sequence+2u,std::memory_order_release);')
    assert reader.index('seq.load(std::memory_order_acquire)')<reader.index('s.entries=entries.load(std::memory_order_relaxed)')<reader.index('std::atomic_thread_fence(std::memory_order_acquire);')<reader.index('seq.load(std::memory_order_relaxed)')
    accepted,bad=outcomes();assert len(accepted)==3 and not bad
    controls={}
    for missing in ('writer_fence','reader_fence','final_release','begin_acquire'):
        allowed,torn=outcomes(**{missing:False});assert len(allowed)==14 and len(torn)==11
        controls[missing]={'accepted':len(allowed),'incoherent':len(torn),'witness':torn[0]}
    result={'status':'PASS','model':'derived-axiom finite RF illustration; not independent C++ model checker','assignments':225,'coherent_accepted':len(accepted),'incoherent_accepted':len(bad),'missing_order_controls':controls,'assumptions':['serialized sole writer','atomic aligned uint32 data','no full seq wrap during bounded read'],'production_source_order_checked':True}
    print(json.dumps(result,sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
