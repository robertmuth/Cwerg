# write_s                        RegStats:  0/ 3   0/ 4
# write_x                        RegStats:  0/ 6   0/ 9
# write_u                        RegStats:  0/ 5   0/ 6
# write_d                        RegStats:  0/ 6   0/11
# write_c                        RegStats:  0/ 0   0/ 7
# print_ln                       RegStats:  0/ 0   0/ 4
# print_s_ln                     RegStats:  0/ 0   0/ 3
# print_d_ln                     RegStats:  0/ 0   0/ 3
# print_u_ln                     RegStats:  0/ 0   0/ 3
# print_x_ln                     RegStats:  0/ 0   0/ 3
# print_c_ln                     RegStats:  0/ 0   0/ 3
# memset                         RegStats:  0/ 4   0/ 2
# memcpy                         RegStats:  0/ 4   0/ 2
# abort                          RegStats:  0/ 0   0/ 2
# malloc                         RegStats:  3/ 0   1/18
# free                           RegStats:  0/ 0   0/ 1
# mymemset                       RegStats:  0/ 4   0/ 3
# mymemcpy                       RegStats:  0/ 4   0/ 3
# njGetWidth                     RegStats:  0/ 0   0/ 1
# njGetHeight                    RegStats:  0/ 0   0/ 1
# njIsColor                      RegStats:  0/ 0   0/ 1
# njGetImage                     RegStats:  0/ 0   0/ 3
# njGetImageSize                 RegStats:  0/ 0   0/ 7
# njClip                         RegStats:  0/ 1   0/ 1
# njRowIDCT                      RegStats:  0/ 8   0/70
# njColIDCT                      RegStats:  2/10  14/106
# __static_1_njShowBits          RegStats:  0/ 2   0/41
# njSkipBits                     RegStats:  1/ 0   0/ 4
# njGetBits                      RegStats:  0/ 0   2/ 0
# njByteAlign                    RegStats:  0/ 0   0/ 2
# __static_2_njSkip              RegStats:  0/ 0   0/ 8
# njDecode16                     RegStats:  0/ 0   0/ 8
# __static_3_njDecodeLength      RegStats:  0/ 0   0/ 6
# njSkipMarker                   RegStats:  0/ 0   0/ 1
# njDecodeSOF                    RegStats:  4/ 1   0/117
# njDecodeDHT                    RegStats:  5/ 6   0/31
# njDecodeDQT                    RegStats:  0/ 3   0/15
# njDecodeDRI                    RegStats:  0/ 0   0/ 6
# njGetVLC                       RegStats:  4/ 4   0/11
# njDecodeBlock                  RegStats:  3/ 2   1/53
# njDecodeScan                   RegStats:  8/ 1   0/80
# njUpsampleH                    RegStats:  7/ 0   2/139
# njUpsampleV                    RegStats:  9/ 0   8/136
# njConvert                      RegStats: 11/ 0   3/76
# njInit                         RegStats:  0/ 0   0/ 1
# njDone                         RegStats:  1/ 0   0/11
# njDecode                       RegStats:  0/ 1   2/24
# write_str                      RegStats:  0/ 3   0/ 4
# write_dec                      RegStats:  0/ 5   0/ 6
# main                           RegStats:  4/ 0   3/30
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
.reg S64 [%S64_5]
.reg U64 [%U64_1 len]
.reg A64 [s]
.bbl %start  #  edge_out[while_1_cond]  live_out[fd  len  s]
    poparg fd
    poparg s
    mov len 0
    bra while_1_cond
.bbl while_1  #  edge_out[while_1_cond]  live_out[fd  len  s]
    add %U64_1 len 1
    mov len %U64_1
.bbl while_1_cond  #  edge_out[while_1  while_1_exit]  live_out[fd  len  s]
    ld %S8_3 s len
    conv %S32_4 %S8_3
    bne %S32_4 0 while_1
.bbl while_1_exit
    pusharg len
    pusharg s
    pusharg fd
    bsr write
    poparg %S64_5
    pusharg %S64_5
    ret

.fun write_x NORMAL [S64] = [S32 U32]
.reg S8 [%S8_11 %S8_5]
.reg S32 [%S32_8 fd]
.reg S64 [%S64_19]
.reg U32 [%U32_10 %U32_14 %U32_3 %U32_4 %U32_9 val]
.reg U64 [%U64_18 %U64_2 pos]
.reg A64 [%A64_16]
.stk buffer 1 16
.bbl %start  #  edge_out[while_1]  live_out[fd  pos  val]
    poparg fd
    poparg val
    mov pos 16
.bbl while_1  #  edge_out[if_2_false  if_2_true]  live_out[%U32_3  %U64_2  fd  pos  val]
    sub %U64_2 pos 1
    mov pos %U64_2
    rem %U32_3 val 16
    blt 9:U32 %U32_3 if_2_false
.bbl if_2_true  #  edge_out[if_2_end]  live_out[%U64_2  fd  pos  val]
    add %U32_4 %U32_3 48
    conv %S8_5 %U32_4
    st.stk buffer %U64_2 %S8_5
    bra if_2_end
.bbl if_2_false  #  edge_out[if_2_end]  live_out[%U64_2  fd  pos  val]
    mov %S32_8 87
    conv %U32_9 %S32_8
    add %U32_10 %U32_9 %U32_3
    conv %S8_11 %U32_10
    st.stk buffer %U64_2 %S8_11
.bbl if_2_end  #  edge_out[while_1_cond]  live_out[%U32_14  %U64_2  fd  pos  val]
    div %U32_14 val 16
    mov val %U32_14
.bbl while_1_cond  #  edge_out[while_1  while_1_exit]  live_out[%U64_2  fd  pos  val]
    bne %U32_14 0 while_1
.bbl while_1_exit
    lea.stk %A64_16 buffer %U64_2
    sub %U64_18 16 %U64_2
    pusharg %U64_18
    pusharg %A64_16
    pusharg fd
    bsr write
    poparg %S64_19
    pusharg %S64_19
    ret

.fun write_u NORMAL [S64] = [S32 U32]
.reg S8 [%S8_5]
.reg S32 [fd]
.reg S64 [%S64_13]
.reg U32 [%U32_3 %U32_4 %U32_8 val]
.reg U64 [%U64_12 %U64_2 pos]
.reg A64 [%A64_10]
.stk buffer 1 16
.bbl %start  #  edge_out[while_1]  live_out[fd  pos  val]
    poparg fd
    poparg val
    mov pos 16
.bbl while_1  #  edge_out[while_1_cond]  live_out[%U32_8  %U64_2  fd  pos  val]
    sub %U64_2 pos 1
    mov pos %U64_2
    rem %U32_3 val 10
    add %U32_4 %U32_3 48
    conv %S8_5 %U32_4
    st.stk buffer %U64_2 %S8_5
    div %U32_8 val 10
    mov val %U32_8
.bbl while_1_cond  #  edge_out[while_1  while_1_exit]  live_out[%U64_2  fd  pos  val]
    bne %U32_8 0 while_1
.bbl while_1_exit
    lea.stk %A64_10 buffer %U64_2
    sub %U64_12 16 %U64_2
    pusharg %U64_12
    pusharg %A64_10
    pusharg fd
    bsr write
    poparg %S64_13
    pusharg %S64_13
    ret

.fun write_d NORMAL [S64] = [S32 S32]
.reg S8 [%S8_9]
.reg S32 [%S32_3 fd sval]
.reg S64 [%S64_2 %S64_21]
.reg U32 [%U32_1 %U32_12 %U32_4 %U32_7 %U32_8 val]
.reg U64 [%U64_13 %U64_20 %U64_6 pos]
.reg A64 [%A64_18]
.stk buffer 1 16
.bbl %start  #  edge_out[if_2_end  if_2_true]  live_out[fd  sval]
    poparg fd
    poparg sval
    blt sval 0 if_2_end
.bbl if_2_true
    conv %U32_1 sval
    pusharg %U32_1
    pusharg fd
    bsr write_u
    poparg %S64_2
    pusharg %S64_2
    ret
.bbl if_2_end  #  edge_out[while_1]  live_out[fd  pos  val]
    sub %S32_3 0 sval
    conv %U32_4 %S32_3
    mov val %U32_4
    mov pos 16
.bbl while_1  #  edge_out[while_1_cond]  live_out[%U32_12  %U64_6  fd  pos  val]
    sub %U64_6 pos 1
    mov pos %U64_6
    rem %U32_7 val 10
    add %U32_8 %U32_7 48
    conv %S8_9 %U32_8
    st.stk buffer %U64_6 %S8_9
    div %U32_12 val 10
    mov val %U32_12
.bbl while_1_cond  #  edge_out[while_1  while_1_exit]  live_out[%U64_6  fd  pos  val]
    bne %U32_12 0 while_1
.bbl while_1_exit
    sub %U64_13 %U64_6 1
    st.stk buffer %U64_13 45:S8
    lea.stk %A64_18 buffer %U64_13
    sub %U64_20 16 %U64_13
    pusharg %U64_20
    pusharg %A64_18
    pusharg fd
    bsr write
    poparg %S64_21
    pusharg %S64_21
    ret

.fun write_c NORMAL [S64] = [S32 U8]
.reg S8 [%S8_1]
.reg S32 [%S32_6 fd]
.reg S64 [%S64_4 %S64_7]
.reg U8 [c]
.reg A64 [%A64_3]
.stk buffer 1 16
.bbl %start
    poparg fd
    poparg c
    conv %S8_1 c
    st.stk buffer 0 %S8_1
    lea.stk %A64_3 buffer 0
    pusharg 1:U64
    pusharg %A64_3
    pusharg fd
    bsr write
    poparg %S64_4
    conv %S32_6 %S64_4
    conv %S64_7 %S32_6
    pusharg %S64_7
    ret

.fun print_ln NORMAL [] = [A64 U64]
.reg S64 [%S64_1 %S64_3]
.reg U64 [n]
.reg A64 [s]
.bbl %start
    poparg s
    poparg n
    pusharg n
    pusharg s
    pusharg 1:S32
    bsr write
    poparg %S64_1
    pusharg 10:U8
    pusharg 1:S32
    bsr write_c
    poparg %S64_3
    ret

.fun print_s_ln NORMAL [] = [A64]
.reg S64 [%S64_1 %S64_3]
.reg A64 [s]
.bbl %start
    poparg s
    pusharg s
    pusharg 1:S32
    bsr write_s
    poparg %S64_1
    pusharg 10:U8
    pusharg 1:S32
    bsr write_c
    poparg %S64_3
    ret

.fun print_d_ln NORMAL [] = [S32]
.reg S32 [n]
.reg S64 [%S64_1 %S64_3]
.bbl %start
    poparg n
    pusharg n
    pusharg 1:S32
    bsr write_d
    poparg %S64_1
    pusharg 10:U8
    pusharg 1:S32
    bsr write_c
    poparg %S64_3
    ret

.fun print_u_ln NORMAL [] = [U32]
.reg S64 [%S64_1 %S64_3]
.reg U32 [n]
.bbl %start
    poparg n
    pusharg n
    pusharg 1:S32
    bsr write_u
    poparg %S64_1
    pusharg 10:U8
    pusharg 1:S32
    bsr write_c
    poparg %S64_3
    ret

.fun print_x_ln NORMAL [] = [U32]
.reg S64 [%S64_1 %S64_3]
.reg U32 [n]
.bbl %start
    poparg n
    pusharg n
    pusharg 1:S32
    bsr write_x
    poparg %S64_1
    pusharg 10:U8
    pusharg 1:S32
    bsr write_c
    poparg %S64_3
    ret

.fun print_c_ln NORMAL [] = [U8]
.reg S64 [%S64_1 %S64_3]
.reg U8 [c]
.bbl %start
    poparg c
    pusharg c
    pusharg 1:S32
    bsr write_c
    poparg %S64_1
    pusharg 10:U8
    pusharg 1:S32
    bsr write_c
    poparg %S64_3
    ret

.fun memset NORMAL [A64] = [A64 S32 U64]
.reg S8 [%S8_1]
.reg S32 [value]
.reg U64 [%U64_3 i n]
.reg A64 [ptr]
.bbl %start  #  edge_out[for_1_cond]  live_out[i  n  ptr  value]
    poparg ptr
    poparg value
    poparg n
    mov i 0
    bra for_1_cond
.bbl for_1  #  edge_out[for_1_next]  live_out[i  n  ptr  value]
    conv %S8_1 value
    st ptr i %S8_1
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[i  n  ptr  value]
    add %U64_3 i 1
    mov i %U64_3
.bbl for_1_cond  #  edge_out[for_1  for_1_exit]  live_out[i  n  ptr  value]
    blt i n for_1
.bbl for_1_exit
    pusharg ptr
    ret

.fun memcpy NORMAL [A64] = [A64 A64 U64]
.reg S8 [%S8_2]
.reg U64 [%U64_4 i n]
.reg A64 [dst src]
.bbl %start  #  edge_out[for_1_cond]  live_out[dst  i  n  src]
    poparg dst
    poparg src
    poparg n
    mov i 0
    bra for_1_cond
.bbl for_1  #  edge_out[for_1_next]  live_out[dst  i  n  src]
    ld %S8_2 src i
    st dst i %S8_2
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[dst  i  n  src]
    add %U64_4 i 1
    mov i %U64_4
.bbl for_1_cond  #  edge_out[for_1  for_1_exit]  live_out[dst  i  n  src]
    blt i n for_1
.bbl for_1_exit
    pusharg dst
    ret

.fun abort NORMAL [] = []
.reg S32 [%S32_1 %S32_2]
.bbl %start
    bsr getpid
    poparg %S32_1
    pusharg 3:S32
    pusharg %S32_1
    bsr kill
    poparg %S32_2
    pusharg 1:S32
    bsr exit
    ret

.fun malloc NORMAL [A64] = [U64]
.reg U64 [%U64_1 %U64_10 %U64_11 %U64_12 %U64_18 %U64_19 %U64_20 %U64_21 size]
.reg A64 [%A64_14 %A64_15 %A64_17 %A64_23 %A64_24 %A64_25 %A64_28 %A64_3 %A64_30 %A64_32 %A64_33 %A64_4 %A64_8]
.bbl %start  #  edge_out[if_1_end  if_1_true]  live_out[%U64_1  size]
    poparg size
    mov %U64_1 1048576
    ld.mem %A64_3 __static_1__malloc_start 0
    bne %A64_3 0 if_1_end
.bbl if_1_true  #  edge_out[if_1_end]  live_out[%U64_1  size]
    pusharg 0:A64
    bsr xbrk
    poparg %A64_4
    st.mem __static_1__malloc_start 0 %A64_4
    ld.mem %A64_8 __static_1__malloc_start 0
    st.mem __static_2__malloc_end 0 %A64_8
.bbl if_1_end  #  edge_out[if_3_end  if_3_true]  live_out[%U64_1  %U64_12]
    add %U64_10 size 15
    div %U64_11 %U64_10 16
    shl %U64_12 %U64_11 4
    ld.mem %A64_14 __static_1__malloc_start 0
    lea %A64_15 %A64_14 %U64_12
    ld.mem %A64_17 __static_2__malloc_end 0
    ble %A64_15 %A64_17 if_3_end
.bbl if_3_true  #  edge_out[if_2_true  if_3_end]  live_out[%U64_12]
    add %U64_18 %U64_12 %U64_1
    sub %U64_19 %U64_18 1
    div %U64_20 %U64_19 %U64_1
    mul %U64_21 %U64_20 %U64_1
    ld.mem %A64_23 __static_2__malloc_end 0
    lea %A64_24 %A64_23 %U64_21
    pusharg %A64_24
    bsr xbrk
    poparg %A64_25
    st.mem __static_2__malloc_end 0 %A64_25
    ld.mem %A64_28 __static_2__malloc_end 0
    beq %A64_28 %A64_24 if_3_end
.bbl if_2_true  #  edge_out[if_3_end]  live_out[%U64_12]
    bsr abort
.bbl if_3_end
    ld.mem %A64_30 __static_1__malloc_start 0
    ld.mem %A64_32 __static_1__malloc_start 0
    lea %A64_33 %A64_32 %U64_12
    st.mem __static_1__malloc_start 0 %A64_33
    pusharg %A64_30
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
.reg A64 [ptr]
.bbl %start  #  edge_out[for_1_cond]  live_out[i  num  ptr  value]
    poparg ptr
    poparg value
    poparg num
    mov i 0
    bra for_1_cond
.bbl for_1  #  edge_out[for_1_next]  live_out[i  num  ptr  value]
    conv %S8_1 value
    st ptr i %S8_1
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[i  num  ptr  value]
    add %S32_3 i 1
    mov i %S32_3
.bbl for_1_cond  #  edge_out[for_1  for_1_exit]  live_out[i  num  ptr  value]
    conv %U64_4 i
    blt %U64_4 num for_1
.bbl for_1_exit
    ret

