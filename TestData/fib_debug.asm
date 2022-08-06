# fibonacci examples exercises recursion

# ========================================
.fun fibonacci NORMAL [U32] = [U32]
    .reg U32 [x in out] 

.bbl start
	poparg in
	line "file1"  1
    blt 1:U32 in difficult
    line "file1" 2
	pusharg in
    ret

	.bbl difficult
	line "file1"  3
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
    line "file2" 10
    pusharg out
    ret

# ========================================
.fun main NORMAL [S32] = []
    .reg U32 [x]
	.bbl start
	line "file2" 1
    mov x = 7

    pusharg x
    bsr fibonacci
    poparg x

    pusharg x
    bsr print_u_ln

    pusharg 0:S32
    ret




