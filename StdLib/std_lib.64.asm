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
  lea %A64_6:A64 = buffer
  mov pos = 16

.bbl while_1
  sub %U64_7:U64 = pos 1
  mov pos = %U64_7
  .reg U32 [digit]
  rem %U32_8:U32 = val 16
  mov digit = %U32_8
  ble digit 9 if_2_true
  bra if_2_false

.bbl if_2_true
  add %U32_9:U32 = 48:U32 digit
  conv %S8_10:S8 = %U32_9
  lea %A64_11:A64 = buffer
  lea %A64_12:A64 = %A64_11 pos
  st %A64_12 0 = %S8_10
  bra if_2_end

.bbl if_2_false
  sub %S32_13:S32 = 97:S32 10
  conv %U32_14:U32 = %S32_13
  add %U32_15:U32 = %U32_14 digit
  conv %S8_16:S8 = %U32_15
  lea %A64_17:A64 = buffer
  lea %A64_18:A64 = %A64_17 pos
  st %A64_18 0 = %S8_16

.bbl if_2_end
  div %U32_19:U32 = val 16
  mov val = %U32_19

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A64_20:A64 = buffer
  lea %A64_21:A64 = %A64_20 pos
  lea %A64_22:A64 = buffer
  sub %U64_23:U64 = 16:U64 pos
  pusharg %U64_23
  pusharg %A64_21
  pusharg fd
  bsr write
  poparg %S64_24:S64
  mov %out = %S64_24
  pusharg %out
  ret


.fun write_u NORMAL [S64] = [S32 U32]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg val:U32
.stk buffer 1 16
  .reg U64 [pos]
  lea %A64_25:A64 = buffer
  mov pos = 16

.bbl while_1
  sub %U64_26:U64 = pos 1
  mov pos = %U64_26
  rem %U32_27:U32 = val 10
  add %U32_28:U32 = 48:U32 %U32_27
  conv %S8_29:S8 = %U32_28
  lea %A64_30:A64 = buffer
  lea %A64_31:A64 = %A64_30 pos
  st %A64_31 0 = %S8_29
  div %U32_32:U32 = val 10
  mov val = %U32_32

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A64_33:A64 = buffer
  lea %A64_34:A64 = %A64_33 pos
  lea %A64_35:A64 = buffer
  sub %U64_36:U64 = 16:U64 pos
  pusharg %U64_36
  pusharg %A64_34
  pusharg fd
  bsr write
  poparg %S64_37:S64
  mov %out = %S64_37
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
  conv %U32_38:U32 = sval
  pusharg %U32_38
  pusharg fd
  bsr write_u
  poparg %S64_39:S64
  mov %out = %S64_39
  pusharg %out
  ret

.bbl if_2_end
  .reg U32 [val]
  sub %S32_40:S32 = 0  sval
  conv %U32_41:U32 = %S32_40
  mov val = %U32_41
.stk buffer 1 16
  .reg U64 [pos]
  lea %A64_42:A64 = buffer
  mov pos = 16

.bbl while_1
  sub %U64_43:U64 = pos 1
  mov pos = %U64_43
  rem %U32_44:U32 = val 10
  add %U32_45:U32 = 48:U32 %U32_44
  conv %S8_46:S8 = %U32_45
  lea %A64_47:A64 = buffer
  lea %A64_48:A64 = %A64_47 pos
  st %A64_48 0 = %S8_46
  div %U32_49:U32 = val 10
  mov val = %U32_49

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  sub %U64_50:U64 = pos 1
  mov pos = %U64_50
  lea %A64_51:A64 = buffer
  lea %A64_52:A64 = %A64_51 pos
  mov %S8_53:S8 = 45
  st %A64_52 0 = %S8_53
  lea %A64_54:A64 = buffer
  lea %A64_55:A64 = %A64_54 pos
  lea %A64_56:A64 = buffer
  sub %U64_57:U64 = 16:U64 pos
  pusharg %U64_57
  pusharg %A64_55
  pusharg fd
  bsr write
  poparg %S64_58:S64
  mov %out = %S64_58
  pusharg %out
  ret


