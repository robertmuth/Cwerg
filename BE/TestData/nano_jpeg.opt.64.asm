# write_s                        RegStats:  0/ 3   0/ 5   0/ 2
# write_c                        RegStats:  0/ 0   0/10   0/ 3
# print_s_ln                     RegStats:  0/ 0   0/ 3   0/ 1
# abort                          RegStats:  0/ 0   0/ 2   0/ 1
# malloc                         RegStats:  2/ 0   1/18   1/ 2
# free                           RegStats:  0/ 0   0/ 1   0/ 1
# mymemset                       RegStats:  0/ 4   0/ 4   0/ 2
# mymemcpy                       RegStats:  0/ 4   0/ 4   0/ 2
# njGetWidth                     RegStats:  0/ 0   0/ 1   0/ 1
# njGetHeight                    RegStats:  0/ 0   0/ 1   0/ 1
# njIsColor                      RegStats:  0/ 0   0/ 1   0/ 1
# njGetImage                     RegStats:  0/ 0   0/ 3   0/ 2
# njGetImageSize                 RegStats:  0/ 0   0/ 7   0/ 2
# njClip                         RegStats:  0/ 1   0/ 2   0/ 1
# njRowIDCT                      RegStats:  0/ 8   0/49   0/ 9
# njColIDCT                      RegStats:  9/ 2   1/91   9/ 9
# __static_1_njShowBits          RegStats:  0/ 2   0/48   0/ 4
# njSkipBits                     RegStats:  1/ 0   0/ 4   0/ 1
# njGetBits                      RegStats:  0/ 0   2/ 0   2/ 0
# njByteAlign                    RegStats:  0/ 0   0/ 2   0/ 1
# __static_2_njSkip              RegStats:  0/ 0   0/ 8   0/ 3
# njDecode16                     RegStats:  0/ 0   0/13   0/ 3
# __static_3_njDecodeLength      RegStats:  0/ 0   0/ 7   0/ 3
# njSkipMarker                   RegStats:  0/ 0   0/ 1   0/ 1
# njDecodeSOF                    RegStats:  4/ 1   0/123   0/ 3
# njDecodeDHT                    RegStats:  5/ 3   0/32   0/ 3
# njDecodeDQT                    RegStats:  0/ 2   0/18   0/ 3
# njDecodeDRI                    RegStats:  0/ 0   0/ 7   0/ 2
# njGetVLC                       RegStats:  4/ 0   0/16   0/ 2
# njDecodeBlock                  RegStats:  3/ 1   1/65   1/ 4
# njDecodeScan                   RegStats:  8/ 0   0/81   0/ 3
# njUpsampleH                    RegStats:  7/ 0   0/191   0/ 3
# njUpsampleV                    RegStats:  9/ 0   1/185   3/ 3
# njConvert                      RegStats: 11/ 0   3/65   3/ 3
# njInit                         RegStats:  0/ 0   0/ 1   0/ 1
# njDone                         RegStats:  1/ 0   0/10   0/ 2
# njDecode                       RegStats:  0/ 1   2/34   2/ 3
# write_str                      RegStats:  0/ 3   0/ 5   0/ 2
# write_dec                      RegStats:  0/ 3   0/ 7   0/ 2
# main                           RegStats:  3/ 0   3/28   2/ 3
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

.fun kill BUILTIN [S32] = [S32 S32]

.fun getpid BUILTIN [S32] = []

.fun write_s NORMAL [S64] = [S32 A64]
.reg S8 $1_narrowed_S8
.reg S8 $2_narrowed_S8
.reg S32 %S32_4
.reg S32 %S8_3
.reg S32 fd
.reg S64 %out
.reg U64 len
.reg A64 s
.bbl %start  #  edge_out[while_1_cond]  live_out[fd  len  s]
    poparg fd
    poparg s
    mov len 0
    bra while_1_cond
.bbl while_1  #  edge_out[while_1_cond]  live_out[fd  len  s]
    add len len 1
.bbl while_1_cond  #  edge_out[while_1  while_1_exit]  live_out[fd  len  s]
    ld $1_narrowed_S8 s len
    conv %S8_3 $1_narrowed_S8
    conv $2_narrowed_S8 %S8_3
    conv %S32_4 $2_narrowed_S8
    bne %S32_4 0 while_1
.bbl while_1_exit
    pusharg len
    pusharg s
    pusharg fd
    bsr write
    poparg %out
    pusharg %out
    ret

.fun write_c NORMAL [S64] = [S32 U32]
.reg S8 $2_narrowed_S8
.reg S8 $3_narrowed_S8
.reg S32 %S32_6
.reg S32 %S8_1
.reg S32 fd
.reg S64 %S64_4
.reg S64 %out
.reg U8 $1_narrowed_U8
.reg U32 c
.reg A64 %A64_3
.stk buffer 1 16
.bbl %start
    poparg fd
    poparg c
    conv $1_narrowed_U8 c
    conv $2_narrowed_S8 $1_narrowed_U8
    conv %S8_1 $2_narrowed_S8
    conv $3_narrowed_S8 %S8_1
    st.stk buffer 0 $3_narrowed_S8
    lea.stk %A64_3 buffer 0
    pusharg 1:U64
    pusharg %A64_3
    pusharg fd
    bsr write
    poparg %S64_4
    conv %S32_6 %S64_4
    conv %out %S32_6
    pusharg %out
    ret

.fun print_s_ln NORMAL [] = [A64]
.reg S64 %S64_1
.reg S64 %S64_3
.reg A64 s
.bbl %start
    poparg s
    pusharg s
    pusharg 1:S32
    bsr write_s
    poparg %S64_1
    pusharg 10:U32
    pusharg 1:S32
    bsr write_c
    poparg %S64_3
    ret

.fun abort NORMAL [] = []
.reg S32 %S32_1
.reg S32 %S32_2
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
.reg U64 %U64_10
.reg U64 %U64_11
.reg U64 %U64_18
.reg U64 %U64_19
.reg U64 %U64_20
.reg U64 increment
.reg U64 rounded_size
.reg U64 size
.reg A64 %A64_14
.reg A64 %A64_15
.reg A64 %A64_17
.reg A64 %A64_23
.reg A64 %A64_25
.reg A64 %A64_28
.reg A64 %A64_3
.reg A64 %A64_32
.reg A64 %A64_33
.reg A64 %A64_4
.reg A64 %A64_8
.reg A64 %out
.reg A64 new_end
.bbl %start  #  edge_out[if_1_end  if_1_true]  live_out[size]
    poparg size
    ld.mem %A64_3 __static_1__malloc_start 0
    bne %A64_3 0 if_1_end
.bbl if_1_true  #  edge_out[if_1_end]  live_out[size]
    pusharg 0:A64
    bsr xbrk
    poparg %A64_4
    st.mem __static_1__malloc_start 0 %A64_4
    ld.mem %A64_8 __static_1__malloc_start 0
    st.mem __static_2__malloc_end 0 %A64_8
.bbl if_1_end  #  edge_out[if_3_end  if_3_true]  live_out[rounded_size]
    add %U64_10 size 15
    div %U64_11 %U64_10 16
    shl rounded_size %U64_11 4
    ld.mem %A64_14 __static_1__malloc_start 0
    lea %A64_15 %A64_14 rounded_size
    ld.mem %A64_17 __static_2__malloc_end 0
    ble %A64_15 %A64_17 if_3_end
.bbl if_3_true  #  edge_out[if_2_true  if_3_end]  live_out[rounded_size]
    add %U64_18 rounded_size 1048576
    sub %U64_19 %U64_18 1
    div %U64_20 %U64_19 1048576
    shl increment %U64_20 20
    ld.mem %A64_23 __static_2__malloc_end 0
    lea new_end %A64_23 increment
    pusharg new_end
    bsr xbrk
    poparg %A64_25
    st.mem __static_2__malloc_end 0 %A64_25
    ld.mem %A64_28 __static_2__malloc_end 0
    beq %A64_28 new_end if_3_end
.bbl if_2_true  #  edge_out[if_3_end]  live_out[rounded_size]
    bsr abort
.bbl if_3_end
    ld.mem %out __static_1__malloc_start 0
    ld.mem %A64_32 __static_1__malloc_start 0
    lea %A64_33 %A64_32 rounded_size
    st.mem __static_1__malloc_start 0 %A64_33
    pusharg %out
    ret

.fun free NORMAL [] = [A64]
.reg A64 ptr
.bbl %start
    poparg ptr
    ret

.fun mymemset NORMAL [] = [A64 S32 U64]
.reg S8 $1_narrowed_S8
.reg S8 $2_narrowed_S8
.reg S32 %S8_1
.reg S32 i
.reg S32 value
.reg U64 %U64_4
.reg U64 num
.reg A64 ptr
.bbl %start  #  edge_out[for_1_cond]  live_out[i  num  ptr  value]
    poparg ptr
    poparg value
    poparg num
    mov i 0
    bra for_1_cond
.bbl for_1  #  edge_out[for_1_next]  live_out[i  num  ptr  value]
    conv $1_narrowed_S8 value
    conv %S8_1 $1_narrowed_S8
    conv $2_narrowed_S8 %S8_1
    st ptr i $2_narrowed_S8
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[i  num  ptr  value]
    add i i 1
.bbl for_1_cond  #  edge_out[for_1  for_1_exit]  live_out[i  num  ptr  value]
    conv %U64_4 i
    blt %U64_4 num for_1
.bbl for_1_exit
    ret

.fun mymemcpy NORMAL [] = [A64 A64 U64]
.reg S8 $1_narrowed_S8
.reg S8 $2_narrowed_S8
.reg S32 %S8_6
.reg S32 i
.reg U64 %U64_9
.reg U64 num
.reg A64 destination
.reg A64 source
.bbl %start  #  edge_out[for_1_cond]  live_out[destination  i  num  source]
    poparg destination
    poparg source
    poparg num
    mov i 0
    bra for_1_cond
.bbl for_1  #  edge_out[for_1_next]  live_out[destination  i  num  source]
    ld $1_narrowed_S8 source i
    conv %S8_6 $1_narrowed_S8
    conv $2_narrowed_S8 %S8_6
    st destination i $2_narrowed_S8
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[destination  i  num  source]
    add i i 1
.bbl for_1_cond  #  edge_out[for_1  for_1_exit]  live_out[destination  i  num  source]
    conv %U64_9 i
    blt %U64_9 num for_1
.bbl for_1_exit
    ret

.fun njGetWidth NORMAL [S32] = []
.reg S32 %out
.bbl %start
    ld.mem %out nj 24
    pusharg %out
    ret

.fun njGetHeight NORMAL [S32] = []
.reg S32 %out
.bbl %start
    ld.mem %out nj 28
    pusharg %out
    ret

.fun njIsColor NORMAL [S32] = []
.reg U32 %U32_18
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
.reg U32 %U32_21
.reg A64 $1_%out
.reg A64 %out
.bbl %start  #  edge_out[if_1_false  if_1_true]
    ld.mem %U32_21 nj 48
    bne %U32_21 1 if_1_false
.bbl if_1_true
    ld.mem %out nj 92
    pusharg %out
    ret
.bbl if_1_false
    ld.mem $1_%out nj 525020
    pusharg $1_%out
    ret

.fun njGetImageSize NORMAL [S32] = []
.reg S32 %S32_31
.reg S32 %S32_34
.reg S32 %S32_35
.reg S32 %out
.reg U32 %U32_36
.reg U32 %U32_39
.reg U32 %U32_40
.bbl %start
    ld.mem %S32_31 nj 24
    ld.mem %S32_34 nj 28
    mul %S32_35 %S32_31 %S32_34
    conv %U32_36 %S32_35
    ld.mem %U32_39 nj 48
    mul %U32_40 %U32_36 %U32_39
    conv %out %U32_40
    pusharg %out
    ret

.fun njClip NORMAL [U32] = [S32]
.reg S32 x
.reg U8 $1_narrowed_U8
.reg U32 %out
.bbl %start  #  edge_out[if_2_false  if_2_true]  live_out[x]
    poparg x
    ble 0:S32 x if_2_false
.bbl if_2_true
    pusharg 0:U32
    ret
.bbl if_2_false  #  edge_out[if_1_true  if_2_end]  live_out[x]
    ble x 255 if_2_end
.bbl if_1_true
    pusharg 255:U32
    ret
.bbl if_2_end
    conv $1_narrowed_U8 x
    conv %out $1_narrowed_U8
    pusharg %out
    ret

.fun njRowIDCT NORMAL [] = [A64]
.reg S32 $1_x8
.reg S32 $2_x8
.reg S32 $3_x0
.reg S32 $4_x8
.reg S32 $5_x0
.reg S32 %S32_100
.reg S32 %S32_110
.reg S32 %S32_111
.reg S32 %S32_112
.reg S32 %S32_114
.reg S32 %S32_115
.reg S32 %S32_116
.reg S32 %S32_118
.reg S32 %S32_119
.reg S32 %S32_120
.reg S32 %S32_121
.reg S32 %S32_123
.reg S32 %S32_124
.reg S32 %S32_126
.reg S32 %S32_127
.reg S32 %S32_129
.reg S32 %S32_130
.reg S32 %S32_132
.reg S32 %S32_133
.reg S32 %S32_135
.reg S32 %S32_136
.reg S32 %S32_138
.reg S32 %S32_139
.reg S32 %S32_44
.reg S32 %S32_48
.reg S32 %S32_51
.reg S32 %S32_54
.reg S32 %S32_57
.reg S32 %S32_60
.reg S32 %S32_63
.reg S32 %S32_64
.reg S32 %S32_65
.reg S32 %S32_73
.reg S32 %S32_74
.reg S32 %S32_76
.reg S32 %S32_79
.reg S32 %S32_82
.reg S32 %S32_84
.reg S32 %S32_87
.reg S32 %S32_90
.reg S32 %S32_94
.reg S32 %S32_97
.reg S32 x0
.reg S32 x1
.reg S32 x2
.reg S32 x3
.reg S32 x4
.reg S32 x5
.reg S32 x6
.reg S32 x7
.reg S32 x8
.reg A64 blk
.bbl %start  #  edge_out[if_1_end  if_1_true]  live_out[blk  x1  x2  x3  x4  x5  x6  x7]
    poparg blk
    ld %S32_44 blk 16
    shl x1 %S32_44 11
    ld x2 blk 24
    or %S32_48 x1 x2
    ld x3 blk 8
    or %S32_51 %S32_48 x3
    ld x4 blk 4
    or %S32_54 %S32_51 x4
    ld x5 blk 28
    or %S32_57 %S32_54 x5
    ld x6 blk 20
    or %S32_60 %S32_57 x6
    ld x7 blk 12
    or %S32_63 %S32_60 x7
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
    add x0 %S32_74 128
    add %S32_76 x4 x5
    mul x8 %S32_76 565
    mul %S32_79 x4 2276
    add x4 x8 %S32_79
    mul %S32_82 x5 3406
    sub x5 x8 %S32_82
    add %S32_84 x6 x7
    mul $1_x8 %S32_84 2408
    mul %S32_87 x6 799
    sub x6 $1_x8 %S32_87
    mul %S32_90 x7 4017
    sub x7 $1_x8 %S32_90
    add $2_x8 x0 x1
    sub $3_x0 x0 x1
    add %S32_94 x3 x2
    mul x1 %S32_94 1108
    mul %S32_97 x2 3784
    sub x2 x1 %S32_97
    mul %S32_100 x3 1568
    add x3 x1 %S32_100
    add x1 x4 x6
    sub x4 x4 x6
    add x6 x5 x7
    sub x5 x5 x7
    add x7 $2_x8 x3
    sub $4_x8 $2_x8 x3
    add x3 $3_x0 x2
    sub $5_x0 $3_x0 x2
    add %S32_110 x4 x5
    mul %S32_111 %S32_110 181
    add %S32_112 %S32_111 128
    shr x2 %S32_112 8
    sub %S32_114 x4 x5
    mul %S32_115 %S32_114 181
    add %S32_116 %S32_115 128
    shr x4 %S32_116 8
    add %S32_118 x7 x1
    shr %S32_119 %S32_118 8
    st blk 0 %S32_119
    add %S32_120 x3 x2
    shr %S32_121 %S32_120 8
    st blk 4 %S32_121
    add %S32_123 $5_x0 x4
    shr %S32_124 %S32_123 8
    st blk 8 %S32_124
    add %S32_126 $4_x8 x6
    shr %S32_127 %S32_126 8
    st blk 12 %S32_127
    sub %S32_129 $4_x8 x6
    shr %S32_130 %S32_129 8
    st blk 16 %S32_130
    sub %S32_132 $5_x0 x4
    shr %S32_133 %S32_132 8
    st blk 20 %S32_133
    sub %S32_135 x3 x2
    shr %S32_136 %S32_135 8
    st blk 24 %S32_136
    sub %S32_138 x7 x1
    shr %S32_139 %S32_138 8
    st blk 28 %S32_139
    ret

