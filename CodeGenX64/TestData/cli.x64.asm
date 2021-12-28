# cli

.fun main NORMAL [U32] = [U32 A64]

.bbl start
    poparg argc:U32
    poparg argv:A64

    pusharg argc
    bsr print_u_ln

    mov i:U32 0
    bra check
.bbl loop
    shl index:U32 i 3
    ld  arg:A64 argv index
    pusharg arg
    bsr print_s_ln
    add i i 1
.bbl check
    blt i argc loop
    pusharg 0:U32
    ret
