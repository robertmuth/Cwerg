# Prepend this to cwerg IR code  before running it through CodeGenA64/codegen.py

# syscall overview here: https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md

# This linkerdef may go away since we can query it with the xbrk syscall
.mem $$rw_data_end 8 BUILTIN

############################################################
# Syscall wrappers
############################################################
.fun clock_gettime NORMAL [S32] = [S32 A64]
.bbl start
    poparg clk_id:S32
    poparg timespec:A64
    pusharg timespec
    pusharg clk_id
    syscall clock_gettime 228:U8
    poparg res:S32
    pusharg res
    ret

.fun nanosleep NORMAL [S32] = [A64 A64]
.bbl start
    poparg spec1:A64
    poparg spec2:A64
    pusharg spec2
    pusharg spec1
    syscall nanosleep 35:U8
    poparg res:S32
    pusharg res
    ret

.fun close NORMAL [S32] = [S32]
.bbl start
    poparg fh:S32
    pusharg fh
    syscall close 3:U8
    poparg res:S32
    pusharg res
    ret

.fun exit NORMAL [] = [S32]
.bbl start
    poparg out:S32
    pusharg out
    syscall exit 60:U8
    trap

.fun fcntl NORMAL [S64] = [S32 U32 U64]
.bbl start
    poparg fd:S32
    poparg cmd:U32
    poparg arg:U64
    pusharg arg
    pusharg cmd
    pusharg fd
    syscall fcntl 72:U8
    poparg res:S64
    pusharg res
    ret

.fun ioctl NORMAL [S64] = [S32 U32 U64]
.bbl start
    poparg fd:S32
    poparg cmd:U32
    poparg arg:U64
    pusharg arg
    pusharg cmd
    pusharg fd
    syscall ioctl 16:U8
    poparg res:S64
    pusharg res
    ret

.fun fstat NORMAL [S32] = [S32 A64]
.bbl start
    poparg fd:S32
    poparg stat:A64
    pusharg stat
    pusharg fd
    syscall fstat 5:U8
    poparg res:S32
    pusharg res
    ret

.fun getcwd NORMAL [S32] = [A64 U64]
.bbl start
    poparg buffer:A64
    poparg size:U64
    pusharg size
    pusharg buffer
    syscall getcwd 79:U8
    poparg res:S32
    pusharg res
    ret

.fun getpid NORMAL [S32] = []
.bbl start
    syscall getpid 39:U8
    poparg res:S32
    pusharg res
    ret

.fun kill NORMAL [S32] = [S32 S32]
.bbl start
    poparg pid:S32
    poparg sig:S32
    pusharg sig
    pusharg pid
    syscall kill 62:U8
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
    syscall lseek 8:U8
    poparg res:S64
    pusharg res
    ret


.fun openat NORMAL [S32] = [S32 A64 S32 S32]
.bbl start
    poparg dirfd:S32
    poparg path:A64
    poparg flags:S32
    poparg mode:S32
    pusharg mode
    pusharg flags
    pusharg path
    pusharg dirfd
    syscall openat 257:U16
    poparg res:S32
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
    bsr openat
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
    syscall read 0:U8
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
    syscall write 1:U8
    poparg res:S64
    pusharg res
    ret

# Note the sbrk syscall behaves differently from the library function:
# The Linux system call returns the new program break on success. On failure,
# the system call returns the current break.
# It also return the current program break when give zero as an argument
.fun xbrk NORMAL [A64] = [A64]
.bbl start
    poparg addr:A64
    pusharg addr
    syscall xbrk 12:U8
    poparg res:A64
    pusharg res
    ret

.fun waitid NORMAL [S32] = [S32 S32 A64 S32 A64]
.bbl entry
    poparg which:S32
    poparg pid:S32
    poparg infop:A64
    poparg options:S32
    poparg ru:A64
    pusharg ru
    pusharg options
    pusharg infop
    pusharg pid
    pusharg which
    syscall waitid 247:U8
    poparg res:S32
    pusharg res
    ret

.fun yield NORMAL [S32] = []
.bbl start
    syscall yield 24:U8
    poparg res:S32
    pusharg res
    ret

.fun x64_syscall_exit SIGNATURE [] = [S32]
.fun x64_syscall_clone SIGNATURE [S32] = [U64 A64 A64 A64 A64]
.fun x64_thread_function SIGNATURE [] = [U64]


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
    syscall x64_syscall_clone 56:U32
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
    lea sp sp -16 # compensate for the syscall poping 16 bytes off the stack
               # needs to be adjusted when the syscall expansion changes
    ld user_arg sp 0
    # ld proc sp 8
    pusharg user_arg
    jsr proc x64_thread_function
    pusharg 0:S32
    syscall x64_syscall_exit 60:U8
    trap # unreachable
    pusharg 0:S32
    ret

.fun socket NORMAL [S32] = [U32 U32 U32]
.bbl entry
    poparg domain:U32
    poparg type:U32
    poparg protocol:U32
    pusharg protocol
    pusharg type
    pusharg domain
    syscall socket 41:U8
    poparg res:S32
    pusharg res
    ret

# addr and addrlen are in/out parameters and nullable
.fun bind NORMAL [S32] = [S32 A64 U32]
.bbl entry
    poparg sockfd:S32
    poparg addr:A64
    poparg addrlen:U32
    pusharg addrlen
    pusharg addr
    pusharg sockfd
    syscall bind 49:U8
    poparg res:S32
    pusharg res
    ret

.fun listen NORMAL [S32] = [S32 U32]
.bbl entry
    poparg sockfd:S32
    poparg backlog:U32
    pusharg backlog
    pusharg sockfd
    syscall listen 50:U8
    poparg res:S32
    pusharg res
    ret

.fun accept4 NORMAL [S32] = [S32 U64 U64 U32]
.bbl entry
    poparg sockfd:S32
    poparg addr:U64
    poparg addrlen:U64
    poparg flags:U32
    pusharg flags
    pusharg addrlen
    pusharg addr
    pusharg sockfd
    syscall accept4 288:U16
    poparg res:S32
    pusharg res
    ret

.fun sendto NORMAL [S64] = [S32 A64 U64 U32 U64 U32]
.bbl entry
    poparg sockfd:S32
    poparg buf:A64
    poparg len:U64
    poparg flags:U32
    poparg dest_addr:U64
    poparg dest_addrlen:U32
    pusharg dest_addrlen
    pusharg dest_addr
    pusharg flags
    pusharg len
    pusharg buf
    pusharg sockfd
    syscall sendto 44:U16
    poparg res:S64
    pusharg res
    ret

.fun setsockopt NORMAL [S32] = [S32 U32 U32 A64 U32]
.bbl entry
    poparg sockfd:S32
    poparg level:U32
    poparg optname:U32
    poparg optval:A64
    poparg optlen:U32
    pusharg optlen
    pusharg optval
    pusharg optname
    pusharg level
    pusharg sockfd
    syscall setsockopt 54:U8
    poparg res:S32
    pusharg res
    ret


.fun recvfrom NORMAL [S64] = [S32 A64 U64 A64 U32 U64 U64]
.bbl entry
    poparg sockfd:S32
    poparg buf:A64
    poparg len:U64
    poparg flags:A64
    poparg sock_addr:U64
    poparg sock_addrlen:U64
    pusharg sock_addrlen
    pusharg sock_addr
    pusharg flags
    pusharg len
    pusharg buf
    pusharg sockfd
    syscall recvfrom 45:U8
    poparg res:S64
    pusharg res
    ret