.fun njColIDCT NORMAL [] = [A64 A64 S32]
.reg S32 $1_x8
.reg S32 $2_x8
.reg S32 $3_x8
.reg S32 %S32_142
.reg S32 %S32_144
.reg S32 %S32_147
.reg S32 %S32_150
.reg S32 %S32_152
.reg S32 %S32_155
.reg S32 %S32_160
.reg S32 %S32_162
.reg S32 %S32_165
.reg S32 %S32_167
.reg S32 %S32_170
.reg S32 %S32_172
.reg S32 %S32_175
.reg S32 %S32_176
.reg S32 %S32_177
.reg S32 %S32_178
.reg S32 %S32_179
.reg S32 %S32_185
.reg S32 %S32_186
.reg S32 %S32_188
.reg S32 %S32_189
.reg S32 %S32_192
.reg S32 %S32_193
.reg S32 %S32_196
.reg S32 %S32_197
.reg S32 %S32_199
.reg S32 %S32_200
.reg S32 %S32_203
.reg S32 %S32_204
.reg S32 %S32_207
.reg S32 %S32_208
.reg S32 %S32_212
.reg S32 %S32_213
.reg S32 %S32_216
.reg S32 %S32_217
.reg S32 %S32_220
.reg S32 %S32_221
.reg S32 %S32_231
.reg S32 %S32_232
.reg S32 %S32_233
.reg S32 %S32_235
.reg S32 %S32_236
.reg S32 %S32_237
.reg S32 %S32_239
.reg S32 %S32_240
.reg S32 %S32_241
.reg S32 %S32_244
.reg S32 %S32_245
.reg S32 %S32_246
.reg S32 %S32_249
.reg S32 %S32_250
.reg S32 %S32_251
.reg S32 %S32_254
.reg S32 %S32_255
.reg S32 %S32_256
.reg S32 %S32_259
.reg S32 %S32_260
.reg S32 %S32_261
.reg S32 %S32_264
.reg S32 %S32_265
.reg S32 %S32_266
.reg S32 %S32_269
.reg S32 %S32_270
.reg S32 %S32_271
.reg S32 %S32_274
.reg S32 %S32_275
.reg S32 %S32_276
.reg S32 stride
.reg S32 x0
.reg S32 x1
.reg S32 x2
.reg S32 x3
.reg S32 x4
.reg S32 x5
.reg S32 x6
.reg S32 x7
.reg S32 x8
.reg U8 $10_narrowed_U8
.reg U8 $11_narrowed_U8
.reg U8 $12_narrowed_U8
.reg U8 $13_narrowed_U8
.reg U8 $14_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U8 $8_narrowed_U8
.reg U8 $9_narrowed_U8
.reg U32 %U8_180
.reg U32 %U8_182
.reg U32 %U8_242
.reg U32 %U8_247
.reg U32 %U8_252
.reg U32 %U8_257
.reg U32 %U8_262
.reg U32 %U8_267
.reg U32 %U8_272
.reg U32 %U8_277
.reg A64 blk
.reg A64 out
.bbl %start  #  edge_out[if_3_end  if_3_true]  live_out[blk  out  stride  x1  x2  x3  x4  x5  x6  x7]
    poparg blk
    poparg out
    poparg stride
    mov %S32_142 128
    ld %S32_144 blk %S32_142
    shl x1 %S32_144 8
    mov %S32_147 192
    ld x2 blk %S32_147
    or %S32_150 x1 x2
    mov %S32_152 64
    ld x3 blk %S32_152
    or %S32_155 %S32_150 x3
    ld x4 blk 32
    or %S32_160 %S32_155 x4
    mov %S32_162 224
    ld x5 blk %S32_162
    or %S32_165 %S32_160 x5
    mov %S32_167 160
    ld x6 blk %S32_167
    or %S32_170 %S32_165 x6
    mov %S32_172 96
    ld x7 blk %S32_172
    or %S32_175 %S32_170 x7
    bne %S32_175 0 if_3_end
.bbl if_3_true  #  edge_out[for_1_cond]  live_out[out  stride  x0  x1]
    ld %S32_176 blk 0
    add %S32_177 %S32_176 32
    shr %S32_178 %S32_177 6
    add %S32_179 %S32_178 128
    pusharg %S32_179
    bsr njClip
    poparg %U8_180
    conv $4_narrowed_U8 %U8_180
    conv x1 $4_narrowed_U8
    mov x0 8
    bra for_1_cond
.bbl for_1  #  edge_out[for_1_next]  live_out[out  stride  x0  x1]
    conv $5_narrowed_U8 x1
    conv %U8_182 $5_narrowed_U8
    conv $6_narrowed_U8 %U8_182
    st out 0 $6_narrowed_U8
    lea out out stride
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[out  stride  x0  x1]
    sub x0 x0 1
.bbl for_1_cond  #  edge_out[for_1  for_1_exit]  live_out[out  stride  x0  x1]
    bne x0 0 for_1
.bbl for_1_exit
    ret
.bbl if_3_end
    ld %S32_185 blk 0
    shl %S32_186 %S32_185 8
    add x0 %S32_186 8192
    add %S32_188 x4 x5
    mul %S32_189 %S32_188 565
    add x8 %S32_189 4
    mul %S32_192 x4 2276
    add %S32_193 x8 %S32_192
    shr x4 %S32_193 3
    mul %S32_196 x5 3406
    sub %S32_197 x8 %S32_196
    shr x5 %S32_197 3
    add %S32_199 x6 x7
    mul %S32_200 %S32_199 2408
    add $1_x8 %S32_200 4
    mul %S32_203 x6 799
    sub %S32_204 $1_x8 %S32_203
    shr x6 %S32_204 3
    mul %S32_207 x7 4017
    sub %S32_208 $1_x8 %S32_207
    shr x7 %S32_208 3
    add $2_x8 x0 x1
    sub x0 x0 x1
    add %S32_212 x3 x2
    mul %S32_213 %S32_212 1108
    add x1 %S32_213 4
    mul %S32_216 x2 3784
    sub %S32_217 x1 %S32_216
    shr x2 %S32_217 3
    mul %S32_220 x3 1568
    add %S32_221 x1 %S32_220
    shr x3 %S32_221 3
    add x1 x4 x6
    sub x4 x4 x6
    add x6 x5 x7
    sub x5 x5 x7
    add x7 $2_x8 x3
    sub $3_x8 $2_x8 x3
    add x3 x0 x2
    sub x0 x0 x2
    add %S32_231 x4 x5
    mul %S32_232 %S32_231 181
    add %S32_233 %S32_232 128
    shr x2 %S32_233 8
    sub %S32_235 x4 x5
    mul %S32_236 %S32_235 181
    add %S32_237 %S32_236 128
    shr x4 %S32_237 8
    add %S32_239 x7 x1
    shr %S32_240 %S32_239 14
    add %S32_241 %S32_240 128
    pusharg %S32_241
    bsr njClip
    poparg %U8_242
    conv $7_narrowed_U8 %U8_242
    st out 0 $7_narrowed_U8
    lea out out stride
    add %S32_244 x3 x2
    shr %S32_245 %S32_244 14
    add %S32_246 %S32_245 128
    pusharg %S32_246
    bsr njClip
    poparg %U8_247
    conv $8_narrowed_U8 %U8_247
    st out 0 $8_narrowed_U8
    lea out out stride
    add %S32_249 x0 x4
    shr %S32_250 %S32_249 14
    add %S32_251 %S32_250 128
    pusharg %S32_251
    bsr njClip
    poparg %U8_252
    conv $9_narrowed_U8 %U8_252
    st out 0 $9_narrowed_U8
    lea out out stride
    add %S32_254 $3_x8 x6
    shr %S32_255 %S32_254 14
    add %S32_256 %S32_255 128
    pusharg %S32_256
    bsr njClip
    poparg %U8_257
    conv $10_narrowed_U8 %U8_257
    st out 0 $10_narrowed_U8
    lea out out stride
    sub %S32_259 $3_x8 x6
    shr %S32_260 %S32_259 14
    add %S32_261 %S32_260 128
    pusharg %S32_261
    bsr njClip
    poparg %U8_262
    conv $11_narrowed_U8 %U8_262
    st out 0 $11_narrowed_U8
    lea out out stride
    sub %S32_264 x0 x4
    shr %S32_265 %S32_264 14
    add %S32_266 %S32_265 128
    pusharg %S32_266
    bsr njClip
    poparg %U8_267
    conv $12_narrowed_U8 %U8_267
    st out 0 $12_narrowed_U8
    lea out out stride
    sub %S32_269 x3 x2
    shr %S32_270 %S32_269 14
    add %S32_271 %S32_270 128
    pusharg %S32_271
    bsr njClip
    poparg %U8_272
    conv $13_narrowed_U8 %U8_272
    st out 0 $13_narrowed_U8
    lea out out stride
    sub %S32_274 x7 x1
    shr %S32_275 %S32_274 14
    add %S32_276 %S32_275 128
    pusharg %S32_276
    bsr njClip
    poparg %U8_277
    conv $14_narrowed_U8 %U8_277
    st out 0 $14_narrowed_U8
    ret

.fun __static_1_njShowBits NORMAL [S32] = [S32]
.reg S32 %S32_280
.reg S32 %S32_283
.reg S32 %S32_284
.reg S32 %S32_285
.reg S32 %S32_290
.reg S32 %S32_291
.reg S32 %S32_306
.reg S32 %S32_307
.reg S32 %S32_312
.reg S32 %S32_313
.reg S32 %S32_318
.reg S32 %S32_319
.reg S32 %S32_320
.reg S32 %S32_321
.reg S32 %S32_324
.reg S32 %S32_327
.reg S32 %S32_340
.reg S32 %S32_341
.reg S32 %S32_348
.reg S32 %S32_349
.reg S32 %S32_354
.reg S32 %S32_355
.reg S32 %S32_356
.reg S32 %S32_357
.reg S32 %S32_362
.reg S32 %S32_363
.reg S32 %S32_370
.reg S32 %S32_373
.reg S32 %S32_376
.reg S32 %S32_377
.reg S32 %S32_378
.reg S32 %S32_379
.reg S32 %S32_380
.reg S32 %out
.reg S32 bits
.reg U8 $1_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U32 marker
.reg U32 newbyte
.reg A64 %A64_296
.reg A64 %A64_300
.reg A64 %A64_301
.reg A64 %A64_330
.reg A64 %A64_334
.reg A64 %A64_335
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
    ld $1_narrowed_U8 %A64_296 0
    conv newbyte $1_narrowed_U8
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
    conv $2_narrowed_U8 newbyte
    conv %S32_320 $2_narrowed_U8
    or %S32_321 %S32_319 %S32_320
    st.mem nj 524752 %S32_321
    conv $3_narrowed_U8 newbyte
    conv %S32_324 $3_narrowed_U8
    bne %S32_324 255 while_1_cond
.bbl if_6_true  #  edge_out[if_5_false  if_5_true]  live_out[bits]
    ld.mem %S32_327 nj 16
    beq %S32_327 0 if_5_false
.bbl if_5_true  #  edge_out[if_5_true_1  switch_344_default]  live_out[bits  marker]
    ld.mem %A64_330 nj 4
    ld $4_narrowed_U8 %A64_330 0
    conv marker $4_narrowed_U8
    ld.mem %A64_334 nj 4
    lea %A64_335 %A64_334 1
    st.mem nj 4 %A64_335
    ld.mem %S32_340 nj 16
    sub %S32_341 %S32_340 1
    st.mem nj 16 %S32_341
    conv $5_narrowed_U8 marker
    conv marker $5_narrowed_U8
    blt 255:U32 marker switch_344_default
.bbl if_5_true_1  #  edge_out[switch_344_217  switch_344_default  while_1_cond  while_1_cond]  live_out[bits  marker]
    switch marker switch_344_tab
.bbl switch_344_217  #  edge_out[while_1_cond]  live_out[bits]
    st.mem nj 16 0:S32
    bra while_1_cond
.bbl switch_344_default  #  edge_out[if_4_false  if_4_true]  live_out[bits  marker]
    conv $6_narrowed_U8 marker
    conv %S32_348 $6_narrowed_U8
    and %S32_349 %S32_348 248
    beq %S32_349 208 if_4_false
.bbl if_4_true  #  edge_out[while_1_cond]  live_out[bits]
    st.mem nj 0 5:S32
    bra while_1_cond
.bbl if_4_false  #  edge_out[while_1_cond]  live_out[bits]
    ld.mem %S32_354 nj 524752
    shl %S32_355 %S32_354 8
    conv $7_narrowed_U8 marker
    conv %S32_356 $7_narrowed_U8
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
    and %out %S32_378 %S32_380
    pusharg %out
    ret

.fun njSkipBits NORMAL [] = [S32]
.reg S32 %S32_384
.reg S32 %S32_385
.reg S32 %S32_388
.reg S32 %S32_389
.reg S32 bits
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
.reg S32 %out
.reg S32 bits
.bbl %start
    poparg bits
    pusharg bits
    bsr __static_1_njShowBits
    poparg %out
    pusharg bits
    bsr njSkipBits
    pusharg %out
    ret

