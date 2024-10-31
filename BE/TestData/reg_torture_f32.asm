# uses about 40 global regs

.fun test NORMAL [R32] = [R32]
.reg R32 [%out]

.bbl %start
  poparg ireg:R32
  .reg R32 [ireg00]
  add %R32_1:R32 = ireg 0
  mov ireg00 = %R32_1
  .reg R32 [ireg01]
  add %R32_2:R32 = ireg 1
  mov ireg01 = %R32_2
  .reg R32 [ireg02]
  add %R32_3:R32 = ireg 2
  mov ireg02 = %R32_3
  .reg R32 [ireg03]
  add %R32_4:R32 = ireg 3
  mov ireg03 = %R32_4
  .reg R32 [ireg04]
  add %R32_5:R32 = ireg 4
  mov ireg04 = %R32_5
  .reg R32 [ireg05]
  add %R32_6:R32 = ireg 5
  mov ireg05 = %R32_6
  .reg R32 [ireg06]
  add %R32_7:R32 = ireg 6
  mov ireg06 = %R32_7
  .reg R32 [ireg07]
  add %R32_8:R32 = ireg 7
  mov ireg07 = %R32_8
  .reg R32 [ireg08]
  add %R32_9:R32 = ireg 8
  mov ireg08 = %R32_9
  .reg R32 [ireg09]
  add %R32_10:R32 = ireg 9
  mov ireg09 = %R32_10
  .reg R32 [ireg10]
  add %R32_11:R32 = ireg 10
  mov ireg10 = %R32_11
  .reg R32 [ireg11]
  add %R32_12:R32 = ireg 11
  mov ireg11 = %R32_12
  .reg R32 [ireg12]
  add %R32_13:R32 = ireg 12
  mov ireg12 = %R32_13
  .reg R32 [ireg13]
  add %R32_14:R32 = ireg 12
  mov ireg13 = %R32_14
  .reg R32 [ireg14]
  add %R32_15:R32 = ireg 14
  mov ireg14 = %R32_15
  .reg R32 [ireg15]
  add %R32_16:R32 = ireg 15
  mov ireg15 = %R32_16
  .reg R32 [ireg16]
  add %R32_17:R32 = ireg 16
  mov ireg16 = %R32_17
  .reg R32 [ireg17]
  add %R32_18:R32 = ireg 17
  mov ireg17 = %R32_18
  .reg R32 [ireg18]
  add %R32_19:R32 = ireg 18
  mov ireg18 = %R32_19
  .reg R32 [ireg19]
  add %R32_20:R32 = ireg 19
  mov ireg19 = %R32_20
  .reg R32 [ireg20]
  add %R32_21:R32 = ireg 20
  mov ireg20 = %R32_21
  .reg R32 [ireg21]
  add %R32_22:R32 = ireg 21
  mov ireg21 = %R32_22
  .reg R32 [ireg22]
  add %R32_23:R32 = ireg 22
  mov ireg22 = %R32_23
  .reg R32 [ireg23]
  add %R32_24:R32 = ireg 22
  mov ireg23 = %R32_24
  .reg R32 [ireg24]
  add %R32_25:R32 = ireg 24
  mov ireg24 = %R32_25
  .reg R32 [ireg25]
  add %R32_26:R32 = ireg 25
  mov ireg25 = %R32_26
  .reg R32 [ireg26]
  add %R32_27:R32 = ireg 26
  mov ireg26 = %R32_27
  .reg R32 [ireg27]
  add %R32_28:R32 = ireg 27
  mov ireg27 = %R32_28
  .reg R32 [ireg28]
  add %R32_29:R32 = ireg 28
  mov ireg28 = %R32_29
  .reg R32 [ireg29]
  add %R32_30:R32 = ireg 29
  mov ireg29 = %R32_30
  .reg R32 [ireg30]
  add %R32_31:R32 = ireg 30
  mov ireg30 = %R32_31
  .reg R32 [ireg31]
  add %R32_32:R32 = ireg 31
  mov ireg31 = %R32_32
  .reg R32 [ireg32]
  add %R32_33:R32 = ireg 32
  mov ireg32 = %R32_33
  .reg R32 [ireg33]
  add %R32_34:R32 = ireg 32
  mov ireg33 = %R32_34
  .reg R32 [ireg34]
  add %R32_35:R32 = ireg 34
  mov ireg34 = %R32_35
  .reg R32 [ireg35]
  add %R32_36:R32 = ireg 35
  mov ireg35 = %R32_36
  .reg R32 [ireg36]
  add %R32_37:R32 = ireg 36
  mov ireg36 = %R32_37
  .reg R32 [ireg37]
  add %R32_38:R32 = ireg 37
  mov ireg37 = %R32_38
  .reg R32 [ireg38]
  add %R32_39:R32 = ireg 38
  mov ireg38 = %R32_39
  .reg R32 [ireg39]
  add %R32_40:R32 = ireg 39
  mov ireg39 = %R32_40
  .reg U32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  blt ireg10 15 if_2_true
  bra if_2_false

.bbl if_2_true
  .reg R32 [tmp]
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
  .reg R32 [__local_4_tmp]
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
  mov ireg04 = ireg03
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
    pusharg 10:R32
    bsr test
    poparg y:R32
    conv z:U32 y
    pusharg z
    bsr print_u_ln

    pusharg 0:S32
    ret