.fun mymemcpy NORMAL [] = [A64 A64 U64]
.reg S8 [%S8_6]
.reg S32 [%S32_8 i]
.reg U64 [%U64_9 num]
.reg A64 [destination source]
.bbl %start  #  edge_out[for_1_cond]  live_out[destination  i  num  source]
    poparg destination
    poparg source
    poparg num
    mov i 0
    bra for_1_cond
.bbl for_1  #  edge_out[for_1_next]  live_out[destination  i  num  source]
    ld %S8_6 source i
    st destination i %S8_6
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[destination  i  num  source]
    add %S32_8 i 1
    mov i %S32_8
.bbl for_1_cond  #  edge_out[for_1  for_1_exit]  live_out[destination  i  num  source]
    conv %U64_9 i
    blt %U64_9 num for_1
.bbl for_1_exit
    ret

.fun njGetWidth NORMAL [S32] = []
.reg S32 [%S32_12]
.bbl %start
    ld.mem %S32_12 nj 24
    pusharg %S32_12
    ret

.fun njGetHeight NORMAL [S32] = []
.reg S32 [%S32_15]
.bbl %start
    ld.mem %S32_15 nj 28
    pusharg %S32_15
    ret

.fun njIsColor NORMAL [S32] = []
.reg U32 [%U32_18]
.bbl %start  #  edge_out[if_1_false  if_1_true]
    ld.mem %U32_18 nj 48
    beq %U32_18 1 if_1_false
.bbl if_1_true
    pusharg 1:S32
    ret
.bbl if_1_false
    pusharg 0:S32
    ret

.fun njGetImage NORMAL [A64] = []
.reg U32 [%U32_21]
.reg A64 [%A64_25 %A64_28]
.bbl %start  #  edge_out[if_1_false  if_1_true]
    ld.mem %U32_21 nj 48
    bne %U32_21 1 if_1_false
.bbl if_1_true
    ld.mem %A64_25 nj 92
    pusharg %A64_25
    ret
.bbl if_1_false
    ld.mem %A64_28 nj 525020
    pusharg %A64_28
    ret

.fun njGetImageSize NORMAL [S32] = []
.reg S32 [%S32_31 %S32_34 %S32_35 %S32_41]
.reg U32 [%U32_36 %U32_39 %U32_40]
.bbl %start
    ld.mem %S32_31 nj 24
    ld.mem %S32_34 nj 28
    mul %S32_35 %S32_31 %S32_34
    conv %U32_36 %S32_35
    ld.mem %U32_39 nj 48
    mul %U32_40 %U32_36 %U32_39
    conv %S32_41 %U32_40
    pusharg %S32_41
    ret

.fun njClip NORMAL [U8] = [S32]
.reg S32 [x]
.reg U8 [%U8_42]
.bbl %start  #  edge_out[if_2_false  if_2_true]  live_out[x]
    poparg x
    ble 0:S32 x if_2_false
.bbl if_2_true
    pusharg 0:U8
    ret
.bbl if_2_false  #  edge_out[if_1_true  if_2_end]  live_out[x]
    ble x 255 if_2_end
.bbl if_1_true
    pusharg 255:U8
    ret
.bbl if_2_end
    conv %U8_42 x
    pusharg %U8_42
    ret

.fun njRowIDCT NORMAL [] = [A64]
.reg S32 [%S32_100 %S32_101 %S32_102 %S32_103 %S32_104 %S32_105 %S32_106 %S32_107 %S32_108 %S32_109 %S32_110 %S32_111 %S32_112 %S32_113 %S32_114 %S32_115 %S32_116 %S32_117 %S32_118 %S32_119 %S32_120 %S32_121 %S32_123 %S32_124 %S32_126 %S32_127 %S32_129 %S32_130 %S32_132 %S32_133 %S32_135 %S32_136 %S32_138 %S32_139 %S32_44 %S32_45 %S32_47 %S32_48 %S32_50 %S32_51 %S32_53 %S32_54 %S32_56 %S32_57 %S32_59 %S32_60 %S32_62 %S32_63 %S32_64 %S32_65 %S32_73 %S32_74 %S32_75 %S32_76 %S32_77 %S32_78 %S32_79 %S32_80 %S32_81 %S32_82 %S32_83 %S32_84 %S32_85 %S32_86 %S32_87 %S32_88 %S32_89 %S32_90 %S32_91 %S32_92 %S32_93 %S32_94 %S32_95 %S32_96 %S32_97 %S32_98 %S32_99]
.reg A64 [blk]
.bbl %start  #  edge_out[if_1_end  if_1_true]  live_out[%S32_45  %S32_47  %S32_50  %S32_53  %S32_56  %S32_59  %S32_62  blk]
    poparg blk
    ld %S32_44 blk 16
    shl %S32_45 %S32_44 11
    ld %S32_47 blk 24
    or %S32_48 %S32_45 %S32_47
    ld %S32_50 blk 8
    or %S32_51 %S32_48 %S32_50
    ld %S32_53 blk 4
    or %S32_54 %S32_51 %S32_53
    ld %S32_56 blk 28
    or %S32_57 %S32_54 %S32_56
    ld %S32_59 blk 20
    or %S32_60 %S32_57 %S32_59
    ld %S32_62 blk 12
    or %S32_63 %S32_60 %S32_62
    bne %S32_63 0 if_1_end
.bbl if_1_true
    ld %S32_64 blk 0
    shl %S32_65 %S32_64 3
    st blk 28 %S32_65
    st blk 24 %S32_65
    st blk 20 %S32_65
    st blk 16 %S32_65
    st blk 12 %S32_65
    st blk 8 %S32_65
    st blk 4 %S32_65
    st blk 0 %S32_65
    ret
.bbl if_1_end
    ld %S32_73 blk 0
    shl %S32_74 %S32_73 11
    add %S32_75 %S32_74 128
    add %S32_76 %S32_53 %S32_56
    mul %S32_77 %S32_76 565
    mov %S32_78 2276
    mul %S32_79 %S32_53 %S32_78
    add %S32_80 %S32_77 %S32_79
    mov %S32_81 3406
    mul %S32_82 %S32_56 %S32_81
    sub %S32_83 %S32_77 %S32_82
    add %S32_84 %S32_59 %S32_62
    mul %S32_85 %S32_84 2408
    mov %S32_86 799
    mul %S32_87 %S32_59 %S32_86
    sub %S32_88 %S32_85 %S32_87
    mov %S32_89 4017
    mul %S32_90 %S32_62 %S32_89
    sub %S32_91 %S32_85 %S32_90
    add %S32_92 %S32_75 %S32_45
    sub %S32_93 %S32_75 %S32_45
    add %S32_94 %S32_50 %S32_47
    mul %S32_95 %S32_94 1108
    mov %S32_96 3784
    mul %S32_97 %S32_47 %S32_96
    sub %S32_98 %S32_95 %S32_97
    mov %S32_99 1568
    mul %S32_100 %S32_50 %S32_99
    add %S32_101 %S32_95 %S32_100
    add %S32_102 %S32_80 %S32_88
    sub %S32_103 %S32_80 %S32_88
    add %S32_104 %S32_83 %S32_91
    sub %S32_105 %S32_83 %S32_91
    add %S32_106 %S32_92 %S32_101
    sub %S32_107 %S32_92 %S32_101
    add %S32_108 %S32_93 %S32_98
    sub %S32_109 %S32_93 %S32_98
    add %S32_110 %S32_103 %S32_105
    mul %S32_111 %S32_110 181
    add %S32_112 %S32_111 128
    shr %S32_113 %S32_112 8
    sub %S32_114 %S32_103 %S32_105
    mul %S32_115 %S32_114 181
    add %S32_116 %S32_115 128
    shr %S32_117 %S32_116 8
    add %S32_118 %S32_106 %S32_102
    shr %S32_119 %S32_118 8
    st blk 0 %S32_119
    add %S32_120 %S32_108 %S32_113
    shr %S32_121 %S32_120 8
    st blk 4 %S32_121
    add %S32_123 %S32_109 %S32_117
    shr %S32_124 %S32_123 8
    st blk 8 %S32_124
    add %S32_126 %S32_107 %S32_104
    shr %S32_127 %S32_126 8
    st blk 12 %S32_127
    sub %S32_129 %S32_107 %S32_104
    shr %S32_130 %S32_129 8
    st blk 16 %S32_130
    sub %S32_132 %S32_109 %S32_117
    shr %S32_133 %S32_132 8
    st blk 20 %S32_133
    sub %S32_135 %S32_108 %S32_113
    shr %S32_136 %S32_135 8
    st blk 24 %S32_136
    sub %S32_138 %S32_106 %S32_102
    shr %S32_139 %S32_138 8
    st blk 28 %S32_139
    ret

.fun njColIDCT NORMAL [] = [A64 A64 S32]
.reg S32 [%S32_141 %S32_142 %S32_144 %S32_145 %S32_146 %S32_147 %S32_149 %S32_150 %S32_151 %S32_152 %S32_154 %S32_155 %S32_157 %S32_159 %S32_160 %S32_161 %S32_162 %S32_164 %S32_165 %S32_166 %S32_167 %S32_169 %S32_170 %S32_171 %S32_172 %S32_174 %S32_175 %S32_176 %S32_177 %S32_178 %S32_179 %S32_181 %S32_184 %S32_185 %S32_186 %S32_187 %S32_188 %S32_189 %S32_190 %S32_191 %S32_192 %S32_193 %S32_194 %S32_195 %S32_196 %S32_197 %S32_198 %S32_199 %S32_200 %S32_201 %S32_202 %S32_203 %S32_204 %S32_205 %S32_206 %S32_207 %S32_208 %S32_209 %S32_210 %S32_211 %S32_212 %S32_213 %S32_214 %S32_215 %S32_216 %S32_217 %S32_218 %S32_219 %S32_220 %S32_221 %S32_222 %S32_223 %S32_224 %S32_225 %S32_226 %S32_227 %S32_228 %S32_229 %S32_230 %S32_231 %S32_232 %S32_233 %S32_234 %S32_235 %S32_236 %S32_237 %S32_238 %S32_239 %S32_240 %S32_241 %S32_244 %S32_245 %S32_246 %S32_249 %S32_250 %S32_251 %S32_254 %S32_255 %S32_256 %S32_259 %S32_260 %S32_261 %S32_264 %S32_265 %S32_266 %S32_269 %S32_270 %S32_271 %S32_274 %S32_275 %S32_276 stride x0]
.reg U8 [%U8_180 %U8_182 %U8_242 %U8_247 %U8_252 %U8_257 %U8_262 %U8_267 %U8_272 %U8_277]
.reg A64 [%A64_183 %A64_243 %A64_248 %A64_253 %A64_258 %A64_263 %A64_268 blk out]
.bbl %start  #  edge_out[if_3_end  if_3_true]  live_out[%S32_145  %S32_149  %S32_154  %S32_159  %S32_164  %S32_169  %S32_174  blk  out  stride]
    poparg blk
    poparg out
    poparg stride
    mov %S32_141 32
    shl %S32_142 %S32_141 2
    ld %S32_144 blk %S32_142
    shl %S32_145 %S32_144 8
    mov %S32_146 48
    shl %S32_147 %S32_146 2
    ld %S32_149 blk %S32_147
    or %S32_150 %S32_145 %S32_149
    mov %S32_151 16
    shl %S32_152 %S32_151 2
    ld %S32_154 blk %S32_152
    or %S32_155 %S32_150 %S32_154
    mov %S32_157 32
    ld %S32_159 blk %S32_157
    or %S32_160 %S32_155 %S32_159
    mov %S32_161 56
    shl %S32_162 %S32_161 2
    ld %S32_164 blk %S32_162
    or %S32_165 %S32_160 %S32_164
    mov %S32_166 40
    shl %S32_167 %S32_166 2
    ld %S32_169 blk %S32_167
    or %S32_170 %S32_165 %S32_169
    mov %S32_171 24
    shl %S32_172 %S32_171 2
    ld %S32_174 blk %S32_172
    or %S32_175 %S32_170 %S32_174
    bne %S32_175 0 if_3_end
.bbl if_3_true  #  edge_out[for_1_cond]  live_out[%S32_181  out  stride  x0]
    ld %S32_176 blk 0
    add %S32_177 %S32_176 32
    shr %S32_178 %S32_177 6
    add %S32_179 %S32_178 128
    pusharg %S32_179
    bsr njClip
    poparg %U8_180
    conv %S32_181 %U8_180
    mov x0 8
    bra for_1_cond
.bbl for_1  #  edge_out[for_1_next]  live_out[%S32_181  out  stride  x0]
    conv %U8_182 %S32_181
    st out 0 %U8_182
    lea %A64_183 out stride
    mov out %A64_183
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[%S32_181  out  stride  x0]
    sub %S32_184 x0 1
    mov x0 %S32_184
.bbl for_1_cond  #  edge_out[for_1  for_1_exit]  live_out[%S32_181  out  stride  x0]
    bne x0 0 for_1
.bbl for_1_exit
    ret
.bbl if_3_end
    ld %S32_185 blk 0
    shl %S32_186 %S32_185 8
    add %S32_187 %S32_186 8192
    add %S32_188 %S32_159 %S32_164
    mul %S32_189 %S32_188 565
    add %S32_190 %S32_189 4
    mov %S32_191 2276
    mul %S32_192 %S32_159 %S32_191
    add %S32_193 %S32_190 %S32_192
    shr %S32_194 %S32_193 3
    mov %S32_195 3406
    mul %S32_196 %S32_164 %S32_195
    sub %S32_197 %S32_190 %S32_196
    shr %S32_198 %S32_197 3
    add %S32_199 %S32_169 %S32_174
    mul %S32_200 %S32_199 2408
    add %S32_201 %S32_200 4
    mov %S32_202 799
    mul %S32_203 %S32_169 %S32_202
    sub %S32_204 %S32_201 %S32_203
    shr %S32_205 %S32_204 3
    mov %S32_206 4017
    mul %S32_207 %S32_174 %S32_206
    sub %S32_208 %S32_201 %S32_207
    shr %S32_209 %S32_208 3
    add %S32_210 %S32_187 %S32_145
    sub %S32_211 %S32_187 %S32_145
    add %S32_212 %S32_154 %S32_149
    mul %S32_213 %S32_212 1108
    add %S32_214 %S32_213 4
    mov %S32_215 3784
    mul %S32_216 %S32_149 %S32_215
    sub %S32_217 %S32_214 %S32_216
    shr %S32_218 %S32_217 3
    mov %S32_219 1568
    mul %S32_220 %S32_154 %S32_219
    add %S32_221 %S32_214 %S32_220
    shr %S32_222 %S32_221 3
    add %S32_223 %S32_194 %S32_205
    sub %S32_224 %S32_194 %S32_205
    add %S32_225 %S32_198 %S32_209
    sub %S32_226 %S32_198 %S32_209
    add %S32_227 %S32_210 %S32_222
    sub %S32_228 %S32_210 %S32_222
    add %S32_229 %S32_211 %S32_218
    sub %S32_230 %S32_211 %S32_218
    add %S32_231 %S32_224 %S32_226
    mul %S32_232 %S32_231 181
    add %S32_233 %S32_232 128
    shr %S32_234 %S32_233 8
    sub %S32_235 %S32_224 %S32_226
    mul %S32_236 %S32_235 181
    add %S32_237 %S32_236 128
    shr %S32_238 %S32_237 8
    add %S32_239 %S32_227 %S32_223
    shr %S32_240 %S32_239 14
    add %S32_241 %S32_240 128
    pusharg %S32_241
    bsr njClip
    poparg %U8_242
    st out 0 %U8_242
    lea %A64_243 out stride
    add %S32_244 %S32_229 %S32_234
    shr %S32_245 %S32_244 14
    add %S32_246 %S32_245 128
    pusharg %S32_246
    bsr njClip
    poparg %U8_247
    st %A64_243 0 %U8_247
    lea %A64_248 %A64_243 stride
    add %S32_249 %S32_230 %S32_238
    shr %S32_250 %S32_249 14
    add %S32_251 %S32_250 128
    pusharg %S32_251
    bsr njClip
    poparg %U8_252
    st %A64_243 stride %U8_252
    lea %A64_253 %A64_248 stride
    add %S32_254 %S32_228 %S32_225
    shr %S32_255 %S32_254 14
    add %S32_256 %S32_255 128
    pusharg %S32_256
    bsr njClip
    poparg %U8_257
    st %A64_248 stride %U8_257
    lea %A64_258 %A64_253 stride
    sub %S32_259 %S32_228 %S32_225
    shr %S32_260 %S32_259 14
    add %S32_261 %S32_260 128
    pusharg %S32_261
    bsr njClip
    poparg %U8_262
    st %A64_253 stride %U8_262
    lea %A64_263 %A64_258 stride
    sub %S32_264 %S32_230 %S32_238
    shr %S32_265 %S32_264 14
    add %S32_266 %S32_265 128
    pusharg %S32_266
    bsr njClip
    poparg %U8_267
    st %A64_258 stride %U8_267
    lea %A64_268 %A64_263 stride
    sub %S32_269 %S32_229 %S32_234
    shr %S32_270 %S32_269 14
    add %S32_271 %S32_270 128
    pusharg %S32_271
    bsr njClip
    poparg %U8_272
    st %A64_263 stride %U8_272
    sub %S32_274 %S32_227 %S32_223
    shr %S32_275 %S32_274 14
    add %S32_276 %S32_275 128
    pusharg %S32_276
    bsr njClip
    poparg %U8_277
    st %A64_268 stride %U8_277
    ret

