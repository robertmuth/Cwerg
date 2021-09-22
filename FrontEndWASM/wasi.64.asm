# based on
# https://github.com/WebAssembly/WASI/blob/main/phases/snapshot/docs.md

######################################################################
# HELPERS CLONED FROM StdLib
######################################################################

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

.fun write_lu NORMAL [S64] = [S32 U64]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg val:U64
.stk buffer 1 16
  .reg U64 [pos]
  lea %A64_1:A64 = buffer
  mov pos = 16

.bbl while_1
  sub %U64_2:U64 = pos 1
  mov pos = %U64_2
  rem %U32_3:U64 = val 10
  add %U32_4:U64 = 48:U64 %U32_3
  conv %S8_5:S8 = %U32_4
  lea %A64_6:A64 = buffer
  lea %A64_7:A64 = %A64_6 pos
  st %A64_7 0 = %S8_5
  div %U32_8:U64 = val 10
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


.fun write_ld NORMAL [S64] = [S32 S64]
.reg S64 [%out]

.bbl %start
  poparg fd:S32
  poparg sval:S64
  ble 0:S64 sval if_2_true
  bra if_2_end

.bbl if_2_true
  conv %U32_1:U64 = sval
  pusharg %U32_1
  pusharg fd
  bsr write_lu
  poparg %S64_2:S64
  mov %out = %S64_2
  pusharg %out
  ret

.bbl if_2_end
  .reg U64 [val]
  sub %S32_3:S64 = 0  sval
  conv val = %S32_3
.stk buffer 1 32
  .reg U64 [pos]
  lea %A64_5:A64 = buffer
  mov pos = 32

.bbl while_1
  sub pos = pos 1
  rem %U32_7:U64 = val 10
  add %U32_8:U64 = 48:U64 %U32_7
  conv %S8_9:S8 = %U32_8
  lea %A64_10:A64 = buffer
  lea %A64_11:A64 = %A64_10 pos
  st %A64_11 0 = %S8_9
  div val = val 10

.bbl while_1_cond
  bne val 0 while_1

  sub pos = pos 1
  lea %A64_15:A64 = buffer pos
  mov %S8_16:S8 = 45
  st %A64_15 0 = %S8_16
  lea %A64_18:A64 = buffer pos
  lea %A64_19:A64 = buffer
  sub %U64_20:U64 = 32:U64 pos
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
# WASM MEMORY MANAGEMENT
######################################################################

.mem __memory_base 8 RW
  .data 8 [0]    # base
  .data 8 [0]    # top


.fun __wasi_init NORMAL [] = []
.bbl prolog
   # init memory
   pusharg 0:A64
   bsr xbrk
   poparg addr:A64
   st.mem __memory_base 0 addr
   st.mem __memory_base 8 addr
   # init pre-open dirs
   .stk cwd 1 1024
   lea.stk addr cwd 0
   pusharg 1024:U64
   pusharg addr
   bsr getcwd
   poparg res:S32
   # fd3
   pusharg 0:S32 # mode
   pusharg 0:S32 # RDONLY
   pusharg addr
   bsr open
   poparg res
   beq res 3 next
   trap
 .bbl next
   # fd4
   pusharg 0:S32 # mode
   pusharg 0:S32 # RDONLY
   pusharg addr
   bsr open
   poparg res
   beq res 4 end
   trap
  .bbl end
   ret

.fun __memory_grow NORMAL [S32] = [S32]
.bbl prolog
    poparg size:S32
    ld.mem bot:U64 __memory_base 0
    ld.mem top:U64 __memory_base 8
    sub top top bot
    shr top top 16
    conv out:S32 top
    beq size 0 epilog

    conv usize:U32 size
    shl usize usize 16
    ld.mem atop:A64 __memory_base 8
    lea atop atop usize
    pusharg atop
    bsr xbrk
    poparg res:A64
    ble atop res success
    pusharg -1:S32
    ret

.bbl success
    st.mem __memory_base 8 atop

.bbl epilog
    pusharg out
    ret

######################################################################
# PSEUDO WASI
######################################################################

.fun $wasi$print_i64_ln NORMAL [] = [A64 S64]
.bbl %start
  poparg dummy:A64
  poparg n:S64
  mov %S32_2:S32 = 1
  pusharg n
  pusharg %S32_2
  bsr write_ld
  poparg %S64_1:S64
  mov %S32_4:S32 = 1
  mov %U8_5:U8 = 10
  pusharg %U8_5
  pusharg %S32_4
  bsr write_c
  poparg %S64_3:S64
  ret

 .fun $wasi$print_i32_ln NORMAL [] = [A64 S32]
  .bbl %start
    poparg dummy:A64
    poparg n:S32
    conv n2:S64 n
    pusharg n2
    pusharg dummy
    bsr $wasi$print_i64_ln
    ret

.fun print_s_ln NORMAL [] = [A64]
.bbl %start
  poparg s:A64
  mov %S32_2:S32 = 1
  pusharg s
  pusharg %S32_2
  bsr write_s
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

