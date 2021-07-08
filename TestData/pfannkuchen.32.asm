############################################################
# FrontEndC/TestData/pfannkuchen.c
############################################################

.mem s 4 RW
.data 64 [0]

.mem t 4 RW
.data 64 [0]

.mem maxflips 4 RW
.data 1 [0 0 0 0]

.mem max_n 4 RW
.data 4 [0]

.mem odd 4 RW
.data 1 [0 0 0 0]

.mem checksum 4 RW
.data 1 [0 0 0 0]


.fun flip NORMAL [S32] = [A32 A32]
.reg S32 [%out]

.bbl %start
  poparg s:A32
  poparg t:A32
  .reg S32 [i]
  .reg A32 [x]
  .reg A32 [y]
  .reg S32 [c]
  mov x = t
  mov y = s
  lea %A32_1:A32 = max_n
  ld %S32_2:S32 = %A32_1 0
  mov i = %S32_2
  bra for_2_cond

.bbl for_2
  ld %S32_3:S32 = y 0
  st x 0 = %S32_3
  lea %A32_4:A32 = x 4
  mov x = %A32_4
  lea %A32_5:A32 = y 4
  mov y = %A32_5

.bbl for_2_next
  sub %S32_6:S32 = i 1
  mov i = %S32_6

.bbl for_2_cond
  blt 0:S32 i for_2
  bra for_2_exit

.bbl for_2_exit
  mov i = 1

.bbl while_1
  mov x = t
  ld %S32_7:S32 = t 0
  mul %S32_8:S32 = %S32_7 4
  lea %A32_9:A32 = t %S32_8
  mov y = %A32_9
  bra for_3_cond

.bbl for_3
  ld %S32_10:S32 = x 0
  mov c = %S32_10
  ld %S32_11:S32 = y 0
  st x 0 = %S32_11
  lea %A32_12:A32 = x 4
  mov x = %A32_12
  st y 0 = c
  lea %A32_13:A32 = y -4
  mov y = %A32_13

.bbl for_3_cond
  blt x y for_3
  bra for_3_exit

.bbl for_3_exit
  add %S32_14:S32 = i 1
  mov i = %S32_14

.bbl while_1_cond
  ld %S32_15:S32 = t 0
  mul %S32_16:S32 = %S32_15 4
  lea %A32_17:A32 = t %S32_16
  ld %S32_18:S32 = %A32_17 0
  bne %S32_18 0 while_1
  bra while_1_exit

.bbl while_1_exit
  mov %out = i
  pusharg %out
  ret


.fun rotate NORMAL [] = [S32 A32]

.bbl %start
  poparg n:S32
  poparg s:A32
  .reg S32 [c]
  .reg S32 [i]
  ld %S32_1:S32 = s 0
  mov c = %S32_1
  mov i = 1
  bra for_1_cond

.bbl for_1
  mul %S32_2:S32 = i 4
  lea %A32_3:A32 = s %S32_2
  ld %S32_4:S32 = %A32_3 0
  sub %S32_5:S32 = i 1
  mul %S32_6:S32 = %S32_5 4
  lea %A32_7:A32 = s %S32_6
  st %A32_7 0 = %S32_4

.bbl for_1_next
  add %S32_8:S32 = i 1
  mov i = %S32_8

.bbl for_1_cond
  ble i n for_1
  bra for_1_exit

.bbl for_1_exit
  mul %S32_9:S32 = n 4
  lea %A32_10:A32 = s %S32_9
  st %A32_10 0 = c
  ret


.fun tk NORMAL [] = [S32 A32 A32]

.bbl %start
  poparg n:S32
  poparg s:A32
  poparg t:A32
  .reg S32 [i]
  mov i = 0
  .reg S32 [f]
.stk c 4 64
  .reg S32 [x]
  mov x = 0
  bra for_2_cond

.bbl for_2
  lea %A32_1:A32 = c
  mul %S32_2:S32 = x 4
  lea %A32_3:A32 = %A32_1 %S32_2
  mov %S32_4:S32 = 0
  st %A32_3 0 = %S32_4

.bbl for_2_next
  add %S32_5:S32 = x 1
  mov x = %S32_5

.bbl for_2_cond
  blt x 16 for_2
  bra for_2_exit

.bbl for_2_exit
  bra while_1_cond

.bbl while_1
  pusharg s
  pusharg i
  bsr rotate
  lea %A32_6:A32 = c
  mul %S32_7:S32 = i 4
  lea %A32_8:A32 = %A32_6 %S32_7
  ld %S32_9:S32 = %A32_8 0
  ble i %S32_9 if_4_true
  bra if_4_end

.bbl if_4_true
  lea %A32_10:A32 = c
  mul %S32_11:S32 = i 4
  lea %A32_12:A32 = %A32_10 %S32_11
  mov %S32_13:S32 = 0
  st %A32_12 0 = %S32_13
  add %S32_14:S32 = i 1
  mov i = %S32_14
  bra while_1_cond

.bbl if_4_end
  lea %A32_15:A32 = c
  mul %S32_16:S32 = i 4
  lea %A32_17:A32 = %A32_15 %S32_16
  ld %S32_18:S32 = %A32_17 0
  add %S32_19:S32 = %S32_18 1
  lea %A32_20:A32 = c
  mul %S32_21:S32 = i 4
  lea %A32_22:A32 = %A32_20 %S32_21
  st %A32_22 0 = %S32_19
  mov i = 1
  lea %A32_23:A32 = odd
  ld %S32_24:S32 = %A32_23 0
  xor %S32_25:S32 = %S32_24 -1
  lea %A32_26:A32 = odd
  st %A32_26 0 = %S32_25
  ld %S32_27:S32 = s 0
  bne %S32_27 0 if_8_true
  bra while_1_cond

