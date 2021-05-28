.mem __static_2__malloc_end 8 RW
    .data 8 "\x00"
.mem __static_1__malloc_start 8 RW
    .data 8 "\x00"
.mem __static_4_counts 1 RW
    .data 16 "\x00"
.mem nj 8 RW
    .data 525032 "\x00"
.mem njZZ 1 RW
    .data 1 "\x00\x01\x08\x10\x09\x02\x03\n\x11\x18 \x19\x12\x0b\x04\x05\x0c\x13\x1a!(0)\"\x1b\x14\x0d\x06\x07\x0e\x15\x1c#*1892+$\x1d\x16\x0f\x17\x1e%,3:;4-&\x1f'.5<=6/7>?"
.mem string_const_1 4 RO
    .data 1 "Usage: nanojpeg <input.jpg> <output.ppm>\x00"
.mem string_const_2 4 RO
    .data 1 "Error opening the input file.\x00"
.mem string_const_3 4 RO
    .data 1 "Error decoding the input file.\x00"
.mem string_const_4 4 RO
    .data 1 "Error opening the output file.\x00"
.mem string_const_5 4 RO
    .data 1 "P6\n\x00"
.mem string_const_6 4 RO
    .data 1 "P5\n\x00"
.mem string_const_7 4 RO
    .data 1 " \x00"
.mem string_const_8 4 RO
    .data 1 "\n\x00"
.mem string_const_9 4 RO
    .data 1 "255\n\x00"

.fun exit BUILTIN [] = [S32]

.fun xbrk BUILTIN [A64] = [A64]

.fun open BUILTIN [S32] = [A64 S32 S32]

.fun close BUILTIN [S32] = [S32]

.fun write BUILTIN [S64] = [S32 A64 U64]

.fun read BUILTIN [S64] = [S32 A64 U64]

.fun lseek BUILTIN [S64] = [S32 S64 S32]

.fun raise BUILTIN [S32] = [S32]

.fun kill BUILTIN [S32] = [S32 S32]

.fun getpid BUILTIN [S32] = []

.fun write_s NORMAL [S64] = [S32 A64]
.reg S8 [%S8_3]
.reg S32 [%S32_4 fd]
.reg S64 [%S64_5 %out]
.reg U64 [%U64_1 len]
.reg A64 [%A64_2 s]
.bbl %start
    poparg fd
    poparg s
    mov len 0
    bra while_1_cond
.bbl while_1
    add %U64_1 len 1
    mov len %U64_1
.bbl while_1_cond
    lea %A64_2 s len
    ld %S8_3 %A64_2 0
    conv %S32_4 %S8_3
    bne %S32_4 0 while_1
    bra while_1_exit
.bbl while_1_exit
    pusharg len
    pusharg s
    pusharg fd
    bsr write
    poparg %S64_5
    mov %out %S64_5
    pusharg %out
    ret

.fun write_x NORMAL [S64] = [S32 U32]
.reg S8 [%S8_11 %S8_5]
.reg S32 [%S32_8 fd]
.reg S64 [%S64_19 %out]
.reg U32 [%U32_10 %U32_14 %U32_3 %U32_4 %U32_9 digit val]
.reg U64 [%U64_18 %U64_2 pos]
.reg A64 [%A64_1 %A64_12 %A64_13 %A64_15 %A64_16 %A64_17 %A64_6 %A64_7]
.stk buffer 1 16
.bbl %start
    poparg fd
    poparg val
    lea.stk %A64_1 buffer 0
    mov pos 16
.bbl while_1
    sub %U64_2 pos 1
    mov pos %U64_2
    rem %U32_3 val 16
    mov digit %U32_3
    ble digit 9 if_2_true
    bra if_2_false
.bbl if_2_true
    add %U32_4 48 digit
    conv %S8_5 %U32_4
    lea.stk %A64_6 buffer 0
    lea %A64_7 %A64_6 pos
    st %A64_7 0 %S8_5
    bra if_2_end
.bbl if_2_false
    sub %S32_8 97 10
    conv %U32_9 %S32_8
    add %U32_10 %U32_9 digit
    conv %S8_11 %U32_10
    lea.stk %A64_12 buffer 0
    lea %A64_13 %A64_12 pos
    st %A64_13 0 %S8_11
.bbl if_2_end
    div %U32_14 val 16
    mov val %U32_14
.bbl while_1_cond
    bne val 0 while_1
    bra while_1_exit
.bbl while_1_exit
    lea.stk %A64_15 buffer 0
    lea %A64_16 %A64_15 pos
    lea.stk %A64_17 buffer 0
    sub %U64_18 16 pos
    pusharg %U64_18
    pusharg %A64_16
    pusharg fd
    bsr write
    poparg %S64_19
    mov %out %S64_19
    pusharg %out
    ret

.fun write_u NORMAL [S64] = [S32 U32]
.reg S8 [%S8_5]
.reg S32 [fd]
.reg S64 [%S64_13 %out]
.reg U32 [%U32_3 %U32_4 %U32_8 val]
.reg U64 [%U64_12 %U64_2 pos]
.reg A64 [%A64_1 %A64_10 %A64_11 %A64_6 %A64_7 %A64_9]
.stk buffer 1 16
.bbl %start
    poparg fd
    poparg val
    lea.stk %A64_1 buffer 0
    mov pos 16
.bbl while_1
    sub %U64_2 pos 1
    mov pos %U64_2
    rem %U32_3 val 10
    add %U32_4 48 %U32_3
    conv %S8_5 %U32_4
    lea.stk %A64_6 buffer 0
    lea %A64_7 %A64_6 pos
    st %A64_7 0 %S8_5
    div %U32_8 val 10
    mov val %U32_8
.bbl while_1_cond
    bne val 0 while_1
    bra while_1_exit
.bbl while_1_exit
    lea.stk %A64_9 buffer 0
    lea %A64_10 %A64_9 pos
    lea.stk %A64_11 buffer 0
    sub %U64_12 16 pos
    pusharg %U64_12
    pusharg %A64_10
    pusharg fd
    bsr write
    poparg %S64_13
    mov %out %S64_13
    pusharg %out
    ret

.fun write_d NORMAL [S64] = [S32 S32]
.reg S8 [%S8_16 %S8_9]
.reg S32 [%S32_3 fd sval]
.reg S64 [%S64_2 %S64_21 %out]
.reg U32 [%U32_1 %U32_12 %U32_4 %U32_7 %U32_8 val]
.reg U64 [%U64_13 %U64_20 %U64_6 pos]
.reg A64 [%A64_10 %A64_11 %A64_14 %A64_15 %A64_17 %A64_18 %A64_19 %A64_5]
.stk buffer 1 16
.bbl %start
    poparg fd
    poparg sval
    ble 0:S32 sval if_2_true
    bra if_2_end
.bbl if_2_true
    conv %U32_1 sval
    pusharg %U32_1
    pusharg fd
    bsr write_u
    poparg %S64_2
    mov %out %S64_2
    pusharg %out
    ret
.bbl if_2_end
    sub %S32_3 0 sval
    conv %U32_4 %S32_3
    mov val %U32_4
    lea.stk %A64_5 buffer 0
    mov pos 16
.bbl while_1
    sub %U64_6 pos 1
    mov pos %U64_6
    rem %U32_7 val 10
    add %U32_8 48 %U32_7
    conv %S8_9 %U32_8
    lea.stk %A64_10 buffer 0
    lea %A64_11 %A64_10 pos
    st %A64_11 0 %S8_9
    div %U32_12 val 10
    mov val %U32_12
.bbl while_1_cond
    bne val 0 while_1
    bra while_1_exit
.bbl while_1_exit
    sub %U64_13 pos 1
    mov pos %U64_13
    lea.stk %A64_14 buffer 0
    lea %A64_15 %A64_14 pos
    mov %S8_16 45
    st %A64_15 0 %S8_16
    lea.stk %A64_17 buffer 0
    lea %A64_18 %A64_17 pos
    lea.stk %A64_19 buffer 0
    sub %U64_20 16 pos
    pusharg %U64_20
    pusharg %A64_18
    pusharg fd
    bsr write
    poparg %S64_21
    mov %out %S64_21
    pusharg %out
    ret

.fun write_c NORMAL [S64] = [S32 U8]
.reg S8 [%S8_1]
.reg S32 [%S32_6 fd]
.reg S64 [%S64_4 %S64_7 %out]
.reg U8 [c]
.reg U64 [%U64_5]
.reg A64 [%A64_2 %A64_3]
.stk buffer 1 16
.bbl %start
    poparg fd
    poparg c
    conv %S8_1 c
    lea.stk %A64_2 buffer 0
    st %A64_2 0 %S8_1
    lea.stk %A64_3 buffer 0
    mov %U64_5 1
    pusharg %U64_5
    pusharg %A64_3
    pusharg fd
    bsr write
    poparg %S64_4
    conv %S32_6 %S64_4
    conv %S64_7 %S32_6
    mov %out %S64_7
    pusharg %out
    ret

.fun print_ln NORMAL [] = [A64 U64]
.reg S32 [%S32_2 %S32_4]
.reg S64 [%S64_1 %S64_3]
.reg U8 [%U8_5]
.reg U64 [n]
.reg A64 [s]
.bbl %start
    poparg s
    poparg n
    mov %S32_2 1
    pusharg n
    pusharg s
    pusharg %S32_2
    bsr write
    poparg %S64_1
    mov %S32_4 1
    mov %U8_5 10
    pusharg %U8_5
    pusharg %S32_4
    bsr write_c
    poparg %S64_3
    ret

.fun print_s_ln NORMAL [] = [A64]
.reg S32 [%S32_2 %S32_4]
.reg S64 [%S64_1 %S64_3]
.reg U8 [%U8_5]
.reg A64 [s]
.bbl %start
    poparg s
    mov %S32_2 1
    pusharg s
    pusharg %S32_2
    bsr write_s
    poparg %S64_1
    mov %S32_4 1
    mov %U8_5 10
    pusharg %U8_5
    pusharg %S32_4
    bsr write_c
    poparg %S64_3
    ret

.fun print_d_ln NORMAL [] = [S32]
.reg S32 [%S32_2 %S32_4 n]
.reg S64 [%S64_1 %S64_3]
.reg U8 [%U8_5]
.bbl %start
    poparg n
    mov %S32_2 1
    pusharg n
    pusharg %S32_2
    bsr write_d
    poparg %S64_1
    mov %S32_4 1
    mov %U8_5 10
    pusharg %U8_5
    pusharg %S32_4
    bsr write_c
    poparg %S64_3
    ret

.fun print_u_ln NORMAL [] = [U32]
.reg S32 [%S32_2 %S32_4]
.reg S64 [%S64_1 %S64_3]
.reg U8 [%U8_5]
.reg U32 [n]
.bbl %start
    poparg n
    mov %S32_2 1
    pusharg n
    pusharg %S32_2
    bsr write_u
    poparg %S64_1
    mov %S32_4 1
    mov %U8_5 10
    pusharg %U8_5
    pusharg %S32_4
    bsr write_c
    poparg %S64_3
    ret

.fun print_x_ln NORMAL [] = [U32]
.reg S32 [%S32_2 %S32_4]
.reg S64 [%S64_1 %S64_3]
.reg U8 [%U8_5]
.reg U32 [n]
.bbl %start
    poparg n
    mov %S32_2 1
    pusharg n
    pusharg %S32_2
    bsr write_x
    poparg %S64_1
    mov %S32_4 1
    mov %U8_5 10
    pusharg %U8_5
    pusharg %S32_4
    bsr write_c
    poparg %S64_3
    ret

.fun print_c_ln NORMAL [] = [U8]
.reg S32 [%S32_2 %S32_4]
.reg S64 [%S64_1 %S64_3]
.reg U8 [%U8_5 c]
.bbl %start
    poparg c
    mov %S32_2 1
    pusharg c
    pusharg %S32_2
    bsr write_c
    poparg %S64_1
    mov %S32_4 1
    mov %U8_5 10
    pusharg %U8_5
    pusharg %S32_4
    bsr write_c
    poparg %S64_3
    ret

.fun memset NORMAL [A64] = [A64 S32 U64]
.reg S8 [%S8_1]
.reg S32 [%S32_3 i value]
.reg U64 [%U64_4 n]
.reg A64 [%A64_2 %out ptr]
.bbl %start
    poparg ptr
    poparg value
    poparg n
    mov i 0
    bra for_1_cond
.bbl for_1
    conv %S8_1 value
    lea %A64_2 ptr i
    st %A64_2 0 %S8_1
.bbl for_1_next
    add %S32_3 i 1
    mov i %S32_3
.bbl for_1_cond
    conv %U64_4 i
    blt %U64_4 n for_1
    bra for_1_exit
.bbl for_1_exit
    mov %out ptr
    pusharg %out
    ret

.fun memcpy NORMAL [A64] = [A64 A64 U64]
.reg S8 [%S8_2]
.reg S32 [%S32_4 i]
.reg U64 [%U64_5 n]
.reg A64 [%A64_1 %A64_3 %out dst src]
.bbl %start
    poparg dst
    poparg src
    poparg n
    mov i 0
    bra for_1_cond
.bbl for_1
    lea %A64_1 src i
    ld %S8_2 %A64_1 0
    lea %A64_3 dst i
    st %A64_3 0 %S8_2
.bbl for_1_next
    add %S32_4 i 1
    mov i %S32_4
.bbl for_1_cond
    conv %U64_5 i
    blt %U64_5 n for_1
    bra for_1_exit
.bbl for_1_exit
    mov %out dst
    pusharg %out
    ret

.fun abort NORMAL [] = []
.reg S32 [%S32_1 %S32_2 %S32_3 %S32_4]
.bbl %start
    bsr getpid
    poparg %S32_1
    mov %S32_3 3
    pusharg %S32_3
    pusharg %S32_1
    bsr kill
    poparg %S32_2
    mov %S32_4 1
    pusharg %S32_4
    bsr exit
    ret

.fun malloc NORMAL [A64] = [U64]
.reg S32 [%S32_1]
.reg U64 [%U64_11 %U64_12 %U64_13 %U64_19 %U64_2 %U64_20 %U64_21 %U64_22 increment page_size rounded_size size]
.reg A64 [%A64_10 %A64_14 %A64_15 %A64_16 %A64_17 %A64_18 %A64_23 %A64_24 %A64_25 %A64_26 %A64_27 %A64_28 %A64_29 %A64_3 %A64_30 %A64_31 %A64_32 %A64_33 %A64_34 %A64_35 %A64_4 %A64_5 %A64_6 %A64_7 %A64_8 %A64_9 %out new_end result]
.bbl %start
    poparg size
    shl %S32_1 1 20
    conv %U64_2 %S32_1
    mov page_size %U64_2
    lea.mem %A64_3 __static_1__malloc_start 0
    ld %A64_4 %A64_3 0
    beq %A64_4 0 if_1_true
    bra if_1_end
.bbl if_1_true
    lea %A64_6 0 0
    pusharg %A64_6
    bsr xbrk
    poparg %A64_5
    lea.mem %A64_7 __static_1__malloc_start 0
    st %A64_7 0 %A64_5
    lea.mem %A64_8 __static_1__malloc_start 0
    ld %A64_9 %A64_8 0
    lea.mem %A64_10 __static_2__malloc_end 0
    st %A64_10 0 %A64_9
.bbl if_1_end
    add %U64_11 size 15
    div %U64_12 %U64_11 16
    mul %U64_13 %U64_12 16
    mov rounded_size %U64_13
    lea.mem %A64_14 __static_1__malloc_start 0
    ld %A64_15 %A64_14 0
    lea %A64_16 %A64_15 rounded_size
    lea.mem %A64_17 __static_2__malloc_end 0
    ld %A64_18 %A64_17 0
    blt %A64_18 %A64_16 if_3_true
    bra if_3_end
.bbl if_3_true
    add %U64_19 rounded_size page_size
    sub %U64_20 %U64_19 1
    div %U64_21 %U64_20 page_size
    mul %U64_22 %U64_21 page_size
    mov increment %U64_22
    lea.mem %A64_23 __static_2__malloc_end 0
    ld %A64_24 %A64_23 0
    lea %A64_25 %A64_24 increment
    mov new_end %A64_25
    pusharg new_end
    bsr xbrk
    poparg %A64_26
    lea.mem %A64_27 __static_2__malloc_end 0
    st %A64_27 0 %A64_26
    lea.mem %A64_28 __static_2__malloc_end 0
    ld %A64_29 %A64_28 0
    bne %A64_29 new_end if_2_true
    bra if_3_end
.bbl if_2_true
    bsr abort
.bbl if_3_end
    lea.mem %A64_30 __static_1__malloc_start 0
    ld %A64_31 %A64_30 0
    mov result %A64_31
    lea.mem %A64_32 __static_1__malloc_start 0
    ld %A64_33 %A64_32 0
    lea %A64_34 %A64_33 rounded_size
    lea.mem %A64_35 __static_1__malloc_start 0
    st %A64_35 0 %A64_34
    mov %out result
    pusharg %out
    ret

.fun free NORMAL [] = [A64]
.reg A64 [ptr]
.bbl %start
    poparg ptr
    ret

.fun mymemset NORMAL [] = [A64 S32 U64]
.reg S8 [%S8_1]
.reg S32 [%S32_3 i value]
.reg U64 [%U64_4 num]
.reg A64 [%A64_2 ptr]
.bbl %start
    poparg ptr
    poparg value
    poparg num
    mov i 0
    bra for_1_cond
.bbl for_1
    conv %S8_1 value
    lea %A64_2 ptr i
    st %A64_2 0 %S8_1
.bbl for_1_next
    add %S32_3 i 1
    mov i %S32_3
.bbl for_1_cond
    conv %U64_4 i
    blt %U64_4 num for_1
    bra for_1_exit
.bbl for_1_exit
    ret

.fun mymemcpy NORMAL [] = [A64 A64 U64]
.reg S8 [%S8_6]
.reg S32 [%S32_8 i]
.reg U64 [%U64_9 num]
.reg A64 [%A64_5 %A64_7 destination source]
.bbl %start
    poparg destination
    poparg source
    poparg num
    mov i 0
    bra for_1_cond
.bbl for_1
    lea %A64_5 source i
    ld %S8_6 %A64_5 0
    lea %A64_7 destination i
    st %A64_7 0 %S8_6
.bbl for_1_next
    add %S32_8 i 1
    mov i %S32_8
.bbl for_1_cond
    conv %U64_9 i
    blt %U64_9 num for_1
    bra for_1_exit
.bbl for_1_exit
    ret

.fun njGetWidth NORMAL [S32] = []
.reg S32 [%S32_12 %out]
.reg A64 [%A64_10 %A64_11]
.bbl %start
    lea.mem %A64_10 nj 0
    lea %A64_11 %A64_10 24
    ld %S32_12 %A64_11 0
    mov %out %S32_12
    pusharg %out
    ret

.fun njGetHeight NORMAL [S32] = []
.reg S32 [%S32_15 %out]
.reg A64 [%A64_13 %A64_14]
.bbl %start
    lea.mem %A64_13 nj 0
    lea %A64_14 %A64_13 28
    ld %S32_15 %A64_14 0
    mov %out %S32_15
    pusharg %out
    ret

.fun njIsColor NORMAL [S32] = []
.reg S32 [%out]
.reg U32 [%U32_18]
.reg A64 [%A64_16 %A64_17]
.bbl %start
    lea.mem %A64_16 nj 0
    lea %A64_17 %A64_16 48
    ld %U32_18 %A64_17 0
    bne %U32_18 1 if_1_true
    bra if_1_false
.bbl if_1_true
    mov %out 1
    pusharg %out
    ret
    bra if_1_end
.bbl if_1_false
    mov %out 0
    pusharg %out
    ret
.bbl if_1_end

.fun njGetImage NORMAL [A64] = []
.reg U32 [%U32_21]
.reg A64 [%A64_19 %A64_20 %A64_22 %A64_23 %A64_24 %A64_25 %A64_26 %A64_27 %A64_28 %out]
.bbl %start
    lea.mem %A64_19 nj 0
    lea %A64_20 %A64_19 48
    ld %U32_21 %A64_20 0
    beq %U32_21 1 if_1_true
    bra if_1_false
.bbl if_1_true
    lea.mem %A64_22 nj 0
    lea %A64_23 %A64_22 52
    lea %A64_24 %A64_23 40
    ld %A64_25 %A64_24 0
    mov %out %A64_25
    pusharg %out
    ret
    bra if_1_end
.bbl if_1_false
    lea.mem %A64_26 nj 0
    lea %A64_27 %A64_26 525020
    ld %A64_28 %A64_27 0
    mov %out %A64_28
    pusharg %out
    ret
.bbl if_1_end

