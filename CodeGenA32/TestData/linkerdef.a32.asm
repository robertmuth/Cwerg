# linkerdef

.mem dummy 4 RW
.data 4 "0"

# ========================================
.fun main NORMAL [S32] = []
.bbl start
    ld.mem x:U32 = dummy 0

    pusharg x
    bsr print_x_ln

    lea.mem a:A32 $$rw_data_end 0
    bitcast x a

    pusharg x
    bsr print_x_ln

    pusharg 0:S32
    ret
