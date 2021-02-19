# cli

.fun main NORMAL [U32] = [U32 A32]

.bbl start
    poparg argc:U32
    poparg argv:A32

    pusharg argc
    bsr print_num_ln

    mov i:U32 0
    bra check
.bbl loop
    shl index:U32 i 2
    ld  arg:A32 argv index
    pusharg arg
    bsr puts
    add i i 1
.bbl check
    blt i argc loop
    pusharg 0:U32
    ret