.bbl if_8_true
  ld %S32_28:S32 = s 0
  mul %S32_29:S32 = %S32_28 4
  lea %A32_30:A32 = s %S32_29
  ld %S32_31:S32 = %A32_30 0
  bne %S32_31 0 if_5_true
  bra if_5_false

.bbl if_5_true
  pusharg t
  pusharg s
  bsr flip
  poparg %S32_32:S32
  mov f = %S32_32
  bra if_5_end

.bbl if_5_false
  mov f = 1

.bbl if_5_end
  lea %A32_33:A32 = maxflips
  ld %S32_34:S32 = %A32_33 0
  blt %S32_34 f if_6_true
  bra if_6_end

.bbl if_6_true
  lea %A32_35:A32 = maxflips
  st %A32_35 0 = f

.bbl if_6_end
  lea %A32_36:A32 = odd
  ld %S32_37:S32 = %A32_36 0
  bne %S32_37 0 if_7_true
  bra if_7_false

.bbl if_7_true
  lea %A32_38:A32 = checksum
  ld %S32_39:S32 = %A32_38 0
  sub %S32_40:S32 = %S32_39 f
  lea %A32_41:A32 = checksum
  st %A32_41 0 = %S32_40
  bra while_1_cond

.bbl if_7_false
  lea %A32_42:A32 = checksum
  ld %S32_43:S32 = %A32_42 0
  add %S32_44:S32 = %S32_43 f
  lea %A32_45:A32 = checksum
  st %A32_45 0 = %S32_44

.bbl while_1_cond
  blt i n while_1
  bra while_1_exit

.bbl while_1_exit
  ret


.fun main NORMAL [S32] = [S32 A32]
.reg S32 [%out]

.bbl %start
  poparg argc:S32
  poparg v:A32
  .reg S32 [i]
  lea %A32_1:A32 = max_n
  mov %S32_2:S32 = 11
  st %A32_1 0 = %S32_2
  mov i = 0
  bra for_1_cond

.bbl for_1
  lea %A32_3:A32 = s
  mul %S32_4:S32 = i 4
  lea %A32_5:A32 = %A32_3 %S32_4
  st %A32_5 0 = i

.bbl for_1_next
  add %S32_6:S32 = i 1
  mov i = %S32_6

.bbl for_1_cond
  lea %A32_7:A32 = max_n
  ld %S32_8:S32 = %A32_7 0
  blt i %S32_8 for_1
  bra for_1_exit

.bbl for_1_exit
  lea %A32_9:A32 = max_n
  ld %S32_10:S32 = %A32_9 0
  lea %A32_11:A32 = s
  lea %A32_12:A32 = t
  pusharg %A32_12
  pusharg %A32_11
  pusharg %S32_10
  bsr tk
.mem string_const_1 4 RO
.data 1 "max_n: \x00"
  lea %A32_13:A32 = string_const_1
  mov %S32_15:S32 = 1
  pusharg %A32_13
  pusharg %S32_15
  bsr write_s
  poparg %S32_14:S32
  lea %A32_16:A32 = max_n
  ld %S32_17:S32 = %A32_16 0
  mov %S32_19:S32 = 1
  pusharg %S32_17
  pusharg %S32_19
  bsr write_d
  poparg %S32_18:S32
.mem string_const_2 4 RO
.data 1 " crc: \x00"
  lea %A32_20:A32 = string_const_2
  mov %S32_22:S32 = 1
  pusharg %A32_20
  pusharg %S32_22
  bsr write_s
  poparg %S32_21:S32
  lea %A32_23:A32 = checksum
  ld %S32_24:S32 = %A32_23 0
  mov %S32_26:S32 = 1
  pusharg %S32_24
  pusharg %S32_26
  bsr write_d
  poparg %S32_25:S32
.mem string_const_3 4 RO
.data 1 "  flips: \x00"
  lea %A32_27:A32 = string_const_3
  mov %S32_29:S32 = 1
  pusharg %A32_27
  pusharg %S32_29
  bsr write_s
  poparg %S32_28:S32
  lea %A32_30:A32 = maxflips
  ld %S32_31:S32 = %A32_30 0
  mov %S32_33:S32 = 1
  pusharg %S32_31
  pusharg %S32_33
  bsr write_d
  poparg %S32_32:S32
.mem string_const_4 4 RO
.data 1 "\n\x00"
  lea %A32_34:A32 = string_const_4
  mov %S32_36:S32 = 1
  pusharg %A32_34
  pusharg %S32_36
  bsr write_s
  poparg %S32_35:S32
  lea %A32_37:A32 = checksum
  ld %S32_38:S32 = %A32_37 0
  bne %S32_38 556355 if_3_true
  bra if_3_end

.bbl if_3_true
  bsr abort

.bbl if_3_end
  lea %A32_39:A32 = maxflips
  ld %S32_40:S32 = %A32_39 0
  bne %S32_40 51 if_4_true
  bra if_4_end

.bbl if_4_true
  bsr abort

.bbl if_4_end
  mov %out = 0
  pusharg %out
  ret
