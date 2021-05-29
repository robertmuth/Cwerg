############################################################
# std_lib.c
############################################################

.mem __static_2__malloc_end 8 RW
.data 8 [0]

.mem __static_1__malloc_start 8 RW
.data 8 [0]


.fun write_s NORMAL [S64] = [S32 A64]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg s:A64
  .reg U64 [len]
  mov len = 0
  bra while_1_cond

.bbl while_1
  add %U64_1:U64 = len 1
  mov len = %U64_1

.bbl while_1_cond
  lea %A64_2:A64 = s len
  ld %S8_3:S8 = %A64_2 0
  conv %S32_4:S32 = %S8_3
  bne %S32_4 0 while_1
  bra while_1_exit

.bbl while_1_exit
  pusharg len
  pusharg s
  pusharg fd
  bsr write
  poparg %S64_5:S64
  mov %out = %S64_5
  pusharg %out
  ret


.fun write_x NORMAL [S64] = [S32 U32]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg val:U32
.stk buffer 1 16
  .reg U64 [pos]
  lea %A64_1:A64 = buffer
  mov pos = 16

.bbl while_1
  sub %U64_2:U64 = pos 1
  mov pos = %U64_2
  .reg U32 [digit]
  rem %U32_3:U32 = val 16
  mov digit = %U32_3
  ble digit 9 if_2_true
  bra if_2_false

.bbl if_2_true
  add %U32_4:U32 = 48:U32 digit
  conv %S8_5:S8 = %U32_4
  lea %A64_6:A64 = buffer
  lea %A64_7:A64 = %A64_6 pos
  st %A64_7 0 = %S8_5
  bra if_2_end

.bbl if_2_false
  sub %S32_8:S32 = 97:S32 10
  conv %U32_9:U32 = %S32_8
  add %U32_10:U32 = %U32_9 digit
  conv %S8_11:S8 = %U32_10
  lea %A64_12:A64 = buffer
  lea %A64_13:A64 = %A64_12 pos
  st %A64_13 0 = %S8_11

.bbl if_2_end
  div %U32_14:U32 = val 16
  mov val = %U32_14

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A64_15:A64 = buffer
  lea %A64_16:A64 = %A64_15 pos
  lea %A64_17:A64 = buffer
  sub %U64_18:U64 = 16:U64 pos
  pusharg %U64_18
  pusharg %A64_16
  pusharg fd
  bsr write
  poparg %S64_19:S64
  mov %out = %S64_19
  pusharg %out
  ret


.fun write_u NORMAL [S64] = [S32 U32]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg val:U32
.stk buffer 1 16
  .reg U64 [pos]
  lea %A64_1:A64 = buffer
  mov pos = 16

.bbl while_1
  sub %U64_2:U64 = pos 1
  mov pos = %U64_2
  rem %U32_3:U32 = val 10
  add %U32_4:U32 = 48:U32 %U32_3
  conv %S8_5:S8 = %U32_4
  lea %A64_6:A64 = buffer
  lea %A64_7:A64 = %A64_6 pos
  st %A64_7 0 = %S8_5
  div %U32_8:U32 = val 10
  mov val = %U32_8

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A64_9:A64 = buffer
  lea %A64_10:A64 = %A64_9 pos
  lea %A64_11:A64 = buffer
  sub %U64_12:U64 = 16:U64 pos
  pusharg %U64_12
  pusharg %A64_10
  pusharg fd
  bsr write
  poparg %S64_13:S64
  mov %out = %S64_13
  pusharg %out
  ret


.fun write_d NORMAL [S64] = [S32 S32]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg sval:S32
  ble 0:S32 sval if_2_true
  bra if_2_end

.bbl if_2_true
  conv %U32_1:U32 = sval
  pusharg %U32_1
  pusharg fd
  bsr write_u
  poparg %S64_2:S64
  mov %out = %S64_2
  pusharg %out
  ret

.bbl if_2_end
  .reg U32 [val]
  sub %S32_3:S32 = 0  sval
  conv %U32_4:U32 = %S32_3
  mov val = %U32_4
