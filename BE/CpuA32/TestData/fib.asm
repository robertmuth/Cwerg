
# sig: IN: [U32] -> OUT: []  stk_size:1
.fun putchar 16
    sub_imm al sp sp 16
.bbl start 4
    add_imm al r1 sp 0
    mov_regimm al r0 r0 lsl 0
    strb_imm_add al sp 0 r0
    mov_imm al r2 1
    mov_imm al r0 1
    str_imm_sub_pre al sp 4 r7
    movw al r7 4
    svc al 0
    ldr_imm_add_post al r7 sp 4
    add_imm al sp sp 16
    bx al lr
.endfun


# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_num 16
    stmdb_update al sp reglist:0x4040
    sub_imm al sp sp 8
.bbl start 4
    mov_imm al r1 10
    udiv al r1 r0 r1
    mov_imm al r2 10
    mul al r1 r1 r2
    sub_regimm al r6 r0 r1 lsl 0
    mov_imm al r1 10
    udiv al r4 r0 r1
    cmp_imm al r4 0
    b eq expr:jump24:skip
.bbl ddd 4
    mov_regimm al r0 r4 lsl 0
    bl al expr:call:print_num
.bbl skip 4
    add_imm al r6 r6 48
    mov_regimm al r0 r6 lsl 0
    bl al expr:call:putchar
    add_imm al sp sp 8
    ldmia_update al reglist:0x8040 sp
.endfun

# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_num_ln 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl start 4
    bl al expr:call:print_num
    mov_imm al r0 10
    bl al expr:call:putchar
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun


# sig: IN: [U32] -> OUT: [U32]  stk_size:0
.fun fibonacci 16
    stmdb_update al sp reglist:0x40c0
    sub_imm al sp sp 4
.bbl start 4
    mov_regimm al r6 r0 lsl 0
    cmp_imm al r6 1
    b hi expr:jump24:difficult
.bbl start_1 4
    mov_regimm al r0 r6 lsl 0
    add_imm al sp sp 4
    ldmia_update al reglist:0x80c0 sp
.bbl difficult 4
    sub_imm al r0 r6 1
    bl al expr:call:fibonacci
    mov_regimm al r7 r0 lsl 0
    sub_imm al r0 r6 2
    bl al expr:call:fibonacci
    add_regimm al r0 r7 r0 lsl 0
    add_imm al sp sp 4
    ldmia_update al reglist:0x80c0 sp
.endfun

# sig: IN: [] -> OUT: [S32]  stk_size:0
.fun main 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl start 4
    mov_imm al r0 7
    bl al expr:call:fibonacci
    bl al expr:call:print_num_ln
    mov_imm al r0 0
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun

.fun _start 16
    mov_imm al r10 0
 .bbl loop 16
    add_imm al r0 r10 0
    bl  al expr:call:fibonacci
    bl  al expr:call:print_num_ln

    add_imm al r10 r10 1
    cmp_imm al r10 10
    b ne expr:jump24:loop

    # exit 0
    mov_imm al r0 0
    mov_imm al r7 1
    svc al 0