.fun njGetImageSize NORMAL [S32] = []
.reg S32 [%S32_31 %S32_34 %S32_35 %S32_41 %out]
.reg U32 [%U32_36 %U32_39 %U32_40]
.reg A64 [%A64_29 %A64_30 %A64_32 %A64_33 %A64_37 %A64_38]
.bbl %start
    lea.mem %A64_29 nj 0
    lea %A64_30 %A64_29 24
    ld %S32_31 %A64_30 0
    lea.mem %A64_32 nj 0
    lea %A64_33 %A64_32 28
    ld %S32_34 %A64_33 0
    mul %S32_35 %S32_31 %S32_34
    conv %U32_36 %S32_35
    lea.mem %A64_37 nj 0
    lea %A64_38 %A64_37 48
    ld %U32_39 %A64_38 0
    mul %U32_40 %U32_36 %U32_39
    conv %S32_41 %U32_40
    mov %out %S32_41
    pusharg %out
    ret

.fun njClip NORMAL [U8] = [S32]
.reg S32 [x]
.reg U8 [%U8_42 %out]
.bbl %start
    poparg x
    blt x 0 if_2_true
    bra if_2_false
.bbl if_2_true
    mov %out 0
    pusharg %out
    ret
    bra if_2_end
.bbl if_2_false
    blt 255:S32 x if_1_true
    bra if_2_end
.bbl if_1_true
    mov %out 255
    pusharg %out
    ret
.bbl if_2_end
    conv %U8_42 x
    mov %out %U8_42
    pusharg %out
    ret

.fun njRowIDCT NORMAL [] = [A64]
.reg S32 [%S32_100 %S32_101 %S32_102 %S32_103 %S32_104 %S32_105 %S32_106 %S32_107 %S32_108 %S32_109 %S32_110 %S32_111 %S32_112 %S32_113 %S32_114 %S32_115 %S32_116 %S32_117 %S32_118 %S32_119 %S32_120 %S32_121 %S32_123 %S32_124 %S32_126 %S32_127 %S32_129 %S32_130 %S32_132 %S32_133 %S32_135 %S32_136 %S32_138 %S32_139 %S32_44 %S32_45 %S32_47 %S32_48 %S32_50 %S32_51 %S32_53 %S32_54 %S32_56 %S32_57 %S32_59 %S32_60 %S32_62 %S32_63 %S32_64 %S32_65 %S32_73 %S32_74 %S32_75 %S32_76 %S32_77 %S32_78 %S32_79 %S32_80 %S32_81 %S32_82 %S32_83 %S32_84 %S32_85 %S32_86 %S32_87 %S32_88 %S32_89 %S32_90 %S32_91 %S32_92 %S32_93 %S32_94 %S32_95 %S32_96 %S32_97 %S32_98 %S32_99 x0 x1 x2 x3 x4 x5 x6 x7 x8]
.reg A64 [%A64_122 %A64_125 %A64_128 %A64_131 %A64_134 %A64_137 %A64_140 %A64_43 %A64_46 %A64_49 %A64_52 %A64_55 %A64_58 %A64_61 %A64_66 %A64_67 %A64_68 %A64_69 %A64_70 %A64_71 %A64_72 blk]
.bbl %start
    poparg blk
    lea %A64_43 blk 16
    ld %S32_44 %A64_43 0
    shl %S32_45 %S32_44 11
    mov x1 %S32_45
    lea %A64_46 blk 24
    ld %S32_47 %A64_46 0
    mov x2 %S32_47
    or %S32_48 %S32_45 %S32_47
    lea %A64_49 blk 8
    ld %S32_50 %A64_49 0
    mov x3 %S32_50
    or %S32_51 %S32_48 %S32_50
    lea %A64_52 blk 4
    ld %S32_53 %A64_52 0
    mov x4 %S32_53
    or %S32_54 %S32_51 %S32_53
    lea %A64_55 blk 28
    ld %S32_56 %A64_55 0
    mov x5 %S32_56
    or %S32_57 %S32_54 %S32_56
    lea %A64_58 blk 20
    ld %S32_59 %A64_58 0
    mov x6 %S32_59
    or %S32_60 %S32_57 %S32_59
    lea %A64_61 blk 12
    ld %S32_62 %A64_61 0
    mov x7 %S32_62
    or %S32_63 %S32_60 %S32_62
    bne %S32_63 0 if_1_end
    bra if_1_true
.bbl if_1_true
    ld %S32_64 blk 0
    shl %S32_65 %S32_64 3
    lea %A64_66 blk 28
    st %A64_66 0 %S32_65
    lea %A64_67 blk 24
    st %A64_67 0 %S32_65
    lea %A64_68 blk 20
    st %A64_68 0 %S32_65
    lea %A64_69 blk 16
    st %A64_69 0 %S32_65
    lea %A64_70 blk 12
    st %A64_70 0 %S32_65
    lea %A64_71 blk 8
    st %A64_71 0 %S32_65
    lea %A64_72 blk 4
    st %A64_72 0 %S32_65
    st blk 0 %S32_65
    ret
.bbl if_1_end
    ld %S32_73 blk 0
    shl %S32_74 %S32_73 11
    add %S32_75 %S32_74 128
    mov x0 %S32_75
    add %S32_76 x4 x5
    mul %S32_77 %S32_76 565
    mov x8 %S32_77
    sub %S32_78 2841 565
    mul %S32_79 x4 %S32_78
    add %S32_80 x8 %S32_79
    mov x4 %S32_80
    add %S32_81 2841 565
    mul %S32_82 x5 %S32_81
    sub %S32_83 x8 %S32_82
    mov x5 %S32_83
    add %S32_84 x6 x7
    mul %S32_85 %S32_84 2408
    mov x8 %S32_85
    sub %S32_86 2408 1609
    mul %S32_87 x6 %S32_86
    sub %S32_88 x8 %S32_87
    mov x6 %S32_88
    add %S32_89 2408 1609
    mul %S32_90 x7 %S32_89
    sub %S32_91 x8 %S32_90
    mov x7 %S32_91
    add %S32_92 x0 x1
    mov x8 %S32_92
    sub %S32_93 x0 x1
    mov x0 %S32_93
    add %S32_94 x3 x2
    mul %S32_95 %S32_94 1108
    mov x1 %S32_95
    add %S32_96 2676 1108
    mul %S32_97 x2 %S32_96
    sub %S32_98 x1 %S32_97
    mov x2 %S32_98
    sub %S32_99 2676 1108
    mul %S32_100 x3 %S32_99
    add %S32_101 x1 %S32_100
    mov x3 %S32_101
    add %S32_102 x4 x6
    mov x1 %S32_102
    sub %S32_103 x4 x6
    mov x4 %S32_103
    add %S32_104 x5 x7
    mov x6 %S32_104
    sub %S32_105 x5 x7
    mov x5 %S32_105
    add %S32_106 x8 x3
    mov x7 %S32_106
    sub %S32_107 x8 x3
    mov x8 %S32_107
    add %S32_108 x0 x2
    mov x3 %S32_108
    sub %S32_109 x0 x2
    mov x0 %S32_109
    add %S32_110 x4 x5
    mul %S32_111 %S32_110 181
    add %S32_112 %S32_111 128
    shr %S32_113 %S32_112 8
    mov x2 %S32_113
    sub %S32_114 x4 x5
    mul %S32_115 %S32_114 181
    add %S32_116 %S32_115 128
    shr %S32_117 %S32_116 8
    mov x4 %S32_117
    add %S32_118 x7 x1
    shr %S32_119 %S32_118 8
    st blk 0 %S32_119
    add %S32_120 x3 x2
    shr %S32_121 %S32_120 8
    lea %A64_122 blk 4
    st %A64_122 0 %S32_121
    add %S32_123 x0 x4
    shr %S32_124 %S32_123 8
    lea %A64_125 blk 8
    st %A64_125 0 %S32_124
    add %S32_126 x8 x6
    shr %S32_127 %S32_126 8
    lea %A64_128 blk 12
    st %A64_128 0 %S32_127
    sub %S32_129 x8 x6
    shr %S32_130 %S32_129 8
    lea %A64_131 blk 16
    st %A64_131 0 %S32_130
    sub %S32_132 x0 x4
    shr %S32_133 %S32_132 8
    lea %A64_134 blk 20
    st %A64_134 0 %S32_133
    sub %S32_135 x3 x2
    shr %S32_136 %S32_135 8
    lea %A64_137 blk 24
    st %A64_137 0 %S32_136
    sub %S32_138 x7 x1
    shr %S32_139 %S32_138 8
    lea %A64_140 blk 28
    st %A64_140 0 %S32_139
    ret

.fun njColIDCT NORMAL [] = [A64 A64 S32]
.reg S32 [%S32_141 %S32_142 %S32_144 %S32_145 %S32_146 %S32_147 %S32_149 %S32_150 %S32_151 %S32_152 %S32_154 %S32_155 %S32_156 %S32_157 %S32_159 %S32_160 %S32_161 %S32_162 %S32_164 %S32_165 %S32_166 %S32_167 %S32_169 %S32_170 %S32_171 %S32_172 %S32_174 %S32_175 %S32_176 %S32_177 %S32_178 %S32_179 %S32_181 %S32_184 %S32_185 %S32_186 %S32_187 %S32_188 %S32_189 %S32_190 %S32_191 %S32_192 %S32_193 %S32_194 %S32_195 %S32_196 %S32_197 %S32_198 %S32_199 %S32_200 %S32_201 %S32_202 %S32_203 %S32_204 %S32_205 %S32_206 %S32_207 %S32_208 %S32_209 %S32_210 %S32_211 %S32_212 %S32_213 %S32_214 %S32_215 %S32_216 %S32_217 %S32_218 %S32_219 %S32_220 %S32_221 %S32_222 %S32_223 %S32_224 %S32_225 %S32_226 %S32_227 %S32_228 %S32_229 %S32_230 %S32_231 %S32_232 %S32_233 %S32_234 %S32_235 %S32_236 %S32_237 %S32_238 %S32_239 %S32_240 %S32_241 %S32_244 %S32_245 %S32_246 %S32_249 %S32_250 %S32_251 %S32_254 %S32_255 %S32_256 %S32_259 %S32_260 %S32_261 %S32_264 %S32_265 %S32_266 %S32_269 %S32_270 %S32_271 %S32_274 %S32_275 %S32_276 stride x0 x1 x2 x3 x4 x5 x6 x7 x8]
.reg U8 [%U8_180 %U8_182 %U8_242 %U8_247 %U8_252 %U8_257 %U8_262 %U8_267 %U8_272 %U8_277]
.reg A64 [%A64_143 %A64_148 %A64_153 %A64_158 %A64_163 %A64_168 %A64_173 %A64_183 %A64_243 %A64_248 %A64_253 %A64_258 %A64_263 %A64_268 %A64_273 blk out]
.bbl %start
    poparg blk
    poparg out
    poparg stride
    mul %S32_141 8 4
    mul %S32_142 %S32_141 4
    lea %A64_143 blk %S32_142
    ld %S32_144 %A64_143 0
    shl %S32_145 %S32_144 8
    mov x1 %S32_145
    mul %S32_146 8 6
    mul %S32_147 %S32_146 4
    lea %A64_148 blk %S32_147
    ld %S32_149 %A64_148 0
    mov x2 %S32_149
    or %S32_150 %S32_145 %S32_149
    mul %S32_151 8 2
    mul %S32_152 %S32_151 4
    lea %A64_153 blk %S32_152
    ld %S32_154 %A64_153 0
    mov x3 %S32_154
    or %S32_155 %S32_150 %S32_154
    mul %S32_156 8 1
    mul %S32_157 %S32_156 4
    lea %A64_158 blk %S32_157
    ld %S32_159 %A64_158 0
    mov x4 %S32_159
    or %S32_160 %S32_155 %S32_159
    mul %S32_161 8 7
    mul %S32_162 %S32_161 4
    lea %A64_163 blk %S32_162
    ld %S32_164 %A64_163 0
    mov x5 %S32_164
    or %S32_165 %S32_160 %S32_164
    mul %S32_166 8 5
    mul %S32_167 %S32_166 4
    lea %A64_168 blk %S32_167
    ld %S32_169 %A64_168 0
    mov x6 %S32_169
    or %S32_170 %S32_165 %S32_169
    mul %S32_171 8 3
    mul %S32_172 %S32_171 4
    lea %A64_173 blk %S32_172
    ld %S32_174 %A64_173 0
    mov x7 %S32_174
    or %S32_175 %S32_170 %S32_174
    bne %S32_175 0 if_3_end
    bra if_3_true
.bbl if_3_true
    ld %S32_176 blk 0
    add %S32_177 %S32_176 32
    shr %S32_178 %S32_177 6
    add %S32_179 %S32_178 128
    pusharg %S32_179
    bsr njClip
    poparg %U8_180
    conv %S32_181 %U8_180
    mov x1 %S32_181
    mov x0 8
    bra for_1_cond
.bbl for_1
    conv %U8_182 x1
    st out 0 %U8_182
    lea %A64_183 out stride
    mov out %A64_183
.bbl for_1_next
    sub %S32_184 x0 1
    mov x0 %S32_184
.bbl for_1_cond
    bne x0 0 for_1
    bra for_1_exit
.bbl for_1_exit
    ret
.bbl if_3_end
    ld %S32_185 blk 0
    shl %S32_186 %S32_185 8
    add %S32_187 %S32_186 8192
    mov x0 %S32_187
    add %S32_188 x4 x5
    mul %S32_189 %S32_188 565
    add %S32_190 %S32_189 4
    mov x8 %S32_190
    sub %S32_191 2841 565
    mul %S32_192 x4 %S32_191
    add %S32_193 x8 %S32_192
    shr %S32_194 %S32_193 3
    mov x4 %S32_194
    add %S32_195 2841 565
    mul %S32_196 x5 %S32_195
    sub %S32_197 x8 %S32_196
    shr %S32_198 %S32_197 3
    mov x5 %S32_198
    add %S32_199 x6 x7
    mul %S32_200 %S32_199 2408
    add %S32_201 %S32_200 4
    mov x8 %S32_201
    sub %S32_202 2408 1609
    mul %S32_203 x6 %S32_202
    sub %S32_204 x8 %S32_203
    shr %S32_205 %S32_204 3
    mov x6 %S32_205
    add %S32_206 2408 1609
    mul %S32_207 x7 %S32_206
    sub %S32_208 x8 %S32_207
    shr %S32_209 %S32_208 3
    mov x7 %S32_209
    add %S32_210 x0 x1
    mov x8 %S32_210
    sub %S32_211 x0 x1
    mov x0 %S32_211
    add %S32_212 x3 x2
    mul %S32_213 %S32_212 1108
    add %S32_214 %S32_213 4
    mov x1 %S32_214
    add %S32_215 2676 1108
    mul %S32_216 x2 %S32_215
    sub %S32_217 x1 %S32_216
    shr %S32_218 %S32_217 3
    mov x2 %S32_218
    sub %S32_219 2676 1108
    mul %S32_220 x3 %S32_219
    add %S32_221 x1 %S32_220
    shr %S32_222 %S32_221 3
    mov x3 %S32_222
    add %S32_223 x4 x6
    mov x1 %S32_223
    sub %S32_224 x4 x6
    mov x4 %S32_224
    add %S32_225 x5 x7
    mov x6 %S32_225
    sub %S32_226 x5 x7
    mov x5 %S32_226
    add %S32_227 x8 x3
    mov x7 %S32_227
    sub %S32_228 x8 x3
    mov x8 %S32_228
    add %S32_229 x0 x2
    mov x3 %S32_229
    sub %S32_230 x0 x2
    mov x0 %S32_230
    add %S32_231 x4 x5
    mul %S32_232 %S32_231 181
    add %S32_233 %S32_232 128
    shr %S32_234 %S32_233 8
    mov x2 %S32_234
    sub %S32_235 x4 x5
    mul %S32_236 %S32_235 181
    add %S32_237 %S32_236 128
    shr %S32_238 %S32_237 8
    mov x4 %S32_238
    add %S32_239 x7 x1
    shr %S32_240 %S32_239 14
    add %S32_241 %S32_240 128
    pusharg %S32_241
    bsr njClip
    poparg %U8_242
    st out 0 %U8_242
    lea %A64_243 out stride
    mov out %A64_243
    add %S32_244 x3 x2
    shr %S32_245 %S32_244 14
    add %S32_246 %S32_245 128
    pusharg %S32_246
    bsr njClip
    poparg %U8_247
    st out 0 %U8_247
    lea %A64_248 out stride
    mov out %A64_248
    add %S32_249 x0 x4
    shr %S32_250 %S32_249 14
    add %S32_251 %S32_250 128
    pusharg %S32_251
    bsr njClip
    poparg %U8_252
    st out 0 %U8_252
    lea %A64_253 out stride
    mov out %A64_253
    add %S32_254 x8 x6
    shr %S32_255 %S32_254 14
    add %S32_256 %S32_255 128
    pusharg %S32_256
    bsr njClip
    poparg %U8_257
    st out 0 %U8_257
    lea %A64_258 out stride
    mov out %A64_258
    sub %S32_259 x8 x6
    shr %S32_260 %S32_259 14
    add %S32_261 %S32_260 128
    pusharg %S32_261
    bsr njClip
    poparg %U8_262
    st out 0 %U8_262
    lea %A64_263 out stride
    mov out %A64_263
    sub %S32_264 x0 x4
    shr %S32_265 %S32_264 14
    add %S32_266 %S32_265 128
    pusharg %S32_266
    bsr njClip
    poparg %U8_267
    st out 0 %U8_267
    lea %A64_268 out stride
    mov out %A64_268
    sub %S32_269 x3 x2
    shr %S32_270 %S32_269 14
    add %S32_271 %S32_270 128
    pusharg %S32_271
    bsr njClip
    poparg %U8_272
    st out 0 %U8_272
    lea %A64_273 out stride
    mov out %A64_273
    sub %S32_274 x7 x1
    shr %S32_275 %S32_274 14
    add %S32_276 %S32_275 128
    pusharg %S32_276
    bsr njClip
    poparg %U8_277
    st out 0 %U8_277
    ret

.fun __static_1_njShowBits NORMAL [S32] = [S32]
.reg S32 [%S32_280 %S32_283 %S32_284 %S32_285 %S32_290 %S32_291 %S32_306 %S32_307 %S32_312 %S32_313 %S32_318 %S32_319 %S32_320 %S32_321 %S32_324 %S32_327 %S32_340 %S32_341 %S32_347 %S32_348 %S32_349 %S32_351 %S32_354 %S32_355 %S32_356 %S32_357 %S32_362 %S32_363 %S32_367 %S32_370 %S32_373 %S32_376 %S32_377 %S32_378 %S32_379 %S32_380 %S32_381 %out bits]
.reg U8 [%U8_297 %U8_331 marker newbyte]
.reg A64 [%A64_278 %A64_279 %A64_281 %A64_282 %A64_286 %A64_287 %A64_288 %A64_289 %A64_292 %A64_293 %A64_294 %A64_295 %A64_296 %A64_298 %A64_299 %A64_300 %A64_301 %A64_302 %A64_303 %A64_304 %A64_305 %A64_308 %A64_309 %A64_310 %A64_311 %A64_314 %A64_315 %A64_316 %A64_317 %A64_322 %A64_323 %A64_325 %A64_326 %A64_328 %A64_329 %A64_330 %A64_332 %A64_333 %A64_334 %A64_335 %A64_336 %A64_337 %A64_338 %A64_339 %A64_342 %A64_343 %A64_345 %A64_346 %A64_350 %A64_352 %A64_353 %A64_358 %A64_359 %A64_360 %A64_361 %A64_364 %A64_365 %A64_366 %A64_368 %A64_369 %A64_371 %A64_372 %A64_374 %A64_375]
.jtb switch_344_tab 256 switch_344_default [0 switch_344_0 217 switch_344_217 255 switch_344_255]
.bbl %start
    poparg bits
    bne bits 0 if_2_end
    bra if_2_true
.bbl if_2_true
    mov %out 0
    pusharg %out
    ret
.bbl if_2_end
    bra while_1_cond
.bbl while_1
    lea.mem %A64_278 nj 0
    lea %A64_279 %A64_278 16
    ld %S32_280 %A64_279 0
    ble %S32_280 0 if_3_true
    bra if_3_end
.bbl if_3_true
    lea.mem %A64_281 nj 0
    lea %A64_282 %A64_281 524752
    ld %S32_283 %A64_282 0
    shl %S32_284 %S32_283 8
    or %S32_285 %S32_284 255
    lea.mem %A64_286 nj 0
    lea %A64_287 %A64_286 524752
    st %A64_287 0 %S32_285
    lea.mem %A64_288 nj 0
    lea %A64_289 %A64_288 524756
    ld %S32_290 %A64_289 0
    add %S32_291 %S32_290 8
    lea.mem %A64_292 nj 0
    lea %A64_293 %A64_292 524756
    st %A64_293 0 %S32_291
    bra while_1_cond
