############################################################
# std_lib.c
############################################################

.mem __static_2__malloc_end 4 RW
.data 4 [0]

.mem __static_1__malloc_start 4 RW
.data 4 [0]


.fun write_s NORMAL [S32] = [S32 A32]

.bbl %start
  poparg fd:S32
  poparg s:A32
  mov len:U32 = 0
  bra while_1_cond

.bbl while_1
  add %U32_1:U32 = len 1
  mov len = %U32_1

.bbl while_1_cond
  lea %A32_2:A32 = s len
  ld %S8_3:S8 = %A32_2 0
  conv %S32_4:S32 = %S8_3
  bne %S32_4 0 while_1
  bra while_1_exit

.bbl while_1_exit
  pusharg len
  pusharg s
  pusharg fd
  bsr write
  poparg %S32_5:S32
  mov %out:S32 = %S32_5
  pusharg %out
  ret


.fun write_x NORMAL [S32] = [S32 U32]

.bbl %start
  poparg fd:S32
  poparg val:U32
.stk buffer 1 16
  lea %A32_1:A32 = buffer
  mov pos:U32 = 16

.bbl while_1
  sub %U32_2:U32 = pos 1
  mov pos = %U32_2
  rem %U32_3:U32 = val 16
  mov digit:U32 = %U32_3
  ble digit 9 if_2_true
  bra if_2_false

.bbl if_2_true
  add %U32_4:U32 = 48:U32 digit
  conv %S8_5:S8 = %U32_4
  lea %A32_6:A32 = buffer
  lea %A32_7:A32 = %A32_6 pos
  st %A32_7 0 = %S8_5
  bra if_2_end

.bbl if_2_false
  sub %S32_8:S32 = 97:S32 10
  conv %U32_9:U32 = %S32_8
  add %U32_10:U32 = %U32_9 digit
  conv %S8_11:S8 = %U32_10
  lea %A32_12:A32 = buffer
  lea %A32_13:A32 = %A32_12 pos
  st %A32_13 0 = %S8_11

.bbl if_2_end
  div %U32_14:U32 = val 16
  mov val = %U32_14

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_15:A32 = buffer
  lea %A32_16:A32 = %A32_15 pos
  lea %A32_17:A32 = buffer
  sub %U32_18:U32 = 16:U32 pos
  pusharg %U32_18
  pusharg %A32_16
  pusharg fd
  bsr write
  poparg %S32_19:S32
  mov %out:S32 = %S32_19
  pusharg %out
  ret


.fun write_u NORMAL [S32] = [S32 U32]

.bbl %start
  poparg fd:S32
  poparg val:U32
.stk buffer 1 16
  lea %A32_1:A32 = buffer
  mov pos:U32 = 16

.bbl while_1
  sub %U32_2:U32 = pos 1
  mov pos = %U32_2
  rem %U32_3:U32 = val 10
  add %U32_4:U32 = 48:U32 %U32_3
  conv %S8_5:S8 = %U32_4
  lea %A32_6:A32 = buffer
  lea %A32_7:A32 = %A32_6 pos
  st %A32_7 0 = %S8_5
  div %U32_8:U32 = val 10
  mov val = %U32_8

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_9:A32 = buffer
  lea %A32_10:A32 = %A32_9 pos
  lea %A32_11:A32 = buffer
  sub %U32_12:U32 = 16:U32 pos
  pusharg %U32_12
  pusharg %A32_10
  pusharg fd
  bsr write
  poparg %S32_13:S32
  mov %out:S32 = %S32_13
  pusharg %out
  ret


.fun write_d NORMAL [S32] = [S32 S32]

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
  poparg %S32_2:S32
  mov %out:S32 = %S32_2
  pusharg %out
  ret

.bbl if_2_end
  sub %S32_3:S32 = 0  sval
  conv %U32_4:U32 = %S32_3
  mov val:U32 = %U32_4
.stk buffer 1 16
  lea %A32_5:A32 = buffer
  mov pos:U32 = 16