.fun $wasi$path_open NORMAL [S32] = [A64 S32 S32 S32 S32 S32 S64 S64 S32 S32]
  .bbl %start
    poparg mem_base:A64
    poparg dirfd:S32
    poparg dirflags:S32
    poparg path_offset:S32
    poparg path_size:S32
    poparg oflags:S32
    poparg fs_rights_base:S64
    poparg fs_rights_inheriting:S64
    poparg fdflags:S32
    poparg result_offset:S32

  .stk buffer 1 1024
    lea.stk dst:A64 buffer 0
    lea src:A64 mem_base path_offset
    blt  path_size 1024:S32 copy
    pusharg -1:S32  # path too long
    ret
  .bbl loop
   ld b:U8 src 0
   lea src src 1
   st dst  0 b
   lea dst dst 1
   sub path_size path_size 1
  .bbl copy
    bne path_size 0 loop
    st dst 0 0:U32  # zero terminator

   mov mode:S32 420 # 0644
   mov flag:S32 0

   .reg S32 [f]
   and f oflags 1 # creat 0100 = 128
   shl f f 7
   or flag flag f

   and f oflags 4 # excl 0200  256
   shl f f 6
   or flag flag f

   and f oflags 8 # trunc 01000 512
   shl f f 6
   or flag flag f

   and f fdflags 1 # append 0x2000 1024
   shl f f 10
   or flag flag f

   .reg S64 [g]
   and g fs_rights_base 64 #  FD_WRITE
   cmpeq w:S32 0 1 g 0
   and g fs_rights_base 2 #  FD_READ
   cmpeq r:S32 0 1 g 0
   shl f w r      # readonly=0, writeonly=1, readwrite=2
   or flag flag f

   lea.stk dst buffer 0

   pusharg mode
   pusharg flag
   pusharg dst
   bsr open
   poparg fd:S32
   blt fd 0 end
   st mem_base result_offset fd
   mov fd 0
 .bbl end
   pusharg fd
   ret

.mem __unimplemented_path_filestat_get 8 RW
  .data 1 "path_filestat_get NYI\n\0"

.fun $wasi$path_filestat_get NORMAL [S32] = [A64 S32 S32 S32 S32 S32]
  .bbl prolog
    poparg mem_base:A64
    poparg fd:S32
    poparg flags:S32
    poparg path_offset:S32
    poparg path_size:S32
    poparg buf_offset:S32

    # TODO: unimplemented
    lea.mem msg:A64 __unimplemented_path_filestat_get 0
    pusharg msg
    pusharg 2:S32
    bsr write_s
    poparg dummy:S64
    trap
    pusharg -1:S32
    ret

.mem __unimplemented_path_unlink_file 8 RW
  .data 1 "path_unlink_file NYI\n\0"


.fun $wasi$path_unlink_file NORMAL [S32] = [A64 S32 S32 S32]
  .bbl prolog
    poparg mem_base:A64
    poparg fd:S32
    poparg path_offset:S32
    poparg path_size:S32

    # TODO: unimplemented
    lea.mem msg:A64 __unimplemented_path_unlink_file 0
    pusharg msg
    pusharg 2:S32
    bsr write_s
    poparg dummy:S64
    trap
    pusharg -1:S32
    ret

# (mem-addr, status) ->
.fun $wasi$proc_exit NORMAL [] = [A64 S32]
  .bbl %start
    poparg dummy:A64
    poparg status:S32
    pusharg status
    bsr exit
    ret

.fun $wasi$fd_close NORMAL [S32] = [A64 S32]
  .bbl %start
    poparg mem_base:A64
    poparg fd:S32
    pusharg fd
    bsr close
    poparg err:S32
    pusharg err
    ret

# Terrible hack we hard-code 2 path
# fd=3 -> "/"
# fd=4 -> "./"

.fun $wasi$fd_prestat_get NORMAL [S32] = [A64 S32 S32]
  .bbl %start
    poparg mem_base:A64
    poparg fd:S32
    poparg result_offset:S32
    lea result:A64 mem_base result_offset
  .bbl fd3
    bne fd 3:S32 fd4
    st result 0  0:U32 # __WASI_PREOPENTYPE_DIR
    st result 4  2:U32 # strlen("/") + 1
    pusharg 0:S32
    ret
  .bbl fd4
    bne fd 4:S32 bad
    st result 0  0:U32 # __WASI_PREOPENTYPE_DIR
    st result 4  3:U32 # strlen("./") + 1
    pusharg 0:S32
    ret
  .bbl bad
    pusharg 8:S32  # __WASI_ERRNO_BADF
    ret

.fun $wasi$fd_prestat_dir_name NORMAL [S32] = [A64 S32 S32 S32]
  .bbl %start
    poparg mem_base:A64
    poparg fd:S32
    poparg path_offset:S32
    poparg path_size:S32
    lea path:A64 mem_base path_offset
  .bbl fd3
    bne fd 3:S32 fd4
    st path 0 47:U8 # '/'
    st path 1 0:U8 #
    pusharg 0:S32
    ret
  .bbl fd4
    bne fd 4:S32 bad
    st path 0 46:U8  # '.'
    st path 1 47:U8  # '/'
    st path 2 0:U8  #
    pusharg 0:S32
    ret
  .bbl bad
    pusharg 8:S32  # __WASI_ERRNO_BADF
    ret