.bbl if_3_end
    lea.mem %A64_294 nj 0
    lea %A64_295 %A64_294 4
    ld %A64_296 %A64_295 0
    ld %U8_297 %A64_296 0
    mov newbyte %U8_297
    lea.mem %A64_298 nj 0
    lea %A64_299 %A64_298 4
    ld %A64_300 %A64_299 0
    lea %A64_301 %A64_300 1
    lea.mem %A64_302 nj 0
    lea %A64_303 %A64_302 4
    st %A64_303 0 %A64_301
    lea.mem %A64_304 nj 0
    lea %A64_305 %A64_304 16
    ld %S32_306 %A64_305 0
    sub %S32_307 %S32_306 1
    lea.mem %A64_308 nj 0
    lea %A64_309 %A64_308 16
    st %A64_309 0 %S32_307
    lea.mem %A64_310 nj 0
    lea %A64_311 %A64_310 524756
    ld %S32_312 %A64_311 0
    add %S32_313 %S32_312 8
    lea.mem %A64_314 nj 0
    lea %A64_315 %A64_314 524756
    st %A64_315 0 %S32_313
    lea.mem %A64_316 nj 0
    lea %A64_317 %A64_316 524752
    ld %S32_318 %A64_317 0
    shl %S32_319 %S32_318 8
    conv %S32_320 newbyte
    or %S32_321 %S32_319 %S32_320
    lea.mem %A64_322 nj 0
    lea %A64_323 %A64_322 524752
    st %A64_323 0 %S32_321
    conv %S32_324 newbyte
    beq %S32_324 255 if_6_true
    bra while_1_cond
.bbl if_6_true
    lea.mem %A64_325 nj 0
    lea %A64_326 %A64_325 16
    ld %S32_327 %A64_326 0
    bne %S32_327 0 if_5_true
    bra if_5_false
.bbl if_5_true
    lea.mem %A64_328 nj 0
    lea %A64_329 %A64_328 4
    ld %A64_330 %A64_329 0
    ld %U8_331 %A64_330 0
    mov marker %U8_331
    lea.mem %A64_332 nj 0
    lea %A64_333 %A64_332 4
    ld %A64_334 %A64_333 0
    lea %A64_335 %A64_334 1
    lea.mem %A64_336 nj 0
    lea %A64_337 %A64_336 4
    st %A64_337 0 %A64_335
    lea.mem %A64_338 nj 0
    lea %A64_339 %A64_338 16
    ld %S32_340 %A64_339 0
    sub %S32_341 %S32_340 1
    lea.mem %A64_342 nj 0
    lea %A64_343 %A64_342 16
    st %A64_343 0 %S32_341
    blt 255:U8 marker switch_344_default
    switch marker switch_344_tab
.bbl switch_344_0
.bbl switch_344_255
    bra switch_344_end
.bbl switch_344_217
    lea.mem %A64_345 nj 0
    lea %A64_346 %A64_345 16
    mov %S32_347 0
    st %A64_346 0 %S32_347
    bra switch_344_end
.bbl switch_344_default
    conv %S32_348 marker
    and %S32_349 %S32_348 248
    bne %S32_349 208 if_4_true
    bra if_4_false
.bbl if_4_true
    lea.mem %A64_350 nj 0
    mov %S32_351 5
    st %A64_350 0 %S32_351
    bra if_4_end
.bbl if_4_false
    lea.mem %A64_352 nj 0
    lea %A64_353 %A64_352 524752
    ld %S32_354 %A64_353 0
    shl %S32_355 %S32_354 8
    conv %S32_356 marker
    or %S32_357 %S32_355 %S32_356
    lea.mem %A64_358 nj 0
    lea %A64_359 %A64_358 524752
    st %A64_359 0 %S32_357
    lea.mem %A64_360 nj 0
    lea %A64_361 %A64_360 524756
    ld %S32_362 %A64_361 0
    add %S32_363 %S32_362 8
    lea.mem %A64_364 nj 0
    lea %A64_365 %A64_364 524756
    st %A64_365 0 %S32_363
.bbl if_4_end
.bbl switch_344_end
    bra while_1_cond
.bbl if_5_false
    lea.mem %A64_366 nj 0
    mov %S32_367 5
    st %A64_366 0 %S32_367
.bbl while_1_cond
    lea.mem %A64_368 nj 0
    lea %A64_369 %A64_368 524756
    ld %S32_370 %A64_369 0
    blt %S32_370 bits while_1
    bra while_1_exit
.bbl while_1_exit
    lea.mem %A64_371 nj 0
    lea %A64_372 %A64_371 524752
    ld %S32_373 %A64_372 0
    lea.mem %A64_374 nj 0
    lea %A64_375 %A64_374 524756
    ld %S32_376 %A64_375 0
    sub %S32_377 %S32_376 bits
    shr %S32_378 %S32_373 %S32_377
    shl %S32_379 1 bits
    sub %S32_380 %S32_379 1
    and %S32_381 %S32_378 %S32_380
    mov %out %S32_381
    pusharg %out
    ret

.fun njSkipBits NORMAL [] = [S32]
.reg S32 [%S32_384 %S32_385 %S32_388 %S32_389 bits]
.reg A64 [%A64_382 %A64_383 %A64_386 %A64_387 %A64_390 %A64_391]
.bbl %start
    poparg bits
    lea.mem %A64_382 nj 0
    lea %A64_383 %A64_382 524756
    ld %S32_384 %A64_383 0
    blt %S32_384 bits if_1_true
    bra if_1_end
.bbl if_1_true
    pusharg bits
    bsr __static_1_njShowBits
    poparg %S32_385
.bbl if_1_end
    lea.mem %A64_386 nj 0
    lea %A64_387 %A64_386 524756
    ld %S32_388 %A64_387 0
    sub %S32_389 %S32_388 bits
    lea.mem %A64_390 nj 0
    lea %A64_391 %A64_390 524756
    st %A64_391 0 %S32_389
    ret

.fun njGetBits NORMAL [S32] = [S32]
.reg S32 [%S32_392 %out bits res]
.bbl %start
    poparg bits
    pusharg bits
    bsr __static_1_njShowBits
    poparg %S32_392
    mov res %S32_392
    pusharg bits
    bsr njSkipBits
    mov %out res
    pusharg %out
    ret

.fun njByteAlign NORMAL [] = []
.reg S32 [%S32_395 %S32_396]
.reg A64 [%A64_393 %A64_394 %A64_397 %A64_398]
.bbl %start
    lea.mem %A64_393 nj 0
    lea %A64_394 %A64_393 524756
    ld %S32_395 %A64_394 0
    and %S32_396 %S32_395 248
    lea.mem %A64_397 nj 0
    lea %A64_398 %A64_397 524756
    st %A64_398 0 %S32_396
    ret

.fun __static_2_njSkip NORMAL [] = [S32]
.reg S32 [%S32_407 %S32_408 %S32_413 %S32_414 %S32_419 %S32_421 count]
.reg A64 [%A64_399 %A64_400 %A64_401 %A64_402 %A64_403 %A64_404 %A64_405 %A64_406 %A64_409 %A64_410 %A64_411 %A64_412 %A64_415 %A64_416 %A64_417 %A64_418 %A64_420]
.bbl %start
    poparg count
    lea.mem %A64_399 nj 0
    lea %A64_400 %A64_399 4
    ld %A64_401 %A64_400 0
    lea %A64_402 %A64_401 count
    lea.mem %A64_403 nj 0
    lea %A64_404 %A64_403 4
    st %A64_404 0 %A64_402
    lea.mem %A64_405 nj 0
    lea %A64_406 %A64_405 16
    ld %S32_407 %A64_406 0
    sub %S32_408 %S32_407 count
    lea.mem %A64_409 nj 0
    lea %A64_410 %A64_409 16
    st %A64_410 0 %S32_408
    lea.mem %A64_411 nj 0
    lea %A64_412 %A64_411 20
    ld %S32_413 %A64_412 0
    sub %S32_414 %S32_413 count
    lea.mem %A64_415 nj 0
    lea %A64_416 %A64_415 20
    st %A64_416 0 %S32_414
    lea.mem %A64_417 nj 0
    lea %A64_418 %A64_417 16
    ld %S32_419 %A64_418 0
    blt %S32_419 0 if_1_true
    bra if_1_end
.bbl if_1_true
    lea.mem %A64_420 nj 0
    mov %S32_421 5
    st %A64_420 0 %S32_421
.bbl if_1_end
    ret

.fun njDecode16 NORMAL [U16] = [A64]
.reg S32 [%S32_423 %S32_424 %S32_427 %S32_428]
.reg U8 [%U8_422 %U8_426]
.reg U16 [%U16_429 %out]
.reg A64 [%A64_425 pos]
.bbl %start
    poparg pos
    ld %U8_422 pos 0
    conv %S32_423 %U8_422
    shl %S32_424 %S32_423 8
    lea %A64_425 pos 1
    ld %U8_426 %A64_425 0
    conv %S32_427 %U8_426
    or %S32_428 %S32_424 %S32_427
    conv %U16_429 %S32_428
    mov %out %U16_429
    pusharg %out
    ret

.fun __static_3_njDecodeLength NORMAL [] = []
.reg S32 [%S32_432 %S32_434 %S32_439 %S32_444 %S32_447 %S32_449 %S32_450]
.reg U16 [%U16_438]
.reg A64 [%A64_430 %A64_431 %A64_433 %A64_435 %A64_436 %A64_437 %A64_440 %A64_441 %A64_442 %A64_443 %A64_445 %A64_446 %A64_448]
.bbl %start
    lea.mem %A64_430 nj 0
    lea %A64_431 %A64_430 16
    ld %S32_432 %A64_431 0
    blt %S32_432 2 while_1
    bra if_4_end
.bbl while_1
    lea.mem %A64_433 nj 0
    mov %S32_434 5
    st %A64_433 0 %S32_434
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra if_4_end
.bbl if_4_end
    lea.mem %A64_435 nj 0
    lea %A64_436 %A64_435 4
    ld %A64_437 %A64_436 0
    pusharg %A64_437
    bsr njDecode16
    poparg %U16_438
    conv %S32_439 %U16_438
    lea.mem %A64_440 nj 0
    lea %A64_441 %A64_440 20
    st %A64_441 0 %S32_439
    lea.mem %A64_442 nj 0
    lea %A64_443 %A64_442 20
    ld %S32_444 %A64_443 0
    lea.mem %A64_445 nj 0
    lea %A64_446 %A64_445 16
    ld %S32_447 %A64_446 0
    blt %S32_447 %S32_444 while_2
    bra if_6_end
.bbl while_2
    lea.mem %A64_448 nj 0
    mov %S32_449 5
    st %A64_448 0 %S32_449
    ret
.bbl while_2_cond
    bne 0:S32 0 while_2
    bra if_6_end
.bbl if_6_end
    mov %S32_450 2
    pusharg %S32_450
    bsr __static_2_njSkip
    ret

.fun njSkipMarker NORMAL [] = []
.reg S32 [%S32_453]
.reg A64 [%A64_451 %A64_452]
.bbl %start
    bsr __static_3_njDecodeLength
    lea.mem %A64_451 nj 0
    lea %A64_452 %A64_451 20
    ld %S32_453 %A64_452 0
    pusharg %S32_453
    bsr __static_2_njSkip
    ret

.fun njDecodeSOF NORMAL [] = []
.reg S32 [%S32_456 %S32_459 %S32_461 %S32_466 %S32_468 %S32_474 %S32_482 %S32_487 %S32_490 %S32_492 %S32_501 %S32_507 %S32_510 %S32_517 %S32_524 %S32_530 %S32_531 %S32_534 %S32_536 %S32_538 %S32_539 %S32_540 %S32_542 %S32_548 %S32_549 %S32_552 %S32_554 %S32_556 %S32_557 %S32_558 %S32_560 %S32_566 %S32_568 %S32_570 %S32_571 %S32_574 %S32_576 %S32_577 %S32_578 %S32_582 %S32_584 %S32_586 %S32_588 %S32_589 %S32_601 %S32_603 %S32_606 %S32_611 %S32_614 %S32_615 %S32_616 %S32_619 %S32_620 %S32_625 %S32_628 %S32_629 %S32_630 %S32_633 %S32_634 %S32_641 %S32_643 %S32_644 %S32_645 %S32_646 %S32_647 %S32_651 %S32_653 %S32_654 %S32_655 %S32_656 %S32_657 %S32_661 %S32_663 %S32_664 %S32_665 %S32_668 %S32_670 %S32_672 %S32_674 %S32_676 %S32_678 %S32_681 %S32_682 %S32_684 %S32_685 %S32_686 %S32_691 %S32_692 %S32_703 %S32_706 %S32_707 %S32_721 %S32_724 i ssxmax ssymax]
.reg U8 [%U8_465 %U8_497 %U8_523 %U8_529 %U8_547 %U8_565]
.reg U16 [%U16_473 %U16_481]
.reg U32 [%U32_498 %U32_504 %U32_511 %U32_514 %U32_515 %U32_591 %U32_594 %U32_597 %U32_694 %U32_697 %U32_700 %U32_708 %U32_711 %U32_712]
.reg U64 [%U64_687 %U64_713]
.reg A64 [%A64_454 %A64_455 %A64_457 %A64_458 %A64_460 %A64_462 %A64_463 %A64_464 %A64_467 %A64_469 %A64_470 %A64_471 %A64_472 %A64_475 %A64_476 %A64_477 %A64_478 %A64_479 %A64_480 %A64_483 %A64_484 %A64_485 %A64_486 %A64_488 %A64_489 %A64_491 %A64_493 %A64_494 %A64_495 %A64_496 %A64_499 %A64_500 %A64_502 %A64_503 %A64_506 %A64_508 %A64_509 %A64_512 %A64_513 %A64_516 %A64_518 %A64_519 %A64_520 %A64_521 %A64_522 %A64_525 %A64_526 %A64_527 %A64_528 %A64_532 %A64_533 %A64_535 %A64_537 %A64_541 %A64_543 %A64_544 %A64_545 %A64_546 %A64_550 %A64_551 %A64_553 %A64_555 %A64_559 %A64_561 %A64_562 %A64_563 %A64_564 %A64_567 %A64_569 %A64_572 %A64_573 %A64_575 %A64_579 %A64_580 %A64_581 %A64_583 %A64_585 %A64_587 %A64_590 %A64_592 %A64_593 %A64_595 %A64_596 %A64_598 %A64_599 %A64_600 %A64_602 %A64_604 %A64_605 %A64_607 %A64_608 %A64_609 %A64_610 %A64_612 %A64_613 %A64_617 %A64_618 %A64_621 %A64_622 %A64_623 %A64_624 %A64_626 %A64_627 %A64_631 %A64_632 %A64_635 %A64_636 %A64_637 %A64_638 %A64_639 %A64_640 %A64_642 %A64_648 %A64_649 %A64_650 %A64_652 %A64_658 %A64_659 %A64_660 %A64_662 %A64_666 %A64_667 %A64_669 %A64_671 %A64_673 %A64_675 %A64_677 %A64_679 %A64_680 %A64_683 %A64_688 %A64_689 %A64_690 %A64_693 %A64_695 %A64_696 %A64_698 %A64_699 %A64_701 %A64_702 %A64_704 %A64_705 %A64_709 %A64_710 %A64_714 %A64_715 %A64_716 %A64_717 %A64_718 %A64_719 %A64_720 %A64_722 %A64_723 c]
.jtb switch_505_tab 4 switch_505_default [1 switch_505_1 3 switch_505_3]
.bbl %start
    mov ssxmax 0
    mov ssymax 0
    bsr __static_3_njDecodeLength
.bbl while_1
    lea.mem %A64_454 nj 0
    lea %A64_455 %A64_454 0
    ld %S32_456 %A64_455 0
    bne %S32_456 0 if_17_true
    bra while_1_cond
.bbl if_17_true
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra while_1_exit
.bbl while_1_exit
    lea.mem %A64_457 nj 0
    lea %A64_458 %A64_457 20
    ld %S32_459 %A64_458 0
    blt %S32_459 9 while_2
    bra if_20_end
.bbl while_2
    lea.mem %A64_460 nj 0
    mov %S32_461 5
    st %A64_460 0 %S32_461
    ret
.bbl while_2_cond
    bne 0:S32 0 while_2
    bra if_20_end
.bbl if_20_end
    lea.mem %A64_462 nj 0
    lea %A64_463 %A64_462 4
    ld %A64_464 %A64_463 0
    ld %U8_465 %A64_464 0
    conv %S32_466 %U8_465
    bne %S32_466 8 while_3
    bra if_22_end
.bbl while_3
    lea.mem %A64_467 nj 0
    mov %S32_468 2
    st %A64_467 0 %S32_468
    ret
.bbl while_3_cond
    bne 0:S32 0 while_3
    bra if_22_end
.bbl if_22_end
    lea.mem %A64_469 nj 0
    lea %A64_470 %A64_469 4
    ld %A64_471 %A64_470 0
    lea %A64_472 %A64_471 1
    pusharg %A64_472
    bsr njDecode16
    poparg %U16_473
    conv %S32_474 %U16_473
    lea.mem %A64_475 nj 0
    lea %A64_476 %A64_475 28
    st %A64_476 0 %S32_474
    lea.mem %A64_477 nj 0
    lea %A64_478 %A64_477 4
    ld %A64_479 %A64_478 0
    lea %A64_480 %A64_479 3
    pusharg %A64_480
    bsr njDecode16
    poparg %U16_481
    conv %S32_482 %U16_481
    lea.mem %A64_483 nj 0
    lea %A64_484 %A64_483 24
    st %A64_484 0 %S32_482
    lea.mem %A64_485 nj 0
    lea %A64_486 %A64_485 24
    ld %S32_487 %A64_486 0
    bne %S32_487 0 branch_50
    bra while_4
.bbl branch_50
    lea.mem %A64_488 nj 0
    lea %A64_489 %A64_488 28
    ld %S32_490 %A64_489 0
    bne %S32_490 0 if_24_end
    bra while_4
.bbl while_4
    lea.mem %A64_491 nj 0
    mov %S32_492 5
    st %A64_491 0 %S32_492
    ret
.bbl while_4_cond
    bne 0:S32 0 while_4
    bra if_24_end
.bbl if_24_end
    lea.mem %A64_493 nj 0
    lea %A64_494 %A64_493 4
    ld %A64_495 %A64_494 0
    lea %A64_496 %A64_495 5
    ld %U8_497 %A64_496 0
    conv %U32_498 %U8_497
    lea.mem %A64_499 nj 0
    lea %A64_500 %A64_499 48
    st %A64_500 0 %U32_498
    mov %S32_501 6
    pusharg %S32_501
    bsr __static_2_njSkip
    lea.mem %A64_502 nj 0
    lea %A64_503 %A64_502 48
    ld %U32_504 %A64_503 0
    blt 3:U32 %U32_504 switch_505_default
    switch %U32_504 switch_505_tab
.bbl switch_505_1
.bbl switch_505_3
    bra switch_505_end
.bbl switch_505_default
.bbl while_5
    lea.mem %A64_506 nj 0
    mov %S32_507 2
    st %A64_506 0 %S32_507
    ret
.bbl while_5_cond
    bne 0:S32 0 while_5
    bra while_5_exit
.bbl while_5_exit
.bbl switch_505_end
    lea.mem %A64_508 nj 0
    lea %A64_509 %A64_508 20
    ld %S32_510 %A64_509 0
    conv %U32_511 %S32_510
    lea.mem %A64_512 nj 0
    lea %A64_513 %A64_512 48
    ld %U32_514 %A64_513 0
    mul %U32_515 %U32_514 3
    blt %U32_511 %U32_515 while_6
    bra if_27_end
.bbl while_6
    lea.mem %A64_516 nj 0
    mov %S32_517 5
    st %A64_516 0 %S32_517
    ret
.bbl while_6_cond
    bne 0:S32 0 while_6
    bra if_27_end
.bbl if_27_end
    mov i 0
    lea.mem %A64_518 nj 0
    lea %A64_519 %A64_518 52
    mov c %A64_519
    bra for_15_cond
.bbl for_15
    lea.mem %A64_520 nj 0
    lea %A64_521 %A64_520 4
    ld %A64_522 %A64_521 0
    ld %U8_523 %A64_522 0
    conv %S32_524 %U8_523
    st c 0 %S32_524
    lea.mem %A64_525 nj 0
    lea %A64_526 %A64_525 4
    ld %A64_527 %A64_526 0
    lea %A64_528 %A64_527 1
    ld %U8_529 %A64_528 0
    conv %S32_530 %U8_529
    shr %S32_531 %S32_530 4
    lea %A64_532 c 4
    st %A64_532 0 %S32_531
    bne %S32_531 0 if_29_end
    bra while_7
