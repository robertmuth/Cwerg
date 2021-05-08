# malloc

# ========================================
.fun main NORMAL [U32] = []
.bbl start
    mov size:U32 1
.bbl loop
    pusharg size
    bsr malloc
    poparg addr:A32
    bitcast x:U32 addr
    pusharg x
    bsr print_x_ln
    mul size size 4
    blt size 0x1000000 loop
    pusharg 0:U32
    ret
