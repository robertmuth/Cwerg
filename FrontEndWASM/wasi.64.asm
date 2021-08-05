# based on
# https://github.com/bytecodealliance/wasmtime/blob/main/docs/WASI-tutorial.md

######################################################################
# HELPERS CLONED FROM StdLib
######################################################################


.fun write_u NORMAL [S64] = [S32 U32]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg val:U32
.stk buffer 1 16
  .reg U64 [pos]
  lea %A64_1:A64 = buffer
  mov pos = 16

.bbl while_1
  sub %U64_2:U64 = pos 1
  mov pos = %U64_2
  rem %U32_3:U32 = val 10
  add %U32_4:U32 = 48:U32 %U32_3
  conv %S8_5:S8 = %U32_4
  lea %A64_6:A64 = buffer
  lea %A64_7:A64 = %A64_6 pos
  st %A64_7 0 = %S8_5
  div %U32_8:U32 = val 10
  mov val = %U32_8

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A64_9:A64 = buffer
  lea %A64_10:A64 = %A64_9 pos
  lea %A64_11:A64 = buffer
  sub %U64_12:U64 = 16:U64 pos
  pusharg %U64_12
  pusharg %A64_10
  pusharg fd
  bsr write
  poparg %S64_13:S64
  mov %out = %S64_13
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
  conv %U32_1:U32 = sval
  pusharg %U32_1
  pusharg fd
  bsr write_u
  poparg %S64_2:S64
  mov %out = %S64_2
  pusharg %out
  ret

.bbl if_2_end
  .reg U32 [val]
  sub %S32_3:S32 = 0  sval
  conv %U32_4:U32 = %S32_3
  mov val = %U32_4
.stk buffer 1 16
  .reg U64 [pos]
  lea %A64_5:A64 = buffer
  mov pos = 16

.bbl while_1
  sub %U64_6:U64 = pos 1
  mov pos = %U64_6
  rem %U32_7:U32 = val 10
  add %U32_8:U32 = 48:U32 %U32_7
  conv %S8_9:S8 = %U32_8
  lea %A64_10:A64 = buffer
  lea %A64_11:A64 = %A64_10 pos
  st %A64_11 0 = %S8_9
  div %U32_12:U32 = val 10
  mov val = %U32_12

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  sub %U64_13:U64 = pos 1
  mov pos = %U64_13
  lea %A64_14:A64 = buffer
  lea %A64_15:A64 = %A64_14 pos
  mov %S8_16:S8 = 45
  st %A64_15 0 = %S8_16
  lea %A64_17:A64 = buffer
  lea %A64_18:A64 = %A64_17 pos
  lea %A64_19:A64 = buffer
  sub %U64_20:U64 = 16:U64 pos
  pusharg %U64_20
  pusharg %A64_18
  pusharg fd
  bsr write
  poparg %S64_21:S64
  mov %out = %S64_21
  pusharg %out
  ret


.fun write_c NORMAL [S64] = [S32 U8]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg c:U8
.stk buffer 1 16
  conv %S8_1:S8 = c
  lea %A64_2:A64 = buffer
  st %A64_2 0 = %S8_1
  lea %A64_3:A64 = buffer
  mov %U64_5:U64 = 1
  pusharg %U64_5
  pusharg %A64_3
  pusharg fd
  bsr write
  poparg %S64_4:S64
  conv %S32_6:S32 = %S64_4
  conv %S64_7:S64 = %S32_6
  mov %out = %S64_7
  pusharg %out
  ret

######################################################################
# PSEUDO WASI
######################################################################
.fun $wasi$print_i32_ln NORMAL [] = [A64 S32]

.bbl %start
  poparg dummy:A64
  poparg n:S32
  mov %S32_2:S32 = 1
  pusharg n
  pusharg %S32_2
  bsr write_d
  poparg %S64_1:S64
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S64_3:S64
  ret

######################################################################
# REAL WASI
######################################################################
# (mem-addr, status) ->
.fun $wasi$clock_time_get NORMAL [S32] = [A64 S32 S64 S32]
  .bbl %start
    .stk timespec 8 16
    poparg membase:A64
    poparg clk_id:S32
    poparg precision_dummy:S64
    poparg result_offset:S32
    lea.stk ts:A64 timespec 0
    pusharg ts
    pusharg clk_id
    bsr clock_gettime
    poparg status:S32
    ld sec:U64 ts 0
    ld nsec:U64 ts 8
    mul sec sec 1000000000:U64
    add sec sec nsec
    st membase result_offset sec
    pusharg statu:S32
    ret


# (mem-addr, status) ->
.fun $wasi$proc_exit NORMAL [] = [A64 S32]
  .bbl %start
    poparg dummy:A64
    poparg status:S32
    pusharg status
    bsr exit
    ret

.fun $wasi$fd_write NORMAL [S32] = [A64 S32 S32 S32 S32]

  .bbl %start
    poparg mem_base:A64
    poparg fd:S32
    poparg array_offset:S32
    poparg array_size:S32
    poparg result_offset:S32

    lea array:A64 mem_base array_offset
    lea result:A64 mem_base result_offset
    mov count:S32 0:S32
    mov errno:S32 0:S32
    bra check

  .bbl loop
    ld buf_offset:S32 array 0:U32
    lea buf:A64 mem_base buf_offset
    ld len:U32 array 4:U32
    conv len64:U64 len
    lea array array 8:U32
    sub array_size array_size 1
    pusharg len64
    pusharg buf
    pusharg fd
    bsr write
    poparg errno64:S64
    blt errno64 0 epilog
    conv errno errno64
    add count count errno
  .bbl check
    blt 0:S32 array_size loop
  .bbl epilog
    st result 0:U32 count
    pusharg errno
    ret

.mem global_argc 0 EXTERN
.mem global_argv 0 EXTERN

# (mem-addr, argc-offset, total-size-offset) -> errro
.fun $wasi$args_sizes_get NORMAL [S32] = [A64 S32 S32]
.bbl prolog
    poparg mem_base:A64
    poparg argc_offset:S32
    poparg total_size_offset:S32
    # handle argc
    ld.mem argc:S32 global_argc 0
    st mem_base argc_offset argc
    # handle total-size
    mov total_size:S32 0:S32
    ld.mem argv:A64 global_argv 0
.bbl loop_argv
    beq argc 0 done_argv
    sub argc argc 1

    ld s:A64 argv 0
    lea argv argv 8

.bbl strlen
    add total_size total_size 1
    ld b:U8 s 0
    lea s s 1
    bne b 0:U8 strlen
    bra loop_argv
.bbl done_argv
    st mem_base total_size_offset total_size
    pusharg 0:S32
    ret

# (mem-addr, argv-offset, string-data-offset) -> errro
.fun $wasi$args_get NORMAL [S32] = [A64 S32 S32]
.bbl prolog
    poparg mem_base:A64
    poparg argv_offset:S32
    poparg string_data_offset:S32

    ld.mem argv:A64 global_argv 0
    ld.mem argc:S32 global_argc 0

.bbl loop_argv
    beq argc 0 done_argv
    sub argc argc 1
    st mem_base argv_offset string_data_offset
    add argv_offset argv_offset 4
    ld s:A64 argv 0
    lea argv argv 8

.bbl strcpy
    ld b:U8 s 0
    lea s s 1
    st mem_base string_data_offset b
    add string_data_offset string_data_offset 1
    bne b 0:U8 strcpy
    bra loop_argv

.bbl done_argv
    pusharg 0:S32
    ret