.bbl while_7
    lea.mem %A64_533 nj 0
    mov %S32_534 5
    st %A64_533 0 %S32_534
    ret
.bbl while_7_cond
    bne 0:S32 0 while_7
    bra if_29_end
.bbl if_29_end
    lea %A64_535 c 4
    ld %S32_536 %A64_535 0
    lea %A64_537 c 4
    ld %S32_538 %A64_537 0
    sub %S32_539 %S32_538 1
    and %S32_540 %S32_536 %S32_539
    bne %S32_540 0 while_8
    bra if_31_end
.bbl while_8
    lea.mem %A64_541 nj 0
    mov %S32_542 2
    st %A64_541 0 %S32_542
    ret
.bbl while_8_cond
    bne 0:S32 0 while_8
    bra if_31_end
.bbl if_31_end
    lea.mem %A64_543 nj 0
    lea %A64_544 %A64_543 4
    ld %A64_545 %A64_544 0
    lea %A64_546 %A64_545 1
    ld %U8_547 %A64_546 0
    conv %S32_548 %U8_547
    and %S32_549 %S32_548 15
    lea %A64_550 c 8
    st %A64_550 0 %S32_549
    bne %S32_549 0 if_33_end
    bra while_9
.bbl while_9
    lea.mem %A64_551 nj 0
    mov %S32_552 5
    st %A64_551 0 %S32_552
    ret
.bbl while_9_cond
    bne 0:S32 0 while_9
    bra if_33_end
.bbl if_33_end
    lea %A64_553 c 8
    ld %S32_554 %A64_553 0
    lea %A64_555 c 8
    ld %S32_556 %A64_555 0
    sub %S32_557 %S32_556 1
    and %S32_558 %S32_554 %S32_557
    bne %S32_558 0 while_10
    bra if_35_end
.bbl while_10
    lea.mem %A64_559 nj 0
    mov %S32_560 2
    st %A64_559 0 %S32_560
    ret
.bbl while_10_cond
    bne 0:S32 0 while_10
    bra if_35_end
.bbl if_35_end
    lea.mem %A64_561 nj 0
    lea %A64_562 %A64_561 4
    ld %A64_563 %A64_562 0
    lea %A64_564 %A64_563 2
    ld %U8_565 %A64_564 0
    conv %S32_566 %U8_565
    lea %A64_567 c 24
    st %A64_567 0 %S32_566
    and %S32_568 %S32_566 252
    bne %S32_568 0 while_11
    bra if_37_end
.bbl while_11
    lea.mem %A64_569 nj 0
    mov %S32_570 5
    st %A64_569 0 %S32_570
    ret
.bbl while_11_cond
    bne 0:S32 0 while_11
    bra if_37_end
.bbl if_37_end
    mov %S32_571 3
    pusharg %S32_571
    bsr __static_2_njSkip
    lea.mem %A64_572 nj 0
    lea %A64_573 %A64_572 200
    ld %S32_574 %A64_573 0
    lea %A64_575 c 24
    ld %S32_576 %A64_575 0
    shl %S32_577 1 %S32_576
    or %S32_578 %S32_574 %S32_577
    lea.mem %A64_579 nj 0
    lea %A64_580 %A64_579 200
    st %A64_580 0 %S32_578
    lea %A64_581 c 4
    ld %S32_582 %A64_581 0
    blt ssxmax %S32_582 if_38_true
    bra if_38_end
.bbl if_38_true
    lea %A64_583 c 4
    ld %S32_584 %A64_583 0
    mov ssxmax %S32_584
.bbl if_38_end
    lea %A64_585 c 8
    ld %S32_586 %A64_585 0
    blt ssymax %S32_586 if_39_true
    bra for_15_next
.bbl if_39_true
    lea %A64_587 c 8
    ld %S32_588 %A64_587 0
    mov ssymax %S32_588
.bbl for_15_next
    add %S32_589 i 1
    mov i %S32_589
    lea %A64_590 c 48
    mov c %A64_590
.bbl for_15_cond
    conv %U32_591 i
    lea.mem %A64_592 nj 0
    lea %A64_593 %A64_592 48
    ld %U32_594 %A64_593 0
    blt %U32_591 %U32_594 for_15
    bra for_15_exit
.bbl for_15_exit
    lea.mem %A64_595 nj 0
    lea %A64_596 %A64_595 48
    ld %U32_597 %A64_596 0
    beq %U32_597 1 if_41_true
    bra if_41_end
.bbl if_41_true
    lea.mem %A64_598 nj 0
    lea %A64_599 %A64_598 52
    mov c %A64_599
    mov ssymax 1
    mov ssxmax 1
    lea %A64_600 c 8
    mov %S32_601 1
    st %A64_600 0 %S32_601
    lea %A64_602 c 4
    st %A64_602 0 %S32_601
.bbl if_41_end
    shl %S32_603 ssxmax 3
    lea.mem %A64_604 nj 0
    lea %A64_605 %A64_604 40
    st %A64_605 0 %S32_603
    shl %S32_606 ssymax 3
    lea.mem %A64_607 nj 0
    lea %A64_608 %A64_607 44
    st %A64_608 0 %S32_606
    lea.mem %A64_609 nj 0
    lea %A64_610 %A64_609 24
    ld %S32_611 %A64_610 0
    lea.mem %A64_612 nj 0
    lea %A64_613 %A64_612 40
    ld %S32_614 %A64_613 0
    add %S32_615 %S32_611 %S32_614
    sub %S32_616 %S32_615 1
    lea.mem %A64_617 nj 0
    lea %A64_618 %A64_617 40
    ld %S32_619 %A64_618 0
    div %S32_620 %S32_616 %S32_619
    lea.mem %A64_621 nj 0
    lea %A64_622 %A64_621 32
    st %A64_622 0 %S32_620
    lea.mem %A64_623 nj 0
    lea %A64_624 %A64_623 28
    ld %S32_625 %A64_624 0
    lea.mem %A64_626 nj 0
    lea %A64_627 %A64_626 44
    ld %S32_628 %A64_627 0
    add %S32_629 %S32_625 %S32_628
    sub %S32_630 %S32_629 1
    lea.mem %A64_631 nj 0
    lea %A64_632 %A64_631 44
    ld %S32_633 %A64_632 0
    div %S32_634 %S32_630 %S32_633
    lea.mem %A64_635 nj 0
    lea %A64_636 %A64_635 36
    st %A64_636 0 %S32_634
    mov i 0
    lea.mem %A64_637 nj 0
    lea %A64_638 %A64_637 52
    mov c %A64_638
    bra for_16_cond
.bbl for_16
    lea.mem %A64_639 nj 0
    lea %A64_640 %A64_639 24
    ld %S32_641 %A64_640 0
    lea %A64_642 c 4
    ld %S32_643 %A64_642 0
    mul %S32_644 %S32_641 %S32_643
    add %S32_645 %S32_644 ssxmax
    sub %S32_646 %S32_645 1
    div %S32_647 %S32_646 ssxmax
    lea %A64_648 c 12
    st %A64_648 0 %S32_647
    lea.mem %A64_649 nj 0
    lea %A64_650 %A64_649 28
    ld %S32_651 %A64_650 0
    lea %A64_652 c 8
    ld %S32_653 %A64_652 0
    mul %S32_654 %S32_651 %S32_653
    add %S32_655 %S32_654 ssymax
    sub %S32_656 %S32_655 1
    div %S32_657 %S32_656 ssymax
    lea %A64_658 c 16
    st %A64_658 0 %S32_657
    lea.mem %A64_659 nj 0
    lea %A64_660 %A64_659 32
    ld %S32_661 %A64_660 0
    lea %A64_662 c 4
    ld %S32_663 %A64_662 0
    mul %S32_664 %S32_661 %S32_663
    shl %S32_665 %S32_664 3
    lea %A64_666 c 20
    st %A64_666 0 %S32_665
    lea %A64_667 c 12
    ld %S32_668 %A64_667 0
    blt %S32_668 3 branch_52
    bra branch_51
.bbl branch_52
    lea %A64_669 c 4
    ld %S32_670 %A64_669 0
    bne %S32_670 ssxmax while_12
    bra branch_51
.bbl branch_51
    lea %A64_671 c 16
    ld %S32_672 %A64_671 0
    blt %S32_672 3 branch_53
    bra if_43_end
.bbl branch_53
    lea %A64_673 c 8
    ld %S32_674 %A64_673 0
    bne %S32_674 ssymax while_12
    bra if_43_end
.bbl while_12
    lea.mem %A64_675 nj 0
    mov %S32_676 2
    st %A64_675 0 %S32_676
    ret
.bbl while_12_cond
    bne 0:S32 0 while_12
    bra if_43_end
.bbl if_43_end
    lea %A64_677 c 20
    ld %S32_678 %A64_677 0
    lea.mem %A64_679 nj 0
    lea %A64_680 %A64_679 36
    ld %S32_681 %A64_680 0
    mul %S32_682 %S32_678 %S32_681
    lea %A64_683 c 8
    ld %S32_684 %A64_683 0
    mul %S32_685 %S32_682 %S32_684
    shl %S32_686 %S32_685 3
    conv %U64_687 %S32_686
    pusharg %U64_687
    bsr malloc
    poparg %A64_688
    lea %A64_689 c 40
    st %A64_689 0 %A64_688
    bne %A64_688 0 for_16_next
    bra while_13
.bbl while_13
    lea.mem %A64_690 nj 0
    mov %S32_691 3
    st %A64_690 0 %S32_691
    ret
.bbl while_13_cond
    bne 0:S32 0 while_13
    bra for_16_next
.bbl for_16_next
    add %S32_692 i 1
    mov i %S32_692
    lea %A64_693 c 48
    mov c %A64_693
.bbl for_16_cond
    conv %U32_694 i
    lea.mem %A64_695 nj 0
    lea %A64_696 %A64_695 48
    ld %U32_697 %A64_696 0
    blt %U32_694 %U32_697 for_16
    bra for_16_exit
.bbl for_16_exit
    lea.mem %A64_698 nj 0
    lea %A64_699 %A64_698 48
    ld %U32_700 %A64_699 0
    beq %U32_700 3 if_49_true
    bra if_49_end
.bbl if_49_true
    lea.mem %A64_701 nj 0
    lea %A64_702 %A64_701 24
    ld %S32_703 %A64_702 0
    lea.mem %A64_704 nj 0
    lea %A64_705 %A64_704 28
    ld %S32_706 %A64_705 0
    mul %S32_707 %S32_703 %S32_706
    conv %U32_708 %S32_707
    lea.mem %A64_709 nj 0
    lea %A64_710 %A64_709 48
    ld %U32_711 %A64_710 0
    mul %U32_712 %U32_708 %U32_711
    conv %U64_713 %U32_712
    pusharg %U64_713
    bsr malloc
    poparg %A64_714
    lea.mem %A64_715 nj 0
    lea %A64_716 %A64_715 525020
    st %A64_716 0 %A64_714
    lea.mem %A64_717 nj 0
    lea %A64_718 %A64_717 525020
    ld %A64_719 %A64_718 0
    bne %A64_719 0 if_49_end
    bra while_14
.bbl while_14
    lea.mem %A64_720 nj 0
    mov %S32_721 3
    st %A64_720 0 %S32_721
    ret
.bbl while_14_cond
    bne 0:S32 0 while_14
    bra if_49_end
.bbl if_49_end
    lea.mem %A64_722 nj 0
    lea %A64_723 %A64_722 20
    ld %S32_724 %A64_723 0
    pusharg %S32_724
    bsr __static_2_njSkip
    ret

.fun njDecodeDHT NORMAL [] = []
.reg S32 [%S32_727 %S32_732 %S32_733 %S32_735 %S32_736 %S32_738 %S32_739 %S32_740 %S32_741 %S32_748 %S32_750 %S32_751 %S32_754 %S32_755 %S32_757 %S32_759 %S32_762 %S32_765 %S32_767 %S32_768 %S32_769 %S32_770 %S32_772 %S32_781 %S32_782 %S32_783 %S32_784 %S32_789 %S32_792 %S32_794 codelen currcnt i j remain spread]
.reg U8 [%U8_731 %U8_746 %U8_761 %U8_777 %U8_778 %U8_785 code]
.reg A64 [%A64_725 %A64_726 %A64_728 %A64_729 %A64_730 %A64_734 %A64_737 %A64_742 %A64_743 %A64_744 %A64_745 %A64_747 %A64_749 %A64_752 %A64_753 %A64_756 %A64_758 %A64_760 %A64_763 %A64_764 %A64_766 %A64_771 %A64_773 %A64_774 %A64_775 %A64_776 %A64_779 %A64_780 %A64_786 %A64_787 %A64_788 %A64_790 %A64_791 %A64_793 vlc]
.bbl %start
    bsr __static_3_njDecodeLength
.bbl while_1
    lea.mem %A64_725 nj 0
    lea %A64_726 %A64_725 0
    ld %S32_727 %A64_726 0
    bne %S32_727 0 if_13_true
    bra while_1_cond
.bbl if_13_true
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra while_1_exit
.bbl while_1_exit
    bra while_7_cond
.bbl while_7
    lea.mem %A64_728 nj 0
    lea %A64_729 %A64_728 4
    ld %A64_730 %A64_729 0
    ld %U8_731 %A64_730 0
    conv %S32_732 %U8_731
    mov i %S32_732
    and %S32_733 i 236
    bne %S32_733 0 while_2
    bra if_16_end
.bbl while_2
    lea.mem %A64_734 nj 0
    mov %S32_735 5
    st %A64_734 0 %S32_735
    ret
.bbl while_2_cond
    bne 0:S32 0 while_2
    bra if_16_end
.bbl if_16_end
    and %S32_736 i 2
    bne %S32_736 0 while_3
    bra if_18_end
.bbl while_3
    lea.mem %A64_737 nj 0
    mov %S32_738 2
    st %A64_737 0 %S32_738
    ret
.bbl while_3_cond
    bne 0:S32 0 while_3
    bra if_18_end
.bbl if_18_end
    shr %S32_739 i 3
    or %S32_740 i %S32_739
    and %S32_741 %S32_740 3
    mov i %S32_741
    mov codelen 1
    bra for_9_cond
.bbl for_9
    lea.mem %A64_742 nj 0
    lea %A64_743 %A64_742 4
    ld %A64_744 %A64_743 0
    lea %A64_745 %A64_744 codelen
    ld %U8_746 %A64_745 0
    lea.mem %A64_747 __static_4_counts 0
    sub %S32_748 codelen 1
    lea %A64_749 %A64_747 %S32_748
    st %A64_749 0 %U8_746
.bbl for_9_next
    add %S32_750 codelen 1
    mov codelen %S32_750
.bbl for_9_cond
    ble codelen 16 for_9
    bra for_9_exit
.bbl for_9_exit
    mov %S32_751 17
    pusharg %S32_751
    bsr __static_2_njSkip
    lea.mem %A64_752 nj 0
    lea %A64_753 %A64_752 464
    mul %S32_754 i 65536
    mul %S32_755 %S32_754 2
    lea %A64_756 %A64_753 %S32_755
    mov vlc %A64_756
    mov spread 65536
    mov remain 65536
    mov codelen 1
    bra for_12_cond
.bbl for_12
    shr %S32_757 spread 1
    mov spread %S32_757
    lea.mem %A64_758 __static_4_counts 0
    sub %S32_759 codelen 1
    lea %A64_760 %A64_758 %S32_759
    ld %U8_761 %A64_760 0
    conv %S32_762 %U8_761
    mov currcnt %S32_762
    bne currcnt 0 if_20_end
    bra for_12_next
.bbl if_20_end
    lea.mem %A64_763 nj 0
    lea %A64_764 %A64_763 20
    ld %S32_765 %A64_764 0
    blt %S32_765 currcnt while_4
    bra if_22_end
.bbl while_4
    lea.mem %A64_766 nj 0
    mov %S32_767 5
    st %A64_766 0 %S32_767
    ret
.bbl while_4_cond
    bne 0:S32 0 while_4
    bra if_22_end
.bbl if_22_end
    sub %S32_768 16 codelen
    shl %S32_769 currcnt %S32_768
    sub %S32_770 remain %S32_769
    mov remain %S32_770
    blt remain 0 while_5
    bra if_24_end
.bbl while_5
    lea.mem %A64_771 nj 0
    mov %S32_772 5
    st %A64_771 0 %S32_772
    ret
.bbl while_5_cond
    bne 0:S32 0 while_5
    bra if_24_end
.bbl if_24_end
    mov i 0
    bra for_11_cond
.bbl for_11
    lea.mem %A64_773 nj 0
    lea %A64_774 %A64_773 4
    ld %A64_775 %A64_774 0
    lea %A64_776 %A64_775 i
    ld %U8_777 %A64_776 0
    mov code %U8_777
    mov j spread
    bra for_10_cond
.bbl for_10
    conv %U8_778 codelen
    st vlc 0 %U8_778
    lea %A64_779 vlc 1
    st %A64_779 0 code
    lea %A64_780 vlc 2
    mov vlc %A64_780
.bbl for_10_next
    sub %S32_781 j 1
    mov j %S32_781
.bbl for_10_cond
    bne j 0 for_10
    bra for_11_next
.bbl for_11_next
    add %S32_782 i 1
    mov i %S32_782
.bbl for_11_cond
    blt i currcnt for_11
    bra for_11_exit
.bbl for_11_exit
    pusharg currcnt
    bsr __static_2_njSkip
.bbl for_12_next
    add %S32_783 codelen 1
    mov codelen %S32_783
.bbl for_12_cond
    ble codelen 16 for_12
    bra for_12_exit
.bbl for_12_exit
    bra while_6_cond
.bbl while_6
    sub %S32_784 remain 1
    mov remain %S32_784
    mov %U8_785 0
    st vlc 0 %U8_785
    lea %A64_786 vlc 2
    mov vlc %A64_786
.bbl while_6_cond
    bne remain 0 while_6
    bra while_7_cond
.bbl while_7_cond
    lea.mem %A64_787 nj 0
    lea %A64_788 %A64_787 20
    ld %S32_789 %A64_788 0
    ble 17:S32 %S32_789 while_7
    bra while_7_exit
.bbl while_7_exit
    lea.mem %A64_790 nj 0
    lea %A64_791 %A64_790 20
    ld %S32_792 %A64_791 0
    bne %S32_792 0 while_8
    bra if_31_end
.bbl while_8
    lea.mem %A64_793 nj 0
    mov %S32_794 5
    st %A64_793 0 %S32_794
    ret
.bbl while_8_cond
    bne 0:S32 0 while_8
    bra if_31_end
.bbl if_31_end
    ret

.fun njDecodeDQT NORMAL [] = []
.reg S32 [%S32_797 %S32_802 %S32_803 %S32_805 %S32_808 %S32_809 %S32_810 %S32_815 %S32_820 %S32_824 %S32_825 %S32_828 %S32_831 %S32_833 i]
.reg U8 [%U8_801 %U8_822]
.reg A64 [%A64_795 %A64_796 %A64_798 %A64_799 %A64_800 %A64_804 %A64_806 %A64_807 %A64_811 %A64_812 %A64_813 %A64_814 %A64_816 %A64_817 %A64_818 %A64_819 %A64_821 %A64_823 %A64_826 %A64_827 %A64_829 %A64_830 %A64_832 t]
.bbl %start
    bsr __static_3_njDecodeLength
.bbl while_1
    lea.mem %A64_795 nj 0
    lea %A64_796 %A64_795 0
    ld %S32_797 %A64_796 0
    bne %S32_797 0 if_6_true
    bra while_1_cond
.bbl if_6_true
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra while_1_exit
.bbl while_1_exit
    bra while_3_cond
.bbl while_3
    lea.mem %A64_798 nj 0
    lea %A64_799 %A64_798 4
    ld %A64_800 %A64_799 0
    ld %U8_801 %A64_800 0
    conv %S32_802 %U8_801
    mov i %S32_802
    and %S32_803 i 252
    bne %S32_803 0 while_2
    bra if_9_end
.bbl while_2
    lea.mem %A64_804 nj 0
    mov %S32_805 5
    st %A64_804 0 %S32_805
    ret
.bbl while_2_cond
    bne 0:S32 0 while_2
    bra if_9_end
.bbl if_9_end
    lea.mem %A64_806 nj 0
    lea %A64_807 %A64_806 204
    ld %S32_808 %A64_807 0
    shl %S32_809 1 i
    or %S32_810 %S32_808 %S32_809
    lea.mem %A64_811 nj 0
    lea %A64_812 %A64_811 204
    st %A64_812 0 %S32_810
    lea.mem %A64_813 nj 0
    lea %A64_814 %A64_813 208
    mul %S32_815 i 64
    lea %A64_816 %A64_814 %S32_815
    mov t %A64_816
    mov i 0
    bra for_5_cond
