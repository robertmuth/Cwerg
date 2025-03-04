# demonstrates multiple return values

# ========================================
# function with 5 return values
.fun multi NORMAL [R32 R32 R32 R32] = [R32 R32]
.bbl start
    poparg a:R32
    poparg b:R32
    add add:R32 = a b
    sub sub:R32 = a b
    mul mul:R32 = a b
    div div:R32 = a b
    # rem mod = a b
    # pusharg mod
    pusharg div
    pusharg mul
    pusharg sub
    pusharg add
    ret

# ========================================
.fun main NORMAL [S32] = []
.reg R32 [a s m d M x y]
.bbl start
      mov xi:S32 = 70
      mov yi:S32 = 6

      conv x xi
      conv y yi

      pusharg y
      pusharg x
      bsr multi
      poparg a
      poparg s
      poparg m
      poparg d
      # poparg M

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
