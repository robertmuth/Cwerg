
.mem fmt 4 rodata
    .data 1 "hello world\n"
.endmem

.fun _start 16
    movz_x_imm x2 12
    adrp  x1 expr:adr_prel_pg_hi21:fmt:0
    add_imm_x x1 x1 expr:add_abs_lo12_nc:fmt:0
    movz_x_imm x0 1
    movz_x_imm x8 0x40
    svc 0

    movz_x_imm x0 0
    movz_x_imm x8 0x5d
    svc 0
.endfun

