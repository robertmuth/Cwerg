

.fun njRowIDCT NORMAL [] = [A32]

.bbl %start
  poparg blk:A32
  .reg S32 [x0]
  .reg S32 [x1]
  .reg S32 [x2]
  .reg S32 [x3]
  .reg S32 [x4]
  .reg S32 [x5]
  .reg S32 [x6]
  .reg S32 [x7]
  .reg S32 [x8]
  lea %A32_1:A32 = blk 16
  ld %S32_2:S32 = %A32_1 0
  shl %S32_3:S32 = %S32_2 11
  mov x1 = %S32_3
  lea %A32_4:A32 = blk 24
  ld %S32_5:S32 = %A32_4 0
  mov x2 = %S32_5
  or %S32_6:S32 = %S32_3 %S32_5
  lea %A32_7:A32 = blk 8
  ld %S32_8:S32 = %A32_7 0
  mov x3 = %S32_8
  or %S32_9:S32 = %S32_6 %S32_8
  lea %A32_10:A32 = blk 4
  ld %S32_11:S32 = %A32_10 0
  mov x4 = %S32_11
  or %S32_12:S32 = %S32_9 %S32_11
  lea %A32_13:A32 = blk 28
  ld %S32_14:S32 = %A32_13 0
  mov x5 = %S32_14
  or %S32_15:S32 = %S32_12 %S32_14
  lea %A32_16:A32 = blk 20
  ld %S32_17:S32 = %A32_16 0
  mov x6 = %S32_17
  or %S32_18:S32 = %S32_15 %S32_17
  lea %A32_19:A32 = blk 12
  ld %S32_20:S32 = %A32_19 0
  mov x7 = %S32_20
  or %S32_21:S32 = %S32_18 %S32_20
  bne %S32_21 0 if_1_end
  bra if_1_true

.bbl if_1_true
  ld %S32_22:S32 = blk 0
  shl %S32_23:S32 = %S32_22 3
  lea %A32_24:A32 = blk 28
  st %A32_24 0 = %S32_23
  lea %A32_25:A32 = blk 24
  st %A32_25 0 = %S32_23
  lea %A32_26:A32 = blk 20
  st %A32_26 0 = %S32_23
  lea %A32_27:A32 = blk 16
  st %A32_27 0 = %S32_23
  lea %A32_28:A32 = blk 12
  st %A32_28 0 = %S32_23
  lea %A32_29:A32 = blk 8
  st %A32_29 0 = %S32_23
  lea %A32_30:A32 = blk 4
  st %A32_30 0 = %S32_23
  st blk 0 = %S32_23
  ret

.bbl if_1_end
  ld %S32_31:S32 = blk 0
  shl %S32_32:S32 = %S32_31 11
  add %S32_33:S32 = %S32_32 128
  mov x0 = %S32_33
  add %S32_34:S32 = x4 x5
  mul %S32_35:S32 = %S32_34 565
  mov x8 = %S32_35
  sub %S32_36:S32 = 2841:S32 565
  mul %S32_37:S32 = x4 %S32_36
  add %S32_38:S32 = x8 %S32_37
  mov x4 = %S32_38
  add %S32_39:S32 = 2841:S32 565
  mul %S32_40:S32 = x5 %S32_39
  sub %S32_41:S32 = x8 %S32_40
  mov x5 = %S32_41
  add %S32_42:S32 = x6 x7
  mul %S32_43:S32 = %S32_42 2408
  mov x8 = %S32_43
  sub %S32_44:S32 = 2408:S32 1609
  mul %S32_45:S32 = x6 %S32_44
  sub %S32_46:S32 = x8 %S32_45
  mov x6 = %S32_46
  add %S32_47:S32 = 2408:S32 1609
  mul %S32_48:S32 = x7 %S32_47
  sub %S32_49:S32 = x8 %S32_48
  mov x7 = %S32_49
  add %S32_50:S32 = x0 x1
  mov x8 = %S32_50
  sub %S32_51:S32 = x0 x1
  mov x0 = %S32_51
  add %S32_52:S32 = x3 x2
  mul %S32_53:S32 = %S32_52 1108
  mov x1 = %S32_53
  add %S32_54:S32 = 2676:S32 1108
  mul %S32_55:S32 = x2 %S32_54
  sub %S32_56:S32 = x1 %S32_55
  mov x2 = %S32_56
  sub %S32_57:S32 = 2676:S32 1108
  mul %S32_58:S32 = x3 %S32_57
  add %S32_59:S32 = x1 %S32_58
  mov x3 = %S32_59
  add %S32_60:S32 = x4 x6
  mov x1 = %S32_60
  sub %S32_61:S32 = x4 x6
  mov x4 = %S32_61
  add %S32_62:S32 = x5 x7
  mov x6 = %S32_62
  sub %S32_63:S32 = x5 x7
  mov x5 = %S32_63
  add %S32_64:S32 = x8 x3
  mov x7 = %S32_64
  sub %S32_65:S32 = x8 x3
  mov x8 = %S32_65
  add %S32_66:S32 = x0 x2
  mov x3 = %S32_66
  sub %S32_67:S32 = x0 x2
  mov x0 = %S32_67
  add %S32_68:S32 = x4 x5
  mul %S32_69:S32 = %S32_68 181
  add %S32_70:S32 = %S32_69 128
  shr %S32_71:S32 = %S32_70 8
  mov x2 = %S32_71
  sub %S32_72:S32 = x4 x5
  mul %S32_73:S32 = %S32_72 181
  add %S32_74:S32 = %S32_73 128
  shr %S32_75:S32 = %S32_74 8
  mov x4 = %S32_75
  add %S32_76:S32 = x7 x1
  shr %S32_77:S32 = %S32_76 8
  st blk 0 = %S32_77
  add %S32_78:S32 = x3 x2
  shr %S32_79:S32 = %S32_78 8
  lea %A32_80:A32 = blk 4
  st %A32_80 0 = %S32_79
  add %S32_81:S32 = x0 x4
  shr %S32_82:S32 = %S32_81 8
  lea %A32_83:A32 = blk 8
  st %A32_83 0 = %S32_82
  add %S32_84:S32 = x8 x6
  shr %S32_85:S32 = %S32_84 8
  lea %A32_86:A32 = blk 12
  st %A32_86 0 = %S32_85
  sub %S32_87:S32 = x8 x6
  shr %S32_88:S32 = %S32_87 8
  lea %A32_89:A32 = blk 16
  st %A32_89 0 = %S32_88
  sub %S32_90:S32 = x0 x4
  shr %S32_91:S32 = %S32_90 8
  lea %A32_92:A32 = blk 20
  st %A32_92 0 = %S32_91
  sub %S32_93:S32 = x3 x2
  shr %S32_94:S32 = %S32_93 8
  lea %A32_95:A32 = blk 24
  st %A32_95 0 = %S32_94
  sub %S32_96:S32 = x7 x1
  shr %S32_97:S32 = %S32_96 8
  lea %A32_98:A32 = blk 28
  st %A32_98 0 = %S32_97
  ret

