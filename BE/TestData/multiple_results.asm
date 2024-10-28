# demonstrates multiple return values

# ========================================
# function with 5 return values
.fun multi NORMAL [U32 U32 U32 U32 U32] = [U32 U32]
.reg U32 [a b add  sub mul div mod] 
.bbl start
    poparg a
    poparg b
    add add = a b
    sub sub = a b
    mul mul = a b
    div div = a b
    rem mod = a b
    pusharg mod
    pusharg div
    pusharg mul
    pusharg sub
    pusharg add
    ret


# function with heterogeneous return values
.fun hetero NORMAL [S8 S16 S32 U8 U16 U32] = []
.bbl start
    pusharg 0:U32
    pusharg 1:U16
    pusharg 2:U8
    pusharg -3:S32
    pusharg -4:S16
    pusharg -5:S8
    ret
# ========================================
.fun main NORMAL [S32] = []
.reg U32 [a s m d M x y]
.bbl start
    pusharg 6:U32
    pusharg 70:U32
    bsr multi
    poparg a
    poparg s
    poparg m
    poparg d
    poparg M

    pusharg a
    bsr print_u_ln

    pusharg s
    bsr print_u_ln

    pusharg m
    bsr print_u_ln

    pusharg d
    bsr print_u_ln

    pusharg M
    bsr print_u_ln

    ###

    bsr hetero
    poparg s8:S8
    poparg s16:S16
    poparg s32:S32
    poparg u8:U8
    poparg u16:U16
    poparg u32:U32

    conv ss:S32 s8
    pusharg ss
    bsr print_d_ln

    conv ss s16
    pusharg ss
    bsr print_d_ln

    pusharg s32
    bsr print_d_ln

    conv uu:U32 u8
    pusharg uu
    bsr print_u_ln

    conv uu u16
    pusharg uu
    bsr print_u_ln

    pusharg u32
    bsr print_u_ln

    pusharg 0:S32
    ret




