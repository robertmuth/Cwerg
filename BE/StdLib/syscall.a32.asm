# Prepend this to cwerg IR code  before running it through CodeGenA32/codegen.py

# syscall overview here: https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md

# This linkerdef may go away since we can query it with the xbrk syscall
.mem $$rw_data_end 4 BUILTIN

.fun a32_syscall_clock_gettime SIGNATURE [S32] = [S32 A32]
.fun a32_syscall_close SIGNATURE [S32] = [S32]
.fun a32_syscall_exit SIGNATURE [] = [S32]
.fun a32_syscall_fcntl SIGNATURE [S32] = [S32 U32 U32]
.fun a32_syscall_ioctl SIGNATURE [S32] = [S32 U32 U32]
.fun a32_syscall_fstat SIGNATURE [S32] = [S32 A32]
.fun a32_syscall_getcwd SIGNATURE [S32] = [A32 U32]
.fun a32_syscall_getpid SIGNATURE [S32] = []
.fun a32_syscall_kill SIGNATURE [S32] = [S32 S32]
.fun a32_syscall_clone SIGNATURE [S32] = [U32 A32 A32 A32 A32]
.fun a32_syscall_lseek SIGNATURE [S32] = [S32 S32 S32]
.fun a32_syscall_open SIGNATURE [S32] = [A32 S32 S32]
.fun a32_syscall_read SIGNATURE [S32] = [S32 A32 U32]
.fun a32_syscall_write SIGNATURE [S32] = [S32 A32 U32]
.fun a32_syscall_xbrk SIGNATURE [A32] = [A32]
.fun a32_syscall_nanosleep SIGNATURE [S32] = [A32 A32]
.fun a32_syscall_waitid SIGNATURE [S32] = [S32 S32 A32 S32 A32]
.fun a32_syscall_yield SIGNATURE [S32] = []

.fun a32_thread_function SIGNATURE [] = [U32]

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

.fun nanosleep NORMAL [S32] = [A32 A32]
.bbl start
    poparg spec1:A32
    poparg spec2:A32
    pusharg spec2
    pusharg spec1
    syscall a32_syscall_nanosleep 162:U8
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

.fun fcntl NORMAL [S32] = [S32 U32 U32]
.bbl start
    poparg fd:S32
    poparg cmd:U32
    poparg arg:U32
    pusharg arg
    pusharg cmd
    pusharg fd
    syscall a32_syscall_fcntl 55:U32
    poparg res:S32
    pusharg res
    ret

.fun ioctl NORMAL [S32] = [S32 U32 U32]
.bbl start
    poparg fd:S32
    poparg cmd:U32
    poparg arg:U32
    pusharg arg
    pusharg cmd
    pusharg fd
    syscall a32_syscall_fcntl 54:U32
    poparg res:S32
    pusharg res
    ret

.fun fstat NORMAL [S32] = [S32 A32]
.bbl start
    poparg fd:S32
    poparg stat:A32
    pusharg stat
    pusharg fd
    syscall a32_syscall_fstat 108:U32
    poparg res:S32
    pusharg res
    ret

.fun getcwd NORMAL [S32] = [A32 U32]
.bbl start
    poparg buffer:A32
    poparg size:U32
    pusharg size
    pusharg buffer
    syscall a32_syscall_getcwd 183:U32
    poparg res:S32
    pusharg res
    ret

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

.fun clone NORMAL [S32] = [U32 A32 A32 A32 A32]
.bbl start
    poparg flags:U32
    poparg stack:A32
    poparg ptid:A32
    poparg ctid:A32
    poparg regs:A32
    pusharg regs
    pusharg ctid
    pusharg ptid
    pusharg stack
    pusharg flags
    syscall a32_syscall_clone 120:U32
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

# Note the sbrk syscall behaves differently from the library function:
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

.fun waitid NORMAL [S32] = [S32 S32 A32 S32 A32]
.bbl entry
    poparg which:S32
    poparg pid:S32
    poparg infop:A32
    poparg options:S32
    poparg ru:A32
    pusharg ru
    pusharg options
    pusharg infop
    pusharg pid
    pusharg which
    syscall a32_syscall_waitid 280:U16
    poparg res:S32
    pusharg res
    ret

.fun yield NORMAL [S32] = []
.bbl start
    syscall a32_syscall_yield 158:U8
    poparg res:S32
    pusharg res
    ret

.fun spawn NORMAL [S32] = [C32 A32 A32 U32 U32]
.bbl entry
    poparg proc:C32
    poparg new_stack:A32
    poparg new_tls:A32
    poparg user_arg:U32
    poparg flags:U32
    # align stack
    bitcast stk:U32 new_stack
    sub stk stk 16  # make space for two parameters
    and stk stk 0xfffffff8  # 8 byte aligned
    bitcast new_stack stk
    # We need to save this to the new stack as there is not guarantee
    # that these values will end up in (preserved) registers. (see below)
    st new_stack 4 proc
    st new_stack 0 user_arg
    #
    pusharg 0:A32
    pusharg 0:A32
    pusharg 0:A32
    pusharg new_stack
    pusharg flags
    syscall a32_syscall_clone 120:U32
    poparg ret:S32
    beq ret 0 child
    pusharg ret
    ret

.bbl child
    # Why do we have to save the user_arg temporarily onto the new stack?
    # If user_arg ends up in register we might get lucky because the register
    # are presumably preserved when we reach here.
    # But if user_arg is spilled onto the old stack it is not clear if we can see it
    # at this point.
    # NOTE: the syscall pops two regs of the stack. We have to compensate for this
    getsp sp:A32
    ld user_arg sp -8
    ld proc sp -4
    # trap
    pusharg user_arg
    jsr proc a32_thread_function
    pusharg 0:S32
    syscall a32_syscall_exit 1:U8
    trap # unreachable
    pusharg 0:S32
    ret