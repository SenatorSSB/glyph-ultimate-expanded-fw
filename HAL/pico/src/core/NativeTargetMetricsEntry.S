.syntax unified
.cpu cortex-m0plus
.thumb

// No push, C call or active-frame paint. Only caller-clobbered r0-r3/ip
// are touched; LR and callee-saved registers reach the real entry unchanged.
.macro OWN_CORE_ENTRY name, bottom, top, stateoffset, target
.section .text.\name,"ax",%progbits
.global \name
.type \name,%function
.thumb_func
\name:
    ldr r0, =\bottom
    ldr r1, =\top
    mov r2, sp
    movs r3, #7
    tst r2, r3
    bne 9f
    tst r0, r3
    bne 9f
    tst r1, r3
    bne 9f
    subs r3, r1, r0
    movs r1, #128
    lsls r1, r1, #4
    cmp r3, r1
    bne 9f
    ldr r1, =\top
    adds r3, r0, #0
    adds r3, #32
    cmp r2, r3
    blo 9f
    cmp r2, r1
    bhi 9f
    mrs r3, PRIMASK
    mov ip, r3
    cpsid i
    ldr r3, =glyph_native_metric_scans + \stateoffset
    str r0, [r3, #0]
    adds r0, #32
    str r0, [r3, #4]
    str r1, [r3, #8]
    str r2, [r3, #12]
    str r2, [r3, #16]
    str r1, [r3, #20]
    str r0, [r3, #24]
    movs r1, #25
    str r1, [r3, #36]
    ldr r1, =0xade175c3
1:
    cmp r0, r2
    bhs 2f
    str r1, [r0]
    adds r0, #4
    b 1b
2:
    mov r3, ip
    msr PRIMASK, r3
    ldr r0, =\target
    bx r0
9:
    ldr r0, =glyph_native_metric_scans + \stateoffset
    movs r1, #20
    str r1, [r0, #36]
    ldr r0, =\target
    bx r0
.size \name, .-\name
.endm

OWN_CORE_ENTRY __wrap_main, __StackBottom, __StackTop, 0, __real_main
OWN_CORE_ENTRY GlyphNativeMetricCore1Entry, __StackOneBottom, __StackOneTop, 48, main1

.section .text.__wrap_multicore_launch_core1,"ax",%progbits
.global __wrap_multicore_launch_core1
.type __wrap_multicore_launch_core1,%function
.thumb_func
__wrap_multicore_launch_core1:
    ldr r1, =main1
    cmp r0, r1
    bne 1f
    ldr r0, =GlyphNativeMetricCore1Entry
    ldr r1, =__real_multicore_launch_core1
    bx r1
1:
    // An unexpected launch is passed through unchanged, with observation
    // explicitly invalid. No arbitrary entry pointer is retained or called.
    ldr r1, =glyph_native_metric_scans + 48
    movs r2, #4
    str r2, [r1, #36]
    ldr r1, =__real_multicore_launch_core1
    bx r1
.size __wrap_multicore_launch_core1, .-__wrap_multicore_launch_core1
