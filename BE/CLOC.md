## ISA Neutral Code
### Regular Code (Python)

```
File                                    blank        comment           code
--------------------------------------------------------------------------------------
BE/Elf/elfhelper.py                       154             44            923
BE/Base/ir.py                             162             40            546
BE/Base/lowering.py                       115             25            546
BE/Base/serialize.py                       78             17            427
BE/Base/reaching_defs.py                   81             62            389
BE/Base/liveness.py                        70             48            331
BE/Base/cfg.py                             43             16            265
BE/Base/reg_stats.py                       46             17            223
BE/Base/reg_alloc.py                       49             32            213
BE/Base/sanity.py                          28              5            194
BE/Base/optimize.py                        48             13            190
BE/Elf/elf_unit.py                         21              4            110
BE/Base/eval.py                            26              3             88
BE/Base/canonicalize.py                     5              1             29
--------------------------------------------------------------------------------------
SUM:                                      926            327           4474
--------------------------------------------------------------------------------------
```

### Table Code (Python)

```
File                                 blank        comment           code
-----------------------------------------------------------------------------------
BE/Elf/enum_tab.py                      93             21           1051
BE/Base/opcode_tab.py                  237            144            839
-----------------------------------------------------------------------------------
SUM:                                   330            165           1890
-----------------------------------------------------------------------------------
```
### Regular Code (C++)

```
File                                    blank        comment           code
--------------------------------------------------------------------------------------
BE/Base/ir.h                              179            107            791
BE/Base/serialize.cc                       72             20            758
BE/Base/lowering.cc                        56             18            713
BE/Elf/elfhelper.cc                        66             45            536
BE/Base/reaching_defs.cc                   46             23            481
BE/Base/ir.cc                              71             39            469
BE/Elf/elfhelper.h                         82             33            419
BE/Base/cfg.cc                             44             23            411
BE/Base/liveness.cc                        35             44            358
BE/Base/reg_stats.cc                       35              6            296
BE/Base/reg_alloc.cc                       26              2            237
BE/Base/optimize_tool.cc                   37              7            205
BE/Elf/elf_unit.h                          28              5            196
BE/Base/eval.cc                            16              3            140
BE/Base/sanity.cc                          21              1            113
BE/Elf/elf_tool.cc                          8              3             71
BE/Base/optimize.cc                        13              1             52
BE/Base/liveness.h                         19             17             48
BE/Base/serialize.h                        14              1             41
BE/Base/canonicalize.cc                     3              1             40
BE/Base/reg_alloc.h                        15              8             38
BE/Base/lowering.h                         17              5             34
BE/Base/reg_stats.h                        17              4             27
BE/Base/cfg.h                              16              1             17
BE/Base/reaching_defs.h                     9              1             11
BE/Base/eval.h                              4              1              9
BE/Base/optimize.h                          7              1              9
BE/Base/sanity.h                            6              1              7
BE/Base/canonicalize.h                      4              1              5
--------------------------------------------------------------------------------------
SUM:                                      966            422           6532
--------------------------------------------------------------------------------------
```

### Generated Files (C++)

