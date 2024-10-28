# demonstrates the use of the .stk directives

.fun printf_u builtin [] = [a32  u32]

==========================
.mem fmt 4 ro
.data 1 "%d\n\0"

# ========================================
.fun main main [s32] = []
    .reg [x y index] u32
    .reg [f] a32
    .reg [out] s32
    .stk array 4 4000
.bbl start
    mov.i x = 0
.bbl loop
    mul index x 4
    st.stkr array index = x
    add x = x 1
    blt loop x 1000

    mov.i x = 0
    lea f fmt
.bbl loop2
    mul index = x 4
    ld.stkr y = array index
    pusharg y
    pusharg f
    bsr printf_u
    add x = x 1
    blt loop2 x 1000
    mov out = 0
    pusharg out
    ret