.fun njByteAlign NORMAL [] = []
.reg S32 %S32_395
.reg S32 %S32_396
.bbl %start
    ld.mem %S32_395 nj 524756
    and %S32_396 %S32_395 248
    st.mem nj 524756 %S32_396
    ret

.fun __static_2_njSkip NORMAL [] = [S32]
.reg S32 %S32_407
.reg S32 %S32_408
.reg S32 %S32_413
.reg S32 %S32_414
.reg S32 %S32_419
.reg S32 count
.reg A64 %A64_401
.reg A64 %A64_402
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

.fun njDecode16 NORMAL [U32] = [A64]
.reg S32 %S32_423
.reg S32 %S32_424
.reg S32 %S32_427
.reg S32 %S32_428
.reg U8 $1_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U16 $5_narrowed_U16
.reg U32 %U8_422
.reg U32 %U8_426
.reg U32 %out
.reg A64 pos
.bbl %start
    poparg pos
    ld $1_narrowed_U8 pos 0
    conv %U8_422 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_422
    conv %S32_423 $2_narrowed_U8
    shl %S32_424 %S32_423 8
    ld $3_narrowed_U8 pos 1
    conv %U8_426 $3_narrowed_U8
    conv $4_narrowed_U8 %U8_426
    conv %S32_427 $4_narrowed_U8
    or %S32_428 %S32_424 %S32_427
    conv $5_narrowed_U16 %S32_428
    conv %out $5_narrowed_U16
    pusharg %out
    ret

.fun __static_3_njDecodeLength NORMAL [] = []
.reg S32 %S32_432
.reg S32 %S32_439
.reg S32 %S32_444
.reg S32 %S32_447
.reg U16 $1_narrowed_U16
.reg U32 %U16_438
.reg A64 %A64_437
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
    conv $1_narrowed_U16 %U16_438
    conv %S32_439 $1_narrowed_U16
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
.reg S32 %S32_453
.bbl %start
    bsr __static_3_njDecodeLength
    ld.mem %S32_453 nj 20
    pusharg %S32_453
    bsr __static_2_njSkip
    ret

.fun njDecodeSOF NORMAL [] = []
.reg S32 %S32_456
.reg S32 %S32_459
.reg S32 %S32_466
.reg S32 %S32_474
.reg S32 %S32_482
.reg S32 %S32_487
.reg S32 %S32_490
.reg S32 %S32_510
.reg S32 %S32_524
.reg S32 %S32_530
.reg S32 %S32_531
.reg S32 %S32_536
.reg S32 %S32_538
.reg S32 %S32_539
.reg S32 %S32_540
.reg S32 %S32_548
.reg S32 %S32_549
.reg S32 %S32_554
.reg S32 %S32_556
.reg S32 %S32_557
.reg S32 %S32_558
.reg S32 %S32_566
.reg S32 %S32_568
.reg S32 %S32_574
.reg S32 %S32_576
.reg S32 %S32_577
.reg S32 %S32_578
.reg S32 %S32_582
.reg S32 %S32_586
.reg S32 %S32_603
.reg S32 %S32_606
.reg S32 %S32_611
.reg S32 %S32_614
.reg S32 %S32_615
.reg S32 %S32_616
.reg S32 %S32_619
.reg S32 %S32_620
.reg S32 %S32_625
.reg S32 %S32_628
.reg S32 %S32_629
.reg S32 %S32_630
.reg S32 %S32_633
.reg S32 %S32_634
.reg S32 %S32_641
.reg S32 %S32_643
.reg S32 %S32_644
.reg S32 %S32_645
.reg S32 %S32_646
.reg S32 %S32_647
.reg S32 %S32_651
.reg S32 %S32_653
.reg S32 %S32_654
.reg S32 %S32_655
.reg S32 %S32_656
.reg S32 %S32_657
.reg S32 %S32_661
.reg S32 %S32_663
.reg S32 %S32_664
.reg S32 %S32_665
.reg S32 %S32_668
.reg S32 %S32_670
.reg S32 %S32_672
.reg S32 %S32_674
.reg S32 %S32_678
.reg S32 %S32_681
.reg S32 %S32_682
.reg S32 %S32_684
.reg S32 %S32_685
.reg S32 %S32_686
.reg S32 %S32_703
.reg S32 %S32_706
.reg S32 %S32_707
.reg S32 %S32_724
.reg S32 i
.reg S32 ssxmax
.reg S32 ssymax
.reg U8 $10_narrowed_U8
.reg U8 $11_narrowed_U8
.reg U8 $12_narrowed_U8
.reg U8 $1_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U8 $8_narrowed_U8
.reg U8 $9_narrowed_U8
.reg U16 $13_narrowed_U16
.reg U16 $14_narrowed_U16
.reg U32 %U16_473
.reg U32 %U16_481
.reg U32 %U32_498
.reg U32 %U32_504
.reg U32 %U32_511
.reg U32 %U32_514
.reg U32 %U32_515
.reg U32 %U32_591
.reg U32 %U32_594
.reg U32 %U32_597
.reg U32 %U32_694
.reg U32 %U32_697
.reg U32 %U32_700
.reg U32 %U32_708
.reg U32 %U32_711
.reg U32 %U32_712
.reg U32 %U8_465
.reg U32 %U8_497
.reg U32 %U8_523
.reg U32 %U8_529
.reg U32 %U8_547
.reg U32 %U8_565
.reg U64 %U64_687
.reg U64 %U64_713
.reg A64 %A64_464
.reg A64 %A64_471
.reg A64 %A64_472
.reg A64 %A64_479
.reg A64 %A64_480
.reg A64 %A64_495
.reg A64 %A64_522
.reg A64 %A64_527
.reg A64 %A64_545
.reg A64 %A64_563
.reg A64 %A64_688
.reg A64 %A64_714
.reg A64 %A64_719
.reg A64 c
.jtb switch_505_tab 4 while_5 [1 switch_505_end 3 switch_505_end]
.bbl %start  #  edge_out[while_1]  live_out[ssxmax  ssymax]
    mov ssxmax 0
    mov ssymax 0
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_17_true  while_1_exit]  live_out[ssxmax  ssymax]
    ld.mem %S32_456 nj 0
    beq %S32_456 0 while_1_exit
.bbl if_17_true
    ret
.bbl while_1_exit  #  edge_out[if_20_end  while_2]  live_out[ssxmax  ssymax]
    ld.mem %S32_459 nj 20
    ble 9:S32 %S32_459 if_20_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_20_end  #  edge_out[if_22_end  while_3]  live_out[ssxmax  ssymax]
    ld.mem %A64_464 nj 4
    ld $1_narrowed_U8 %A64_464 0
    conv %U8_465 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_465
    conv %S32_466 $2_narrowed_U8
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
    conv $13_narrowed_U16 %U16_473
    conv %S32_474 $13_narrowed_U16
    st.mem nj 28 %S32_474
    ld.mem %A64_479 nj 4
    lea %A64_480 %A64_479 3
    pusharg %A64_480
    bsr njDecode16
    poparg %U16_481
    conv $14_narrowed_U16 %U16_481
    conv %S32_482 $14_narrowed_U16
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
    ld $3_narrowed_U8 %A64_495 5
    conv %U8_497 $3_narrowed_U8
    conv $4_narrowed_U8 %U8_497
    conv %U32_498 $4_narrowed_U8
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
    lea.mem c nj 52
    bra for_15_cond
.bbl for_15  #  edge_out[if_29_end  while_7]  live_out[c  i  ssxmax  ssymax]
    ld.mem %A64_522 nj 4
    ld $5_narrowed_U8 %A64_522 0
    conv %U8_523 $5_narrowed_U8
    conv $6_narrowed_U8 %U8_523
    conv %S32_524 $6_narrowed_U8
    st c 0 %S32_524
    ld.mem %A64_527 nj 4
    ld $7_narrowed_U8 %A64_527 1
    conv %U8_529 $7_narrowed_U8
    conv $8_narrowed_U8 %U8_529
    conv %S32_530 $8_narrowed_U8
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
    ld $9_narrowed_U8 %A64_545 1
    conv %U8_547 $9_narrowed_U8
    conv $10_narrowed_U8 %U8_547
    conv %S32_548 $10_narrowed_U8
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
    ld $11_narrowed_U8 %A64_563 2
    conv %U8_565 $11_narrowed_U8
    conv $12_narrowed_U8 %U8_565
    conv %S32_566 $12_narrowed_U8
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
    ld ssxmax c 4
.bbl if_38_end  #  edge_out[for_15_next  if_39_true]  live_out[c  i  ssxmax  ssymax]
    ld %S32_586 c 8
    ble %S32_586 ssymax for_15_next
.bbl if_39_true  #  edge_out[for_15_next]  live_out[c  i  ssxmax  ssymax]
    ld ssymax c 8
.bbl for_15_next  #  edge_out[for_15_cond]  live_out[c  i  ssxmax  ssymax]
    add i i 1
    lea c c 48
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
    lea.mem c nj 52
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
    add i i 1
    lea c c 48
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
.reg S32 %S32_727
.reg S32 %S32_733
.reg S32 %S32_736
.reg S32 %S32_739
.reg S32 %S32_740
.reg S32 %S32_748
.reg S32 %S32_754
.reg S32 %S32_755
.reg S32 %S32_759
.reg S32 %S32_765
.reg S32 %S32_768
.reg S32 %S32_769
.reg S32 %S32_789
.reg S32 %S32_792
.reg S32 codelen
.reg S32 currcnt
.reg S32 i
.reg S32 j
.reg S32 remain
.reg S32 spread
.reg U8 $10_narrowed_U8
.reg U8 $1_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U8 $8_narrowed_U8
.reg U8 $9_narrowed_U8
.reg U32 %U8_731
.reg U32 %U8_746
.reg U32 %U8_761
.reg U32 %U8_778
.reg U32 code
.reg A64 %A64_730
.reg A64 %A64_744
.reg A64 %A64_753
.reg A64 %A64_775
.reg A64 vlc
.bbl %start  #  edge_out[while_1]
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_13_true  while_7_cond]
    ld.mem %S32_727 nj 0
    beq %S32_727 0 while_7_cond
.bbl if_13_true
    ret
.bbl while_7  #  edge_out[if_16_end  while_2]  live_out[i]
    ld.mem %A64_730 nj 4
    ld $1_narrowed_U8 %A64_730 0
    conv %U8_731 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_731
    conv i $2_narrowed_U8
    and %S32_733 i 236
    beq %S32_733 0 if_16_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_16_end  #  edge_out[if_18_end  while_3]  live_out[i]
    and %S32_736 i 2
    beq %S32_736 0 if_18_end
.bbl while_3
    st.mem nj 0 2:S32
    ret
.bbl if_18_end  #  edge_out[for_9_cond]  live_out[codelen  i]
    shr %S32_739 i 3
    or %S32_740 i %S32_739
    and i %S32_740 3
    mov codelen 1
    bra for_9_cond
.bbl for_9  #  edge_out[for_9_next]  live_out[codelen  i]
    ld.mem %A64_744 nj 4
    ld $3_narrowed_U8 %A64_744 codelen
    conv %U8_746 $3_narrowed_U8
    sub %S32_748 codelen 1
    conv $4_narrowed_U8 %U8_746
    st.mem __static_4_counts %S32_748 $4_narrowed_U8
.bbl for_9_next  #  edge_out[for_9_cond]  live_out[codelen  i]
    add codelen codelen 1
.bbl for_9_cond  #  edge_out[for_9  for_9_exit]  live_out[codelen  i]
    ble codelen 16 for_9
.bbl for_9_exit  #  edge_out[for_12_cond]  live_out[codelen  remain  spread  vlc]
    pusharg 17:S32
    bsr __static_2_njSkip
    lea.mem %A64_753 nj 464
    shl %S32_754 i 16
    shl %S32_755 %S32_754 1
    lea vlc %A64_753 %S32_755
    mov spread 65536
    mov remain 65536
    mov codelen 1
    bra for_12_cond
.bbl for_12  #  edge_out[for_12_next  if_20_end]  live_out[codelen  currcnt  remain  spread  vlc]
    shr spread spread 1
    sub %S32_759 codelen 1
    ld.mem $5_narrowed_U8 __static_4_counts %S32_759
    conv %U8_761 $5_narrowed_U8
    conv $6_narrowed_U8 %U8_761
    conv currcnt $6_narrowed_U8
    beq currcnt 0 for_12_next
.bbl if_20_end  #  edge_out[if_22_end  while_4]  live_out[codelen  currcnt  remain  spread  vlc]
    ld.mem %S32_765 nj 20
    ble currcnt %S32_765 if_22_end
.bbl while_4
    st.mem nj 0 5:S32
    ret
.bbl if_22_end  #  edge_out[if_24_end  while_5]  live_out[codelen  currcnt  remain  spread  vlc]
    sub %S32_768 16 codelen
    shl %S32_769 currcnt %S32_768
    sub remain remain %S32_769
    ble 0:S32 remain if_24_end
.bbl while_5
    st.mem nj 0 5:S32
    ret
.bbl if_24_end  #  edge_out[for_11_cond]  live_out[codelen  currcnt  i  remain  spread  vlc]
    mov i 0
    bra for_11_cond
.bbl for_11  #  edge_out[for_10_cond]  live_out[code  codelen  currcnt  i  j  remain  spread  vlc]
    ld.mem %A64_775 nj 4
    ld $7_narrowed_U8 %A64_775 i
    conv code $7_narrowed_U8
    mov j spread
    bra for_10_cond
.bbl for_10  #  edge_out[for_10_next]  live_out[code  codelen  currcnt  i  j  remain  spread  vlc]
    conv $8_narrowed_U8 codelen
    conv %U8_778 $8_narrowed_U8
    conv $9_narrowed_U8 %U8_778
    st vlc 0 $9_narrowed_U8
    conv $10_narrowed_U8 code
    st vlc 1 $10_narrowed_U8
    lea vlc vlc 2
.bbl for_10_next  #  edge_out[for_10_cond]  live_out[code  codelen  currcnt  i  j  remain  spread  vlc]
    sub j j 1
.bbl for_10_cond  #  edge_out[for_10  for_11_next]  live_out[code  codelen  currcnt  i  j  remain  spread  vlc]
    bne j 0 for_10
.bbl for_11_next  #  edge_out[for_11_cond]  live_out[codelen  currcnt  i  remain  spread  vlc]
    add i i 1
.bbl for_11_cond  #  edge_out[for_11  for_11_exit]  live_out[codelen  currcnt  i  remain  spread  vlc]
    blt i currcnt for_11
.bbl for_11_exit  #  edge_out[for_12_next]  live_out[codelen  remain  spread  vlc]
    pusharg currcnt
    bsr __static_2_njSkip
.bbl for_12_next  #  edge_out[for_12_cond]  live_out[codelen  remain  spread  vlc]
    add codelen codelen 1
.bbl for_12_cond  #  edge_out[for_12  for_12_condbra1]  live_out[codelen  remain  spread  vlc]
    ble codelen 16 for_12
.bbl for_12_condbra1  #  edge_out[while_6_cond]
    bra while_6_cond
