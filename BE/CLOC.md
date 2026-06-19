## ISA Neutral Code
### Regular Code (Python)

```
File                                           blank        comment           code
----------------------------------------------------------------------------------
BE/Elf/elfhelper.py                              154             44            923
BE/Base/ir.py                                    175             47            600
BE/Base/lowering.py                              112             33            558
BE/Base/serialize.py                              83             18            429
BE/Base/liveness.py                               70             48            331
BE/Base/reaching_defs.py                          68             29            320
BE/Base/cfg.py                                    44             19            268
BE/Base/reg_stats.py                              46             17            223
BE/Base/reg_alloc.py                              48             32            213
BE/Base/sanity.py                                 30              7            199
BE/Base/optimize.py                               44             14            189
BE/Elf/elf_unit.py                                21              4            110
BE/Base/eval.py                                   26              3             89
BE/CodeGenCommon/cpu_neutral.py                   12              2             45
BE/Base/canonicalize.py                            5              1             29
----------------------------------------------------------------------------------
SUM:                                             938            318           4526
----------------------------------------------------------------------------------
```

### Table Code (Python)

```
File                              blank        comment           code
--------------------------------------------------------------------------------
BE/Elf/enum_tab.py                   94             21           1059
--------------------------------------------------------------------------------
```
### Regular Code (C++)

```
File                                           blank        comment           code
----------------------------------------------------------------------------------
BE/Base/ir.h                                     182            109            815
BE/Base/serialize.cc                              71             23            758
BE/Base/lowering.cc                               55             19            730
BE/Elf/elfhelper.cc                               66             45            536
BE/Base/ir.cc                                     77             41            504
BE/Elf/elfhelper.h                                82             33            419
BE/Base/cfg.cc                                    45             27            417
BE/Base/reaching_defs.cc                          36             10            381
BE/Base/liveness.cc                               35             44            358
BE/Base/reg_stats.cc                              35              6            297
BE/Base/reg_alloc.cc                              26              2            236
BE/Base/optimize_tool.cc                          37              7            205
BE/Base/sanity.cc                                 24              1            199
BE/Elf/elf_unit.h                                 28              5            196
BE/Base/eval.cc                                   18              3            144
BE/Elf/elf_tool.cc                                 8              3             71
BE/CodeGenCommon/cpu_neutral.cc                   10              0             55
BE/Base/lowering.h                                22              1             54
BE/Base/optimize.cc                               12              1             51
BE/Base/liveness.h                                19             19             48
BE/CodeGenCommon/cpu_neutral.h                    11              0             42
BE/Base/serialize.h                               14              1             41
BE/Base/canonicalize.cc                            3              1             40
BE/Base/reg_alloc.h                               15              8             38
BE/Base/reg_stats.h                               17              4             27
BE/Base/cfg.h                                     17              1             19
BE/Base/reaching_defs.h                            9              2             10
BE/Base/eval.h                                     4              1              9
BE/Base/optimize.h                                 7              1              9
BE/Base/canonicalize.h                             4              1              5
BE/Base/sanity.h                                   4              1              5
----------------------------------------------------------------------------------
SUM:                                             993            420           6719
----------------------------------------------------------------------------------
```

### Generated Files (C++)

