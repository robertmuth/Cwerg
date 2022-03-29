
.mem newline 4 rodata
    .data 1 "\n"
.endmem

# This is called with r0:argc r1:argv
.fun main 16
    orr_x_reg x20 xzr x0 lsl 0
    orr_x_reg x21 xzr x1 lsl 0

    b expr:jump26:argc_check
.bbl loop 4
    ldr_x_imm_post x1 x21 8
    sub_x_imm x20 x20 1

# strlen computation: x1 contains string x2 will contain it's length
    movz_x_imm x2 0
    b expr:jump26:null_check
.bbl next_byte 4
    add_x_imm x2 x2 1
.bbl null_check 4
    ldr_b_reg_x w0 x1 x2 lsl 0
    subs_x_imm xzr x0 0
    b_ne expr:condbr19:next_byte
# print string
    movz_x_imm x0 1
    movz_x_imm x8 0x40
    svc 0
# print newline
    movz_x_imm x2 1
    adrp x1 expr:adr_prel_pg_hi21:newline:0
    add_x_imm x1 x1 expr:add_abs_lo12_nc:newline:0
    movz_x_imm x0 1
    movz_x_imm x8 0x40
    svc 0

.bbl argc_check 4
    subs_x_imm xzr x20 0
    b_ne expr:condbr19:loop
# exit
    movz_x_imm x0 0
    ret x30
.endfun	

.fun _start 16
    ldr_x_imm x0 sp 0
    add_x_imm x1 sp 8
    bl expr:call26:main
    movz_x_imm x8 0x5d
    svc 0
    brk 1
.endfun