.fun __static_1_njShowBits NORMAL [S32] = [S32]
.reg S32 [%S32_280 %S32_283 %S32_284 %S32_285 %S32_290 %S32_291 %S32_306 %S32_307 %S32_312 %S32_313 %S32_318 %S32_319 %S32_320 %S32_321 %S32_324 %S32_327 %S32_340 %S32_341 %S32_348 %S32_349 %S32_354 %S32_355 %S32_356 %S32_357 %S32_362 %S32_363 %S32_370 %S32_373 %S32_376 %S32_377 %S32_378 %S32_379 %S32_380 %S32_381 bits]
.reg U8 [%U8_297 %U8_331]
.reg A64 [%A64_296 %A64_300 %A64_301 %A64_330 %A64_334 %A64_335]
.jtb switch_344_tab 256 switch_344_default [0 while_1_cond 217 switch_344_217 255 while_1_cond]
.bbl %start  #  edge_out[if_2_true  while_1_cond]  live_out[bits]
    poparg bits
    bne bits 0 while_1_cond
.bbl if_2_true
    pusharg 0:S32
    ret
.bbl while_1  #  edge_out[if_3_end  if_3_true]  live_out[bits]
    ld.mem %S32_280 nj 16
    blt 0:S32 %S32_280 if_3_end
.bbl if_3_true  #  edge_out[while_1_cond]  live_out[bits]
    ld.mem %S32_283 nj 524752
    shl %S32_284 %S32_283 8
    or %S32_285 %S32_284 255
    st.mem nj 524752 %S32_285
    ld.mem %S32_290 nj 524756
    add %S32_291 %S32_290 8
    st.mem nj 524756 %S32_291
    bra while_1_cond
.bbl if_3_end  #  edge_out[if_6_true  while_1_cond]  live_out[bits]
    ld.mem %A64_296 nj 4
    ld %U8_297 %A64_296 0
    ld.mem %A64_300 nj 4
    lea %A64_301 %A64_300 1
    st.mem nj 4 %A64_301
    ld.mem %S32_306 nj 16
    sub %S32_307 %S32_306 1
    st.mem nj 16 %S32_307
    ld.mem %S32_312 nj 524756
    add %S32_313 %S32_312 8
    st.mem nj 524756 %S32_313
    ld.mem %S32_318 nj 524752
    shl %S32_319 %S32_318 8
    conv %S32_320 %U8_297
    or %S32_321 %S32_319 %S32_320
    st.mem nj 524752 %S32_321
    conv %S32_324 %U8_297
    bne %S32_324 255 while_1_cond
.bbl if_6_true  #  edge_out[if_5_false  if_5_true]  live_out[bits]
    ld.mem %S32_327 nj 16
    beq %S32_327 0 if_5_false
.bbl if_5_true  #  edge_out[if_5_true_1  switch_344_default]  live_out[%U8_331  bits]
    ld.mem %A64_330 nj 4
    ld %U8_331 %A64_330 0
    ld.mem %A64_334 nj 4
    lea %A64_335 %A64_334 1
    st.mem nj 4 %A64_335
    ld.mem %S32_340 nj 16
    sub %S32_341 %S32_340 1
    st.mem nj 16 %S32_341
    blt 255:U8 %U8_331 switch_344_default
.bbl if_5_true_1  #  edge_out[switch_344_217  switch_344_default  while_1_cond  while_1_cond]  live_out[%U8_331  bits]
    switch %U8_331 switch_344_tab
.bbl switch_344_217  #  edge_out[while_1_cond]  live_out[bits]
    st.mem nj 16 0:S32
    bra while_1_cond
.bbl switch_344_default  #  edge_out[if_4_false  if_4_true]  live_out[%U8_331  bits]
    conv %S32_348 %U8_331
    and %S32_349 %S32_348 248
    beq %S32_349 208 if_4_false
.bbl if_4_true  #  edge_out[while_1_cond]  live_out[bits]
    st.mem nj 0 5:S32
    bra while_1_cond
.bbl if_4_false  #  edge_out[while_1_cond]  live_out[bits]
    ld.mem %S32_354 nj 524752
    shl %S32_355 %S32_354 8
    conv %S32_356 %U8_331
    or %S32_357 %S32_355 %S32_356
    st.mem nj 524752 %S32_357
    ld.mem %S32_362 nj 524756
    add %S32_363 %S32_362 8
    st.mem nj 524756 %S32_363
    bra while_1_cond
.bbl if_5_false  #  edge_out[while_1_cond]  live_out[bits]
    st.mem nj 0 5:S32
.bbl while_1_cond  #  edge_out[while_1  while_1_exit]  live_out[bits]
    ld.mem %S32_370 nj 524756
    blt %S32_370 bits while_1
.bbl while_1_exit
    ld.mem %S32_373 nj 524752
    ld.mem %S32_376 nj 524756
    sub %S32_377 %S32_376 bits
    shr %S32_378 %S32_373 %S32_377
    shl %S32_379 1 bits
    sub %S32_380 %S32_379 1
    and %S32_381 %S32_378 %S32_380
    pusharg %S32_381
    ret

.fun njSkipBits NORMAL [] = [S32]
.reg S32 [%S32_384 %S32_385 %S32_388 %S32_389 bits]
.bbl %start  #  edge_out[if_1_end  if_1_true]  live_out[bits]
    poparg bits
    ld.mem %S32_384 nj 524756
    ble bits %S32_384 if_1_end
.bbl if_1_true  #  edge_out[if_1_end]  live_out[bits]
    pusharg bits
    bsr __static_1_njShowBits
    poparg %S32_385
.bbl if_1_end
    ld.mem %S32_388 nj 524756
    sub %S32_389 %S32_388 bits
    st.mem nj 524756 %S32_389
    ret

.fun njGetBits NORMAL [S32] = [S32]
.reg S32 [%S32_392 bits]
.bbl %start
    poparg bits
    pusharg bits
    bsr __static_1_njShowBits
    poparg %S32_392
    pusharg bits
    bsr njSkipBits
    pusharg %S32_392
    ret

.fun njByteAlign NORMAL [] = []
.reg S32 [%S32_395 %S32_396]
.bbl %start
    ld.mem %S32_395 nj 524756
    and %S32_396 %S32_395 248
    st.mem nj 524756 %S32_396
    ret

.fun __static_2_njSkip NORMAL [] = [S32]
.reg S32 [%S32_407 %S32_408 %S32_413 %S32_414 %S32_419 count]
.reg A64 [%A64_401 %A64_402]
.bbl %start  #  edge_out[if_1_end  if_1_true]
    poparg count
    ld.mem %A64_401 nj 4
    lea %A64_402 %A64_401 count
    st.mem nj 4 %A64_402
    ld.mem %S32_407 nj 16
    sub %S32_408 %S32_407 count
    st.mem nj 16 %S32_408
    ld.mem %S32_413 nj 20
    sub %S32_414 %S32_413 count
    st.mem nj 20 %S32_414
    ld.mem %S32_419 nj 16
    ble 0:S32 %S32_419 if_1_end
.bbl if_1_true  #  edge_out[if_1_end]
    st.mem nj 0 5:S32
.bbl if_1_end
    ret

.fun njDecode16 NORMAL [U16] = [A64]
.reg S32 [%S32_423 %S32_424 %S32_427 %S32_428]
.reg U8 [%U8_422 %U8_426]
.reg U16 [%U16_429]
.reg A64 [pos]
.bbl %start
    poparg pos
    ld %U8_422 pos 0
    conv %S32_423 %U8_422
    shl %S32_424 %S32_423 8
    ld %U8_426 pos 1
    conv %S32_427 %U8_426
    or %S32_428 %S32_424 %S32_427
    conv %U16_429 %S32_428
    pusharg %U16_429
    ret

.fun __static_3_njDecodeLength NORMAL [] = []
.reg S32 [%S32_432 %S32_439 %S32_444 %S32_447]
.reg U16 [%U16_438]
.reg A64 [%A64_437]
.bbl %start  #  edge_out[if_4_end  while_1]
    ld.mem %S32_432 nj 16
    ble 2:S32 %S32_432 if_4_end
.bbl while_1
    st.mem nj 0 5:S32
    ret
.bbl if_4_end  #  edge_out[if_6_end  while_2]
    ld.mem %A64_437 nj 4
    pusharg %A64_437
    bsr njDecode16
    poparg %U16_438
    conv %S32_439 %U16_438
    st.mem nj 20 %S32_439
    ld.mem %S32_444 nj 20
    ld.mem %S32_447 nj 16
    ble %S32_444 %S32_447 if_6_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_6_end
    pusharg 2:S32
    bsr __static_2_njSkip
    ret

.fun njSkipMarker NORMAL [] = []
.reg S32 [%S32_453]
.bbl %start
    bsr __static_3_njDecodeLength
    ld.mem %S32_453 nj 20
    pusharg %S32_453
    bsr __static_2_njSkip
    ret

.fun njDecodeSOF NORMAL [] = []
.reg S32 [%S32_456 %S32_459 %S32_466 %S32_474 %S32_482 %S32_487 %S32_490 %S32_510 %S32_524 %S32_530 %S32_531 %S32_536 %S32_538 %S32_539 %S32_540 %S32_548 %S32_549 %S32_554 %S32_556 %S32_557 %S32_558 %S32_566 %S32_568 %S32_574 %S32_576 %S32_577 %S32_578 %S32_582 %S32_584 %S32_586 %S32_588 %S32_589 %S32_603 %S32_606 %S32_611 %S32_614 %S32_615 %S32_616 %S32_619 %S32_620 %S32_625 %S32_628 %S32_629 %S32_630 %S32_633 %S32_634 %S32_641 %S32_643 %S32_644 %S32_645 %S32_646 %S32_647 %S32_651 %S32_653 %S32_654 %S32_655 %S32_656 %S32_657 %S32_661 %S32_663 %S32_664 %S32_665 %S32_668 %S32_670 %S32_672 %S32_674 %S32_678 %S32_681 %S32_682 %S32_684 %S32_685 %S32_686 %S32_692 %S32_703 %S32_706 %S32_707 %S32_724 i ssxmax ssymax]
.reg U8 [%U8_465 %U8_497 %U8_523 %U8_529 %U8_547 %U8_565]
.reg U16 [%U16_473 %U16_481]
.reg U32 [%U32_498 %U32_504 %U32_511 %U32_514 %U32_515 %U32_591 %U32_594 %U32_597 %U32_694 %U32_697 %U32_700 %U32_708 %U32_711 %U32_712]
.reg U64 [%U64_687 %U64_713]
.reg A64 [%A64_464 %A64_471 %A64_472 %A64_479 %A64_480 %A64_495 %A64_519 %A64_522 %A64_527 %A64_545 %A64_563 %A64_590 %A64_638 %A64_688 %A64_693 %A64_714 %A64_719 c]
.jtb switch_505_tab 4 while_5 [1 switch_505_end 3 switch_505_end]
.bbl %start  #  edge_out[while_1]  live_out[ssxmax  ssymax]
    mov ssxmax 0
    mov ssymax 0
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_17_true  while_1_cond]  live_out[ssxmax  ssymax]
    ld.mem %S32_456 nj 0
    beq %S32_456 0 while_1_cond
.bbl if_17_true
    ret
.bbl while_1_cond  #  edge_out[while_1_exit]  live_out[ssxmax  ssymax]
.bbl while_1_exit  #  edge_out[if_20_end  while_2]  live_out[ssxmax  ssymax]
    ld.mem %S32_459 nj 20
    ble 9:S32 %S32_459 if_20_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_20_end  #  edge_out[if_22_end  while_3]  live_out[ssxmax  ssymax]
    ld.mem %A64_464 nj 4
    ld %U8_465 %A64_464 0
    conv %S32_466 %U8_465
    beq %S32_466 8 if_22_end
.bbl while_3
    st.mem nj 0 2:S32
    ret
.bbl if_22_end  #  edge_out[branch_50  while_4]  live_out[ssxmax  ssymax]
    ld.mem %A64_471 nj 4
    lea %A64_472 %A64_471 1
    pusharg %A64_472
    bsr njDecode16
    poparg %U16_473
    conv %S32_474 %U16_473
    st.mem nj 28 %S32_474
    ld.mem %A64_479 nj 4
    lea %A64_480 %A64_479 3
    pusharg %A64_480
    bsr njDecode16
    poparg %U16_481
    conv %S32_482 %U16_481
    st.mem nj 24 %S32_482
    ld.mem %S32_487 nj 24
    beq %S32_487 0 while_4
.bbl branch_50  #  edge_out[if_24_end  while_4]  live_out[ssxmax  ssymax]
    ld.mem %S32_490 nj 28
    bne %S32_490 0 if_24_end
.bbl while_4
    st.mem nj 0 5:S32
    ret
.bbl if_24_end  #  edge_out[if_24_end_1  while_5]  live_out[%U32_504  ssxmax  ssymax]
    ld.mem %A64_495 nj 4
    ld %U8_497 %A64_495 5
    conv %U32_498 %U8_497
    st.mem nj 48 %U32_498
    pusharg 6:S32
    bsr __static_2_njSkip
    ld.mem %U32_504 nj 48
    blt 3:U32 %U32_504 while_5
.bbl if_24_end_1  #  edge_out[switch_505_end  switch_505_end  while_5]  live_out[ssxmax  ssymax]
    switch %U32_504 switch_505_tab
.bbl while_5
    st.mem nj 0 2:S32
    ret
.bbl switch_505_end  #  edge_out[if_27_end  while_6]  live_out[ssxmax  ssymax]
    ld.mem %S32_510 nj 20
    conv %U32_511 %S32_510
    ld.mem %U32_514 nj 48
    mul %U32_515 %U32_514 3
    ble %U32_515 %U32_511 if_27_end
.bbl while_6
    st.mem nj 0 5:S32
    ret
.bbl if_27_end  #  edge_out[for_15_cond]  live_out[c  i  ssxmax  ssymax]
    mov i 0
    lea.mem %A64_519 nj 52
    mov c %A64_519
    bra for_15_cond
.bbl for_15  #  edge_out[if_29_end  while_7]  live_out[c  i  ssxmax  ssymax]
    ld.mem %A64_522 nj 4
    ld %U8_523 %A64_522 0
    conv %S32_524 %U8_523
    st c 0 %S32_524
    ld.mem %A64_527 nj 4
    ld %U8_529 %A64_527 1
    conv %S32_530 %U8_529
    shr %S32_531 %S32_530 4
    st c 4 %S32_531
    bne %S32_531 0 if_29_end
.bbl while_7
    st.mem nj 0 5:S32
    ret
.bbl if_29_end  #  edge_out[if_31_end  while_8]  live_out[c  i  ssxmax  ssymax]
    ld %S32_536 c 4
    ld %S32_538 c 4
    sub %S32_539 %S32_538 1
    and %S32_540 %S32_536 %S32_539
    beq %S32_540 0 if_31_end
.bbl while_8
    st.mem nj 0 2:S32
    ret
.bbl if_31_end  #  edge_out[if_33_end  while_9]  live_out[c  i  ssxmax  ssymax]
    ld.mem %A64_545 nj 4
    ld %U8_547 %A64_545 1
    conv %S32_548 %U8_547
    and %S32_549 %S32_548 15
    st c 8 %S32_549
    bne %S32_549 0 if_33_end
.bbl while_9
    st.mem nj 0 5:S32
    ret
.bbl if_33_end  #  edge_out[if_35_end  while_10]  live_out[c  i  ssxmax  ssymax]
    ld %S32_554 c 8
    ld %S32_556 c 8
    sub %S32_557 %S32_556 1
    and %S32_558 %S32_554 %S32_557
    beq %S32_558 0 if_35_end
.bbl while_10
    st.mem nj 0 2:S32
    ret
.bbl if_35_end  #  edge_out[if_37_end  while_11]  live_out[c  i  ssxmax  ssymax]
    ld.mem %A64_563 nj 4
    ld %U8_565 %A64_563 2
    conv %S32_566 %U8_565
    st c 24 %S32_566
    and %S32_568 %S32_566 252
    beq %S32_568 0 if_37_end
.bbl while_11
    st.mem nj 0 5:S32
    ret
