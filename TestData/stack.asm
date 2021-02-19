# demonstrates the use of the .stk directives

# ========================================
.fun main NORMAL [S32] = []
    .reg U32 [x y index] 
    .stk array 4 4000
.bbl start
    mov x = 0
.bbl loop
    mul index x 4
    st.stk array index = x
    add x = x 1
    blt x 1000 loop

    mov x = 0
.bbl loop2
    mul index = x 4
    ld.stk y = array index
    pusharg y
    bsr print_num_ln
    add x = x 1
    blt x 1000 loop2
    pusharg 0:S32
    ret




