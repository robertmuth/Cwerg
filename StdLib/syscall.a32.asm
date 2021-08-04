# Prepend this to cwerg IR code  before running it through CodeGenA32/codegen.py

# syscall overview here: https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md

# This linkerdef may go away since we can query it with the xbrk syscall
.mem $$rw_data_end 4 BUILTIN

.fun a32_syscall_clock_gettime SIGNATURE [S32] = [S32 A32]
.fun a32_syscall_close SIGNATURE [S32] = [S32]
.fun a32_syscall_exit SIGNATURE [] = [S32]
.fun a32_syscall_getpid SIGNATURE [S32] = []
.fun a32_syscall_kill SIGNATURE [S32] = [S32 S32]
.fun a32_syscall_lseek SIGNATURE [S32] = [S32 S32 S32]
.fun a32_syscall_open SIGNATURE [S32] = [A32 S32 S32]
.fun a32_syscall_read SIGNATURE [S32] = [S32 A32 U32]
.fun a32_syscall_write SIGNATURE [S32] = [S32 A32 U32]
.fun a32_syscall_xbrk SIGNATURE [A32] = [A32]


############################################################
# Syscall wrappers
############################################################
.fun clock_gettime NORMAL [S32] = [S32 A32]
.bbl start
    poparg clk_id:S32
    poparg timespec:A32
    pusharg timespec
    pusharg clk_id
    syscall a32_syscall_clock_gettime 0xe4:U32
    poparg res:S32
    pusharg res
    ret

.fun close NORMAL [S32] = [S32]
.bbl start
    poparg fh:S32
    pusharg fh
    syscall a32_syscall_close 6:U32
    poparg res:S32
    pusharg res
    ret

.fun exit NORMAL [] = [S32]
.bbl start
    poparg out:S32
    pusharg out
    syscall a32_syscall_exit 1:U32
    trap

.fun getpid NORMAL [S32] = []
.bbl start
    syscall a32_syscall_getpid 20:U32
    poparg res:S32
    pusharg res
    ret

.fun kill NORMAL [S32] = [S32 S32]
.bbl start
    poparg pid:S32
    poparg sig:S32
    pusharg sig
    pusharg pid
    syscall a32_syscall_kill 37:U32
    poparg res:S32
    pusharg res
    ret

.fun lseek NORMAL [S32] = [S32 S32 S32]
.bbl start
    poparg fd:S32
    poparg offset:S32
    poparg mode:S32
    pusharg mode
    pusharg offset
    pusharg fd
    syscall a32_syscall_lseek 19:U32
    poparg res:S32
    pusharg res
    ret

.fun open NORMAL [S32] = [A32 S32 S32]
.bbl start
    poparg path:A32
    poparg flags:S32
    poparg mode:S32
    pusharg mode
    pusharg flags
    pusharg path
    syscall a32_syscall_open 5:U32
    poparg res:S32
    pusharg res
    ret

.fun read NORMAL [S32] = [S32 A32 U32]
.bbl start
    poparg fh:S32
    poparg buf:A32
    poparg len:U32
    pusharg len
    pusharg buf
    pusharg fh
    syscall a32_syscall_read 3:U32
    poparg res:S32
    pusharg res
    ret

.fun write NORMAL [S32] = [S32 A32 U32]
.bbl start
    poparg fh:S32
    poparg buf:A32
    poparg len:U32
    pusharg len
    pusharg buf
    pusharg fh
    syscall a32_syscall_write 4:U32
    poparg res:S32
    pusharg res
    ret

# Note the syscall behaves differently from the library function:
# The Linux system call returns the new program break on success. On failure,
# the system call returns the current break.
# It also return the current program break when give zero as an argument
.fun xbrk NORMAL [A32] = [A32]
.bbl start
    poparg addr:A32
    pusharg addr
    syscall a32_syscall_xbrk 45:U32
    poparg res:A32
    pusharg res
    ret
