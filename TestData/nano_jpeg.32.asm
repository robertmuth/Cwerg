############################################################
# ../nanojpeg.c
############################################################

.mem __static_4_counts 1 RW
.data 16 [0]



.fun mymemset NORMAL [] = [A32 S32 U32]

.bbl %start
  poparg ptr:A32
  poparg value:S32
  poparg num:U32
  .reg S32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  conv %S8_1:S8 = value
  lea %A32_2:A32 = ptr i
  st %A32_2 0 = %S8_1

.bbl for_1_next
  add %S32_3:S32 = i 1
  mov i = %S32_3

.bbl for_1_cond
  conv %U32_4:U32 = i
  blt %U32_4 num for_1
  bra for_1_exit

.bbl for_1_exit
  ret


.fun mymemcpy NORMAL [] = [A32 A32 U32]

.bbl %start
  poparg destination:A32
  poparg source:A32
  poparg num:U32
  .reg S32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  lea %A32_5:A32 = source i
  ld %S8_6:S8 = %A32_5 0
  lea %A32_7:A32 = destination i
  st %A32_7 0 = %S8_6

.bbl for_1_next
  add %S32_8:S32 = i 1
  mov i = %S32_8

.bbl for_1_cond
  conv %U32_9:U32 = i
  blt %U32_9 num for_1
  bra for_1_exit

.bbl for_1_exit
  ret

.mem nj 4 RW
.data 525000 [0]

.mem njZZ 1 RW
.data 1 [0 1 8 16 9 2 3 10 17 24 32 25 18 11 4 5 12 19 26 33 40 48 41 34 27 20 13 6 7 14 21 28 35 42 49 56 57 50 43 36 29 22 15 23 30 37 44 51 58 59 52 45 38 31 39 46 53 60 61 54 47 55 62 63]


.fun njGetWidth NORMAL [S32] = []
.reg S32 [%out]

.bbl %start
  lea %A32_10:A32 = nj
  lea %A32_11:A32 = %A32_10 16
  ld %S32_12:S32 = %A32_11 0
  mov %out = %S32_12
  pusharg %out
  ret


.fun njGetHeight NORMAL [S32] = []
.reg S32 [%out]

.bbl %start
  lea %A32_13:A32 = nj
  lea %A32_14:A32 = %A32_13 20
  ld %S32_15:S32 = %A32_14 0
  mov %out = %S32_15
  pusharg %out
  ret


.fun njIsColor NORMAL [S32] = []
.reg S32 [%out]

.bbl %start
  lea %A32_16:A32 = nj
  lea %A32_17:A32 = %A32_16 40
  ld %U32_18:U32 = %A32_17 0
  bne %U32_18 1 if_1_true
  bra if_1_false

.bbl if_1_true
  mov %out = 1
  pusharg %out
  ret
  bra if_1_end

.bbl if_1_false
  mov %out = 0
  pusharg %out
  ret

.bbl if_1_end


.fun njGetImage NORMAL [A32] = []
.reg A32 [%out]

.bbl %start
  lea %A32_19:A32 = nj
  lea %A32_20:A32 = %A32_19 40
  ld %U32_21:U32 = %A32_20 0
  beq %U32_21 1 if_1_true
  bra if_1_false

.bbl if_1_true
  lea %A32_22:A32 = nj
  lea %A32_23:A32 = %A32_22 44
  lea %A32_24:A32 = %A32_23 40
  ld %A32_25:A32 = %A32_24 0
  mov %out = %A32_25
  pusharg %out
  ret
  bra if_1_end

.bbl if_1_false
  lea %A32_26:A32 = nj
  lea %A32_27:A32 = %A32_26 524996
  ld %A32_28:A32 = %A32_27 0
  mov %out = %A32_28
  pusharg %out
  ret

.bbl if_1_end


.fun njGetImageSize NORMAL [S32] = []
.reg S32 [%out]

.bbl %start
  lea %A32_29:A32 = nj
  lea %A32_30:A32 = %A32_29 16
  ld %S32_31:S32 = %A32_30 0
  lea %A32_32:A32 = nj
  lea %A32_33:A32 = %A32_32 20
  ld %S32_34:S32 = %A32_33 0
  mul %S32_35:S32 = %S32_31 %S32_34
  conv %U32_36:U32 = %S32_35
  lea %A32_37:A32 = nj
  lea %A32_38:A32 = %A32_37 40
  ld %U32_39:U32 = %A32_38 0
  mul %U32_40:U32 = %U32_36 %U32_39
  conv %S32_41:S32 = %U32_40
  mov %out = %S32_41
  pusharg %out
  ret


.fun njClip NORMAL [U8] = [S32]
.reg U8 [%out]

.bbl %start
  poparg x:S32
  blt x 0 if_2_true
  bra if_2_false

.bbl if_2_true
  mov %out = 0
  pusharg %out
  ret
  bra if_2_end

.bbl if_2_false
  blt 255:S32 x if_1_true
  bra if_2_end

.bbl if_1_true
  mov %out = 255
  pusharg %out
  ret

.bbl if_2_end
  conv %U8_42:U8 = x
  mov %out = %U8_42
  pusharg %out
  ret


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
  lea %A32_43:A32 = blk 16
  ld %S32_44:S32 = %A32_43 0
  shl %S32_45:S32 = %S32_44 11
  mov x1 = %S32_45
  lea %A32_46:A32 = blk 24
  ld %S32_47:S32 = %A32_46 0
  mov x2 = %S32_47
  or %S32_48:S32 = %S32_45 %S32_47
  lea %A32_49:A32 = blk 8
  ld %S32_50:S32 = %A32_49 0
  mov x3 = %S32_50
  or %S32_51:S32 = %S32_48 %S32_50
  lea %A32_52:A32 = blk 4
  ld %S32_53:S32 = %A32_52 0
  mov x4 = %S32_53
  or %S32_54:S32 = %S32_51 %S32_53
  lea %A32_55:A32 = blk 28
  ld %S32_56:S32 = %A32_55 0
  mov x5 = %S32_56
  or %S32_57:S32 = %S32_54 %S32_56
  lea %A32_58:A32 = blk 20
  ld %S32_59:S32 = %A32_58 0
  mov x6 = %S32_59
  or %S32_60:S32 = %S32_57 %S32_59
  lea %A32_61:A32 = blk 12
  ld %S32_62:S32 = %A32_61 0
  mov x7 = %S32_62
  or %S32_63:S32 = %S32_60 %S32_62
  bne %S32_63 0 if_1_end
  bra if_1_true

.bbl if_1_true
  ld %S32_64:S32 = blk 0
  shl %S32_65:S32 = %S32_64 3
  lea %A32_66:A32 = blk 28
  st %A32_66 0 = %S32_65
  lea %A32_67:A32 = blk 24
  st %A32_67 0 = %S32_65
  lea %A32_68:A32 = blk 20
  st %A32_68 0 = %S32_65
  lea %A32_69:A32 = blk 16
  st %A32_69 0 = %S32_65
  lea %A32_70:A32 = blk 12
  st %A32_70 0 = %S32_65
  lea %A32_71:A32 = blk 8
  st %A32_71 0 = %S32_65
  lea %A32_72:A32 = blk 4
  st %A32_72 0 = %S32_65
  st blk 0 = %S32_65
  ret

.bbl if_1_end
  ld %S32_73:S32 = blk 0
  shl %S32_74:S32 = %S32_73 11
  add %S32_75:S32 = %S32_74 128
  mov x0 = %S32_75
  add %S32_76:S32 = x4 x5
  mul %S32_77:S32 = %S32_76 565
  mov x8 = %S32_77
  sub %S32_78:S32 = 2841:S32 565
  mul %S32_79:S32 = x4 %S32_78
  add %S32_80:S32 = x8 %S32_79
  mov x4 = %S32_80
  add %S32_81:S32 = 2841:S32 565
  mul %S32_82:S32 = x5 %S32_81
  sub %S32_83:S32 = x8 %S32_82
  mov x5 = %S32_83
  add %S32_84:S32 = x6 x7
  mul %S32_85:S32 = %S32_84 2408
  mov x8 = %S32_85
  sub %S32_86:S32 = 2408:S32 1609
  mul %S32_87:S32 = x6 %S32_86
  sub %S32_88:S32 = x8 %S32_87
  mov x6 = %S32_88
  add %S32_89:S32 = 2408:S32 1609
  mul %S32_90:S32 = x7 %S32_89
  sub %S32_91:S32 = x8 %S32_90
  mov x7 = %S32_91
  add %S32_92:S32 = x0 x1
  mov x8 = %S32_92
  sub %S32_93:S32 = x0 x1
  mov x0 = %S32_93
  add %S32_94:S32 = x3 x2
  mul %S32_95:S32 = %S32_94 1108
  mov x1 = %S32_95
  add %S32_96:S32 = 2676:S32 1108
  mul %S32_97:S32 = x2 %S32_96
  sub %S32_98:S32 = x1 %S32_97
  mov x2 = %S32_98
  sub %S32_99:S32 = 2676:S32 1108
  mul %S32_100:S32 = x3 %S32_99
  add %S32_101:S32 = x1 %S32_100
  mov x3 = %S32_101
  add %S32_102:S32 = x4 x6
  mov x1 = %S32_102
  sub %S32_103:S32 = x4 x6
  mov x4 = %S32_103
  add %S32_104:S32 = x5 x7
  mov x6 = %S32_104
  sub %S32_105:S32 = x5 x7
  mov x5 = %S32_105
  add %S32_106:S32 = x8 x3
  mov x7 = %S32_106
  sub %S32_107:S32 = x8 x3
  mov x8 = %S32_107
  add %S32_108:S32 = x0 x2
  mov x3 = %S32_108
  sub %S32_109:S32 = x0 x2
  mov x0 = %S32_109
  add %S32_110:S32 = x4 x5
  mul %S32_111:S32 = %S32_110 181
  add %S32_112:S32 = %S32_111 128
  shr %S32_113:S32 = %S32_112 8
  mov x2 = %S32_113
  sub %S32_114:S32 = x4 x5
  mul %S32_115:S32 = %S32_114 181
  add %S32_116:S32 = %S32_115 128
  shr %S32_117:S32 = %S32_116 8
  mov x4 = %S32_117
  add %S32_118:S32 = x7 x1
  shr %S32_119:S32 = %S32_118 8
  st blk 0 = %S32_119
  add %S32_120:S32 = x3 x2
  shr %S32_121:S32 = %S32_120 8
  lea %A32_122:A32 = blk 4
  st %A32_122 0 = %S32_121
  add %S32_123:S32 = x0 x4
  shr %S32_124:S32 = %S32_123 8
  lea %A32_125:A32 = blk 8
  st %A32_125 0 = %S32_124
  add %S32_126:S32 = x8 x6
  shr %S32_127:S32 = %S32_126 8
  lea %A32_128:A32 = blk 12
  st %A32_128 0 = %S32_127
  sub %S32_129:S32 = x8 x6
  shr %S32_130:S32 = %S32_129 8
  lea %A32_131:A32 = blk 16
  st %A32_131 0 = %S32_130
  sub %S32_132:S32 = x0 x4
  shr %S32_133:S32 = %S32_132 8
  lea %A32_134:A32 = blk 20
  st %A32_134 0 = %S32_133
  sub %S32_135:S32 = x3 x2
  shr %S32_136:S32 = %S32_135 8
  lea %A32_137:A32 = blk 24
  st %A32_137 0 = %S32_136
  sub %S32_138:S32 = x7 x1
  shr %S32_139:S32 = %S32_138 8
  lea %A32_140:A32 = blk 28
  st %A32_140 0 = %S32_139
  ret


.fun njColIDCT NORMAL [] = [A32 A32 S32]

.bbl %start
  poparg blk:A32
  poparg out:A32
  poparg stride:S32
  .reg S32 [x0]
  .reg S32 [x1]
  .reg S32 [x2]
  .reg S32 [x3]
  .reg S32 [x4]
  .reg S32 [x5]
  .reg S32 [x6]
  .reg S32 [x7]
  .reg S32 [x8]
  mul %S32_141:S32 = 8:S32 4
  mul %S32_142:S32 = %S32_141 4
  lea %A32_143:A32 = blk %S32_142
  ld %S32_144:S32 = %A32_143 0
  shl %S32_145:S32 = %S32_144 8
  mov x1 = %S32_145
  mul %S32_146:S32 = 8:S32 6
  mul %S32_147:S32 = %S32_146 4
  lea %A32_148:A32 = blk %S32_147
  ld %S32_149:S32 = %A32_148 0
  mov x2 = %S32_149
  or %S32_150:S32 = %S32_145 %S32_149
  mul %S32_151:S32 = 8:S32 2
  mul %S32_152:S32 = %S32_151 4
  lea %A32_153:A32 = blk %S32_152
  ld %S32_154:S32 = %A32_153 0
  mov x3 = %S32_154
  or %S32_155:S32 = %S32_150 %S32_154
  mul %S32_156:S32 = 8:S32 1
  mul %S32_157:S32 = %S32_156 4
  lea %A32_158:A32 = blk %S32_157
  ld %S32_159:S32 = %A32_158 0
  mov x4 = %S32_159
  or %S32_160:S32 = %S32_155 %S32_159
  mul %S32_161:S32 = 8:S32 7
  mul %S32_162:S32 = %S32_161 4
  lea %A32_163:A32 = blk %S32_162
  ld %S32_164:S32 = %A32_163 0
  mov x5 = %S32_164
  or %S32_165:S32 = %S32_160 %S32_164
  mul %S32_166:S32 = 8:S32 5
  mul %S32_167:S32 = %S32_166 4
  lea %A32_168:A32 = blk %S32_167
  ld %S32_169:S32 = %A32_168 0
  mov x6 = %S32_169
  or %S32_170:S32 = %S32_165 %S32_169
  mul %S32_171:S32 = 8:S32 3
  mul %S32_172:S32 = %S32_171 4
  lea %A32_173:A32 = blk %S32_172
  ld %S32_174:S32 = %A32_173 0
  mov x7 = %S32_174
  or %S32_175:S32 = %S32_170 %S32_174
  bne %S32_175 0 if_3_end
  bra if_3_true

.bbl if_3_true
  ld %S32_176:S32 = blk 0
  add %S32_177:S32 = %S32_176 32
  shr %S32_178:S32 = %S32_177 6
  add %S32_179:S32 = %S32_178 128
  pusharg %S32_179
  bsr njClip
  poparg %U8_180:U8
  conv %S32_181:S32 = %U8_180
  mov x1 = %S32_181
  mov x0 = 8
  bra for_1_cond

.bbl for_1
  conv %U8_182:U8 = x1
  st out 0 = %U8_182
  lea %A32_183:A32 = out stride
  mov out = %A32_183

.bbl for_1_next
  sub %S32_184:S32 = x0 1
  mov x0 = %S32_184

.bbl for_1_cond
  bne x0 0 for_1
  bra for_1_exit

.bbl for_1_exit
  ret