.bbl while_6  #  edge_out[while_6_cond]  live_out[remain  vlc]
    sub remain remain 1
    st vlc 0 0:U8
    lea vlc vlc 2
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
.reg S32 %S32_797
.reg S32 %S32_803
.reg S32 %S32_808
.reg S32 %S32_809
.reg S32 %S32_810
.reg S32 %S32_815
.reg S32 %S32_820
.reg S32 %S32_828
.reg S32 %S32_831
.reg S32 i
.reg U8 $1_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U32 %U8_801
.reg U32 %U8_822
.reg A64 %A64_800
.reg A64 %A64_814
.reg A64 %A64_819
.reg A64 t
.bbl %start  #  edge_out[while_1]
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_6_true  while_3_cond]
    ld.mem %S32_797 nj 0
    beq %S32_797 0 while_3_cond
.bbl if_6_true
    ret
.bbl while_3  #  edge_out[if_9_end  while_2]  live_out[i]
    ld.mem %A64_800 nj 4
    ld $1_narrowed_U8 %A64_800 0
    conv %U8_801 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_801
    conv i $2_narrowed_U8
    and %S32_803 i 252
    beq %S32_803 0 if_9_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_9_end  #  edge_out[for_5_cond]  live_out[i  t]
    ld.mem %S32_808 nj 204
    shl %S32_809 1 i
    or %S32_810 %S32_808 %S32_809
    st.mem nj 204 %S32_810
    lea.mem %A64_814 nj 208
    shl %S32_815 i 6
    lea t %A64_814 %S32_815
    mov i 0
    bra for_5_cond
.bbl for_5  #  edge_out[for_5_next]  live_out[i  t]
    ld.mem %A64_819 nj 4
    add %S32_820 i 1
    ld $3_narrowed_U8 %A64_819 %S32_820
    conv %U8_822 $3_narrowed_U8
    conv $4_narrowed_U8 %U8_822
    st t i $4_narrowed_U8
.bbl for_5_next  #  edge_out[for_5_cond]  live_out[i  t]
    add i i 1
.bbl for_5_cond  #  edge_out[for_5  for_5_exit]  live_out[i  t]
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
.reg S32 %S32_836
.reg S32 %S32_839
.reg S32 %S32_846
.reg S32 %S32_851
.reg U16 $1_narrowed_U16
.reg U32 %U16_845
.reg A64 %A64_844
.bbl %start  #  edge_out[while_1]
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_3_true  while_1_exit]
    ld.mem %S32_836 nj 0
    beq %S32_836 0 while_1_exit
.bbl if_3_true
    ret
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
    conv $1_narrowed_U16 %U16_845
    conv %S32_846 $1_narrowed_U16
    st.mem nj 525016 %S32_846
    ld.mem %S32_851 nj 20
    pusharg %S32_851
    bsr __static_2_njSkip
    ret

.fun njGetVLC NORMAL [S32] = [A64 A64]
.reg S32 %S32_854
.reg S32 %S32_861
.reg S32 %S32_869
.reg S32 %S32_870
.reg S32 %S32_871
.reg S32 %S32_872
.reg S32 bits
.reg S32 value
.reg U8 $1_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U32 %U8_857
.reg U32 %U8_864
.reg U32 %U8_866
.reg A64 %A64_862
.reg A64 code
.reg A64 vlc
.bbl %start  #  edge_out[if_1_end  if_1_true]  live_out[bits  code  value  vlc]
    poparg vlc
    poparg code
    pusharg 16:S32
    bsr __static_1_njShowBits
    poparg value
    shl %S32_854 value 1
    ld $1_narrowed_U8 vlc %S32_854
    conv %U8_857 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_857
    conv bits $2_narrowed_U8
    bne bits 0 if_1_end
.bbl if_1_true
    st.mem nj 0 5:S32
    pusharg 0:S32
    ret
.bbl if_1_end  #  edge_out[if_2_end  if_2_true]  live_out[code  value]
    pusharg bits
    bsr njSkipBits
    shl %S32_861 value 1
    lea %A64_862 vlc %S32_861
    ld $3_narrowed_U8 %A64_862 1
    conv %U8_864 $3_narrowed_U8
    conv $4_narrowed_U8 %U8_864
    conv value $4_narrowed_U8
    beq code 0 if_2_end
.bbl if_2_true  #  edge_out[if_2_end]  live_out[value]
    conv $5_narrowed_U8 value
    conv %U8_866 $5_narrowed_U8
    conv $6_narrowed_U8 %U8_866
    st code 0 $6_narrowed_U8
.bbl if_2_end  #  edge_out[if_3_end  if_3_true]  live_out[bits]
    and bits value 15
    bne bits 0 if_3_end
.bbl if_3_true
    pusharg 0:S32
    ret
.bbl if_3_end  #  edge_out[if_4_end  if_4_true]  live_out[bits  value]
    pusharg bits
    bsr njGetBits
    poparg value
    sub %S32_869 bits 1
    shl %S32_870 1 %S32_869
    ble %S32_870 value if_4_end
.bbl if_4_true  #  edge_out[if_4_end]  live_out[value]
    shl %S32_871 -1 bits
    add %S32_872 %S32_871 1
    add value value %S32_872
.bbl if_4_end
    pusharg value
    ret

.fun njDecodeBlock NORMAL [] = [A64 A64]
.reg S8 $13_narrowed_S8
.reg S8 $14_narrowed_S8
.reg S32 %S32_883
.reg S32 %S32_887
.reg S32 %S32_888
.reg S32 %S32_889
.reg S32 %S32_891
.reg S32 %S32_893
.reg S32 %S32_896
.reg S32 %S32_900
.reg S32 %S32_901
.reg S32 %S32_904
.reg S32 %S32_905
.reg S32 %S32_911
.reg S32 %S32_912
.reg S32 %S32_913
.reg S32 %S32_919
.reg S32 %S32_922
.reg S32 %S32_923
.reg S32 %S32_926
.reg S32 %S32_931
.reg S32 %S32_932
.reg S32 %S32_933
.reg S32 %S32_940
.reg S32 %S32_941
.reg S32 %S32_942
.reg S32 %S32_945
.reg S32 %S32_946
.reg S32 %S32_952
.reg S32 %S32_953
.reg S32 %S32_957
.reg S32 %S32_962
.reg S32 %S32_966
.reg S32 %S8_951
.reg S32 coef
.reg S32 value
.reg U8 $10_narrowed_U8
.reg U8 $11_narrowed_U8
.reg U8 $12_narrowed_U8
.reg U8 $1_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U8 $8_narrowed_U8
.reg U8 $9_narrowed_U8
.reg U32 %U8_903
.reg U32 %U8_918
.reg U32 %U8_921
.reg U32 %U8_925
.reg U32 %U8_930
.reg U32 %U8_944
.reg A64 %A64_877
.reg A64 %A64_885
.reg A64 %A64_890
.reg A64 %A64_898
.reg A64 %A64_909
.reg A64 %A64_914
.reg A64 %A64_915
.reg A64 %A64_938
.reg A64 %A64_948
.reg A64 %A64_956
.reg A64 %A64_958
.reg A64 %A64_961
.reg A64 %A64_963
.reg A64 %A64_964
.reg A64 c
.reg A64 out
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
    ld $1_narrowed_U8 %A64_898 %S32_901
    conv %U8_903 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_903
    conv %S32_904 $2_narrowed_U8
    mul %S32_905 %S32_896 %S32_904
    st.mem nj 524760 %S32_905
.bbl while_3  #  edge_out[if_6_end  while_3_exit]  live_out[c  coef  out  value]
    lea.mem %A64_909 nj 464
    ld %S32_911 c 28
    shl %S32_912 %S32_911 16
    shl %S32_913 %S32_912 1
    lea %A64_914 %A64_909 %S32_913
    lea.stk %A64_915 code 0
    pusharg %A64_915
    pusharg %A64_914
    bsr njGetVLC
    poparg value
    ld.stk $3_narrowed_U8 code 0
    conv %U8_918 $3_narrowed_U8
    conv $4_narrowed_U8 %U8_918
    conv %S32_919 $4_narrowed_U8
    beq %S32_919 0 while_3_exit
.bbl if_6_end  #  edge_out[branch_14  if_8_end]  live_out[c  coef  out  value]
    ld.stk $5_narrowed_U8 code 0
    conv %U8_921 $5_narrowed_U8
    conv $6_narrowed_U8 %U8_921
    conv %S32_922 $6_narrowed_U8
    and %S32_923 %S32_922 15
    bne %S32_923 0 if_8_end
.bbl branch_14  #  edge_out[if_8_end  while_1]  live_out[c  coef  out  value]
    ld.stk $7_narrowed_U8 code 0
    conv %U8_925 $7_narrowed_U8
    conv $8_narrowed_U8 %U8_925
    conv %S32_926 $8_narrowed_U8
    beq %S32_926 240 if_8_end
.bbl while_1
    st.mem nj 0 5:S32
    ret
.bbl if_8_end  #  edge_out[if_10_end  while_2]  live_out[c  coef  out  value]
    ld.stk $9_narrowed_U8 code 0
    conv %U8_930 $9_narrowed_U8
    conv $10_narrowed_U8 %U8_930
    conv %S32_931 $10_narrowed_U8
    shr %S32_932 %S32_931 4
    add %S32_933 %S32_932 1
    add coef coef %S32_933
    ble coef 63 if_10_end
.bbl while_2
    st.mem nj 0 5:S32
    ret
.bbl if_10_end  #  edge_out[while_3_cond]  live_out[c  coef  out]
    lea.mem %A64_938 nj 208
    ld %S32_940 c 24
    shl %S32_941 %S32_940 6
    add %S32_942 coef %S32_941
    ld $11_narrowed_U8 %A64_938 %S32_942
    conv %U8_944 $11_narrowed_U8
    conv $12_narrowed_U8 %U8_944
    conv %S32_945 $12_narrowed_U8
    mul %S32_946 value %S32_945
    lea.mem %A64_948 nj 524760
    ld.mem $13_narrowed_S8 njZZ coef
    conv %S8_951 $13_narrowed_S8
    conv $14_narrowed_S8 %S8_951
    conv %S32_952 $14_narrowed_S8
    shl %S32_953 %S32_952 2
    st %A64_948 %S32_953 %S32_946
.bbl while_3_cond  #  edge_out[while_3  while_3_exit]  live_out[c  coef  out]
    blt coef 63 while_3
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
    add coef coef 8
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
    add coef coef 1
.bbl for_5_cond  #  edge_out[for_5  for_5_exit]  live_out[c  coef  out]
    blt coef 8 for_5
.bbl for_5_exit
    ret

.fun njDecodeScan NORMAL [] = []
.reg S32 %S32_1002
.reg S32 %S32_1004
.reg S32 %S32_1012
.reg S32 %S32_1013
.reg S32 %S32_1021
.reg S32 %S32_1022
.reg S32 %S32_1029
.reg S32 %S32_1030
.reg S32 %S32_1031
.reg S32 %S32_1044
.reg S32 %S32_1050
.reg S32 %S32_1056
.reg S32 %S32_1061
.reg S32 %S32_1067
.reg S32 %S32_1068
.reg S32 %S32_1069
.reg S32 %S32_1071
.reg S32 %S32_1072
.reg S32 %S32_1074
.reg S32 %S32_1075
.reg S32 %S32_1076
.reg S32 %S32_1077
.reg S32 %S32_1078
.reg S32 %S32_1082
.reg S32 %S32_1085
.reg S32 %S32_1088
.reg S32 %S32_1098
.reg S32 %S32_1102
.reg S32 %S32_1105
.reg S32 %S32_1109
.reg S32 %S32_1110
.reg S32 %S32_1113
.reg S32 %S32_1120
.reg S32 %S32_973
.reg S32 %S32_976
.reg S32 i
.reg S32 mbx
.reg S32 mby
.reg S32 nextrst
.reg S32 rstcount
.reg S32 sbx
.reg S32 sby
.reg U8 $10_narrowed_U8
.reg U8 $11_narrowed_U8
.reg U8 $12_narrowed_U8
.reg U8 $13_narrowed_U8
.reg U8 $14_narrowed_U8
.reg U8 $15_narrowed_U8
.reg U8 $16_narrowed_U8
.reg U8 $1_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U8 $8_narrowed_U8
.reg U8 $9_narrowed_U8
.reg U32 %U32_1036
.reg U32 %U32_1039
.reg U32 %U32_1091
.reg U32 %U32_1094
.reg U32 %U32_977
.reg U32 %U32_980
.reg U32 %U32_981
.reg U32 %U32_982
.reg U32 %U32_989
.reg U32 %U32_992
.reg U32 %U8_1001
.reg U32 %U8_1011
.reg U32 %U8_1020
.reg U32 %U8_1028
.reg U32 %U8_1043
.reg U32 %U8_1049
.reg U32 %U8_1055
.reg U32 %U8_988
.reg A64 %A64_1000
.reg A64 %A64_1009
.reg A64 %A64_1018
.reg A64 %A64_1026
.reg A64 %A64_1042
.reg A64 %A64_1047
.reg A64 %A64_1053
.reg A64 %A64_1065
.reg A64 %A64_1079
.reg A64 %A64_1119
.reg A64 %A64_1121
.reg A64 %A64_987
.reg A64 c
.bbl %start  #  edge_out[while_1]  live_out[nextrst  rstcount]
    ld.mem rstcount nj 525016
    mov nextrst 0
    bsr __static_3_njDecodeLength
.bbl while_1  #  edge_out[if_15_true  while_1_exit]  live_out[nextrst  rstcount]
    ld.mem %S32_973 nj 0
    beq %S32_973 0 while_1_exit
.bbl if_15_true
    ret
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
    ld $1_narrowed_U8 %A64_987 0
    conv %U8_988 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_988
    conv %U32_989 $2_narrowed_U8
    ld.mem %U32_992 nj 48
    beq %U32_989 %U32_992 if_20_end
.bbl while_3
    st.mem nj 0 2:S32
    ret
.bbl if_20_end  #  edge_out[for_9_cond]  live_out[c  i  nextrst  rstcount]
    pusharg 1:S32
    bsr __static_2_njSkip
    mov i 0
    lea.mem c nj 52
    bra for_9_cond
.bbl for_9  #  edge_out[if_22_end  while_4]  live_out[c  i  nextrst  rstcount]
    ld.mem %A64_1000 nj 4
    ld $3_narrowed_U8 %A64_1000 0
    conv %U8_1001 $3_narrowed_U8
    conv $4_narrowed_U8 %U8_1001
    conv %S32_1002 $4_narrowed_U8
    ld %S32_1004 c 0
    beq %S32_1002 %S32_1004 if_22_end
.bbl while_4
    st.mem nj 0 5:S32
    ret
.bbl if_22_end  #  edge_out[if_24_end  while_5]  live_out[c  i  nextrst  rstcount]
    ld.mem %A64_1009 nj 4
    ld $5_narrowed_U8 %A64_1009 1
    conv %U8_1011 $5_narrowed_U8
    conv $6_narrowed_U8 %U8_1011
    conv %S32_1012 $6_narrowed_U8
    and %S32_1013 %S32_1012 238
    beq %S32_1013 0 if_24_end
