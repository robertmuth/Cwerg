# uses about 40 global regs

.fun test NORMAL [U32] = [U32]
.reg U32 %out

.bbl %start
  poparg ireg:U32
  .reg U32 ireg00
  add %U32_1:U32 = ireg 0
  mov ireg00 = %U32_1
  .reg U32 ireg01
  add %U32_2:U32 = ireg 1
  mov ireg01 = %U32_2
  .reg U32 ireg02
  add %U32_3:U32 = ireg 2
  mov ireg02 = %U32_3
  .reg U32 ireg03
  add %U32_4:U32 = ireg 2
  mov ireg03 = %U32_4
  .reg U32 ireg04
  add %U32_5:U32 = ireg 4
  mov ireg04 = %U32_5
  .reg U32 ireg05
  add %U32_6:U32 = ireg 5
  mov ireg05 = %U32_6
  .reg U32 ireg06
  add %U32_7:U32 = ireg 6
  mov ireg06 = %U32_7
  .reg U32 ireg07
  add %U32_8:U32 = ireg 7
  mov ireg07 = %U32_8
  .reg U32 ireg08
  add %U32_9:U32 = ireg 8
  mov ireg08 = %U32_9
  .reg U32 ireg09
  add %U32_10:U32 = ireg 9
  mov ireg09 = %U32_10
  .reg U32 ireg10
  add %U32_11:U32 = ireg 10
  mov ireg10 = %U32_11
  .reg U32 ireg11
  add %U32_12:U32 = ireg 11
  mov ireg11 = %U32_12
  .reg U32 ireg12
  add %U32_13:U32 = ireg 12
  mov ireg12 = %U32_13
  .reg U32 ireg13
  add %U32_14:U32 = ireg 12
  mov ireg13 = %U32_14
  .reg U32 ireg14
  add %U32_15:U32 = ireg 14
  mov ireg14 = %U32_15
  .reg U32 ireg15
  add %U32_16:U32 = ireg 15
  mov ireg15 = %U32_16
  .reg U32 ireg16
  add %U32_17:U32 = ireg 16
  mov ireg16 = %U32_17
  .reg U32 ireg17
  add %U32_18:U32 = ireg 17
  mov ireg17 = %U32_18
  .reg U32 ireg18
  add %U32_19:U32 = ireg 18
  mov ireg18 = %U32_19
  .reg U32 ireg19
  add %U32_20:U32 = ireg 19
  mov ireg19 = %U32_20
  .reg U32 ireg20
  add %U32_21:U32 = ireg 20
  mov ireg20 = %U32_21
  .reg U32 ireg21
  add %U32_22:U32 = ireg 21
  mov ireg21 = %U32_22
  .reg U32 ireg22
  add %U32_23:U32 = ireg 22
  mov ireg22 = %U32_23
  .reg U32 ireg23
  add %U32_24:U32 = ireg 22
  mov ireg23 = %U32_24
  .reg U32 ireg24
  add %U32_25:U32 = ireg 24
  mov ireg24 = %U32_25
  .reg U32 ireg25
  add %U32_26:U32 = ireg 25
  mov ireg25 = %U32_26
  .reg U32 ireg26
  add %U32_27:U32 = ireg 26
  mov ireg26 = %U32_27
  .reg U32 ireg27
  add %U32_28:U32 = ireg 27
  mov ireg27 = %U32_28
  .reg U32 ireg28
  add %U32_29:U32 = ireg 28
  mov ireg28 = %U32_29
  .reg U32 ireg29
  add %U32_30:U32 = ireg 29
  mov ireg29 = %U32_30
  .reg U32 ireg30
  add %U32_31:U32 = ireg 30
  mov ireg30 = %U32_31
  .reg U32 ireg31
  add %U32_32:U32 = ireg 31
  mov ireg31 = %U32_32
  .reg U32 ireg32
  add %U32_33:U32 = ireg 32
  mov ireg32 = %U32_33
  .reg U32 ireg33
  add %U32_34:U32 = ireg 32
  mov ireg33 = %U32_34
  .reg U32 ireg34
  add %U32_35:U32 = ireg 34
  mov ireg34 = %U32_35
  .reg U32 ireg35
  add %U32_36:U32 = ireg 35
  mov ireg35 = %U32_36
  .reg U32 ireg36
  add %U32_37:U32 = ireg 36
  mov ireg36 = %U32_37
  .reg U32 ireg37
  add %U32_38:U32 = ireg 37
  mov ireg37 = %U32_38
  .reg U32 ireg38
  add %U32_39:U32 = ireg 38
  mov ireg38 = %U32_39
  .reg U32 ireg39
  add %U32_40:U32 = ireg 39
  mov ireg39 = %U32_40
  .reg U32 i
  mov i = 0
  bra for_1_cond

