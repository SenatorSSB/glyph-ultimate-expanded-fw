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

def check_source_order(source):
    opening=source[source.index('inline bool begin('):source.index('public:')]
    initial=source[source.index('inline void Initial('):source.index('inline void Return(')]
    returning=source[source.index('inline void Return('):source.index('    void ReadInto(')]
    reader=source[source.index('    void ReadInto('):source.index('\n};',source.index('    void ReadInto('))]
    # Both ordinary openings and the terminal flags-only publication retain
    # odd-before-release-fence. All payload is enclosed by begin/end helpers.
    assert opening.count('seq.store(sequence+1u,std::memory_order_relaxed);')==2
    assert opening.count('std::atomic_thread_fence(std::memory_order_release);')==2
    assert opening.index('seq.store(sequence+1u,std::memory_order_relaxed);')<opening.index('std::atomic_thread_fence(std::memory_order_release);')<opening.index('flag(SequenceExhausted);')<opening.index('seq.store(sequence+2u,std::memory_order_release);')
    assert 'sequence>=UINT32_MAX-3u' in opening and 'sequence==UINT32_MAX-3u' in opening
    assert 'inline void end(uint32_t sequence){seq.store(sequence+2u,std::memory_order_release);}' in opening
    for writer,payload in ((initial,'const uint32_t id=bump(entries,EntriesOverflow);'),(returning,'bump(returns,ReturnsOverflow);')):
        assert writer.index('if(!begin(sequence))return;')<writer.index(payload)<writer.index('end(sequence);')
    assert reader.index('seq.load(std::memory_order_acquire)')<reader.index('s.entries=entries.load(std::memory_order_relaxed)')<reader.index('std::atomic_thread_fence(std::memory_order_acquire);')<reader.index('seq.load(std::memory_order_relaxed)')
    assert opening.rindex('seq.store(sequence+1u,std::memory_order_relaxed);')<opening.rindex('std::atomic_thread_fence(std::memory_order_release);')

def main():
    source=(ROOT/'include/core/RecoveryPrivateDcdDiagnostics.hpp').read_text()
    check_source_order(source)
    source_controls={
        'writer_fence':source.replace('std::atomic_thread_fence(std::memory_order_release);',''),
        'reader_fence':source.replace('std::atomic_thread_fence(std::memory_order_acquire);',''),
        'begin_acquire':source.replace('seq.load(std::memory_order_acquire)','seq.load(std::memory_order_relaxed)'),
        'final_release':source.replace('seq.store(sequence+2u,std::memory_order_release);','seq.store(sequence+2u,std::memory_order_relaxed);'),
        'sequence_guard':source.replace('sequence>=UINT32_MAX-3u','sequence>UINT32_MAX-3u'),
    }
    for name,changed in source_controls.items():
        try:check_source_order(changed)
        except (AssertionError,ValueError):pass
        else:raise AssertionError('source-order negative accepted: '+name)
    accepted,bad=outcomes();assert len(accepted)==3 and not bad
    controls={}
    for missing in ('writer_fence','reader_fence','final_release','begin_acquire'):
        allowed,torn=outcomes(**{missing:False});assert len(allowed)==14 and len(torn)==11
        controls[missing]={'accepted':len(allowed),'incoherent':len(torn),'witness':torn[0]}
    result={'status':'PASS','model':'derived-axiom finite RF illustration; not independent C++ model checker','assignments':225,'coherent_accepted':len(accepted),'incoherent_accepted':len(bad),'missing_order_controls':controls,'assumptions':['serialized sole writer','atomic aligned uint32 data','sequence terminal guard prevents wrap/ABA'],'production_source_order_checked':True,'source_order_negative_controls':list(source_controls)}
    print(json.dumps(result,sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
