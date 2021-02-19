# fibonacci examples exercises recursion

# ========================================
.fun fibonacci NORMAL [U32] = [U32]
    .reg U32 [x in out] 

.bbl start
    poparg in
    blt 1:U32 in difficult
    pusharg in
    ret

.bbl difficult
    mov out = 0
    sub x = in 1

    pusharg x
    bsr fibonacci
    poparg x

    add out = out x
    sub x = in 2

    pusharg x
    bsr fibonacci
    poparg x

    add out = out x
    pusharg out
    ret

# ========================================
.fun main NORMAL [S32] = []
    .reg U32 [x]
.bbl start
    mov x = 7

    pusharg x
    bsr fibonacci
    poparg x

    pusharg x
    bsr print_num_ln

    pusharg 0:S32
    ret




