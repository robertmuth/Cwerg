# Prepend this to cwerg IR code  before running it through CodeGenA32/codegen.py

# syscall overview here: https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md
.fun a32_syscall_write SIGNATURE [S32] = [S32 A32 U32]
.fun a32_syscall_read SIGNATURE [S32] = [S32 A32 U32]
.fun a32_syscall_open SIGNATURE [S32] = [A32 S32 S32]
.fun a32_syscall_close SIGNATURE [S32] = [S32]
.fun a32_syscall_lseek SIGNATURE [S32] = [S32 S32 S32]
.fun a32_syscall_brk SIGNATURE [A32] = [A32]
.fun a32_syscall_exit SIGNATURE [] = [U32]


############################################################
# Syscall wrappers
############################################################

.fun exit NORMAL [] = [U32]
.bbl start
    poparg out:U32
    pusharg out
    syscall a32_syscall_exit 1:U32
    trap

.fun brk NORMAL [A32] = [A32]
.bbl start
    poparg addr:A32
    pusharg addr
    syscall a32_syscall_brk 45:U32
    poparg res:A32
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

.fun close NORMAL [S32] = [S32]
.bbl start
    poparg fh:S32
    pusharg fh
    syscall a32_syscall_close 6:U32
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