.stk buffer 1 16
  .reg U64 [pos]
  lea %A64_5:A64 = buffer
  mov pos = 16

.bbl while_1
  sub %U64_6:U64 = pos 1
  mov pos = %U64_6
  rem %U32_7:U32 = val 10
  add %U32_8:U32 = 48:U32 %U32_7
  conv %S8_9:S8 = %U32_8
  lea %A64_10:A64 = buffer
  lea %A64_11:A64 = %A64_10 pos
  st %A64_11 0 = %S8_9
  div %U32_12:U32 = val 10
  mov val = %U32_12

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  sub %U64_13:U64 = pos 1
  mov pos = %U64_13
  lea %A64_14:A64 = buffer
  lea %A64_15:A64 = %A64_14 pos
  mov %S8_16:S8 = 45
  st %A64_15 0 = %S8_16
  lea %A64_17:A64 = buffer
  lea %A64_18:A64 = %A64_17 pos
  lea %A64_19:A64 = buffer
  sub %U64_20:U64 = 16:U64 pos
  pusharg %U64_20
  pusharg %A64_18
  pusharg fd
  bsr write
  poparg %S64_21:S64
  mov %out = %S64_21
  pusharg %out
  ret


.fun write_c NORMAL [S64] = [S32 U8]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg c:U8
.stk buffer 1 16
  conv %S8_1:S8 = c
  lea %A64_2:A64 = buffer
  st %A64_2 0 = %S8_1
  lea %A64_3:A64 = buffer
  mov %U64_5:U64 = 1
  pusharg %U64_5
  pusharg %A64_3
  pusharg fd
  bsr write
  poparg %S64_4:S64
  conv %S32_6:S32 = %S64_4
  conv %S64_7:S64 = %S32_6
  mov %out = %S64_7
  pusharg %out
  ret


.fun print_ln NORMAL [] = [A64 U64]

.bbl %start
  poparg s:A64
  poparg n:U64
  mov %S32_2:S32 = 1
  pusharg n
  pusharg s
  pusharg %S32_2
  bsr write
  poparg %S64_1:S64
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S64_3:S64
  ret


.fun print_s_ln NORMAL [] = [A64]

.bbl %start
  poparg s:A64
  mov %S32_2:S32 = 1
  pusharg s
  pusharg %S32_2
  bsr write_s
  poparg %S64_1:S64
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S64_3:S64
  ret


.fun print_d_ln NORMAL [] = [S32]

.bbl %start
  poparg n:S32
  mov %S32_2:S32 = 1
  pusharg n
  pusharg %S32_2
  bsr write_d
  poparg %S64_1:S64
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S64_3:S64
  ret


.fun print_u_ln NORMAL [] = [U32]

.bbl %start
  poparg n:U32
  mov %S32_2:S32 = 1
  pusharg n
  pusharg %S32_2
  bsr write_u
  poparg %S64_1:S64
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S64_3:S64
  ret


.fun print_x_ln NORMAL [] = [U32]

.bbl %start
  poparg n:U32
  mov %S32_2:S32 = 1
  pusharg n
  pusharg %S32_2
  bsr write_x
  poparg %S64_1:S64
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S64_3:S64
  ret


.fun print_c_ln NORMAL [] = [U8]

.bbl %start
  poparg c:U8
  mov %S32_2:S32 = 1
  pusharg c
  pusharg %S32_2
  bsr write_c
  poparg %S64_1:S64
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S64_3:S64
  ret


.fun memset NORMAL [A64] = [A64 S32 U64]
.reg A64 [%out]

.bbl %start
  poparg ptr:A64
  poparg value:S32
  poparg n:U64
  .reg U64 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  conv %S8_1:S8 = value
  lea %A64_2:A64 = ptr i
  st %A64_2 0 = %S8_1

.bbl for_1_next
  add %U64_3:U64 = i 1
  mov i = %U64_3

.bbl for_1_cond
  blt i n for_1
  bra for_1_exit

.bbl for_1_exit
  mov %out = ptr
  pusharg %out
  ret