.bbl if_3_end
  ld %S32_185:S32 = blk 0
  shl %S32_186:S32 = %S32_185 8
  add %S32_187:S32 = %S32_186 8192
  mov x0 = %S32_187
  add %S32_188:S32 = x4 x5
  mul %S32_189:S32 = %S32_188 565
  add %S32_190:S32 = %S32_189 4
  mov x8 = %S32_190
  sub %S32_191:S32 = 2841:S32 565
  mul %S32_192:S32 = x4 %S32_191
  add %S32_193:S32 = x8 %S32_192
  shr %S32_194:S32 = %S32_193 3
  mov x4 = %S32_194
  add %S32_195:S32 = 2841:S32 565
  mul %S32_196:S32 = x5 %S32_195
  sub %S32_197:S32 = x8 %S32_196
  shr %S32_198:S32 = %S32_197 3
  mov x5 = %S32_198
  add %S32_199:S32 = x6 x7
  mul %S32_200:S32 = %S32_199 2408
  add %S32_201:S32 = %S32_200 4
  mov x8 = %S32_201
  sub %S32_202:S32 = 2408:S32 1609
  mul %S32_203:S32 = x6 %S32_202
  sub %S32_204:S32 = x8 %S32_203
  shr %S32_205:S32 = %S32_204 3
  mov x6 = %S32_205
  add %S32_206:S32 = 2408:S32 1609
  mul %S32_207:S32 = x7 %S32_206
  sub %S32_208:S32 = x8 %S32_207
  shr %S32_209:S32 = %S32_208 3
  mov x7 = %S32_209
  add %S32_210:S32 = x0 x1
  mov x8 = %S32_210
  sub %S32_211:S32 = x0 x1
  mov x0 = %S32_211
  add %S32_212:S32 = x3 x2
  mul %S32_213:S32 = %S32_212 1108
  add %S32_214:S32 = %S32_213 4
  mov x1 = %S32_214
  add %S32_215:S32 = 2676:S32 1108
  mul %S32_216:S32 = x2 %S32_215
  sub %S32_217:S32 = x1 %S32_216
  shr %S32_218:S32 = %S32_217 3
  mov x2 = %S32_218
  sub %S32_219:S32 = 2676:S32 1108
  mul %S32_220:S32 = x3 %S32_219
  add %S32_221:S32 = x1 %S32_220
  shr %S32_222:S32 = %S32_221 3
  mov x3 = %S32_222
  add %S32_223:S32 = x4 x6
  mov x1 = %S32_223
  sub %S32_224:S32 = x4 x6
  mov x4 = %S32_224
  add %S32_225:S32 = x5 x7
  mov x6 = %S32_225
  sub %S32_226:S32 = x5 x7
  mov x5 = %S32_226
  add %S32_227:S32 = x8 x3
  mov x7 = %S32_227
  sub %S32_228:S32 = x8 x3
  mov x8 = %S32_228
  add %S32_229:S32 = x0 x2
  mov x3 = %S32_229
  sub %S32_230:S32 = x0 x2
  mov x0 = %S32_230
  add %S32_231:S32 = x4 x5
  mul %S32_232:S32 = %S32_231 181
  add %S32_233:S32 = %S32_232 128
  shr %S32_234:S32 = %S32_233 8
  mov x2 = %S32_234
  sub %S32_235:S32 = x4 x5
  mul %S32_236:S32 = %S32_235 181
  add %S32_237:S32 = %S32_236 128
  shr %S32_238:S32 = %S32_237 8
  mov x4 = %S32_238
  add %S32_239:S32 = x7 x1
  shr %S32_240:S32 = %S32_239 14
  add %S32_241:S32 = %S32_240 128
  pusharg %S32_241
  bsr njClip
  poparg %U8_242:U8
  st out 0 = %U8_242
  lea %A32_243:A32 = out stride
  mov out = %A32_243
  add %S32_244:S32 = x3 x2
  shr %S32_245:S32 = %S32_244 14
  add %S32_246:S32 = %S32_245 128
  pusharg %S32_246
  bsr njClip
  poparg %U8_247:U8
  st out 0 = %U8_247
  lea %A32_248:A32 = out stride
  mov out = %A32_248
  add %S32_249:S32 = x0 x4
  shr %S32_250:S32 = %S32_249 14
  add %S32_251:S32 = %S32_250 128
  pusharg %S32_251
  bsr njClip
  poparg %U8_252:U8
  st out 0 = %U8_252
  lea %A32_253:A32 = out stride
  mov out = %A32_253
  add %S32_254:S32 = x8 x6
  shr %S32_255:S32 = %S32_254 14
  add %S32_256:S32 = %S32_255 128
  pusharg %S32_256
  bsr njClip
  poparg %U8_257:U8
  st out 0 = %U8_257
  lea %A32_258:A32 = out stride
  mov out = %A32_258
  sub %S32_259:S32 = x8 x6
  shr %S32_260:S32 = %S32_259 14
  add %S32_261:S32 = %S32_260 128
  pusharg %S32_261
  bsr njClip
  poparg %U8_262:U8
  st out 0 = %U8_262
  lea %A32_263:A32 = out stride
  mov out = %A32_263
  sub %S32_264:S32 = x0 x4
  shr %S32_265:S32 = %S32_264 14
  add %S32_266:S32 = %S32_265 128
  pusharg %S32_266
  bsr njClip
  poparg %U8_267:U8
  st out 0 = %U8_267
  lea %A32_268:A32 = out stride
  mov out = %A32_268
  sub %S32_269:S32 = x3 x2
  shr %S32_270:S32 = %S32_269 14
  add %S32_271:S32 = %S32_270 128
  pusharg %S32_271
  bsr njClip
  poparg %U8_272:U8
  st out 0 = %U8_272
  lea %A32_273:A32 = out stride
  mov out = %A32_273
  sub %S32_274:S32 = x7 x1
  shr %S32_275:S32 = %S32_274 14
  add %S32_276:S32 = %S32_275 128
  pusharg %S32_276
  bsr njClip
  poparg %U8_277:U8
  st out 0 = %U8_277
  ret


.fun __static_1_njShowBits NORMAL [S32] = [S32]
.reg S32 [%out]

.bbl %start
  poparg bits:S32
  .reg U8 [newbyte]
  bne bits 0 if_2_end
  bra if_2_true

.bbl if_2_true
  mov %out = 0
  pusharg %out
  ret

.bbl if_2_end
  bra while_1_cond

.bbl while_1
  lea %A32_278:A32 = nj
  lea %A32_279:A32 = %A32_278 8
  ld %S32_280:S32 = %A32_279 0
  ble %S32_280 0 if_3_true
  bra if_3_end

.bbl if_3_true
  lea %A32_281:A32 = nj
  lea %A32_282:A32 = %A32_281 524728
  ld %S32_283:S32 = %A32_282 0
  shl %S32_284:S32 = %S32_283 8
  or %S32_285:S32 = %S32_284 255
  lea %A32_286:A32 = nj
  lea %A32_287:A32 = %A32_286 524728
  st %A32_287 0 = %S32_285
  lea %A32_288:A32 = nj
  lea %A32_289:A32 = %A32_288 524732
  ld %S32_290:S32 = %A32_289 0
  add %S32_291:S32 = %S32_290 8
  lea %A32_292:A32 = nj
  lea %A32_293:A32 = %A32_292 524732
  st %A32_293 0 = %S32_291
  bra while_1_cond

.bbl if_3_end
  lea %A32_294:A32 = nj
  lea %A32_295:A32 = %A32_294 4
  ld %A32_296:A32 = %A32_295 0
  ld %U8_297:U8 = %A32_296 0
  mov newbyte = %U8_297
  lea %A32_298:A32 = nj
  lea %A32_299:A32 = %A32_298 4
  ld %A32_300:A32 = %A32_299 0
  lea %A32_301:A32 = %A32_300 1
  lea %A32_302:A32 = nj
  lea %A32_303:A32 = %A32_302 4
  st %A32_303 0 = %A32_301
  lea %A32_304:A32 = nj
  lea %A32_305:A32 = %A32_304 8
  ld %S32_306:S32 = %A32_305 0
  sub %S32_307:S32 = %S32_306 1
  lea %A32_308:A32 = nj
  lea %A32_309:A32 = %A32_308 8
  st %A32_309 0 = %S32_307
  lea %A32_310:A32 = nj
  lea %A32_311:A32 = %A32_310 524732
  ld %S32_312:S32 = %A32_311 0
  add %S32_313:S32 = %S32_312 8
  lea %A32_314:A32 = nj
  lea %A32_315:A32 = %A32_314 524732
  st %A32_315 0 = %S32_313
  lea %A32_316:A32 = nj
  lea %A32_317:A32 = %A32_316 524728
  ld %S32_318:S32 = %A32_317 0
  shl %S32_319:S32 = %S32_318 8
  conv %S32_320:S32 = newbyte
  or %S32_321:S32 = %S32_319 %S32_320
  lea %A32_322:A32 = nj
  lea %A32_323:A32 = %A32_322 524728
  st %A32_323 0 = %S32_321
  conv %S32_324:S32 = newbyte
  beq %S32_324 255 if_6_true
  bra while_1_cond

.bbl if_6_true
  lea %A32_325:A32 = nj
  lea %A32_326:A32 = %A32_325 8
  ld %S32_327:S32 = %A32_326 0
  bne %S32_327 0 if_5_true
  bra if_5_false

.bbl if_5_true
  .reg U8 [marker]
  lea %A32_328:A32 = nj
  lea %A32_329:A32 = %A32_328 4
  ld %A32_330:A32 = %A32_329 0
  ld %U8_331:U8 = %A32_330 0
  mov marker = %U8_331
  lea %A32_332:A32 = nj
  lea %A32_333:A32 = %A32_332 4
  ld %A32_334:A32 = %A32_333 0
  lea %A32_335:A32 = %A32_334 1
  lea %A32_336:A32 = nj
  lea %A32_337:A32 = %A32_336 4
  st %A32_337 0 = %A32_335
  lea %A32_338:A32 = nj
  lea %A32_339:A32 = %A32_338 8
  ld %S32_340:S32 = %A32_339 0
  sub %S32_341:S32 = %S32_340 1
  lea %A32_342:A32 = nj
  lea %A32_343:A32 = %A32_342 8
  st %A32_343 0 = %S32_341
  blt 255:U8 marker switch_344_default
  .jtb switch_344_tab  256 switch_344_default [0 switch_344_0 255 switch_344_255 217 switch_344_217]
  switch marker switch_344_tab
.bbl switch_344_0
.bbl switch_344_255
  bra switch_344_end
.bbl switch_344_217
  lea %A32_345:A32 = nj
  lea %A32_346:A32 = %A32_345 8
  mov %S32_347:S32 = 0
  st %A32_346 0 = %S32_347
  bra switch_344_end
.bbl switch_344_default
  conv %S32_348:S32 = marker
  and %S32_349:S32 = %S32_348 248
  bne %S32_349 208 if_4_true
  bra if_4_false

.bbl if_4_true
  lea %A32_350:A32 = nj
  mov %S32_351:S32 = 5
  st %A32_350 0 = %S32_351
  bra if_4_end

.bbl if_4_false
  lea %A32_352:A32 = nj
  lea %A32_353:A32 = %A32_352 524728
  ld %S32_354:S32 = %A32_353 0
  shl %S32_355:S32 = %S32_354 8
  conv %S32_356:S32 = marker
  or %S32_357:S32 = %S32_355 %S32_356
  lea %A32_358:A32 = nj
  lea %A32_359:A32 = %A32_358 524728
  st %A32_359 0 = %S32_357
  lea %A32_360:A32 = nj
  lea %A32_361:A32 = %A32_360 524732
  ld %S32_362:S32 = %A32_361 0
  add %S32_363:S32 = %S32_362 8
  lea %A32_364:A32 = nj
  lea %A32_365:A32 = %A32_364 524732
  st %A32_365 0 = %S32_363

.bbl if_4_end

.bbl switch_344_end
  bra while_1_cond

.bbl if_5_false
  lea %A32_366:A32 = nj
  mov %S32_367:S32 = 5
  st %A32_366 0 = %S32_367

.bbl while_1_cond
  lea %A32_368:A32 = nj
  lea %A32_369:A32 = %A32_368 524732
  ld %S32_370:S32 = %A32_369 0
  blt %S32_370 bits while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_371:A32 = nj
  lea %A32_372:A32 = %A32_371 524728
  ld %S32_373:S32 = %A32_372 0
  lea %A32_374:A32 = nj
  lea %A32_375:A32 = %A32_374 524732
  ld %S32_376:S32 = %A32_375 0
  sub %S32_377:S32 = %S32_376 bits
  shr %S32_378:S32 = %S32_373 %S32_377
  shl %S32_379:S32 = 1:S32 bits
  sub %S32_380:S32 = %S32_379 1
  and %S32_381:S32 = %S32_378 %S32_380
  mov %out = %S32_381
  pusharg %out
  ret


.fun njSkipBits NORMAL [] = [S32]

.bbl %start
  poparg bits:S32
  lea %A32_382:A32 = nj
  lea %A32_383:A32 = %A32_382 524732
  ld %S32_384:S32 = %A32_383 0
  blt %S32_384 bits if_1_true
  bra if_1_end

.bbl if_1_true
  pusharg bits
  bsr __static_1_njShowBits
  poparg %S32_385:S32

.bbl if_1_end
  lea %A32_386:A32 = nj
  lea %A32_387:A32 = %A32_386 524732
  ld %S32_388:S32 = %A32_387 0
  sub %S32_389:S32 = %S32_388 bits
  lea %A32_390:A32 = nj
  lea %A32_391:A32 = %A32_390 524732
  st %A32_391 0 = %S32_389
  ret


.fun njGetBits NORMAL [S32] = [S32]
.reg S32 [%out]

.bbl %start
  poparg bits:S32
  .reg S32 [res]
  pusharg bits
  bsr __static_1_njShowBits
  poparg %S32_392:S32
  mov res = %S32_392
  pusharg bits
  bsr njSkipBits
  mov %out = res
  pusharg %out
  ret


.fun njByteAlign NORMAL [] = []

.bbl %start
  lea %A32_393:A32 = nj
  lea %A32_394:A32 = %A32_393 524732
  ld %S32_395:S32 = %A32_394 0
  and %S32_396:S32 = %S32_395 248
  lea %A32_397:A32 = nj
  lea %A32_398:A32 = %A32_397 524732
  st %A32_398 0 = %S32_396
  ret


.fun __static_2_njSkip NORMAL [] = [S32]

.bbl %start
  poparg count:S32
  lea %A32_399:A32 = nj
  lea %A32_400:A32 = %A32_399 4
  ld %A32_401:A32 = %A32_400 0
  lea %A32_402:A32 = %A32_401 count
  lea %A32_403:A32 = nj
  lea %A32_404:A32 = %A32_403 4
  st %A32_404 0 = %A32_402
  lea %A32_405:A32 = nj
  lea %A32_406:A32 = %A32_405 8
  ld %S32_407:S32 = %A32_406 0
  sub %S32_408:S32 = %S32_407 count
  lea %A32_409:A32 = nj
  lea %A32_410:A32 = %A32_409 8
  st %A32_410 0 = %S32_408
  lea %A32_411:A32 = nj
  lea %A32_412:A32 = %A32_411 12
  ld %S32_413:S32 = %A32_412 0
  sub %S32_414:S32 = %S32_413 count
  lea %A32_415:A32 = nj
  lea %A32_416:A32 = %A32_415 12
  st %A32_416 0 = %S32_414
  lea %A32_417:A32 = nj
  lea %A32_418:A32 = %A32_417 8
  ld %S32_419:S32 = %A32_418 0
  blt %S32_419 0 if_1_true
  bra if_1_end

.bbl if_1_true
  lea %A32_420:A32 = nj
  mov %S32_421:S32 = 5
  st %A32_420 0 = %S32_421

.bbl if_1_end
  ret


.fun njDecode16 NORMAL [U16] = [A32]
.reg U16 [%out]

.bbl %start
  poparg pos:A32
  ld %U8_422:U8 = pos 0
  conv %S32_423:S32 = %U8_422
  shl %S32_424:S32 = %S32_423 8
  lea %A32_425:A32 = pos 1
  ld %U8_426:U8 = %A32_425 0
  conv %S32_427:S32 = %U8_426
  or %S32_428:S32 = %S32_424 %S32_427
  conv %U16_429:U16 = %S32_428
  mov %out = %U16_429
  pusharg %out
  ret


.fun __static_3_njDecodeLength NORMAL [] = []

.bbl %start
  lea %A32_430:A32 = nj
  lea %A32_431:A32 = %A32_430 8
  ld %S32_432:S32 = %A32_431 0
  blt %S32_432 2 while_1
  bra if_4_end

.bbl while_1
  lea %A32_433:A32 = nj
  mov %S32_434:S32 = 5
  st %A32_433 0 = %S32_434
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra if_4_end

.bbl if_4_end
  lea %A32_435:A32 = nj
  lea %A32_436:A32 = %A32_435 4
  ld %A32_437:A32 = %A32_436 0
  pusharg %A32_437
  bsr njDecode16
  poparg %U16_438:U16
  conv %S32_439:S32 = %U16_438
  lea %A32_440:A32 = nj
  lea %A32_441:A32 = %A32_440 12
  st %A32_441 0 = %S32_439
  lea %A32_442:A32 = nj
  lea %A32_443:A32 = %A32_442 12
  ld %S32_444:S32 = %A32_443 0
  lea %A32_445:A32 = nj
  lea %A32_446:A32 = %A32_445 8
  ld %S32_447:S32 = %A32_446 0
  blt %S32_447 %S32_444 while_2
  bra if_6_end

.bbl while_2
  lea %A32_448:A32 = nj
  mov %S32_449:S32 = 5
  st %A32_448 0 = %S32_449
  ret

.bbl while_2_cond
  bne 0:S32 0 while_2
  bra if_6_end

.bbl if_6_end
  mov %S32_450:S32 = 2
  pusharg %S32_450
  bsr __static_2_njSkip
  ret


.fun njSkipMarker NORMAL [] = []

.bbl %start
  bsr __static_3_njDecodeLength
  lea %A32_451:A32 = nj
  lea %A32_452:A32 = %A32_451 12
  ld %S32_453:S32 = %A32_452 0
  pusharg %S32_453
  bsr __static_2_njSkip
  ret


.fun njDecodeSOF NORMAL [] = []

.bbl %start
  .reg S32 [i]
  .reg S32 [ssxmax]
  mov ssxmax = 0
  .reg S32 [ssymax]
  mov ssymax = 0
  .reg A32 [c]
  bsr __static_3_njDecodeLength

.bbl while_1
  lea %A32_454:A32 = nj
  lea %A32_455:A32 = %A32_454 0
  ld %S32_456:S32 = %A32_455 0
  bne %S32_456 0 if_17_true
  bra while_1_cond

.bbl if_17_true
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_457:A32 = nj
  lea %A32_458:A32 = %A32_457 12
  ld %S32_459:S32 = %A32_458 0
  blt %S32_459 9 while_2
  bra if_20_end

.bbl while_2
  lea %A32_460:A32 = nj
  mov %S32_461:S32 = 5
  st %A32_460 0 = %S32_461
  ret

.bbl while_2_cond
  bne 0:S32 0 while_2
  bra if_20_end

