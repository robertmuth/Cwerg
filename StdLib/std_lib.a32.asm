# overview here: https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md
.fun arm_syscall_write SIGNATURE [S32] = [S32 A32 U32]
.fun arm_syscall_read SIGNATURE [S32] = [S32 A32 U32]
.fun arm_syscall_open SIGNATURE [S32] = [A32 S32 S32]
.fun arm_syscall_close SIGNATURE [S32] = [S32]
.fun arm_syscall_lseek SIGNATURE [S32] = [S32 S32 S32]

.fun arm_syscall_brk SIGNATURE [A32] = [A32]
.fun arm_syscall_exit SIGNATURE [] = [U32]

############################################################
# linkerdefs
############################################################

.mem $$rw_data_end 4 EXTERN

############################################################
# Syscall wrappers
############################################################
	
.fun exit NORMAL [] = [U32]
.bbl start
    poparg out:U32
    pusharg out
    syscall arm_syscall_exit 1:U32
    trap

.fun brk NORMAL [A32] = [A32]
.bbl start
    poparg addr:A32
    pusharg addr
    syscall arm_syscall_brk 45:U32
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
    syscall arm_syscall_open 5:U32
    poparg res:S32
    pusharg res
    ret

.fun close NORMAL [S32] = [S32]
.bbl start
    poparg fh:S32
    pusharg fh
    syscall arm_syscall_close 6:U32
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
    syscall arm_syscall_write 4:U32
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
    syscall arm_syscall_read 3:U32
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
    syscall arm_syscall_lseek 19:U32
    poparg res:S32
    pusharg res
    ret

############################################################
# libc like helpers
############################################################	

.fun putchar NORMAL [] = [U8]
    .stk buffer 1 1
.bbl start
    poparg char:U8
    lea.stk buf:A32 buffer 0
    st buf 0 = char
    pusharg 1:U32
    pusharg buf
    pusharg 1:S32 # stdout
    syscall arm_syscall_write 4:U32
    poparg dummy:S32
    ret

# ========================================
.fun writeln NORMAL [] = [A32 U32]
.bbl start
    poparg buf:A32
    poparg len:U32

    pusharg len
    pusharg buf
    pusharg 1:S32 # stdout
    syscall arm_syscall_write 4:U32
    poparg dummy:S32
    pusharg 10:U8 # line feed
    bsr putchar
    ret

# ========================================
.fun puts NORMAL [] = [A32]
.bbl start
    poparg buf:A32
    mov len:U32 0
    bra check
.bbl loop
    add len len 1
.bbl check
    ld c:U8 buf len
    bne c 0 loop
    pusharg len
    pusharg buf
    bsr writeln
    ret

# ========================================
.fun print_num NORMAL [] = [U32]
.bbl start
      poparg x:U32
      rem rem:U32 = x 10
      div div:U32 = x 10
      beq div 0 skip
.bbl ddd
      pusharg div
      bsr print_num
.bbl skip
      add rem rem 48
      conv rem8:U8 rem
      pusharg rem8
      bsr putchar
      ret

# ========================================
.fun print_num_ln NORMAL [] = [U32]
.bbl start
    poparg x:U32
    pusharg x
    bsr print_num
    pusharg 10:U8 # line feed
    bsr putchar
    ret

# ========================================
.fun print_hex_num NORMAL [] = [U32]
.bbl start
      poparg x:U32
      and rem:U32 = x 0xf
      shr div:U32 = x 4
      beq div 0 skip
.bbl ddd
      pusharg div
      bsr print_hex_num
.bbl skip
      cmplt addend:U32 48 55 rem 10
      add rem rem addend
      conv rem8:U8 rem
      pusharg rem8
      bsr putchar
      ret

# ========================================
.fun print_hex_num_ln NORMAL [] = [U32]
.bbl start
    poparg x:U32
    pusharg x
    bsr print_hex_num
    pusharg 10:U8 # line feed
    bsr putchar
    ret

# state for malloc. Another way of doing this without linkerdefs
# would have been by calling brk(NULL)git
.mem $$malloc_state 4 RW
.data  8 [0]  # start + end

# dummy free
.fun free NORMAL [] = [A32]
.bbl start
    poparg x:A32
    ret

.fun malloc NORMAL [A32] = [U32]
.bbl start
    poparg size:U32
    add size size 15
    and size size 0xfffffff0
    ld.mem start:A32 =  $$malloc_state 0
    ld.mem end:A32 =  $$malloc_state 4
    bne start 0 normal
.bbl init
    pusharg 0:A32
    bsr brk
    poparg start
    mov end start
    st.mem $$malloc_state 0 start
    st.mem $$malloc_state 4 end
.bbl normal
    lea new_start:A32  start size
    ble new_start end done
    lea new_end:A32 end 0x200000 # round up quite bit. We want 1MB alignment to be safe
    bitcast x:U32 new_end
    and x x 0xfff00000
    bitcast new_end x
    pusharg new_end
    bsr brk
    poparg res:A32
    beq res new_end done_after_brk
    pusharg 0:A32
    ret
.bbl done_after_brk
    st.mem $$malloc_state 4 new_end
.bbl done
    st.mem $$malloc_state 0 new_start
    pusharg start
    ret