.bbl while_5
    st.mem nj 0 5:S32
    ret
.bbl if_24_end  #  edge_out[for_9_next]  live_out[c  i  nextrst  rstcount]
    ld.mem %A64_1018 nj 4
    ld $7_narrowed_U8 %A64_1018 1
    conv %U8_1020 $7_narrowed_U8
    conv $8_narrowed_U8 %U8_1020
    conv %S32_1021 $8_narrowed_U8
    shr %S32_1022 %S32_1021 4
    st c 32 %S32_1022
    ld.mem %A64_1026 nj 4
    ld $9_narrowed_U8 %A64_1026 1
    conv %U8_1028 $9_narrowed_U8
    conv $10_narrowed_U8 %U8_1028
    conv %S32_1029 $10_narrowed_U8
    and %S32_1030 %S32_1029 1
    or %S32_1031 %S32_1030 2
    st c 28 %S32_1031
    pusharg 2:S32
    bsr __static_2_njSkip
.bbl for_9_next  #  edge_out[for_9_cond]  live_out[c  i  nextrst  rstcount]
    add i i 1
    lea c c 48
.bbl for_9_cond  #  edge_out[for_9  for_9_exit]  live_out[c  i  nextrst  rstcount]
    conv %U32_1036 i
    ld.mem %U32_1039 nj 48
    blt %U32_1036 %U32_1039 for_9
.bbl for_9_exit  #  edge_out[branch_40  while_6]  live_out[nextrst  rstcount]
    ld.mem %A64_1042 nj 4
    ld $11_narrowed_U8 %A64_1042 0
    conv %U8_1043 $11_narrowed_U8
    conv $12_narrowed_U8 %U8_1043
    conv %S32_1044 $12_narrowed_U8
    bne %S32_1044 0 while_6
.bbl branch_40  #  edge_out[branch_39  while_6]  live_out[nextrst  rstcount]
    ld.mem %A64_1047 nj 4
    ld $13_narrowed_U8 %A64_1047 1
    conv %U8_1049 $13_narrowed_U8
    conv $14_narrowed_U8 %U8_1049
    conv %S32_1050 $14_narrowed_U8
    bne %S32_1050 63 while_6
.bbl branch_39  #  edge_out[if_27_end  while_6]  live_out[nextrst  rstcount]
    ld.mem %A64_1053 nj 4
    ld $15_narrowed_U8 %A64_1053 2
    conv %U8_1055 $15_narrowed_U8
    conv $16_narrowed_U8 %U8_1055
    conv %S32_1056 $16_narrowed_U8
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
    lea.mem c nj 52
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
.bbl while_7  #  edge_out[for_10_next  if_28_true]  live_out[c  i  mbx  mby  nextrst  rstcount  sbx  sby]
    ld.mem %S32_1082 nj 0
    beq %S32_1082 0 for_10_next
.bbl if_28_true
    ret
.bbl for_10_next  #  edge_out[for_10_cond]  live_out[c  i  mbx  mby  nextrst  rstcount  sbx  sby]
    add sbx sbx 1
.bbl for_10_cond  #  edge_out[for_10  for_11_next]  live_out[c  i  mbx  mby  nextrst  rstcount  sbx  sby]
    ld %S32_1085 c 4
    blt sbx %S32_1085 for_10
.bbl for_11_next  #  edge_out[for_11_cond]  live_out[c  i  mbx  mby  nextrst  rstcount  sby]
    add sby sby 1
.bbl for_11_cond  #  edge_out[for_11  for_12_next]  live_out[c  i  mbx  mby  nextrst  rstcount  sby]
    ld %S32_1088 c 8
    blt sby %S32_1088 for_11
.bbl for_12_next  #  edge_out[for_12_cond]  live_out[c  i  mbx  mby  nextrst  rstcount]
    add i i 1
    lea c c 48
.bbl for_12_cond  #  edge_out[for_12  for_12_exit]  live_out[c  i  mbx  mby  nextrst  rstcount]
    conv %U32_1091 i
    ld.mem %U32_1094 nj 48
    blt %U32_1091 %U32_1094 for_12
.bbl for_12_exit  #  edge_out[if_34_end  if_34_true]  live_out[mbx  mby  nextrst  rstcount]
    add mbx mbx 1
    ld.mem %S32_1098 nj 32
    blt mbx %S32_1098 if_34_end
.bbl if_34_true  #  edge_out[for_14_exit  if_34_end]  live_out[mbx  mby  nextrst  rstcount]
    mov mbx 0
    add mby mby 1
    ld.mem %S32_1102 nj 36
    ble %S32_1102 mby for_14_exit
.bbl if_34_end  #  edge_out[branch_41  for_14]  live_out[mbx  mby  nextrst  rstcount]
    ld.mem %S32_1105 nj 525016
    beq %S32_1105 0 for_14
.bbl branch_41  #  edge_out[for_14  if_38_true]  live_out[mbx  mby  nextrst  rstcount]
    sub rstcount rstcount 1
    bne rstcount 0 for_14
.bbl if_38_true  #  edge_out[branch_42  while_8]  live_out[i  mbx  mby  nextrst]
    bsr njByteAlign
    pusharg 16:S32
    bsr njGetBits
    poparg i
    and %S32_1109 i 65528
    bne %S32_1109 65488 while_8
.bbl branch_42  #  edge_out[if_36_end  while_8]  live_out[mbx  mby  nextrst]
    and %S32_1110 i 7
    beq %S32_1110 nextrst if_36_end
.bbl while_8
    st.mem nj 0 5:S32
    ret
.bbl if_36_end  #  edge_out[for_13_cond]  live_out[i  mbx  mby  nextrst  rstcount]
    add %S32_1113 nextrst 1
    and nextrst %S32_1113 7
    ld.mem rstcount nj 525016
    mov i 0
    bra for_13_cond
.bbl for_13  #  edge_out[for_13_next]  live_out[i  mbx  mby  nextrst  rstcount]
    lea.mem %A64_1119 nj 52
    mul %S32_1120 i 48
    lea %A64_1121 %A64_1119 %S32_1120
    st %A64_1121 36 0:S32
.bbl for_13_next  #  edge_out[for_13_cond]  live_out[i  mbx  mby  nextrst  rstcount]
    add i i 1
.bbl for_13_cond  #  edge_out[for_13  for_13_condbra1]  live_out[i  mbx  mby  nextrst  rstcount]
    blt i 3 for_13
.bbl for_13_condbra1  #  edge_out[for_14]
    bra for_14
.bbl for_14_exit
    st.mem nj 0 6:S32
    ret

.fun njUpsampleH NORMAL [] = [A64]
.reg S32 %S32_1128
.reg S32 %S32_1131
.reg S32 %S32_1133
.reg S32 %S32_1134
.reg S32 %S32_1135
.reg S32 %S32_1145
.reg S32 %S32_1146
.reg S32 %S32_1149
.reg S32 %S32_1150
.reg S32 %S32_1151
.reg S32 %S32_1152
.reg S32 %S32_1153
.reg S32 %S32_1156
.reg S32 %S32_1157
.reg S32 %S32_1160
.reg S32 %S32_1161
.reg S32 %S32_1162
.reg S32 %S32_1165
.reg S32 %S32_1166
.reg S32 %S32_1167
.reg S32 %S32_1168
.reg S32 %S32_1169
.reg S32 %S32_1173
.reg S32 %S32_1174
.reg S32 %S32_1177
.reg S32 %S32_1178
.reg S32 %S32_1179
.reg S32 %S32_1182
.reg S32 %S32_1183
.reg S32 %S32_1184
.reg S32 %S32_1185
.reg S32 %S32_1186
.reg S32 %S32_1191
.reg S32 %S32_1192
.reg S32 %S32_1193
.reg S32 %S32_1196
.reg S32 %S32_1197
.reg S32 %S32_1198
.reg S32 %S32_1199
.reg S32 %S32_1202
.reg S32 %S32_1203
.reg S32 %S32_1204
.reg S32 %S32_1205
.reg S32 %S32_1208
.reg S32 %S32_1209
.reg S32 %S32_1210
.reg S32 %S32_1211
.reg S32 %S32_1212
.reg S32 %S32_1214
.reg S32 %S32_1215
.reg S32 %S32_1219
.reg S32 %S32_1220
.reg S32 %S32_1221
.reg S32 %S32_1224
.reg S32 %S32_1225
.reg S32 %S32_1226
.reg S32 %S32_1227
.reg S32 %S32_1230
.reg S32 %S32_1231
.reg S32 %S32_1232
.reg S32 %S32_1233
.reg S32 %S32_1236
.reg S32 %S32_1237
.reg S32 %S32_1238
.reg S32 %S32_1239
.reg S32 %S32_1240
.reg S32 %S32_1242
.reg S32 %S32_1243
.reg S32 %S32_1247
.reg S32 %S32_1250
.reg S32 %S32_1251
.reg S32 %S32_1255
.reg S32 %S32_1256
.reg S32 %S32_1259
.reg S32 %S32_1260
.reg S32 %S32_1261
.reg S32 %S32_1264
.reg S32 %S32_1265
.reg S32 %S32_1266
.reg S32 %S32_1267
.reg S32 %S32_1268
.reg S32 %S32_1273
.reg S32 %S32_1274
.reg S32 %S32_1277
.reg S32 %S32_1278
.reg S32 %S32_1279
.reg S32 %S32_1282
.reg S32 %S32_1283
.reg S32 %S32_1284
.reg S32 %S32_1285
.reg S32 %S32_1286
.reg S32 %S32_1291
.reg S32 %S32_1292
.reg S32 %S32_1295
.reg S32 %S32_1296
.reg S32 %S32_1297
.reg S32 %S32_1298
.reg S32 %S32_1299
.reg S32 %S32_1304
.reg S32 %S32_1305
.reg S32 %S32_1308
.reg S32 x
.reg S32 xmax
.reg S32 y
.reg U8 $10_narrowed_U8
.reg U8 $11_narrowed_U8
.reg U8 $12_narrowed_U8
.reg U8 $13_narrowed_U8
.reg U8 $14_narrowed_U8
.reg U8 $15_narrowed_U8
.reg U8 $16_narrowed_U8
.reg U8 $17_narrowed_U8
.reg U8 $18_narrowed_U8
.reg U8 $19_narrowed_U8
.reg U8 $1_narrowed_U8
.reg U8 $20_narrowed_U8
.reg U8 $21_narrowed_U8
.reg U8 $22_narrowed_U8
.reg U8 $23_narrowed_U8
.reg U8 $24_narrowed_U8
.reg U8 $25_narrowed_U8
.reg U8 $26_narrowed_U8
.reg U8 $27_narrowed_U8
.reg U8 $28_narrowed_U8
.reg U8 $29_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $30_narrowed_U8
.reg U8 $31_narrowed_U8
.reg U8 $32_narrowed_U8
.reg U8 $33_narrowed_U8
.reg U8 $34_narrowed_U8
.reg U8 $35_narrowed_U8
.reg U8 $36_narrowed_U8
.reg U8 $37_narrowed_U8
.reg U8 $38_narrowed_U8
.reg U8 $39_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $40_narrowed_U8
.reg U8 $41_narrowed_U8
.reg U8 $42_narrowed_U8
.reg U8 $43_narrowed_U8
.reg U8 $44_narrowed_U8
.reg U8 $45_narrowed_U8
.reg U8 $46_narrowed_U8
.reg U8 $47_narrowed_U8
.reg U8 $48_narrowed_U8
.reg U8 $49_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $50_narrowed_U8
.reg U8 $51_narrowed_U8
.reg U8 $52_narrowed_U8
.reg U8 $53_narrowed_U8
.reg U8 $54_narrowed_U8
.reg U8 $55_narrowed_U8
.reg U8 $56_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U8 $8_narrowed_U8
.reg U8 $9_narrowed_U8
.reg U32 %U8_1144
.reg U32 %U8_1148
.reg U32 %U8_1154
.reg U32 %U8_1155
.reg U32 %U8_1159
.reg U32 %U8_1164
.reg U32 %U8_1170
.reg U32 %U8_1172
.reg U32 %U8_1176
.reg U32 %U8_1181
.reg U32 %U8_1187
.reg U32 %U8_1190
.reg U32 %U8_1195
.reg U32 %U8_1201
.reg U32 %U8_1207
.reg U32 %U8_1213
.reg U32 %U8_1218
.reg U32 %U8_1223
.reg U32 %U8_1229
.reg U32 %U8_1235
.reg U32 %U8_1241
.reg U32 %U8_1254
.reg U32 %U8_1258
.reg U32 %U8_1263
.reg U32 %U8_1269
.reg U32 %U8_1272
.reg U32 %U8_1276
.reg U32 %U8_1281
.reg U32 %U8_1287
.reg U32 %U8_1290
.reg U32 %U8_1294
.reg U32 %U8_1300
.reg U64 %U64_1136
.reg A64 %A64_1311
.reg A64 c
.reg A64 lin
.reg A64 lout
.reg A64 out
.bbl %start  #  edge_out[if_5_end  while_1]  live_out[c  out  xmax]
    poparg c
    ld %S32_1128 c 12
    sub xmax %S32_1128 3
    ld %S32_1131 c 12
    ld %S32_1133 c 16
    mul %S32_1134 %S32_1131 %S32_1133
    shl %S32_1135 %S32_1134 1
    conv %U64_1136 %S32_1135
    pusharg %U64_1136
    bsr malloc
    poparg out
    bne out 0 if_5_end
.bbl while_1
    st.mem nj 0 3:S32
    ret
.bbl if_5_end  #  edge_out[for_3_cond]  live_out[c  lin  lout  out  xmax  y]
    ld lin c 40
    mov lout out
    ld y c 16
    bra for_3_cond