.bbl if_20_end
  lea %A32_462:A32 = nj
  lea %A32_463:A32 = %A32_462 4
  ld %A32_464:A32 = %A32_463 0
  ld %U8_465:U8 = %A32_464 0
  conv %S32_466:S32 = %U8_465
  bne %S32_466 8 while_3
  bra if_22_end

.bbl while_3
  lea %A32_467:A32 = nj
  mov %S32_468:S32 = 2
  st %A32_467 0 = %S32_468
  ret

.bbl while_3_cond
  bne 0:S32 0 while_3
  bra if_22_end

.bbl if_22_end
  lea %A32_469:A32 = nj
  lea %A32_470:A32 = %A32_469 4
  ld %A32_471:A32 = %A32_470 0
  lea %A32_472:A32 = %A32_471 1
  pusharg %A32_472
  bsr njDecode16
  poparg %U16_473:U16
  conv %S32_474:S32 = %U16_473
  lea %A32_475:A32 = nj
  lea %A32_476:A32 = %A32_475 20
  st %A32_476 0 = %S32_474
  lea %A32_477:A32 = nj
  lea %A32_478:A32 = %A32_477 4
  ld %A32_479:A32 = %A32_478 0
  lea %A32_480:A32 = %A32_479 3
  pusharg %A32_480
  bsr njDecode16
  poparg %U16_481:U16
  conv %S32_482:S32 = %U16_481
  lea %A32_483:A32 = nj
  lea %A32_484:A32 = %A32_483 16
  st %A32_484 0 = %S32_482
  lea %A32_485:A32 = nj
  lea %A32_486:A32 = %A32_485 16
  ld %S32_487:S32 = %A32_486 0
  bne %S32_487 0 branch_50
  bra while_4

.bbl branch_50
  lea %A32_488:A32 = nj
  lea %A32_489:A32 = %A32_488 20
  ld %S32_490:S32 = %A32_489 0
  bne %S32_490 0 if_24_end
  bra while_4

.bbl while_4
  lea %A32_491:A32 = nj
  mov %S32_492:S32 = 5
  st %A32_491 0 = %S32_492
  ret

.bbl while_4_cond
  bne 0:S32 0 while_4
  bra if_24_end

.bbl if_24_end
  lea %A32_493:A32 = nj
  lea %A32_494:A32 = %A32_493 4
  ld %A32_495:A32 = %A32_494 0
  lea %A32_496:A32 = %A32_495 5
  ld %U8_497:U8 = %A32_496 0
  conv %U32_498:U32 = %U8_497
  lea %A32_499:A32 = nj
  lea %A32_500:A32 = %A32_499 40
  st %A32_500 0 = %U32_498
  mov %S32_501:S32 = 6
  pusharg %S32_501
  bsr __static_2_njSkip
  lea %A32_502:A32 = nj
  lea %A32_503:A32 = %A32_502 40
  ld %U32_504:U32 = %A32_503 0
  blt 3:U32 %U32_504 switch_505_default
  .jtb switch_505_tab  4 switch_505_default [1 switch_505_1 3 switch_505_3]
  switch %U32_504 switch_505_tab
.bbl switch_505_1
.bbl switch_505_3
  bra switch_505_end
.bbl switch_505_default

.bbl while_5
  lea %A32_506:A32 = nj
  mov %S32_507:S32 = 2
  st %A32_506 0 = %S32_507
  ret

.bbl while_5_cond
  bne 0:S32 0 while_5
  bra while_5_exit

.bbl while_5_exit

.bbl switch_505_end
  lea %A32_508:A32 = nj
  lea %A32_509:A32 = %A32_508 12
  ld %S32_510:S32 = %A32_509 0
  conv %U32_511:U32 = %S32_510
  lea %A32_512:A32 = nj
  lea %A32_513:A32 = %A32_512 40
  ld %U32_514:U32 = %A32_513 0
  mul %U32_515:U32 = %U32_514 3
  blt %U32_511 %U32_515 while_6
  bra if_27_end

.bbl while_6
  lea %A32_516:A32 = nj
  mov %S32_517:S32 = 5
  st %A32_516 0 = %S32_517
  ret

.bbl while_6_cond
  bne 0:S32 0 while_6
  bra if_27_end

.bbl if_27_end
  mov i = 0
  lea %A32_518:A32 = nj
  lea %A32_519:A32 = %A32_518 44
  mov c = %A32_519
  bra for_15_cond

.bbl for_15
  lea %A32_520:A32 = nj
  lea %A32_521:A32 = %A32_520 4
  ld %A32_522:A32 = %A32_521 0
  ld %U8_523:U8 = %A32_522 0
  conv %S32_524:S32 = %U8_523
  st c 0 = %S32_524
  lea %A32_525:A32 = nj
  lea %A32_526:A32 = %A32_525 4
  ld %A32_527:A32 = %A32_526 0
  lea %A32_528:A32 = %A32_527 1
  ld %U8_529:U8 = %A32_528 0
  conv %S32_530:S32 = %U8_529
  shr %S32_531:S32 = %S32_530 4
  lea %A32_532:A32 = c 4
  st %A32_532 0 = %S32_531
  bne %S32_531 0 if_29_end
  bra while_7

.bbl while_7
  lea %A32_533:A32 = nj
  mov %S32_534:S32 = 5
  st %A32_533 0 = %S32_534
  ret

.bbl while_7_cond
  bne 0:S32 0 while_7
  bra if_29_end

.bbl if_29_end
  lea %A32_535:A32 = c 4
  ld %S32_536:S32 = %A32_535 0
  lea %A32_537:A32 = c 4
  ld %S32_538:S32 = %A32_537 0
  sub %S32_539:S32 = %S32_538 1
  and %S32_540:S32 = %S32_536 %S32_539
  bne %S32_540 0 while_8
  bra if_31_end

.bbl while_8
  lea %A32_541:A32 = nj
  mov %S32_542:S32 = 2
  st %A32_541 0 = %S32_542
  ret

.bbl while_8_cond
  bne 0:S32 0 while_8
  bra if_31_end

.bbl if_31_end
  lea %A32_543:A32 = nj
  lea %A32_544:A32 = %A32_543 4
  ld %A32_545:A32 = %A32_544 0
  lea %A32_546:A32 = %A32_545 1
  ld %U8_547:U8 = %A32_546 0
  conv %S32_548:S32 = %U8_547
  and %S32_549:S32 = %S32_548 15
  lea %A32_550:A32 = c 8
  st %A32_550 0 = %S32_549
  bne %S32_549 0 if_33_end
  bra while_9

.bbl while_9
  lea %A32_551:A32 = nj
  mov %S32_552:S32 = 5
  st %A32_551 0 = %S32_552
  ret

.bbl while_9_cond
  bne 0:S32 0 while_9
  bra if_33_end

.bbl if_33_end
  lea %A32_553:A32 = c 8
  ld %S32_554:S32 = %A32_553 0
  lea %A32_555:A32 = c 8
  ld %S32_556:S32 = %A32_555 0
  sub %S32_557:S32 = %S32_556 1
  and %S32_558:S32 = %S32_554 %S32_557
  bne %S32_558 0 while_10
  bra if_35_end

.bbl while_10
  lea %A32_559:A32 = nj
  mov %S32_560:S32 = 2
  st %A32_559 0 = %S32_560
  ret

.bbl while_10_cond
  bne 0:S32 0 while_10
  bra if_35_end

.bbl if_35_end
  lea %A32_561:A32 = nj
  lea %A32_562:A32 = %A32_561 4
  ld %A32_563:A32 = %A32_562 0
  lea %A32_564:A32 = %A32_563 2
  ld %U8_565:U8 = %A32_564 0
  conv %S32_566:S32 = %U8_565
  lea %A32_567:A32 = c 24
  st %A32_567 0 = %S32_566
  and %S32_568:S32 = %S32_566 252
  bne %S32_568 0 while_11
  bra if_37_end

.bbl while_11
  lea %A32_569:A32 = nj
  mov %S32_570:S32 = 5
  st %A32_569 0 = %S32_570
  ret

.bbl while_11_cond
  bne 0:S32 0 while_11
  bra if_37_end

.bbl if_37_end
  mov %S32_571:S32 = 3
  pusharg %S32_571
  bsr __static_2_njSkip
  lea %A32_572:A32 = nj
  lea %A32_573:A32 = %A32_572 176
  ld %S32_574:S32 = %A32_573 0
  lea %A32_575:A32 = c 24
  ld %S32_576:S32 = %A32_575 0
  shl %S32_577:S32 = 1:S32 %S32_576
  or %S32_578:S32 = %S32_574 %S32_577
  lea %A32_579:A32 = nj
  lea %A32_580:A32 = %A32_579 176
  st %A32_580 0 = %S32_578
  lea %A32_581:A32 = c 4
  ld %S32_582:S32 = %A32_581 0
  blt ssxmax %S32_582 if_38_true
  bra if_38_end

.bbl if_38_true
  lea %A32_583:A32 = c 4
  ld %S32_584:S32 = %A32_583 0
  mov ssxmax = %S32_584

.bbl if_38_end
  lea %A32_585:A32 = c 8
  ld %S32_586:S32 = %A32_585 0
  blt ssymax %S32_586 if_39_true
  bra for_15_next

.bbl if_39_true
  lea %A32_587:A32 = c 8
  ld %S32_588:S32 = %A32_587 0
  mov ssymax = %S32_588

.bbl for_15_next
  add %S32_589:S32 = i 1
  mov i = %S32_589
  lea %A32_590:A32 = c 44
  mov c = %A32_590

.bbl for_15_cond
  conv %U32_591:U32 = i
  lea %A32_592:A32 = nj
  lea %A32_593:A32 = %A32_592 40
  ld %U32_594:U32 = %A32_593 0
  blt %U32_591 %U32_594 for_15
  bra for_15_exit

.bbl for_15_exit
  lea %A32_595:A32 = nj
  lea %A32_596:A32 = %A32_595 40
  ld %U32_597:U32 = %A32_596 0
  beq %U32_597 1 if_41_true
  bra if_41_end

.bbl if_41_true
  lea %A32_598:A32 = nj
  lea %A32_599:A32 = %A32_598 44
  mov c = %A32_599
  mov ssymax = 1
  mov ssxmax = 1
  lea %A32_600:A32 = c 8
  mov %S32_601:S32 = 1
  st %A32_600 0 = %S32_601
  lea %A32_602:A32 = c 4
  st %A32_602 0 = %S32_601

.bbl if_41_end
  shl %S32_603:S32 = ssxmax 3
  lea %A32_604:A32 = nj
  lea %A32_605:A32 = %A32_604 32
  st %A32_605 0 = %S32_603
  shl %S32_606:S32 = ssymax 3
  lea %A32_607:A32 = nj
  lea %A32_608:A32 = %A32_607 36
  st %A32_608 0 = %S32_606
  lea %A32_609:A32 = nj
  lea %A32_610:A32 = %A32_609 16
  ld %S32_611:S32 = %A32_610 0
  lea %A32_612:A32 = nj
  lea %A32_613:A32 = %A32_612 32
  ld %S32_614:S32 = %A32_613 0
  add %S32_615:S32 = %S32_611 %S32_614
  sub %S32_616:S32 = %S32_615 1
  lea %A32_617:A32 = nj
  lea %A32_618:A32 = %A32_617 32
  ld %S32_619:S32 = %A32_618 0
  div %S32_620:S32 = %S32_616 %S32_619
  lea %A32_621:A32 = nj
  lea %A32_622:A32 = %A32_621 24
  st %A32_622 0 = %S32_620
  lea %A32_623:A32 = nj
  lea %A32_624:A32 = %A32_623 20
  ld %S32_625:S32 = %A32_624 0
  lea %A32_626:A32 = nj
  lea %A32_627:A32 = %A32_626 36
  ld %S32_628:S32 = %A32_627 0
  add %S32_629:S32 = %S32_625 %S32_628
  sub %S32_630:S32 = %S32_629 1
  lea %A32_631:A32 = nj
  lea %A32_632:A32 = %A32_631 36
  ld %S32_633:S32 = %A32_632 0
  div %S32_634:S32 = %S32_630 %S32_633
  lea %A32_635:A32 = nj
  lea %A32_636:A32 = %A32_635 28
  st %A32_636 0 = %S32_634
  mov i = 0
  lea %A32_637:A32 = nj
  lea %A32_638:A32 = %A32_637 44
  mov c = %A32_638
  bra for_16_cond

.bbl for_16
  lea %A32_639:A32 = nj
  lea %A32_640:A32 = %A32_639 16
  ld %S32_641:S32 = %A32_640 0
  lea %A32_642:A32 = c 4
  ld %S32_643:S32 = %A32_642 0
  mul %S32_644:S32 = %S32_641 %S32_643
  add %S32_645:S32 = %S32_644 ssxmax
  sub %S32_646:S32 = %S32_645 1
  div %S32_647:S32 = %S32_646 ssxmax
  lea %A32_648:A32 = c 12
  st %A32_648 0 = %S32_647
  lea %A32_649:A32 = nj
  lea %A32_650:A32 = %A32_649 20
  ld %S32_651:S32 = %A32_650 0
  lea %A32_652:A32 = c 8
  ld %S32_653:S32 = %A32_652 0
  mul %S32_654:S32 = %S32_651 %S32_653
  add %S32_655:S32 = %S32_654 ssymax
  sub %S32_656:S32 = %S32_655 1
  div %S32_657:S32 = %S32_656 ssymax
  lea %A32_658:A32 = c 16
  st %A32_658 0 = %S32_657
  lea %A32_659:A32 = nj
  lea %A32_660:A32 = %A32_659 24
  ld %S32_661:S32 = %A32_660 0
  lea %A32_662:A32 = c 4
  ld %S32_663:S32 = %A32_662 0
  mul %S32_664:S32 = %S32_661 %S32_663
  shl %S32_665:S32 = %S32_664 3
  lea %A32_666:A32 = c 20
  st %A32_666 0 = %S32_665
  lea %A32_667:A32 = c 12
  ld %S32_668:S32 = %A32_667 0
  blt %S32_668 3 branch_52
  bra branch_51

.bbl branch_52
  lea %A32_669:A32 = c 4
  ld %S32_670:S32 = %A32_669 0
  bne %S32_670 ssxmax while_12
  bra branch_51

.bbl branch_51
  lea %A32_671:A32 = c 16
  ld %S32_672:S32 = %A32_671 0
  blt %S32_672 3 branch_53
  bra if_43_end

.bbl branch_53
  lea %A32_673:A32 = c 8
  ld %S32_674:S32 = %A32_673 0
  bne %S32_674 ssymax while_12
  bra if_43_end

.bbl while_12
  lea %A32_675:A32 = nj
  mov %S32_676:S32 = 2
  st %A32_675 0 = %S32_676
  ret

.bbl while_12_cond
  bne 0:S32 0 while_12
  bra if_43_end

.bbl if_43_end
  lea %A32_677:A32 = c 20
  ld %S32_678:S32 = %A32_677 0
  lea %A32_679:A32 = nj
  lea %A32_680:A32 = %A32_679 28
  ld %S32_681:S32 = %A32_680 0
  mul %S32_682:S32 = %S32_678 %S32_681
  lea %A32_683:A32 = c 8
  ld %S32_684:S32 = %A32_683 0
  mul %S32_685:S32 = %S32_682 %S32_684
  shl %S32_686:S32 = %S32_685 3
  conv %U32_687:U32 = %S32_686
  pusharg %U32_687
  bsr malloc
  poparg %A32_688:A32
  lea %A32_689:A32 = c 40
  st %A32_689 0 = %A32_688
  bne %A32_688 0 for_16_next
  bra while_13

.bbl while_13
  lea %A32_690:A32 = nj
  mov %S32_691:S32 = 3
  st %A32_690 0 = %S32_691
  ret

.bbl while_13_cond
  bne 0:S32 0 while_13
  bra for_16_next

.bbl for_16_next
  add %S32_692:S32 = i 1
  mov i = %S32_692
  lea %A32_693:A32 = c 44
  mov c = %A32_693

.bbl for_16_cond
  conv %U32_694:U32 = i
  lea %A32_695:A32 = nj
  lea %A32_696:A32 = %A32_695 40
  ld %U32_697:U32 = %A32_696 0
  blt %U32_694 %U32_697 for_16
  bra for_16_exit

.bbl for_16_exit
  lea %A32_698:A32 = nj
  lea %A32_699:A32 = %A32_698 40
  ld %U32_700:U32 = %A32_699 0
  beq %U32_700 3 if_49_true
  bra if_49_end

.bbl if_49_true
  lea %A32_701:A32 = nj
  lea %A32_702:A32 = %A32_701 16
  ld %S32_703:S32 = %A32_702 0
  lea %A32_704:A32 = nj
  lea %A32_705:A32 = %A32_704 20
  ld %S32_706:S32 = %A32_705 0
  mul %S32_707:S32 = %S32_703 %S32_706
  conv %U32_708:U32 = %S32_707
  lea %A32_709:A32 = nj
  lea %A32_710:A32 = %A32_709 40
  ld %U32_711:U32 = %A32_710 0
  mul %U32_712:U32 = %U32_708 %U32_711
  pusharg %U32_712
  bsr malloc
  poparg %A32_713:A32
  lea %A32_714:A32 = nj
  lea %A32_715:A32 = %A32_714 524996
  st %A32_715 0 = %A32_713
  lea %A32_716:A32 = nj
  lea %A32_717:A32 = %A32_716 524996
  ld %A32_718:A32 = %A32_717 0
  bne %A32_718 0 if_49_end
  bra while_14

