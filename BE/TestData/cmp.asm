# cmp


## U32
.fun cmplt_u32_u32 NORMAL [U32] = [U32 U32 U32 U32]
.bbl start
    poparg op1:U32
    poparg op2:U32
    poparg cmp1:U32
    poparg cmp2:U32
    cmplt x:U32 op1 op2 cmp1 cmp2
    pusharg x
    ret

.fun cmpeq_u32_u32 NORMAL [U32] = [U32 U32 U32 U32]
.bbl start
    poparg op1:U32
    poparg op2:U32
    poparg cmp1:U32
    poparg cmp2:U32
    cmpeq x:U32 op1 op2 cmp1 cmp2
    pusharg x
    ret

## S32
.fun cmplt_s32_s32 NORMAL [S32] = [S32 S32 S32 S32]
.bbl start
    poparg op1:S32
    poparg op2:S32
    poparg cmp1:S32
    poparg cmp2:S32
    cmplt x:S32 op1 op2 cmp1 cmp2
    pusharg x
    ret

.fun cmpeq_s32_s32 NORMAL [S32] = [S32 S32 S32 S32]
.bbl start
    poparg op1:S32
    poparg op2:S32
    poparg cmp1:S32
    poparg cmp2:S32
    cmpeq x:S32 op1 op2 cmp1 cmp2
    pusharg x
    ret

## F32
.fun cmplt_u32_f32 NORMAL [U32] = [U32 U32 F32 F32]
.bbl start
    poparg op1:U32
    poparg op2:U32
    poparg cmp1:F32
    poparg cmp2:F32
    cmplt x:U32 op1 op2 cmp1 cmp2
    pusharg x
    ret

.fun cmpeq_s32_f32 NORMAL [S32] = [S32 S32 F32 F32]
.bbl start
    poparg op1:S32
    poparg op2:S32
    poparg cmp1:F32
    poparg cmp2:F32
    cmpeq x:S32 op1 op2 cmp1 cmp2
    pusharg x
    ret

## F64
 .fun cmplt_u32_f64 NORMAL [U32] = [U32 U32 F64 F64]
 .bbl start
     poparg op1:U32
     poparg op2:U32
     poparg cmp1:F64
     poparg cmp2:F64
     cmplt x:U32 op1 op2 cmp1 cmp2
     pusharg x
     ret

 .fun cmpeq_s32_f64 NORMAL [S32] = [S32 S32 F64 F64]
 .bbl start
     poparg op1:S32
     poparg op2:S32
     poparg cmp1:F64
     poparg cmp2:F64
     cmpeq x:S32 op1 op2 cmp1 cmp2
     pusharg x
     ret

# ========================================
.fun main NORMAL [S32] = []
    .reg U32 [u]
    .reg S32 [s]

.bbl start
    ## cmplt_u32_u32
    pusharg 1:U32
    pusharg 2:U32
    pusharg 111:U32
    pusharg 222:U32
    bsr cmplt_u32_u32
    poparg u
    pusharg u
    bsr print_u_ln

    pusharg 2:U32
    pusharg 1:U32
    pusharg 111:U32
    pusharg 222:U32
    bsr cmplt_u32_u32
    poparg u
    pusharg u
    bsr print_u_ln

    ## cmpeq_u32_u32
    pusharg 1:U32
    pusharg 2:U32
    pusharg 333:U32
    pusharg 444:U32
    bsr cmpeq_u32_u32
    poparg u
    pusharg u
    bsr print_u_ln

    pusharg 2:U32
    pusharg 2:U32
    pusharg 333:U32
    pusharg 444:U32
    bsr cmpeq_u32_u32
    poparg u
    pusharg u
    bsr print_u_ln

    ## cmplt_u32_f32
    pusharg 1:F32
    pusharg 2:F32
    pusharg 555:U32
    pusharg 666:U32
    bsr cmplt_u32_f32
    poparg u
    pusharg u
    bsr print_u_ln

    pusharg 2:F32
    pusharg 1:F32
    pusharg 555:U32
    pusharg 666:U32
    bsr cmplt_u32_f32
    poparg u
    pusharg u
    bsr print_u_ln

    ## cmplt_u32_f64
    pusharg 1:F64
    pusharg 2:F64
    pusharg 777:U32
    pusharg 888:U32
    bsr cmplt_u32_f64
    poparg u
    pusharg u
    bsr print_u_ln

    pusharg 2:F64
    pusharg 1:F64
    pusharg 777:U32
    pusharg 888:U32
    bsr cmplt_u32_f64
    poparg u
    pusharg u
    bsr print_u_ln

    ## cmplt_s32_s32 N
    pusharg -1:S32
    pusharg 1:S32
    pusharg 1111:S32
    pusharg 2222:S32
    bsr cmplt_s32_s32
    poparg s
    conv u s
    pusharg u
    bsr print_u_ln

    pusharg 1:S32
    pusharg -1:S32
    pusharg 1111:S32
    pusharg 2222:S32
    bsr cmplt_s32_s32
    poparg s
    conv u s
    pusharg u
    bsr print_u_ln

    ## cmpeq_s32_s32
    pusharg -1:S32
    pusharg 1:S32
    pusharg 3333:S32
    pusharg 4444:S32
    bsr cmpeq_s32_s32
    poparg s
    conv u s
    pusharg u
    bsr print_u_ln

    pusharg -1:S32
    pusharg -1:S32
    pusharg 3333:S32
    pusharg 4444:S32
    bsr cmpeq_s32_s32
    poparg s
    conv u s
    pusharg u
    bsr print_u_ln

    ## cmpeq_s32_f32
    pusharg 1:F32
    pusharg 2:F32
    pusharg 5555:S32
    pusharg 6666:S32
    bsr cmpeq_s32_f32
    poparg s
    conv u s
    pusharg u
    bsr print_u_ln

    pusharg 2:F32
    pusharg 2:F32
    pusharg 5555:S32
    pusharg 6666:S32
    bsr cmpeq_s32_f32
    poparg s
    conv u s
    pusharg u
    bsr print_u_ln

    ## cmpeq_s32_f64
    pusharg 1:F64
    pusharg 2:F64
    pusharg 5555:S32
    pusharg 6666:S32
    bsr cmpeq_s32_f64
    poparg s
    conv u s
    pusharg u
    bsr print_u_ln

    pusharg 2:F64
    pusharg 2:F64
    pusharg 5555:S32
    pusharg 6666:S32
    bsr cmpeq_s32_f64
    poparg s
    conv u s
    pusharg u
    bsr print_u_ln
    ##
    pusharg 0:S32
    ret
