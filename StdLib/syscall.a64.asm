# Prepend this to cwerg IR code  before running it through CodeGenA64/codegen.py

# syscall overview here: https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md

# This linkerdef may go away since we can query it with the xbrk syscall
.mem $$rw_data_end 8 EXTERN

.fun a64_syscall_close SIGNATURE [S32] = [S32]
.fun a64_syscall_exit SIGNATURE [] = [S32]
.fun a64_syscall_getpid SIGNATURE [S32] = []
.fun a64_syscall_kill SIGNATURE [S32] = [S32 S32]
.fun a64_syscall_lseek SIGNATURE [S64] = [S32 S64 S32]
.fun a64_syscall_open_at SIGNATURE [S32] = [S32 A64 S32 S32]
.fun a64_syscall_read SIGNATURE [S64] = [S32 A64 U64]
.fun a64_syscall_write SIGNATURE [S64] = [S32 A64 U64]
.fun a64_syscall_xbrk SIGNATURE [A64] = [A64]


############################################################
# Syscall wrappers
############################################################
.fun close NORMAL [S32] = [S32]
.bbl start
    poparg fh:S32
    pusharg fh
    syscall a64_syscall_close 57:U32
    poparg res:S32
    pusharg res
    ret

.fun exit NORMAL [] = [S32]
.bbl start
    poparg out:S32
    pusharg out
    syscall a64_syscall_exit 93:U32
    trap

.fun getpid NORMAL [S32] = []
.bbl start
    syscall a64_syscall_getpid 172:U32
    poparg res:S32
    pusharg res
    ret

.fun kill NORMAL [S32] = [S32 S32]
.bbl start
    poparg pid:S32
    poparg sig:S32
    pusharg sig
    pusharg pid
    syscall a64_syscall_kill 129:U32
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
    syscall a64_syscall_lseek 62:U32
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
    syscall a64_syscall_open_at 56:U32
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
    syscall a64_syscall_read 63:U32
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
    syscall a64_syscall_write 64:U32
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
    syscall a64_syscall_xbrk 214:U32
    poparg res:A64
    pusharg res
    ret
