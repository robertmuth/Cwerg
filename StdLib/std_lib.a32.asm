# Prepend this to cwerg IR code  before running it through CodeGenA32/codegen.py


############################################################
# linkerdefs
############################################################

.mem $$rw_data_end 4 EXTERN

############################################################
# libc like helpers
############################################################	

.fun print_c NORMAL [] = [U8]
    .stk buffer 1 1
.bbl start
    poparg char:U8
    lea.stk buf:A32 buffer 0
    st buf 0 = char
    pusharg 1:U32
    pusharg buf
    pusharg 1:S32 # stdout
    bsr write
    poparg dummy:S32
    ret

.fun print_c_ln NORMAL [] = [U8]
    .stk buffer 1 1
.bbl start
    poparg c:U8
    pusharg c
    bsr print_c
    pusharg 10:U8 # line feed
    bsr print_c
    ret

# ========================================
.fun print_ln NORMAL [] = [A32 U32]
.bbl start
    poparg buf:A32
    poparg len:U32

    pusharg len
    pusharg buf
    pusharg 1:S32 # stdout
    bsr write
    poparg dummy:S32
    pusharg 10:U8 # line feed
    bsr print_c
    ret

# ========================================
.fun print_s_ln NORMAL [] = [A32]
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
    bsr print_ln
    ret

# ========================================
.fun print_u NORMAL [] = [U32]
.bbl start
      poparg x:U32
      rem rem:U32 = x 10
      div div:U32 = x 10
      beq div 0 skip
.bbl ddd
      pusharg div
      bsr print_u
.bbl skip
      add rem rem 48
      conv rem8:U8 rem
      pusharg rem8
      bsr print_c
      ret

# ========================================
.fun print_u_ln NORMAL [] = [U32]
.bbl start
    poparg x:U32
    pusharg x
    bsr print_u
    pusharg 10:U8 # line feed
    bsr print_c
    ret

# ========================================
.fun print_x NORMAL [] = [U32]
.bbl start
      poparg x:U32
      and rem:U32 = x 0xf
      shr div:U32 = x 4
      beq div 0 skip
.bbl ddd
      pusharg div
      bsr print_x
.bbl skip
      cmplt addend:U32 48 55 rem 10
      add rem rem addend
      conv rem8:U8 rem
      pusharg rem8
      bsr print_c
      ret

# ========================================
.fun print_x_ln NORMAL [] = [U32]
.bbl start
    poparg x:U32
    pusharg x
    bsr print_x
    pusharg 10:U8 # line feed
    bsr print_c
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