.bbl while_14
  lea %A32_719:A32 = nj
  mov %S32_720:S32 = 3
  st %A32_719 0 = %S32_720
  ret

.bbl while_14_cond
  bne 0:S32 0 while_14
  bra if_49_end

.bbl if_49_end
  lea %A32_721:A32 = nj
  lea %A32_722:A32 = %A32_721 12
  ld %S32_723:S32 = %A32_722 0
  pusharg %S32_723
  bsr __static_2_njSkip
  ret


.fun njDecodeDHT NORMAL [] = []

.bbl %start
  .reg S32 [codelen]
  .reg S32 [currcnt]
  .reg S32 [remain]
  .reg S32 [spread]
  .reg S32 [i]
  .reg S32 [j]
  .reg A32 [vlc]
  bsr __static_3_njDecodeLength

.bbl while_1
  lea %A32_724:A32 = nj
  lea %A32_725:A32 = %A32_724 0
  ld %S32_726:S32 = %A32_725 0
  bne %S32_726 0 if_13_true
  bra while_1_cond

.bbl if_13_true
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra while_1_exit

.bbl while_1_exit
  bra while_7_cond

.bbl while_7
  lea %A32_727:A32 = nj
  lea %A32_728:A32 = %A32_727 4
  ld %A32_729:A32 = %A32_728 0
  ld %U8_730:U8 = %A32_729 0
  conv %S32_731:S32 = %U8_730
  mov i = %S32_731
  and %S32_732:S32 = i 236
  bne %S32_732 0 while_2
  bra if_16_end

.bbl while_2
  lea %A32_733:A32 = nj
  mov %S32_734:S32 = 5
  st %A32_733 0 = %S32_734
  ret

.bbl while_2_cond
  bne 0:S32 0 while_2
  bra if_16_end

.bbl if_16_end
  and %S32_735:S32 = i 2
  bne %S32_735 0 while_3
  bra if_18_end

.bbl while_3
  lea %A32_736:A32 = nj
  mov %S32_737:S32 = 2
  st %A32_736 0 = %S32_737
  ret

.bbl while_3_cond
  bne 0:S32 0 while_3
  bra if_18_end

.bbl if_18_end
  shr %S32_738:S32 = i 3
  or %S32_739:S32 = i %S32_738
  and %S32_740:S32 = %S32_739 3
  mov i = %S32_740
  mov codelen = 1
  bra for_9_cond

.bbl for_9
  lea %A32_741:A32 = nj
  lea %A32_742:A32 = %A32_741 4
  ld %A32_743:A32 = %A32_742 0
  lea %A32_744:A32 = %A32_743 codelen
  ld %U8_745:U8 = %A32_744 0
  lea %A32_746:A32 = __static_4_counts
  sub %S32_747:S32 = codelen 1
  lea %A32_748:A32 = %A32_746 %S32_747
  st %A32_748 0 = %U8_745

.bbl for_9_next
  add %S32_749:S32 = codelen 1
  mov codelen = %S32_749

.bbl for_9_cond
  ble codelen 16 for_9
  bra for_9_exit

.bbl for_9_exit
  mov %S32_750:S32 = 17
  pusharg %S32_750
  bsr __static_2_njSkip
  lea %A32_751:A32 = nj
  lea %A32_752:A32 = %A32_751 440
  mul %S32_753:S32 = i 65536
  mul %S32_754:S32 = %S32_753 2
  lea %A32_755:A32 = %A32_752 %S32_754
  mov vlc = %A32_755
  mov spread = 65536
  mov remain = 65536
  mov codelen = 1
  bra for_12_cond

.bbl for_12
  shr %S32_756:S32 = spread 1
  mov spread = %S32_756
  lea %A32_757:A32 = __static_4_counts
  sub %S32_758:S32 = codelen 1
  lea %A32_759:A32 = %A32_757 %S32_758
  ld %U8_760:U8 = %A32_759 0
  conv %S32_761:S32 = %U8_760
  mov currcnt = %S32_761
  bne currcnt 0 if_20_end
  bra for_12_next

.bbl if_20_end
  lea %A32_762:A32 = nj
  lea %A32_763:A32 = %A32_762 12
  ld %S32_764:S32 = %A32_763 0
  blt %S32_764 currcnt while_4
  bra if_22_end

.bbl while_4
  lea %A32_765:A32 = nj
  mov %S32_766:S32 = 5
  st %A32_765 0 = %S32_766
  ret

.bbl while_4_cond
  bne 0:S32 0 while_4
  bra if_22_end

.bbl if_22_end
  sub %S32_767:S32 = 16:S32 codelen
  shl %S32_768:S32 = currcnt %S32_767
  sub %S32_769:S32 = remain %S32_768
  mov remain = %S32_769
  blt remain 0 while_5
  bra if_24_end

.bbl while_5
  lea %A32_770:A32 = nj
  mov %S32_771:S32 = 5
  st %A32_770 0 = %S32_771
  ret

.bbl while_5_cond
  bne 0:S32 0 while_5
  bra if_24_end

.bbl if_24_end
  mov i = 0
  bra for_11_cond

.bbl for_11
  .reg U8 [code]
  lea %A32_772:A32 = nj
  lea %A32_773:A32 = %A32_772 4
  ld %A32_774:A32 = %A32_773 0
  lea %A32_775:A32 = %A32_774 i
  ld %U8_776:U8 = %A32_775 0
  mov code = %U8_776
  mov j = spread
  bra for_10_cond

.bbl for_10
  conv %U8_777:U8 = codelen
  st vlc 0 = %U8_777
  lea %A32_778:A32 = vlc 1
  st %A32_778 0 = code
  lea %A32_779:A32 = vlc 2
  mov vlc = %A32_779

.bbl for_10_next
  sub %S32_780:S32 = j 1
  mov j = %S32_780

.bbl for_10_cond
  bne j 0 for_10
  bra for_11_next

.bbl for_11_next
  add %S32_781:S32 = i 1
  mov i = %S32_781

.bbl for_11_cond
  blt i currcnt for_11
  bra for_11_exit

.bbl for_11_exit
  pusharg currcnt
  bsr __static_2_njSkip

.bbl for_12_next
  add %S32_782:S32 = codelen 1
  mov codelen = %S32_782

.bbl for_12_cond
  ble codelen 16 for_12
  bra for_12_exit

.bbl for_12_exit
  bra while_6_cond

.bbl while_6
  sub %S32_783:S32 = remain 1
  mov remain = %S32_783
  mov %U8_784:U8 = 0
  st vlc 0 = %U8_784
  lea %A32_785:A32 = vlc 2
  mov vlc = %A32_785

.bbl while_6_cond
  bne remain 0 while_6
  bra while_7_cond

.bbl while_7_cond
  lea %A32_786:A32 = nj
  lea %A32_787:A32 = %A32_786 12
  ld %S32_788:S32 = %A32_787 0
  ble 17:S32 %S32_788 while_7
  bra while_7_exit

.bbl while_7_exit
  lea %A32_789:A32 = nj
  lea %A32_790:A32 = %A32_789 12
  ld %S32_791:S32 = %A32_790 0
  bne %S32_791 0 while_8
  bra if_31_end

.bbl while_8
  lea %A32_792:A32 = nj
  mov %S32_793:S32 = 5
  st %A32_792 0 = %S32_793
  ret

.bbl while_8_cond
  bne 0:S32 0 while_8
  bra if_31_end

.bbl if_31_end
  ret


.fun njDecodeDQT NORMAL [] = []

.bbl %start
  .reg S32 [i]
  .reg A32 [t]
  bsr __static_3_njDecodeLength

.bbl while_1
  lea %A32_794:A32 = nj
  lea %A32_795:A32 = %A32_794 0
  ld %S32_796:S32 = %A32_795 0
  bne %S32_796 0 if_6_true
  bra while_1_cond

.bbl if_6_true
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra while_1_exit

.bbl while_1_exit
  bra while_3_cond

.bbl while_3
  lea %A32_797:A32 = nj
  lea %A32_798:A32 = %A32_797 4
  ld %A32_799:A32 = %A32_798 0
  ld %U8_800:U8 = %A32_799 0
  conv %S32_801:S32 = %U8_800
  mov i = %S32_801
  and %S32_802:S32 = i 252
  bne %S32_802 0 while_2
  bra if_9_end

.bbl while_2
  lea %A32_803:A32 = nj
  mov %S32_804:S32 = 5
  st %A32_803 0 = %S32_804
  ret

.bbl while_2_cond
  bne 0:S32 0 while_2
  bra if_9_end

.bbl if_9_end
  lea %A32_805:A32 = nj
  lea %A32_806:A32 = %A32_805 180
  ld %S32_807:S32 = %A32_806 0
  shl %S32_808:S32 = 1:S32 i
  or %S32_809:S32 = %S32_807 %S32_808
  lea %A32_810:A32 = nj
  lea %A32_811:A32 = %A32_810 180
  st %A32_811 0 = %S32_809
  lea %A32_812:A32 = nj
  lea %A32_813:A32 = %A32_812 184
  mul %S32_814:S32 = i 64
  lea %A32_815:A32 = %A32_813 %S32_814
  mov t = %A32_815
  mov i = 0
  bra for_5_cond

.bbl for_5
  lea %A32_816:A32 = nj
  lea %A32_817:A32 = %A32_816 4
  ld %A32_818:A32 = %A32_817 0
  add %S32_819:S32 = i 1
  lea %A32_820:A32 = %A32_818 %S32_819
  ld %U8_821:U8 = %A32_820 0
  lea %A32_822:A32 = t i
  st %A32_822 0 = %U8_821

.bbl for_5_next
  add %S32_823:S32 = i 1
  mov i = %S32_823

.bbl for_5_cond
  blt i 64 for_5
  bra for_5_exit

.bbl for_5_exit
  mov %S32_824:S32 = 65
  pusharg %S32_824
  bsr __static_2_njSkip

.bbl while_3_cond
  lea %A32_825:A32 = nj
  lea %A32_826:A32 = %A32_825 12
  ld %S32_827:S32 = %A32_826 0
  ble 65:S32 %S32_827 while_3
  bra while_3_exit

.bbl while_3_exit
  lea %A32_828:A32 = nj
  lea %A32_829:A32 = %A32_828 12
  ld %S32_830:S32 = %A32_829 0
  bne %S32_830 0 while_4
  bra if_13_end

.bbl while_4
  lea %A32_831:A32 = nj
  mov %S32_832:S32 = 5
  st %A32_831 0 = %S32_832
  ret

.bbl while_4_cond
  bne 0:S32 0 while_4
  bra if_13_end

.bbl if_13_end
  ret


.fun njDecodeDRI NORMAL [] = []

.bbl %start
  bsr __static_3_njDecodeLength

.bbl while_1
  lea %A32_833:A32 = nj
  lea %A32_834:A32 = %A32_833 0
  ld %S32_835:S32 = %A32_834 0
  bne %S32_835 0 if_3_true
  bra while_1_cond

.bbl if_3_true
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_836:A32 = nj
  lea %A32_837:A32 = %A32_836 12
  ld %S32_838:S32 = %A32_837 0
  blt %S32_838 2 while_2
  bra if_6_end

.bbl while_2
  lea %A32_839:A32 = nj
  mov %S32_840:S32 = 5
  st %A32_839 0 = %S32_840
  ret

.bbl while_2_cond
  bne 0:S32 0 while_2
  bra if_6_end

.bbl if_6_end
  lea %A32_841:A32 = nj
  lea %A32_842:A32 = %A32_841 4
  ld %A32_843:A32 = %A32_842 0
  pusharg %A32_843
  bsr njDecode16
  poparg %U16_844:U16
  conv %S32_845:S32 = %U16_844
  lea %A32_846:A32 = nj
  lea %A32_847:A32 = %A32_846 524992
  st %A32_847 0 = %S32_845
  lea %A32_848:A32 = nj
  lea %A32_849:A32 = %A32_848 12
  ld %S32_850:S32 = %A32_849 0
  pusharg %S32_850
  bsr __static_2_njSkip
  ret


.fun njGetVLC NORMAL [S32] = [A32 A32]
.reg S32 [%out]

.bbl %start
  poparg vlc:A32
  poparg code:A32
  .reg S32 [value]
  mov %S32_852:S32 = 16
  pusharg %S32_852
  bsr __static_1_njShowBits
  poparg %S32_851:S32
  mov value = %S32_851
  .reg S32 [bits]
  mul %S32_853:S32 = value 2
  lea %A32_854:A32 = vlc %S32_853
  lea %A32_855:A32 = %A32_854 0
  ld %U8_856:U8 = %A32_855 0
  conv %S32_857:S32 = %U8_856
  mov bits = %S32_857
  bne bits 0 if_1_end
  bra if_1_true

.bbl if_1_true
  lea %A32_858:A32 = nj
  mov %S32_859:S32 = 5
  st %A32_858 0 = %S32_859
  mov %out = 0
  pusharg %out
  ret

.bbl if_1_end
  pusharg bits
  bsr njSkipBits
  mul %S32_860:S32 = value 2
  lea %A32_861:A32 = vlc %S32_860
  lea %A32_862:A32 = %A32_861 1
  ld %U8_863:U8 = %A32_862 0
  conv %S32_864:S32 = %U8_863
  mov value = %S32_864
  bne code 0 if_2_true
  bra if_2_end

.bbl if_2_true
  conv %U8_865:U8 = value
  st code 0 = %U8_865

.bbl if_2_end
  and %S32_866:S32 = value 15
  mov bits = %S32_866
  bne bits 0 if_3_end
  bra if_3_true

.bbl if_3_true
  mov %out = 0
  pusharg %out
  ret

.bbl if_3_end
  pusharg bits
  bsr njGetBits
  poparg %S32_867:S32
  mov value = %S32_867
  sub %S32_868:S32 = bits 1
  shl %S32_869:S32 = 1:S32 %S32_868
  blt value %S32_869 if_4_true
  bra if_4_end

.bbl if_4_true
  shl %S32_870:S32 = -1:S32 bits
  add %S32_871:S32 = %S32_870 1
  add %S32_872:S32 = value %S32_871
  mov value = %S32_872

.bbl if_4_end
  mov %out = value
  pusharg %out
  ret


.fun njDecodeBlock NORMAL [] = [A32 A32]

.bbl %start
  poparg c:A32
  poparg out:A32
.stk code 1 1
  lea %A32_873:A32 = code
  mov %U8_874:U8 = 0
  st %A32_873 0 = %U8_874
  .reg S32 [value]
  .reg S32 [coef]
  mov coef = 0
  lea %A32_875:A32 = nj
  lea %A32_876:A32 = %A32_875 524736
  lea %A32_877:A32 = nj
  lea %A32_878:A32 = %A32_877 524736
  mov %S32_879:S32 = 0
  mov %U32_880:U32 = 256
  pusharg %U32_880
  pusharg %S32_879
  pusharg %A32_876
  bsr mymemset
  lea %A32_881:A32 = c 36
  ld %S32_882:S32 = %A32_881 0
  lea %A32_883:A32 = nj
  lea %A32_884:A32 = %A32_883 440
  lea %A32_885:A32 = c 32
  ld %S32_886:S32 = %A32_885 0
  mul %S32_887:S32 = %S32_886 65536
  mul %S32_888:S32 = %S32_887 2
  lea %A32_889:A32 = %A32_884 %S32_888
  lea %A32_891:A32 = 0:A32
  pusharg %A32_891
  pusharg %A32_889
  bsr njGetVLC
  poparg %S32_890:S32
  add %S32_892:S32 = %S32_882 %S32_890
  lea %A32_893:A32 = c 36
  st %A32_893 0 = %S32_892
  lea %A32_894:A32 = c 36
  ld %S32_895:S32 = %A32_894 0
  lea %A32_896:A32 = nj
  lea %A32_897:A32 = %A32_896 184
  lea %A32_898:A32 = c 24
  ld %S32_899:S32 = %A32_898 0
  mul %S32_900:S32 = %S32_899 64
  lea %A32_901:A32 = %A32_897 %S32_900
  ld %U8_902:U8 = %A32_901 0
  conv %S32_903:S32 = %U8_902
  mul %S32_904:S32 = %S32_895 %S32_903
  lea %A32_905:A32 = nj
  lea %A32_906:A32 = %A32_905 524736
  st %A32_906 0 = %S32_904

.bbl while_3
  lea %A32_907:A32 = nj
  lea %A32_908:A32 = %A32_907 440
  lea %A32_909:A32 = c 28
  ld %S32_910:S32 = %A32_909 0
  mul %S32_911:S32 = %S32_910 65536
  mul %S32_912:S32 = %S32_911 2
  lea %A32_913:A32 = %A32_908 %S32_912
  lea %A32_914:A32 = code
  pusharg %A32_914
  pusharg %A32_913
  bsr njGetVLC
  poparg %S32_915:S32
  mov value = %S32_915
  lea %A32_916:A32 = code
  ld %U8_917:U8 = %A32_916 0
  conv %S32_918:S32 = %U8_917
  bne %S32_918 0 if_6_end
  bra while_3_exit