.bbl for_3  #  edge_out[for_2_cond]  live_out[c  lin  lout  out  x  xmax  y]
    ld $1_narrowed_U8 lin 0
    conv %U8_1144 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_1144
    conv %S32_1145 $2_narrowed_U8
    mul %S32_1146 %S32_1145 139
    ld $3_narrowed_U8 lin 1
    conv %U8_1148 $3_narrowed_U8
    conv $4_narrowed_U8 %U8_1148
    conv %S32_1149 $4_narrowed_U8
    mul %S32_1150 %S32_1149 -11
    add %S32_1151 %S32_1146 %S32_1150
    add %S32_1152 %S32_1151 64
    shr %S32_1153 %S32_1152 7
    pusharg %S32_1153
    bsr njClip
    poparg %U8_1154
    conv $5_narrowed_U8 %U8_1154
    st lout 0 $5_narrowed_U8
    ld $6_narrowed_U8 lin 0
    conv %U8_1155 $6_narrowed_U8
    conv $7_narrowed_U8 %U8_1155
    conv %S32_1156 $7_narrowed_U8
    mul %S32_1157 %S32_1156 104
    ld $8_narrowed_U8 lin 1
    conv %U8_1159 $8_narrowed_U8
    conv $9_narrowed_U8 %U8_1159
    conv %S32_1160 $9_narrowed_U8
    mul %S32_1161 %S32_1160 27
    add %S32_1162 %S32_1157 %S32_1161
    ld $10_narrowed_U8 lin 2
    conv %U8_1164 $10_narrowed_U8
    conv $11_narrowed_U8 %U8_1164
    conv %S32_1165 $11_narrowed_U8
    mul %S32_1166 %S32_1165 -3
    add %S32_1167 %S32_1162 %S32_1166
    add %S32_1168 %S32_1167 64
    shr %S32_1169 %S32_1168 7
    pusharg %S32_1169
    bsr njClip
    poparg %U8_1170
    conv $12_narrowed_U8 %U8_1170
    st lout 1 $12_narrowed_U8
    ld $13_narrowed_U8 lin 0
    conv %U8_1172 $13_narrowed_U8
    conv $14_narrowed_U8 %U8_1172
    conv %S32_1173 $14_narrowed_U8
    mul %S32_1174 %S32_1173 28
    ld $15_narrowed_U8 lin 1
    conv %U8_1176 $15_narrowed_U8
    conv $16_narrowed_U8 %U8_1176
    conv %S32_1177 $16_narrowed_U8
    mul %S32_1178 %S32_1177 109
    add %S32_1179 %S32_1174 %S32_1178
    ld $17_narrowed_U8 lin 2
    conv %U8_1181 $17_narrowed_U8
    conv $18_narrowed_U8 %U8_1181
    conv %S32_1182 $18_narrowed_U8
    mul %S32_1183 %S32_1182 -9
    add %S32_1184 %S32_1179 %S32_1183
    add %S32_1185 %S32_1184 64
    shr %S32_1186 %S32_1185 7
    pusharg %S32_1186
    bsr njClip
    poparg %U8_1187
    conv $19_narrowed_U8 %U8_1187
    st lout 2 $19_narrowed_U8
    mov x 0
    bra for_2_cond
.bbl for_2  #  edge_out[for_2_next]  live_out[c  lin  lout  out  x  xmax  y]
    ld $20_narrowed_U8 lin x
    conv %U8_1190 $20_narrowed_U8
    conv $21_narrowed_U8 %U8_1190
    conv %S32_1191 $21_narrowed_U8
    mul %S32_1192 %S32_1191 -9
    add %S32_1193 x 1
    ld $22_narrowed_U8 lin %S32_1193
    conv %U8_1195 $22_narrowed_U8
    conv $23_narrowed_U8 %U8_1195
    conv %S32_1196 $23_narrowed_U8
    mul %S32_1197 %S32_1196 111
    add %S32_1198 %S32_1192 %S32_1197
    add %S32_1199 x 2
    ld $24_narrowed_U8 lin %S32_1199
    conv %U8_1201 $24_narrowed_U8
    conv $25_narrowed_U8 %U8_1201
    conv %S32_1202 $25_narrowed_U8
    mul %S32_1203 %S32_1202 29
    add %S32_1204 %S32_1198 %S32_1203
    add %S32_1205 x 3
    ld $26_narrowed_U8 lin %S32_1205
    conv %U8_1207 $26_narrowed_U8
    conv $27_narrowed_U8 %U8_1207
    conv %S32_1208 $27_narrowed_U8
    mul %S32_1209 %S32_1208 -3
    add %S32_1210 %S32_1204 %S32_1209
    add %S32_1211 %S32_1210 64
    shr %S32_1212 %S32_1211 7
    pusharg %S32_1212
    bsr njClip
    poparg %U8_1213
    shl %S32_1214 x 1
    add %S32_1215 %S32_1214 3
    conv $28_narrowed_U8 %U8_1213
    st lout %S32_1215 $28_narrowed_U8
    ld $29_narrowed_U8 lin x
    conv %U8_1218 $29_narrowed_U8
    conv $30_narrowed_U8 %U8_1218
    conv %S32_1219 $30_narrowed_U8
    mul %S32_1220 %S32_1219 -3
    add %S32_1221 x 1
    ld $31_narrowed_U8 lin %S32_1221
    conv %U8_1223 $31_narrowed_U8
    conv $32_narrowed_U8 %U8_1223
    conv %S32_1224 $32_narrowed_U8
    mul %S32_1225 %S32_1224 29
    add %S32_1226 %S32_1220 %S32_1225
    add %S32_1227 x 2
    ld $33_narrowed_U8 lin %S32_1227
    conv %U8_1229 $33_narrowed_U8
    conv $34_narrowed_U8 %U8_1229
    conv %S32_1230 $34_narrowed_U8
    mul %S32_1231 %S32_1230 111
    add %S32_1232 %S32_1226 %S32_1231
    add %S32_1233 x 3
    ld $35_narrowed_U8 lin %S32_1233
    conv %U8_1235 $35_narrowed_U8
    conv $36_narrowed_U8 %U8_1235
    conv %S32_1236 $36_narrowed_U8
    mul %S32_1237 %S32_1236 -9
    add %S32_1238 %S32_1232 %S32_1237
    add %S32_1239 %S32_1238 64
    shr %S32_1240 %S32_1239 7
    pusharg %S32_1240
    bsr njClip
    poparg %U8_1241
    shl %S32_1242 x 1
    add %S32_1243 %S32_1242 4
    conv $37_narrowed_U8 %U8_1241
    st lout %S32_1243 $37_narrowed_U8
.bbl for_2_next  #  edge_out[for_2_cond]  live_out[c  lin  lout  out  x  xmax  y]
    add x x 1
.bbl for_2_cond  #  edge_out[for_2  for_2_exit]  live_out[c  lin  lout  out  x  xmax  y]
    blt x xmax for_2
.bbl for_2_exit  #  edge_out[for_3_next]  live_out[c  lin  lout  out  xmax  y]
    ld %S32_1247 c 20
    lea lin lin %S32_1247
    ld %S32_1250 c 12
    shl %S32_1251 %S32_1250 1
    lea lout lout %S32_1251
    ld $38_narrowed_U8 lin -1
    conv %U8_1254 $38_narrowed_U8
    conv $39_narrowed_U8 %U8_1254
    conv %S32_1255 $39_narrowed_U8
    mul %S32_1256 %S32_1255 28
    ld $40_narrowed_U8 lin -2
    conv %U8_1258 $40_narrowed_U8
    conv $41_narrowed_U8 %U8_1258
    conv %S32_1259 $41_narrowed_U8
    mul %S32_1260 %S32_1259 109
    add %S32_1261 %S32_1256 %S32_1260
    ld $42_narrowed_U8 lin -3
    conv %U8_1263 $42_narrowed_U8
    conv $43_narrowed_U8 %U8_1263
    conv %S32_1264 $43_narrowed_U8
    mul %S32_1265 %S32_1264 -9
    add %S32_1266 %S32_1261 %S32_1265
    add %S32_1267 %S32_1266 64
    shr %S32_1268 %S32_1267 7
    pusharg %S32_1268
    bsr njClip
    poparg %U8_1269
    conv $44_narrowed_U8 %U8_1269
    st lout -3 $44_narrowed_U8
    ld $45_narrowed_U8 lin -1
    conv %U8_1272 $45_narrowed_U8
    conv $46_narrowed_U8 %U8_1272
    conv %S32_1273 $46_narrowed_U8
    mul %S32_1274 %S32_1273 104
    ld $47_narrowed_U8 lin -2
    conv %U8_1276 $47_narrowed_U8
    conv $48_narrowed_U8 %U8_1276
    conv %S32_1277 $48_narrowed_U8
    mul %S32_1278 %S32_1277 27
    add %S32_1279 %S32_1274 %S32_1278
    ld $49_narrowed_U8 lin -3
    conv %U8_1281 $49_narrowed_U8
    conv $50_narrowed_U8 %U8_1281
    conv %S32_1282 $50_narrowed_U8
    mul %S32_1283 %S32_1282 -3
    add %S32_1284 %S32_1279 %S32_1283
    add %S32_1285 %S32_1284 64
    shr %S32_1286 %S32_1285 7
    pusharg %S32_1286
    bsr njClip
    poparg %U8_1287
    conv $51_narrowed_U8 %U8_1287
    st lout -2 $51_narrowed_U8
    ld $52_narrowed_U8 lin -1
    conv %U8_1290 $52_narrowed_U8
    conv $53_narrowed_U8 %U8_1290
    conv %S32_1291 $53_narrowed_U8
    mul %S32_1292 %S32_1291 139
    ld $54_narrowed_U8 lin -2
    conv %U8_1294 $54_narrowed_U8
    conv $55_narrowed_U8 %U8_1294
    conv %S32_1295 $55_narrowed_U8
    mul %S32_1296 %S32_1295 -11
    add %S32_1297 %S32_1292 %S32_1296
    add %S32_1298 %S32_1297 64
    shr %S32_1299 %S32_1298 7
    pusharg %S32_1299
    bsr njClip
    poparg %U8_1300
    conv $56_narrowed_U8 %U8_1300
    st lout -1 $56_narrowed_U8
.bbl for_3_next  #  edge_out[for_3_cond]  live_out[c  lin  lout  out  xmax  y]
    sub y y 1
.bbl for_3_cond  #  edge_out[for_3  for_3_exit]  live_out[c  lin  lout  out  xmax  y]
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
    st c 40 out
    ret

.fun njUpsampleV NORMAL [] = [A64]
.reg S32 %S32_1319
.reg S32 %S32_1321
.reg S32 %S32_1322
.reg S32 %S32_1323
.reg S32 %S32_1333
.reg S32 %S32_1334
.reg S32 %S32_1337
.reg S32 %S32_1338
.reg S32 %S32_1339
.reg S32 %S32_1340
.reg S32 %S32_1341
.reg S32 %S32_1345
.reg S32 %S32_1346
.reg S32 %S32_1349
.reg S32 %S32_1350
.reg S32 %S32_1351
.reg S32 %S32_1354
.reg S32 %S32_1355
.reg S32 %S32_1356
.reg S32 %S32_1357
.reg S32 %S32_1358
.reg S32 %S32_1362
.reg S32 %S32_1363
.reg S32 %S32_1366
.reg S32 %S32_1367
.reg S32 %S32_1368
.reg S32 %S32_1371
.reg S32 %S32_1372
.reg S32 %S32_1373
.reg S32 %S32_1374
.reg S32 %S32_1375
.reg S32 %S32_1380
.reg S32 %S32_1382
.reg S32 %S32_1385
.reg S32 %S32_1386
.reg S32 %S32_1388
.reg S32 %S32_1389
.reg S32 %S32_1390
.reg S32 %S32_1393
.reg S32 %S32_1394
.reg S32 %S32_1395
.reg S32 %S32_1398
.reg S32 %S32_1399
.reg S32 %S32_1400
.reg S32 %S32_1401
.reg S32 %S32_1402
.reg S32 %S32_1405
.reg S32 %S32_1408
.reg S32 %S32_1409
.reg S32 %S32_1411
.reg S32 %S32_1412
.reg S32 %S32_1413
.reg S32 %S32_1416
.reg S32 %S32_1417
.reg S32 %S32_1418
.reg S32 %S32_1421
.reg S32 %S32_1422
.reg S32 %S32_1423
.reg S32 %S32_1424
.reg S32 %S32_1425
.reg S32 %S32_1432
.reg S32 %S32_1433
.reg S32 %S32_1434
.reg S32 %S32_1437
.reg S32 %S32_1438
.reg S32 %S32_1439
.reg S32 %S32_1440
.reg S32 %S32_1443
.reg S32 %S32_1444
.reg S32 %S32_1445
.reg S32 %S32_1446
.reg S32 %S32_1447
.reg S32 %S32_1451
.reg S32 %S32_1452
.reg S32 %S32_1453
.reg S32 %S32_1456
.reg S32 %S32_1457
.reg S32 %S32_1458
.reg S32 %S32_1459
.reg S32 %S32_1462
.reg S32 %S32_1463
.reg S32 %S32_1464
.reg S32 %S32_1465
.reg S32 %S32_1466
.reg S32 %S32_1470
.reg S32 %S32_1471
.reg S32 %S32_1472
.reg S32 %S32_1475
.reg S32 %S32_1476
.reg S32 %S32_1477
.reg S32 %S32_1478
.reg S32 %S32_1479
.reg S32 %S32_1483
.reg S32 %S32_1484
.reg S32 %S32_1487
.reg S32 s1
.reg S32 s2
.reg S32 w
.reg S32 x
.reg S32 y
.reg U8 $10_narrowed_U8
.reg U8 $11_narrowed_U8
.reg U8 $12_narrowed_U8
.reg U8 $13_narrowed_U8
.reg U8 $14_narrowed_U8
.reg U8 $15_narrowed_U8
.reg U8 $16_narrowed_U8
.reg U8 $17_narrowed_U8
.reg U8 $18_narrowed_U8
.reg U8 $19_narrowed_U8
.reg U8 $1_narrowed_U8
.reg U8 $20_narrowed_U8
.reg U8 $21_narrowed_U8
.reg U8 $22_narrowed_U8
.reg U8 $23_narrowed_U8
.reg U8 $24_narrowed_U8
.reg U8 $25_narrowed_U8
.reg U8 $26_narrowed_U8
.reg U8 $27_narrowed_U8
.reg U8 $28_narrowed_U8
.reg U8 $29_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $30_narrowed_U8
.reg U8 $31_narrowed_U8
.reg U8 $32_narrowed_U8
.reg U8 $33_narrowed_U8
.reg U8 $34_narrowed_U8
.reg U8 $35_narrowed_U8
.reg U8 $36_narrowed_U8
.reg U8 $37_narrowed_U8
.reg U8 $38_narrowed_U8
.reg U8 $39_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $40_narrowed_U8
.reg U8 $41_narrowed_U8
.reg U8 $42_narrowed_U8
.reg U8 $43_narrowed_U8
.reg U8 $44_narrowed_U8
.reg U8 $45_narrowed_U8
.reg U8 $46_narrowed_U8
.reg U8 $47_narrowed_U8
.reg U8 $48_narrowed_U8
.reg U8 $49_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $50_narrowed_U8
.reg U8 $51_narrowed_U8
.reg U8 $52_narrowed_U8
.reg U8 $53_narrowed_U8
.reg U8 $54_narrowed_U8
.reg U8 $55_narrowed_U8
.reg U8 $56_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U8 $8_narrowed_U8
.reg U8 $9_narrowed_U8
.reg U32 %U8_1332
.reg U32 %U8_1336
.reg U32 %U8_1342
.reg U32 %U8_1344
.reg U32 %U8_1348
.reg U32 %U8_1353
.reg U32 %U8_1359
.reg U32 %U8_1361
.reg U32 %U8_1365
.reg U32 %U8_1370
.reg U32 %U8_1376
.reg U32 %U8_1384
.reg U32 %U8_1387
.reg U32 %U8_1392
.reg U32 %U8_1397
.reg U32 %U8_1403
.reg U32 %U8_1407
.reg U32 %U8_1410
.reg U32 %U8_1415
.reg U32 %U8_1420
.reg U32 %U8_1426
.reg U32 %U8_1431
.reg U32 %U8_1436
.reg U32 %U8_1442
.reg U32 %U8_1448
.reg U32 %U8_1450
.reg U32 %U8_1455
.reg U32 %U8_1461
.reg U32 %U8_1467
.reg U32 %U8_1469
.reg U32 %U8_1474
.reg U32 %U8_1480
.reg U64 %U64_1324
.reg A64 %A64_1329
.reg A64 %A64_1490
.reg A64 c
.reg A64 cin
.reg A64 cout
.reg A64 out
.bbl %start  #  edge_out[if_5_end  while_1]  live_out[c  out  s1  s2  w]
    poparg c
    ld w c 12
    ld s1 c 20
    add s2 s1 s1
    ld %S32_1319 c 12
    ld %S32_1321 c 16
    mul %S32_1322 %S32_1319 %S32_1321
    shl %S32_1323 %S32_1322 1
    conv %U64_1324 %S32_1323
    pusharg %U64_1324
    bsr malloc
    poparg out
    bne out 0 if_5_end