.bbl if_37_end  #  edge_out[if_38_end  if_38_true]  live_out[c  i  ssxmax  ssymax]
    pusharg 3:S32
    bsr __static_2_njSkip
    ld.mem %S32_574 nj 200
    ld %S32_576 c 24
    shl %S32_577 1 %S32_576
    or %S32_578 %S32_574 %S32_577
    st.mem nj 200 %S32_578
    ld %S32_582 c 4
    ble %S32_582 ssxmax if_38_end
.bbl if_38_true  #  edge_out[if_38_end]  live_out[c  i  ssxmax  ssymax]
    ld %S32_584 c 4
    mov ssxmax %S32_584
.bbl if_38_end  #  edge_out[for_15_next  if_39_true]  live_out[c  i  ssxmax  ssymax]
    ld %S32_586 c 8
    ble %S32_586 ssymax for_15_next
.bbl if_39_true  #  edge_out[for_15_next]  live_out[c  i  ssxmax  ssymax]
    ld %S32_588 c 8
    mov ssymax %S32_588
.bbl for_15_next  #  edge_out[for_15_cond]  live_out[c  i  ssxmax  ssymax]
    add %S32_589 i 1
    mov i %S32_589
    lea %A64_590 c 48
    mov c %A64_590
.bbl for_15_cond  #  edge_out[for_15  for_15_exit]  live_out[c  i  ssxmax  ssymax]
    conv %U32_591 i
    ld.mem %U32_594 nj 48
    blt %U32_591 %U32_594 for_15
.bbl for_15_exit  #  edge_out[if_41_end  if_41_true]  live_out[ssxmax  ssymax]
    ld.mem %U32_597 nj 48
    bne %U32_597 1 if_41_end
.bbl if_41_true  #  edge_out[if_41_end]  live_out[ssxmax  ssymax]
    mov ssymax 1
    mov ssxmax 1
    st.mem nj 60 1:S32
    st.mem nj 56 1:S32
.bbl if_41_end  #  edge_out[for_16_cond]  live_out[c  i  ssxmax  ssymax]
    shl %S32_603 ssxmax 3
    st.mem nj 40 %S32_603
    shl %S32_606 ssymax 3
    st.mem nj 44 %S32_606
    ld.mem %S32_611 nj 24
    ld.mem %S32_614 nj 40
    add %S32_615 %S32_611 %S32_614
    sub %S32_616 %S32_615 1
    ld.mem %S32_619 nj 40
    div %S32_620 %S32_616 %S32_619
    st.mem nj 32 %S32_620
    ld.mem %S32_625 nj 28
    ld.mem %S32_628 nj 44
    add %S32_629 %S32_625 %S32_628
    sub %S32_630 %S32_629 1
    ld.mem %S32_633 nj 44
    div %S32_634 %S32_630 %S32_633
    st.mem nj 36 %S32_634
    mov i 0
    lea.mem %A64_638 nj 52
    mov c %A64_638
    bra for_16_cond
.bbl for_16  #  edge_out[branch_51  branch_52]  live_out[c  i  ssxmax  ssymax]
    ld.mem %S32_641 nj 24
    ld %S32_643 c 4
    mul %S32_644 %S32_641 %S32_643
    add %S32_645 %S32_644 ssxmax
    sub %S32_646 %S32_645 1
    div %S32_647 %S32_646 ssxmax
    st c 12 %S32_647
    ld.mem %S32_651 nj 28
    ld %S32_653 c 8
    mul %S32_654 %S32_651 %S32_653
    add %S32_655 %S32_654 ssymax
    sub %S32_656 %S32_655 1
    div %S32_657 %S32_656 ssymax
    st c 16 %S32_657
    ld.mem %S32_661 nj 32
    ld %S32_663 c 4
    mul %S32_664 %S32_661 %S32_663
    shl %S32_665 %S32_664 3
    st c 20 %S32_665
    ld %S32_668 c 12
    ble 3:S32 %S32_668 branch_51
.bbl branch_52  #  edge_out[branch_51  while_12]  live_out[c  i  ssxmax  ssymax]
    ld %S32_670 c 4
    bne %S32_670 ssxmax while_12
.bbl branch_51  #  edge_out[branch_53  if_43_end]  live_out[c  i  ssxmax  ssymax]
    ld %S32_672 c 16
    ble 3:S32 %S32_672 if_43_end
.bbl branch_53  #  edge_out[if_43_end  while_12]  live_out[c  i  ssxmax  ssymax]
    ld %S32_674 c 8
    beq %S32_674 ssymax if_43_end
.bbl while_12
    st.mem nj 0 2:S32
    ret
.bbl if_43_end  #  edge_out[for_16_next  while_13]  live_out[c  i  ssxmax  ssymax]
    ld %S32_678 c 20
    ld.mem %S32_681 nj 36
    mul %S32_682 %S32_678 %S32_681
    ld %S32_684 c 8
    mul %S32_685 %S32_682 %S32_684
    shl %S32_686 %S32_685 3
    conv %U64_687 %S32_686
    pusharg %U64_687
    bsr malloc
    poparg %A64_688
    st c 40 %A64_688
    bne %A64_688 0 for_16_next
.bbl while_13
    st.mem nj 0 3:S32
    ret
.bbl for_16_next  #  edge_out[for_16_cond]  live_out[c  i  ssxmax  ssymax]
    add %S32_692 i 1
    mov i %S32_692
    lea %A64_693 c 48
    mov c %A64_693
.bbl for_16_cond  #  edge_out[for_16  for_16_exit]  live_out[c  i  ssxmax  ssymax]
    conv %U32_694 i
    ld.mem %U32_697 nj 48
    blt %U32_694 %U32_697 for_16
.bbl for_16_exit  #  edge_out[if_49_end  if_49_true]
    ld.mem %U32_700 nj 48
    bne %U32_700 3 if_49_end
.bbl if_49_true  #  edge_out[if_49_end  while_14]
    ld.mem %S32_703 nj 24
    ld.mem %S32_706 nj 28
    mul %S32_707 %S32_703 %S32_706
    conv %U32_708 %S32_707
    ld.mem %U32_711 nj 48
    mul %U32_712 %U32_708 %U32_711
    conv %U64_713 %U32_712
    pusharg %U64_713
    bsr malloc
    poparg %A64_714
    st.mem nj 525020 %A64_714
    ld.mem %A64_719 nj 525020
    bne %A64_719 0 if_49_end
.bbl while_14
    st.mem nj 0 3:S32
    ret
.bbl if_49_end
    ld.mem %S32_724 nj 20
    pusharg %S32_724
    bsr __static_2_njSkip
    ret

.fun njDecodeDHT NORMAL [] = []
.reg S32 [%S32_727 %S32_732 %S32_733 %S32_736 %S32_739 %S32_740 %S32_741 %S32_748 %S32_750 %S32_754 %S32_755 %S32_757 %S32_759 %S32_762 %S32_765 %S32_768 %S32_769 %S32_770 %S32_781 %S32_782 %S32_783 %S32_784 %S32_789 %S32_792 codelen i j remain spread]
.reg U8 [%U8_731 %U8_746 %U8_761 %U8_777 %U8_778]
.reg A64 [%A64_730 %A64_744 %A64_753 %A64_756 %A64_775 %A64_780 %A64_786 vlc]
.bbl %start  #  edge_out[while_1]
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_13_true  while_1_cond]
    ld.mem %S32_727 nj 0
    beq %S32_727 0 while_1_cond
.bbl if_13_true
    ret
.bbl while_1_cond  #  edge_out[while_7_cond]
    bra while_7_cond
.bbl while_7  #  edge_out[if_16_end  while_2]  live_out[%S32_732]
    ld.mem %A64_730 nj 4
    ld %U8_731 %A64_730 0
    conv %S32_732 %U8_731
    and %S32_733 %S32_732 236
    beq %S32_733 0 if_16_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_16_end  #  edge_out[if_18_end  while_3]  live_out[%S32_732]
    and %S32_736 %S32_732 2
    beq %S32_736 0 if_18_end
.bbl while_3
    st.mem nj 0 2:S32
    ret
.bbl if_18_end  #  edge_out[for_9_cond]  live_out[%S32_741  codelen]
    shr %S32_739 %S32_732 3
    or %S32_740 %S32_732 %S32_739
    and %S32_741 %S32_740 3
    mov codelen 1
    bra for_9_cond
.bbl for_9  #  edge_out[for_9_next]  live_out[%S32_741  codelen]
    ld.mem %A64_744 nj 4
    ld %U8_746 %A64_744 codelen
    sub %S32_748 codelen 1
    st.mem __static_4_counts %S32_748 %U8_746
.bbl for_9_next  #  edge_out[for_9_cond]  live_out[%S32_741  codelen]
    add %S32_750 codelen 1
    mov codelen %S32_750
.bbl for_9_cond  #  edge_out[for_9  for_9_exit]  live_out[%S32_741  codelen]
    ble codelen 16 for_9
.bbl for_9_exit  #  edge_out[for_12_cond]  live_out[codelen  remain  spread  vlc]
    pusharg 17:S32
    bsr __static_2_njSkip
    lea.mem %A64_753 nj 464
    shl %S32_754 %S32_741 16
    shl %S32_755 %S32_754 1
    lea %A64_756 %A64_753 %S32_755
    mov vlc %A64_756
    mov spread 65536
    mov remain 65536
    mov codelen 1
    bra for_12_cond
.bbl for_12  #  edge_out[for_12_next  if_20_end]  live_out[%S32_757  %S32_762  codelen  remain  spread  vlc]
    shr %S32_757 spread 1
    mov spread %S32_757
    sub %S32_759 codelen 1
    ld.mem %U8_761 __static_4_counts %S32_759
    conv %S32_762 %U8_761
    beq %S32_762 0 for_12_next
.bbl if_20_end  #  edge_out[if_22_end  while_4]  live_out[%S32_757  %S32_762  codelen  remain  spread  vlc]
    ld.mem %S32_765 nj 20
    ble %S32_762 %S32_765 if_22_end
.bbl while_4
    st.mem nj 0 5:S32
    ret
.bbl if_22_end  #  edge_out[if_24_end  while_5]  live_out[%S32_757  %S32_762  codelen  remain  spread  vlc]
    sub %S32_768 16 codelen
    shl %S32_769 %S32_762 %S32_768
    sub %S32_770 remain %S32_769
    mov remain %S32_770
    ble 0:S32 %S32_770 if_24_end
.bbl while_5
    st.mem nj 0 5:S32
    ret
.bbl if_24_end  #  edge_out[for_11_cond]  live_out[%S32_757  %S32_762  codelen  i  remain  spread  vlc]
    mov i 0
    bra for_11_cond
.bbl for_11  #  edge_out[for_10_cond]  live_out[%S32_757  %S32_762  %U8_777  codelen  i  j  remain  spread  vlc]
    ld.mem %A64_775 nj 4
    ld %U8_777 %A64_775 i
    mov j %S32_757
    bra for_10_cond
.bbl for_10  #  edge_out[for_10_next]  live_out[%S32_757  %S32_762  %U8_777  codelen  i  j  remain  spread  vlc]
    conv %U8_778 codelen
    st vlc 0 %U8_778
    st vlc 1 %U8_777
    lea %A64_780 vlc 2
    mov vlc %A64_780
.bbl for_10_next  #  edge_out[for_10_cond]  live_out[%S32_757  %S32_762  %U8_777  codelen  i  j  remain  spread  vlc]
    sub %S32_781 j 1
    mov j %S32_781
.bbl for_10_cond  #  edge_out[for_10  for_11_next]  live_out[%S32_757  %S32_762  %U8_777  codelen  i  j  remain  spread  vlc]
    bne j 0 for_10
.bbl for_11_next  #  edge_out[for_11_cond]  live_out[%S32_757  %S32_762  codelen  i  remain  spread  vlc]
    add %S32_782 i 1
    mov i %S32_782
.bbl for_11_cond  #  edge_out[for_11  for_11_exit]  live_out[%S32_757  %S32_762  codelen  i  remain  spread  vlc]
    blt i %S32_762 for_11
.bbl for_11_exit  #  edge_out[for_12_next]  live_out[codelen  remain  spread  vlc]
    pusharg %S32_762
    bsr __static_2_njSkip
.bbl for_12_next  #  edge_out[for_12_cond]  live_out[codelen  remain  spread  vlc]
    add %S32_783 codelen 1
    mov codelen %S32_783
.bbl for_12_cond  #  edge_out[for_12  for_12_condbra1]  live_out[codelen  remain  spread  vlc]
    ble codelen 16 for_12
.bbl for_12_condbra1  #  edge_out[while_6_cond]
    bra while_6_cond
.bbl while_6  #  edge_out[while_6_cond]  live_out[remain  vlc]
    sub %S32_784 remain 1
    mov remain %S32_784
    st vlc 0 0:U8
    lea %A64_786 vlc 2
    mov vlc %A64_786
.bbl while_6_cond  #  edge_out[while_6  while_7_cond]  live_out[remain  vlc]
    bne remain 0 while_6
.bbl while_7_cond  #  edge_out[while_7  while_7_exit]
    ld.mem %S32_789 nj 20
    ble 17:S32 %S32_789 while_7
.bbl while_7_exit  #  edge_out[if_31_end  while_8]
    ld.mem %S32_792 nj 20
    beq %S32_792 0 if_31_end
.bbl while_8
    st.mem nj 0 5:S32
    ret
.bbl if_31_end
    ret

.fun njDecodeDQT NORMAL [] = []
.reg S32 [%S32_797 %S32_802 %S32_803 %S32_808 %S32_809 %S32_810 %S32_815 %S32_820 %S32_824 %S32_828 %S32_831 i]
.reg U8 [%U8_801 %U8_822]
.reg A64 [%A64_800 %A64_814 %A64_816 %A64_819]
.bbl %start  #  edge_out[while_1]
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_6_true  while_1_cond]
    ld.mem %S32_797 nj 0
    beq %S32_797 0 while_1_cond
.bbl if_6_true
    ret
.bbl while_1_cond  #  edge_out[while_3_cond]
    bra while_3_cond
.bbl while_3  #  edge_out[if_9_end  while_2]  live_out[%S32_802]
    ld.mem %A64_800 nj 4
    ld %U8_801 %A64_800 0
    conv %S32_802 %U8_801
    and %S32_803 %S32_802 252
    beq %S32_803 0 if_9_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_9_end  #  edge_out[for_5_cond]  live_out[%A64_816  i]
    ld.mem %S32_808 nj 204
    shl %S32_809 1 %S32_802
    or %S32_810 %S32_808 %S32_809
    st.mem nj 204 %S32_810
    lea.mem %A64_814 nj 208
    shl %S32_815 %S32_802 6
    lea %A64_816 %A64_814 %S32_815
    mov i 0
    bra for_5_cond
.bbl for_5  #  edge_out[for_5_next]  live_out[%A64_816  i]
    ld.mem %A64_819 nj 4
    add %S32_820 i 1
    ld %U8_822 %A64_819 %S32_820
    st %A64_816 i %U8_822
.bbl for_5_next  #  edge_out[for_5_cond]  live_out[%A64_816  i]
    add %S32_824 i 1
    mov i %S32_824
.bbl for_5_cond  #  edge_out[for_5  for_5_exit]  live_out[%A64_816  i]
    blt i 64 for_5
.bbl for_5_exit  #  edge_out[while_3_cond]
    pusharg 65:S32
    bsr __static_2_njSkip
.bbl while_3_cond  #  edge_out[while_3  while_3_exit]
    ld.mem %S32_828 nj 20
    ble 65:S32 %S32_828 while_3
.bbl while_3_exit  #  edge_out[if_13_end  while_4]
    ld.mem %S32_831 nj 20
    beq %S32_831 0 if_13_end
.bbl while_4
    st.mem nj 0 5:S32
    ret
.bbl if_13_end
    ret

.fun njDecodeDRI NORMAL [] = []
.reg S32 [%S32_836 %S32_839 %S32_846 %S32_851]
.reg U16 [%U16_845]
.reg A64 [%A64_844]
.bbl %start  #  edge_out[while_1]
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_3_true  while_1_cond]
    ld.mem %S32_836 nj 0
    beq %S32_836 0 while_1_cond
.bbl if_3_true
    ret
.bbl while_1_cond  #  edge_out[while_1_exit]
.bbl while_1_exit  #  edge_out[if_6_end  while_2]
    ld.mem %S32_839 nj 20
    ble 2:S32 %S32_839 if_6_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_6_end
    ld.mem %A64_844 nj 4
    pusharg %A64_844
    bsr njDecode16
    poparg %U16_845
    conv %S32_846 %U16_845
    st.mem nj 525016 %S32_846
    ld.mem %S32_851 nj 20
    pusharg %S32_851
    bsr __static_2_njSkip
    ret

