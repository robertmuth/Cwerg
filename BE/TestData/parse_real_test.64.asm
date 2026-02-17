

.fun $sig/void_A64_U64 SIGNATURE [] = [A64 U64]


.fun $sig/U8_U8_U8 SIGNATURE [U8] = [U8 U8]


.fun $sig/U8_U16_U16 SIGNATURE [U8] = [U16 U16]


.fun $sig/U8_U32_U32 SIGNATURE [U8] = [U32 U32]


.fun $sig/U8_U64_U64 SIGNATURE [U8] = [U64 U64]


.fun $sig/U8_S8_S8 SIGNATURE [U8] = [S8 S8]


.fun $sig/U8_S16_S16 SIGNATURE [U8] = [S16 S16]


.fun $sig/U8_S32_S32 SIGNATURE [U8] = [S32 S32]


.fun $sig/U8_S64_S64 SIGNATURE [U8] = [S64 S64]


.fun $sig/U8_R32_R32 SIGNATURE [U8] = [R32 R32]


.fun $sig/U8_R64_R64 SIGNATURE [U8] = [R64 R64]


.fun $sig/U8_A64_A64 SIGNATURE [U8] = [A64 A64]


.fun $sig/U64_A64_A64_U64 SIGNATURE [U64] = [A64 A64 U64]


.fun $sig/U64_U8_A64 SIGNATURE [U64] = [U8 A64]


.fun $sig/U64_U16_A64 SIGNATURE [U64] = [U16 A64]


.fun $sig/U64_U32_A64 SIGNATURE [U64] = [U32 A64]


.fun $sig/U64_U64_A64 SIGNATURE [U64] = [U64 A64]


.fun $sig/U64_S16_A64 SIGNATURE [U64] = [S16 A64]


.fun $sig/U64_S32_A64 SIGNATURE [U64] = [S32 A64]


.fun $sig/U64_R64 SIGNATURE [U64] = [R64]


.fun $sig/U8_R64 SIGNATURE [U8] = [R64]


.fun $sig/R64_U8_U64_U64 SIGNATURE [R64] = [U8 U64 U64]


.fun $sig/R32_U8_U32_U32 SIGNATURE [R32] = [U8 U32 U32]


.fun $sig/R64_R64_S32 SIGNATURE [R64] = [R64 S32]


.fun $sig/S32_R64 SIGNATURE [S32] = [R64]


.fun $sig/U64_R64_A64 SIGNATURE [U64] = [R64 A64]


.fun $sig/U64_U8_U8_A64 SIGNATURE [U64] = [U8 U8 A64]


.fun $sig/U64_A64_U64_A64 SIGNATURE [U64] = [A64 U64 A64]


.fun $sig/S32_A64 SIGNATURE [S32] = [A64]


.fun $sig/U64_R64_U64_U8_A64 SIGNATURE [U64] = [R64 U64 U8 A64]


.fun $sig/U8_U8 SIGNATURE [U8] = [U8]


.fun $sig/U64_U64_U8_A64 SIGNATURE [U64] = [U64 U8 A64]


.fun $sig/S32_A64_A64 SIGNATURE [S32] = [A64 A64]


.fun $sig/S64_S32_A64_U64 SIGNATURE [S64] = [S32 A64 U64]


.fun $sig/S64_S32_U32_U64 SIGNATURE [S64] = [S32 U32 U64]


.fun $sig/void_S32_A64_A64 SIGNATURE [] = [S32 A64 A64]


.fun $sig/void_S32_U32_U32_A64 SIGNATURE [] = [S32 U32 U32 A64]


.fun $sig/void_S32_U32_A64_A64 SIGNATURE [] = [S32 U32 A64 A64]


.fun $sig/A64_A64_A64_U64 SIGNATURE [A64] = [A64 A64 U64]


.fun $sig/U64_U8_A64_A64 SIGNATURE [U64] = [U8 A64 A64]


.fun $sig/U32_A64 SIGNATURE [U32] = [A64]


.fun $sig/U64_U16_A64_A64 SIGNATURE [U64] = [U16 A64 A64]


.fun $sig/U64_U32_A64_A64 SIGNATURE [U64] = [U32 A64 A64]


.fun $sig/U64_U64_A64_A64 SIGNATURE [U64] = [U64 A64 A64]


.fun $sig/U64_S16_A64_A64 SIGNATURE [U64] = [S16 A64 A64]


.fun $sig/U64_S32_A64_A64 SIGNATURE [U64] = [S32 A64 A64]


.fun $sig/U64_A64_A64_A64 SIGNATURE [U64] = [A64 A64 A64]


.fun $sig/U64_R64_A64_A64 SIGNATURE [U64] = [R64 A64 A64]


.fun $sig/void_A64_A64 SIGNATURE [] = [A64 A64]


.fun $sig/void_A64_U8_U64_A64 SIGNATURE [] = [A64 U8 U64 A64]


.fun $sig/R64_U64_S32_U8 SIGNATURE [R64] = [U64 S32 U8]


.fun $sig/R64_A64 SIGNATURE [R64] = [A64]


.fun $sig/void_void SIGNATURE [] = []


.fun $sig/S32_S32_A64 SIGNATURE [S32] = [S32 A64]

.mem $gen/global_val_1 1 RO
.data 1 "inf" # 0 3 vec<3,u8>

.mem $gen/global_val_2 1 RO
.data 1 "nan" # 0 3 vec<3,u8>

.mem $gen/global_val_3 1 RO
.data 1 "Expr2" # 0 5 vec<5,u8>

.mem $gen/global_val_4 1 RO
.data 1 "out of bounds\n" # 0 14 vec<14,u8>

.mem $gen/global_val_5 1 RO
.data 1 "true" # 0 4 vec<4,u8>

.mem $gen/global_val_6 1 RO
.data 1 "false" # 0 5 vec<5,u8>

.mem $gen/global_val_7 1 RO
.data 1 "s was not completely consumed" # 0 29 vec<29,u8>

.mem $gen/global_val_8 1 RO
.data 1 "+inf" # 0 4 vec<4,u8>

.mem $gen/global_val_9 1 RO
.data 1 "AssertEqR64" # 0 11 vec<11,u8>

.mem $gen/global_val_10 1 RO
.data 1 " failed in " # 0 11 vec<11,u8>

.mem $gen/global_val_11 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:25" # 0 54 vec<54,u8>

.mem $gen/global_val_12 1 RO
.data 1 ": " # 0 2 vec<2,u8>

.mem $gen/global_val_13 1 RO
.data 1 "Id" # 0 2 vec<2,u8>

.mem $gen/global_val_14 1 RO
.data 1 " VS " # 0 4 vec<4,u8>

.mem $gen/global_val_15 1 RO
.data 1 "ExprCall" # 0 8 vec<8,u8>

.mem $gen/global_val_16 1 RO
.data 1 " at " # 0 4 vec<4,u8>

.mem $gen/global_val_17 1 RO
.data 1 [10] # 0 1 vec<1,u8>

.mem $gen/global_val_18 1 RO
.data 1 "-inf" # 0 4 vec<4,u8>

.mem $gen/global_val_19 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:26" # 0 54 vec<54,u8>

.mem $gen/global_val_20 1 RO
.data 1 "+nan" # 0 4 vec<4,u8>

.mem $gen/global_val_21 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:29" # 0 54 vec<54,u8>

.mem $gen/global_val_22 1 RO
.data 1 "-nan" # 0 4 vec<4,u8>

.mem $gen/global_val_23 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:30" # 0 54 vec<54,u8>

.mem $gen/global_val_24 1 RO
.data 1 [48] # 0 1 vec<1,u8>

.mem $gen/global_val_25 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:39" # 0 54 vec<54,u8>

.mem $gen/global_val_26 1 RO
.data 1 "ValNum" # 0 6 vec<6,u8>

.mem $gen/global_val_27 1 RO
.data 1 "+0" # 0 2 vec<2,u8>

.mem $gen/global_val_28 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:40" # 0 54 vec<54,u8>

.mem $gen/global_val_29 1 RO
.data 1 "-0" # 0 2 vec<2,u8>

.mem $gen/global_val_30 1 RO
.data 1 "AssertEq" # 0 8 vec<8,u8>

.mem $gen/global_val_31 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:41" # 0 54 vec<54,u8>

.mem $gen/global_val_32 1 RO
.data 6 [48] # 0 6 vec<6,u8>

.mem $gen/global_val_33 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:42" # 0 54 vec<54,u8>

.mem $gen/global_val_34 1 RO
.data 1 "+000000" # 0 7 vec<7,u8>

.mem $gen/global_val_35 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:43" # 0 54 vec<54,u8>

.mem $gen/global_val_36 1 RO
.data 1 "-000000" # 0 7 vec<7,u8>

.mem $gen/global_val_37 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:44" # 0 54 vec<54,u8>

.mem $gen/global_val_38 1 RO
.data 1 ".0" # 0 2 vec<2,u8>

.mem $gen/global_val_39 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:45" # 0 54 vec<54,u8>

.mem $gen/global_val_40 1 RO
.data 1 ".00000" # 0 6 vec<6,u8>

.mem $gen/global_val_41 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:46" # 0 54 vec<54,u8>

.mem $gen/global_val_42 1 RO
.data 1 "000000.00000" # 0 12 vec<12,u8>

.mem $gen/global_val_43 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:47" # 0 54 vec<54,u8>

.mem $gen/global_val_44 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:48" # 0 54 vec<54,u8>

.mem $gen/global_val_45 1 RO
.data 1 [49] # 0 1 vec<1,u8>

.mem $gen/global_val_46 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:53" # 0 54 vec<54,u8>

.mem $gen/global_val_47 1 RO
.data 1 ".1e1" # 0 4 vec<4,u8>

.mem $gen/global_val_48 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:54" # 0 54 vec<54,u8>

.mem $gen/global_val_49 1 RO
.data 1 ".0000000001e10" # 0 14 vec<14,u8>

.mem $gen/global_val_50 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:55" # 0 54 vec<54,u8>

.mem $gen/global_val_51 1 RO
.data 3 [54] # 0 3 vec<3,u8>

.mem $gen/global_val_52 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:56" # 0 54 vec<54,u8>

.mem $gen/global_val_53 1 RO
.data 1 "666.00000" # 0 9 vec<9,u8>

.mem $gen/global_val_54 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:57" # 0 54 vec<54,u8>

.mem $gen/global_val_55 1 RO
.data 1 "1e-500" # 0 6 vec<6,u8>

.mem $gen/global_val_56 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:58" # 0 54 vec<54,u8>

.mem $gen/global_val_57 1 RO
.data 1 "-1e-500" # 0 7 vec<7,u8>

.mem $gen/global_val_58 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:59" # 0 54 vec<54,u8>

.mem $gen/global_val_59 1 RO
.data 1 "1e+500" # 0 6 vec<6,u8>

.mem $gen/global_val_60 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:60" # 0 54 vec<54,u8>

.mem $gen/global_val_61 1 RO
.data 1 "-1e+500" # 0 7 vec<7,u8>

.mem $gen/global_val_62 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:61" # 0 54 vec<54,u8>

.mem $gen/global_val_63 1 RO
.data 1 "3.141592653589793238462643" # 0 26 vec<26,u8>

.mem $gen/global_val_64 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:63" # 0 54 vec<54,u8>

.mem $gen/global_val_65 1 RO
.data 1 "ValCompound" # 0 11 vec<11,u8>

.mem $gen/global_val_66 1 RO
.data 1 "2.718281828459045235360287" # 0 26 vec<26,u8>

.mem $gen/global_val_67 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:65" # 0 54 vec<54,u8>

.mem $gen/global_val_68 1 RO
.data 1 "0x0" # 0 3 vec<3,u8>

.mem $gen/global_val_69 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:73" # 0 54 vec<54,u8>

.mem $gen/global_val_70 1 RO
.data 1 "0x.0" # 0 4 vec<4,u8>

.mem $gen/global_val_71 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:74" # 0 54 vec<54,u8>

.mem $gen/global_val_72 1 RO
.data 1 "0x1p0" # 0 5 vec<5,u8>

.mem $gen/global_val_73 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:75" # 0 54 vec<54,u8>

.mem $gen/global_val_74 1 RO
.data 1 "0x1p-1" # 0 6 vec<6,u8>

.mem $gen/global_val_75 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:76" # 0 54 vec<54,u8>

.mem $gen/global_val_76 1 RO
.data 1 "0x1p-2" # 0 6 vec<6,u8>

.mem $gen/global_val_77 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:77" # 0 54 vec<54,u8>

.mem $gen/global_val_78 1 RO
.data 1 "0x1p-3" # 0 6 vec<6,u8>

.mem $gen/global_val_79 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:78" # 0 54 vec<54,u8>

.mem $gen/global_val_80 1 RO
.data 1 "0x1p14" # 0 6 vec<6,u8>

.mem $gen/global_val_81 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:79" # 0 54 vec<54,u8>

.mem $gen/global_val_82 1 RO
.data 1 "0x10p+10" # 0 8 vec<8,u8>

.mem $gen/global_val_83 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:80" # 0 54 vec<54,u8>

.mem $gen/global_val_84 1 RO
.data 1 "0x1p-1022" # 0 9 vec<9,u8>

.mem $gen/global_val_85 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:81" # 0 54 vec<54,u8>

.mem $gen/global_val_86 1 RO
.data 1 "Expr1" # 0 5 vec<5,u8>

.mem $gen/global_val_87 1 RO
.data 1 "0x10p-10" # 0 8 vec<8,u8>

.mem $gen/global_val_88 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:82" # 0 54 vec<54,u8>

.mem $gen/global_val_89 1 RO
.data 1 "-0x0" # 0 4 vec<4,u8>

.mem $gen/global_val_90 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:84" # 0 54 vec<54,u8>

.mem $gen/global_val_91 1 RO
.data 1 "-0x.0" # 0 5 vec<5,u8>

.mem $gen/global_val_92 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:85" # 0 54 vec<54,u8>

.mem $gen/global_val_93 1 RO
.data 1 "-0x0p0" # 0 6 vec<6,u8>

.mem $gen/global_val_94 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:86" # 0 54 vec<54,u8>

.mem $gen/global_val_95 1 RO
.data 1 "-0x1p0" # 0 6 vec<6,u8>

.mem $gen/global_val_96 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:87" # 0 54 vec<54,u8>

.mem $gen/global_val_97 1 RO
.data 1 "-0x1p-1" # 0 7 vec<7,u8>

.mem $gen/global_val_98 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:88" # 0 54 vec<54,u8>

.mem $gen/global_val_99 1 RO
.data 1 "-0x1p-2" # 0 7 vec<7,u8>

.mem $gen/global_val_100 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:89" # 0 54 vec<54,u8>

.mem $gen/global_val_101 1 RO
.data 1 "-0x1p-3" # 0 7 vec<7,u8>

.mem $gen/global_val_102 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:90" # 0 54 vec<54,u8>

.mem $gen/global_val_103 1 RO
.data 1 "-0x1p14" # 0 7 vec<7,u8>

.mem $gen/global_val_104 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:91" # 0 54 vec<54,u8>

.mem $gen/global_val_105 1 RO
.data 1 "-0x10p+10" # 0 9 vec<9,u8>

.mem $gen/global_val_106 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:92" # 0 54 vec<54,u8>

.mem $gen/global_val_107 1 RO
.data 1 "-0x1p-1022" # 0 10 vec<10,u8>

.mem $gen/global_val_108 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:93" # 0 54 vec<54,u8>

.mem $gen/global_val_109 1 RO
.data 1 "-0x10p-10" # 0 9 vec<9,u8>

.mem $gen/global_val_110 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:94" # 0 54 vec<54,u8>

.mem $gen/global_val_111 1 RO
.data 1 "0x0000p0" # 0 8 vec<8,u8>

.mem $gen/global_val_112 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:96" # 0 54 vec<54,u8>

.mem $gen/global_val_113 1 RO
.data 1 "0x0.00000p0" # 0 11 vec<11,u8>

.mem $gen/global_val_114 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:97" # 0 54 vec<54,u8>

.mem $gen/global_val_115 1 RO
.data 1 "0x1.0p0" # 0 7 vec<7,u8>

.mem $gen/global_val_116 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:98" # 0 54 vec<54,u8>

.mem $gen/global_val_117 1 RO
.data 1 "0x10p0" # 0 6 vec<6,u8>

.mem $gen/global_val_118 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:99" # 0 54 vec<54,u8>

.mem $gen/global_val_119 1 RO
.data 1 "0x10.0p0" # 0 8 vec<8,u8>

.mem $gen/global_val_120 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:100" # 0 55 vec<55,u8>

.mem $gen/global_val_121 1 RO
.data 1 "0x10p-4" # 0 7 vec<7,u8>

.mem $gen/global_val_122 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:101" # 0 55 vec<55,u8>

.mem $gen/global_val_123 1 RO
.data 1 "0x100p-8" # 0 8 vec<8,u8>

.mem $gen/global_val_124 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:102" # 0 55 vec<55,u8>

.mem $gen/global_val_125 1 RO
.data 1 "0x100.00p-8" # 0 11 vec<11,u8>

.mem $gen/global_val_126 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:103" # 0 55 vec<55,u8>

.mem $gen/global_val_127 1 RO
.data 1 "0x0.01p8" # 0 8 vec<8,u8>

.mem $gen/global_val_128 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:104" # 0 55 vec<55,u8>

.mem $gen/global_val_129 1 RO
.data 1 "0x0.ffffp0" # 0 10 vec<10,u8>

.mem $gen/global_val_130 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:106" # 0 55 vec<55,u8>

.mem $gen/global_val_131 1 RO
.data 1 "0x0.ffffffffp0" # 0 14 vec<14,u8>

.mem $gen/global_val_132 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:107" # 0 55 vec<55,u8>

.mem $gen/global_val_133 1 RO
.data 1 "0x0.ffffffffffffp0" # 0 18 vec<18,u8>

.mem $gen/global_val_134 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:108" # 0 55 vec<55,u8>

.mem $gen/global_val_135 1 RO
.data 1 "0x0.fffffffffffff8p0" # 0 20 vec<20,u8>

.mem $gen/global_val_136 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:109" # 0 55 vec<55,u8>

.mem $gen/global_val_137 1 RO
.data 1 "0x0.fffffffffffffffffffffp0" # 0 27 vec<27,u8>

.mem $gen/global_val_138 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:111" # 0 55 vec<55,u8>

.mem $gen/global_val_139 1 RO
.data 1 "0x1fffffffffffffp0" # 0 18 vec<18,u8>

.mem $gen/global_val_140 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:113" # 0 55 vec<55,u8>

.mem $gen/global_val_141 1 RO
.data 1 "0x1fffffffffffffffffffffp0" # 0 26 vec<26,u8>

.mem $gen/global_val_142 1 RO
.data 1 "/home/muth/Projects/Cwerg/FE/Lib/parse_real_test.cw:114" # 0 55 vec<55,u8>

.mem $gen/global_val_143 1 RO
.data 1 "OK\n" # 0 3 vec<3,u8>


.fun cmp/eq<bool> NORMAL [U8] = [U8 U8]
.bbl entry
  poparg a:U8
  poparg b:U8
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<u8> NORMAL [U8] = [U8 U8]
.bbl entry
  poparg a:U8
  poparg b:U8
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<u16> NORMAL [U8] = [U16 U16]
.bbl entry
  poparg a:U16
  poparg b:U16
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<u32> NORMAL [U8] = [U32 U32]
.bbl entry
  poparg a:U32
  poparg b:U32
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<u64> NORMAL [U8] = [U64 U64]
.bbl entry
  poparg a:U64
  poparg b:U64
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<s8> NORMAL [U8] = [S8 S8]
.bbl entry
  poparg a:S8
  poparg b:S8
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<s16> NORMAL [U8] = [S16 S16]
.bbl entry
  poparg a:S16
  poparg b:S16
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<s32> NORMAL [U8] = [S32 S32]
.bbl entry
  poparg a:S32
  poparg b:S32
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<s64> NORMAL [U8] = [S64 S64]
.bbl entry
  poparg a:S64
  poparg b:S64
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<r32> NORMAL [U8] = [R32 R32]
.bbl entry
  poparg a:R32
  poparg b:R32
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<r64> NORMAL [U8] = [R64 R64]
.bbl entry
  poparg a:R64
  poparg b:R64
  bne a b br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<ptr<rec<cmp/r64r>>> NORMAL [U8] = [A64 A64]
.bbl entry
  poparg a:A64
  poparg b:A64
  ld val:R64 = a 0
  ld err:R64 = a 8
  add expr2:R64 = val err
  ld val.1:R64 = b 0
  ld err.1:R64 = b 8
  sub expr2.1:R64 = val.1 err.1
  blt expr2 expr2.1 br_f
  ld val.2:R64 = a 0
  ld err.2:R64 = a 8
  sub expr2.2:R64 = val.2 err.2
  ld val.3:R64 = b 0
  ld err.3:R64 = b 8
  add expr2.3:R64 = val.3 err.3
  blt expr2.3 expr2.2 br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun cmp/eq<ptr<rec<cmp/r32r>>> NORMAL [U8] = [A64 A64]
.bbl entry
  poparg a:A64
  poparg b:A64
  ld val:R32 = a 0
  ld err:R32 = a 4
  add expr2:R32 = val err
  ld val.1:R32 = b 0
  ld err.1:R32 = b 4
  sub expr2.1:R32 = val.1 err.1
  blt expr2 expr2.1 br_f
  ld val.2:R32 = a 0
  ld err.2:R32 = a 4
  sub expr2.2:R32 = val.2 err.2
  ld val.3:R32 = b 0
  ld err.3:R32 = b 4
  add expr2.3:R32 = val.3 err.3
  blt expr2.3 expr2.2 br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun fmt_int/mymemcpy NORMAL [U64] = [A64 A64 U64]
.bbl entry
  poparg dst:A64
  poparg src:A64
  poparg size:U64
  mov it%1:U64 = 0:U64
.bbl _
  blt it%1 size br_join.1
  bra _.end  # break
.bbl br_join.1
.bbl br_join
  mov i:U64 = it%1
  add expr2:U64 = it%1 1:U64
  mov it%1 = expr2
  lea new_base:A64 = dst i
  lea new_base.1:A64 = src i
  .reg U8 copy
  ld copy = new_base.1 0
  st new_base 0 = copy
  bra _  # continue
.bbl _.end
  pusharg size
  ret


.fun fmt_int/FmtDec<u8> NORMAL [U64] = [U8 A64]
.bbl entry
  poparg v:U8
  poparg out:A64
  mov v%1:U8 = v
  .stk tmp%1 1 1024
  lea.stk var_stk_base:A64 tmp%1 0
  mov pos%1:U64 = 32:U64
.bbl _
  sub expr2:U64 = pos%1 1:U64
  mov pos%1 = expr2
  rem expr2.1:U8 = v%1 10:U8
  mov c:U8 = expr2.1
  mov c8:U8 = c
  .reg U8 expr
  blt 9:U8 c8 br_f
  mov expr = 48:U8
  bra end_expr
.bbl br_f
  mov expr = 87:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  add expr2.2:U8 = c8 expr
  mov c8 = expr2.2
  lea.stk lhsaddr:A64 = tmp%1 0
  lea new_base:A64 = lhsaddr pos%1
  st new_base 0 = c8
  div expr2.3:U8 = v%1 10:U8
  mov v%1 = expr2.3
  beq v%1 0:U8 br_join.1
  bra _  # continue
.bbl br_join.1
.bbl _.end
  ld length:U64 = out 8
  cmplt expr2.4:U64 = pos%1 length pos%1 length
  sub expr2.5:U64 = 32:U64 expr2.4
  mov n:U64 = expr2.5
  ld pointer:A64 = out 0
  lea.stk lhsaddr.1:A64 = tmp%1 0
  lea new_base.1:A64 = lhsaddr.1 pos%1
  pusharg n
  pusharg new_base.1
  pusharg pointer
  bsr fmt_int/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt_int/FmtDec<u16> NORMAL [U64] = [U16 A64]
.bbl entry
  poparg v:U16
  poparg out:A64
  mov v%1:U16 = v
  .stk tmp%1 1 1024
  lea.stk var_stk_base:A64 tmp%1 0
  mov pos%1:U64 = 32:U64
.bbl _
  sub expr2:U64 = pos%1 1:U64
  mov pos%1 = expr2
  rem expr2.1:U16 = v%1 10:U16
  mov c:U16 = expr2.1
  conv as:U8 = c
  mov c8:U8 = as
  .reg U8 expr
  blt 9:U8 c8 br_f
  mov expr = 48:U8
  bra end_expr
.bbl br_f
  mov expr = 87:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  add expr2.2:U8 = c8 expr
  mov c8 = expr2.2
  lea.stk lhsaddr:A64 = tmp%1 0
  lea new_base:A64 = lhsaddr pos%1
  st new_base 0 = c8
  div expr2.3:U16 = v%1 10:U16
  mov v%1 = expr2.3
  beq v%1 0:U16 br_join.1
  bra _  # continue
.bbl br_join.1
.bbl _.end
  ld length:U64 = out 8
  cmplt expr2.4:U64 = pos%1 length pos%1 length
  sub expr2.5:U64 = 32:U64 expr2.4
  mov n:U64 = expr2.5
  ld pointer:A64 = out 0
  lea.stk lhsaddr.1:A64 = tmp%1 0
  lea new_base.1:A64 = lhsaddr.1 pos%1
  pusharg n
  pusharg new_base.1
  pusharg pointer
  bsr fmt_int/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt_int/FmtDec<u32> NORMAL [U64] = [U32 A64]
.bbl entry
  poparg v:U32
  poparg out:A64
  mov v%1:U32 = v
  .stk tmp%1 1 1024
  lea.stk var_stk_base:A64 tmp%1 0
  mov pos%1:U64 = 32:U64
.bbl _
  sub expr2:U64 = pos%1 1:U64
  mov pos%1 = expr2
  rem expr2.1:U32 = v%1 10:U32
  mov c:U32 = expr2.1
  conv as:U8 = c
  mov c8:U8 = as
  .reg U8 expr
  blt 9:U8 c8 br_f
  mov expr = 48:U8
  bra end_expr
.bbl br_f
  mov expr = 87:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  add expr2.2:U8 = c8 expr
  mov c8 = expr2.2
  lea.stk lhsaddr:A64 = tmp%1 0
  lea new_base:A64 = lhsaddr pos%1
  st new_base 0 = c8
  div expr2.3:U32 = v%1 10:U32
  mov v%1 = expr2.3
  beq v%1 0:U32 br_join.1
  bra _  # continue
.bbl br_join.1
.bbl _.end
  ld length:U64 = out 8
  cmplt expr2.4:U64 = pos%1 length pos%1 length
  sub expr2.5:U64 = 32:U64 expr2.4
  mov n:U64 = expr2.5
  ld pointer:A64 = out 0
  lea.stk lhsaddr.1:A64 = tmp%1 0
  lea new_base.1:A64 = lhsaddr.1 pos%1
  pusharg n
  pusharg new_base.1
  pusharg pointer
  bsr fmt_int/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt_int/FmtDec<u64> NORMAL [U64] = [U64 A64]
.bbl entry
  poparg v:U64
  poparg out:A64
  mov v%1:U64 = v
  .stk tmp%1 1 1024
  lea.stk var_stk_base:A64 tmp%1 0
  mov pos%1:U64 = 32:U64
.bbl _
  sub expr2:U64 = pos%1 1:U64
  mov pos%1 = expr2
  rem expr2.1:U64 = v%1 10:U64
  mov c:U64 = expr2.1
  conv as:U8 = c
  mov c8:U8 = as
  .reg U8 expr
  blt 9:U8 c8 br_f
  mov expr = 48:U8
  bra end_expr
.bbl br_f
  mov expr = 87:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  add expr2.2:U8 = c8 expr
  mov c8 = expr2.2
  lea.stk lhsaddr:A64 = tmp%1 0
  lea new_base:A64 = lhsaddr pos%1
  st new_base 0 = c8
  div expr2.3:U64 = v%1 10:U64
  mov v%1 = expr2.3
  beq v%1 0:U64 br_join.1
  bra _  # continue
.bbl br_join.1
.bbl _.end
  ld length:U64 = out 8
  cmplt expr2.4:U64 = pos%1 length pos%1 length
  sub expr2.5:U64 = 32:U64 expr2.4
  mov n:U64 = expr2.5
  ld pointer:A64 = out 0
  lea.stk lhsaddr.1:A64 = tmp%1 0
  lea new_base.1:A64 = lhsaddr.1 pos%1
  pusharg n
  pusharg new_base.1
  pusharg pointer
  bsr fmt_int/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt_int/FmtDec<s16> NORMAL [U64] = [S16 A64]
.bbl entry
  poparg v:S16
  poparg out:A64
  ld length:U64 = out 8
  bne length 0:U64 br_join
  pusharg 0:U64
  ret
.bbl br_join
  ble 0:S16 v br_f
  sub expr2:S16 = 0:S16 v
  mov v_unsigned:S16 = expr2
  ld pointer:A64 = out 0
  st pointer 0 = 45:U8
  .reg U64 expr
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  ld length.1:U64 = out 8
  mov orig_len%1:U64 = length.1
  ble 1:U64 orig_len%1 br_join.2
  trap
.bbl br_join.2
  ld pointer.1:A64 = out 0
  lea at:A64 = pointer.1 1
  st var_stk_base 0 = at
  sub expr2.1:U64 = orig_len%1 1:U64
  st var_stk_base 8 = expr2.1
  bra end_expr.1
.bbl end_expr.1
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v_unsigned
  bsr fmt_int/FmtDec<s16>
  poparg call:U64
  mov expr = call
  bra end_expr
.bbl end_expr
  add expr2.2:U64 = 1:U64 expr
  pusharg expr2.2
  ret
.bbl br_f
  .stk arg1.1 8 16
  lea.stk var_stk_base.1:A64 arg1.1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base.1 0 = copy
  ld copy = out 8
  st var_stk_base.1 8 = copy
  conv as:U16 = v
  lea.stk lhsaddr.1:A64 = arg1.1 0
  pusharg lhsaddr.1
  pusharg as
  bsr fmt_int/FmtDec<u16>
  poparg call.1:U64
  pusharg call.1
  ret
.bbl br_join.1


.fun fmt_int/FmtDec<s32> NORMAL [U64] = [S32 A64]
.bbl entry
  poparg v:S32
  poparg out:A64
  ld length:U64 = out 8
  bne length 0:U64 br_join
  pusharg 0:U64
  ret
.bbl br_join
  ble 0:S32 v br_f
  ld pointer:A64 = out 0
  st pointer 0 = 45:U8
  sub expr2:S32 = 0:S32 v
  conv as:U32 = expr2
  mov v_unsigned:U32 = as
  .reg U64 expr
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  ld length.1:U64 = out 8
  mov orig_len%1:U64 = length.1
  ble 1:U64 orig_len%1 br_join.2
  trap
.bbl br_join.2
  ld pointer.1:A64 = out 0
  lea at:A64 = pointer.1 1
  st var_stk_base 0 = at
  sub expr2.1:U64 = orig_len%1 1:U64
  st var_stk_base 8 = expr2.1
  bra end_expr.1
.bbl end_expr.1
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v_unsigned
  bsr fmt_int/FmtDec<u32>
  poparg call:U64
  mov expr = call
  bra end_expr
.bbl end_expr
  add expr2.2:U64 = 1:U64 expr
  pusharg expr2.2
  ret
.bbl br_f
  .stk arg1.1 8 16
  lea.stk var_stk_base.1:A64 arg1.1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base.1 0 = copy
  ld copy = out 8
  st var_stk_base.1 8 = copy
  conv as.1:U32 = v
  lea.stk lhsaddr.1:A64 = arg1.1 0
  pusharg lhsaddr.1
  pusharg as.1
  bsr fmt_int/FmtDec<u32>
  poparg call.1:U64
  pusharg call.1
  ret
.bbl br_join.1


.fun fmt_int/FmtHex<u64> NORMAL [U64] = [U64 A64]
.bbl entry
  poparg v:U64
  poparg out:A64
  mov v%1:U64 = v
  .stk tmp%1 1 1024
  lea.stk var_stk_base:A64 tmp%1 0
  mov pos%1:U64 = 64:U64
.bbl _
  sub expr2:U64 = pos%1 1:U64
  mov pos%1 = expr2
  rem expr2.1:U64 = v%1 16:U64
  mov c:U64 = expr2.1
  conv as:U8 = c
  mov c8:U8 = as
  .reg U8 expr
  blt 9:U8 c8 br_f
  mov expr = 48:U8
  bra end_expr
.bbl br_f
  mov expr = 87:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  add expr2.2:U8 = c8 expr
  mov c8 = expr2.2
  lea.stk lhsaddr:A64 = tmp%1 0
  lea new_base:A64 = lhsaddr pos%1
  st new_base 0 = c8
  div expr2.3:U64 = v%1 16:U64
  mov v%1 = expr2.3
  beq v%1 0:U64 br_join.1
  bra _  # continue
.bbl br_join.1
.bbl _.end
  ld length:U64 = out 8
  cmplt expr2.4:U64 = pos%1 length pos%1 length
  sub expr2.5:U64 = 64:U64 expr2.4
  mov n:U64 = expr2.5
  ld pointer:A64 = out 0
  lea.stk lhsaddr.1:A64 = tmp%1 0
  lea new_base.1:A64 = lhsaddr.1 pos%1
  pusharg n
  pusharg new_base.1
  pusharg pointer
  bsr fmt_int/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt_int/FmtHex<u32> NORMAL [U64] = [U32 A64]
.bbl entry
  poparg v:U32
  poparg out:A64
  mov v%1:U32 = v
  .stk tmp%1 1 1024
  lea.stk var_stk_base:A64 tmp%1 0
  mov pos%1:U64 = 32:U64
.bbl _
  sub expr2:U64 = pos%1 1:U64
  mov pos%1 = expr2
  rem expr2.1:U32 = v%1 16:U32
  mov c:U32 = expr2.1
  conv as:U8 = c
  mov c8:U8 = as
  .reg U8 expr
  blt 9:U8 c8 br_f
  mov expr = 48:U8
  bra end_expr
.bbl br_f
  mov expr = 87:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  add expr2.2:U8 = c8 expr
  mov c8 = expr2.2
  lea.stk lhsaddr:A64 = tmp%1 0
  lea new_base:A64 = lhsaddr pos%1
  st new_base 0 = c8
  div expr2.3:U32 = v%1 16:U32
  mov v%1 = expr2.3
  beq v%1 0:U32 br_join.1
  bra _  # continue
.bbl br_join.1
.bbl _.end
  ld length:U64 = out 8
  cmplt expr2.4:U64 = pos%1 length pos%1 length
  sub expr2.5:U64 = 32:U64 expr2.4
  mov n:U64 = expr2.5
  ld pointer:A64 = out 0
  lea.stk lhsaddr.1:A64 = tmp%1 0
  lea new_base.1:A64 = lhsaddr.1 pos%1
  pusharg n
  pusharg new_base.1
  pusharg pointer
  bsr fmt_int/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt_int/FmtHex<u16> NORMAL [U64] = [U16 A64]
.bbl entry
  poparg v:U16
  poparg out:A64
  mov v%1:U16 = v
  .stk tmp%1 1 1024
  lea.stk var_stk_base:A64 tmp%1 0
  mov pos%1:U64 = 32:U64
.bbl _
  sub expr2:U64 = pos%1 1:U64
  mov pos%1 = expr2
  rem expr2.1:U16 = v%1 16:U16
  mov c:U16 = expr2.1
  conv as:U8 = c
  mov c8:U8 = as
  .reg U8 expr
  blt 9:U8 c8 br_f
  mov expr = 48:U8
  bra end_expr
.bbl br_f
  mov expr = 87:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  add expr2.2:U8 = c8 expr
  mov c8 = expr2.2
  lea.stk lhsaddr:A64 = tmp%1 0
  lea new_base:A64 = lhsaddr pos%1
  st new_base 0 = c8
  div expr2.3:U16 = v%1 16:U16
  mov v%1 = expr2.3
  beq v%1 0:U16 br_join.1
  bra _  # continue
.bbl br_join.1
.bbl _.end
  ld length:U64 = out 8
  cmplt expr2.4:U64 = pos%1 length pos%1 length
  sub expr2.5:U64 = 32:U64 expr2.4
  mov n:U64 = expr2.5
  ld pointer:A64 = out 0
  lea.stk lhsaddr.1:A64 = tmp%1 0
  lea new_base.1:A64 = lhsaddr.1 pos%1
  pusharg n
  pusharg new_base.1
  pusharg pointer
  bsr fmt_int/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt_int/FmtHex<u8> NORMAL [U64] = [U8 A64]
.bbl entry
  poparg v:U8
  poparg out:A64
  mov v%1:U8 = v
  .stk tmp%1 1 1024
  lea.stk var_stk_base:A64 tmp%1 0
  mov pos%1:U64 = 32:U64
.bbl _
  sub expr2:U64 = pos%1 1:U64
  mov pos%1 = expr2
  rem expr2.1:U8 = v%1 16:U8
  mov c:U8 = expr2.1
  mov c8:U8 = c
  .reg U8 expr
  blt 9:U8 c8 br_f
  mov expr = 48:U8
  bra end_expr
.bbl br_f
  mov expr = 87:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  add expr2.2:U8 = c8 expr
  mov c8 = expr2.2
  lea.stk lhsaddr:A64 = tmp%1 0
  lea new_base:A64 = lhsaddr pos%1
  st new_base 0 = c8
  div expr2.3:U8 = v%1 16:U8
  mov v%1 = expr2.3
  beq v%1 0:U8 br_join.1
  bra _  # continue
.bbl br_join.1
.bbl _.end
  ld length:U64 = out 8
  cmplt expr2.4:U64 = pos%1 length pos%1 length
  sub expr2.5:U64 = 32:U64 expr2.4
  mov n:U64 = expr2.5
  ld pointer:A64 = out 0
  lea.stk lhsaddr.1:A64 = tmp%1 0
  lea new_base.1:A64 = lhsaddr.1 pos%1
  pusharg n
  pusharg new_base.1
  pusharg pointer
  bsr fmt_int/mymemcpy
  poparg call:U64
  pusharg call
  ret

.mem num_real/r64_exponent_bits 4 RO
.data 1 "\x0b\x00\x00\x00" # 0 4 u32

.mem num_real/r64_mantissa_bits 4 RO
.data 1 "4\x00\x00\x00" # 0 4 u32

.mem num_real/r64_mantissa_mask 8 RO
.data 1 "\xff\xff\xff\xff\xff\xff\x0f\x00" # 0 8 u64

.mem num_real/r64_exponent_mask 8 RO
.data 1 "\xff\x07\x00\x00\x00\x00\x00\x00" # 0 8 u64

.mem num_real/r64_raw_exponent_nan 8 RO
.data 1 "\xff\x07\x00\x00\x00\x00\x00\x00" # 0 8 u64

.mem num_real/r64_raw_exponent_subnormal 8 RO
.data 8 [0] # 0 8 u64

.mem num_real/r64_exponent_max 4 RO
.data 1 "\xff\x03\x00\x00" # 0 4 s32

.mem num_real/r64_exponent_min 4 RO
.data 1 "\x02\xfc\xff\xff" # 0 4 s32

.mem num_real/r64_exponent_nan 4 RO
.data 1 "\x00\x04\x00\x00" # 0 4 s32

.mem num_real/r64_exponent_subnormal 4 RO
.data 1 "\x01\xfc\xff\xff" # 0 4 s32

.mem num_real/r64_exponent_bias 4 RO
.data 1 "\xff\x03\x00\x00" # 0 4 s32

.mem num_real/r64_min 8 RO
.data 1 "\x00\x00\x00\x00\x00\x00\x10\x80" # 0 8 r64

.mem num_real/zero_pos_r64 8 RO
.data 8 [0] # 0 8 r64

.mem num_real/zero_neg_r64 8 RO
.data 1 "\x00\x00\x00\x00\x00\x00\x00\x80" # 0 8 r64

.mem num_real/r64_mantissa_infinity 8 RO
.data 8 [0] # 0 8 u64

.mem num_real/inf_pos_r64 8 RO
.data 1 "\x00\x00\x00\x00\x00\x00\xf0\x7f" # 0 8 r64

.mem num_real/inf_neg_r64 8 RO
.data 1 "\x00\x00\x00\x00\x00\x00\xf0\xff" # 0 8 r64

.mem num_real/r64_mantissa_nan 8 RO
.data 1 "\x00\x00\x00\x00\x00\x00\x08\x00" # 0 8 u64

.mem num_real/nan_pos_r64 8 RO
.data 1 "\x00\x00\x00\x00\x00\x00\xf8\x7f" # 0 8 r64

.mem num_real/nan_neg_r64 8 RO
.data 1 "\x00\x00\x00\x00\x00\x00\xf8\xff" # 0 8 r64

.mem num_real/r32_exponent_bits 4 RO
.data 1 "\x08\x00\x00\x00" # 0 4 u32

.mem num_real/r32_mantissa_bits 4 RO
.data 1 "\x17\x00\x00\x00" # 0 4 u32

.mem num_real/r32_exponent_max 4 RO
.data 1 "\x7f\x00\x00\x00" # 0 4 s32

.mem num_real/r32_exponent_min 4 RO
.data 1 "\x82\xff\xff\xff" # 0 4 s32

.mem num_real/powers_of_ten 8 RO
.data 6 [0] # 0 6 vec<309,r64>
.data 1 [240] # 6 1 vec<309,r64>
.data 1 [63] # 7 1 vec<309,r64>
.data 6 [0] # 8 6 vec<309,r64>
.data 1 [36] # 14 1 vec<309,r64>
.data 1 [64] # 15 1 vec<309,r64>
.data 6 [0] # 16 6 vec<309,r64>
.data 1 [89] # 22 1 vec<309,r64>
.data 1 [64] # 23 1 vec<309,r64>
.data 5 [0] # 24 5 vec<309,r64>
.data 1 [64] # 29 1 vec<309,r64>
.data 1 [143] # 30 1 vec<309,r64>
.data 1 [64] # 31 1 vec<309,r64>
.data 5 [0] # 32 5 vec<309,r64>
.data 1 [136] # 37 1 vec<309,r64>
.data 1 [195] # 38 1 vec<309,r64>
.data 1 [64] # 39 1 vec<309,r64>
.data 5 [0] # 40 5 vec<309,r64>
.data 1 [106] # 45 1 vec<309,r64>
.data 1 [248] # 46 1 vec<309,r64>
.data 1 [64] # 47 1 vec<309,r64>
.data 4 [0] # 48 4 vec<309,r64>
.data 1 [128] # 52 1 vec<309,r64>
.data 1 [132] # 53 1 vec<309,r64>
.data 1 [46] # 54 1 vec<309,r64>
.data 1 [65] # 55 1 vec<309,r64>
.data 4 [0] # 56 4 vec<309,r64>
.data 1 [208] # 60 1 vec<309,r64>
.data 1 [18] # 61 1 vec<309,r64>
.data 1 [99] # 62 1 vec<309,r64>
.data 1 [65] # 63 1 vec<309,r64>
.data 4 [0] # 64 4 vec<309,r64>
.data 1 [132] # 68 1 vec<309,r64>
.data 1 [215] # 69 1 vec<309,r64>
.data 1 [151] # 70 1 vec<309,r64>
.data 1 [65] # 71 1 vec<309,r64>
.data 4 [0] # 72 4 vec<309,r64>
.data 1 [101] # 76 1 vec<309,r64>
.data 2 [205] # 77 2 vec<309,r64>
.data 1 [65] # 79 1 vec<309,r64>
.data 3 [0] # 80 3 vec<309,r64>
.data 1 [32] # 83 1 vec<309,r64>
.data 1 [95] # 84 1 vec<309,r64>
.data 1 [160] # 85 1 vec<309,r64>
.data 1 [2] # 86 1 vec<309,r64>
.data 1 [66] # 87 1 vec<309,r64>
.data 3 [0] # 88 3 vec<309,r64>
.data 1 [232] # 91 1 vec<309,r64>
.data 1 [118] # 92 1 vec<309,r64>
.data 1 [72] # 93 1 vec<309,r64>
.data 1 [55] # 94 1 vec<309,r64>
.data 1 [66] # 95 1 vec<309,r64>
.data 3 [0] # 96 3 vec<309,r64>
.data 1 [162] # 99 1 vec<309,r64>
.data 1 [148] # 100 1 vec<309,r64>
.data 1 [26] # 101 1 vec<309,r64>
.data 1 [109] # 102 1 vec<309,r64>
.data 1 [66] # 103 1 vec<309,r64>
.data 2 [0] # 104 2 vec<309,r64>
.data 1 [64] # 106 1 vec<309,r64>
.data 1 [229] # 107 1 vec<309,r64>
.data 1 [156] # 108 1 vec<309,r64>
.data 1 [48] # 109 1 vec<309,r64>
.data 1 [162] # 110 1 vec<309,r64>
.data 1 [66] # 111 1 vec<309,r64>
.data 2 [0] # 112 2 vec<309,r64>
.data 1 [144] # 114 1 vec<309,r64>
.data 1 [30] # 115 1 vec<309,r64>
.data 1 [196] # 116 1 vec<309,r64>
.data 1 [188] # 117 1 vec<309,r64>
.data 1 [214] # 118 1 vec<309,r64>
.data 1 [66] # 119 1 vec<309,r64>
.data 2 [0] # 120 2 vec<309,r64>
.data 1 [52] # 122 1 vec<309,r64>
.data 1 [38] # 123 1 vec<309,r64>
.data 1 [245] # 124 1 vec<309,r64>
.data 1 [107] # 125 1 vec<309,r64>
.data 1 [12] # 126 1 vec<309,r64>
.data 1 [67] # 127 1 vec<309,r64>
.data 1 [0] # 128 1 vec<309,r64>
.data 1 [128] # 129 1 vec<309,r64>
.data 1 [224] # 130 1 vec<309,r64>
.data 1 [55] # 131 1 vec<309,r64>
.data 1 [121] # 132 1 vec<309,r64>
.data 1 [195] # 133 1 vec<309,r64>
.data 1 [65] # 134 1 vec<309,r64>
.data 1 [67] # 135 1 vec<309,r64>
.data 1 [0] # 136 1 vec<309,r64>
.data 1 [160] # 137 1 vec<309,r64>
.data 1 [216] # 138 1 vec<309,r64>
.data 1 [133] # 139 1 vec<309,r64>
.data 1 [87] # 140 1 vec<309,r64>
.data 1 [52] # 141 1 vec<309,r64>
.data 1 [118] # 142 1 vec<309,r64>
.data 1 [67] # 143 1 vec<309,r64>
.data 1 [0] # 144 1 vec<309,r64>
.data 1 [200] # 145 1 vec<309,r64>
.data 1 [78] # 146 1 vec<309,r64>
.data 1 [103] # 147 1 vec<309,r64>
.data 1 [109] # 148 1 vec<309,r64>
.data 1 [193] # 149 1 vec<309,r64>
.data 1 [171] # 150 1 vec<309,r64>
.data 1 [67] # 151 1 vec<309,r64>
.data 1 [0] # 152 1 vec<309,r64>
.data 1 [61] # 153 1 vec<309,r64>
.data 1 [145] # 154 1 vec<309,r64>
.data 1 [96] # 155 1 vec<309,r64>
.data 1 [228] # 156 1 vec<309,r64>
.data 1 [88] # 157 1 vec<309,r64>
.data 1 [225] # 158 1 vec<309,r64>
.data 1 [67] # 159 1 vec<309,r64>
.data 1 [64] # 160 1 vec<309,r64>
.data 1 [140] # 161 1 vec<309,r64>
.data 1 [181] # 162 1 vec<309,r64>
.data 1 [120] # 163 1 vec<309,r64>
.data 1 [29] # 164 1 vec<309,r64>
.data 1 [175] # 165 1 vec<309,r64>
.data 1 [21] # 166 1 vec<309,r64>
.data 1 [68] # 167 1 vec<309,r64>
.data 1 [80] # 168 1 vec<309,r64>
.data 1 [239] # 169 1 vec<309,r64>
.data 1 [226] # 170 1 vec<309,r64>
.data 1 [214] # 171 1 vec<309,r64>
.data 1 [228] # 172 1 vec<309,r64>
.data 1 [26] # 173 1 vec<309,r64>
.data 1 [75] # 174 1 vec<309,r64>
.data 1 [68] # 175 1 vec<309,r64>
.data 1 [146] # 176 1 vec<309,r64>
.data 1 [213] # 177 1 vec<309,r64>
.data 1 [77] # 178 1 vec<309,r64>
.data 1 [6] # 179 1 vec<309,r64>
.data 1 [207] # 180 1 vec<309,r64>
.data 1 [240] # 181 1 vec<309,r64>
.data 1 [128] # 182 1 vec<309,r64>
.data 1 [68] # 183 1 vec<309,r64>
.data 1 [246] # 184 1 vec<309,r64>
.data 1 [74] # 185 1 vec<309,r64>
.data 1 [225] # 186 1 vec<309,r64>
.data 1 [199] # 187 1 vec<309,r64>
.data 1 [2] # 188 1 vec<309,r64>
.data 1 [45] # 189 1 vec<309,r64>
.data 1 [181] # 190 1 vec<309,r64>
.data 1 [68] # 191 1 vec<309,r64>
.data 1 [180] # 192 1 vec<309,r64>
.data 1 [157] # 193 1 vec<309,r64>
.data 1 [217] # 194 1 vec<309,r64>
.data 1 [121] # 195 1 vec<309,r64>
.data 1 [67] # 196 1 vec<309,r64>
.data 1 [120] # 197 1 vec<309,r64>
.data 1 [234] # 198 1 vec<309,r64>
.data 1 [68] # 199 1 vec<309,r64>
.data 1 [145] # 200 1 vec<309,r64>
.data 1 [2] # 201 1 vec<309,r64>
.data 1 [40] # 202 1 vec<309,r64>
.data 1 [44] # 203 1 vec<309,r64>
.data 1 [42] # 204 1 vec<309,r64>
.data 1 [139] # 205 1 vec<309,r64>
.data 1 [32] # 206 1 vec<309,r64>
.data 1 [69] # 207 1 vec<309,r64>
.data 1 [53] # 208 1 vec<309,r64>
.data 1 [3] # 209 1 vec<309,r64>
.data 1 [50] # 210 1 vec<309,r64>
.data 1 [183] # 211 1 vec<309,r64>
.data 1 [244] # 212 1 vec<309,r64>
.data 1 [173] # 213 1 vec<309,r64>
.data 1 [84] # 214 1 vec<309,r64>
.data 1 [69] # 215 1 vec<309,r64>
.data 1 [2] # 216 1 vec<309,r64>
.data 1 [132] # 217 1 vec<309,r64>
.data 1 [254] # 218 1 vec<309,r64>
.data 1 [228] # 219 1 vec<309,r64>
.data 1 [113] # 220 1 vec<309,r64>
.data 1 [217] # 221 1 vec<309,r64>
.data 1 [137] # 222 1 vec<309,r64>
.data 1 [69] # 223 1 vec<309,r64>
.data 1 [129] # 224 1 vec<309,r64>
.data 1 [18] # 225 1 vec<309,r64>
.data 1 [31] # 226 1 vec<309,r64>
.data 1 [47] # 227 1 vec<309,r64>
.data 1 [231] # 228 1 vec<309,r64>
.data 1 [39] # 229 1 vec<309,r64>
.data 1 [192] # 230 1 vec<309,r64>
.data 1 [69] # 231 1 vec<309,r64>
.data 1 [33] # 232 1 vec<309,r64>
.data 1 [215] # 233 1 vec<309,r64>
.data 1 [230] # 234 1 vec<309,r64>
.data 1 [250] # 235 1 vec<309,r64>
.data 1 [224] # 236 1 vec<309,r64>
.data 1 [49] # 237 1 vec<309,r64>
.data 1 [244] # 238 1 vec<309,r64>
.data 1 [69] # 239 1 vec<309,r64>
.data 1 [234] # 240 1 vec<309,r64>
.data 1 [140] # 241 1 vec<309,r64>
.data 1 [160] # 242 1 vec<309,r64>
.data 1 [57] # 243 1 vec<309,r64>
.data 1 [89] # 244 1 vec<309,r64>
.data 1 [62] # 245 1 vec<309,r64>
.data 1 [41] # 246 1 vec<309,r64>
.data 1 [70] # 247 1 vec<309,r64>
.data 1 [36] # 248 1 vec<309,r64>
.data 1 [176] # 249 1 vec<309,r64>
.data 1 [8] # 250 1 vec<309,r64>
.data 1 [136] # 251 1 vec<309,r64>
.data 1 [239] # 252 1 vec<309,r64>
.data 1 [141] # 253 1 vec<309,r64>
.data 1 [95] # 254 1 vec<309,r64>
.data 1 [70] # 255 1 vec<309,r64>
.data 1 [23] # 256 1 vec<309,r64>
.data 1 [110] # 257 1 vec<309,r64>
.data 1 [5] # 258 1 vec<309,r64>
.data 2 [181] # 259 2 vec<309,r64>
.data 1 [184] # 261 1 vec<309,r64>
.data 1 [147] # 262 1 vec<309,r64>
.data 1 [70] # 263 1 vec<309,r64>
.data 1 [156] # 264 1 vec<309,r64>
.data 1 [201] # 265 1 vec<309,r64>
.data 1 [70] # 266 1 vec<309,r64>
.data 1 [34] # 267 1 vec<309,r64>
.data 1 [227] # 268 1 vec<309,r64>
.data 1 [166] # 269 1 vec<309,r64>
.data 1 [200] # 270 1 vec<309,r64>
.data 1 [70] # 271 1 vec<309,r64>
.data 1 [3] # 272 1 vec<309,r64>
.data 1 [124] # 273 1 vec<309,r64>
.data 1 [216] # 274 1 vec<309,r64>
.data 1 [234] # 275 1 vec<309,r64>
.data 1 [155] # 276 1 vec<309,r64>
.data 1 [208] # 277 1 vec<309,r64>
.data 1 [254] # 278 1 vec<309,r64>
.data 1 [70] # 279 1 vec<309,r64>
.data 1 [130] # 280 1 vec<309,r64>
.data 1 [77] # 281 1 vec<309,r64>
.data 1 [199] # 282 1 vec<309,r64>
.data 1 [114] # 283 1 vec<309,r64>
.data 1 [97] # 284 1 vec<309,r64>
.data 1 [66] # 285 1 vec<309,r64>
.data 1 [51] # 286 1 vec<309,r64>
.data 1 [71] # 287 1 vec<309,r64>
.data 1 [227] # 288 1 vec<309,r64>
.data 1 [32] # 289 1 vec<309,r64>
.data 1 [121] # 290 1 vec<309,r64>
.data 1 [207] # 291 1 vec<309,r64>
.data 1 [249] # 292 1 vec<309,r64>
.data 1 [18] # 293 1 vec<309,r64>
.data 1 [104] # 294 1 vec<309,r64>
.data 1 [71] # 295 1 vec<309,r64>
.data 1 [27] # 296 1 vec<309,r64>
.data 1 [105] # 297 1 vec<309,r64>
.data 1 [87] # 298 1 vec<309,r64>
.data 1 [67] # 299 1 vec<309,r64>
.data 1 [184] # 300 1 vec<309,r64>
.data 1 [23] # 301 1 vec<309,r64>
.data 1 [158] # 302 1 vec<309,r64>
.data 1 [71] # 303 1 vec<309,r64>
.data 1 [177] # 304 1 vec<309,r64>
.data 1 [161] # 305 1 vec<309,r64>
.data 1 [22] # 306 1 vec<309,r64>
.data 1 [42] # 307 1 vec<309,r64>
.data 1 [211] # 308 1 vec<309,r64>
.data 1 [206] # 309 1 vec<309,r64>
.data 1 [210] # 310 1 vec<309,r64>
.data 1 [71] # 311 1 vec<309,r64>
.data 1 [29] # 312 1 vec<309,r64>
.data 1 [74] # 313 1 vec<309,r64>
.data 1 [156] # 314 1 vec<309,r64>
.data 1 [244] # 315 1 vec<309,r64>
.data 1 [135] # 316 1 vec<309,r64>
.data 1 [130] # 317 1 vec<309,r64>
.data 1 [7] # 318 1 vec<309,r64>
.data 1 [72] # 319 1 vec<309,r64>
.data 1 [165] # 320 1 vec<309,r64>
.data 1 [92] # 321 1 vec<309,r64>
.data 1 [195] # 322 1 vec<309,r64>
.data 1 [241] # 323 1 vec<309,r64>
.data 1 [41] # 324 1 vec<309,r64>
.data 1 [99] # 325 1 vec<309,r64>
.data 1 [61] # 326 1 vec<309,r64>
.data 1 [72] # 327 1 vec<309,r64>
.data 1 [231] # 328 1 vec<309,r64>
.data 1 [25] # 329 1 vec<309,r64>
.data 1 [26] # 330 1 vec<309,r64>
.data 1 [55] # 331 1 vec<309,r64>
.data 1 [250] # 332 1 vec<309,r64>
.data 1 [93] # 333 1 vec<309,r64>
.data 1 [114] # 334 1 vec<309,r64>
.data 1 [72] # 335 1 vec<309,r64>
.data 1 [97] # 336 1 vec<309,r64>
.data 1 [160] # 337 1 vec<309,r64>
.data 1 [224] # 338 1 vec<309,r64>
.data 1 [196] # 339 1 vec<309,r64>
.data 1 [120] # 340 1 vec<309,r64>
.data 1 [245] # 341 1 vec<309,r64>
.data 1 [166] # 342 1 vec<309,r64>
.data 1 [72] # 343 1 vec<309,r64>
.data 1 [121] # 344 1 vec<309,r64>
.data 1 [200] # 345 1 vec<309,r64>
.data 1 [24] # 346 1 vec<309,r64>
.data 1 [246] # 347 1 vec<309,r64>
.data 1 [214] # 348 1 vec<309,r64>
.data 1 [178] # 349 1 vec<309,r64>
.data 1 [220] # 350 1 vec<309,r64>
.data 1 [72] # 351 1 vec<309,r64>
.data 1 [76] # 352 1 vec<309,r64>
.data 1 [125] # 353 1 vec<309,r64>
.data 1 [207] # 354 1 vec<309,r64>
.data 1 [89] # 355 1 vec<309,r64>
.data 1 [198] # 356 1 vec<309,r64>
.data 1 [239] # 357 1 vec<309,r64>
.data 1 [17] # 358 1 vec<309,r64>
.data 1 [73] # 359 1 vec<309,r64>
.data 1 [158] # 360 1 vec<309,r64>
.data 1 [92] # 361 1 vec<309,r64>
.data 1 [67] # 362 1 vec<309,r64>
.data 1 [240] # 363 1 vec<309,r64>
.data 1 [183] # 364 1 vec<309,r64>
.data 1 [107] # 365 1 vec<309,r64>
.data 1 [70] # 366 1 vec<309,r64>
.data 1 [73] # 367 1 vec<309,r64>
.data 1 [198] # 368 1 vec<309,r64>
.data 1 [51] # 369 1 vec<309,r64>
.data 1 [84] # 370 1 vec<309,r64>
.data 1 [236] # 371 1 vec<309,r64>
.data 1 [165] # 372 1 vec<309,r64>
.data 1 [6] # 373 1 vec<309,r64>
.data 1 [124] # 374 1 vec<309,r64>
.data 1 [73] # 375 1 vec<309,r64>
.data 1 [92] # 376 1 vec<309,r64>
.data 1 [160] # 377 1 vec<309,r64>
.data 1 [180] # 378 1 vec<309,r64>
.data 1 [179] # 379 1 vec<309,r64>
.data 1 [39] # 380 1 vec<309,r64>
.data 1 [132] # 381 1 vec<309,r64>
.data 1 [177] # 382 1 vec<309,r64>
.data 1 [73] # 383 1 vec<309,r64>
.data 1 [115] # 384 1 vec<309,r64>
.data 1 [200] # 385 1 vec<309,r64>
.data 1 [161] # 386 1 vec<309,r64>
.data 1 [160] # 387 1 vec<309,r64>
.data 1 [49] # 388 1 vec<309,r64>
.data 2 [229] # 389 2 vec<309,r64>
.data 1 [73] # 391 1 vec<309,r64>
.data 1 [143] # 392 1 vec<309,r64>
.data 1 [58] # 393 1 vec<309,r64>
.data 1 [202] # 394 1 vec<309,r64>
.data 1 [8] # 395 1 vec<309,r64>
.data 1 [126] # 396 1 vec<309,r64>
.data 1 [94] # 397 1 vec<309,r64>
.data 1 [27] # 398 1 vec<309,r64>
.data 1 [74] # 399 1 vec<309,r64>
.data 1 [154] # 400 1 vec<309,r64>
.data 1 [100] # 401 1 vec<309,r64>
.data 1 [126] # 402 1 vec<309,r64>
.data 1 [197] # 403 1 vec<309,r64>
.data 1 [14] # 404 1 vec<309,r64>
.data 1 [27] # 405 1 vec<309,r64>
.data 1 [81] # 406 1 vec<309,r64>
.data 1 [74] # 407 1 vec<309,r64>
.data 1 [192] # 408 1 vec<309,r64>
.data 1 [253] # 409 1 vec<309,r64>
.data 1 [221] # 410 1 vec<309,r64>
.data 1 [118] # 411 1 vec<309,r64>
.data 1 [210] # 412 1 vec<309,r64>
.data 1 [97] # 413 1 vec<309,r64>
.data 1 [133] # 414 1 vec<309,r64>
.data 1 [74] # 415 1 vec<309,r64>
.data 1 [48] # 416 1 vec<309,r64>
.data 1 [125] # 417 1 vec<309,r64>
.data 1 [149] # 418 1 vec<309,r64>
.data 1 [20] # 419 1 vec<309,r64>
.data 1 [71] # 420 1 vec<309,r64>
.data 2 [186] # 421 2 vec<309,r64>
.data 1 [74] # 423 1 vec<309,r64>
.data 1 [62] # 424 1 vec<309,r64>
.data 1 [110] # 425 1 vec<309,r64>
.data 1 [221] # 426 1 vec<309,r64>
.data 2 [108] # 427 2 vec<309,r64>
.data 1 [180] # 429 1 vec<309,r64>
.data 1 [240] # 430 1 vec<309,r64>
.data 1 [74] # 431 1 vec<309,r64>
.data 1 [206] # 432 1 vec<309,r64>
.data 1 [201] # 433 1 vec<309,r64>
.data 1 [20] # 434 1 vec<309,r64>
.data 1 [136] # 435 1 vec<309,r64>
.data 1 [135] # 436 1 vec<309,r64>
.data 1 [225] # 437 1 vec<309,r64>
.data 1 [36] # 438 1 vec<309,r64>
.data 1 [75] # 439 1 vec<309,r64>
.data 1 [65] # 440 1 vec<309,r64>
.data 1 [252] # 441 1 vec<309,r64>
.data 1 [25] # 442 1 vec<309,r64>
.data 1 [106] # 443 1 vec<309,r64>
.data 1 [233] # 444 1 vec<309,r64>
.data 1 [25] # 445 1 vec<309,r64>
.data 1 [90] # 446 1 vec<309,r64>
.data 1 [75] # 447 1 vec<309,r64>
.data 1 [169] # 448 1 vec<309,r64>
.data 1 [61] # 449 1 vec<309,r64>
.data 1 [80] # 450 1 vec<309,r64>
.data 1 [226] # 451 1 vec<309,r64>
.data 1 [49] # 452 1 vec<309,r64>
.data 1 [80] # 453 1 vec<309,r64>
.data 1 [144] # 454 1 vec<309,r64>
.data 1 [75] # 455 1 vec<309,r64>
.data 1 [19] # 456 1 vec<309,r64>
.data 1 [77] # 457 1 vec<309,r64>
.data 1 [228] # 458 1 vec<309,r64>
.data 1 [90] # 459 1 vec<309,r64>
.data 1 [62] # 460 1 vec<309,r64>
.data 1 [100] # 461 1 vec<309,r64>
.data 1 [196] # 462 1 vec<309,r64>
.data 1 [75] # 463 1 vec<309,r64>
.data 1 [87] # 464 1 vec<309,r64>
.data 1 [96] # 465 1 vec<309,r64>
.data 1 [157] # 466 1 vec<309,r64>
.data 1 [241] # 467 1 vec<309,r64>
.data 1 [77] # 468 1 vec<309,r64>
.data 1 [125] # 469 1 vec<309,r64>
.data 1 [249] # 470 1 vec<309,r64>
.data 1 [75] # 471 1 vec<309,r64>
.data 1 [109] # 472 1 vec<309,r64>
.data 1 [184] # 473 1 vec<309,r64>
.data 1 [4] # 474 1 vec<309,r64>
.data 1 [110] # 475 1 vec<309,r64>
.data 1 [161] # 476 1 vec<309,r64>
.data 1 [220] # 477 1 vec<309,r64>
.data 1 [47] # 478 1 vec<309,r64>
.data 1 [76] # 479 1 vec<309,r64>
.data 1 [68] # 480 1 vec<309,r64>
.data 1 [243] # 481 1 vec<309,r64>
.data 1 [194] # 482 1 vec<309,r64>
.data 2 [228] # 483 2 vec<309,r64>
.data 1 [233] # 485 1 vec<309,r64>
.data 1 [99] # 486 1 vec<309,r64>
.data 1 [76] # 487 1 vec<309,r64>
.data 1 [21] # 488 1 vec<309,r64>
.data 1 [176] # 489 1 vec<309,r64>
.data 1 [243] # 490 1 vec<309,r64>
.data 1 [29] # 491 1 vec<309,r64>
.data 1 [94] # 492 1 vec<309,r64>
.data 1 [228] # 493 1 vec<309,r64>
.data 1 [152] # 494 1 vec<309,r64>
.data 1 [76] # 495 1 vec<309,r64>
.data 1 [27] # 496 1 vec<309,r64>
.data 1 [156] # 497 1 vec<309,r64>
.data 1 [112] # 498 1 vec<309,r64>
.data 1 [165] # 499 1 vec<309,r64>
.data 1 [117] # 500 1 vec<309,r64>
.data 1 [29] # 501 1 vec<309,r64>
.data 1 [207] # 502 1 vec<309,r64>
.data 1 [76] # 503 1 vec<309,r64>
.data 1 [145] # 504 1 vec<309,r64>
.data 1 [97] # 505 1 vec<309,r64>
.data 1 [102] # 506 1 vec<309,r64>
.data 1 [135] # 507 1 vec<309,r64>
.data 1 [105] # 508 1 vec<309,r64>
.data 1 [114] # 509 1 vec<309,r64>
.data 1 [3] # 510 1 vec<309,r64>
.data 1 [77] # 511 1 vec<309,r64>
.data 1 [245] # 512 1 vec<309,r64>
.data 1 [249] # 513 1 vec<309,r64>
.data 1 [63] # 514 1 vec<309,r64>
.data 1 [233] # 515 1 vec<309,r64>
.data 1 [3] # 516 1 vec<309,r64>
.data 1 [79] # 517 1 vec<309,r64>
.data 1 [56] # 518 1 vec<309,r64>
.data 1 [77] # 519 1 vec<309,r64>
.data 1 [114] # 520 1 vec<309,r64>
.data 1 [248] # 521 1 vec<309,r64>
.data 1 [143] # 522 1 vec<309,r64>
.data 1 [227] # 523 1 vec<309,r64>
.data 1 [196] # 524 1 vec<309,r64>
.data 1 [98] # 525 1 vec<309,r64>
.data 1 [110] # 526 1 vec<309,r64>
.data 1 [77] # 527 1 vec<309,r64>
.data 1 [71] # 528 1 vec<309,r64>
.data 1 [251] # 529 1 vec<309,r64>
.data 1 [57] # 530 1 vec<309,r64>
.data 1 [14] # 531 1 vec<309,r64>
.data 1 [187] # 532 1 vec<309,r64>
.data 1 [253] # 533 1 vec<309,r64>
.data 1 [162] # 534 1 vec<309,r64>
.data 1 [77] # 535 1 vec<309,r64>
.data 1 [25] # 536 1 vec<309,r64>
.data 1 [122] # 537 1 vec<309,r64>
.data 1 [200] # 538 1 vec<309,r64>
.data 1 [209] # 539 1 vec<309,r64>
.data 1 [41] # 540 1 vec<309,r64>
.data 1 [189] # 541 1 vec<309,r64>
.data 1 [215] # 542 1 vec<309,r64>
.data 1 [77] # 543 1 vec<309,r64>
.data 1 [159] # 544 1 vec<309,r64>
.data 1 [152] # 545 1 vec<309,r64>
.data 1 [58] # 546 1 vec<309,r64>
.data 1 [70] # 547 1 vec<309,r64>
.data 1 [116] # 548 1 vec<309,r64>
.data 1 [172] # 549 1 vec<309,r64>
.data 1 [13] # 550 1 vec<309,r64>
.data 1 [78] # 551 1 vec<309,r64>
.data 1 [100] # 552 1 vec<309,r64>
.data 1 [159] # 553 1 vec<309,r64>
.data 1 [228] # 554 1 vec<309,r64>
.data 1 [171] # 555 1 vec<309,r64>
.data 1 [200] # 556 1 vec<309,r64>
.data 1 [139] # 557 1 vec<309,r64>
.data 1 [66] # 558 1 vec<309,r64>
.data 1 [78] # 559 1 vec<309,r64>
.data 1 [61] # 560 1 vec<309,r64>
.data 1 [199] # 561 1 vec<309,r64>
.data 1 [221] # 562 1 vec<309,r64>
.data 1 [214] # 563 1 vec<309,r64>
.data 1 [186] # 564 1 vec<309,r64>
.data 1 [46] # 565 1 vec<309,r64>
.data 1 [119] # 566 1 vec<309,r64>
.data 1 [78] # 567 1 vec<309,r64>
.data 1 [12] # 568 1 vec<309,r64>
.data 1 [57] # 569 1 vec<309,r64>
.data 1 [149] # 570 1 vec<309,r64>
.data 1 [140] # 571 1 vec<309,r64>
.data 1 [105] # 572 1 vec<309,r64>
.data 1 [250] # 573 1 vec<309,r64>
.data 1 [172] # 574 1 vec<309,r64>
.data 1 [78] # 575 1 vec<309,r64>
.data 1 [167] # 576 1 vec<309,r64>
.data 1 [67] # 577 1 vec<309,r64>
.data 1 [221] # 578 1 vec<309,r64>
.data 1 [247] # 579 1 vec<309,r64>
.data 1 [129] # 580 1 vec<309,r64>
.data 1 [28] # 581 1 vec<309,r64>
.data 1 [226] # 582 1 vec<309,r64>
.data 1 [78] # 583 1 vec<309,r64>
.data 1 [145] # 584 1 vec<309,r64>
.data 1 [148] # 585 1 vec<309,r64>
.data 1 [212] # 586 1 vec<309,r64>
.data 1 [117] # 587 1 vec<309,r64>
.data 1 [162] # 588 1 vec<309,r64>
.data 1 [163] # 589 1 vec<309,r64>
.data 1 [22] # 590 1 vec<309,r64>
.data 1 [79] # 591 1 vec<309,r64>
.data 1 [181] # 592 1 vec<309,r64>
.data 1 [185] # 593 1 vec<309,r64>
.data 1 [73] # 594 1 vec<309,r64>
.data 1 [19] # 595 1 vec<309,r64>
.data 1 [139] # 596 1 vec<309,r64>
.data 2 [76] # 597 2 vec<309,r64>
.data 1 [79] # 599 1 vec<309,r64>
.data 1 [17] # 600 1 vec<309,r64>
.data 1 [20] # 601 1 vec<309,r64>
.data 1 [14] # 602 1 vec<309,r64>
.data 1 [236] # 603 1 vec<309,r64>
.data 1 [214] # 604 1 vec<309,r64>
.data 1 [175] # 605 1 vec<309,r64>
.data 1 [129] # 606 1 vec<309,r64>
.data 1 [79] # 607 1 vec<309,r64>
.data 1 [22] # 608 1 vec<309,r64>
.data 1 [153] # 609 1 vec<309,r64>
.data 1 [17] # 610 1 vec<309,r64>
.data 1 [167] # 611 1 vec<309,r64>
.data 1 [204] # 612 1 vec<309,r64>
.data 1 [27] # 613 1 vec<309,r64>
.data 1 [182] # 614 1 vec<309,r64>
.data 1 [79] # 615 1 vec<309,r64>
.data 1 [91] # 616 1 vec<309,r64>
.data 1 [255] # 617 1 vec<309,r64>
.data 1 [213] # 618 1 vec<309,r64>
.data 1 [208] # 619 1 vec<309,r64>
.data 1 [191] # 620 1 vec<309,r64>
.data 1 [162] # 621 1 vec<309,r64>
.data 1 [235] # 622 1 vec<309,r64>
.data 1 [79] # 623 1 vec<309,r64>
.data 1 [153] # 624 1 vec<309,r64>
.data 1 [191] # 625 1 vec<309,r64>
.data 1 [133] # 626 1 vec<309,r64>
.data 1 [226] # 627 1 vec<309,r64>
.data 1 [183] # 628 1 vec<309,r64>
.data 1 [69] # 629 1 vec<309,r64>
.data 1 [33] # 630 1 vec<309,r64>
.data 1 [80] # 631 1 vec<309,r64>
.data 1 [127] # 632 1 vec<309,r64>
.data 1 [47] # 633 1 vec<309,r64>
.data 1 [39] # 634 1 vec<309,r64>
.data 1 [219] # 635 1 vec<309,r64>
.data 1 [37] # 636 1 vec<309,r64>
.data 1 [151] # 637 1 vec<309,r64>
.data 1 [85] # 638 1 vec<309,r64>
.data 1 [80] # 639 1 vec<309,r64>
.data 1 [95] # 640 1 vec<309,r64>
.data 1 [251] # 641 1 vec<309,r64>
.data 1 [240] # 642 1 vec<309,r64>
.data 1 [81] # 643 1 vec<309,r64>
.data 1 [239] # 644 1 vec<309,r64>
.data 1 [252] # 645 1 vec<309,r64>
.data 1 [138] # 646 1 vec<309,r64>
.data 1 [80] # 647 1 vec<309,r64>
.data 1 [27] # 648 1 vec<309,r64>
.data 1 [157] # 649 1 vec<309,r64>
.data 1 [54] # 650 1 vec<309,r64>
.data 1 [147] # 651 1 vec<309,r64>
.data 1 [21] # 652 1 vec<309,r64>
.data 1 [222] # 653 1 vec<309,r64>
.data 1 [192] # 654 1 vec<309,r64>
.data 1 [80] # 655 1 vec<309,r64>
.data 1 [98] # 656 1 vec<309,r64>
.data 1 [68] # 657 1 vec<309,r64>
.data 1 [4] # 658 1 vec<309,r64>
.data 1 [248] # 659 1 vec<309,r64>
.data 1 [154] # 660 1 vec<309,r64>
.data 1 [21] # 661 1 vec<309,r64>
.data 1 [245] # 662 1 vec<309,r64>
.data 1 [80] # 663 1 vec<309,r64>
.data 1 [123] # 664 1 vec<309,r64>
.data 1 [85] # 665 1 vec<309,r64>
.data 1 [5] # 666 1 vec<309,r64>
.data 1 [182] # 667 1 vec<309,r64>
.data 1 [1] # 668 1 vec<309,r64>
.data 1 [91] # 669 1 vec<309,r64>
.data 1 [42] # 670 1 vec<309,r64>
.data 1 [81] # 671 1 vec<309,r64>
.data 1 [109] # 672 1 vec<309,r64>
.data 1 [85] # 673 1 vec<309,r64>
.data 1 [195] # 674 1 vec<309,r64>
.data 1 [17] # 675 1 vec<309,r64>
.data 1 [225] # 676 1 vec<309,r64>
.data 1 [120] # 677 1 vec<309,r64>
.data 1 [96] # 678 1 vec<309,r64>
.data 1 [81] # 679 1 vec<309,r64>
.data 1 [200] # 680 1 vec<309,r64>
.data 1 [42] # 681 1 vec<309,r64>
.data 1 [52] # 682 1 vec<309,r64>
.data 1 [86] # 683 1 vec<309,r64>
.data 1 [25] # 684 1 vec<309,r64>
.data 1 [151] # 685 1 vec<309,r64>
.data 1 [148] # 686 1 vec<309,r64>
.data 1 [81] # 687 1 vec<309,r64>
.data 1 [122] # 688 1 vec<309,r64>
.data 1 [53] # 689 1 vec<309,r64>
.data 1 [193] # 690 1 vec<309,r64>
.data 1 [171] # 691 1 vec<309,r64>
.data 1 [223] # 692 1 vec<309,r64>
.data 1 [188] # 693 1 vec<309,r64>
.data 1 [201] # 694 1 vec<309,r64>
.data 1 [81] # 695 1 vec<309,r64>
.data 1 [108] # 696 1 vec<309,r64>
.data 1 [193] # 697 1 vec<309,r64>
.data 1 [88] # 698 1 vec<309,r64>
.data 1 [203] # 699 1 vec<309,r64>
.data 1 [11] # 700 1 vec<309,r64>
.data 1 [22] # 701 1 vec<309,r64>
.data 1 [0] # 702 1 vec<309,r64>
.data 1 [82] # 703 1 vec<309,r64>
.data 1 [199] # 704 1 vec<309,r64>
.data 1 [241] # 705 1 vec<309,r64>
.data 1 [46] # 706 1 vec<309,r64>
.data 1 [190] # 707 1 vec<309,r64>
.data 1 [142] # 708 1 vec<309,r64>
.data 1 [27] # 709 1 vec<309,r64>
.data 1 [52] # 710 1 vec<309,r64>
.data 1 [82] # 711 1 vec<309,r64>
.data 1 [57] # 712 1 vec<309,r64>
.data 1 [174] # 713 1 vec<309,r64>
.data 1 [186] # 714 1 vec<309,r64>
.data 1 [109] # 715 1 vec<309,r64>
.data 1 [114] # 716 1 vec<309,r64>
.data 1 [34] # 717 1 vec<309,r64>
.data 1 [105] # 718 1 vec<309,r64>
.data 1 [82] # 719 1 vec<309,r64>
.data 1 [199] # 720 1 vec<309,r64>
.data 1 [89] # 721 1 vec<309,r64>
.data 1 [41] # 722 1 vec<309,r64>
.data 1 [9] # 723 1 vec<309,r64>
.data 1 [15] # 724 1 vec<309,r64>
.data 1 [107] # 725 1 vec<309,r64>
.data 1 [159] # 726 1 vec<309,r64>
.data 1 [82] # 727 1 vec<309,r64>
.data 1 [29] # 728 1 vec<309,r64>
.data 1 [216] # 729 1 vec<309,r64>
.data 1 [185] # 730 1 vec<309,r64>
.data 1 [101] # 731 1 vec<309,r64>
.data 1 [233] # 732 1 vec<309,r64>
.data 1 [162] # 733 1 vec<309,r64>
.data 1 [211] # 734 1 vec<309,r64>
.data 1 [82] # 735 1 vec<309,r64>
.data 1 [36] # 736 1 vec<309,r64>
.data 1 [78] # 737 1 vec<309,r64>
.data 1 [40] # 738 1 vec<309,r64>
.data 1 [191] # 739 1 vec<309,r64>
.data 1 [163] # 740 1 vec<309,r64>
.data 1 [139] # 741 1 vec<309,r64>
.data 1 [8] # 742 1 vec<309,r64>
.data 1 [83] # 743 1 vec<309,r64>
.data 1 [173] # 744 1 vec<309,r64>
.data 1 [97] # 745 1 vec<309,r64>
.data 1 [242] # 746 1 vec<309,r64>
.data 1 [174] # 747 1 vec<309,r64>
.data 1 [140] # 748 1 vec<309,r64>
.data 1 [174] # 749 1 vec<309,r64>
.data 1 [62] # 750 1 vec<309,r64>
.data 1 [83] # 751 1 vec<309,r64>
.data 1 [12] # 752 1 vec<309,r64>
.data 1 [125] # 753 1 vec<309,r64>
.data 1 [87] # 754 1 vec<309,r64>
.data 1 [237] # 755 1 vec<309,r64>
.data 1 [23] # 756 1 vec<309,r64>
.data 1 [45] # 757 1 vec<309,r64>
.data 1 [115] # 758 1 vec<309,r64>
.data 1 [83] # 759 1 vec<309,r64>
.data 1 [79] # 760 1 vec<309,r64>
.data 1 [92] # 761 1 vec<309,r64>
.data 1 [173] # 762 1 vec<309,r64>
.data 1 [232] # 763 1 vec<309,r64>
.data 1 [93] # 764 1 vec<309,r64>
.data 1 [248] # 765 1 vec<309,r64>
.data 1 [167] # 766 1 vec<309,r64>
.data 1 [83] # 767 1 vec<309,r64>
.data 1 [99] # 768 1 vec<309,r64>
.data 1 [179] # 769 1 vec<309,r64>
.data 1 [216] # 770 1 vec<309,r64>
.data 1 [98] # 771 1 vec<309,r64>
.data 1 [117] # 772 1 vec<309,r64>
.data 1 [246] # 773 1 vec<309,r64>
.data 1 [221] # 774 1 vec<309,r64>
.data 1 [83] # 775 1 vec<309,r64>
.data 1 [30] # 776 1 vec<309,r64>
.data 1 [112] # 777 1 vec<309,r64>
.data 1 [199] # 778 1 vec<309,r64>
.data 1 [93] # 779 1 vec<309,r64>
.data 1 [9] # 780 1 vec<309,r64>
.data 1 [186] # 781 1 vec<309,r64>
.data 1 [18] # 782 1 vec<309,r64>
.data 1 [84] # 783 1 vec<309,r64>
.data 1 [37] # 784 1 vec<309,r64>
.data 1 [76] # 785 1 vec<309,r64>
.data 1 [57] # 786 1 vec<309,r64>
.data 1 [181] # 787 1 vec<309,r64>
.data 1 [139] # 788 1 vec<309,r64>
.data 1 [104] # 789 1 vec<309,r64>
.data 1 [71] # 790 1 vec<309,r64>
.data 1 [84] # 791 1 vec<309,r64>
.data 1 [46] # 792 1 vec<309,r64>
.data 1 [159] # 793 1 vec<309,r64>
.data 1 [135] # 794 1 vec<309,r64>
.data 1 [162] # 795 1 vec<309,r64>
.data 1 [174] # 796 1 vec<309,r64>
.data 1 [66] # 797 1 vec<309,r64>
.data 1 [125] # 798 1 vec<309,r64>
.data 1 [84] # 799 1 vec<309,r64>
.data 1 [125] # 800 1 vec<309,r64>
.data 1 [195] # 801 1 vec<309,r64>
.data 1 [148] # 802 1 vec<309,r64>
.data 1 [37] # 803 1 vec<309,r64>
.data 1 [173] # 804 1 vec<309,r64>
.data 1 [73] # 805 1 vec<309,r64>
.data 1 [178] # 806 1 vec<309,r64>
.data 1 [84] # 807 1 vec<309,r64>
.data 1 [92] # 808 1 vec<309,r64>
.data 1 [244] # 809 1 vec<309,r64>
.data 1 [249] # 810 1 vec<309,r64>
.data 1 [110] # 811 1 vec<309,r64>
.data 1 [24] # 812 1 vec<309,r64>
.data 1 [220] # 813 1 vec<309,r64>
.data 1 [230] # 814 1 vec<309,r64>
.data 1 [84] # 815 1 vec<309,r64>
.data 1 [115] # 816 1 vec<309,r64>
.data 1 [113] # 817 1 vec<309,r64>
.data 1 [184] # 818 1 vec<309,r64>
.data 1 [138] # 819 1 vec<309,r64>
.data 1 [30] # 820 1 vec<309,r64>
.data 1 [147] # 821 1 vec<309,r64>
.data 1 [28] # 822 1 vec<309,r64>
.data 1 [85] # 823 1 vec<309,r64>
.data 1 [232] # 824 1 vec<309,r64>
.data 1 [70] # 825 1 vec<309,r64>
.data 1 [179] # 826 1 vec<309,r64>
.data 1 [22] # 827 1 vec<309,r64>
.data 1 [243] # 828 1 vec<309,r64>
.data 1 [219] # 829 1 vec<309,r64>
.data 1 [81] # 830 1 vec<309,r64>
.data 1 [85] # 831 1 vec<309,r64>
.data 1 [162] # 832 1 vec<309,r64>
.data 1 [24] # 833 1 vec<309,r64>
.data 1 [96] # 834 1 vec<309,r64>
.data 1 [220] # 835 1 vec<309,r64>
.data 1 [239] # 836 1 vec<309,r64>
.data 1 [82] # 837 1 vec<309,r64>
.data 1 [134] # 838 1 vec<309,r64>
.data 1 [85] # 839 1 vec<309,r64>
.data 1 [202] # 840 1 vec<309,r64>
.data 1 [30] # 841 1 vec<309,r64>
.data 1 [120] # 842 1 vec<309,r64>
.data 1 [211] # 843 1 vec<309,r64>
.data 1 [171] # 844 1 vec<309,r64>
.data 1 [231] # 845 1 vec<309,r64>
.data 1 [187] # 846 1 vec<309,r64>
.data 1 [85] # 847 1 vec<309,r64>
.data 1 [63] # 848 1 vec<309,r64>
.data 1 [19] # 849 1 vec<309,r64>
.data 1 [43] # 850 1 vec<309,r64>
.data 1 [100] # 851 1 vec<309,r64>
.data 1 [203] # 852 1 vec<309,r64>
.data 1 [112] # 853 1 vec<309,r64>
.data 1 [241] # 854 1 vec<309,r64>
.data 1 [85] # 855 1 vec<309,r64>
.data 1 [14] # 856 1 vec<309,r64>
.data 1 [216] # 857 1 vec<309,r64>
.data 1 [53] # 858 1 vec<309,r64>
.data 1 [61] # 859 1 vec<309,r64>
.data 1 [254] # 860 1 vec<309,r64>
.data 1 [204] # 861 1 vec<309,r64>
.data 1 [37] # 862 1 vec<309,r64>
.data 1 [86] # 863 1 vec<309,r64>
.data 1 [18] # 864 1 vec<309,r64>
.data 1 [78] # 865 1 vec<309,r64>
.data 1 [131] # 866 1 vec<309,r64>
.data 1 [204] # 867 1 vec<309,r64>
.data 1 [61] # 868 1 vec<309,r64>
.data 1 [64] # 869 1 vec<309,r64>
.data 1 [91] # 870 1 vec<309,r64>
.data 1 [86] # 871 1 vec<309,r64>
.data 1 [203] # 872 1 vec<309,r64>
.data 1 [16] # 873 1 vec<309,r64>
.data 1 [210] # 874 1 vec<309,r64>
.data 1 [159] # 875 1 vec<309,r64>
.data 1 [38] # 876 1 vec<309,r64>
.data 1 [8] # 877 1 vec<309,r64>
.data 1 [145] # 878 1 vec<309,r64>
.data 1 [86] # 879 1 vec<309,r64>
.data 1 [254] # 880 1 vec<309,r64>
.data 1 [148] # 881 1 vec<309,r64>
.data 1 [198] # 882 1 vec<309,r64>
.data 1 [71] # 883 1 vec<309,r64>
.data 1 [48] # 884 1 vec<309,r64>
.data 1 [74] # 885 1 vec<309,r64>
.data 1 [197] # 886 1 vec<309,r64>
.data 1 [86] # 887 1 vec<309,r64>
.data 1 [61] # 888 1 vec<309,r64>
.data 1 [58] # 889 1 vec<309,r64>
.data 1 [184] # 890 1 vec<309,r64>
.data 1 [89] # 891 1 vec<309,r64>
.data 1 [188] # 892 1 vec<309,r64>
.data 1 [156] # 893 1 vec<309,r64>
.data 1 [250] # 894 1 vec<309,r64>
.data 1 [86] # 895 1 vec<309,r64>
.data 1 [102] # 896 1 vec<309,r64>
.data 1 [36] # 897 1 vec<309,r64>
.data 1 [19] # 898 1 vec<309,r64>
.data 1 [184] # 899 1 vec<309,r64>
.data 1 [245] # 900 1 vec<309,r64>
.data 1 [161] # 901 1 vec<309,r64>
.data 1 [48] # 902 1 vec<309,r64>
.data 1 [87] # 903 1 vec<309,r64>
.data 1 [128] # 904 1 vec<309,r64>
.data 1 [237] # 905 1 vec<309,r64>
.data 1 [23] # 906 1 vec<309,r64>
.data 1 [38] # 907 1 vec<309,r64>
.data 1 [115] # 908 1 vec<309,r64>
.data 1 [202] # 909 1 vec<309,r64>
.data 1 [100] # 910 1 vec<309,r64>
.data 1 [87] # 911 1 vec<309,r64>
.data 1 [224] # 912 1 vec<309,r64>
.data 1 [232] # 913 1 vec<309,r64>
.data 1 [157] # 914 1 vec<309,r64>
.data 1 [239] # 915 1 vec<309,r64>
.data 1 [15] # 916 1 vec<309,r64>
.data 1 [253] # 917 1 vec<309,r64>
.data 1 [153] # 918 1 vec<309,r64>
.data 1 [87] # 919 1 vec<309,r64>
.data 1 [140] # 920 1 vec<309,r64>
.data 1 [177] # 921 1 vec<309,r64>
.data 1 [194] # 922 1 vec<309,r64>
.data 1 [245] # 923 1 vec<309,r64>
.data 1 [41] # 924 1 vec<309,r64>
.data 1 [62] # 925 1 vec<309,r64>
.data 1 [208] # 926 1 vec<309,r64>
.data 1 [87] # 927 1 vec<309,r64>
.data 1 [239] # 928 1 vec<309,r64>
.data 1 [93] # 929 1 vec<309,r64>
.data 1 [51] # 930 1 vec<309,r64>
.data 1 [115] # 931 1 vec<309,r64>
.data 1 [180] # 932 1 vec<309,r64>
.data 1 [77] # 933 1 vec<309,r64>
.data 1 [4] # 934 1 vec<309,r64>
.data 1 [88] # 935 1 vec<309,r64>
.data 1 [107] # 936 1 vec<309,r64>
.data 1 [53] # 937 1 vec<309,r64>
.data 1 [0] # 938 1 vec<309,r64>
.data 1 [144] # 939 1 vec<309,r64>
.data 1 [33] # 940 1 vec<309,r64>
.data 1 [97] # 941 1 vec<309,r64>
.data 1 [57] # 942 1 vec<309,r64>
.data 1 [88] # 943 1 vec<309,r64>
.data 1 [197] # 944 1 vec<309,r64>
.data 1 [66] # 945 1 vec<309,r64>
.data 1 [0] # 946 1 vec<309,r64>
.data 1 [244] # 947 1 vec<309,r64>
.data 1 [105] # 948 1 vec<309,r64>
.data 1 [185] # 949 1 vec<309,r64>
.data 1 [111] # 950 1 vec<309,r64>
.data 1 [88] # 951 1 vec<309,r64>
.data 1 [187] # 952 1 vec<309,r64>
.data 1 [41] # 953 1 vec<309,r64>
.data 1 [128] # 954 1 vec<309,r64>
.data 1 [56] # 955 1 vec<309,r64>
.data 1 [226] # 956 1 vec<309,r64>
.data 1 [211] # 957 1 vec<309,r64>
.data 1 [163] # 958 1 vec<309,r64>
.data 1 [88] # 959 1 vec<309,r64>
.data 1 [42] # 960 1 vec<309,r64>
.data 1 [52] # 961 1 vec<309,r64>
.data 1 [160] # 962 1 vec<309,r64>
.data 1 [198] # 963 1 vec<309,r64>
.data 1 [218] # 964 1 vec<309,r64>
.data 1 [200] # 965 1 vec<309,r64>
.data 1 [216] # 966 1 vec<309,r64>
.data 1 [88] # 967 1 vec<309,r64>
.data 1 [53] # 968 1 vec<309,r64>
.data 1 [65] # 969 1 vec<309,r64>
.data 1 [72] # 970 1 vec<309,r64>
.data 1 [120] # 971 1 vec<309,r64>
.data 1 [17] # 972 1 vec<309,r64>
.data 1 [251] # 973 1 vec<309,r64>
.data 1 [14] # 974 1 vec<309,r64>
.data 1 [89] # 975 1 vec<309,r64>
.data 1 [193] # 976 1 vec<309,r64>
.data 1 [40] # 977 1 vec<309,r64>
.data 1 [45] # 978 1 vec<309,r64>
.data 1 [235] # 979 1 vec<309,r64>
.data 1 [234] # 980 1 vec<309,r64>
.data 1 [92] # 981 1 vec<309,r64>
.data 1 [67] # 982 1 vec<309,r64>
.data 1 [89] # 983 1 vec<309,r64>
.data 1 [241] # 984 1 vec<309,r64>
.data 1 [114] # 985 1 vec<309,r64>
.data 1 [248] # 986 1 vec<309,r64>
.data 1 [165] # 987 1 vec<309,r64>
.data 1 [37] # 988 1 vec<309,r64>
.data 1 [52] # 989 1 vec<309,r64>
.data 1 [120] # 990 1 vec<309,r64>
.data 1 [89] # 991 1 vec<309,r64>
.data 1 [173] # 992 1 vec<309,r64>
.data 1 [143] # 993 1 vec<309,r64>
.data 1 [118] # 994 1 vec<309,r64>
.data 1 [15] # 995 1 vec<309,r64>
.data 1 [47] # 996 1 vec<309,r64>
.data 1 [65] # 997 1 vec<309,r64>
.data 1 [174] # 998 1 vec<309,r64>
.data 1 [89] # 999 1 vec<309,r64>
.data 1 [204] # 1000 1 vec<309,r64>
.data 1 [25] # 1001 1 vec<309,r64>
.data 1 [170] # 1002 1 vec<309,r64>
.data 1 [105] # 1003 1 vec<309,r64>
.data 1 [189] # 1004 1 vec<309,r64>
.data 1 [232] # 1005 1 vec<309,r64>
.data 1 [226] # 1006 1 vec<309,r64>
.data 1 [89] # 1007 1 vec<309,r64>
.data 1 [63] # 1008 1 vec<309,r64>
.data 1 [160] # 1009 1 vec<309,r64>
.data 1 [20] # 1010 1 vec<309,r64>
.data 1 [196] # 1011 1 vec<309,r64>
.data 1 [236] # 1012 1 vec<309,r64>
.data 1 [162] # 1013 1 vec<309,r64>
.data 1 [23] # 1014 1 vec<309,r64>
.data 1 [90] # 1015 1 vec<309,r64>
.data 1 [79] # 1016 1 vec<309,r64>
.data 1 [200] # 1017 1 vec<309,r64>
.data 1 [25] # 1018 1 vec<309,r64>
.data 1 [245] # 1019 1 vec<309,r64>
.data 1 [167] # 1020 1 vec<309,r64>
.data 1 [139] # 1021 1 vec<309,r64>
.data 1 [77] # 1022 1 vec<309,r64>
.data 1 [90] # 1023 1 vec<309,r64>
.data 1 [50] # 1024 1 vec<309,r64>
.data 1 [29] # 1025 1 vec<309,r64>
.data 1 [48] # 1026 1 vec<309,r64>
.data 1 [249] # 1027 1 vec<309,r64>
.data 1 [72] # 1028 1 vec<309,r64>
.data 1 [119] # 1029 1 vec<309,r64>
.data 1 [130] # 1030 1 vec<309,r64>
.data 1 [90] # 1031 1 vec<309,r64>
.data 1 [126] # 1032 1 vec<309,r64>
.data 1 [36] # 1033 1 vec<309,r64>
.data 1 [124] # 1034 1 vec<309,r64>
.data 1 [55] # 1035 1 vec<309,r64>
.data 1 [27] # 1036 1 vec<309,r64>
.data 1 [21] # 1037 1 vec<309,r64>
.data 1 [183] # 1038 1 vec<309,r64>
.data 1 [90] # 1039 1 vec<309,r64>
.data 1 [158] # 1040 1 vec<309,r64>
.data 1 [45] # 1041 1 vec<309,r64>
.data 1 [91] # 1042 1 vec<309,r64>
.data 1 [5] # 1043 1 vec<309,r64>
.data 1 [98] # 1044 1 vec<309,r64>
.data 1 [218] # 1045 1 vec<309,r64>
.data 1 [236] # 1046 1 vec<309,r64>
.data 1 [90] # 1047 1 vec<309,r64>
.data 1 [130] # 1048 1 vec<309,r64>
.data 1 [252] # 1049 1 vec<309,r64>
.data 1 [88] # 1050 1 vec<309,r64>
.data 1 [67] # 1051 1 vec<309,r64>
.data 1 [125] # 1052 1 vec<309,r64>
.data 1 [8] # 1053 1 vec<309,r64>
.data 1 [34] # 1054 1 vec<309,r64>
.data 1 [91] # 1055 1 vec<309,r64>
.data 1 [163] # 1056 1 vec<309,r64>
.data 1 [59] # 1057 1 vec<309,r64>
.data 1 [47] # 1058 1 vec<309,r64>
.data 1 [148] # 1059 1 vec<309,r64>
.data 1 [156] # 1060 1 vec<309,r64>
.data 1 [138] # 1061 1 vec<309,r64>
.data 1 [86] # 1062 1 vec<309,r64>
.data 1 [91] # 1063 1 vec<309,r64>
.data 1 [140] # 1064 1 vec<309,r64>
.data 1 [10] # 1065 1 vec<309,r64>
.data 1 [59] # 1066 1 vec<309,r64>
.data 1 [185] # 1067 1 vec<309,r64>
.data 1 [67] # 1068 1 vec<309,r64>
.data 1 [45] # 1069 1 vec<309,r64>
.data 1 [140] # 1070 1 vec<309,r64>
.data 1 [91] # 1071 1 vec<309,r64>
.data 1 [151] # 1072 1 vec<309,r64>
.data 1 [230] # 1073 1 vec<309,r64>
.data 1 [196] # 1074 1 vec<309,r64>
.data 1 [83] # 1075 1 vec<309,r64>
.data 1 [74] # 1076 1 vec<309,r64>
.data 1 [156] # 1077 1 vec<309,r64>
.data 1 [193] # 1078 1 vec<309,r64>
.data 1 [91] # 1079 1 vec<309,r64>
.data 1 [61] # 1080 1 vec<309,r64>
.data 1 [32] # 1081 1 vec<309,r64>
.data 1 [182] # 1082 1 vec<309,r64>
.data 1 [232] # 1083 1 vec<309,r64>
.data 1 [92] # 1084 1 vec<309,r64>
.data 1 [3] # 1085 1 vec<309,r64>
.data 1 [246] # 1086 1 vec<309,r64>
.data 1 [91] # 1087 1 vec<309,r64>
.data 1 [77] # 1088 1 vec<309,r64>
.data 1 [168] # 1089 1 vec<309,r64>
.data 1 [227] # 1090 1 vec<309,r64>
.data 1 [34] # 1091 1 vec<309,r64>
.data 1 [52] # 1092 1 vec<309,r64>
.data 1 [132] # 1093 1 vec<309,r64>
.data 1 [43] # 1094 1 vec<309,r64>
.data 1 [92] # 1095 1 vec<309,r64>
.data 1 [48] # 1096 1 vec<309,r64>
.data 1 [73] # 1097 1 vec<309,r64>
.data 1 [206] # 1098 1 vec<309,r64>
.data 1 [149] # 1099 1 vec<309,r64>
.data 1 [160] # 1100 1 vec<309,r64>
.data 1 [50] # 1101 1 vec<309,r64>
.data 1 [97] # 1102 1 vec<309,r64>
.data 1 [92] # 1103 1 vec<309,r64>
.data 1 [124] # 1104 1 vec<309,r64>
.data 1 [219] # 1105 1 vec<309,r64>
.data 1 [65] # 1106 1 vec<309,r64>
.data 1 [187] # 1107 1 vec<309,r64>
.data 1 [72] # 1108 1 vec<309,r64>
.data 1 [127] # 1109 1 vec<309,r64>
.data 1 [149] # 1110 1 vec<309,r64>
.data 1 [92] # 1111 1 vec<309,r64>
.data 1 [91] # 1112 1 vec<309,r64>
.data 1 [82] # 1113 1 vec<309,r64>
.data 1 [18] # 1114 1 vec<309,r64>
.data 1 [234] # 1115 1 vec<309,r64>
.data 1 [26] # 1116 1 vec<309,r64>
.data 1 [223] # 1117 1 vec<309,r64>
.data 1 [202] # 1118 1 vec<309,r64>
.data 1 [92] # 1119 1 vec<309,r64>
.data 1 [121] # 1120 1 vec<309,r64>
.data 1 [115] # 1121 1 vec<309,r64>
.data 1 [75] # 1122 1 vec<309,r64>
.data 1 [210] # 1123 1 vec<309,r64>
.data 1 [112] # 1124 1 vec<309,r64>
.data 1 [203] # 1125 1 vec<309,r64>
.data 1 [0] # 1126 1 vec<309,r64>
.data 1 [93] # 1127 1 vec<309,r64>
.data 1 [87] # 1128 1 vec<309,r64>
.data 1 [80] # 1129 1 vec<309,r64>
.data 1 [222] # 1130 1 vec<309,r64>
.data 1 [6] # 1131 1 vec<309,r64>
.data 1 [77] # 1132 1 vec<309,r64>
.data 1 [254] # 1133 1 vec<309,r64>
.data 1 [52] # 1134 1 vec<309,r64>
.data 1 [93] # 1135 1 vec<309,r64>
.data 1 [109] # 1136 1 vec<309,r64>
.data 1 [228] # 1137 1 vec<309,r64>
.data 1 [149] # 1138 1 vec<309,r64>
.data 1 [72] # 1139 1 vec<309,r64>
.data 1 [224] # 1140 1 vec<309,r64>
.data 1 [61] # 1141 1 vec<309,r64>
.data 1 [106] # 1142 1 vec<309,r64>
.data 1 [93] # 1143 1 vec<309,r64>
.data 1 [196] # 1144 1 vec<309,r64>
.data 1 [174] # 1145 1 vec<309,r64>
.data 1 [93] # 1146 1 vec<309,r64>
.data 1 [45] # 1147 1 vec<309,r64>
.data 1 [172] # 1148 1 vec<309,r64>
.data 1 [102] # 1149 1 vec<309,r64>
.data 1 [160] # 1150 1 vec<309,r64>
.data 1 [93] # 1151 1 vec<309,r64>
.data 1 [117] # 1152 1 vec<309,r64>
.data 1 [26] # 1153 1 vec<309,r64>
.data 1 [181] # 1154 1 vec<309,r64>
.data 1 [56] # 1155 1 vec<309,r64>
.data 1 [87] # 1156 1 vec<309,r64>
.data 1 [128] # 1157 1 vec<309,r64>
.data 1 [212] # 1158 1 vec<309,r64>
.data 1 [93] # 1159 1 vec<309,r64>
.data 1 [18] # 1160 1 vec<309,r64>
.data 1 [97] # 1161 1 vec<309,r64>
.data 1 [226] # 1162 1 vec<309,r64>
.data 1 [6] # 1163 1 vec<309,r64>
.data 1 [109] # 1164 1 vec<309,r64>
.data 1 [160] # 1165 1 vec<309,r64>
.data 1 [9] # 1166 1 vec<309,r64>
.data 1 [94] # 1167 1 vec<309,r64>
.data 1 [171] # 1168 1 vec<309,r64>
.data 1 [124] # 1169 1 vec<309,r64>
.data 1 [77] # 1170 1 vec<309,r64>
.data 1 [36] # 1171 1 vec<309,r64>
.data 1 [68] # 1172 1 vec<309,r64>
.data 1 [4] # 1173 1 vec<309,r64>
.data 1 [64] # 1174 1 vec<309,r64>
.data 1 [94] # 1175 1 vec<309,r64>
.data 1 [214] # 1176 1 vec<309,r64>
.data 1 [219] # 1177 1 vec<309,r64>
.data 1 [96] # 1178 1 vec<309,r64>
.data 1 [45] # 1179 1 vec<309,r64>
.data 1 [85] # 1180 1 vec<309,r64>
.data 1 [5] # 1181 1 vec<309,r64>
.data 1 [116] # 1182 1 vec<309,r64>
.data 1 [94] # 1183 1 vec<309,r64>
.data 1 [204] # 1184 1 vec<309,r64>
.data 1 [18] # 1185 1 vec<309,r64>
.data 1 [185] # 1186 1 vec<309,r64>
.data 1 [120] # 1187 1 vec<309,r64>
.data 1 [170] # 1188 1 vec<309,r64>
.data 1 [6] # 1189 1 vec<309,r64>
.data 1 [169] # 1190 1 vec<309,r64>
.data 1 [94] # 1191 1 vec<309,r64>
.data 1 [127] # 1192 1 vec<309,r64>
.data 1 [87] # 1193 1 vec<309,r64>
.data 1 [231] # 1194 1 vec<309,r64>
.data 1 [22] # 1195 1 vec<309,r64>
.data 1 [85] # 1196 1 vec<309,r64>
.data 1 [72] # 1197 1 vec<309,r64>
.data 1 [223] # 1198 1 vec<309,r64>
.data 1 [94] # 1199 1 vec<309,r64>
.data 1 [175] # 1200 1 vec<309,r64>
.data 1 [150] # 1201 1 vec<309,r64>
.data 1 [80] # 1202 1 vec<309,r64>
.data 1 [46] # 1203 1 vec<309,r64>
.data 1 [53] # 1204 1 vec<309,r64>
.data 1 [141] # 1205 1 vec<309,r64>
.data 1 [19] # 1206 1 vec<309,r64>
.data 1 [95] # 1207 1 vec<309,r64>
.data 1 [91] # 1208 1 vec<309,r64>
.data 1 [188] # 1209 1 vec<309,r64>
.data 1 [228] # 1210 1 vec<309,r64>
.data 1 [121] # 1211 1 vec<309,r64>
.data 1 [130] # 1212 1 vec<309,r64>
.data 1 [112] # 1213 1 vec<309,r64>
.data 1 [72] # 1214 1 vec<309,r64>
.data 1 [95] # 1215 1 vec<309,r64>
.data 1 [114] # 1216 1 vec<309,r64>
.data 1 [235] # 1217 1 vec<309,r64>
.data 1 [93] # 1218 1 vec<309,r64>
.data 1 [24] # 1219 1 vec<309,r64>
.data 1 [163] # 1220 1 vec<309,r64>
.data 1 [140] # 1221 1 vec<309,r64>
.data 1 [126] # 1222 1 vec<309,r64>
.data 1 [95] # 1223 1 vec<309,r64>
.data 1 [39] # 1224 1 vec<309,r64>
.data 1 [179] # 1225 1 vec<309,r64>
.data 1 [58] # 1226 1 vec<309,r64>
.data 1 [239] # 1227 1 vec<309,r64>
.data 1 [229] # 1228 1 vec<309,r64>
.data 1 [23] # 1229 1 vec<309,r64>
.data 1 [179] # 1230 1 vec<309,r64>
.data 1 [95] # 1231 1 vec<309,r64>
.data 1 [241] # 1232 1 vec<309,r64>
.data 1 [95] # 1233 1 vec<309,r64>
.data 1 [9] # 1234 1 vec<309,r64>
.data 1 [107] # 1235 1 vec<309,r64>
.data 1 [223] # 1236 1 vec<309,r64>
.data 1 [221] # 1237 1 vec<309,r64>
.data 1 [231] # 1238 1 vec<309,r64>
.data 1 [95] # 1239 1 vec<309,r64>
.data 1 [237] # 1240 1 vec<309,r64>
.data 1 [183] # 1241 1 vec<309,r64>
.data 1 [203] # 1242 1 vec<309,r64>
.data 1 [69] # 1243 1 vec<309,r64>
.data 1 [87] # 1244 1 vec<309,r64>
.data 1 [213] # 1245 1 vec<309,r64>
.data 1 [29] # 1246 1 vec<309,r64>
.data 1 [96] # 1247 1 vec<309,r64>
.data 1 [244] # 1248 1 vec<309,r64>
.data 1 [82] # 1249 1 vec<309,r64>
.data 1 [159] # 1250 1 vec<309,r64>
.data 1 [139] # 1251 1 vec<309,r64>
.data 1 [86] # 1252 1 vec<309,r64>
.data 1 [165] # 1253 1 vec<309,r64>
.data 1 [82] # 1254 1 vec<309,r64>
.data 1 [96] # 1255 1 vec<309,r64>
.data 1 [177] # 1256 1 vec<309,r64>
.data 1 [39] # 1257 1 vec<309,r64>
.data 1 [135] # 1258 1 vec<309,r64>
.data 1 [46] # 1259 1 vec<309,r64>
.data 1 [172] # 1260 1 vec<309,r64>
.data 1 [78] # 1261 1 vec<309,r64>
.data 1 [135] # 1262 1 vec<309,r64>
.data 1 [96] # 1263 1 vec<309,r64>
.data 1 [157] # 1264 1 vec<309,r64>
.data 1 [241] # 1265 1 vec<309,r64>
.data 1 [40] # 1266 1 vec<309,r64>
.data 1 [58] # 1267 1 vec<309,r64>
.data 1 [87] # 1268 1 vec<309,r64>
.data 1 [34] # 1269 1 vec<309,r64>
.data 1 [189] # 1270 1 vec<309,r64>
.data 1 [96] # 1271 1 vec<309,r64>
.data 1 [2] # 1272 1 vec<309,r64>
.data 1 [151] # 1273 1 vec<309,r64>
.data 1 [89] # 1274 1 vec<309,r64>
.data 1 [132] # 1275 1 vec<309,r64>
.data 1 [118] # 1276 1 vec<309,r64>
.data 1 [53] # 1277 1 vec<309,r64>
.data 1 [242] # 1278 1 vec<309,r64>
.data 1 [96] # 1279 1 vec<309,r64>
.data 1 [195] # 1280 1 vec<309,r64>
.data 1 [252] # 1281 1 vec<309,r64>
.data 1 [111] # 1282 1 vec<309,r64>
.data 1 [37] # 1283 1 vec<309,r64>
.data 1 [212] # 1284 1 vec<309,r64>
.data 1 [194] # 1285 1 vec<309,r64>
.data 1 [38] # 1286 1 vec<309,r64>
.data 1 [97] # 1287 1 vec<309,r64>
.data 1 [244] # 1288 1 vec<309,r64>
.data 1 [251] # 1289 1 vec<309,r64>
.data 1 [203] # 1290 1 vec<309,r64>
.data 1 [46] # 1291 1 vec<309,r64>
.data 1 [137] # 1292 1 vec<309,r64>
.data 1 [115] # 1293 1 vec<309,r64>
.data 1 [92] # 1294 1 vec<309,r64>
.data 1 [97] # 1295 1 vec<309,r64>
.data 1 [120] # 1296 1 vec<309,r64>
.data 1 [125] # 1297 1 vec<309,r64>
.data 1 [63] # 1298 1 vec<309,r64>
.data 1 [189] # 1299 1 vec<309,r64>
.data 1 [53] # 1300 1 vec<309,r64>
.data 1 [200] # 1301 1 vec<309,r64>
.data 1 [145] # 1302 1 vec<309,r64>
.data 1 [97] # 1303 1 vec<309,r64>
.data 1 [214] # 1304 1 vec<309,r64>
.data 1 [92] # 1305 1 vec<309,r64>
.data 1 [143] # 1306 1 vec<309,r64>
.data 1 [44] # 1307 1 vec<309,r64>
.data 1 [67] # 1308 1 vec<309,r64>
.data 1 [58] # 1309 1 vec<309,r64>
.data 1 [198] # 1310 1 vec<309,r64>
.data 1 [97] # 1311 1 vec<309,r64>
.data 1 [12] # 1312 1 vec<309,r64>
.data 1 [52] # 1313 1 vec<309,r64>
.data 1 [179] # 1314 1 vec<309,r64>
.data 1 [247] # 1315 1 vec<309,r64>
.data 1 [211] # 1316 1 vec<309,r64>
.data 1 [200] # 1317 1 vec<309,r64>
.data 1 [251] # 1318 1 vec<309,r64>
.data 1 [97] # 1319 1 vec<309,r64>
.data 1 [135] # 1320 1 vec<309,r64>
.data 1 [0] # 1321 1 vec<309,r64>
.data 1 [208] # 1322 1 vec<309,r64>
.data 1 [122] # 1323 1 vec<309,r64>
.data 1 [132] # 1324 1 vec<309,r64>
.data 1 [93] # 1325 1 vec<309,r64>
.data 1 [49] # 1326 1 vec<309,r64>
.data 1 [98] # 1327 1 vec<309,r64>
.data 1 [169] # 1328 1 vec<309,r64>
.data 1 [0] # 1329 1 vec<309,r64>
.data 1 [132] # 1330 1 vec<309,r64>
.data 1 [153] # 1331 1 vec<309,r64>
.data 1 [229] # 1332 1 vec<309,r64>
.data 1 [180] # 1333 1 vec<309,r64>
.data 1 [101] # 1334 1 vec<309,r64>
.data 1 [98] # 1335 1 vec<309,r64>
.data 1 [212] # 1336 1 vec<309,r64>
.data 1 [0] # 1337 1 vec<309,r64>
.data 1 [229] # 1338 1 vec<309,r64>
.data 1 [255] # 1339 1 vec<309,r64>
.data 1 [30] # 1340 1 vec<309,r64>
.data 1 [34] # 1341 1 vec<309,r64>
.data 1 [155] # 1342 1 vec<309,r64>
.data 1 [98] # 1343 1 vec<309,r64>
.data 1 [132] # 1344 1 vec<309,r64>
.data 1 [32] # 1345 1 vec<309,r64>
.data 1 [239] # 1346 1 vec<309,r64>
.data 1 [95] # 1347 1 vec<309,r64>
.data 1 [83] # 1348 1 vec<309,r64>
.data 1 [245] # 1349 1 vec<309,r64>
.data 1 [208] # 1350 1 vec<309,r64>
.data 1 [98] # 1351 1 vec<309,r64>
.data 1 [165] # 1352 1 vec<309,r64>
.data 1 [232] # 1353 1 vec<309,r64>
.data 1 [234] # 1354 1 vec<309,r64>
.data 1 [55] # 1355 1 vec<309,r64>
.data 1 [168] # 1356 1 vec<309,r64>
.data 1 [50] # 1357 1 vec<309,r64>
.data 1 [5] # 1358 1 vec<309,r64>
.data 1 [99] # 1359 1 vec<309,r64>
.data 1 [207] # 1360 1 vec<309,r64>
.data 1 [162] # 1361 1 vec<309,r64>
.data 1 [229] # 1362 1 vec<309,r64>
.data 1 [69] # 1363 1 vec<309,r64>
.data 1 [82] # 1364 1 vec<309,r64>
.data 1 [127] # 1365 1 vec<309,r64>
.data 1 [58] # 1366 1 vec<309,r64>
.data 1 [99] # 1367 1 vec<309,r64>
.data 1 [193] # 1368 1 vec<309,r64>
.data 1 [133] # 1369 1 vec<309,r64>
.data 1 [175] # 1370 1 vec<309,r64>
.data 1 [107] # 1371 1 vec<309,r64>
.data 1 [147] # 1372 1 vec<309,r64>
.data 1 [143] # 1373 1 vec<309,r64>
.data 1 [112] # 1374 1 vec<309,r64>
.data 1 [99] # 1375 1 vec<309,r64>
.data 1 [50] # 1376 1 vec<309,r64>
.data 1 [103] # 1377 1 vec<309,r64>
.data 1 [155] # 1378 1 vec<309,r64>
.data 1 [70] # 1379 1 vec<309,r64>
.data 1 [120] # 1380 1 vec<309,r64>
.data 1 [179] # 1381 1 vec<309,r64>
.data 1 [164] # 1382 1 vec<309,r64>
.data 1 [99] # 1383 1 vec<309,r64>
.data 1 [254] # 1384 1 vec<309,r64>
.data 1 [64] # 1385 1 vec<309,r64>
.data 1 [66] # 1386 1 vec<309,r64>
.data 1 [88] # 1387 1 vec<309,r64>
.data 1 [86] # 1388 1 vec<309,r64>
.data 1 [224] # 1389 1 vec<309,r64>
.data 1 [217] # 1390 1 vec<309,r64>
.data 1 [99] # 1391 1 vec<309,r64>
.data 1 [159] # 1392 1 vec<309,r64>
.data 1 [104] # 1393 1 vec<309,r64>
.data 1 [41] # 1394 1 vec<309,r64>
.data 1 [247] # 1395 1 vec<309,r64>
.data 1 [53] # 1396 1 vec<309,r64>
.data 1 [44] # 1397 1 vec<309,r64>
.data 1 [16] # 1398 1 vec<309,r64>
.data 1 [100] # 1399 1 vec<309,r64>
.data 1 [198] # 1400 1 vec<309,r64>
.data 1 [194] # 1401 1 vec<309,r64>
.data 1 [243] # 1402 1 vec<309,r64>
.data 1 [116] # 1403 1 vec<309,r64>
.data 1 [67] # 1404 1 vec<309,r64>
.data 1 [55] # 1405 1 vec<309,r64>
.data 1 [68] # 1406 1 vec<309,r64>
.data 1 [100] # 1407 1 vec<309,r64>
.data 1 [120] # 1408 1 vec<309,r64>
.data 1 [179] # 1409 1 vec<309,r64>
.data 1 [48] # 1410 1 vec<309,r64>
.data 1 [82] # 1411 1 vec<309,r64>
.data 1 [20] # 1412 1 vec<309,r64>
.data 1 [69] # 1413 1 vec<309,r64>
.data 1 [121] # 1414 1 vec<309,r64>
.data 1 [100] # 1415 1 vec<309,r64>
.data 1 [86] # 1416 1 vec<309,r64>
.data 1 [224] # 1417 1 vec<309,r64>
.data 1 [188] # 1418 1 vec<309,r64>
.data 1 [102] # 1419 1 vec<309,r64>
.data 1 [89] # 1420 1 vec<309,r64>
.data 1 [150] # 1421 1 vec<309,r64>
.data 1 [175] # 1422 1 vec<309,r64>
.data 1 [100] # 1423 1 vec<309,r64>
.data 1 [54] # 1424 1 vec<309,r64>
.data 1 [12] # 1425 1 vec<309,r64>
.data 1 [54] # 1426 1 vec<309,r64>
.data 1 [224] # 1427 1 vec<309,r64>
.data 1 [247] # 1428 1 vec<309,r64>
.data 1 [189] # 1429 1 vec<309,r64>
.data 1 [227] # 1430 1 vec<309,r64>
.data 1 [100] # 1431 1 vec<309,r64>
.data 1 [67] # 1432 1 vec<309,r64>
.data 1 [143] # 1433 1 vec<309,r64>
.data 1 [67] # 1434 1 vec<309,r64>
.data 1 [216] # 1435 1 vec<309,r64>
.data 1 [117] # 1436 1 vec<309,r64>
.data 1 [173] # 1437 1 vec<309,r64>
.data 1 [24] # 1438 1 vec<309,r64>
.data 1 [101] # 1439 1 vec<309,r64>
.data 1 [20] # 1440 1 vec<309,r64>
.data 1 [115] # 1441 1 vec<309,r64>
.data 1 [84] # 1442 1 vec<309,r64>
.data 1 [78] # 1443 1 vec<309,r64>
.data 1 [211] # 1444 1 vec<309,r64>
.data 1 [216] # 1445 1 vec<309,r64>
.data 1 [78] # 1446 1 vec<309,r64>
.data 1 [101] # 1447 1 vec<309,r64>
.data 1 [236] # 1448 1 vec<309,r64>
.data 1 [199] # 1449 1 vec<309,r64>
.data 1 [244] # 1450 1 vec<309,r64>
.data 1 [16] # 1451 1 vec<309,r64>
.data 1 [132] # 1452 1 vec<309,r64>
.data 1 [71] # 1453 1 vec<309,r64>
.data 1 [131] # 1454 1 vec<309,r64>
.data 1 [101] # 1455 1 vec<309,r64>
.data 1 [232] # 1456 1 vec<309,r64>
.data 1 [249] # 1457 1 vec<309,r64>
.data 1 [49] # 1458 1 vec<309,r64>
.data 1 [21] # 1459 1 vec<309,r64>
.data 1 [101] # 1460 1 vec<309,r64>
.data 1 [25] # 1461 1 vec<309,r64>
.data 1 [184] # 1462 1 vec<309,r64>
.data 1 [101] # 1463 1 vec<309,r64>
.data 1 [97] # 1464 1 vec<309,r64>
.data 1 [120] # 1465 1 vec<309,r64>
.data 1 [126] # 1466 1 vec<309,r64>
.data 1 [90] # 1467 1 vec<309,r64>
.data 1 [190] # 1468 1 vec<309,r64>
.data 1 [31] # 1469 1 vec<309,r64>
.data 1 [238] # 1470 1 vec<309,r64>
.data 1 [101] # 1471 1 vec<309,r64>
.data 1 [61] # 1472 1 vec<309,r64>
.data 1 [11] # 1473 1 vec<309,r64>
.data 1 [143] # 1474 1 vec<309,r64>
.data 1 [248] # 1475 1 vec<309,r64>
.data 1 [214] # 1476 1 vec<309,r64>
.data 1 [211] # 1477 1 vec<309,r64>
.data 1 [34] # 1478 1 vec<309,r64>
.data 1 [102] # 1479 1 vec<309,r64>
.data 1 [12] # 1480 1 vec<309,r64>
.data 1 [206] # 1481 1 vec<309,r64>
.data 1 [178] # 1482 1 vec<309,r64>
.data 1 [182] # 1483 1 vec<309,r64>
.data 1 [204] # 1484 1 vec<309,r64>
.data 1 [136] # 1485 1 vec<309,r64>
.data 1 [87] # 1486 1 vec<309,r64>
.data 1 [102] # 1487 1 vec<309,r64>
.data 1 [143] # 1488 1 vec<309,r64>
.data 1 [129] # 1489 1 vec<309,r64>
.data 1 [95] # 1490 1 vec<309,r64>
.data 1 [228] # 1491 1 vec<309,r64>
.data 1 [255] # 1492 1 vec<309,r64>
.data 1 [106] # 1493 1 vec<309,r64>
.data 1 [141] # 1494 1 vec<309,r64>
.data 1 [102] # 1495 1 vec<309,r64>
.data 1 [249] # 1496 1 vec<309,r64>
.data 1 [176] # 1497 1 vec<309,r64>
.data 1 [187] # 1498 1 vec<309,r64>
.data 1 [238] # 1499 1 vec<309,r64>
.data 1 [223] # 1500 1 vec<309,r64>
.data 1 [98] # 1501 1 vec<309,r64>
.data 1 [194] # 1502 1 vec<309,r64>
.data 1 [102] # 1503 1 vec<309,r64>
.data 1 [56] # 1504 1 vec<309,r64>
.data 1 [157] # 1505 1 vec<309,r64>
.data 1 [106] # 1506 1 vec<309,r64>
.data 1 [234] # 1507 1 vec<309,r64>
.data 1 [151] # 1508 1 vec<309,r64>
.data 1 [251] # 1509 1 vec<309,r64>
.data 1 [246] # 1510 1 vec<309,r64>
.data 1 [102] # 1511 1 vec<309,r64>
.data 1 [134] # 1512 1 vec<309,r64>
.data 1 [68] # 1513 1 vec<309,r64>
.data 1 [5] # 1514 1 vec<309,r64>
.data 1 [229] # 1515 1 vec<309,r64>
.data 1 [125] # 1516 1 vec<309,r64>
.data 1 [186] # 1517 1 vec<309,r64>
.data 1 [44] # 1518 1 vec<309,r64>
.data 1 [103] # 1519 1 vec<309,r64>
.data 1 [212] # 1520 1 vec<309,r64>
.data 1 [74] # 1521 1 vec<309,r64>
.data 1 [35] # 1522 1 vec<309,r64>
.data 1 [175] # 1523 1 vec<309,r64>
.data 1 [142] # 1524 1 vec<309,r64>
.data 1 [244] # 1525 1 vec<309,r64>
.data 1 [97] # 1526 1 vec<309,r64>
.data 1 [103] # 1527 1 vec<309,r64>
.data 1 [137] # 1528 1 vec<309,r64>
.data 1 [29] # 1529 1 vec<309,r64>
.data 1 [236] # 1530 1 vec<309,r64>
.data 1 [90] # 1531 1 vec<309,r64>
.data 1 [178] # 1532 1 vec<309,r64>
.data 1 [113] # 1533 1 vec<309,r64>
.data 1 [150] # 1534 1 vec<309,r64>
.data 1 [103] # 1535 1 vec<309,r64>
.data 1 [235] # 1536 1 vec<309,r64>
.data 1 [36] # 1537 1 vec<309,r64>
.data 1 [167] # 1538 1 vec<309,r64>
.data 1 [241] # 1539 1 vec<309,r64>
.data 1 [30] # 1540 1 vec<309,r64>
.data 1 [14] # 1541 1 vec<309,r64>
.data 1 [204] # 1542 1 vec<309,r64>
.data 1 [103] # 1543 1 vec<309,r64>
.data 1 [19] # 1544 1 vec<309,r64>
.data 1 [119] # 1545 1 vec<309,r64>
.data 1 [8] # 1546 1 vec<309,r64>
.data 1 [87] # 1547 1 vec<309,r64>
.data 1 [211] # 1548 1 vec<309,r64>
.data 1 [136] # 1549 1 vec<309,r64>
.data 1 [1] # 1550 1 vec<309,r64>
.data 1 [104] # 1551 1 vec<309,r64>
.data 1 [215] # 1552 1 vec<309,r64>
.data 1 [148] # 1553 1 vec<309,r64>
.data 1 [202] # 1554 1 vec<309,r64>
.data 1 [44] # 1555 1 vec<309,r64>
.data 1 [8] # 1556 1 vec<309,r64>
.data 1 [235] # 1557 1 vec<309,r64>
.data 1 [53] # 1558 1 vec<309,r64>
.data 1 [104] # 1559 1 vec<309,r64>
.data 1 [13] # 1560 1 vec<309,r64>
.data 1 [58] # 1561 1 vec<309,r64>
.data 1 [253] # 1562 1 vec<309,r64>
.data 1 [55] # 1563 1 vec<309,r64>
.data 1 [202] # 1564 1 vec<309,r64>
.data 1 [101] # 1565 1 vec<309,r64>
.data 1 [107] # 1566 1 vec<309,r64>
.data 1 [104] # 1567 1 vec<309,r64>
.data 1 [72] # 1568 1 vec<309,r64>
.data 1 [68] # 1569 1 vec<309,r64>
.data 1 [254] # 1570 1 vec<309,r64>
.data 1 [98] # 1571 1 vec<309,r64>
.data 1 [158] # 1572 1 vec<309,r64>
.data 1 [31] # 1573 1 vec<309,r64>
.data 1 [161] # 1574 1 vec<309,r64>
.data 1 [104] # 1575 1 vec<309,r64>
.data 1 [90] # 1576 1 vec<309,r64>
.data 1 [213] # 1577 1 vec<309,r64>
.data 1 [189] # 1578 1 vec<309,r64>
.data 1 [251] # 1579 1 vec<309,r64>
.data 1 [133] # 1580 1 vec<309,r64>
.data 1 [103] # 1581 1 vec<309,r64>
.data 1 [213] # 1582 1 vec<309,r64>
.data 1 [104] # 1583 1 vec<309,r64>
.data 1 [177] # 1584 1 vec<309,r64>
.data 1 [74] # 1585 1 vec<309,r64>
.data 1 [173] # 1586 1 vec<309,r64>
.data 1 [122] # 1587 1 vec<309,r64>
.data 1 [103] # 1588 1 vec<309,r64>
.data 1 [193] # 1589 1 vec<309,r64>
.data 1 [10] # 1590 1 vec<309,r64>
.data 1 [105] # 1591 1 vec<309,r64>
.data 1 [175] # 1592 1 vec<309,r64>
.data 1 [78] # 1593 1 vec<309,r64>
.data 2 [172] # 1594 2 vec<309,r64>
.data 1 [224] # 1596 1 vec<309,r64>
.data 1 [184] # 1597 1 vec<309,r64>
.data 1 [64] # 1598 1 vec<309,r64>
.data 1 [105] # 1599 1 vec<309,r64>
.data 1 [90] # 1600 1 vec<309,r64>
.data 1 [98] # 1601 1 vec<309,r64>
.data 2 [215] # 1602 2 vec<309,r64>
.data 1 [24] # 1604 1 vec<309,r64>
.data 1 [231] # 1605 1 vec<309,r64>
.data 1 [116] # 1606 1 vec<309,r64>
.data 1 [105] # 1607 1 vec<309,r64>
.data 1 [241] # 1608 1 vec<309,r64>
.data 1 [58] # 1609 1 vec<309,r64>
.data 1 [205] # 1610 1 vec<309,r64>
.data 1 [13] # 1611 1 vec<309,r64>
.data 1 [223] # 1612 1 vec<309,r64>
.data 1 [32] # 1613 1 vec<309,r64>
.data 1 [170] # 1614 1 vec<309,r64>
.data 1 [105] # 1615 1 vec<309,r64>
.data 1 [214] # 1616 1 vec<309,r64>
.data 1 [68] # 1617 1 vec<309,r64>
.data 1 [160] # 1618 1 vec<309,r64>
.data 1 [104] # 1619 1 vec<309,r64>
.data 1 [139] # 1620 1 vec<309,r64>
.data 1 [84] # 1621 1 vec<309,r64>
.data 1 [224] # 1622 1 vec<309,r64>
.data 1 [105] # 1623 1 vec<309,r64>
.data 1 [12] # 1624 1 vec<309,r64>
.data 1 [86] # 1625 1 vec<309,r64>
.data 1 [200] # 1626 1 vec<309,r64>
.data 1 [66] # 1627 1 vec<309,r64>
.data 1 [174] # 1628 1 vec<309,r64>
.data 1 [105] # 1629 1 vec<309,r64>
.data 1 [20] # 1630 1 vec<309,r64>
.data 1 [106] # 1631 1 vec<309,r64>
.data 1 [143] # 1632 1 vec<309,r64>
.data 1 [107] # 1633 1 vec<309,r64>
.data 1 [122] # 1634 1 vec<309,r64>
.data 1 [211] # 1635 1 vec<309,r64>
.data 1 [25] # 1636 1 vec<309,r64>
.data 1 [132] # 1637 1 vec<309,r64>
.data 1 [73] # 1638 1 vec<309,r64>
.data 1 [106] # 1639 1 vec<309,r64>
.data 1 [115] # 1640 1 vec<309,r64>
.data 1 [6] # 1641 1 vec<309,r64>
.data 1 [89] # 1642 1 vec<309,r64>
.data 1 [72] # 1643 1 vec<309,r64>
.data 1 [32] # 1644 1 vec<309,r64>
.data 1 [229] # 1645 1 vec<309,r64>
.data 1 [127] # 1646 1 vec<309,r64>
.data 1 [106] # 1647 1 vec<309,r64>
.data 1 [8] # 1648 1 vec<309,r64>
.data 1 [164] # 1649 1 vec<309,r64>
.data 1 [55] # 1650 1 vec<309,r64>
.data 1 [45] # 1651 1 vec<309,r64>
.data 1 [52] # 1652 1 vec<309,r64>
.data 1 [239] # 1653 1 vec<309,r64>
.data 1 [179] # 1654 1 vec<309,r64>
.data 1 [106] # 1655 1 vec<309,r64>
.data 1 [10] # 1656 1 vec<309,r64>
.data 1 [141] # 1657 1 vec<309,r64>
.data 1 [133] # 1658 1 vec<309,r64>
.data 1 [56] # 1659 1 vec<309,r64>
.data 1 [1] # 1660 1 vec<309,r64>
.data 1 [235] # 1661 1 vec<309,r64>
.data 1 [232] # 1662 1 vec<309,r64>
.data 1 [106] # 1663 1 vec<309,r64>
.data 1 [76] # 1664 1 vec<309,r64>
.data 1 [240] # 1665 1 vec<309,r64>
.data 1 [166] # 1666 1 vec<309,r64>
.data 1 [134] # 1667 1 vec<309,r64>
.data 1 [193] # 1668 1 vec<309,r64>
.data 1 [37] # 1669 1 vec<309,r64>
.data 1 [31] # 1670 1 vec<309,r64>
.data 1 [107] # 1671 1 vec<309,r64>
.data 1 [48] # 1672 1 vec<309,r64>
.data 1 [86] # 1673 1 vec<309,r64>
.data 1 [40] # 1674 1 vec<309,r64>
.data 1 [244] # 1675 1 vec<309,r64>
.data 1 [152] # 1676 1 vec<309,r64>
.data 1 [119] # 1677 1 vec<309,r64>
.data 1 [83] # 1678 1 vec<309,r64>
.data 1 [107] # 1679 1 vec<309,r64>
.data 1 [187] # 1680 1 vec<309,r64>
.data 1 [107] # 1681 1 vec<309,r64>
.data 1 [50] # 1682 1 vec<309,r64>
.data 1 [49] # 1683 1 vec<309,r64>
.data 1 [127] # 1684 1 vec<309,r64>
.data 1 [85] # 1685 1 vec<309,r64>
.data 1 [136] # 1686 1 vec<309,r64>
.data 1 [107] # 1687 1 vec<309,r64>
.data 1 [170] # 1688 1 vec<309,r64>
.data 1 [6] # 1689 1 vec<309,r64>
.data 1 [127] # 1690 1 vec<309,r64>
.data 1 [253] # 1691 1 vec<309,r64>
.data 1 [222] # 1692 1 vec<309,r64>
.data 1 [106] # 1693 1 vec<309,r64>
.data 1 [190] # 1694 1 vec<309,r64>
.data 1 [107] # 1695 1 vec<309,r64>
.data 1 [42] # 1696 1 vec<309,r64>
.data 1 [100] # 1697 1 vec<309,r64>
.data 1 [111] # 1698 1 vec<309,r64>
.data 1 [94] # 1699 1 vec<309,r64>
.data 1 [203] # 1700 1 vec<309,r64>
.data 1 [2] # 1701 1 vec<309,r64>
.data 1 [243] # 1702 1 vec<309,r64>
.data 1 [107] # 1703 1 vec<309,r64>
.data 1 [53] # 1704 1 vec<309,r64>
.data 1 [61] # 1705 1 vec<309,r64>
.data 1 [11] # 1706 1 vec<309,r64>
.data 1 [54] # 1707 1 vec<309,r64>
.data 1 [126] # 1708 1 vec<309,r64>
.data 1 [195] # 1709 1 vec<309,r64>
.data 1 [39] # 1710 1 vec<309,r64>
.data 1 [108] # 1711 1 vec<309,r64>
.data 1 [130] # 1712 1 vec<309,r64>
.data 1 [12] # 1713 1 vec<309,r64>
.data 1 [142] # 1714 1 vec<309,r64>
.data 1 [195] # 1715 1 vec<309,r64>
.data 1 [93] # 1716 1 vec<309,r64>
.data 1 [180] # 1717 1 vec<309,r64>
.data 1 [93] # 1718 1 vec<309,r64>
.data 1 [108] # 1719 1 vec<309,r64>
.data 1 [209] # 1720 1 vec<309,r64>
.data 1 [199] # 1721 1 vec<309,r64>
.data 1 [56] # 1722 1 vec<309,r64>
.data 1 [154] # 1723 1 vec<309,r64>
.data 1 [186] # 1724 1 vec<309,r64>
.data 1 [144] # 1725 1 vec<309,r64>
.data 1 [146] # 1726 1 vec<309,r64>
.data 1 [108] # 1727 1 vec<309,r64>
.data 1 [198] # 1728 1 vec<309,r64>
.data 1 [249] # 1729 1 vec<309,r64>
.data 1 [198] # 1730 1 vec<309,r64>
.data 1 [64] # 1731 1 vec<309,r64>
.data 1 [233] # 1732 1 vec<309,r64>
.data 1 [52] # 1733 1 vec<309,r64>
.data 1 [199] # 1734 1 vec<309,r64>
.data 1 [108] # 1735 1 vec<309,r64>
.data 1 [55] # 1736 1 vec<309,r64>
.data 1 [184] # 1737 1 vec<309,r64>
.data 1 [248] # 1738 1 vec<309,r64>
.data 1 [144] # 1739 1 vec<309,r64>
.data 1 [35] # 1740 1 vec<309,r64>
.data 1 [2] # 1741 1 vec<309,r64>
.data 1 [253] # 1742 1 vec<309,r64>
.data 1 [108] # 1743 1 vec<309,r64>
.data 1 [35] # 1744 1 vec<309,r64>
.data 1 [115] # 1745 1 vec<309,r64>
.data 1 [155] # 1746 1 vec<309,r64>
.data 1 [58] # 1747 1 vec<309,r64>
.data 1 [86] # 1748 1 vec<309,r64>
.data 1 [33] # 1749 1 vec<309,r64>
.data 1 [50] # 1750 1 vec<309,r64>
.data 1 [109] # 1751 1 vec<309,r64>
.data 1 [235] # 1752 1 vec<309,r64>
.data 1 [79] # 1753 1 vec<309,r64>
.data 1 [66] # 1754 1 vec<309,r64>
.data 1 [201] # 1755 1 vec<309,r64>
.data 1 [171] # 1756 1 vec<309,r64>
.data 1 [169] # 1757 1 vec<309,r64>
.data 1 [102] # 1758 1 vec<309,r64>
.data 1 [109] # 1759 1 vec<309,r64>
.data 1 [230] # 1760 1 vec<309,r64>
.data 1 [227] # 1761 1 vec<309,r64>
.data 1 [146] # 1762 1 vec<309,r64>
.data 1 [187] # 1763 1 vec<309,r64>
.data 1 [22] # 1764 1 vec<309,r64>
.data 1 [84] # 1765 1 vec<309,r64>
.data 1 [156] # 1766 1 vec<309,r64>
.data 1 [109] # 1767 1 vec<309,r64>
.data 1 [112] # 1768 1 vec<309,r64>
.data 1 [206] # 1769 1 vec<309,r64>
.data 1 [59] # 1770 1 vec<309,r64>
.data 1 [53] # 1771 1 vec<309,r64>
.data 1 [142] # 1772 1 vec<309,r64>
.data 1 [180] # 1773 1 vec<309,r64>
.data 1 [209] # 1774 1 vec<309,r64>
.data 1 [109] # 1775 1 vec<309,r64>
.data 1 [12] # 1776 1 vec<309,r64>
.data 1 [194] # 1777 1 vec<309,r64>
.data 1 [138] # 1778 1 vec<309,r64>
.data 1 [194] # 1779 1 vec<309,r64>
.data 1 [177] # 1780 1 vec<309,r64>
.data 1 [33] # 1781 1 vec<309,r64>
.data 1 [6] # 1782 1 vec<309,r64>
.data 1 [110] # 1783 1 vec<309,r64>
.data 1 [143] # 1784 1 vec<309,r64>
.data 1 [114] # 1785 1 vec<309,r64>
.data 1 [45] # 1786 1 vec<309,r64>
.data 1 [51] # 1787 1 vec<309,r64>
.data 1 [30] # 1788 1 vec<309,r64>
.data 1 [170] # 1789 1 vec<309,r64>
.data 1 [59] # 1790 1 vec<309,r64>
.data 1 [110] # 1791 1 vec<309,r64>
.data 1 [153] # 1792 1 vec<309,r64>
.data 1 [103] # 1793 1 vec<309,r64>
.data 1 [252] # 1794 1 vec<309,r64>
.data 1 [223] # 1795 1 vec<309,r64>
.data 1 [82] # 1796 1 vec<309,r64>
.data 1 [74] # 1797 1 vec<309,r64>
.data 1 [113] # 1798 1 vec<309,r64>
.data 1 [110] # 1799 1 vec<309,r64>
.data 1 [127] # 1800 1 vec<309,r64>
.data 1 [129] # 1801 1 vec<309,r64>
.data 1 [251] # 1802 1 vec<309,r64>
.data 1 [151] # 1803 1 vec<309,r64>
.data 1 [231] # 1804 1 vec<309,r64>
.data 1 [156] # 1805 1 vec<309,r64>
.data 1 [165] # 1806 1 vec<309,r64>
.data 1 [110] # 1807 1 vec<309,r64>
.data 1 [223] # 1808 1 vec<309,r64>
.data 1 [97] # 1809 1 vec<309,r64>
.data 1 [250] # 1810 1 vec<309,r64>
.data 1 [125] # 1811 1 vec<309,r64>
.data 1 [33] # 1812 1 vec<309,r64>
.data 1 [4] # 1813 1 vec<309,r64>
.data 1 [219] # 1814 1 vec<309,r64>
.data 1 [110] # 1815 1 vec<309,r64>
.data 1 [44] # 1816 1 vec<309,r64>
.data 1 [125] # 1817 1 vec<309,r64>
.data 1 [188] # 1818 1 vec<309,r64>
.data 1 [238] # 1819 1 vec<309,r64>
.data 1 [148] # 1820 1 vec<309,r64>
.data 1 [226] # 1821 1 vec<309,r64>
.data 1 [16] # 1822 1 vec<309,r64>
.data 1 [111] # 1823 1 vec<309,r64>
.data 1 [118] # 1824 1 vec<309,r64>
.data 1 [156] # 1825 1 vec<309,r64>
.data 1 [107] # 1826 1 vec<309,r64>
.data 1 [42] # 1827 1 vec<309,r64>
.data 1 [58] # 1828 1 vec<309,r64>
.data 1 [27] # 1829 1 vec<309,r64>
.data 1 [69] # 1830 1 vec<309,r64>
.data 1 [111] # 1831 1 vec<309,r64>
.data 1 [148] # 1832 1 vec<309,r64>
.data 1 [131] # 1833 1 vec<309,r64>
.data 1 [6] # 1834 1 vec<309,r64>
.data 1 [181] # 1835 1 vec<309,r64>
.data 1 [8] # 1836 1 vec<309,r64>
.data 1 [98] # 1837 1 vec<309,r64>
.data 1 [122] # 1838 1 vec<309,r64>
.data 1 [111] # 1839 1 vec<309,r64>
.data 1 [61] # 1840 1 vec<309,r64>
.data 1 [18] # 1841 1 vec<309,r64>
.data 1 [36] # 1842 1 vec<309,r64>
.data 1 [113] # 1843 1 vec<309,r64>
.data 1 [69] # 1844 1 vec<309,r64>
.data 1 [125] # 1845 1 vec<309,r64>
.data 1 [176] # 1846 1 vec<309,r64>
.data 1 [111] # 1847 1 vec<309,r64>
.data 1 [204] # 1848 1 vec<309,r64>
.data 1 [22] # 1849 1 vec<309,r64>
.data 1 [109] # 1850 1 vec<309,r64>
.data 1 [205] # 1851 1 vec<309,r64>
.data 1 [150] # 1852 1 vec<309,r64>
.data 1 [156] # 1853 1 vec<309,r64>
.data 1 [228] # 1854 1 vec<309,r64>
.data 1 [111] # 1855 1 vec<309,r64>
.data 1 [127] # 1856 1 vec<309,r64>
.data 1 [92] # 1857 1 vec<309,r64>
.data 1 [200] # 1858 1 vec<309,r64>
.data 1 [128] # 1859 1 vec<309,r64>
.data 1 [188] # 1860 1 vec<309,r64>
.data 1 [195] # 1861 1 vec<309,r64>
.data 1 [25] # 1862 1 vec<309,r64>
.data 1 [112] # 1863 1 vec<309,r64>
.data 1 [207] # 1864 1 vec<309,r64>
.data 1 [57] # 1865 1 vec<309,r64>
.data 1 [125] # 1866 1 vec<309,r64>
.data 1 [208] # 1867 1 vec<309,r64>
.data 1 [85] # 1868 1 vec<309,r64>
.data 1 [26] # 1869 1 vec<309,r64>
.data 1 [80] # 1870 1 vec<309,r64>
.data 1 [112] # 1871 1 vec<309,r64>
.data 1 [67] # 1872 1 vec<309,r64>
.data 1 [136] # 1873 1 vec<309,r64>
.data 1 [156] # 1874 1 vec<309,r64>
.data 1 [68] # 1875 1 vec<309,r64>
.data 1 [235] # 1876 1 vec<309,r64>
.data 1 [32] # 1877 1 vec<309,r64>
.data 1 [132] # 1878 1 vec<309,r64>
.data 1 [112] # 1879 1 vec<309,r64>
.data 1 [84] # 1880 1 vec<309,r64>
.data 1 [170] # 1881 1 vec<309,r64>
.data 1 [195] # 1882 1 vec<309,r64>
.data 1 [21] # 1883 1 vec<309,r64>
.data 1 [38] # 1884 1 vec<309,r64>
.data 1 [41] # 1885 1 vec<309,r64>
.data 1 [185] # 1886 1 vec<309,r64>
.data 1 [112] # 1887 1 vec<309,r64>
.data 1 [233] # 1888 1 vec<309,r64>
.data 1 [148] # 1889 1 vec<309,r64>
.data 1 [52] # 1890 1 vec<309,r64>
.data 1 [155] # 1891 1 vec<309,r64>
.data 1 [111] # 1892 1 vec<309,r64>
.data 1 [115] # 1893 1 vec<309,r64>
.data 1 [239] # 1894 1 vec<309,r64>
.data 1 [112] # 1895 1 vec<309,r64>
.data 1 [17] # 1896 1 vec<309,r64>
.data 1 [221] # 1897 1 vec<309,r64>
.data 1 [0] # 1898 1 vec<309,r64>
.data 1 [193] # 1899 1 vec<309,r64>
.data 1 [37] # 1900 1 vec<309,r64>
.data 1 [168] # 1901 1 vec<309,r64>
.data 1 [35] # 1902 1 vec<309,r64>
.data 1 [113] # 1903 1 vec<309,r64>
.data 1 [86] # 1904 1 vec<309,r64>
.data 1 [20] # 1905 1 vec<309,r64>
.data 1 [65] # 1906 1 vec<309,r64>
.data 1 [49] # 1907 1 vec<309,r64>
.data 1 [47] # 1908 1 vec<309,r64>
.data 1 [146] # 1909 1 vec<309,r64>
.data 1 [88] # 1910 1 vec<309,r64>
.data 1 [113] # 1911 1 vec<309,r64>
.data 1 [107] # 1912 1 vec<309,r64>
.data 1 [89] # 1913 1 vec<309,r64>
.data 1 [145] # 1914 1 vec<309,r64>
.data 1 [253] # 1915 1 vec<309,r64>
.data 1 [186] # 1916 1 vec<309,r64>
.data 1 [182] # 1917 1 vec<309,r64>
.data 1 [142] # 1918 1 vec<309,r64>
.data 1 [113] # 1919 1 vec<309,r64>
.data 1 [227] # 1920 1 vec<309,r64>
.data 1 [215] # 1921 1 vec<309,r64>
.data 1 [122] # 1922 1 vec<309,r64>
.data 1 [222] # 1923 1 vec<309,r64>
.data 1 [52] # 1924 1 vec<309,r64>
.data 1 [50] # 1925 1 vec<309,r64>
.data 1 [195] # 1926 1 vec<309,r64>
.data 1 [113] # 1927 1 vec<309,r64>
.data 1 [220] # 1928 1 vec<309,r64>
.data 1 [141] # 1929 1 vec<309,r64>
.data 1 [25] # 1930 1 vec<309,r64>
.data 1 [22] # 1931 1 vec<309,r64>
.data 1 [194] # 1932 1 vec<309,r64>
.data 1 [254] # 1933 1 vec<309,r64>
.data 1 [247] # 1934 1 vec<309,r64>
.data 1 [113] # 1935 1 vec<309,r64>
.data 1 [83] # 1936 1 vec<309,r64>
.data 1 [241] # 1937 1 vec<309,r64>
.data 1 [159] # 1938 1 vec<309,r64>
.data 1 [155] # 1939 1 vec<309,r64>
.data 1 [114] # 1940 1 vec<309,r64>
.data 1 [254] # 1941 1 vec<309,r64>
.data 1 [45] # 1942 1 vec<309,r64>
.data 1 [114] # 1943 1 vec<309,r64>
.data 1 [212] # 1944 1 vec<309,r64>
.data 1 [246] # 1945 1 vec<309,r64>
.data 1 [67] # 1946 1 vec<309,r64>
.data 1 [161] # 1947 1 vec<309,r64>
.data 1 [7] # 1948 1 vec<309,r64>
.data 1 [191] # 1949 1 vec<309,r64>
.data 1 [98] # 1950 1 vec<309,r64>
.data 1 [114] # 1951 1 vec<309,r64>
.data 1 [137] # 1952 1 vec<309,r64>
.data 1 [244] # 1953 1 vec<309,r64>
.data 1 [148] # 1954 1 vec<309,r64>
.data 1 [137] # 1955 1 vec<309,r64>
.data 1 [201] # 1956 1 vec<309,r64>
.data 1 [110] # 1957 1 vec<309,r64>
.data 1 [151] # 1958 1 vec<309,r64>
.data 1 [114] # 1959 1 vec<309,r64>
.data 1 [171] # 1960 1 vec<309,r64>
.data 1 [49] # 1961 1 vec<309,r64>
.data 1 [250] # 1962 1 vec<309,r64>
.data 1 [235] # 1963 1 vec<309,r64>
.data 1 [123] # 1964 1 vec<309,r64>
.data 1 [74] # 1965 1 vec<309,r64>
.data 1 [205] # 1966 1 vec<309,r64>
.data 1 [114] # 1967 1 vec<309,r64>
.data 1 [11] # 1968 1 vec<309,r64>
.data 1 [95] # 1969 1 vec<309,r64>
.data 1 [124] # 1970 1 vec<309,r64>
.data 1 [115] # 1971 1 vec<309,r64>
.data 1 [141] # 1972 1 vec<309,r64>
.data 1 [78] # 1973 1 vec<309,r64>
.data 1 [2] # 1974 1 vec<309,r64>
.data 1 [115] # 1975 1 vec<309,r64>
.data 1 [205] # 1976 1 vec<309,r64>
.data 1 [118] # 1977 1 vec<309,r64>
.data 1 [91] # 1978 1 vec<309,r64>
.data 1 [208] # 1979 1 vec<309,r64>
.data 1 [48] # 1980 1 vec<309,r64>
.data 1 [226] # 1981 1 vec<309,r64>
.data 1 [54] # 1982 1 vec<309,r64>
.data 1 [115] # 1983 1 vec<309,r64>
.data 1 [129] # 1984 1 vec<309,r64>
.data 1 [84] # 1985 1 vec<309,r64>
.data 1 [114] # 1986 1 vec<309,r64>
.data 1 [4] # 1987 1 vec<309,r64>
.data 1 [189] # 1988 1 vec<309,r64>
.data 1 [154] # 1989 1 vec<309,r64>
.data 1 [108] # 1990 1 vec<309,r64>
.data 1 [115] # 1991 1 vec<309,r64>
.data 1 [208] # 1992 1 vec<309,r64>
.data 1 [116] # 1993 1 vec<309,r64>
.data 1 [199] # 1994 1 vec<309,r64>
.data 1 [34] # 1995 1 vec<309,r64>
.data 1 [182] # 1996 1 vec<309,r64>
.data 1 [224] # 1997 1 vec<309,r64>
.data 1 [161] # 1998 1 vec<309,r64>
.data 1 [115] # 1999 1 vec<309,r64>
.data 1 [4] # 2000 1 vec<309,r64>
.data 1 [82] # 2001 1 vec<309,r64>
.data 1 [121] # 2002 1 vec<309,r64>
.data 1 [171] # 2003 1 vec<309,r64>
.data 1 [227] # 2004 1 vec<309,r64>
.data 1 [88] # 2005 1 vec<309,r64>
.data 1 [214] # 2006 1 vec<309,r64>
.data 1 [115] # 2007 1 vec<309,r64>
.data 1 [134] # 2008 1 vec<309,r64>
.data 1 [166] # 2009 1 vec<309,r64>
.data 1 [87] # 2010 1 vec<309,r64>
.data 1 [150] # 2011 1 vec<309,r64>
.data 1 [28] # 2012 1 vec<309,r64>
.data 1 [239] # 2013 1 vec<309,r64>
.data 1 [11] # 2014 1 vec<309,r64>
.data 1 [116] # 2015 1 vec<309,r64>
.data 1 [20] # 2016 1 vec<309,r64>
.data 1 [200] # 2017 1 vec<309,r64>
.data 1 [246] # 2018 1 vec<309,r64>
.data 1 [221] # 2019 1 vec<309,r64>
.data 1 [113] # 2020 1 vec<309,r64>
.data 1 [117] # 2021 1 vec<309,r64>
.data 1 [65] # 2022 1 vec<309,r64>
.data 1 [116] # 2023 1 vec<309,r64>
.data 1 [24] # 2024 1 vec<309,r64>
.data 1 [122] # 2025 1 vec<309,r64>
.data 1 [116] # 2026 1 vec<309,r64>
.data 1 [85] # 2027 1 vec<309,r64>
.data 1 [206] # 2028 1 vec<309,r64>
.data 1 [210] # 2029 1 vec<309,r64>
.data 1 [117] # 2030 1 vec<309,r64>
.data 1 [116] # 2031 1 vec<309,r64>
.data 1 [158] # 2032 1 vec<309,r64>
.data 1 [152] # 2033 1 vec<309,r64>
.data 1 [209] # 2034 1 vec<309,r64>
.data 1 [234] # 2035 1 vec<309,r64>
.data 1 [129] # 2036 1 vec<309,r64>
.data 1 [71] # 2037 1 vec<309,r64>
.data 1 [171] # 2038 1 vec<309,r64>
.data 1 [116] # 2039 1 vec<309,r64>
.data 1 [99] # 2040 1 vec<309,r64>
.data 1 [255] # 2041 1 vec<309,r64>
.data 1 [194] # 2042 1 vec<309,r64>
.data 1 [50] # 2043 1 vec<309,r64>
.data 1 [177] # 2044 1 vec<309,r64>
.data 1 [12] # 2045 1 vec<309,r64>
.data 1 [225] # 2046 1 vec<309,r64>
.data 1 [116] # 2047 1 vec<309,r64>
.data 1 [60] # 2048 1 vec<309,r64>
.data 1 [191] # 2049 1 vec<309,r64>
.data 1 [115] # 2050 1 vec<309,r64>
.data 1 [127] # 2051 1 vec<309,r64>
.data 1 [221] # 2052 1 vec<309,r64>
.data 1 [79] # 2053 1 vec<309,r64>
.data 1 [21] # 2054 1 vec<309,r64>
.data 1 [117] # 2055 1 vec<309,r64>
.data 1 [11] # 2056 1 vec<309,r64>
.data 1 [175] # 2057 1 vec<309,r64>
.data 1 [80] # 2058 1 vec<309,r64>
.data 1 [223] # 2059 1 vec<309,r64>
.data 1 [212] # 2060 1 vec<309,r64>
.data 1 [163] # 2061 1 vec<309,r64>
.data 1 [74] # 2062 1 vec<309,r64>
.data 1 [117] # 2063 1 vec<309,r64>
.data 1 [103] # 2064 1 vec<309,r64>
.data 1 [109] # 2065 1 vec<309,r64>
.data 1 [146] # 2066 1 vec<309,r64>
.data 1 [11] # 2067 1 vec<309,r64>
.data 1 [101] # 2068 1 vec<309,r64>
.data 1 [166] # 2069 1 vec<309,r64>
.data 1 [128] # 2070 1 vec<309,r64>
.data 1 [117] # 2071 1 vec<309,r64>
.data 1 [192] # 2072 1 vec<309,r64>
.data 1 [8] # 2073 1 vec<309,r64>
.data 1 [119] # 2074 1 vec<309,r64>
.data 1 [78] # 2075 1 vec<309,r64>
.data 1 [254] # 2076 1 vec<309,r64>
.data 1 [207] # 2077 1 vec<309,r64>
.data 1 [180] # 2078 1 vec<309,r64>
.data 1 [117] # 2079 1 vec<309,r64>
.data 1 [241] # 2080 1 vec<309,r64>
.data 1 [202] # 2081 1 vec<309,r64>
.data 1 [20] # 2082 1 vec<309,r64>
.data 1 [226] # 2083 1 vec<309,r64>
.data 1 [253] # 2084 1 vec<309,r64>
.data 1 [3] # 2085 1 vec<309,r64>
.data 1 [234] # 2086 1 vec<309,r64>
.data 1 [117] # 2087 1 vec<309,r64>
.data 1 [214] # 2088 1 vec<309,r64>
.data 1 [254] # 2089 1 vec<309,r64>
.data 1 [76] # 2090 1 vec<309,r64>
.data 1 [173] # 2091 1 vec<309,r64>
.data 1 [126] # 2092 1 vec<309,r64>
.data 1 [66] # 2093 1 vec<309,r64>
.data 1 [32] # 2094 1 vec<309,r64>
.data 1 [118] # 2095 1 vec<309,r64>
.data 1 [140] # 2096 1 vec<309,r64>
.data 1 [62] # 2097 1 vec<309,r64>
.data 1 [160] # 2098 1 vec<309,r64>
.data 1 [88] # 2099 1 vec<309,r64>
.data 1 [30] # 2100 1 vec<309,r64>
.data 1 [83] # 2101 1 vec<309,r64>
.data 1 [84] # 2102 1 vec<309,r64>
.data 1 [118] # 2103 1 vec<309,r64>
.data 1 [47] # 2104 1 vec<309,r64>
.data 1 [78] # 2105 1 vec<309,r64>
.data 1 [200] # 2106 1 vec<309,r64>
.data 1 [238] # 2107 1 vec<309,r64>
.data 1 [229] # 2108 1 vec<309,r64>
.data 1 [103] # 2109 1 vec<309,r64>
.data 1 [137] # 2110 1 vec<309,r64>
.data 1 [118] # 2111 1 vec<309,r64>
.data 1 [187] # 2112 1 vec<309,r64>
.data 1 [97] # 2113 1 vec<309,r64>
.data 1 [122] # 2114 1 vec<309,r64>
.data 1 [106] # 2115 1 vec<309,r64>
.data 1 [223] # 2116 1 vec<309,r64>
.data 1 [193] # 2117 1 vec<309,r64>
.data 1 [191] # 2118 1 vec<309,r64>
.data 1 [118] # 2119 1 vec<309,r64>
.data 1 [21] # 2120 1 vec<309,r64>
.data 1 [125] # 2121 1 vec<309,r64>
.data 1 [140] # 2122 1 vec<309,r64>
.data 1 [162] # 2123 1 vec<309,r64>
.data 1 [43] # 2124 1 vec<309,r64>
.data 1 [217] # 2125 1 vec<309,r64>
.data 1 [243] # 2126 1 vec<309,r64>
.data 1 [118] # 2127 1 vec<309,r64>
.data 1 [90] # 2128 1 vec<309,r64>
.data 1 [156] # 2129 1 vec<309,r64>
.data 1 [47] # 2130 1 vec<309,r64>
.data 1 [139] # 2131 1 vec<309,r64>
.data 1 [118] # 2132 1 vec<309,r64>
.data 1 [207] # 2133 1 vec<309,r64>
.data 1 [40] # 2134 1 vec<309,r64>
.data 1 [119] # 2135 1 vec<309,r64>
.data 1 [112] # 2136 1 vec<309,r64>
.data 1 [131] # 2137 1 vec<309,r64>
.data 1 [251] # 2138 1 vec<309,r64>
.data 1 [45] # 2139 1 vec<309,r64>
.data 1 [84] # 2140 1 vec<309,r64>
.data 1 [3] # 2141 1 vec<309,r64>
.data 1 [95] # 2142 1 vec<309,r64>
.data 1 [119] # 2143 1 vec<309,r64>
.data 1 [38] # 2144 1 vec<309,r64>
.data 1 [50] # 2145 1 vec<309,r64>
.data 1 [189] # 2146 1 vec<309,r64>
.data 1 [156] # 2147 1 vec<309,r64>
.data 1 [20] # 2148 1 vec<309,r64>
.data 1 [98] # 2149 1 vec<309,r64>
.data 1 [147] # 2150 1 vec<309,r64>
.data 1 [119] # 2151 1 vec<309,r64>
.data 1 [176] # 2152 1 vec<309,r64>
.data 1 [126] # 2153 1 vec<309,r64>
.data 1 [236] # 2154 1 vec<309,r64>
.data 1 [195] # 2155 1 vec<309,r64>
.data 1 [153] # 2156 1 vec<309,r64>
.data 1 [58] # 2157 1 vec<309,r64>
.data 1 [200] # 2158 1 vec<309,r64>
.data 1 [119] # 2159 1 vec<309,r64>
.data 1 [92] # 2160 1 vec<309,r64>
.data 1 [158] # 2161 1 vec<309,r64>
.data 1 [231] # 2162 1 vec<309,r64>
.data 1 [52] # 2163 1 vec<309,r64>
.data 1 [64] # 2164 1 vec<309,r64>
.data 1 [73] # 2165 1 vec<309,r64>
.data 1 [254] # 2166 1 vec<309,r64>
.data 1 [119] # 2167 1 vec<309,r64>
.data 1 [249] # 2168 1 vec<309,r64>
.data 1 [194] # 2169 1 vec<309,r64>
.data 1 [16] # 2170 1 vec<309,r64>
.data 1 [33] # 2171 1 vec<309,r64>
.data 1 [200] # 2172 1 vec<309,r64>
.data 1 [237] # 2173 1 vec<309,r64>
.data 1 [50] # 2174 1 vec<309,r64>
.data 1 [120] # 2175 1 vec<309,r64>
.data 1 [184] # 2176 1 vec<309,r64>
.data 1 [243] # 2177 1 vec<309,r64>
.data 1 [84] # 2178 1 vec<309,r64>
.data 1 [41] # 2179 1 vec<309,r64>
.data 1 [58] # 2180 1 vec<309,r64>
.data 1 [169] # 2181 1 vec<309,r64>
.data 1 [103] # 2182 1 vec<309,r64>
.data 1 [120] # 2183 1 vec<309,r64>
.data 1 [165] # 2184 1 vec<309,r64>
.data 1 [48] # 2185 1 vec<309,r64>
.data 1 [170] # 2186 1 vec<309,r64>
.data 1 [179] # 2187 1 vec<309,r64>
.data 1 [136] # 2188 1 vec<309,r64>
.data 1 [147] # 2189 1 vec<309,r64>
.data 1 [157] # 2190 1 vec<309,r64>
.data 1 [120] # 2191 1 vec<309,r64>
.data 1 [103] # 2192 1 vec<309,r64>
.data 1 [94] # 2193 1 vec<309,r64>
.data 1 [74] # 2194 1 vec<309,r64>
.data 1 [112] # 2195 1 vec<309,r64>
.data 1 [53] # 2196 1 vec<309,r64>
.data 1 [124] # 2197 1 vec<309,r64>
.data 1 [210] # 2198 1 vec<309,r64>
.data 1 [120] # 2199 1 vec<309,r64>
.data 1 [1] # 2200 1 vec<309,r64>
.data 1 [246] # 2201 1 vec<309,r64>
.data 1 [92] # 2202 1 vec<309,r64>
.data 1 [204] # 2203 1 vec<309,r64>
.data 1 [66] # 2204 1 vec<309,r64>
.data 1 [27] # 2205 1 vec<309,r64>
.data 1 [7] # 2206 1 vec<309,r64>
.data 1 [121] # 2207 1 vec<309,r64>
.data 1 [130] # 2208 1 vec<309,r64>
.data 1 [51] # 2209 1 vec<309,r64>
.data 1 [116] # 2210 1 vec<309,r64>
.data 1 [127] # 2211 1 vec<309,r64>
.data 1 [19] # 2212 1 vec<309,r64>
.data 1 [226] # 2213 1 vec<309,r64>
.data 1 [60] # 2214 1 vec<309,r64>
.data 1 [121] # 2215 1 vec<309,r64>
.data 1 [49] # 2216 1 vec<309,r64>
.data 1 [160] # 2217 1 vec<309,r64>
.data 1 [168] # 2218 1 vec<309,r64>
.data 1 [47] # 2219 1 vec<309,r64>
.data 1 [76] # 2220 1 vec<309,r64>
.data 1 [13] # 2221 1 vec<309,r64>
.data 1 [114] # 2222 1 vec<309,r64>
.data 1 [121] # 2223 1 vec<309,r64>
.data 1 [61] # 2224 1 vec<309,r64>
.data 1 [200] # 2225 1 vec<309,r64>
.data 1 [146] # 2226 1 vec<309,r64>
.data 1 [59] # 2227 1 vec<309,r64>
.data 1 [159] # 2228 1 vec<309,r64>
.data 1 [144] # 2229 1 vec<309,r64>
.data 1 [166] # 2230 1 vec<309,r64>
.data 1 [121] # 2231 1 vec<309,r64>
.data 1 [77] # 2232 1 vec<309,r64>
.data 1 [122] # 2233 1 vec<309,r64>
.data 1 [119] # 2234 1 vec<309,r64>
.data 1 [10] # 2235 1 vec<309,r64>
.data 1 [199] # 2236 1 vec<309,r64>
.data 1 [52] # 2237 1 vec<309,r64>
.data 1 [220] # 2238 1 vec<309,r64>
.data 1 [121] # 2239 1 vec<309,r64>
.data 1 [112] # 2240 1 vec<309,r64>
.data 1 [172] # 2241 1 vec<309,r64>
.data 1 [138] # 2242 1 vec<309,r64>
.data 1 [102] # 2243 1 vec<309,r64>
.data 1 [252] # 2244 1 vec<309,r64>
.data 1 [160] # 2245 1 vec<309,r64>
.data 1 [17] # 2246 1 vec<309,r64>
.data 1 [122] # 2247 1 vec<309,r64>
.data 1 [140] # 2248 1 vec<309,r64>
.data 1 [87] # 2249 1 vec<309,r64>
.data 1 [45] # 2250 1 vec<309,r64>
.data 1 [128] # 2251 1 vec<309,r64>
.data 1 [59] # 2252 1 vec<309,r64>
.data 1 [9] # 2253 1 vec<309,r64>
.data 1 [70] # 2254 1 vec<309,r64>
.data 1 [122] # 2255 1 vec<309,r64>
.data 1 [111] # 2256 1 vec<309,r64>
.data 1 [173] # 2257 1 vec<309,r64>
.data 1 [56] # 2258 1 vec<309,r64>
.data 1 [96] # 2259 1 vec<309,r64>
.data 1 [138] # 2260 1 vec<309,r64>
.data 1 [139] # 2261 1 vec<309,r64>
.data 1 [123] # 2262 1 vec<309,r64>
.data 1 [122] # 2263 1 vec<309,r64>
.data 1 [101] # 2264 1 vec<309,r64>
.data 1 [108] # 2265 1 vec<309,r64>
.data 1 [35] # 2266 1 vec<309,r64>
.data 1 [124] # 2267 1 vec<309,r64>
.data 1 [54] # 2268 1 vec<309,r64>
.data 1 [55] # 2269 1 vec<309,r64>
.data 1 [177] # 2270 1 vec<309,r64>
.data 1 [122] # 2271 1 vec<309,r64>
.data 1 [127] # 2272 1 vec<309,r64>
.data 1 [71] # 2273 1 vec<309,r64>
.data 1 [44] # 2274 1 vec<309,r64>
.data 1 [27] # 2275 1 vec<309,r64>
.data 1 [4] # 2276 1 vec<309,r64>
.data 1 [133] # 2277 1 vec<309,r64>
.data 1 [229] # 2278 1 vec<309,r64>
.data 1 [122] # 2279 1 vec<309,r64>
.data 1 [94] # 2280 1 vec<309,r64>
.data 1 [89] # 2281 1 vec<309,r64>
.data 1 [247] # 2282 1 vec<309,r64>
.data 1 [33] # 2283 1 vec<309,r64>
.data 1 [69] # 2284 1 vec<309,r64>
.data 1 [230] # 2285 1 vec<309,r64>
.data 1 [26] # 2286 1 vec<309,r64>
.data 1 [123] # 2287 1 vec<309,r64>
.data 1 [219] # 2288 1 vec<309,r64>
.data 1 [151] # 2289 1 vec<309,r64>
.data 1 [58] # 2290 1 vec<309,r64>
.data 1 [53] # 2291 1 vec<309,r64>
.data 1 [235] # 2292 1 vec<309,r64>
.data 1 [207] # 2293 1 vec<309,r64>
.data 1 [80] # 2294 1 vec<309,r64>
.data 1 [123] # 2295 1 vec<309,r64>
.data 1 [210] # 2296 1 vec<309,r64>
.data 1 [61] # 2297 1 vec<309,r64>
.data 1 [137] # 2298 1 vec<309,r64>
.data 1 [2] # 2299 1 vec<309,r64>
.data 1 [230] # 2300 1 vec<309,r64>
.data 1 [3] # 2301 1 vec<309,r64>
.data 1 [133] # 2302 1 vec<309,r64>
.data 1 [123] # 2303 1 vec<309,r64>
.data 1 [70] # 2304 1 vec<309,r64>
.data 1 [141] # 2305 1 vec<309,r64>
.data 1 [43] # 2306 1 vec<309,r64>
.data 1 [131] # 2307 1 vec<309,r64>
.data 1 [223] # 2308 1 vec<309,r64>
.data 1 [68] # 2309 1 vec<309,r64>
.data 1 [186] # 2310 1 vec<309,r64>
.data 1 [123] # 2311 1 vec<309,r64>
.data 1 [76] # 2312 1 vec<309,r64>
.data 1 [56] # 2313 1 vec<309,r64>
.data 1 [251] # 2314 1 vec<309,r64>
.data 1 [177] # 2315 1 vec<309,r64>
.data 1 [11] # 2316 1 vec<309,r64>
.data 1 [107] # 2317 1 vec<309,r64>
.data 1 [240] # 2318 1 vec<309,r64>
.data 1 [123] # 2319 1 vec<309,r64>
.data 1 [95] # 2320 1 vec<309,r64>
.data 1 [6] # 2321 1 vec<309,r64>
.data 1 [122] # 2322 1 vec<309,r64>
.data 1 [158] # 2323 1 vec<309,r64>
.data 1 [206] # 2324 1 vec<309,r64>
.data 1 [133] # 2325 1 vec<309,r64>
.data 1 [36] # 2326 1 vec<309,r64>
.data 1 [124] # 2327 1 vec<309,r64>
.data 1 [246] # 2328 1 vec<309,r64>
.data 1 [135] # 2329 1 vec<309,r64>
.data 1 [24] # 2330 1 vec<309,r64>
.data 1 [70] # 2331 1 vec<309,r64>
.data 1 [66] # 2332 1 vec<309,r64>
.data 1 [167] # 2333 1 vec<309,r64>
.data 1 [89] # 2334 1 vec<309,r64>
.data 1 [124] # 2335 1 vec<309,r64>
.data 1 [250] # 2336 1 vec<309,r64>
.data 1 [84] # 2337 1 vec<309,r64>
.data 1 [207] # 2338 1 vec<309,r64>
.data 1 [107] # 2339 1 vec<309,r64>
.data 1 [137] # 2340 1 vec<309,r64>
.data 1 [8] # 2341 1 vec<309,r64>
.data 1 [144] # 2342 1 vec<309,r64>
.data 1 [124] # 2343 1 vec<309,r64>
.data 1 [56] # 2344 1 vec<309,r64>
.data 1 [42] # 2345 1 vec<309,r64>
.data 1 [195] # 2346 1 vec<309,r64>
.data 1 [198] # 2347 1 vec<309,r64>
.data 1 [171] # 2348 1 vec<309,r64>
.data 1 [10] # 2349 1 vec<309,r64>
.data 1 [196] # 2350 1 vec<309,r64>
.data 1 [124] # 2351 1 vec<309,r64>
.data 1 [199] # 2352 1 vec<309,r64>
.data 1 [244] # 2353 1 vec<309,r64>
.data 1 [115] # 2354 1 vec<309,r64>
.data 1 [184] # 2355 1 vec<309,r64>
.data 1 [86] # 2356 1 vec<309,r64>
.data 1 [13] # 2357 1 vec<309,r64>
.data 1 [249] # 2358 1 vec<309,r64>
.data 1 [124] # 2359 1 vec<309,r64>
.data 1 [248] # 2360 1 vec<309,r64>
.data 1 [241] # 2361 1 vec<309,r64>
.data 1 [144] # 2362 1 vec<309,r64>
.data 1 [102] # 2363 1 vec<309,r64>
.data 1 [172] # 2364 1 vec<309,r64>
.data 1 [80] # 2365 1 vec<309,r64>
.data 1 [47] # 2366 1 vec<309,r64>
.data 1 [125] # 2367 1 vec<309,r64>
.data 1 [59] # 2368 1 vec<309,r64>
.data 1 [151] # 2369 1 vec<309,r64>
.data 1 [26] # 2370 1 vec<309,r64>
.data 1 [192] # 2371 1 vec<309,r64>
.data 1 [107] # 2372 1 vec<309,r64>
.data 1 [146] # 2373 1 vec<309,r64>
.data 1 [99] # 2374 1 vec<309,r64>
.data 1 [125] # 2375 1 vec<309,r64>
.data 1 [10] # 2376 1 vec<309,r64>
.data 1 [61] # 2377 1 vec<309,r64>
.data 1 [33] # 2378 1 vec<309,r64>
.data 1 [176] # 2379 1 vec<309,r64>
.data 1 [6] # 2380 1 vec<309,r64>
.data 1 [119] # 2381 1 vec<309,r64>
.data 1 [152] # 2382 1 vec<309,r64>
.data 1 [125] # 2383 1 vec<309,r64>
.data 1 [76] # 2384 1 vec<309,r64>
.data 1 [140] # 2385 1 vec<309,r64>
.data 1 [41] # 2386 1 vec<309,r64>
.data 1 [92] # 2387 1 vec<309,r64>
.data 1 [200] # 2388 1 vec<309,r64>
.data 1 [148] # 2389 1 vec<309,r64>
.data 1 [206] # 2390 1 vec<309,r64>
.data 1 [125] # 2391 1 vec<309,r64>
.data 1 [176] # 2392 1 vec<309,r64>
.data 1 [247] # 2393 1 vec<309,r64>
.data 1 [153] # 2394 1 vec<309,r64>
.data 1 [57] # 2395 1 vec<309,r64>
.data 1 [253] # 2396 1 vec<309,r64>
.data 1 [28] # 2397 1 vec<309,r64>
.data 1 [3] # 2398 1 vec<309,r64>
.data 1 [126] # 2399 1 vec<309,r64>
.data 1 [156] # 2400 1 vec<309,r64>
.data 1 [117] # 2401 1 vec<309,r64>
.data 1 [0] # 2402 1 vec<309,r64>
.data 1 [136] # 2403 1 vec<309,r64>
.data 1 [60] # 2404 1 vec<309,r64>
.data 1 [228] # 2405 1 vec<309,r64>
.data 1 [55] # 2406 1 vec<309,r64>
.data 1 [126] # 2407 1 vec<309,r64>
.data 1 [3] # 2408 1 vec<309,r64>
.data 1 [147] # 2409 1 vec<309,r64>
.data 1 [0] # 2410 1 vec<309,r64>
.data 1 [170] # 2411 1 vec<309,r64>
.data 1 [75] # 2412 1 vec<309,r64>
.data 1 [221] # 2413 1 vec<309,r64>
.data 1 [109] # 2414 1 vec<309,r64>
.data 1 [126] # 2415 1 vec<309,r64>
.data 1 [226] # 2416 1 vec<309,r64>
.data 1 [91] # 2417 1 vec<309,r64>
.data 1 [64] # 2418 1 vec<309,r64>
.data 1 [74] # 2419 1 vec<309,r64>
.data 1 [79] # 2420 1 vec<309,r64>
.data 1 [170] # 2421 1 vec<309,r64>
.data 1 [162] # 2422 1 vec<309,r64>
.data 1 [126] # 2423 1 vec<309,r64>
.data 1 [218] # 2424 1 vec<309,r64>
.data 1 [114] # 2425 1 vec<309,r64>
.data 1 [208] # 2426 1 vec<309,r64>
.data 1 [28] # 2427 1 vec<309,r64>
.data 1 [227] # 2428 1 vec<309,r64>
.data 1 [84] # 2429 1 vec<309,r64>
.data 1 [215] # 2430 1 vec<309,r64>
.data 1 [126] # 2431 1 vec<309,r64>
.data 1 [144] # 2432 1 vec<309,r64>
.data 1 [143] # 2433 1 vec<309,r64>
.data 1 [4] # 2434 1 vec<309,r64>
.data 1 [228] # 2435 1 vec<309,r64>
.data 1 [27] # 2436 1 vec<309,r64>
.data 1 [42] # 2437 1 vec<309,r64>
.data 1 [13] # 2438 1 vec<309,r64>
.data 1 [127] # 2439 1 vec<309,r64>
.data 1 [186] # 2440 1 vec<309,r64>
.data 1 [217] # 2441 1 vec<309,r64>
.data 1 [130] # 2442 1 vec<309,r64>
.data 1 [110] # 2443 1 vec<309,r64>
.data 1 [81] # 2444 1 vec<309,r64>
.data 1 [58] # 2445 1 vec<309,r64>
.data 1 [66] # 2446 1 vec<309,r64>
.data 1 [127] # 2447 1 vec<309,r64>
.data 1 [41] # 2448 1 vec<309,r64>
.data 1 [144] # 2449 1 vec<309,r64>
.data 1 [35] # 2450 1 vec<309,r64>
.data 1 [202] # 2451 1 vec<309,r64>
.data 1 [229] # 2452 1 vec<309,r64>
.data 1 [200] # 2453 1 vec<309,r64>
.data 1 [118] # 2454 1 vec<309,r64>
.data 1 [127] # 2455 1 vec<309,r64>
.data 1 [51] # 2456 1 vec<309,r64>
.data 1 [116] # 2457 1 vec<309,r64>
.data 1 [172] # 2458 1 vec<309,r64>
.data 1 [60] # 2459 1 vec<309,r64>
.data 1 [31] # 2460 1 vec<309,r64>
.data 1 [123] # 2461 1 vec<309,r64>
.data 1 [172] # 2462 1 vec<309,r64>
.data 1 [127] # 2463 1 vec<309,r64>
.data 1 [160] # 2464 1 vec<309,r64>
.data 1 [200] # 2465 1 vec<309,r64>
.data 1 [235] # 2466 1 vec<309,r64>
.data 1 [133] # 2467 1 vec<309,r64>
.data 1 [243] # 2468 1 vec<309,r64>
.data 1 [204] # 2469 1 vec<309,r64>
.data 1 [225] # 2470 1 vec<309,r64>
.data 1 [127] # 2471 1 vec<309,r64>


.fun num_real/r64_raw_mantissa NORMAL [U64] = [R64]
.bbl entry
  poparg val:R64
  bitcast bitcast:U64 = val
  and expr2:U64 = bitcast 4503599627370495:U64
  pusharg expr2
  ret


.fun num_real/r64_raw_exponent NORMAL [U64] = [R64]
.bbl entry
  poparg val:R64
  bitcast bitcast:U64 = val
  shl expr2:U64 = bitcast 1:U64
  shr expr2.1:U64 = expr2 53:U64
  pusharg expr2.1
  ret


.fun num_real/r64_is_negative NORMAL [U8] = [R64]
.bbl entry
  poparg val:R64
  bitcast bitcast:S64 = val
  ble 0:S64 bitcast br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun num_real/r64_is_nan NORMAL [U8] = [R64]
.bbl entry
  poparg val:R64
  bitcast bitcast:U64 = val
  and expr2:U64 = bitcast 4503599627370495:U64
  bne expr2 2251799813685248:U64 br_f
  bitcast bitcast.1:U64 = val
  shl expr2.1:U64 = bitcast.1 1:U64
  shr expr2.2:U64 = expr2.1 53:U64
  bne expr2.2 2047:U64 br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun num_real/r64_is_subnormal NORMAL [U8] = [R64]
.bbl entry
  poparg val:R64
  bitcast bitcast:U64 = val
  shl expr2:U64 = bitcast 1:U64
  shr expr2.1:U64 = expr2 53:U64
  bne expr2.1 0:U64 br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun num_real/r64_is_inf NORMAL [U8] = [R64]
.bbl entry
  poparg val:R64
  bitcast bitcast:U64 = val
  and expr2:U64 = bitcast 4503599627370495:U64
  bne expr2 0:U64 br_f
  bitcast bitcast.1:U64 = val
  shl expr2.1:U64 = bitcast.1 1:U64
  shr expr2.2:U64 = expr2.1 53:U64
  bne expr2.2 2047:U64 br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun num_real/make_r64 NORMAL [R64] = [U8 U64 U64]
.bbl entry
  poparg negative:U8
  poparg exponent:U64
  poparg mantissa:U64
  conv as:U64 = negative
  mov out:U64 = as
  shl expr2:U64 = out 11:U64
  mov out = expr2
  or expr2.1:U64 = out exponent
  mov out = expr2.1
  shl expr2.2:U64 = out 52:U64
  mov out = expr2.2
  or expr2.3:U64 = out mantissa
  mov out = expr2.3
  bitcast bitcast:R64 = out
  pusharg bitcast
  ret


.fun num_real/make_r32 NORMAL [R32] = [U8 U32 U32]
.bbl entry
  poparg negative:U8
  poparg raw_exp:U32
  poparg raw_mantissa:U32
  conv as:U32 = negative
  mov out:U32 = as
  shl expr2:U32 = out 8:U32
  mov out = expr2
  or expr2.1:U32 = out raw_exp
  mov out = expr2.1
  shl expr2.2:U32 = out 23:U32
  mov out = expr2.2
  or expr2.3:U32 = out raw_mantissa
  mov out = expr2.3
  bitcast bitcast:R32 = out
  pusharg bitcast
  ret

.mem fmt_real/log2_10 8 RO
.data 1 "q\xa3y\x09O\x93\n@" # 0 8 r64

.mem fmt_real/log10_2_to_52 8 RO
.data 1 ">&\x03c\x9fN/@" # 0 8 r64

.mem fmt_real/target_range_hi 8 RO
.data 1 "\x00\x00\x00\x00\x00\x00@C" # 0 8 r64

.mem fmt_real/target_range_lo 8 RO
.data 1 "\x9a\x99\x99\x99\x99\x99\x09C" # 0 8 r64


.fun fmt_real/mymemcpy NORMAL [U64] = [A64 A64 U64]
.bbl entry
  poparg dst:A64
  poparg src:A64
  poparg size:U64
  mov it%1:U64 = 0:U64
.bbl _
  blt it%1 size br_join.1
  bra _.end  # break
.bbl br_join.1
.bbl br_join
  mov i:U64 = it%1
  add expr2:U64 = it%1 1:U64
  mov it%1 = expr2
  lea new_base:A64 = dst i
  lea new_base.1:A64 = src i
  .reg U8 copy
  ld copy = new_base.1 0
  st new_base 0 = copy
  bra _  # continue
.bbl _.end
  pusharg size
  ret


.fun fmt_real/div_by_power_of_10 NORMAL [R64] = [R64 S32]
.bbl entry
  poparg val:R64
  poparg pow10:S32
  blt pow10 0:S32 br_f
  lea.mem lhsaddr:A64 = num_real/powers_of_ten 0
  conv scaled:S64 = pow10
  mul scaled = scaled 8
  lea new_base:A64 = lhsaddr scaled
  ld deref:R64 = new_base 0
  div expr2:R64 = val deref
  pusharg expr2
  ret
.bbl br_f
  lea.mem lhsaddr.1:A64 = num_real/powers_of_ten 0
  sub expr1:S32 = 0 pow10
  conv scaled.1:S64 = expr1
  mul scaled.1 = scaled.1 8
  lea new_base.1:A64 = lhsaddr.1 scaled.1
  ld deref.1:R64 = new_base.1 0
  mul expr2.1:R64 = val deref.1
  pusharg expr2.1
  ret
.bbl br_join


.fun fmt_real/find_t NORMAL [S32] = [R64]
.bbl entry
  poparg val:R64
  bitcast bitcast:U64 = val
  shl expr2:U64 = bitcast 1:U64
  shr expr2.1:U64 = expr2 53:U64
  conv as:S32 = expr2.1
  sub expr2.2:S32 = as 1023:S32
  mov biased_exp:S32 = expr2.2
  conv as.1:R64 = biased_exp
  div expr2.3:R64 = as.1 0x1.a934f0979a371p+1:R64
  sub expr2.4:R64 = 0x1.f4e9f6303263ep+3:R64 expr2.3
  conv as.2:S32 = expr2.4
  sub expr1:S32 = 0 as.2
  mov t:S32 = expr1
.bbl _
.bbl br_join
  pusharg t
  pusharg val
  bsr fmt_real/div_by_power_of_10
  poparg call:R64
  mov x:R64 = call
  blt 0x1.999999999999ap+49:R64 x br_f
  sub expr2.5:S32 = t 1:S32
  mov t = expr2.5
  bra br_join.1
.bbl br_f
  ble x 0x1.0000000000000p+53:R64 br_f.1
  add expr2.6:S32 = t 1:S32
  mov t = expr2.6
  bra br_join.2
.bbl br_f.1
  pusharg t
  ret
.bbl br_join.3
.bbl br_join.2
.bbl br_join.1
  bra _  # continue
.bbl _.end


.fun fmt_real/FmtNan NORMAL [U64] = [R64 A64]
.bbl entry
  poparg val:R64
  poparg out:A64
  bitcast bitcast:U64 = val
  and expr2:U64 = bitcast 4503599627370495:U64
  mov mantissa:U64 = expr2
  .reg U8 expr
  bitcast bitcast.1:S64 = val
  ble 0:S64 bitcast.1 br_f
  mov expr = 1:U8
  bra end_expr
.bbl br_f
  mov expr = 0:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  mov is_negative:U8 = expr
  ld pointer:A64 = out 0
  beq is_negative 0 br_f.1
  st pointer 0 = 45:U8
  bra end_expr.1
.bbl br_f.1
  st pointer 0 = 43:U8
  bra end_expr.1
.bbl br_join.1
.bbl end_expr.1
  bne mantissa 0:U64 br_f.2
  .reg U64 expr.1
  .stk e_slice%1 8 16
  lea.stk var_stk_base:A64 e_slice%1 0
  lea.mem lhsaddr:A64 = $gen/global_val_1 0
  st var_stk_base 0 = lhsaddr
  st var_stk_base 8 = 3:U64
  .stk e_out%1 8 16
  lea.stk var_stk_base.1:A64 e_out%1 0
  ld length:U64 = out 8
  mov orig_len%1:U64 = length
  ble 1:U64 orig_len%1 br_join.3
  trap
.bbl br_join.3
  ld pointer.1:A64 = out 0
  lea at:A64 = pointer.1 1
  st var_stk_base.1 0 = at
  sub expr2.1:U64 = orig_len%1 1:U64
  st var_stk_base.1 8 = expr2.1
  bra end_expr.3
.bbl end_expr.3
  lea.stk lhsaddr.1:A64 = e_out%1 0
  ld length.1:U64 = lhsaddr.1 8
  ble 3:U64 length.1 br_join.4
  trap
.bbl br_join.4
  mov it%1:U64 = 0:U64
.bbl _
  blt it%1 3:U64 br_join.6
  bra _.end  # break
.bbl br_join.6
.bbl br_join.5
  mov i:U64 = it%1
  add expr2.2:U64 = it%1 1:U64
  mov it%1 = expr2.2
  lea.stk lhsaddr.2:A64 = e_out%1 0
  ld pointer.2:A64 = lhsaddr.2 0
  lea new_base:A64 = pointer.2 i
  lea.stk lhsaddr.3:A64 = e_slice%1 0
  ld pointer.3:A64 = lhsaddr.3 0
  lea new_base.1:A64 = pointer.3 i
  .reg U8 copy
  ld copy = new_base.1 0
  st new_base 0 = copy
  bra _  # continue
.bbl _.end
  mov expr.1 = 3:U64
  bra end_expr.2
.bbl end_expr.2
  add expr2.3:U64 = 1:U64 expr.1
  pusharg expr2.3
  ret
.bbl br_f.2
  bne mantissa 2251799813685248:U64 br_join.7
  .reg U64 expr.2
  .stk e_slice%2 8 16
  lea.stk var_stk_base.2:A64 e_slice%2 0
  lea.mem lhsaddr.4:A64 = $gen/global_val_2 0
  st var_stk_base.2 0 = lhsaddr.4
  st var_stk_base.2 8 = 3:U64
  .stk e_out%2 8 16
  lea.stk var_stk_base.3:A64 e_out%2 0
  ld length.2:U64 = out 8
  mov orig_len%2:U64 = length.2
  ble 1:U64 orig_len%2 br_join.8
  trap
.bbl br_join.8
  ld pointer.4:A64 = out 0
  lea at.1:A64 = pointer.4 1
  st var_stk_base.3 0 = at.1
  sub expr2.4:U64 = orig_len%2 1:U64
  st var_stk_base.3 8 = expr2.4
  bra end_expr.5
.bbl end_expr.5
  lea.stk lhsaddr.5:A64 = e_out%2 0
  ld length.3:U64 = lhsaddr.5 8
  ble 3:U64 length.3 br_join.9
  trap
.bbl br_join.9
  mov it%2:U64 = 0:U64
.bbl _.1
  blt it%2 3:U64 br_join.11
  bra _.1.end  # break
.bbl br_join.11
.bbl br_join.10
  mov i.1:U64 = it%2
  add expr2.5:U64 = it%2 1:U64
  mov it%2 = expr2.5
  lea.stk lhsaddr.6:A64 = e_out%2 0
  ld pointer.5:A64 = lhsaddr.6 0
  lea new_base.2:A64 = pointer.5 i.1
  lea.stk lhsaddr.7:A64 = e_slice%2 0
  ld pointer.6:A64 = lhsaddr.7 0
  lea new_base.3:A64 = pointer.6 i.1
  .reg U8 copy.1
  ld copy.1 = new_base.3 0
  st new_base.2 0 = copy.1
  bra _.1  # continue
.bbl _.1.end
  mov expr.2 = 3:U64
  bra end_expr.4
.bbl end_expr.4
  add expr2.6:U64 = 1:U64 expr.2
  pusharg expr2.6
  ret
.bbl br_join.7
.bbl br_join.2
  pusharg 0:U64
  ret


.fun fmt_real/FmtExponentE NORMAL [U64] = [S32 A64]
.bbl entry
  poparg exp:S32
  poparg out:A64
  ld length:U64 = out 8
  ble 4:U64 length br_join
  pusharg 0:U64
  ret
.bbl br_join
  mov i:U64 = 2:U64
  ld pointer:A64 = out 0
  st pointer 0 = 101:U8
  ble 0:S32 exp br_f
  ld pointer.1:A64 = out 0
  lea at:A64 = pointer.1 1
  st at 0 = 45:U8
  blt exp -9:S32 br_join.2
  ld pointer.2:A64 = out 0
  lea at.1:A64 = pointer.2 2
  st at.1 0 = 48:U8
  add expr2:U64 = i 1:U64
  mov i = expr2
.bbl br_join.2
  .reg U64 expr
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  ld length.1:U64 = out 8
  mov orig_len%1:U64 = length.1
  mov orig_size%1:U64 = i
  ble orig_size%1 orig_len%1 br_join.3
  trap
.bbl br_join.3
  ld pointer.3:A64 = out 0
  lea new_base:A64 = pointer.3 orig_size%1
  st var_stk_base 0 = new_base
  sub expr2.1:U64 = orig_len%1 orig_size%1
  st var_stk_base 8 = expr2.1
  bra end_expr.1
.bbl end_expr.1
  sub expr1:S32 = 0 exp
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg expr1
  bsr fmt_int/FmtDec<s32>
  poparg call:U64
  mov expr = call
  bra end_expr
.bbl end_expr
  add expr2.2:U64 = i expr
  pusharg expr2.2
  ret
.bbl br_f
  ld pointer.4:A64 = out 0
  lea at.2:A64 = pointer.4 1
  st at.2 0 = 43:U8
  blt 9:S32 exp br_join.4
  ld pointer.5:A64 = out 0
  lea at.3:A64 = pointer.5 2
  st at.3 0 = 48:U8
  add expr2.3:U64 = i 1:U64
  mov i = expr2.3
.bbl br_join.4
  .reg U64 expr.1
  .stk arg1.1 8 16
  lea.stk var_stk_base.1:A64 arg1.1 0
  ld length.2:U64 = out 8
  mov orig_len%2:U64 = length.2
  mov orig_size%2:U64 = i
  ble orig_size%2 orig_len%2 br_join.5
  trap
.bbl br_join.5
  ld pointer.6:A64 = out 0
  lea new_base.1:A64 = pointer.6 orig_size%2
  st var_stk_base.1 0 = new_base.1
  sub expr2.4:U64 = orig_len%2 orig_size%2
  st var_stk_base.1 8 = expr2.4
  bra end_expr.3
.bbl end_expr.3
  lea.stk lhsaddr.1:A64 = arg1.1 0
  pusharg lhsaddr.1
  pusharg exp
  bsr fmt_int/FmtDec<s32>
  poparg call.1:U64
  mov expr.1 = call.1
  bra end_expr.2
.bbl end_expr.2
  add expr2.5:U64 = i expr.1
  pusharg expr2.5
  ret
.bbl br_join.1


.fun fmt_real/FmtSign NORMAL [U64] = [U8 U8 A64]
.bbl entry
  poparg is_negative:U8
  poparg force_sign:U8
  poparg out:A64
  beq is_negative 0 br_f
  ld pointer:A64 = out 0
  st pointer 0 = 45:U8
  pusharg 1:U64
  ret
.bbl br_f
  beq force_sign 0 br_f.1
  ld pointer.1:A64 = out 0
  st pointer.1 0 = 43:U8
  pusharg 1:U64
  ret
.bbl br_f.1
  pusharg 0:U64
  ret
.bbl br_join.2
.bbl br_join.1
.bbl br_join


.fun fmt_real/FmtMantissaE NORMAL [U64] = [A64 U64 A64]
.bbl entry
  poparg digits:A64
  poparg precision:U64
  poparg out:A64
  ld length:U64 = digits 8
  mov num_digits:U64 = length
  ld pointer:A64 = out 0
  ld pointer.1:A64 = digits 0
  .reg U8 copy
  ld copy = pointer.1 0
  st pointer 0 = copy
  ld pointer.2:A64 = out 0
  lea at:A64 = pointer.2 1
  st at 0 = 46:U8
  add expr2:U64 = precision 1:U64
  mov end_eval%1:U64 = expr2
  mov it%1:U64 = 1:U64
.bbl _
  blt it%1 end_eval%1 br_join.1
  bra _.end  # break
.bbl br_join.1
.bbl br_join
  mov j:U64 = it%1
  add expr2.1:U64 = it%1 1:U64
  mov it%1 = expr2.1
  ble num_digits j br_f
  ld pointer.3:A64 = out 0
  add expr2.2:U64 = j 1:U64
  lea new_base:A64 = pointer.3 expr2.2
  ld pointer.4:A64 = digits 0
  lea new_base.1:A64 = pointer.4 j
  .reg U8 copy.1
  ld copy.1 = new_base.1 0
  st new_base 0 = copy.1
  bra br_join.2
.bbl br_f
  ld pointer.5:A64 = out 0
  add expr2.3:U64 = j 1:U64
  lea new_base.2:A64 = pointer.5 expr2.3
  st new_base.2 0 = 48:U8
.bbl br_join.2
  bra _  # continue
.bbl _.end
  add expr2.4:U64 = precision 2:U64
  pusharg expr2.4
  ret


.fun fmt_real/RoundDigitsUp NORMAL [S32] = [A64]
.bbl entry
  poparg digits:A64
  ld length:U64 = digits 8
  mov end_eval%1:U64 = length
  mov it%1:U64 = 0:U64
.bbl _
  blt it%1 end_eval%1 br_join.1
  bra _.end  # break
.bbl br_join.1
.bbl br_join
  mov pos:U64 = it%1
  add expr2:U64 = it%1 1:U64
  mov it%1 = expr2
  ld length.1:U64 = digits 8
  sub expr2.1:U64 = length.1 pos
  sub expr2.2:U64 = expr2.1 1:U64
  mov i:U64 = expr2.2
  ld pointer:A64 = digits 0
  lea new_base:A64 = pointer i
  ld deref:U8 = new_base 0
  bne deref 57:U8 br_f
  ld pointer.1:A64 = digits 0
  lea new_base.1:A64 = pointer.1 i
  st new_base.1 0 = 48:U8
  bra br_join.2
.bbl br_f
  ld pointer.2:A64 = digits 0
  lea new_base.2:A64 = pointer.2 i
  mov deref_assign:A64 = new_base.2
  ld deref.1:U8 = deref_assign 0
  add expr2.3:U8 = deref.1 1:U8
  st deref_assign 0 = expr2.3
  pusharg 0:S32
  ret
.bbl br_join.2
  bra _  # continue
.bbl _.end
  ld length.2:U64 = digits 8
  sub expr2.4:U64 = length.2 1:U64
  mov end_eval%2:U64 = expr2.4
  mov it%2:U64 = 0:U64
.bbl _.1
  blt it%2 end_eval%2 br_join.4
  bra _.1.end  # break
.bbl br_join.4
.bbl br_join.3
  mov pos.1:U64 = it%2
  add expr2.5:U64 = it%2 1:U64
  mov it%2 = expr2.5
  ld length.3:U64 = digits 8
  sub expr2.6:U64 = length.3 pos.1
  sub expr2.7:U64 = expr2.6 1:U64
  mov i.1:U64 = expr2.7
  ld pointer.3:A64 = digits 0
  lea new_base.3:A64 = pointer.3 i.1
  ld pointer.4:A64 = digits 0
  sub expr2.8:U64 = i.1 1:U64
  lea new_base.4:A64 = pointer.4 expr2.8
  .reg U8 copy
  ld copy = new_base.4 0
  st new_base.3 0 = copy
  bra _.1  # continue
.bbl _.1.end
  ld pointer.5:A64 = digits 0
  st pointer.5 0 = 49:U8
  pusharg 1:S32
  ret


.fun fmt_real/FmtE<r64> NORMAL [U64] = [R64 U64 U8 A64]
.bbl entry
  poparg val:R64
  poparg precision:U64
  poparg force_sign:U8
  poparg out:A64
  .reg U8 expr
  bitcast bitcast:S64 = val
  ble 0:S64 bitcast br_f
  mov expr = 1:U8
  bra end_expr
.bbl br_f
  mov expr = 0:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  mov is_negative:U8 = expr
  .stk buffer 1 32
  ld length:U64 = out 8
  add expr2:U64 = precision 8:U64
  ble expr2 length br_join.1
  pusharg 0:U64
  ret
.bbl br_join.1
  add expr2.1:U64 = precision 1:U64
  ble expr2.1 32:U64 br_join.2
  pusharg 0:U64
  ret
.bbl br_join.2
  bitcast bitcast.1:U64 = val
  shl expr2.2:U64 = bitcast.1 1:U64
  shr expr2.3:U64 = expr2.2 53:U64
  bne expr2.3 0:U64 br_join.3
  bitcast bitcast.2:U64 = val
  and expr2.4:U64 = bitcast.2 4503599627370495:U64
  bne expr2.4 0:U64 br_join.4
  lea.stk lhsaddr:A64 = buffer 0
  st lhsaddr 0 = 48:U8
  mov i:U64 = 0:U64
  .reg U64 expr.1
  .stk arg2 8 16
  lea.stk var_stk_base:A64 arg2 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr.1:A64 = arg2 0
  pusharg lhsaddr.1
  pusharg force_sign
  pusharg is_negative
  bsr fmt_real/FmtSign
  poparg call:U64
  mov expr.1 = call
  bra end_expr.1
.bbl end_expr.1
  add expr2.5:U64 = i expr.1
  mov i = expr2.5
  .reg U64 expr.2
  .stk arg0 8 16
  lea.stk var_stk_base.1:A64 arg0 0
  lea.stk lhsaddr.2:A64 = buffer 0
  st var_stk_base.1 0 = lhsaddr.2
  st var_stk_base.1 8 = 1:U64
  .stk arg2.1 8 16
  lea.stk var_stk_base.2:A64 arg2.1 0
  ld length.1:U64 = out 8
  mov orig_len%1:U64 = length.1
  mov orig_size%1:U64 = i
  ble orig_size%1 orig_len%1 br_join.5
  trap
.bbl br_join.5
  ld pointer:A64 = out 0
  lea new_base:A64 = pointer orig_size%1
  st var_stk_base.2 0 = new_base
  sub expr2.6:U64 = orig_len%1 orig_size%1
  st var_stk_base.2 8 = expr2.6
  bra end_expr.3
.bbl end_expr.3
  lea.stk lhsaddr.3:A64 = arg0 0
  lea.stk lhsaddr.4:A64 = arg2.1 0
  pusharg lhsaddr.4
  pusharg precision
  pusharg lhsaddr.3
  bsr fmt_real/FmtMantissaE
  poparg call.1:U64
  mov expr.2 = call.1
  bra end_expr.2
.bbl end_expr.2
  add expr2.7:U64 = i expr.2
  mov i = expr2.7
  .reg U64 expr.3
  .stk arg1 8 16
  lea.stk var_stk_base.3:A64 arg1 0
  ld length.2:U64 = out 8
  mov orig_len%2:U64 = length.2
  mov orig_size%2:U64 = i
  ble orig_size%2 orig_len%2 br_join.6
  trap
.bbl br_join.6
  ld pointer.1:A64 = out 0
  lea new_base.1:A64 = pointer.1 orig_size%2
  st var_stk_base.3 0 = new_base.1
  sub expr2.8:U64 = orig_len%2 orig_size%2
  st var_stk_base.3 8 = expr2.8
  bra end_expr.5
.bbl end_expr.5
  lea.stk lhsaddr.5:A64 = arg1 0
  pusharg lhsaddr.5
  pusharg 0:S32
  bsr fmt_real/FmtExponentE
  poparg call.2:U64
  mov expr.3 = call.2
  bra end_expr.4
.bbl end_expr.4
  add expr2.9:U64 = i expr.3
  mov i = expr2.9
  pusharg i
  ret
.bbl br_join.4
  pusharg 0:U64
  ret
.bbl br_join.3
  bitcast bitcast.3:U64 = val
  shl expr2.10:U64 = bitcast.3 1:U64
  shr expr2.11:U64 = expr2.10 53:U64
  bne expr2.11 2047:U64 br_join.7
  .stk arg1.1 8 16
  lea.stk var_stk_base.4:A64 arg1.1 0
  .reg U64 copy.1
  ld copy.1 = out 0
  st var_stk_base.4 0 = copy.1
  ld copy.1 = out 8
  st var_stk_base.4 8 = copy.1
  lea.stk lhsaddr.6:A64 = arg1.1 0
  pusharg lhsaddr.6
  pusharg val
  bsr fmt_real/FmtNan
  poparg call.3:U64
  pusharg call.3
  ret
.bbl br_join.7
  sub expr1:R64 = 0 val
  cmplt expr1 = expr1 val val 0
  pusharg expr1
  bsr fmt_real/find_t
  poparg call.4:S32
  mov t:S32 = call.4
  pusharg t
  pusharg val
  bsr fmt_real/div_by_power_of_10
  poparg call.5:R64
  mov x:R64 = call.5
  bitcast bitcast.4:U64 = x
  and expr2.12:U64 = bitcast.4 4503599627370495:U64
  add expr2.13:U64 = expr2.12 4503599627370496:U64
  mov mantissa:U64 = expr2.13
  bitcast bitcast.5:U64 = x
  shl expr2.14:U64 = bitcast.5 1:U64
  shr expr2.15:U64 = expr2.14 53:U64
  conv as:S32 = expr2.15
  sub expr2.16:S32 = as 1023:S32
  mov exponent:S32 = expr2.16
  blt exponent 49:S32 br_failed_and
  ble exponent 52:S32 br_join.8
.bbl br_failed_and
  .stk e_cond%1 8 16
  lea.stk var_stk_base.5:A64 e_cond%1 0
  lea.mem lhsaddr.7:A64 = $gen/global_val_3 0
  st var_stk_base.5 0 = lhsaddr.7
  st var_stk_base.5 8 = 5:U64
  .stk e_text%1 8 16
  lea.stk var_stk_base.6:A64 e_text%1 0
  lea.mem lhsaddr.8:A64 = $gen/global_val_4 0
  st var_stk_base.6 0 = lhsaddr.8
  st var_stk_base.6 8 = 14:U64
  lea.stk lhsaddr.9:A64 = e_cond%1 0
  ld pointer.2:A64 = lhsaddr.9 0
  pusharg 5:U64
  pusharg pointer.2
  bsr print_ln
  lea.stk lhsaddr.10:A64 = e_text%1 0
  ld pointer.3:A64 = lhsaddr.10 0
  pusharg 14:U64
  pusharg pointer.3
  bsr print_ln
  trap
.bbl br_join.8
  beq exponent 52:S32 br_join.9
  sub expr2.17:S32 = t 1:S32
  mov t = expr2.17
  mul expr2.18:U64 = mantissa 10:U64
  mov mantissa = expr2.18
  sub expr2.19:S32 = 52:S32 exponent
  conv as.1:U64 = expr2.19
  shr expr2.20:U64 = mantissa as.1
  mov mantissa = expr2.20
.bbl br_join.9
  .reg U64 expr.4
  .stk arg1.2 8 16
  lea.stk var_stk_base.7:A64 arg1.2 0
  lea.stk lhsaddr.11:A64 = buffer 0
  st var_stk_base.7 0 = lhsaddr.11
  st var_stk_base.7 8 = 32:U64
  lea.stk lhsaddr.12:A64 = arg1.2 0
  pusharg lhsaddr.12
  pusharg mantissa
  bsr fmt_int/FmtDec<u64>
  poparg call.6:U64
  mov expr.4 = call.6
  bra end_expr.6
.bbl end_expr.6
  mov num_digits:U64 = expr.4
  add expr2.21:U64 = precision 1:U64
  ble num_digits expr2.21 br_join.10
  lea.stk lhsaddr.13:A64 = buffer 0
  add expr2.22:U64 = precision 2:U64
  lea new_base.2:A64 = lhsaddr.13 expr2.22
  ld deref:U8 = new_base.2 0
  blt deref 53:U8 br_join.10
  .reg S32 expr.5
  .stk arg0.1 8 16
  lea.stk var_stk_base.8:A64 arg0.1 0
  lea.stk lhsaddr.14:A64 = buffer 0
  st var_stk_base.8 0 = lhsaddr.14
  add expr2.23:U64 = precision 1:U64
  st var_stk_base.8 8 = expr2.23
  lea.stk lhsaddr.15:A64 = arg0.1 0
  pusharg lhsaddr.15
  bsr fmt_real/RoundDigitsUp
  poparg call.7:S32
  mov expr.5 = call.7
  bra end_expr.7
.bbl end_expr.7
  add expr2.24:S32 = t expr.5
  mov t = expr2.24
.bbl br_join.10
  sub expr2.25:U64 = num_digits 1:U64
  conv as.2:S32 = expr2.25
  add expr2.26:S32 = t as.2
  mov t = expr2.26
  mov i.1:U64 = 0:U64
  .reg U64 expr.6
  .stk arg2.2 8 16
  lea.stk var_stk_base.9:A64 arg2.2 0
  .reg U64 copy.2
  ld copy.2 = out 0
  st var_stk_base.9 0 = copy.2
  ld copy.2 = out 8
  st var_stk_base.9 8 = copy.2
  lea.stk lhsaddr.16:A64 = arg2.2 0
  pusharg lhsaddr.16
  pusharg force_sign
  pusharg is_negative
  bsr fmt_real/FmtSign
  poparg call.8:U64
  mov expr.6 = call.8
  bra end_expr.8
.bbl end_expr.8
  add expr2.27:U64 = i.1 expr.6
  mov i.1 = expr2.27
  .reg U64 expr.7
  .stk arg0.2 8 16
  lea.stk var_stk_base.10:A64 arg0.2 0
  lea.stk lhsaddr.17:A64 = buffer 0
  st var_stk_base.10 0 = lhsaddr.17
  st var_stk_base.10 8 = num_digits
  .stk arg2.3 8 16
  lea.stk var_stk_base.11:A64 arg2.3 0
  ld length.3:U64 = out 8
  mov orig_len%3:U64 = length.3
  mov orig_size%3:U64 = i.1
  ble orig_size%3 orig_len%3 br_join.11
  trap
.bbl br_join.11
  ld pointer.4:A64 = out 0
  lea new_base.3:A64 = pointer.4 orig_size%3
  st var_stk_base.11 0 = new_base.3
  sub expr2.28:U64 = orig_len%3 orig_size%3
  st var_stk_base.11 8 = expr2.28
  bra end_expr.10
.bbl end_expr.10
  lea.stk lhsaddr.18:A64 = arg0.2 0
  lea.stk lhsaddr.19:A64 = arg2.3 0
  pusharg lhsaddr.19
  pusharg precision
  pusharg lhsaddr.18
  bsr fmt_real/FmtMantissaE
  poparg call.9:U64
  mov expr.7 = call.9
  bra end_expr.9
.bbl end_expr.9
  add expr2.29:U64 = i.1 expr.7
  mov i.1 = expr2.29
  .reg U64 expr.8
  .stk arg1.3 8 16
  lea.stk var_stk_base.12:A64 arg1.3 0
  ld length.4:U64 = out 8
  mov orig_len%4:U64 = length.4
  mov orig_size%4:U64 = i.1
  ble orig_size%4 orig_len%4 br_join.12
  trap
.bbl br_join.12
  ld pointer.5:A64 = out 0
  lea new_base.4:A64 = pointer.5 orig_size%4
  st var_stk_base.12 0 = new_base.4
  sub expr2.30:U64 = orig_len%4 orig_size%4
  st var_stk_base.12 8 = expr2.30
  bra end_expr.12
.bbl end_expr.12
  lea.stk lhsaddr.20:A64 = arg1.3 0
  pusharg lhsaddr.20
  pusharg t
  bsr fmt_real/FmtExponentE
  poparg call.10:U64
  mov expr.8 = call.10
  bra end_expr.11
.bbl end_expr.11
  add expr2.31:U64 = i.1 expr.8
  mov i.1 = expr2.31
  pusharg i.1
  ret


.fun fmt_real/to_hex_digit NORMAL [U8] = [U8]
.bbl entry
  poparg digit:U8
  add expr2:U8 = digit 48:U8
  mov expr3_t:U8 = expr2
  add expr2.1:U8 = digit 87:U8
  mov expr3_f:U8 = expr2.1
  blt 9:U8 digit br_f
  pusharg expr3_t
  ret
.bbl br_f
  pusharg expr3_f
  ret
.bbl br_join


.fun fmt_real/FmtMantissaHex NORMAL [U64] = [U64 U8 A64]
.bbl entry
  poparg frac_bits:U64
  poparg is_denorm:U8
  poparg out:A64
  ld pointer:A64 = out 0
  st pointer 0 = 48:U8
  ld pointer.1:A64 = out 0
  lea at:A64 = pointer.1 1
  st at 0 = 120:U8
  ld pointer.2:A64 = out 0
  lea at.1:A64 = pointer.2 2
  beq is_denorm 0 br_f
  st at.1 0 = 48:U8
  bra end_expr
.bbl br_f
  st at.1 0 = 49:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  ld pointer.3:A64 = out 0
  lea at.2:A64 = pointer.3 3
  st at.2 0 = 46:U8
  mov bits:U64 = frac_bits
  mov i:U64 = 4:U64
.bbl _
  bne bits 0:U64 br_join.1
  bra _.end  # break
.bbl br_join.1
  ld pointer.4:A64 = out 0
  lea new_base:A64 = pointer.4 i
  shr expr2:U64 = bits 48:U64
  conv as:U8 = expr2
  mov inl_arg:U8 = as
  add expr2.1:U8 = inl_arg 48:U8
  mov expr3_t:U8 = expr2.1
  add expr2.2:U8 = inl_arg 87:U8
  mov expr3_f:U8 = expr2.2
  blt 9:U8 inl_arg br_f.1
  st new_base 0 = expr3_t
  bra end_expr.1
.bbl br_f.1
  st new_base 0 = expr3_f
  bra end_expr.1
.bbl br_join.2
.bbl end_expr.1
  add expr2.3:U64 = i 1:U64
  mov i = expr2.3
  and expr2.4:U64 = bits 281474976710655:U64
  mov bits = expr2.4
  shl expr2.5:U64 = bits 4:U64
  mov bits = expr2.5
  bra _  # continue
.bbl _.end
  pusharg i
  ret


.fun fmt_real/FmtExponentHex NORMAL [U64] = [U64 U8 A64]
.bbl entry
  poparg raw_exponent:U64
  poparg is_potential_zero:U8
  poparg out:A64
  conv as:S32 = raw_exponent
  mov exp:S32 = as
  bne raw_exponent 0:U64 br_f
  .reg S32 expr
  beq is_potential_zero 0 br_f.1
  mov expr = 0:S32
  bra end_expr
.bbl br_f.1
  mov expr = -1022:S32
  bra end_expr
.bbl br_join.1
.bbl end_expr
  mov exp = expr
  bra br_join
.bbl br_f
  sub expr2:S32 = exp 1023:S32
  mov exp = expr2
.bbl br_join
  ld pointer:A64 = out 0
  st pointer 0 = 112:U8
  ble 0:S32 exp br_f.2
  ld pointer.1:A64 = out 0
  lea at:A64 = pointer.1 1
  st at 0 = 45:U8
  sub expr1:S32 = 0 exp
  mov exp = expr1
  bra br_join.2
.bbl br_f.2
  ld pointer.2:A64 = out 0
  lea at.1:A64 = pointer.2 1
  st at.1 0 = 43:U8
.bbl br_join.2
  .reg U64 expr.1
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  ld length:U64 = out 8
  mov orig_len%1:U64 = length
  ble 2:U64 orig_len%1 br_join.3
  trap
.bbl br_join.3
  ld pointer.3:A64 = out 0
  lea at.2:A64 = pointer.3 2
  st var_stk_base 0 = at.2
  sub expr2.1:U64 = orig_len%1 2:U64
  st var_stk_base 8 = expr2.1
  bra end_expr.2
.bbl end_expr.2
  conv as.1:U32 = exp
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg as.1
  bsr fmt_int/FmtDec<u32>
  poparg call:U64
  mov expr.1 = call
  bra end_expr.1
.bbl end_expr.1
  add expr2.2:U64 = 2:U64 expr.1
  pusharg expr2.2
  ret


.fun fmt_real/FmtHex<r64> NORMAL [U64] = [R64 A64]
.bbl entry
  poparg val:R64
  poparg out:A64
  bitcast bitcast:U64 = val
  and expr2:U64 = bitcast 4503599627370495:U64
  mov frac_bits:U64 = expr2
  .reg U8 expr
  bitcast bitcast.1:S64 = val
  ble 0:S64 bitcast.1 br_f
  mov expr = 1:U8
  bra end_expr
.bbl br_f
  mov expr = 0:U8
  bra end_expr
.bbl br_join
.bbl end_expr
  mov is_negative:U8 = expr
  bitcast bitcast.2:U64 = val
  shl expr2.1:U64 = bitcast.2 1:U64
  shr expr2.2:U64 = expr2.1 53:U64
  mov raw_exponent:U64 = expr2.2
  bne raw_exponent 2047:U64 br_join.1
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg val
  bsr fmt_real/FmtNan
  poparg call:U64
  pusharg call
  ret
.bbl br_join.1
  mov i:U64 = 0:U64
  beq is_negative 0 br_join.2
  ld pointer:A64 = out 0
  lea new_base:A64 = pointer i
  st new_base 0 = 45:U8
  add expr2.3:U64 = i 1:U64
  mov i = expr2.3
.bbl br_join.2
  .reg U64 expr.1
  .stk arg2 8 16
  lea.stk var_stk_base.1:A64 arg2 0
  ld length:U64 = out 8
  mov orig_len%1:U64 = length
  mov orig_size%1:U64 = i
  ble orig_size%1 orig_len%1 br_join.3
  trap
.bbl br_join.3
  ld pointer.1:A64 = out 0
  lea new_base.1:A64 = pointer.1 orig_size%1
  st var_stk_base.1 0 = new_base.1
  sub expr2.4:U64 = orig_len%1 orig_size%1
  st var_stk_base.1 8 = expr2.4
  bra end_expr.2
.bbl end_expr.2
  .reg U8 expr.2
  bne raw_exponent 0:U64 br_f.1
  mov expr.2 = 1:U8
  bra end_expr.3
.bbl br_f.1
  mov expr.2 = 0:U8
  bra end_expr.3
.bbl br_join.4
.bbl end_expr.3
  lea.stk lhsaddr.1:A64 = arg2 0
  pusharg lhsaddr.1
  pusharg expr.2
  pusharg frac_bits
  bsr fmt_real/FmtMantissaHex
  poparg call.1:U64
  mov expr.1 = call.1
  bra end_expr.1
.bbl end_expr.1
  add expr2.5:U64 = i expr.1
  mov i = expr2.5
  .reg U64 expr.3
  .stk arg2.1 8 16
  lea.stk var_stk_base.2:A64 arg2.1 0
  ld length.1:U64 = out 8
  mov orig_len%2:U64 = length.1
  mov orig_size%2:U64 = i
  ble orig_size%2 orig_len%2 br_join.5
  trap
.bbl br_join.5
  ld pointer.2:A64 = out 0
  lea new_base.2:A64 = pointer.2 orig_size%2
  st var_stk_base.2 0 = new_base.2
  sub expr2.6:U64 = orig_len%2 orig_size%2
  st var_stk_base.2 8 = expr2.6
  bra end_expr.5
.bbl end_expr.5
  .reg U8 expr.4
  bne frac_bits 0:U64 br_f.2
  mov expr.4 = 1:U8
  bra end_expr.6
.bbl br_f.2
  mov expr.4 = 0:U8
  bra end_expr.6
.bbl br_join.6
.bbl end_expr.6
  lea.stk lhsaddr.2:A64 = arg2.1 0
  pusharg lhsaddr.2
  pusharg expr.4
  pusharg raw_exponent
  bsr fmt_real/FmtExponentHex
  poparg call.2:U64
  mov expr.3 = call.2
  bra end_expr.4
.bbl end_expr.4
  add expr2.7:U64 = i expr.3
  mov i = expr2.7
  pusharg i
  ret

.mem os/EPERM 4 RO
.data 4 [255] # 0 4 wrapped<os/Error>

.mem os/ENOENT 4 RO
.data 1 "\xfe\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ESRCH 4 RO
.data 1 "\xfd\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EINTR 4 RO
.data 1 "\xfc\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EIO 4 RO
.data 1 "\xfb\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENXIO 4 RO
.data 1 "\xfa\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/E2BIG 4 RO
.data 1 "\xf9\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOEXEC 4 RO
.data 1 "\xf8\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EBADF 4 RO
.data 1 "\xf7\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ECHILD 4 RO
.data 1 "\xf6\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EAGAIN 4 RO
.data 1 "\xf5\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOMEM 4 RO
.data 1 "\xf4\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EACCES 4 RO
.data 1 "\xf3\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EFAULT 4 RO
.data 1 "\xf2\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOTBLK 4 RO
.data 1 "\xf1\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EBUSY 4 RO
.data 1 "\xf0\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EEXIST 4 RO
.data 1 "\xef\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EXDEV 4 RO
.data 1 "\xee\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENODEV 4 RO
.data 1 "\xed\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOTDIR 4 RO
.data 1 "\xec\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EISDIR 4 RO
.data 1 "\xeb\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EINVAL 4 RO
.data 1 "\xea\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENFILE 4 RO
.data 1 "\xe9\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EMFILE 4 RO
.data 1 "\xe8\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOTTY 4 RO
.data 1 "\xe7\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ETXTBSY 4 RO
.data 1 "\xe6\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EFBIG 4 RO
.data 1 "\xe5\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOSPC 4 RO
.data 1 "\xe4\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ESPIPE 4 RO
.data 1 "\xe3\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EROFS 4 RO
.data 1 "\xe2\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EMLINK 4 RO
.data 1 "\xe1\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EPIPE 4 RO
.data 1 "\xe0\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EDOM 4 RO
.data 1 "\xdf\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ERANGE 4 RO
.data 1 "\xde\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EDEADLK 4 RO
.data 1 "\xdd\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENAMETOOLONG 4 RO
.data 1 "\xdc\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOLCK 4 RO
.data 1 "\xdb\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOSYS 4 RO
.data 1 "\xda\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOTEMPTY 4 RO
.data 1 "\xd9\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ELOOP 4 RO
.data 1 "\xd8\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOMSG 4 RO
.data 1 "\xd6\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EIDRM 4 RO
.data 1 "\xd5\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ECHRNG 4 RO
.data 1 "\xd4\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EL2NSYNC 4 RO
.data 1 "\xd3\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EL3HLT 4 RO
.data 1 "\xd2\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EL3RST 4 RO
.data 1 "\xd1\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ELNRNG 4 RO
.data 1 "\xd0\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EUNATCH 4 RO
.data 1 "\xcf\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOCSI 4 RO
.data 1 "\xce\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EL2HLT 4 RO
.data 1 "\xcd\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EBADE 4 RO
.data 1 "\xcc\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EBADR 4 RO
.data 1 "\xcb\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EXFULL 4 RO
.data 1 "\xca\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOANO 4 RO
.data 1 "\xc9\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EBADRQC 4 RO
.data 1 "\xc8\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EBADSLT 4 RO
.data 1 "\xc7\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EBFONT 4 RO
.data 1 "\xc5\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOSTR 4 RO
.data 1 "\xc4\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENODATA 4 RO
.data 1 "\xc3\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ETIME 4 RO
.data 1 "\xc2\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOSR 4 RO
.data 1 "\xc1\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENONET 4 RO
.data 1 "\xc0\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOPKG 4 RO
.data 1 "\xbf\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EREMOTE 4 RO
.data 1 "\xbe\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOLINK 4 RO
.data 1 "\xbd\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EADV 4 RO
.data 1 "\xbc\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ESRMNT 4 RO
.data 1 "\xbb\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ECOMM 4 RO
.data 1 "\xba\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EPROTO 4 RO
.data 1 "\xb9\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EMULTIHOP 4 RO
.data 1 "\xb8\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EDOTDOT 4 RO
.data 1 "\xb7\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EBADMSG 4 RO
.data 1 "\xb6\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EOVERFLOW 4 RO
.data 1 "\xb5\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOTUNIQ 4 RO
.data 1 "\xb4\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EBADFD 4 RO
.data 1 "\xb3\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EREMCHG 4 RO
.data 1 "\xb2\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ELIBACC 4 RO
.data 1 "\xb1\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ELIBBAD 4 RO
.data 1 "\xb0\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ELIBSCN 4 RO
.data 1 "\xaf\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ELIBMAX 4 RO
.data 1 "\xae\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ELIBEXEC 4 RO
.data 1 "\xad\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EILSEQ 4 RO
.data 1 "\xac\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ERESTART 4 RO
.data 1 "\xab\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ESTRPIPE 4 RO
.data 1 "\xaa\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EUSERS 4 RO
.data 1 "\xa9\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOTSOCK 4 RO
.data 1 "\xa8\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EDESTADDRREQ 4 RO
.data 1 "\xa7\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EMSGSIZE 4 RO
.data 1 "\xa6\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EPROTOTYPE 4 RO
.data 1 "\xa5\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOPROTOOPT 4 RO
.data 1 "\xa4\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EPROTONOSUPPORT 4 RO
.data 1 "\xa3\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ESOCKTNOSUPPORT 4 RO
.data 1 "\xa2\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EOPNOTSUPP 4 RO
.data 1 "\xa1\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EPFNOSUPPORT 4 RO
.data 1 "\xa0\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EAFNOSUPPORT 4 RO
.data 1 "\x9f\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EADDRINUSE 4 RO
.data 1 "\x9e\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EADDRNOTAVAIL 4 RO
.data 1 "\x9d\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENETDOWN 4 RO
.data 1 "\x9c\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENETUNREACH 4 RO
.data 1 "\x9b\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENETRESET 4 RO
.data 1 "\x9a\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ECONNABORTED 4 RO
.data 1 "\x99\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ECONNRESET 4 RO
.data 1 "\x98\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOBUFS 4 RO
.data 1 "\x97\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EISCONN 4 RO
.data 1 "\x96\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOTCONN 4 RO
.data 1 "\x95\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ESHUTDOWN 4 RO
.data 1 "\x94\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ETOOMANYREFS 4 RO
.data 1 "\x93\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ETIMEDOUT 4 RO
.data 1 "\x92\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ECONNREFUSED 4 RO
.data 1 "\x91\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EHOSTDOWN 4 RO
.data 1 "\x90\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EHOSTUNREACH 4 RO
.data 1 "\x8f\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EALREADY 4 RO
.data 1 "\x8e\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EINPROGRESS 4 RO
.data 1 "\x8d\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ESTALE 4 RO
.data 1 "\x8c\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EUCLEAN 4 RO
.data 1 "\x8b\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOTNAM 4 RO
.data 1 "\x8a\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENAVAIL 4 RO
.data 1 "\x89\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EISNAM 4 RO
.data 1 "\x88\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EREMOTEIO 4 RO
.data 1 "\x87\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EDQUOT 4 RO
.data 1 "\x86\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOMEDIUM 4 RO
.data 1 "\x85\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EMEDIUMTYPE 4 RO
.data 1 "\x84\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ECANCELED 4 RO
.data 1 "\x83\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOKEY 4 RO
.data 1 "\x82\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EKEYEXPIRED 4 RO
.data 1 "\x81\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EKEYREVOKED 4 RO
.data 1 "\x80\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EKEYREJECTED 4 RO
.data 1 "\x7f\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EOWNERDEAD 4 RO
.data 1 "~\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ENOTRECOVERABLE 4 RO
.data 1 "}\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/ERFKILL 4 RO
.data 1 "|\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/EHWPOISON 4 RO
.data 1 "{\xff\xff\xff" # 0 4 wrapped<os/Error>

.mem os/Stdin 4 RO
.data 4 [0] # 0 4 wrapped<os/FD>

.mem os/Stdout 4 RO
.data 1 "\x01\x00\x00\x00" # 0 4 wrapped<os/FD>

.mem os/Stderr 4 RO
.data 1 "\x02\x00\x00\x00" # 0 4 wrapped<os/FD>

.mem os/O_CREAT 4 RO
.data 1 "@\x00\x00\x00" # 0 4 u32

.mem os/O_EXCL 4 RO
.data 1 "\x80\x00\x00\x00" # 0 4 u32

.mem os/O_NOCTTY 4 RO
.data 1 "\x00\x01\x00\x00" # 0 4 u32

.mem os/O_TRUNC 4 RO
.data 1 "\x00\x02\x00\x00" # 0 4 u32

.mem os/O_APPEND 4 RO
.data 1 "\x00\x04\x00\x00" # 0 4 u32

.mem os/O_ACCMODE 4 RO
.data 1 "\x03\x00\x00\x00" # 0 4 u32

.mem os/O_RDONLY 4 RO
.data 4 [0] # 0 4 u32

.mem os/O_WRONLY 4 RO
.data 1 "\x01\x00\x00\x00" # 0 4 u32

.mem os/O_RDWR 4 RO
.data 1 "\x02\x00\x00\x00" # 0 4 u32

.mem os/O_NONBLOCK 4 RO
.data 1 "\x00\x08\x00\x00" # 0 4 u32

.mem os/O_DSYNC 4 RO
.data 1 "\x00\x10\x00\x00" # 0 4 u32

.mem os/O_DIRECT 4 RO
.data 1 "\x00@\x00\x00" # 0 4 u32

.mem os/O_LARGEFILE 4 RO
.data 1 "\x00\x80\x00\x00" # 0 4 u32

.mem os/O_DIRECTORY 4 RO
.data 1 "\x00\x00\x01\x00" # 0 4 u32

.mem os/O_NOFOLLOW 4 RO
.data 1 "\x00\x00\x02\x00" # 0 4 u32

.mem os/O_NOATIME 4 RO
.data 1 "\x00\x00\x04\x00" # 0 4 u32

.mem os/O_CLOEXEC 4 RO
.data 1 "\x00\x00\x08\x00" # 0 4 u32


.fun os/FileWrite NORMAL [] = [S32 A64 A64]
.bbl entry
  poparg fd:S32
  poparg buffer:A64
  poparg large_result:A64
  ld pointer:A64 = buffer 0
  ld length:U64 = buffer 8
  pusharg length
  pusharg pointer
  pusharg fd
  bsr write
  poparg call:S64
  mov res:S64 = call
  ble 0:S64 res br_f
  st large_result 0 = 17:U16
  conv as:S32 = res
  st large_result 8 = as
  ret
.bbl br_f
  st large_result 0 = 8:U16
  conv as.1:U64 = res
  st large_result 8 = as.1
  ret
.bbl br_join


.fun os/FileRead NORMAL [] = [S32 A64 A64]
.bbl entry
  poparg fd:S32
  poparg buffer:A64
  poparg large_result:A64
  ld pointer:A64 = buffer 0
  ld length:U64 = buffer 8
  pusharg length
  pusharg pointer
  pusharg fd
  bsr read
  poparg call:S64
  mov res:S64 = call
  ble 0:S64 res br_f
  st large_result 0 = 17:U16
  conv as:S32 = res
  st large_result 8 = as
  ret
.bbl br_f
  st large_result 0 = 8:U16
  conv as.1:U64 = res
  st large_result 8 = as.1
  ret
.bbl br_join


.fun os/TimeNanoSleep NORMAL [S32] = [A64 A64]
.bbl entry
  poparg req:A64
  poparg rem:A64
  pusharg rem
  pusharg req
  bsr nanosleep
  poparg call:S32
  mov res:S32 = call
  pusharg res
  ret


.fun os/FcntlInt NORMAL [] = [S32 U32 U32 A64]
.bbl entry
  poparg fd:S32
  poparg op:U32
  poparg arg:U32
  poparg large_result:A64
  conv as:U64 = arg
  pusharg as
  pusharg op
  pusharg fd
  bsr fcntl
  poparg call:S64
  mov res:S64 = call
  ble 0:S64 res br_f
  st large_result 0 = 17:U16
  conv as.1:S32 = res
  st large_result 8 = as.1
  ret
.bbl br_f
  st large_result 0 = 8:U16
  conv as.2:U64 = res
  st large_result 8 = as.2
  ret
.bbl br_join


.fun os/Ioctl NORMAL [] = [S32 U32 A64 A64]
.bbl entry
  poparg fd:S32
  poparg op:U32
  poparg arg:A64
  poparg large_result:A64
  bitcast bitcast:U64 = arg
  pusharg bitcast
  pusharg op
  pusharg fd
  bsr ioctl
  poparg call:S64
  mov res:S64 = call
  ble 0:S64 res br_f
  st large_result 0 = 17:U16
  conv as:S32 = res
  st large_result 8 = as
  ret
.bbl br_f
  st large_result 0 = 8:U16
  conv as.1:U64 = res
  st large_result 8 = as.1
  ret
.bbl br_join

.mem fmt/FORMATED_STRING_MAX_LEN 8 RO
.data 1 "\x00\x10\x00\x00\x00\x00\x00\x00" # 0 8 u64

.mem fmt/TRUE_STR 8 RO
# rec: rec<xtuple_span<u8>>
.addr.mem 8 $gen/global_val_5 0
.data 1 "\x04\x00\x00\x00\x00\x00\x00\x00" # 8 8 u64

.mem fmt/FALSE_STR 8 RO
# rec: rec<xtuple_span<u8>>
.addr.mem 8 $gen/global_val_6 0
.data 1 "\x05\x00\x00\x00\x00\x00\x00\x00" # 8 8 u64


.fun fmt/mymemcpy NORMAL [U64] = [A64 A64 U64]
.bbl entry
  poparg dst:A64
  poparg src:A64
  poparg size:U64
  mov it%1:U64 = 0:U64
.bbl _
  blt it%1 size br_join.1
  bra _.end  # break
.bbl br_join.1
.bbl br_join
  mov i:U64 = it%1
  add expr2:U64 = it%1 1:U64
  mov it%1 = expr2
  lea new_base:A64 = dst i
  lea new_base.1:A64 = src i
  .reg U8 copy
  ld copy = new_base.1 0
  st new_base 0 = copy
  bra _  # continue
.bbl _.end
  pusharg size
  ret


.fun fmt/SysRender<bool> NORMAL [U64] = [U8 A64 A64]
.bbl entry
  poparg v:U8
  poparg buffer:A64
  poparg options:A64
  .stk s 8 16
  lea.stk var_stk_base:A64 s 0
  beq v 0 br_f
  lea.mem lhsaddr:A64 = fmt/TRUE_STR 0
  .reg U64 copy
  ld copy = lhsaddr 0
  st var_stk_base 0 = copy
  ld copy = lhsaddr 8
  st var_stk_base 8 = copy
  bra end_expr
.bbl br_f
  lea.mem lhsaddr.1:A64 = fmt/FALSE_STR 0
  .reg U64 copy.1
  ld copy.1 = lhsaddr.1 0
  st var_stk_base 0 = copy.1
  ld copy.1 = lhsaddr.1 8
  st var_stk_base 8 = copy.1
  bra end_expr
.bbl br_join
.bbl end_expr
  ld length:U64 = buffer 8
  lea.stk lhsaddr.2:A64 = s 0
  ld length.1:U64 = lhsaddr.2 8
  cmplt expr2:U64 = length length.1 length length.1
  mov n:U64 = expr2
  ld pointer:A64 = buffer 0
  lea.stk lhsaddr.3:A64 = s 0
  ld pointer.1:A64 = lhsaddr.3 0
  pusharg n
  pusharg pointer.1
  pusharg pointer
  bsr fmt/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt/str_to_u32 NORMAL [U32] = [A64]
.bbl entry
  poparg s:A64
  mov x:U32 = 0:U32
  ld length:U64 = s 8
  mov end_eval%1:U64 = length
  mov it%1:U64 = 0:U64
.bbl _
  blt it%1 end_eval%1 br_join.1
  bra _.end  # break
.bbl br_join.1
.bbl br_join
  mov i:U64 = it%1
  add expr2:U64 = it%1 1:U64
  mov it%1 = expr2
  mul expr2.1:U32 = x 10:U32
  mov x = expr2.1
  ld pointer:A64 = s 0
  lea new_base:A64 = pointer i
  ld deref:U8 = new_base 0
  mov c:U8 = deref
  sub expr2.2:U8 = c 48:U8
  conv as:U32 = expr2.2
  add expr2.3:U32 = x as
  mov x = expr2.3
  bra _  # continue
.bbl _.end
  pusharg x
  ret


.fun fmt/SysRender<u8> NORMAL [U64] = [U8 A64 A64]
.bbl entry
  poparg v:U8
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtDec<u8>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<u16> NORMAL [U64] = [U16 A64 A64]
.bbl entry
  poparg v:U16
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtDec<u16>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<u32> NORMAL [U64] = [U32 A64 A64]
.bbl entry
  poparg v:U32
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtDec<u32>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<u64> NORMAL [U64] = [U64 A64 A64]
.bbl entry
  poparg v:U64
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtDec<u64>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<s16> NORMAL [U64] = [S16 A64 A64]
.bbl entry
  poparg v:S16
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtDec<s16>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<s32> NORMAL [U64] = [S32 A64 A64]
.bbl entry
  poparg v:S32
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtDec<s32>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<ptr<rec<xtuple_span<u8>>>> NORMAL [U64] = [A64 A64 A64]
.bbl entry
  poparg v:A64
  poparg buffer:A64
  poparg options:A64
  ld length:U64 = buffer 8
  ld length.1:U64 = v 8
  cmplt expr2:U64 = length length.1 length length.1
  mov n:U64 = expr2
  ld pointer:A64 = buffer 0
  ld pointer.1:A64 = v 0
  pusharg n
  pusharg pointer.1
  pusharg pointer
  bsr fmt/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<ptr<rec<xtuple_span_mut<u8>>>> NORMAL [U64] = [A64 A64 A64]
.bbl entry
  poparg v:A64
  poparg buffer:A64
  poparg options:A64
  ld length:U64 = buffer 8
  ld length.1:U64 = v 8
  cmplt expr2:U64 = length length.1 length length.1
  mov n:U64 = expr2
  ld pointer:A64 = buffer 0
  ld pointer.1:A64 = v 0
  pusharg n
  pusharg pointer.1
  pusharg pointer
  bsr fmt/mymemcpy
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<wrapped<fmt/uint_hex>> NORMAL [U64] = [U64 A64 A64]
.bbl entry
  poparg v:U64
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtHex<u64>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<wrapped<fmt/u64_hex>> NORMAL [U64] = [U64 A64 A64]
.bbl entry
  poparg v:U64
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtHex<u64>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<wrapped<fmt/u32_hex>> NORMAL [U64] = [U32 A64 A64]
.bbl entry
  poparg v:U32
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtHex<u32>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<wrapped<fmt/u16_hex>> NORMAL [U64] = [U16 A64 A64]
.bbl entry
  poparg v:U16
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtHex<u16>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<wrapped<fmt/u8_hex>> NORMAL [U64] = [U8 A64 A64]
.bbl entry
  poparg v:U8
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_int/FmtHex<u8>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<wrapped<fmt/rune>> NORMAL [U64] = [U8 A64 A64]
.bbl entry
  poparg v:U8
  poparg buffer:A64
  poparg options:A64
  ld length:U64 = buffer 8
  bne length 0:U64 br_f
  pusharg 0:U64
  ret
.bbl br_f
  ld pointer:A64 = buffer 0
  st pointer 0 = v
  pusharg 1:U64
  ret
.bbl br_join


.fun fmt/SysRender<wrapped<fmt/r64_hex>> NORMAL [U64] = [R64 A64 A64]
.bbl entry
  poparg v:R64
  poparg out:A64
  poparg options:A64
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg v
  bsr fmt_real/FmtHex<r64>
  poparg call:U64
  pusharg call
  ret


.fun fmt/SysRender<r64> NORMAL [U64] = [R64 A64 A64]
.bbl entry
  poparg v:R64
  poparg out:A64
  poparg options:A64
  .stk arg3 8 16
  lea.stk var_stk_base:A64 arg3 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg3 0
  pusharg lhsaddr
  pusharg 0:U8
  pusharg 6:U64
  pusharg v
  bsr fmt_real/FmtE<r64>
  poparg call:U64
  pusharg call
  ret


.fun fmt/to_hex_digit NORMAL [U8] = [U8]
.bbl entry
  poparg digit:U8
  add expr2:U8 = digit 48:U8
  mov expr3_t:U8 = expr2
  add expr2.1:U8 = digit 87:U8
  mov expr3_f:U8 = expr2.1
  blt 9:U8 digit br_f
  pusharg expr3_t
  ret
.bbl br_f
  pusharg expr3_f
  ret
.bbl br_join


.fun fmt/SysRender<ptr<wrapped<fmt/str_hex>>> NORMAL [U64] = [A64 A64 A64]
.bbl entry
  poparg v:A64
  poparg out:A64
  poparg options:A64
  .stk v_str 8 16
  lea.stk var_stk_base:A64 v_str 0
  .reg U64 copy
  ld copy = v 0
  st var_stk_base 0 = copy
  ld copy = v 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = v_str 0
  ld length:U64 = lhsaddr 8
  mov dst_len:U64 = length
  ld length.1:U64 = out 8
  blt length.1 dst_len br_f
  mov it%1:U64 = 0:U64
.bbl _
  blt it%1 dst_len br_join.2
  bra _.end  # break
.bbl br_join.2
.bbl br_join.1
  mov i:U64 = it%1
  add expr2:U64 = it%1 1:U64
  mov it%1 = expr2
  lea.stk lhsaddr.1:A64 = v_str 0
  ld pointer:A64 = lhsaddr.1 0
  lea new_base:A64 = pointer i
  ld deref:U8 = new_base 0
  mov c:U8 = deref
  mul expr2.1:U64 = i 2:U64
  mov o1:U64 = expr2.1
  add expr2.2:U64 = o1 1:U64
  mov o2:U64 = expr2.2
  ld pointer.1:A64 = out 0
  lea new_base.1:A64 = pointer.1 o1
  shr expr2.3:U8 = c 4:U8
  mov inl_arg:U8 = expr2.3
  add expr2.4:U8 = inl_arg 48:U8
  mov expr3_t:U8 = expr2.4
  add expr2.5:U8 = inl_arg 87:U8
  mov expr3_f:U8 = expr2.5
  blt 9:U8 inl_arg br_f.1
  st new_base.1 0 = expr3_t
  bra end_expr
.bbl br_f.1
  st new_base.1 0 = expr3_f
  bra end_expr
.bbl br_join.3
.bbl end_expr
  ld pointer.2:A64 = out 0
  lea new_base.2:A64 = pointer.2 o2
  and expr2.6:U8 = c 15:U8
  mov inl_arg.1:U8 = expr2.6
  add expr2.7:U8 = inl_arg.1 48:U8
  mov expr3_t.1:U8 = expr2.7
  add expr2.8:U8 = inl_arg.1 87:U8
  mov expr3_f.1:U8 = expr2.8
  blt 9:U8 inl_arg.1 br_f.2
  st new_base.2 0 = expr3_t.1
  bra end_expr.1
.bbl br_f.2
  st new_base.2 0 = expr3_f.1
  bra end_expr.1
.bbl br_join.4
.bbl end_expr.1
  bra _  # continue
.bbl _.end
  mul expr2.9:U64 = dst_len 2:U64
  pusharg expr2.9
  ret
.bbl br_f
  ld length.2:U64 = out 8
  mov end_eval%2:U64 = length.2
  mov it%2:U64 = 0:U64
.bbl _.1
  blt it%2 end_eval%2 br_join.6
  bra _.1.end  # break
.bbl br_join.6
.bbl br_join.5
  mov i.1:U64 = it%2
  add expr2.10:U64 = it%2 1:U64
  mov it%2 = expr2.10
  ld pointer.3:A64 = out 0
  lea new_base.3:A64 = pointer.3 i.1
  st new_base.3 0 = 46:U8
  bra _.1  # continue
.bbl _.1.end
  pusharg 0:U64
  ret
.bbl br_join


.fun fmt/SysRender<ptr<void>> NORMAL [U64] = [A64 A64 A64]
.bbl entry
  poparg v:A64
  poparg out:A64
  poparg options:A64
  bitcast bitcast:U64 = v
  mov h:U64 = bitcast
  .stk arg1 8 16
  lea.stk var_stk_base:A64 arg1 0
  .reg U64 copy
  ld copy = out 0
  st var_stk_base 0 = copy
  ld copy = out 8
  st var_stk_base 8 = copy
  lea.stk lhsaddr:A64 = arg1 0
  pusharg lhsaddr
  pusharg h
  bsr fmt_int/FmtHex<u64>
  poparg call:U64
  pusharg call
  ret


.fun fmt/strz_to_slice NORMAL [] = [A64 A64]
.bbl entry
  poparg s:A64
  poparg large_result:A64
  mov i:U64 = 0:U64
.bbl _
  lea new_base:A64 = s i
  ld deref:U8 = new_base 0
  bne deref 0:U8 br_join
  bra _.end  # break
.bbl br_join
  add expr2:U64 = i 1:U64
  mov i = expr2
  bra _  # continue
.bbl _.end
  st large_result 0 = s
  st large_result 8 = i
  ret

.mem parse_real/ParseError 8 RO
# rec: rec<parse_real/ResultR64>
.data 16 [0] # 0 16 auto


.fun parse_real/is_hex_digit NORMAL [U8] = [U8]
.bbl entry
  poparg c:U8
  blt c 48:U8 br_failed_and
  ble c 57:U8 br_failed_or
.bbl br_failed_and
  blt c 97:U8 br_f
  blt 102:U8 c br_f
.bbl br_failed_or
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun parse_real/hex_digit_val NORMAL [U8] = [U8]
.bbl entry
  poparg c:U8
  sub expr2:U8 = c 48:U8
  mov expr3_t:U8 = expr2
  sub expr2.1:U8 = c 97:U8
  add expr2.2:U8 = expr2.1 10:U8
  mov expr3_f:U8 = expr2.2
  blt 57:U8 c br_f
  pusharg expr3_t
  ret
.bbl br_f
  pusharg expr3_f
  ret
.bbl br_join


.fun parse_real/is_dec_digit NORMAL [U8] = [U8]
.bbl entry
  poparg c:U8
  blt c 48:U8 br_f
  blt 57:U8 c br_f
  pusharg 1:U8
  ret
.bbl br_f
  pusharg 0:U8
  ret
.bbl br_join


.fun parse_real/dec_digit_val NORMAL [U8] = [U8]
.bbl entry
  poparg c:U8
  sub expr2:U8 = c 48:U8
  pusharg expr2
  ret


.fun parse_real/parse_r64_hex_helper NORMAL [] = [A64 U8 U64 A64]
.bbl entry
  poparg s:A64
  poparg negative:U8
  poparg offset:U64
  poparg large_result:A64
  mov i:U64 = offset
  ld length:U64 = s 8
  mov n:U64 = length
  mov c:U8 = 0:U8
  blt i n br_join
  lea.mem lhsaddr:A64 = parse_real/ParseError 0
  .reg U64 copy
  ld copy = lhsaddr 0
  st large_result 0 = copy
  ld copy = lhsaddr 8
  st large_result 8 = copy
  ret
.bbl br_join
  ld pointer:A64 = s 0
  lea new_base:A64 = pointer i
  ld deref:U8 = new_base 0
  mov c = deref
  add expr2:U64 = i 1:U64
  mov i = expr2
  mov mant:U64 = 0:U64
  mov exp_adjustments:S32 = 0:S32
  mov exp:S32 = 0:S32
.bbl end_of_input
  mov digits%1:U32 = 15:U32
.bbl _
  beq c 48:U8 br_join.1
  bra _.end  # break
.bbl br_join.1
  blt i n br_join.2
  bra end_of_input.end  # break
.bbl br_join.2
  ld pointer.1:A64 = s 0
  lea new_base.1:A64 = pointer.1 i
  ld deref.1:U8 = new_base.1 0
  mov c = deref.1
  add expr2.1:U64 = i 1:U64
  mov i = expr2.1
  bra _  # continue
.bbl _.end
.bbl _.1
  .reg U8 expr
  mov inl_arg:U8 = c
  blt inl_arg 48:U8 br_failed_and
  ble inl_arg 57:U8 br_failed_or
.bbl br_failed_and
  blt inl_arg 97:U8 br_f
  blt 102:U8 inl_arg br_f
.bbl br_failed_or
  mov expr = 1:U8
  bra end_expr
.bbl br_f
  mov expr = 0:U8
  bra end_expr
.bbl br_join.4
.bbl end_expr
  bne expr 0 br_join.3
  bra _.1.end  # break
.bbl br_join.3
  bne digits%1 0:U32 br_f.1
  add expr2.2:S32 = exp_adjustments 1:S32
  mov exp_adjustments = expr2.2
  bra br_join.5
.bbl br_f.1
  mul expr2.3:U64 = mant 16:U64
  mov mant = expr2.3
  .reg U8 expr.1
  mov inl_arg.1:U8 = c
  sub expr2.4:U8 = inl_arg.1 48:U8
  mov expr3_t:U8 = expr2.4
  sub expr2.5:U8 = inl_arg.1 97:U8
  add expr2.6:U8 = expr2.5 10:U8
  mov expr3_f:U8 = expr2.6
  blt 57:U8 inl_arg.1 br_f.2
  mov expr.1 = expr3_t
  bra end_expr.1
.bbl br_f.2
  mov expr.1 = expr3_f
  bra end_expr.1
.bbl br_join.6
.bbl end_expr.1
  conv as:U64 = expr.1
  add expr2.7:U64 = mant as
  mov mant = expr2.7
  sub expr2.8:U32 = digits%1 1:U32
  mov digits%1 = expr2.8
.bbl br_join.5
  blt i n br_join.7
  bra end_of_input.end  # break
.bbl br_join.7
  ld pointer.2:A64 = s 0
  lea new_base.2:A64 = pointer.2 i
  ld deref.2:U8 = new_base.2 0
  mov c = deref.2
  add expr2.9:U64 = i 1:U64
  mov i = expr2.9
  bra _.1  # continue
.bbl _.1.end
  bne c 46:U8 br_join.8
  blt i n br_join.9
  bra end_of_input.end  # break
.bbl br_join.9
  ld pointer.3:A64 = s 0
  lea new_base.3:A64 = pointer.3 i
  ld deref.3:U8 = new_base.3 0
  mov c = deref.3
  add expr2.10:U64 = i 1:U64
  mov i = expr2.10
.bbl _.2
  .reg U8 expr.2
  mov inl_arg.2:U8 = c
  blt inl_arg.2 48:U8 br_failed_and.1
  ble inl_arg.2 57:U8 br_failed_or.1
.bbl br_failed_and.1
  blt inl_arg.2 97:U8 br_f.3
  blt 102:U8 inl_arg.2 br_f.3
.bbl br_failed_or.1
  mov expr.2 = 1:U8
  bra end_expr.2
.bbl br_f.3
  mov expr.2 = 0:U8
  bra end_expr.2
.bbl br_join.11
.bbl end_expr.2
  bne expr.2 0 br_join.10
  bra _.2.end  # break
.bbl br_join.10
  beq digits%1 0:U32 br_join.12
  mul expr2.11:U64 = mant 16:U64
  mov mant = expr2.11
  .reg U8 expr.3
  mov inl_arg.3:U8 = c
  sub expr2.12:U8 = inl_arg.3 48:U8
  mov expr3_t.1:U8 = expr2.12
  sub expr2.13:U8 = inl_arg.3 97:U8
  add expr2.14:U8 = expr2.13 10:U8
  mov expr3_f.1:U8 = expr2.14
  blt 57:U8 inl_arg.3 br_f.4
  mov expr.3 = expr3_t.1
  bra end_expr.3
.bbl br_f.4
  mov expr.3 = expr3_f.1
  bra end_expr.3
.bbl br_join.13
.bbl end_expr.3
  conv as.1:U64 = expr.3
  add expr2.15:U64 = mant as.1
  mov mant = expr2.15
  sub expr2.16:S32 = exp_adjustments 1:S32
  mov exp_adjustments = expr2.16
  sub expr2.17:U32 = digits%1 1:U32
  mov digits%1 = expr2.17
.bbl br_join.12
  blt i n br_join.14
  bra end_of_input.end  # break
.bbl br_join.14
  ld pointer.4:A64 = s 0
  lea new_base.4:A64 = pointer.4 i
  ld deref.4:U8 = new_base.4 0
  mov c = deref.4
  add expr2.18:U64 = i 1:U64
  mov i = expr2.18
  bra _.2  # continue
.bbl _.2.end
.bbl br_join.8
.bbl end_of_input.end
  bne c 112:U8 br_join.15
  blt i n br_join.16
  lea.mem lhsaddr.1:A64 = parse_real/ParseError 0
  .reg U64 copy.1
  ld copy.1 = lhsaddr.1 0
  st large_result 0 = copy.1
  ld copy.1 = lhsaddr.1 8
  st large_result 8 = copy.1
  ret
.bbl br_join.16
  ld pointer.5:A64 = s 0
  lea new_base.5:A64 = pointer.5 i
  ld deref.5:U8 = new_base.5 0
  mov c = deref.5
  add expr2.19:U64 = i 1:U64
  mov i = expr2.19
  mov negative%1:U8 = 0:U8
  beq c 45:U8 br_failed_or.2
  bne c 43:U8 br_join.17
.bbl br_failed_or.2
  bne c 45:U8 br_join.18
  mov negative%1 = 1:U8
.bbl br_join.18
  blt i n br_join.19
  lea.mem lhsaddr.2:A64 = parse_real/ParseError 0
  .reg U64 copy.2
  ld copy.2 = lhsaddr.2 0
  st large_result 0 = copy.2
  ld copy.2 = lhsaddr.2 8
  st large_result 8 = copy.2
  ret
.bbl br_join.19
  ld pointer.6:A64 = s 0
  lea new_base.6:A64 = pointer.6 i
  ld deref.6:U8 = new_base.6 0
  mov c = deref.6
  add expr2.20:U64 = i 1:U64
  mov i = expr2.20
.bbl br_join.17
.bbl _.3
  .reg U8 expr.4
  mov inl_arg.4:U8 = c
  blt inl_arg.4 48:U8 br_f.5
  blt 57:U8 inl_arg.4 br_f.5
  mov expr.4 = 1:U8
  bra end_expr.4
.bbl br_f.5
  mov expr.4 = 0:U8
  bra end_expr.4
.bbl br_join.21
.bbl end_expr.4
  bne expr.4 0 br_join.20
  bra _.3.end  # break
.bbl br_join.20
  mul expr2.21:S32 = exp 10:S32
  mov exp = expr2.21
  .reg U8 expr.5
  mov inl_arg.5:U8 = c
  sub expr2.22:U8 = inl_arg.5 48:U8
  mov expr.5 = expr2.22
  bra end_expr.5
.bbl end_expr.5
  conv as.2:S32 = expr.5
  add expr2.23:S32 = exp as.2
  mov exp = expr2.23
  blt i n br_join.22
  bra _.3.end  # break
.bbl br_join.22
  ld pointer.7:A64 = s 0
  lea new_base.7:A64 = pointer.7 i
  ld deref.7:U8 = new_base.7 0
  mov c = deref.7
  add expr2.24:U64 = i 1:U64
  mov i = expr2.24
  bra _.3  # continue
.bbl _.3.end
  beq negative%1 0 br_join.23
  sub expr1:S32 = 0 exp
  mov exp = expr1
.bbl br_join.23
.bbl br_join.15
  bne mant 0:U64 br_join.24
  .stk expr3_t.2 8 16
  lea.stk var_stk_base:A64 expr3_t.2 0
  st var_stk_base 0 = -0x0.0p+0:R64
  st var_stk_base 8 = i
  .stk expr3_f.2 8 16
  lea.stk var_stk_base.1:A64 expr3_f.2 0
  st var_stk_base.1 0 = 0x0.0p+0:R64
  st var_stk_base.1 8 = i
  beq negative 0 br_f.6
  lea.stk lhsaddr.3:A64 = expr3_t.2 0
  .reg U64 copy.3
  ld copy.3 = lhsaddr.3 0
  st large_result 0 = copy.3
  ld copy.3 = lhsaddr.3 8
  st large_result 8 = copy.3
  ret
.bbl br_f.6
  lea.stk lhsaddr.4:A64 = expr3_f.2 0
  .reg U64 copy.4
  ld copy.4 = lhsaddr.4 0
  st large_result 0 = copy.4
  ld copy.4 = lhsaddr.4 8
  st large_result 8 = copy.4
  ret
.bbl br_join.25
.bbl br_join.24
  mul expr2.25:S32 = exp_adjustments 4:S32
  add expr2.26:S32 = exp expr2.25
  mov exp = expr2.26
  add expr2.27:S32 = exp 52:S32
  mov exp = expr2.27
.bbl _.4
  shr expr2.28:U64 = mant 52:U64
  beq expr2.28 0:U64 br_join.26
  bra _.4.end  # break
.bbl br_join.26
  shl expr2.29:U64 = mant 8:U64
  mov mant = expr2.29
  sub expr2.30:S32 = exp 8:S32
  mov exp = expr2.30
  bra _.4  # continue
.bbl _.4.end
.bbl _.5
  shr expr2.31:U64 = mant 52:U64
  bne expr2.31 1:U64 br_join.27
  bra _.5.end  # break
.bbl br_join.27
  shr expr2.32:U64 = mant 1:U64
  mov mant = expr2.32
  add expr2.33:S32 = exp 1:S32
  mov exp = expr2.33
  bra _.5  # continue
.bbl _.5.end
  ble exp 1023:S32 br_join.28
  lea.mem lhsaddr.5:A64 = parse_real/ParseError 0
  .reg U64 copy.5
  ld copy.5 = lhsaddr.5 0
  st large_result 0 = copy.5
  ld copy.5 = lhsaddr.5 8
  st large_result 8 = copy.5
  ret
.bbl br_join.28
  ble -1022:S32 exp br_join.29
  lea.mem lhsaddr.6:A64 = parse_real/ParseError 0
  .reg U64 copy.6
  ld copy.6 = lhsaddr.6 0
  st large_result 0 = copy.6
  ld copy.6 = lhsaddr.6 8
  st large_result 8 = copy.6
  ret
.bbl br_join.29
  add expr2.34:S32 = exp 1023:S32
  mov exp = expr2.34
  conv as.3:U64 = exp
  and expr2.35:U64 = as.3 2047:U64
  mov exp_u64:U64 = expr2.35
  and expr2.36:U64 = mant 4503599627370495:U64
  mov mant = expr2.36
  pusharg mant
  pusharg exp_u64
  pusharg negative
  bsr num_real/make_r64
  poparg call:R64
  mov complex_init_tmp:R64 = call
  st large_result 0 = complex_init_tmp
  st large_result 8 = i
  ret


.fun parse_real/parse_r64_hex NORMAL [] = [A64 A64]
.bbl entry
  poparg s:A64
  poparg large_result:A64
  ld length:U64 = s 8
  ble 5:U64 length br_join
  lea.mem lhsaddr:A64 = parse_real/ParseError 0
  .reg U64 copy
  ld copy = lhsaddr 0
  st large_result 0 = copy
  ld copy = lhsaddr 8
  st large_result 8 = copy
  ret
.bbl br_join
  mov i:U64 = 0:U64
  ld pointer:A64 = s 0
  lea new_base:A64 = pointer i
  ld deref:U8 = new_base 0
  mov c:U8 = deref
  mov negative:U8 = 0:U8
  beq c 45:U8 br_failed_or
  bne c 43:U8 br_join.1
.bbl br_failed_or
  add expr2:U64 = i 1:U64
  mov i = expr2
  bne c 45:U8 br_join.2
  mov negative = 1:U8
.bbl br_join.2
.bbl br_join.1
  ld pointer.1:A64 = s 0
  lea new_base.1:A64 = pointer.1 i
  ld deref.1:U8 = new_base.1 0
  bne deref.1 48:U8 br_failed_or.1
  ld pointer.2:A64 = s 0
  add expr2.1:U64 = i 1:U64
  lea new_base.2:A64 = pointer.2 expr2.1
  ld deref.2:U8 = new_base.2 0
  beq deref.2 120:U8 br_join.3
.bbl br_failed_or.1
  lea.mem lhsaddr.1:A64 = parse_real/ParseError 0
  .reg U64 copy.1
  ld copy.1 = lhsaddr.1 0
  st large_result 0 = copy.1
  ld copy.1 = lhsaddr.1 8
  st large_result 8 = copy.1
  ret
.bbl br_join.3
  add expr2.2:U64 = i 2:U64
  mov i = expr2.2
  .stk arg0 8 16
  lea.stk var_stk_base:A64 arg0 0
  ld length.1:U64 = s 8
  mov orig_len%1:U64 = length.1
  mov orig_size%1:U64 = i
  ble orig_size%1 orig_len%1 br_join.4
  trap
.bbl br_join.4
  ld pointer.3:A64 = s 0
  lea new_base.3:A64 = pointer.3 orig_size%1
  st var_stk_base 0 = new_base.3
  sub expr2.3:U64 = orig_len%1 orig_size%1
  st var_stk_base 8 = expr2.3
  bra end_expr.1
.bbl end_expr.1
  .stk result 8 16
  lea.stk lhsaddr.2:A64 = arg0 0
  lea.stk lhsaddr.3:A64 = result 0
  pusharg lhsaddr.3
  pusharg i
  pusharg negative
  pusharg lhsaddr.2
  bsr parse_real/parse_r64_hex_helper
  lea.stk lhsaddr.4:A64 = result 0
  .reg U64 copy.2
  ld copy.2 = lhsaddr.4 0
  st large_result 0 = copy.2
  ld copy.2 = lhsaddr.4 8
  st large_result 8 = copy.2
  bra end_expr
.bbl end_expr
  ret


.fun parse_real/r64_dec_fast_helper NORMAL [R64] = [U64 S32 U8]
.bbl entry
  poparg mant_orig:U64
  poparg exp_orig:S32
  poparg negative:U8
  mov exp:S32 = exp_orig
  mov mant:U64 = mant_orig
.bbl _
  ble 9007199254740992:U64 mant br_join
  bra _.end  # break
.bbl br_join
  div expr2:U64 = mant 10:U64
  mov mant = expr2
  add expr2.1:S32 = exp 1:S32
  mov exp = expr2.1
  bra _  # continue
.bbl _.end
  blt exp 309:S32 br_join.1
  beq negative 0 br_f
  pusharg -inf:R64
  ret
.bbl br_f
  pusharg +inf:R64
  ret
.bbl br_join.2
.bbl br_join.1
  blt -309:S32 exp br_join.3
  beq negative 0 br_f.1
  pusharg -0x0.0p+0:R64
  ret
.bbl br_f.1
  pusharg 0x0.0p+0:R64
  ret
.bbl br_join.4
.bbl br_join.3
  conv as:S64 = mant
  conv as.1:R64 = as
  mov out:R64 = as.1
  beq negative 0 br_join.5
  sub expr1:R64 = 0 out
  mov out = expr1
.bbl br_join.5
  blt exp 0:S32 br_f.2
  lea.mem lhsaddr:A64 = num_real/powers_of_ten 0
  conv scaled:S64 = exp
  mul scaled = scaled 8
  lea new_base:A64 = lhsaddr scaled
  ld deref:R64 = new_base 0
  mul expr2.2:R64 = out deref
  pusharg expr2.2
  ret
.bbl br_f.2
  lea.mem lhsaddr.1:A64 = num_real/powers_of_ten 0
  sub expr1.1:S32 = 0 exp
  conv scaled.1:S64 = expr1.1
  mul scaled.1 = scaled.1 8
  lea new_base.1:A64 = lhsaddr.1 scaled.1
  ld deref.1:R64 = new_base.1 0
  div expr2.3:R64 = out deref.1
  pusharg expr2.3
  ret
.bbl br_join.6


.fun parse_real/parse_r64 NORMAL [] = [A64 A64]
.bbl entry
  poparg s:A64
  poparg large_result:A64
  mov i:U64 = 0:U64
  ld length:U64 = s 8
  mov n:U64 = length
  mov c:U8 = 0:U8
  blt i n br_join
  lea.mem lhsaddr:A64 = parse_real/ParseError 0
  .reg U64 copy
  ld copy = lhsaddr 0
  st large_result 0 = copy
  ld copy = lhsaddr 8
  st large_result 8 = copy
  ret
.bbl br_join
  ld pointer:A64 = s 0
  lea new_base:A64 = pointer i
  ld deref:U8 = new_base 0
  mov c = deref
  add expr2:U64 = i 1:U64
  mov i = expr2
  mov negative:U8 = 0:U8
  beq c 45:U8 br_failed_or
  bne c 43:U8 br_join.1
.bbl br_failed_or
  bne c 45:U8 br_join.2
  mov negative = 1:U8
.bbl br_join.2
  blt i n br_join.3
  lea.mem lhsaddr.1:A64 = parse_real/ParseError 0
  .reg U64 copy.1
  ld copy.1 = lhsaddr.1 0
  st large_result 0 = copy.1
  ld copy.1 = lhsaddr.1 8
  st large_result 8 = copy.1
  ret
.bbl br_join.3
  ld pointer.1:A64 = s 0
  lea new_base.1:A64 = pointer.1 i
  ld deref.1:U8 = new_base.1 0
  mov c = deref.1
  add expr2.1:U64 = i 1:U64
  mov i = expr2.1
.bbl br_join.1
  bne c 105:U8 br_join.4
  add expr2.2:U64 = i 2:U64
  blt n expr2.2 br_failed_or.1
  ld pointer.2:A64 = s 0
  lea new_base.2:A64 = pointer.2 i
  ld deref.2:U8 = new_base.2 0
  bne deref.2 110:U8 br_failed_or.1
  ld pointer.3:A64 = s 0
  add expr2.3:U64 = i 1:U64
  lea new_base.3:A64 = pointer.3 expr2.3
  ld deref.3:U8 = new_base.3 0
  beq deref.3 102:U8 br_join.5
.bbl br_failed_or.1
  lea.mem lhsaddr.2:A64 = parse_real/ParseError 0
  .reg U64 copy.2
  ld copy.2 = lhsaddr.2 0
  st large_result 0 = copy.2
  ld copy.2 = lhsaddr.2 8
  st large_result 8 = copy.2
  ret
.bbl br_join.5
  .stk expr3_t 8 16
  lea.stk var_stk_base:A64 expr3_t 0
  st var_stk_base 0 = -inf:R64
  add expr2.4:U64 = i 2:U64
  st var_stk_base 8 = expr2.4
  .stk expr3_f 8 16
  lea.stk var_stk_base.1:A64 expr3_f 0
  st var_stk_base.1 0 = +inf:R64
  add expr2.5:U64 = i 2:U64
  st var_stk_base.1 8 = expr2.5
  beq negative 0 br_f
  lea.stk lhsaddr.3:A64 = expr3_t 0
  .reg U64 copy.3
  ld copy.3 = lhsaddr.3 0
  st large_result 0 = copy.3
  ld copy.3 = lhsaddr.3 8
  st large_result 8 = copy.3
  ret
.bbl br_f
  lea.stk lhsaddr.4:A64 = expr3_f 0
  .reg U64 copy.4
  ld copy.4 = lhsaddr.4 0
  st large_result 0 = copy.4
  ld copy.4 = lhsaddr.4 8
  st large_result 8 = copy.4
  ret
.bbl br_join.6
.bbl br_join.4
  bne c 110:U8 br_join.7
  add expr2.6:U64 = i 2:U64
  blt n expr2.6 br_failed_or.2
  ld pointer.4:A64 = s 0
  lea new_base.4:A64 = pointer.4 i
  ld deref.4:U8 = new_base.4 0
  bne deref.4 97:U8 br_failed_or.2
  ld pointer.5:A64 = s 0
  add expr2.7:U64 = i 1:U64
  lea new_base.5:A64 = pointer.5 expr2.7
  ld deref.5:U8 = new_base.5 0
  beq deref.5 110:U8 br_join.8
.bbl br_failed_or.2
  lea.mem lhsaddr.5:A64 = parse_real/ParseError 0
  .reg U64 copy.5
  ld copy.5 = lhsaddr.5 0
  st large_result 0 = copy.5
  ld copy.5 = lhsaddr.5 8
  st large_result 8 = copy.5
  ret
.bbl br_join.8
  .stk expr3_t.1 8 16
  lea.stk var_stk_base.2:A64 expr3_t.1 0
  st var_stk_base.2 0 = -nan:R64
  add expr2.8:U64 = i 2:U64
  st var_stk_base.2 8 = expr2.8
  .stk expr3_f.1 8 16
  lea.stk var_stk_base.3:A64 expr3_f.1 0
  st var_stk_base.3 0 = +nan:R64
  add expr2.9:U64 = i 2:U64
  st var_stk_base.3 8 = expr2.9
  beq negative 0 br_f.1
  lea.stk lhsaddr.6:A64 = expr3_t.1 0
  .reg U64 copy.6
  ld copy.6 = lhsaddr.6 0
  st large_result 0 = copy.6
  ld copy.6 = lhsaddr.6 8
  st large_result 8 = copy.6
  ret
.bbl br_f.1
  lea.stk lhsaddr.7:A64 = expr3_f.1 0
  .reg U64 copy.7
  ld copy.7 = lhsaddr.7 0
  st large_result 0 = copy.7
  ld copy.7 = lhsaddr.7 8
  st large_result 8 = copy.7
  ret
.bbl br_join.9
.bbl br_join.7
  bne c 48:U8 br_join.10
  blt n i br_join.10
  ld pointer.6:A64 = s 0
  lea new_base.6:A64 = pointer.6 i
  ld deref.6:U8 = new_base.6 0
  bne deref.6 120:U8 br_join.10
  add expr2.10:U64 = i 1:U64
  mov i = expr2.10
  .stk arg0 8 16
  lea.stk var_stk_base.4:A64 arg0 0
  .reg U64 copy.8
  ld copy.8 = s 0
  st var_stk_base.4 0 = copy.8
  ld copy.8 = s 8
  st var_stk_base.4 8 = copy.8
  .stk result 8 16
  lea.stk lhsaddr.8:A64 = arg0 0
  lea.stk lhsaddr.9:A64 = result 0
  pusharg lhsaddr.9
  pusharg i
  pusharg negative
  pusharg lhsaddr.8
  bsr parse_real/parse_r64_hex_helper
  lea.stk lhsaddr.10:A64 = result 0
  .reg U64 copy.9
  ld copy.9 = lhsaddr.10 0
  st large_result 0 = copy.9
  ld copy.9 = lhsaddr.10 8
  st large_result 8 = copy.9
  bra end_expr
.bbl end_expr
  ret
.bbl br_join.10
  mov mant:U64 = 0:U64
  mov exp_adjustments:S32 = 0:S32
  mov exp:S32 = 0:S32
  mov imprecise:U8 = 0:U8
.bbl end_of_input
  mov digits%1:S32 = 19:S32
.bbl _
  beq c 48:U8 br_join.11
  bra _.end  # break
.bbl br_join.11
  blt i n br_join.12
  bra end_of_input.end  # break
.bbl br_join.12
  ld pointer.7:A64 = s 0
  lea new_base.7:A64 = pointer.7 i
  ld deref.7:U8 = new_base.7 0
  mov c = deref.7
  add expr2.11:U64 = i 1:U64
  mov i = expr2.11
  bra _  # continue
.bbl _.end
.bbl _.1
  .reg U8 expr
  mov inl_arg:U8 = c
  blt inl_arg 48:U8 br_f.2
  blt 57:U8 inl_arg br_f.2
  mov expr = 1:U8
  bra end_expr.1
.bbl br_f.2
  mov expr = 0:U8
  bra end_expr.1
.bbl br_join.14
.bbl end_expr.1
  bne expr 0 br_join.13
  bra _.1.end  # break
.bbl br_join.13
  bne digits%1 0:S32 br_f.3
  beq c 48:U8 br_join.16
  mov imprecise = 1:U8
.bbl br_join.16
  add expr2.12:S32 = exp_adjustments 1:S32
  mov exp_adjustments = expr2.12
  bra br_join.15
.bbl br_f.3
  mul expr2.13:U64 = mant 10:U64
  mov mant = expr2.13
  .reg U8 expr.1
  mov inl_arg.1:U8 = c
  sub expr2.14:U8 = inl_arg.1 48:U8
  mov expr.1 = expr2.14
  bra end_expr.2
.bbl end_expr.2
  conv as:U64 = expr.1
  add expr2.15:U64 = mant as
  mov mant = expr2.15
  sub expr2.16:S32 = digits%1 1:S32
  mov digits%1 = expr2.16
.bbl br_join.15
  blt i n br_join.17
  bra end_of_input.end  # break
.bbl br_join.17
  ld pointer.8:A64 = s 0
  lea new_base.8:A64 = pointer.8 i
  ld deref.8:U8 = new_base.8 0
  mov c = deref.8
  add expr2.17:U64 = i 1:U64
  mov i = expr2.17
  bra _.1  # continue
.bbl _.1.end
  bne c 46:U8 br_join.18
  blt i n br_join.19
  bra end_of_input.end  # break
.bbl br_join.19
  ld pointer.9:A64 = s 0
  lea new_base.9:A64 = pointer.9 i
  ld deref.9:U8 = new_base.9 0
  mov c = deref.9
  add expr2.18:U64 = i 1:U64
  mov i = expr2.18
.bbl _.2
  .reg U8 expr.2
  mov inl_arg.2:U8 = c
  blt inl_arg.2 48:U8 br_f.4
  blt 57:U8 inl_arg.2 br_f.4
  mov expr.2 = 1:U8
  bra end_expr.3
.bbl br_f.4
  mov expr.2 = 0:U8
  bra end_expr.3
.bbl br_join.21
.bbl end_expr.3
  bne expr.2 0 br_join.20
  bra _.2.end  # break
.bbl br_join.20
  beq digits%1 0:S32 br_f.5
  mul expr2.19:U64 = mant 10:U64
  mov mant = expr2.19
  .reg U8 expr.3
  mov inl_arg.3:U8 = c
  sub expr2.20:U8 = inl_arg.3 48:U8
  mov expr.3 = expr2.20
  bra end_expr.4
.bbl end_expr.4
  conv as.1:U64 = expr.3
  add expr2.21:U64 = mant as.1
  mov mant = expr2.21
  sub expr2.22:S32 = exp_adjustments 1:S32
  mov exp_adjustments = expr2.22
  sub expr2.23:S32 = digits%1 1:S32
  mov digits%1 = expr2.23
  bra br_join.22
.bbl br_f.5
  beq c 48:U8 br_join.23
  mov imprecise = 1:U8
.bbl br_join.23
.bbl br_join.22
  blt i n br_join.24
  bra end_of_input.end  # break
.bbl br_join.24
  ld pointer.10:A64 = s 0
  lea new_base.10:A64 = pointer.10 i
  ld deref.10:U8 = new_base.10 0
  mov c = deref.10
  add expr2.24:U64 = i 1:U64
  mov i = expr2.24
  bra _.2  # continue
.bbl _.2.end
.bbl br_join.18
.bbl end_of_input.end
  bne c 101:U8 br_join.25
  blt i n br_join.26
  lea.mem lhsaddr.11:A64 = parse_real/ParseError 0
  .reg U64 copy.10
  ld copy.10 = lhsaddr.11 0
  st large_result 0 = copy.10
  ld copy.10 = lhsaddr.11 8
  st large_result 8 = copy.10
  ret
.bbl br_join.26
  ld pointer.11:A64 = s 0
  lea new_base.11:A64 = pointer.11 i
  ld deref.11:U8 = new_base.11 0
  mov c = deref.11
  add expr2.25:U64 = i 1:U64
  mov i = expr2.25
  mov negative%1:U8 = 0:U8
  beq c 45:U8 br_failed_or.3
  bne c 43:U8 br_join.27
.bbl br_failed_or.3
  bne c 45:U8 br_join.28
  mov negative%1 = 1:U8
.bbl br_join.28
  blt i n br_join.29
  lea.mem lhsaddr.12:A64 = parse_real/ParseError 0
  .reg U64 copy.11
  ld copy.11 = lhsaddr.12 0
  st large_result 0 = copy.11
  ld copy.11 = lhsaddr.12 8
  st large_result 8 = copy.11
  ret
.bbl br_join.29
  ld pointer.12:A64 = s 0
  lea new_base.12:A64 = pointer.12 i
  ld deref.12:U8 = new_base.12 0
  mov c = deref.12
  add expr2.26:U64 = i 1:U64
  mov i = expr2.26
.bbl br_join.27
.bbl _.3
  .reg U8 expr.4
  mov inl_arg.4:U8 = c
  blt inl_arg.4 48:U8 br_f.6
  blt 57:U8 inl_arg.4 br_f.6
  mov expr.4 = 1:U8
  bra end_expr.5
.bbl br_f.6
  mov expr.4 = 0:U8
  bra end_expr.5
.bbl br_join.31
.bbl end_expr.5
  bne expr.4 0 br_join.30
  bra _.3.end  # break
.bbl br_join.30
  mul expr2.27:S32 = exp 10:S32
  mov exp = expr2.27
  .reg U8 expr.5
  mov inl_arg.5:U8 = c
  sub expr2.28:U8 = inl_arg.5 48:U8
  mov expr.5 = expr2.28
  bra end_expr.6
.bbl end_expr.6
  conv as.2:S32 = expr.5
  add expr2.29:S32 = exp as.2
  mov exp = expr2.29
  blt i n br_join.32
  bra _.3.end  # break
.bbl br_join.32
  ld pointer.13:A64 = s 0
  lea new_base.13:A64 = pointer.13 i
  ld deref.13:U8 = new_base.13 0
  mov c = deref.13
  add expr2.30:U64 = i 1:U64
  mov i = expr2.30
  bra _.3  # continue
.bbl _.3.end
  beq negative%1 0 br_join.33
  sub expr1:S32 = 0 exp
  mov exp = expr1
.bbl br_join.33
.bbl br_join.25
  bne mant 0:U64 br_join.34
  .stk expr3_t.2 8 16
  lea.stk var_stk_base.5:A64 expr3_t.2 0
  st var_stk_base.5 0 = -0x0.0p+0:R64
  st var_stk_base.5 8 = i
  .stk expr3_f.2 8 16
  lea.stk var_stk_base.6:A64 expr3_f.2 0
  st var_stk_base.6 0 = 0x0.0p+0:R64
  st var_stk_base.6 8 = i
  beq negative 0 br_f.7
  lea.stk lhsaddr.13:A64 = expr3_t.2 0
  .reg U64 copy.12
  ld copy.12 = lhsaddr.13 0
  st large_result 0 = copy.12
  ld copy.12 = lhsaddr.13 8
  st large_result 8 = copy.12
  ret
.bbl br_f.7
  lea.stk lhsaddr.14:A64 = expr3_f.2 0
  .reg U64 copy.13
  ld copy.13 = lhsaddr.14 0
  st large_result 0 = copy.13
  ld copy.13 = lhsaddr.14 8
  st large_result 8 = copy.13
  ret
.bbl br_join.35
.bbl br_join.34
  add expr2.31:S32 = exp exp_adjustments
  mov exp = expr2.31
.bbl _.4
  rem expr2.32:U64 = mant 10:U64
  beq expr2.32 0:U64 br_join.36
  bra _.4.end  # break
.bbl br_join.36
  div expr2.33:U64 = mant 10:U64
  mov mant = expr2.33
  add expr2.34:S32 = exp 1:S32
  mov exp = expr2.34
  bra _.4  # continue
.bbl _.4.end
  pusharg negative
  pusharg exp
  pusharg mant
  bsr parse_real/r64_dec_fast_helper
  poparg call:R64
  mov complex_init_tmp:R64 = call
  st large_result 0 = complex_init_tmp
  st large_result 8 = i
  ret

.mem parse_real_test/u64_max 8 RO
.data 8 [255] # 0 8 u64

.mem parse_real_test/u32_max 4 RO
.data 4 [255] # 0 4 u32

.mem parse_real_test/REL_ERR1 8 RO
.data 1 "\x16V\xe7\x9e\xaf\x03\xc2<" # 0 8 r64


.fun parse_real_test/parse_r64 NORMAL [R64] = [A64]
.bbl entry
  poparg s:A64
  .stk x 8 16
  lea.stk var_stk_base:A64 x 0
  .stk arg0 8 16
  lea.stk var_stk_base.1:A64 arg0 0
  .reg U64 copy
  ld copy = s 0
  st var_stk_base.1 0 = copy
  ld copy = s 8
  st var_stk_base.1 8 = copy
  .stk result 8 16
  lea.stk lhsaddr:A64 = arg0 0
  lea.stk lhsaddr.1:A64 = result 0
  pusharg lhsaddr.1
  pusharg lhsaddr
  bsr parse_real/parse_r64
  lea.stk lhsaddr.2:A64 = result 0
  .reg U64 copy.1
  ld copy.1 = lhsaddr.2 0
  st var_stk_base 0 = copy.1
  ld copy.1 = lhsaddr.2 8
  st var_stk_base 8 = copy.1
  bra end_expr
.bbl end_expr
  lea.stk lhsaddr.3:A64 = x 0
  ld length:U64 = lhsaddr.3 8
  ld length.1:U64 = s 8
  beq length length.1 br_join
  .stk e_cond%1 8 16
  lea.stk var_stk_base.2:A64 e_cond%1 0
  lea.mem lhsaddr.4:A64 = $gen/global_val_3 0
  st var_stk_base.2 0 = lhsaddr.4
  st var_stk_base.2 8 = 5:U64
  .stk e_text%1 8 16
  lea.stk var_stk_base.3:A64 e_text%1 0
  lea.mem lhsaddr.5:A64 = $gen/global_val_7 0
  st var_stk_base.3 0 = lhsaddr.5
  st var_stk_base.3 8 = 29:U64
  lea.stk lhsaddr.6:A64 = e_cond%1 0
  ld pointer:A64 = lhsaddr.6 0
  pusharg 5:U64
  pusharg pointer
  bsr print_ln
  lea.stk lhsaddr.7:A64 = e_text%1 0
  ld pointer.1:A64 = lhsaddr.7 0
  pusharg 29:U64
  pusharg pointer.1
  bsr print_ln
  trap
.bbl br_join
  lea.stk lhsaddr.8:A64 = x 0
  ld value:R64 = lhsaddr.8 0
  pusharg value
  ret


.fun parse_real_test/test_nan NORMAL [] = []
.bbl entry
  .reg R64 expr
  .stk arg0 8 16
  lea.stk var_stk_base:A64 arg0 0
  lea.mem lhsaddr:A64 = $gen/global_val_8 0
  st var_stk_base 0 = lhsaddr
  st var_stk_base 8 = 4:U64
  lea.stk lhsaddr.1:A64 = arg0 0
  pusharg lhsaddr.1
  bsr parse_real_test/parse_r64
  poparg call:R64
  mov expr = call
  bra end_expr
.bbl end_expr
  mov a_val%1:R64 = expr
  bitcast bitcast:U64 = a_val%1
  beq 9218868437227405312:U64 bitcast br_join
  .stk msg_eval%1 8 16
  lea.stk var_stk_base.1:A64 msg_eval%1 0
  lea.mem lhsaddr.2:A64 = $gen/global_val_9 0
  st var_stk_base.1 0 = lhsaddr.2
  st var_stk_base.1 8 = 11:U64
  lea.stk lhsaddr.3:A64 = msg_eval%1 0
  ld pointer:A64 = lhsaddr.3 0
  pusharg 11:U64
  pusharg pointer
  pusharg 1:S32
  bsr write
  poparg call.1:S64
  .stk msg_eval%2 8 16
  lea.stk var_stk_base.2:A64 msg_eval%2 0
  lea.mem lhsaddr.4:A64 = $gen/global_val_10 0
  st var_stk_base.2 0 = lhsaddr.4
  st var_stk_base.2 8 = 11:U64
  lea.stk lhsaddr.5:A64 = msg_eval%2 0
  ld pointer.1:A64 = lhsaddr.5 0
  pusharg 11:U64
  pusharg pointer.1
  pusharg 1:S32
  bsr write
  poparg call.2:S64
  .stk msg_eval%3 8 16
  lea.stk var_stk_base.3:A64 msg_eval%3 0
  lea.mem lhsaddr.6:A64 = $gen/global_val_11 0
  st var_stk_base.3 0 = lhsaddr.6
  st var_stk_base.3 8 = 54:U64
  lea.stk lhsaddr.7:A64 = msg_eval%3 0
  ld pointer.2:A64 = lhsaddr.7 0
  pusharg 54:U64
  pusharg pointer.2
  pusharg 1:S32
  bsr write
  poparg call.3:S64
  .stk msg_eval%4 8 16
  lea.stk var_stk_base.4:A64 msg_eval%4 0
  lea.mem lhsaddr.8:A64 = $gen/global_val_12 0
  st var_stk_base.4 0 = lhsaddr.8
  st var_stk_base.4 8 = 2:U64
  lea.stk lhsaddr.9:A64 = msg_eval%4 0
  ld pointer.3:A64 = lhsaddr.9 0
  pusharg 2:U64
  pusharg pointer.3
  pusharg 1:S32
  bsr write
  poparg call.4:S64
  .stk msg_eval%5 8 16
  lea.stk var_stk_base.5:A64 msg_eval%5 0
  lea.mem lhsaddr.10:A64 = $gen/global_val_13 0
  st var_stk_base.5 0 = lhsaddr.10
  st var_stk_base.5 8 = 2:U64
  lea.stk lhsaddr.11:A64 = msg_eval%5 0
  ld pointer.4:A64 = lhsaddr.11 0
  pusharg 2:U64
  pusharg pointer.4
  pusharg 1:S32
  bsr write
  poparg call.5:S64
  .stk msg_eval%6 8 16
  lea.stk var_stk_base.6:A64 msg_eval%6 0
  lea.mem lhsaddr.12:A64 = $gen/global_val_14 0
  st var_stk_base.6 0 = lhsaddr.12
  st var_stk_base.6 8 = 4:U64
  lea.stk lhsaddr.13:A64 = msg_eval%6 0
  ld pointer.5:A64 = lhsaddr.13 0
  pusharg 4:U64
  pusharg pointer.5
  pusharg 1:S32
  bsr write
  poparg call.6:S64
  .stk msg_eval%7 8 16
  lea.stk var_stk_base.7:A64 msg_eval%7 0
  lea.mem lhsaddr.14:A64 = $gen/global_val_15 0
  st var_stk_base.7 0 = lhsaddr.14
  st var_stk_base.7 8 = 8:U64
  lea.stk lhsaddr.15:A64 = msg_eval%7 0
  ld pointer.6:A64 = lhsaddr.15 0
  pusharg 8:U64
  pusharg pointer.6
  pusharg 1:S32
  bsr write
  poparg call.7:S64
  .stk msg_eval%8 8 16
  lea.stk var_stk_base.8:A64 msg_eval%8 0
  lea.mem lhsaddr.16:A64 = $gen/global_val_16 0
  st var_stk_base.8 0 = lhsaddr.16
  st var_stk_base.8 8 = 4:U64
  lea.stk lhsaddr.17:A64 = msg_eval%8 0
  ld pointer.7:A64 = lhsaddr.17 0
  pusharg 4:U64
  pusharg pointer.7
  pusharg 1:S32
  bsr write
  poparg call.8:S64
  .stk msg_eval%9 8 16
  lea.stk var_stk_base.9:A64 msg_eval%9 0
  lea.mem lhsaddr.18:A64 = $gen/global_val_11 0
  st var_stk_base.9 0 = lhsaddr.18
  st var_stk_base.9 8 = 54:U64
  lea.stk lhsaddr.19:A64 = msg_eval%9 0
  ld pointer.8:A64 = lhsaddr.19 0
  pusharg 54:U64
  pusharg pointer.8
  pusharg 1:S32
  bsr write
  poparg call.9:S64
  .stk msg_eval%10 8 16
  lea.stk var_stk_base.10:A64 msg_eval%10 0
  lea.mem lhsaddr.20:A64 = $gen/global_val_17 0
  st var_stk_base.10 0 = lhsaddr.20
  st var_stk_base.10 8 = 1:U64
  lea.stk lhsaddr.21:A64 = msg_eval%10 0
  ld pointer.9:A64 = lhsaddr.21 0
  pusharg 1:U64
  pusharg pointer.9
  pusharg 1:S32
  bsr write
  poparg call.10:S64
  trap
.bbl br_join
  .reg R64 expr.1
  .stk arg0.1 8 16
  lea.stk var_stk_base.11:A64 arg0.1 0
  lea.mem lhsaddr.22:A64 = $gen/global_val_18 0
  st var_stk_base.11 0 = lhsaddr.22
  st var_stk_base.11 8 = 4:U64
  lea.stk lhsaddr.23:A64 = arg0.1 0
  pusharg lhsaddr.23
  bsr parse_real_test/parse_r64
  poparg call.11:R64
  mov expr.1 = call.11
  bra end_expr.1
.bbl end_expr.1
  mov a_val%3:R64 = expr.1
  bitcast bitcast.1:U64 = a_val%3
  beq 18442240474082181120:U64 bitcast.1 br_join.1
  .stk msg_eval%11 8 16
  lea.stk var_stk_base.12:A64 msg_eval%11 0
  lea.mem lhsaddr.24:A64 = $gen/global_val_9 0
  st var_stk_base.12 0 = lhsaddr.24
  st var_stk_base.12 8 = 11:U64
  lea.stk lhsaddr.25:A64 = msg_eval%11 0
  ld pointer.10:A64 = lhsaddr.25 0
  pusharg 11:U64
  pusharg pointer.10
  pusharg 1:S32
  bsr write
  poparg call.12:S64
  .stk msg_eval%12 8 16
  lea.stk var_stk_base.13:A64 msg_eval%12 0
  lea.mem lhsaddr.26:A64 = $gen/global_val_10 0
  st var_stk_base.13 0 = lhsaddr.26
  st var_stk_base.13 8 = 11:U64
  lea.stk lhsaddr.27:A64 = msg_eval%12 0
  ld pointer.11:A64 = lhsaddr.27 0
  pusharg 11:U64
  pusharg pointer.11
  pusharg 1:S32
  bsr write
  poparg call.13:S64
  .stk msg_eval%13 8 16
  lea.stk var_stk_base.14:A64 msg_eval%13 0
  lea.mem lhsaddr.28:A64 = $gen/global_val_19 0
  st var_stk_base.14 0 = lhsaddr.28
  st var_stk_base.14 8 = 54:U64
  lea.stk lhsaddr.29:A64 = msg_eval%13 0
  ld pointer.12:A64 = lhsaddr.29 0
  pusharg 54:U64
  pusharg pointer.12
  pusharg 1:S32
  bsr write
  poparg call.14:S64
  .stk msg_eval%14 8 16
  lea.stk var_stk_base.15:A64 msg_eval%14 0
  lea.mem lhsaddr.30:A64 = $gen/global_val_12 0
  st var_stk_base.15 0 = lhsaddr.30
  st var_stk_base.15 8 = 2:U64
  lea.stk lhsaddr.31:A64 = msg_eval%14 0
  ld pointer.13:A64 = lhsaddr.31 0
  pusharg 2:U64
  pusharg pointer.13
  pusharg 1:S32
  bsr write
  poparg call.15:S64
  .stk msg_eval%15 8 16
  lea.stk var_stk_base.16:A64 msg_eval%15 0
  lea.mem lhsaddr.32:A64 = $gen/global_val_13 0
  st var_stk_base.16 0 = lhsaddr.32
  st var_stk_base.16 8 = 2:U64
  lea.stk lhsaddr.33:A64 = msg_eval%15 0
  ld pointer.14:A64 = lhsaddr.33 0
  pusharg 2:U64
  pusharg pointer.14
  pusharg 1:S32
  bsr write
  poparg call.16:S64
  .stk msg_eval%16 8 16
  lea.stk var_stk_base.17:A64 msg_eval%16 0
  lea.mem lhsaddr.34:A64 = $gen/global_val_14 0
  st var_stk_base.17 0 = lhsaddr.34
  st var_stk_base.17 8 = 4:U64
  lea.stk lhsaddr.35:A64 = msg_eval%16 0
  ld pointer.15:A64 = lhsaddr.35 0
  pusharg 4:U64
  pusharg pointer.15
  pusharg 1:S32
  bsr write
  poparg call.17:S64
  .stk msg_eval%17 8 16
  lea.stk var_stk_base.18:A64 msg_eval%17 0
  lea.mem lhsaddr.36:A64 = $gen/global_val_15 0
  st var_stk_base.18 0 = lhsaddr.36
  st var_stk_base.18 8 = 8:U64
  lea.stk lhsaddr.37:A64 = msg_eval%17 0
  ld pointer.16:A64 = lhsaddr.37 0
  pusharg 8:U64
  pusharg pointer.16
  pusharg 1:S32
  bsr write
  poparg call.18:S64
  .stk msg_eval%18 8 16
  lea.stk var_stk_base.19:A64 msg_eval%18 0
  lea.mem lhsaddr.38:A64 = $gen/global_val_16 0
  st var_stk_base.19 0 = lhsaddr.38
  st var_stk_base.19 8 = 4:U64
  lea.stk lhsaddr.39:A64 = msg_eval%18 0
  ld pointer.17:A64 = lhsaddr.39 0
  pusharg 4:U64
  pusharg pointer.17
  pusharg 1:S32
  bsr write
  poparg call.19:S64
  .stk msg_eval%19 8 16
  lea.stk var_stk_base.20:A64 msg_eval%19 0
  lea.mem lhsaddr.40:A64 = $gen/global_val_19 0
  st var_stk_base.20 0 = lhsaddr.40
  st var_stk_base.20 8 = 54:U64
  lea.stk lhsaddr.41:A64 = msg_eval%19 0
  ld pointer.18:A64 = lhsaddr.41 0
  pusharg 54:U64
  pusharg pointer.18
  pusharg 1:S32
  bsr write
  poparg call.20:S64
  .stk msg_eval%20 8 16
  lea.stk var_stk_base.21:A64 msg_eval%20 0
  lea.mem lhsaddr.42:A64 = $gen/global_val_17 0
  st var_stk_base.21 0 = lhsaddr.42
  st var_stk_base.21 8 = 1:U64
  lea.stk lhsaddr.43:A64 = msg_eval%20 0
  ld pointer.19:A64 = lhsaddr.43 0
  pusharg 1:U64
  pusharg pointer.19
  pusharg 1:S32
  bsr write
  poparg call.21:S64
  trap
.bbl br_join.1
.bbl br_join.2
  .reg R64 expr.2
  .stk arg0.2 8 16
  lea.stk var_stk_base.22:A64 arg0.2 0
  lea.mem lhsaddr.44:A64 = $gen/global_val_20 0
  st var_stk_base.22 0 = lhsaddr.44
  st var_stk_base.22 8 = 4:U64
  lea.stk lhsaddr.45:A64 = arg0.2 0
  pusharg lhsaddr.45
  bsr parse_real_test/parse_r64
  poparg call.22:R64
  mov expr.2 = call.22
  bra end_expr.2
.bbl end_expr.2
  mov a_val%7:R64 = expr.2
  bitcast bitcast.2:U64 = a_val%7
  beq 9221120237041090560:U64 bitcast.2 br_join.3
  .stk msg_eval%31 8 16
  lea.stk var_stk_base.23:A64 msg_eval%31 0
  lea.mem lhsaddr.46:A64 = $gen/global_val_9 0
  st var_stk_base.23 0 = lhsaddr.46
  st var_stk_base.23 8 = 11:U64
  lea.stk lhsaddr.47:A64 = msg_eval%31 0
  ld pointer.20:A64 = lhsaddr.47 0
  pusharg 11:U64
  pusharg pointer.20
  pusharg 1:S32
  bsr write
  poparg call.23:S64
  .stk msg_eval%32 8 16
  lea.stk var_stk_base.24:A64 msg_eval%32 0
  lea.mem lhsaddr.48:A64 = $gen/global_val_10 0
  st var_stk_base.24 0 = lhsaddr.48
  st var_stk_base.24 8 = 11:U64
  lea.stk lhsaddr.49:A64 = msg_eval%32 0
  ld pointer.21:A64 = lhsaddr.49 0
  pusharg 11:U64
  pusharg pointer.21
  pusharg 1:S32
  bsr write
  poparg call.24:S64
  .stk msg_eval%33 8 16
  lea.stk var_stk_base.25:A64 msg_eval%33 0
  lea.mem lhsaddr.50:A64 = $gen/global_val_21 0
  st var_stk_base.25 0 = lhsaddr.50
  st var_stk_base.25 8 = 54:U64
  lea.stk lhsaddr.51:A64 = msg_eval%33 0
  ld pointer.22:A64 = lhsaddr.51 0
  pusharg 54:U64
  pusharg pointer.22
  pusharg 1:S32
  bsr write
  poparg call.25:S64
  .stk msg_eval%34 8 16
  lea.stk var_stk_base.26:A64 msg_eval%34 0
  lea.mem lhsaddr.52:A64 = $gen/global_val_12 0
  st var_stk_base.26 0 = lhsaddr.52
  st var_stk_base.26 8 = 2:U64
  lea.stk lhsaddr.53:A64 = msg_eval%34 0
  ld pointer.23:A64 = lhsaddr.53 0
  pusharg 2:U64
  pusharg pointer.23
  pusharg 1:S32
  bsr write
  poparg call.26:S64
  .stk msg_eval%35 8 16
  lea.stk var_stk_base.27:A64 msg_eval%35 0
  lea.mem lhsaddr.54:A64 = $gen/global_val_13 0
  st var_stk_base.27 0 = lhsaddr.54
  st var_stk_base.27 8 = 2:U64
  lea.stk lhsaddr.55:A64 = msg_eval%35 0
  ld pointer.24:A64 = lhsaddr.55 0
  pusharg 2:U64
  pusharg pointer.24
  pusharg 1:S32
  bsr write
  poparg call.27:S64
  .stk msg_eval%36 8 16
  lea.stk var_stk_base.28:A64 msg_eval%36 0
  lea.mem lhsaddr.56:A64 = $gen/global_val_14 0
  st var_stk_base.28 0 = lhsaddr.56
  st var_stk_base.28 8 = 4:U64
  lea.stk lhsaddr.57:A64 = msg_eval%36 0
  ld pointer.25:A64 = lhsaddr.57 0
  pusharg 4:U64
  pusharg pointer.25
  pusharg 1:S32
  bsr write
  poparg call.28:S64
  .stk msg_eval%37 8 16
  lea.stk var_stk_base.29:A64 msg_eval%37 0
  lea.mem lhsaddr.58:A64 = $gen/global_val_15 0
  st var_stk_base.29 0 = lhsaddr.58
  st var_stk_base.29 8 = 8:U64
  lea.stk lhsaddr.59:A64 = msg_eval%37 0
  ld pointer.26:A64 = lhsaddr.59 0
  pusharg 8:U64
  pusharg pointer.26
  pusharg 1:S32
  bsr write
  poparg call.29:S64
  .stk msg_eval%38 8 16
  lea.stk var_stk_base.30:A64 msg_eval%38 0
  lea.mem lhsaddr.60:A64 = $gen/global_val_16 0
  st var_stk_base.30 0 = lhsaddr.60
  st var_stk_base.30 8 = 4:U64
  lea.stk lhsaddr.61:A64 = msg_eval%38 0
  ld pointer.27:A64 = lhsaddr.61 0
  pusharg 4:U64
  pusharg pointer.27
  pusharg 1:S32
  bsr write
  poparg call.30:S64
  .stk msg_eval%39 8 16
  lea.stk var_stk_base.31:A64 msg_eval%39 0
  lea.mem lhsaddr.62:A64 = $gen/global_val_21 0
  st var_stk_base.31 0 = lhsaddr.62
  st var_stk_base.31 8 = 54:U64
  lea.stk lhsaddr.63:A64 = msg_eval%39 0
  ld pointer.28:A64 = lhsaddr.63 0
  pusharg 54:U64
  pusharg pointer.28
  pusharg 1:S32
  bsr write
  poparg call.31:S64
  .stk msg_eval%40 8 16
  lea.stk var_stk_base.32:A64 msg_eval%40 0
  lea.mem lhsaddr.64:A64 = $gen/global_val_17 0
  st var_stk_base.32 0 = lhsaddr.64
  st var_stk_base.32 8 = 1:U64
  lea.stk lhsaddr.65:A64 = msg_eval%40 0
  ld pointer.29:A64 = lhsaddr.65 0
  pusharg 1:U64
  pusharg pointer.29
  pusharg 1:S32
  bsr write
  poparg call.32:S64
  trap
.bbl br_join.3
  .reg R64 expr.3
  .stk arg0.3 8 16
  lea.stk var_stk_base.33:A64 arg0.3 0
  lea.mem lhsaddr.66:A64 = $gen/global_val_22 0
  st var_stk_base.33 0 = lhsaddr.66
  st var_stk_base.33 8 = 4:U64
  lea.stk lhsaddr.67:A64 = arg0.3 0
  pusharg lhsaddr.67
  bsr parse_real_test/parse_r64
  poparg call.33:R64
  mov expr.3 = call.33
  bra end_expr.3
.bbl end_expr.3
  mov a_val%9:R64 = expr.3
  bitcast bitcast.3:U64 = a_val%9
  beq 18444492273895866368:U64 bitcast.3 br_join.4
  .stk msg_eval%41 8 16
  lea.stk var_stk_base.34:A64 msg_eval%41 0
  lea.mem lhsaddr.68:A64 = $gen/global_val_9 0
  st var_stk_base.34 0 = lhsaddr.68
  st var_stk_base.34 8 = 11:U64
  lea.stk lhsaddr.69:A64 = msg_eval%41 0
  ld pointer.30:A64 = lhsaddr.69 0
  pusharg 11:U64
  pusharg pointer.30
  pusharg 1:S32
  bsr write
  poparg call.34:S64
  .stk msg_eval%42 8 16
  lea.stk var_stk_base.35:A64 msg_eval%42 0
  lea.mem lhsaddr.70:A64 = $gen/global_val_10 0
  st var_stk_base.35 0 = lhsaddr.70
  st var_stk_base.35 8 = 11:U64
  lea.stk lhsaddr.71:A64 = msg_eval%42 0
  ld pointer.31:A64 = lhsaddr.71 0
  pusharg 11:U64
  pusharg pointer.31
  pusharg 1:S32
  bsr write
  poparg call.35:S64
  .stk msg_eval%43 8 16
  lea.stk var_stk_base.36:A64 msg_eval%43 0
  lea.mem lhsaddr.72:A64 = $gen/global_val_23 0
  st var_stk_base.36 0 = lhsaddr.72
  st var_stk_base.36 8 = 54:U64
  lea.stk lhsaddr.73:A64 = msg_eval%43 0
  ld pointer.32:A64 = lhsaddr.73 0
  pusharg 54:U64
  pusharg pointer.32
  pusharg 1:S32
  bsr write
  poparg call.36:S64
  .stk msg_eval%44 8 16
  lea.stk var_stk_base.37:A64 msg_eval%44 0
  lea.mem lhsaddr.74:A64 = $gen/global_val_12 0
  st var_stk_base.37 0 = lhsaddr.74
  st var_stk_base.37 8 = 2:U64
  lea.stk lhsaddr.75:A64 = msg_eval%44 0
  ld pointer.33:A64 = lhsaddr.75 0
  pusharg 2:U64
  pusharg pointer.33
  pusharg 1:S32
  bsr write
  poparg call.37:S64
  .stk msg_eval%45 8 16
  lea.stk var_stk_base.38:A64 msg_eval%45 0
  lea.mem lhsaddr.76:A64 = $gen/global_val_13 0
  st var_stk_base.38 0 = lhsaddr.76
  st var_stk_base.38 8 = 2:U64
  lea.stk lhsaddr.77:A64 = msg_eval%45 0
  ld pointer.34:A64 = lhsaddr.77 0
  pusharg 2:U64
  pusharg pointer.34
  pusharg 1:S32
  bsr write
  poparg call.38:S64
  .stk msg_eval%46 8 16
  lea.stk var_stk_base.39:A64 msg_eval%46 0
  lea.mem lhsaddr.78:A64 = $gen/global_val_14 0
  st var_stk_base.39 0 = lhsaddr.78
  st var_stk_base.39 8 = 4:U64
  lea.stk lhsaddr.79:A64 = msg_eval%46 0
  ld pointer.35:A64 = lhsaddr.79 0
  pusharg 4:U64
  pusharg pointer.35
  pusharg 1:S32
  bsr write
  poparg call.39:S64
  .stk msg_eval%47 8 16
  lea.stk var_stk_base.40:A64 msg_eval%47 0
  lea.mem lhsaddr.80:A64 = $gen/global_val_15 0
  st var_stk_base.40 0 = lhsaddr.80
  st var_stk_base.40 8 = 8:U64
  lea.stk lhsaddr.81:A64 = msg_eval%47 0
  ld pointer.36:A64 = lhsaddr.81 0
  pusharg 8:U64
  pusharg pointer.36
  pusharg 1:S32
  bsr write
  poparg call.40:S64
  .stk msg_eval%48 8 16
  lea.stk var_stk_base.41:A64 msg_eval%48 0
  lea.mem lhsaddr.82:A64 = $gen/global_val_16 0
  st var_stk_base.41 0 = lhsaddr.82
  st var_stk_base.41 8 = 4:U64
  lea.stk lhsaddr.83:A64 = msg_eval%48 0
  ld pointer.37:A64 = lhsaddr.83 0
  pusharg 4:U64
  pusharg pointer.37
  pusharg 1:S32
  bsr write
  poparg call.41:S64
  .stk msg_eval%49 8 16
  lea.stk var_stk_base.42:A64 msg_eval%49 0
  lea.mem lhsaddr.84:A64 = $gen/global_val_23 0
  st var_stk_base.42 0 = lhsaddr.84
  st var_stk_base.42 8 = 54:U64
  lea.stk lhsaddr.85:A64 = msg_eval%49 0
  ld pointer.38:A64 = lhsaddr.85 0
  pusharg 54:U64
  pusharg pointer.38
  pusharg 1:S32
  bsr write
  poparg call.42:S64
  .stk msg_eval%50 8 16
  lea.stk var_stk_base.43:A64 msg_eval%50 0
  lea.mem lhsaddr.86:A64 = $gen/global_val_17 0
  st var_stk_base.43 0 = lhsaddr.86
  st var_stk_base.43 8 = 1:U64
  lea.stk lhsaddr.87:A64 = msg_eval%50 0
  ld pointer.39:A64 = lhsaddr.87 0
  pusharg 1:U64
  pusharg pointer.39
  pusharg 1:S32
  bsr write
  poparg call.43:S64
  trap
.bbl br_join.4
.bbl br_join.5
  ret


.fun parse_real_test/test_dec NORMAL [] = []
.bbl entry
.bbl br_join
  .reg R64 expr
  .stk arg0 8 16
  lea.stk var_stk_base:A64 arg0 0
  lea.mem lhsaddr:A64 = $gen/global_val_24 0
  st var_stk_base 0 = lhsaddr
  st var_stk_base 8 = 1:U64
  lea.stk lhsaddr.1:A64 = arg0 0
  pusharg lhsaddr.1
  bsr parse_real_test/parse_r64
  poparg call:R64
  mov expr = call
  bra end_expr
.bbl end_expr
  mov a_val%3:R64 = expr
  bitcast bitcast:U64 = a_val%3
  beq 0:U64 bitcast br_join.1
  .stk msg_eval%11 8 16
  lea.stk var_stk_base.1:A64 msg_eval%11 0
  lea.mem lhsaddr.2:A64 = $gen/global_val_9 0
  st var_stk_base.1 0 = lhsaddr.2
  st var_stk_base.1 8 = 11:U64
  lea.stk lhsaddr.3:A64 = msg_eval%11 0
  ld pointer:A64 = lhsaddr.3 0
  pusharg 11:U64
  pusharg pointer
  pusharg 1:S32
  bsr write
  poparg call.1:S64
  .stk msg_eval%12 8 16
  lea.stk var_stk_base.2:A64 msg_eval%12 0
  lea.mem lhsaddr.4:A64 = $gen/global_val_10 0
  st var_stk_base.2 0 = lhsaddr.4
  st var_stk_base.2 8 = 11:U64
  lea.stk lhsaddr.5:A64 = msg_eval%12 0
  ld pointer.1:A64 = lhsaddr.5 0
  pusharg 11:U64
  pusharg pointer.1
  pusharg 1:S32
  bsr write
  poparg call.2:S64
  .stk msg_eval%13 8 16
  lea.stk var_stk_base.3:A64 msg_eval%13 0
  lea.mem lhsaddr.6:A64 = $gen/global_val_25 0
  st var_stk_base.3 0 = lhsaddr.6
  st var_stk_base.3 8 = 54:U64
  lea.stk lhsaddr.7:A64 = msg_eval%13 0
  ld pointer.2:A64 = lhsaddr.7 0
  pusharg 54:U64
  pusharg pointer.2
  pusharg 1:S32
  bsr write
  poparg call.3:S64
  .stk msg_eval%14 8 16
  lea.stk var_stk_base.4:A64 msg_eval%14 0
  lea.mem lhsaddr.8:A64 = $gen/global_val_12 0
  st var_stk_base.4 0 = lhsaddr.8
  st var_stk_base.4 8 = 2:U64
  lea.stk lhsaddr.9:A64 = msg_eval%14 0
  ld pointer.3:A64 = lhsaddr.9 0
  pusharg 2:U64
  pusharg pointer.3
  pusharg 1:S32
  bsr write
  poparg call.4:S64
  .stk msg_eval%15 8 16
  lea.stk var_stk_base.5:A64 msg_eval%15 0
  lea.mem lhsaddr.10:A64 = $gen/global_val_26 0
  st var_stk_base.5 0 = lhsaddr.10
  st var_stk_base.5 8 = 6:U64
  lea.stk lhsaddr.11:A64 = msg_eval%15 0
  ld pointer.4:A64 = lhsaddr.11 0
  pusharg 6:U64
  pusharg pointer.4
  pusharg 1:S32
  bsr write
  poparg call.5:S64
  .stk msg_eval%16 8 16
  lea.stk var_stk_base.6:A64 msg_eval%16 0
  lea.mem lhsaddr.12:A64 = $gen/global_val_14 0
  st var_stk_base.6 0 = lhsaddr.12
  st var_stk_base.6 8 = 4:U64
  lea.stk lhsaddr.13:A64 = msg_eval%16 0
  ld pointer.5:A64 = lhsaddr.13 0
  pusharg 4:U64
  pusharg pointer.5
  pusharg 1:S32
  bsr write
  poparg call.6:S64
  .stk msg_eval%17 8 16
  lea.stk var_stk_base.7:A64 msg_eval%17 0
  lea.mem lhsaddr.14:A64 = $gen/global_val_15 0
  st var_stk_base.7 0 = lhsaddr.14
  st var_stk_base.7 8 = 8:U64
  lea.stk lhsaddr.15:A64 = msg_eval%17 0
  ld pointer.6:A64 = lhsaddr.15 0
  pusharg 8:U64
  pusharg pointer.6
  pusharg 1:S32
  bsr write
  poparg call.7:S64
  .stk msg_eval%18 8 16
  lea.stk var_stk_base.8:A64 msg_eval%18 0
  lea.mem lhsaddr.16:A64 = $gen/global_val_16 0
  st var_stk_base.8 0 = lhsaddr.16
  st var_stk_base.8 8 = 4:U64
  lea.stk lhsaddr.17:A64 = msg_eval%18 0
  ld pointer.7:A64 = lhsaddr.17 0
  pusharg 4:U64
  pusharg pointer.7
  pusharg 1:S32
  bsr write
  poparg call.8:S64
  .stk msg_eval%19 8 16
  lea.stk var_stk_base.9:A64 msg_eval%19 0
  lea.mem lhsaddr.18:A64 = $gen/global_val_25 0
  st var_stk_base.9 0 = lhsaddr.18
  st var_stk_base.9 8 = 54:U64
  lea.stk lhsaddr.19:A64 = msg_eval%19 0
  ld pointer.8:A64 = lhsaddr.19 0
  pusharg 54:U64
  pusharg pointer.8
  pusharg 1:S32
  bsr write
  poparg call.9:S64
  .stk msg_eval%20 8 16
  lea.stk var_stk_base.10:A64 msg_eval%20 0
  lea.mem lhsaddr.20:A64 = $gen/global_val_17 0
  st var_stk_base.10 0 = lhsaddr.20
  st var_stk_base.10 8 = 1:U64
  lea.stk lhsaddr.21:A64 = msg_eval%20 0
  ld pointer.9:A64 = lhsaddr.21 0
  pusharg 1:U64
  pusharg pointer.9
  pusharg 1:S32
  bsr write
  poparg call.10:S64
  trap
.bbl br_join.1
  .reg R64 expr.1
  .stk arg0.1 8 16
  lea.stk var_stk_base.11:A64 arg0.1 0
  lea.mem lhsaddr.22:A64 = $gen/global_val_27 0
  st var_stk_base.11 0 = lhsaddr.22
  st var_stk_base.11 8 = 2:U64
  lea.stk lhsaddr.23:A64 = arg0.1 0
  pusharg lhsaddr.23
  bsr parse_real_test/parse_r64
  poparg call.11:R64
  mov expr.1 = call.11
  bra end_expr.1
.bbl end_expr.1
  mov a_val%5:R64 = expr.1
  bitcast bitcast.1:U64 = a_val%5
  beq 0:U64 bitcast.1 br_join.2
  .stk msg_eval%21 8 16
  lea.stk var_stk_base.12:A64 msg_eval%21 0
  lea.mem lhsaddr.24:A64 = $gen/global_val_9 0
  st var_stk_base.12 0 = lhsaddr.24
  st var_stk_base.12 8 = 11:U64
  lea.stk lhsaddr.25:A64 = msg_eval%21 0
  ld pointer.10:A64 = lhsaddr.25 0
  pusharg 11:U64
  pusharg pointer.10
  pusharg 1:S32
  bsr write
  poparg call.12:S64
  .stk msg_eval%22 8 16
  lea.stk var_stk_base.13:A64 msg_eval%22 0
  lea.mem lhsaddr.26:A64 = $gen/global_val_10 0
  st var_stk_base.13 0 = lhsaddr.26
  st var_stk_base.13 8 = 11:U64
  lea.stk lhsaddr.27:A64 = msg_eval%22 0
  ld pointer.11:A64 = lhsaddr.27 0
  pusharg 11:U64
  pusharg pointer.11
  pusharg 1:S32
  bsr write
  poparg call.13:S64
  .stk msg_eval%23 8 16
  lea.stk var_stk_base.14:A64 msg_eval%23 0
  lea.mem lhsaddr.28:A64 = $gen/global_val_28 0
  st var_stk_base.14 0 = lhsaddr.28
  st var_stk_base.14 8 = 54:U64
  lea.stk lhsaddr.29:A64 = msg_eval%23 0
  ld pointer.12:A64 = lhsaddr.29 0
  pusharg 54:U64
  pusharg pointer.12
  pusharg 1:S32
  bsr write
  poparg call.14:S64
  .stk msg_eval%24 8 16
  lea.stk var_stk_base.15:A64 msg_eval%24 0
  lea.mem lhsaddr.30:A64 = $gen/global_val_12 0
  st var_stk_base.15 0 = lhsaddr.30
  st var_stk_base.15 8 = 2:U64
  lea.stk lhsaddr.31:A64 = msg_eval%24 0
  ld pointer.13:A64 = lhsaddr.31 0
  pusharg 2:U64
  pusharg pointer.13
  pusharg 1:S32
  bsr write
  poparg call.15:S64
  .stk msg_eval%25 8 16
  lea.stk var_stk_base.16:A64 msg_eval%25 0
  lea.mem lhsaddr.32:A64 = $gen/global_val_26 0
  st var_stk_base.16 0 = lhsaddr.32
  st var_stk_base.16 8 = 6:U64
  lea.stk lhsaddr.33:A64 = msg_eval%25 0
  ld pointer.14:A64 = lhsaddr.33 0
  pusharg 6:U64
  pusharg pointer.14
  pusharg 1:S32
  bsr write
  poparg call.16:S64
  .stk msg_eval%26 8 16
  lea.stk var_stk_base.17:A64 msg_eval%26 0
  lea.mem lhsaddr.34:A64 = $gen/global_val_14 0
  st var_stk_base.17 0 = lhsaddr.34
  st var_stk_base.17 8 = 4:U64
  lea.stk lhsaddr.35:A64 = msg_eval%26 0
  ld pointer.15:A64 = lhsaddr.35 0
  pusharg 4:U64
  pusharg pointer.15
  pusharg 1:S32
  bsr write
  poparg call.17:S64
  .stk msg_eval%27 8 16
  lea.stk var_stk_base.18:A64 msg_eval%27 0
  lea.mem lhsaddr.36:A64 = $gen/global_val_15 0
  st var_stk_base.18 0 = lhsaddr.36
  st var_stk_base.18 8 = 8:U64
  lea.stk lhsaddr.37:A64 = msg_eval%27 0
  ld pointer.16:A64 = lhsaddr.37 0
  pusharg 8:U64
  pusharg pointer.16
  pusharg 1:S32
  bsr write
  poparg call.18:S64
  .stk msg_eval%28 8 16
  lea.stk var_stk_base.19:A64 msg_eval%28 0
  lea.mem lhsaddr.38:A64 = $gen/global_val_16 0
  st var_stk_base.19 0 = lhsaddr.38
  st var_stk_base.19 8 = 4:U64
  lea.stk lhsaddr.39:A64 = msg_eval%28 0
  ld pointer.17:A64 = lhsaddr.39 0
  pusharg 4:U64
  pusharg pointer.17
  pusharg 1:S32
  bsr write
  poparg call.19:S64
  .stk msg_eval%29 8 16
  lea.stk var_stk_base.20:A64 msg_eval%29 0
  lea.mem lhsaddr.40:A64 = $gen/global_val_28 0
  st var_stk_base.20 0 = lhsaddr.40
  st var_stk_base.20 8 = 54:U64
  lea.stk lhsaddr.41:A64 = msg_eval%29 0
  ld pointer.18:A64 = lhsaddr.41 0
  pusharg 54:U64
  pusharg pointer.18
  pusharg 1:S32
  bsr write
  poparg call.20:S64
  .stk msg_eval%30 8 16
  lea.stk var_stk_base.21:A64 msg_eval%30 0
  lea.mem lhsaddr.42:A64 = $gen/global_val_17 0
  st var_stk_base.21 0 = lhsaddr.42
  st var_stk_base.21 8 = 1:U64
  lea.stk lhsaddr.43:A64 = msg_eval%30 0
  ld pointer.19:A64 = lhsaddr.43 0
  pusharg 1:U64
  pusharg pointer.19
  pusharg 1:S32
  bsr write
  poparg call.21:S64
  trap
.bbl br_join.2
  .reg R64 expr.2
  .stk arg0.2 8 16
  lea.stk var_stk_base.22:A64 arg0.2 0
  lea.mem lhsaddr.44:A64 = $gen/global_val_29 0
  st var_stk_base.22 0 = lhsaddr.44
  st var_stk_base.22 8 = 2:U64
  lea.stk lhsaddr.45:A64 = arg0.2 0
  pusharg lhsaddr.45
  bsr parse_real_test/parse_r64
  poparg call.22:R64
  mov expr.2 = call.22
  bra end_expr.2
.bbl end_expr.2
  mov a_val%7:R64 = expr.2
  beq -0x0.0p+0:R64 a_val%7 br_join.3
  .stk msg_eval%31 8 16
  lea.stk var_stk_base.23:A64 msg_eval%31 0
  lea.mem lhsaddr.46:A64 = $gen/global_val_30 0
  st var_stk_base.23 0 = lhsaddr.46
  st var_stk_base.23 8 = 8:U64
  lea.stk lhsaddr.47:A64 = msg_eval%31 0
  ld pointer.20:A64 = lhsaddr.47 0
  pusharg 8:U64
  pusharg pointer.20
  pusharg 1:S32
  bsr write
  poparg call.23:S64
  .stk msg_eval%32 8 16
  lea.stk var_stk_base.24:A64 msg_eval%32 0
  lea.mem lhsaddr.48:A64 = $gen/global_val_10 0
  st var_stk_base.24 0 = lhsaddr.48
  st var_stk_base.24 8 = 11:U64
  lea.stk lhsaddr.49:A64 = msg_eval%32 0
  ld pointer.21:A64 = lhsaddr.49 0
  pusharg 11:U64
  pusharg pointer.21
  pusharg 1:S32
  bsr write
  poparg call.24:S64
  .stk msg_eval%33 8 16
  lea.stk var_stk_base.25:A64 msg_eval%33 0
  lea.mem lhsaddr.50:A64 = $gen/global_val_31 0
  st var_stk_base.25 0 = lhsaddr.50
  st var_stk_base.25 8 = 54:U64
  lea.stk lhsaddr.51:A64 = msg_eval%33 0
  ld pointer.22:A64 = lhsaddr.51 0
  pusharg 54:U64
  pusharg pointer.22
  pusharg 1:S32
  bsr write
  poparg call.25:S64
  .stk msg_eval%34 8 16
  lea.stk var_stk_base.26:A64 msg_eval%34 0
  lea.mem lhsaddr.52:A64 = $gen/global_val_12 0
  st var_stk_base.26 0 = lhsaddr.52
  st var_stk_base.26 8 = 2:U64
  lea.stk lhsaddr.53:A64 = msg_eval%34 0
  ld pointer.23:A64 = lhsaddr.53 0
  pusharg 2:U64
  pusharg pointer.23
  pusharg 1:S32
  bsr write
  poparg call.26:S64
  .stk msg_eval%35 8 16
  lea.stk var_stk_base.27:A64 msg_eval%35 0
  lea.mem lhsaddr.54:A64 = $gen/global_val_26 0
  st var_stk_base.27 0 = lhsaddr.54
  st var_stk_base.27 8 = 6:U64
  lea.stk lhsaddr.55:A64 = msg_eval%35 0
  ld pointer.24:A64 = lhsaddr.55 0
  pusharg 6:U64
  pusharg pointer.24
  pusharg 1:S32
  bsr write
  poparg call.27:S64
  .stk msg_eval%36 8 16
  lea.stk var_stk_base.28:A64 msg_eval%36 0
  lea.mem lhsaddr.56:A64 = $gen/global_val_14 0
  st var_stk_base.28 0 = lhsaddr.56
  st var_stk_base.28 8 = 4:U64
  lea.stk lhsaddr.57:A64 = msg_eval%36 0
  ld pointer.25:A64 = lhsaddr.57 0
  pusharg 4:U64
  pusharg pointer.25
  pusharg 1:S32
  bsr write
  poparg call.28:S64
  .stk msg_eval%37 8 16
  lea.stk var_stk_base.29:A64 msg_eval%37 0
  lea.mem lhsaddr.58:A64 = $gen/global_val_15 0
  st var_stk_base.29 0 = lhsaddr.58
  st var_stk_base.29 8 = 8:U64
  lea.stk lhsaddr.59:A64 = msg_eval%37 0
  ld pointer.26:A64 = lhsaddr.59 0
  pusharg 8:U64
  pusharg pointer.26
  pusharg 1:S32
  bsr write
  poparg call.29:S64
  .stk msg_eval%38 8 16
  lea.stk var_stk_base.30:A64 msg_eval%38 0
  lea.mem lhsaddr.60:A64 = $gen/global_val_16 0
  st var_stk_base.30 0 = lhsaddr.60
  st var_stk_base.30 8 = 4:U64
  lea.stk lhsaddr.61:A64 = msg_eval%38 0
  ld pointer.27:A64 = lhsaddr.61 0
  pusharg 4:U64
  pusharg pointer.27
  pusharg 1:S32
  bsr write
  poparg call.30:S64
  .stk msg_eval%39 8 16
  lea.stk var_stk_base.31:A64 msg_eval%39 0
  lea.mem lhsaddr.62:A64 = $gen/global_val_31 0
  st var_stk_base.31 0 = lhsaddr.62
  st var_stk_base.31 8 = 54:U64
  lea.stk lhsaddr.63:A64 = msg_eval%39 0
  ld pointer.28:A64 = lhsaddr.63 0
  pusharg 54:U64
  pusharg pointer.28
  pusharg 1:S32
  bsr write
  poparg call.31:S64
  .stk msg_eval%40 8 16
  lea.stk var_stk_base.32:A64 msg_eval%40 0
  lea.mem lhsaddr.64:A64 = $gen/global_val_17 0
  st var_stk_base.32 0 = lhsaddr.64
  st var_stk_base.32 8 = 1:U64
  lea.stk lhsaddr.65:A64 = msg_eval%40 0
  ld pointer.29:A64 = lhsaddr.65 0
  pusharg 1:U64
  pusharg pointer.29
  pusharg 1:S32
  bsr write
  poparg call.32:S64
  trap
.bbl br_join.3
  .reg R64 expr.3
  .stk arg0.3 8 16
  lea.stk var_stk_base.33:A64 arg0.3 0
  lea.mem lhsaddr.66:A64 = $gen/global_val_32 0
  st var_stk_base.33 0 = lhsaddr.66
  st var_stk_base.33 8 = 6:U64
  lea.stk lhsaddr.67:A64 = arg0.3 0
  pusharg lhsaddr.67
  bsr parse_real_test/parse_r64
  poparg call.33:R64
  mov expr.3 = call.33
  bra end_expr.3
.bbl end_expr.3
  mov a_val%9:R64 = expr.3
  bitcast bitcast.2:U64 = a_val%9
  beq 0:U64 bitcast.2 br_join.4
  .stk msg_eval%41 8 16
  lea.stk var_stk_base.34:A64 msg_eval%41 0
  lea.mem lhsaddr.68:A64 = $gen/global_val_9 0
  st var_stk_base.34 0 = lhsaddr.68
  st var_stk_base.34 8 = 11:U64
  lea.stk lhsaddr.69:A64 = msg_eval%41 0
  ld pointer.30:A64 = lhsaddr.69 0
  pusharg 11:U64
  pusharg pointer.30
  pusharg 1:S32
  bsr write
  poparg call.34:S64
  .stk msg_eval%42 8 16
  lea.stk var_stk_base.35:A64 msg_eval%42 0
  lea.mem lhsaddr.70:A64 = $gen/global_val_10 0
  st var_stk_base.35 0 = lhsaddr.70
  st var_stk_base.35 8 = 11:U64
  lea.stk lhsaddr.71:A64 = msg_eval%42 0
  ld pointer.31:A64 = lhsaddr.71 0
  pusharg 11:U64
  pusharg pointer.31
  pusharg 1:S32
  bsr write
  poparg call.35:S64
  .stk msg_eval%43 8 16
  lea.stk var_stk_base.36:A64 msg_eval%43 0
  lea.mem lhsaddr.72:A64 = $gen/global_val_33 0
  st var_stk_base.36 0 = lhsaddr.72
  st var_stk_base.36 8 = 54:U64
  lea.stk lhsaddr.73:A64 = msg_eval%43 0
  ld pointer.32:A64 = lhsaddr.73 0
  pusharg 54:U64
  pusharg pointer.32
  pusharg 1:S32
  bsr write
  poparg call.36:S64
  .stk msg_eval%44 8 16
  lea.stk var_stk_base.37:A64 msg_eval%44 0
  lea.mem lhsaddr.74:A64 = $gen/global_val_12 0
  st var_stk_base.37 0 = lhsaddr.74
  st var_stk_base.37 8 = 2:U64
  lea.stk lhsaddr.75:A64 = msg_eval%44 0
  ld pointer.33:A64 = lhsaddr.75 0
  pusharg 2:U64
  pusharg pointer.33
  pusharg 1:S32
  bsr write
  poparg call.37:S64
  .stk msg_eval%45 8 16
  lea.stk var_stk_base.38:A64 msg_eval%45 0
  lea.mem lhsaddr.76:A64 = $gen/global_val_26 0
  st var_stk_base.38 0 = lhsaddr.76
  st var_stk_base.38 8 = 6:U64
  lea.stk lhsaddr.77:A64 = msg_eval%45 0
  ld pointer.34:A64 = lhsaddr.77 0
  pusharg 6:U64
  pusharg pointer.34
  pusharg 1:S32
  bsr write
  poparg call.38:S64
  .stk msg_eval%46 8 16
  lea.stk var_stk_base.39:A64 msg_eval%46 0
  lea.mem lhsaddr.78:A64 = $gen/global_val_14 0
  st var_stk_base.39 0 = lhsaddr.78
  st var_stk_base.39 8 = 4:U64
  lea.stk lhsaddr.79:A64 = msg_eval%46 0
  ld pointer.35:A64 = lhsaddr.79 0
  pusharg 4:U64
  pusharg pointer.35
  pusharg 1:S32
  bsr write
  poparg call.39:S64
  .stk msg_eval%47 8 16
  lea.stk var_stk_base.40:A64 msg_eval%47 0
  lea.mem lhsaddr.80:A64 = $gen/global_val_15 0
  st var_stk_base.40 0 = lhsaddr.80
  st var_stk_base.40 8 = 8:U64
  lea.stk lhsaddr.81:A64 = msg_eval%47 0
  ld pointer.36:A64 = lhsaddr.81 0
  pusharg 8:U64
  pusharg pointer.36
  pusharg 1:S32
  bsr write
  poparg call.40:S64
  .stk msg_eval%48 8 16
  lea.stk var_stk_base.41:A64 msg_eval%48 0
  lea.mem lhsaddr.82:A64 = $gen/global_val_16 0
  st var_stk_base.41 0 = lhsaddr.82
  st var_stk_base.41 8 = 4:U64
  lea.stk lhsaddr.83:A64 = msg_eval%48 0
  ld pointer.37:A64 = lhsaddr.83 0
  pusharg 4:U64
  pusharg pointer.37
  pusharg 1:S32
  bsr write
  poparg call.41:S64
  .stk msg_eval%49 8 16
  lea.stk var_stk_base.42:A64 msg_eval%49 0
  lea.mem lhsaddr.84:A64 = $gen/global_val_33 0
  st var_stk_base.42 0 = lhsaddr.84
  st var_stk_base.42 8 = 54:U64
  lea.stk lhsaddr.85:A64 = msg_eval%49 0
  ld pointer.38:A64 = lhsaddr.85 0
  pusharg 54:U64
  pusharg pointer.38
  pusharg 1:S32
  bsr write
  poparg call.42:S64
  .stk msg_eval%50 8 16
  lea.stk var_stk_base.43:A64 msg_eval%50 0
  lea.mem lhsaddr.86:A64 = $gen/global_val_17 0
  st var_stk_base.43 0 = lhsaddr.86
  st var_stk_base.43 8 = 1:U64
  lea.stk lhsaddr.87:A64 = msg_eval%50 0
  ld pointer.39:A64 = lhsaddr.87 0
  pusharg 1:U64
  pusharg pointer.39
  pusharg 1:S32
  bsr write
  poparg call.43:S64
  trap
.bbl br_join.4
  .reg R64 expr.4
  .stk arg0.4 8 16
  lea.stk var_stk_base.44:A64 arg0.4 0
  lea.mem lhsaddr.88:A64 = $gen/global_val_34 0
  st var_stk_base.44 0 = lhsaddr.88
  st var_stk_base.44 8 = 7:U64
  lea.stk lhsaddr.89:A64 = arg0.4 0
  pusharg lhsaddr.89
  bsr parse_real_test/parse_r64
  poparg call.44:R64
  mov expr.4 = call.44
  bra end_expr.4
.bbl end_expr.4
  mov a_val%11:R64 = expr.4
  bitcast bitcast.3:U64 = a_val%11
  beq 0:U64 bitcast.3 br_join.5
  .stk msg_eval%51 8 16
  lea.stk var_stk_base.45:A64 msg_eval%51 0
  lea.mem lhsaddr.90:A64 = $gen/global_val_9 0
  st var_stk_base.45 0 = lhsaddr.90
  st var_stk_base.45 8 = 11:U64
  lea.stk lhsaddr.91:A64 = msg_eval%51 0
  ld pointer.40:A64 = lhsaddr.91 0
  pusharg 11:U64
  pusharg pointer.40
  pusharg 1:S32
  bsr write
  poparg call.45:S64
  .stk msg_eval%52 8 16
  lea.stk var_stk_base.46:A64 msg_eval%52 0
  lea.mem lhsaddr.92:A64 = $gen/global_val_10 0
  st var_stk_base.46 0 = lhsaddr.92
  st var_stk_base.46 8 = 11:U64
  lea.stk lhsaddr.93:A64 = msg_eval%52 0
  ld pointer.41:A64 = lhsaddr.93 0
  pusharg 11:U64
  pusharg pointer.41
  pusharg 1:S32
  bsr write
  poparg call.46:S64
  .stk msg_eval%53 8 16
  lea.stk var_stk_base.47:A64 msg_eval%53 0
  lea.mem lhsaddr.94:A64 = $gen/global_val_35 0
  st var_stk_base.47 0 = lhsaddr.94
  st var_stk_base.47 8 = 54:U64
  lea.stk lhsaddr.95:A64 = msg_eval%53 0
  ld pointer.42:A64 = lhsaddr.95 0
  pusharg 54:U64
  pusharg pointer.42
  pusharg 1:S32
  bsr write
  poparg call.47:S64
  .stk msg_eval%54 8 16
  lea.stk var_stk_base.48:A64 msg_eval%54 0
  lea.mem lhsaddr.96:A64 = $gen/global_val_12 0
  st var_stk_base.48 0 = lhsaddr.96
  st var_stk_base.48 8 = 2:U64
  lea.stk lhsaddr.97:A64 = msg_eval%54 0
  ld pointer.43:A64 = lhsaddr.97 0
  pusharg 2:U64
  pusharg pointer.43
  pusharg 1:S32
  bsr write
  poparg call.48:S64
  .stk msg_eval%55 8 16
  lea.stk var_stk_base.49:A64 msg_eval%55 0
  lea.mem lhsaddr.98:A64 = $gen/global_val_26 0
  st var_stk_base.49 0 = lhsaddr.98
  st var_stk_base.49 8 = 6:U64
  lea.stk lhsaddr.99:A64 = msg_eval%55 0
  ld pointer.44:A64 = lhsaddr.99 0
  pusharg 6:U64
  pusharg pointer.44
  pusharg 1:S32
  bsr write
  poparg call.49:S64
  .stk msg_eval%56 8 16
  lea.stk var_stk_base.50:A64 msg_eval%56 0
  lea.mem lhsaddr.100:A64 = $gen/global_val_14 0
  st var_stk_base.50 0 = lhsaddr.100
  st var_stk_base.50 8 = 4:U64
  lea.stk lhsaddr.101:A64 = msg_eval%56 0
  ld pointer.45:A64 = lhsaddr.101 0
  pusharg 4:U64
  pusharg pointer.45
  pusharg 1:S32
  bsr write
  poparg call.50:S64
  .stk msg_eval%57 8 16
  lea.stk var_stk_base.51:A64 msg_eval%57 0
  lea.mem lhsaddr.102:A64 = $gen/global_val_15 0
  st var_stk_base.51 0 = lhsaddr.102
  st var_stk_base.51 8 = 8:U64
  lea.stk lhsaddr.103:A64 = msg_eval%57 0
  ld pointer.46:A64 = lhsaddr.103 0
  pusharg 8:U64
  pusharg pointer.46
  pusharg 1:S32
  bsr write
  poparg call.51:S64
  .stk msg_eval%58 8 16
  lea.stk var_stk_base.52:A64 msg_eval%58 0
  lea.mem lhsaddr.104:A64 = $gen/global_val_16 0
  st var_stk_base.52 0 = lhsaddr.104
  st var_stk_base.52 8 = 4:U64
  lea.stk lhsaddr.105:A64 = msg_eval%58 0
  ld pointer.47:A64 = lhsaddr.105 0
  pusharg 4:U64
  pusharg pointer.47
  pusharg 1:S32
  bsr write
  poparg call.52:S64
  .stk msg_eval%59 8 16
  lea.stk var_stk_base.53:A64 msg_eval%59 0
  lea.mem lhsaddr.106:A64 = $gen/global_val_35 0
  st var_stk_base.53 0 = lhsaddr.106
  st var_stk_base.53 8 = 54:U64
  lea.stk lhsaddr.107:A64 = msg_eval%59 0
  ld pointer.48:A64 = lhsaddr.107 0
  pusharg 54:U64
  pusharg pointer.48
  pusharg 1:S32
  bsr write
  poparg call.53:S64
  .stk msg_eval%60 8 16
  lea.stk var_stk_base.54:A64 msg_eval%60 0
  lea.mem lhsaddr.108:A64 = $gen/global_val_17 0
  st var_stk_base.54 0 = lhsaddr.108
  st var_stk_base.54 8 = 1:U64
  lea.stk lhsaddr.109:A64 = msg_eval%60 0
  ld pointer.49:A64 = lhsaddr.109 0
  pusharg 1:U64
  pusharg pointer.49
  pusharg 1:S32
  bsr write
  poparg call.54:S64
  trap
.bbl br_join.5
  .reg R64 expr.5
  .stk arg0.5 8 16
  lea.stk var_stk_base.55:A64 arg0.5 0
  lea.mem lhsaddr.110:A64 = $gen/global_val_36 0
  st var_stk_base.55 0 = lhsaddr.110
  st var_stk_base.55 8 = 7:U64
  lea.stk lhsaddr.111:A64 = arg0.5 0
  pusharg lhsaddr.111
  bsr parse_real_test/parse_r64
  poparg call.55:R64
  mov expr.5 = call.55
  bra end_expr.5
.bbl end_expr.5
  mov a_val%13:R64 = expr.5
  bitcast bitcast.4:U64 = a_val%13
  beq 9223372036854775808:U64 bitcast.4 br_join.6
  .stk msg_eval%61 8 16
  lea.stk var_stk_base.56:A64 msg_eval%61 0
  lea.mem lhsaddr.112:A64 = $gen/global_val_9 0
  st var_stk_base.56 0 = lhsaddr.112
  st var_stk_base.56 8 = 11:U64
  lea.stk lhsaddr.113:A64 = msg_eval%61 0
  ld pointer.50:A64 = lhsaddr.113 0
  pusharg 11:U64
  pusharg pointer.50
  pusharg 1:S32
  bsr write
  poparg call.56:S64
  .stk msg_eval%62 8 16
  lea.stk var_stk_base.57:A64 msg_eval%62 0
  lea.mem lhsaddr.114:A64 = $gen/global_val_10 0
  st var_stk_base.57 0 = lhsaddr.114
  st var_stk_base.57 8 = 11:U64
  lea.stk lhsaddr.115:A64 = msg_eval%62 0
  ld pointer.51:A64 = lhsaddr.115 0
  pusharg 11:U64
  pusharg pointer.51
  pusharg 1:S32
  bsr write
  poparg call.57:S64
  .stk msg_eval%63 8 16
  lea.stk var_stk_base.58:A64 msg_eval%63 0
  lea.mem lhsaddr.116:A64 = $gen/global_val_37 0
  st var_stk_base.58 0 = lhsaddr.116
  st var_stk_base.58 8 = 54:U64
  lea.stk lhsaddr.117:A64 = msg_eval%63 0
  ld pointer.52:A64 = lhsaddr.117 0
  pusharg 54:U64
  pusharg pointer.52
  pusharg 1:S32
  bsr write
  poparg call.58:S64
  .stk msg_eval%64 8 16
  lea.stk var_stk_base.59:A64 msg_eval%64 0
  lea.mem lhsaddr.118:A64 = $gen/global_val_12 0
  st var_stk_base.59 0 = lhsaddr.118
  st var_stk_base.59 8 = 2:U64
  lea.stk lhsaddr.119:A64 = msg_eval%64 0
  ld pointer.53:A64 = lhsaddr.119 0
  pusharg 2:U64
  pusharg pointer.53
  pusharg 1:S32
  bsr write
  poparg call.59:S64
  .stk msg_eval%65 8 16
  lea.stk var_stk_base.60:A64 msg_eval%65 0
  lea.mem lhsaddr.120:A64 = $gen/global_val_26 0
  st var_stk_base.60 0 = lhsaddr.120
  st var_stk_base.60 8 = 6:U64
  lea.stk lhsaddr.121:A64 = msg_eval%65 0
  ld pointer.54:A64 = lhsaddr.121 0
  pusharg 6:U64
  pusharg pointer.54
  pusharg 1:S32
  bsr write
  poparg call.60:S64
  .stk msg_eval%66 8 16
  lea.stk var_stk_base.61:A64 msg_eval%66 0
  lea.mem lhsaddr.122:A64 = $gen/global_val_14 0
  st var_stk_base.61 0 = lhsaddr.122
  st var_stk_base.61 8 = 4:U64
  lea.stk lhsaddr.123:A64 = msg_eval%66 0
  ld pointer.55:A64 = lhsaddr.123 0
  pusharg 4:U64
  pusharg pointer.55
  pusharg 1:S32
  bsr write
  poparg call.61:S64
  .stk msg_eval%67 8 16
  lea.stk var_stk_base.62:A64 msg_eval%67 0
  lea.mem lhsaddr.124:A64 = $gen/global_val_15 0
  st var_stk_base.62 0 = lhsaddr.124
  st var_stk_base.62 8 = 8:U64
  lea.stk lhsaddr.125:A64 = msg_eval%67 0
  ld pointer.56:A64 = lhsaddr.125 0
  pusharg 8:U64
  pusharg pointer.56
  pusharg 1:S32
  bsr write
  poparg call.62:S64
  .stk msg_eval%68 8 16
  lea.stk var_stk_base.63:A64 msg_eval%68 0
  lea.mem lhsaddr.126:A64 = $gen/global_val_16 0
  st var_stk_base.63 0 = lhsaddr.126
  st var_stk_base.63 8 = 4:U64
  lea.stk lhsaddr.127:A64 = msg_eval%68 0
  ld pointer.57:A64 = lhsaddr.127 0
  pusharg 4:U64
  pusharg pointer.57
  pusharg 1:S32
  bsr write
  poparg call.63:S64
  .stk msg_eval%69 8 16
  lea.stk var_stk_base.64:A64 msg_eval%69 0
  lea.mem lhsaddr.128:A64 = $gen/global_val_37 0
  st var_stk_base.64 0 = lhsaddr.128
  st var_stk_base.64 8 = 54:U64
  lea.stk lhsaddr.129:A64 = msg_eval%69 0
  ld pointer.58:A64 = lhsaddr.129 0
  pusharg 54:U64
  pusharg pointer.58
  pusharg 1:S32
  bsr write
  poparg call.64:S64
  .stk msg_eval%70 8 16
  lea.stk var_stk_base.65:A64 msg_eval%70 0
  lea.mem lhsaddr.130:A64 = $gen/global_val_17 0
  st var_stk_base.65 0 = lhsaddr.130
  st var_stk_base.65 8 = 1:U64
  lea.stk lhsaddr.131:A64 = msg_eval%70 0
  ld pointer.59:A64 = lhsaddr.131 0
  pusharg 1:U64
  pusharg pointer.59
  pusharg 1:S32
  bsr write
  poparg call.65:S64
  trap
.bbl br_join.6
  .reg R64 expr.6
  .stk arg0.6 8 16
  lea.stk var_stk_base.66:A64 arg0.6 0
  lea.mem lhsaddr.132:A64 = $gen/global_val_38 0
  st var_stk_base.66 0 = lhsaddr.132
  st var_stk_base.66 8 = 2:U64
  lea.stk lhsaddr.133:A64 = arg0.6 0
  pusharg lhsaddr.133
  bsr parse_real_test/parse_r64
  poparg call.66:R64
  mov expr.6 = call.66
  bra end_expr.6
.bbl end_expr.6
  mov a_val%15:R64 = expr.6
  bitcast bitcast.5:U64 = a_val%15
  beq 0:U64 bitcast.5 br_join.7
  .stk msg_eval%71 8 16
  lea.stk var_stk_base.67:A64 msg_eval%71 0
  lea.mem lhsaddr.134:A64 = $gen/global_val_9 0
  st var_stk_base.67 0 = lhsaddr.134
  st var_stk_base.67 8 = 11:U64
  lea.stk lhsaddr.135:A64 = msg_eval%71 0
  ld pointer.60:A64 = lhsaddr.135 0
  pusharg 11:U64
  pusharg pointer.60
  pusharg 1:S32
  bsr write
  poparg call.67:S64
  .stk msg_eval%72 8 16
  lea.stk var_stk_base.68:A64 msg_eval%72 0
  lea.mem lhsaddr.136:A64 = $gen/global_val_10 0
  st var_stk_base.68 0 = lhsaddr.136
  st var_stk_base.68 8 = 11:U64
  lea.stk lhsaddr.137:A64 = msg_eval%72 0
  ld pointer.61:A64 = lhsaddr.137 0
  pusharg 11:U64
  pusharg pointer.61
  pusharg 1:S32
  bsr write
  poparg call.68:S64
  .stk msg_eval%73 8 16
  lea.stk var_stk_base.69:A64 msg_eval%73 0
  lea.mem lhsaddr.138:A64 = $gen/global_val_39 0
  st var_stk_base.69 0 = lhsaddr.138
  st var_stk_base.69 8 = 54:U64
  lea.stk lhsaddr.139:A64 = msg_eval%73 0
  ld pointer.62:A64 = lhsaddr.139 0
  pusharg 54:U64
  pusharg pointer.62
  pusharg 1:S32
  bsr write
  poparg call.69:S64
  .stk msg_eval%74 8 16
  lea.stk var_stk_base.70:A64 msg_eval%74 0
  lea.mem lhsaddr.140:A64 = $gen/global_val_12 0
  st var_stk_base.70 0 = lhsaddr.140
  st var_stk_base.70 8 = 2:U64
  lea.stk lhsaddr.141:A64 = msg_eval%74 0
  ld pointer.63:A64 = lhsaddr.141 0
  pusharg 2:U64
  pusharg pointer.63
  pusharg 1:S32
  bsr write
  poparg call.70:S64
  .stk msg_eval%75 8 16
  lea.stk var_stk_base.71:A64 msg_eval%75 0
  lea.mem lhsaddr.142:A64 = $gen/global_val_26 0
  st var_stk_base.71 0 = lhsaddr.142
  st var_stk_base.71 8 = 6:U64
  lea.stk lhsaddr.143:A64 = msg_eval%75 0
  ld pointer.64:A64 = lhsaddr.143 0
  pusharg 6:U64
  pusharg pointer.64
  pusharg 1:S32
  bsr write
  poparg call.71:S64
  .stk msg_eval%76 8 16
  lea.stk var_stk_base.72:A64 msg_eval%76 0
  lea.mem lhsaddr.144:A64 = $gen/global_val_14 0
  st var_stk_base.72 0 = lhsaddr.144
  st var_stk_base.72 8 = 4:U64
  lea.stk lhsaddr.145:A64 = msg_eval%76 0
  ld pointer.65:A64 = lhsaddr.145 0
  pusharg 4:U64
  pusharg pointer.65
  pusharg 1:S32
  bsr write
  poparg call.72:S64
  .stk msg_eval%77 8 16
  lea.stk var_stk_base.73:A64 msg_eval%77 0
  lea.mem lhsaddr.146:A64 = $gen/global_val_15 0
  st var_stk_base.73 0 = lhsaddr.146
  st var_stk_base.73 8 = 8:U64
  lea.stk lhsaddr.147:A64 = msg_eval%77 0
  ld pointer.66:A64 = lhsaddr.147 0
  pusharg 8:U64
  pusharg pointer.66
  pusharg 1:S32
  bsr write
  poparg call.73:S64
  .stk msg_eval%78 8 16
  lea.stk var_stk_base.74:A64 msg_eval%78 0
  lea.mem lhsaddr.148:A64 = $gen/global_val_16 0
  st var_stk_base.74 0 = lhsaddr.148
  st var_stk_base.74 8 = 4:U64
  lea.stk lhsaddr.149:A64 = msg_eval%78 0
  ld pointer.67:A64 = lhsaddr.149 0
  pusharg 4:U64
  pusharg pointer.67
  pusharg 1:S32
  bsr write
  poparg call.74:S64
  .stk msg_eval%79 8 16
  lea.stk var_stk_base.75:A64 msg_eval%79 0
  lea.mem lhsaddr.150:A64 = $gen/global_val_39 0
  st var_stk_base.75 0 = lhsaddr.150
  st var_stk_base.75 8 = 54:U64
  lea.stk lhsaddr.151:A64 = msg_eval%79 0
  ld pointer.68:A64 = lhsaddr.151 0
  pusharg 54:U64
  pusharg pointer.68
  pusharg 1:S32
  bsr write
  poparg call.75:S64
  .stk msg_eval%80 8 16
  lea.stk var_stk_base.76:A64 msg_eval%80 0
  lea.mem lhsaddr.152:A64 = $gen/global_val_17 0
  st var_stk_base.76 0 = lhsaddr.152
  st var_stk_base.76 8 = 1:U64
  lea.stk lhsaddr.153:A64 = msg_eval%80 0
  ld pointer.69:A64 = lhsaddr.153 0
  pusharg 1:U64
  pusharg pointer.69
  pusharg 1:S32
  bsr write
  poparg call.76:S64
  trap
.bbl br_join.7
  .reg R64 expr.7
  .stk arg0.7 8 16
  lea.stk var_stk_base.77:A64 arg0.7 0
  lea.mem lhsaddr.154:A64 = $gen/global_val_40 0
  st var_stk_base.77 0 = lhsaddr.154
  st var_stk_base.77 8 = 6:U64
  lea.stk lhsaddr.155:A64 = arg0.7 0
  pusharg lhsaddr.155
  bsr parse_real_test/parse_r64
  poparg call.77:R64
  mov expr.7 = call.77
  bra end_expr.7
.bbl end_expr.7
  mov a_val%17:R64 = expr.7
  bitcast bitcast.6:U64 = a_val%17
  beq 0:U64 bitcast.6 br_join.8
  .stk msg_eval%81 8 16
  lea.stk var_stk_base.78:A64 msg_eval%81 0
  lea.mem lhsaddr.156:A64 = $gen/global_val_9 0
  st var_stk_base.78 0 = lhsaddr.156
  st var_stk_base.78 8 = 11:U64
  lea.stk lhsaddr.157:A64 = msg_eval%81 0
  ld pointer.70:A64 = lhsaddr.157 0
  pusharg 11:U64
  pusharg pointer.70
  pusharg 1:S32
  bsr write
  poparg call.78:S64
  .stk msg_eval%82 8 16
  lea.stk var_stk_base.79:A64 msg_eval%82 0
  lea.mem lhsaddr.158:A64 = $gen/global_val_10 0
  st var_stk_base.79 0 = lhsaddr.158
  st var_stk_base.79 8 = 11:U64
  lea.stk lhsaddr.159:A64 = msg_eval%82 0
  ld pointer.71:A64 = lhsaddr.159 0
  pusharg 11:U64
  pusharg pointer.71
  pusharg 1:S32
  bsr write
  poparg call.79:S64
  .stk msg_eval%83 8 16
  lea.stk var_stk_base.80:A64 msg_eval%83 0
  lea.mem lhsaddr.160:A64 = $gen/global_val_41 0
  st var_stk_base.80 0 = lhsaddr.160
  st var_stk_base.80 8 = 54:U64
  lea.stk lhsaddr.161:A64 = msg_eval%83 0
  ld pointer.72:A64 = lhsaddr.161 0
  pusharg 54:U64
  pusharg pointer.72
  pusharg 1:S32
  bsr write
  poparg call.80:S64
  .stk msg_eval%84 8 16
  lea.stk var_stk_base.81:A64 msg_eval%84 0
  lea.mem lhsaddr.162:A64 = $gen/global_val_12 0
  st var_stk_base.81 0 = lhsaddr.162
  st var_stk_base.81 8 = 2:U64
  lea.stk lhsaddr.163:A64 = msg_eval%84 0
  ld pointer.73:A64 = lhsaddr.163 0
  pusharg 2:U64
  pusharg pointer.73
  pusharg 1:S32
  bsr write
  poparg call.81:S64
  .stk msg_eval%85 8 16
  lea.stk var_stk_base.82:A64 msg_eval%85 0
  lea.mem lhsaddr.164:A64 = $gen/global_val_26 0
  st var_stk_base.82 0 = lhsaddr.164
  st var_stk_base.82 8 = 6:U64
  lea.stk lhsaddr.165:A64 = msg_eval%85 0
  ld pointer.74:A64 = lhsaddr.165 0
  pusharg 6:U64
  pusharg pointer.74
  pusharg 1:S32
  bsr write
  poparg call.82:S64
  .stk msg_eval%86 8 16
  lea.stk var_stk_base.83:A64 msg_eval%86 0
  lea.mem lhsaddr.166:A64 = $gen/global_val_14 0
  st var_stk_base.83 0 = lhsaddr.166
  st var_stk_base.83 8 = 4:U64
  lea.stk lhsaddr.167:A64 = msg_eval%86 0
  ld pointer.75:A64 = lhsaddr.167 0
  pusharg 4:U64
  pusharg pointer.75
  pusharg 1:S32
  bsr write
  poparg call.83:S64
  .stk msg_eval%87 8 16
  lea.stk var_stk_base.84:A64 msg_eval%87 0
  lea.mem lhsaddr.168:A64 = $gen/global_val_15 0
  st var_stk_base.84 0 = lhsaddr.168
  st var_stk_base.84 8 = 8:U64
  lea.stk lhsaddr.169:A64 = msg_eval%87 0
  ld pointer.76:A64 = lhsaddr.169 0
  pusharg 8:U64
  pusharg pointer.76
  pusharg 1:S32
  bsr write
  poparg call.84:S64
  .stk msg_eval%88 8 16
  lea.stk var_stk_base.85:A64 msg_eval%88 0
  lea.mem lhsaddr.170:A64 = $gen/global_val_16 0
  st var_stk_base.85 0 = lhsaddr.170
  st var_stk_base.85 8 = 4:U64
  lea.stk lhsaddr.171:A64 = msg_eval%88 0
  ld pointer.77:A64 = lhsaddr.171 0
  pusharg 4:U64
  pusharg pointer.77
  pusharg 1:S32
  bsr write
  poparg call.85:S64
  .stk msg_eval%89 8 16
  lea.stk var_stk_base.86:A64 msg_eval%89 0
  lea.mem lhsaddr.172:A64 = $gen/global_val_41 0
  st var_stk_base.86 0 = lhsaddr.172
  st var_stk_base.86 8 = 54:U64
  lea.stk lhsaddr.173:A64 = msg_eval%89 0
  ld pointer.78:A64 = lhsaddr.173 0
  pusharg 54:U64
  pusharg pointer.78
  pusharg 1:S32
  bsr write
  poparg call.86:S64
  .stk msg_eval%90 8 16
  lea.stk var_stk_base.87:A64 msg_eval%90 0
  lea.mem lhsaddr.174:A64 = $gen/global_val_17 0
  st var_stk_base.87 0 = lhsaddr.174
  st var_stk_base.87 8 = 1:U64
  lea.stk lhsaddr.175:A64 = msg_eval%90 0
  ld pointer.79:A64 = lhsaddr.175 0
  pusharg 1:U64
  pusharg pointer.79
  pusharg 1:S32
  bsr write
  poparg call.87:S64
  trap
.bbl br_join.8
  .reg R64 expr.8
  .stk arg0.8 8 16
  lea.stk var_stk_base.88:A64 arg0.8 0
  lea.mem lhsaddr.176:A64 = $gen/global_val_42 0
  st var_stk_base.88 0 = lhsaddr.176
  st var_stk_base.88 8 = 12:U64
  lea.stk lhsaddr.177:A64 = arg0.8 0
  pusharg lhsaddr.177
  bsr parse_real_test/parse_r64
  poparg call.88:R64
  mov expr.8 = call.88
  bra end_expr.8
.bbl end_expr.8
  mov a_val%19:R64 = expr.8
  bitcast bitcast.7:U64 = a_val%19
  beq 0:U64 bitcast.7 br_join.9
  .stk msg_eval%91 8 16
  lea.stk var_stk_base.89:A64 msg_eval%91 0
  lea.mem lhsaddr.178:A64 = $gen/global_val_9 0
  st var_stk_base.89 0 = lhsaddr.178
  st var_stk_base.89 8 = 11:U64
  lea.stk lhsaddr.179:A64 = msg_eval%91 0
  ld pointer.80:A64 = lhsaddr.179 0
  pusharg 11:U64
  pusharg pointer.80
  pusharg 1:S32
  bsr write
  poparg call.89:S64
  .stk msg_eval%92 8 16
  lea.stk var_stk_base.90:A64 msg_eval%92 0
  lea.mem lhsaddr.180:A64 = $gen/global_val_10 0
  st var_stk_base.90 0 = lhsaddr.180
  st var_stk_base.90 8 = 11:U64
  lea.stk lhsaddr.181:A64 = msg_eval%92 0
  ld pointer.81:A64 = lhsaddr.181 0
  pusharg 11:U64
  pusharg pointer.81
  pusharg 1:S32
  bsr write
  poparg call.90:S64
  .stk msg_eval%93 8 16
  lea.stk var_stk_base.91:A64 msg_eval%93 0
  lea.mem lhsaddr.182:A64 = $gen/global_val_43 0
  st var_stk_base.91 0 = lhsaddr.182
  st var_stk_base.91 8 = 54:U64
  lea.stk lhsaddr.183:A64 = msg_eval%93 0
  ld pointer.82:A64 = lhsaddr.183 0
  pusharg 54:U64
  pusharg pointer.82
  pusharg 1:S32
  bsr write
  poparg call.91:S64
  .stk msg_eval%94 8 16
  lea.stk var_stk_base.92:A64 msg_eval%94 0
  lea.mem lhsaddr.184:A64 = $gen/global_val_12 0
  st var_stk_base.92 0 = lhsaddr.184
  st var_stk_base.92 8 = 2:U64
  lea.stk lhsaddr.185:A64 = msg_eval%94 0
  ld pointer.83:A64 = lhsaddr.185 0
  pusharg 2:U64
  pusharg pointer.83
  pusharg 1:S32
  bsr write
  poparg call.92:S64
  .stk msg_eval%95 8 16
  lea.stk var_stk_base.93:A64 msg_eval%95 0
  lea.mem lhsaddr.186:A64 = $gen/global_val_26 0
  st var_stk_base.93 0 = lhsaddr.186
  st var_stk_base.93 8 = 6:U64
  lea.stk lhsaddr.187:A64 = msg_eval%95 0
  ld pointer.84:A64 = lhsaddr.187 0
  pusharg 6:U64
  pusharg pointer.84
  pusharg 1:S32
  bsr write
  poparg call.93:S64
  .stk msg_eval%96 8 16
  lea.stk var_stk_base.94:A64 msg_eval%96 0
  lea.mem lhsaddr.188:A64 = $gen/global_val_14 0
  st var_stk_base.94 0 = lhsaddr.188
  st var_stk_base.94 8 = 4:U64
  lea.stk lhsaddr.189:A64 = msg_eval%96 0
  ld pointer.85:A64 = lhsaddr.189 0
  pusharg 4:U64
  pusharg pointer.85
  pusharg 1:S32
  bsr write
  poparg call.94:S64
  .stk msg_eval%97 8 16
  lea.stk var_stk_base.95:A64 msg_eval%97 0
  lea.mem lhsaddr.190:A64 = $gen/global_val_15 0
  st var_stk_base.95 0 = lhsaddr.190
  st var_stk_base.95 8 = 8:U64
  lea.stk lhsaddr.191:A64 = msg_eval%97 0
  ld pointer.86:A64 = lhsaddr.191 0
  pusharg 8:U64
  pusharg pointer.86
  pusharg 1:S32
  bsr write
  poparg call.95:S64
  .stk msg_eval%98 8 16
  lea.stk var_stk_base.96:A64 msg_eval%98 0
  lea.mem lhsaddr.192:A64 = $gen/global_val_16 0
  st var_stk_base.96 0 = lhsaddr.192
  st var_stk_base.96 8 = 4:U64
  lea.stk lhsaddr.193:A64 = msg_eval%98 0
  ld pointer.87:A64 = lhsaddr.193 0
  pusharg 4:U64
  pusharg pointer.87
  pusharg 1:S32
  bsr write
  poparg call.96:S64
  .stk msg_eval%99 8 16
  lea.stk var_stk_base.97:A64 msg_eval%99 0
  lea.mem lhsaddr.194:A64 = $gen/global_val_43 0
  st var_stk_base.97 0 = lhsaddr.194
  st var_stk_base.97 8 = 54:U64
  lea.stk lhsaddr.195:A64 = msg_eval%99 0
  ld pointer.88:A64 = lhsaddr.195 0
  pusharg 54:U64
  pusharg pointer.88
  pusharg 1:S32
  bsr write
  poparg call.97:S64
  .stk msg_eval%100 8 16
  lea.stk var_stk_base.98:A64 msg_eval%100 0
  lea.mem lhsaddr.196:A64 = $gen/global_val_17 0
  st var_stk_base.98 0 = lhsaddr.196
  st var_stk_base.98 8 = 1:U64
  lea.stk lhsaddr.197:A64 = msg_eval%100 0
  ld pointer.89:A64 = lhsaddr.197 0
  pusharg 1:U64
  pusharg pointer.89
  pusharg 1:S32
  bsr write
  poparg call.98:S64
  trap
.bbl br_join.9
  .reg R64 expr.9
  .stk arg0.9 8 16
  lea.stk var_stk_base.99:A64 arg0.9 0
  lea.mem lhsaddr.198:A64 = $gen/global_val_42 0
  st var_stk_base.99 0 = lhsaddr.198
  st var_stk_base.99 8 = 12:U64
  lea.stk lhsaddr.199:A64 = arg0.9 0
  pusharg lhsaddr.199
  bsr parse_real_test/parse_r64
  poparg call.99:R64
  mov expr.9 = call.99
  bra end_expr.9
.bbl end_expr.9
  mov a_val%21:R64 = expr.9
  bitcast bitcast.8:U64 = a_val%21
  beq 0:U64 bitcast.8 br_join.10
  .stk msg_eval%101 8 16
  lea.stk var_stk_base.100:A64 msg_eval%101 0
  lea.mem lhsaddr.200:A64 = $gen/global_val_9 0
  st var_stk_base.100 0 = lhsaddr.200
  st var_stk_base.100 8 = 11:U64
  lea.stk lhsaddr.201:A64 = msg_eval%101 0
  ld pointer.90:A64 = lhsaddr.201 0
  pusharg 11:U64
  pusharg pointer.90
  pusharg 1:S32
  bsr write
  poparg call.100:S64
  .stk msg_eval%102 8 16
  lea.stk var_stk_base.101:A64 msg_eval%102 0
  lea.mem lhsaddr.202:A64 = $gen/global_val_10 0
  st var_stk_base.101 0 = lhsaddr.202
  st var_stk_base.101 8 = 11:U64
  lea.stk lhsaddr.203:A64 = msg_eval%102 0
  ld pointer.91:A64 = lhsaddr.203 0
  pusharg 11:U64
  pusharg pointer.91
  pusharg 1:S32
  bsr write
  poparg call.101:S64
  .stk msg_eval%103 8 16
  lea.stk var_stk_base.102:A64 msg_eval%103 0
  lea.mem lhsaddr.204:A64 = $gen/global_val_44 0
  st var_stk_base.102 0 = lhsaddr.204
  st var_stk_base.102 8 = 54:U64
  lea.stk lhsaddr.205:A64 = msg_eval%103 0
  ld pointer.92:A64 = lhsaddr.205 0
  pusharg 54:U64
  pusharg pointer.92
  pusharg 1:S32
  bsr write
  poparg call.102:S64
  .stk msg_eval%104 8 16
  lea.stk var_stk_base.103:A64 msg_eval%104 0
  lea.mem lhsaddr.206:A64 = $gen/global_val_12 0
  st var_stk_base.103 0 = lhsaddr.206
  st var_stk_base.103 8 = 2:U64
  lea.stk lhsaddr.207:A64 = msg_eval%104 0
  ld pointer.93:A64 = lhsaddr.207 0
  pusharg 2:U64
  pusharg pointer.93
  pusharg 1:S32
  bsr write
  poparg call.103:S64
  .stk msg_eval%105 8 16
  lea.stk var_stk_base.104:A64 msg_eval%105 0
  lea.mem lhsaddr.208:A64 = $gen/global_val_26 0
  st var_stk_base.104 0 = lhsaddr.208
  st var_stk_base.104 8 = 6:U64
  lea.stk lhsaddr.209:A64 = msg_eval%105 0
  ld pointer.94:A64 = lhsaddr.209 0
  pusharg 6:U64
  pusharg pointer.94
  pusharg 1:S32
  bsr write
  poparg call.104:S64
  .stk msg_eval%106 8 16
  lea.stk var_stk_base.105:A64 msg_eval%106 0
  lea.mem lhsaddr.210:A64 = $gen/global_val_14 0
  st var_stk_base.105 0 = lhsaddr.210
  st var_stk_base.105 8 = 4:U64
  lea.stk lhsaddr.211:A64 = msg_eval%106 0
  ld pointer.95:A64 = lhsaddr.211 0
  pusharg 4:U64
  pusharg pointer.95
  pusharg 1:S32
  bsr write
  poparg call.105:S64
  .stk msg_eval%107 8 16
  lea.stk var_stk_base.106:A64 msg_eval%107 0
  lea.mem lhsaddr.212:A64 = $gen/global_val_15 0
  st var_stk_base.106 0 = lhsaddr.212
  st var_stk_base.106 8 = 8:U64
  lea.stk lhsaddr.213:A64 = msg_eval%107 0
  ld pointer.96:A64 = lhsaddr.213 0
  pusharg 8:U64
  pusharg pointer.96
  pusharg 1:S32
  bsr write
  poparg call.106:S64
  .stk msg_eval%108 8 16
  lea.stk var_stk_base.107:A64 msg_eval%108 0
  lea.mem lhsaddr.214:A64 = $gen/global_val_16 0
  st var_stk_base.107 0 = lhsaddr.214
  st var_stk_base.107 8 = 4:U64
  lea.stk lhsaddr.215:A64 = msg_eval%108 0
  ld pointer.97:A64 = lhsaddr.215 0
  pusharg 4:U64
  pusharg pointer.97
  pusharg 1:S32
  bsr write
  poparg call.107:S64
  .stk msg_eval%109 8 16
  lea.stk var_stk_base.108:A64 msg_eval%109 0
  lea.mem lhsaddr.216:A64 = $gen/global_val_44 0
  st var_stk_base.108 0 = lhsaddr.216
  st var_stk_base.108 8 = 54:U64
  lea.stk lhsaddr.217:A64 = msg_eval%109 0
  ld pointer.98:A64 = lhsaddr.217 0
  pusharg 54:U64
  pusharg pointer.98
  pusharg 1:S32
  bsr write
  poparg call.108:S64
  .stk msg_eval%110 8 16
  lea.stk var_stk_base.109:A64 msg_eval%110 0
  lea.mem lhsaddr.218:A64 = $gen/global_val_17 0
  st var_stk_base.109 0 = lhsaddr.218
  st var_stk_base.109 8 = 1:U64
  lea.stk lhsaddr.219:A64 = msg_eval%110 0
  ld pointer.99:A64 = lhsaddr.219 0
  pusharg 1:U64
  pusharg pointer.99
  pusharg 1:S32
  bsr write
  poparg call.109:S64
  trap
.bbl br_join.10
  .reg R64 expr.10
  .stk arg0.10 8 16
  lea.stk var_stk_base.110:A64 arg0.10 0
  lea.mem lhsaddr.220:A64 = $gen/global_val_45 0
  st var_stk_base.110 0 = lhsaddr.220
  st var_stk_base.110 8 = 1:U64
  lea.stk lhsaddr.221:A64 = arg0.10 0
  pusharg lhsaddr.221
  bsr parse_real_test/parse_r64
  poparg call.110:R64
  mov expr.10 = call.110
  bra end_expr.10
.bbl end_expr.10
  mov a_val%23:R64 = expr.10
  bitcast bitcast.9:U64 = a_val%23
  beq 4607182418800017408:U64 bitcast.9 br_join.11
  .stk msg_eval%111 8 16
  lea.stk var_stk_base.111:A64 msg_eval%111 0
  lea.mem lhsaddr.222:A64 = $gen/global_val_9 0
  st var_stk_base.111 0 = lhsaddr.222
  st var_stk_base.111 8 = 11:U64
  lea.stk lhsaddr.223:A64 = msg_eval%111 0
  ld pointer.100:A64 = lhsaddr.223 0
  pusharg 11:U64
  pusharg pointer.100
  pusharg 1:S32
  bsr write
  poparg call.111:S64
  .stk msg_eval%112 8 16
  lea.stk var_stk_base.112:A64 msg_eval%112 0
  lea.mem lhsaddr.224:A64 = $gen/global_val_10 0
  st var_stk_base.112 0 = lhsaddr.224
  st var_stk_base.112 8 = 11:U64
  lea.stk lhsaddr.225:A64 = msg_eval%112 0
  ld pointer.101:A64 = lhsaddr.225 0
  pusharg 11:U64
  pusharg pointer.101
  pusharg 1:S32
  bsr write
  poparg call.112:S64
  .stk msg_eval%113 8 16
  lea.stk var_stk_base.113:A64 msg_eval%113 0
  lea.mem lhsaddr.226:A64 = $gen/global_val_46 0
  st var_stk_base.113 0 = lhsaddr.226
  st var_stk_base.113 8 = 54:U64
  lea.stk lhsaddr.227:A64 = msg_eval%113 0
  ld pointer.102:A64 = lhsaddr.227 0
  pusharg 54:U64
  pusharg pointer.102
  pusharg 1:S32
  bsr write
  poparg call.113:S64
  .stk msg_eval%114 8 16
  lea.stk var_stk_base.114:A64 msg_eval%114 0
  lea.mem lhsaddr.228:A64 = $gen/global_val_12 0
  st var_stk_base.114 0 = lhsaddr.228
  st var_stk_base.114 8 = 2:U64
  lea.stk lhsaddr.229:A64 = msg_eval%114 0
  ld pointer.103:A64 = lhsaddr.229 0
  pusharg 2:U64
  pusharg pointer.103
  pusharg 1:S32
  bsr write
  poparg call.114:S64
  .stk msg_eval%115 8 16
  lea.stk var_stk_base.115:A64 msg_eval%115 0
  lea.mem lhsaddr.230:A64 = $gen/global_val_26 0
  st var_stk_base.115 0 = lhsaddr.230
  st var_stk_base.115 8 = 6:U64
  lea.stk lhsaddr.231:A64 = msg_eval%115 0
  ld pointer.104:A64 = lhsaddr.231 0
  pusharg 6:U64
  pusharg pointer.104
  pusharg 1:S32
  bsr write
  poparg call.115:S64
  .stk msg_eval%116 8 16
  lea.stk var_stk_base.116:A64 msg_eval%116 0
  lea.mem lhsaddr.232:A64 = $gen/global_val_14 0
  st var_stk_base.116 0 = lhsaddr.232
  st var_stk_base.116 8 = 4:U64
  lea.stk lhsaddr.233:A64 = msg_eval%116 0
  ld pointer.105:A64 = lhsaddr.233 0
  pusharg 4:U64
  pusharg pointer.105
  pusharg 1:S32
  bsr write
  poparg call.116:S64
  .stk msg_eval%117 8 16
  lea.stk var_stk_base.117:A64 msg_eval%117 0
  lea.mem lhsaddr.234:A64 = $gen/global_val_15 0
  st var_stk_base.117 0 = lhsaddr.234
  st var_stk_base.117 8 = 8:U64
  lea.stk lhsaddr.235:A64 = msg_eval%117 0
  ld pointer.106:A64 = lhsaddr.235 0
  pusharg 8:U64
  pusharg pointer.106
  pusharg 1:S32
  bsr write
  poparg call.117:S64
  .stk msg_eval%118 8 16
  lea.stk var_stk_base.118:A64 msg_eval%118 0
  lea.mem lhsaddr.236:A64 = $gen/global_val_16 0
  st var_stk_base.118 0 = lhsaddr.236
  st var_stk_base.118 8 = 4:U64
  lea.stk lhsaddr.237:A64 = msg_eval%118 0
  ld pointer.107:A64 = lhsaddr.237 0
  pusharg 4:U64
  pusharg pointer.107
  pusharg 1:S32
  bsr write
  poparg call.118:S64
  .stk msg_eval%119 8 16
  lea.stk var_stk_base.119:A64 msg_eval%119 0
  lea.mem lhsaddr.238:A64 = $gen/global_val_46 0
  st var_stk_base.119 0 = lhsaddr.238
  st var_stk_base.119 8 = 54:U64
  lea.stk lhsaddr.239:A64 = msg_eval%119 0
  ld pointer.108:A64 = lhsaddr.239 0
  pusharg 54:U64
  pusharg pointer.108
  pusharg 1:S32
  bsr write
  poparg call.119:S64
  .stk msg_eval%120 8 16
  lea.stk var_stk_base.120:A64 msg_eval%120 0
  lea.mem lhsaddr.240:A64 = $gen/global_val_17 0
  st var_stk_base.120 0 = lhsaddr.240
  st var_stk_base.120 8 = 1:U64
  lea.stk lhsaddr.241:A64 = msg_eval%120 0
  ld pointer.109:A64 = lhsaddr.241 0
  pusharg 1:U64
  pusharg pointer.109
  pusharg 1:S32
  bsr write
  poparg call.120:S64
  trap
.bbl br_join.11
  .reg R64 expr.11
  .stk arg0.11 8 16
  lea.stk var_stk_base.121:A64 arg0.11 0
  lea.mem lhsaddr.242:A64 = $gen/global_val_47 0
  st var_stk_base.121 0 = lhsaddr.242
  st var_stk_base.121 8 = 4:U64
  lea.stk lhsaddr.243:A64 = arg0.11 0
  pusharg lhsaddr.243
  bsr parse_real_test/parse_r64
  poparg call.121:R64
  mov expr.11 = call.121
  bra end_expr.11
.bbl end_expr.11
  mov a_val%25:R64 = expr.11
  bitcast bitcast.10:U64 = a_val%25
  beq 4607182418800017408:U64 bitcast.10 br_join.12
  .stk msg_eval%121 8 16
  lea.stk var_stk_base.122:A64 msg_eval%121 0
  lea.mem lhsaddr.244:A64 = $gen/global_val_9 0
  st var_stk_base.122 0 = lhsaddr.244
  st var_stk_base.122 8 = 11:U64
  lea.stk lhsaddr.245:A64 = msg_eval%121 0
  ld pointer.110:A64 = lhsaddr.245 0
  pusharg 11:U64
  pusharg pointer.110
  pusharg 1:S32
  bsr write
  poparg call.122:S64
  .stk msg_eval%122 8 16
  lea.stk var_stk_base.123:A64 msg_eval%122 0
  lea.mem lhsaddr.246:A64 = $gen/global_val_10 0
  st var_stk_base.123 0 = lhsaddr.246
  st var_stk_base.123 8 = 11:U64
  lea.stk lhsaddr.247:A64 = msg_eval%122 0
  ld pointer.111:A64 = lhsaddr.247 0
  pusharg 11:U64
  pusharg pointer.111
  pusharg 1:S32
  bsr write
  poparg call.123:S64
  .stk msg_eval%123 8 16
  lea.stk var_stk_base.124:A64 msg_eval%123 0
  lea.mem lhsaddr.248:A64 = $gen/global_val_48 0
  st var_stk_base.124 0 = lhsaddr.248
  st var_stk_base.124 8 = 54:U64
  lea.stk lhsaddr.249:A64 = msg_eval%123 0
  ld pointer.112:A64 = lhsaddr.249 0
  pusharg 54:U64
  pusharg pointer.112
  pusharg 1:S32
  bsr write
  poparg call.124:S64
  .stk msg_eval%124 8 16
  lea.stk var_stk_base.125:A64 msg_eval%124 0
  lea.mem lhsaddr.250:A64 = $gen/global_val_12 0
  st var_stk_base.125 0 = lhsaddr.250
  st var_stk_base.125 8 = 2:U64
  lea.stk lhsaddr.251:A64 = msg_eval%124 0
  ld pointer.113:A64 = lhsaddr.251 0
  pusharg 2:U64
  pusharg pointer.113
  pusharg 1:S32
  bsr write
  poparg call.125:S64
  .stk msg_eval%125 8 16
  lea.stk var_stk_base.126:A64 msg_eval%125 0
  lea.mem lhsaddr.252:A64 = $gen/global_val_26 0
  st var_stk_base.126 0 = lhsaddr.252
  st var_stk_base.126 8 = 6:U64
  lea.stk lhsaddr.253:A64 = msg_eval%125 0
  ld pointer.114:A64 = lhsaddr.253 0
  pusharg 6:U64
  pusharg pointer.114
  pusharg 1:S32
  bsr write
  poparg call.126:S64
  .stk msg_eval%126 8 16
  lea.stk var_stk_base.127:A64 msg_eval%126 0
  lea.mem lhsaddr.254:A64 = $gen/global_val_14 0
  st var_stk_base.127 0 = lhsaddr.254
  st var_stk_base.127 8 = 4:U64
  lea.stk lhsaddr.255:A64 = msg_eval%126 0
  ld pointer.115:A64 = lhsaddr.255 0
  pusharg 4:U64
  pusharg pointer.115
  pusharg 1:S32
  bsr write
  poparg call.127:S64
  .stk msg_eval%127 8 16
  lea.stk var_stk_base.128:A64 msg_eval%127 0
  lea.mem lhsaddr.256:A64 = $gen/global_val_15 0
  st var_stk_base.128 0 = lhsaddr.256
  st var_stk_base.128 8 = 8:U64
  lea.stk lhsaddr.257:A64 = msg_eval%127 0
  ld pointer.116:A64 = lhsaddr.257 0
  pusharg 8:U64
  pusharg pointer.116
  pusharg 1:S32
  bsr write
  poparg call.128:S64
  .stk msg_eval%128 8 16
  lea.stk var_stk_base.129:A64 msg_eval%128 0
  lea.mem lhsaddr.258:A64 = $gen/global_val_16 0
  st var_stk_base.129 0 = lhsaddr.258
  st var_stk_base.129 8 = 4:U64
  lea.stk lhsaddr.259:A64 = msg_eval%128 0
  ld pointer.117:A64 = lhsaddr.259 0
  pusharg 4:U64
  pusharg pointer.117
  pusharg 1:S32
  bsr write
  poparg call.129:S64
  .stk msg_eval%129 8 16
  lea.stk var_stk_base.130:A64 msg_eval%129 0
  lea.mem lhsaddr.260:A64 = $gen/global_val_48 0
  st var_stk_base.130 0 = lhsaddr.260
  st var_stk_base.130 8 = 54:U64
  lea.stk lhsaddr.261:A64 = msg_eval%129 0
  ld pointer.118:A64 = lhsaddr.261 0
  pusharg 54:U64
  pusharg pointer.118
  pusharg 1:S32
  bsr write
  poparg call.130:S64
  .stk msg_eval%130 8 16
  lea.stk var_stk_base.131:A64 msg_eval%130 0
  lea.mem lhsaddr.262:A64 = $gen/global_val_17 0
  st var_stk_base.131 0 = lhsaddr.262
  st var_stk_base.131 8 = 1:U64
  lea.stk lhsaddr.263:A64 = msg_eval%130 0
  ld pointer.119:A64 = lhsaddr.263 0
  pusharg 1:U64
  pusharg pointer.119
  pusharg 1:S32
  bsr write
  poparg call.131:S64
  trap
.bbl br_join.12
  .reg R64 expr.12
  .stk arg0.12 8 16
  lea.stk var_stk_base.132:A64 arg0.12 0
  lea.mem lhsaddr.264:A64 = $gen/global_val_49 0
  st var_stk_base.132 0 = lhsaddr.264
  st var_stk_base.132 8 = 14:U64
  lea.stk lhsaddr.265:A64 = arg0.12 0
  pusharg lhsaddr.265
  bsr parse_real_test/parse_r64
  poparg call.132:R64
  mov expr.12 = call.132
  bra end_expr.12
.bbl end_expr.12
  mov a_val%27:R64 = expr.12
  bitcast bitcast.11:U64 = a_val%27
  beq 4607182418800017408:U64 bitcast.11 br_join.13
  .stk msg_eval%131 8 16
  lea.stk var_stk_base.133:A64 msg_eval%131 0
  lea.mem lhsaddr.266:A64 = $gen/global_val_9 0
  st var_stk_base.133 0 = lhsaddr.266
  st var_stk_base.133 8 = 11:U64
  lea.stk lhsaddr.267:A64 = msg_eval%131 0
  ld pointer.120:A64 = lhsaddr.267 0
  pusharg 11:U64
  pusharg pointer.120
  pusharg 1:S32
  bsr write
  poparg call.133:S64
  .stk msg_eval%132 8 16
  lea.stk var_stk_base.134:A64 msg_eval%132 0
  lea.mem lhsaddr.268:A64 = $gen/global_val_10 0
  st var_stk_base.134 0 = lhsaddr.268
  st var_stk_base.134 8 = 11:U64
  lea.stk lhsaddr.269:A64 = msg_eval%132 0
  ld pointer.121:A64 = lhsaddr.269 0
  pusharg 11:U64
  pusharg pointer.121
  pusharg 1:S32
  bsr write
  poparg call.134:S64
  .stk msg_eval%133 8 16
  lea.stk var_stk_base.135:A64 msg_eval%133 0
  lea.mem lhsaddr.270:A64 = $gen/global_val_50 0
  st var_stk_base.135 0 = lhsaddr.270
  st var_stk_base.135 8 = 54:U64
  lea.stk lhsaddr.271:A64 = msg_eval%133 0
  ld pointer.122:A64 = lhsaddr.271 0
  pusharg 54:U64
  pusharg pointer.122
  pusharg 1:S32
  bsr write
  poparg call.135:S64
  .stk msg_eval%134 8 16
  lea.stk var_stk_base.136:A64 msg_eval%134 0
  lea.mem lhsaddr.272:A64 = $gen/global_val_12 0
  st var_stk_base.136 0 = lhsaddr.272
  st var_stk_base.136 8 = 2:U64
  lea.stk lhsaddr.273:A64 = msg_eval%134 0
  ld pointer.123:A64 = lhsaddr.273 0
  pusharg 2:U64
  pusharg pointer.123
  pusharg 1:S32
  bsr write
  poparg call.136:S64
  .stk msg_eval%135 8 16
  lea.stk var_stk_base.137:A64 msg_eval%135 0
  lea.mem lhsaddr.274:A64 = $gen/global_val_26 0
  st var_stk_base.137 0 = lhsaddr.274
  st var_stk_base.137 8 = 6:U64
  lea.stk lhsaddr.275:A64 = msg_eval%135 0
  ld pointer.124:A64 = lhsaddr.275 0
  pusharg 6:U64
  pusharg pointer.124
  pusharg 1:S32
  bsr write
  poparg call.137:S64
  .stk msg_eval%136 8 16
  lea.stk var_stk_base.138:A64 msg_eval%136 0
  lea.mem lhsaddr.276:A64 = $gen/global_val_14 0
  st var_stk_base.138 0 = lhsaddr.276
  st var_stk_base.138 8 = 4:U64
  lea.stk lhsaddr.277:A64 = msg_eval%136 0
  ld pointer.125:A64 = lhsaddr.277 0
  pusharg 4:U64
  pusharg pointer.125
  pusharg 1:S32
  bsr write
  poparg call.138:S64
  .stk msg_eval%137 8 16
  lea.stk var_stk_base.139:A64 msg_eval%137 0
  lea.mem lhsaddr.278:A64 = $gen/global_val_15 0
  st var_stk_base.139 0 = lhsaddr.278
  st var_stk_base.139 8 = 8:U64
  lea.stk lhsaddr.279:A64 = msg_eval%137 0
  ld pointer.126:A64 = lhsaddr.279 0
  pusharg 8:U64
  pusharg pointer.126
  pusharg 1:S32
  bsr write
  poparg call.139:S64
  .stk msg_eval%138 8 16
  lea.stk var_stk_base.140:A64 msg_eval%138 0
  lea.mem lhsaddr.280:A64 = $gen/global_val_16 0
  st var_stk_base.140 0 = lhsaddr.280
  st var_stk_base.140 8 = 4:U64
  lea.stk lhsaddr.281:A64 = msg_eval%138 0
  ld pointer.127:A64 = lhsaddr.281 0
  pusharg 4:U64
  pusharg pointer.127
  pusharg 1:S32
  bsr write
  poparg call.140:S64
  .stk msg_eval%139 8 16
  lea.stk var_stk_base.141:A64 msg_eval%139 0
  lea.mem lhsaddr.282:A64 = $gen/global_val_50 0
  st var_stk_base.141 0 = lhsaddr.282
  st var_stk_base.141 8 = 54:U64
  lea.stk lhsaddr.283:A64 = msg_eval%139 0
  ld pointer.128:A64 = lhsaddr.283 0
  pusharg 54:U64
  pusharg pointer.128
  pusharg 1:S32
  bsr write
  poparg call.141:S64
  .stk msg_eval%140 8 16
  lea.stk var_stk_base.142:A64 msg_eval%140 0
  lea.mem lhsaddr.284:A64 = $gen/global_val_17 0
  st var_stk_base.142 0 = lhsaddr.284
  st var_stk_base.142 8 = 1:U64
  lea.stk lhsaddr.285:A64 = msg_eval%140 0
  ld pointer.129:A64 = lhsaddr.285 0
  pusharg 1:U64
  pusharg pointer.129
  pusharg 1:S32
  bsr write
  poparg call.142:S64
  trap
.bbl br_join.13
  .reg R64 expr.13
  .stk arg0.13 8 16
  lea.stk var_stk_base.143:A64 arg0.13 0
  lea.mem lhsaddr.286:A64 = $gen/global_val_51 0
  st var_stk_base.143 0 = lhsaddr.286
  st var_stk_base.143 8 = 3:U64
  lea.stk lhsaddr.287:A64 = arg0.13 0
  pusharg lhsaddr.287
  bsr parse_real_test/parse_r64
  poparg call.143:R64
  mov expr.13 = call.143
  bra end_expr.13
.bbl end_expr.13
  mov a_val%29:R64 = expr.13
  bitcast bitcast.12:U64 = a_val%29
  beq 4649069413771771904:U64 bitcast.12 br_join.14
  .stk msg_eval%141 8 16
  lea.stk var_stk_base.144:A64 msg_eval%141 0
  lea.mem lhsaddr.288:A64 = $gen/global_val_9 0
  st var_stk_base.144 0 = lhsaddr.288
  st var_stk_base.144 8 = 11:U64
  lea.stk lhsaddr.289:A64 = msg_eval%141 0
  ld pointer.130:A64 = lhsaddr.289 0
  pusharg 11:U64
  pusharg pointer.130
  pusharg 1:S32
  bsr write
  poparg call.144:S64
  .stk msg_eval%142 8 16
  lea.stk var_stk_base.145:A64 msg_eval%142 0
  lea.mem lhsaddr.290:A64 = $gen/global_val_10 0
  st var_stk_base.145 0 = lhsaddr.290
  st var_stk_base.145 8 = 11:U64
  lea.stk lhsaddr.291:A64 = msg_eval%142 0
  ld pointer.131:A64 = lhsaddr.291 0
  pusharg 11:U64
  pusharg pointer.131
  pusharg 1:S32
  bsr write
  poparg call.145:S64
  .stk msg_eval%143 8 16
  lea.stk var_stk_base.146:A64 msg_eval%143 0
  lea.mem lhsaddr.292:A64 = $gen/global_val_52 0
  st var_stk_base.146 0 = lhsaddr.292
  st var_stk_base.146 8 = 54:U64
  lea.stk lhsaddr.293:A64 = msg_eval%143 0
  ld pointer.132:A64 = lhsaddr.293 0
  pusharg 54:U64
  pusharg pointer.132
  pusharg 1:S32
  bsr write
  poparg call.146:S64
  .stk msg_eval%144 8 16
  lea.stk var_stk_base.147:A64 msg_eval%144 0
  lea.mem lhsaddr.294:A64 = $gen/global_val_12 0
  st var_stk_base.147 0 = lhsaddr.294
  st var_stk_base.147 8 = 2:U64
  lea.stk lhsaddr.295:A64 = msg_eval%144 0
  ld pointer.133:A64 = lhsaddr.295 0
  pusharg 2:U64
  pusharg pointer.133
  pusharg 1:S32
  bsr write
  poparg call.147:S64
  .stk msg_eval%145 8 16
  lea.stk var_stk_base.148:A64 msg_eval%145 0
  lea.mem lhsaddr.296:A64 = $gen/global_val_26 0
  st var_stk_base.148 0 = lhsaddr.296
  st var_stk_base.148 8 = 6:U64
  lea.stk lhsaddr.297:A64 = msg_eval%145 0
  ld pointer.134:A64 = lhsaddr.297 0
  pusharg 6:U64
  pusharg pointer.134
  pusharg 1:S32
  bsr write
  poparg call.148:S64
  .stk msg_eval%146 8 16
  lea.stk var_stk_base.149:A64 msg_eval%146 0
  lea.mem lhsaddr.298:A64 = $gen/global_val_14 0
  st var_stk_base.149 0 = lhsaddr.298
  st var_stk_base.149 8 = 4:U64
  lea.stk lhsaddr.299:A64 = msg_eval%146 0
  ld pointer.135:A64 = lhsaddr.299 0
  pusharg 4:U64
  pusharg pointer.135
  pusharg 1:S32
  bsr write
  poparg call.149:S64
  .stk msg_eval%147 8 16
  lea.stk var_stk_base.150:A64 msg_eval%147 0
  lea.mem lhsaddr.300:A64 = $gen/global_val_15 0
  st var_stk_base.150 0 = lhsaddr.300
  st var_stk_base.150 8 = 8:U64
  lea.stk lhsaddr.301:A64 = msg_eval%147 0
  ld pointer.136:A64 = lhsaddr.301 0
  pusharg 8:U64
  pusharg pointer.136
  pusharg 1:S32
  bsr write
  poparg call.150:S64
  .stk msg_eval%148 8 16
  lea.stk var_stk_base.151:A64 msg_eval%148 0
  lea.mem lhsaddr.302:A64 = $gen/global_val_16 0
  st var_stk_base.151 0 = lhsaddr.302
  st var_stk_base.151 8 = 4:U64
  lea.stk lhsaddr.303:A64 = msg_eval%148 0
  ld pointer.137:A64 = lhsaddr.303 0
  pusharg 4:U64
  pusharg pointer.137
  pusharg 1:S32
  bsr write
  poparg call.151:S64
  .stk msg_eval%149 8 16
  lea.stk var_stk_base.152:A64 msg_eval%149 0
  lea.mem lhsaddr.304:A64 = $gen/global_val_52 0
  st var_stk_base.152 0 = lhsaddr.304
  st var_stk_base.152 8 = 54:U64
  lea.stk lhsaddr.305:A64 = msg_eval%149 0
  ld pointer.138:A64 = lhsaddr.305 0
  pusharg 54:U64
  pusharg pointer.138
  pusharg 1:S32
  bsr write
  poparg call.152:S64
  .stk msg_eval%150 8 16
  lea.stk var_stk_base.153:A64 msg_eval%150 0
  lea.mem lhsaddr.306:A64 = $gen/global_val_17 0
  st var_stk_base.153 0 = lhsaddr.306
  st var_stk_base.153 8 = 1:U64
  lea.stk lhsaddr.307:A64 = msg_eval%150 0
  ld pointer.139:A64 = lhsaddr.307 0
  pusharg 1:U64
  pusharg pointer.139
  pusharg 1:S32
  bsr write
  poparg call.153:S64
  trap
.bbl br_join.14
  .reg R64 expr.14
  .stk arg0.14 8 16
  lea.stk var_stk_base.154:A64 arg0.14 0
  lea.mem lhsaddr.308:A64 = $gen/global_val_53 0
  st var_stk_base.154 0 = lhsaddr.308
  st var_stk_base.154 8 = 9:U64
  lea.stk lhsaddr.309:A64 = arg0.14 0
  pusharg lhsaddr.309
  bsr parse_real_test/parse_r64
  poparg call.154:R64
  mov expr.14 = call.154
  bra end_expr.14
.bbl end_expr.14
  mov a_val%31:R64 = expr.14
  bitcast bitcast.13:U64 = a_val%31
  beq 4649069413771771904:U64 bitcast.13 br_join.15
  .stk msg_eval%151 8 16
  lea.stk var_stk_base.155:A64 msg_eval%151 0
  lea.mem lhsaddr.310:A64 = $gen/global_val_9 0
  st var_stk_base.155 0 = lhsaddr.310
  st var_stk_base.155 8 = 11:U64
  lea.stk lhsaddr.311:A64 = msg_eval%151 0
  ld pointer.140:A64 = lhsaddr.311 0
  pusharg 11:U64
  pusharg pointer.140
  pusharg 1:S32
  bsr write
  poparg call.155:S64
  .stk msg_eval%152 8 16
  lea.stk var_stk_base.156:A64 msg_eval%152 0
  lea.mem lhsaddr.312:A64 = $gen/global_val_10 0
  st var_stk_base.156 0 = lhsaddr.312
  st var_stk_base.156 8 = 11:U64
  lea.stk lhsaddr.313:A64 = msg_eval%152 0
  ld pointer.141:A64 = lhsaddr.313 0
  pusharg 11:U64
  pusharg pointer.141
  pusharg 1:S32
  bsr write
  poparg call.156:S64
  .stk msg_eval%153 8 16
  lea.stk var_stk_base.157:A64 msg_eval%153 0
  lea.mem lhsaddr.314:A64 = $gen/global_val_54 0
  st var_stk_base.157 0 = lhsaddr.314
  st var_stk_base.157 8 = 54:U64
  lea.stk lhsaddr.315:A64 = msg_eval%153 0
  ld pointer.142:A64 = lhsaddr.315 0
  pusharg 54:U64
  pusharg pointer.142
  pusharg 1:S32
  bsr write
  poparg call.157:S64
  .stk msg_eval%154 8 16
  lea.stk var_stk_base.158:A64 msg_eval%154 0
  lea.mem lhsaddr.316:A64 = $gen/global_val_12 0
  st var_stk_base.158 0 = lhsaddr.316
  st var_stk_base.158 8 = 2:U64
  lea.stk lhsaddr.317:A64 = msg_eval%154 0
  ld pointer.143:A64 = lhsaddr.317 0
  pusharg 2:U64
  pusharg pointer.143
  pusharg 1:S32
  bsr write
  poparg call.158:S64
  .stk msg_eval%155 8 16
  lea.stk var_stk_base.159:A64 msg_eval%155 0
  lea.mem lhsaddr.318:A64 = $gen/global_val_26 0
  st var_stk_base.159 0 = lhsaddr.318
  st var_stk_base.159 8 = 6:U64
  lea.stk lhsaddr.319:A64 = msg_eval%155 0
  ld pointer.144:A64 = lhsaddr.319 0
  pusharg 6:U64
  pusharg pointer.144
  pusharg 1:S32
  bsr write
  poparg call.159:S64
  .stk msg_eval%156 8 16
  lea.stk var_stk_base.160:A64 msg_eval%156 0
  lea.mem lhsaddr.320:A64 = $gen/global_val_14 0
  st var_stk_base.160 0 = lhsaddr.320
  st var_stk_base.160 8 = 4:U64
  lea.stk lhsaddr.321:A64 = msg_eval%156 0
  ld pointer.145:A64 = lhsaddr.321 0
  pusharg 4:U64
  pusharg pointer.145
  pusharg 1:S32
  bsr write
  poparg call.160:S64
  .stk msg_eval%157 8 16
  lea.stk var_stk_base.161:A64 msg_eval%157 0
  lea.mem lhsaddr.322:A64 = $gen/global_val_15 0
  st var_stk_base.161 0 = lhsaddr.322
  st var_stk_base.161 8 = 8:U64
  lea.stk lhsaddr.323:A64 = msg_eval%157 0
  ld pointer.146:A64 = lhsaddr.323 0
  pusharg 8:U64
  pusharg pointer.146
  pusharg 1:S32
  bsr write
  poparg call.161:S64
  .stk msg_eval%158 8 16
  lea.stk var_stk_base.162:A64 msg_eval%158 0
  lea.mem lhsaddr.324:A64 = $gen/global_val_16 0
  st var_stk_base.162 0 = lhsaddr.324
  st var_stk_base.162 8 = 4:U64
  lea.stk lhsaddr.325:A64 = msg_eval%158 0
  ld pointer.147:A64 = lhsaddr.325 0
  pusharg 4:U64
  pusharg pointer.147
  pusharg 1:S32
  bsr write
  poparg call.162:S64
  .stk msg_eval%159 8 16
  lea.stk var_stk_base.163:A64 msg_eval%159 0
  lea.mem lhsaddr.326:A64 = $gen/global_val_54 0
  st var_stk_base.163 0 = lhsaddr.326
  st var_stk_base.163 8 = 54:U64
  lea.stk lhsaddr.327:A64 = msg_eval%159 0
  ld pointer.148:A64 = lhsaddr.327 0
  pusharg 54:U64
  pusharg pointer.148
  pusharg 1:S32
  bsr write
  poparg call.163:S64
  .stk msg_eval%160 8 16
  lea.stk var_stk_base.164:A64 msg_eval%160 0
  lea.mem lhsaddr.328:A64 = $gen/global_val_17 0
  st var_stk_base.164 0 = lhsaddr.328
  st var_stk_base.164 8 = 1:U64
  lea.stk lhsaddr.329:A64 = msg_eval%160 0
  ld pointer.149:A64 = lhsaddr.329 0
  pusharg 1:U64
  pusharg pointer.149
  pusharg 1:S32
  bsr write
  poparg call.164:S64
  trap
.bbl br_join.15
  .reg R64 expr.15
  .stk arg0.15 8 16
  lea.stk var_stk_base.165:A64 arg0.15 0
  lea.mem lhsaddr.330:A64 = $gen/global_val_55 0
  st var_stk_base.165 0 = lhsaddr.330
  st var_stk_base.165 8 = 6:U64
  lea.stk lhsaddr.331:A64 = arg0.15 0
  pusharg lhsaddr.331
  bsr parse_real_test/parse_r64
  poparg call.165:R64
  mov expr.15 = call.165
  bra end_expr.15
.bbl end_expr.15
  mov a_val%33:R64 = expr.15
  bitcast bitcast.14:U64 = a_val%33
  beq 0:U64 bitcast.14 br_join.16
  .stk msg_eval%161 8 16
  lea.stk var_stk_base.166:A64 msg_eval%161 0
  lea.mem lhsaddr.332:A64 = $gen/global_val_9 0
  st var_stk_base.166 0 = lhsaddr.332
  st var_stk_base.166 8 = 11:U64
  lea.stk lhsaddr.333:A64 = msg_eval%161 0
  ld pointer.150:A64 = lhsaddr.333 0
  pusharg 11:U64
  pusharg pointer.150
  pusharg 1:S32
  bsr write
  poparg call.166:S64
  .stk msg_eval%162 8 16
  lea.stk var_stk_base.167:A64 msg_eval%162 0
  lea.mem lhsaddr.334:A64 = $gen/global_val_10 0
  st var_stk_base.167 0 = lhsaddr.334
  st var_stk_base.167 8 = 11:U64
  lea.stk lhsaddr.335:A64 = msg_eval%162 0
  ld pointer.151:A64 = lhsaddr.335 0
  pusharg 11:U64
  pusharg pointer.151
  pusharg 1:S32
  bsr write
  poparg call.167:S64
  .stk msg_eval%163 8 16
  lea.stk var_stk_base.168:A64 msg_eval%163 0
  lea.mem lhsaddr.336:A64 = $gen/global_val_56 0
  st var_stk_base.168 0 = lhsaddr.336
  st var_stk_base.168 8 = 54:U64
  lea.stk lhsaddr.337:A64 = msg_eval%163 0
  ld pointer.152:A64 = lhsaddr.337 0
  pusharg 54:U64
  pusharg pointer.152
  pusharg 1:S32
  bsr write
  poparg call.168:S64
  .stk msg_eval%164 8 16
  lea.stk var_stk_base.169:A64 msg_eval%164 0
  lea.mem lhsaddr.338:A64 = $gen/global_val_12 0
  st var_stk_base.169 0 = lhsaddr.338
  st var_stk_base.169 8 = 2:U64
  lea.stk lhsaddr.339:A64 = msg_eval%164 0
  ld pointer.153:A64 = lhsaddr.339 0
  pusharg 2:U64
  pusharg pointer.153
  pusharg 1:S32
  bsr write
  poparg call.169:S64
  .stk msg_eval%165 8 16
  lea.stk var_stk_base.170:A64 msg_eval%165 0
  lea.mem lhsaddr.340:A64 = $gen/global_val_26 0
  st var_stk_base.170 0 = lhsaddr.340
  st var_stk_base.170 8 = 6:U64
  lea.stk lhsaddr.341:A64 = msg_eval%165 0
  ld pointer.154:A64 = lhsaddr.341 0
  pusharg 6:U64
  pusharg pointer.154
  pusharg 1:S32
  bsr write
  poparg call.170:S64
  .stk msg_eval%166 8 16
  lea.stk var_stk_base.171:A64 msg_eval%166 0
  lea.mem lhsaddr.342:A64 = $gen/global_val_14 0
  st var_stk_base.171 0 = lhsaddr.342
  st var_stk_base.171 8 = 4:U64
  lea.stk lhsaddr.343:A64 = msg_eval%166 0
  ld pointer.155:A64 = lhsaddr.343 0
  pusharg 4:U64
  pusharg pointer.155
  pusharg 1:S32
  bsr write
  poparg call.171:S64
  .stk msg_eval%167 8 16
  lea.stk var_stk_base.172:A64 msg_eval%167 0
  lea.mem lhsaddr.344:A64 = $gen/global_val_15 0
  st var_stk_base.172 0 = lhsaddr.344
  st var_stk_base.172 8 = 8:U64
  lea.stk lhsaddr.345:A64 = msg_eval%167 0
  ld pointer.156:A64 = lhsaddr.345 0
  pusharg 8:U64
  pusharg pointer.156
  pusharg 1:S32
  bsr write
  poparg call.172:S64
  .stk msg_eval%168 8 16
  lea.stk var_stk_base.173:A64 msg_eval%168 0
  lea.mem lhsaddr.346:A64 = $gen/global_val_16 0
  st var_stk_base.173 0 = lhsaddr.346
  st var_stk_base.173 8 = 4:U64
  lea.stk lhsaddr.347:A64 = msg_eval%168 0
  ld pointer.157:A64 = lhsaddr.347 0
  pusharg 4:U64
  pusharg pointer.157
  pusharg 1:S32
  bsr write
  poparg call.173:S64
  .stk msg_eval%169 8 16
  lea.stk var_stk_base.174:A64 msg_eval%169 0
  lea.mem lhsaddr.348:A64 = $gen/global_val_56 0
  st var_stk_base.174 0 = lhsaddr.348
  st var_stk_base.174 8 = 54:U64
  lea.stk lhsaddr.349:A64 = msg_eval%169 0
  ld pointer.158:A64 = lhsaddr.349 0
  pusharg 54:U64
  pusharg pointer.158
  pusharg 1:S32
  bsr write
  poparg call.174:S64
  .stk msg_eval%170 8 16
  lea.stk var_stk_base.175:A64 msg_eval%170 0
  lea.mem lhsaddr.350:A64 = $gen/global_val_17 0
  st var_stk_base.175 0 = lhsaddr.350
  st var_stk_base.175 8 = 1:U64
  lea.stk lhsaddr.351:A64 = msg_eval%170 0
  ld pointer.159:A64 = lhsaddr.351 0
  pusharg 1:U64
  pusharg pointer.159
  pusharg 1:S32
  bsr write
  poparg call.175:S64
  trap
.bbl br_join.16
  .reg R64 expr.16
  .stk arg0.16 8 16
  lea.stk var_stk_base.176:A64 arg0.16 0
  lea.mem lhsaddr.352:A64 = $gen/global_val_57 0
  st var_stk_base.176 0 = lhsaddr.352
  st var_stk_base.176 8 = 7:U64
  lea.stk lhsaddr.353:A64 = arg0.16 0
  pusharg lhsaddr.353
  bsr parse_real_test/parse_r64
  poparg call.176:R64
  mov expr.16 = call.176
  bra end_expr.16
.bbl end_expr.16
  mov a_val%35:R64 = expr.16
  bitcast bitcast.15:U64 = a_val%35
  beq 9223372036854775808:U64 bitcast.15 br_join.17
  .stk msg_eval%171 8 16
  lea.stk var_stk_base.177:A64 msg_eval%171 0
  lea.mem lhsaddr.354:A64 = $gen/global_val_9 0
  st var_stk_base.177 0 = lhsaddr.354
  st var_stk_base.177 8 = 11:U64
  lea.stk lhsaddr.355:A64 = msg_eval%171 0
  ld pointer.160:A64 = lhsaddr.355 0
  pusharg 11:U64
  pusharg pointer.160
  pusharg 1:S32
  bsr write
  poparg call.177:S64
  .stk msg_eval%172 8 16
  lea.stk var_stk_base.178:A64 msg_eval%172 0
  lea.mem lhsaddr.356:A64 = $gen/global_val_10 0
  st var_stk_base.178 0 = lhsaddr.356
  st var_stk_base.178 8 = 11:U64
  lea.stk lhsaddr.357:A64 = msg_eval%172 0
  ld pointer.161:A64 = lhsaddr.357 0
  pusharg 11:U64
  pusharg pointer.161
  pusharg 1:S32
  bsr write
  poparg call.178:S64
  .stk msg_eval%173 8 16
  lea.stk var_stk_base.179:A64 msg_eval%173 0
  lea.mem lhsaddr.358:A64 = $gen/global_val_58 0
  st var_stk_base.179 0 = lhsaddr.358
  st var_stk_base.179 8 = 54:U64
  lea.stk lhsaddr.359:A64 = msg_eval%173 0
  ld pointer.162:A64 = lhsaddr.359 0
  pusharg 54:U64
  pusharg pointer.162
  pusharg 1:S32
  bsr write
  poparg call.179:S64
  .stk msg_eval%174 8 16
  lea.stk var_stk_base.180:A64 msg_eval%174 0
  lea.mem lhsaddr.360:A64 = $gen/global_val_12 0
  st var_stk_base.180 0 = lhsaddr.360
  st var_stk_base.180 8 = 2:U64
  lea.stk lhsaddr.361:A64 = msg_eval%174 0
  ld pointer.163:A64 = lhsaddr.361 0
  pusharg 2:U64
  pusharg pointer.163
  pusharg 1:S32
  bsr write
  poparg call.180:S64
  .stk msg_eval%175 8 16
  lea.stk var_stk_base.181:A64 msg_eval%175 0
  lea.mem lhsaddr.362:A64 = $gen/global_val_26 0
  st var_stk_base.181 0 = lhsaddr.362
  st var_stk_base.181 8 = 6:U64
  lea.stk lhsaddr.363:A64 = msg_eval%175 0
  ld pointer.164:A64 = lhsaddr.363 0
  pusharg 6:U64
  pusharg pointer.164
  pusharg 1:S32
  bsr write
  poparg call.181:S64
  .stk msg_eval%176 8 16
  lea.stk var_stk_base.182:A64 msg_eval%176 0
  lea.mem lhsaddr.364:A64 = $gen/global_val_14 0
  st var_stk_base.182 0 = lhsaddr.364
  st var_stk_base.182 8 = 4:U64
  lea.stk lhsaddr.365:A64 = msg_eval%176 0
  ld pointer.165:A64 = lhsaddr.365 0
  pusharg 4:U64
  pusharg pointer.165
  pusharg 1:S32
  bsr write
  poparg call.182:S64
  .stk msg_eval%177 8 16
  lea.stk var_stk_base.183:A64 msg_eval%177 0
  lea.mem lhsaddr.366:A64 = $gen/global_val_15 0
  st var_stk_base.183 0 = lhsaddr.366
  st var_stk_base.183 8 = 8:U64
  lea.stk lhsaddr.367:A64 = msg_eval%177 0
  ld pointer.166:A64 = lhsaddr.367 0
  pusharg 8:U64
  pusharg pointer.166
  pusharg 1:S32
  bsr write
  poparg call.183:S64
  .stk msg_eval%178 8 16
  lea.stk var_stk_base.184:A64 msg_eval%178 0
  lea.mem lhsaddr.368:A64 = $gen/global_val_16 0
  st var_stk_base.184 0 = lhsaddr.368
  st var_stk_base.184 8 = 4:U64
  lea.stk lhsaddr.369:A64 = msg_eval%178 0
  ld pointer.167:A64 = lhsaddr.369 0
  pusharg 4:U64
  pusharg pointer.167
  pusharg 1:S32
  bsr write
  poparg call.184:S64
  .stk msg_eval%179 8 16
  lea.stk var_stk_base.185:A64 msg_eval%179 0
  lea.mem lhsaddr.370:A64 = $gen/global_val_58 0
  st var_stk_base.185 0 = lhsaddr.370
  st var_stk_base.185 8 = 54:U64
  lea.stk lhsaddr.371:A64 = msg_eval%179 0
  ld pointer.168:A64 = lhsaddr.371 0
  pusharg 54:U64
  pusharg pointer.168
  pusharg 1:S32
  bsr write
  poparg call.185:S64
  .stk msg_eval%180 8 16
  lea.stk var_stk_base.186:A64 msg_eval%180 0
  lea.mem lhsaddr.372:A64 = $gen/global_val_17 0
  st var_stk_base.186 0 = lhsaddr.372
  st var_stk_base.186 8 = 1:U64
  lea.stk lhsaddr.373:A64 = msg_eval%180 0
  ld pointer.169:A64 = lhsaddr.373 0
  pusharg 1:U64
  pusharg pointer.169
  pusharg 1:S32
  bsr write
  poparg call.186:S64
  trap
.bbl br_join.17
  .reg R64 expr.17
  .stk arg0.17 8 16
  lea.stk var_stk_base.187:A64 arg0.17 0
  lea.mem lhsaddr.374:A64 = $gen/global_val_59 0
  st var_stk_base.187 0 = lhsaddr.374
  st var_stk_base.187 8 = 6:U64
  lea.stk lhsaddr.375:A64 = arg0.17 0
  pusharg lhsaddr.375
  bsr parse_real_test/parse_r64
  poparg call.187:R64
  mov expr.17 = call.187
  bra end_expr.17
.bbl end_expr.17
  mov a_val%37:R64 = expr.17
  bitcast bitcast.16:U64 = a_val%37
  beq 9218868437227405312:U64 bitcast.16 br_join.18
  .stk msg_eval%181 8 16
  lea.stk var_stk_base.188:A64 msg_eval%181 0
  lea.mem lhsaddr.376:A64 = $gen/global_val_9 0
  st var_stk_base.188 0 = lhsaddr.376
  st var_stk_base.188 8 = 11:U64
  lea.stk lhsaddr.377:A64 = msg_eval%181 0
  ld pointer.170:A64 = lhsaddr.377 0
  pusharg 11:U64
  pusharg pointer.170
  pusharg 1:S32
  bsr write
  poparg call.188:S64
  .stk msg_eval%182 8 16
  lea.stk var_stk_base.189:A64 msg_eval%182 0
  lea.mem lhsaddr.378:A64 = $gen/global_val_10 0
  st var_stk_base.189 0 = lhsaddr.378
  st var_stk_base.189 8 = 11:U64
  lea.stk lhsaddr.379:A64 = msg_eval%182 0
  ld pointer.171:A64 = lhsaddr.379 0
  pusharg 11:U64
  pusharg pointer.171
  pusharg 1:S32
  bsr write
  poparg call.189:S64
  .stk msg_eval%183 8 16
  lea.stk var_stk_base.190:A64 msg_eval%183 0
  lea.mem lhsaddr.380:A64 = $gen/global_val_60 0
  st var_stk_base.190 0 = lhsaddr.380
  st var_stk_base.190 8 = 54:U64
  lea.stk lhsaddr.381:A64 = msg_eval%183 0
  ld pointer.172:A64 = lhsaddr.381 0
  pusharg 54:U64
  pusharg pointer.172
  pusharg 1:S32
  bsr write
  poparg call.190:S64
  .stk msg_eval%184 8 16
  lea.stk var_stk_base.191:A64 msg_eval%184 0
  lea.mem lhsaddr.382:A64 = $gen/global_val_12 0
  st var_stk_base.191 0 = lhsaddr.382
  st var_stk_base.191 8 = 2:U64
  lea.stk lhsaddr.383:A64 = msg_eval%184 0
  ld pointer.173:A64 = lhsaddr.383 0
  pusharg 2:U64
  pusharg pointer.173
  pusharg 1:S32
  bsr write
  poparg call.191:S64
  .stk msg_eval%185 8 16
  lea.stk var_stk_base.192:A64 msg_eval%185 0
  lea.mem lhsaddr.384:A64 = $gen/global_val_13 0
  st var_stk_base.192 0 = lhsaddr.384
  st var_stk_base.192 8 = 2:U64
  lea.stk lhsaddr.385:A64 = msg_eval%185 0
  ld pointer.174:A64 = lhsaddr.385 0
  pusharg 2:U64
  pusharg pointer.174
  pusharg 1:S32
  bsr write
  poparg call.192:S64
  .stk msg_eval%186 8 16
  lea.stk var_stk_base.193:A64 msg_eval%186 0
  lea.mem lhsaddr.386:A64 = $gen/global_val_14 0
  st var_stk_base.193 0 = lhsaddr.386
  st var_stk_base.193 8 = 4:U64
  lea.stk lhsaddr.387:A64 = msg_eval%186 0
  ld pointer.175:A64 = lhsaddr.387 0
  pusharg 4:U64
  pusharg pointer.175
  pusharg 1:S32
  bsr write
  poparg call.193:S64
  .stk msg_eval%187 8 16
  lea.stk var_stk_base.194:A64 msg_eval%187 0
  lea.mem lhsaddr.388:A64 = $gen/global_val_15 0
  st var_stk_base.194 0 = lhsaddr.388
  st var_stk_base.194 8 = 8:U64
  lea.stk lhsaddr.389:A64 = msg_eval%187 0
  ld pointer.176:A64 = lhsaddr.389 0
  pusharg 8:U64
  pusharg pointer.176
  pusharg 1:S32
  bsr write
  poparg call.194:S64
  .stk msg_eval%188 8 16
  lea.stk var_stk_base.195:A64 msg_eval%188 0
  lea.mem lhsaddr.390:A64 = $gen/global_val_16 0
  st var_stk_base.195 0 = lhsaddr.390
  st var_stk_base.195 8 = 4:U64
  lea.stk lhsaddr.391:A64 = msg_eval%188 0
  ld pointer.177:A64 = lhsaddr.391 0
  pusharg 4:U64
  pusharg pointer.177
  pusharg 1:S32
  bsr write
  poparg call.195:S64
  .stk msg_eval%189 8 16
  lea.stk var_stk_base.196:A64 msg_eval%189 0
  lea.mem lhsaddr.392:A64 = $gen/global_val_60 0
  st var_stk_base.196 0 = lhsaddr.392
  st var_stk_base.196 8 = 54:U64
  lea.stk lhsaddr.393:A64 = msg_eval%189 0
  ld pointer.178:A64 = lhsaddr.393 0
  pusharg 54:U64
  pusharg pointer.178
  pusharg 1:S32
  bsr write
  poparg call.196:S64
  .stk msg_eval%190 8 16
  lea.stk var_stk_base.197:A64 msg_eval%190 0
  lea.mem lhsaddr.394:A64 = $gen/global_val_17 0
  st var_stk_base.197 0 = lhsaddr.394
  st var_stk_base.197 8 = 1:U64
  lea.stk lhsaddr.395:A64 = msg_eval%190 0
  ld pointer.179:A64 = lhsaddr.395 0
  pusharg 1:U64
  pusharg pointer.179
  pusharg 1:S32
  bsr write
  poparg call.197:S64
  trap
.bbl br_join.18
  .reg R64 expr.18
  .stk arg0.18 8 16
  lea.stk var_stk_base.198:A64 arg0.18 0
  lea.mem lhsaddr.396:A64 = $gen/global_val_61 0
  st var_stk_base.198 0 = lhsaddr.396
  st var_stk_base.198 8 = 7:U64
  lea.stk lhsaddr.397:A64 = arg0.18 0
  pusharg lhsaddr.397
  bsr parse_real_test/parse_r64
  poparg call.198:R64
  mov expr.18 = call.198
  bra end_expr.18
.bbl end_expr.18
  mov a_val%39:R64 = expr.18
  bitcast bitcast.17:U64 = a_val%39
  beq 18442240474082181120:U64 bitcast.17 br_join.19
  .stk msg_eval%191 8 16
  lea.stk var_stk_base.199:A64 msg_eval%191 0
  lea.mem lhsaddr.398:A64 = $gen/global_val_9 0
  st var_stk_base.199 0 = lhsaddr.398
  st var_stk_base.199 8 = 11:U64
  lea.stk lhsaddr.399:A64 = msg_eval%191 0
  ld pointer.180:A64 = lhsaddr.399 0
  pusharg 11:U64
  pusharg pointer.180
  pusharg 1:S32
  bsr write
  poparg call.199:S64
  .stk msg_eval%192 8 16
  lea.stk var_stk_base.200:A64 msg_eval%192 0
  lea.mem lhsaddr.400:A64 = $gen/global_val_10 0
  st var_stk_base.200 0 = lhsaddr.400
  st var_stk_base.200 8 = 11:U64
  lea.stk lhsaddr.401:A64 = msg_eval%192 0
  ld pointer.181:A64 = lhsaddr.401 0
  pusharg 11:U64
  pusharg pointer.181
  pusharg 1:S32
  bsr write
  poparg call.200:S64
  .stk msg_eval%193 8 16
  lea.stk var_stk_base.201:A64 msg_eval%193 0
  lea.mem lhsaddr.402:A64 = $gen/global_val_62 0
  st var_stk_base.201 0 = lhsaddr.402
  st var_stk_base.201 8 = 54:U64
  lea.stk lhsaddr.403:A64 = msg_eval%193 0
  ld pointer.182:A64 = lhsaddr.403 0
  pusharg 54:U64
  pusharg pointer.182
  pusharg 1:S32
  bsr write
  poparg call.201:S64
  .stk msg_eval%194 8 16
  lea.stk var_stk_base.202:A64 msg_eval%194 0
  lea.mem lhsaddr.404:A64 = $gen/global_val_12 0
  st var_stk_base.202 0 = lhsaddr.404
  st var_stk_base.202 8 = 2:U64
  lea.stk lhsaddr.405:A64 = msg_eval%194 0
  ld pointer.183:A64 = lhsaddr.405 0
  pusharg 2:U64
  pusharg pointer.183
  pusharg 1:S32
  bsr write
  poparg call.202:S64
  .stk msg_eval%195 8 16
  lea.stk var_stk_base.203:A64 msg_eval%195 0
  lea.mem lhsaddr.406:A64 = $gen/global_val_13 0
  st var_stk_base.203 0 = lhsaddr.406
  st var_stk_base.203 8 = 2:U64
  lea.stk lhsaddr.407:A64 = msg_eval%195 0
  ld pointer.184:A64 = lhsaddr.407 0
  pusharg 2:U64
  pusharg pointer.184
  pusharg 1:S32
  bsr write
  poparg call.203:S64
  .stk msg_eval%196 8 16
  lea.stk var_stk_base.204:A64 msg_eval%196 0
  lea.mem lhsaddr.408:A64 = $gen/global_val_14 0
  st var_stk_base.204 0 = lhsaddr.408
  st var_stk_base.204 8 = 4:U64
  lea.stk lhsaddr.409:A64 = msg_eval%196 0
  ld pointer.185:A64 = lhsaddr.409 0
  pusharg 4:U64
  pusharg pointer.185
  pusharg 1:S32
  bsr write
  poparg call.204:S64
  .stk msg_eval%197 8 16
  lea.stk var_stk_base.205:A64 msg_eval%197 0
  lea.mem lhsaddr.410:A64 = $gen/global_val_15 0
  st var_stk_base.205 0 = lhsaddr.410
  st var_stk_base.205 8 = 8:U64
  lea.stk lhsaddr.411:A64 = msg_eval%197 0
  ld pointer.186:A64 = lhsaddr.411 0
  pusharg 8:U64
  pusharg pointer.186
  pusharg 1:S32
  bsr write
  poparg call.205:S64
  .stk msg_eval%198 8 16
  lea.stk var_stk_base.206:A64 msg_eval%198 0
  lea.mem lhsaddr.412:A64 = $gen/global_val_16 0
  st var_stk_base.206 0 = lhsaddr.412
  st var_stk_base.206 8 = 4:U64
  lea.stk lhsaddr.413:A64 = msg_eval%198 0
  ld pointer.187:A64 = lhsaddr.413 0
  pusharg 4:U64
  pusharg pointer.187
  pusharg 1:S32
  bsr write
  poparg call.206:S64
  .stk msg_eval%199 8 16
  lea.stk var_stk_base.207:A64 msg_eval%199 0
  lea.mem lhsaddr.414:A64 = $gen/global_val_62 0
  st var_stk_base.207 0 = lhsaddr.414
  st var_stk_base.207 8 = 54:U64
  lea.stk lhsaddr.415:A64 = msg_eval%199 0
  ld pointer.188:A64 = lhsaddr.415 0
  pusharg 54:U64
  pusharg pointer.188
  pusharg 1:S32
  bsr write
  poparg call.207:S64
  .stk msg_eval%200 8 16
  lea.stk var_stk_base.208:A64 msg_eval%200 0
  lea.mem lhsaddr.416:A64 = $gen/global_val_17 0
  st var_stk_base.208 0 = lhsaddr.416
  st var_stk_base.208 8 = 1:U64
  lea.stk lhsaddr.417:A64 = msg_eval%200 0
  ld pointer.189:A64 = lhsaddr.417 0
  pusharg 1:U64
  pusharg pointer.189
  pusharg 1:S32
  bsr write
  poparg call.208:S64
  trap
.bbl br_join.19
  .stk e_val%41 8 16
  lea.stk var_stk_base.209:A64 e_val%41 0
  st var_stk_base.209 0 = 0x1.921fb54442d18p+1:R64
  st var_stk_base.209 8 = 0x1.203af9ee75616p-51:R64
  .stk a_val%41 8 16
  lea.stk var_stk_base.210:A64 a_val%41 0
  .stk arg0.19 8 16
  lea.stk var_stk_base.211:A64 arg0.19 0
  lea.mem lhsaddr.418:A64 = $gen/global_val_63 0
  st var_stk_base.211 0 = lhsaddr.418
  st var_stk_base.211 8 = 26:U64
  lea.stk lhsaddr.419:A64 = arg0.19 0
  pusharg lhsaddr.419
  bsr parse_real_test/parse_r64
  poparg call.209:R64
  st var_stk_base.210 0 = call.209
  bra end_expr.19
.bbl end_expr.19
  st var_stk_base.210 8 = 0:U64
  .reg U8 expr.19
  .stk arg0.20 8 16
  lea.stk var_stk_base.212:A64 arg0.20 0
  lea.stk lhsaddr.420:A64 = e_val%41 0
  .reg U64 copy
  ld copy = lhsaddr.420 0
  st var_stk_base.212 0 = copy
  ld copy = lhsaddr.420 8
  st var_stk_base.212 8 = copy
  .stk arg1 8 16
  lea.stk var_stk_base.213:A64 arg1 0
  lea.stk lhsaddr.421:A64 = a_val%41 0
  .reg U64 copy.1
  ld copy.1 = lhsaddr.421 0
  st var_stk_base.213 0 = copy.1
  ld copy.1 = lhsaddr.421 8
  st var_stk_base.213 8 = copy.1
  lea.stk lhsaddr.422:A64 = arg0.20 0
  lea.stk lhsaddr.423:A64 = arg1 0
  pusharg lhsaddr.423
  pusharg lhsaddr.422
  bsr cmp/eq<ptr<rec<cmp/r64r>>>
  poparg call.210:U8
  mov expr.19 = call.210
  bra end_expr.20
.bbl end_expr.20
  bne expr.19 0 br_join.20
  .stk msg_eval%201 8 16
  lea.stk var_stk_base.214:A64 msg_eval%201 0
  lea.mem lhsaddr.424:A64 = $gen/global_val_30 0
  st var_stk_base.214 0 = lhsaddr.424
  st var_stk_base.214 8 = 8:U64
  lea.stk lhsaddr.425:A64 = msg_eval%201 0
  ld pointer.190:A64 = lhsaddr.425 0
  pusharg 8:U64
  pusharg pointer.190
  pusharg 1:S32
  bsr write
  poparg call.211:S64
  .stk msg_eval%202 8 16
  lea.stk var_stk_base.215:A64 msg_eval%202 0
  lea.mem lhsaddr.426:A64 = $gen/global_val_10 0
  st var_stk_base.215 0 = lhsaddr.426
  st var_stk_base.215 8 = 11:U64
  lea.stk lhsaddr.427:A64 = msg_eval%202 0
  ld pointer.191:A64 = lhsaddr.427 0
  pusharg 11:U64
  pusharg pointer.191
  pusharg 1:S32
  bsr write
  poparg call.212:S64
  .stk msg_eval%203 8 16
  lea.stk var_stk_base.216:A64 msg_eval%203 0
  lea.mem lhsaddr.428:A64 = $gen/global_val_64 0
  st var_stk_base.216 0 = lhsaddr.428
  st var_stk_base.216 8 = 54:U64
  lea.stk lhsaddr.429:A64 = msg_eval%203 0
  ld pointer.192:A64 = lhsaddr.429 0
  pusharg 54:U64
  pusharg pointer.192
  pusharg 1:S32
  bsr write
  poparg call.213:S64
  .stk msg_eval%204 8 16
  lea.stk var_stk_base.217:A64 msg_eval%204 0
  lea.mem lhsaddr.430:A64 = $gen/global_val_12 0
  st var_stk_base.217 0 = lhsaddr.430
  st var_stk_base.217 8 = 2:U64
  lea.stk lhsaddr.431:A64 = msg_eval%204 0
  ld pointer.193:A64 = lhsaddr.431 0
  pusharg 2:U64
  pusharg pointer.193
  pusharg 1:S32
  bsr write
  poparg call.214:S64
  .stk msg_eval%205 8 16
  lea.stk var_stk_base.218:A64 msg_eval%205 0
  lea.mem lhsaddr.432:A64 = $gen/global_val_65 0
  st var_stk_base.218 0 = lhsaddr.432
  st var_stk_base.218 8 = 11:U64
  lea.stk lhsaddr.433:A64 = msg_eval%205 0
  ld pointer.194:A64 = lhsaddr.433 0
  pusharg 11:U64
  pusharg pointer.194
  pusharg 1:S32
  bsr write
  poparg call.215:S64
  .stk msg_eval%206 8 16
  lea.stk var_stk_base.219:A64 msg_eval%206 0
  lea.mem lhsaddr.434:A64 = $gen/global_val_14 0
  st var_stk_base.219 0 = lhsaddr.434
  st var_stk_base.219 8 = 4:U64
  lea.stk lhsaddr.435:A64 = msg_eval%206 0
  ld pointer.195:A64 = lhsaddr.435 0
  pusharg 4:U64
  pusharg pointer.195
  pusharg 1:S32
  bsr write
  poparg call.216:S64
  .stk msg_eval%207 8 16
  lea.stk var_stk_base.220:A64 msg_eval%207 0
  lea.mem lhsaddr.436:A64 = $gen/global_val_65 0
  st var_stk_base.220 0 = lhsaddr.436
  st var_stk_base.220 8 = 11:U64
  lea.stk lhsaddr.437:A64 = msg_eval%207 0
  ld pointer.196:A64 = lhsaddr.437 0
  pusharg 11:U64
  pusharg pointer.196
  pusharg 1:S32
  bsr write
  poparg call.217:S64
  .stk msg_eval%208 8 16
  lea.stk var_stk_base.221:A64 msg_eval%208 0
  lea.mem lhsaddr.438:A64 = $gen/global_val_16 0
  st var_stk_base.221 0 = lhsaddr.438
  st var_stk_base.221 8 = 4:U64
  lea.stk lhsaddr.439:A64 = msg_eval%208 0
  ld pointer.197:A64 = lhsaddr.439 0
  pusharg 4:U64
  pusharg pointer.197
  pusharg 1:S32
  bsr write
  poparg call.218:S64
  .stk msg_eval%209 8 16
  lea.stk var_stk_base.222:A64 msg_eval%209 0
  lea.mem lhsaddr.440:A64 = $gen/global_val_64 0
  st var_stk_base.222 0 = lhsaddr.440
  st var_stk_base.222 8 = 54:U64
  lea.stk lhsaddr.441:A64 = msg_eval%209 0
  ld pointer.198:A64 = lhsaddr.441 0
  pusharg 54:U64
  pusharg pointer.198
  pusharg 1:S32
  bsr write
  poparg call.219:S64
  .stk msg_eval%210 8 16
  lea.stk var_stk_base.223:A64 msg_eval%210 0
  lea.mem lhsaddr.442:A64 = $gen/global_val_17 0
  st var_stk_base.223 0 = lhsaddr.442
  st var_stk_base.223 8 = 1:U64
  lea.stk lhsaddr.443:A64 = msg_eval%210 0
  ld pointer.199:A64 = lhsaddr.443 0
  pusharg 1:U64
  pusharg pointer.199
  pusharg 1:S32
  bsr write
  poparg call.220:S64
  trap
.bbl br_join.20
  .stk e_val%43 8 16
  lea.stk var_stk_base.224:A64 e_val%43 0
  st var_stk_base.224 0 = 0x1.5bf0a8b145769p+1:R64
  st var_stk_base.224 8 = 0x1.203af9ee75616p-51:R64
  .stk a_val%43 8 16
  lea.stk var_stk_base.225:A64 a_val%43 0
  .stk arg0.21 8 16
  lea.stk var_stk_base.226:A64 arg0.21 0
  lea.mem lhsaddr.444:A64 = $gen/global_val_66 0
  st var_stk_base.226 0 = lhsaddr.444
  st var_stk_base.226 8 = 26:U64
  lea.stk lhsaddr.445:A64 = arg0.21 0
  pusharg lhsaddr.445
  bsr parse_real_test/parse_r64
  poparg call.221:R64
  st var_stk_base.225 0 = call.221
  bra end_expr.21
.bbl end_expr.21
  st var_stk_base.225 8 = 0:U64
  .reg U8 expr.20
  .stk arg0.22 8 16
  lea.stk var_stk_base.227:A64 arg0.22 0
  lea.stk lhsaddr.446:A64 = e_val%43 0
  .reg U64 copy.2
  ld copy.2 = lhsaddr.446 0
  st var_stk_base.227 0 = copy.2
  ld copy.2 = lhsaddr.446 8
  st var_stk_base.227 8 = copy.2
  .stk arg1.1 8 16
  lea.stk var_stk_base.228:A64 arg1.1 0
  lea.stk lhsaddr.447:A64 = a_val%43 0
  .reg U64 copy.3
  ld copy.3 = lhsaddr.447 0
  st var_stk_base.228 0 = copy.3
  ld copy.3 = lhsaddr.447 8
  st var_stk_base.228 8 = copy.3
  lea.stk lhsaddr.448:A64 = arg0.22 0
  lea.stk lhsaddr.449:A64 = arg1.1 0
  pusharg lhsaddr.449
  pusharg lhsaddr.448
  bsr cmp/eq<ptr<rec<cmp/r64r>>>
  poparg call.222:U8
  mov expr.20 = call.222
  bra end_expr.22
.bbl end_expr.22
  bne expr.20 0 br_join.21
  .stk msg_eval%211 8 16
  lea.stk var_stk_base.229:A64 msg_eval%211 0
  lea.mem lhsaddr.450:A64 = $gen/global_val_30 0
  st var_stk_base.229 0 = lhsaddr.450
  st var_stk_base.229 8 = 8:U64
  lea.stk lhsaddr.451:A64 = msg_eval%211 0
  ld pointer.200:A64 = lhsaddr.451 0
  pusharg 8:U64
  pusharg pointer.200
  pusharg 1:S32
  bsr write
  poparg call.223:S64
  .stk msg_eval%212 8 16
  lea.stk var_stk_base.230:A64 msg_eval%212 0
  lea.mem lhsaddr.452:A64 = $gen/global_val_10 0
  st var_stk_base.230 0 = lhsaddr.452
  st var_stk_base.230 8 = 11:U64
  lea.stk lhsaddr.453:A64 = msg_eval%212 0
  ld pointer.201:A64 = lhsaddr.453 0
  pusharg 11:U64
  pusharg pointer.201
  pusharg 1:S32
  bsr write
  poparg call.224:S64
  .stk msg_eval%213 8 16
  lea.stk var_stk_base.231:A64 msg_eval%213 0
  lea.mem lhsaddr.454:A64 = $gen/global_val_67 0
  st var_stk_base.231 0 = lhsaddr.454
  st var_stk_base.231 8 = 54:U64
  lea.stk lhsaddr.455:A64 = msg_eval%213 0
  ld pointer.202:A64 = lhsaddr.455 0
  pusharg 54:U64
  pusharg pointer.202
  pusharg 1:S32
  bsr write
  poparg call.225:S64
  .stk msg_eval%214 8 16
  lea.stk var_stk_base.232:A64 msg_eval%214 0
  lea.mem lhsaddr.456:A64 = $gen/global_val_12 0
  st var_stk_base.232 0 = lhsaddr.456
  st var_stk_base.232 8 = 2:U64
  lea.stk lhsaddr.457:A64 = msg_eval%214 0
  ld pointer.203:A64 = lhsaddr.457 0
  pusharg 2:U64
  pusharg pointer.203
  pusharg 1:S32
  bsr write
  poparg call.226:S64
  .stk msg_eval%215 8 16
  lea.stk var_stk_base.233:A64 msg_eval%215 0
  lea.mem lhsaddr.458:A64 = $gen/global_val_65 0
  st var_stk_base.233 0 = lhsaddr.458
  st var_stk_base.233 8 = 11:U64
  lea.stk lhsaddr.459:A64 = msg_eval%215 0
  ld pointer.204:A64 = lhsaddr.459 0
  pusharg 11:U64
  pusharg pointer.204
  pusharg 1:S32
  bsr write
  poparg call.227:S64
  .stk msg_eval%216 8 16
  lea.stk var_stk_base.234:A64 msg_eval%216 0
  lea.mem lhsaddr.460:A64 = $gen/global_val_14 0
  st var_stk_base.234 0 = lhsaddr.460
  st var_stk_base.234 8 = 4:U64
  lea.stk lhsaddr.461:A64 = msg_eval%216 0
  ld pointer.205:A64 = lhsaddr.461 0
  pusharg 4:U64
  pusharg pointer.205
  pusharg 1:S32
  bsr write
  poparg call.228:S64
  .stk msg_eval%217 8 16
  lea.stk var_stk_base.235:A64 msg_eval%217 0
  lea.mem lhsaddr.462:A64 = $gen/global_val_65 0
  st var_stk_base.235 0 = lhsaddr.462
  st var_stk_base.235 8 = 11:U64
  lea.stk lhsaddr.463:A64 = msg_eval%217 0
  ld pointer.206:A64 = lhsaddr.463 0
  pusharg 11:U64
  pusharg pointer.206
  pusharg 1:S32
  bsr write
  poparg call.229:S64
  .stk msg_eval%218 8 16
  lea.stk var_stk_base.236:A64 msg_eval%218 0
  lea.mem lhsaddr.464:A64 = $gen/global_val_16 0
  st var_stk_base.236 0 = lhsaddr.464
  st var_stk_base.236 8 = 4:U64
  lea.stk lhsaddr.465:A64 = msg_eval%218 0
  ld pointer.207:A64 = lhsaddr.465 0
  pusharg 4:U64
  pusharg pointer.207
  pusharg 1:S32
  bsr write
  poparg call.230:S64
  .stk msg_eval%219 8 16
  lea.stk var_stk_base.237:A64 msg_eval%219 0
  lea.mem lhsaddr.466:A64 = $gen/global_val_67 0
  st var_stk_base.237 0 = lhsaddr.466
  st var_stk_base.237 8 = 54:U64
  lea.stk lhsaddr.467:A64 = msg_eval%219 0
  ld pointer.208:A64 = lhsaddr.467 0
  pusharg 54:U64
  pusharg pointer.208
  pusharg 1:S32
  bsr write
  poparg call.231:S64
  .stk msg_eval%220 8 16
  lea.stk var_stk_base.238:A64 msg_eval%220 0
  lea.mem lhsaddr.468:A64 = $gen/global_val_17 0
  st var_stk_base.238 0 = lhsaddr.468
  st var_stk_base.238 8 = 1:U64
  lea.stk lhsaddr.469:A64 = msg_eval%220 0
  ld pointer.209:A64 = lhsaddr.469 0
  pusharg 1:U64
  pusharg pointer.209
  pusharg 1:S32
  bsr write
  poparg call.232:S64
  trap
.bbl br_join.21
  ret


.fun parse_real_test/test_hex NORMAL [] = []
.bbl entry
  .reg R64 expr
  .stk arg0 8 16
  lea.stk var_stk_base:A64 arg0 0
  lea.mem lhsaddr:A64 = $gen/global_val_68 0
  st var_stk_base 0 = lhsaddr
  st var_stk_base 8 = 3:U64
  lea.stk lhsaddr.1:A64 = arg0 0
  pusharg lhsaddr.1
  bsr parse_real_test/parse_r64
  poparg call:R64
  mov expr = call
  bra end_expr
.bbl end_expr
  mov a_val%1:R64 = expr
  bitcast bitcast:U64 = a_val%1
  beq 0:U64 bitcast br_join
  .stk msg_eval%1 8 16
  lea.stk var_stk_base.1:A64 msg_eval%1 0
  lea.mem lhsaddr.2:A64 = $gen/global_val_9 0
  st var_stk_base.1 0 = lhsaddr.2
  st var_stk_base.1 8 = 11:U64
  lea.stk lhsaddr.3:A64 = msg_eval%1 0
  ld pointer:A64 = lhsaddr.3 0
  pusharg 11:U64
  pusharg pointer
  pusharg 1:S32
  bsr write
  poparg call.1:S64
  .stk msg_eval%2 8 16
  lea.stk var_stk_base.2:A64 msg_eval%2 0
  lea.mem lhsaddr.4:A64 = $gen/global_val_10 0
  st var_stk_base.2 0 = lhsaddr.4
  st var_stk_base.2 8 = 11:U64
  lea.stk lhsaddr.5:A64 = msg_eval%2 0
  ld pointer.1:A64 = lhsaddr.5 0
  pusharg 11:U64
  pusharg pointer.1
  pusharg 1:S32
  bsr write
  poparg call.2:S64
  .stk msg_eval%3 8 16
  lea.stk var_stk_base.3:A64 msg_eval%3 0
  lea.mem lhsaddr.6:A64 = $gen/global_val_69 0
  st var_stk_base.3 0 = lhsaddr.6
  st var_stk_base.3 8 = 54:U64
  lea.stk lhsaddr.7:A64 = msg_eval%3 0
  ld pointer.2:A64 = lhsaddr.7 0
  pusharg 54:U64
  pusharg pointer.2
  pusharg 1:S32
  bsr write
  poparg call.3:S64
  .stk msg_eval%4 8 16
  lea.stk var_stk_base.4:A64 msg_eval%4 0
  lea.mem lhsaddr.8:A64 = $gen/global_val_12 0
  st var_stk_base.4 0 = lhsaddr.8
  st var_stk_base.4 8 = 2:U64
  lea.stk lhsaddr.9:A64 = msg_eval%4 0
  ld pointer.3:A64 = lhsaddr.9 0
  pusharg 2:U64
  pusharg pointer.3
  pusharg 1:S32
  bsr write
  poparg call.4:S64
  .stk msg_eval%5 8 16
  lea.stk var_stk_base.5:A64 msg_eval%5 0
  lea.mem lhsaddr.10:A64 = $gen/global_val_26 0
  st var_stk_base.5 0 = lhsaddr.10
  st var_stk_base.5 8 = 6:U64
  lea.stk lhsaddr.11:A64 = msg_eval%5 0
  ld pointer.4:A64 = lhsaddr.11 0
  pusharg 6:U64
  pusharg pointer.4
  pusharg 1:S32
  bsr write
  poparg call.5:S64
  .stk msg_eval%6 8 16
  lea.stk var_stk_base.6:A64 msg_eval%6 0
  lea.mem lhsaddr.12:A64 = $gen/global_val_14 0
  st var_stk_base.6 0 = lhsaddr.12
  st var_stk_base.6 8 = 4:U64
  lea.stk lhsaddr.13:A64 = msg_eval%6 0
  ld pointer.5:A64 = lhsaddr.13 0
  pusharg 4:U64
  pusharg pointer.5
  pusharg 1:S32
  bsr write
  poparg call.6:S64
  .stk msg_eval%7 8 16
  lea.stk var_stk_base.7:A64 msg_eval%7 0
  lea.mem lhsaddr.14:A64 = $gen/global_val_15 0
  st var_stk_base.7 0 = lhsaddr.14
  st var_stk_base.7 8 = 8:U64
  lea.stk lhsaddr.15:A64 = msg_eval%7 0
  ld pointer.6:A64 = lhsaddr.15 0
  pusharg 8:U64
  pusharg pointer.6
  pusharg 1:S32
  bsr write
  poparg call.7:S64
  .stk msg_eval%8 8 16
  lea.stk var_stk_base.8:A64 msg_eval%8 0
  lea.mem lhsaddr.16:A64 = $gen/global_val_16 0
  st var_stk_base.8 0 = lhsaddr.16
  st var_stk_base.8 8 = 4:U64
  lea.stk lhsaddr.17:A64 = msg_eval%8 0
  ld pointer.7:A64 = lhsaddr.17 0
  pusharg 4:U64
  pusharg pointer.7
  pusharg 1:S32
  bsr write
  poparg call.8:S64
  .stk msg_eval%9 8 16
  lea.stk var_stk_base.9:A64 msg_eval%9 0
  lea.mem lhsaddr.18:A64 = $gen/global_val_69 0
  st var_stk_base.9 0 = lhsaddr.18
  st var_stk_base.9 8 = 54:U64
  lea.stk lhsaddr.19:A64 = msg_eval%9 0
  ld pointer.8:A64 = lhsaddr.19 0
  pusharg 54:U64
  pusharg pointer.8
  pusharg 1:S32
  bsr write
  poparg call.9:S64
  .stk msg_eval%10 8 16
  lea.stk var_stk_base.10:A64 msg_eval%10 0
  lea.mem lhsaddr.20:A64 = $gen/global_val_17 0
  st var_stk_base.10 0 = lhsaddr.20
  st var_stk_base.10 8 = 1:U64
  lea.stk lhsaddr.21:A64 = msg_eval%10 0
  ld pointer.9:A64 = lhsaddr.21 0
  pusharg 1:U64
  pusharg pointer.9
  pusharg 1:S32
  bsr write
  poparg call.10:S64
  trap
.bbl br_join
  .reg R64 expr.1
  .stk arg0.1 8 16
  lea.stk var_stk_base.11:A64 arg0.1 0
  lea.mem lhsaddr.22:A64 = $gen/global_val_70 0
  st var_stk_base.11 0 = lhsaddr.22
  st var_stk_base.11 8 = 4:U64
  lea.stk lhsaddr.23:A64 = arg0.1 0
  pusharg lhsaddr.23
  bsr parse_real_test/parse_r64
  poparg call.11:R64
  mov expr.1 = call.11
  bra end_expr.1
.bbl end_expr.1
  mov a_val%3:R64 = expr.1
  bitcast bitcast.1:U64 = a_val%3
  beq 0:U64 bitcast.1 br_join.1
  .stk msg_eval%11 8 16
  lea.stk var_stk_base.12:A64 msg_eval%11 0
  lea.mem lhsaddr.24:A64 = $gen/global_val_9 0
  st var_stk_base.12 0 = lhsaddr.24
  st var_stk_base.12 8 = 11:U64
  lea.stk lhsaddr.25:A64 = msg_eval%11 0
  ld pointer.10:A64 = lhsaddr.25 0
  pusharg 11:U64
  pusharg pointer.10
  pusharg 1:S32
  bsr write
  poparg call.12:S64
  .stk msg_eval%12 8 16
  lea.stk var_stk_base.13:A64 msg_eval%12 0
  lea.mem lhsaddr.26:A64 = $gen/global_val_10 0
  st var_stk_base.13 0 = lhsaddr.26
  st var_stk_base.13 8 = 11:U64
  lea.stk lhsaddr.27:A64 = msg_eval%12 0
  ld pointer.11:A64 = lhsaddr.27 0
  pusharg 11:U64
  pusharg pointer.11
  pusharg 1:S32
  bsr write
  poparg call.13:S64
  .stk msg_eval%13 8 16
  lea.stk var_stk_base.14:A64 msg_eval%13 0
  lea.mem lhsaddr.28:A64 = $gen/global_val_71 0
  st var_stk_base.14 0 = lhsaddr.28
  st var_stk_base.14 8 = 54:U64
  lea.stk lhsaddr.29:A64 = msg_eval%13 0
  ld pointer.12:A64 = lhsaddr.29 0
  pusharg 54:U64
  pusharg pointer.12
  pusharg 1:S32
  bsr write
  poparg call.14:S64
  .stk msg_eval%14 8 16
  lea.stk var_stk_base.15:A64 msg_eval%14 0
  lea.mem lhsaddr.30:A64 = $gen/global_val_12 0
  st var_stk_base.15 0 = lhsaddr.30
  st var_stk_base.15 8 = 2:U64
  lea.stk lhsaddr.31:A64 = msg_eval%14 0
  ld pointer.13:A64 = lhsaddr.31 0
  pusharg 2:U64
  pusharg pointer.13
  pusharg 1:S32
  bsr write
  poparg call.15:S64
  .stk msg_eval%15 8 16
  lea.stk var_stk_base.16:A64 msg_eval%15 0
  lea.mem lhsaddr.32:A64 = $gen/global_val_26 0
  st var_stk_base.16 0 = lhsaddr.32
  st var_stk_base.16 8 = 6:U64
  lea.stk lhsaddr.33:A64 = msg_eval%15 0
  ld pointer.14:A64 = lhsaddr.33 0
  pusharg 6:U64
  pusharg pointer.14
  pusharg 1:S32
  bsr write
  poparg call.16:S64
  .stk msg_eval%16 8 16
  lea.stk var_stk_base.17:A64 msg_eval%16 0
  lea.mem lhsaddr.34:A64 = $gen/global_val_14 0
  st var_stk_base.17 0 = lhsaddr.34
  st var_stk_base.17 8 = 4:U64
  lea.stk lhsaddr.35:A64 = msg_eval%16 0
  ld pointer.15:A64 = lhsaddr.35 0
  pusharg 4:U64
  pusharg pointer.15
  pusharg 1:S32
  bsr write
  poparg call.17:S64
  .stk msg_eval%17 8 16
  lea.stk var_stk_base.18:A64 msg_eval%17 0
  lea.mem lhsaddr.36:A64 = $gen/global_val_15 0
  st var_stk_base.18 0 = lhsaddr.36
  st var_stk_base.18 8 = 8:U64
  lea.stk lhsaddr.37:A64 = msg_eval%17 0
  ld pointer.16:A64 = lhsaddr.37 0
  pusharg 8:U64
  pusharg pointer.16
  pusharg 1:S32
  bsr write
  poparg call.18:S64
  .stk msg_eval%18 8 16
  lea.stk var_stk_base.19:A64 msg_eval%18 0
  lea.mem lhsaddr.38:A64 = $gen/global_val_16 0
  st var_stk_base.19 0 = lhsaddr.38
  st var_stk_base.19 8 = 4:U64
  lea.stk lhsaddr.39:A64 = msg_eval%18 0
  ld pointer.17:A64 = lhsaddr.39 0
  pusharg 4:U64
  pusharg pointer.17
  pusharg 1:S32
  bsr write
  poparg call.19:S64
  .stk msg_eval%19 8 16
  lea.stk var_stk_base.20:A64 msg_eval%19 0
  lea.mem lhsaddr.40:A64 = $gen/global_val_71 0
  st var_stk_base.20 0 = lhsaddr.40
  st var_stk_base.20 8 = 54:U64
  lea.stk lhsaddr.41:A64 = msg_eval%19 0
  ld pointer.18:A64 = lhsaddr.41 0
  pusharg 54:U64
  pusharg pointer.18
  pusharg 1:S32
  bsr write
  poparg call.20:S64
  .stk msg_eval%20 8 16
  lea.stk var_stk_base.21:A64 msg_eval%20 0
  lea.mem lhsaddr.42:A64 = $gen/global_val_17 0
  st var_stk_base.21 0 = lhsaddr.42
  st var_stk_base.21 8 = 1:U64
  lea.stk lhsaddr.43:A64 = msg_eval%20 0
  ld pointer.19:A64 = lhsaddr.43 0
  pusharg 1:U64
  pusharg pointer.19
  pusharg 1:S32
  bsr write
  poparg call.21:S64
  trap
.bbl br_join.1
  .reg R64 expr.2
  .stk arg0.2 8 16
  lea.stk var_stk_base.22:A64 arg0.2 0
  lea.mem lhsaddr.44:A64 = $gen/global_val_72 0
  st var_stk_base.22 0 = lhsaddr.44
  st var_stk_base.22 8 = 5:U64
  lea.stk lhsaddr.45:A64 = arg0.2 0
  pusharg lhsaddr.45
  bsr parse_real_test/parse_r64
  poparg call.22:R64
  mov expr.2 = call.22
  bra end_expr.2
.bbl end_expr.2
  mov a_val%5:R64 = expr.2
  bitcast bitcast.2:U64 = a_val%5
  beq 4607182418800017408:U64 bitcast.2 br_join.2
  .stk msg_eval%21 8 16
  lea.stk var_stk_base.23:A64 msg_eval%21 0
  lea.mem lhsaddr.46:A64 = $gen/global_val_9 0
  st var_stk_base.23 0 = lhsaddr.46
  st var_stk_base.23 8 = 11:U64
  lea.stk lhsaddr.47:A64 = msg_eval%21 0
  ld pointer.20:A64 = lhsaddr.47 0
  pusharg 11:U64
  pusharg pointer.20
  pusharg 1:S32
  bsr write
  poparg call.23:S64
  .stk msg_eval%22 8 16
  lea.stk var_stk_base.24:A64 msg_eval%22 0
  lea.mem lhsaddr.48:A64 = $gen/global_val_10 0
  st var_stk_base.24 0 = lhsaddr.48
  st var_stk_base.24 8 = 11:U64
  lea.stk lhsaddr.49:A64 = msg_eval%22 0
  ld pointer.21:A64 = lhsaddr.49 0
  pusharg 11:U64
  pusharg pointer.21
  pusharg 1:S32
  bsr write
  poparg call.24:S64
  .stk msg_eval%23 8 16
  lea.stk var_stk_base.25:A64 msg_eval%23 0
  lea.mem lhsaddr.50:A64 = $gen/global_val_73 0
  st var_stk_base.25 0 = lhsaddr.50
  st var_stk_base.25 8 = 54:U64
  lea.stk lhsaddr.51:A64 = msg_eval%23 0
  ld pointer.22:A64 = lhsaddr.51 0
  pusharg 54:U64
  pusharg pointer.22
  pusharg 1:S32
  bsr write
  poparg call.25:S64
  .stk msg_eval%24 8 16
  lea.stk var_stk_base.26:A64 msg_eval%24 0
  lea.mem lhsaddr.52:A64 = $gen/global_val_12 0
  st var_stk_base.26 0 = lhsaddr.52
  st var_stk_base.26 8 = 2:U64
  lea.stk lhsaddr.53:A64 = msg_eval%24 0
  ld pointer.23:A64 = lhsaddr.53 0
  pusharg 2:U64
  pusharg pointer.23
  pusharg 1:S32
  bsr write
  poparg call.26:S64
  .stk msg_eval%25 8 16
  lea.stk var_stk_base.27:A64 msg_eval%25 0
  lea.mem lhsaddr.54:A64 = $gen/global_val_26 0
  st var_stk_base.27 0 = lhsaddr.54
  st var_stk_base.27 8 = 6:U64
  lea.stk lhsaddr.55:A64 = msg_eval%25 0
  ld pointer.24:A64 = lhsaddr.55 0
  pusharg 6:U64
  pusharg pointer.24
  pusharg 1:S32
  bsr write
  poparg call.27:S64
  .stk msg_eval%26 8 16
  lea.stk var_stk_base.28:A64 msg_eval%26 0
  lea.mem lhsaddr.56:A64 = $gen/global_val_14 0
  st var_stk_base.28 0 = lhsaddr.56
  st var_stk_base.28 8 = 4:U64
  lea.stk lhsaddr.57:A64 = msg_eval%26 0
  ld pointer.25:A64 = lhsaddr.57 0
  pusharg 4:U64
  pusharg pointer.25
  pusharg 1:S32
  bsr write
  poparg call.28:S64
  .stk msg_eval%27 8 16
  lea.stk var_stk_base.29:A64 msg_eval%27 0
  lea.mem lhsaddr.58:A64 = $gen/global_val_15 0
  st var_stk_base.29 0 = lhsaddr.58
  st var_stk_base.29 8 = 8:U64
  lea.stk lhsaddr.59:A64 = msg_eval%27 0
  ld pointer.26:A64 = lhsaddr.59 0
  pusharg 8:U64
  pusharg pointer.26
  pusharg 1:S32
  bsr write
  poparg call.29:S64
  .stk msg_eval%28 8 16
  lea.stk var_stk_base.30:A64 msg_eval%28 0
  lea.mem lhsaddr.60:A64 = $gen/global_val_16 0
  st var_stk_base.30 0 = lhsaddr.60
  st var_stk_base.30 8 = 4:U64
  lea.stk lhsaddr.61:A64 = msg_eval%28 0
  ld pointer.27:A64 = lhsaddr.61 0
  pusharg 4:U64
  pusharg pointer.27
  pusharg 1:S32
  bsr write
  poparg call.30:S64
  .stk msg_eval%29 8 16
  lea.stk var_stk_base.31:A64 msg_eval%29 0
  lea.mem lhsaddr.62:A64 = $gen/global_val_73 0
  st var_stk_base.31 0 = lhsaddr.62
  st var_stk_base.31 8 = 54:U64
  lea.stk lhsaddr.63:A64 = msg_eval%29 0
  ld pointer.28:A64 = lhsaddr.63 0
  pusharg 54:U64
  pusharg pointer.28
  pusharg 1:S32
  bsr write
  poparg call.31:S64
  .stk msg_eval%30 8 16
  lea.stk var_stk_base.32:A64 msg_eval%30 0
  lea.mem lhsaddr.64:A64 = $gen/global_val_17 0
  st var_stk_base.32 0 = lhsaddr.64
  st var_stk_base.32 8 = 1:U64
  lea.stk lhsaddr.65:A64 = msg_eval%30 0
  ld pointer.29:A64 = lhsaddr.65 0
  pusharg 1:U64
  pusharg pointer.29
  pusharg 1:S32
  bsr write
  poparg call.32:S64
  trap
.bbl br_join.2
  .reg R64 expr.3
  .stk arg0.3 8 16
  lea.stk var_stk_base.33:A64 arg0.3 0
  lea.mem lhsaddr.66:A64 = $gen/global_val_74 0
  st var_stk_base.33 0 = lhsaddr.66
  st var_stk_base.33 8 = 6:U64
  lea.stk lhsaddr.67:A64 = arg0.3 0
  pusharg lhsaddr.67
  bsr parse_real_test/parse_r64
  poparg call.33:R64
  mov expr.3 = call.33
  bra end_expr.3
.bbl end_expr.3
  mov a_val%7:R64 = expr.3
  bitcast bitcast.3:U64 = a_val%7
  beq 4602678819172646912:U64 bitcast.3 br_join.3
  .stk msg_eval%31 8 16
  lea.stk var_stk_base.34:A64 msg_eval%31 0
  lea.mem lhsaddr.68:A64 = $gen/global_val_9 0
  st var_stk_base.34 0 = lhsaddr.68
  st var_stk_base.34 8 = 11:U64
  lea.stk lhsaddr.69:A64 = msg_eval%31 0
  ld pointer.30:A64 = lhsaddr.69 0
  pusharg 11:U64
  pusharg pointer.30
  pusharg 1:S32
  bsr write
  poparg call.34:S64
  .stk msg_eval%32 8 16
  lea.stk var_stk_base.35:A64 msg_eval%32 0
  lea.mem lhsaddr.70:A64 = $gen/global_val_10 0
  st var_stk_base.35 0 = lhsaddr.70
  st var_stk_base.35 8 = 11:U64
  lea.stk lhsaddr.71:A64 = msg_eval%32 0
  ld pointer.31:A64 = lhsaddr.71 0
  pusharg 11:U64
  pusharg pointer.31
  pusharg 1:S32
  bsr write
  poparg call.35:S64
  .stk msg_eval%33 8 16
  lea.stk var_stk_base.36:A64 msg_eval%33 0
  lea.mem lhsaddr.72:A64 = $gen/global_val_75 0
  st var_stk_base.36 0 = lhsaddr.72
  st var_stk_base.36 8 = 54:U64
  lea.stk lhsaddr.73:A64 = msg_eval%33 0
  ld pointer.32:A64 = lhsaddr.73 0
  pusharg 54:U64
  pusharg pointer.32
  pusharg 1:S32
  bsr write
  poparg call.36:S64
  .stk msg_eval%34 8 16
  lea.stk var_stk_base.37:A64 msg_eval%34 0
  lea.mem lhsaddr.74:A64 = $gen/global_val_12 0
  st var_stk_base.37 0 = lhsaddr.74
  st var_stk_base.37 8 = 2:U64
  lea.stk lhsaddr.75:A64 = msg_eval%34 0
  ld pointer.33:A64 = lhsaddr.75 0
  pusharg 2:U64
  pusharg pointer.33
  pusharg 1:S32
  bsr write
  poparg call.37:S64
  .stk msg_eval%35 8 16
  lea.stk var_stk_base.38:A64 msg_eval%35 0
  lea.mem lhsaddr.76:A64 = $gen/global_val_26 0
  st var_stk_base.38 0 = lhsaddr.76
  st var_stk_base.38 8 = 6:U64
  lea.stk lhsaddr.77:A64 = msg_eval%35 0
  ld pointer.34:A64 = lhsaddr.77 0
  pusharg 6:U64
  pusharg pointer.34
  pusharg 1:S32
  bsr write
  poparg call.38:S64
  .stk msg_eval%36 8 16
  lea.stk var_stk_base.39:A64 msg_eval%36 0
  lea.mem lhsaddr.78:A64 = $gen/global_val_14 0
  st var_stk_base.39 0 = lhsaddr.78
  st var_stk_base.39 8 = 4:U64
  lea.stk lhsaddr.79:A64 = msg_eval%36 0
  ld pointer.35:A64 = lhsaddr.79 0
  pusharg 4:U64
  pusharg pointer.35
  pusharg 1:S32
  bsr write
  poparg call.39:S64
  .stk msg_eval%37 8 16
  lea.stk var_stk_base.40:A64 msg_eval%37 0
  lea.mem lhsaddr.80:A64 = $gen/global_val_15 0
  st var_stk_base.40 0 = lhsaddr.80
  st var_stk_base.40 8 = 8:U64
  lea.stk lhsaddr.81:A64 = msg_eval%37 0
  ld pointer.36:A64 = lhsaddr.81 0
  pusharg 8:U64
  pusharg pointer.36
  pusharg 1:S32
  bsr write
  poparg call.40:S64
  .stk msg_eval%38 8 16
  lea.stk var_stk_base.41:A64 msg_eval%38 0
  lea.mem lhsaddr.82:A64 = $gen/global_val_16 0
  st var_stk_base.41 0 = lhsaddr.82
  st var_stk_base.41 8 = 4:U64
  lea.stk lhsaddr.83:A64 = msg_eval%38 0
  ld pointer.37:A64 = lhsaddr.83 0
  pusharg 4:U64
  pusharg pointer.37
  pusharg 1:S32
  bsr write
  poparg call.41:S64
  .stk msg_eval%39 8 16
  lea.stk var_stk_base.42:A64 msg_eval%39 0
  lea.mem lhsaddr.84:A64 = $gen/global_val_75 0
  st var_stk_base.42 0 = lhsaddr.84
  st var_stk_base.42 8 = 54:U64
  lea.stk lhsaddr.85:A64 = msg_eval%39 0
  ld pointer.38:A64 = lhsaddr.85 0
  pusharg 54:U64
  pusharg pointer.38
  pusharg 1:S32
  bsr write
  poparg call.42:S64
  .stk msg_eval%40 8 16
  lea.stk var_stk_base.43:A64 msg_eval%40 0
  lea.mem lhsaddr.86:A64 = $gen/global_val_17 0
  st var_stk_base.43 0 = lhsaddr.86
  st var_stk_base.43 8 = 1:U64
  lea.stk lhsaddr.87:A64 = msg_eval%40 0
  ld pointer.39:A64 = lhsaddr.87 0
  pusharg 1:U64
  pusharg pointer.39
  pusharg 1:S32
  bsr write
  poparg call.43:S64
  trap
.bbl br_join.3
  .reg R64 expr.4
  .stk arg0.4 8 16
  lea.stk var_stk_base.44:A64 arg0.4 0
  lea.mem lhsaddr.88:A64 = $gen/global_val_76 0
  st var_stk_base.44 0 = lhsaddr.88
  st var_stk_base.44 8 = 6:U64
  lea.stk lhsaddr.89:A64 = arg0.4 0
  pusharg lhsaddr.89
  bsr parse_real_test/parse_r64
  poparg call.44:R64
  mov expr.4 = call.44
  bra end_expr.4
.bbl end_expr.4
  mov a_val%9:R64 = expr.4
  bitcast bitcast.4:U64 = a_val%9
  beq 4598175219545276416:U64 bitcast.4 br_join.4
  .stk msg_eval%41 8 16
  lea.stk var_stk_base.45:A64 msg_eval%41 0
  lea.mem lhsaddr.90:A64 = $gen/global_val_9 0
  st var_stk_base.45 0 = lhsaddr.90
  st var_stk_base.45 8 = 11:U64
  lea.stk lhsaddr.91:A64 = msg_eval%41 0
  ld pointer.40:A64 = lhsaddr.91 0
  pusharg 11:U64
  pusharg pointer.40
  pusharg 1:S32
  bsr write
  poparg call.45:S64
  .stk msg_eval%42 8 16
  lea.stk var_stk_base.46:A64 msg_eval%42 0
  lea.mem lhsaddr.92:A64 = $gen/global_val_10 0
  st var_stk_base.46 0 = lhsaddr.92
  st var_stk_base.46 8 = 11:U64
  lea.stk lhsaddr.93:A64 = msg_eval%42 0
  ld pointer.41:A64 = lhsaddr.93 0
  pusharg 11:U64
  pusharg pointer.41
  pusharg 1:S32
  bsr write
  poparg call.46:S64
  .stk msg_eval%43 8 16
  lea.stk var_stk_base.47:A64 msg_eval%43 0
  lea.mem lhsaddr.94:A64 = $gen/global_val_77 0
  st var_stk_base.47 0 = lhsaddr.94
  st var_stk_base.47 8 = 54:U64
  lea.stk lhsaddr.95:A64 = msg_eval%43 0
  ld pointer.42:A64 = lhsaddr.95 0
  pusharg 54:U64
  pusharg pointer.42
  pusharg 1:S32
  bsr write
  poparg call.47:S64
  .stk msg_eval%44 8 16
  lea.stk var_stk_base.48:A64 msg_eval%44 0
  lea.mem lhsaddr.96:A64 = $gen/global_val_12 0
  st var_stk_base.48 0 = lhsaddr.96
  st var_stk_base.48 8 = 2:U64
  lea.stk lhsaddr.97:A64 = msg_eval%44 0
  ld pointer.43:A64 = lhsaddr.97 0
  pusharg 2:U64
  pusharg pointer.43
  pusharg 1:S32
  bsr write
  poparg call.48:S64
  .stk msg_eval%45 8 16
  lea.stk var_stk_base.49:A64 msg_eval%45 0
  lea.mem lhsaddr.98:A64 = $gen/global_val_26 0
  st var_stk_base.49 0 = lhsaddr.98
  st var_stk_base.49 8 = 6:U64
  lea.stk lhsaddr.99:A64 = msg_eval%45 0
  ld pointer.44:A64 = lhsaddr.99 0
  pusharg 6:U64
  pusharg pointer.44
  pusharg 1:S32
  bsr write
  poparg call.49:S64
  .stk msg_eval%46 8 16
  lea.stk var_stk_base.50:A64 msg_eval%46 0
  lea.mem lhsaddr.100:A64 = $gen/global_val_14 0
  st var_stk_base.50 0 = lhsaddr.100
  st var_stk_base.50 8 = 4:U64
  lea.stk lhsaddr.101:A64 = msg_eval%46 0
  ld pointer.45:A64 = lhsaddr.101 0
  pusharg 4:U64
  pusharg pointer.45
  pusharg 1:S32
  bsr write
  poparg call.50:S64
  .stk msg_eval%47 8 16
  lea.stk var_stk_base.51:A64 msg_eval%47 0
  lea.mem lhsaddr.102:A64 = $gen/global_val_15 0
  st var_stk_base.51 0 = lhsaddr.102
  st var_stk_base.51 8 = 8:U64
  lea.stk lhsaddr.103:A64 = msg_eval%47 0
  ld pointer.46:A64 = lhsaddr.103 0
  pusharg 8:U64
  pusharg pointer.46
  pusharg 1:S32
  bsr write
  poparg call.51:S64
  .stk msg_eval%48 8 16
  lea.stk var_stk_base.52:A64 msg_eval%48 0
  lea.mem lhsaddr.104:A64 = $gen/global_val_16 0
  st var_stk_base.52 0 = lhsaddr.104
  st var_stk_base.52 8 = 4:U64
  lea.stk lhsaddr.105:A64 = msg_eval%48 0
  ld pointer.47:A64 = lhsaddr.105 0
  pusharg 4:U64
  pusharg pointer.47
  pusharg 1:S32
  bsr write
  poparg call.52:S64
  .stk msg_eval%49 8 16
  lea.stk var_stk_base.53:A64 msg_eval%49 0
  lea.mem lhsaddr.106:A64 = $gen/global_val_77 0
  st var_stk_base.53 0 = lhsaddr.106
  st var_stk_base.53 8 = 54:U64
  lea.stk lhsaddr.107:A64 = msg_eval%49 0
  ld pointer.48:A64 = lhsaddr.107 0
  pusharg 54:U64
  pusharg pointer.48
  pusharg 1:S32
  bsr write
  poparg call.53:S64
  .stk msg_eval%50 8 16
  lea.stk var_stk_base.54:A64 msg_eval%50 0
  lea.mem lhsaddr.108:A64 = $gen/global_val_17 0
  st var_stk_base.54 0 = lhsaddr.108
  st var_stk_base.54 8 = 1:U64
  lea.stk lhsaddr.109:A64 = msg_eval%50 0
  ld pointer.49:A64 = lhsaddr.109 0
  pusharg 1:U64
  pusharg pointer.49
  pusharg 1:S32
  bsr write
  poparg call.54:S64
  trap
.bbl br_join.4
  .reg R64 expr.5
  .stk arg0.5 8 16
  lea.stk var_stk_base.55:A64 arg0.5 0
  lea.mem lhsaddr.110:A64 = $gen/global_val_78 0
  st var_stk_base.55 0 = lhsaddr.110
  st var_stk_base.55 8 = 6:U64
  lea.stk lhsaddr.111:A64 = arg0.5 0
  pusharg lhsaddr.111
  bsr parse_real_test/parse_r64
  poparg call.55:R64
  mov expr.5 = call.55
  bra end_expr.5
.bbl end_expr.5
  mov a_val%11:R64 = expr.5
  bitcast bitcast.5:U64 = a_val%11
  beq 4593671619917905920:U64 bitcast.5 br_join.5
  .stk msg_eval%51 8 16
  lea.stk var_stk_base.56:A64 msg_eval%51 0
  lea.mem lhsaddr.112:A64 = $gen/global_val_9 0
  st var_stk_base.56 0 = lhsaddr.112
  st var_stk_base.56 8 = 11:U64
  lea.stk lhsaddr.113:A64 = msg_eval%51 0
  ld pointer.50:A64 = lhsaddr.113 0
  pusharg 11:U64
  pusharg pointer.50
  pusharg 1:S32
  bsr write
  poparg call.56:S64
  .stk msg_eval%52 8 16
  lea.stk var_stk_base.57:A64 msg_eval%52 0
  lea.mem lhsaddr.114:A64 = $gen/global_val_10 0
  st var_stk_base.57 0 = lhsaddr.114
  st var_stk_base.57 8 = 11:U64
  lea.stk lhsaddr.115:A64 = msg_eval%52 0
  ld pointer.51:A64 = lhsaddr.115 0
  pusharg 11:U64
  pusharg pointer.51
  pusharg 1:S32
  bsr write
  poparg call.57:S64
  .stk msg_eval%53 8 16
  lea.stk var_stk_base.58:A64 msg_eval%53 0
  lea.mem lhsaddr.116:A64 = $gen/global_val_79 0
  st var_stk_base.58 0 = lhsaddr.116
  st var_stk_base.58 8 = 54:U64
  lea.stk lhsaddr.117:A64 = msg_eval%53 0
  ld pointer.52:A64 = lhsaddr.117 0
  pusharg 54:U64
  pusharg pointer.52
  pusharg 1:S32
  bsr write
  poparg call.58:S64
  .stk msg_eval%54 8 16
  lea.stk var_stk_base.59:A64 msg_eval%54 0
  lea.mem lhsaddr.118:A64 = $gen/global_val_12 0
  st var_stk_base.59 0 = lhsaddr.118
  st var_stk_base.59 8 = 2:U64
  lea.stk lhsaddr.119:A64 = msg_eval%54 0
  ld pointer.53:A64 = lhsaddr.119 0
  pusharg 2:U64
  pusharg pointer.53
  pusharg 1:S32
  bsr write
  poparg call.59:S64
  .stk msg_eval%55 8 16
  lea.stk var_stk_base.60:A64 msg_eval%55 0
  lea.mem lhsaddr.120:A64 = $gen/global_val_26 0
  st var_stk_base.60 0 = lhsaddr.120
  st var_stk_base.60 8 = 6:U64
  lea.stk lhsaddr.121:A64 = msg_eval%55 0
  ld pointer.54:A64 = lhsaddr.121 0
  pusharg 6:U64
  pusharg pointer.54
  pusharg 1:S32
  bsr write
  poparg call.60:S64
  .stk msg_eval%56 8 16
  lea.stk var_stk_base.61:A64 msg_eval%56 0
  lea.mem lhsaddr.122:A64 = $gen/global_val_14 0
  st var_stk_base.61 0 = lhsaddr.122
  st var_stk_base.61 8 = 4:U64
  lea.stk lhsaddr.123:A64 = msg_eval%56 0
  ld pointer.55:A64 = lhsaddr.123 0
  pusharg 4:U64
  pusharg pointer.55
  pusharg 1:S32
  bsr write
  poparg call.61:S64
  .stk msg_eval%57 8 16
  lea.stk var_stk_base.62:A64 msg_eval%57 0
  lea.mem lhsaddr.124:A64 = $gen/global_val_15 0
  st var_stk_base.62 0 = lhsaddr.124
  st var_stk_base.62 8 = 8:U64
  lea.stk lhsaddr.125:A64 = msg_eval%57 0
  ld pointer.56:A64 = lhsaddr.125 0
  pusharg 8:U64
  pusharg pointer.56
  pusharg 1:S32
  bsr write
  poparg call.62:S64
  .stk msg_eval%58 8 16
  lea.stk var_stk_base.63:A64 msg_eval%58 0
  lea.mem lhsaddr.126:A64 = $gen/global_val_16 0
  st var_stk_base.63 0 = lhsaddr.126
  st var_stk_base.63 8 = 4:U64
  lea.stk lhsaddr.127:A64 = msg_eval%58 0
  ld pointer.57:A64 = lhsaddr.127 0
  pusharg 4:U64
  pusharg pointer.57
  pusharg 1:S32
  bsr write
  poparg call.63:S64
  .stk msg_eval%59 8 16
  lea.stk var_stk_base.64:A64 msg_eval%59 0
  lea.mem lhsaddr.128:A64 = $gen/global_val_79 0
  st var_stk_base.64 0 = lhsaddr.128
  st var_stk_base.64 8 = 54:U64
  lea.stk lhsaddr.129:A64 = msg_eval%59 0
  ld pointer.58:A64 = lhsaddr.129 0
  pusharg 54:U64
  pusharg pointer.58
  pusharg 1:S32
  bsr write
  poparg call.64:S64
  .stk msg_eval%60 8 16
  lea.stk var_stk_base.65:A64 msg_eval%60 0
  lea.mem lhsaddr.130:A64 = $gen/global_val_17 0
  st var_stk_base.65 0 = lhsaddr.130
  st var_stk_base.65 8 = 1:U64
  lea.stk lhsaddr.131:A64 = msg_eval%60 0
  ld pointer.59:A64 = lhsaddr.131 0
  pusharg 1:U64
  pusharg pointer.59
  pusharg 1:S32
  bsr write
  poparg call.65:S64
  trap
.bbl br_join.5
  .reg R64 expr.6
  .stk arg0.6 8 16
  lea.stk var_stk_base.66:A64 arg0.6 0
  lea.mem lhsaddr.132:A64 = $gen/global_val_80 0
  st var_stk_base.66 0 = lhsaddr.132
  st var_stk_base.66 8 = 6:U64
  lea.stk lhsaddr.133:A64 = arg0.6 0
  pusharg lhsaddr.133
  bsr parse_real_test/parse_r64
  poparg call.66:R64
  mov expr.6 = call.66
  bra end_expr.6
.bbl end_expr.6
  mov a_val%13:R64 = expr.6
  bitcast bitcast.6:U64 = a_val%13
  beq 4670232813583204352:U64 bitcast.6 br_join.6
  .stk msg_eval%61 8 16
  lea.stk var_stk_base.67:A64 msg_eval%61 0
  lea.mem lhsaddr.134:A64 = $gen/global_val_9 0
  st var_stk_base.67 0 = lhsaddr.134
  st var_stk_base.67 8 = 11:U64
  lea.stk lhsaddr.135:A64 = msg_eval%61 0
  ld pointer.60:A64 = lhsaddr.135 0
  pusharg 11:U64
  pusharg pointer.60
  pusharg 1:S32
  bsr write
  poparg call.67:S64
  .stk msg_eval%62 8 16
  lea.stk var_stk_base.68:A64 msg_eval%62 0
  lea.mem lhsaddr.136:A64 = $gen/global_val_10 0
  st var_stk_base.68 0 = lhsaddr.136
  st var_stk_base.68 8 = 11:U64
  lea.stk lhsaddr.137:A64 = msg_eval%62 0
  ld pointer.61:A64 = lhsaddr.137 0
  pusharg 11:U64
  pusharg pointer.61
  pusharg 1:S32
  bsr write
  poparg call.68:S64
  .stk msg_eval%63 8 16
  lea.stk var_stk_base.69:A64 msg_eval%63 0
  lea.mem lhsaddr.138:A64 = $gen/global_val_81 0
  st var_stk_base.69 0 = lhsaddr.138
  st var_stk_base.69 8 = 54:U64
  lea.stk lhsaddr.139:A64 = msg_eval%63 0
  ld pointer.62:A64 = lhsaddr.139 0
  pusharg 54:U64
  pusharg pointer.62
  pusharg 1:S32
  bsr write
  poparg call.69:S64
  .stk msg_eval%64 8 16
  lea.stk var_stk_base.70:A64 msg_eval%64 0
  lea.mem lhsaddr.140:A64 = $gen/global_val_12 0
  st var_stk_base.70 0 = lhsaddr.140
  st var_stk_base.70 8 = 2:U64
  lea.stk lhsaddr.141:A64 = msg_eval%64 0
  ld pointer.63:A64 = lhsaddr.141 0
  pusharg 2:U64
  pusharg pointer.63
  pusharg 1:S32
  bsr write
  poparg call.70:S64
  .stk msg_eval%65 8 16
  lea.stk var_stk_base.71:A64 msg_eval%65 0
  lea.mem lhsaddr.142:A64 = $gen/global_val_26 0
  st var_stk_base.71 0 = lhsaddr.142
  st var_stk_base.71 8 = 6:U64
  lea.stk lhsaddr.143:A64 = msg_eval%65 0
  ld pointer.64:A64 = lhsaddr.143 0
  pusharg 6:U64
  pusharg pointer.64
  pusharg 1:S32
  bsr write
  poparg call.71:S64
  .stk msg_eval%66 8 16
  lea.stk var_stk_base.72:A64 msg_eval%66 0
  lea.mem lhsaddr.144:A64 = $gen/global_val_14 0
  st var_stk_base.72 0 = lhsaddr.144
  st var_stk_base.72 8 = 4:U64
  lea.stk lhsaddr.145:A64 = msg_eval%66 0
  ld pointer.65:A64 = lhsaddr.145 0
  pusharg 4:U64
  pusharg pointer.65
  pusharg 1:S32
  bsr write
  poparg call.72:S64
  .stk msg_eval%67 8 16
  lea.stk var_stk_base.73:A64 msg_eval%67 0
  lea.mem lhsaddr.146:A64 = $gen/global_val_15 0
  st var_stk_base.73 0 = lhsaddr.146
  st var_stk_base.73 8 = 8:U64
  lea.stk lhsaddr.147:A64 = msg_eval%67 0
  ld pointer.66:A64 = lhsaddr.147 0
  pusharg 8:U64
  pusharg pointer.66
  pusharg 1:S32
  bsr write
  poparg call.73:S64
  .stk msg_eval%68 8 16
  lea.stk var_stk_base.74:A64 msg_eval%68 0
  lea.mem lhsaddr.148:A64 = $gen/global_val_16 0
  st var_stk_base.74 0 = lhsaddr.148
  st var_stk_base.74 8 = 4:U64
  lea.stk lhsaddr.149:A64 = msg_eval%68 0
  ld pointer.67:A64 = lhsaddr.149 0
  pusharg 4:U64
  pusharg pointer.67
  pusharg 1:S32
  bsr write
  poparg call.74:S64
  .stk msg_eval%69 8 16
  lea.stk var_stk_base.75:A64 msg_eval%69 0
  lea.mem lhsaddr.150:A64 = $gen/global_val_81 0
  st var_stk_base.75 0 = lhsaddr.150
  st var_stk_base.75 8 = 54:U64
  lea.stk lhsaddr.151:A64 = msg_eval%69 0
  ld pointer.68:A64 = lhsaddr.151 0
  pusharg 54:U64
  pusharg pointer.68
  pusharg 1:S32
  bsr write
  poparg call.75:S64
  .stk msg_eval%70 8 16
  lea.stk var_stk_base.76:A64 msg_eval%70 0
  lea.mem lhsaddr.152:A64 = $gen/global_val_17 0
  st var_stk_base.76 0 = lhsaddr.152
  st var_stk_base.76 8 = 1:U64
  lea.stk lhsaddr.153:A64 = msg_eval%70 0
  ld pointer.69:A64 = lhsaddr.153 0
  pusharg 1:U64
  pusharg pointer.69
  pusharg 1:S32
  bsr write
  poparg call.76:S64
  trap
.bbl br_join.6
  .reg R64 expr.7
  .stk arg0.7 8 16
  lea.stk var_stk_base.77:A64 arg0.7 0
  lea.mem lhsaddr.154:A64 = $gen/global_val_82 0
  st var_stk_base.77 0 = lhsaddr.154
  st var_stk_base.77 8 = 8:U64
  lea.stk lhsaddr.155:A64 = arg0.7 0
  pusharg lhsaddr.155
  bsr parse_real_test/parse_r64
  poparg call.77:R64
  mov expr.7 = call.77
  bra end_expr.7
.bbl end_expr.7
  mov a_val%15:R64 = expr.7
  bitcast bitcast.7:U64 = a_val%15
  beq 4670232813583204352:U64 bitcast.7 br_join.7
  .stk msg_eval%71 8 16
  lea.stk var_stk_base.78:A64 msg_eval%71 0
  lea.mem lhsaddr.156:A64 = $gen/global_val_9 0
  st var_stk_base.78 0 = lhsaddr.156
  st var_stk_base.78 8 = 11:U64
  lea.stk lhsaddr.157:A64 = msg_eval%71 0
  ld pointer.70:A64 = lhsaddr.157 0
  pusharg 11:U64
  pusharg pointer.70
  pusharg 1:S32
  bsr write
  poparg call.78:S64
  .stk msg_eval%72 8 16
  lea.stk var_stk_base.79:A64 msg_eval%72 0
  lea.mem lhsaddr.158:A64 = $gen/global_val_10 0
  st var_stk_base.79 0 = lhsaddr.158
  st var_stk_base.79 8 = 11:U64
  lea.stk lhsaddr.159:A64 = msg_eval%72 0
  ld pointer.71:A64 = lhsaddr.159 0
  pusharg 11:U64
  pusharg pointer.71
  pusharg 1:S32
  bsr write
  poparg call.79:S64
  .stk msg_eval%73 8 16
  lea.stk var_stk_base.80:A64 msg_eval%73 0
  lea.mem lhsaddr.160:A64 = $gen/global_val_83 0
  st var_stk_base.80 0 = lhsaddr.160
  st var_stk_base.80 8 = 54:U64
  lea.stk lhsaddr.161:A64 = msg_eval%73 0
  ld pointer.72:A64 = lhsaddr.161 0
  pusharg 54:U64
  pusharg pointer.72
  pusharg 1:S32
  bsr write
  poparg call.80:S64
  .stk msg_eval%74 8 16
  lea.stk var_stk_base.81:A64 msg_eval%74 0
  lea.mem lhsaddr.162:A64 = $gen/global_val_12 0
  st var_stk_base.81 0 = lhsaddr.162
  st var_stk_base.81 8 = 2:U64
  lea.stk lhsaddr.163:A64 = msg_eval%74 0
  ld pointer.73:A64 = lhsaddr.163 0
  pusharg 2:U64
  pusharg pointer.73
  pusharg 1:S32
  bsr write
  poparg call.81:S64
  .stk msg_eval%75 8 16
  lea.stk var_stk_base.82:A64 msg_eval%75 0
  lea.mem lhsaddr.164:A64 = $gen/global_val_26 0
  st var_stk_base.82 0 = lhsaddr.164
  st var_stk_base.82 8 = 6:U64
  lea.stk lhsaddr.165:A64 = msg_eval%75 0
  ld pointer.74:A64 = lhsaddr.165 0
  pusharg 6:U64
  pusharg pointer.74
  pusharg 1:S32
  bsr write
  poparg call.82:S64
  .stk msg_eval%76 8 16
  lea.stk var_stk_base.83:A64 msg_eval%76 0
  lea.mem lhsaddr.166:A64 = $gen/global_val_14 0
  st var_stk_base.83 0 = lhsaddr.166
  st var_stk_base.83 8 = 4:U64
  lea.stk lhsaddr.167:A64 = msg_eval%76 0
  ld pointer.75:A64 = lhsaddr.167 0
  pusharg 4:U64
  pusharg pointer.75
  pusharg 1:S32
  bsr write
  poparg call.83:S64
  .stk msg_eval%77 8 16
  lea.stk var_stk_base.84:A64 msg_eval%77 0
  lea.mem lhsaddr.168:A64 = $gen/global_val_15 0
  st var_stk_base.84 0 = lhsaddr.168
  st var_stk_base.84 8 = 8:U64
  lea.stk lhsaddr.169:A64 = msg_eval%77 0
  ld pointer.76:A64 = lhsaddr.169 0
  pusharg 8:U64
  pusharg pointer.76
  pusharg 1:S32
  bsr write
  poparg call.84:S64
  .stk msg_eval%78 8 16
  lea.stk var_stk_base.85:A64 msg_eval%78 0
  lea.mem lhsaddr.170:A64 = $gen/global_val_16 0
  st var_stk_base.85 0 = lhsaddr.170
  st var_stk_base.85 8 = 4:U64
  lea.stk lhsaddr.171:A64 = msg_eval%78 0
  ld pointer.77:A64 = lhsaddr.171 0
  pusharg 4:U64
  pusharg pointer.77
  pusharg 1:S32
  bsr write
  poparg call.85:S64
  .stk msg_eval%79 8 16
  lea.stk var_stk_base.86:A64 msg_eval%79 0
  lea.mem lhsaddr.172:A64 = $gen/global_val_83 0
  st var_stk_base.86 0 = lhsaddr.172
  st var_stk_base.86 8 = 54:U64
  lea.stk lhsaddr.173:A64 = msg_eval%79 0
  ld pointer.78:A64 = lhsaddr.173 0
  pusharg 54:U64
  pusharg pointer.78
  pusharg 1:S32
  bsr write
  poparg call.86:S64
  .stk msg_eval%80 8 16
  lea.stk var_stk_base.87:A64 msg_eval%80 0
  lea.mem lhsaddr.174:A64 = $gen/global_val_17 0
  st var_stk_base.87 0 = lhsaddr.174
  st var_stk_base.87 8 = 1:U64
  lea.stk lhsaddr.175:A64 = msg_eval%80 0
  ld pointer.79:A64 = lhsaddr.175 0
  pusharg 1:U64
  pusharg pointer.79
  pusharg 1:S32
  bsr write
  poparg call.87:S64
  trap
.bbl br_join.7
  .reg R64 expr.8
  .stk arg0.8 8 16
  lea.stk var_stk_base.88:A64 arg0.8 0
  lea.mem lhsaddr.176:A64 = $gen/global_val_84 0
  st var_stk_base.88 0 = lhsaddr.176
  st var_stk_base.88 8 = 9:U64
  lea.stk lhsaddr.177:A64 = arg0.8 0
  pusharg lhsaddr.177
  bsr parse_real_test/parse_r64
  poparg call.88:R64
  mov expr.8 = call.88
  bra end_expr.8
.bbl end_expr.8
  mov a_val%17:R64 = expr.8
  bitcast bitcast.8:U64 = a_val%17
  beq 4503599627370496:U64 bitcast.8 br_join.8
  .stk msg_eval%81 8 16
  lea.stk var_stk_base.89:A64 msg_eval%81 0
  lea.mem lhsaddr.178:A64 = $gen/global_val_9 0
  st var_stk_base.89 0 = lhsaddr.178
  st var_stk_base.89 8 = 11:U64
  lea.stk lhsaddr.179:A64 = msg_eval%81 0
  ld pointer.80:A64 = lhsaddr.179 0
  pusharg 11:U64
  pusharg pointer.80
  pusharg 1:S32
  bsr write
  poparg call.89:S64
  .stk msg_eval%82 8 16
  lea.stk var_stk_base.90:A64 msg_eval%82 0
  lea.mem lhsaddr.180:A64 = $gen/global_val_10 0
  st var_stk_base.90 0 = lhsaddr.180
  st var_stk_base.90 8 = 11:U64
  lea.stk lhsaddr.181:A64 = msg_eval%82 0
  ld pointer.81:A64 = lhsaddr.181 0
  pusharg 11:U64
  pusharg pointer.81
  pusharg 1:S32
  bsr write
  poparg call.90:S64
  .stk msg_eval%83 8 16
  lea.stk var_stk_base.91:A64 msg_eval%83 0
  lea.mem lhsaddr.182:A64 = $gen/global_val_85 0
  st var_stk_base.91 0 = lhsaddr.182
  st var_stk_base.91 8 = 54:U64
  lea.stk lhsaddr.183:A64 = msg_eval%83 0
  ld pointer.82:A64 = lhsaddr.183 0
  pusharg 54:U64
  pusharg pointer.82
  pusharg 1:S32
  bsr write
  poparg call.91:S64
  .stk msg_eval%84 8 16
  lea.stk var_stk_base.92:A64 msg_eval%84 0
  lea.mem lhsaddr.184:A64 = $gen/global_val_12 0
  st var_stk_base.92 0 = lhsaddr.184
  st var_stk_base.92 8 = 2:U64
  lea.stk lhsaddr.185:A64 = msg_eval%84 0
  ld pointer.83:A64 = lhsaddr.185 0
  pusharg 2:U64
  pusharg pointer.83
  pusharg 1:S32
  bsr write
  poparg call.92:S64
  .stk msg_eval%85 8 16
  lea.stk var_stk_base.93:A64 msg_eval%85 0
  lea.mem lhsaddr.186:A64 = $gen/global_val_86 0
  st var_stk_base.93 0 = lhsaddr.186
  st var_stk_base.93 8 = 5:U64
  lea.stk lhsaddr.187:A64 = msg_eval%85 0
  ld pointer.84:A64 = lhsaddr.187 0
  pusharg 5:U64
  pusharg pointer.84
  pusharg 1:S32
  bsr write
  poparg call.93:S64
  .stk msg_eval%86 8 16
  lea.stk var_stk_base.94:A64 msg_eval%86 0
  lea.mem lhsaddr.188:A64 = $gen/global_val_14 0
  st var_stk_base.94 0 = lhsaddr.188
  st var_stk_base.94 8 = 4:U64
  lea.stk lhsaddr.189:A64 = msg_eval%86 0
  ld pointer.85:A64 = lhsaddr.189 0
  pusharg 4:U64
  pusharg pointer.85
  pusharg 1:S32
  bsr write
  poparg call.94:S64
  .stk msg_eval%87 8 16
  lea.stk var_stk_base.95:A64 msg_eval%87 0
  lea.mem lhsaddr.190:A64 = $gen/global_val_15 0
  st var_stk_base.95 0 = lhsaddr.190
  st var_stk_base.95 8 = 8:U64
  lea.stk lhsaddr.191:A64 = msg_eval%87 0
  ld pointer.86:A64 = lhsaddr.191 0
  pusharg 8:U64
  pusharg pointer.86
  pusharg 1:S32
  bsr write
  poparg call.95:S64
  .stk msg_eval%88 8 16
  lea.stk var_stk_base.96:A64 msg_eval%88 0
  lea.mem lhsaddr.192:A64 = $gen/global_val_16 0
  st var_stk_base.96 0 = lhsaddr.192
  st var_stk_base.96 8 = 4:U64
  lea.stk lhsaddr.193:A64 = msg_eval%88 0
  ld pointer.87:A64 = lhsaddr.193 0
  pusharg 4:U64
  pusharg pointer.87
  pusharg 1:S32
  bsr write
  poparg call.96:S64
  .stk msg_eval%89 8 16
  lea.stk var_stk_base.97:A64 msg_eval%89 0
  lea.mem lhsaddr.194:A64 = $gen/global_val_85 0
  st var_stk_base.97 0 = lhsaddr.194
  st var_stk_base.97 8 = 54:U64
  lea.stk lhsaddr.195:A64 = msg_eval%89 0
  ld pointer.88:A64 = lhsaddr.195 0
  pusharg 54:U64
  pusharg pointer.88
  pusharg 1:S32
  bsr write
  poparg call.97:S64
  .stk msg_eval%90 8 16
  lea.stk var_stk_base.98:A64 msg_eval%90 0
  lea.mem lhsaddr.196:A64 = $gen/global_val_17 0
  st var_stk_base.98 0 = lhsaddr.196
  st var_stk_base.98 8 = 1:U64
  lea.stk lhsaddr.197:A64 = msg_eval%90 0
  ld pointer.89:A64 = lhsaddr.197 0
  pusharg 1:U64
  pusharg pointer.89
  pusharg 1:S32
  bsr write
  poparg call.98:S64
  trap
.bbl br_join.8
  .reg R64 expr.9
  .stk arg0.9 8 16
  lea.stk var_stk_base.99:A64 arg0.9 0
  lea.mem lhsaddr.198:A64 = $gen/global_val_87 0
  st var_stk_base.99 0 = lhsaddr.198
  st var_stk_base.99 8 = 8:U64
  lea.stk lhsaddr.199:A64 = arg0.9 0
  pusharg lhsaddr.199
  bsr parse_real_test/parse_r64
  poparg call.99:R64
  mov expr.9 = call.99
  bra end_expr.9
.bbl end_expr.9
  mov a_val%19:R64 = expr.9
  bitcast bitcast.9:U64 = a_val%19
  beq 4580160821035794432:U64 bitcast.9 br_join.9
  .stk msg_eval%91 8 16
  lea.stk var_stk_base.100:A64 msg_eval%91 0
  lea.mem lhsaddr.200:A64 = $gen/global_val_9 0
  st var_stk_base.100 0 = lhsaddr.200
  st var_stk_base.100 8 = 11:U64
  lea.stk lhsaddr.201:A64 = msg_eval%91 0
  ld pointer.90:A64 = lhsaddr.201 0
  pusharg 11:U64
  pusharg pointer.90
  pusharg 1:S32
  bsr write
  poparg call.100:S64
  .stk msg_eval%92 8 16
  lea.stk var_stk_base.101:A64 msg_eval%92 0
  lea.mem lhsaddr.202:A64 = $gen/global_val_10 0
  st var_stk_base.101 0 = lhsaddr.202
  st var_stk_base.101 8 = 11:U64
  lea.stk lhsaddr.203:A64 = msg_eval%92 0
  ld pointer.91:A64 = lhsaddr.203 0
  pusharg 11:U64
  pusharg pointer.91
  pusharg 1:S32
  bsr write
  poparg call.101:S64
  .stk msg_eval%93 8 16
  lea.stk var_stk_base.102:A64 msg_eval%93 0
  lea.mem lhsaddr.204:A64 = $gen/global_val_88 0
  st var_stk_base.102 0 = lhsaddr.204
  st var_stk_base.102 8 = 54:U64
  lea.stk lhsaddr.205:A64 = msg_eval%93 0
  ld pointer.92:A64 = lhsaddr.205 0
  pusharg 54:U64
  pusharg pointer.92
  pusharg 1:S32
  bsr write
  poparg call.102:S64
  .stk msg_eval%94 8 16
  lea.stk var_stk_base.103:A64 msg_eval%94 0
  lea.mem lhsaddr.206:A64 = $gen/global_val_12 0
  st var_stk_base.103 0 = lhsaddr.206
  st var_stk_base.103 8 = 2:U64
  lea.stk lhsaddr.207:A64 = msg_eval%94 0
  ld pointer.93:A64 = lhsaddr.207 0
  pusharg 2:U64
  pusharg pointer.93
  pusharg 1:S32
  bsr write
  poparg call.103:S64
  .stk msg_eval%95 8 16
  lea.stk var_stk_base.104:A64 msg_eval%95 0
  lea.mem lhsaddr.208:A64 = $gen/global_val_26 0
  st var_stk_base.104 0 = lhsaddr.208
  st var_stk_base.104 8 = 6:U64
  lea.stk lhsaddr.209:A64 = msg_eval%95 0
  ld pointer.94:A64 = lhsaddr.209 0
  pusharg 6:U64
  pusharg pointer.94
  pusharg 1:S32
  bsr write
  poparg call.104:S64
  .stk msg_eval%96 8 16
  lea.stk var_stk_base.105:A64 msg_eval%96 0
  lea.mem lhsaddr.210:A64 = $gen/global_val_14 0
  st var_stk_base.105 0 = lhsaddr.210
  st var_stk_base.105 8 = 4:U64
  lea.stk lhsaddr.211:A64 = msg_eval%96 0
  ld pointer.95:A64 = lhsaddr.211 0
  pusharg 4:U64
  pusharg pointer.95
  pusharg 1:S32
  bsr write
  poparg call.105:S64
  .stk msg_eval%97 8 16
  lea.stk var_stk_base.106:A64 msg_eval%97 0
  lea.mem lhsaddr.212:A64 = $gen/global_val_15 0
  st var_stk_base.106 0 = lhsaddr.212
  st var_stk_base.106 8 = 8:U64
  lea.stk lhsaddr.213:A64 = msg_eval%97 0
  ld pointer.96:A64 = lhsaddr.213 0
  pusharg 8:U64
  pusharg pointer.96
  pusharg 1:S32
  bsr write
  poparg call.106:S64
  .stk msg_eval%98 8 16
  lea.stk var_stk_base.107:A64 msg_eval%98 0
  lea.mem lhsaddr.214:A64 = $gen/global_val_16 0
  st var_stk_base.107 0 = lhsaddr.214
  st var_stk_base.107 8 = 4:U64
  lea.stk lhsaddr.215:A64 = msg_eval%98 0
  ld pointer.97:A64 = lhsaddr.215 0
  pusharg 4:U64
  pusharg pointer.97
  pusharg 1:S32
  bsr write
  poparg call.107:S64
  .stk msg_eval%99 8 16
  lea.stk var_stk_base.108:A64 msg_eval%99 0
  lea.mem lhsaddr.216:A64 = $gen/global_val_88 0
  st var_stk_base.108 0 = lhsaddr.216
  st var_stk_base.108 8 = 54:U64
  lea.stk lhsaddr.217:A64 = msg_eval%99 0
  ld pointer.98:A64 = lhsaddr.217 0
  pusharg 54:U64
  pusharg pointer.98
  pusharg 1:S32
  bsr write
  poparg call.108:S64
  .stk msg_eval%100 8 16
  lea.stk var_stk_base.109:A64 msg_eval%100 0
  lea.mem lhsaddr.218:A64 = $gen/global_val_17 0
  st var_stk_base.109 0 = lhsaddr.218
  st var_stk_base.109 8 = 1:U64
  lea.stk lhsaddr.219:A64 = msg_eval%100 0
  ld pointer.99:A64 = lhsaddr.219 0
  pusharg 1:U64
  pusharg pointer.99
  pusharg 1:S32
  bsr write
  poparg call.109:S64
  trap
.bbl br_join.9
  .reg R64 expr.10
  .stk arg0.10 8 16
  lea.stk var_stk_base.110:A64 arg0.10 0
  lea.mem lhsaddr.220:A64 = $gen/global_val_89 0
  st var_stk_base.110 0 = lhsaddr.220
  st var_stk_base.110 8 = 4:U64
  lea.stk lhsaddr.221:A64 = arg0.10 0
  pusharg lhsaddr.221
  bsr parse_real_test/parse_r64
  poparg call.110:R64
  mov expr.10 = call.110
  bra end_expr.10
.bbl end_expr.10
  mov a_val%21:R64 = expr.10
  bitcast bitcast.10:U64 = a_val%21
  beq 9223372036854775808:U64 bitcast.10 br_join.10
  .stk msg_eval%101 8 16
  lea.stk var_stk_base.111:A64 msg_eval%101 0
  lea.mem lhsaddr.222:A64 = $gen/global_val_9 0
  st var_stk_base.111 0 = lhsaddr.222
  st var_stk_base.111 8 = 11:U64
  lea.stk lhsaddr.223:A64 = msg_eval%101 0
  ld pointer.100:A64 = lhsaddr.223 0
  pusharg 11:U64
  pusharg pointer.100
  pusharg 1:S32
  bsr write
  poparg call.111:S64
  .stk msg_eval%102 8 16
  lea.stk var_stk_base.112:A64 msg_eval%102 0
  lea.mem lhsaddr.224:A64 = $gen/global_val_10 0
  st var_stk_base.112 0 = lhsaddr.224
  st var_stk_base.112 8 = 11:U64
  lea.stk lhsaddr.225:A64 = msg_eval%102 0
  ld pointer.101:A64 = lhsaddr.225 0
  pusharg 11:U64
  pusharg pointer.101
  pusharg 1:S32
  bsr write
  poparg call.112:S64
  .stk msg_eval%103 8 16
  lea.stk var_stk_base.113:A64 msg_eval%103 0
  lea.mem lhsaddr.226:A64 = $gen/global_val_90 0
  st var_stk_base.113 0 = lhsaddr.226
  st var_stk_base.113 8 = 54:U64
  lea.stk lhsaddr.227:A64 = msg_eval%103 0
  ld pointer.102:A64 = lhsaddr.227 0
  pusharg 54:U64
  pusharg pointer.102
  pusharg 1:S32
  bsr write
  poparg call.113:S64
  .stk msg_eval%104 8 16
  lea.stk var_stk_base.114:A64 msg_eval%104 0
  lea.mem lhsaddr.228:A64 = $gen/global_val_12 0
  st var_stk_base.114 0 = lhsaddr.228
  st var_stk_base.114 8 = 2:U64
  lea.stk lhsaddr.229:A64 = msg_eval%104 0
  ld pointer.103:A64 = lhsaddr.229 0
  pusharg 2:U64
  pusharg pointer.103
  pusharg 1:S32
  bsr write
  poparg call.114:S64
  .stk msg_eval%105 8 16
  lea.stk var_stk_base.115:A64 msg_eval%105 0
  lea.mem lhsaddr.230:A64 = $gen/global_val_26 0
  st var_stk_base.115 0 = lhsaddr.230
  st var_stk_base.115 8 = 6:U64
  lea.stk lhsaddr.231:A64 = msg_eval%105 0
  ld pointer.104:A64 = lhsaddr.231 0
  pusharg 6:U64
  pusharg pointer.104
  pusharg 1:S32
  bsr write
  poparg call.115:S64
  .stk msg_eval%106 8 16
  lea.stk var_stk_base.116:A64 msg_eval%106 0
  lea.mem lhsaddr.232:A64 = $gen/global_val_14 0
  st var_stk_base.116 0 = lhsaddr.232
  st var_stk_base.116 8 = 4:U64
  lea.stk lhsaddr.233:A64 = msg_eval%106 0
  ld pointer.105:A64 = lhsaddr.233 0
  pusharg 4:U64
  pusharg pointer.105
  pusharg 1:S32
  bsr write
  poparg call.116:S64
  .stk msg_eval%107 8 16
  lea.stk var_stk_base.117:A64 msg_eval%107 0
  lea.mem lhsaddr.234:A64 = $gen/global_val_15 0
  st var_stk_base.117 0 = lhsaddr.234
  st var_stk_base.117 8 = 8:U64
  lea.stk lhsaddr.235:A64 = msg_eval%107 0
  ld pointer.106:A64 = lhsaddr.235 0
  pusharg 8:U64
  pusharg pointer.106
  pusharg 1:S32
  bsr write
  poparg call.117:S64
  .stk msg_eval%108 8 16
  lea.stk var_stk_base.118:A64 msg_eval%108 0
  lea.mem lhsaddr.236:A64 = $gen/global_val_16 0
  st var_stk_base.118 0 = lhsaddr.236
  st var_stk_base.118 8 = 4:U64
  lea.stk lhsaddr.237:A64 = msg_eval%108 0
  ld pointer.107:A64 = lhsaddr.237 0
  pusharg 4:U64
  pusharg pointer.107
  pusharg 1:S32
  bsr write
  poparg call.118:S64
  .stk msg_eval%109 8 16
  lea.stk var_stk_base.119:A64 msg_eval%109 0
  lea.mem lhsaddr.238:A64 = $gen/global_val_90 0
  st var_stk_base.119 0 = lhsaddr.238
  st var_stk_base.119 8 = 54:U64
  lea.stk lhsaddr.239:A64 = msg_eval%109 0
  ld pointer.108:A64 = lhsaddr.239 0
  pusharg 54:U64
  pusharg pointer.108
  pusharg 1:S32
  bsr write
  poparg call.119:S64
  .stk msg_eval%110 8 16
  lea.stk var_stk_base.120:A64 msg_eval%110 0
  lea.mem lhsaddr.240:A64 = $gen/global_val_17 0
  st var_stk_base.120 0 = lhsaddr.240
  st var_stk_base.120 8 = 1:U64
  lea.stk lhsaddr.241:A64 = msg_eval%110 0
  ld pointer.109:A64 = lhsaddr.241 0
  pusharg 1:U64
  pusharg pointer.109
  pusharg 1:S32
  bsr write
  poparg call.120:S64
  trap
.bbl br_join.10
  .reg R64 expr.11
  .stk arg0.11 8 16
  lea.stk var_stk_base.121:A64 arg0.11 0
  lea.mem lhsaddr.242:A64 = $gen/global_val_91 0
  st var_stk_base.121 0 = lhsaddr.242
  st var_stk_base.121 8 = 5:U64
  lea.stk lhsaddr.243:A64 = arg0.11 0
  pusharg lhsaddr.243
  bsr parse_real_test/parse_r64
  poparg call.121:R64
  mov expr.11 = call.121
  bra end_expr.11
.bbl end_expr.11
  mov a_val%23:R64 = expr.11
  bitcast bitcast.11:U64 = a_val%23
  beq 9223372036854775808:U64 bitcast.11 br_join.11
  .stk msg_eval%111 8 16
  lea.stk var_stk_base.122:A64 msg_eval%111 0
  lea.mem lhsaddr.244:A64 = $gen/global_val_9 0
  st var_stk_base.122 0 = lhsaddr.244
  st var_stk_base.122 8 = 11:U64
  lea.stk lhsaddr.245:A64 = msg_eval%111 0
  ld pointer.110:A64 = lhsaddr.245 0
  pusharg 11:U64
  pusharg pointer.110
  pusharg 1:S32
  bsr write
  poparg call.122:S64
  .stk msg_eval%112 8 16
  lea.stk var_stk_base.123:A64 msg_eval%112 0
  lea.mem lhsaddr.246:A64 = $gen/global_val_10 0
  st var_stk_base.123 0 = lhsaddr.246
  st var_stk_base.123 8 = 11:U64
  lea.stk lhsaddr.247:A64 = msg_eval%112 0
  ld pointer.111:A64 = lhsaddr.247 0
  pusharg 11:U64
  pusharg pointer.111
  pusharg 1:S32
  bsr write
  poparg call.123:S64
  .stk msg_eval%113 8 16
  lea.stk var_stk_base.124:A64 msg_eval%113 0
  lea.mem lhsaddr.248:A64 = $gen/global_val_92 0
  st var_stk_base.124 0 = lhsaddr.248
  st var_stk_base.124 8 = 54:U64
  lea.stk lhsaddr.249:A64 = msg_eval%113 0
  ld pointer.112:A64 = lhsaddr.249 0
  pusharg 54:U64
  pusharg pointer.112
  pusharg 1:S32
  bsr write
  poparg call.124:S64
  .stk msg_eval%114 8 16
  lea.stk var_stk_base.125:A64 msg_eval%114 0
  lea.mem lhsaddr.250:A64 = $gen/global_val_12 0
  st var_stk_base.125 0 = lhsaddr.250
  st var_stk_base.125 8 = 2:U64
  lea.stk lhsaddr.251:A64 = msg_eval%114 0
  ld pointer.113:A64 = lhsaddr.251 0
  pusharg 2:U64
  pusharg pointer.113
  pusharg 1:S32
  bsr write
  poparg call.125:S64
  .stk msg_eval%115 8 16
  lea.stk var_stk_base.126:A64 msg_eval%115 0
  lea.mem lhsaddr.252:A64 = $gen/global_val_26 0
  st var_stk_base.126 0 = lhsaddr.252
  st var_stk_base.126 8 = 6:U64
  lea.stk lhsaddr.253:A64 = msg_eval%115 0
  ld pointer.114:A64 = lhsaddr.253 0
  pusharg 6:U64
  pusharg pointer.114
  pusharg 1:S32
  bsr write
  poparg call.126:S64
  .stk msg_eval%116 8 16
  lea.stk var_stk_base.127:A64 msg_eval%116 0
  lea.mem lhsaddr.254:A64 = $gen/global_val_14 0
  st var_stk_base.127 0 = lhsaddr.254
  st var_stk_base.127 8 = 4:U64
  lea.stk lhsaddr.255:A64 = msg_eval%116 0
  ld pointer.115:A64 = lhsaddr.255 0
  pusharg 4:U64
  pusharg pointer.115
  pusharg 1:S32
  bsr write
  poparg call.127:S64
  .stk msg_eval%117 8 16
  lea.stk var_stk_base.128:A64 msg_eval%117 0
  lea.mem lhsaddr.256:A64 = $gen/global_val_15 0
  st var_stk_base.128 0 = lhsaddr.256
  st var_stk_base.128 8 = 8:U64
  lea.stk lhsaddr.257:A64 = msg_eval%117 0
  ld pointer.116:A64 = lhsaddr.257 0
  pusharg 8:U64
  pusharg pointer.116
  pusharg 1:S32
  bsr write
  poparg call.128:S64
  .stk msg_eval%118 8 16
  lea.stk var_stk_base.129:A64 msg_eval%118 0
  lea.mem lhsaddr.258:A64 = $gen/global_val_16 0
  st var_stk_base.129 0 = lhsaddr.258
  st var_stk_base.129 8 = 4:U64
  lea.stk lhsaddr.259:A64 = msg_eval%118 0
  ld pointer.117:A64 = lhsaddr.259 0
  pusharg 4:U64
  pusharg pointer.117
  pusharg 1:S32
  bsr write
  poparg call.129:S64
  .stk msg_eval%119 8 16
  lea.stk var_stk_base.130:A64 msg_eval%119 0
  lea.mem lhsaddr.260:A64 = $gen/global_val_92 0
  st var_stk_base.130 0 = lhsaddr.260
  st var_stk_base.130 8 = 54:U64
  lea.stk lhsaddr.261:A64 = msg_eval%119 0
  ld pointer.118:A64 = lhsaddr.261 0
  pusharg 54:U64
  pusharg pointer.118
  pusharg 1:S32
  bsr write
  poparg call.130:S64
  .stk msg_eval%120 8 16
  lea.stk var_stk_base.131:A64 msg_eval%120 0
  lea.mem lhsaddr.262:A64 = $gen/global_val_17 0
  st var_stk_base.131 0 = lhsaddr.262
  st var_stk_base.131 8 = 1:U64
  lea.stk lhsaddr.263:A64 = msg_eval%120 0
  ld pointer.119:A64 = lhsaddr.263 0
  pusharg 1:U64
  pusharg pointer.119
  pusharg 1:S32
  bsr write
  poparg call.131:S64
  trap
.bbl br_join.11
  .reg R64 expr.12
  .stk arg0.12 8 16
  lea.stk var_stk_base.132:A64 arg0.12 0
  lea.mem lhsaddr.264:A64 = $gen/global_val_93 0
  st var_stk_base.132 0 = lhsaddr.264
  st var_stk_base.132 8 = 6:U64
  lea.stk lhsaddr.265:A64 = arg0.12 0
  pusharg lhsaddr.265
  bsr parse_real_test/parse_r64
  poparg call.132:R64
  mov expr.12 = call.132
  bra end_expr.12
.bbl end_expr.12
  mov a_val%25:R64 = expr.12
  bitcast bitcast.12:U64 = a_val%25
  beq 9223372036854775808:U64 bitcast.12 br_join.12
  .stk msg_eval%121 8 16
  lea.stk var_stk_base.133:A64 msg_eval%121 0
  lea.mem lhsaddr.266:A64 = $gen/global_val_9 0
  st var_stk_base.133 0 = lhsaddr.266
  st var_stk_base.133 8 = 11:U64
  lea.stk lhsaddr.267:A64 = msg_eval%121 0
  ld pointer.120:A64 = lhsaddr.267 0
  pusharg 11:U64
  pusharg pointer.120
  pusharg 1:S32
  bsr write
  poparg call.133:S64
  .stk msg_eval%122 8 16
  lea.stk var_stk_base.134:A64 msg_eval%122 0
  lea.mem lhsaddr.268:A64 = $gen/global_val_10 0
  st var_stk_base.134 0 = lhsaddr.268
  st var_stk_base.134 8 = 11:U64
  lea.stk lhsaddr.269:A64 = msg_eval%122 0
  ld pointer.121:A64 = lhsaddr.269 0
  pusharg 11:U64
  pusharg pointer.121
  pusharg 1:S32
  bsr write
  poparg call.134:S64
  .stk msg_eval%123 8 16
  lea.stk var_stk_base.135:A64 msg_eval%123 0
  lea.mem lhsaddr.270:A64 = $gen/global_val_94 0
  st var_stk_base.135 0 = lhsaddr.270
  st var_stk_base.135 8 = 54:U64
  lea.stk lhsaddr.271:A64 = msg_eval%123 0
  ld pointer.122:A64 = lhsaddr.271 0
  pusharg 54:U64
  pusharg pointer.122
  pusharg 1:S32
  bsr write
  poparg call.135:S64
  .stk msg_eval%124 8 16
  lea.stk var_stk_base.136:A64 msg_eval%124 0
  lea.mem lhsaddr.272:A64 = $gen/global_val_12 0
  st var_stk_base.136 0 = lhsaddr.272
  st var_stk_base.136 8 = 2:U64
  lea.stk lhsaddr.273:A64 = msg_eval%124 0
  ld pointer.123:A64 = lhsaddr.273 0
  pusharg 2:U64
  pusharg pointer.123
  pusharg 1:S32
  bsr write
  poparg call.136:S64
  .stk msg_eval%125 8 16
  lea.stk var_stk_base.137:A64 msg_eval%125 0
  lea.mem lhsaddr.274:A64 = $gen/global_val_26 0
  st var_stk_base.137 0 = lhsaddr.274
  st var_stk_base.137 8 = 6:U64
  lea.stk lhsaddr.275:A64 = msg_eval%125 0
  ld pointer.124:A64 = lhsaddr.275 0
  pusharg 6:U64
  pusharg pointer.124
  pusharg 1:S32
  bsr write
  poparg call.137:S64
  .stk msg_eval%126 8 16
  lea.stk var_stk_base.138:A64 msg_eval%126 0
  lea.mem lhsaddr.276:A64 = $gen/global_val_14 0
  st var_stk_base.138 0 = lhsaddr.276
  st var_stk_base.138 8 = 4:U64
  lea.stk lhsaddr.277:A64 = msg_eval%126 0
  ld pointer.125:A64 = lhsaddr.277 0
  pusharg 4:U64
  pusharg pointer.125
  pusharg 1:S32
  bsr write
  poparg call.138:S64
  .stk msg_eval%127 8 16
  lea.stk var_stk_base.139:A64 msg_eval%127 0
  lea.mem lhsaddr.278:A64 = $gen/global_val_15 0
  st var_stk_base.139 0 = lhsaddr.278
  st var_stk_base.139 8 = 8:U64
  lea.stk lhsaddr.279:A64 = msg_eval%127 0
  ld pointer.126:A64 = lhsaddr.279 0
  pusharg 8:U64
  pusharg pointer.126
  pusharg 1:S32
  bsr write
  poparg call.139:S64
  .stk msg_eval%128 8 16
  lea.stk var_stk_base.140:A64 msg_eval%128 0
  lea.mem lhsaddr.280:A64 = $gen/global_val_16 0
  st var_stk_base.140 0 = lhsaddr.280
  st var_stk_base.140 8 = 4:U64
  lea.stk lhsaddr.281:A64 = msg_eval%128 0
  ld pointer.127:A64 = lhsaddr.281 0
  pusharg 4:U64
  pusharg pointer.127
  pusharg 1:S32
  bsr write
  poparg call.140:S64
  .stk msg_eval%129 8 16
  lea.stk var_stk_base.141:A64 msg_eval%129 0
  lea.mem lhsaddr.282:A64 = $gen/global_val_94 0
  st var_stk_base.141 0 = lhsaddr.282
  st var_stk_base.141 8 = 54:U64
  lea.stk lhsaddr.283:A64 = msg_eval%129 0
  ld pointer.128:A64 = lhsaddr.283 0
  pusharg 54:U64
  pusharg pointer.128
  pusharg 1:S32
  bsr write
  poparg call.141:S64
  .stk msg_eval%130 8 16
  lea.stk var_stk_base.142:A64 msg_eval%130 0
  lea.mem lhsaddr.284:A64 = $gen/global_val_17 0
  st var_stk_base.142 0 = lhsaddr.284
  st var_stk_base.142 8 = 1:U64
  lea.stk lhsaddr.285:A64 = msg_eval%130 0
  ld pointer.129:A64 = lhsaddr.285 0
  pusharg 1:U64
  pusharg pointer.129
  pusharg 1:S32
  bsr write
  poparg call.142:S64
  trap
.bbl br_join.12
  .reg R64 expr.13
  .stk arg0.13 8 16
  lea.stk var_stk_base.143:A64 arg0.13 0
  lea.mem lhsaddr.286:A64 = $gen/global_val_95 0
  st var_stk_base.143 0 = lhsaddr.286
  st var_stk_base.143 8 = 6:U64
  lea.stk lhsaddr.287:A64 = arg0.13 0
  pusharg lhsaddr.287
  bsr parse_real_test/parse_r64
  poparg call.143:R64
  mov expr.13 = call.143
  bra end_expr.13
.bbl end_expr.13
  mov a_val%27:R64 = expr.13
  bitcast bitcast.13:U64 = a_val%27
  beq 13830554455654793216:U64 bitcast.13 br_join.13
  .stk msg_eval%131 8 16
  lea.stk var_stk_base.144:A64 msg_eval%131 0
  lea.mem lhsaddr.288:A64 = $gen/global_val_9 0
  st var_stk_base.144 0 = lhsaddr.288
  st var_stk_base.144 8 = 11:U64
  lea.stk lhsaddr.289:A64 = msg_eval%131 0
  ld pointer.130:A64 = lhsaddr.289 0
  pusharg 11:U64
  pusharg pointer.130
  pusharg 1:S32
  bsr write
  poparg call.144:S64
  .stk msg_eval%132 8 16
  lea.stk var_stk_base.145:A64 msg_eval%132 0
  lea.mem lhsaddr.290:A64 = $gen/global_val_10 0
  st var_stk_base.145 0 = lhsaddr.290
  st var_stk_base.145 8 = 11:U64
  lea.stk lhsaddr.291:A64 = msg_eval%132 0
  ld pointer.131:A64 = lhsaddr.291 0
  pusharg 11:U64
  pusharg pointer.131
  pusharg 1:S32
  bsr write
  poparg call.145:S64
  .stk msg_eval%133 8 16
  lea.stk var_stk_base.146:A64 msg_eval%133 0
  lea.mem lhsaddr.292:A64 = $gen/global_val_96 0
  st var_stk_base.146 0 = lhsaddr.292
  st var_stk_base.146 8 = 54:U64
  lea.stk lhsaddr.293:A64 = msg_eval%133 0
  ld pointer.132:A64 = lhsaddr.293 0
  pusharg 54:U64
  pusharg pointer.132
  pusharg 1:S32
  bsr write
  poparg call.146:S64
  .stk msg_eval%134 8 16
  lea.stk var_stk_base.147:A64 msg_eval%134 0
  lea.mem lhsaddr.294:A64 = $gen/global_val_12 0
  st var_stk_base.147 0 = lhsaddr.294
  st var_stk_base.147 8 = 2:U64
  lea.stk lhsaddr.295:A64 = msg_eval%134 0
  ld pointer.133:A64 = lhsaddr.295 0
  pusharg 2:U64
  pusharg pointer.133
  pusharg 1:S32
  bsr write
  poparg call.147:S64
  .stk msg_eval%135 8 16
  lea.stk var_stk_base.148:A64 msg_eval%135 0
  lea.mem lhsaddr.296:A64 = $gen/global_val_26 0
  st var_stk_base.148 0 = lhsaddr.296
  st var_stk_base.148 8 = 6:U64
  lea.stk lhsaddr.297:A64 = msg_eval%135 0
  ld pointer.134:A64 = lhsaddr.297 0
  pusharg 6:U64
  pusharg pointer.134
  pusharg 1:S32
  bsr write
  poparg call.148:S64
  .stk msg_eval%136 8 16
  lea.stk var_stk_base.149:A64 msg_eval%136 0
  lea.mem lhsaddr.298:A64 = $gen/global_val_14 0
  st var_stk_base.149 0 = lhsaddr.298
  st var_stk_base.149 8 = 4:U64
  lea.stk lhsaddr.299:A64 = msg_eval%136 0
  ld pointer.135:A64 = lhsaddr.299 0
  pusharg 4:U64
  pusharg pointer.135
  pusharg 1:S32
  bsr write
  poparg call.149:S64
  .stk msg_eval%137 8 16
  lea.stk var_stk_base.150:A64 msg_eval%137 0
  lea.mem lhsaddr.300:A64 = $gen/global_val_15 0
  st var_stk_base.150 0 = lhsaddr.300
  st var_stk_base.150 8 = 8:U64
  lea.stk lhsaddr.301:A64 = msg_eval%137 0
  ld pointer.136:A64 = lhsaddr.301 0
  pusharg 8:U64
  pusharg pointer.136
  pusharg 1:S32
  bsr write
  poparg call.150:S64
  .stk msg_eval%138 8 16
  lea.stk var_stk_base.151:A64 msg_eval%138 0
  lea.mem lhsaddr.302:A64 = $gen/global_val_16 0
  st var_stk_base.151 0 = lhsaddr.302
  st var_stk_base.151 8 = 4:U64
  lea.stk lhsaddr.303:A64 = msg_eval%138 0
  ld pointer.137:A64 = lhsaddr.303 0
  pusharg 4:U64
  pusharg pointer.137
  pusharg 1:S32
  bsr write
  poparg call.151:S64
  .stk msg_eval%139 8 16
  lea.stk var_stk_base.152:A64 msg_eval%139 0
  lea.mem lhsaddr.304:A64 = $gen/global_val_96 0
  st var_stk_base.152 0 = lhsaddr.304
  st var_stk_base.152 8 = 54:U64
  lea.stk lhsaddr.305:A64 = msg_eval%139 0
  ld pointer.138:A64 = lhsaddr.305 0
  pusharg 54:U64
  pusharg pointer.138
  pusharg 1:S32
  bsr write
  poparg call.152:S64
  .stk msg_eval%140 8 16
  lea.stk var_stk_base.153:A64 msg_eval%140 0
  lea.mem lhsaddr.306:A64 = $gen/global_val_17 0
  st var_stk_base.153 0 = lhsaddr.306
  st var_stk_base.153 8 = 1:U64
  lea.stk lhsaddr.307:A64 = msg_eval%140 0
  ld pointer.139:A64 = lhsaddr.307 0
  pusharg 1:U64
  pusharg pointer.139
  pusharg 1:S32
  bsr write
  poparg call.153:S64
  trap
.bbl br_join.13
  .reg R64 expr.14
  .stk arg0.14 8 16
  lea.stk var_stk_base.154:A64 arg0.14 0
  lea.mem lhsaddr.308:A64 = $gen/global_val_97 0
  st var_stk_base.154 0 = lhsaddr.308
  st var_stk_base.154 8 = 7:U64
  lea.stk lhsaddr.309:A64 = arg0.14 0
  pusharg lhsaddr.309
  bsr parse_real_test/parse_r64
  poparg call.154:R64
  mov expr.14 = call.154
  bra end_expr.14
.bbl end_expr.14
  mov a_val%29:R64 = expr.14
  bitcast bitcast.14:U64 = a_val%29
  beq 13826050856027422720:U64 bitcast.14 br_join.14
  .stk msg_eval%141 8 16
  lea.stk var_stk_base.155:A64 msg_eval%141 0
  lea.mem lhsaddr.310:A64 = $gen/global_val_9 0
  st var_stk_base.155 0 = lhsaddr.310
  st var_stk_base.155 8 = 11:U64
  lea.stk lhsaddr.311:A64 = msg_eval%141 0
  ld pointer.140:A64 = lhsaddr.311 0
  pusharg 11:U64
  pusharg pointer.140
  pusharg 1:S32
  bsr write
  poparg call.155:S64
  .stk msg_eval%142 8 16
  lea.stk var_stk_base.156:A64 msg_eval%142 0
  lea.mem lhsaddr.312:A64 = $gen/global_val_10 0
  st var_stk_base.156 0 = lhsaddr.312
  st var_stk_base.156 8 = 11:U64
  lea.stk lhsaddr.313:A64 = msg_eval%142 0
  ld pointer.141:A64 = lhsaddr.313 0
  pusharg 11:U64
  pusharg pointer.141
  pusharg 1:S32
  bsr write
  poparg call.156:S64
  .stk msg_eval%143 8 16
  lea.stk var_stk_base.157:A64 msg_eval%143 0
  lea.mem lhsaddr.314:A64 = $gen/global_val_98 0
  st var_stk_base.157 0 = lhsaddr.314
  st var_stk_base.157 8 = 54:U64
  lea.stk lhsaddr.315:A64 = msg_eval%143 0
  ld pointer.142:A64 = lhsaddr.315 0
  pusharg 54:U64
  pusharg pointer.142
  pusharg 1:S32
  bsr write
  poparg call.157:S64
  .stk msg_eval%144 8 16
  lea.stk var_stk_base.158:A64 msg_eval%144 0
  lea.mem lhsaddr.316:A64 = $gen/global_val_12 0
  st var_stk_base.158 0 = lhsaddr.316
  st var_stk_base.158 8 = 2:U64
  lea.stk lhsaddr.317:A64 = msg_eval%144 0
  ld pointer.143:A64 = lhsaddr.317 0
  pusharg 2:U64
  pusharg pointer.143
  pusharg 1:S32
  bsr write
  poparg call.158:S64
  .stk msg_eval%145 8 16
  lea.stk var_stk_base.159:A64 msg_eval%145 0
  lea.mem lhsaddr.318:A64 = $gen/global_val_26 0
  st var_stk_base.159 0 = lhsaddr.318
  st var_stk_base.159 8 = 6:U64
  lea.stk lhsaddr.319:A64 = msg_eval%145 0
  ld pointer.144:A64 = lhsaddr.319 0
  pusharg 6:U64
  pusharg pointer.144
  pusharg 1:S32
  bsr write
  poparg call.159:S64
  .stk msg_eval%146 8 16
  lea.stk var_stk_base.160:A64 msg_eval%146 0
  lea.mem lhsaddr.320:A64 = $gen/global_val_14 0
  st var_stk_base.160 0 = lhsaddr.320
  st var_stk_base.160 8 = 4:U64
  lea.stk lhsaddr.321:A64 = msg_eval%146 0
  ld pointer.145:A64 = lhsaddr.321 0
  pusharg 4:U64
  pusharg pointer.145
  pusharg 1:S32
  bsr write
  poparg call.160:S64
  .stk msg_eval%147 8 16
  lea.stk var_stk_base.161:A64 msg_eval%147 0
  lea.mem lhsaddr.322:A64 = $gen/global_val_15 0
  st var_stk_base.161 0 = lhsaddr.322
  st var_stk_base.161 8 = 8:U64
  lea.stk lhsaddr.323:A64 = msg_eval%147 0
  ld pointer.146:A64 = lhsaddr.323 0
  pusharg 8:U64
  pusharg pointer.146
  pusharg 1:S32
  bsr write
  poparg call.161:S64
  .stk msg_eval%148 8 16
  lea.stk var_stk_base.162:A64 msg_eval%148 0
  lea.mem lhsaddr.324:A64 = $gen/global_val_16 0
  st var_stk_base.162 0 = lhsaddr.324
  st var_stk_base.162 8 = 4:U64
  lea.stk lhsaddr.325:A64 = msg_eval%148 0
  ld pointer.147:A64 = lhsaddr.325 0
  pusharg 4:U64
  pusharg pointer.147
  pusharg 1:S32
  bsr write
  poparg call.162:S64
  .stk msg_eval%149 8 16
  lea.stk var_stk_base.163:A64 msg_eval%149 0
  lea.mem lhsaddr.326:A64 = $gen/global_val_98 0
  st var_stk_base.163 0 = lhsaddr.326
  st var_stk_base.163 8 = 54:U64
  lea.stk lhsaddr.327:A64 = msg_eval%149 0
  ld pointer.148:A64 = lhsaddr.327 0
  pusharg 54:U64
  pusharg pointer.148
  pusharg 1:S32
  bsr write
  poparg call.163:S64
  .stk msg_eval%150 8 16
  lea.stk var_stk_base.164:A64 msg_eval%150 0
  lea.mem lhsaddr.328:A64 = $gen/global_val_17 0
  st var_stk_base.164 0 = lhsaddr.328
  st var_stk_base.164 8 = 1:U64
  lea.stk lhsaddr.329:A64 = msg_eval%150 0
  ld pointer.149:A64 = lhsaddr.329 0
  pusharg 1:U64
  pusharg pointer.149
  pusharg 1:S32
  bsr write
  poparg call.164:S64
  trap
.bbl br_join.14
  .reg R64 expr.15
  .stk arg0.15 8 16
  lea.stk var_stk_base.165:A64 arg0.15 0
  lea.mem lhsaddr.330:A64 = $gen/global_val_99 0
  st var_stk_base.165 0 = lhsaddr.330
  st var_stk_base.165 8 = 7:U64
  lea.stk lhsaddr.331:A64 = arg0.15 0
  pusharg lhsaddr.331
  bsr parse_real_test/parse_r64
  poparg call.165:R64
  mov expr.15 = call.165
  bra end_expr.15
.bbl end_expr.15
  mov a_val%31:R64 = expr.15
  bitcast bitcast.15:U64 = a_val%31
  beq 13821547256400052224:U64 bitcast.15 br_join.15
  .stk msg_eval%151 8 16
  lea.stk var_stk_base.166:A64 msg_eval%151 0
  lea.mem lhsaddr.332:A64 = $gen/global_val_9 0
  st var_stk_base.166 0 = lhsaddr.332
  st var_stk_base.166 8 = 11:U64
  lea.stk lhsaddr.333:A64 = msg_eval%151 0
  ld pointer.150:A64 = lhsaddr.333 0
  pusharg 11:U64
  pusharg pointer.150
  pusharg 1:S32
  bsr write
  poparg call.166:S64
  .stk msg_eval%152 8 16
  lea.stk var_stk_base.167:A64 msg_eval%152 0
  lea.mem lhsaddr.334:A64 = $gen/global_val_10 0
  st var_stk_base.167 0 = lhsaddr.334
  st var_stk_base.167 8 = 11:U64
  lea.stk lhsaddr.335:A64 = msg_eval%152 0
  ld pointer.151:A64 = lhsaddr.335 0
  pusharg 11:U64
  pusharg pointer.151
  pusharg 1:S32
  bsr write
  poparg call.167:S64
  .stk msg_eval%153 8 16
  lea.stk var_stk_base.168:A64 msg_eval%153 0
  lea.mem lhsaddr.336:A64 = $gen/global_val_100 0
  st var_stk_base.168 0 = lhsaddr.336
  st var_stk_base.168 8 = 54:U64
  lea.stk lhsaddr.337:A64 = msg_eval%153 0
  ld pointer.152:A64 = lhsaddr.337 0
  pusharg 54:U64
  pusharg pointer.152
  pusharg 1:S32
  bsr write
  poparg call.168:S64
  .stk msg_eval%154 8 16
  lea.stk var_stk_base.169:A64 msg_eval%154 0
  lea.mem lhsaddr.338:A64 = $gen/global_val_12 0
  st var_stk_base.169 0 = lhsaddr.338
  st var_stk_base.169 8 = 2:U64
  lea.stk lhsaddr.339:A64 = msg_eval%154 0
  ld pointer.153:A64 = lhsaddr.339 0
  pusharg 2:U64
  pusharg pointer.153
  pusharg 1:S32
  bsr write
  poparg call.169:S64
  .stk msg_eval%155 8 16
  lea.stk var_stk_base.170:A64 msg_eval%155 0
  lea.mem lhsaddr.340:A64 = $gen/global_val_26 0
  st var_stk_base.170 0 = lhsaddr.340
  st var_stk_base.170 8 = 6:U64
  lea.stk lhsaddr.341:A64 = msg_eval%155 0
  ld pointer.154:A64 = lhsaddr.341 0
  pusharg 6:U64
  pusharg pointer.154
  pusharg 1:S32
  bsr write
  poparg call.170:S64
  .stk msg_eval%156 8 16
  lea.stk var_stk_base.171:A64 msg_eval%156 0
  lea.mem lhsaddr.342:A64 = $gen/global_val_14 0
  st var_stk_base.171 0 = lhsaddr.342
  st var_stk_base.171 8 = 4:U64
  lea.stk lhsaddr.343:A64 = msg_eval%156 0
  ld pointer.155:A64 = lhsaddr.343 0
  pusharg 4:U64
  pusharg pointer.155
  pusharg 1:S32
  bsr write
  poparg call.171:S64
  .stk msg_eval%157 8 16
  lea.stk var_stk_base.172:A64 msg_eval%157 0
  lea.mem lhsaddr.344:A64 = $gen/global_val_15 0
  st var_stk_base.172 0 = lhsaddr.344
  st var_stk_base.172 8 = 8:U64
  lea.stk lhsaddr.345:A64 = msg_eval%157 0
  ld pointer.156:A64 = lhsaddr.345 0
  pusharg 8:U64
  pusharg pointer.156
  pusharg 1:S32
  bsr write
  poparg call.172:S64
  .stk msg_eval%158 8 16
  lea.stk var_stk_base.173:A64 msg_eval%158 0
  lea.mem lhsaddr.346:A64 = $gen/global_val_16 0
  st var_stk_base.173 0 = lhsaddr.346
  st var_stk_base.173 8 = 4:U64
  lea.stk lhsaddr.347:A64 = msg_eval%158 0
  ld pointer.157:A64 = lhsaddr.347 0
  pusharg 4:U64
  pusharg pointer.157
  pusharg 1:S32
  bsr write
  poparg call.173:S64
  .stk msg_eval%159 8 16
  lea.stk var_stk_base.174:A64 msg_eval%159 0
  lea.mem lhsaddr.348:A64 = $gen/global_val_100 0
  st var_stk_base.174 0 = lhsaddr.348
  st var_stk_base.174 8 = 54:U64
  lea.stk lhsaddr.349:A64 = msg_eval%159 0
  ld pointer.158:A64 = lhsaddr.349 0
  pusharg 54:U64
  pusharg pointer.158
  pusharg 1:S32
  bsr write
  poparg call.174:S64
  .stk msg_eval%160 8 16
  lea.stk var_stk_base.175:A64 msg_eval%160 0
  lea.mem lhsaddr.350:A64 = $gen/global_val_17 0
  st var_stk_base.175 0 = lhsaddr.350
  st var_stk_base.175 8 = 1:U64
  lea.stk lhsaddr.351:A64 = msg_eval%160 0
  ld pointer.159:A64 = lhsaddr.351 0
  pusharg 1:U64
  pusharg pointer.159
  pusharg 1:S32
  bsr write
  poparg call.175:S64
  trap
.bbl br_join.15
  .reg R64 expr.16
  .stk arg0.16 8 16
  lea.stk var_stk_base.176:A64 arg0.16 0
  lea.mem lhsaddr.352:A64 = $gen/global_val_101 0
  st var_stk_base.176 0 = lhsaddr.352
  st var_stk_base.176 8 = 7:U64
  lea.stk lhsaddr.353:A64 = arg0.16 0
  pusharg lhsaddr.353
  bsr parse_real_test/parse_r64
  poparg call.176:R64
  mov expr.16 = call.176
  bra end_expr.16
.bbl end_expr.16
  mov a_val%33:R64 = expr.16
  bitcast bitcast.16:U64 = a_val%33
  beq 13817043656772681728:U64 bitcast.16 br_join.16
  .stk msg_eval%161 8 16
  lea.stk var_stk_base.177:A64 msg_eval%161 0
  lea.mem lhsaddr.354:A64 = $gen/global_val_9 0
  st var_stk_base.177 0 = lhsaddr.354
  st var_stk_base.177 8 = 11:U64
  lea.stk lhsaddr.355:A64 = msg_eval%161 0
  ld pointer.160:A64 = lhsaddr.355 0
  pusharg 11:U64
  pusharg pointer.160
  pusharg 1:S32
  bsr write
  poparg call.177:S64
  .stk msg_eval%162 8 16
  lea.stk var_stk_base.178:A64 msg_eval%162 0
  lea.mem lhsaddr.356:A64 = $gen/global_val_10 0
  st var_stk_base.178 0 = lhsaddr.356
  st var_stk_base.178 8 = 11:U64
  lea.stk lhsaddr.357:A64 = msg_eval%162 0
  ld pointer.161:A64 = lhsaddr.357 0
  pusharg 11:U64
  pusharg pointer.161
  pusharg 1:S32
  bsr write
  poparg call.178:S64
  .stk msg_eval%163 8 16
  lea.stk var_stk_base.179:A64 msg_eval%163 0
  lea.mem lhsaddr.358:A64 = $gen/global_val_102 0
  st var_stk_base.179 0 = lhsaddr.358
  st var_stk_base.179 8 = 54:U64
  lea.stk lhsaddr.359:A64 = msg_eval%163 0
  ld pointer.162:A64 = lhsaddr.359 0
  pusharg 54:U64
  pusharg pointer.162
  pusharg 1:S32
  bsr write
  poparg call.179:S64
  .stk msg_eval%164 8 16
  lea.stk var_stk_base.180:A64 msg_eval%164 0
  lea.mem lhsaddr.360:A64 = $gen/global_val_12 0
  st var_stk_base.180 0 = lhsaddr.360
  st var_stk_base.180 8 = 2:U64
  lea.stk lhsaddr.361:A64 = msg_eval%164 0
  ld pointer.163:A64 = lhsaddr.361 0
  pusharg 2:U64
  pusharg pointer.163
  pusharg 1:S32
  bsr write
  poparg call.180:S64
  .stk msg_eval%165 8 16
  lea.stk var_stk_base.181:A64 msg_eval%165 0
  lea.mem lhsaddr.362:A64 = $gen/global_val_26 0
  st var_stk_base.181 0 = lhsaddr.362
  st var_stk_base.181 8 = 6:U64
  lea.stk lhsaddr.363:A64 = msg_eval%165 0
  ld pointer.164:A64 = lhsaddr.363 0
  pusharg 6:U64
  pusharg pointer.164
  pusharg 1:S32
  bsr write
  poparg call.181:S64
  .stk msg_eval%166 8 16
  lea.stk var_stk_base.182:A64 msg_eval%166 0
  lea.mem lhsaddr.364:A64 = $gen/global_val_14 0
  st var_stk_base.182 0 = lhsaddr.364
  st var_stk_base.182 8 = 4:U64
  lea.stk lhsaddr.365:A64 = msg_eval%166 0
  ld pointer.165:A64 = lhsaddr.365 0
  pusharg 4:U64
  pusharg pointer.165
  pusharg 1:S32
  bsr write
  poparg call.182:S64
  .stk msg_eval%167 8 16
  lea.stk var_stk_base.183:A64 msg_eval%167 0
  lea.mem lhsaddr.366:A64 = $gen/global_val_15 0
  st var_stk_base.183 0 = lhsaddr.366
  st var_stk_base.183 8 = 8:U64
  lea.stk lhsaddr.367:A64 = msg_eval%167 0
  ld pointer.166:A64 = lhsaddr.367 0
  pusharg 8:U64
  pusharg pointer.166
  pusharg 1:S32
  bsr write
  poparg call.183:S64
  .stk msg_eval%168 8 16
  lea.stk var_stk_base.184:A64 msg_eval%168 0
  lea.mem lhsaddr.368:A64 = $gen/global_val_16 0
  st var_stk_base.184 0 = lhsaddr.368
  st var_stk_base.184 8 = 4:U64
  lea.stk lhsaddr.369:A64 = msg_eval%168 0
  ld pointer.167:A64 = lhsaddr.369 0
  pusharg 4:U64
  pusharg pointer.167
  pusharg 1:S32
  bsr write
  poparg call.184:S64
  .stk msg_eval%169 8 16
  lea.stk var_stk_base.185:A64 msg_eval%169 0
  lea.mem lhsaddr.370:A64 = $gen/global_val_102 0
  st var_stk_base.185 0 = lhsaddr.370
  st var_stk_base.185 8 = 54:U64
  lea.stk lhsaddr.371:A64 = msg_eval%169 0
  ld pointer.168:A64 = lhsaddr.371 0
  pusharg 54:U64
  pusharg pointer.168
  pusharg 1:S32
  bsr write
  poparg call.185:S64
  .stk msg_eval%170 8 16
  lea.stk var_stk_base.186:A64 msg_eval%170 0
  lea.mem lhsaddr.372:A64 = $gen/global_val_17 0
  st var_stk_base.186 0 = lhsaddr.372
  st var_stk_base.186 8 = 1:U64
  lea.stk lhsaddr.373:A64 = msg_eval%170 0
  ld pointer.169:A64 = lhsaddr.373 0
  pusharg 1:U64
  pusharg pointer.169
  pusharg 1:S32
  bsr write
  poparg call.186:S64
  trap
.bbl br_join.16
  .reg R64 expr.17
  .stk arg0.17 8 16
  lea.stk var_stk_base.187:A64 arg0.17 0
  lea.mem lhsaddr.374:A64 = $gen/global_val_103 0
  st var_stk_base.187 0 = lhsaddr.374
  st var_stk_base.187 8 = 7:U64
  lea.stk lhsaddr.375:A64 = arg0.17 0
  pusharg lhsaddr.375
  bsr parse_real_test/parse_r64
  poparg call.187:R64
  mov expr.17 = call.187
  bra end_expr.17
.bbl end_expr.17
  mov a_val%35:R64 = expr.17
  bitcast bitcast.17:U64 = a_val%35
  beq 13893604850437980160:U64 bitcast.17 br_join.17
  .stk msg_eval%171 8 16
  lea.stk var_stk_base.188:A64 msg_eval%171 0
  lea.mem lhsaddr.376:A64 = $gen/global_val_9 0
  st var_stk_base.188 0 = lhsaddr.376
  st var_stk_base.188 8 = 11:U64
  lea.stk lhsaddr.377:A64 = msg_eval%171 0
  ld pointer.170:A64 = lhsaddr.377 0
  pusharg 11:U64
  pusharg pointer.170
  pusharg 1:S32
  bsr write
  poparg call.188:S64
  .stk msg_eval%172 8 16
  lea.stk var_stk_base.189:A64 msg_eval%172 0
  lea.mem lhsaddr.378:A64 = $gen/global_val_10 0
  st var_stk_base.189 0 = lhsaddr.378
  st var_stk_base.189 8 = 11:U64
  lea.stk lhsaddr.379:A64 = msg_eval%172 0
  ld pointer.171:A64 = lhsaddr.379 0
  pusharg 11:U64
  pusharg pointer.171
  pusharg 1:S32
  bsr write
  poparg call.189:S64
  .stk msg_eval%173 8 16
  lea.stk var_stk_base.190:A64 msg_eval%173 0
  lea.mem lhsaddr.380:A64 = $gen/global_val_104 0
  st var_stk_base.190 0 = lhsaddr.380
  st var_stk_base.190 8 = 54:U64
  lea.stk lhsaddr.381:A64 = msg_eval%173 0
  ld pointer.172:A64 = lhsaddr.381 0
  pusharg 54:U64
  pusharg pointer.172
  pusharg 1:S32
  bsr write
  poparg call.190:S64
  .stk msg_eval%174 8 16
  lea.stk var_stk_base.191:A64 msg_eval%174 0
  lea.mem lhsaddr.382:A64 = $gen/global_val_12 0
  st var_stk_base.191 0 = lhsaddr.382
  st var_stk_base.191 8 = 2:U64
  lea.stk lhsaddr.383:A64 = msg_eval%174 0
  ld pointer.173:A64 = lhsaddr.383 0
  pusharg 2:U64
  pusharg pointer.173
  pusharg 1:S32
  bsr write
  poparg call.191:S64
  .stk msg_eval%175 8 16
  lea.stk var_stk_base.192:A64 msg_eval%175 0
  lea.mem lhsaddr.384:A64 = $gen/global_val_26 0
  st var_stk_base.192 0 = lhsaddr.384
  st var_stk_base.192 8 = 6:U64
  lea.stk lhsaddr.385:A64 = msg_eval%175 0
  ld pointer.174:A64 = lhsaddr.385 0
  pusharg 6:U64
  pusharg pointer.174
  pusharg 1:S32
  bsr write
  poparg call.192:S64
  .stk msg_eval%176 8 16
  lea.stk var_stk_base.193:A64 msg_eval%176 0
  lea.mem lhsaddr.386:A64 = $gen/global_val_14 0
  st var_stk_base.193 0 = lhsaddr.386
  st var_stk_base.193 8 = 4:U64
  lea.stk lhsaddr.387:A64 = msg_eval%176 0
  ld pointer.175:A64 = lhsaddr.387 0
  pusharg 4:U64
  pusharg pointer.175
  pusharg 1:S32
  bsr write
  poparg call.193:S64
  .stk msg_eval%177 8 16
  lea.stk var_stk_base.194:A64 msg_eval%177 0
  lea.mem lhsaddr.388:A64 = $gen/global_val_15 0
  st var_stk_base.194 0 = lhsaddr.388
  st var_stk_base.194 8 = 8:U64
  lea.stk lhsaddr.389:A64 = msg_eval%177 0
  ld pointer.176:A64 = lhsaddr.389 0
  pusharg 8:U64
  pusharg pointer.176
  pusharg 1:S32
  bsr write
  poparg call.194:S64
  .stk msg_eval%178 8 16
  lea.stk var_stk_base.195:A64 msg_eval%178 0
  lea.mem lhsaddr.390:A64 = $gen/global_val_16 0
  st var_stk_base.195 0 = lhsaddr.390
  st var_stk_base.195 8 = 4:U64
  lea.stk lhsaddr.391:A64 = msg_eval%178 0
  ld pointer.177:A64 = lhsaddr.391 0
  pusharg 4:U64
  pusharg pointer.177
  pusharg 1:S32
  bsr write
  poparg call.195:S64
  .stk msg_eval%179 8 16
  lea.stk var_stk_base.196:A64 msg_eval%179 0
  lea.mem lhsaddr.392:A64 = $gen/global_val_104 0
  st var_stk_base.196 0 = lhsaddr.392
  st var_stk_base.196 8 = 54:U64
  lea.stk lhsaddr.393:A64 = msg_eval%179 0
  ld pointer.178:A64 = lhsaddr.393 0
  pusharg 54:U64
  pusharg pointer.178
  pusharg 1:S32
  bsr write
  poparg call.196:S64
  .stk msg_eval%180 8 16
  lea.stk var_stk_base.197:A64 msg_eval%180 0
  lea.mem lhsaddr.394:A64 = $gen/global_val_17 0
  st var_stk_base.197 0 = lhsaddr.394
  st var_stk_base.197 8 = 1:U64
  lea.stk lhsaddr.395:A64 = msg_eval%180 0
  ld pointer.179:A64 = lhsaddr.395 0
  pusharg 1:U64
  pusharg pointer.179
  pusharg 1:S32
  bsr write
  poparg call.197:S64
  trap
.bbl br_join.17
  .reg R64 expr.18
  .stk arg0.18 8 16
  lea.stk var_stk_base.198:A64 arg0.18 0
  lea.mem lhsaddr.396:A64 = $gen/global_val_105 0
  st var_stk_base.198 0 = lhsaddr.396
  st var_stk_base.198 8 = 9:U64
  lea.stk lhsaddr.397:A64 = arg0.18 0
  pusharg lhsaddr.397
  bsr parse_real_test/parse_r64
  poparg call.198:R64
  mov expr.18 = call.198
  bra end_expr.18
.bbl end_expr.18
  mov a_val%37:R64 = expr.18
  bitcast bitcast.18:U64 = a_val%37
  beq 13893604850437980160:U64 bitcast.18 br_join.18
  .stk msg_eval%181 8 16
  lea.stk var_stk_base.199:A64 msg_eval%181 0
  lea.mem lhsaddr.398:A64 = $gen/global_val_9 0
  st var_stk_base.199 0 = lhsaddr.398
  st var_stk_base.199 8 = 11:U64
  lea.stk lhsaddr.399:A64 = msg_eval%181 0
  ld pointer.180:A64 = lhsaddr.399 0
  pusharg 11:U64
  pusharg pointer.180
  pusharg 1:S32
  bsr write
  poparg call.199:S64
  .stk msg_eval%182 8 16
  lea.stk var_stk_base.200:A64 msg_eval%182 0
  lea.mem lhsaddr.400:A64 = $gen/global_val_10 0
  st var_stk_base.200 0 = lhsaddr.400
  st var_stk_base.200 8 = 11:U64
  lea.stk lhsaddr.401:A64 = msg_eval%182 0
  ld pointer.181:A64 = lhsaddr.401 0
  pusharg 11:U64
  pusharg pointer.181
  pusharg 1:S32
  bsr write
  poparg call.200:S64
  .stk msg_eval%183 8 16
  lea.stk var_stk_base.201:A64 msg_eval%183 0
  lea.mem lhsaddr.402:A64 = $gen/global_val_106 0
  st var_stk_base.201 0 = lhsaddr.402
  st var_stk_base.201 8 = 54:U64
  lea.stk lhsaddr.403:A64 = msg_eval%183 0
  ld pointer.182:A64 = lhsaddr.403 0
  pusharg 54:U64
  pusharg pointer.182
  pusharg 1:S32
  bsr write
  poparg call.201:S64
  .stk msg_eval%184 8 16
  lea.stk var_stk_base.202:A64 msg_eval%184 0
  lea.mem lhsaddr.404:A64 = $gen/global_val_12 0
  st var_stk_base.202 0 = lhsaddr.404
  st var_stk_base.202 8 = 2:U64
  lea.stk lhsaddr.405:A64 = msg_eval%184 0
  ld pointer.183:A64 = lhsaddr.405 0
  pusharg 2:U64
  pusharg pointer.183
  pusharg 1:S32
  bsr write
  poparg call.202:S64
  .stk msg_eval%185 8 16
  lea.stk var_stk_base.203:A64 msg_eval%185 0
  lea.mem lhsaddr.406:A64 = $gen/global_val_26 0
  st var_stk_base.203 0 = lhsaddr.406
  st var_stk_base.203 8 = 6:U64
  lea.stk lhsaddr.407:A64 = msg_eval%185 0
  ld pointer.184:A64 = lhsaddr.407 0
  pusharg 6:U64
  pusharg pointer.184
  pusharg 1:S32
  bsr write
  poparg call.203:S64
  .stk msg_eval%186 8 16
  lea.stk var_stk_base.204:A64 msg_eval%186 0
  lea.mem lhsaddr.408:A64 = $gen/global_val_14 0
  st var_stk_base.204 0 = lhsaddr.408
  st var_stk_base.204 8 = 4:U64
  lea.stk lhsaddr.409:A64 = msg_eval%186 0
  ld pointer.185:A64 = lhsaddr.409 0
  pusharg 4:U64
  pusharg pointer.185
  pusharg 1:S32
  bsr write
  poparg call.204:S64
  .stk msg_eval%187 8 16
  lea.stk var_stk_base.205:A64 msg_eval%187 0
  lea.mem lhsaddr.410:A64 = $gen/global_val_15 0
  st var_stk_base.205 0 = lhsaddr.410
  st var_stk_base.205 8 = 8:U64
  lea.stk lhsaddr.411:A64 = msg_eval%187 0
  ld pointer.186:A64 = lhsaddr.411 0
  pusharg 8:U64
  pusharg pointer.186
  pusharg 1:S32
  bsr write
  poparg call.205:S64
  .stk msg_eval%188 8 16
  lea.stk var_stk_base.206:A64 msg_eval%188 0
  lea.mem lhsaddr.412:A64 = $gen/global_val_16 0
  st var_stk_base.206 0 = lhsaddr.412
  st var_stk_base.206 8 = 4:U64
  lea.stk lhsaddr.413:A64 = msg_eval%188 0
  ld pointer.187:A64 = lhsaddr.413 0
  pusharg 4:U64
  pusharg pointer.187
  pusharg 1:S32
  bsr write
  poparg call.206:S64
  .stk msg_eval%189 8 16
  lea.stk var_stk_base.207:A64 msg_eval%189 0
  lea.mem lhsaddr.414:A64 = $gen/global_val_106 0
  st var_stk_base.207 0 = lhsaddr.414
  st var_stk_base.207 8 = 54:U64
  lea.stk lhsaddr.415:A64 = msg_eval%189 0
  ld pointer.188:A64 = lhsaddr.415 0
  pusharg 54:U64
  pusharg pointer.188
  pusharg 1:S32
  bsr write
  poparg call.207:S64
  .stk msg_eval%190 8 16
  lea.stk var_stk_base.208:A64 msg_eval%190 0
  lea.mem lhsaddr.416:A64 = $gen/global_val_17 0
  st var_stk_base.208 0 = lhsaddr.416
  st var_stk_base.208 8 = 1:U64
  lea.stk lhsaddr.417:A64 = msg_eval%190 0
  ld pointer.189:A64 = lhsaddr.417 0
  pusharg 1:U64
  pusharg pointer.189
  pusharg 1:S32
  bsr write
  poparg call.208:S64
  trap
.bbl br_join.18
  .reg R64 expr.19
  .stk arg0.19 8 16
  lea.stk var_stk_base.209:A64 arg0.19 0
  lea.mem lhsaddr.418:A64 = $gen/global_val_107 0
  st var_stk_base.209 0 = lhsaddr.418
  st var_stk_base.209 8 = 10:U64
  lea.stk lhsaddr.419:A64 = arg0.19 0
  pusharg lhsaddr.419
  bsr parse_real_test/parse_r64
  poparg call.209:R64
  mov expr.19 = call.209
  bra end_expr.19
.bbl end_expr.19
  mov a_val%39:R64 = expr.19
  bitcast bitcast.19:U64 = a_val%39
  beq 9227875636482146304:U64 bitcast.19 br_join.19
  .stk msg_eval%191 8 16
  lea.stk var_stk_base.210:A64 msg_eval%191 0
  lea.mem lhsaddr.420:A64 = $gen/global_val_9 0
  st var_stk_base.210 0 = lhsaddr.420
  st var_stk_base.210 8 = 11:U64
  lea.stk lhsaddr.421:A64 = msg_eval%191 0
  ld pointer.190:A64 = lhsaddr.421 0
  pusharg 11:U64
  pusharg pointer.190
  pusharg 1:S32
  bsr write
  poparg call.210:S64
  .stk msg_eval%192 8 16
  lea.stk var_stk_base.211:A64 msg_eval%192 0
  lea.mem lhsaddr.422:A64 = $gen/global_val_10 0
  st var_stk_base.211 0 = lhsaddr.422
  st var_stk_base.211 8 = 11:U64
  lea.stk lhsaddr.423:A64 = msg_eval%192 0
  ld pointer.191:A64 = lhsaddr.423 0
  pusharg 11:U64
  pusharg pointer.191
  pusharg 1:S32
  bsr write
  poparg call.211:S64
  .stk msg_eval%193 8 16
  lea.stk var_stk_base.212:A64 msg_eval%193 0
  lea.mem lhsaddr.424:A64 = $gen/global_val_108 0
  st var_stk_base.212 0 = lhsaddr.424
  st var_stk_base.212 8 = 54:U64
  lea.stk lhsaddr.425:A64 = msg_eval%193 0
  ld pointer.192:A64 = lhsaddr.425 0
  pusharg 54:U64
  pusharg pointer.192
  pusharg 1:S32
  bsr write
  poparg call.212:S64
  .stk msg_eval%194 8 16
  lea.stk var_stk_base.213:A64 msg_eval%194 0
  lea.mem lhsaddr.426:A64 = $gen/global_val_12 0
  st var_stk_base.213 0 = lhsaddr.426
  st var_stk_base.213 8 = 2:U64
  lea.stk lhsaddr.427:A64 = msg_eval%194 0
  ld pointer.193:A64 = lhsaddr.427 0
  pusharg 2:U64
  pusharg pointer.193
  pusharg 1:S32
  bsr write
  poparg call.213:S64
  .stk msg_eval%195 8 16
  lea.stk var_stk_base.214:A64 msg_eval%195 0
  lea.mem lhsaddr.428:A64 = $gen/global_val_13 0
  st var_stk_base.214 0 = lhsaddr.428
  st var_stk_base.214 8 = 2:U64
  lea.stk lhsaddr.429:A64 = msg_eval%195 0
  ld pointer.194:A64 = lhsaddr.429 0
  pusharg 2:U64
  pusharg pointer.194
  pusharg 1:S32
  bsr write
  poparg call.214:S64
  .stk msg_eval%196 8 16
  lea.stk var_stk_base.215:A64 msg_eval%196 0
  lea.mem lhsaddr.430:A64 = $gen/global_val_14 0
  st var_stk_base.215 0 = lhsaddr.430
  st var_stk_base.215 8 = 4:U64
  lea.stk lhsaddr.431:A64 = msg_eval%196 0
  ld pointer.195:A64 = lhsaddr.431 0
  pusharg 4:U64
  pusharg pointer.195
  pusharg 1:S32
  bsr write
  poparg call.215:S64
  .stk msg_eval%197 8 16
  lea.stk var_stk_base.216:A64 msg_eval%197 0
  lea.mem lhsaddr.432:A64 = $gen/global_val_15 0
  st var_stk_base.216 0 = lhsaddr.432
  st var_stk_base.216 8 = 8:U64
  lea.stk lhsaddr.433:A64 = msg_eval%197 0
  ld pointer.196:A64 = lhsaddr.433 0
  pusharg 8:U64
  pusharg pointer.196
  pusharg 1:S32
  bsr write
  poparg call.216:S64
  .stk msg_eval%198 8 16
  lea.stk var_stk_base.217:A64 msg_eval%198 0
  lea.mem lhsaddr.434:A64 = $gen/global_val_16 0
  st var_stk_base.217 0 = lhsaddr.434
  st var_stk_base.217 8 = 4:U64
  lea.stk lhsaddr.435:A64 = msg_eval%198 0
  ld pointer.197:A64 = lhsaddr.435 0
  pusharg 4:U64
  pusharg pointer.197
  pusharg 1:S32
  bsr write
  poparg call.217:S64
  .stk msg_eval%199 8 16
  lea.stk var_stk_base.218:A64 msg_eval%199 0
  lea.mem lhsaddr.436:A64 = $gen/global_val_108 0
  st var_stk_base.218 0 = lhsaddr.436
  st var_stk_base.218 8 = 54:U64
  lea.stk lhsaddr.437:A64 = msg_eval%199 0
  ld pointer.198:A64 = lhsaddr.437 0
  pusharg 54:U64
  pusharg pointer.198
  pusharg 1:S32
  bsr write
  poparg call.218:S64
  .stk msg_eval%200 8 16
  lea.stk var_stk_base.219:A64 msg_eval%200 0
  lea.mem lhsaddr.438:A64 = $gen/global_val_17 0
  st var_stk_base.219 0 = lhsaddr.438
  st var_stk_base.219 8 = 1:U64
  lea.stk lhsaddr.439:A64 = msg_eval%200 0
  ld pointer.199:A64 = lhsaddr.439 0
  pusharg 1:U64
  pusharg pointer.199
  pusharg 1:S32
  bsr write
  poparg call.219:S64
  trap
.bbl br_join.19
  .reg R64 expr.20
  .stk arg0.20 8 16
  lea.stk var_stk_base.220:A64 arg0.20 0
  lea.mem lhsaddr.440:A64 = $gen/global_val_109 0
  st var_stk_base.220 0 = lhsaddr.440
  st var_stk_base.220 8 = 9:U64
  lea.stk lhsaddr.441:A64 = arg0.20 0
  pusharg lhsaddr.441
  bsr parse_real_test/parse_r64
  poparg call.220:R64
  mov expr.20 = call.220
  bra end_expr.20
.bbl end_expr.20
  mov a_val%41:R64 = expr.20
  bitcast bitcast.20:U64 = a_val%41
  beq 13803532857890570240:U64 bitcast.20 br_join.20
  .stk msg_eval%201 8 16
  lea.stk var_stk_base.221:A64 msg_eval%201 0
  lea.mem lhsaddr.442:A64 = $gen/global_val_9 0
  st var_stk_base.221 0 = lhsaddr.442
  st var_stk_base.221 8 = 11:U64
  lea.stk lhsaddr.443:A64 = msg_eval%201 0
  ld pointer.200:A64 = lhsaddr.443 0
  pusharg 11:U64
  pusharg pointer.200
  pusharg 1:S32
  bsr write
  poparg call.221:S64
  .stk msg_eval%202 8 16
  lea.stk var_stk_base.222:A64 msg_eval%202 0
  lea.mem lhsaddr.444:A64 = $gen/global_val_10 0
  st var_stk_base.222 0 = lhsaddr.444
  st var_stk_base.222 8 = 11:U64
  lea.stk lhsaddr.445:A64 = msg_eval%202 0
  ld pointer.201:A64 = lhsaddr.445 0
  pusharg 11:U64
  pusharg pointer.201
  pusharg 1:S32
  bsr write
  poparg call.222:S64
  .stk msg_eval%203 8 16
  lea.stk var_stk_base.223:A64 msg_eval%203 0
  lea.mem lhsaddr.446:A64 = $gen/global_val_110 0
  st var_stk_base.223 0 = lhsaddr.446
  st var_stk_base.223 8 = 54:U64
  lea.stk lhsaddr.447:A64 = msg_eval%203 0
  ld pointer.202:A64 = lhsaddr.447 0
  pusharg 54:U64
  pusharg pointer.202
  pusharg 1:S32
  bsr write
  poparg call.223:S64
  .stk msg_eval%204 8 16
  lea.stk var_stk_base.224:A64 msg_eval%204 0
  lea.mem lhsaddr.448:A64 = $gen/global_val_12 0
  st var_stk_base.224 0 = lhsaddr.448
  st var_stk_base.224 8 = 2:U64
  lea.stk lhsaddr.449:A64 = msg_eval%204 0
  ld pointer.203:A64 = lhsaddr.449 0
  pusharg 2:U64
  pusharg pointer.203
  pusharg 1:S32
  bsr write
  poparg call.224:S64
  .stk msg_eval%205 8 16
  lea.stk var_stk_base.225:A64 msg_eval%205 0
  lea.mem lhsaddr.450:A64 = $gen/global_val_26 0
  st var_stk_base.225 0 = lhsaddr.450
  st var_stk_base.225 8 = 6:U64
  lea.stk lhsaddr.451:A64 = msg_eval%205 0
  ld pointer.204:A64 = lhsaddr.451 0
  pusharg 6:U64
  pusharg pointer.204
  pusharg 1:S32
  bsr write
  poparg call.225:S64
  .stk msg_eval%206 8 16
  lea.stk var_stk_base.226:A64 msg_eval%206 0
  lea.mem lhsaddr.452:A64 = $gen/global_val_14 0
  st var_stk_base.226 0 = lhsaddr.452
  st var_stk_base.226 8 = 4:U64
  lea.stk lhsaddr.453:A64 = msg_eval%206 0
  ld pointer.205:A64 = lhsaddr.453 0
  pusharg 4:U64
  pusharg pointer.205
  pusharg 1:S32
  bsr write
  poparg call.226:S64
  .stk msg_eval%207 8 16
  lea.stk var_stk_base.227:A64 msg_eval%207 0
  lea.mem lhsaddr.454:A64 = $gen/global_val_15 0
  st var_stk_base.227 0 = lhsaddr.454
  st var_stk_base.227 8 = 8:U64
  lea.stk lhsaddr.455:A64 = msg_eval%207 0
  ld pointer.206:A64 = lhsaddr.455 0
  pusharg 8:U64
  pusharg pointer.206
  pusharg 1:S32
  bsr write
  poparg call.227:S64
  .stk msg_eval%208 8 16
  lea.stk var_stk_base.228:A64 msg_eval%208 0
  lea.mem lhsaddr.456:A64 = $gen/global_val_16 0
  st var_stk_base.228 0 = lhsaddr.456
  st var_stk_base.228 8 = 4:U64
  lea.stk lhsaddr.457:A64 = msg_eval%208 0
  ld pointer.207:A64 = lhsaddr.457 0
  pusharg 4:U64
  pusharg pointer.207
  pusharg 1:S32
  bsr write
  poparg call.228:S64
  .stk msg_eval%209 8 16
  lea.stk var_stk_base.229:A64 msg_eval%209 0
  lea.mem lhsaddr.458:A64 = $gen/global_val_110 0
  st var_stk_base.229 0 = lhsaddr.458
  st var_stk_base.229 8 = 54:U64
  lea.stk lhsaddr.459:A64 = msg_eval%209 0
  ld pointer.208:A64 = lhsaddr.459 0
  pusharg 54:U64
  pusharg pointer.208
  pusharg 1:S32
  bsr write
  poparg call.229:S64
  .stk msg_eval%210 8 16
  lea.stk var_stk_base.230:A64 msg_eval%210 0
  lea.mem lhsaddr.460:A64 = $gen/global_val_17 0
  st var_stk_base.230 0 = lhsaddr.460
  st var_stk_base.230 8 = 1:U64
  lea.stk lhsaddr.461:A64 = msg_eval%210 0
  ld pointer.209:A64 = lhsaddr.461 0
  pusharg 1:U64
  pusharg pointer.209
  pusharg 1:S32
  bsr write
  poparg call.230:S64
  trap
.bbl br_join.20
  .reg R64 expr.21
  .stk arg0.21 8 16
  lea.stk var_stk_base.231:A64 arg0.21 0
  lea.mem lhsaddr.462:A64 = $gen/global_val_111 0
  st var_stk_base.231 0 = lhsaddr.462
  st var_stk_base.231 8 = 8:U64
  lea.stk lhsaddr.463:A64 = arg0.21 0
  pusharg lhsaddr.463
  bsr parse_real_test/parse_r64
  poparg call.231:R64
  mov expr.21 = call.231
  bra end_expr.21
.bbl end_expr.21
  mov a_val%43:R64 = expr.21
  bitcast bitcast.21:U64 = a_val%43
  beq 0:U64 bitcast.21 br_join.21
  .stk msg_eval%211 8 16
  lea.stk var_stk_base.232:A64 msg_eval%211 0
  lea.mem lhsaddr.464:A64 = $gen/global_val_9 0
  st var_stk_base.232 0 = lhsaddr.464
  st var_stk_base.232 8 = 11:U64
  lea.stk lhsaddr.465:A64 = msg_eval%211 0
  ld pointer.210:A64 = lhsaddr.465 0
  pusharg 11:U64
  pusharg pointer.210
  pusharg 1:S32
  bsr write
  poparg call.232:S64
  .stk msg_eval%212 8 16
  lea.stk var_stk_base.233:A64 msg_eval%212 0
  lea.mem lhsaddr.466:A64 = $gen/global_val_10 0
  st var_stk_base.233 0 = lhsaddr.466
  st var_stk_base.233 8 = 11:U64
  lea.stk lhsaddr.467:A64 = msg_eval%212 0
  ld pointer.211:A64 = lhsaddr.467 0
  pusharg 11:U64
  pusharg pointer.211
  pusharg 1:S32
  bsr write
  poparg call.233:S64
  .stk msg_eval%213 8 16
  lea.stk var_stk_base.234:A64 msg_eval%213 0
  lea.mem lhsaddr.468:A64 = $gen/global_val_112 0
  st var_stk_base.234 0 = lhsaddr.468
  st var_stk_base.234 8 = 54:U64
  lea.stk lhsaddr.469:A64 = msg_eval%213 0
  ld pointer.212:A64 = lhsaddr.469 0
  pusharg 54:U64
  pusharg pointer.212
  pusharg 1:S32
  bsr write
  poparg call.234:S64
  .stk msg_eval%214 8 16
  lea.stk var_stk_base.235:A64 msg_eval%214 0
  lea.mem lhsaddr.470:A64 = $gen/global_val_12 0
  st var_stk_base.235 0 = lhsaddr.470
  st var_stk_base.235 8 = 2:U64
  lea.stk lhsaddr.471:A64 = msg_eval%214 0
  ld pointer.213:A64 = lhsaddr.471 0
  pusharg 2:U64
  pusharg pointer.213
  pusharg 1:S32
  bsr write
  poparg call.235:S64
  .stk msg_eval%215 8 16
  lea.stk var_stk_base.236:A64 msg_eval%215 0
  lea.mem lhsaddr.472:A64 = $gen/global_val_26 0
  st var_stk_base.236 0 = lhsaddr.472
  st var_stk_base.236 8 = 6:U64
  lea.stk lhsaddr.473:A64 = msg_eval%215 0
  ld pointer.214:A64 = lhsaddr.473 0
  pusharg 6:U64
  pusharg pointer.214
  pusharg 1:S32
  bsr write
  poparg call.236:S64
  .stk msg_eval%216 8 16
  lea.stk var_stk_base.237:A64 msg_eval%216 0
  lea.mem lhsaddr.474:A64 = $gen/global_val_14 0
  st var_stk_base.237 0 = lhsaddr.474
  st var_stk_base.237 8 = 4:U64
  lea.stk lhsaddr.475:A64 = msg_eval%216 0
  ld pointer.215:A64 = lhsaddr.475 0
  pusharg 4:U64
  pusharg pointer.215
  pusharg 1:S32
  bsr write
  poparg call.237:S64
  .stk msg_eval%217 8 16
  lea.stk var_stk_base.238:A64 msg_eval%217 0
  lea.mem lhsaddr.476:A64 = $gen/global_val_15 0
  st var_stk_base.238 0 = lhsaddr.476
  st var_stk_base.238 8 = 8:U64
  lea.stk lhsaddr.477:A64 = msg_eval%217 0
  ld pointer.216:A64 = lhsaddr.477 0
  pusharg 8:U64
  pusharg pointer.216
  pusharg 1:S32
  bsr write
  poparg call.238:S64
  .stk msg_eval%218 8 16
  lea.stk var_stk_base.239:A64 msg_eval%218 0
  lea.mem lhsaddr.478:A64 = $gen/global_val_16 0
  st var_stk_base.239 0 = lhsaddr.478
  st var_stk_base.239 8 = 4:U64
  lea.stk lhsaddr.479:A64 = msg_eval%218 0
  ld pointer.217:A64 = lhsaddr.479 0
  pusharg 4:U64
  pusharg pointer.217
  pusharg 1:S32
  bsr write
  poparg call.239:S64
  .stk msg_eval%219 8 16
  lea.stk var_stk_base.240:A64 msg_eval%219 0
  lea.mem lhsaddr.480:A64 = $gen/global_val_112 0
  st var_stk_base.240 0 = lhsaddr.480
  st var_stk_base.240 8 = 54:U64
  lea.stk lhsaddr.481:A64 = msg_eval%219 0
  ld pointer.218:A64 = lhsaddr.481 0
  pusharg 54:U64
  pusharg pointer.218
  pusharg 1:S32
  bsr write
  poparg call.240:S64
  .stk msg_eval%220 8 16
  lea.stk var_stk_base.241:A64 msg_eval%220 0
  lea.mem lhsaddr.482:A64 = $gen/global_val_17 0
  st var_stk_base.241 0 = lhsaddr.482
  st var_stk_base.241 8 = 1:U64
  lea.stk lhsaddr.483:A64 = msg_eval%220 0
  ld pointer.219:A64 = lhsaddr.483 0
  pusharg 1:U64
  pusharg pointer.219
  pusharg 1:S32
  bsr write
  poparg call.241:S64
  trap
.bbl br_join.21
  .reg R64 expr.22
  .stk arg0.22 8 16
  lea.stk var_stk_base.242:A64 arg0.22 0
  lea.mem lhsaddr.484:A64 = $gen/global_val_113 0
  st var_stk_base.242 0 = lhsaddr.484
  st var_stk_base.242 8 = 11:U64
  lea.stk lhsaddr.485:A64 = arg0.22 0
  pusharg lhsaddr.485
  bsr parse_real_test/parse_r64
  poparg call.242:R64
  mov expr.22 = call.242
  bra end_expr.22
.bbl end_expr.22
  mov a_val%45:R64 = expr.22
  bitcast bitcast.22:U64 = a_val%45
  beq 0:U64 bitcast.22 br_join.22
  .stk msg_eval%221 8 16
  lea.stk var_stk_base.243:A64 msg_eval%221 0
  lea.mem lhsaddr.486:A64 = $gen/global_val_9 0
  st var_stk_base.243 0 = lhsaddr.486
  st var_stk_base.243 8 = 11:U64
  lea.stk lhsaddr.487:A64 = msg_eval%221 0
  ld pointer.220:A64 = lhsaddr.487 0
  pusharg 11:U64
  pusharg pointer.220
  pusharg 1:S32
  bsr write
  poparg call.243:S64
  .stk msg_eval%222 8 16
  lea.stk var_stk_base.244:A64 msg_eval%222 0
  lea.mem lhsaddr.488:A64 = $gen/global_val_10 0
  st var_stk_base.244 0 = lhsaddr.488
  st var_stk_base.244 8 = 11:U64
  lea.stk lhsaddr.489:A64 = msg_eval%222 0
  ld pointer.221:A64 = lhsaddr.489 0
  pusharg 11:U64
  pusharg pointer.221
  pusharg 1:S32
  bsr write
  poparg call.244:S64
  .stk msg_eval%223 8 16
  lea.stk var_stk_base.245:A64 msg_eval%223 0
  lea.mem lhsaddr.490:A64 = $gen/global_val_114 0
  st var_stk_base.245 0 = lhsaddr.490
  st var_stk_base.245 8 = 54:U64
  lea.stk lhsaddr.491:A64 = msg_eval%223 0
  ld pointer.222:A64 = lhsaddr.491 0
  pusharg 54:U64
  pusharg pointer.222
  pusharg 1:S32
  bsr write
  poparg call.245:S64
  .stk msg_eval%224 8 16
  lea.stk var_stk_base.246:A64 msg_eval%224 0
  lea.mem lhsaddr.492:A64 = $gen/global_val_12 0
  st var_stk_base.246 0 = lhsaddr.492
  st var_stk_base.246 8 = 2:U64
  lea.stk lhsaddr.493:A64 = msg_eval%224 0
  ld pointer.223:A64 = lhsaddr.493 0
  pusharg 2:U64
  pusharg pointer.223
  pusharg 1:S32
  bsr write
  poparg call.246:S64
  .stk msg_eval%225 8 16
  lea.stk var_stk_base.247:A64 msg_eval%225 0
  lea.mem lhsaddr.494:A64 = $gen/global_val_26 0
  st var_stk_base.247 0 = lhsaddr.494
  st var_stk_base.247 8 = 6:U64
  lea.stk lhsaddr.495:A64 = msg_eval%225 0
  ld pointer.224:A64 = lhsaddr.495 0
  pusharg 6:U64
  pusharg pointer.224
  pusharg 1:S32
  bsr write
  poparg call.247:S64
  .stk msg_eval%226 8 16
  lea.stk var_stk_base.248:A64 msg_eval%226 0
  lea.mem lhsaddr.496:A64 = $gen/global_val_14 0
  st var_stk_base.248 0 = lhsaddr.496
  st var_stk_base.248 8 = 4:U64
  lea.stk lhsaddr.497:A64 = msg_eval%226 0
  ld pointer.225:A64 = lhsaddr.497 0
  pusharg 4:U64
  pusharg pointer.225
  pusharg 1:S32
  bsr write
  poparg call.248:S64
  .stk msg_eval%227 8 16
  lea.stk var_stk_base.249:A64 msg_eval%227 0
  lea.mem lhsaddr.498:A64 = $gen/global_val_15 0
  st var_stk_base.249 0 = lhsaddr.498
  st var_stk_base.249 8 = 8:U64
  lea.stk lhsaddr.499:A64 = msg_eval%227 0
  ld pointer.226:A64 = lhsaddr.499 0
  pusharg 8:U64
  pusharg pointer.226
  pusharg 1:S32
  bsr write
  poparg call.249:S64
  .stk msg_eval%228 8 16
  lea.stk var_stk_base.250:A64 msg_eval%228 0
  lea.mem lhsaddr.500:A64 = $gen/global_val_16 0
  st var_stk_base.250 0 = lhsaddr.500
  st var_stk_base.250 8 = 4:U64
  lea.stk lhsaddr.501:A64 = msg_eval%228 0
  ld pointer.227:A64 = lhsaddr.501 0
  pusharg 4:U64
  pusharg pointer.227
  pusharg 1:S32
  bsr write
  poparg call.250:S64
  .stk msg_eval%229 8 16
  lea.stk var_stk_base.251:A64 msg_eval%229 0
  lea.mem lhsaddr.502:A64 = $gen/global_val_114 0
  st var_stk_base.251 0 = lhsaddr.502
  st var_stk_base.251 8 = 54:U64
  lea.stk lhsaddr.503:A64 = msg_eval%229 0
  ld pointer.228:A64 = lhsaddr.503 0
  pusharg 54:U64
  pusharg pointer.228
  pusharg 1:S32
  bsr write
  poparg call.251:S64
  .stk msg_eval%230 8 16
  lea.stk var_stk_base.252:A64 msg_eval%230 0
  lea.mem lhsaddr.504:A64 = $gen/global_val_17 0
  st var_stk_base.252 0 = lhsaddr.504
  st var_stk_base.252 8 = 1:U64
  lea.stk lhsaddr.505:A64 = msg_eval%230 0
  ld pointer.229:A64 = lhsaddr.505 0
  pusharg 1:U64
  pusharg pointer.229
  pusharg 1:S32
  bsr write
  poparg call.252:S64
  trap
.bbl br_join.22
  .reg R64 expr.23
  .stk arg0.23 8 16
  lea.stk var_stk_base.253:A64 arg0.23 0
  lea.mem lhsaddr.506:A64 = $gen/global_val_115 0
  st var_stk_base.253 0 = lhsaddr.506
  st var_stk_base.253 8 = 7:U64
  lea.stk lhsaddr.507:A64 = arg0.23 0
  pusharg lhsaddr.507
  bsr parse_real_test/parse_r64
  poparg call.253:R64
  mov expr.23 = call.253
  bra end_expr.23
.bbl end_expr.23
  mov a_val%47:R64 = expr.23
  bitcast bitcast.23:U64 = a_val%47
  beq 4607182418800017408:U64 bitcast.23 br_join.23
  .stk msg_eval%231 8 16
  lea.stk var_stk_base.254:A64 msg_eval%231 0
  lea.mem lhsaddr.508:A64 = $gen/global_val_9 0
  st var_stk_base.254 0 = lhsaddr.508
  st var_stk_base.254 8 = 11:U64
  lea.stk lhsaddr.509:A64 = msg_eval%231 0
  ld pointer.230:A64 = lhsaddr.509 0
  pusharg 11:U64
  pusharg pointer.230
  pusharg 1:S32
  bsr write
  poparg call.254:S64
  .stk msg_eval%232 8 16
  lea.stk var_stk_base.255:A64 msg_eval%232 0
  lea.mem lhsaddr.510:A64 = $gen/global_val_10 0
  st var_stk_base.255 0 = lhsaddr.510
  st var_stk_base.255 8 = 11:U64
  lea.stk lhsaddr.511:A64 = msg_eval%232 0
  ld pointer.231:A64 = lhsaddr.511 0
  pusharg 11:U64
  pusharg pointer.231
  pusharg 1:S32
  bsr write
  poparg call.255:S64
  .stk msg_eval%233 8 16
  lea.stk var_stk_base.256:A64 msg_eval%233 0
  lea.mem lhsaddr.512:A64 = $gen/global_val_116 0
  st var_stk_base.256 0 = lhsaddr.512
  st var_stk_base.256 8 = 54:U64
  lea.stk lhsaddr.513:A64 = msg_eval%233 0
  ld pointer.232:A64 = lhsaddr.513 0
  pusharg 54:U64
  pusharg pointer.232
  pusharg 1:S32
  bsr write
  poparg call.256:S64
  .stk msg_eval%234 8 16
  lea.stk var_stk_base.257:A64 msg_eval%234 0
  lea.mem lhsaddr.514:A64 = $gen/global_val_12 0
  st var_stk_base.257 0 = lhsaddr.514
  st var_stk_base.257 8 = 2:U64
  lea.stk lhsaddr.515:A64 = msg_eval%234 0
  ld pointer.233:A64 = lhsaddr.515 0
  pusharg 2:U64
  pusharg pointer.233
  pusharg 1:S32
  bsr write
  poparg call.257:S64
  .stk msg_eval%235 8 16
  lea.stk var_stk_base.258:A64 msg_eval%235 0
  lea.mem lhsaddr.516:A64 = $gen/global_val_26 0
  st var_stk_base.258 0 = lhsaddr.516
  st var_stk_base.258 8 = 6:U64
  lea.stk lhsaddr.517:A64 = msg_eval%235 0
  ld pointer.234:A64 = lhsaddr.517 0
  pusharg 6:U64
  pusharg pointer.234
  pusharg 1:S32
  bsr write
  poparg call.258:S64
  .stk msg_eval%236 8 16
  lea.stk var_stk_base.259:A64 msg_eval%236 0
  lea.mem lhsaddr.518:A64 = $gen/global_val_14 0
  st var_stk_base.259 0 = lhsaddr.518
  st var_stk_base.259 8 = 4:U64
  lea.stk lhsaddr.519:A64 = msg_eval%236 0
  ld pointer.235:A64 = lhsaddr.519 0
  pusharg 4:U64
  pusharg pointer.235
  pusharg 1:S32
  bsr write
  poparg call.259:S64
  .stk msg_eval%237 8 16
  lea.stk var_stk_base.260:A64 msg_eval%237 0
  lea.mem lhsaddr.520:A64 = $gen/global_val_15 0
  st var_stk_base.260 0 = lhsaddr.520
  st var_stk_base.260 8 = 8:U64
  lea.stk lhsaddr.521:A64 = msg_eval%237 0
  ld pointer.236:A64 = lhsaddr.521 0
  pusharg 8:U64
  pusharg pointer.236
  pusharg 1:S32
  bsr write
  poparg call.260:S64
  .stk msg_eval%238 8 16
  lea.stk var_stk_base.261:A64 msg_eval%238 0
  lea.mem lhsaddr.522:A64 = $gen/global_val_16 0
  st var_stk_base.261 0 = lhsaddr.522
  st var_stk_base.261 8 = 4:U64
  lea.stk lhsaddr.523:A64 = msg_eval%238 0
  ld pointer.237:A64 = lhsaddr.523 0
  pusharg 4:U64
  pusharg pointer.237
  pusharg 1:S32
  bsr write
  poparg call.261:S64
  .stk msg_eval%239 8 16
  lea.stk var_stk_base.262:A64 msg_eval%239 0
  lea.mem lhsaddr.524:A64 = $gen/global_val_116 0
  st var_stk_base.262 0 = lhsaddr.524
  st var_stk_base.262 8 = 54:U64
  lea.stk lhsaddr.525:A64 = msg_eval%239 0
  ld pointer.238:A64 = lhsaddr.525 0
  pusharg 54:U64
  pusharg pointer.238
  pusharg 1:S32
  bsr write
  poparg call.262:S64
  .stk msg_eval%240 8 16
  lea.stk var_stk_base.263:A64 msg_eval%240 0
  lea.mem lhsaddr.526:A64 = $gen/global_val_17 0
  st var_stk_base.263 0 = lhsaddr.526
  st var_stk_base.263 8 = 1:U64
  lea.stk lhsaddr.527:A64 = msg_eval%240 0
  ld pointer.239:A64 = lhsaddr.527 0
  pusharg 1:U64
  pusharg pointer.239
  pusharg 1:S32
  bsr write
  poparg call.263:S64
  trap
.bbl br_join.23
  .reg R64 expr.24
  .stk arg0.24 8 16
  lea.stk var_stk_base.264:A64 arg0.24 0
  lea.mem lhsaddr.528:A64 = $gen/global_val_117 0
  st var_stk_base.264 0 = lhsaddr.528
  st var_stk_base.264 8 = 6:U64
  lea.stk lhsaddr.529:A64 = arg0.24 0
  pusharg lhsaddr.529
  bsr parse_real_test/parse_r64
  poparg call.264:R64
  mov expr.24 = call.264
  bra end_expr.24
.bbl end_expr.24
  mov a_val%49:R64 = expr.24
  bitcast bitcast.24:U64 = a_val%49
  beq 4625196817309499392:U64 bitcast.24 br_join.24
  .stk msg_eval%241 8 16
  lea.stk var_stk_base.265:A64 msg_eval%241 0
  lea.mem lhsaddr.530:A64 = $gen/global_val_9 0
  st var_stk_base.265 0 = lhsaddr.530
  st var_stk_base.265 8 = 11:U64
  lea.stk lhsaddr.531:A64 = msg_eval%241 0
  ld pointer.240:A64 = lhsaddr.531 0
  pusharg 11:U64
  pusharg pointer.240
  pusharg 1:S32
  bsr write
  poparg call.265:S64
  .stk msg_eval%242 8 16
  lea.stk var_stk_base.266:A64 msg_eval%242 0
  lea.mem lhsaddr.532:A64 = $gen/global_val_10 0
  st var_stk_base.266 0 = lhsaddr.532
  st var_stk_base.266 8 = 11:U64
  lea.stk lhsaddr.533:A64 = msg_eval%242 0
  ld pointer.241:A64 = lhsaddr.533 0
  pusharg 11:U64
  pusharg pointer.241
  pusharg 1:S32
  bsr write
  poparg call.266:S64
  .stk msg_eval%243 8 16
  lea.stk var_stk_base.267:A64 msg_eval%243 0
  lea.mem lhsaddr.534:A64 = $gen/global_val_118 0
  st var_stk_base.267 0 = lhsaddr.534
  st var_stk_base.267 8 = 54:U64
  lea.stk lhsaddr.535:A64 = msg_eval%243 0
  ld pointer.242:A64 = lhsaddr.535 0
  pusharg 54:U64
  pusharg pointer.242
  pusharg 1:S32
  bsr write
  poparg call.267:S64
  .stk msg_eval%244 8 16
  lea.stk var_stk_base.268:A64 msg_eval%244 0
  lea.mem lhsaddr.536:A64 = $gen/global_val_12 0
  st var_stk_base.268 0 = lhsaddr.536
  st var_stk_base.268 8 = 2:U64
  lea.stk lhsaddr.537:A64 = msg_eval%244 0
  ld pointer.243:A64 = lhsaddr.537 0
  pusharg 2:U64
  pusharg pointer.243
  pusharg 1:S32
  bsr write
  poparg call.268:S64
  .stk msg_eval%245 8 16
  lea.stk var_stk_base.269:A64 msg_eval%245 0
  lea.mem lhsaddr.538:A64 = $gen/global_val_26 0
  st var_stk_base.269 0 = lhsaddr.538
  st var_stk_base.269 8 = 6:U64
  lea.stk lhsaddr.539:A64 = msg_eval%245 0
  ld pointer.244:A64 = lhsaddr.539 0
  pusharg 6:U64
  pusharg pointer.244
  pusharg 1:S32
  bsr write
  poparg call.269:S64
  .stk msg_eval%246 8 16
  lea.stk var_stk_base.270:A64 msg_eval%246 0
  lea.mem lhsaddr.540:A64 = $gen/global_val_14 0
  st var_stk_base.270 0 = lhsaddr.540
  st var_stk_base.270 8 = 4:U64
  lea.stk lhsaddr.541:A64 = msg_eval%246 0
  ld pointer.245:A64 = lhsaddr.541 0
  pusharg 4:U64
  pusharg pointer.245
  pusharg 1:S32
  bsr write
  poparg call.270:S64
  .stk msg_eval%247 8 16
  lea.stk var_stk_base.271:A64 msg_eval%247 0
  lea.mem lhsaddr.542:A64 = $gen/global_val_15 0
  st var_stk_base.271 0 = lhsaddr.542
  st var_stk_base.271 8 = 8:U64
  lea.stk lhsaddr.543:A64 = msg_eval%247 0
  ld pointer.246:A64 = lhsaddr.543 0
  pusharg 8:U64
  pusharg pointer.246
  pusharg 1:S32
  bsr write
  poparg call.271:S64
  .stk msg_eval%248 8 16
  lea.stk var_stk_base.272:A64 msg_eval%248 0
  lea.mem lhsaddr.544:A64 = $gen/global_val_16 0
  st var_stk_base.272 0 = lhsaddr.544
  st var_stk_base.272 8 = 4:U64
  lea.stk lhsaddr.545:A64 = msg_eval%248 0
  ld pointer.247:A64 = lhsaddr.545 0
  pusharg 4:U64
  pusharg pointer.247
  pusharg 1:S32
  bsr write
  poparg call.272:S64
  .stk msg_eval%249 8 16
  lea.stk var_stk_base.273:A64 msg_eval%249 0
  lea.mem lhsaddr.546:A64 = $gen/global_val_118 0
  st var_stk_base.273 0 = lhsaddr.546
  st var_stk_base.273 8 = 54:U64
  lea.stk lhsaddr.547:A64 = msg_eval%249 0
  ld pointer.248:A64 = lhsaddr.547 0
  pusharg 54:U64
  pusharg pointer.248
  pusharg 1:S32
  bsr write
  poparg call.273:S64
  .stk msg_eval%250 8 16
  lea.stk var_stk_base.274:A64 msg_eval%250 0
  lea.mem lhsaddr.548:A64 = $gen/global_val_17 0
  st var_stk_base.274 0 = lhsaddr.548
  st var_stk_base.274 8 = 1:U64
  lea.stk lhsaddr.549:A64 = msg_eval%250 0
  ld pointer.249:A64 = lhsaddr.549 0
  pusharg 1:U64
  pusharg pointer.249
  pusharg 1:S32
  bsr write
  poparg call.274:S64
  trap
.bbl br_join.24
  .reg R64 expr.25
  .stk arg0.25 8 16
  lea.stk var_stk_base.275:A64 arg0.25 0
  lea.mem lhsaddr.550:A64 = $gen/global_val_119 0
  st var_stk_base.275 0 = lhsaddr.550
  st var_stk_base.275 8 = 8:U64
  lea.stk lhsaddr.551:A64 = arg0.25 0
  pusharg lhsaddr.551
  bsr parse_real_test/parse_r64
  poparg call.275:R64
  mov expr.25 = call.275
  bra end_expr.25
.bbl end_expr.25
  mov a_val%51:R64 = expr.25
  bitcast bitcast.25:U64 = a_val%51
  beq 4625196817309499392:U64 bitcast.25 br_join.25
  .stk msg_eval%251 8 16
  lea.stk var_stk_base.276:A64 msg_eval%251 0
  lea.mem lhsaddr.552:A64 = $gen/global_val_9 0
  st var_stk_base.276 0 = lhsaddr.552
  st var_stk_base.276 8 = 11:U64
  lea.stk lhsaddr.553:A64 = msg_eval%251 0
  ld pointer.250:A64 = lhsaddr.553 0
  pusharg 11:U64
  pusharg pointer.250
  pusharg 1:S32
  bsr write
  poparg call.276:S64
  .stk msg_eval%252 8 16
  lea.stk var_stk_base.277:A64 msg_eval%252 0
  lea.mem lhsaddr.554:A64 = $gen/global_val_10 0
  st var_stk_base.277 0 = lhsaddr.554
  st var_stk_base.277 8 = 11:U64
  lea.stk lhsaddr.555:A64 = msg_eval%252 0
  ld pointer.251:A64 = lhsaddr.555 0
  pusharg 11:U64
  pusharg pointer.251
  pusharg 1:S32
  bsr write
  poparg call.277:S64
  .stk msg_eval%253 8 16
  lea.stk var_stk_base.278:A64 msg_eval%253 0
  lea.mem lhsaddr.556:A64 = $gen/global_val_120 0
  st var_stk_base.278 0 = lhsaddr.556
  st var_stk_base.278 8 = 55:U64
  lea.stk lhsaddr.557:A64 = msg_eval%253 0
  ld pointer.252:A64 = lhsaddr.557 0
  pusharg 55:U64
  pusharg pointer.252
  pusharg 1:S32
  bsr write
  poparg call.278:S64
  .stk msg_eval%254 8 16
  lea.stk var_stk_base.279:A64 msg_eval%254 0
  lea.mem lhsaddr.558:A64 = $gen/global_val_12 0
  st var_stk_base.279 0 = lhsaddr.558
  st var_stk_base.279 8 = 2:U64
  lea.stk lhsaddr.559:A64 = msg_eval%254 0
  ld pointer.253:A64 = lhsaddr.559 0
  pusharg 2:U64
  pusharg pointer.253
  pusharg 1:S32
  bsr write
  poparg call.279:S64
  .stk msg_eval%255 8 16
  lea.stk var_stk_base.280:A64 msg_eval%255 0
  lea.mem lhsaddr.560:A64 = $gen/global_val_26 0
  st var_stk_base.280 0 = lhsaddr.560
  st var_stk_base.280 8 = 6:U64
  lea.stk lhsaddr.561:A64 = msg_eval%255 0
  ld pointer.254:A64 = lhsaddr.561 0
  pusharg 6:U64
  pusharg pointer.254
  pusharg 1:S32
  bsr write
  poparg call.280:S64
  .stk msg_eval%256 8 16
  lea.stk var_stk_base.281:A64 msg_eval%256 0
  lea.mem lhsaddr.562:A64 = $gen/global_val_14 0
  st var_stk_base.281 0 = lhsaddr.562
  st var_stk_base.281 8 = 4:U64
  lea.stk lhsaddr.563:A64 = msg_eval%256 0
  ld pointer.255:A64 = lhsaddr.563 0
  pusharg 4:U64
  pusharg pointer.255
  pusharg 1:S32
  bsr write
  poparg call.281:S64
  .stk msg_eval%257 8 16
  lea.stk var_stk_base.282:A64 msg_eval%257 0
  lea.mem lhsaddr.564:A64 = $gen/global_val_15 0
  st var_stk_base.282 0 = lhsaddr.564
  st var_stk_base.282 8 = 8:U64
  lea.stk lhsaddr.565:A64 = msg_eval%257 0
  ld pointer.256:A64 = lhsaddr.565 0
  pusharg 8:U64
  pusharg pointer.256
  pusharg 1:S32
  bsr write
  poparg call.282:S64
  .stk msg_eval%258 8 16
  lea.stk var_stk_base.283:A64 msg_eval%258 0
  lea.mem lhsaddr.566:A64 = $gen/global_val_16 0
  st var_stk_base.283 0 = lhsaddr.566
  st var_stk_base.283 8 = 4:U64
  lea.stk lhsaddr.567:A64 = msg_eval%258 0
  ld pointer.257:A64 = lhsaddr.567 0
  pusharg 4:U64
  pusharg pointer.257
  pusharg 1:S32
  bsr write
  poparg call.283:S64
  .stk msg_eval%259 8 16
  lea.stk var_stk_base.284:A64 msg_eval%259 0
  lea.mem lhsaddr.568:A64 = $gen/global_val_120 0
  st var_stk_base.284 0 = lhsaddr.568
  st var_stk_base.284 8 = 55:U64
  lea.stk lhsaddr.569:A64 = msg_eval%259 0
  ld pointer.258:A64 = lhsaddr.569 0
  pusharg 55:U64
  pusharg pointer.258
  pusharg 1:S32
  bsr write
  poparg call.284:S64
  .stk msg_eval%260 8 16
  lea.stk var_stk_base.285:A64 msg_eval%260 0
  lea.mem lhsaddr.570:A64 = $gen/global_val_17 0
  st var_stk_base.285 0 = lhsaddr.570
  st var_stk_base.285 8 = 1:U64
  lea.stk lhsaddr.571:A64 = msg_eval%260 0
  ld pointer.259:A64 = lhsaddr.571 0
  pusharg 1:U64
  pusharg pointer.259
  pusharg 1:S32
  bsr write
  poparg call.285:S64
  trap
.bbl br_join.25
  .reg R64 expr.26
  .stk arg0.26 8 16
  lea.stk var_stk_base.286:A64 arg0.26 0
  lea.mem lhsaddr.572:A64 = $gen/global_val_121 0
  st var_stk_base.286 0 = lhsaddr.572
  st var_stk_base.286 8 = 7:U64
  lea.stk lhsaddr.573:A64 = arg0.26 0
  pusharg lhsaddr.573
  bsr parse_real_test/parse_r64
  poparg call.286:R64
  mov expr.26 = call.286
  bra end_expr.26
.bbl end_expr.26
  mov a_val%53:R64 = expr.26
  bitcast bitcast.26:U64 = a_val%53
  beq 4607182418800017408:U64 bitcast.26 br_join.26
  .stk msg_eval%261 8 16
  lea.stk var_stk_base.287:A64 msg_eval%261 0
  lea.mem lhsaddr.574:A64 = $gen/global_val_9 0
  st var_stk_base.287 0 = lhsaddr.574
  st var_stk_base.287 8 = 11:U64
  lea.stk lhsaddr.575:A64 = msg_eval%261 0
  ld pointer.260:A64 = lhsaddr.575 0
  pusharg 11:U64
  pusharg pointer.260
  pusharg 1:S32
  bsr write
  poparg call.287:S64
  .stk msg_eval%262 8 16
  lea.stk var_stk_base.288:A64 msg_eval%262 0
  lea.mem lhsaddr.576:A64 = $gen/global_val_10 0
  st var_stk_base.288 0 = lhsaddr.576
  st var_stk_base.288 8 = 11:U64
  lea.stk lhsaddr.577:A64 = msg_eval%262 0
  ld pointer.261:A64 = lhsaddr.577 0
  pusharg 11:U64
  pusharg pointer.261
  pusharg 1:S32
  bsr write
  poparg call.288:S64
  .stk msg_eval%263 8 16
  lea.stk var_stk_base.289:A64 msg_eval%263 0
  lea.mem lhsaddr.578:A64 = $gen/global_val_122 0
  st var_stk_base.289 0 = lhsaddr.578
  st var_stk_base.289 8 = 55:U64
  lea.stk lhsaddr.579:A64 = msg_eval%263 0
  ld pointer.262:A64 = lhsaddr.579 0
  pusharg 55:U64
  pusharg pointer.262
  pusharg 1:S32
  bsr write
  poparg call.289:S64
  .stk msg_eval%264 8 16
  lea.stk var_stk_base.290:A64 msg_eval%264 0
  lea.mem lhsaddr.580:A64 = $gen/global_val_12 0
  st var_stk_base.290 0 = lhsaddr.580
  st var_stk_base.290 8 = 2:U64
  lea.stk lhsaddr.581:A64 = msg_eval%264 0
  ld pointer.263:A64 = lhsaddr.581 0
  pusharg 2:U64
  pusharg pointer.263
  pusharg 1:S32
  bsr write
  poparg call.290:S64
  .stk msg_eval%265 8 16
  lea.stk var_stk_base.291:A64 msg_eval%265 0
  lea.mem lhsaddr.582:A64 = $gen/global_val_26 0
  st var_stk_base.291 0 = lhsaddr.582
  st var_stk_base.291 8 = 6:U64
  lea.stk lhsaddr.583:A64 = msg_eval%265 0
  ld pointer.264:A64 = lhsaddr.583 0
  pusharg 6:U64
  pusharg pointer.264
  pusharg 1:S32
  bsr write
  poparg call.291:S64
  .stk msg_eval%266 8 16
  lea.stk var_stk_base.292:A64 msg_eval%266 0
  lea.mem lhsaddr.584:A64 = $gen/global_val_14 0
  st var_stk_base.292 0 = lhsaddr.584
  st var_stk_base.292 8 = 4:U64
  lea.stk lhsaddr.585:A64 = msg_eval%266 0
  ld pointer.265:A64 = lhsaddr.585 0
  pusharg 4:U64
  pusharg pointer.265
  pusharg 1:S32
  bsr write
  poparg call.292:S64
  .stk msg_eval%267 8 16
  lea.stk var_stk_base.293:A64 msg_eval%267 0
  lea.mem lhsaddr.586:A64 = $gen/global_val_15 0
  st var_stk_base.293 0 = lhsaddr.586
  st var_stk_base.293 8 = 8:U64
  lea.stk lhsaddr.587:A64 = msg_eval%267 0
  ld pointer.266:A64 = lhsaddr.587 0
  pusharg 8:U64
  pusharg pointer.266
  pusharg 1:S32
  bsr write
  poparg call.293:S64
  .stk msg_eval%268 8 16
  lea.stk var_stk_base.294:A64 msg_eval%268 0
  lea.mem lhsaddr.588:A64 = $gen/global_val_16 0
  st var_stk_base.294 0 = lhsaddr.588
  st var_stk_base.294 8 = 4:U64
  lea.stk lhsaddr.589:A64 = msg_eval%268 0
  ld pointer.267:A64 = lhsaddr.589 0
  pusharg 4:U64
  pusharg pointer.267
  pusharg 1:S32
  bsr write
  poparg call.294:S64
  .stk msg_eval%269 8 16
  lea.stk var_stk_base.295:A64 msg_eval%269 0
  lea.mem lhsaddr.590:A64 = $gen/global_val_122 0
  st var_stk_base.295 0 = lhsaddr.590
  st var_stk_base.295 8 = 55:U64
  lea.stk lhsaddr.591:A64 = msg_eval%269 0
  ld pointer.268:A64 = lhsaddr.591 0
  pusharg 55:U64
  pusharg pointer.268
  pusharg 1:S32
  bsr write
  poparg call.295:S64
  .stk msg_eval%270 8 16
  lea.stk var_stk_base.296:A64 msg_eval%270 0
  lea.mem lhsaddr.592:A64 = $gen/global_val_17 0
  st var_stk_base.296 0 = lhsaddr.592
  st var_stk_base.296 8 = 1:U64
  lea.stk lhsaddr.593:A64 = msg_eval%270 0
  ld pointer.269:A64 = lhsaddr.593 0
  pusharg 1:U64
  pusharg pointer.269
  pusharg 1:S32
  bsr write
  poparg call.296:S64
  trap
.bbl br_join.26
  .reg R64 expr.27
  .stk arg0.27 8 16
  lea.stk var_stk_base.297:A64 arg0.27 0
  lea.mem lhsaddr.594:A64 = $gen/global_val_123 0
  st var_stk_base.297 0 = lhsaddr.594
  st var_stk_base.297 8 = 8:U64
  lea.stk lhsaddr.595:A64 = arg0.27 0
  pusharg lhsaddr.595
  bsr parse_real_test/parse_r64
  poparg call.297:R64
  mov expr.27 = call.297
  bra end_expr.27
.bbl end_expr.27
  mov a_val%55:R64 = expr.27
  bitcast bitcast.27:U64 = a_val%55
  beq 4607182418800017408:U64 bitcast.27 br_join.27
  .stk msg_eval%271 8 16
  lea.stk var_stk_base.298:A64 msg_eval%271 0
  lea.mem lhsaddr.596:A64 = $gen/global_val_9 0
  st var_stk_base.298 0 = lhsaddr.596
  st var_stk_base.298 8 = 11:U64
  lea.stk lhsaddr.597:A64 = msg_eval%271 0
  ld pointer.270:A64 = lhsaddr.597 0
  pusharg 11:U64
  pusharg pointer.270
  pusharg 1:S32
  bsr write
  poparg call.298:S64
  .stk msg_eval%272 8 16
  lea.stk var_stk_base.299:A64 msg_eval%272 0
  lea.mem lhsaddr.598:A64 = $gen/global_val_10 0
  st var_stk_base.299 0 = lhsaddr.598
  st var_stk_base.299 8 = 11:U64
  lea.stk lhsaddr.599:A64 = msg_eval%272 0
  ld pointer.271:A64 = lhsaddr.599 0
  pusharg 11:U64
  pusharg pointer.271
  pusharg 1:S32
  bsr write
  poparg call.299:S64
  .stk msg_eval%273 8 16
  lea.stk var_stk_base.300:A64 msg_eval%273 0
  lea.mem lhsaddr.600:A64 = $gen/global_val_124 0
  st var_stk_base.300 0 = lhsaddr.600
  st var_stk_base.300 8 = 55:U64
  lea.stk lhsaddr.601:A64 = msg_eval%273 0
  ld pointer.272:A64 = lhsaddr.601 0
  pusharg 55:U64
  pusharg pointer.272
  pusharg 1:S32
  bsr write
  poparg call.300:S64
  .stk msg_eval%274 8 16
  lea.stk var_stk_base.301:A64 msg_eval%274 0
  lea.mem lhsaddr.602:A64 = $gen/global_val_12 0
  st var_stk_base.301 0 = lhsaddr.602
  st var_stk_base.301 8 = 2:U64
  lea.stk lhsaddr.603:A64 = msg_eval%274 0
  ld pointer.273:A64 = lhsaddr.603 0
  pusharg 2:U64
  pusharg pointer.273
  pusharg 1:S32
  bsr write
  poparg call.301:S64
  .stk msg_eval%275 8 16
  lea.stk var_stk_base.302:A64 msg_eval%275 0
  lea.mem lhsaddr.604:A64 = $gen/global_val_26 0
  st var_stk_base.302 0 = lhsaddr.604
  st var_stk_base.302 8 = 6:U64
  lea.stk lhsaddr.605:A64 = msg_eval%275 0
  ld pointer.274:A64 = lhsaddr.605 0
  pusharg 6:U64
  pusharg pointer.274
  pusharg 1:S32
  bsr write
  poparg call.302:S64
  .stk msg_eval%276 8 16
  lea.stk var_stk_base.303:A64 msg_eval%276 0
  lea.mem lhsaddr.606:A64 = $gen/global_val_14 0
  st var_stk_base.303 0 = lhsaddr.606
  st var_stk_base.303 8 = 4:U64
  lea.stk lhsaddr.607:A64 = msg_eval%276 0
  ld pointer.275:A64 = lhsaddr.607 0
  pusharg 4:U64
  pusharg pointer.275
  pusharg 1:S32
  bsr write
  poparg call.303:S64
  .stk msg_eval%277 8 16
  lea.stk var_stk_base.304:A64 msg_eval%277 0
  lea.mem lhsaddr.608:A64 = $gen/global_val_15 0
  st var_stk_base.304 0 = lhsaddr.608
  st var_stk_base.304 8 = 8:U64
  lea.stk lhsaddr.609:A64 = msg_eval%277 0
  ld pointer.276:A64 = lhsaddr.609 0
  pusharg 8:U64
  pusharg pointer.276
  pusharg 1:S32
  bsr write
  poparg call.304:S64
  .stk msg_eval%278 8 16
  lea.stk var_stk_base.305:A64 msg_eval%278 0
  lea.mem lhsaddr.610:A64 = $gen/global_val_16 0
  st var_stk_base.305 0 = lhsaddr.610
  st var_stk_base.305 8 = 4:U64
  lea.stk lhsaddr.611:A64 = msg_eval%278 0
  ld pointer.277:A64 = lhsaddr.611 0
  pusharg 4:U64
  pusharg pointer.277
  pusharg 1:S32
  bsr write
  poparg call.305:S64
  .stk msg_eval%279 8 16
  lea.stk var_stk_base.306:A64 msg_eval%279 0
  lea.mem lhsaddr.612:A64 = $gen/global_val_124 0
  st var_stk_base.306 0 = lhsaddr.612
  st var_stk_base.306 8 = 55:U64
  lea.stk lhsaddr.613:A64 = msg_eval%279 0
  ld pointer.278:A64 = lhsaddr.613 0
  pusharg 55:U64
  pusharg pointer.278
  pusharg 1:S32
  bsr write
  poparg call.306:S64
  .stk msg_eval%280 8 16
  lea.stk var_stk_base.307:A64 msg_eval%280 0
  lea.mem lhsaddr.614:A64 = $gen/global_val_17 0
  st var_stk_base.307 0 = lhsaddr.614
  st var_stk_base.307 8 = 1:U64
  lea.stk lhsaddr.615:A64 = msg_eval%280 0
  ld pointer.279:A64 = lhsaddr.615 0
  pusharg 1:U64
  pusharg pointer.279
  pusharg 1:S32
  bsr write
  poparg call.307:S64
  trap
.bbl br_join.27
  .reg R64 expr.28
  .stk arg0.28 8 16
  lea.stk var_stk_base.308:A64 arg0.28 0
  lea.mem lhsaddr.616:A64 = $gen/global_val_125 0
  st var_stk_base.308 0 = lhsaddr.616
  st var_stk_base.308 8 = 11:U64
  lea.stk lhsaddr.617:A64 = arg0.28 0
  pusharg lhsaddr.617
  bsr parse_real_test/parse_r64
  poparg call.308:R64
  mov expr.28 = call.308
  bra end_expr.28
.bbl end_expr.28
  mov a_val%57:R64 = expr.28
  bitcast bitcast.28:U64 = a_val%57
  beq 4607182418800017408:U64 bitcast.28 br_join.28
  .stk msg_eval%281 8 16
  lea.stk var_stk_base.309:A64 msg_eval%281 0
  lea.mem lhsaddr.618:A64 = $gen/global_val_9 0
  st var_stk_base.309 0 = lhsaddr.618
  st var_stk_base.309 8 = 11:U64
  lea.stk lhsaddr.619:A64 = msg_eval%281 0
  ld pointer.280:A64 = lhsaddr.619 0
  pusharg 11:U64
  pusharg pointer.280
  pusharg 1:S32
  bsr write
  poparg call.309:S64
  .stk msg_eval%282 8 16
  lea.stk var_stk_base.310:A64 msg_eval%282 0
  lea.mem lhsaddr.620:A64 = $gen/global_val_10 0
  st var_stk_base.310 0 = lhsaddr.620
  st var_stk_base.310 8 = 11:U64
  lea.stk lhsaddr.621:A64 = msg_eval%282 0
  ld pointer.281:A64 = lhsaddr.621 0
  pusharg 11:U64
  pusharg pointer.281
  pusharg 1:S32
  bsr write
  poparg call.310:S64
  .stk msg_eval%283 8 16
  lea.stk var_stk_base.311:A64 msg_eval%283 0
  lea.mem lhsaddr.622:A64 = $gen/global_val_126 0
  st var_stk_base.311 0 = lhsaddr.622
  st var_stk_base.311 8 = 55:U64
  lea.stk lhsaddr.623:A64 = msg_eval%283 0
  ld pointer.282:A64 = lhsaddr.623 0
  pusharg 55:U64
  pusharg pointer.282
  pusharg 1:S32
  bsr write
  poparg call.311:S64
  .stk msg_eval%284 8 16
  lea.stk var_stk_base.312:A64 msg_eval%284 0
  lea.mem lhsaddr.624:A64 = $gen/global_val_12 0
  st var_stk_base.312 0 = lhsaddr.624
  st var_stk_base.312 8 = 2:U64
  lea.stk lhsaddr.625:A64 = msg_eval%284 0
  ld pointer.283:A64 = lhsaddr.625 0
  pusharg 2:U64
  pusharg pointer.283
  pusharg 1:S32
  bsr write
  poparg call.312:S64
  .stk msg_eval%285 8 16
  lea.stk var_stk_base.313:A64 msg_eval%285 0
  lea.mem lhsaddr.626:A64 = $gen/global_val_26 0
  st var_stk_base.313 0 = lhsaddr.626
  st var_stk_base.313 8 = 6:U64
  lea.stk lhsaddr.627:A64 = msg_eval%285 0
  ld pointer.284:A64 = lhsaddr.627 0
  pusharg 6:U64
  pusharg pointer.284
  pusharg 1:S32
  bsr write
  poparg call.313:S64
  .stk msg_eval%286 8 16
  lea.stk var_stk_base.314:A64 msg_eval%286 0
  lea.mem lhsaddr.628:A64 = $gen/global_val_14 0
  st var_stk_base.314 0 = lhsaddr.628
  st var_stk_base.314 8 = 4:U64
  lea.stk lhsaddr.629:A64 = msg_eval%286 0
  ld pointer.285:A64 = lhsaddr.629 0
  pusharg 4:U64
  pusharg pointer.285
  pusharg 1:S32
  bsr write
  poparg call.314:S64
  .stk msg_eval%287 8 16
  lea.stk var_stk_base.315:A64 msg_eval%287 0
  lea.mem lhsaddr.630:A64 = $gen/global_val_15 0
  st var_stk_base.315 0 = lhsaddr.630
  st var_stk_base.315 8 = 8:U64
  lea.stk lhsaddr.631:A64 = msg_eval%287 0
  ld pointer.286:A64 = lhsaddr.631 0
  pusharg 8:U64
  pusharg pointer.286
  pusharg 1:S32
  bsr write
  poparg call.315:S64
  .stk msg_eval%288 8 16
  lea.stk var_stk_base.316:A64 msg_eval%288 0
  lea.mem lhsaddr.632:A64 = $gen/global_val_16 0
  st var_stk_base.316 0 = lhsaddr.632
  st var_stk_base.316 8 = 4:U64
  lea.stk lhsaddr.633:A64 = msg_eval%288 0
  ld pointer.287:A64 = lhsaddr.633 0
  pusharg 4:U64
  pusharg pointer.287
  pusharg 1:S32
  bsr write
  poparg call.316:S64
  .stk msg_eval%289 8 16
  lea.stk var_stk_base.317:A64 msg_eval%289 0
  lea.mem lhsaddr.634:A64 = $gen/global_val_126 0
  st var_stk_base.317 0 = lhsaddr.634
  st var_stk_base.317 8 = 55:U64
  lea.stk lhsaddr.635:A64 = msg_eval%289 0
  ld pointer.288:A64 = lhsaddr.635 0
  pusharg 55:U64
  pusharg pointer.288
  pusharg 1:S32
  bsr write
  poparg call.317:S64
  .stk msg_eval%290 8 16
  lea.stk var_stk_base.318:A64 msg_eval%290 0
  lea.mem lhsaddr.636:A64 = $gen/global_val_17 0
  st var_stk_base.318 0 = lhsaddr.636
  st var_stk_base.318 8 = 1:U64
  lea.stk lhsaddr.637:A64 = msg_eval%290 0
  ld pointer.289:A64 = lhsaddr.637 0
  pusharg 1:U64
  pusharg pointer.289
  pusharg 1:S32
  bsr write
  poparg call.318:S64
  trap
.bbl br_join.28
  .reg R64 expr.29
  .stk arg0.29 8 16
  lea.stk var_stk_base.319:A64 arg0.29 0
  lea.mem lhsaddr.638:A64 = $gen/global_val_127 0
  st var_stk_base.319 0 = lhsaddr.638
  st var_stk_base.319 8 = 8:U64
  lea.stk lhsaddr.639:A64 = arg0.29 0
  pusharg lhsaddr.639
  bsr parse_real_test/parse_r64
  poparg call.319:R64
  mov expr.29 = call.319
  bra end_expr.29
.bbl end_expr.29
  mov a_val%59:R64 = expr.29
  bitcast bitcast.29:U64 = a_val%59
  beq 4607182418800017408:U64 bitcast.29 br_join.29
  .stk msg_eval%291 8 16
  lea.stk var_stk_base.320:A64 msg_eval%291 0
  lea.mem lhsaddr.640:A64 = $gen/global_val_9 0
  st var_stk_base.320 0 = lhsaddr.640
  st var_stk_base.320 8 = 11:U64
  lea.stk lhsaddr.641:A64 = msg_eval%291 0
  ld pointer.290:A64 = lhsaddr.641 0
  pusharg 11:U64
  pusharg pointer.290
  pusharg 1:S32
  bsr write
  poparg call.320:S64
  .stk msg_eval%292 8 16
  lea.stk var_stk_base.321:A64 msg_eval%292 0
  lea.mem lhsaddr.642:A64 = $gen/global_val_10 0
  st var_stk_base.321 0 = lhsaddr.642
  st var_stk_base.321 8 = 11:U64
  lea.stk lhsaddr.643:A64 = msg_eval%292 0
  ld pointer.291:A64 = lhsaddr.643 0
  pusharg 11:U64
  pusharg pointer.291
  pusharg 1:S32
  bsr write
  poparg call.321:S64
  .stk msg_eval%293 8 16
  lea.stk var_stk_base.322:A64 msg_eval%293 0
  lea.mem lhsaddr.644:A64 = $gen/global_val_128 0
  st var_stk_base.322 0 = lhsaddr.644
  st var_stk_base.322 8 = 55:U64
  lea.stk lhsaddr.645:A64 = msg_eval%293 0
  ld pointer.292:A64 = lhsaddr.645 0
  pusharg 55:U64
  pusharg pointer.292
  pusharg 1:S32
  bsr write
  poparg call.322:S64
  .stk msg_eval%294 8 16
  lea.stk var_stk_base.323:A64 msg_eval%294 0
  lea.mem lhsaddr.646:A64 = $gen/global_val_12 0
  st var_stk_base.323 0 = lhsaddr.646
  st var_stk_base.323 8 = 2:U64
  lea.stk lhsaddr.647:A64 = msg_eval%294 0
  ld pointer.293:A64 = lhsaddr.647 0
  pusharg 2:U64
  pusharg pointer.293
  pusharg 1:S32
  bsr write
  poparg call.323:S64
  .stk msg_eval%295 8 16
  lea.stk var_stk_base.324:A64 msg_eval%295 0
  lea.mem lhsaddr.648:A64 = $gen/global_val_26 0
  st var_stk_base.324 0 = lhsaddr.648
  st var_stk_base.324 8 = 6:U64
  lea.stk lhsaddr.649:A64 = msg_eval%295 0
  ld pointer.294:A64 = lhsaddr.649 0
  pusharg 6:U64
  pusharg pointer.294
  pusharg 1:S32
  bsr write
  poparg call.324:S64
  .stk msg_eval%296 8 16
  lea.stk var_stk_base.325:A64 msg_eval%296 0
  lea.mem lhsaddr.650:A64 = $gen/global_val_14 0
  st var_stk_base.325 0 = lhsaddr.650
  st var_stk_base.325 8 = 4:U64
  lea.stk lhsaddr.651:A64 = msg_eval%296 0
  ld pointer.295:A64 = lhsaddr.651 0
  pusharg 4:U64
  pusharg pointer.295
  pusharg 1:S32
  bsr write
  poparg call.325:S64
  .stk msg_eval%297 8 16
  lea.stk var_stk_base.326:A64 msg_eval%297 0
  lea.mem lhsaddr.652:A64 = $gen/global_val_15 0
  st var_stk_base.326 0 = lhsaddr.652
  st var_stk_base.326 8 = 8:U64
  lea.stk lhsaddr.653:A64 = msg_eval%297 0
  ld pointer.296:A64 = lhsaddr.653 0
  pusharg 8:U64
  pusharg pointer.296
  pusharg 1:S32
  bsr write
  poparg call.326:S64
  .stk msg_eval%298 8 16
  lea.stk var_stk_base.327:A64 msg_eval%298 0
  lea.mem lhsaddr.654:A64 = $gen/global_val_16 0
  st var_stk_base.327 0 = lhsaddr.654
  st var_stk_base.327 8 = 4:U64
  lea.stk lhsaddr.655:A64 = msg_eval%298 0
  ld pointer.297:A64 = lhsaddr.655 0
  pusharg 4:U64
  pusharg pointer.297
  pusharg 1:S32
  bsr write
  poparg call.327:S64
  .stk msg_eval%299 8 16
  lea.stk var_stk_base.328:A64 msg_eval%299 0
  lea.mem lhsaddr.656:A64 = $gen/global_val_128 0
  st var_stk_base.328 0 = lhsaddr.656
  st var_stk_base.328 8 = 55:U64
  lea.stk lhsaddr.657:A64 = msg_eval%299 0
  ld pointer.298:A64 = lhsaddr.657 0
  pusharg 55:U64
  pusharg pointer.298
  pusharg 1:S32
  bsr write
  poparg call.328:S64
  .stk msg_eval%300 8 16
  lea.stk var_stk_base.329:A64 msg_eval%300 0
  lea.mem lhsaddr.658:A64 = $gen/global_val_17 0
  st var_stk_base.329 0 = lhsaddr.658
  st var_stk_base.329 8 = 1:U64
  lea.stk lhsaddr.659:A64 = msg_eval%300 0
  ld pointer.299:A64 = lhsaddr.659 0
  pusharg 1:U64
  pusharg pointer.299
  pusharg 1:S32
  bsr write
  poparg call.329:S64
  trap
.bbl br_join.29
  .reg R64 expr.30
  .stk arg0.30 8 16
  lea.stk var_stk_base.330:A64 arg0.30 0
  lea.mem lhsaddr.660:A64 = $gen/global_val_129 0
  st var_stk_base.330 0 = lhsaddr.660
  st var_stk_base.330 8 = 10:U64
  lea.stk lhsaddr.661:A64 = arg0.30 0
  pusharg lhsaddr.661
  bsr parse_real_test/parse_r64
  poparg call.330:R64
  mov expr.30 = call.330
  bra end_expr.30
.bbl end_expr.30
  mov a_val%61:R64 = expr.30
  bitcast bitcast.30:U64 = a_val%61
  beq 4607182281361063936:U64 bitcast.30 br_join.30
  .stk msg_eval%301 8 16
  lea.stk var_stk_base.331:A64 msg_eval%301 0
  lea.mem lhsaddr.662:A64 = $gen/global_val_9 0
  st var_stk_base.331 0 = lhsaddr.662
  st var_stk_base.331 8 = 11:U64
  lea.stk lhsaddr.663:A64 = msg_eval%301 0
  ld pointer.300:A64 = lhsaddr.663 0
  pusharg 11:U64
  pusharg pointer.300
  pusharg 1:S32
  bsr write
  poparg call.331:S64
  .stk msg_eval%302 8 16
  lea.stk var_stk_base.332:A64 msg_eval%302 0
  lea.mem lhsaddr.664:A64 = $gen/global_val_10 0
  st var_stk_base.332 0 = lhsaddr.664
  st var_stk_base.332 8 = 11:U64
  lea.stk lhsaddr.665:A64 = msg_eval%302 0
  ld pointer.301:A64 = lhsaddr.665 0
  pusharg 11:U64
  pusharg pointer.301
  pusharg 1:S32
  bsr write
  poparg call.332:S64
  .stk msg_eval%303 8 16
  lea.stk var_stk_base.333:A64 msg_eval%303 0
  lea.mem lhsaddr.666:A64 = $gen/global_val_130 0
  st var_stk_base.333 0 = lhsaddr.666
  st var_stk_base.333 8 = 55:U64
  lea.stk lhsaddr.667:A64 = msg_eval%303 0
  ld pointer.302:A64 = lhsaddr.667 0
  pusharg 55:U64
  pusharg pointer.302
  pusharg 1:S32
  bsr write
  poparg call.333:S64
  .stk msg_eval%304 8 16
  lea.stk var_stk_base.334:A64 msg_eval%304 0
  lea.mem lhsaddr.668:A64 = $gen/global_val_12 0
  st var_stk_base.334 0 = lhsaddr.668
  st var_stk_base.334 8 = 2:U64
  lea.stk lhsaddr.669:A64 = msg_eval%304 0
  ld pointer.303:A64 = lhsaddr.669 0
  pusharg 2:U64
  pusharg pointer.303
  pusharg 1:S32
  bsr write
  poparg call.334:S64
  .stk msg_eval%305 8 16
  lea.stk var_stk_base.335:A64 msg_eval%305 0
  lea.mem lhsaddr.670:A64 = $gen/global_val_26 0
  st var_stk_base.335 0 = lhsaddr.670
  st var_stk_base.335 8 = 6:U64
  lea.stk lhsaddr.671:A64 = msg_eval%305 0
  ld pointer.304:A64 = lhsaddr.671 0
  pusharg 6:U64
  pusharg pointer.304
  pusharg 1:S32
  bsr write
  poparg call.335:S64
  .stk msg_eval%306 8 16
  lea.stk var_stk_base.336:A64 msg_eval%306 0
  lea.mem lhsaddr.672:A64 = $gen/global_val_14 0
  st var_stk_base.336 0 = lhsaddr.672
  st var_stk_base.336 8 = 4:U64
  lea.stk lhsaddr.673:A64 = msg_eval%306 0
  ld pointer.305:A64 = lhsaddr.673 0
  pusharg 4:U64
  pusharg pointer.305
  pusharg 1:S32
  bsr write
  poparg call.336:S64
  .stk msg_eval%307 8 16
  lea.stk var_stk_base.337:A64 msg_eval%307 0
  lea.mem lhsaddr.674:A64 = $gen/global_val_15 0
  st var_stk_base.337 0 = lhsaddr.674
  st var_stk_base.337 8 = 8:U64
  lea.stk lhsaddr.675:A64 = msg_eval%307 0
  ld pointer.306:A64 = lhsaddr.675 0
  pusharg 8:U64
  pusharg pointer.306
  pusharg 1:S32
  bsr write
  poparg call.337:S64
  .stk msg_eval%308 8 16
  lea.stk var_stk_base.338:A64 msg_eval%308 0
  lea.mem lhsaddr.676:A64 = $gen/global_val_16 0
  st var_stk_base.338 0 = lhsaddr.676
  st var_stk_base.338 8 = 4:U64
  lea.stk lhsaddr.677:A64 = msg_eval%308 0
  ld pointer.307:A64 = lhsaddr.677 0
  pusharg 4:U64
  pusharg pointer.307
  pusharg 1:S32
  bsr write
  poparg call.338:S64
  .stk msg_eval%309 8 16
  lea.stk var_stk_base.339:A64 msg_eval%309 0
  lea.mem lhsaddr.678:A64 = $gen/global_val_130 0
  st var_stk_base.339 0 = lhsaddr.678
  st var_stk_base.339 8 = 55:U64
  lea.stk lhsaddr.679:A64 = msg_eval%309 0
  ld pointer.308:A64 = lhsaddr.679 0
  pusharg 55:U64
  pusharg pointer.308
  pusharg 1:S32
  bsr write
  poparg call.339:S64
  .stk msg_eval%310 8 16
  lea.stk var_stk_base.340:A64 msg_eval%310 0
  lea.mem lhsaddr.680:A64 = $gen/global_val_17 0
  st var_stk_base.340 0 = lhsaddr.680
  st var_stk_base.340 8 = 1:U64
  lea.stk lhsaddr.681:A64 = msg_eval%310 0
  ld pointer.309:A64 = lhsaddr.681 0
  pusharg 1:U64
  pusharg pointer.309
  pusharg 1:S32
  bsr write
  poparg call.340:S64
  trap
.bbl br_join.30
  .reg R64 expr.31
  .stk arg0.31 8 16
  lea.stk var_stk_base.341:A64 arg0.31 0
  lea.mem lhsaddr.682:A64 = $gen/global_val_131 0
  st var_stk_base.341 0 = lhsaddr.682
  st var_stk_base.341 8 = 14:U64
  lea.stk lhsaddr.683:A64 = arg0.31 0
  pusharg lhsaddr.683
  bsr parse_real_test/parse_r64
  poparg call.341:R64
  mov expr.31 = call.341
  bra end_expr.31
.bbl end_expr.31
  mov a_val%63:R64 = expr.31
  bitcast bitcast.31:U64 = a_val%63
  beq 4607182418797920256:U64 bitcast.31 br_join.31
  .stk msg_eval%311 8 16
  lea.stk var_stk_base.342:A64 msg_eval%311 0
  lea.mem lhsaddr.684:A64 = $gen/global_val_9 0
  st var_stk_base.342 0 = lhsaddr.684
  st var_stk_base.342 8 = 11:U64
  lea.stk lhsaddr.685:A64 = msg_eval%311 0
  ld pointer.310:A64 = lhsaddr.685 0
  pusharg 11:U64
  pusharg pointer.310
  pusharg 1:S32
  bsr write
  poparg call.342:S64
  .stk msg_eval%312 8 16
  lea.stk var_stk_base.343:A64 msg_eval%312 0
  lea.mem lhsaddr.686:A64 = $gen/global_val_10 0
  st var_stk_base.343 0 = lhsaddr.686
  st var_stk_base.343 8 = 11:U64
  lea.stk lhsaddr.687:A64 = msg_eval%312 0
  ld pointer.311:A64 = lhsaddr.687 0
  pusharg 11:U64
  pusharg pointer.311
  pusharg 1:S32
  bsr write
  poparg call.343:S64
  .stk msg_eval%313 8 16
  lea.stk var_stk_base.344:A64 msg_eval%313 0
  lea.mem lhsaddr.688:A64 = $gen/global_val_132 0
  st var_stk_base.344 0 = lhsaddr.688
  st var_stk_base.344 8 = 55:U64
  lea.stk lhsaddr.689:A64 = msg_eval%313 0
  ld pointer.312:A64 = lhsaddr.689 0
  pusharg 55:U64
  pusharg pointer.312
  pusharg 1:S32
  bsr write
  poparg call.344:S64
  .stk msg_eval%314 8 16
  lea.stk var_stk_base.345:A64 msg_eval%314 0
  lea.mem lhsaddr.690:A64 = $gen/global_val_12 0
  st var_stk_base.345 0 = lhsaddr.690
  st var_stk_base.345 8 = 2:U64
  lea.stk lhsaddr.691:A64 = msg_eval%314 0
  ld pointer.313:A64 = lhsaddr.691 0
  pusharg 2:U64
  pusharg pointer.313
  pusharg 1:S32
  bsr write
  poparg call.345:S64
  .stk msg_eval%315 8 16
  lea.stk var_stk_base.346:A64 msg_eval%315 0
  lea.mem lhsaddr.692:A64 = $gen/global_val_26 0
  st var_stk_base.346 0 = lhsaddr.692
  st var_stk_base.346 8 = 6:U64
  lea.stk lhsaddr.693:A64 = msg_eval%315 0
  ld pointer.314:A64 = lhsaddr.693 0
  pusharg 6:U64
  pusharg pointer.314
  pusharg 1:S32
  bsr write
  poparg call.346:S64
  .stk msg_eval%316 8 16
  lea.stk var_stk_base.347:A64 msg_eval%316 0
  lea.mem lhsaddr.694:A64 = $gen/global_val_14 0
  st var_stk_base.347 0 = lhsaddr.694
  st var_stk_base.347 8 = 4:U64
  lea.stk lhsaddr.695:A64 = msg_eval%316 0
  ld pointer.315:A64 = lhsaddr.695 0
  pusharg 4:U64
  pusharg pointer.315
  pusharg 1:S32
  bsr write
  poparg call.347:S64
  .stk msg_eval%317 8 16
  lea.stk var_stk_base.348:A64 msg_eval%317 0
  lea.mem lhsaddr.696:A64 = $gen/global_val_15 0
  st var_stk_base.348 0 = lhsaddr.696
  st var_stk_base.348 8 = 8:U64
  lea.stk lhsaddr.697:A64 = msg_eval%317 0
  ld pointer.316:A64 = lhsaddr.697 0
  pusharg 8:U64
  pusharg pointer.316
  pusharg 1:S32
  bsr write
  poparg call.348:S64
  .stk msg_eval%318 8 16
  lea.stk var_stk_base.349:A64 msg_eval%318 0
  lea.mem lhsaddr.698:A64 = $gen/global_val_16 0
  st var_stk_base.349 0 = lhsaddr.698
  st var_stk_base.349 8 = 4:U64
  lea.stk lhsaddr.699:A64 = msg_eval%318 0
  ld pointer.317:A64 = lhsaddr.699 0
  pusharg 4:U64
  pusharg pointer.317
  pusharg 1:S32
  bsr write
  poparg call.349:S64
  .stk msg_eval%319 8 16
  lea.stk var_stk_base.350:A64 msg_eval%319 0
  lea.mem lhsaddr.700:A64 = $gen/global_val_132 0
  st var_stk_base.350 0 = lhsaddr.700
  st var_stk_base.350 8 = 55:U64
  lea.stk lhsaddr.701:A64 = msg_eval%319 0
  ld pointer.318:A64 = lhsaddr.701 0
  pusharg 55:U64
  pusharg pointer.318
  pusharg 1:S32
  bsr write
  poparg call.350:S64
  .stk msg_eval%320 8 16
  lea.stk var_stk_base.351:A64 msg_eval%320 0
  lea.mem lhsaddr.702:A64 = $gen/global_val_17 0
  st var_stk_base.351 0 = lhsaddr.702
  st var_stk_base.351 8 = 1:U64
  lea.stk lhsaddr.703:A64 = msg_eval%320 0
  ld pointer.319:A64 = lhsaddr.703 0
  pusharg 1:U64
  pusharg pointer.319
  pusharg 1:S32
  bsr write
  poparg call.351:S64
  trap
.bbl br_join.31
  .reg R64 expr.32
  .stk arg0.32 8 16
  lea.stk var_stk_base.352:A64 arg0.32 0
  lea.mem lhsaddr.704:A64 = $gen/global_val_133 0
  st var_stk_base.352 0 = lhsaddr.704
  st var_stk_base.352 8 = 18:U64
  lea.stk lhsaddr.705:A64 = arg0.32 0
  pusharg lhsaddr.705
  bsr parse_real_test/parse_r64
  poparg call.352:R64
  mov expr.32 = call.352
  bra end_expr.32
.bbl end_expr.32
  mov a_val%65:R64 = expr.32
  bitcast bitcast.32:U64 = a_val%65
  beq 4607182418800017376:U64 bitcast.32 br_join.32
  .stk msg_eval%321 8 16
  lea.stk var_stk_base.353:A64 msg_eval%321 0
  lea.mem lhsaddr.706:A64 = $gen/global_val_9 0
  st var_stk_base.353 0 = lhsaddr.706
  st var_stk_base.353 8 = 11:U64
  lea.stk lhsaddr.707:A64 = msg_eval%321 0
  ld pointer.320:A64 = lhsaddr.707 0
  pusharg 11:U64
  pusharg pointer.320
  pusharg 1:S32
  bsr write
  poparg call.353:S64
  .stk msg_eval%322 8 16
  lea.stk var_stk_base.354:A64 msg_eval%322 0
  lea.mem lhsaddr.708:A64 = $gen/global_val_10 0
  st var_stk_base.354 0 = lhsaddr.708
  st var_stk_base.354 8 = 11:U64
  lea.stk lhsaddr.709:A64 = msg_eval%322 0
  ld pointer.321:A64 = lhsaddr.709 0
  pusharg 11:U64
  pusharg pointer.321
  pusharg 1:S32
  bsr write
  poparg call.354:S64
  .stk msg_eval%323 8 16
  lea.stk var_stk_base.355:A64 msg_eval%323 0
  lea.mem lhsaddr.710:A64 = $gen/global_val_134 0
  st var_stk_base.355 0 = lhsaddr.710
  st var_stk_base.355 8 = 55:U64
  lea.stk lhsaddr.711:A64 = msg_eval%323 0
  ld pointer.322:A64 = lhsaddr.711 0
  pusharg 55:U64
  pusharg pointer.322
  pusharg 1:S32
  bsr write
  poparg call.355:S64
  .stk msg_eval%324 8 16
  lea.stk var_stk_base.356:A64 msg_eval%324 0
  lea.mem lhsaddr.712:A64 = $gen/global_val_12 0
  st var_stk_base.356 0 = lhsaddr.712
  st var_stk_base.356 8 = 2:U64
  lea.stk lhsaddr.713:A64 = msg_eval%324 0
  ld pointer.323:A64 = lhsaddr.713 0
  pusharg 2:U64
  pusharg pointer.323
  pusharg 1:S32
  bsr write
  poparg call.356:S64
  .stk msg_eval%325 8 16
  lea.stk var_stk_base.357:A64 msg_eval%325 0
  lea.mem lhsaddr.714:A64 = $gen/global_val_26 0
  st var_stk_base.357 0 = lhsaddr.714
  st var_stk_base.357 8 = 6:U64
  lea.stk lhsaddr.715:A64 = msg_eval%325 0
  ld pointer.324:A64 = lhsaddr.715 0
  pusharg 6:U64
  pusharg pointer.324
  pusharg 1:S32
  bsr write
  poparg call.357:S64
  .stk msg_eval%326 8 16
  lea.stk var_stk_base.358:A64 msg_eval%326 0
  lea.mem lhsaddr.716:A64 = $gen/global_val_14 0
  st var_stk_base.358 0 = lhsaddr.716
  st var_stk_base.358 8 = 4:U64
  lea.stk lhsaddr.717:A64 = msg_eval%326 0
  ld pointer.325:A64 = lhsaddr.717 0
  pusharg 4:U64
  pusharg pointer.325
  pusharg 1:S32
  bsr write
  poparg call.358:S64
  .stk msg_eval%327 8 16
  lea.stk var_stk_base.359:A64 msg_eval%327 0
  lea.mem lhsaddr.718:A64 = $gen/global_val_15 0
  st var_stk_base.359 0 = lhsaddr.718
  st var_stk_base.359 8 = 8:U64
  lea.stk lhsaddr.719:A64 = msg_eval%327 0
  ld pointer.326:A64 = lhsaddr.719 0
  pusharg 8:U64
  pusharg pointer.326
  pusharg 1:S32
  bsr write
  poparg call.359:S64
  .stk msg_eval%328 8 16
  lea.stk var_stk_base.360:A64 msg_eval%328 0
  lea.mem lhsaddr.720:A64 = $gen/global_val_16 0
  st var_stk_base.360 0 = lhsaddr.720
  st var_stk_base.360 8 = 4:U64
  lea.stk lhsaddr.721:A64 = msg_eval%328 0
  ld pointer.327:A64 = lhsaddr.721 0
  pusharg 4:U64
  pusharg pointer.327
  pusharg 1:S32
  bsr write
  poparg call.360:S64
  .stk msg_eval%329 8 16
  lea.stk var_stk_base.361:A64 msg_eval%329 0
  lea.mem lhsaddr.722:A64 = $gen/global_val_134 0
  st var_stk_base.361 0 = lhsaddr.722
  st var_stk_base.361 8 = 55:U64
  lea.stk lhsaddr.723:A64 = msg_eval%329 0
  ld pointer.328:A64 = lhsaddr.723 0
  pusharg 55:U64
  pusharg pointer.328
  pusharg 1:S32
  bsr write
  poparg call.361:S64
  .stk msg_eval%330 8 16
  lea.stk var_stk_base.362:A64 msg_eval%330 0
  lea.mem lhsaddr.724:A64 = $gen/global_val_17 0
  st var_stk_base.362 0 = lhsaddr.724
  st var_stk_base.362 8 = 1:U64
  lea.stk lhsaddr.725:A64 = msg_eval%330 0
  ld pointer.329:A64 = lhsaddr.725 0
  pusharg 1:U64
  pusharg pointer.329
  pusharg 1:S32
  bsr write
  poparg call.362:S64
  trap
.bbl br_join.32
  .reg R64 expr.33
  .stk arg0.33 8 16
  lea.stk var_stk_base.363:A64 arg0.33 0
  lea.mem lhsaddr.726:A64 = $gen/global_val_135 0
  st var_stk_base.363 0 = lhsaddr.726
  st var_stk_base.363 8 = 20:U64
  lea.stk lhsaddr.727:A64 = arg0.33 0
  pusharg lhsaddr.727
  bsr parse_real_test/parse_r64
  poparg call.363:R64
  mov expr.33 = call.363
  bra end_expr.33
.bbl end_expr.33
  mov a_val%67:R64 = expr.33
  bitcast bitcast.33:U64 = a_val%67
  beq 4607182418800017407:U64 bitcast.33 br_join.33
  .stk msg_eval%331 8 16
  lea.stk var_stk_base.364:A64 msg_eval%331 0
  lea.mem lhsaddr.728:A64 = $gen/global_val_9 0
  st var_stk_base.364 0 = lhsaddr.728
  st var_stk_base.364 8 = 11:U64
  lea.stk lhsaddr.729:A64 = msg_eval%331 0
  ld pointer.330:A64 = lhsaddr.729 0
  pusharg 11:U64
  pusharg pointer.330
  pusharg 1:S32
  bsr write
  poparg call.364:S64
  .stk msg_eval%332 8 16
  lea.stk var_stk_base.365:A64 msg_eval%332 0
  lea.mem lhsaddr.730:A64 = $gen/global_val_10 0
  st var_stk_base.365 0 = lhsaddr.730
  st var_stk_base.365 8 = 11:U64
  lea.stk lhsaddr.731:A64 = msg_eval%332 0
  ld pointer.331:A64 = lhsaddr.731 0
  pusharg 11:U64
  pusharg pointer.331
  pusharg 1:S32
  bsr write
  poparg call.365:S64
  .stk msg_eval%333 8 16
  lea.stk var_stk_base.366:A64 msg_eval%333 0
  lea.mem lhsaddr.732:A64 = $gen/global_val_136 0
  st var_stk_base.366 0 = lhsaddr.732
  st var_stk_base.366 8 = 55:U64
  lea.stk lhsaddr.733:A64 = msg_eval%333 0
  ld pointer.332:A64 = lhsaddr.733 0
  pusharg 55:U64
  pusharg pointer.332
  pusharg 1:S32
  bsr write
  poparg call.366:S64
  .stk msg_eval%334 8 16
  lea.stk var_stk_base.367:A64 msg_eval%334 0
  lea.mem lhsaddr.734:A64 = $gen/global_val_12 0
  st var_stk_base.367 0 = lhsaddr.734
  st var_stk_base.367 8 = 2:U64
  lea.stk lhsaddr.735:A64 = msg_eval%334 0
  ld pointer.333:A64 = lhsaddr.735 0
  pusharg 2:U64
  pusharg pointer.333
  pusharg 1:S32
  bsr write
  poparg call.367:S64
  .stk msg_eval%335 8 16
  lea.stk var_stk_base.368:A64 msg_eval%335 0
  lea.mem lhsaddr.736:A64 = $gen/global_val_26 0
  st var_stk_base.368 0 = lhsaddr.736
  st var_stk_base.368 8 = 6:U64
  lea.stk lhsaddr.737:A64 = msg_eval%335 0
  ld pointer.334:A64 = lhsaddr.737 0
  pusharg 6:U64
  pusharg pointer.334
  pusharg 1:S32
  bsr write
  poparg call.368:S64
  .stk msg_eval%336 8 16
  lea.stk var_stk_base.369:A64 msg_eval%336 0
  lea.mem lhsaddr.738:A64 = $gen/global_val_14 0
  st var_stk_base.369 0 = lhsaddr.738
  st var_stk_base.369 8 = 4:U64
  lea.stk lhsaddr.739:A64 = msg_eval%336 0
  ld pointer.335:A64 = lhsaddr.739 0
  pusharg 4:U64
  pusharg pointer.335
  pusharg 1:S32
  bsr write
  poparg call.369:S64
  .stk msg_eval%337 8 16
  lea.stk var_stk_base.370:A64 msg_eval%337 0
  lea.mem lhsaddr.740:A64 = $gen/global_val_15 0
  st var_stk_base.370 0 = lhsaddr.740
  st var_stk_base.370 8 = 8:U64
  lea.stk lhsaddr.741:A64 = msg_eval%337 0
  ld pointer.336:A64 = lhsaddr.741 0
  pusharg 8:U64
  pusharg pointer.336
  pusharg 1:S32
  bsr write
  poparg call.370:S64
  .stk msg_eval%338 8 16
  lea.stk var_stk_base.371:A64 msg_eval%338 0
  lea.mem lhsaddr.742:A64 = $gen/global_val_16 0
  st var_stk_base.371 0 = lhsaddr.742
  st var_stk_base.371 8 = 4:U64
  lea.stk lhsaddr.743:A64 = msg_eval%338 0
  ld pointer.337:A64 = lhsaddr.743 0
  pusharg 4:U64
  pusharg pointer.337
  pusharg 1:S32
  bsr write
  poparg call.371:S64
  .stk msg_eval%339 8 16
  lea.stk var_stk_base.372:A64 msg_eval%339 0
  lea.mem lhsaddr.744:A64 = $gen/global_val_136 0
  st var_stk_base.372 0 = lhsaddr.744
  st var_stk_base.372 8 = 55:U64
  lea.stk lhsaddr.745:A64 = msg_eval%339 0
  ld pointer.338:A64 = lhsaddr.745 0
  pusharg 55:U64
  pusharg pointer.338
  pusharg 1:S32
  bsr write
  poparg call.372:S64
  .stk msg_eval%340 8 16
  lea.stk var_stk_base.373:A64 msg_eval%340 0
  lea.mem lhsaddr.746:A64 = $gen/global_val_17 0
  st var_stk_base.373 0 = lhsaddr.746
  st var_stk_base.373 8 = 1:U64
  lea.stk lhsaddr.747:A64 = msg_eval%340 0
  ld pointer.339:A64 = lhsaddr.747 0
  pusharg 1:U64
  pusharg pointer.339
  pusharg 1:S32
  bsr write
  poparg call.373:S64
  trap
.bbl br_join.33
  .reg R64 expr.34
  .stk arg0.34 8 16
  lea.stk var_stk_base.374:A64 arg0.34 0
  lea.mem lhsaddr.748:A64 = $gen/global_val_137 0
  st var_stk_base.374 0 = lhsaddr.748
  st var_stk_base.374 8 = 27:U64
  lea.stk lhsaddr.749:A64 = arg0.34 0
  pusharg lhsaddr.749
  bsr parse_real_test/parse_r64
  poparg call.374:R64
  mov expr.34 = call.374
  bra end_expr.34
.bbl end_expr.34
  mov a_val%69:R64 = expr.34
  bitcast bitcast.34:U64 = a_val%69
  beq 4607182418800017407:U64 bitcast.34 br_join.34
  .stk msg_eval%341 8 16
  lea.stk var_stk_base.375:A64 msg_eval%341 0
  lea.mem lhsaddr.750:A64 = $gen/global_val_9 0
  st var_stk_base.375 0 = lhsaddr.750
  st var_stk_base.375 8 = 11:U64
  lea.stk lhsaddr.751:A64 = msg_eval%341 0
  ld pointer.340:A64 = lhsaddr.751 0
  pusharg 11:U64
  pusharg pointer.340
  pusharg 1:S32
  bsr write
  poparg call.375:S64
  .stk msg_eval%342 8 16
  lea.stk var_stk_base.376:A64 msg_eval%342 0
  lea.mem lhsaddr.752:A64 = $gen/global_val_10 0
  st var_stk_base.376 0 = lhsaddr.752
  st var_stk_base.376 8 = 11:U64
  lea.stk lhsaddr.753:A64 = msg_eval%342 0
  ld pointer.341:A64 = lhsaddr.753 0
  pusharg 11:U64
  pusharg pointer.341
  pusharg 1:S32
  bsr write
  poparg call.376:S64
  .stk msg_eval%343 8 16
  lea.stk var_stk_base.377:A64 msg_eval%343 0
  lea.mem lhsaddr.754:A64 = $gen/global_val_138 0
  st var_stk_base.377 0 = lhsaddr.754
  st var_stk_base.377 8 = 55:U64
  lea.stk lhsaddr.755:A64 = msg_eval%343 0
  ld pointer.342:A64 = lhsaddr.755 0
  pusharg 55:U64
  pusharg pointer.342
  pusharg 1:S32
  bsr write
  poparg call.377:S64
  .stk msg_eval%344 8 16
  lea.stk var_stk_base.378:A64 msg_eval%344 0
  lea.mem lhsaddr.756:A64 = $gen/global_val_12 0
  st var_stk_base.378 0 = lhsaddr.756
  st var_stk_base.378 8 = 2:U64
  lea.stk lhsaddr.757:A64 = msg_eval%344 0
  ld pointer.343:A64 = lhsaddr.757 0
  pusharg 2:U64
  pusharg pointer.343
  pusharg 1:S32
  bsr write
  poparg call.378:S64
  .stk msg_eval%345 8 16
  lea.stk var_stk_base.379:A64 msg_eval%345 0
  lea.mem lhsaddr.758:A64 = $gen/global_val_26 0
  st var_stk_base.379 0 = lhsaddr.758
  st var_stk_base.379 8 = 6:U64
  lea.stk lhsaddr.759:A64 = msg_eval%345 0
  ld pointer.344:A64 = lhsaddr.759 0
  pusharg 6:U64
  pusharg pointer.344
  pusharg 1:S32
  bsr write
  poparg call.379:S64
  .stk msg_eval%346 8 16
  lea.stk var_stk_base.380:A64 msg_eval%346 0
  lea.mem lhsaddr.760:A64 = $gen/global_val_14 0
  st var_stk_base.380 0 = lhsaddr.760
  st var_stk_base.380 8 = 4:U64
  lea.stk lhsaddr.761:A64 = msg_eval%346 0
  ld pointer.345:A64 = lhsaddr.761 0
  pusharg 4:U64
  pusharg pointer.345
  pusharg 1:S32
  bsr write
  poparg call.380:S64
  .stk msg_eval%347 8 16
  lea.stk var_stk_base.381:A64 msg_eval%347 0
  lea.mem lhsaddr.762:A64 = $gen/global_val_15 0
  st var_stk_base.381 0 = lhsaddr.762
  st var_stk_base.381 8 = 8:U64
  lea.stk lhsaddr.763:A64 = msg_eval%347 0
  ld pointer.346:A64 = lhsaddr.763 0
  pusharg 8:U64
  pusharg pointer.346
  pusharg 1:S32
  bsr write
  poparg call.381:S64
  .stk msg_eval%348 8 16
  lea.stk var_stk_base.382:A64 msg_eval%348 0
  lea.mem lhsaddr.764:A64 = $gen/global_val_16 0
  st var_stk_base.382 0 = lhsaddr.764
  st var_stk_base.382 8 = 4:U64
  lea.stk lhsaddr.765:A64 = msg_eval%348 0
  ld pointer.347:A64 = lhsaddr.765 0
  pusharg 4:U64
  pusharg pointer.347
  pusharg 1:S32
  bsr write
  poparg call.382:S64
  .stk msg_eval%349 8 16
  lea.stk var_stk_base.383:A64 msg_eval%349 0
  lea.mem lhsaddr.766:A64 = $gen/global_val_138 0
  st var_stk_base.383 0 = lhsaddr.766
  st var_stk_base.383 8 = 55:U64
  lea.stk lhsaddr.767:A64 = msg_eval%349 0
  ld pointer.348:A64 = lhsaddr.767 0
  pusharg 55:U64
  pusharg pointer.348
  pusharg 1:S32
  bsr write
  poparg call.383:S64
  .stk msg_eval%350 8 16
  lea.stk var_stk_base.384:A64 msg_eval%350 0
  lea.mem lhsaddr.768:A64 = $gen/global_val_17 0
  st var_stk_base.384 0 = lhsaddr.768
  st var_stk_base.384 8 = 1:U64
  lea.stk lhsaddr.769:A64 = msg_eval%350 0
  ld pointer.349:A64 = lhsaddr.769 0
  pusharg 1:U64
  pusharg pointer.349
  pusharg 1:S32
  bsr write
  poparg call.384:S64
  trap
.bbl br_join.34
  .reg R64 expr.35
  .stk arg0.35 8 16
  lea.stk var_stk_base.385:A64 arg0.35 0
  lea.mem lhsaddr.770:A64 = $gen/global_val_139 0
  st var_stk_base.385 0 = lhsaddr.770
  st var_stk_base.385 8 = 18:U64
  lea.stk lhsaddr.771:A64 = arg0.35 0
  pusharg lhsaddr.771
  bsr parse_real_test/parse_r64
  poparg call.385:R64
  mov expr.35 = call.385
  bra end_expr.35
.bbl end_expr.35
  mov a_val%71:R64 = expr.35
  bitcast bitcast.35:U64 = a_val%71
  beq 4845873199050653695:U64 bitcast.35 br_join.35
  .stk msg_eval%351 8 16
  lea.stk var_stk_base.386:A64 msg_eval%351 0
  lea.mem lhsaddr.772:A64 = $gen/global_val_9 0
  st var_stk_base.386 0 = lhsaddr.772
  st var_stk_base.386 8 = 11:U64
  lea.stk lhsaddr.773:A64 = msg_eval%351 0
  ld pointer.350:A64 = lhsaddr.773 0
  pusharg 11:U64
  pusharg pointer.350
  pusharg 1:S32
  bsr write
  poparg call.386:S64
  .stk msg_eval%352 8 16
  lea.stk var_stk_base.387:A64 msg_eval%352 0
  lea.mem lhsaddr.774:A64 = $gen/global_val_10 0
  st var_stk_base.387 0 = lhsaddr.774
  st var_stk_base.387 8 = 11:U64
  lea.stk lhsaddr.775:A64 = msg_eval%352 0
  ld pointer.351:A64 = lhsaddr.775 0
  pusharg 11:U64
  pusharg pointer.351
  pusharg 1:S32
  bsr write
  poparg call.387:S64
  .stk msg_eval%353 8 16
  lea.stk var_stk_base.388:A64 msg_eval%353 0
  lea.mem lhsaddr.776:A64 = $gen/global_val_140 0
  st var_stk_base.388 0 = lhsaddr.776
  st var_stk_base.388 8 = 55:U64
  lea.stk lhsaddr.777:A64 = msg_eval%353 0
  ld pointer.352:A64 = lhsaddr.777 0
  pusharg 55:U64
  pusharg pointer.352
  pusharg 1:S32
  bsr write
  poparg call.388:S64
  .stk msg_eval%354 8 16
  lea.stk var_stk_base.389:A64 msg_eval%354 0
  lea.mem lhsaddr.778:A64 = $gen/global_val_12 0
  st var_stk_base.389 0 = lhsaddr.778
  st var_stk_base.389 8 = 2:U64
  lea.stk lhsaddr.779:A64 = msg_eval%354 0
  ld pointer.353:A64 = lhsaddr.779 0
  pusharg 2:U64
  pusharg pointer.353
  pusharg 1:S32
  bsr write
  poparg call.389:S64
  .stk msg_eval%355 8 16
  lea.stk var_stk_base.390:A64 msg_eval%355 0
  lea.mem lhsaddr.780:A64 = $gen/global_val_26 0
  st var_stk_base.390 0 = lhsaddr.780
  st var_stk_base.390 8 = 6:U64
  lea.stk lhsaddr.781:A64 = msg_eval%355 0
  ld pointer.354:A64 = lhsaddr.781 0
  pusharg 6:U64
  pusharg pointer.354
  pusharg 1:S32
  bsr write
  poparg call.390:S64
  .stk msg_eval%356 8 16
  lea.stk var_stk_base.391:A64 msg_eval%356 0
  lea.mem lhsaddr.782:A64 = $gen/global_val_14 0
  st var_stk_base.391 0 = lhsaddr.782
  st var_stk_base.391 8 = 4:U64
  lea.stk lhsaddr.783:A64 = msg_eval%356 0
  ld pointer.355:A64 = lhsaddr.783 0
  pusharg 4:U64
  pusharg pointer.355
  pusharg 1:S32
  bsr write
  poparg call.391:S64
  .stk msg_eval%357 8 16
  lea.stk var_stk_base.392:A64 msg_eval%357 0
  lea.mem lhsaddr.784:A64 = $gen/global_val_15 0
  st var_stk_base.392 0 = lhsaddr.784
  st var_stk_base.392 8 = 8:U64
  lea.stk lhsaddr.785:A64 = msg_eval%357 0
  ld pointer.356:A64 = lhsaddr.785 0
  pusharg 8:U64
  pusharg pointer.356
  pusharg 1:S32
  bsr write
  poparg call.392:S64
  .stk msg_eval%358 8 16
  lea.stk var_stk_base.393:A64 msg_eval%358 0
  lea.mem lhsaddr.786:A64 = $gen/global_val_16 0
  st var_stk_base.393 0 = lhsaddr.786
  st var_stk_base.393 8 = 4:U64
  lea.stk lhsaddr.787:A64 = msg_eval%358 0
  ld pointer.357:A64 = lhsaddr.787 0
  pusharg 4:U64
  pusharg pointer.357
  pusharg 1:S32
  bsr write
  poparg call.393:S64
  .stk msg_eval%359 8 16
  lea.stk var_stk_base.394:A64 msg_eval%359 0
  lea.mem lhsaddr.788:A64 = $gen/global_val_140 0
  st var_stk_base.394 0 = lhsaddr.788
  st var_stk_base.394 8 = 55:U64
  lea.stk lhsaddr.789:A64 = msg_eval%359 0
  ld pointer.358:A64 = lhsaddr.789 0
  pusharg 55:U64
  pusharg pointer.358
  pusharg 1:S32
  bsr write
  poparg call.394:S64
  .stk msg_eval%360 8 16
  lea.stk var_stk_base.395:A64 msg_eval%360 0
  lea.mem lhsaddr.790:A64 = $gen/global_val_17 0
  st var_stk_base.395 0 = lhsaddr.790
  st var_stk_base.395 8 = 1:U64
  lea.stk lhsaddr.791:A64 = msg_eval%360 0
  ld pointer.359:A64 = lhsaddr.791 0
  pusharg 1:U64
  pusharg pointer.359
  pusharg 1:S32
  bsr write
  poparg call.395:S64
  trap
.bbl br_join.35
  .reg R64 expr.36
  .stk arg0.36 8 16
  lea.stk var_stk_base.396:A64 arg0.36 0
  lea.mem lhsaddr.792:A64 = $gen/global_val_141 0
  st var_stk_base.396 0 = lhsaddr.792
  st var_stk_base.396 8 = 26:U64
  lea.stk lhsaddr.793:A64 = arg0.36 0
  pusharg lhsaddr.793
  bsr parse_real_test/parse_r64
  poparg call.396:R64
  mov expr.36 = call.396
  bra end_expr.36
.bbl end_expr.36
  mov a_val%73:R64 = expr.36
  bitcast bitcast.36:U64 = a_val%73
  beq 4989988387126509567:U64 bitcast.36 br_join.36
  .stk msg_eval%361 8 16
  lea.stk var_stk_base.397:A64 msg_eval%361 0
  lea.mem lhsaddr.794:A64 = $gen/global_val_9 0
  st var_stk_base.397 0 = lhsaddr.794
  st var_stk_base.397 8 = 11:U64
  lea.stk lhsaddr.795:A64 = msg_eval%361 0
  ld pointer.360:A64 = lhsaddr.795 0
  pusharg 11:U64
  pusharg pointer.360
  pusharg 1:S32
  bsr write
  poparg call.397:S64
  .stk msg_eval%362 8 16
  lea.stk var_stk_base.398:A64 msg_eval%362 0
  lea.mem lhsaddr.796:A64 = $gen/global_val_10 0
  st var_stk_base.398 0 = lhsaddr.796
  st var_stk_base.398 8 = 11:U64
  lea.stk lhsaddr.797:A64 = msg_eval%362 0
  ld pointer.361:A64 = lhsaddr.797 0
  pusharg 11:U64
  pusharg pointer.361
  pusharg 1:S32
  bsr write
  poparg call.398:S64
  .stk msg_eval%363 8 16
  lea.stk var_stk_base.399:A64 msg_eval%363 0
  lea.mem lhsaddr.798:A64 = $gen/global_val_142 0
  st var_stk_base.399 0 = lhsaddr.798
  st var_stk_base.399 8 = 55:U64
  lea.stk lhsaddr.799:A64 = msg_eval%363 0
  ld pointer.362:A64 = lhsaddr.799 0
  pusharg 55:U64
  pusharg pointer.362
  pusharg 1:S32
  bsr write
  poparg call.399:S64
  .stk msg_eval%364 8 16
  lea.stk var_stk_base.400:A64 msg_eval%364 0
  lea.mem lhsaddr.800:A64 = $gen/global_val_12 0
  st var_stk_base.400 0 = lhsaddr.800
  st var_stk_base.400 8 = 2:U64
  lea.stk lhsaddr.801:A64 = msg_eval%364 0
  ld pointer.363:A64 = lhsaddr.801 0
  pusharg 2:U64
  pusharg pointer.363
  pusharg 1:S32
  bsr write
  poparg call.400:S64
  .stk msg_eval%365 8 16
  lea.stk var_stk_base.401:A64 msg_eval%365 0
  lea.mem lhsaddr.802:A64 = $gen/global_val_26 0
  st var_stk_base.401 0 = lhsaddr.802
  st var_stk_base.401 8 = 6:U64
  lea.stk lhsaddr.803:A64 = msg_eval%365 0
  ld pointer.364:A64 = lhsaddr.803 0
  pusharg 6:U64
  pusharg pointer.364
  pusharg 1:S32
  bsr write
  poparg call.401:S64
  .stk msg_eval%366 8 16
  lea.stk var_stk_base.402:A64 msg_eval%366 0
  lea.mem lhsaddr.804:A64 = $gen/global_val_14 0
  st var_stk_base.402 0 = lhsaddr.804
  st var_stk_base.402 8 = 4:U64
  lea.stk lhsaddr.805:A64 = msg_eval%366 0
  ld pointer.365:A64 = lhsaddr.805 0
  pusharg 4:U64
  pusharg pointer.365
  pusharg 1:S32
  bsr write
  poparg call.402:S64
  .stk msg_eval%367 8 16
  lea.stk var_stk_base.403:A64 msg_eval%367 0
  lea.mem lhsaddr.806:A64 = $gen/global_val_15 0
  st var_stk_base.403 0 = lhsaddr.806
  st var_stk_base.403 8 = 8:U64
  lea.stk lhsaddr.807:A64 = msg_eval%367 0
  ld pointer.366:A64 = lhsaddr.807 0
  pusharg 8:U64
  pusharg pointer.366
  pusharg 1:S32
  bsr write
  poparg call.403:S64
  .stk msg_eval%368 8 16
  lea.stk var_stk_base.404:A64 msg_eval%368 0
  lea.mem lhsaddr.808:A64 = $gen/global_val_16 0
  st var_stk_base.404 0 = lhsaddr.808
  st var_stk_base.404 8 = 4:U64
  lea.stk lhsaddr.809:A64 = msg_eval%368 0
  ld pointer.367:A64 = lhsaddr.809 0
  pusharg 4:U64
  pusharg pointer.367
  pusharg 1:S32
  bsr write
  poparg call.404:S64
  .stk msg_eval%369 8 16
  lea.stk var_stk_base.405:A64 msg_eval%369 0
  lea.mem lhsaddr.810:A64 = $gen/global_val_142 0
  st var_stk_base.405 0 = lhsaddr.810
  st var_stk_base.405 8 = 55:U64
  lea.stk lhsaddr.811:A64 = msg_eval%369 0
  ld pointer.368:A64 = lhsaddr.811 0
  pusharg 55:U64
  pusharg pointer.368
  pusharg 1:S32
  bsr write
  poparg call.405:S64
  .stk msg_eval%370 8 16
  lea.stk var_stk_base.406:A64 msg_eval%370 0
  lea.mem lhsaddr.812:A64 = $gen/global_val_17 0
  st var_stk_base.406 0 = lhsaddr.812
  st var_stk_base.406 8 = 1:U64
  lea.stk lhsaddr.813:A64 = msg_eval%370 0
  ld pointer.369:A64 = lhsaddr.813 0
  pusharg 1:U64
  pusharg pointer.369
  pusharg 1:S32
  bsr write
  poparg call.406:S64
  trap
.bbl br_join.36
  ret


.fun main NORMAL [S32] = []
.bbl entry
  bsr parse_real_test/test_nan
  bsr parse_real_test/test_dec
  bsr parse_real_test/test_hex
  .stk msg_eval%1 8 16
  lea.stk var_stk_base:A64 msg_eval%1 0
  lea.mem lhsaddr:A64 = $gen/global_val_143 0
  st var_stk_base 0 = lhsaddr
  st var_stk_base 8 = 3:U64
  lea.stk lhsaddr.1:A64 = msg_eval%1 0
  ld pointer:A64 = lhsaddr.1 0
  pusharg 3:U64
  pusharg pointer
  pusharg 1:S32
  bsr write
  poparg call:S64
  pusharg 0:S32
  ret
