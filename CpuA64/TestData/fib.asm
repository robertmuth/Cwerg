
.fun putchar 16
    sub_x_imm sp sp 16
.bbl start 4
    add_x_imm x1 sp 0
    str_b_imm x1 0 w0
    movz_x_imm x2 1
    movz_x_imm x0 1
    movz_x_imm x8 0x40
    svc 0
    add_x_imm sp sp 16
    ret x30
.endfun


.fun print_num 16
    stp_x_imm_pre sp -16 x29 x30
.bbl start 4
    movz_x_imm x2 10
    udiv_x x1 x0 x2
    msub_x x29 x1 x2 x0
    subs_x_imm xzr x1 0
    b_eq expr:condbr19:skip
.bbl ddd 4
    orr_x_reg x0 xzr x1 lsl 0
    bl lr expr:call26:print_num
.bbl skip 4
    add_x_imm x0 x29 48
    bl lr expr:call26:putchar
    ldp_x_imm_post x29 x30 sp 16
    ret x30
.endfun


.fun fibonacci 16
    stp_x_imm_pre sp -16 x29 x30
    stp_x_imm_pre sp -16 x27 x28
.bbl start 4
    subs_x_imm xzr x0 1
    b_hi expr:condbr19:difficult
.bbl start_1 4
    ldp_x_imm_post x27 x28 sp 16
    ldp_x_imm_post x29 x30 sp 16
    ret x30


.bbl difficult 4
    orr_x_reg x29 xzr x0 lsl 0
    sub_x_imm x0 x29 1
    bl lr expr:call26:fibonacci
    orr_x_reg x28 xzr x0 lsl 0
    sub_x_imm x0 x29 2
    bl lr expr:call26:fibonacci
    add_x_reg x0 x0 x28 lsl 0
    ldp_x_imm_post x27 x28 sp 16
    ldp_x_imm_post x29 x30 sp 16
    ret x30
.endfun


.fun _start 16
    movz_x_imm x20 0
 .bbl loop 16
    orr_x_reg x0 xzr x20 lsl 0
    bl lr expr:call26:fibonacci
    bl lr expr:call26:print_num

    movz_x_imm x0 10
    bl lr expr:call26:putchar

    add_x_imm x20 x20 1
    subs_x_imm xzr x20 10
    b_ne expr:condbr19:loop

    movz_x_imm x0 0
    movz_x_imm x8 0x5d
    svc 0
.endfun
