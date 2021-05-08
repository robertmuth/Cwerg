# indirect function call

# simple function which will print out 1
.fun fun1 NORMAL [] = []
.bbl start
    # load constant into new register x
    mov x:U32 1
    pusharg x
    bsr print_u_ln
    ret

.fun fun2 NORMAL [] = []
.bbl start
    mov x:U32 2
    pusharg x
    bsr print_u_ln
    ret

.fun fun3 NORMAL [] = []
.bbl start
    mov x:U32 3
    pusharg x
    bsr print_u_ln
    ret

.mem fun_pointers 8 RO
.addr.fun 8  fun1
.addr.fun 8  fun2
.addr.fun 8  fun3

.fun main NORMAL [S32] = []
.reg C64 [fp] 
.bbl start

    bsr fun1
    bsr fun2
    bsr fun3

    lea.fun fp = fun1 
    jsr fp fun1

    lea.fun fp = fun2 
    # fun1 just denotes a signature which is the same as fun2
    jsr fp fun1

    lea.fun fp = fun3 
    # fun1 just denotes a signature which is the same as fun3
    jsr fp fun1

    ld.mem fp = fun_pointers  0
    jsr fp fun1
    ld.mem fp = fun_pointers  8
    jsr fp fun1
    ld.mem fp = fun_pointers  16
    jsr fp fun1
    pusharg 0:S32
    ret




