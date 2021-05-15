############################################################
# std_lib.c
############################################################

.mem __static_2__malloc_end 4 RW
.data 4 [0]

.mem __static_1__malloc_start 4 RW
.data 4 [0]


.fun write_s NORMAL [S32] = [S32 A32]
.reg S32 [%out]

.bbl %start
  poparg fd:S32
  poparg s:A32
  .reg U32 [len]
  mov len = 0
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
  mov %out = %S32_5
  pusharg %out
  ret


.fun write_x NORMAL [S32] = [S32 U32]
.reg S32 [%out]

.bbl %start
  poparg fd:S32
  poparg val:U32
.stk buffer 1 16
  .reg U32 [pos]
  lea %A32_6:A32 = buffer
  mov pos = 16

.bbl while_1
  sub %U32_7:U32 = pos 1
  mov pos = %U32_7
  .reg U32 [digit]
  rem %U32_8:U32 = val 16
  mov digit = %U32_8
  ble digit 9 if_2_true
  bra if_2_false

.bbl if_2_true
  add %U32_9:U32 = 48:U32 digit
  conv %S8_10:S8 = %U32_9
  lea %A32_11:A32 = buffer
  lea %A32_12:A32 = %A32_11 pos
  st %A32_12 0 = %S8_10
  bra if_2_end

.bbl if_2_false
  sub %S32_13:S32 = 97:S32 10
  conv %U32_14:U32 = %S32_13
  add %U32_15:U32 = %U32_14 digit
  conv %S8_16:S8 = %U32_15
  lea %A32_17:A32 = buffer
  lea %A32_18:A32 = %A32_17 pos
  st %A32_18 0 = %S8_16

.bbl if_2_end
  div %U32_19:U32 = val 16
  mov val = %U32_19

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_20:A32 = buffer
  lea %A32_21:A32 = %A32_20 pos
  lea %A32_22:A32 = buffer
  sub %U32_23:U32 = 16:U32 pos
  pusharg %U32_23
  pusharg %A32_21
  pusharg fd
  bsr write
  poparg %S32_24:S32
  mov %out = %S32_24
  pusharg %out
  ret


.fun write_u NORMAL [S32] = [S32 U32]
.reg S32 [%out]

.bbl %start
  poparg fd:S32
  poparg val:U32
.stk buffer 1 16
  .reg U32 [pos]
  lea %A32_25:A32 = buffer
  mov pos = 16

.bbl while_1
  sub %U32_26:U32 = pos 1
  mov pos = %U32_26
  rem %U32_27:U32 = val 10
  add %U32_28:U32 = 48:U32 %U32_27
  conv %S8_29:S8 = %U32_28
  lea %A32_30:A32 = buffer
  lea %A32_31:A32 = %A32_30 pos
  st %A32_31 0 = %S8_29
  div %U32_32:U32 = val 10
  mov val = %U32_32

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_33:A32 = buffer
  lea %A32_34:A32 = %A32_33 pos
  lea %A32_35:A32 = buffer
  sub %U32_36:U32 = 16:U32 pos
  pusharg %U32_36
  pusharg %A32_34
  pusharg fd
  bsr write
  poparg %S32_37:S32
  mov %out = %S32_37
  pusharg %out
  ret


.fun write_d NORMAL [S32] = [S32 S32]
.reg S32 [%out]

.bbl %start
  poparg fd:S32
  poparg sval:S32
  ble 0:S32 sval if_2_true
  bra if_2_end

.bbl if_2_true
  conv %U32_38:U32 = sval
  pusharg %U32_38
  pusharg fd
  bsr write_u
  poparg %S32_39:S32
  mov %out = %S32_39
  pusharg %out
  ret

.bbl if_2_end
  .reg U32 [val]
  sub %S32_40:S32 = 0  sval
  conv %U32_41:U32 = %S32_40
  mov val = %U32_41
.stk buffer 1 16
  .reg U32 [pos]
  lea %A32_42:A32 = buffer
  mov pos = 16