.fun memcpy NORMAL [A64] = [A64 A64 U64]
.reg A64 [%out]

.bbl %start
  poparg dst:A64
  poparg src:A64
  poparg n:U64
  .reg U64 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  lea %A64_1:A64 = src i
  ld %S8_2:S8 = %A64_1 0
  lea %A64_3:A64 = dst i
  st %A64_3 0 = %S8_2

.bbl for_1_next
  add %U64_4:U64 = i 1
  mov i = %U64_4

.bbl for_1_cond
  blt i n for_1
  bra for_1_exit

.bbl for_1_exit
  mov %out = dst
  pusharg %out
  ret


.fun abort NORMAL [] = []

.bbl %start
  bsr getpid
  poparg %S32_1:S32
  mov %S32_3:S32 = 3
  pusharg %S32_3
  pusharg %S32_1
  bsr kill
  poparg %S32_2:S32
  mov %S32_4:S32 = 1
  pusharg %S32_4
  bsr exit
  ret


.fun malloc NORMAL [A64] = [U64]
.reg A64 [%out]

.bbl %start
  poparg size:U64
  .reg U64 [page_size]
  shl %U64_1:U64 = 1:U64 20
  mov page_size = %U64_1
  lea %A64_2:A64 = __static_1__malloc_start
  ld %A64_3:A64 = %A64_2 0
  beq %A64_3 0 if_1_true
  bra if_1_end

.bbl if_1_true
  lea %A64_5:A64 = 0:A64
  pusharg %A64_5
  bsr xbrk
  poparg %A64_4:A64
  lea %A64_6:A64 = __static_1__malloc_start
  st %A64_6 0 = %A64_4
  lea %A64_7:A64 = __static_1__malloc_start
  ld %A64_8:A64 = %A64_7 0
  lea %A64_9:A64 = __static_2__malloc_end
  st %A64_9 0 = %A64_8

.bbl if_1_end
  .reg U64 [rounded_size]
  add %U64_10:U64 = size 15
  div %U64_11:U64 = %U64_10 16
  mul %U64_12:U64 = %U64_11 16
  mov rounded_size = %U64_12
  lea %A64_13:A64 = __static_1__malloc_start
  ld %A64_14:A64 = %A64_13 0
  lea %A64_15:A64 = %A64_14 rounded_size
  lea %A64_16:A64 = __static_2__malloc_end
  ld %A64_17:A64 = %A64_16 0
  blt %A64_17 %A64_15 if_3_true
  bra if_3_end

.bbl if_3_true
  .reg U64 [increment]
  add %U64_18:U64 = rounded_size page_size
  sub %U64_19:U64 = %U64_18 1
  div %U64_20:U64 = %U64_19 page_size
  mul %U64_21:U64 = %U64_20 page_size
  mov increment = %U64_21
  .reg A64 [new_end]
  lea %A64_22:A64 = __static_2__malloc_end
  ld %A64_23:A64 = %A64_22 0
  lea %A64_24:A64 = %A64_23 increment
  mov new_end = %A64_24
  pusharg new_end
  bsr xbrk
  poparg %A64_25:A64
  lea %A64_26:A64 = __static_2__malloc_end
  st %A64_26 0 = %A64_25
  lea %A64_27:A64 = __static_2__malloc_end
  ld %A64_28:A64 = %A64_27 0
  bne %A64_28 new_end if_2_true
  bra if_3_end

.bbl if_2_true
  bsr abort

.bbl if_3_end
  .reg A64 [result]
  lea %A64_29:A64 = __static_1__malloc_start
  ld %A64_30:A64 = %A64_29 0
  mov result = %A64_30
  lea %A64_31:A64 = __static_1__malloc_start
  ld %A64_32:A64 = %A64_31 0
  lea %A64_33:A64 = %A64_32 rounded_size
  lea %A64_34:A64 = __static_1__malloc_start
  st %A64_34 0 = %A64_33
  mov %out = result
  pusharg %out
  ret


.fun free NORMAL [] = [A64]

.bbl %start
  poparg ptr:A64
  ret
