# based on
# https://github.com/bytecodealliance/wasmtime/blob/main/docs/WASI-tutorial.md


######################################################################
# HELPER CLONED FROM StdLib
######################################################################
.fun write_u NORMAL [S32] = [S32 U32]
.reg S32 [%out]

.bbl %start
  poparg fd:S32
  poparg val:U32
.stk buffer 1 16
  .reg U32 [pos]
  lea %A32_1:A32 = buffer
  mov pos = 16

.bbl while_1
  sub %U32_2:U32 = pos 1
  mov pos = %U32_2
  rem %U32_3:U32 = val 10
  add %U32_4:U32 = 48:U32 %U32_3
  conv %S8_5:S8 = %U32_4
  lea %A32_6:A32 = buffer
  lea %A32_7:A32 = %A32_6 pos
  st %A32_7 0 = %S8_5
  div %U32_8:U32 = val 10
  mov val = %U32_8

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  lea %A32_9:A32 = buffer
  lea %A32_10:A32 = %A32_9 pos
  lea %A32_11:A32 = buffer
  sub %U32_12:U32 = 16:U32 pos
  pusharg %U32_12
  pusharg %A32_10
  pusharg fd
  bsr write
  poparg %S32_13:S32
  mov %out = %S32_13
  pusharg %out
  ret

.fun write_c NORMAL [S32] = [S32 U8]
.reg S32 [%out]

.bbl %start
  poparg fd:S32
  poparg c:U8
.stk buffer 1 16
  conv %S8_1:S8 = c
  lea %A32_2:A32 = buffer
  st %A32_2 0 = %S8_1
  lea %A32_3:A32 = buffer
  mov %U32_5:U32 = 1
  pusharg %U32_5
  pusharg %A32_3
  pusharg fd
  bsr write
  poparg %S32_4:S32
  mov %out = %S32_4
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
  conv %U32_1:U32 = sval
  pusharg %U32_1
  pusharg fd
  bsr write_u
  poparg %S32_2:S32
  mov %out = %S32_2
  pusharg %out
  ret

.bbl if_2_end
  .reg U32 [val]
  sub %S32_3:S32 = 0  sval
  conv %U32_4:U32 = %S32_3
  mov val = %U32_4
.stk buffer 1 16
  .reg U32 [pos]
  lea %A32_5:A32 = buffer
  mov pos = 16

.bbl while_1
  sub %U32_6:U32 = pos 1
  mov pos = %U32_6
  rem %U32_7:U32 = val 10
  add %U32_8:U32 = 48:U32 %U32_7
  conv %S8_9:S8 = %U32_8
  lea %A32_10:A32 = buffer
  lea %A32_11:A32 = %A32_10 pos
  st %A32_11 0 = %S8_9
  div %U32_12:U32 = val 10
  mov val = %U32_12

.bbl while_1_cond
  bne val 0 while_1
  bra while_1_exit

.bbl while_1_exit
  sub %U32_13:U32 = pos 1
  mov pos = %U32_13
  lea %A32_14:A32 = buffer
  lea %A32_15:A32 = %A32_14 pos
  mov %S8_16:S8 = 45
  st %A32_15 0 = %S8_16
  lea %A32_17:A32 = buffer
  lea %A32_18:A32 = %A32_17 pos
  lea %A32_19:A32 = buffer
  sub %U32_20:U32 = 16:U32 pos
  pusharg %U32_20
  pusharg %A32_18
  pusharg fd
  bsr write
  poparg %S32_21:S32
  mov %out = %S32_21
  pusharg %out
  ret

######################################################################
# PSEUDO WASI
######################################################################

.fun $wasi$print_i32_ln NORMAL [] = [A32 S32]
.bbl %start
  poparg dummy:A32
  poparg n:S32
  mov %S32_2:S32 = 1
  pusharg n
  pusharg %S32_2
  bsr write_d
  poparg %S32_1:S32
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S32_3:S32
  ret

######################################################################
# REAL WASI
######################################################################

# (mem-addr, fd, start-of-array-offset, length-of-array, result-offset) -> errro
.fun $wasi$fd_write NORMAL [S32] = [A32 S32 S32 S32 S32]

  .bbl %start
    poparg mem_base:A32
    poparg fd:S32
    poparg array_offset:S32
    poparg array_size:S32
    poparg result_offset:S32

    lea array:A32 mem_base array_offset
    lea result:A32 mem_base result_offset
    mov count:S32 0:S32
    mov errno:S32 0:S32
    bra check

  .bbl loop
    ld buf_offset:S32 array 0:U32
    lea buf:A32 mem_base buf_offset
    ld len:U32 array 4:U32
    lea array array 8:U32
    sub array_size array_size 1
    pusharg len
    pusharg buf
    pusharg fd
    bsr write
    poparg errno
    blt errno 0 epilog
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
.fun $wasi$args_sizes_get NORMAL [S32] = [A32 S32 S32]
.bbl prolog
    poparg mem_base:A32
    poparg argc_offset:S32
    poparg total_size_offset:S32
    # handle argc
    ld.mem argc:S32 global_argc 0
    st mem_base argc_offset argc
    # handle total-size
    mov total_size:S32 0:S32
    ld.mem argv:A32 global_argv 0
.bbl loop_argv
    beq argc 0 done_argv
    sub argc argc 1

    ld s:A32 argv 0
    lea argv argv 4

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
.fun $wasi$args_get NORMAL [S32] = [A32 S32 S32]
.bbl prolog
    poparg mem_base:A32
    poparg argv_offset:S32
    poparg string_data_offset:S32
    ld.mem argv:A32 global_argv 0
    ld.mem argc:S32 global_argc 0

.bbl loop_argv
    beq argc 0 done_argv
    sub argc argc 1
    st mem_base argv_offset string_data_offset
    add argv_offset argv_offset 4
    ld s:A32 argv 0
    lea argv argv 4

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




