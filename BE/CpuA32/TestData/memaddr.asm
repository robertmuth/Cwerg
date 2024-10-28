# size 10
.mem LINE 4 rodata
    .data 10 "="
.endmem
# size 10
.mem HASH 4 rodata
    .data 10 "="
.endmem
# size 10
.mem SEMI 4 rodata
    .data 10 ";"
.endmem
# size 12
.mem string_pointers 8 rodata
    .addr.mem 4 LINE 0x0
    .addr.mem 4 HASH 0x0
    .addr.mem 4 SEMI 0x0
.endmem


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

# sig: IN: [A32 U32] -> OUT: []  stk_size:0
.fun writeln 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl start 4
    mov_regimm al r2 r1 lsl 0
    mov_regimm al r1 r0 lsl 0
    mov_imm al r0 1
    str_imm_sub_pre al sp 4 r7
    movw al r7 4
    svc al 0
    ldr_imm_add_post al r7 sp 4
    mov_regimm al r1 r0 lsl 0
    mov_imm al r0 10
    bl al expr:call:putchar
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun


# sig: IN: [] -> OUT: [S32]  stk_size:0
.fun main 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl start 4
    movw al r0 expr:movw_abs_nc:string_pointers
    movt al r0 expr:movt_abs:string_pointers
    ldr_imm_add al r0 r0 0
    mov_imm al r1 10
    bl al expr:call:writeln
    movw al r0 expr:movw_abs_nc:string_pointers:4
    movt al r0 expr:movt_abs:string_pointers:4
    ldr_imm_add al r0 r0 0
    mov_imm al r1 10
    bl al expr:call:writeln
    movw al r0 expr:movw_abs_nc:string_pointers:8
    movt al r0 expr:movt_abs:string_pointers:8
    ldr_imm_add al r0 r0 0
    mov_imm al r1 10
    bl al expr:call:writeln
    mov_imm al r0 0
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun

.fun _start 16
    bl  al expr:call:main

    # exit 0
    mov_imm al r0 0
    mov_imm al r7 1
    svc al 0