.bbl for_5
    lea.mem %A64_817 nj 0
    lea %A64_818 %A64_817 4
    ld %A64_819 %A64_818 0
    add %S32_820 i 1
    lea %A64_821 %A64_819 %S32_820
    ld %U8_822 %A64_821 0
    lea %A64_823 t i
    st %A64_823 0 %U8_822
.bbl for_5_next
    add %S32_824 i 1
    mov i %S32_824
.bbl for_5_cond
    blt i 64 for_5
    bra for_5_exit
.bbl for_5_exit
    mov %S32_825 65
    pusharg %S32_825
    bsr __static_2_njSkip
.bbl while_3_cond
    lea.mem %A64_826 nj 0
    lea %A64_827 %A64_826 20
    ld %S32_828 %A64_827 0
    ble 65:S32 %S32_828 while_3
    bra while_3_exit
.bbl while_3_exit
    lea.mem %A64_829 nj 0
    lea %A64_830 %A64_829 20
    ld %S32_831 %A64_830 0
    bne %S32_831 0 while_4
    bra if_13_end
.bbl while_4
    lea.mem %A64_832 nj 0
    mov %S32_833 5
    st %A64_832 0 %S32_833
    ret
.bbl while_4_cond
    bne 0:S32 0 while_4
    bra if_13_end
.bbl if_13_end
    ret

.fun njDecodeDRI NORMAL [] = []
.reg S32 [%S32_836 %S32_839 %S32_841 %S32_846 %S32_851]
.reg U16 [%U16_845]
.reg A64 [%A64_834 %A64_835 %A64_837 %A64_838 %A64_840 %A64_842 %A64_843 %A64_844 %A64_847 %A64_848 %A64_849 %A64_850]
.bbl %start
    bsr __static_3_njDecodeLength
.bbl while_1
    lea.mem %A64_834 nj 0
    lea %A64_835 %A64_834 0
    ld %S32_836 %A64_835 0
    bne %S32_836 0 if_3_true
    bra while_1_cond
.bbl if_3_true
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra while_1_exit
.bbl while_1_exit
    lea.mem %A64_837 nj 0
    lea %A64_838 %A64_837 20
    ld %S32_839 %A64_838 0
    blt %S32_839 2 while_2
    bra if_6_end
.bbl while_2
    lea.mem %A64_840 nj 0
    mov %S32_841 5
    st %A64_840 0 %S32_841
    ret
.bbl while_2_cond
    bne 0:S32 0 while_2
    bra if_6_end
.bbl if_6_end
    lea.mem %A64_842 nj 0
    lea %A64_843 %A64_842 4
    ld %A64_844 %A64_843 0
    pusharg %A64_844
    bsr njDecode16
    poparg %U16_845
    conv %S32_846 %U16_845
    lea.mem %A64_847 nj 0
    lea %A64_848 %A64_847 525016
    st %A64_848 0 %S32_846
    lea.mem %A64_849 nj 0
    lea %A64_850 %A64_849 20
    ld %S32_851 %A64_850 0
    pusharg %S32_851
    bsr __static_2_njSkip
    ret

.fun njGetVLC NORMAL [S32] = [A64 A64]
.reg S32 [%S32_852 %S32_853 %S32_854 %S32_858 %S32_860 %S32_861 %S32_865 %S32_867 %S32_868 %S32_869 %S32_870 %S32_871 %S32_872 %S32_873 %out bits value]
.reg U8 [%U8_857 %U8_864 %U8_866]
.reg A64 [%A64_855 %A64_856 %A64_859 %A64_862 %A64_863 code vlc]
.bbl %start
    poparg vlc
    poparg code
    mov %S32_853 16
    pusharg %S32_853
    bsr __static_1_njShowBits
    poparg %S32_852
    mov value %S32_852
    mul %S32_854 value 2
    lea %A64_855 vlc %S32_854
    lea %A64_856 %A64_855 0
    ld %U8_857 %A64_856 0
    conv %S32_858 %U8_857
    mov bits %S32_858
    bne bits 0 if_1_end
    bra if_1_true
.bbl if_1_true
    lea.mem %A64_859 nj 0
    mov %S32_860 5
    st %A64_859 0 %S32_860
    mov %out 0
    pusharg %out
    ret
.bbl if_1_end
    pusharg bits
    bsr njSkipBits
    mul %S32_861 value 2
    lea %A64_862 vlc %S32_861
    lea %A64_863 %A64_862 1
    ld %U8_864 %A64_863 0
    conv %S32_865 %U8_864
    mov value %S32_865
    bne code 0 if_2_true
    bra if_2_end
.bbl if_2_true
    conv %U8_866 value
    st code 0 %U8_866
.bbl if_2_end
    and %S32_867 value 15
    mov bits %S32_867
    bne bits 0 if_3_end
    bra if_3_true
.bbl if_3_true
    mov %out 0
    pusharg %out
    ret
.bbl if_3_end
    pusharg bits
    bsr njGetBits
    poparg %S32_868
    mov value %S32_868
    sub %S32_869 bits 1
    shl %S32_870 1 %S32_869
    blt value %S32_870 if_4_true
    bra if_4_end
.bbl if_4_true
    shl %S32_871 -1 bits
    add %S32_872 %S32_871 1
    add %S32_873 value %S32_872
    mov value %S32_873
.bbl if_4_end
    mov %out value
    pusharg %out
    ret

.fun njDecodeBlock NORMAL [] = [A64 A64]
.reg S8 [%S8_951]
.reg S32 [%S32_880 %S32_883 %S32_887 %S32_888 %S32_889 %S32_891 %S32_893 %S32_896 %S32_900 %S32_901 %S32_904 %S32_905 %S32_911 %S32_912 %S32_913 %S32_916 %S32_919 %S32_922 %S32_923 %S32_926 %S32_928 %S32_931 %S32_932 %S32_933 %S32_934 %S32_936 %S32_940 %S32_941 %S32_942 %S32_945 %S32_946 %S32_952 %S32_953 %S32_957 %S32_959 %S32_962 %S32_966 %S32_967 coef value]
.reg U8 [%U8_875 %U8_903 %U8_918 %U8_921 %U8_925 %U8_930 %U8_944]
.reg U64 [%U64_881]
.reg A64 [%A64_874 %A64_876 %A64_877 %A64_878 %A64_879 %A64_882 %A64_884 %A64_885 %A64_886 %A64_890 %A64_892 %A64_894 %A64_895 %A64_897 %A64_898 %A64_899 %A64_902 %A64_906 %A64_907 %A64_908 %A64_909 %A64_910 %A64_914 %A64_915 %A64_917 %A64_920 %A64_924 %A64_927 %A64_929 %A64_935 %A64_937 %A64_938 %A64_939 %A64_943 %A64_947 %A64_948 %A64_949 %A64_950 %A64_954 %A64_955 %A64_956 %A64_958 %A64_960 %A64_961 %A64_963 %A64_964 %A64_965 c out]
.stk code 1 1
.bbl %start
    poparg c
    poparg out
    lea.stk %A64_874 code 0
    mov %U8_875 0
    st %A64_874 0 %U8_875
    mov coef 0
    lea.mem %A64_876 nj 0
    lea %A64_877 %A64_876 524760
    lea.mem %A64_878 nj 0
    lea %A64_879 %A64_878 524760
    mov %S32_880 0
    mov %U64_881 256
    pusharg %U64_881
    pusharg %S32_880
    pusharg %A64_877
    bsr mymemset
    lea %A64_882 c 36
    ld %S32_883 %A64_882 0
    lea.mem %A64_884 nj 0
    lea %A64_885 %A64_884 464
    lea %A64_886 c 32
    ld %S32_887 %A64_886 0
    mul %S32_888 %S32_887 65536
    mul %S32_889 %S32_888 2
    lea %A64_890 %A64_885 %S32_889
    lea %A64_892 0 0
    pusharg %A64_892
    pusharg %A64_890
    bsr njGetVLC
    poparg %S32_891
    add %S32_893 %S32_883 %S32_891
    lea %A64_894 c 36
    st %A64_894 0 %S32_893
    lea %A64_895 c 36
    ld %S32_896 %A64_895 0
    lea.mem %A64_897 nj 0
    lea %A64_898 %A64_897 208
    lea %A64_899 c 24
    ld %S32_900 %A64_899 0
    mul %S32_901 %S32_900 64
    lea %A64_902 %A64_898 %S32_901
    ld %U8_903 %A64_902 0
    conv %S32_904 %U8_903
    mul %S32_905 %S32_896 %S32_904
    lea.mem %A64_906 nj 0
    lea %A64_907 %A64_906 524760
    st %A64_907 0 %S32_905
.bbl while_3
    lea.mem %A64_908 nj 0
    lea %A64_909 %A64_908 464
    lea %A64_910 c 28
    ld %S32_911 %A64_910 0
    mul %S32_912 %S32_911 65536
    mul %S32_913 %S32_912 2
    lea %A64_914 %A64_909 %S32_913
    lea.stk %A64_915 code 0
    pusharg %A64_915
    pusharg %A64_914
    bsr njGetVLC
    poparg %S32_916
    mov value %S32_916
    lea.stk %A64_917 code 0
    ld %U8_918 %A64_917 0
    conv %S32_919 %U8_918
    bne %S32_919 0 if_6_end
    bra while_3_exit
.bbl if_6_end
    lea.stk %A64_920 code 0
    ld %U8_921 %A64_920 0
    conv %S32_922 %U8_921
    and %S32_923 %S32_922 15
    bne %S32_923 0 if_8_end
    bra branch_14
.bbl branch_14
    lea.stk %A64_924 code 0
    ld %U8_925 %A64_924 0
    conv %S32_926 %U8_925
    bne %S32_926 240 while_1
    bra if_8_end
.bbl while_1
    lea.mem %A64_927 nj 0
    mov %S32_928 5
    st %A64_927 0 %S32_928
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra if_8_end
.bbl if_8_end
    lea.stk %A64_929 code 0
    ld %U8_930 %A64_929 0
    conv %S32_931 %U8_930
    shr %S32_932 %S32_931 4
    add %S32_933 %S32_932 1
    add %S32_934 coef %S32_933
    mov coef %S32_934
    blt 63:S32 coef while_2
    bra if_10_end
.bbl while_2
    lea.mem %A64_935 nj 0
    mov %S32_936 5
    st %A64_935 0 %S32_936
    ret
.bbl while_2_cond
    bne 0:S32 0 while_2
    bra if_10_end
.bbl if_10_end
    lea.mem %A64_937 nj 0
    lea %A64_938 %A64_937 208
    lea %A64_939 c 24
    ld %S32_940 %A64_939 0
    mul %S32_941 %S32_940 64
    add %S32_942 coef %S32_941
    lea %A64_943 %A64_938 %S32_942
    ld %U8_944 %A64_943 0
    conv %S32_945 %U8_944
    mul %S32_946 value %S32_945
    lea.mem %A64_947 nj 0
    lea %A64_948 %A64_947 524760
    lea.mem %A64_949 njZZ 0
    lea %A64_950 %A64_949 coef
    ld %S8_951 %A64_950 0
    conv %S32_952 %S8_951
    mul %S32_953 %S32_952 4
    lea %A64_954 %A64_948 %S32_953
    st %A64_954 0 %S32_946
.bbl while_3_cond
    blt coef 63 while_3
    bra while_3_exit
.bbl while_3_exit
    mov coef 0
    bra for_4_cond
.bbl for_4
    lea.mem %A64_955 nj 0
    lea %A64_956 %A64_955 524760
    mul %S32_957 coef 4
    lea %A64_958 %A64_956 %S32_957
    pusharg %A64_958
    bsr njRowIDCT
.bbl for_4_next
    add %S32_959 coef 8
    mov coef %S32_959
.bbl for_4_cond
    blt coef 64 for_4
    bra for_4_exit
.bbl for_4_exit
    mov coef 0
    bra for_5_cond
.bbl for_5
    lea.mem %A64_960 nj 0
    lea %A64_961 %A64_960 524760
    mul %S32_962 coef 4
    lea %A64_963 %A64_961 %S32_962
    lea %A64_964 out coef
    lea %A64_965 c 20
    ld %S32_966 %A64_965 0
    pusharg %S32_966
    pusharg %A64_964
    pusharg %A64_963
    bsr njColIDCT
.bbl for_5_next
    add %S32_967 coef 1
    mov coef %S32_967
.bbl for_5_cond
    blt coef 8 for_5
    bra for_5_exit
.bbl for_5_exit
    ret

.fun njDecodeScan NORMAL [] = []
.reg S32 [%S32_1002 %S32_1004 %S32_1006 %S32_1012 %S32_1013 %S32_1015 %S32_1021 %S32_1022 %S32_1029 %S32_1030 %S32_1031 %S32_1033 %S32_1034 %S32_1044 %S32_1050 %S32_1056 %S32_1058 %S32_1061 %S32_1067 %S32_1068 %S32_1069 %S32_1071 %S32_1072 %S32_1074 %S32_1075 %S32_1076 %S32_1077 %S32_1078 %S32_1082 %S32_1083 %S32_1085 %S32_1086 %S32_1088 %S32_1089 %S32_1095 %S32_1098 %S32_1099 %S32_1102 %S32_1105 %S32_1106 %S32_1107 %S32_1108 %S32_1109 %S32_1110 %S32_1112 %S32_1113 %S32_1114 %S32_1117 %S32_1120 %S32_1123 %S32_1124 %S32_1126 %S32_970 %S32_973 %S32_976 %S32_984 %S32_994 %S32_995 i mbx mby nextrst rstcount sbx sby]
.reg U8 [%U8_1001 %U8_1011 %U8_1020 %U8_1028 %U8_1043 %U8_1049 %U8_1055 %U8_988]
.reg U32 [%U32_1036 %U32_1039 %U32_1091 %U32_1094 %U32_977 %U32_980 %U32_981 %U32_982 %U32_989 %U32_992]
.reg A64 [%A64_1000 %A64_1003 %A64_1005 %A64_1007 %A64_1008 %A64_1009 %A64_1010 %A64_1014 %A64_1016 %A64_1017 %A64_1018 %A64_1019 %A64_1023 %A64_1024 %A64_1025 %A64_1026 %A64_1027 %A64_1032 %A64_1035 %A64_1037 %A64_1038 %A64_1040 %A64_1041 %A64_1042 %A64_1045 %A64_1046 %A64_1047 %A64_1048 %A64_1051 %A64_1052 %A64_1053 %A64_1054 %A64_1057 %A64_1059 %A64_1060 %A64_1062 %A64_1063 %A64_1064 %A64_1065 %A64_1066 %A64_1070 %A64_1073 %A64_1079 %A64_1080 %A64_1081 %A64_1084 %A64_1087 %A64_1090 %A64_1092 %A64_1093 %A64_1096 %A64_1097 %A64_1100 %A64_1101 %A64_1103 %A64_1104 %A64_1111 %A64_1115 %A64_1116 %A64_1118 %A64_1119 %A64_1121 %A64_1122 %A64_1125 %A64_968 %A64_969 %A64_971 %A64_972 %A64_974 %A64_975 %A64_978 %A64_979 %A64_983 %A64_985 %A64_986 %A64_987 %A64_990 %A64_991 %A64_993 %A64_996 %A64_997 %A64_998 %A64_999 c]
.bbl %start
    lea.mem %A64_968 nj 0
    lea %A64_969 %A64_968 525016
    ld %S32_970 %A64_969 0
    mov rstcount %S32_970
    mov nextrst 0
    bsr __static_3_njDecodeLength
.bbl while_1
    lea.mem %A64_971 nj 0
    lea %A64_972 %A64_971 0
    ld %S32_973 %A64_972 0
    bne %S32_973 0 if_15_true
    bra while_1_cond
.bbl if_15_true
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra while_1_exit
.bbl while_1_exit
    lea.mem %A64_974 nj 0
    lea %A64_975 %A64_974 20
    ld %S32_976 %A64_975 0
    conv %U32_977 %S32_976
    lea.mem %A64_978 nj 0
    lea %A64_979 %A64_978 48
    ld %U32_980 %A64_979 0
    mul %U32_981 2 %U32_980
    add %U32_982 4 %U32_981
    blt %U32_977 %U32_982 while_2
    bra if_18_end
.bbl while_2
    lea.mem %A64_983 nj 0
    mov %S32_984 5
    st %A64_983 0 %S32_984
    ret
.bbl while_2_cond
    bne 0:S32 0 while_2
    bra if_18_end
.bbl if_18_end
    lea.mem %A64_985 nj 0
    lea %A64_986 %A64_985 4
    ld %A64_987 %A64_986 0
    ld %U8_988 %A64_987 0
    conv %U32_989 %U8_988
    lea.mem %A64_990 nj 0
    lea %A64_991 %A64_990 48
    ld %U32_992 %A64_991 0
    bne %U32_989 %U32_992 while_3
    bra if_20_end
.bbl while_3
    lea.mem %A64_993 nj 0
    mov %S32_994 2
    st %A64_993 0 %S32_994
    ret
.bbl while_3_cond
    bne 0:S32 0 while_3
    bra if_20_end
.bbl if_20_end
    mov %S32_995 1
    pusharg %S32_995
    bsr __static_2_njSkip
    mov i 0
    lea.mem %A64_996 nj 0
    lea %A64_997 %A64_996 52
    mov c %A64_997
    bra for_9_cond
.bbl for_9
    lea.mem %A64_998 nj 0
    lea %A64_999 %A64_998 4
    ld %A64_1000 %A64_999 0
    ld %U8_1001 %A64_1000 0
    conv %S32_1002 %U8_1001
    lea %A64_1003 c 0
    ld %S32_1004 %A64_1003 0
    bne %S32_1002 %S32_1004 while_4
    bra if_22_end
.bbl while_4
    lea.mem %A64_1005 nj 0
    mov %S32_1006 5
    st %A64_1005 0 %S32_1006
    ret
.bbl while_4_cond
    bne 0:S32 0 while_4
    bra if_22_end
.bbl if_22_end
    lea.mem %A64_1007 nj 0
    lea %A64_1008 %A64_1007 4
    ld %A64_1009 %A64_1008 0
    lea %A64_1010 %A64_1009 1
    ld %U8_1011 %A64_1010 0
    conv %S32_1012 %U8_1011
    and %S32_1013 %S32_1012 238
    bne %S32_1013 0 while_5
    bra if_24_end
.bbl while_5
    lea.mem %A64_1014 nj 0
    mov %S32_1015 5
    st %A64_1014 0 %S32_1015
    ret
.bbl while_5_cond
    bne 0:S32 0 while_5
    bra if_24_end
.bbl if_24_end
    lea.mem %A64_1016 nj 0
    lea %A64_1017 %A64_1016 4
    ld %A64_1018 %A64_1017 0
    lea %A64_1019 %A64_1018 1
    ld %U8_1020 %A64_1019 0
    conv %S32_1021 %U8_1020
    shr %S32_1022 %S32_1021 4
    lea %A64_1023 c 32
    st %A64_1023 0 %S32_1022
    lea.mem %A64_1024 nj 0
    lea %A64_1025 %A64_1024 4
    ld %A64_1026 %A64_1025 0
    lea %A64_1027 %A64_1026 1
    ld %U8_1028 %A64_1027 0
    conv %S32_1029 %U8_1028
    and %S32_1030 %S32_1029 1
    or %S32_1031 %S32_1030 2
    lea %A64_1032 c 28
    st %A64_1032 0 %S32_1031
    mov %S32_1033 2
    pusharg %S32_1033
    bsr __static_2_njSkip
.bbl for_9_next
    add %S32_1034 i 1
    mov i %S32_1034
    lea %A64_1035 c 48
    mov c %A64_1035
.bbl for_9_cond
    conv %U32_1036 i
    lea.mem %A64_1037 nj 0
    lea %A64_1038 %A64_1037 48
    ld %U32_1039 %A64_1038 0
    blt %U32_1036 %U32_1039 for_9
    bra for_9_exit
.bbl for_9_exit
    lea.mem %A64_1040 nj 0
    lea %A64_1041 %A64_1040 4
    ld %A64_1042 %A64_1041 0
    ld %U8_1043 %A64_1042 0
    conv %S32_1044 %U8_1043
    bne %S32_1044 0 while_6
    bra branch_40
.bbl branch_40
    lea.mem %A64_1045 nj 0
    lea %A64_1046 %A64_1045 4
    ld %A64_1047 %A64_1046 0
    lea %A64_1048 %A64_1047 1
    ld %U8_1049 %A64_1048 0
    conv %S32_1050 %U8_1049
    bne %S32_1050 63 while_6
    bra branch_39