.bbl while_1
    st.mem nj 0 3:S32
    ret
.bbl if_5_end  #  edge_out[for_3_cond]  live_out[c  out  s1  s2  w  x]
    mov x 0
    bra for_3_cond
.bbl for_3  #  edge_out[for_2_cond]  live_out[c  cin  cout  out  s1  s2  w  x  y]
    ld %A64_1329 c 40
    lea cin %A64_1329 x
    lea cout out x
    ld $1_narrowed_U8 %A64_1329 x
    conv %U8_1332 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_1332
    conv %S32_1333 $2_narrowed_U8
    mul %S32_1334 %S32_1333 139
    ld $3_narrowed_U8 cin s1
    conv %U8_1336 $3_narrowed_U8
    conv $4_narrowed_U8 %U8_1336
    conv %S32_1337 $4_narrowed_U8
    mul %S32_1338 %S32_1337 -11
    add %S32_1339 %S32_1334 %S32_1338
    add %S32_1340 %S32_1339 64
    shr %S32_1341 %S32_1340 7
    pusharg %S32_1341
    bsr njClip
    poparg %U8_1342
    conv $5_narrowed_U8 %U8_1342
    st out x $5_narrowed_U8
    lea cout cout w
    ld $6_narrowed_U8 %A64_1329 x
    conv %U8_1344 $6_narrowed_U8
    conv $7_narrowed_U8 %U8_1344
    conv %S32_1345 $7_narrowed_U8
    mul %S32_1346 %S32_1345 104
    ld $8_narrowed_U8 cin s1
    conv %U8_1348 $8_narrowed_U8
    conv $9_narrowed_U8 %U8_1348
    conv %S32_1349 $9_narrowed_U8
    mul %S32_1350 %S32_1349 27
    add %S32_1351 %S32_1346 %S32_1350
    ld $10_narrowed_U8 cin s2
    conv %U8_1353 $10_narrowed_U8
    conv $11_narrowed_U8 %U8_1353
    conv %S32_1354 $11_narrowed_U8
    mul %S32_1355 %S32_1354 -3
    add %S32_1356 %S32_1351 %S32_1355
    add %S32_1357 %S32_1356 64
    shr %S32_1358 %S32_1357 7
    pusharg %S32_1358
    bsr njClip
    poparg %U8_1359
    conv $12_narrowed_U8 %U8_1359
    st cout 0 $12_narrowed_U8
    lea cout cout w
    ld $13_narrowed_U8 %A64_1329 x
    conv %U8_1361 $13_narrowed_U8
    conv $14_narrowed_U8 %U8_1361
    conv %S32_1362 $14_narrowed_U8
    mul %S32_1363 %S32_1362 28
    ld $15_narrowed_U8 cin s1
    conv %U8_1365 $15_narrowed_U8
    conv $16_narrowed_U8 %U8_1365
    conv %S32_1366 $16_narrowed_U8
    mul %S32_1367 %S32_1366 109
    add %S32_1368 %S32_1363 %S32_1367
    ld $17_narrowed_U8 cin s2
    conv %U8_1370 $17_narrowed_U8
    conv $18_narrowed_U8 %U8_1370
    conv %S32_1371 $18_narrowed_U8
    mul %S32_1372 %S32_1371 -9
    add %S32_1373 %S32_1368 %S32_1372
    add %S32_1374 %S32_1373 64
    shr %S32_1375 %S32_1374 7
    pusharg %S32_1375
    bsr njClip
    poparg %U8_1376
    conv $19_narrowed_U8 %U8_1376
    st cout 0 $19_narrowed_U8
    lea cout cout w
    lea cin cin s1
    ld %S32_1380 c 16
    sub y %S32_1380 3
    bra for_2_cond
.bbl for_2  #  edge_out[for_2_next]  live_out[c  cin  cout  out  s1  s2  w  x  y]
    sub %S32_1382 0 s1
    ld $20_narrowed_U8 cin %S32_1382
    conv %U8_1384 $20_narrowed_U8
    conv $21_narrowed_U8 %U8_1384
    conv %S32_1385 $21_narrowed_U8
    mul %S32_1386 %S32_1385 -9
    ld $22_narrowed_U8 cin 0
    conv %U8_1387 $22_narrowed_U8
    conv $23_narrowed_U8 %U8_1387
    conv %S32_1388 $23_narrowed_U8
    mul %S32_1389 %S32_1388 111
    add %S32_1390 %S32_1386 %S32_1389
    ld $24_narrowed_U8 cin s1
    conv %U8_1392 $24_narrowed_U8
    conv $25_narrowed_U8 %U8_1392
    conv %S32_1393 $25_narrowed_U8
    mul %S32_1394 %S32_1393 29
    add %S32_1395 %S32_1390 %S32_1394
    ld $26_narrowed_U8 cin s2
    conv %U8_1397 $26_narrowed_U8
    conv $27_narrowed_U8 %U8_1397
    conv %S32_1398 $27_narrowed_U8
    mul %S32_1399 %S32_1398 -3
    add %S32_1400 %S32_1395 %S32_1399
    add %S32_1401 %S32_1400 64
    shr %S32_1402 %S32_1401 7
    pusharg %S32_1402
    bsr njClip
    poparg %U8_1403
    conv $28_narrowed_U8 %U8_1403
    st cout 0 $28_narrowed_U8
    lea cout cout w
    sub %S32_1405 0 s1
    ld $29_narrowed_U8 cin %S32_1405
    conv %U8_1407 $29_narrowed_U8
    conv $30_narrowed_U8 %U8_1407
    conv %S32_1408 $30_narrowed_U8
    mul %S32_1409 %S32_1408 -3
    ld $31_narrowed_U8 cin 0
    conv %U8_1410 $31_narrowed_U8
    conv $32_narrowed_U8 %U8_1410
    conv %S32_1411 $32_narrowed_U8
    mul %S32_1412 %S32_1411 29
    add %S32_1413 %S32_1409 %S32_1412
    ld $33_narrowed_U8 cin s1
    conv %U8_1415 $33_narrowed_U8
    conv $34_narrowed_U8 %U8_1415
    conv %S32_1416 $34_narrowed_U8
    mul %S32_1417 %S32_1416 111
    add %S32_1418 %S32_1413 %S32_1417
    ld $35_narrowed_U8 cin s2
    conv %U8_1420 $35_narrowed_U8
    conv $36_narrowed_U8 %U8_1420
    conv %S32_1421 $36_narrowed_U8
    mul %S32_1422 %S32_1421 -9
    add %S32_1423 %S32_1418 %S32_1422
    add %S32_1424 %S32_1423 64
    shr %S32_1425 %S32_1424 7
    pusharg %S32_1425
    bsr njClip
    poparg %U8_1426
    conv $37_narrowed_U8 %U8_1426
    st cout 0 $37_narrowed_U8
    lea cout cout w
    lea cin cin s1
.bbl for_2_next  #  edge_out[for_2_cond]  live_out[c  cin  cout  out  s1  s2  w  x  y]
    sub y y 1
.bbl for_2_cond  #  edge_out[for_2  for_2_exit]  live_out[c  cin  cout  out  s1  s2  w  x  y]
    bne y 0 for_2
.bbl for_2_exit  #  edge_out[for_3_next]  live_out[c  out  s1  s2  w  x]
    lea cin cin s1
    ld $38_narrowed_U8 cin 0
    conv %U8_1431 $38_narrowed_U8
    conv $39_narrowed_U8 %U8_1431
    conv %S32_1432 $39_narrowed_U8
    mul %S32_1433 %S32_1432 28
    sub %S32_1434 0 s1
    ld $40_narrowed_U8 cin %S32_1434
    conv %U8_1436 $40_narrowed_U8
    conv $41_narrowed_U8 %U8_1436
    conv %S32_1437 $41_narrowed_U8
    mul %S32_1438 %S32_1437 109
    add %S32_1439 %S32_1433 %S32_1438
    sub %S32_1440 0 s2
    ld $42_narrowed_U8 cin %S32_1440
    conv %U8_1442 $42_narrowed_U8
    conv $43_narrowed_U8 %U8_1442
    conv %S32_1443 $43_narrowed_U8
    mul %S32_1444 %S32_1443 -9
    add %S32_1445 %S32_1439 %S32_1444
    add %S32_1446 %S32_1445 64
    shr %S32_1447 %S32_1446 7
    pusharg %S32_1447
    bsr njClip
    poparg %U8_1448
    conv $44_narrowed_U8 %U8_1448
    st cout 0 $44_narrowed_U8
    lea cout cout w
    ld $45_narrowed_U8 cin 0
    conv %U8_1450 $45_narrowed_U8
    conv $46_narrowed_U8 %U8_1450
    conv %S32_1451 $46_narrowed_U8
    mul %S32_1452 %S32_1451 104
    sub %S32_1453 0 s1
    ld $47_narrowed_U8 cin %S32_1453
    conv %U8_1455 $47_narrowed_U8
    conv $48_narrowed_U8 %U8_1455
    conv %S32_1456 $48_narrowed_U8
    mul %S32_1457 %S32_1456 27
    add %S32_1458 %S32_1452 %S32_1457
    sub %S32_1459 0 s2
    ld $49_narrowed_U8 cin %S32_1459
    conv %U8_1461 $49_narrowed_U8
    conv $50_narrowed_U8 %U8_1461
    conv %S32_1462 $50_narrowed_U8
    mul %S32_1463 %S32_1462 -3
    add %S32_1464 %S32_1458 %S32_1463
    add %S32_1465 %S32_1464 64
    shr %S32_1466 %S32_1465 7
    pusharg %S32_1466
    bsr njClip
    poparg %U8_1467
    conv $51_narrowed_U8 %U8_1467
    st cout 0 $51_narrowed_U8
    lea cout cout w
    ld $52_narrowed_U8 cin 0
    conv %U8_1469 $52_narrowed_U8
    conv $53_narrowed_U8 %U8_1469
    conv %S32_1470 $53_narrowed_U8
    mul %S32_1471 %S32_1470 139
    sub %S32_1472 0 s1
    ld $54_narrowed_U8 cin %S32_1472
    conv %U8_1474 $54_narrowed_U8
    conv $55_narrowed_U8 %U8_1474
    conv %S32_1475 $55_narrowed_U8
    mul %S32_1476 %S32_1475 -11
    add %S32_1477 %S32_1471 %S32_1476
    add %S32_1478 %S32_1477 64
    shr %S32_1479 %S32_1478 7
    pusharg %S32_1479
    bsr njClip
    poparg %U8_1480
    conv $56_narrowed_U8 %U8_1480
    st cout 0 $56_narrowed_U8
.bbl for_3_next  #  edge_out[for_3_cond]  live_out[c  out  s1  s2  w  x]
    add x x 1
.bbl for_3_cond  #  edge_out[for_3  for_3_exit]  live_out[c  out  s1  s2  w  x]
    blt x w for_3
.bbl for_3_exit
    ld %S32_1483 c 16
    shl %S32_1484 %S32_1483 1
    st c 16 %S32_1484
    ld %S32_1487 c 12
    st c 20 %S32_1487
    ld %A64_1490 c 40
    pusharg %A64_1490
    bsr free
    st c 40 out
    ret

.fun njConvert NORMAL [] = []
.reg S32 %S32_1495
.reg S32 %S32_1498
.reg S32 %S32_1501
.reg S32 %S32_1503
.reg S32 %S32_1506
.reg S32 %S32_1509
.reg S32 %S32_1511
.reg S32 %S32_1514
.reg S32 %S32_1516
.reg S32 %S32_1519
.reg S32 %S32_1521
.reg S32 %S32_1524
.reg S32 %S32_1526
.reg S32 %S32_1529
.reg S32 %S32_1563
.reg S32 %S32_1567
.reg S32 %S32_1571
.reg S32 %S32_1573
.reg S32 %S32_1574
.reg S32 %S32_1575
.reg S32 %S32_1576
.reg S32 %S32_1578
.reg S32 %S32_1579
.reg S32 %S32_1580
.reg S32 %S32_1581
.reg S32 %S32_1582
.reg S32 %S32_1583
.reg S32 %S32_1586
.reg S32 %S32_1587
.reg S32 %S32_1588
.reg S32 %S32_1589
.reg S32 %S32_1596
.reg S32 %S32_1600
.reg S32 %S32_1606
.reg S32 %S32_1612
.reg S32 %S32_1618
.reg S32 %S32_1622
.reg S32 %S32_1630
.reg S32 %S32_1639
.reg S32 %S32_1644
.reg S32 %S32_1649
.reg S32 %S32_1654
.reg S32 %S32_1659
.reg S32 %S32_1665
.reg S32 __local_26_y
.reg S32 cb
.reg S32 cr
.reg S32 i
.reg S32 x
.reg S32 y
.reg S32 yy
.reg U8 $1_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U8 $8_narrowed_U8
.reg U8 $9_narrowed_U8
.reg U32 %U32_1534
.reg U32 %U32_1537
.reg U32 %U32_1540
.reg U32 %U8_1562
.reg U32 %U8_1566
.reg U32 %U8_1570
.reg U32 %U8_1577
.reg U32 %U8_1584
.reg U32 %U8_1590
.reg U64 %U64_1650
.reg A64 %A64_1626
.reg A64 %A64_1635
.reg A64 c
.reg A64 pcb
.reg A64 pcr
.reg A64 pin
.reg A64 pout
.reg A64 prgb
.reg A64 py
.bbl %start  #  edge_out[for_5_cond]  live_out[c  i]
    mov i 0
    lea.mem c nj 52
    bra for_5_cond
.bbl while_3  #  edge_out[if_9_true  while_1]  live_out[c  i]
    ld %S32_1495 c 12
    ld.mem %S32_1498 nj 24
    ble %S32_1498 %S32_1495 while_1
.bbl if_9_true  #  edge_out[while_1]  live_out[c  i]
    pusharg c
    bsr njUpsampleH
.bbl while_1  #  edge_out[if_10_true  while_1_exit]  live_out[c  i]
    ld.mem %S32_1501 nj 0
    beq %S32_1501 0 while_1_exit
.bbl if_10_true
    ret
.bbl while_1_exit  #  edge_out[if_12_true  while_2]  live_out[c  i]
    ld %S32_1503 c 16
    ld.mem %S32_1506 nj 28
    ble %S32_1506 %S32_1503 while_2