# struct stat {
#  0 	unsigned long	st_dev;
#  8	unsigned long	st_ino;
# 16	unsigned int	st_mode;
# 20 	unsigned int	st_nlink;
# 24 	unsigned int	st_uid;
# 28 	unsigned int	st_gid;
# 32 	unsigned long	st_rdev;
# 40 	unsigned long	__pad1;
# 48 	long		    st_size;
# 56 	int		        st_blksize;
# 60 	int		        __pad2;
# 64 	long		    st_blocks;
# 72 	long		    st_atime;
# 80 	unsigned long	st_atime_nsec;
# 88 	long		    st_mtime;
# 96 	unsigned long	st_mtime_nsec;
#104 	long		    st_ctime;
#112 	unsigned long	st_ctime_nsec;
#116 	unsigned int	__unused4;
#120 	unsigned int	__unused5;
# };


# struct fdstat {
# 0 fs_filetype
# 2 fs_flags
# 8 fs_rights_base
#16 fs_rights_inheriting
# }

.fun $wasi$fd_fdstat_get NORMAL [S32] = [A64 S32 S32]
  .bbl %start
    poparg mem_base:A64
    poparg fd:S32
    poparg result_offset:S32
    #
    pusharg 0:A64
    pusharg 3:U32 # F_GETFL
    pusharg fd
    bsr fcntl
    poparg res:S32
    ble 0:S32 res ok_fcntl
    pusharg res
    ret
  .bbl ok_fcntl
    .stk stat 8 256
    lea.stk stk_stat:A64 stat 0
    pusharg stk_stat
    pusharg fd
    bsr fstat
    poparg res
    ble 0:S32 res ok_fstat
    pusharg res
    ret
  .bbl ok_fstat
    lea wasi_fdstat:A64 mem_base result_offset
    ld mode:U32 stk_stat 16
    shr mode mode 12
    mov fs_filetype:U8 0
    cmpeq fs_filetype 1:U8 fs_filetype 6:U32 mode   # __WASI_FILETYPE_BLOCK_DEVICE
    cmpeq fs_filetype 2:U8 fs_filetype 2:U32 mode   # __WASI_FILETYPE_CHARACTER_DEVICE
    cmpeq fs_filetype 3:U8 fs_filetype 4:U32 mode   # __WASI_FILETYPE_DIRECTORY
    cmpeq fs_filetype 4:U8 fs_filetype 8:U32 mode   # __WASI_FILETYPE_REGULAR_FILE
    cmpeq fs_filetype 7:U8 fs_filetype 10:U32 mode  # __WASI_FILETYPE_SYMBOLIC_LINK
    mov fs_flags:U16 0
    st wasi_fdstat 0 fs_filetype
    st wasi_fdstat 2 fs_flags
    st wasi_fdstat 8 -1:S64  # fs_rights_base
    st wasi_fdstat 16 -1:S64 # fs_rights_inheriting;
    pusharg 0:S32
    ret

.mem __unimplemented_fd_fdstat_set_flags 8 RW
  .data 1 "fd_fdstat_set_flags NYI\n\0"

.fun $wasi$fd_fdstat_set_flags NORMAL [S32] = [A64 S32 S32]
  .bbl prolog
    poparg mem_base:A64
    poparg fd:S32
    poparg flags:S32
    # TODO: unimplemented
    lea.mem msg:A64 __unimplemented_fd_fdstat_set_flags 0
    pusharg msg
    pusharg 2:S32
    bsr write_s
    poparg dummy:S64
    trap
    pusharg -1:S32
    ret

.mem __unimplemented_fd_seek 8 RW
  .data 1 "fd_seek NYI\n\0"

.fun $wasi$fd_seek NORMAL [S32] = [A64 S32 S64 S32 S32]
  .bbl %start
    poparg mem_base:A64
    poparg fd:S32
    poparg delta:S64
    poparg whence:S32
    poparg result_offset:S32
    # TODO: unimplemented
    lea.mem msg:A64 __unimplemented_fd_seek 0
    pusharg msg
    pusharg 2:S32
    bsr write_s
    poparg dummy:S64

    trap
    pusharg -1:S32
    ret

.fun $wasi$fd_read NORMAL [S32] = [A64 S32 S32 S32 S32]

  .bbl %start
    poparg mem_base:A64
    poparg fd:S32
    poparg array_offset:S32
    poparg array_size:S32
    poparg result_offset:S32

    lea array:A64 mem_base array_offset
    mov count:S64 0:S64
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
    bsr read
    poparg errno:S64
    ble 0:S64 errno success
    conv errno32:S32 errno
    pusharg errno32
    ret
  .bbl success
    add count count errno
    conv actual_len64:U64 errno
    blt actual_len64 len64 epilog
  .bbl check
    blt 0:S32 array_size loop
  .bbl epilog
    conv count32:S32 count
    lea result:A64 mem_base result_offset
    st result 0:U32 count32
    pusharg 0:S32
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