.bbl while_1
  sub %U32_6:U32 = pos 1
  mov pos = %U32_6
  rem %U32_7:U32 = val 10
  add %U32_8:U32 = 48:U32 %U32_7
  conv %S8_9:S8 = %U32_8
  lea %A32_10:A32 = buffer
  lea %A32_11:A32 = %A32_10 pos
  st %A32_11 0 = %S8_9
  div %U32_12:U32 = val 10
  mov val = %U32_12

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  sub %U32_13:U32 = pos 1
  mov pos = %U32_13
  lea %A32_14:A32 = buffer
  lea %A32_15:A32 = %A32_14 pos
  mov %S8_16:S8 = 45
  st %A32_15 0 = %S8_16
  lea %A32_17:A32 = buffer
  lea %A32_18:A32 = %A32_17 pos
  lea %A32_19:A32 = buffer
  sub %U32_20:U32 = 16:U32 pos
  pusharg %U32_20
  pusharg %A32_18
  pusharg fd
  bsr write
  poparg %S32_21:S32
  mov %out = %S32_21
  pusharg %out
  ret


.fun write_c NORMAL [S32] = [S32 U8]

.bbl %start
  poparg fd:S32
  poparg c:U8
.stk buffer 1 16
  conv %S8_1:S8 = c
  lea %A32_2:A32 = buffer
  st %A32_2 0 = %S8_1
  lea %A32_3:A32 = buffer
  mov %U32_5:U32 = 1
  pusharg %U32_5
  pusharg %A32_3
  pusharg fd
  bsr write
  poparg %S32_4:S32
  mov %out:S32 = %S32_4
  pusharg %out
  ret


.fun print_ln NORMAL [] = [A32 U32]

.bbl %start
  poparg s:A32
  poparg n:U32
  mov %S32_2:S32 = 1
  pusharg n
  pusharg s
  pusharg %S32_2
  bsr write
  poparg %S32_1:S32
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S32_3:S32
  ret


.fun print_s_ln NORMAL [] = [A32]

.bbl %start
  poparg s:A32
  mov %S32_2:S32 = 1
  pusharg s
  pusharg %S32_2
  bsr write_s
  poparg %S32_1:S32
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S32_3:S32
  ret


.fun print_d_ln NORMAL [] = [S32]

.bbl %start
  poparg n:S32
  mov %S32_2:S32 = 1
  pusharg n
  pusharg %S32_2
  bsr write_d
  poparg %S32_1:S32
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S32_3:S32
  ret


.fun print_u_ln NORMAL [] = [U32]

.bbl %start
  poparg n:U32
  mov %S32_2:S32 = 1
  pusharg n
  pusharg %S32_2
  bsr write_u
  poparg %S32_1:S32
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S32_3:S32
  ret


.fun print_x_ln NORMAL [] = [U32]

.bbl %start
  poparg n:U32
  mov %S32_2:S32 = 1
  pusharg n
  pusharg %S32_2
  bsr write_x
  poparg %S32_1:S32
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S32_3:S32
  ret

.fun print_x_x_ln NORMAL [] = [U32 U32]

.bbl %start
  poparg a:U32
  poparg b:U32

  pusharg a
  pusharg 1:S32
  bsr write_x
  poparg dummy:S32

  pusharg 32:U8
  pusharg 1:S32
  bsr write_c
  poparg dummy

  pusharg b
  pusharg 1:S32
  bsr write_x
  poparg dummy

  pusharg 10:U8
  pusharg 1:S32
  bsr write_c
  poparg dummy
  ret

.fun print_x_x_x_ln NORMAL [] = [U32 U32 U32]

.bbl %start
  poparg a:U32
  poparg b:U32
  poparg c:U32

  pusharg a
  pusharg 1:S32
  bsr write_x
  poparg dummy:S32

  pusharg 32:U8
  pusharg 1:S32
  bsr write_c
  poparg dummy

  pusharg b
  pusharg 1:S32
  bsr write_x
  poparg dummy

  pusharg 32:U8
  pusharg 1:S32
  bsr write_c
  poparg dummy

  pusharg c
  pusharg 1:S32
  bsr write_x
  poparg dummy

  pusharg 10:U8
  pusharg 1:S32
  bsr write_c
  poparg dummy
  ret

.fun print_c_ln NORMAL [] = [U8]

.bbl %start
  poparg c:U8
  mov %S32_2:S32 = 1
  pusharg c
  pusharg %S32_2
  bsr write_c
  poparg %S32_1:S32
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S32_3:S32
  ret