.bbl branch_39
    lea.mem %A64_1051 nj 0
    lea %A64_1052 %A64_1051 4
    ld %A64_1053 %A64_1052 0
    lea %A64_1054 %A64_1053 2
    ld %U8_1055 %A64_1054 0
    conv %S32_1056 %U8_1055
    bne %S32_1056 0 while_6
    bra if_27_end
.bbl while_6
    lea.mem %A64_1057 nj 0
    mov %S32_1058 2
    st %A64_1057 0 %S32_1058
    ret
.bbl while_6_cond
    bne 0:S32 0 while_6
    bra if_27_end
.bbl if_27_end
    lea.mem %A64_1059 nj 0
    lea %A64_1060 %A64_1059 20
    ld %S32_1061 %A64_1060 0
    pusharg %S32_1061
    bsr __static_2_njSkip
    mov mby 0
    mov mbx 0
    bra for_14_cond
.bbl for_14
    mov i 0
    lea.mem %A64_1062 nj 0
    lea %A64_1063 %A64_1062 52
    mov c %A64_1063
    bra for_12_cond
.bbl for_12
    mov sby 0
    bra for_11_cond
.bbl for_11
    mov sbx 0
    bra for_10_cond
.bbl for_10
    lea %A64_1064 c 40
    ld %A64_1065 %A64_1064 0
    lea %A64_1066 c 8
    ld %S32_1067 %A64_1066 0
    mul %S32_1068 mby %S32_1067
    add %S32_1069 %S32_1068 sby
    lea %A64_1070 c 20
    ld %S32_1071 %A64_1070 0
    mul %S32_1072 %S32_1069 %S32_1071
    lea %A64_1073 c 4
    ld %S32_1074 %A64_1073 0
    mul %S32_1075 mbx %S32_1074
    add %S32_1076 %S32_1072 %S32_1075
    add %S32_1077 %S32_1076 sbx
    shl %S32_1078 %S32_1077 3
    lea %A64_1079 %A64_1065 %S32_1078
    pusharg %A64_1079
    pusharg c
    bsr njDecodeBlock
.bbl while_7
    lea.mem %A64_1080 nj 0
    lea %A64_1081 %A64_1080 0
    ld %S32_1082 %A64_1081 0
    bne %S32_1082 0 if_28_true
    bra while_7_cond
.bbl if_28_true
    ret
.bbl while_7_cond
    bne 0:S32 0 while_7
    bra for_10_next
.bbl for_10_next
    add %S32_1083 sbx 1
    mov sbx %S32_1083
.bbl for_10_cond
    lea %A64_1084 c 4
    ld %S32_1085 %A64_1084 0
    blt sbx %S32_1085 for_10
    bra for_11_next
.bbl for_11_next
    add %S32_1086 sby 1
    mov sby %S32_1086
.bbl for_11_cond
    lea %A64_1087 c 8
    ld %S32_1088 %A64_1087 0
    blt sby %S32_1088 for_11
    bra for_12_next
.bbl for_12_next
    add %S32_1089 i 1
    mov i %S32_1089
    lea %A64_1090 c 48
    mov c %A64_1090
.bbl for_12_cond
    conv %U32_1091 i
    lea.mem %A64_1092 nj 0
    lea %A64_1093 %A64_1092 48
    ld %U32_1094 %A64_1093 0
    blt %U32_1091 %U32_1094 for_12
    bra for_12_exit
.bbl for_12_exit
    add %S32_1095 mbx 1
    mov mbx %S32_1095
    lea.mem %A64_1096 nj 0
    lea %A64_1097 %A64_1096 32
    ld %S32_1098 %A64_1097 0
    ble %S32_1098 %S32_1095 if_34_true
    bra if_34_end
.bbl if_34_true
    mov mbx 0
    add %S32_1099 mby 1
    mov mby %S32_1099
    lea.mem %A64_1100 nj 0
    lea %A64_1101 %A64_1100 36
    ld %S32_1102 %A64_1101 0
    ble %S32_1102 %S32_1099 for_14_exit
    bra if_34_end
.bbl if_34_end
    lea.mem %A64_1103 nj 0
    lea %A64_1104 %A64_1103 525016
    ld %S32_1105 %A64_1104 0
    bne %S32_1105 0 branch_41
    bra for_14_cond
.bbl branch_41
    sub %S32_1106 rstcount 1
    mov rstcount %S32_1106
    bne %S32_1106 0 for_14_cond
    bra if_38_true
.bbl if_38_true
    bsr njByteAlign
    mov %S32_1108 16
    pusharg %S32_1108
    bsr njGetBits
    poparg %S32_1107
    mov i %S32_1107
    and %S32_1109 i 65528
    bne %S32_1109 65488 while_8
    bra branch_42
.bbl branch_42
    and %S32_1110 i 7
    bne %S32_1110 nextrst while_8
    bra if_36_end
.bbl while_8
    lea.mem %A64_1111 nj 0
    mov %S32_1112 5
    st %A64_1111 0 %S32_1112
    ret
.bbl while_8_cond
    bne 0:S32 0 while_8
    bra if_36_end
.bbl if_36_end
    add %S32_1113 nextrst 1
    and %S32_1114 %S32_1113 7
    mov nextrst %S32_1114
    lea.mem %A64_1115 nj 0
    lea %A64_1116 %A64_1115 525016
    ld %S32_1117 %A64_1116 0
    mov rstcount %S32_1117
    mov i 0
    bra for_13_cond
.bbl for_13
    lea.mem %A64_1118 nj 0
    lea %A64_1119 %A64_1118 52
    mul %S32_1120 i 48
    lea %A64_1121 %A64_1119 %S32_1120
    lea %A64_1122 %A64_1121 36
    mov %S32_1123 0
    st %A64_1122 0 %S32_1123
.bbl for_13_next
    add %S32_1124 i 1
    mov i %S32_1124
.bbl for_13_cond
    blt i 3 for_13
    bra for_14_cond
.bbl for_14_cond
    bra for_14
.bbl for_14_exit
    lea.mem %A64_1125 nj 0
    mov %S32_1126 6
    st %A64_1125 0 %S32_1126
    ret

.fun njUpsampleH NORMAL [] = [A64]
.reg S32 [%S32_1128 %S32_1129 %S32_1131 %S32_1133 %S32_1134 %S32_1135 %S32_1139 %S32_1143 %S32_1145 %S32_1146 %S32_1149 %S32_1150 %S32_1151 %S32_1152 %S32_1153 %S32_1156 %S32_1157 %S32_1160 %S32_1161 %S32_1162 %S32_1165 %S32_1166 %S32_1167 %S32_1168 %S32_1169 %S32_1173 %S32_1174 %S32_1177 %S32_1178 %S32_1179 %S32_1182 %S32_1183 %S32_1184 %S32_1185 %S32_1186 %S32_1191 %S32_1192 %S32_1193 %S32_1196 %S32_1197 %S32_1198 %S32_1199 %S32_1202 %S32_1203 %S32_1204 %S32_1205 %S32_1208 %S32_1209 %S32_1210 %S32_1211 %S32_1212 %S32_1214 %S32_1215 %S32_1219 %S32_1220 %S32_1221 %S32_1224 %S32_1225 %S32_1226 %S32_1227 %S32_1230 %S32_1231 %S32_1232 %S32_1233 %S32_1236 %S32_1237 %S32_1238 %S32_1239 %S32_1240 %S32_1242 %S32_1243 %S32_1245 %S32_1247 %S32_1250 %S32_1251 %S32_1255 %S32_1256 %S32_1259 %S32_1260 %S32_1261 %S32_1264 %S32_1265 %S32_1266 %S32_1267 %S32_1268 %S32_1273 %S32_1274 %S32_1277 %S32_1278 %S32_1279 %S32_1282 %S32_1283 %S32_1284 %S32_1285 %S32_1286 %S32_1291 %S32_1292 %S32_1295 %S32_1296 %S32_1297 %S32_1298 %S32_1299 %S32_1302 %S32_1304 %S32_1305 %S32_1308 x xmax y]
.reg U8 [%U8_1144 %U8_1148 %U8_1154 %U8_1155 %U8_1159 %U8_1164 %U8_1170 %U8_1172 %U8_1176 %U8_1181 %U8_1187 %U8_1190 %U8_1195 %U8_1201 %U8_1207 %U8_1213 %U8_1218 %U8_1223 %U8_1229 %U8_1235 %U8_1241 %U8_1254 %U8_1258 %U8_1263 %U8_1269 %U8_1272 %U8_1276 %U8_1281 %U8_1287 %U8_1290 %U8_1294 %U8_1300]
.reg U64 [%U64_1136]
.reg A64 [%A64_1127 %A64_1130 %A64_1132 %A64_1137 %A64_1138 %A64_1140 %A64_1141 %A64_1142 %A64_1147 %A64_1158 %A64_1163 %A64_1171 %A64_1175 %A64_1180 %A64_1188 %A64_1189 %A64_1194 %A64_1200 %A64_1206 %A64_1216 %A64_1217 %A64_1222 %A64_1228 %A64_1234 %A64_1244 %A64_1246 %A64_1248 %A64_1249 %A64_1252 %A64_1253 %A64_1257 %A64_1262 %A64_1270 %A64_1271 %A64_1275 %A64_1280 %A64_1288 %A64_1289 %A64_1293 %A64_1301 %A64_1303 %A64_1306 %A64_1307 %A64_1309 %A64_1310 %A64_1311 %A64_1312 c lin lout out]
.bbl %start
    poparg c
    lea %A64_1127 c 12
    ld %S32_1128 %A64_1127 0
    sub %S32_1129 %S32_1128 3
    mov xmax %S32_1129
    lea %A64_1130 c 12
    ld %S32_1131 %A64_1130 0
    lea %A64_1132 c 16
    ld %S32_1133 %A64_1132 0
    mul %S32_1134 %S32_1131 %S32_1133
    shl %S32_1135 %S32_1134 1
    conv %U64_1136 %S32_1135
    pusharg %U64_1136
    bsr malloc
    poparg %A64_1137
    mov out %A64_1137
    bne out 0 if_5_end
    bra while_1
.bbl while_1
    lea.mem %A64_1138 nj 0
    mov %S32_1139 3
    st %A64_1138 0 %S32_1139
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra if_5_end
.bbl if_5_end
    lea %A64_1140 c 40
    ld %A64_1141 %A64_1140 0
    mov lin %A64_1141
    mov lout out
    lea %A64_1142 c 16
    ld %S32_1143 %A64_1142 0
    mov y %S32_1143
    bra for_3_cond
.bbl for_3
    ld %U8_1144 lin 0
    conv %S32_1145 %U8_1144
    mul %S32_1146 139 %S32_1145
    lea %A64_1147 lin 1
    ld %U8_1148 %A64_1147 0
    conv %S32_1149 %U8_1148
    mul %S32_1150 -11 %S32_1149
    add %S32_1151 %S32_1146 %S32_1150
    add %S32_1152 %S32_1151 64
    shr %S32_1153 %S32_1152 7
    pusharg %S32_1153
    bsr njClip
    poparg %U8_1154
    st lout 0 %U8_1154
    ld %U8_1155 lin 0
    conv %S32_1156 %U8_1155
    mul %S32_1157 104 %S32_1156
    lea %A64_1158 lin 1
    ld %U8_1159 %A64_1158 0
    conv %S32_1160 %U8_1159
    mul %S32_1161 27 %S32_1160
    add %S32_1162 %S32_1157 %S32_1161
    lea %A64_1163 lin 2
    ld %U8_1164 %A64_1163 0
    conv %S32_1165 %U8_1164
    mul %S32_1166 -3 %S32_1165
    add %S32_1167 %S32_1162 %S32_1166
    add %S32_1168 %S32_1167 64
    shr %S32_1169 %S32_1168 7
    pusharg %S32_1169
    bsr njClip
    poparg %U8_1170
    lea %A64_1171 lout 1
    st %A64_1171 0 %U8_1170
    ld %U8_1172 lin 0
    conv %S32_1173 %U8_1172
    mul %S32_1174 28 %S32_1173
    lea %A64_1175 lin 1
    ld %U8_1176 %A64_1175 0
    conv %S32_1177 %U8_1176
    mul %S32_1178 109 %S32_1177
    add %S32_1179 %S32_1174 %S32_1178
    lea %A64_1180 lin 2
    ld %U8_1181 %A64_1180 0
    conv %S32_1182 %U8_1181
    mul %S32_1183 -9 %S32_1182
    add %S32_1184 %S32_1179 %S32_1183
    add %S32_1185 %S32_1184 64
    shr %S32_1186 %S32_1185 7
    pusharg %S32_1186
    bsr njClip
    poparg %U8_1187
    lea %A64_1188 lout 2
    st %A64_1188 0 %U8_1187
    mov x 0
    bra for_2_cond
.bbl for_2
    lea %A64_1189 lin x
    ld %U8_1190 %A64_1189 0
    conv %S32_1191 %U8_1190
    mul %S32_1192 -9 %S32_1191
    add %S32_1193 x 1
    lea %A64_1194 lin %S32_1193
    ld %U8_1195 %A64_1194 0
    conv %S32_1196 %U8_1195
    mul %S32_1197 111 %S32_1196
    add %S32_1198 %S32_1192 %S32_1197
    add %S32_1199 x 2
    lea %A64_1200 lin %S32_1199
    ld %U8_1201 %A64_1200 0
    conv %S32_1202 %U8_1201
    mul %S32_1203 29 %S32_1202
    add %S32_1204 %S32_1198 %S32_1203
    add %S32_1205 x 3
    lea %A64_1206 lin %S32_1205
    ld %U8_1207 %A64_1206 0
    conv %S32_1208 %U8_1207
    mul %S32_1209 -3 %S32_1208
    add %S32_1210 %S32_1204 %S32_1209
    add %S32_1211 %S32_1210 64
    shr %S32_1212 %S32_1211 7
    pusharg %S32_1212
    bsr njClip
    poparg %U8_1213
    shl %S32_1214 x 1
    add %S32_1215 %S32_1214 3
    lea %A64_1216 lout %S32_1215
    st %A64_1216 0 %U8_1213
    lea %A64_1217 lin x
    ld %U8_1218 %A64_1217 0
    conv %S32_1219 %U8_1218
    mul %S32_1220 -3 %S32_1219
    add %S32_1221 x 1
    lea %A64_1222 lin %S32_1221
    ld %U8_1223 %A64_1222 0
    conv %S32_1224 %U8_1223
    mul %S32_1225 29 %S32_1224
    add %S32_1226 %S32_1220 %S32_1225
    add %S32_1227 x 2
    lea %A64_1228 lin %S32_1227
    ld %U8_1229 %A64_1228 0
    conv %S32_1230 %U8_1229
    mul %S32_1231 111 %S32_1230
    add %S32_1232 %S32_1226 %S32_1231
    add %S32_1233 x 3
    lea %A64_1234 lin %S32_1233
    ld %U8_1235 %A64_1234 0
    conv %S32_1236 %U8_1235
    mul %S32_1237 -9 %S32_1236
    add %S32_1238 %S32_1232 %S32_1237
    add %S32_1239 %S32_1238 64
    shr %S32_1240 %S32_1239 7
    pusharg %S32_1240
    bsr njClip
    poparg %U8_1241
    shl %S32_1242 x 1
    add %S32_1243 %S32_1242 4
    lea %A64_1244 lout %S32_1243
    st %A64_1244 0 %U8_1241
.bbl for_2_next
    add %S32_1245 x 1
    mov x %S32_1245
.bbl for_2_cond
    blt x xmax for_2
    bra for_2_exit
.bbl for_2_exit
    lea %A64_1246 c 20
    ld %S32_1247 %A64_1246 0
    lea %A64_1248 lin %S32_1247
    mov lin %A64_1248
    lea %A64_1249 c 12
    ld %S32_1250 %A64_1249 0
    shl %S32_1251 %S32_1250 1
    lea %A64_1252 lout %S32_1251
    mov lout %A64_1252
    lea %A64_1253 lin -1
    ld %U8_1254 %A64_1253 0
    conv %S32_1255 %U8_1254
    mul %S32_1256 28 %S32_1255
    lea %A64_1257 lin -2
    ld %U8_1258 %A64_1257 0
    conv %S32_1259 %U8_1258
    mul %S32_1260 109 %S32_1259
    add %S32_1261 %S32_1256 %S32_1260
    lea %A64_1262 lin -3
    ld %U8_1263 %A64_1262 0
    conv %S32_1264 %U8_1263
    mul %S32_1265 -9 %S32_1264
    add %S32_1266 %S32_1261 %S32_1265
    add %S32_1267 %S32_1266 64
    shr %S32_1268 %S32_1267 7
    pusharg %S32_1268
    bsr njClip
    poparg %U8_1269
    lea %A64_1270 lout -3
    st %A64_1270 0 %U8_1269
    lea %A64_1271 lin -1
    ld %U8_1272 %A64_1271 0
    conv %S32_1273 %U8_1272
    mul %S32_1274 104 %S32_1273
    lea %A64_1275 lin -2
    ld %U8_1276 %A64_1275 0
    conv %S32_1277 %U8_1276
    mul %S32_1278 27 %S32_1277
    add %S32_1279 %S32_1274 %S32_1278
    lea %A64_1280 lin -3
    ld %U8_1281 %A64_1280 0
    conv %S32_1282 %U8_1281
    mul %S32_1283 -3 %S32_1282
    add %S32_1284 %S32_1279 %S32_1283
    add %S32_1285 %S32_1284 64
    shr %S32_1286 %S32_1285 7
    pusharg %S32_1286
    bsr njClip
    poparg %U8_1287
    lea %A64_1288 lout -2
    st %A64_1288 0 %U8_1287
    lea %A64_1289 lin -1
    ld %U8_1290 %A64_1289 0
    conv %S32_1291 %U8_1290
    mul %S32_1292 139 %S32_1291
    lea %A64_1293 lin -2
    ld %U8_1294 %A64_1293 0
    conv %S32_1295 %U8_1294
    mul %S32_1296 -11 %S32_1295
    add %S32_1297 %S32_1292 %S32_1296
    add %S32_1298 %S32_1297 64
    shr %S32_1299 %S32_1298 7
    pusharg %S32_1299
    bsr njClip
    poparg %U8_1300
    lea %A64_1301 lout -1
    st %A64_1301 0 %U8_1300
.bbl for_3_next
    sub %S32_1302 y 1
    mov y %S32_1302
.bbl for_3_cond
    bne y 0 for_3
    bra for_3_exit
.bbl for_3_exit
    lea %A64_1303 c 12
    ld %S32_1304 %A64_1303 0
    shl %S32_1305 %S32_1304 1
    lea %A64_1306 c 12
    st %A64_1306 0 %S32_1305
    lea %A64_1307 c 12
    ld %S32_1308 %A64_1307 0
    lea %A64_1309 c 20
    st %A64_1309 0 %S32_1308
    lea %A64_1310 c 40
    ld %A64_1311 %A64_1310 0
    pusharg %A64_1311
    bsr free
    lea %A64_1312 c 40
    st %A64_1312 0 out
    ret

