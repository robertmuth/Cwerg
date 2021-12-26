# Prepend this to cwerg IR code  before running it through CodeGenA64/codegen.py

# syscall overview here: https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md

# This linkerdef may go away since we can query it with the xbrk syscall
.mem $$rw_data_end 8 BUILTIN

.fun x64_syscall_clock_gettime SIGNATURE [S32] = [S32 A64]
.fun x64_syscall_close SIGNATURE [S32] = [S32]
.fun x64_syscall_exit SIGNATURE [] = [S32]
.fun x64_syscall_fcntl SIGNATURE [S32] = [S32 U32 A64]
.fun x64_syscall_fstat SIGNATURE [S32] = [S32 A64]
.fun x64_syscall_getcwd SIGNATURE [S32] = [A64 U64]
.fun x64_syscall_getpid SIGNATURE [S32] = []
.fun x64_syscall_kill SIGNATURE [S32] = [S32 S32]
.fun x64_syscall_lseek SIGNATURE [S64] = [S32 S64 S32]
.fun x64_syscall_open_at SIGNATURE [S32] = [S32 A64 S32 S32]
.fun x64_syscall_read SIGNATURE [S64] = [S32 A64 U64]
.fun x64_syscall_write SIGNATURE [S64] = [S32 A64 U64]
.fun x64_syscall_xbrk SIGNATURE [A64] = [A64]


############################################################
# Syscall wrappers
############################################################
.fun clock_gettime NORMAL [S32] = [S32 A64]
.bbl start
    poparg clk_id:S32
    poparg timespec:A64
    pusharg timespec
    pusharg clk_id
    syscall x64_syscall_clock_gettime 228:U8
    poparg res:S32
    pusharg res
    ret

.fun close NORMAL [S32] = [S32]
.bbl start
    poparg fh:S32
    pusharg fh
    syscall x64_syscall_close 3:U8
    poparg res:S32
    pusharg res
    ret

.fun exit NORMAL [] = [S32]
.bbl start
    poparg out:S32
    pusharg out
    syscall x64_syscall_exit 60:U8
    trap

.fun fcntl NORMAL [S32] = [S32 U32 A64]
.bbl start
    poparg fd:S32
    poparg cmd:U32
    poparg arg:A64
    pusharg arg
    pusharg cmd
    pusharg fd
    syscall x64_syscall_fcntl 72:U8
    poparg res:S32
    pusharg res
    ret

.fun fstat NORMAL [S32] = [S32 A64]
.bbl start
    poparg fd:S32
    poparg stat:A64
    pusharg stat
    pusharg fd
    syscall x64_syscall_fstat 5:U8
    poparg res:S32
    pusharg res
    ret

.fun getcwd NORMAL [S32] = [A64 U64]
.bbl start
    poparg buffer:A64
    poparg size:U64
    pusharg size
    pusharg buffer
    syscall x64_syscall_getcwd 79:U8
    poparg res:S32
    pusharg res
    ret

.fun getpid NORMAL [S32] = []
.bbl start
    syscall x64_syscall_getpid 39:U8
    poparg res:S32
    pusharg res
    ret

.fun kill NORMAL [S32] = [S32 S32]
.bbl start
    poparg pid:S32
    poparg sig:S32
    pusharg sig
    pusharg pid
    syscall x64_syscall_kill 62:U8
    poparg res:S32
    pusharg res
    ret

.fun lseek NORMAL [S64] = [S32 S64 S32]
.bbl start
    poparg fd:S32
    poparg offset:S64
    poparg mode:S32
    pusharg mode
    pusharg offset
    pusharg fd
    syscall x64_syscall_lseek 8:U8
    poparg res:S64
    pusharg res
    ret

.fun open NORMAL [S32] = [A64 S32 S32]
.bbl start
    poparg path:A64
    poparg flags:S32
    poparg mode:S32
    pusharg mode
    pusharg flags
    pusharg path
    pusharg -100:S32
    syscall x64_syscall_open_at 2:U8
    poparg res:S32
    pusharg res
    ret

.fun read NORMAL [S64] = [S32 A64 U64]
.bbl start
    poparg fh:S32
    poparg buf:A64
    poparg len:U64
    pusharg len
    pusharg buf
    pusharg fh
    syscall x64_syscall_read 0:U8
    poparg res:S64
    pusharg res
    ret

.fun write NORMAL [S64] = [S32 A64 U64]
.bbl start
    poparg fh:S32
    poparg buf:A64
    poparg len:U64
    pusharg len
    pusharg buf
    pusharg fh
    syscall x64_syscall_write 1:U8
    poparg res:S64
    pusharg res
    ret

# Note the syscall behaves differently from the library function:
# The Linux system call returns the new program break on success. On failure,
# the system call returns the current break.
# It also return the current program break when give zero as an argument
.fun xbrk NORMAL [A64] = [A64]
.bbl start
    poparg addr:A64
    pusharg addr
    syscall x64_syscall_xbrk 12:U8
    poparg res:A64
    pusharg res
    ret
