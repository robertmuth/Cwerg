# demonstrates the use of struct related directives
# these are just syntactic sugar for the .num directive

.fun printf_u BUILTIN [] = [A64 U32]

==========================
.mem fmt 4 RO
.data 1 "%d\n\0"


.struct struct1
.field f1 4 4  # generates the number struct1.f1
.field f2 4 4  # generates the number struct1.f2
.field f3 4 4 
.field f4 4 4 
.endstruct     # generated struct1.alignment & struct1.sizeof

.struct struct2
.field g1 4 4 
.field g2 4 4 
.field g3 4 4 
.field g4 4 4 
.endstruct

# ========================================
.fun main MAIN [S32] = []
    .reg U32 [x] 
    .reg A64 [f] 
    .reg S32 [out] 
    .stk s1 struct1.alignment struct1.sizeof
    .stk s2 struct2.alignment struct2.sizeof
	
.bbl start
    mov.i x = 66
    st s1 struct1.f1 = x
    add.i x = x 1
    st s1 struct1.f2 = x
    add.i x = x 1
    st s1 struct1.f3 = x
    add.i x = x 1
    st s1 struct1.f4 = x
    add.i x = x 1

    st s2 struct2.g1 = x
    add.i x = x 1
    st s2 struct2.g2 = x
    add.i x = x 1
    st s2 struct2.g3 = x
    add.i x = x 1
    st s2 struct2.g4 = x
    add.i x = x 1
    

    lea f fmt
    ld x = s1 struct1.f1
    pusharg  x
    pusharg  f
    bsr printf_u

    ld x = s1 struct1.f2
    pusharg  x
    pusharg  f
    bsr printf_u

    ld x = s1 struct1.f3
    pusharg  x
    pusharg  f
    bsr printf_u

    ld x = s1 struct1.f4
    pusharg  x
    pusharg  f
    bsr printf_u

    ld x = s2 struct2.g1
    pusharg  x
    pusharg  f
    bsr printf_u

    ld x = s2 struct2.g2
    pusharg  x
    pusharg  f
    bsr printf_u

    ld x = s2 struct2.g3
    pusharg  x
    pusharg  f
    bsr printf_u

    ld x = s2 struct2.g4
    pusharg  x
    pusharg  f
    bsr printf_u

    mov out = 0
    pusharg out
    ret