.fun njUpsampleV NORMAL [] = [A64]
.reg S32 [%S32_1314 %S32_1316 %S32_1317 %S32_1319 %S32_1321 %S32_1322 %S32_1323 %S32_1327 %S32_1333 %S32_1334 %S32_1337 %S32_1338 %S32_1339 %S32_1340 %S32_1341 %S32_1345 %S32_1346 %S32_1349 %S32_1350 %S32_1351 %S32_1354 %S32_1355 %S32_1356 %S32_1357 %S32_1358 %S32_1362 %S32_1363 %S32_1366 %S32_1367 %S32_1368 %S32_1371 %S32_1372 %S32_1373 %S32_1374 %S32_1375 %S32_1380 %S32_1381 %S32_1382 %S32_1385 %S32_1386 %S32_1388 %S32_1389 %S32_1390 %S32_1393 %S32_1394 %S32_1395 %S32_1398 %S32_1399 %S32_1400 %S32_1401 %S32_1402 %S32_1405 %S32_1408 %S32_1409 %S32_1411 %S32_1412 %S32_1413 %S32_1416 %S32_1417 %S32_1418 %S32_1421 %S32_1422 %S32_1423 %S32_1424 %S32_1425 %S32_1429 %S32_1432 %S32_1433 %S32_1434 %S32_1437 %S32_1438 %S32_1439 %S32_1440 %S32_1443 %S32_1444 %S32_1445 %S32_1446 %S32_1447 %S32_1451 %S32_1452 %S32_1453 %S32_1456 %S32_1457 %S32_1458 %S32_1459 %S32_1462 %S32_1463 %S32_1464 %S32_1465 %S32_1466 %S32_1470 %S32_1471 %S32_1472 %S32_1475 %S32_1476 %S32_1477 %S32_1478 %S32_1479 %S32_1481 %S32_1483 %S32_1484 %S32_1487 s1 s2 w x y]
.reg U8 [%U8_1332 %U8_1336 %U8_1342 %U8_1344 %U8_1348 %U8_1353 %U8_1359 %U8_1361 %U8_1365 %U8_1370 %U8_1376 %U8_1384 %U8_1387 %U8_1392 %U8_1397 %U8_1403 %U8_1407 %U8_1410 %U8_1415 %U8_1420 %U8_1426 %U8_1431 %U8_1436 %U8_1442 %U8_1448 %U8_1450 %U8_1455 %U8_1461 %U8_1467 %U8_1469 %U8_1474 %U8_1480]
.reg U64 [%U64_1324]
.reg A64 [%A64_1313 %A64_1315 %A64_1318 %A64_1320 %A64_1325 %A64_1326 %A64_1328 %A64_1329 %A64_1330 %A64_1331 %A64_1335 %A64_1343 %A64_1347 %A64_1352 %A64_1360 %A64_1364 %A64_1369 %A64_1377 %A64_1378 %A64_1379 %A64_1383 %A64_1391 %A64_1396 %A64_1404 %A64_1406 %A64_1414 %A64_1419 %A64_1427 %A64_1428 %A64_1430 %A64_1435 %A64_1441 %A64_1449 %A64_1454 %A64_1460 %A64_1468 %A64_1473 %A64_1482 %A64_1485 %A64_1486 %A64_1488 %A64_1489 %A64_1490 %A64_1491 c cin cout out]
.bbl %start
    poparg c
    lea %A64_1313 c 12
    ld %S32_1314 %A64_1313 0
    mov w %S32_1314
    lea %A64_1315 c 20
    ld %S32_1316 %A64_1315 0
    mov s1 %S32_1316
    add %S32_1317 s1 s1
    mov s2 %S32_1317
    lea %A64_1318 c 12
    ld %S32_1319 %A64_1318 0
    lea %A64_1320 c 16
    ld %S32_1321 %A64_1320 0
    mul %S32_1322 %S32_1319 %S32_1321
    shl %S32_1323 %S32_1322 1
    conv %U64_1324 %S32_1323
    pusharg %U64_1324
    bsr malloc
    poparg %A64_1325
    mov out %A64_1325
    bne out 0 if_5_end
    bra while_1
.bbl while_1
    lea.mem %A64_1326 nj 0
    mov %S32_1327 3
    st %A64_1326 0 %S32_1327
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra if_5_end
.bbl if_5_end
    mov x 0
    bra for_3_cond
.bbl for_3
    lea %A64_1328 c 40
    ld %A64_1329 %A64_1328 0
    lea %A64_1330 %A64_1329 x
    mov cin %A64_1330
    lea %A64_1331 out x
    mov cout %A64_1331
    ld %U8_1332 cin 0
    conv %S32_1333 %U8_1332
    mul %S32_1334 139 %S32_1333
    lea %A64_1335 cin s1
    ld %U8_1336 %A64_1335 0
    conv %S32_1337 %U8_1336
    mul %S32_1338 -11 %S32_1337
    add %S32_1339 %S32_1334 %S32_1338
    add %S32_1340 %S32_1339 64
    shr %S32_1341 %S32_1340 7
    pusharg %S32_1341
    bsr njClip
    poparg %U8_1342
    st cout 0 %U8_1342
    lea %A64_1343 cout w
    mov cout %A64_1343
    ld %U8_1344 cin 0
    conv %S32_1345 %U8_1344
    mul %S32_1346 104 %S32_1345
    lea %A64_1347 cin s1
    ld %U8_1348 %A64_1347 0
    conv %S32_1349 %U8_1348
    mul %S32_1350 27 %S32_1349
    add %S32_1351 %S32_1346 %S32_1350
    lea %A64_1352 cin s2
    ld %U8_1353 %A64_1352 0
    conv %S32_1354 %U8_1353
    mul %S32_1355 -3 %S32_1354
    add %S32_1356 %S32_1351 %S32_1355
    add %S32_1357 %S32_1356 64
    shr %S32_1358 %S32_1357 7
    pusharg %S32_1358
    bsr njClip
    poparg %U8_1359
    st cout 0 %U8_1359
    lea %A64_1360 cout w
    mov cout %A64_1360
    ld %U8_1361 cin 0
    conv %S32_1362 %U8_1361
    mul %S32_1363 28 %S32_1362
    lea %A64_1364 cin s1
    ld %U8_1365 %A64_1364 0
    conv %S32_1366 %U8_1365
    mul %S32_1367 109 %S32_1366
    add %S32_1368 %S32_1363 %S32_1367
    lea %A64_1369 cin s2
    ld %U8_1370 %A64_1369 0
    conv %S32_1371 %U8_1370
    mul %S32_1372 -9 %S32_1371
    add %S32_1373 %S32_1368 %S32_1372
    add %S32_1374 %S32_1373 64
    shr %S32_1375 %S32_1374 7
    pusharg %S32_1375
    bsr njClip
    poparg %U8_1376
    st cout 0 %U8_1376
    lea %A64_1377 cout w
    mov cout %A64_1377
    lea %A64_1378 cin s1
    mov cin %A64_1378
    lea %A64_1379 c 16
    ld %S32_1380 %A64_1379 0
    sub %S32_1381 %S32_1380 3
    mov y %S32_1381
    bra for_2_cond
.bbl for_2
    sub %S32_1382 0 s1
    lea %A64_1383 cin %S32_1382
    ld %U8_1384 %A64_1383 0
    conv %S32_1385 %U8_1384
    mul %S32_1386 -9 %S32_1385
    ld %U8_1387 cin 0
    conv %S32_1388 %U8_1387
    mul %S32_1389 111 %S32_1388
    add %S32_1390 %S32_1386 %S32_1389
    lea %A64_1391 cin s1
    ld %U8_1392 %A64_1391 0
    conv %S32_1393 %U8_1392
    mul %S32_1394 29 %S32_1393
    add %S32_1395 %S32_1390 %S32_1394
    lea %A64_1396 cin s2
    ld %U8_1397 %A64_1396 0
    conv %S32_1398 %U8_1397
    mul %S32_1399 -3 %S32_1398
    add %S32_1400 %S32_1395 %S32_1399
    add %S32_1401 %S32_1400 64
    shr %S32_1402 %S32_1401 7
    pusharg %S32_1402
    bsr njClip
    poparg %U8_1403
    st cout 0 %U8_1403
    lea %A64_1404 cout w
    mov cout %A64_1404
    sub %S32_1405 0 s1
    lea %A64_1406 cin %S32_1405
    ld %U8_1407 %A64_1406 0
    conv %S32_1408 %U8_1407
    mul %S32_1409 -3 %S32_1408
    ld %U8_1410 cin 0
    conv %S32_1411 %U8_1410
    mul %S32_1412 29 %S32_1411
    add %S32_1413 %S32_1409 %S32_1412
    lea %A64_1414 cin s1
    ld %U8_1415 %A64_1414 0
    conv %S32_1416 %U8_1415
    mul %S32_1417 111 %S32_1416
    add %S32_1418 %S32_1413 %S32_1417
    lea %A64_1419 cin s2
    ld %U8_1420 %A64_1419 0
    conv %S32_1421 %U8_1420
    mul %S32_1422 -9 %S32_1421
    add %S32_1423 %S32_1418 %S32_1422
    add %S32_1424 %S32_1423 64
    shr %S32_1425 %S32_1424 7
    pusharg %S32_1425
    bsr njClip
    poparg %U8_1426
    st cout 0 %U8_1426
    lea %A64_1427 cout w
    mov cout %A64_1427
    lea %A64_1428 cin s1
    mov cin %A64_1428
.bbl for_2_next
    sub %S32_1429 y 1
    mov y %S32_1429
.bbl for_2_cond
    bne y 0 for_2
    bra for_2_exit
.bbl for_2_exit
    lea %A64_1430 cin s1
    mov cin %A64_1430
    ld %U8_1431 cin 0
    conv %S32_1432 %U8_1431
    mul %S32_1433 28 %S32_1432
    sub %S32_1434 0 s1
    lea %A64_1435 cin %S32_1434
    ld %U8_1436 %A64_1435 0
    conv %S32_1437 %U8_1436
    mul %S32_1438 109 %S32_1437
    add %S32_1439 %S32_1433 %S32_1438
    sub %S32_1440 0 s2
    lea %A64_1441 cin %S32_1440
    ld %U8_1442 %A64_1441 0
    conv %S32_1443 %U8_1442
    mul %S32_1444 -9 %S32_1443
    add %S32_1445 %S32_1439 %S32_1444
    add %S32_1446 %S32_1445 64
    shr %S32_1447 %S32_1446 7
    pusharg %S32_1447
    bsr njClip
    poparg %U8_1448
    st cout 0 %U8_1448
    lea %A64_1449 cout w
    mov cout %A64_1449
    ld %U8_1450 cin 0
    conv %S32_1451 %U8_1450
    mul %S32_1452 104 %S32_1451
    sub %S32_1453 0 s1
    lea %A64_1454 cin %S32_1453
    ld %U8_1455 %A64_1454 0
    conv %S32_1456 %U8_1455
    mul %S32_1457 27 %S32_1456
    add %S32_1458 %S32_1452 %S32_1457
    sub %S32_1459 0 s2
    lea %A64_1460 cin %S32_1459
    ld %U8_1461 %A64_1460 0
    conv %S32_1462 %U8_1461
    mul %S32_1463 -3 %S32_1462
    add %S32_1464 %S32_1458 %S32_1463
    add %S32_1465 %S32_1464 64
    shr %S32_1466 %S32_1465 7
    pusharg %S32_1466
    bsr njClip
    poparg %U8_1467
    st cout 0 %U8_1467
    lea %A64_1468 cout w
    mov cout %A64_1468
    ld %U8_1469 cin 0
    conv %S32_1470 %U8_1469
    mul %S32_1471 139 %S32_1470
    sub %S32_1472 0 s1
    lea %A64_1473 cin %S32_1472
    ld %U8_1474 %A64_1473 0
    conv %S32_1475 %U8_1474
    mul %S32_1476 -11 %S32_1475
    add %S32_1477 %S32_1471 %S32_1476
    add %S32_1478 %S32_1477 64
    shr %S32_1479 %S32_1478 7
    pusharg %S32_1479
    bsr njClip
    poparg %U8_1480
    st cout 0 %U8_1480
.bbl for_3_next
    add %S32_1481 x 1
    mov x %S32_1481
.bbl for_3_cond
    blt x w for_3
    bra for_3_exit
.bbl for_3_exit
    lea %A64_1482 c 16
    ld %S32_1483 %A64_1482 0
    shl %S32_1484 %S32_1483 1
    lea %A64_1485 c 16
    st %A64_1485 0 %S32_1484
    lea %A64_1486 c 12
    ld %S32_1487 %A64_1486 0
    lea %A64_1488 c 20
    st %A64_1488 0 %S32_1487
    lea %A64_1489 c 40
    ld %A64_1490 %A64_1489 0
    pusharg %A64_1490
    bsr free
    lea %A64_1491 c 40
    st %A64_1491 0 out
    ret

.fun njConvert NORMAL [] = []
.reg S32 [%S32_1495 %S32_1498 %S32_1501 %S32_1503 %S32_1506 %S32_1509 %S32_1511 %S32_1514 %S32_1516 %S32_1519 %S32_1521 %S32_1524 %S32_1526 %S32_1529 %S32_1531 %S32_1532 %S32_1560 %S32_1563 %S32_1564 %S32_1567 %S32_1568 %S32_1571 %S32_1572 %S32_1573 %S32_1574 %S32_1575 %S32_1576 %S32_1578 %S32_1579 %S32_1580 %S32_1581 %S32_1582 %S32_1583 %S32_1586 %S32_1587 %S32_1588 %S32_1589 %S32_1593 %S32_1596 %S32_1600 %S32_1606 %S32_1612 %S32_1614 %S32_1618 %S32_1622 %S32_1630 %S32_1639 %S32_1644 %S32_1645 %S32_1649 %S32_1654 %S32_1659 %S32_1661 %S32_1665 __local_26_y cb cr i x y yy]
.reg U8 [%U8_1562 %U8_1566 %U8_1570 %U8_1577 %U8_1584 %U8_1590]
.reg U32 [%U32_1534 %U32_1537 %U32_1540]
.reg U64 [%U64_1650]
.reg A64 [%A64_1492 %A64_1493 %A64_1494 %A64_1496 %A64_1497 %A64_1499 %A64_1500 %A64_1502 %A64_1504 %A64_1505 %A64_1507 %A64_1508 %A64_1510 %A64_1512 %A64_1513 %A64_1515 %A64_1517 %A64_1518 %A64_1520 %A64_1522 %A64_1523 %A64_1525 %A64_1527 %A64_1528 %A64_1530 %A64_1533 %A64_1535 %A64_1536 %A64_1538 %A64_1539 %A64_1541 %A64_1542 %A64_1543 %A64_1544 %A64_1545 %A64_1546 %A64_1547 %A64_1548 %A64_1549 %A64_1550 %A64_1551 %A64_1552 %A64_1553 %A64_1554 %A64_1555 %A64_1556 %A64_1557 %A64_1558 %A64_1559 %A64_1561 %A64_1565 %A64_1569 %A64_1585 %A64_1591 %A64_1592 %A64_1594 %A64_1595 %A64_1597 %A64_1598 %A64_1599 %A64_1601 %A64_1602 %A64_1603 %A64_1604 %A64_1605 %A64_1607 %A64_1608 %A64_1609 %A64_1610 %A64_1611 %A64_1613 %A64_1615 %A64_1616 %A64_1617 %A64_1619 %A64_1620 %A64_1621 %A64_1623 %A64_1624 %A64_1625 %A64_1626 %A64_1627 %A64_1628 %A64_1629 %A64_1631 %A64_1632 %A64_1633 %A64_1634 %A64_1635 %A64_1636 %A64_1637 %A64_1638 %A64_1640 %A64_1641 %A64_1642 %A64_1643 %A64_1646 %A64_1647 %A64_1648 %A64_1651 %A64_1652 %A64_1653 %A64_1655 %A64_1656 %A64_1657 %A64_1658 %A64_1660 %A64_1662 %A64_1663 %A64_1664 %A64_1666 %A64_1667 %A64_1668 c pcb pcr pin pout prgb py]
.bbl %start
    mov i 0
    lea.mem %A64_1492 nj 0
    lea %A64_1493 %A64_1492 52
    mov c %A64_1493
    bra for_5_cond
.bbl for_5
    bra while_3_cond
.bbl while_3
    lea %A64_1494 c 12
    ld %S32_1495 %A64_1494 0
    lea.mem %A64_1496 nj 0
    lea %A64_1497 %A64_1496 24
    ld %S32_1498 %A64_1497 0
    blt %S32_1495 %S32_1498 if_9_true
    bra while_1
.bbl if_9_true
    pusharg c
    bsr njUpsampleH
.bbl while_1
    lea.mem %A64_1499 nj 0
    lea %A64_1500 %A64_1499 0
    ld %S32_1501 %A64_1500 0
    bne %S32_1501 0 if_10_true
    bra while_1_cond
.bbl if_10_true
    ret
.bbl while_1_cond
    bne 0:S32 0 while_1
    bra while_1_exit
.bbl while_1_exit
    lea %A64_1502 c 16
    ld %S32_1503 %A64_1502 0
    lea.mem %A64_1504 nj 0
    lea %A64_1505 %A64_1504 28
    ld %S32_1506 %A64_1505 0
    blt %S32_1503 %S32_1506 if_12_true
    bra while_2
.bbl if_12_true
    pusharg c
    bsr njUpsampleV
.bbl while_2
    lea.mem %A64_1507 nj 0
    lea %A64_1508 %A64_1507 0
    ld %S32_1509 %A64_1508 0
    bne %S32_1509 0 if_13_true
    bra while_2_cond
.bbl if_13_true
    ret
.bbl while_2_cond
    bne 0:S32 0 while_2
    bra while_3_cond
.bbl while_3_cond
    lea %A64_1510 c 12
    ld %S32_1511 %A64_1510 0
    lea.mem %A64_1512 nj 0
    lea %A64_1513 %A64_1512 24
    ld %S32_1514 %A64_1513 0
    blt %S32_1511 %S32_1514 while_3
    bra branch_24
.bbl branch_24
    lea %A64_1515 c 16
    ld %S32_1516 %A64_1515 0
    lea.mem %A64_1517 nj 0
    lea %A64_1518 %A64_1517 28
    ld %S32_1519 %A64_1518 0
    blt %S32_1516 %S32_1519 while_3
    bra while_3_exit
.bbl while_3_exit
    lea %A64_1520 c 12
    ld %S32_1521 %A64_1520 0
    lea.mem %A64_1522 nj 0
    lea %A64_1523 %A64_1522 24
    ld %S32_1524 %A64_1523 0
    blt %S32_1521 %S32_1524 while_4
    bra branch_25
.bbl branch_25
    lea %A64_1525 c 16
    ld %S32_1526 %A64_1525 0
    lea.mem %A64_1527 nj 0
    lea %A64_1528 %A64_1527 28
    ld %S32_1529 %A64_1528 0
    blt %S32_1526 %S32_1529 while_4
    bra for_5_next
.bbl while_4
    lea.mem %A64_1530 nj 0
    mov %S32_1531 4
    st %A64_1530 0 %S32_1531
    ret
.bbl while_4_cond
    bne 0:S32 0 while_4
    bra for_5_next
.bbl for_5_next
    add %S32_1532 i 1
    mov i %S32_1532
    lea %A64_1533 c 48
    mov c %A64_1533
.bbl for_5_cond
    conv %U32_1534 i
    lea.mem %A64_1535 nj 0
    lea %A64_1536 %A64_1535 48
    ld %U32_1537 %A64_1536 0
    blt %U32_1534 %U32_1537 for_5
    bra for_5_exit
.bbl for_5_exit
    lea.mem %A64_1538 nj 0
    lea %A64_1539 %A64_1538 48
    ld %U32_1540 %A64_1539 0
    beq %U32_1540 3 if_23_true
    bra if_23_false
.bbl if_23_true
    lea.mem %A64_1541 nj 0
    lea %A64_1542 %A64_1541 525020
    ld %A64_1543 %A64_1542 0
    mov prgb %A64_1543
    lea.mem %A64_1544 nj 0
    lea %A64_1545 %A64_1544 52
    lea %A64_1546 %A64_1545 40
    ld %A64_1547 %A64_1546 0
    mov py %A64_1547
    lea.mem %A64_1548 nj 0
    lea %A64_1549 %A64_1548 52
    lea %A64_1550 %A64_1549 48
    lea %A64_1551 %A64_1550 40
    ld %A64_1552 %A64_1551 0
    mov pcb %A64_1552
    lea.mem %A64_1553 nj 0
    lea %A64_1554 %A64_1553 52
    lea %A64_1555 %A64_1554 96
    lea %A64_1556 %A64_1555 40
    ld %A64_1557 %A64_1556 0
    mov pcr %A64_1557
    lea.mem %A64_1558 nj 0
    lea %A64_1559 %A64_1558 28
    ld %S32_1560 %A64_1559 0
    mov yy %S32_1560
    bra for_7_cond
.bbl for_7
    mov x 0
    bra for_6_cond
.bbl for_6
    lea %A64_1561 py x
    ld %U8_1562 %A64_1561 0
    conv %S32_1563 %U8_1562
    shl %S32_1564 %S32_1563 8
    mov y %S32_1564
    lea %A64_1565 pcb x
    ld %U8_1566 %A64_1565 0
    conv %S32_1567 %U8_1566
    sub %S32_1568 %S32_1567 128
    mov cb %S32_1568
    lea %A64_1569 pcr x
    ld %U8_1570 %A64_1569 0
    conv %S32_1571 %U8_1570
    sub %S32_1572 %S32_1571 128
    mov cr %S32_1572
    mul %S32_1573 359 cr
    add %S32_1574 y %S32_1573
    add %S32_1575 %S32_1574 128
    shr %S32_1576 %S32_1575 8
    pusharg %S32_1576
    bsr njClip
    poparg %U8_1577
    st prgb 0 %U8_1577
    mul %S32_1578 88 cb
    sub %S32_1579 y %S32_1578
    mul %S32_1580 183 cr
    sub %S32_1581 %S32_1579 %S32_1580
    add %S32_1582 %S32_1581 128
    shr %S32_1583 %S32_1582 8
    pusharg %S32_1583
    bsr njClip
    poparg %U8_1584
    lea %A64_1585 prgb 1
    st %A64_1585 0 %U8_1584
    mul %S32_1586 454 cb
    add %S32_1587 y %S32_1586
    add %S32_1588 %S32_1587 128
    shr %S32_1589 %S32_1588 8
    pusharg %S32_1589
    bsr njClip
    poparg %U8_1590
    lea %A64_1591 prgb 2
    st %A64_1591 0 %U8_1590
    lea %A64_1592 prgb 3
    mov prgb %A64_1592
