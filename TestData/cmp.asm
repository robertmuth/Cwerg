# cmp

# ========================================
.fun foo NORMAL [U32] = [U32]
    .reg U32 [x]

.bbl start
    poparg x
    cmplt y:U32 0 1 x 5
    cmpeq y 2 y x 2
    pusharg y
    ret

# ========================================
.fun main NORMAL [S32] = []
    .reg U32 [x y]

.bbl start
    mov x = 0
.bbl loop
    pusharg x
    bsr foo
    poparg y

    pusharg y
    bsr print_u_ln

    add x x 1
    blt x 10 loop
    pusharg 0:S32
    ret