.fun njGetVLC NORMAL [S32] = [A64 A64]
.reg S32 [%S32_852 %S32_854 %S32_858 %S32_861 %S32_865 %S32_867 %S32_868 %S32_869 %S32_870 %S32_871 %S32_872 %S32_873 value]
.reg U8 [%U8_857 %U8_864 %U8_866]
.reg A64 [%A64_862 code vlc]
.bbl %start  #  edge_out[if_1_end  if_1_true]  live_out[%S32_852  %S32_858  code  vlc]
    poparg vlc
    poparg code
    pusharg 16:S32
    bsr __static_1_njShowBits
    poparg %S32_852
    shl %S32_854 %S32_852 1
    ld %U8_857 vlc %S32_854
    conv %S32_858 %U8_857
    bne %S32_858 0 if_1_end
.bbl if_1_true
    st.mem nj 0 5:S32
    pusharg 0:S32
    ret
.bbl if_1_end  #  edge_out[if_2_end  if_2_true]  live_out[%S32_865  code]
    pusharg %S32_858
    bsr njSkipBits
    shl %S32_861 %S32_852 1
    lea %A64_862 vlc %S32_861
    ld %U8_864 %A64_862 1
    conv %S32_865 %U8_864
    beq code 0 if_2_end
.bbl if_2_true  #  edge_out[if_2_end]  live_out[%S32_865]
    conv %U8_866 %S32_865
    st code 0 %U8_866
.bbl if_2_end  #  edge_out[if_3_end  if_3_true]  live_out[%S32_867]
    and %S32_867 %S32_865 15
    bne %S32_867 0 if_3_end
.bbl if_3_true
    pusharg 0:S32
    ret
.bbl if_3_end  #  edge_out[if_4_end  if_4_true]  live_out[%S32_867  %S32_868  value]
    pusharg %S32_867
    bsr njGetBits
    poparg %S32_868
    mov value %S32_868
    sub %S32_869 %S32_867 1
    shl %S32_870 1 %S32_869
    ble %S32_870 %S32_868 if_4_end
.bbl if_4_true  #  edge_out[if_4_end]  live_out[value]
    shl %S32_871 -1 %S32_867
    add %S32_872 %S32_871 1
    add %S32_873 %S32_868 %S32_872
    mov value %S32_873
.bbl if_4_end
    pusharg value
    ret

.fun njDecodeBlock NORMAL [] = [A64 A64]
.reg S8 [%S8_951]
.reg S32 [%S32_883 %S32_887 %S32_888 %S32_889 %S32_891 %S32_893 %S32_896 %S32_900 %S32_901 %S32_904 %S32_905 %S32_911 %S32_912 %S32_913 %S32_916 %S32_919 %S32_922 %S32_923 %S32_926 %S32_931 %S32_932 %S32_933 %S32_934 %S32_940 %S32_941 %S32_942 %S32_945 %S32_946 %S32_952 %S32_953 %S32_957 %S32_959 %S32_962 %S32_966 %S32_967 coef]
.reg U8 [%U8_903 %U8_918 %U8_921 %U8_925 %U8_930 %U8_944]
.reg A64 [%A64_877 %A64_885 %A64_890 %A64_898 %A64_909 %A64_914 %A64_915 %A64_938 %A64_948 %A64_956 %A64_958 %A64_961 %A64_963 %A64_964 c out]
.stk code 1 1
.bbl %start  #  edge_out[while_3]  live_out[c  coef  out]
    poparg c
    poparg out
    st.stk code 0 0:U8
    mov coef 0
    lea.mem %A64_877 nj 524760
    pusharg 256:U64
    pusharg 0:S32
    pusharg %A64_877
    bsr mymemset
    ld %S32_883 c 36
    lea.mem %A64_885 nj 464
    ld %S32_887 c 32
    shl %S32_888 %S32_887 16
    shl %S32_889 %S32_888 1
    lea %A64_890 %A64_885 %S32_889
    pusharg 0:A64
    pusharg %A64_890
    bsr njGetVLC
    poparg %S32_891
    add %S32_893 %S32_883 %S32_891
    st c 36 %S32_893
    ld %S32_896 c 36
    lea.mem %A64_898 nj 208
    ld %S32_900 c 24
    shl %S32_901 %S32_900 6
    ld %U8_903 %A64_898 %S32_901
    conv %S32_904 %U8_903
    mul %S32_905 %S32_896 %S32_904
    st.mem nj 524760 %S32_905
.bbl while_3  #  edge_out[if_6_end  while_3_exit]  live_out[%S32_916  c  coef  out]
    lea.mem %A64_909 nj 464
    ld %S32_911 c 28
    shl %S32_912 %S32_911 16
    shl %S32_913 %S32_912 1
    lea %A64_914 %A64_909 %S32_913
    lea.stk %A64_915 code 0
    pusharg %A64_915
    pusharg %A64_914
    bsr njGetVLC
    poparg %S32_916
    ld.stk %U8_918 code 0
    conv %S32_919 %U8_918
    beq %S32_919 0 while_3_exit
.bbl if_6_end  #  edge_out[branch_14  if_8_end]  live_out[%S32_916  c  coef  out]
    ld.stk %U8_921 code 0
    conv %S32_922 %U8_921
    and %S32_923 %S32_922 15
    bne %S32_923 0 if_8_end
.bbl branch_14  #  edge_out[if_8_end  while_1]  live_out[%S32_916  c  coef  out]
    ld.stk %U8_925 code 0
    conv %S32_926 %U8_925
    beq %S32_926 240 if_8_end
.bbl while_1
    st.mem nj 0 5:S32
    ret
.bbl if_8_end  #  edge_out[if_10_end  while_2]  live_out[%S32_916  %S32_934  c  coef  out]
    ld.stk %U8_930 code 0
    conv %S32_931 %U8_930
    shr %S32_932 %S32_931 4
    add %S32_933 %S32_932 1
    add %S32_934 coef %S32_933
    mov coef %S32_934
    ble %S32_934 63 if_10_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_10_end  #  edge_out[while_3_cond]  live_out[%S32_934  c  coef  out]
    lea.mem %A64_938 nj 208
    ld %S32_940 c 24
    shl %S32_941 %S32_940 6
    add %S32_942 %S32_934 %S32_941
    ld %U8_944 %A64_938 %S32_942
    conv %S32_945 %U8_944
    mul %S32_946 %S32_916 %S32_945
    lea.mem %A64_948 nj 524760
    ld.mem %S8_951 njZZ %S32_934
    conv %S32_952 %S8_951
    shl %S32_953 %S32_952 2
    st %A64_948 %S32_953 %S32_946
.bbl while_3_cond  #  edge_out[while_3  while_3_exit]  live_out[c  coef  out]
    blt %S32_934 63 while_3
.bbl while_3_exit  #  edge_out[for_4_cond]  live_out[c  coef  out]
    mov coef 0
    bra for_4_cond
.bbl for_4  #  edge_out[for_4_next]  live_out[c  coef  out]
    lea.mem %A64_956 nj 524760
    shl %S32_957 coef 2
    lea %A64_958 %A64_956 %S32_957
    pusharg %A64_958
    bsr njRowIDCT
.bbl for_4_next  #  edge_out[for_4_cond]  live_out[c  coef  out]
    add %S32_959 coef 8
    mov coef %S32_959
.bbl for_4_cond  #  edge_out[for_4  for_4_exit]  live_out[c  coef  out]
    blt coef 64 for_4
.bbl for_4_exit  #  edge_out[for_5_cond]  live_out[c  coef  out]
    mov coef 0
    bra for_5_cond
.bbl for_5  #  edge_out[for_5_next]  live_out[c  coef  out]
    lea.mem %A64_961 nj 524760
    shl %S32_962 coef 2
    lea %A64_963 %A64_961 %S32_962
    lea %A64_964 out coef
    ld %S32_966 c 20
    pusharg %S32_966
    pusharg %A64_964
    pusharg %A64_963
    bsr njColIDCT
.bbl for_5_next  #  edge_out[for_5_cond]  live_out[c  coef  out]
    add %S32_967 coef 1
    mov coef %S32_967
.bbl for_5_cond  #  edge_out[for_5  for_5_exit]  live_out[c  coef  out]
    blt coef 8 for_5
.bbl for_5_exit
    ret

.fun njDecodeScan NORMAL [] = []
.reg S32 [%S32_1002 %S32_1004 %S32_1012 %S32_1013 %S32_1021 %S32_1022 %S32_1029 %S32_1030 %S32_1031 %S32_1034 %S32_1044 %S32_1050 %S32_1056 %S32_1061 %S32_1067 %S32_1068 %S32_1069 %S32_1071 %S32_1072 %S32_1074 %S32_1075 %S32_1076 %S32_1077 %S32_1078 %S32_1082 %S32_1083 %S32_1085 %S32_1086 %S32_1088 %S32_1089 %S32_1095 %S32_1098 %S32_1099 %S32_1102 %S32_1105 %S32_1106 %S32_1107 %S32_1109 %S32_1110 %S32_1113 %S32_1114 %S32_1117 %S32_1120 %S32_1124 %S32_970 %S32_973 %S32_976 i mbx mby nextrst rstcount sbx sby]
.reg U8 [%U8_1001 %U8_1011 %U8_1020 %U8_1028 %U8_1043 %U8_1049 %U8_1055 %U8_988]
.reg U32 [%U32_1036 %U32_1039 %U32_1091 %U32_1094 %U32_977 %U32_980 %U32_981 %U32_982 %U32_989 %U32_992]
.reg A64 [%A64_1000 %A64_1009 %A64_1018 %A64_1026 %A64_1035 %A64_1042 %A64_1047 %A64_1053 %A64_1063 %A64_1065 %A64_1079 %A64_1090 %A64_1119 %A64_1121 %A64_987 %A64_997 c]
.bbl %start  #  edge_out[while_1]  live_out[nextrst  rstcount]
    ld.mem %S32_970 nj 525016
    mov rstcount %S32_970
    mov nextrst 0
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_15_true  while_1_cond]  live_out[nextrst  rstcount]
    ld.mem %S32_973 nj 0
    beq %S32_973 0 while_1_cond
.bbl if_15_true
    ret
.bbl while_1_cond  #  edge_out[while_1_exit]  live_out[nextrst  rstcount]
.bbl while_1_exit  #  edge_out[if_18_end  while_2]  live_out[nextrst  rstcount]
    ld.mem %S32_976 nj 20
    conv %U32_977 %S32_976
    ld.mem %U32_980 nj 48
    shl %U32_981 %U32_980 1
    add %U32_982 %U32_981 4
    ble %U32_982 %U32_977 if_18_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_18_end  #  edge_out[if_20_end  while_3]  live_out[nextrst  rstcount]
    ld.mem %A64_987 nj 4
    ld %U8_988 %A64_987 0
    conv %U32_989 %U8_988
    ld.mem %U32_992 nj 48
    beq %U32_989 %U32_992 if_20_end
.bbl while_3
    st.mem nj 0 2:S32
    ret
.bbl if_20_end  #  edge_out[for_9_cond]  live_out[c  i  nextrst  rstcount]
    pusharg 1:S32
    bsr __static_2_njSkip
    mov i 0
    lea.mem %A64_997 nj 52
    mov c %A64_997
    bra for_9_cond
.bbl for_9  #  edge_out[if_22_end  while_4]  live_out[c  i  nextrst  rstcount]
    ld.mem %A64_1000 nj 4
    ld %U8_1001 %A64_1000 0
    conv %S32_1002 %U8_1001
    ld %S32_1004 c 0
    beq %S32_1002 %S32_1004 if_22_end
.bbl while_4
    st.mem nj 0 5:S32
    ret
.bbl if_22_end  #  edge_out[if_24_end  while_5]  live_out[c  i  nextrst  rstcount]
    ld.mem %A64_1009 nj 4
    ld %U8_1011 %A64_1009 1
    conv %S32_1012 %U8_1011
    and %S32_1013 %S32_1012 238
    beq %S32_1013 0 if_24_end
.bbl while_5
    st.mem nj 0 5:S32
    ret
.bbl if_24_end  #  edge_out[for_9_next]  live_out[c  i  nextrst  rstcount]
    ld.mem %A64_1018 nj 4
    ld %U8_1020 %A64_1018 1
    conv %S32_1021 %U8_1020
    shr %S32_1022 %S32_1021 4
    st c 32 %S32_1022
    ld.mem %A64_1026 nj 4
    ld %U8_1028 %A64_1026 1
    conv %S32_1029 %U8_1028
    and %S32_1030 %S32_1029 1
    or %S32_1031 %S32_1030 2
    st c 28 %S32_1031
    pusharg 2:S32
    bsr __static_2_njSkip
.bbl for_9_next  #  edge_out[for_9_cond]  live_out[c  i  nextrst  rstcount]
    add %S32_1034 i 1
    mov i %S32_1034
    lea %A64_1035 c 48
    mov c %A64_1035
.bbl for_9_cond  #  edge_out[for_9  for_9_exit]  live_out[c  i  nextrst  rstcount]
    conv %U32_1036 i
    ld.mem %U32_1039 nj 48
    blt %U32_1036 %U32_1039 for_9
.bbl for_9_exit  #  edge_out[branch_40  while_6]  live_out[nextrst  rstcount]
    ld.mem %A64_1042 nj 4
    ld %U8_1043 %A64_1042 0
    conv %S32_1044 %U8_1043
    bne %S32_1044 0 while_6
.bbl branch_40  #  edge_out[branch_39  while_6]  live_out[nextrst  rstcount]
    ld.mem %A64_1047 nj 4
    ld %U8_1049 %A64_1047 1
    conv %S32_1050 %U8_1049
    bne %S32_1050 63 while_6
.bbl branch_39  #  edge_out[if_27_end  while_6]  live_out[nextrst  rstcount]
    ld.mem %A64_1053 nj 4
    ld %U8_1055 %A64_1053 2
    conv %S32_1056 %U8_1055
    beq %S32_1056 0 if_27_end
.bbl while_6
    st.mem nj 0 2:S32
    ret
.bbl if_27_end  #  edge_out[for_14]  live_out[mbx  mby  nextrst  rstcount]
    ld.mem %S32_1061 nj 20
    pusharg %S32_1061
    bsr __static_2_njSkip
    mov mby 0
    mov mbx 0
.bbl for_14  #  edge_out[for_12_cond]  live_out[c  i  mbx  mby  nextrst  rstcount]
    mov i 0
    lea.mem %A64_1063 nj 52
    mov c %A64_1063
    bra for_12_cond
.bbl for_12  #  edge_out[for_11_cond]  live_out[c  i  mbx  mby  nextrst  rstcount  sby]
    mov sby 0
    bra for_11_cond
.bbl for_11  #  edge_out[for_10_cond]  live_out[c  i  mbx  mby  nextrst  rstcount  sbx  sby]
    mov sbx 0
    bra for_10_cond
.bbl for_10  #  edge_out[while_7]  live_out[c  i  mbx  mby  nextrst  rstcount  sbx  sby]
    ld %A64_1065 c 40
    ld %S32_1067 c 8
    mul %S32_1068 mby %S32_1067
    add %S32_1069 %S32_1068 sby
    ld %S32_1071 c 20
    mul %S32_1072 %S32_1069 %S32_1071
    ld %S32_1074 c 4
    mul %S32_1075 mbx %S32_1074
    add %S32_1076 %S32_1072 %S32_1075
    add %S32_1077 %S32_1076 sbx
    shl %S32_1078 %S32_1077 3
    lea %A64_1079 %A64_1065 %S32_1078
    pusharg %A64_1079
    pusharg c
    bsr njDecodeBlock
.bbl while_7  #  edge_out[if_28_true  while_7_cond]  live_out[c  i  mbx  mby  nextrst  rstcount  sbx  sby]
    ld.mem %S32_1082 nj 0
    beq %S32_1082 0 while_7_cond
.bbl if_28_true
    ret
.bbl while_7_cond  #  edge_out[for_10_next]  live_out[c  i  mbx  mby  nextrst  rstcount  sbx  sby]
.bbl for_10_next  #  edge_out[for_10_cond]  live_out[c  i  mbx  mby  nextrst  rstcount  sbx  sby]
    add %S32_1083 sbx 1
    mov sbx %S32_1083
.bbl for_10_cond  #  edge_out[for_10  for_11_next]  live_out[c  i  mbx  mby  nextrst  rstcount  sbx  sby]
    ld %S32_1085 c 4
    blt sbx %S32_1085 for_10
.bbl for_11_next  #  edge_out[for_11_cond]  live_out[c  i  mbx  mby  nextrst  rstcount  sby]
    add %S32_1086 sby 1
    mov sby %S32_1086
.bbl for_11_cond  #  edge_out[for_11  for_12_next]  live_out[c  i  mbx  mby  nextrst  rstcount  sby]
    ld %S32_1088 c 8
    blt sby %S32_1088 for_11
.bbl for_12_next  #  edge_out[for_12_cond]  live_out[c  i  mbx  mby  nextrst  rstcount]
    add %S32_1089 i 1
    mov i %S32_1089
    lea %A64_1090 c 48
    mov c %A64_1090