.bbl for_6_next
    add %S32_1593 x 1
    mov x %S32_1593
.bbl for_6_cond
    lea.mem %A64_1594 nj 0
    lea %A64_1595 %A64_1594 24
    ld %S32_1596 %A64_1595 0
    blt x %S32_1596 for_6
    bra for_6_exit
.bbl for_6_exit
    lea.mem %A64_1597 nj 0
    lea %A64_1598 %A64_1597 52
    lea %A64_1599 %A64_1598 20
    ld %S32_1600 %A64_1599 0
    lea %A64_1601 py %S32_1600
    mov py %A64_1601
    lea.mem %A64_1602 nj 0
    lea %A64_1603 %A64_1602 52
    lea %A64_1604 %A64_1603 48
    lea %A64_1605 %A64_1604 20
    ld %S32_1606 %A64_1605 0
    lea %A64_1607 pcb %S32_1606
    mov pcb %A64_1607
    lea.mem %A64_1608 nj 0
    lea %A64_1609 %A64_1608 52
    lea %A64_1610 %A64_1609 96
    lea %A64_1611 %A64_1610 20
    ld %S32_1612 %A64_1611 0
    lea %A64_1613 pcr %S32_1612
    mov pcr %A64_1613
.bbl for_7_next
    sub %S32_1614 yy 1
    mov yy %S32_1614
.bbl for_7_cond
    bne yy 0 for_7
    bra for_7_exit
.bbl for_7_exit
    bra if_23_end
.bbl if_23_false
    lea.mem %A64_1615 nj 0
    lea %A64_1616 %A64_1615 52
    lea %A64_1617 %A64_1616 12
    ld %S32_1618 %A64_1617 0
    lea.mem %A64_1619 nj 0
    lea %A64_1620 %A64_1619 52
    lea %A64_1621 %A64_1620 20
    ld %S32_1622 %A64_1621 0
    bne %S32_1618 %S32_1622 if_22_true
    bra if_23_end
.bbl if_22_true
    lea.mem %A64_1623 nj 0
    lea %A64_1624 %A64_1623 52
    lea %A64_1625 %A64_1624 40
    ld %A64_1626 %A64_1625 0
    lea.mem %A64_1627 nj 0
    lea %A64_1628 %A64_1627 52
    lea %A64_1629 %A64_1628 20
    ld %S32_1630 %A64_1629 0
    lea %A64_1631 %A64_1626 %S32_1630
    mov pin %A64_1631
    lea.mem %A64_1632 nj 0
    lea %A64_1633 %A64_1632 52
    lea %A64_1634 %A64_1633 40
    ld %A64_1635 %A64_1634 0
    lea.mem %A64_1636 nj 0
    lea %A64_1637 %A64_1636 52
    lea %A64_1638 %A64_1637 12
    ld %S32_1639 %A64_1638 0
    lea %A64_1640 %A64_1635 %S32_1639
    mov pout %A64_1640
    lea.mem %A64_1641 nj 0
    lea %A64_1642 %A64_1641 52
    lea %A64_1643 %A64_1642 16
    ld %S32_1644 %A64_1643 0
    sub %S32_1645 %S32_1644 1
    mov __local_26_y %S32_1645
    bra for_8_cond
.bbl for_8
    lea.mem %A64_1646 nj 0
    lea %A64_1647 %A64_1646 52
    lea %A64_1648 %A64_1647 12
    ld %S32_1649 %A64_1648 0
    conv %U64_1650 %S32_1649
    pusharg %U64_1650
    pusharg pin
    pusharg pout
    bsr mymemcpy
    lea.mem %A64_1651 nj 0
    lea %A64_1652 %A64_1651 52
    lea %A64_1653 %A64_1652 20
    ld %S32_1654 %A64_1653 0
    lea %A64_1655 pin %S32_1654
    mov pin %A64_1655
    lea.mem %A64_1656 nj 0
    lea %A64_1657 %A64_1656 52
    lea %A64_1658 %A64_1657 12
    ld %S32_1659 %A64_1658 0
    lea %A64_1660 pout %S32_1659
    mov pout %A64_1660
.bbl for_8_next
    sub %S32_1661 __local_26_y 1
    mov __local_26_y %S32_1661
.bbl for_8_cond
    bne __local_26_y 0 for_8
    bra for_8_exit
.bbl for_8_exit
    lea.mem %A64_1662 nj 0
    lea %A64_1663 %A64_1662 52
    lea %A64_1664 %A64_1663 12
    ld %S32_1665 %A64_1664 0
    lea.mem %A64_1666 nj 0
    lea %A64_1667 %A64_1666 52
    lea %A64_1668 %A64_1667 20
    st %A64_1668 0 %S32_1665
.bbl if_23_end
    ret

.fun njInit NORMAL [] = []
.reg S32 [%S32_1670]
.reg U64 [%U64_1671]
.reg A64 [%A64_1669]
.bbl %start
    lea.mem %A64_1669 nj 0
    mov %S32_1670 0
    mov %U64_1671 525032
    pusharg %U64_1671
    pusharg %S32_1670
    pusharg %A64_1669
    bsr mymemset
    ret

.fun njDone NORMAL [] = []
.reg S32 [%S32_1674 %S32_1680 %S32_1684 i]
.reg A64 [%A64_1672 %A64_1673 %A64_1675 %A64_1676 %A64_1677 %A64_1678 %A64_1679 %A64_1681 %A64_1682 %A64_1683 %A64_1685 %A64_1686 %A64_1687 %A64_1688 %A64_1689 %A64_1690]
.bbl %start
    mov i 0
    bra for_1_cond
.bbl for_1
    lea.mem %A64_1672 nj 0
    lea %A64_1673 %A64_1672 52
    mul %S32_1674 i 48
    lea %A64_1675 %A64_1673 %S32_1674
    lea %A64_1676 %A64_1675 40
    ld %A64_1677 %A64_1676 0
    bne %A64_1677 0 if_2_true
    bra for_1_next
.bbl if_2_true
    lea.mem %A64_1678 nj 0
    lea %A64_1679 %A64_1678 52
    mul %S32_1680 i 48
    lea %A64_1681 %A64_1679 %S32_1680
    lea %A64_1682 %A64_1681 40
    ld %A64_1683 %A64_1682 0
    pusharg %A64_1683
    bsr free
.bbl for_1_next
    add %S32_1684 i 1
    mov i %S32_1684
.bbl for_1_cond
    blt i 3 for_1
    bra for_1_exit
.bbl for_1_exit
    lea.mem %A64_1685 nj 0
    lea %A64_1686 %A64_1685 525020
    ld %A64_1687 %A64_1686 0
    bne %A64_1687 0 if_4_true
    bra if_4_end
.bbl if_4_true
    lea.mem %A64_1688 nj 0
    lea %A64_1689 %A64_1688 525020
    ld %A64_1690 %A64_1689 0
    pusharg %A64_1690
    bsr free
.bbl if_4_end
    bsr njInit
    ret

.fun njDecode NORMAL [S32] = [A64 S32]
.reg S32 [%S32_1693 %S32_1698 %S32_1703 %S32_1704 %S32_1710 %S32_1711 %S32_1712 %S32_1713 %S32_1716 %S32_1721 %S32_1722 %S32_1734 %S32_1735 %S32_1738 %S32_1741 %S32_1744 %S32_1746 %S32_1749 %out size]
.reg U8 [%U8_1702 %U8_1709 %U8_1720 %U8_1727 %U8_1733]
.reg A64 [%A64_1691 %A64_1692 %A64_1694 %A64_1695 %A64_1696 %A64_1697 %A64_1699 %A64_1700 %A64_1701 %A64_1705 %A64_1706 %A64_1707 %A64_1708 %A64_1714 %A64_1715 %A64_1717 %A64_1718 %A64_1719 %A64_1723 %A64_1724 %A64_1725 %A64_1726 %A64_1729 %A64_1730 %A64_1731 %A64_1732 %A64_1736 %A64_1737 %A64_1739 %A64_1740 %A64_1742 %A64_1743 %A64_1745 %A64_1747 %A64_1748 jpeg]
.jtb switch_1728_tab 255 switch_1728_default [192 switch_1728_192 196 switch_1728_196 218 switch_1728_218 219 switch_1728_219 221 switch_1728_221 254 switch_1728_254]
.bbl %start
    poparg jpeg
    poparg size
    bsr njDone
    lea.mem %A64_1691 nj 0
    lea %A64_1692 %A64_1691 4
    st %A64_1692 0 jpeg
    and %S32_1693 size 2147483647
    lea.mem %A64_1694 nj 0
    lea %A64_1695 %A64_1694 16
    st %A64_1695 0 %S32_1693
    lea.mem %A64_1696 nj 0
    lea %A64_1697 %A64_1696 16
    ld %S32_1698 %A64_1697 0
    blt %S32_1698 2 if_2_true
    bra if_2_end
.bbl if_2_true
    mov %out 1
    pusharg %out
    ret
.bbl if_2_end
    lea.mem %A64_1699 nj 0
    lea %A64_1700 %A64_1699 4
    ld %A64_1701 %A64_1700 0
    ld %U8_1702 %A64_1701 0
    conv %S32_1703 %U8_1702
    xor %S32_1704 %S32_1703 255
    lea.mem %A64_1705 nj 0
    lea %A64_1706 %A64_1705 4
    ld %A64_1707 %A64_1706 0
    lea %A64_1708 %A64_1707 1
    ld %U8_1709 %A64_1708 0
    conv %S32_1710 %U8_1709
    xor %S32_1711 %S32_1710 216
    or %S32_1712 %S32_1704 %S32_1711
    bne %S32_1712 0 if_3_true
    bra if_3_end
.bbl if_3_true
    mov %out 1
    pusharg %out
    ret
.bbl if_3_end
    mov %S32_1713 2
    pusharg %S32_1713
    bsr __static_2_njSkip
    bra while_1_cond
.bbl while_1
    lea.mem %A64_1714 nj 0
    lea %A64_1715 %A64_1714 16
    ld %S32_1716 %A64_1715 0
    blt %S32_1716 2 if_4_true
    bra branch_8
.bbl branch_8
    lea.mem %A64_1717 nj 0
    lea %A64_1718 %A64_1717 4
    ld %A64_1719 %A64_1718 0
    ld %U8_1720 %A64_1719 0
    conv %S32_1721 %U8_1720
    bne %S32_1721 255 if_4_true
    bra if_4_end
.bbl if_4_true
    mov %out 5
    pusharg %out
    ret
.bbl if_4_end
    mov %S32_1722 2
    pusharg %S32_1722
    bsr __static_2_njSkip
    lea.mem %A64_1723 nj 0
    lea %A64_1724 %A64_1723 4
    ld %A64_1725 %A64_1724 0
    lea %A64_1726 %A64_1725 -1
    ld %U8_1727 %A64_1726 0
    blt 254:U8 %U8_1727 switch_1728_default
    switch %U8_1727 switch_1728_tab
.bbl switch_1728_192
    bsr njDecodeSOF
    bra switch_1728_end
.bbl switch_1728_196
    bsr njDecodeDHT
    bra switch_1728_end
.bbl switch_1728_219
    bsr njDecodeDQT
    bra switch_1728_end
.bbl switch_1728_221
    bsr njDecodeDRI
    bra switch_1728_end
.bbl switch_1728_218
    bsr njDecodeScan
    bra switch_1728_end
.bbl switch_1728_254
    bsr njSkipMarker
    bra switch_1728_end
.bbl switch_1728_default
    lea.mem %A64_1729 nj 0
    lea %A64_1730 %A64_1729 4
    ld %A64_1731 %A64_1730 0
    lea %A64_1732 %A64_1731 -1
    ld %U8_1733 %A64_1732 0
    conv %S32_1734 %U8_1733
    and %S32_1735 %S32_1734 240
    beq %S32_1735 224 if_5_true
    bra if_5_false
.bbl if_5_true
    bsr njSkipMarker
    bra while_1_cond
.bbl if_5_false
    mov %out 2
    pusharg %out
    ret
.bbl switch_1728_end
.bbl while_1_cond
    lea.mem %A64_1736 nj 0
    lea %A64_1737 %A64_1736 0
    ld %S32_1738 %A64_1737 0
    bne %S32_1738 0 while_1_exit
    bra while_1
.bbl while_1_exit
    lea.mem %A64_1739 nj 0
    lea %A64_1740 %A64_1739 0
    ld %S32_1741 %A64_1740 0
    bne %S32_1741 6 if_7_true
    bra if_7_end
.bbl if_7_true
    lea.mem %A64_1742 nj 0
    lea %A64_1743 %A64_1742 0
    ld %S32_1744 %A64_1743 0
    mov %out %S32_1744
    pusharg %out
    ret
.bbl if_7_end
    lea.mem %A64_1745 nj 0
    mov %S32_1746 0
    st %A64_1745 0 %S32_1746
    bsr njConvert
    lea.mem %A64_1747 nj 0
    lea %A64_1748 %A64_1747 0
    ld %S32_1749 %A64_1748 0
    mov %out %S32_1749
    pusharg %out
    ret

.fun write_str NORMAL [] = [A64 S32]
.reg S8 [%S8_1752]
.reg S32 [%S32_1753 fd]
.reg S64 [%S64_1754]
.reg U64 [%U64_1750 size]
.reg A64 [%A64_1751 s]
.bbl %start
    poparg s
    poparg fd
    mov size 0
    bra for_1_cond
.bbl for_1_next
    add %U64_1750 size 1
    mov size %U64_1750
.bbl for_1_cond
    lea %A64_1751 s size
    ld %S8_1752 %A64_1751 0
    conv %S32_1753 %S8_1752
    bne %S32_1753 0 for_1_next
    bra for_1_exit
.bbl for_1_exit
    pusharg size
    pusharg s
    pusharg fd
    bsr write
    poparg %S64_1754
    ret

.fun write_dec NORMAL [] = [S32 S32]
.reg S8 [%S8_1757 %S8_1761]
.reg S32 [%S32_1758 %S32_1759 %S32_1760 %S32_1764 %S32_1765 %S32_1767 a fd i]
.reg A64 [%A64_1755 %A64_1756 %A64_1762 %A64_1763 %A64_1766 %A64_1768]
.stk buf 1 64
.bbl %start
    poparg fd
    poparg a
    mov i 63
    lea.stk %A64_1755 buf 0
    lea %A64_1756 %A64_1755 i
    mov %S8_1757 0
    st %A64_1756 0 %S8_1757
    sub %S32_1758 i 1
    mov i %S32_1758
.bbl while_1
    rem %S32_1759 a 10
    add %S32_1760 48 %S32_1759
    conv %S8_1761 %S32_1760
    lea.stk %A64_1762 buf 0
    lea %A64_1763 %A64_1762 i
    st %A64_1763 0 %S8_1761
    sub %S32_1764 i 1
    mov i %S32_1764
    div %S32_1765 a 10
    mov a %S32_1765
.bbl while_1_cond
    bne a 0 while_1
    bra while_1_exit
.bbl while_1_exit
    lea.stk %A64_1766 buf 0
    add %S32_1767 i 1
    lea %A64_1768 %A64_1766 %S32_1767
    pusharg fd
    pusharg %A64_1768
    bsr write_str
    ret

.fun main NORMAL [S32] = [S32 A64]
.reg S32 [%S32_1772 %S32_1773 %S32_1774 %S32_1778 %S32_1779 %S32_1784 %S32_1787 %S32_1788 %S32_1789 %S32_1793 %S32_1794 %S32_1795 %S32_1796 %S32_1797 %S32_1799 %S32_1802 %S32_1804 %S32_1808 %S32_1811 %out argc fd size]
.reg S64 [%S64_1776 %S64_1777 %S64_1782 %S64_1783 %S64_1786 %S64_1810]
.reg U64 [%U64_1780 %U64_1785 %U64_1809]
.reg A64 [%A64_1769 %A64_1770 %A64_1771 %A64_1775 %A64_1781 %A64_1790 %A64_1791 %A64_1792 %A64_1798 %A64_1800 %A64_1801 %A64_1803 %A64_1805 %A64_1806 %A64_1807 argv buf]
.bbl %start
    poparg argc
    poparg argv
    blt argc 3 if_1_true
    bra if_1_end
.bbl if_1_true
    lea.mem %A64_1769 string_const_1 0
    pusharg %A64_1769
    bsr print_s_ln
    mov %out 2
    pusharg %out
    ret
.bbl if_1_end
    lea %A64_1770 argv 8
    ld %A64_1771 %A64_1770 0
    mov %S32_1773 0
    mov %S32_1774 0
    pusharg %S32_1774
    pusharg %S32_1773
    pusharg %A64_1771
    bsr open
    poparg %S32_1772
    mov fd %S32_1772
    blt fd 0 if_2_true
    bra if_2_end
.bbl if_2_true
    lea.mem %A64_1775 string_const_2 0
    pusharg %A64_1775
    bsr print_s_ln
    mov %out 1
    pusharg %out
    ret
.bbl if_2_end
    mov %S64_1777 0
    mov %S32_1778 2
    pusharg %S32_1778
    pusharg %S64_1777
    pusharg fd
    bsr lseek
    poparg %S64_1776
    conv %S32_1779 %S64_1776
    mov size %S32_1779
    conv %U64_1780 size
    pusharg %U64_1780
    bsr malloc
    poparg %A64_1781
    mov buf %A64_1781
    mov %S64_1783 0
    mov %S32_1784 0
    pusharg %S32_1784
    pusharg %S64_1783
    pusharg fd
    bsr lseek
    poparg %S64_1782
    conv %U64_1785 size
    pusharg %U64_1785
    pusharg buf
    pusharg fd
    bsr read
    poparg %S64_1786
    conv %S32_1787 %S64_1786
    mov size %S32_1787
    pusharg fd
    bsr close
    poparg %S32_1788
    bsr njInit
    pusharg size
    pusharg buf
    bsr njDecode
    poparg %S32_1789
    bne %S32_1789 0 if_3_true
    bra if_3_end
.bbl if_3_true
    pusharg buf
    bsr free
    lea.mem %A64_1790 string_const_3 0
    pusharg %A64_1790
    bsr print_s_ln
    mov %out 1
    pusharg %out
    ret
.bbl if_3_end
    pusharg buf
    bsr free
    lea %A64_1791 argv 16
    ld %A64_1792 %A64_1791 0
    or %S32_1793 1 64
    or %S32_1794 %S32_1793 512
    add %S32_1795 2 4
    mul %S32_1796 %S32_1795 64
    pusharg %S32_1796
    pusharg %S32_1794
    pusharg %A64_1792
    bsr open
    poparg %S32_1797
    mov fd %S32_1797
    blt fd 0 if_4_true
    bra if_4_end
.bbl if_4_true
    lea.mem %A64_1798 string_const_4 0
    pusharg %A64_1798
    bsr print_s_ln
    mov %out 1
    pusharg %out
    ret
.bbl if_4_end
    bsr njIsColor
    poparg %S32_1799
    bne %S32_1799 0 if_5_true
    bra if_5_false
.bbl if_5_true
    lea.mem %A64_1800 string_const_5 0
    pusharg fd
    pusharg %A64_1800
    bsr write_str
    bra if_5_end
.bbl if_5_false
    lea.mem %A64_1801 string_const_6 0
    pusharg fd
    pusharg %A64_1801
    bsr write_str
.bbl if_5_end
    bsr njGetWidth
    poparg %S32_1802
    pusharg %S32_1802
    pusharg fd
    bsr write_dec
    lea.mem %A64_1803 string_const_7 0
    pusharg fd
    pusharg %A64_1803
    bsr write_str
    bsr njGetHeight
    poparg %S32_1804
    pusharg %S32_1804
    pusharg fd
    bsr write_dec
    lea.mem %A64_1805 string_const_8 0
    pusharg fd
    pusharg %A64_1805
    bsr write_str
    lea.mem %A64_1806 string_const_9 0
    pusharg fd
    pusharg %A64_1806
    bsr write_str
    bsr njGetImage
    poparg %A64_1807
    bsr njGetImageSize
    poparg %S32_1808
    conv %U64_1809 %S32_1808
    pusharg %U64_1809
    pusharg %A64_1807
    pusharg fd
    bsr write
    poparg %S64_1810
    pusharg fd
    bsr close
    poparg %S32_1811
    bsr njDone
    mov %out 0
    pusharg %out
    ret