.fun write_c NORMAL [S64] = [S32 U8]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg c:U8
.stk buffer 1 16
  conv %S8_59:S8 = c
  lea %A64_60:A64 = buffer
  st %A64_60 0 = %S8_59
  lea %A64_61:A64 = buffer
  mov %U64_63:U64 = 1
  pusharg %U64_63
  pusharg %A64_61
  pusharg fd
  bsr write
  poparg %S64_62:S64
  conv %S32_64:S32 = %S64_62
  conv %S64_65:S64 = %S32_64
  mov %out = %S64_65
  pusharg %out
  ret


.fun print_ln NORMAL [] = [A64 U64]

.bbl %start
  poparg s:A64
  poparg n:U64
  mov %S32_67:S32 = 1
  pusharg n
  pusharg s
  pusharg %S32_67
  bsr write
  poparg %S64_66:S64
  mov %S32_69:S32 = 1
  mov %U8_70:U8 = 10
  pusharg %U8_70
  pusharg %S32_69
  bsr write_c
  poparg %S64_68:S64
  ret


.fun print_s_ln NORMAL [] = [A64]

.bbl %start
  poparg s:A64
  mov %S32_72:S32 = 1
  pusharg s
  pusharg %S32_72
  bsr write_s
  poparg %S64_71:S64
  mov %S32_74:S32 = 1
  mov %U8_75:U8 = 10
  pusharg %U8_75
  pusharg %S32_74
  bsr write_c
  poparg %S64_73:S64
  ret


.fun print_d_ln NORMAL [] = [S32]

.bbl %start
  poparg n:S32
  mov %S32_77:S32 = 1
  pusharg n
  pusharg %S32_77
  bsr write_d
  poparg %S64_76:S64
  mov %S32_79:S32 = 1
  mov %U8_80:U8 = 10
  pusharg %U8_80
  pusharg %S32_79
  bsr write_c
  poparg %S64_78:S64
  ret


.fun print_u_ln NORMAL [] = [U32]

.bbl %start
  poparg n:U32
  mov %S32_82:S32 = 1
  pusharg n
  pusharg %S32_82
  bsr write_u
  poparg %S64_81:S64
  mov %S32_84:S32 = 1
  mov %U8_85:U8 = 10
  pusharg %U8_85
  pusharg %S32_84
  bsr write_c
  poparg %S64_83:S64
  ret


.fun print_x_ln NORMAL [] = [U32]

.bbl %start
  poparg n:U32
  mov %S32_87:S32 = 1
  pusharg n
  pusharg %S32_87
  bsr write_x
  poparg %S64_86:S64
  mov %S32_89:S32 = 1
  mov %U8_90:U8 = 10
  pusharg %U8_90
  pusharg %S32_89
  bsr write_c
  poparg %S64_88:S64
  ret


.fun print_c_ln NORMAL [] = [U8]

.bbl %start
  poparg c:U8
  mov %S32_92:S32 = 1
  pusharg c
  pusharg %S32_92
  bsr write_c
  poparg %S64_91:S64
  mov %S32_94:S32 = 1
  mov %U8_95:U8 = 10
  pusharg %U8_95
  pusharg %S32_94
  bsr write_c
  poparg %S64_93:S64
  ret


.fun memset NORMAL [A64] = [A64 S32 U64]
.reg A64 [%out]

.bbl %start
  poparg ptr:A64
  poparg value:S32
  poparg n:U64
  .reg S32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  conv %S8_96:S8 = value
  lea %A64_97:A64 = ptr i
  st %A64_97 0 = %S8_96

.bbl for_1_next
  add %S32_98:S32 = i 1
  mov i = %S32_98

