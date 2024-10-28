# cli

.fun main NORMAL [S32] = [S32 A32]

.bbl start
    poparg argc:S32
    poparg argv:A32
    conv argc_u:U32 argc
    pusharg argc_u
    bsr print_u_ln

    mov i:S32 0
    bra check
.bbl loop
    shl index:S32 i 2
    ld  arg:A32 argv index
    pusharg arg
    bsr print_s_ln
    add i i 1
.bbl check
    blt i argc loop
    pusharg 0:S32
    ret