.bbl while_1
  sub %U32_43:U32 = pos 1
  mov pos = %U32_43
  rem %U32_44:U32 = val 10
  add %U32_45:U32 = 48:U32 %U32_44
  conv %S8_46:S8 = %U32_45
  lea %A32_47:A32 = buffer
  lea %A32_48:A32 = %A32_47 pos
  st %A32_48 0 = %S8_46
  div %U32_49:U32 = val 10
  mov val = %U32_49

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  sub %U32_50:U32 = pos 1
  mov pos = %U32_50
  lea %A32_51:A32 = buffer
  lea %A32_52:A32 = %A32_51 pos
  mov %S8_53:S8 = 45
  st %A32_52 0 = %S8_53
  lea %A32_54:A32 = buffer
  lea %A32_55:A32 = %A32_54 pos
  lea %A32_56:A32 = buffer
  sub %U32_57:U32 = 16:U32 pos
  pusharg %U32_57
  pusharg %A32_55
  pusharg fd
  bsr write
  poparg %S32_58:S32
  mov %out = %S32_58
  pusharg %out
  ret


.fun write_c NORMAL [S32] = [S32 U8]
.reg S32 [%out]

.bbl %start
  poparg fd:S32
  poparg c:U8
.stk buffer 1 16
  conv %S8_59:S8 = c
  lea %A32_60:A32 = buffer
  st %A32_60 0 = %S8_59
  lea %A32_61:A32 = buffer
  mov %U32_63:U32 = 1
  pusharg %U32_63
  pusharg %A32_61
  pusharg fd
  bsr write
  poparg %S32_62:S32
  mov %out = %S32_62
  pusharg %out
  ret


.fun print_ln NORMAL [] = [A32 U32]

.bbl %start
  poparg s:A32
  poparg n:U32
  mov %S32_65:S32 = 1
  pusharg n
  pusharg s
  pusharg %S32_65
  bsr write
  poparg %S32_64:S32
  mov %S32_67:S32 = 1
  mov %U8_68:U8 = 10
  pusharg %U8_68
  pusharg %S32_67
  bsr write_c
  poparg %S32_66:S32
  ret


.fun print_s_ln NORMAL [] = [A32]

.bbl %start
  poparg s:A32
  mov %S32_70:S32 = 1
  pusharg s
  pusharg %S32_70
  bsr write_s
  poparg %S32_69:S32
  mov %S32_72:S32 = 1
  mov %U8_73:U8 = 10
  pusharg %U8_73
  pusharg %S32_72
  bsr write_c
  poparg %S32_71:S32
  ret


.fun print_d_ln NORMAL [] = [S32]

.bbl %start
  poparg n:S32
  mov %S32_75:S32 = 1
  pusharg n
  pusharg %S32_75
  bsr write_d
  poparg %S32_74:S32
  mov %S32_77:S32 = 1
  mov %U8_78:U8 = 10
  pusharg %U8_78
  pusharg %S32_77
  bsr write_c
  poparg %S32_76:S32
  ret


.fun print_u_ln NORMAL [] = [U32]

.bbl %start
  poparg n:U32
  mov %S32_80:S32 = 1
  pusharg n
  pusharg %S32_80
  bsr write_u
  poparg %S32_79:S32
  mov %S32_82:S32 = 1
  mov %U8_83:U8 = 10
  pusharg %U8_83
  pusharg %S32_82
  bsr write_c
  poparg %S32_81:S32
  ret


.fun print_x_ln NORMAL [] = [U32]

.bbl %start
  poparg n:U32
  mov %S32_85:S32 = 1
  pusharg n
  pusharg %S32_85
  bsr write_x
  poparg %S32_84:S32
  mov %S32_87:S32 = 1
  mov %U8_88:U8 = 10
  pusharg %U8_88
  pusharg %S32_87
  bsr write_c
  poparg %S32_86:S32
  ret


.fun print_c_ln NORMAL [] = [U8]

.bbl %start
  poparg c:U8
  mov %S32_90:S32 = 1
  pusharg c
  pusharg %S32_90
  bsr write_c
  poparg %S32_89:S32
  mov %S32_92:S32 = 1
  mov %U8_93:U8 = 10
  pusharg %U8_93
  pusharg %S32_92
  bsr write_c
  poparg %S32_91:S32
  ret


.fun memset NORMAL [A32] = [A32 S32 U32]
.reg A32 [%out]

.bbl %start
  poparg ptr:A32
  poparg value:S32
  poparg n:U32
  .reg S32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  conv %S8_94:S8 = value
  lea %A32_95:A32 = ptr i
  st %A32_95 0 = %S8_94

.bbl for_1_next
  add %S32_96:S32 = i 1
  mov i = %S32_96