.bbl for_12_cond  #  edge_out[for_12  for_12_exit]  live_out[c  i  mbx  mby  nextrst  rstcount]
    conv %U32_1091 i
    ld.mem %U32_1094 nj 48
    blt %U32_1091 %U32_1094 for_12
.bbl for_12_exit  #  edge_out[if_34_end  if_34_true]  live_out[mbx  mby  nextrst  rstcount]
    add %S32_1095 mbx 1
    mov mbx %S32_1095
    ld.mem %S32_1098 nj 32
    blt %S32_1095 %S32_1098 if_34_end
.bbl if_34_true  #  edge_out[for_14_exit  if_34_end]  live_out[mbx  mby  nextrst  rstcount]
    mov mbx 0
    add %S32_1099 mby 1
    mov mby %S32_1099
    ld.mem %S32_1102 nj 36
    ble %S32_1102 %S32_1099 for_14_exit
.bbl if_34_end  #  edge_out[branch_41  for_14]  live_out[mbx  mby  nextrst  rstcount]
    ld.mem %S32_1105 nj 525016
    beq %S32_1105 0 for_14
.bbl branch_41  #  edge_out[for_14  if_38_true]  live_out[mbx  mby  nextrst  rstcount]
    sub %S32_1106 rstcount 1
    mov rstcount %S32_1106
    bne %S32_1106 0 for_14
.bbl if_38_true  #  edge_out[branch_42  while_8]  live_out[%S32_1107  mbx  mby  nextrst]
    bsr njByteAlign
    pusharg 16:S32
    bsr njGetBits
    poparg %S32_1107
    and %S32_1109 %S32_1107 65528
    bne %S32_1109 65488 while_8
.bbl branch_42  #  edge_out[if_36_end  while_8]  live_out[mbx  mby  nextrst]
    and %S32_1110 %S32_1107 7
    beq %S32_1110 nextrst if_36_end
.bbl while_8
    st.mem nj 0 5:S32
    ret
.bbl if_36_end  #  edge_out[for_13_cond]  live_out[i  mbx  mby  nextrst  rstcount]
    add %S32_1113 nextrst 1
    and %S32_1114 %S32_1113 7
    mov nextrst %S32_1114
    ld.mem %S32_1117 nj 525016
    mov rstcount %S32_1117
    mov i 0
    bra for_13_cond
.bbl for_13  #  edge_out[for_13_next]  live_out[i  mbx  mby  nextrst  rstcount]
    lea.mem %A64_1119 nj 52
    mul %S32_1120 i 48
    lea %A64_1121 %A64_1119 %S32_1120
    st %A64_1121 36 0:S32
.bbl for_13_next  #  edge_out[for_13_cond]  live_out[i  mbx  mby  nextrst  rstcount]
    add %S32_1124 i 1
    mov i %S32_1124
.bbl for_13_cond  #  edge_out[for_13  for_13_condbra1]  live_out[i  mbx  mby  nextrst  rstcount]
    blt i 3 for_13
.bbl for_13_condbra1  #  edge_out[for_14]
    bra for_14
.bbl for_14_exit
    st.mem nj 0 6:S32
    ret

.fun njUpsampleH NORMAL [] = [A64]
.reg S32 [%S32_1128 %S32_1129 %S32_1131 %S32_1133 %S32_1134 %S32_1135 %S32_1143 %S32_1145 %S32_1146 %S32_1149 %S32_1150 %S32_1151 %S32_1152 %S32_1153 %S32_1156 %S32_1157 %S32_1160 %S32_1161 %S32_1162 %S32_1165 %S32_1166 %S32_1167 %S32_1168 %S32_1169 %S32_1173 %S32_1174 %S32_1177 %S32_1178 %S32_1179 %S32_1182 %S32_1183 %S32_1184 %S32_1185 %S32_1186 %S32_1191 %S32_1192 %S32_1193 %S32_1196 %S32_1197 %S32_1198 %S32_1199 %S32_1202 %S32_1203 %S32_1204 %S32_1205 %S32_1208 %S32_1209 %S32_1210 %S32_1211 %S32_1212 %S32_1214 %S32_1215 %S32_1219 %S32_1220 %S32_1221 %S32_1224 %S32_1225 %S32_1226 %S32_1227 %S32_1230 %S32_1231 %S32_1232 %S32_1233 %S32_1236 %S32_1237 %S32_1238 %S32_1239 %S32_1240 %S32_1242 %S32_1243 %S32_1245 %S32_1247 %S32_1250 %S32_1251 %S32_1255 %S32_1256 %S32_1259 %S32_1260 %S32_1261 %S32_1264 %S32_1265 %S32_1266 %S32_1267 %S32_1268 %S32_1273 %S32_1274 %S32_1277 %S32_1278 %S32_1279 %S32_1282 %S32_1283 %S32_1284 %S32_1285 %S32_1286 %S32_1291 %S32_1292 %S32_1295 %S32_1296 %S32_1297 %S32_1298 %S32_1299 %S32_1302 %S32_1304 %S32_1305 %S32_1308 x y]
.reg U8 [%U8_1144 %U8_1148 %U8_1154 %U8_1155 %U8_1159 %U8_1164 %U8_1170 %U8_1172 %U8_1176 %U8_1181 %U8_1187 %U8_1190 %U8_1195 %U8_1201 %U8_1207 %U8_1213 %U8_1218 %U8_1223 %U8_1229 %U8_1235 %U8_1241 %U8_1254 %U8_1258 %U8_1263 %U8_1269 %U8_1272 %U8_1276 %U8_1281 %U8_1287 %U8_1290 %U8_1294 %U8_1300]
.reg U64 [%U64_1136]
.reg A64 [%A64_1137 %A64_1141 %A64_1248 %A64_1252 %A64_1311 c lin lout]
.bbl %start  #  edge_out[if_5_end  while_1]  live_out[%A64_1137  %S32_1129  c]
    poparg c
    ld %S32_1128 c 12
    sub %S32_1129 %S32_1128 3
    ld %S32_1131 c 12
    ld %S32_1133 c 16
    mul %S32_1134 %S32_1131 %S32_1133
    shl %S32_1135 %S32_1134 1
    conv %U64_1136 %S32_1135
    pusharg %U64_1136
    bsr malloc
    poparg %A64_1137
    bne %A64_1137 0 if_5_end
.bbl while_1
    st.mem nj 0 3:S32
    ret
.bbl if_5_end  #  edge_out[for_3_cond]  live_out[%A64_1137  %S32_1129  c  lin  lout  y]
    ld %A64_1141 c 40
    mov lin %A64_1141
    mov lout %A64_1137
    ld %S32_1143 c 16
    mov y %S32_1143
    bra for_3_cond
.bbl for_3  #  edge_out[for_2_cond]  live_out[%A64_1137  %S32_1129  c  lin  lout  x  y]
    ld %U8_1144 lin 0
    conv %S32_1145 %U8_1144
    mul %S32_1146 %S32_1145 139
    ld %U8_1148 lin 1
    conv %S32_1149 %U8_1148
    mul %S32_1150 %S32_1149 -11
    add %S32_1151 %S32_1146 %S32_1150
    add %S32_1152 %S32_1151 64
    shr %S32_1153 %S32_1152 7
    pusharg %S32_1153
    bsr njClip
    poparg %U8_1154
    st lout 0 %U8_1154
    ld %U8_1155 lin 0
    conv %S32_1156 %U8_1155
    mul %S32_1157 %S32_1156 104
    ld %U8_1159 lin 1
    conv %S32_1160 %U8_1159
    mul %S32_1161 %S32_1160 27
    add %S32_1162 %S32_1157 %S32_1161
    ld %U8_1164 lin 2
    conv %S32_1165 %U8_1164
    mul %S32_1166 %S32_1165 -3
    add %S32_1167 %S32_1162 %S32_1166
    add %S32_1168 %S32_1167 64
    shr %S32_1169 %S32_1168 7
    pusharg %S32_1169
    bsr njClip
    poparg %U8_1170
    st lout 1 %U8_1170
    ld %U8_1172 lin 0
    conv %S32_1173 %U8_1172
    mul %S32_1174 %S32_1173 28
    ld %U8_1176 lin 1
    conv %S32_1177 %U8_1176
    mul %S32_1178 %S32_1177 109
    add %S32_1179 %S32_1174 %S32_1178
    ld %U8_1181 lin 2
    conv %S32_1182 %U8_1181
    mul %S32_1183 %S32_1182 -9
    add %S32_1184 %S32_1179 %S32_1183
    add %S32_1185 %S32_1184 64
    shr %S32_1186 %S32_1185 7
    pusharg %S32_1186
    bsr njClip
    poparg %U8_1187
    st lout 2 %U8_1187
    mov x 0
    bra for_2_cond
.bbl for_2  #  edge_out[for_2_next]  live_out[%A64_1137  %S32_1129  c  lin  lout  x  y]
    ld %U8_1190 lin x
    conv %S32_1191 %U8_1190
    mul %S32_1192 %S32_1191 -9
    add %S32_1193 x 1
    ld %U8_1195 lin %S32_1193
    conv %S32_1196 %U8_1195
    mul %S32_1197 %S32_1196 111
    add %S32_1198 %S32_1192 %S32_1197
    add %S32_1199 x 2
    ld %U8_1201 lin %S32_1199
    conv %S32_1202 %U8_1201
    mul %S32_1203 %S32_1202 29
    add %S32_1204 %S32_1198 %S32_1203
    add %S32_1205 x 3
    ld %U8_1207 lin %S32_1205
    conv %S32_1208 %U8_1207
    mul %S32_1209 %S32_1208 -3
    add %S32_1210 %S32_1204 %S32_1209
    add %S32_1211 %S32_1210 64
    shr %S32_1212 %S32_1211 7
    pusharg %S32_1212
    bsr njClip
    poparg %U8_1213
    shl %S32_1214 x 1
    add %S32_1215 %S32_1214 3
    st lout %S32_1215 %U8_1213
    ld %U8_1218 lin x
    conv %S32_1219 %U8_1218
    mul %S32_1220 %S32_1219 -3
    add %S32_1221 x 1
    ld %U8_1223 lin %S32_1221
    conv %S32_1224 %U8_1223
    mul %S32_1225 %S32_1224 29
    add %S32_1226 %S32_1220 %S32_1225
    add %S32_1227 x 2
    ld %U8_1229 lin %S32_1227
    conv %S32_1230 %U8_1229
    mul %S32_1231 %S32_1230 111
    add %S32_1232 %S32_1226 %S32_1231
    add %S32_1233 x 3
    ld %U8_1235 lin %S32_1233
    conv %S32_1236 %U8_1235
    mul %S32_1237 %S32_1236 -9
    add %S32_1238 %S32_1232 %S32_1237
    add %S32_1239 %S32_1238 64
    shr %S32_1240 %S32_1239 7
    pusharg %S32_1240
    bsr njClip
    poparg %U8_1241
    shl %S32_1242 x 1
    add %S32_1243 %S32_1242 4
    st lout %S32_1243 %U8_1241
.bbl for_2_next  #  edge_out[for_2_cond]  live_out[%A64_1137  %S32_1129  c  lin  lout  x  y]
    add %S32_1245 x 1
    mov x %S32_1245
.bbl for_2_cond  #  edge_out[for_2  for_2_exit]  live_out[%A64_1137  %S32_1129  c  lin  lout  x  y]
    blt x %S32_1129 for_2
.bbl for_2_exit  #  edge_out[for_3_next]  live_out[%A64_1137  %S32_1129  c  lin  lout  y]
    ld %S32_1247 c 20
    lea %A64_1248 lin %S32_1247
    mov lin %A64_1248
    ld %S32_1250 c 12
    shl %S32_1251 %S32_1250 1
    lea %A64_1252 lout %S32_1251
    mov lout %A64_1252
    ld %U8_1254 %A64_1248 -1
    conv %S32_1255 %U8_1254
    mul %S32_1256 %S32_1255 28
    ld %U8_1258 %A64_1248 -2
    conv %S32_1259 %U8_1258
    mul %S32_1260 %S32_1259 109
    add %S32_1261 %S32_1256 %S32_1260
    ld %U8_1263 %A64_1248 -3
    conv %S32_1264 %U8_1263
    mul %S32_1265 %S32_1264 -9
    add %S32_1266 %S32_1261 %S32_1265
    add %S32_1267 %S32_1266 64
    shr %S32_1268 %S32_1267 7
    pusharg %S32_1268
    bsr njClip
    poparg %U8_1269
    st %A64_1252 -3 %U8_1269
    ld %U8_1272 %A64_1248 -1
    conv %S32_1273 %U8_1272
    mul %S32_1274 %S32_1273 104
    ld %U8_1276 %A64_1248 -2
    conv %S32_1277 %U8_1276
    mul %S32_1278 %S32_1277 27
    add %S32_1279 %S32_1274 %S32_1278
    ld %U8_1281 %A64_1248 -3
    conv %S32_1282 %U8_1281
    mul %S32_1283 %S32_1282 -3
    add %S32_1284 %S32_1279 %S32_1283
    add %S32_1285 %S32_1284 64
    shr %S32_1286 %S32_1285 7
    pusharg %S32_1286
    bsr njClip
    poparg %U8_1287
    st %A64_1252 -2 %U8_1287
    ld %U8_1290 %A64_1248 -1
    conv %S32_1291 %U8_1290
    mul %S32_1292 %S32_1291 139
    ld %U8_1294 %A64_1248 -2
    conv %S32_1295 %U8_1294
    mul %S32_1296 %S32_1295 -11
    add %S32_1297 %S32_1292 %S32_1296
    add %S32_1298 %S32_1297 64
    shr %S32_1299 %S32_1298 7
    pusharg %S32_1299
    bsr njClip
    poparg %U8_1300
    st %A64_1252 -1 %U8_1300
.bbl for_3_next  #  edge_out[for_3_cond]  live_out[%A64_1137  %S32_1129  c  lin  lout  y]
    sub %S32_1302 y 1
    mov y %S32_1302
.bbl for_3_cond  #  edge_out[for_3  for_3_exit]  live_out[%A64_1137  %S32_1129  c  lin  lout  y]
    bne y 0 for_3
.bbl for_3_exit
    ld %S32_1304 c 12
    shl %S32_1305 %S32_1304 1
    st c 12 %S32_1305
    ld %S32_1308 c 12
    st c 20 %S32_1308
    ld %A64_1311 c 40
    pusharg %A64_1311
    bsr free
    st c 40 %A64_1137
    ret

.fun njUpsampleV NORMAL [] = [A64]
.reg S32 [%S32_1314 %S32_1316 %S32_1317 %S32_1319 %S32_1321 %S32_1322 %S32_1323 %S32_1333 %S32_1334 %S32_1337 %S32_1338 %S32_1339 %S32_1340 %S32_1341 %S32_1345 %S32_1346 %S32_1349 %S32_1350 %S32_1351 %S32_1354 %S32_1355 %S32_1356 %S32_1357 %S32_1358 %S32_1362 %S32_1363 %S32_1366 %S32_1367 %S32_1368 %S32_1371 %S32_1372 %S32_1373 %S32_1374 %S32_1375 %S32_1380 %S32_1381 %S32_1382 %S32_1385 %S32_1386 %S32_1388 %S32_1389 %S32_1390 %S32_1393 %S32_1394 %S32_1395 %S32_1398 %S32_1399 %S32_1400 %S32_1401 %S32_1402 %S32_1405 %S32_1408 %S32_1409 %S32_1411 %S32_1412 %S32_1413 %S32_1416 %S32_1417 %S32_1418 %S32_1421 %S32_1422 %S32_1423 %S32_1424 %S32_1425 %S32_1429 %S32_1432 %S32_1433 %S32_1434 %S32_1437 %S32_1438 %S32_1439 %S32_1440 %S32_1443 %S32_1444 %S32_1445 %S32_1446 %S32_1447 %S32_1451 %S32_1452 %S32_1453 %S32_1456 %S32_1457 %S32_1458 %S32_1459 %S32_1462 %S32_1463 %S32_1464 %S32_1465 %S32_1466 %S32_1470 %S32_1471 %S32_1472 %S32_1475 %S32_1476 %S32_1477 %S32_1478 %S32_1479 %S32_1481 %S32_1483 %S32_1484 %S32_1487 x y]
.reg U8 [%U8_1332 %U8_1336 %U8_1342 %U8_1344 %U8_1348 %U8_1353 %U8_1359 %U8_1361 %U8_1365 %U8_1370 %U8_1376 %U8_1384 %U8_1387 %U8_1392 %U8_1397 %U8_1403 %U8_1407 %U8_1410 %U8_1415 %U8_1420 %U8_1426 %U8_1431 %U8_1436 %U8_1442 %U8_1448 %U8_1450 %U8_1455 %U8_1461 %U8_1467 %U8_1469 %U8_1474 %U8_1480]
.reg U64 [%U64_1324]
.reg A64 [%A64_1325 %A64_1329 %A64_1330 %A64_1331 %A64_1343 %A64_1360 %A64_1377 %A64_1378 %A64_1404 %A64_1427 %A64_1428 %A64_1430 %A64_1449 %A64_1490 c cin cout]
.bbl %start  #  edge_out[if_5_end  while_1]  live_out[%A64_1325  %S32_1314  %S32_1316  %S32_1317  c]
    poparg c
    ld %S32_1314 c 12
    ld %S32_1316 c 20
    add %S32_1317 %S32_1316 %S32_1316
    ld %S32_1319 c 12
    ld %S32_1321 c 16
    mul %S32_1322 %S32_1319 %S32_1321
    shl %S32_1323 %S32_1322 1
    conv %U64_1324 %S32_1323
    pusharg %U64_1324
    bsr malloc
    poparg %A64_1325
    bne %A64_1325 0 if_5_end