.bbl if_12_true  #  edge_out[while_2]  live_out[c  i]
    pusharg c
    bsr njUpsampleV
.bbl while_2  #  edge_out[if_13_true  while_3_cond]  live_out[c  i]
    ld.mem %S32_1509 nj 0
    beq %S32_1509 0 while_3_cond
.bbl if_13_true
    ret
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
    add i i 1
    lea c c 48
.bbl for_5_cond  #  edge_out[for_5_exit  while_3_cond]  live_out[c  i]
    conv %U32_1534 i
    ld.mem %U32_1537 nj 48
    blt %U32_1534 %U32_1537 while_3_cond
.bbl for_5_exit  #  edge_out[if_23_false  if_23_true]
    ld.mem %U32_1540 nj 48
    bne %U32_1540 3 if_23_false
.bbl if_23_true  #  edge_out[for_7_cond]  live_out[pcb  pcr  prgb  py  yy]
    ld.mem prgb nj 525020
    ld.mem py nj 92
    ld.mem pcb nj 140
    ld.mem pcr nj 188
    ld.mem yy nj 28
    bra for_7_cond
.bbl for_7  #  edge_out[for_6_cond]  live_out[pcb  pcr  prgb  py  x  yy]
    mov x 0
    bra for_6_cond
.bbl for_6  #  edge_out[for_6_next]  live_out[pcb  pcr  prgb  py  x  yy]
    ld $1_narrowed_U8 py x
    conv %U8_1562 $1_narrowed_U8
    conv $2_narrowed_U8 %U8_1562
    conv %S32_1563 $2_narrowed_U8
    shl y %S32_1563 8
    ld $3_narrowed_U8 pcb x
    conv %U8_1566 $3_narrowed_U8
    conv $4_narrowed_U8 %U8_1566
    conv %S32_1567 $4_narrowed_U8
    sub cb %S32_1567 128
    ld $5_narrowed_U8 pcr x
    conv %U8_1570 $5_narrowed_U8
    conv $6_narrowed_U8 %U8_1570
    conv %S32_1571 $6_narrowed_U8
    sub cr %S32_1571 128
    mul %S32_1573 cr 359
    add %S32_1574 y %S32_1573
    add %S32_1575 %S32_1574 128
    shr %S32_1576 %S32_1575 8
    pusharg %S32_1576
    bsr njClip
    poparg %U8_1577
    conv $7_narrowed_U8 %U8_1577
    st prgb 0 $7_narrowed_U8
    mul %S32_1578 cb 88
    sub %S32_1579 y %S32_1578
    mul %S32_1580 cr 183
    sub %S32_1581 %S32_1579 %S32_1580
    add %S32_1582 %S32_1581 128
    shr %S32_1583 %S32_1582 8
    pusharg %S32_1583
    bsr njClip
    poparg %U8_1584
    conv $8_narrowed_U8 %U8_1584
    st prgb 1 $8_narrowed_U8
    mul %S32_1586 cb 454
    add %S32_1587 y %S32_1586
    add %S32_1588 %S32_1587 128
    shr %S32_1589 %S32_1588 8
    pusharg %S32_1589
    bsr njClip
    poparg %U8_1590
    conv $9_narrowed_U8 %U8_1590
    st prgb 2 $9_narrowed_U8
    lea prgb prgb 3
.bbl for_6_next  #  edge_out[for_6_cond]  live_out[pcb  pcr  prgb  py  x  yy]
    add x x 1
.bbl for_6_cond  #  edge_out[for_6  for_6_exit]  live_out[pcb  pcr  prgb  py  x  yy]
    ld.mem %S32_1596 nj 24
    blt x %S32_1596 for_6
.bbl for_6_exit  #  edge_out[for_7_next]  live_out[pcb  pcr  prgb  py  yy]
    ld.mem %S32_1600 nj 72
    lea py py %S32_1600
    ld.mem %S32_1606 nj 120
    lea pcb pcb %S32_1606
    ld.mem %S32_1612 nj 168
    lea pcr pcr %S32_1612
.bbl for_7_next  #  edge_out[for_7_cond]  live_out[pcb  pcr  prgb  py  yy]
    sub yy yy 1
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
    lea pin %A64_1626 %S32_1630
    ld.mem %A64_1635 nj 92
    ld.mem %S32_1639 nj 64
    lea pout %A64_1635 %S32_1639
    ld.mem %S32_1644 nj 68
    sub __local_26_y %S32_1644 1
    bra for_8_cond
.bbl for_8  #  edge_out[for_8_next]  live_out[__local_26_y  pin  pout]
    ld.mem %S32_1649 nj 64
    conv %U64_1650 %S32_1649
    pusharg %U64_1650
    pusharg pin
    pusharg pout
    bsr mymemcpy
    ld.mem %S32_1654 nj 72
    lea pin pin %S32_1654
    ld.mem %S32_1659 nj 64
    lea pout pout %S32_1659
.bbl for_8_next  #  edge_out[for_8_cond]  live_out[__local_26_y  pin  pout]
    sub __local_26_y __local_26_y 1
.bbl for_8_cond  #  edge_out[for_8  for_8_exit]  live_out[__local_26_y  pin  pout]
    bne __local_26_y 0 for_8
.bbl for_8_exit  #  edge_out[if_23_end]
    ld.mem %S32_1665 nj 64
    st.mem nj 72 %S32_1665
.bbl if_23_end
    ret

.fun njInit NORMAL [] = []
.reg A64 %A64_1669
.bbl %start
    lea.mem %A64_1669 nj 0
    pusharg 525032:U64
    pusharg 0:S32
    pusharg %A64_1669
    bsr mymemset
    ret

.fun njDone NORMAL [] = []
.reg S32 %S32_1674
.reg S32 %S32_1680
.reg S32 i
.reg A64 %A64_1673
.reg A64 %A64_1675
.reg A64 %A64_1677
.reg A64 %A64_1679
.reg A64 %A64_1681
.reg A64 %A64_1683
.reg A64 %A64_1687
.reg A64 %A64_1690
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
    add i i 1
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
.reg S32 $1_%out
.reg S32 %S32_1693
.reg S32 %S32_1698
.reg S32 %S32_1703
.reg S32 %S32_1704
.reg S32 %S32_1710
.reg S32 %S32_1711
.reg S32 %S32_1712
.reg S32 %S32_1716
.reg S32 %S32_1721
.reg S32 %S32_1734
.reg S32 %S32_1735
.reg S32 %S32_1738
.reg S32 %S32_1741
.reg S32 %out
.reg S32 size
.reg U8 $10_narrowed_U8
.reg U8 $11_narrowed_U8
.reg U8 $2_narrowed_U8
.reg U8 $3_narrowed_U8
.reg U8 $4_narrowed_U8
.reg U8 $5_narrowed_U8
.reg U8 $6_narrowed_U8
.reg U8 $7_narrowed_U8
.reg U8 $8_narrowed_U8
.reg U8 $9_narrowed_U8
.reg U32 %U8_1702
.reg U32 %U8_1709
.reg U32 %U8_1720
.reg U32 %U8_1727
.reg U32 %U8_1733
.reg A64 %A64_1701
.reg A64 %A64_1707
.reg A64 %A64_1719
.reg A64 %A64_1725
.reg A64 %A64_1731
.reg A64 jpeg
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
    ld $2_narrowed_U8 %A64_1701 0
    conv %U8_1702 $2_narrowed_U8
    conv $3_narrowed_U8 %U8_1702
    conv %S32_1703 $3_narrowed_U8
    xor %S32_1704 %S32_1703 255
    ld.mem %A64_1707 nj 4
    ld $4_narrowed_U8 %A64_1707 1
    conv %U8_1709 $4_narrowed_U8
    conv $5_narrowed_U8 %U8_1709
    conv %S32_1710 $5_narrowed_U8
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
    ld $6_narrowed_U8 %A64_1719 0
    conv %U8_1720 $6_narrowed_U8
    conv $7_narrowed_U8 %U8_1720
    conv %S32_1721 $7_narrowed_U8
    beq %S32_1721 255 if_4_end
.bbl if_4_true
    pusharg 5:S32
    ret
.bbl if_4_end  #  edge_out[if_4_end_1  switch_1728_default]  live_out[%U8_1727]
    pusharg 2:S32
    bsr __static_2_njSkip
    ld.mem %A64_1725 nj 4
    ld $8_narrowed_U8 %A64_1725 -1
    conv %U8_1727 $8_narrowed_U8
    conv $9_narrowed_U8 %U8_1727
    conv %U8_1727 $9_narrowed_U8
    blt 254:U32 %U8_1727 switch_1728_default
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
    ld $10_narrowed_U8 %A64_1731 -1
    conv %U8_1733 $10_narrowed_U8
    conv $11_narrowed_U8 %U8_1733
    conv %S32_1734 $11_narrowed_U8
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
    ld.mem %out nj 0
    pusharg %out
    ret
.bbl if_7_end
    st.mem nj 0 0:S32
    bsr njConvert
    ld.mem $1_%out nj 0
    pusharg $1_%out
    ret

.fun write_str NORMAL [] = [A64 S32]
.reg S8 $1_narrowed_S8
.reg S8 $2_narrowed_S8
.reg S32 %S32_1753
.reg S32 %S8_1752
.reg S32 fd
.reg S64 %S64_1754
.reg U64 size
.reg A64 s
.bbl %start  #  edge_out[for_1_cond]  live_out[fd  s  size]
    poparg s
    poparg fd
    mov size 0
    bra for_1_cond
.bbl for_1_next  #  edge_out[for_1_cond]  live_out[fd  s  size]
    add size size 1
.bbl for_1_cond  #  edge_out[for_1_exit  for_1_next]  live_out[fd  s  size]
    ld $1_narrowed_S8 s size
    conv %S8_1752 $1_narrowed_S8
    conv $2_narrowed_S8 %S8_1752
    conv %S32_1753 $2_narrowed_S8
    bne %S32_1753 0 for_1_next
.bbl for_1_exit
    pusharg size
    pusharg s
    pusharg fd
    bsr write
    poparg %S64_1754
    ret

.fun write_dec NORMAL [] = [S32 S32]
.reg S8 $1_narrowed_S8
.reg S8 $2_narrowed_S8
.reg S32 %S32_1759
.reg S32 %S32_1760
.reg S32 %S32_1767
.reg S32 %S8_1761
.reg S32 a
.reg S32 fd
.reg S32 i
.reg A64 %A64_1768
.stk buf 1 64
.bbl %start  #  edge_out[while_1]  live_out[a  fd  i]
    poparg fd
    poparg a
    st.stk buf 63 0:S8
    mov i 62
.bbl while_1  #  edge_out[while_1_cond]  live_out[a  fd  i]
    rem %S32_1759 a 10
    add %S32_1760 %S32_1759 48
    conv $1_narrowed_S8 %S32_1760
    conv %S8_1761 $1_narrowed_S8
    conv $2_narrowed_S8 %S8_1761
    st.stk buf i $2_narrowed_S8
    sub i i 1
    div a a 10
.bbl while_1_cond  #  edge_out[while_1  while_1_exit]  live_out[a  fd  i]
    bne a 0 while_1
.bbl while_1_exit
    add %S32_1767 i 1
    lea.stk %A64_1768 buf %S32_1767
    pusharg fd
    pusharg %A64_1768
    bsr write_str
    ret

.fun main NORMAL [S32] = [S32 A64]
.reg S32 $1_size
.reg S32 %S32_1788
.reg S32 %S32_1789
.reg S32 %S32_1794
.reg S32 %S32_1796
.reg S32 %S32_1799
.reg S32 %S32_1802
.reg S32 %S32_1804
.reg S32 %S32_1808
.reg S32 %S32_1811
.reg S32 argc
.reg S32 fd
.reg S32 size
.reg S64 %S64_1776
.reg S64 %S64_1782
.reg S64 %S64_1786
.reg S64 %S64_1810
.reg U64 %U64_1780
.reg U64 %U64_1785
.reg U64 %U64_1809
.reg A64 %A64_1769
.reg A64 %A64_1771
.reg A64 %A64_1775
.reg A64 %A64_1790
.reg A64 %A64_1792
.reg A64 %A64_1798
.reg A64 %A64_1800
.reg A64 %A64_1801
.reg A64 %A64_1803
.reg A64 %A64_1805
.reg A64 %A64_1806
.reg A64 %A64_1807
.reg A64 argv
.reg A64 buf
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
.bbl if_1_end  #  edge_out[if_2_end  if_2_true]  live_out[argv  fd]
    ld %A64_1771 argv 8
    pusharg 0:S32
    pusharg 0:S32
    pusharg %A64_1771
    bsr open
    poparg fd
    ble 0:S32 fd if_2_end
.bbl if_2_true
    lea.mem %A64_1775 string_const_2 0
    pusharg %A64_1775
    bsr print_s_ln
    pusharg 1:S32
    ret
.bbl if_2_end  #  edge_out[if_3_end  if_3_true]  live_out[argv  buf]
    pusharg 2:S32
    pusharg 0:S64
    pusharg fd
    bsr lseek
    poparg %S64_1776
    conv size %S64_1776
    conv %U64_1780 size
    pusharg %U64_1780
    bsr malloc
    poparg buf
    pusharg 0:S32
    pusharg 0:S64
    pusharg fd
    bsr lseek
    poparg %S64_1782
    conv %U64_1785 size
    pusharg %U64_1785
    pusharg buf
    pusharg fd
    bsr read
    poparg %S64_1786
    conv $1_size %S64_1786
    pusharg fd
    bsr close
    poparg %S32_1788
    bsr njInit
    pusharg $1_size
    pusharg buf
    bsr njDecode
    poparg %S32_1789
    beq %S32_1789 0 if_3_end
.bbl if_3_true
    pusharg buf
    bsr free
    lea.mem %A64_1790 string_const_3 0
    pusharg %A64_1790
    bsr print_s_ln
    pusharg 1:S32
    ret
.bbl if_3_end  #  edge_out[if_4_end  if_4_true]  live_out[fd]
    pusharg buf
    bsr free
    ld %A64_1792 argv 16
    mov %S32_1794 577
    mov %S32_1796 384
    pusharg %S32_1796
    pusharg %S32_1794
    pusharg %A64_1792
    bsr open
    poparg fd
    ble 0:S32 fd if_4_end
.bbl if_4_true
    lea.mem %A64_1798 string_const_4 0
    pusharg %A64_1798
    bsr print_s_ln
    pusharg 1:S32
    ret
.bbl if_4_end  #  edge_out[if_5_false  if_5_true]  live_out[fd]
    bsr njIsColor
    poparg %S32_1799
    beq %S32_1799 0 if_5_false
.bbl if_5_true  #  edge_out[if_5_end]  live_out[fd]
    lea.mem %A64_1800 string_const_5 0
    pusharg fd
    pusharg %A64_1800
    bsr write_str
    bra if_5_end
.bbl if_5_false  #  edge_out[if_5_end]  live_out[fd]
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
    pusharg 0:S32
    ret
