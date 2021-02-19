
.mem fmt 4 rodata
    .data 1 "hello world\n"
.endmem

.fun _start 16
    mov_imm al r2 12
    movw  al r1 0x98
    movt  al r1 0x3
    movw  al r1 expr:movw_abs_nc:fmt:0
    movt  al r1 expr:movt_abs:fmt:0
    mov_imm al r0 1
    mov_imm al r7 4
    svc al 0

    mov_imm al r0 0
    mov_imm al r7 1
    svc al 0
.endfun	