.bbl while_1
    st.mem nj 0 3:S32
    ret
.bbl if_5_end  #  edge_out[for_3_cond]  live_out[%A64_1325  %S32_1314  %S32_1316  %S32_1317  c  x]
    mov x 0
    bra for_3_cond
.bbl for_3  #  edge_out[for_2_cond]  live_out[%A64_1325  %S32_1314  %S32_1316  %S32_1317  c  cin  cout  x  y]
    ld %A64_1329 c 40
    lea %A64_1330 %A64_1329 x
    lea %A64_1331 %A64_1325 x
    ld %U8_1332 %A64_1329 x
    conv %S32_1333 %U8_1332
    mul %S32_1334 %S32_1333 139
    ld %U8_1336 %A64_1330 %S32_1316
    conv %S32_1337 %U8_1336
    mul %S32_1338 %S32_1337 -11
    add %S32_1339 %S32_1334 %S32_1338
    add %S32_1340 %S32_1339 64
    shr %S32_1341 %S32_1340 7
    pusharg %S32_1341
    bsr njClip
    poparg %U8_1342
    st %A64_1325 x %U8_1342
    lea %A64_1343 %A64_1331 %S32_1314
    ld %U8_1344 %A64_1329 x
    conv %S32_1345 %U8_1344
    mul %S32_1346 %S32_1345 104
    ld %U8_1348 %A64_1330 %S32_1316
    conv %S32_1349 %U8_1348
    mul %S32_1350 %S32_1349 27
    add %S32_1351 %S32_1346 %S32_1350
    ld %U8_1353 %A64_1330 %S32_1317
    conv %S32_1354 %U8_1353
    mul %S32_1355 %S32_1354 -3
    add %S32_1356 %S32_1351 %S32_1355
    add %S32_1357 %S32_1356 64
    shr %S32_1358 %S32_1357 7
    pusharg %S32_1358
    bsr njClip
    poparg %U8_1359
    st %A64_1331 %S32_1314 %U8_1359
    lea %A64_1360 %A64_1343 %S32_1314
    ld %U8_1361 %A64_1329 x
    conv %S32_1362 %U8_1361
    mul %S32_1363 %S32_1362 28
    ld %U8_1365 %A64_1330 %S32_1316
    conv %S32_1366 %U8_1365
    mul %S32_1367 %S32_1366 109
    add %S32_1368 %S32_1363 %S32_1367
    ld %U8_1370 %A64_1330 %S32_1317
    conv %S32_1371 %U8_1370
    mul %S32_1372 %S32_1371 -9
    add %S32_1373 %S32_1368 %S32_1372
    add %S32_1374 %S32_1373 64
    shr %S32_1375 %S32_1374 7
    pusharg %S32_1375
    bsr njClip
    poparg %U8_1376
    st %A64_1343 %S32_1314 %U8_1376
    lea %A64_1377 %A64_1360 %S32_1314
    mov cout %A64_1377
    lea %A64_1378 %A64_1330 %S32_1316
    mov cin %A64_1378
    ld %S32_1380 c 16
    sub %S32_1381 %S32_1380 3
    mov y %S32_1381
    bra for_2_cond
.bbl for_2  #  edge_out[for_2_next]  live_out[%A64_1325  %S32_1314  %S32_1316  %S32_1317  c  cin  cout  x  y]
    sub %S32_1382 0 %S32_1316
    ld %U8_1384 cin %S32_1382
    conv %S32_1385 %U8_1384
    mul %S32_1386 %S32_1385 -9
    ld %U8_1387 cin 0
    conv %S32_1388 %U8_1387
    mul %S32_1389 %S32_1388 111
    add %S32_1390 %S32_1386 %S32_1389
    ld %U8_1392 cin %S32_1316
    conv %S32_1393 %U8_1392
    mul %S32_1394 %S32_1393 29
    add %S32_1395 %S32_1390 %S32_1394
    ld %U8_1397 cin %S32_1317
    conv %S32_1398 %U8_1397
    mul %S32_1399 %S32_1398 -3
    add %S32_1400 %S32_1395 %S32_1399
    add %S32_1401 %S32_1400 64
    shr %S32_1402 %S32_1401 7
    pusharg %S32_1402
    bsr njClip
    poparg %U8_1403
    st cout 0 %U8_1403
    lea %A64_1404 cout %S32_1314
    sub %S32_1405 0 %S32_1316
    ld %U8_1407 cin %S32_1405
    conv %S32_1408 %U8_1407
    mul %S32_1409 %S32_1408 -3
    ld %U8_1410 cin 0
    conv %S32_1411 %U8_1410
    mul %S32_1412 %S32_1411 29
    add %S32_1413 %S32_1409 %S32_1412
    ld %U8_1415 cin %S32_1316
    conv %S32_1416 %U8_1415
    mul %S32_1417 %S32_1416 111
    add %S32_1418 %S32_1413 %S32_1417
    ld %U8_1420 cin %S32_1317
    conv %S32_1421 %U8_1420
    mul %S32_1422 %S32_1421 -9
    add %S32_1423 %S32_1418 %S32_1422
    add %S32_1424 %S32_1423 64
    shr %S32_1425 %S32_1424 7
    pusharg %S32_1425
    bsr njClip
    poparg %U8_1426
    st %A64_1404 0 %U8_1426
    lea %A64_1427 %A64_1404 %S32_1314
    mov cout %A64_1427
    lea %A64_1428 cin %S32_1316
    mov cin %A64_1428
.bbl for_2_next  #  edge_out[for_2_cond]  live_out[%A64_1325  %S32_1314  %S32_1316  %S32_1317  c  cin  cout  x  y]
    sub %S32_1429 y 1
    mov y %S32_1429
.bbl for_2_cond  #  edge_out[for_2  for_2_exit]  live_out[%A64_1325  %S32_1314  %S32_1316  %S32_1317  c  cin  cout  x  y]
    bne y 0 for_2
.bbl for_2_exit  #  edge_out[for_3_next]  live_out[%A64_1325  %S32_1314  %S32_1316  %S32_1317  c  x]
    lea %A64_1430 cin %S32_1316
    ld %U8_1431 %A64_1430 0
    conv %S32_1432 %U8_1431
    mul %S32_1433 %S32_1432 28
    sub %S32_1434 0 %S32_1316
    ld %U8_1436 %A64_1430 %S32_1434
    conv %S32_1437 %U8_1436
    mul %S32_1438 %S32_1437 109
    add %S32_1439 %S32_1433 %S32_1438
    sub %S32_1440 0 %S32_1317
    ld %U8_1442 %A64_1430 %S32_1440
    conv %S32_1443 %U8_1442
    mul %S32_1444 %S32_1443 -9
    add %S32_1445 %S32_1439 %S32_1444
    add %S32_1446 %S32_1445 64
    shr %S32_1447 %S32_1446 7
    pusharg %S32_1447
    bsr njClip
    poparg %U8_1448
    st cout 0 %U8_1448
    lea %A64_1449 cout %S32_1314
    ld %U8_1450 %A64_1430 0
    conv %S32_1451 %U8_1450
    mul %S32_1452 %S32_1451 104
    sub %S32_1453 0 %S32_1316
    ld %U8_1455 %A64_1430 %S32_1453
    conv %S32_1456 %U8_1455
    mul %S32_1457 %S32_1456 27
    add %S32_1458 %S32_1452 %S32_1457
    sub %S32_1459 0 %S32_1317
    ld %U8_1461 %A64_1430 %S32_1459
    conv %S32_1462 %U8_1461
    mul %S32_1463 %S32_1462 -3
    add %S32_1464 %S32_1458 %S32_1463
    add %S32_1465 %S32_1464 64
    shr %S32_1466 %S32_1465 7
    pusharg %S32_1466
    bsr njClip
    poparg %U8_1467
    st %A64_1449 0 %U8_1467
    ld %U8_1469 %A64_1430 0
    conv %S32_1470 %U8_1469
    mul %S32_1471 %S32_1470 139
    sub %S32_1472 0 %S32_1316
    ld %U8_1474 %A64_1430 %S32_1472
    conv %S32_1475 %U8_1474
    mul %S32_1476 %S32_1475 -11
    add %S32_1477 %S32_1471 %S32_1476
    add %S32_1478 %S32_1477 64
    shr %S32_1479 %S32_1478 7
    pusharg %S32_1479
    bsr njClip
    poparg %U8_1480
    st %A64_1449 %S32_1314 %U8_1480
.bbl for_3_next  #  edge_out[for_3_cond]  live_out[%A64_1325  %S32_1314  %S32_1316  %S32_1317  c  x]
    add %S32_1481 x 1
    mov x %S32_1481
.bbl for_3_cond  #  edge_out[for_3  for_3_exit]  live_out[%A64_1325  %S32_1314  %S32_1316  %S32_1317  c  x]
    blt x %S32_1314 for_3
.bbl for_3_exit
    ld %S32_1483 c 16
    shl %S32_1484 %S32_1483 1
    st c 16 %S32_1484
    ld %S32_1487 c 12
    st c 20 %S32_1487
    ld %A64_1490 c 40
    pusharg %A64_1490
    bsr free
    st c 40 %A64_1325
    ret

.fun njConvert NORMAL [] = []
.reg S32 [%S32_1495 %S32_1498 %S32_1501 %S32_1503 %S32_1506 %S32_1509 %S32_1511 %S32_1514 %S32_1516 %S32_1519 %S32_1521 %S32_1524 %S32_1526 %S32_1529 %S32_1532 %S32_1560 %S32_1563 %S32_1564 %S32_1567 %S32_1568 %S32_1571 %S32_1572 %S32_1573 %S32_1574 %S32_1575 %S32_1576 %S32_1578 %S32_1579 %S32_1580 %S32_1581 %S32_1582 %S32_1583 %S32_1586 %S32_1587 %S32_1588 %S32_1589 %S32_1593 %S32_1596 %S32_1600 %S32_1606 %S32_1612 %S32_1614 %S32_1618 %S32_1622 %S32_1630 %S32_1639 %S32_1644 %S32_1645 %S32_1649 %S32_1654 %S32_1659 %S32_1661 %S32_1665 __local_26_y i x yy]
.reg U8 [%U8_1562 %U8_1566 %U8_1570 %U8_1577 %U8_1584 %U8_1590]
.reg U32 [%U32_1534 %U32_1537 %U32_1540]
.reg U64 [%U64_1650]
.reg A64 [%A64_1493 %A64_1533 %A64_1543 %A64_1547 %A64_1552 %A64_1557 %A64_1592 %A64_1601 %A64_1607 %A64_1613 %A64_1626 %A64_1631 %A64_1635 %A64_1640 %A64_1655 %A64_1660 c pcb pcr pin pout prgb py]
.bbl %start  #  edge_out[for_5_cond]  live_out[c  i]
    mov i 0
    lea.mem %A64_1493 nj 52
    mov c %A64_1493
    bra for_5_cond
.bbl while_3  #  edge_out[if_9_true  while_1]  live_out[c  i]
    ld %S32_1495 c 12
    ld.mem %S32_1498 nj 24
    ble %S32_1498 %S32_1495 while_1
.bbl if_9_true  #  edge_out[while_1]  live_out[c  i]
    pusharg c
    bsr njUpsampleH
.bbl while_1  #  edge_out[if_10_true  while_1_cond]  live_out[c  i]
    ld.mem %S32_1501 nj 0
    beq %S32_1501 0 while_1_cond
.bbl if_10_true
    ret
.bbl while_1_cond  #  edge_out[while_1_exit]  live_out[c  i]
.bbl while_1_exit  #  edge_out[if_12_true  while_2]  live_out[c  i]
    ld %S32_1503 c 16
    ld.mem %S32_1506 nj 28
    ble %S32_1506 %S32_1503 while_2
.bbl if_12_true  #  edge_out[while_2]  live_out[c  i]
    pusharg c
    bsr njUpsampleV
.bbl while_2  #  edge_out[if_13_true  while_2_cond]  live_out[c  i]
    ld.mem %S32_1509 nj 0
    beq %S32_1509 0 while_2_cond
.bbl if_13_true
    ret
.bbl while_2_cond  #  edge_out[while_3_cond]  live_out[c  i]
.bbl while_3_cond  #  edge_out[branch_24  while_3]  live_out[c  i]
    ld %S32_1511 c 12
    ld.mem %S32_1514 nj 24
    blt %S32_1511 %S32_1514 while_3
.bbl branch_24  #  edge_out[while_3  while_3_exit]  live_out[c  i]
    ld %S32_1516 c 16
    ld.mem %S32_1519 nj 28
    blt %S32_1516 %S32_1519 while_3
.bbl while_3_exit  #  edge_out[branch_25  while_4]  live_out[c  i]
    ld %S32_1521 c 12
    ld.mem %S32_1524 nj 24
    blt %S32_1521 %S32_1524 while_4
.bbl branch_25  #  edge_out[for_5_next  while_4]  live_out[c  i]
    ld %S32_1526 c 16
    ld.mem %S32_1529 nj 28
    ble %S32_1529 %S32_1526 for_5_next
.bbl while_4
    st.mem nj 0 4:S32
    ret
.bbl for_5_next  #  edge_out[for_5_cond]  live_out[c  i]
    add %S32_1532 i 1
    mov i %S32_1532
    lea %A64_1533 c 48
    mov c %A64_1533
.bbl for_5_cond  #  edge_out[for_5_exit  while_3_cond]  live_out[c  i]
    conv %U32_1534 i
    ld.mem %U32_1537 nj 48
    blt %U32_1534 %U32_1537 while_3_cond
.bbl for_5_exit  #  edge_out[if_23_false  if_23_true]
    ld.mem %U32_1540 nj 48
    bne %U32_1540 3 if_23_false
.bbl if_23_true  #  edge_out[for_7_cond]  live_out[pcb  pcr  prgb  py  yy]
    ld.mem %A64_1543 nj 525020
    mov prgb %A64_1543
    ld.mem %A64_1547 nj 92
    mov py %A64_1547
    ld.mem %A64_1552 nj 140
    mov pcb %A64_1552
    ld.mem %A64_1557 nj 188
    mov pcr %A64_1557
    ld.mem %S32_1560 nj 28
    mov yy %S32_1560
    bra for_7_cond
.bbl for_7  #  edge_out[for_6_cond]  live_out[pcb  pcr  prgb  py  x  yy]
    mov x 0
    bra for_6_cond
.bbl for_6  #  edge_out[for_6_next]  live_out[pcb  pcr  prgb  py  x  yy]
    ld %U8_1562 py x
    conv %S32_1563 %U8_1562
    shl %S32_1564 %S32_1563 8
    ld %U8_1566 pcb x
    conv %S32_1567 %U8_1566
    sub %S32_1568 %S32_1567 128
    ld %U8_1570 pcr x
    conv %S32_1571 %U8_1570
    sub %S32_1572 %S32_1571 128
    mul %S32_1573 %S32_1572 359
    add %S32_1574 %S32_1564 %S32_1573
    add %S32_1575 %S32_1574 128
    shr %S32_1576 %S32_1575 8
    pusharg %S32_1576
    bsr njClip
    poparg %U8_1577
    st prgb 0 %U8_1577
    mul %S32_1578 %S32_1568 88
    sub %S32_1579 %S32_1564 %S32_1578
    mul %S32_1580 %S32_1572 183
    sub %S32_1581 %S32_1579 %S32_1580
    add %S32_1582 %S32_1581 128
    shr %S32_1583 %S32_1582 8
    pusharg %S32_1583
    bsr njClip
    poparg %U8_1584
    st prgb 1 %U8_1584
    mul %S32_1586 %S32_1568 454
    add %S32_1587 %S32_1564 %S32_1586
    add %S32_1588 %S32_1587 128
    shr %S32_1589 %S32_1588 8
    pusharg %S32_1589
    bsr njClip
    poparg %U8_1590
    st prgb 2 %U8_1590
    lea %A64_1592 prgb 3
    mov prgb %A64_1592
.bbl for_6_next  #  edge_out[for_6_cond]  live_out[pcb  pcr  prgb  py  x  yy]
    add %S32_1593 x 1
    mov x %S32_1593
