# demonstrates multiple return values

# ========================================
# function with 5 return values
.fun multi NORMAL [R64 R64 R64 R64] = [R64 R64]
.bbl start
    poparg a:R64
    poparg b:R64
    add add:R64 = a b
    sub sub:R64 = a b
    mul mul:R64 = a b
    div div:R64 = a b
    # rem mod:R64 = a b
    # pusharg mod
    pusharg div
    pusharg mul
    pusharg sub
    pusharg add
    ret


# ========================================
.fun main NORMAL [S32] = []
.bbl start
    mov xi:S32 = 70
    mov yi:S32 = 6

    conv x:R64 xi
    conv y:R64 yi

    pusharg y
    pusharg x
    bsr multi
    poparg a:R64
    poparg s:R64
    poparg m:R64
    poparg d:R64

    conv a2:U32 a
    pusharg a2
    bsr print_u_ln

    conv s2:U32 s
    pusharg s2
    bsr print_u_ln

    conv m2:U32 m
    pusharg m2
    bsr print_u_ln

    conv d2:U32 d
    pusharg d2
    bsr print_u_ln

    # conv M2:U32 M
    # pusharg M2
    # bsr print_num_ln

    pusharg 0:S32
    ret