.bbl if_6_end
  lea %A32_919:A32 = code
  ld %U8_920:U8 = %A32_919 0
  conv %S32_921:S32 = %U8_920
  and %S32_922:S32 = %S32_921 15
  bne %S32_922 0 if_8_end
  bra branch_14

.bbl branch_14
  lea %A32_923:A32 = code
  ld %U8_924:U8 = %A32_923 0
  conv %S32_925:S32 = %U8_924
  bne %S32_925 240 while_1
  bra if_8_end

.bbl while_1
  lea %A32_926:A32 = nj
  mov %S32_927:S32 = 5
  st %A32_926 0 = %S32_927
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra if_8_end

.bbl if_8_end
  lea %A32_928:A32 = code
  ld %U8_929:U8 = %A32_928 0
  conv %S32_930:S32 = %U8_929
  shr %S32_931:S32 = %S32_930 4
  add %S32_932:S32 = %S32_931 1
  add %S32_933:S32 = coef %S32_932
  mov coef = %S32_933
  blt 63:S32 coef while_2
  bra if_10_end

.bbl while_2
  lea %A32_934:A32 = nj
  mov %S32_935:S32 = 5
  st %A32_934 0 = %S32_935
  ret

.bbl while_2_cond
  bne 0:S32 0 while_2
  bra if_10_end

.bbl if_10_end
  lea %A32_936:A32 = nj
  lea %A32_937:A32 = %A32_936 184
  lea %A32_938:A32 = c 24
  ld %S32_939:S32 = %A32_938 0
  mul %S32_940:S32 = %S32_939 64
  add %S32_941:S32 = coef %S32_940
  lea %A32_942:A32 = %A32_937 %S32_941
  ld %U8_943:U8 = %A32_942 0
  conv %S32_944:S32 = %U8_943
  mul %S32_945:S32 = value %S32_944
  lea %A32_946:A32 = nj
  lea %A32_947:A32 = %A32_946 524736
  lea %A32_948:A32 = njZZ
  lea %A32_949:A32 = %A32_948 coef
  ld %S8_950:S8 = %A32_949 0
  conv %S32_951:S32 = %S8_950
  mul %S32_952:S32 = %S32_951 4
  lea %A32_953:A32 = %A32_947 %S32_952
  st %A32_953 0 = %S32_945

.bbl while_3_cond
  blt coef 63 while_3
  bra while_3_exit

.bbl while_3_exit
  mov coef = 0
  bra for_4_cond

.bbl for_4
  lea %A32_954:A32 = nj
  lea %A32_955:A32 = %A32_954 524736
  mul %S32_956:S32 = coef 4
  lea %A32_957:A32 = %A32_955 %S32_956
  pusharg %A32_957
  bsr njRowIDCT

.bbl for_4_next
  add %S32_958:S32 = coef 8
  mov coef = %S32_958

.bbl for_4_cond
  blt coef 64 for_4
  bra for_4_exit

.bbl for_4_exit
  mov coef = 0
  bra for_5_cond

.bbl for_5
  lea %A32_959:A32 = nj
  lea %A32_960:A32 = %A32_959 524736
  mul %S32_961:S32 = coef 4
  lea %A32_962:A32 = %A32_960 %S32_961
  lea %A32_963:A32 = out coef
  lea %A32_964:A32 = c 20
  ld %S32_965:S32 = %A32_964 0
  pusharg %S32_965
  pusharg %A32_963
  pusharg %A32_962
  bsr njColIDCT

.bbl for_5_next
  add %S32_966:S32 = coef 1
  mov coef = %S32_966

.bbl for_5_cond
  blt coef 8 for_5
  bra for_5_exit

.bbl for_5_exit
  ret


.fun njDecodeScan NORMAL [] = []

.bbl %start
  .reg S32 [i]
  .reg S32 [mbx]
  .reg S32 [mby]
  .reg S32 [sbx]
  .reg S32 [sby]
  .reg S32 [rstcount]
  lea %A32_967:A32 = nj
  lea %A32_968:A32 = %A32_967 524992
  ld %S32_969:S32 = %A32_968 0
  mov rstcount = %S32_969
  .reg S32 [nextrst]
  mov nextrst = 0
  .reg A32 [c]
  bsr __static_3_njDecodeLength

.bbl while_1
  lea %A32_970:A32 = nj
  lea %A32_971:A32 = %A32_970 0
  ld %S32_972:S32 = %A32_971 0
  bne %S32_972 0 if_15_true
  bra while_1_cond

.bbl if_15_true
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_973:A32 = nj
  lea %A32_974:A32 = %A32_973 12
  ld %S32_975:S32 = %A32_974 0
  conv %U32_976:U32 = %S32_975
  lea %A32_977:A32 = nj
  lea %A32_978:A32 = %A32_977 40
  ld %U32_979:U32 = %A32_978 0
  mul %U32_980:U32 = 2:U32 %U32_979
  add %U32_981:U32 = 4:U32 %U32_980
  blt %U32_976 %U32_981 while_2
  bra if_18_end

.bbl while_2
  lea %A32_982:A32 = nj
  mov %S32_983:S32 = 5
  st %A32_982 0 = %S32_983
  ret

.bbl while_2_cond
  bne 0:S32 0 while_2
  bra if_18_end

.bbl if_18_end
  lea %A32_984:A32 = nj
  lea %A32_985:A32 = %A32_984 4
  ld %A32_986:A32 = %A32_985 0
  ld %U8_987:U8 = %A32_986 0
  conv %U32_988:U32 = %U8_987
  lea %A32_989:A32 = nj
  lea %A32_990:A32 = %A32_989 40
  ld %U32_991:U32 = %A32_990 0
  bne %U32_988 %U32_991 while_3
  bra if_20_end

.bbl while_3
  lea %A32_992:A32 = nj
  mov %S32_993:S32 = 2
  st %A32_992 0 = %S32_993
  ret

.bbl while_3_cond
  bne 0:S32 0 while_3
  bra if_20_end

.bbl if_20_end
  mov %S32_994:S32 = 1
  pusharg %S32_994
  bsr __static_2_njSkip
  mov i = 0
  lea %A32_995:A32 = nj
  lea %A32_996:A32 = %A32_995 44
  mov c = %A32_996
  bra for_9_cond

.bbl for_9
  lea %A32_997:A32 = nj
  lea %A32_998:A32 = %A32_997 4
  ld %A32_999:A32 = %A32_998 0
  ld %U8_1000:U8 = %A32_999 0
  conv %S32_1001:S32 = %U8_1000
  lea %A32_1002:A32 = c 0
  ld %S32_1003:S32 = %A32_1002 0
  bne %S32_1001 %S32_1003 while_4
  bra if_22_end

.bbl while_4
  lea %A32_1004:A32 = nj
  mov %S32_1005:S32 = 5
  st %A32_1004 0 = %S32_1005
  ret

.bbl while_4_cond
  bne 0:S32 0 while_4
  bra if_22_end

.bbl if_22_end
  lea %A32_1006:A32 = nj
  lea %A32_1007:A32 = %A32_1006 4
  ld %A32_1008:A32 = %A32_1007 0
  lea %A32_1009:A32 = %A32_1008 1
  ld %U8_1010:U8 = %A32_1009 0
  conv %S32_1011:S32 = %U8_1010
  and %S32_1012:S32 = %S32_1011 238
  bne %S32_1012 0 while_5
  bra if_24_end

.bbl while_5
  lea %A32_1013:A32 = nj
  mov %S32_1014:S32 = 5
  st %A32_1013 0 = %S32_1014
  ret

.bbl while_5_cond
  bne 0:S32 0 while_5
  bra if_24_end

.bbl if_24_end
  lea %A32_1015:A32 = nj
  lea %A32_1016:A32 = %A32_1015 4
  ld %A32_1017:A32 = %A32_1016 0
  lea %A32_1018:A32 = %A32_1017 1
  ld %U8_1019:U8 = %A32_1018 0
  conv %S32_1020:S32 = %U8_1019
  shr %S32_1021:S32 = %S32_1020 4
  lea %A32_1022:A32 = c 32
  st %A32_1022 0 = %S32_1021
  lea %A32_1023:A32 = nj
  lea %A32_1024:A32 = %A32_1023 4
  ld %A32_1025:A32 = %A32_1024 0
  lea %A32_1026:A32 = %A32_1025 1
  ld %U8_1027:U8 = %A32_1026 0
  conv %S32_1028:S32 = %U8_1027
  and %S32_1029:S32 = %S32_1028 1
  or %S32_1030:S32 = %S32_1029 2
  lea %A32_1031:A32 = c 28
  st %A32_1031 0 = %S32_1030
  mov %S32_1032:S32 = 2
  pusharg %S32_1032
  bsr __static_2_njSkip

.bbl for_9_next
  add %S32_1033:S32 = i 1
  mov i = %S32_1033
  lea %A32_1034:A32 = c 44
  mov c = %A32_1034

.bbl for_9_cond
  conv %U32_1035:U32 = i
  lea %A32_1036:A32 = nj
  lea %A32_1037:A32 = %A32_1036 40
  ld %U32_1038:U32 = %A32_1037 0
  blt %U32_1035 %U32_1038 for_9
  bra for_9_exit

.bbl for_9_exit
  lea %A32_1039:A32 = nj
  lea %A32_1040:A32 = %A32_1039 4
  ld %A32_1041:A32 = %A32_1040 0
  ld %U8_1042:U8 = %A32_1041 0
  conv %S32_1043:S32 = %U8_1042
  bne %S32_1043 0 while_6
  bra branch_40

.bbl branch_40
  lea %A32_1044:A32 = nj
  lea %A32_1045:A32 = %A32_1044 4
  ld %A32_1046:A32 = %A32_1045 0
  lea %A32_1047:A32 = %A32_1046 1
  ld %U8_1048:U8 = %A32_1047 0
  conv %S32_1049:S32 = %U8_1048
  bne %S32_1049 63 while_6
  bra branch_39

.bbl branch_39
  lea %A32_1050:A32 = nj
  lea %A32_1051:A32 = %A32_1050 4
  ld %A32_1052:A32 = %A32_1051 0
  lea %A32_1053:A32 = %A32_1052 2
  ld %U8_1054:U8 = %A32_1053 0
  conv %S32_1055:S32 = %U8_1054
  bne %S32_1055 0 while_6
  bra if_27_end

.bbl while_6
  lea %A32_1056:A32 = nj
  mov %S32_1057:S32 = 2
  st %A32_1056 0 = %S32_1057
  ret

.bbl while_6_cond
  bne 0:S32 0 while_6
  bra if_27_end

.bbl if_27_end
  lea %A32_1058:A32 = nj
  lea %A32_1059:A32 = %A32_1058 12
  ld %S32_1060:S32 = %A32_1059 0
  pusharg %S32_1060
  bsr __static_2_njSkip
  mov mby = 0
  mov mbx = 0
  bra for_14_cond

.bbl for_14
  mov i = 0
  lea %A32_1061:A32 = nj
  lea %A32_1062:A32 = %A32_1061 44
  mov c = %A32_1062
  bra for_12_cond

.bbl for_12
  mov sby = 0
  bra for_11_cond

.bbl for_11
  mov sbx = 0
  bra for_10_cond

.bbl for_10
  lea %A32_1063:A32 = c 40
  ld %A32_1064:A32 = %A32_1063 0
  lea %A32_1065:A32 = c 8
  ld %S32_1066:S32 = %A32_1065 0
  mul %S32_1067:S32 = mby %S32_1066
  add %S32_1068:S32 = %S32_1067 sby
  lea %A32_1069:A32 = c 20
  ld %S32_1070:S32 = %A32_1069 0
  mul %S32_1071:S32 = %S32_1068 %S32_1070
  lea %A32_1072:A32 = c 4
  ld %S32_1073:S32 = %A32_1072 0
  mul %S32_1074:S32 = mbx %S32_1073
  add %S32_1075:S32 = %S32_1071 %S32_1074
  add %S32_1076:S32 = %S32_1075 sbx
  shl %S32_1077:S32 = %S32_1076 3
  lea %A32_1078:A32 = %A32_1064 %S32_1077
  pusharg %A32_1078
  pusharg c
  bsr njDecodeBlock

.bbl while_7
  lea %A32_1079:A32 = nj
  lea %A32_1080:A32 = %A32_1079 0
  ld %S32_1081:S32 = %A32_1080 0
  bne %S32_1081 0 if_28_true
  bra while_7_cond

.bbl if_28_true
  ret

.bbl while_7_cond
  bne 0:S32 0 while_7
  bra for_10_next

.bbl for_10_next
  add %S32_1082:S32 = sbx 1
  mov sbx = %S32_1082

.bbl for_10_cond
  lea %A32_1083:A32 = c 4
  ld %S32_1084:S32 = %A32_1083 0
  blt sbx %S32_1084 for_10
  bra for_11_next

.bbl for_11_next
  add %S32_1085:S32 = sby 1
  mov sby = %S32_1085

.bbl for_11_cond
  lea %A32_1086:A32 = c 8
  ld %S32_1087:S32 = %A32_1086 0
  blt sby %S32_1087 for_11
  bra for_12_next

.bbl for_12_next
  add %S32_1088:S32 = i 1
  mov i = %S32_1088
  lea %A32_1089:A32 = c 44
  mov c = %A32_1089

.bbl for_12_cond
  conv %U32_1090:U32 = i
  lea %A32_1091:A32 = nj
  lea %A32_1092:A32 = %A32_1091 40
  ld %U32_1093:U32 = %A32_1092 0
  blt %U32_1090 %U32_1093 for_12
  bra for_12_exit

.bbl for_12_exit
  add %S32_1094:S32 = mbx 1
  mov mbx = %S32_1094
  lea %A32_1095:A32 = nj
  lea %A32_1096:A32 = %A32_1095 24
  ld %S32_1097:S32 = %A32_1096 0
  ble %S32_1097 %S32_1094 if_34_true
  bra if_34_end

.bbl if_34_true
  mov mbx = 0
  add %S32_1098:S32 = mby 1
  mov mby = %S32_1098
  lea %A32_1099:A32 = nj
  lea %A32_1100:A32 = %A32_1099 28
  ld %S32_1101:S32 = %A32_1100 0
  ble %S32_1101 %S32_1098 for_14_exit
  bra if_34_end

.bbl if_34_end
  lea %A32_1102:A32 = nj
  lea %A32_1103:A32 = %A32_1102 524992
  ld %S32_1104:S32 = %A32_1103 0
  bne %S32_1104 0 branch_41
  bra for_14_cond

.bbl branch_41
  sub %S32_1105:S32 = rstcount 1
  mov rstcount = %S32_1105
  bne %S32_1105 0 for_14_cond
  bra if_38_true

.bbl if_38_true
  bsr njByteAlign
  mov %S32_1107:S32 = 16
  pusharg %S32_1107
  bsr njGetBits
  poparg %S32_1106:S32
  mov i = %S32_1106
  and %S32_1108:S32 = i 65528
  bne %S32_1108 65488 while_8
  bra branch_42

.bbl branch_42
  and %S32_1109:S32 = i 7
  bne %S32_1109 nextrst while_8
  bra if_36_end

.bbl while_8
  lea %A32_1110:A32 = nj
  mov %S32_1111:S32 = 5
  st %A32_1110 0 = %S32_1111
  ret

.bbl while_8_cond
  bne 0:S32 0 while_8
  bra if_36_end

.bbl if_36_end
  add %S32_1112:S32 = nextrst 1
  and %S32_1113:S32 = %S32_1112 7
  mov nextrst = %S32_1113
  lea %A32_1114:A32 = nj
  lea %A32_1115:A32 = %A32_1114 524992
  ld %S32_1116:S32 = %A32_1115 0
  mov rstcount = %S32_1116
  mov i = 0
  bra for_13_cond

.bbl for_13
  lea %A32_1117:A32 = nj
  lea %A32_1118:A32 = %A32_1117 44
  mul %S32_1119:S32 = i 44
  lea %A32_1120:A32 = %A32_1118 %S32_1119
  lea %A32_1121:A32 = %A32_1120 36
  mov %S32_1122:S32 = 0
  st %A32_1121 0 = %S32_1122

.bbl for_13_next
  add %S32_1123:S32 = i 1
  mov i = %S32_1123

.bbl for_13_cond
  blt i 3 for_13
  bra for_14_cond

.bbl for_14_cond
  bra for_14

.bbl for_14_exit
  lea %A32_1124:A32 = nj
  mov %S32_1125:S32 = 6
  st %A32_1124 0 = %S32_1125
  ret


.fun njUpsampleH NORMAL [] = [A32]

