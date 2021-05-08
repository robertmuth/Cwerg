# uses about 40 global regs

.fun test NORMAL [F32] = [F32]
.reg F32 [%out]

.bbl %start
  poparg ireg:F32
  .reg F32 [ireg00]
  add %F32_1:F32 = ireg 0
  mov ireg00 = %F32_1
  .reg F32 [ireg01]
  add %F32_2:F32 = ireg 1
  mov ireg01 = %F32_2
  .reg F32 [ireg02]
  add %F32_3:F32 = ireg 2
  mov ireg02 = %F32_3
  .reg F32 [ireg03]
  add %F32_4:F32 = ireg 3
  mov ireg03 = %F32_4
  .reg F32 [ireg04]
  add %F32_5:F32 = ireg 4
  mov ireg04 = %F32_5
  .reg F32 [ireg05]
  add %F32_6:F32 = ireg 5
  mov ireg05 = %F32_6
  .reg F32 [ireg06]
  add %F32_7:F32 = ireg 6
  mov ireg06 = %F32_7
  .reg F32 [ireg07]
  add %F32_8:F32 = ireg 7
  mov ireg07 = %F32_8
  .reg F32 [ireg08]
  add %F32_9:F32 = ireg 8
  mov ireg08 = %F32_9
  .reg F32 [ireg09]
  add %F32_10:F32 = ireg 9
  mov ireg09 = %F32_10
  .reg F32 [ireg10]
  add %F32_11:F32 = ireg 10
  mov ireg10 = %F32_11
  .reg F32 [ireg11]
  add %F32_12:F32 = ireg 11
  mov ireg11 = %F32_12
  .reg F32 [ireg12]
  add %F32_13:F32 = ireg 12
  mov ireg12 = %F32_13
  .reg F32 [ireg13]
  add %F32_14:F32 = ireg 12
  mov ireg13 = %F32_14
  .reg F32 [ireg14]
  add %F32_15:F32 = ireg 14
  mov ireg14 = %F32_15
  .reg F32 [ireg15]
  add %F32_16:F32 = ireg 15
  mov ireg15 = %F32_16
  .reg F32 [ireg16]
  add %F32_17:F32 = ireg 16
  mov ireg16 = %F32_17
  .reg F32 [ireg17]
  add %F32_18:F32 = ireg 17
  mov ireg17 = %F32_18
  .reg F32 [ireg18]
  add %F32_19:F32 = ireg 18
  mov ireg18 = %F32_19
  .reg F32 [ireg19]
  add %F32_20:F32 = ireg 19
  mov ireg19 = %F32_20
  .reg F32 [ireg20]
  add %F32_21:F32 = ireg 20
  mov ireg20 = %F32_21
  .reg F32 [ireg21]
  add %F32_22:F32 = ireg 21
  mov ireg21 = %F32_22
  .reg F32 [ireg22]
  add %F32_23:F32 = ireg 22
  mov ireg22 = %F32_23
  .reg F32 [ireg23]
  add %F32_24:F32 = ireg 22
  mov ireg23 = %F32_24
  .reg F32 [ireg24]
  add %F32_25:F32 = ireg 24
  mov ireg24 = %F32_25
  .reg F32 [ireg25]
  add %F32_26:F32 = ireg 25
  mov ireg25 = %F32_26
  .reg F32 [ireg26]
  add %F32_27:F32 = ireg 26
  mov ireg26 = %F32_27
  .reg F32 [ireg27]
  add %F32_28:F32 = ireg 27
  mov ireg27 = %F32_28
  .reg F32 [ireg28]
  add %F32_29:F32 = ireg 28
  mov ireg28 = %F32_29
  .reg F32 [ireg29]
  add %F32_30:F32 = ireg 29
  mov ireg29 = %F32_30
  .reg F32 [ireg30]
  add %F32_31:F32 = ireg 30
  mov ireg30 = %F32_31
  .reg F32 [ireg31]
  add %F32_32:F32 = ireg 31
  mov ireg31 = %F32_32
  .reg F32 [ireg32]
  add %F32_33:F32 = ireg 32
  mov ireg32 = %F32_33
  .reg F32 [ireg33]
  add %F32_34:F32 = ireg 32
  mov ireg33 = %F32_34
  .reg F32 [ireg34]
  add %F32_35:F32 = ireg 34
  mov ireg34 = %F32_35
  .reg F32 [ireg35]
  add %F32_36:F32 = ireg 35
  mov ireg35 = %F32_36
  .reg F32 [ireg36]
  add %F32_37:F32 = ireg 36
  mov ireg36 = %F32_37
  .reg F32 [ireg37]
  add %F32_38:F32 = ireg 37
  mov ireg37 = %F32_38
  .reg F32 [ireg38]
  add %F32_39:F32 = ireg 38
  mov ireg38 = %F32_39
  .reg F32 [ireg39]
  add %F32_40:F32 = ireg 39
  mov ireg39 = %F32_40
  .reg U32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  blt ireg10 15 if_2_true
  bra if_2_false

.bbl if_2_true
  .reg F32 [tmp]
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
  .reg F32 [__local_4_tmp]
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


.fun main NORMAL [U32] = []

.bbl start
    pusharg 10:F32
    bsr test
    poparg y:F32
    conv z:U32 y
    pusharg z
    bsr print_u_ln

    pusharg 0:U32
    ret
