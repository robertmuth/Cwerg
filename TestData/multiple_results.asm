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

# ========================================
.fun main NORMAL [S32] = []
.reg U32 [a s m d M x y]
.bbl start
    mov x = 70
    mov y = 6

    pusharg y
    pusharg x
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

    pusharg 0:S32
    ret