.bbl %start
  poparg c:A32
  .reg S32 [xmax]
  lea %A32_1126:A32 = c 12
  ld %S32_1127:S32 = %A32_1126 0
  sub %S32_1128:S32 = %S32_1127 3
  mov xmax = %S32_1128
  .reg A32 [out]
  .reg A32 [lin]
  .reg A32 [lout]
  .reg S32 [x]
  .reg S32 [y]
  lea %A32_1129:A32 = c 12
  ld %S32_1130:S32 = %A32_1129 0
  lea %A32_1131:A32 = c 16
  ld %S32_1132:S32 = %A32_1131 0
  mul %S32_1133:S32 = %S32_1130 %S32_1132
  shl %S32_1134:S32 = %S32_1133 1
  conv %U32_1135:U32 = %S32_1134
  pusharg %U32_1135
  bsr malloc
  poparg %A32_1136:A32
  mov out = %A32_1136
  bne out 0 if_5_end
  bra while_1

.bbl while_1
  lea %A32_1137:A32 = nj
  mov %S32_1138:S32 = 3
  st %A32_1137 0 = %S32_1138
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra if_5_end

.bbl if_5_end
  lea %A32_1139:A32 = c 40
  ld %A32_1140:A32 = %A32_1139 0
  mov lin = %A32_1140
  mov lout = out
  lea %A32_1141:A32 = c 16
  ld %S32_1142:S32 = %A32_1141 0
  mov y = %S32_1142
  bra for_3_cond

.bbl for_3
  ld %U8_1143:U8 = lin 0
  conv %S32_1144:S32 = %U8_1143
  mul %S32_1145:S32 = 139:S32 %S32_1144
  lea %A32_1146:A32 = lin 1
  ld %U8_1147:U8 = %A32_1146 0
  conv %S32_1148:S32 = %U8_1147
  mul %S32_1149:S32 = -11:S32 %S32_1148
  add %S32_1150:S32 = %S32_1145 %S32_1149
  add %S32_1151:S32 = %S32_1150 64
  shr %S32_1152:S32 = %S32_1151 7
  pusharg %S32_1152
  bsr njClip
  poparg %U8_1153:U8
  st lout 0 = %U8_1153
  ld %U8_1154:U8 = lin 0
  conv %S32_1155:S32 = %U8_1154
  mul %S32_1156:S32 = 104:S32 %S32_1155
  lea %A32_1157:A32 = lin 1
  ld %U8_1158:U8 = %A32_1157 0
  conv %S32_1159:S32 = %U8_1158
  mul %S32_1160:S32 = 27:S32 %S32_1159
  add %S32_1161:S32 = %S32_1156 %S32_1160
  lea %A32_1162:A32 = lin 2
  ld %U8_1163:U8 = %A32_1162 0
  conv %S32_1164:S32 = %U8_1163
  mul %S32_1165:S32 = -3:S32 %S32_1164
  add %S32_1166:S32 = %S32_1161 %S32_1165
  add %S32_1167:S32 = %S32_1166 64
  shr %S32_1168:S32 = %S32_1167 7
  pusharg %S32_1168
  bsr njClip
  poparg %U8_1169:U8
  lea %A32_1170:A32 = lout 1
  st %A32_1170 0 = %U8_1169
  ld %U8_1171:U8 = lin 0
  conv %S32_1172:S32 = %U8_1171
  mul %S32_1173:S32 = 28:S32 %S32_1172
  lea %A32_1174:A32 = lin 1
  ld %U8_1175:U8 = %A32_1174 0
  conv %S32_1176:S32 = %U8_1175
  mul %S32_1177:S32 = 109:S32 %S32_1176
  add %S32_1178:S32 = %S32_1173 %S32_1177
  lea %A32_1179:A32 = lin 2
  ld %U8_1180:U8 = %A32_1179 0
  conv %S32_1181:S32 = %U8_1180
  mul %S32_1182:S32 = -9:S32 %S32_1181
  add %S32_1183:S32 = %S32_1178 %S32_1182
  add %S32_1184:S32 = %S32_1183 64
  shr %S32_1185:S32 = %S32_1184 7
  pusharg %S32_1185
  bsr njClip
  poparg %U8_1186:U8
  lea %A32_1187:A32 = lout 2
  st %A32_1187 0 = %U8_1186
  mov x = 0
  bra for_2_cond

.bbl for_2
  lea %A32_1188:A32 = lin x
  ld %U8_1189:U8 = %A32_1188 0
  conv %S32_1190:S32 = %U8_1189
  mul %S32_1191:S32 = -9:S32 %S32_1190
  add %S32_1192:S32 = x 1
  lea %A32_1193:A32 = lin %S32_1192
  ld %U8_1194:U8 = %A32_1193 0
  conv %S32_1195:S32 = %U8_1194
  mul %S32_1196:S32 = 111:S32 %S32_1195
  add %S32_1197:S32 = %S32_1191 %S32_1196
  add %S32_1198:S32 = x 2
  lea %A32_1199:A32 = lin %S32_1198
  ld %U8_1200:U8 = %A32_1199 0
  conv %S32_1201:S32 = %U8_1200
  mul %S32_1202:S32 = 29:S32 %S32_1201
  add %S32_1203:S32 = %S32_1197 %S32_1202
  add %S32_1204:S32 = x 3
  lea %A32_1205:A32 = lin %S32_1204
  ld %U8_1206:U8 = %A32_1205 0
  conv %S32_1207:S32 = %U8_1206
  mul %S32_1208:S32 = -3:S32 %S32_1207
  add %S32_1209:S32 = %S32_1203 %S32_1208
  add %S32_1210:S32 = %S32_1209 64
  shr %S32_1211:S32 = %S32_1210 7
  pusharg %S32_1211
  bsr njClip
  poparg %U8_1212:U8
  shl %S32_1213:S32 = x 1
  add %S32_1214:S32 = %S32_1213 3
  lea %A32_1215:A32 = lout %S32_1214
  st %A32_1215 0 = %U8_1212
  lea %A32_1216:A32 = lin x
  ld %U8_1217:U8 = %A32_1216 0
  conv %S32_1218:S32 = %U8_1217
  mul %S32_1219:S32 = -3:S32 %S32_1218
  add %S32_1220:S32 = x 1
  lea %A32_1221:A32 = lin %S32_1220
  ld %U8_1222:U8 = %A32_1221 0
  conv %S32_1223:S32 = %U8_1222
  mul %S32_1224:S32 = 29:S32 %S32_1223
  add %S32_1225:S32 = %S32_1219 %S32_1224
  add %S32_1226:S32 = x 2
  lea %A32_1227:A32 = lin %S32_1226
  ld %U8_1228:U8 = %A32_1227 0
  conv %S32_1229:S32 = %U8_1228
  mul %S32_1230:S32 = 111:S32 %S32_1229
  add %S32_1231:S32 = %S32_1225 %S32_1230
  add %S32_1232:S32 = x 3
  lea %A32_1233:A32 = lin %S32_1232
  ld %U8_1234:U8 = %A32_1233 0
  conv %S32_1235:S32 = %U8_1234
  mul %S32_1236:S32 = -9:S32 %S32_1235
  add %S32_1237:S32 = %S32_1231 %S32_1236
  add %S32_1238:S32 = %S32_1237 64
  shr %S32_1239:S32 = %S32_1238 7
  pusharg %S32_1239
  bsr njClip
  poparg %U8_1240:U8
  shl %S32_1241:S32 = x 1
  add %S32_1242:S32 = %S32_1241 4
  lea %A32_1243:A32 = lout %S32_1242
  st %A32_1243 0 = %U8_1240

.bbl for_2_next
  add %S32_1244:S32 = x 1
  mov x = %S32_1244

.bbl for_2_cond
  blt x xmax for_2
  bra for_2_exit

.bbl for_2_exit
  lea %A32_1245:A32 = c 20
  ld %S32_1246:S32 = %A32_1245 0
  lea %A32_1247:A32 = lin %S32_1246
  mov lin = %A32_1247
  lea %A32_1248:A32 = c 12
  ld %S32_1249:S32 = %A32_1248 0
  shl %S32_1250:S32 = %S32_1249 1
  lea %A32_1251:A32 = lout %S32_1250
  mov lout = %A32_1251
  lea %A32_1252:A32 = lin -1
  ld %U8_1253:U8 = %A32_1252 0
  conv %S32_1254:S32 = %U8_1253
  mul %S32_1255:S32 = 28:S32 %S32_1254
  lea %A32_1256:A32 = lin -2
  ld %U8_1257:U8 = %A32_1256 0
  conv %S32_1258:S32 = %U8_1257
  mul %S32_1259:S32 = 109:S32 %S32_1258
  add %S32_1260:S32 = %S32_1255 %S32_1259
  lea %A32_1261:A32 = lin -3
  ld %U8_1262:U8 = %A32_1261 0
  conv %S32_1263:S32 = %U8_1262
  mul %S32_1264:S32 = -9:S32 %S32_1263
  add %S32_1265:S32 = %S32_1260 %S32_1264
  add %S32_1266:S32 = %S32_1265 64
  shr %S32_1267:S32 = %S32_1266 7
  pusharg %S32_1267
  bsr njClip
  poparg %U8_1268:U8
  lea %A32_1269:A32 = lout -3
  st %A32_1269 0 = %U8_1268
  lea %A32_1270:A32 = lin -1
  ld %U8_1271:U8 = %A32_1270 0
  conv %S32_1272:S32 = %U8_1271
  mul %S32_1273:S32 = 104:S32 %S32_1272
  lea %A32_1274:A32 = lin -2
  ld %U8_1275:U8 = %A32_1274 0
  conv %S32_1276:S32 = %U8_1275
  mul %S32_1277:S32 = 27:S32 %S32_1276
  add %S32_1278:S32 = %S32_1273 %S32_1277
  lea %A32_1279:A32 = lin -3
  ld %U8_1280:U8 = %A32_1279 0
  conv %S32_1281:S32 = %U8_1280
  mul %S32_1282:S32 = -3:S32 %S32_1281
  add %S32_1283:S32 = %S32_1278 %S32_1282
  add %S32_1284:S32 = %S32_1283 64
  shr %S32_1285:S32 = %S32_1284 7
  pusharg %S32_1285
  bsr njClip
  poparg %U8_1286:U8
  lea %A32_1287:A32 = lout -2
  st %A32_1287 0 = %U8_1286
  lea %A32_1288:A32 = lin -1
  ld %U8_1289:U8 = %A32_1288 0
  conv %S32_1290:S32 = %U8_1289
  mul %S32_1291:S32 = 139:S32 %S32_1290
  lea %A32_1292:A32 = lin -2
  ld %U8_1293:U8 = %A32_1292 0
  conv %S32_1294:S32 = %U8_1293
  mul %S32_1295:S32 = -11:S32 %S32_1294
  add %S32_1296:S32 = %S32_1291 %S32_1295
  add %S32_1297:S32 = %S32_1296 64
  shr %S32_1298:S32 = %S32_1297 7
  pusharg %S32_1298
  bsr njClip
  poparg %U8_1299:U8
  lea %A32_1300:A32 = lout -1
  st %A32_1300 0 = %U8_1299

.bbl for_3_next
  sub %S32_1301:S32 = y 1
  mov y = %S32_1301

.bbl for_3_cond
  bne y 0 for_3
  bra for_3_exit

.bbl for_3_exit
  lea %A32_1302:A32 = c 12
  ld %S32_1303:S32 = %A32_1302 0
  shl %S32_1304:S32 = %S32_1303 1
  lea %A32_1305:A32 = c 12
  st %A32_1305 0 = %S32_1304
  lea %A32_1306:A32 = c 12
  ld %S32_1307:S32 = %A32_1306 0
  lea %A32_1308:A32 = c 20
  st %A32_1308 0 = %S32_1307
  lea %A32_1309:A32 = c 40
  ld %A32_1310:A32 = %A32_1309 0
  pusharg %A32_1310
  bsr free
  lea %A32_1311:A32 = c 40
  st %A32_1311 0 = out
  ret


.fun njUpsampleV NORMAL [] = [A32]

.bbl %start
  poparg c:A32
  .reg S32 [w]
  lea %A32_1312:A32 = c 12
  ld %S32_1313:S32 = %A32_1312 0
  mov w = %S32_1313
  .reg S32 [s1]
  lea %A32_1314:A32 = c 20
  ld %S32_1315:S32 = %A32_1314 0
  mov s1 = %S32_1315
  .reg S32 [s2]
  add %S32_1316:S32 = s1 s1
  mov s2 = %S32_1316
  .reg A32 [out]
  .reg A32 [cin]
  .reg A32 [cout]
  .reg S32 [x]
  .reg S32 [y]
  lea %A32_1317:A32 = c 12
  ld %S32_1318:S32 = %A32_1317 0
  lea %A32_1319:A32 = c 16
  ld %S32_1320:S32 = %A32_1319 0
  mul %S32_1321:S32 = %S32_1318 %S32_1320
  shl %S32_1322:S32 = %S32_1321 1
  conv %U32_1323:U32 = %S32_1322
  pusharg %U32_1323
  bsr malloc
  poparg %A32_1324:A32
  mov out = %A32_1324
  bne out 0 if_5_end
  bra while_1

.bbl while_1
  lea %A32_1325:A32 = nj
  mov %S32_1326:S32 = 3
  st %A32_1325 0 = %S32_1326
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra if_5_end

.bbl if_5_end
  mov x = 0
  bra for_3_cond

.bbl for_3
  lea %A32_1327:A32 = c 40
  ld %A32_1328:A32 = %A32_1327 0
  lea %A32_1329:A32 = %A32_1328 x
  mov cin = %A32_1329
  lea %A32_1330:A32 = out x
  mov cout = %A32_1330
  ld %U8_1331:U8 = cin 0
  conv %S32_1332:S32 = %U8_1331
  mul %S32_1333:S32 = 139:S32 %S32_1332
  lea %A32_1334:A32 = cin s1
  ld %U8_1335:U8 = %A32_1334 0
  conv %S32_1336:S32 = %U8_1335
  mul %S32_1337:S32 = -11:S32 %S32_1336
  add %S32_1338:S32 = %S32_1333 %S32_1337
  add %S32_1339:S32 = %S32_1338 64
  shr %S32_1340:S32 = %S32_1339 7
  pusharg %S32_1340
  bsr njClip
  poparg %U8_1341:U8
  st cout 0 = %U8_1341
  lea %A32_1342:A32 = cout w
  mov cout = %A32_1342
  ld %U8_1343:U8 = cin 0
  conv %S32_1344:S32 = %U8_1343
  mul %S32_1345:S32 = 104:S32 %S32_1344
  lea %A32_1346:A32 = cin s1
  ld %U8_1347:U8 = %A32_1346 0
  conv %S32_1348:S32 = %U8_1347
  mul %S32_1349:S32 = 27:S32 %S32_1348
  add %S32_1350:S32 = %S32_1345 %S32_1349
  lea %A32_1351:A32 = cin s2
  ld %U8_1352:U8 = %A32_1351 0
  conv %S32_1353:S32 = %U8_1352
  mul %S32_1354:S32 = -3:S32 %S32_1353
  add %S32_1355:S32 = %S32_1350 %S32_1354
  add %S32_1356:S32 = %S32_1355 64
  shr %S32_1357:S32 = %S32_1356 7
  pusharg %S32_1357
  bsr njClip
  poparg %U8_1358:U8
  st cout 0 = %U8_1358
  lea %A32_1359:A32 = cout w
  mov cout = %A32_1359
  ld %U8_1360:U8 = cin 0
  conv %S32_1361:S32 = %U8_1360
  mul %S32_1362:S32 = 28:S32 %S32_1361
  lea %A32_1363:A32 = cin s1
  ld %U8_1364:U8 = %A32_1363 0
  conv %S32_1365:S32 = %U8_1364
  mul %S32_1366:S32 = 109:S32 %S32_1365
  add %S32_1367:S32 = %S32_1362 %S32_1366
  lea %A32_1368:A32 = cin s2
  ld %U8_1369:U8 = %A32_1368 0
  conv %S32_1370:S32 = %U8_1369
  mul %S32_1371:S32 = -9:S32 %S32_1370
  add %S32_1372:S32 = %S32_1367 %S32_1371
  add %S32_1373:S32 = %S32_1372 64
  shr %S32_1374:S32 = %S32_1373 7
  pusharg %S32_1374
  bsr njClip
  poparg %U8_1375:U8
  st cout 0 = %U8_1375
  lea %A32_1376:A32 = cout w
  mov cout = %A32_1376
  lea %A32_1377:A32 = cin s1
  mov cin = %A32_1377
  lea %A32_1378:A32 = c 16
  ld %S32_1379:S32 = %A32_1378 0
  sub %S32_1380:S32 = %S32_1379 3
  mov y = %S32_1380
  bra for_2_cond

