.fun fibonacci 16
    stm  al PuW sp reglist:16576
    mov_regimm al r6 lsl r0 0
    cmp_imm al r6 1
    b  hi expr:jump24:difficult

    mov_regimm al r0 lsl r6 0
    ldm  al reglist:32960 pUW sp

.bbl difficult 0
    sub_imm al r0 r6 1
    bl  al lr expr:call:fibonacci
    add_imm al r7 r0 0
    sub_imm al r0 r6 2
    bl  al lr expr:call:fibonacci
    add_regimm al r0 r7 lsl r0 0
    ldm  al reglist:32960 pUW sp
.endfun


.fun putchar 16
    stm al PuW sp reglist:0x4000
    sub_imm al sp sp 16
    strb_imm al PUw sp 0 r0
    # write
    mov_imm al r2 1
    add_imm al r1 sp 0
    mov_imm al r0 1
    mov_imm al r7 4
	svc al 0
    add_imm al sp sp 16
    ldm al reglist:0x8000 pUW sp
.endfun

.fun print_u32 16
    stm al PuW sp reglist:0x4040
    mov_imm al r12 10
    udiv al r6 r0 r12
    mul al r6 r6 r12
    sub_regimm al r6 r0 lsl r6 0
    mov_imm al r12 10
    udiv al r12 r0 r12
    cmp_imm al r12 0
    b eq expr:jump24:skip
    mov_regimm al r0 lsl r12 0
    bl al lr expr:call:print_u32
.bbl skip 16
    # 48 is '0'
    add_imm al r0 r6 48
    bl al lr expr:call:putchar
    ldm al reglist:0x8040 pUW sp
.endfun

.fun _start 16
    mov_imm al r10 0
 .bbl loop 16
    add_imm al r0 r10 0
    bl  al lr expr:call:fibonacci
    bl  al lr expr:call:print_u32

    # putchar newline
    mov_imm al r0 10
    bl  al lr expr:call:putchar

    add_imm al r10 r10 1
    cmp_imm al r10 10
    b ne expr:jump24:loop

    # exit 0
    mov_imm al r0 0
    mov_imm al r7 1
    svc al 0
.endfun