```
File                              blank        comment           code
--------------------------------------------------------------------------------
BE/Elf/enum_gen.cc                   41              4           1970
BE/Elf/enum_gen.h                    22              4            641
--------------------------------------------------------------------------------
SUM:                                 63              8           2611
--------------------------------------------------------------------------------
```
## A32 Code
### Regular Code (Python)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenA32/regs.py                            83             43            401
BE/CodeGenA32/legalize.py                        81             44            339
BE/CpuA32/assembler.py                           42              9            183
BE/CodeGenA32/codegen.py                         44             14            172
BE/CpuA32/symbolic.py                            25             11            119
BE/CodeGenA32/isel_tester.py                     14              0             57
BE/CpuA32/assembler_tool.py                      14              9             42
BE/CpuA32/disassembler_tool.py                    9              0             41
---------------------------------------------------------------------------------
SUM:                                            312            130           1354
---------------------------------------------------------------------------------
```

### Table Code (Python)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CpuA32/opcode_tab.py                    238             82           1149
BE/CodeGenA32/isel_tab.py                  145             80           1081
---------------------------------------------------------------------------------------
SUM:                                       383            162           2230
---------------------------------------------------------------------------------------
```
### Regular Code (C++)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenA32/regs.cc                            57             10            507
BE/CodeGenA32/legalize.cc                        48             16            372
BE/CpuA32/assembler.cc                           32              6            261
BE/CpuA32/symbolic.cc                            21              3            221
BE/CodeGenA32/codegen_tool.cc                    36              5            156
BE/CodeGenA32/codegen.cc                         16              3            126
BE/CpuA32/disassembler_tool.cc                    6              5            101
BE/CodeGenA32/isel_tester.cc                     12              2             95
BE/CodeGenA32/regs.h                             22              7             52
BE/CpuA32/assembler_tool.cc                      10              1             50
BE/CpuA32/assembler.h                            10              2             13
BE/CpuA32/symbolic.h                              6              1             13
BE/CodeGenA32/codegen.h                           8              1             12
BE/CodeGenA32/legalize.h                          7              1             10
---------------------------------------------------------------------------------
SUM:                                            291             63           1989
---------------------------------------------------------------------------------
```

### Generated Files (C++)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CodeGenA32/isel_gen.cc                   32             20           6170
BE/CpuA32/opcode_gen.cc                     42            270           2496
BE/CpuA32/opcode_gen.h                      41             22            637
BE/CodeGenA32/isel_gen.h                    15              6            106
---------------------------------------------------------------------------------------
SUM:                                       130            318           9409
---------------------------------------------------------------------------------------
```
## A64 Code
### Regular Code (Python)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenA64/regs.py                            71             56            333
BE/CodeGenA64/legalize.py                        90             37            315
BE/CpuA64/assembler.py                           45             14            192
BE/CodeGenA64/codegen.py                         46             21            182
BE/CpuA64/symbolic.py                            20             12            109
BE/CodeGenA64/isel_tester.py                     13              0             55
BE/CpuA64/assembler_tool.py                      17              9             45
BE/CpuA64/disassembler_tool.py                    9              1             41
---------------------------------------------------------------------------------
SUM:                                            311            150           1272
---------------------------------------------------------------------------------
```

### Table Code (Python)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CpuA64/opcode_tab.py                    260            133           1397
BE/CodeGenA64/isel_tab.py                  167             66           1245
---------------------------------------------------------------------------------------
SUM:                                       427            199           2642
---------------------------------------------------------------------------------------
```
### Regular Code (C++)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenA64/regs.cc                            47             25            413
BE/CodeGenA64/legalize.cc                        44             14            338
BE/CpuA64/assembler.cc                           35              6            256
BE/CpuA64/symbolic.cc                            20              3            201
BE/CodeGenA64/codegen_tool.cc                    35              5            156
BE/CodeGenA64/codegen.cc                         19              3            124
BE/CpuA64/disassembler_tool.cc                    6              5             97
BE/CodeGenA64/isel_tester.cc                     12              2             95
BE/CodeGenA64/regs.h                             20             10             59
BE/CpuA64/assembler_tool.cc                      10              1             49
BE/CpuA64/assembler.h                            10              2             13
BE/CpuA64/symbolic.h                              7              2             11
BE/CodeGenA64/legalize.h                          7              1             10
BE/CodeGenA64/codegen.h                           5              1              9
---------------------------------------------------------------------------------
SUM:                                            277             80           1831
---------------------------------------------------------------------------------
```

### Generated Files (C++)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CodeGenA64/isel_gen.cc                   47             21           7054
BE/CpuA64/opcode_gen.cc                    290            285           4704
BE/CpuA64/opcode_gen.h                      33             20           1047
BE/CodeGenA64/isel_gen.h                    17              8            102
---------------------------------------------------------------------------------------
SUM:                                       387            334          12907
---------------------------------------------------------------------------------------
```
## X64 Code
### Regular Code (Python)

```
File                                                 blank        comment           code
----------------------------------------------------------------------------------------
BE/CodeGenX64/legalize.py                               94             53            392
BE/CodeGenX64/regs.py                                   69             41            340
BE/CpuX64/assembler.py                                  43              9            201
BE/CodeGenX64/codegen.py                                53             18            200
BE/CpuX64/symbolic.py                                   26              4            131
BE/CpuX64/disassembler_tool.py                          13              0             53
BE/CpuX64/assembler_tool.py                             16              9             45
BE/CodeGenX64/isel_tester.py                            13              0             42
BE/CpuX64/TestData/objdump_extract.py                    6              1             23
----------------------------------------------------------------------------------------
SUM:                                                   333            135           1427
----------------------------------------------------------------------------------------
```

### Table Code (Python)

```
File                                     blank        comment           code
---------------------------------------------------------------------------------------
BE/CpuX64/x86data.js                       145             70           4391
BE/CodeGenX64/isel_tab.py                  150             85           1395
BE/CpuX64/opcode_tab.py                    180             79           1293
---------------------------------------------------------------------------------------
SUM:                                       475            234           7079
---------------------------------------------------------------------------------------
```
### Regular Code (C++)

```
File                                          blank        comment           code
---------------------------------------------------------------------------------
BE/CodeGenX64/legalize.cc                        53             20            494
BE/CodeGenX64/regs.cc                            47             18            415
BE/CpuX64/symbolic.cc                            24              1            349
BE/CpuX64/assembler.cc                           38             11            305
BE/CodeGenX64/codegen_tool.cc                    37              5            164
BE/CodeGenX64/codegen.cc                         24              3            154
BE/CpuX64/disassembler_tool.cc                   11              7            129
BE/CodeGenX64/isel_tester.cc                     12              2             79
BE/CodeGenX64/regs.h                             24             18             72
BE/CpuX64/assembler_tool.cc                      10              1             49
BE/CodeGenX64/legalize.h                         12              1             20
BE/CpuX64/assembler.h                            12              2             15
BE/CpuX64/symbolic.h                              7              2             12
BE/CodeGenX64/codegen.h                           5              1              9
---------------------------------------------------------------------------------
SUM:                                            316             92           2266
---------------------------------------------------------------------------------
```

### Generated Files (C++)

```
File                                             blank        comment           code
------------------------------------------------------------------------------------
BE/CodeGenX64/isel_gen_patterns.h                    3              0          28053
BE/CpuX64/opcode_gen_collisions.h                    3              1          16880
BE/CpuX64/opcode_gen_encodings.h                     1              2          13607
BE/CpuX64/opcode_gen_names.h                         2              3           5455
BE/CpuX64/opcode_gen_enum.h                          1              1           3404
BE/CpuX64/opcode_gen.cc                             29              8            470
BE/CodeGenX64/isel_gen.cc                           34             18            439
BE/CpuX64/opcode_gen.h                              25             15            121
BE/CodeGenX64/isel_gen.h                            18              8             93
------------------------------------------------------------------------------------
SUM:                                               116             56          68522
------------------------------------------------------------------------------------
```