.bbl for_1_cond
  conv %U32_97:U32 = i
  blt %U32_97 n for_1
  bra for_1_exit

.bbl for_1_exit
  mov %out = ptr
  pusharg %out
  ret


.fun memcpy NORMAL [A32] = [A32 A32 U32]
.reg A32 [%out]

.bbl %start
  poparg dst:A32
  poparg src:A32
  poparg n:U32
  .reg S32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  lea %A32_98:A32 = src i
  ld %S8_99:S8 = %A32_98 0
  lea %A32_100:A32 = dst i
  st %A32_100 0 = %S8_99

.bbl for_1_next
  add %S32_101:S32 = i 1
  mov i = %S32_101

.bbl for_1_cond
  conv %U32_102:U32 = i
  blt %U32_102 n for_1
  bra for_1_exit

.bbl for_1_exit
  mov %out = dst
  pusharg %out
  ret


.fun abort NORMAL [] = []

.bbl %start
  bsr getpid
  poparg %S32_103:S32
  mov %S32_105:S32 = 3
  pusharg %S32_105
  pusharg %S32_103
  bsr kill
  poparg %S32_104:S32
  mov %S32_106:S32 = 1
  pusharg %S32_106
  bsr exit
  ret


.fun malloc NORMAL [A32] = [U32]
.reg A32 [%out]

.bbl %start
  poparg size:U32
  .reg U32 [page_size]
  shl %S32_107:S32 = 1:S32 20
  conv %U32_108:U32 = %S32_107
  mov page_size = %U32_108
  lea %A32_109:A32 = __static_1__malloc_start
  ld %A32_110:A32 = %A32_109 0
  beq %A32_110 0 if_1_true
  bra if_1_end

.bbl if_1_true
  lea %A32_112:A32 = 0:A32
  pusharg %A32_112
  bsr xbrk
  poparg %A32_111:A32
  lea %A32_113:A32 = __static_1__malloc_start
  st %A32_113 0 = %A32_111
  lea %A32_114:A32 = __static_1__malloc_start
  ld %A32_115:A32 = %A32_114 0
  lea %A32_116:A32 = __static_2__malloc_end
  st %A32_116 0 = %A32_115

.bbl if_1_end
  .reg U32 [rounded_size]
  add %U32_117:U32 = size 15
  div %U32_118:U32 = %U32_117 16
  mul %U32_119:U32 = %U32_118 16
  mov rounded_size = %U32_119
  lea %A32_120:A32 = __static_1__malloc_start
  ld %A32_121:A32 = %A32_120 0
  lea %A32_122:A32 = %A32_121 rounded_size
  lea %A32_123:A32 = __static_2__malloc_end
  ld %A32_124:A32 = %A32_123 0
  blt %A32_124 %A32_122 if_3_true
  bra if_3_end

.bbl if_3_true
  .reg U32 [increment]
  add %U32_125:U32 = rounded_size page_size
  sub %U32_126:U32 = %U32_125 1
  div %U32_127:U32 = %U32_126 page_size
  mul %U32_128:U32 = %U32_127 page_size
  mov increment = %U32_128
  .reg A32 [new_end]
  lea %A32_129:A32 = __static_2__malloc_end
  ld %A32_130:A32 = %A32_129 0
  lea %A32_131:A32 = %A32_130 increment
  mov new_end = %A32_131
  pusharg new_end
  bsr xbrk
  poparg %A32_132:A32
  lea %A32_133:A32 = __static_2__malloc_end
  st %A32_133 0 = %A32_132
  lea %A32_134:A32 = __static_2__malloc_end
  ld %A32_135:A32 = %A32_134 0
  bne %A32_135 new_end if_2_true
  bra if_3_end

.bbl if_2_true
  bsr abort

.bbl if_3_end
  .reg A32 [result]
  lea %A32_136:A32 = __static_1__malloc_start
  ld %A32_137:A32 = %A32_136 0
  mov result = %A32_137
  lea %A32_138:A32 = __static_1__malloc_start
  ld %A32_139:A32 = %A32_138 0
  lea %A32_140:A32 = %A32_139 rounded_size
  lea %A32_141:A32 = __static_1__malloc_start
  st %A32_141 0 = %A32_140
  mov %out = result
  pusharg %out
  ret


.fun free NORMAL [] = [A32]

.bbl %start
  poparg ptr:A32
  ret