.bbl for_1_cond
  conv %U64_99:U64 = i
  blt %U64_99 n for_1
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
  .reg S32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  lea %A64_100:A64 = src i
  ld %S8_101:S8 = %A64_100 0
  lea %A64_102:A64 = dst i
  st %A64_102 0 = %S8_101

.bbl for_1_next
  add %S32_103:S32 = i 1
  mov i = %S32_103

.bbl for_1_cond
  conv %U64_104:U64 = i
  blt %U64_104 n for_1
  bra for_1_exit

.bbl for_1_exit
  mov %out = dst
  pusharg %out
  ret


.fun abort NORMAL [] = []

.bbl %start
  bsr getpid
  poparg %S32_105:S32
  mov %S32_107:S32 = 3
  pusharg %S32_107
  pusharg %S32_105
  bsr kill
  poparg %S32_106:S32
  mov %S32_108:S32 = 1
  pusharg %S32_108
  bsr exit
  ret


.fun malloc NORMAL [A64] = [U64]
.reg A64 [%out]

.bbl %start
  poparg size:U64
  .reg U64 [page_size]
  shl %S32_109:S32 = 1:S32 20
  conv %U64_110:U64 = %S32_109
  mov page_size = %U64_110
  lea %A64_111:A64 = __static_1__malloc_start
  ld %A64_112:A64 = %A64_111 0
  beq %A64_112 0 if_1_true
  bra if_1_end

.bbl if_1_true
  lea %A64_114:A64 = 0:A64
  pusharg %A64_114
  bsr xbrk
  poparg %A64_113:A64
  lea %A64_115:A64 = __static_1__malloc_start
  st %A64_115 0 = %A64_113
  lea %A64_116:A64 = __static_1__malloc_start
  ld %A64_117:A64 = %A64_116 0
  lea %A64_118:A64 = __static_2__malloc_end
  st %A64_118 0 = %A64_117

.bbl if_1_end
  .reg U64 [rounded_size]
  add %U64_119:U64 = size 15
  div %U64_120:U64 = %U64_119 16
  mul %U64_121:U64 = %U64_120 16
  mov rounded_size = %U64_121
  lea %A64_122:A64 = __static_1__malloc_start
  ld %A64_123:A64 = %A64_122 0
  lea %A64_124:A64 = %A64_123 rounded_size
  lea %A64_125:A64 = __static_2__malloc_end
  ld %A64_126:A64 = %A64_125 0
  blt %A64_126 %A64_124 if_3_true
  bra if_3_end

.bbl if_3_true
  .reg U64 [increment]
  add %U64_127:U64 = rounded_size page_size
  sub %U64_128:U64 = %U64_127 1
  div %U64_129:U64 = %U64_128 page_size
  mul %U64_130:U64 = %U64_129 page_size
  mov increment = %U64_130
  .reg A64 [new_end]
  lea %A64_131:A64 = __static_2__malloc_end
  ld %A64_132:A64 = %A64_131 0
  lea %A64_133:A64 = %A64_132 increment
  mov new_end = %A64_133
  pusharg new_end
  bsr xbrk
  poparg %A64_134:A64
  lea %A64_135:A64 = __static_2__malloc_end
  st %A64_135 0 = %A64_134
  lea %A64_136:A64 = __static_2__malloc_end
  ld %A64_137:A64 = %A64_136 0
  bne %A64_137 new_end if_2_true
  bra if_3_end

.bbl if_2_true
  bsr abort

.bbl if_3_end
  .reg A64 [result]
  lea %A64_138:A64 = __static_1__malloc_start
  ld %A64_139:A64 = %A64_138 0
  mov result = %A64_139
  lea %A64_140:A64 = __static_1__malloc_start
  ld %A64_141:A64 = %A64_140 0
  lea %A64_142:A64 = %A64_141 rounded_size
  lea %A64_143:A64 = __static_1__malloc_start
  st %A64_143 0 = %A64_142
  mov %out = result
  pusharg %out
  ret


.fun free NORMAL [] = [A64]

.bbl %start
  poparg ptr:A64
  ret