.fun memset NORMAL [A32] = [A32 S32 U32]

.bbl %start
  poparg ptr:A32
  poparg value:S32
  poparg n:U32
  mov i:U32 = 0
  bra for_1_cond

.bbl for_1
  conv %S8_1:S8 = value
  lea %A32_2:A32 = ptr i
  st %A32_2 0 = %S8_1

.bbl for_1_next
  add %U32_3:U32 = i 1
  mov i = %U32_3

.bbl for_1_cond
  blt i n for_1
  bra for_1_exit

.bbl for_1_exit
  mov %out:A32 = ptr
  pusharg %out
  ret


.fun memcpy NORMAL [A32] = [A32 A32 U32]

.bbl %start
  poparg dst:A32
  poparg src:A32
  poparg n:U32
  mov i:U32 = 0
  bra for_1_cond

.bbl for_1
  lea %A32_1:A32 = src i
  ld %S8_2:S8 = %A32_1 0
  lea %A32_3:A32 = dst i
  st %A32_3 0 = %S8_2

.bbl for_1_next
  add %U32_4:U32 = i 1
  mov i = %U32_4

.bbl for_1_cond
  blt i n for_1
  bra for_1_exit

.bbl for_1_exit
  mov %out:A32 = dst
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


.fun malloc NORMAL [A32] = [U32]

.bbl %start
  poparg size:U32
  shl %U32_1:U32 = 1:U32 20
  mov page_size:U32 = %U32_1
  lea %A32_2:A32 = __static_1__malloc_start
  ld %A32_3:A32 = %A32_2 0
  beq %A32_3 0 if_1_true
  bra if_1_end

.bbl if_1_true
  lea %A32_5:A32 = 0:A32
  pusharg %A32_5
  bsr xbrk
  poparg %A32_4:A32
  lea %A32_6:A32 = __static_1__malloc_start
  st %A32_6 0 = %A32_4
  lea %A32_7:A32 = __static_1__malloc_start
  ld %A32_8:A32 = %A32_7 0
  lea %A32_9:A32 = __static_2__malloc_end
  st %A32_9 0 = %A32_8

.bbl if_1_end
  add %U32_10:U32 = size 15
  div %U32_11:U32 = %U32_10 16
  mul %U32_12:U32 = %U32_11 16
  mov rounded_size:U32 = %U32_12
  lea %A32_13:A32 = __static_1__malloc_start
  ld %A32_14:A32 = %A32_13 0
  lea %A32_15:A32 = %A32_14 rounded_size
  lea %A32_16:A32 = __static_2__malloc_end
  ld %A32_17:A32 = %A32_16 0
  blt %A32_17 %A32_15 if_3_true
  bra if_3_end

.bbl if_3_true
  add %U32_18:U32 = rounded_size page_size
  sub %U32_19:U32 = %U32_18 1
  div %U32_20:U32 = %U32_19 page_size
  mul %U32_21:U32 = %U32_20 page_size
  mov increment:U32 = %U32_21
  lea %A32_22:A32 = __static_2__malloc_end
  ld %A32_23:A32 = %A32_22 0
  lea %A32_24:A32 = %A32_23 increment
  mov new_end:A32 = %A32_24
  pusharg new_end
  bsr xbrk
  poparg %A32_25:A32
  lea %A32_26:A32 = __static_2__malloc_end
  st %A32_26 0 = %A32_25
  lea %A32_27:A32 = __static_2__malloc_end
  ld %A32_28:A32 = %A32_27 0
  bne %A32_28 new_end if_2_true
  bra if_3_end

.bbl if_2_true
  bsr abort

.bbl if_3_end
  lea %A32_29:A32 = __static_1__malloc_start
  ld %A32_30:A32 = %A32_29 0
  mov result:A32 = %A32_30
  lea %A32_31:A32 = __static_1__malloc_start
  ld %A32_32:A32 = %A32_31 0
  lea %A32_33:A32 = %A32_32 rounded_size
  lea %A32_34:A32 = __static_1__malloc_start
  st %A32_34 0 = %A32_33
  mov %out:A32 = result
  pusharg %out
  ret


.fun free NORMAL [] = [A32]

.bbl %start
  poparg ptr:A32
  ret