.bbl for_2
  sub %S32_1381:S32 = 0  s1
  lea %A32_1382:A32 = cin %S32_1381
  ld %U8_1383:U8 = %A32_1382 0
  conv %S32_1384:S32 = %U8_1383
  mul %S32_1385:S32 = -9:S32 %S32_1384
  ld %U8_1386:U8 = cin 0
  conv %S32_1387:S32 = %U8_1386
  mul %S32_1388:S32 = 111:S32 %S32_1387
  add %S32_1389:S32 = %S32_1385 %S32_1388
  lea %A32_1390:A32 = cin s1
  ld %U8_1391:U8 = %A32_1390 0
  conv %S32_1392:S32 = %U8_1391
  mul %S32_1393:S32 = 29:S32 %S32_1392
  add %S32_1394:S32 = %S32_1389 %S32_1393
  lea %A32_1395:A32 = cin s2
  ld %U8_1396:U8 = %A32_1395 0
  conv %S32_1397:S32 = %U8_1396
  mul %S32_1398:S32 = -3:S32 %S32_1397
  add %S32_1399:S32 = %S32_1394 %S32_1398
  add %S32_1400:S32 = %S32_1399 64
  shr %S32_1401:S32 = %S32_1400 7
  pusharg %S32_1401
  bsr njClip
  poparg %U8_1402:U8
  st cout 0 = %U8_1402
  lea %A32_1403:A32 = cout w
  mov cout = %A32_1403
  sub %S32_1404:S32 = 0  s1
  lea %A32_1405:A32 = cin %S32_1404
  ld %U8_1406:U8 = %A32_1405 0
  conv %S32_1407:S32 = %U8_1406
  mul %S32_1408:S32 = -3:S32 %S32_1407
  ld %U8_1409:U8 = cin 0
  conv %S32_1410:S32 = %U8_1409
  mul %S32_1411:S32 = 29:S32 %S32_1410
  add %S32_1412:S32 = %S32_1408 %S32_1411
  lea %A32_1413:A32 = cin s1
  ld %U8_1414:U8 = %A32_1413 0
  conv %S32_1415:S32 = %U8_1414
  mul %S32_1416:S32 = 111:S32 %S32_1415
  add %S32_1417:S32 = %S32_1412 %S32_1416
  lea %A32_1418:A32 = cin s2
  ld %U8_1419:U8 = %A32_1418 0
  conv %S32_1420:S32 = %U8_1419
  mul %S32_1421:S32 = -9:S32 %S32_1420
  add %S32_1422:S32 = %S32_1417 %S32_1421
  add %S32_1423:S32 = %S32_1422 64
  shr %S32_1424:S32 = %S32_1423 7
  pusharg %S32_1424
  bsr njClip
  poparg %U8_1425:U8
  st cout 0 = %U8_1425
  lea %A32_1426:A32 = cout w
  mov cout = %A32_1426
  lea %A32_1427:A32 = cin s1
  mov cin = %A32_1427

.bbl for_2_next
  sub %S32_1428:S32 = y 1
  mov y = %S32_1428

.bbl for_2_cond
  bne y 0 for_2
  bra for_2_exit

.bbl for_2_exit
  lea %A32_1429:A32 = cin s1
  mov cin = %A32_1429
  ld %U8_1430:U8 = cin 0
  conv %S32_1431:S32 = %U8_1430
  mul %S32_1432:S32 = 28:S32 %S32_1431
  sub %S32_1433:S32 = 0  s1
  lea %A32_1434:A32 = cin %S32_1433
  ld %U8_1435:U8 = %A32_1434 0
  conv %S32_1436:S32 = %U8_1435
  mul %S32_1437:S32 = 109:S32 %S32_1436
  add %S32_1438:S32 = %S32_1432 %S32_1437
  sub %S32_1439:S32 = 0  s2
  lea %A32_1440:A32 = cin %S32_1439
  ld %U8_1441:U8 = %A32_1440 0
  conv %S32_1442:S32 = %U8_1441
  mul %S32_1443:S32 = -9:S32 %S32_1442
  add %S32_1444:S32 = %S32_1438 %S32_1443
  add %S32_1445:S32 = %S32_1444 64
  shr %S32_1446:S32 = %S32_1445 7
  pusharg %S32_1446
  bsr njClip
  poparg %U8_1447:U8
  st cout 0 = %U8_1447
  lea %A32_1448:A32 = cout w
  mov cout = %A32_1448
  ld %U8_1449:U8 = cin 0
  conv %S32_1450:S32 = %U8_1449
  mul %S32_1451:S32 = 104:S32 %S32_1450
  sub %S32_1452:S32 = 0  s1
  lea %A32_1453:A32 = cin %S32_1452
  ld %U8_1454:U8 = %A32_1453 0
  conv %S32_1455:S32 = %U8_1454
  mul %S32_1456:S32 = 27:S32 %S32_1455
  add %S32_1457:S32 = %S32_1451 %S32_1456
  sub %S32_1458:S32 = 0  s2
  lea %A32_1459:A32 = cin %S32_1458
  ld %U8_1460:U8 = %A32_1459 0
  conv %S32_1461:S32 = %U8_1460
  mul %S32_1462:S32 = -3:S32 %S32_1461
  add %S32_1463:S32 = %S32_1457 %S32_1462
  add %S32_1464:S32 = %S32_1463 64
  shr %S32_1465:S32 = %S32_1464 7
  pusharg %S32_1465
  bsr njClip
  poparg %U8_1466:U8
  st cout 0 = %U8_1466
  lea %A32_1467:A32 = cout w
  mov cout = %A32_1467
  ld %U8_1468:U8 = cin 0
  conv %S32_1469:S32 = %U8_1468
  mul %S32_1470:S32 = 139:S32 %S32_1469
  sub %S32_1471:S32 = 0  s1
  lea %A32_1472:A32 = cin %S32_1471
  ld %U8_1473:U8 = %A32_1472 0
  conv %S32_1474:S32 = %U8_1473
  mul %S32_1475:S32 = -11:S32 %S32_1474
  add %S32_1476:S32 = %S32_1470 %S32_1475
  add %S32_1477:S32 = %S32_1476 64
  shr %S32_1478:S32 = %S32_1477 7
  pusharg %S32_1478
  bsr njClip
  poparg %U8_1479:U8
  st cout 0 = %U8_1479

.bbl for_3_next
  add %S32_1480:S32 = x 1
  mov x = %S32_1480

.bbl for_3_cond
  blt x w for_3
  bra for_3_exit

.bbl for_3_exit
  lea %A32_1481:A32 = c 16
  ld %S32_1482:S32 = %A32_1481 0
  shl %S32_1483:S32 = %S32_1482 1
  lea %A32_1484:A32 = c 16
  st %A32_1484 0 = %S32_1483
  lea %A32_1485:A32 = c 12
  ld %S32_1486:S32 = %A32_1485 0
  lea %A32_1487:A32 = c 20
  st %A32_1487 0 = %S32_1486
  lea %A32_1488:A32 = c 40
  ld %A32_1489:A32 = %A32_1488 0
  pusharg %A32_1489
  bsr free
  lea %A32_1490:A32 = c 40
  st %A32_1490 0 = out
  ret


.fun njConvert NORMAL [] = []

.bbl %start
  .reg S32 [i]
  .reg A32 [c]
  mov i = 0
  lea %A32_1491:A32 = nj
  lea %A32_1492:A32 = %A32_1491 44
  mov c = %A32_1492
  bra for_5_cond

.bbl for_5
  bra while_3_cond

.bbl while_3
  lea %A32_1493:A32 = c 12
  ld %S32_1494:S32 = %A32_1493 0
  lea %A32_1495:A32 = nj
  lea %A32_1496:A32 = %A32_1495 16
  ld %S32_1497:S32 = %A32_1496 0
  blt %S32_1494 %S32_1497 if_9_true
  bra while_1

.bbl if_9_true
  pusharg c
  bsr njUpsampleH

.bbl while_1
  lea %A32_1498:A32 = nj
  lea %A32_1499:A32 = %A32_1498 0
  ld %S32_1500:S32 = %A32_1499 0
  bne %S32_1500 0 if_10_true
  bra while_1_cond

.bbl if_10_true
  ret

.bbl while_1_cond
  bne 0:S32 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_1501:A32 = c 16
  ld %S32_1502:S32 = %A32_1501 0
  lea %A32_1503:A32 = nj
  lea %A32_1504:A32 = %A32_1503 20
  ld %S32_1505:S32 = %A32_1504 0
  blt %S32_1502 %S32_1505 if_12_true
  bra while_2

.bbl if_12_true
  pusharg c
  bsr njUpsampleV

.bbl while_2
  lea %A32_1506:A32 = nj
  lea %A32_1507:A32 = %A32_1506 0
  ld %S32_1508:S32 = %A32_1507 0
  bne %S32_1508 0 if_13_true
  bra while_2_cond

.bbl if_13_true
  ret

.bbl while_2_cond
  bne 0:S32 0 while_2
  bra while_3_cond

.bbl while_3_cond
  lea %A32_1509:A32 = c 12
  ld %S32_1510:S32 = %A32_1509 0
  lea %A32_1511:A32 = nj
  lea %A32_1512:A32 = %A32_1511 16
  ld %S32_1513:S32 = %A32_1512 0
  blt %S32_1510 %S32_1513 while_3
  bra branch_24

.bbl branch_24
  lea %A32_1514:A32 = c 16
  ld %S32_1515:S32 = %A32_1514 0
  lea %A32_1516:A32 = nj
  lea %A32_1517:A32 = %A32_1516 20
  ld %S32_1518:S32 = %A32_1517 0
  blt %S32_1515 %S32_1518 while_3
  bra while_3_exit

.bbl while_3_exit
  lea %A32_1519:A32 = c 12
  ld %S32_1520:S32 = %A32_1519 0
  lea %A32_1521:A32 = nj
  lea %A32_1522:A32 = %A32_1521 16
  ld %S32_1523:S32 = %A32_1522 0
  blt %S32_1520 %S32_1523 while_4
  bra branch_25

.bbl branch_25
  lea %A32_1524:A32 = c 16
  ld %S32_1525:S32 = %A32_1524 0
  lea %A32_1526:A32 = nj
  lea %A32_1527:A32 = %A32_1526 20
  ld %S32_1528:S32 = %A32_1527 0
  blt %S32_1525 %S32_1528 while_4
  bra for_5_next

.bbl while_4
  lea %A32_1529:A32 = nj
  mov %S32_1530:S32 = 4
  st %A32_1529 0 = %S32_1530
  ret

.bbl while_4_cond
  bne 0:S32 0 while_4
  bra for_5_next

.bbl for_5_next
  add %S32_1531:S32 = i 1
  mov i = %S32_1531
  lea %A32_1532:A32 = c 44
  mov c = %A32_1532

.bbl for_5_cond
  conv %U32_1533:U32 = i
  lea %A32_1534:A32 = nj
  lea %A32_1535:A32 = %A32_1534 40
  ld %U32_1536:U32 = %A32_1535 0
  blt %U32_1533 %U32_1536 for_5
  bra for_5_exit

.bbl for_5_exit
  lea %A32_1537:A32 = nj
  lea %A32_1538:A32 = %A32_1537 40
  ld %U32_1539:U32 = %A32_1538 0
  beq %U32_1539 3 if_23_true
  bra if_23_false

.bbl if_23_true
  .reg S32 [x]
  .reg S32 [yy]
  .reg A32 [prgb]
  lea %A32_1540:A32 = nj
  lea %A32_1541:A32 = %A32_1540 524996
  ld %A32_1542:A32 = %A32_1541 0
  mov prgb = %A32_1542
  .reg A32 [py]
  lea %A32_1543:A32 = nj
  lea %A32_1544:A32 = %A32_1543 44
  lea %A32_1545:A32 = %A32_1544 40
  ld %A32_1546:A32 = %A32_1545 0
  mov py = %A32_1546
  .reg A32 [pcb]
  lea %A32_1547:A32 = nj
  lea %A32_1548:A32 = %A32_1547 44
  lea %A32_1549:A32 = %A32_1548 44
  lea %A32_1550:A32 = %A32_1549 40
  ld %A32_1551:A32 = %A32_1550 0
  mov pcb = %A32_1551
  .reg A32 [pcr]
  lea %A32_1552:A32 = nj
  lea %A32_1553:A32 = %A32_1552 44
  lea %A32_1554:A32 = %A32_1553 88
  lea %A32_1555:A32 = %A32_1554 40
  ld %A32_1556:A32 = %A32_1555 0
  mov pcr = %A32_1556
  lea %A32_1557:A32 = nj
  lea %A32_1558:A32 = %A32_1557 20
  ld %S32_1559:S32 = %A32_1558 0
  mov yy = %S32_1559
  bra for_7_cond

.bbl for_7
  mov x = 0
  bra for_6_cond

.bbl for_6
  .reg S32 [y]
  lea %A32_1560:A32 = py x
  ld %U8_1561:U8 = %A32_1560 0
  conv %S32_1562:S32 = %U8_1561
  shl %S32_1563:S32 = %S32_1562 8
  mov y = %S32_1563
  .reg S32 [cb]
  lea %A32_1564:A32 = pcb x
  ld %U8_1565:U8 = %A32_1564 0
  conv %S32_1566:S32 = %U8_1565
  sub %S32_1567:S32 = %S32_1566 128
  mov cb = %S32_1567
  .reg S32 [cr]
  lea %A32_1568:A32 = pcr x
  ld %U8_1569:U8 = %A32_1568 0
  conv %S32_1570:S32 = %U8_1569
  sub %S32_1571:S32 = %S32_1570 128
  mov cr = %S32_1571
  mul %S32_1572:S32 = 359:S32 cr
  add %S32_1573:S32 = y %S32_1572
  add %S32_1574:S32 = %S32_1573 128
  shr %S32_1575:S32 = %S32_1574 8
  pusharg %S32_1575
  bsr njClip
  poparg %U8_1576:U8
  st prgb 0 = %U8_1576
  mul %S32_1577:S32 = 88:S32 cb
  sub %S32_1578:S32 = y %S32_1577
  mul %S32_1579:S32 = 183:S32 cr
  sub %S32_1580:S32 = %S32_1578 %S32_1579
  add %S32_1581:S32 = %S32_1580 128
  shr %S32_1582:S32 = %S32_1581 8
  pusharg %S32_1582
  bsr njClip
  poparg %U8_1583:U8
  lea %A32_1584:A32 = prgb 1
  st %A32_1584 0 = %U8_1583
  mul %S32_1585:S32 = 454:S32 cb
  add %S32_1586:S32 = y %S32_1585
  add %S32_1587:S32 = %S32_1586 128
  shr %S32_1588:S32 = %S32_1587 8
  pusharg %S32_1588
  bsr njClip
  poparg %U8_1589:U8
  lea %A32_1590:A32 = prgb 2
  st %A32_1590 0 = %U8_1589
  lea %A32_1591:A32 = prgb 3
  mov prgb = %A32_1591

.bbl for_6_next
  add %S32_1592:S32 = x 1
  mov x = %S32_1592

.bbl for_6_cond
  lea %A32_1593:A32 = nj
  lea %A32_1594:A32 = %A32_1593 16
  ld %S32_1595:S32 = %A32_1594 0
  blt x %S32_1595 for_6
  bra for_6_exit

.bbl for_6_exit
  lea %A32_1596:A32 = nj
  lea %A32_1597:A32 = %A32_1596 44
  lea %A32_1598:A32 = %A32_1597 20
  ld %S32_1599:S32 = %A32_1598 0
  lea %A32_1600:A32 = py %S32_1599
  mov py = %A32_1600
  lea %A32_1601:A32 = nj
  lea %A32_1602:A32 = %A32_1601 44
  lea %A32_1603:A32 = %A32_1602 44
  lea %A32_1604:A32 = %A32_1603 20
  ld %S32_1605:S32 = %A32_1604 0
  lea %A32_1606:A32 = pcb %S32_1605
  mov pcb = %A32_1606
  lea %A32_1607:A32 = nj
  lea %A32_1608:A32 = %A32_1607 44
  lea %A32_1609:A32 = %A32_1608 88
  lea %A32_1610:A32 = %A32_1609 20
  ld %S32_1611:S32 = %A32_1610 0
  lea %A32_1612:A32 = pcr %S32_1611
  mov pcr = %A32_1612

.bbl for_7_next
  sub %S32_1613:S32 = yy 1
  mov yy = %S32_1613

.bbl for_7_cond
  bne yy 0 for_7
  bra for_7_exit

.bbl for_7_exit
  bra if_23_end

.bbl if_23_false
  lea %A32_1614:A32 = nj
  lea %A32_1615:A32 = %A32_1614 44
  lea %A32_1616:A32 = %A32_1615 12
  ld %S32_1617:S32 = %A32_1616 0
  lea %A32_1618:A32 = nj
  lea %A32_1619:A32 = %A32_1618 44
  lea %A32_1620:A32 = %A32_1619 20
  ld %S32_1621:S32 = %A32_1620 0
  bne %S32_1617 %S32_1621 if_22_true
  bra if_23_end