.bbl for_1
  blt ireg10 15 if_2_true
  bra if_2_false

.bbl if_2_true
  .reg U32 tmp
  mov tmp = ireg00
  mov ireg00 = ireg01
  mov ireg01 = ireg02
  mov ireg02 = ireg03
  mov ireg03 = ireg04
  mov ireg04 = ireg05
  mov ireg05 = ireg06
  mov ireg06 = ireg07
  mov ireg07 = ireg08
  mov ireg08 = ireg09
  mov ireg09 = ireg10
  mov ireg10 = ireg11
  mov ireg11 = ireg12
  mov ireg12 = ireg13
  mov ireg13 = ireg14
  mov ireg14 = ireg15
  mov ireg15 = ireg16
  mov ireg16 = ireg17
  mov ireg17 = ireg18
  mov ireg18 = ireg19
  mov ireg19 = ireg20
  mov ireg20 = ireg21
  mov ireg21 = ireg22
  mov ireg22 = ireg23
  mov ireg23 = ireg24
  mov ireg24 = ireg25
  mov ireg25 = ireg26
  mov ireg26 = ireg27
  mov ireg27 = ireg28
  mov ireg28 = ireg29
  mov ireg29 = ireg20
  mov ireg30 = ireg31
  mov ireg31 = ireg32
  mov ireg32 = ireg33
  mov ireg33 = ireg34
  mov ireg34 = ireg35
  mov ireg35 = ireg36
  mov ireg36 = ireg37
  mov ireg37 = ireg38
  mov ireg38 = ireg39
  mov ireg39 = tmp
  bra for_1_next

.bbl if_2_false
  .reg U32 __local_4_tmp
  mov __local_4_tmp = ireg39
  mov ireg39 = ireg38
  mov ireg38 = ireg37
  mov ireg37 = ireg36
  mov ireg36 = ireg35
  mov ireg35 = ireg34
  mov ireg34 = ireg33
  mov ireg33 = ireg32
  mov ireg32 = ireg31
  mov ireg31 = ireg30
  mov ireg30 = ireg29
  mov ireg29 = ireg28
  mov ireg28 = ireg27
  mov ireg27 = ireg26
  mov ireg26 = ireg25
  mov ireg25 = ireg24
  mov ireg24 = ireg23
  mov ireg23 = ireg22
  mov ireg22 = ireg21
  mov ireg21 = ireg20
  mov ireg20 = ireg19
  mov ireg19 = ireg18
  mov ireg18 = ireg17
  mov ireg17 = ireg16
  mov ireg16 = ireg15
  mov ireg15 = ireg14
  mov ireg14 = ireg13
  mov ireg13 = ireg12
  mov ireg12 = ireg11
  mov ireg11 = ireg10
  mov ireg10 = ireg09
  mov ireg09 = ireg08
  mov ireg08 = ireg07
  mov ireg07 = ireg06
  mov ireg06 = ireg05
  mov ireg05 = ireg04
  mov ireg03 = ireg02
  mov ireg02 = ireg01
  mov ireg01 = ireg00
  mov ireg00 = __local_4_tmp

.bbl for_1_next
  add %U32_41:U32 = i 1
  mov i = %U32_41

.bbl for_1_cond
  blt i 50 for_1
  bra for_1_exit

.bbl for_1_exit
  mov %out = ireg10
  pusharg %out
  ret


.fun main NORMAL [S32] = []

.bbl start
    pusharg 10:U32
    bsr test
    poparg y:U32
    pusharg y
    bsr print_u_ln

    pusharg 0:S32
    ret
