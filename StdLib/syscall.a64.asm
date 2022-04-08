# Prepend this to cwerg IR code  before running it through CodeGenA64/codegen.py

# syscall overview here: https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md

# This linkerdef may go away since we can query it with the xbrk syscall
.mem $$rw_data_end 8 BUILTIN

.fun a64_syscall_clock_gettime SIGNATURE [S32] = [S32 A64]
.fun a64_syscall_close SIGNATURE [S32] = [S32]
.fun a64_syscall_exit SIGNATURE [] = [S32]
.fun a64_syscall_fcntl SIGNATURE [S32] = [S32 U32 A64]
.fun a64_syscall_fstat SIGNATURE [S32] = [S32 A64]
.fun a64_syscall_getcwd SIGNATURE [S32] = [A64 U64]
.fun a64_syscall_getpid SIGNATURE [S32] = []
.fun a64_syscall_kill SIGNATURE [S32] = [S32 S32]
.fun a64_syscall_clone SIGNATURE [S32] = [U64 A64 A64 A64 A64]
.fun a64_syscall_lseek SIGNATURE [S64] = [S32 S64 S32]
.fun a64_syscall_open_at SIGNATURE [S32] = [S32 A64 S32 S32]
.fun a64_syscall_read SIGNATURE [S64] = [S32 A64 U64]
.fun a64_syscall_write SIGNATURE [S64] = [S32 A64 U64]
.fun a64_syscall_xbrk SIGNATURE [A64] = [A64]
.fun a64_syscall_nanosleep SIGNATURE [S32] = [A64 A64]
.fun a64_syscall_waitid SIGNATURE [S32] = [S32 S32 A64 S32 A64]
.fun a64_syscall_yield SIGNATURE [S32] = []

.fun a64_thread_function SIGNATURE [] = [U64]

############################################################
# Syscall wrappers
############################################################
.fun clock_gettime NORMAL [S32] = [S32 A64]
.bbl start
    poparg clk_id:S32
    poparg timespec:A64
    pusharg timespec
    pusharg clk_id
    syscall a64_syscall_clock_gettime 0x71:U32
    poparg res:S32
    pusharg res
    ret

.fun nanosleep NORMAL [S32] = [A64 A64]
.bbl start
    poparg spec1:A64
    poparg spec2:A64
    pusharg spec2
    pusharg spec1
    syscall a64_syscall_nanosleep 101:U8
    poparg res:S32
    pusharg res
    ret

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

.fun fcntl NORMAL [S32] = [S32 U32 A64]
.bbl start
    poparg fd:S32
    poparg cmd:U32
    poparg arg:A64
    pusharg arg
    pusharg cmd
    pusharg fd
    syscall a64_syscall_fcntl 25:U32
    poparg res:S32
    pusharg res
    ret

.fun fstat NORMAL [S32] = [S32 A64]
.bbl start
    poparg fd:S32
    poparg stat:A64
    pusharg stat
    pusharg fd
    syscall a64_syscall_fstat 80:U32
    poparg res:S32
    pusharg res
    ret

.fun getcwd NORMAL [S32] = [A64 U64]
.bbl start
    poparg buffer:A64
    poparg size:U64
    pusharg size
    pusharg buffer
    syscall a64_syscall_getcwd 17:U32
    poparg res:S32
    pusharg res
    ret

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

.fun clone NORMAL [S32] = [U64 A64 A64 A64 A64]
.bbl start
    poparg flags:U64
    poparg stack:A64
    poparg ptid:A64
    poparg ctid:A64
    poparg regs:A64
    pusharg regs
    pusharg ctid
    pusharg ptid
    pusharg stack
    pusharg flags
    syscall a64_syscall_clone 220:U32
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

.fun yield NORMAL [S32] = []
.bbl start
    syscall a64_syscall_yield 124:U8
    poparg res:S32
    pusharg res
    ret

.fun spawn NORMAL [S32] = [C64 A64 A64 U64 U64]   
.bbl entry
    poparg proc:C64
    poparg new_stack:A64
    poparg new_tls:A64
    poparg user_arg:U64
    poparg flags:U64
    # align stack 
    bitcast stk:U64 new_stack
    sub stk stk 16  # make space for two parameters
    and stk stk 0xfffffffffffffff0  # 16 byte aligned
    bitcast new_stack stk
    # We need to save this to the new stack as there is not guarantee
    # that these values will end up in (preserved) registers. (see below)
    st new_stack 8 proc
    st new_stack 0 user_arg
    #
    pusharg 0:A64
    pusharg 0:A64
    pusharg 0:A64
    pusharg new_stack
    pusharg flags
    syscall a64_syscall_clone 220:U32
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
    getsp sp:A64
    ld user_arg sp 0
    ld proc sp 8
    pusharg user_arg
    jsr proc a64_thread_function
    pusharg 0:S32
    syscall a64_syscall_exit 93:U8
    trap # unreachable 
    pusharg 0:S32
    ret