```
File                                 blank        comment           code
-----------------------------------------------------------------------------------
BE/Elf/enum_gen.cc                      41              4           1970
BE/Base/opcode_gen.cc                   40              3            993
BE/Elf/enum_gen.h                       22              4            641
BE/Base/opcode_gen.h                    31              5            234
-----------------------------------------------------------------------------------
SUM:                                   134             16           3838
-----------------------------------------------------------------------------------
```
## A32 Code
### Regular Code (Python)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenA32/regs.py                            83             43            401
BE/CodeGenA32/legalize.py                        73             41            300
BE/CodeGenA32/codegen.py                         59             15            232
BE/CpuA32/assembler.py                           42              9            183
BE/CpuA32/symbolic.py                            25             11            119
BE/CodeGenA32/isel_tester.py                     14              0             57
BE/CpuA32/assembler_tool.py                      14              9             42
BE/CpuA32/disassembler_tool.py                    9              0             41
---------------------------------------------------------------------------------
SUM:                                            319            128           1375
---------------------------------------------------------------------------------
```

### Table Code (Python)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CpuA32/opcode_tab.py                    237             82           1151
BE/CodeGenA32/isel_tab.py                  145             80           1077
---------------------------------------------------------------------------------------
SUM:                                       382            162           2228
---------------------------------------------------------------------------------------
```
### Regular Code (C++)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenA32/regs.cc                            55             10            506
BE/CodeGenA32/legalize.cc                        45             14            344
BE/CpuA32/assembler.cc                           32              6            261
BE/CodeGenA32/codegen.cc                         24              3            228
BE/CpuA32/symbolic.cc                            21              3            221
BE/CodeGenA32/codegen_tool.cc                    38              5            146
BE/CpuA32/disassembler_tool.cc                    6              5            101
BE/CodeGenA32/isel_tester.cc                     12              2             94
BE/CodeGenA32/regs.h                             22              7             52
BE/CpuA32/assembler_tool.cc                      10              1             50
BE/CodeGenA32/legalize.h                          7              1             16
BE/CpuA32/assembler.h                            10              2             13
BE/CpuA32/symbolic.h                              6              1             13
BE/CodeGenA32/codegen.h                           8              1             12
---------------------------------------------------------------------------------
SUM:                                            296             61           2057
---------------------------------------------------------------------------------
```

### Generated Files (C++)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CodeGenA32/isel_gen.cc                   32             20           6170
BE/CpuA32/opcode_gen.cc                     41            270           2493
BE/CpuA32/opcode_gen.h                      41             22            637
BE/CodeGenA32/isel_gen.h                    15              6            106
---------------------------------------------------------------------------------------
SUM:                                       129            318           9406
---------------------------------------------------------------------------------------
```
## A64 Code
### Regular Code (Python)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenA64/regs.py                            71             56            333
BE/CodeGenA64/legalize.py                        78             36            274
BE/CodeGenA64/codegen.py                         61             22            244
BE/CpuA64/assembler.py                           45             14            192
BE/CpuA64/symbolic.py                            18             12            108
BE/CodeGenA64/isel_tester.py                     13              0             55
BE/CpuA64/assembler_tool.py                      17              9             45
BE/CpuA64/disassembler_tool.py                    9              1             41
---------------------------------------------------------------------------------
SUM:                                            312            150           1292
---------------------------------------------------------------------------------
```

### Table Code (Python)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CpuA64/opcode_tab.py                    260            133           1397
BE/CodeGenA64/isel_tab.py                  165             66           1242
---------------------------------------------------------------------------------------
SUM:                                       425            199           2639
---------------------------------------------------------------------------------------
```
### Regular Code (C++)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenA64/regs.cc                            45             25            412
BE/CodeGenA64/legalize.cc                        44             13            340
BE/CpuA64/assembler.cc                           35              6            256
BE/CodeGenA64/codegen.cc                         20              3            196
BE/CpuA64/symbolic.cc                            16              3            187
BE/CodeGenA64/codegen_tool.cc                    38              5            147
BE/CpuA64/disassembler_tool.cc                    6              5             97
BE/CodeGenA64/isel_tester.cc                     12              2             94
BE/CodeGenA64/regs.h                             20             10             59
BE/CpuA64/assembler_tool.cc                      10              1             49
BE/CodeGenA64/legalize.h                         10              1             18
BE/CpuA64/assembler.h                            10              2             13
BE/CpuA64/symbolic.h                              7              2             11
BE/CodeGenA64/codegen.h                           5              1              9
---------------------------------------------------------------------------------
SUM:                                            278             79           1888
---------------------------------------------------------------------------------
```

### Generated Files (C++)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CodeGenA64/isel_gen.cc                   47             21           7053
BE/CpuA64/opcode_gen.cc                    290            285           4704
BE/CpuA64/opcode_gen.h                      33             20           1047
BE/CodeGenA64/isel_gen.h                    17              8            102
---------------------------------------------------------------------------------------
SUM:                                       387            334          12906
---------------------------------------------------------------------------------------
```
## X64 Code
### Regular Code (Python)

```
File                                                 blank        comment           code
----------------------------------------------------------------------------------------
BE/CodeGenX64/legalize.py                               89             47            362
BE/CodeGenX64/regs.py                                   69             41            340
BE/CodeGenX64/codegen.py                                60             19            244
BE/CpuX64/assembler.py                                  43              9            201
BE/CpuX64/symbolic.py                                   26              4            131
BE/CpuX64/disassembler_tool.py                          13              0             53
BE/CpuX64/assembler_tool.py                             16              9             45
BE/CodeGenX64/isel_tester.py                            13              0             42
BE/CpuX64/TestData/objdump_extract.py                    6              1             23
----------------------------------------------------------------------------------------
SUM:                                                   335            130           1441
----------------------------------------------------------------------------------------
```

### Table Code (Python)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CodeGenX64/isel_tab.py                  150             85           1395
BE/CpuX64/opcode_tab.py                    180             79           1293
---------------------------------------------------------------------------------------
SUM:                                       330            164           2688
---------------------------------------------------------------------------------------
```
### Regular Code (C++)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenX64/legalize.cc                        52             18            495
BE/CodeGenX64/regs.cc                            45             18            414
BE/CpuX64/symbolic.cc                            24              1            349
BE/CpuX64/assembler.cc                           38             11            304
BE/CodeGenX64/codegen.cc                         24              3            226
BE/CodeGenX64/codegen_tool.cc                    39              5            149
BE/CpuX64/disassembler_tool.cc                   11              7            129
BE/CodeGenX64/isel_tester.cc                     12              2             78
BE/CodeGenX64/regs.h                             24             18             72
BE/CpuX64/assembler_tool.cc                      10              1             49
BE/CodeGenX64/legalize.h                         11              1             19
BE/CpuX64/assembler.h                            12              2             15
BE/CpuX64/symbolic.h                              7              2             12
BE/CodeGenX64/codegen.h                           5              1              9
---------------------------------------------------------------------------------
SUM:                                            314             90           2320
---------------------------------------------------------------------------------
```

### Generated Files (C++)

```
File                                             blank        comment           code
------------------------------------------------------------------------------------
BE/CodeGenX64/isel_gen_patterns.h                    3              0          28033
BE/CpuX64/opcode_gen_collisions.h                    3              1          16880
BE/CpuX64/opcode_gen_encodings.h                     1              2          13607
BE/CpuX64/opcode_gen_names.h                         2              3           5455
BE/CpuX64/opcode_gen_enum.h                          1              1           3404
BE/CpuX64/opcode_gen.cc                             29              8            470
BE/CodeGenX64/isel_gen.cc                           35             18            438
BE/CpuX64/opcode_gen.h                              25             15            121
BE/CodeGenX64/isel_gen.h                            18              8             93
------------------------------------------------------------------------------------
SUM:                                               117             56          68501
------------------------------------------------------------------------------------
```