.bbl if_22_true
  .reg A32 [pin]
  lea %A32_1622:A32 = nj
  lea %A32_1623:A32 = %A32_1622 44
  lea %A32_1624:A32 = %A32_1623 40
  ld %A32_1625:A32 = %A32_1624 0
  lea %A32_1626:A32 = nj
  lea %A32_1627:A32 = %A32_1626 44
  lea %A32_1628:A32 = %A32_1627 20
  ld %S32_1629:S32 = %A32_1628 0
  lea %A32_1630:A32 = %A32_1625 %S32_1629
  mov pin = %A32_1630
  .reg A32 [pout]
  lea %A32_1631:A32 = nj
  lea %A32_1632:A32 = %A32_1631 44
  lea %A32_1633:A32 = %A32_1632 40
  ld %A32_1634:A32 = %A32_1633 0
  lea %A32_1635:A32 = nj
  lea %A32_1636:A32 = %A32_1635 44
  lea %A32_1637:A32 = %A32_1636 12
  ld %S32_1638:S32 = %A32_1637 0
  lea %A32_1639:A32 = %A32_1634 %S32_1638
  mov pout = %A32_1639
  .reg S32 [__local_26_y]
  lea %A32_1640:A32 = nj
  lea %A32_1641:A32 = %A32_1640 44
  lea %A32_1642:A32 = %A32_1641 16
  ld %S32_1643:S32 = %A32_1642 0
  sub %S32_1644:S32 = %S32_1643 1
  mov __local_26_y = %S32_1644
  bra for_8_cond

.bbl for_8
  lea %A32_1645:A32 = nj
  lea %A32_1646:A32 = %A32_1645 44
  lea %A32_1647:A32 = %A32_1646 12
  ld %S32_1648:S32 = %A32_1647 0
  conv %U32_1649:U32 = %S32_1648
  pusharg %U32_1649
  pusharg pin
  pusharg pout
  bsr mymemcpy
  lea %A32_1650:A32 = nj
  lea %A32_1651:A32 = %A32_1650 44
  lea %A32_1652:A32 = %A32_1651 20
  ld %S32_1653:S32 = %A32_1652 0
  lea %A32_1654:A32 = pin %S32_1653
  mov pin = %A32_1654
  lea %A32_1655:A32 = nj
  lea %A32_1656:A32 = %A32_1655 44
  lea %A32_1657:A32 = %A32_1656 12
  ld %S32_1658:S32 = %A32_1657 0
  lea %A32_1659:A32 = pout %S32_1658
  mov pout = %A32_1659

.bbl for_8_next
  sub %S32_1660:S32 = __local_26_y 1
  mov __local_26_y = %S32_1660

.bbl for_8_cond
  bne __local_26_y 0 for_8
  bra for_8_exit

.bbl for_8_exit
  lea %A32_1661:A32 = nj
  lea %A32_1662:A32 = %A32_1661 44
  lea %A32_1663:A32 = %A32_1662 12
  ld %S32_1664:S32 = %A32_1663 0
  lea %A32_1665:A32 = nj
  lea %A32_1666:A32 = %A32_1665 44
  lea %A32_1667:A32 = %A32_1666 20
  st %A32_1667 0 = %S32_1664

.bbl if_23_end
  ret


.fun njInit NORMAL [] = []

.bbl %start
  lea %A32_1668:A32 = nj
  mov %S32_1669:S32 = 0
  mov %U32_1670:U32 = 525000
  pusharg %U32_1670
  pusharg %S32_1669
  pusharg %A32_1668
  bsr mymemset
  ret


.fun njDone NORMAL [] = []

.bbl %start
  .reg S32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  lea %A32_1671:A32 = nj
  lea %A32_1672:A32 = %A32_1671 44
  mul %S32_1673:S32 = i 44
  lea %A32_1674:A32 = %A32_1672 %S32_1673
  lea %A32_1675:A32 = %A32_1674 40
  ld %A32_1676:A32 = %A32_1675 0
  bne %A32_1676 0 if_2_true
  bra for_1_next

.bbl if_2_true
  lea %A32_1677:A32 = nj
  lea %A32_1678:A32 = %A32_1677 44
  mul %S32_1679:S32 = i 44
  lea %A32_1680:A32 = %A32_1678 %S32_1679
  lea %A32_1681:A32 = %A32_1680 40
  ld %A32_1682:A32 = %A32_1681 0
  pusharg %A32_1682
  bsr free

.bbl for_1_next
  add %S32_1683:S32 = i 1
  mov i = %S32_1683

.bbl for_1_cond
  blt i 3 for_1
  bra for_1_exit

.bbl for_1_exit
  lea %A32_1684:A32 = nj
  lea %A32_1685:A32 = %A32_1684 524996
  ld %A32_1686:A32 = %A32_1685 0
  bne %A32_1686 0 if_4_true
  bra if_4_end

.bbl if_4_true
  lea %A32_1687:A32 = nj
  lea %A32_1688:A32 = %A32_1687 524996
  ld %A32_1689:A32 = %A32_1688 0
  pusharg %A32_1689
  bsr free

.bbl if_4_end
  bsr njInit
  ret


.fun njDecode NORMAL [S32] = [A32 S32]
.reg S32 [%out]

.bbl %start
  poparg jpeg:A32
  poparg size:S32
  bsr njDone
  lea %A32_1690:A32 = nj
  lea %A32_1691:A32 = %A32_1690 4
  st %A32_1691 0 = jpeg
  and %S32_1692:S32 = size 2147483647
  lea %A32_1693:A32 = nj
  lea %A32_1694:A32 = %A32_1693 8
  st %A32_1694 0 = %S32_1692
  lea %A32_1695:A32 = nj
  lea %A32_1696:A32 = %A32_1695 8
  ld %S32_1697:S32 = %A32_1696 0
  blt %S32_1697 2 if_2_true
  bra if_2_end

.bbl if_2_true
  mov %out = 1
  pusharg %out
  ret

.bbl if_2_end
  lea %A32_1698:A32 = nj
  lea %A32_1699:A32 = %A32_1698 4
  ld %A32_1700:A32 = %A32_1699 0
  ld %U8_1701:U8 = %A32_1700 0
  conv %S32_1702:S32 = %U8_1701
  xor %S32_1703:S32 = %S32_1702 255
  lea %A32_1704:A32 = nj
  lea %A32_1705:A32 = %A32_1704 4
  ld %A32_1706:A32 = %A32_1705 0
  lea %A32_1707:A32 = %A32_1706 1
  ld %U8_1708:U8 = %A32_1707 0
  conv %S32_1709:S32 = %U8_1708
  xor %S32_1710:S32 = %S32_1709 216
  or %S32_1711:S32 = %S32_1703 %S32_1710
  bne %S32_1711 0 if_3_true
  bra if_3_end

.bbl if_3_true
  mov %out = 1
  pusharg %out
  ret

.bbl if_3_end
  mov %S32_1712:S32 = 2
  pusharg %S32_1712
  bsr __static_2_njSkip
  bra while_1_cond

.bbl while_1
  lea %A32_1713:A32 = nj
  lea %A32_1714:A32 = %A32_1713 8
  ld %S32_1715:S32 = %A32_1714 0
  blt %S32_1715 2 if_4_true
  bra branch_8

.bbl branch_8
  lea %A32_1716:A32 = nj
  lea %A32_1717:A32 = %A32_1716 4
  ld %A32_1718:A32 = %A32_1717 0
  ld %U8_1719:U8 = %A32_1718 0
  conv %S32_1720:S32 = %U8_1719
  bne %S32_1720 255 if_4_true
  bra if_4_end

.bbl if_4_true
  mov %out = 5
  pusharg %out
  ret

.bbl if_4_end
  mov %S32_1721:S32 = 2
  pusharg %S32_1721
  bsr __static_2_njSkip
  lea %A32_1722:A32 = nj
  lea %A32_1723:A32 = %A32_1722 4
  ld %A32_1724:A32 = %A32_1723 0
  lea %A32_1725:A32 = %A32_1724 -1
  ld %U8_1726:U8 = %A32_1725 0
  blt 254:U8 %U8_1726 switch_1727_default
  .jtb switch_1727_tab  255 switch_1727_default [192 switch_1727_192 196 switch_1727_196 219 switch_1727_219 221 switch_1727_221 218 switch_1727_218 254 switch_1727_254]
  switch %U8_1726 switch_1727_tab
.bbl switch_1727_192
  bsr njDecodeSOF
  bra switch_1727_end
.bbl switch_1727_196
  bsr njDecodeDHT
  bra switch_1727_end
.bbl switch_1727_219
  bsr njDecodeDQT
  bra switch_1727_end
.bbl switch_1727_221
  bsr njDecodeDRI
  bra switch_1727_end
.bbl switch_1727_218
  bsr njDecodeScan
  bra switch_1727_end
.bbl switch_1727_254
  bsr njSkipMarker
  bra switch_1727_end
.bbl switch_1727_default
  lea %A32_1728:A32 = nj
  lea %A32_1729:A32 = %A32_1728 4
  ld %A32_1730:A32 = %A32_1729 0
  lea %A32_1731:A32 = %A32_1730 -1
  ld %U8_1732:U8 = %A32_1731 0
  conv %S32_1733:S32 = %U8_1732
  and %S32_1734:S32 = %S32_1733 240
  beq %S32_1734 224 if_5_true
  bra if_5_false

.bbl if_5_true
  bsr njSkipMarker
  bra while_1_cond

.bbl if_5_false
  mov %out = 2
  pusharg %out
  ret

.bbl switch_1727_end

.bbl while_1_cond
  lea %A32_1735:A32 = nj
  lea %A32_1736:A32 = %A32_1735 0
  ld %S32_1737:S32 = %A32_1736 0
  bne %S32_1737 0 while_1_exit
  bra while_1

.bbl while_1_exit
  lea %A32_1738:A32 = nj
  lea %A32_1739:A32 = %A32_1738 0
  ld %S32_1740:S32 = %A32_1739 0
  bne %S32_1740 6 if_7_true
  bra if_7_end

.bbl if_7_true
  lea %A32_1741:A32 = nj
  lea %A32_1742:A32 = %A32_1741 0
  ld %S32_1743:S32 = %A32_1742 0
  mov %out = %S32_1743
  pusharg %out
  ret

.bbl if_7_end
  lea %A32_1744:A32 = nj
  mov %S32_1745:S32 = 0
  st %A32_1744 0 = %S32_1745
  bsr njConvert
  lea %A32_1746:A32 = nj
  lea %A32_1747:A32 = %A32_1746 0
  ld %S32_1748:S32 = %A32_1747 0
  mov %out = %S32_1748
  pusharg %out
  ret


.fun write_str NORMAL [] = [A32 S32]

.bbl %start
  poparg s:A32
  poparg fd:S32
  .reg U32 [size]
  mov size = 0
  bra for_1_cond

.bbl for_1_next
  add %U32_1749:U32 = size 1
  mov size = %U32_1749

.bbl for_1_cond
  lea %A32_1750:A32 = s size
  ld %S8_1751:S8 = %A32_1750 0
  conv %S32_1752:S32 = %S8_1751
  bne %S32_1752 0 for_1_next
  bra for_1_exit

.bbl for_1_exit
  pusharg size
  pusharg s
  pusharg fd
  bsr write
  poparg %S32_1753:S32
  ret


.fun write_dec NORMAL [] = [S32 S32]

.bbl %start
  poparg fd:S32
  poparg a:S32
.stk buf 1 64
  .reg S32 [i]
  mov i = 63
  lea %A32_1754:A32 = buf
  lea %A32_1755:A32 = %A32_1754 i
  mov %S8_1756:S8 = 0
  st %A32_1755 0 = %S8_1756
  sub %S32_1757:S32 = i 1
  mov i = %S32_1757

.bbl while_1
  rem %S32_1758:S32 = a 10
  add %S32_1759:S32 = 48:S32 %S32_1758
  conv %S8_1760:S8 = %S32_1759
  lea %A32_1761:A32 = buf
  lea %A32_1762:A32 = %A32_1761 i
  st %A32_1762 0 = %S8_1760
  sub %S32_1763:S32 = i 1
  mov i = %S32_1763
  div %S32_1764:S32 = a 10
  mov a = %S32_1764

.bbl while_1_cond
  bne a 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_1765:A32 = buf
  add %S32_1766:S32 = i 1
  lea %A32_1767:A32 = %A32_1765 %S32_1766
  pusharg fd
  pusharg %A32_1767
  bsr write_str
  ret


.fun main NORMAL [S32] = [S32 A32]
.reg S32 [%out]

.bbl %start
  poparg argc:S32
  poparg argv:A32
  .reg S32 [size]
  .reg A32 [buf]
  .reg S32 [fd]
  blt argc 3 if_1_true
  bra if_1_end

.bbl if_1_true
.mem string_const_1 4 RO
.data 1 "Usage: nanojpeg <input.jpg> <output.ppm>\x00"
  lea %A32_1768:A32 = string_const_1
  pusharg %A32_1768
  bsr print_s_ln
  mov %out = 2
  pusharg %out
  ret

.bbl if_1_end
  lea %A32_1769:A32 = argv 4
  ld %A32_1770:A32 = %A32_1769 0
  mov %S32_1772:S32 = 0
  mov %S32_1773:S32 = 0
  pusharg %S32_1773
  pusharg %S32_1772
  pusharg %A32_1770
  bsr open
  poparg %S32_1771:S32
  mov fd = %S32_1771
  blt fd 0 if_2_true
  bra if_2_end

.bbl if_2_true
.mem string_const_2 4 RO
.data 1 "Error opening the input file.\x00"
  lea %A32_1774:A32 = string_const_2
  pusharg %A32_1774
  bsr print_s_ln
  mov %out = 1
  pusharg %out
  ret

.bbl if_2_end
  mov %S32_1776:S32 = 0
  mov %S32_1777:S32 = 2
  pusharg %S32_1777
  pusharg %S32_1776
  pusharg fd
  bsr lseek
  poparg %S32_1775:S32
  mov size = %S32_1775
  conv %U32_1778:U32 = size
  pusharg %U32_1778
  bsr malloc
  poparg %A32_1779:A32
  mov buf = %A32_1779
  mov %S32_1781:S32 = 0
  mov %S32_1782:S32 = 0
  pusharg %S32_1782
  pusharg %S32_1781
  pusharg fd
  bsr lseek
  poparg %S32_1780:S32
  conv %U32_1783:U32 = size
  pusharg %U32_1783
  pusharg buf
  pusharg fd
  bsr read
  poparg %S32_1784:S32
  mov size = %S32_1784
  pusharg fd
  bsr close
  poparg %S32_1785:S32
  bsr njInit
  pusharg size
  pusharg buf
  bsr njDecode
  poparg %S32_1786:S32
  bne %S32_1786 0 if_3_true
  bra if_3_end

.bbl if_3_true
  pusharg buf
  bsr free
.mem string_const_3 4 RO
.data 1 "Error decoding the input file.\x00"
  lea %A32_1787:A32 = string_const_3
  pusharg %A32_1787
  bsr print_s_ln
  mov %out = 1
  pusharg %out
  ret

.bbl if_3_end
  pusharg buf
  bsr free
  lea %A32_1788:A32 = argv 8
  ld %A32_1789:A32 = %A32_1788 0
  or %S32_1790:S32 = 1:S32 64
  or %S32_1791:S32 = %S32_1790 512
  add %S32_1792:S32 = 2:S32 4
  mul %S32_1793:S32 = %S32_1792 64
  pusharg %S32_1793
  pusharg %S32_1791
  pusharg %A32_1789
  bsr open
  poparg %S32_1794:S32
  mov fd = %S32_1794
  blt fd 0 if_4_true
  bra if_4_end

.bbl if_4_true
.mem string_const_4 4 RO
.data 1 "Error opening the output file.\x00"
  lea %A32_1795:A32 = string_const_4
  pusharg %A32_1795
  bsr print_s_ln
  mov %out = 1
  pusharg %out
  ret

.bbl if_4_end
  bsr njIsColor
  poparg %S32_1796:S32
  bne %S32_1796 0 if_5_true
  bra if_5_false

.bbl if_5_true
.mem string_const_5 4 RO
.data 1 "P6\n\x00"
  lea %A32_1797:A32 = string_const_5
  pusharg fd
  pusharg %A32_1797
  bsr write_str
  bra if_5_end

.bbl if_5_false
.mem string_const_6 4 RO
.data 1 "P5\n\x00"
  lea %A32_1798:A32 = string_const_6
  pusharg fd
  pusharg %A32_1798
  bsr write_str

.bbl if_5_end
  bsr njGetWidth
  poparg %S32_1799:S32
  pusharg %S32_1799
  pusharg fd
  bsr write_dec
.mem string_const_7 4 RO
.data 1 " \x00"
  lea %A32_1800:A32 = string_const_7
  pusharg fd
  pusharg %A32_1800
  bsr write_str
  bsr njGetHeight
  poparg %S32_1801:S32
  pusharg %S32_1801
  pusharg fd
  bsr write_dec
.mem string_const_8 4 RO
.data 1 "\n\x00"
  lea %A32_1802:A32 = string_const_8
  pusharg fd
  pusharg %A32_1802
  bsr write_str
.mem string_const_9 4 RO
.data 1 "255\n\x00"
  lea %A32_1803:A32 = string_const_9
  pusharg fd
  pusharg %A32_1803
  bsr write_str
  bsr njGetImage
  poparg %A32_1804:A32
  bsr njGetImageSize
  poparg %S32_1805:S32
  conv %U32_1806:U32 = %S32_1805
  pusharg %U32_1806
  pusharg %A32_1804
  pusharg fd
  bsr write
  poparg %S32_1807:S32
  pusharg fd
  bsr close
  poparg %S32_1808:S32
  bsr njDone
  mov %out = 0
  pusharg %out
  ret