.bbl for_6_cond  #  edge_out[for_6  for_6_exit]  live_out[pcb  pcr  prgb  py  x  yy]
    ld.mem %S32_1596 nj 24
    blt x %S32_1596 for_6
.bbl for_6_exit  #  edge_out[for_7_next]  live_out[pcb  pcr  prgb  py  yy]
    ld.mem %S32_1600 nj 72
    lea %A64_1601 py %S32_1600
    mov py %A64_1601
    ld.mem %S32_1606 nj 120
    lea %A64_1607 pcb %S32_1606
    mov pcb %A64_1607
    ld.mem %S32_1612 nj 168
    lea %A64_1613 pcr %S32_1612
    mov pcr %A64_1613
.bbl for_7_next  #  edge_out[for_7_cond]  live_out[pcb  pcr  prgb  py  yy]
    sub %S32_1614 yy 1
    mov yy %S32_1614
.bbl for_7_cond  #  edge_out[for_7  for_7_condbra1]  live_out[pcb  pcr  prgb  py  yy]
    bne yy 0 for_7
.bbl for_7_condbra1  #  edge_out[if_23_end]
    bra if_23_end
.bbl if_23_false  #  edge_out[if_22_true  if_23_end]
    ld.mem %S32_1618 nj 64
    ld.mem %S32_1622 nj 72
    beq %S32_1618 %S32_1622 if_23_end
.bbl if_22_true  #  edge_out[for_8_cond]  live_out[__local_26_y  pin  pout]
    ld.mem %A64_1626 nj 92
    ld.mem %S32_1630 nj 72
    lea %A64_1631 %A64_1626 %S32_1630
    mov pin %A64_1631
    ld.mem %A64_1635 nj 92
    ld.mem %S32_1639 nj 64
    lea %A64_1640 %A64_1635 %S32_1639
    mov pout %A64_1640
    ld.mem %S32_1644 nj 68
    sub %S32_1645 %S32_1644 1
    mov __local_26_y %S32_1645
    bra for_8_cond
.bbl for_8  #  edge_out[for_8_next]  live_out[__local_26_y  pin  pout]
    ld.mem %S32_1649 nj 64
    conv %U64_1650 %S32_1649
    pusharg %U64_1650
    pusharg pin
    pusharg pout
    bsr mymemcpy
    ld.mem %S32_1654 nj 72
    lea %A64_1655 pin %S32_1654
    mov pin %A64_1655
    ld.mem %S32_1659 nj 64
    lea %A64_1660 pout %S32_1659
    mov pout %A64_1660
.bbl for_8_next  #  edge_out[for_8_cond]  live_out[__local_26_y  pin  pout]
    sub %S32_1661 __local_26_y 1
    mov __local_26_y %S32_1661
.bbl for_8_cond  #  edge_out[for_8  for_8_exit]  live_out[__local_26_y  pin  pout]
    bne __local_26_y 0 for_8
.bbl for_8_exit  #  edge_out[if_23_end]
    ld.mem %S32_1665 nj 64
    st.mem nj 72 %S32_1665
.bbl if_23_end
    ret

.fun njInit NORMAL [] = []
.reg A64 [%A64_1669]
.bbl %start
    lea.mem %A64_1669 nj 0
    pusharg 525032:U64
    pusharg 0:S32
    pusharg %A64_1669
    bsr mymemset
    ret

.fun njDone NORMAL [] = []
.reg S32 [%S32_1674 %S32_1680 %S32_1684 i]
.reg A64 [%A64_1673 %A64_1675 %A64_1677 %A64_1679 %A64_1681 %A64_1683 %A64_1687 %A64_1690]
.bbl %start  #  edge_out[for_1_cond]  live_out[i]
    mov i 0
    bra for_1_cond
.bbl for_1  #  edge_out[for_1_next  if_2_true]  live_out[i]
    lea.mem %A64_1673 nj 52
    mul %S32_1674 i 48
    lea %A64_1675 %A64_1673 %S32_1674
    ld %A64_1677 %A64_1675 40
    beq %A64_1677 0 for_1_next
.bbl if_2_true  #  edge_out[for_1_next]  live_out[i]
    lea.mem %A64_1679 nj 52
    mul %S32_1680 i 48
    lea %A64_1681 %A64_1679 %S32_1680
    ld %A64_1683 %A64_1681 40
    pusharg %A64_1683
    bsr free
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[i]
    add %S32_1684 i 1
    mov i %S32_1684
.bbl for_1_cond  #  edge_out[for_1  for_1_exit]  live_out[i]
    blt i 3 for_1
.bbl for_1_exit  #  edge_out[if_4_end  if_4_true]
    ld.mem %A64_1687 nj 525020
    beq %A64_1687 0 if_4_end
.bbl if_4_true  #  edge_out[if_4_end]
    ld.mem %A64_1690 nj 525020
    pusharg %A64_1690
    bsr free
.bbl if_4_end
    bsr njInit
    ret

.fun njDecode NORMAL [S32] = [A64 S32]
.reg S32 [%S32_1693 %S32_1698 %S32_1703 %S32_1704 %S32_1710 %S32_1711 %S32_1712 %S32_1716 %S32_1721 %S32_1734 %S32_1735 %S32_1738 %S32_1741 %S32_1744 %S32_1749 size]
.reg U8 [%U8_1702 %U8_1709 %U8_1720 %U8_1727 %U8_1733]
.reg A64 [%A64_1701 %A64_1707 %A64_1719 %A64_1725 %A64_1731 jpeg]
.jtb switch_1728_tab 255 switch_1728_default [192 switch_1728_192 196 switch_1728_196 218 switch_1728_218 219 switch_1728_219 221 switch_1728_221 254 switch_1728_254]
.bbl %start  #  edge_out[if_2_end  if_2_true]
    poparg jpeg
    poparg size
    bsr njDone
    st.mem nj 4 jpeg
    and %S32_1693 size 2147483647
    st.mem nj 16 %S32_1693
    ld.mem %S32_1698 nj 16
    ble 2:S32 %S32_1698 if_2_end
.bbl if_2_true
    pusharg 1:S32
    ret
.bbl if_2_end  #  edge_out[if_3_end  if_3_true]
    ld.mem %A64_1701 nj 4
    ld %U8_1702 %A64_1701 0
    conv %S32_1703 %U8_1702
    xor %S32_1704 %S32_1703 255
    ld.mem %A64_1707 nj 4
    ld %U8_1709 %A64_1707 1
    conv %S32_1710 %U8_1709
    xor %S32_1711 %S32_1710 216
    or %S32_1712 %S32_1704 %S32_1711
    beq %S32_1712 0 if_3_end
.bbl if_3_true
    pusharg 1:S32
    ret
.bbl if_3_end  #  edge_out[while_1_cond]
    pusharg 2:S32
    bsr __static_2_njSkip
    bra while_1_cond
.bbl while_1  #  edge_out[branch_8  if_4_true]
    ld.mem %S32_1716 nj 16
    blt %S32_1716 2 if_4_true
.bbl branch_8  #  edge_out[if_4_end  if_4_true]
    ld.mem %A64_1719 nj 4
    ld %U8_1720 %A64_1719 0
    conv %S32_1721 %U8_1720
    beq %S32_1721 255 if_4_end
.bbl if_4_true
    pusharg 5:S32
    ret
.bbl if_4_end  #  edge_out[if_4_end_1  switch_1728_default]  live_out[%U8_1727]
    pusharg 2:S32
    bsr __static_2_njSkip
    ld.mem %A64_1725 nj 4
    ld %U8_1727 %A64_1725 -1
    blt 254:U8 %U8_1727 switch_1728_default
.bbl if_4_end_1  #  edge_out[switch_1728_192  switch_1728_196  switch_1728_218  switch_1728_219  switch_1728_221  switch_1728_254  switch_1728_default]
    switch %U8_1727 switch_1728_tab
.bbl switch_1728_192  #  edge_out[while_1_cond]
    bsr njDecodeSOF
    bra while_1_cond
.bbl switch_1728_196  #  edge_out[while_1_cond]
    bsr njDecodeDHT
    bra while_1_cond
.bbl switch_1728_219  #  edge_out[while_1_cond]
    bsr njDecodeDQT
    bra while_1_cond
.bbl switch_1728_221  #  edge_out[while_1_cond]
    bsr njDecodeDRI
    bra while_1_cond
.bbl switch_1728_218  #  edge_out[while_1_cond]
    bsr njDecodeScan
    bra while_1_cond
.bbl switch_1728_254  #  edge_out[while_1_cond]
    bsr njSkipMarker
    bra while_1_cond
.bbl switch_1728_default  #  edge_out[if_5_false  if_5_true]
    ld.mem %A64_1731 nj 4
    ld %U8_1733 %A64_1731 -1
    conv %S32_1734 %U8_1733
    and %S32_1735 %S32_1734 240
    bne %S32_1735 224 if_5_false
.bbl if_5_true  #  edge_out[while_1_cond]
    bsr njSkipMarker
    bra while_1_cond
.bbl if_5_false
    pusharg 2:S32
    ret
.bbl while_1_cond  #  edge_out[while_1  while_1_exit]
    ld.mem %S32_1738 nj 0
    beq %S32_1738 0 while_1
.bbl while_1_exit  #  edge_out[if_7_end  if_7_true]
    ld.mem %S32_1741 nj 0
    beq %S32_1741 6 if_7_end
.bbl if_7_true
    ld.mem %S32_1744 nj 0
    pusharg %S32_1744
    ret
.bbl if_7_end
    st.mem nj 0 0:S32
    bsr njConvert
    ld.mem %S32_1749 nj 0
    pusharg %S32_1749
    ret

.fun write_str NORMAL [] = [A64 S32]
.reg S8 [%S8_1752]
.reg S32 [%S32_1753 fd]
.reg S64 [%S64_1754]
.reg U64 [%U64_1750 size]
.reg A64 [s]
.bbl %start  #  edge_out[for_1_cond]  live_out[fd  s  size]
    poparg s
    poparg fd
    mov size 0
    bra for_1_cond
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[fd  s  size]
    add %U64_1750 size 1
    mov size %U64_1750
.bbl for_1_cond  #  edge_out[for_1_exit  for_1_next]  live_out[fd  s  size]
    ld %S8_1752 s size
    conv %S32_1753 %S8_1752
    bne %S32_1753 0 for_1_next
.bbl for_1_exit
    pusharg size
    pusharg s
    pusharg fd
    bsr write
    poparg %S64_1754
    ret

.fun write_dec NORMAL [] = [S32 S32]
.reg S8 [%S8_1761]
.reg S32 [%S32_1758 %S32_1759 %S32_1760 %S32_1764 %S32_1765 %S32_1767 a fd i]
.reg A64 [%A64_1768]
.stk buf 1 64
.bbl %start  #  edge_out[while_1]  live_out[a  fd  i]
    poparg fd
    poparg a
    st.stk buf 63 0:S8
    mov %S32_1758 62
    mov i %S32_1758
.bbl while_1  #  edge_out[while_1_cond]  live_out[%S32_1764  %S32_1765  a  fd  i]
    rem %S32_1759 a 10
    add %S32_1760 %S32_1759 48
    conv %S8_1761 %S32_1760
    st.stk buf i %S8_1761
    sub %S32_1764 i 1
    mov i %S32_1764
    div %S32_1765 a 10
    mov a %S32_1765
.bbl while_1_cond  #  edge_out[while_1  while_1_exit]  live_out[%S32_1764  a  fd  i]
    bne %S32_1765 0 while_1
.bbl while_1_exit
    add %S32_1767 %S32_1764 1
    lea.stk %A64_1768 buf %S32_1767
    pusharg fd
    pusharg %A64_1768
    bsr write_str
    ret

.fun main NORMAL [S32] = [S32 A64]
.reg S32 [%S32_1772 %S32_1779 %S32_1787 %S32_1788 %S32_1789 %S32_1793 %S32_1794 %S32_1795 %S32_1796 %S32_1797 %S32_1799 %S32_1802 %S32_1804 %S32_1808 %S32_1811 argc]
.reg S64 [%S64_1776 %S64_1782 %S64_1786 %S64_1810]
.reg U64 [%U64_1780 %U64_1785 %U64_1809]
.reg A64 [%A64_1769 %A64_1771 %A64_1775 %A64_1781 %A64_1790 %A64_1792 %A64_1798 %A64_1800 %A64_1801 %A64_1803 %A64_1805 %A64_1806 %A64_1807 argv]
.bbl %start  #  edge_out[if_1_end  if_1_true]  live_out[argv]
    poparg argc
    poparg argv
    ble 3:S32 argc if_1_end
.bbl if_1_true
    lea.mem %A64_1769 string_const_1 0
    pusharg %A64_1769
    bsr print_s_ln
    pusharg 2:S32
    ret
.bbl if_1_end  #  edge_out[if_2_end  if_2_true]  live_out[%S32_1772  argv]
    ld %A64_1771 argv 8
    pusharg 0:S32
    pusharg 0:S32
    pusharg %A64_1771
    bsr open
    poparg %S32_1772
    ble 0:S32 %S32_1772 if_2_end
.bbl if_2_true
    lea.mem %A64_1775 string_const_2 0
    pusharg %A64_1775
    bsr print_s_ln
    pusharg 1:S32
    ret
.bbl if_2_end  #  edge_out[if_3_end  if_3_true]  live_out[%A64_1781  argv]
    pusharg 2:S32
    pusharg 0:S64
    pusharg %S32_1772
    bsr lseek
    poparg %S64_1776
    conv %S32_1779 %S64_1776
    conv %U64_1780 %S32_1779
    pusharg %U64_1780
    bsr malloc
    poparg %A64_1781
    pusharg 0:S32
    pusharg 0:S64
    pusharg %S32_1772
    bsr lseek
    poparg %S64_1782
    conv %U64_1785 %S32_1779
    pusharg %U64_1785
    pusharg %A64_1781
    pusharg %S32_1772
    bsr read
    poparg %S64_1786
    conv %S32_1787 %S64_1786
    pusharg %S32_1772
    bsr close
    poparg %S32_1788
    bsr njInit
    pusharg %S32_1787
    pusharg %A64_1781
    bsr njDecode
    poparg %S32_1789
    beq %S32_1789 0 if_3_end
.bbl if_3_true
    pusharg %A64_1781
    bsr free
    lea.mem %A64_1790 string_const_3 0
    pusharg %A64_1790
    bsr print_s_ln
    pusharg 1:S32
    ret
.bbl if_3_end  #  edge_out[if_4_end  if_4_true]  live_out[%S32_1797]
    pusharg %A64_1781
    bsr free
    ld %A64_1792 argv 16
    mov %S32_1793 65
    or %S32_1794 %S32_1793 512
    mov %S32_1795 6
    shl %S32_1796 %S32_1795 6
    pusharg %S32_1796
    pusharg %S32_1794
    pusharg %A64_1792
    bsr open
    poparg %S32_1797
    ble 0:S32 %S32_1797 if_4_end
.bbl if_4_true
    lea.mem %A64_1798 string_const_4 0
    pusharg %A64_1798
    bsr print_s_ln
    pusharg 1:S32
    ret
.bbl if_4_end  #  edge_out[if_5_false  if_5_true]  live_out[%S32_1797]
    bsr njIsColor
    poparg %S32_1799
    beq %S32_1799 0 if_5_false
.bbl if_5_true  #  edge_out[if_5_end]  live_out[%S32_1797]
    lea.mem %A64_1800 string_const_5 0
    pusharg %S32_1797
    pusharg %A64_1800
    bsr write_str
    bra if_5_end
.bbl if_5_false  #  edge_out[if_5_end]  live_out[%S32_1797]
    lea.mem %A64_1801 string_const_6 0
    pusharg %S32_1797
    pusharg %A64_1801
    bsr write_str
.bbl if_5_end
    bsr njGetWidth
    poparg %S32_1802
    pusharg %S32_1802
    pusharg %S32_1797
    bsr write_dec
    lea.mem %A64_1803 string_const_7 0
    pusharg %S32_1797
    pusharg %A64_1803
    bsr write_str
    bsr njGetHeight
    poparg %S32_1804
    pusharg %S32_1804
    pusharg %S32_1797
    bsr write_dec
    lea.mem %A64_1805 string_const_8 0
    pusharg %S32_1797
    pusharg %A64_1805
    bsr write_str
    lea.mem %A64_1806 string_const_9 0
    pusharg %S32_1797
    pusharg %A64_1806
    bsr write_str
    bsr njGetImage
    poparg %A64_1807
    bsr njGetImageSize
    poparg %S32_1808
    conv %U64_1809 %S32_1808
    pusharg %U64_1809
    pusharg %A64_1807
    pusharg %S32_1797
    bsr write
    poparg %S64_1810
    pusharg %S32_1797
    bsr close
    poparg %S32_1811
    bsr njDone
    pusharg 0:S32
    ret
