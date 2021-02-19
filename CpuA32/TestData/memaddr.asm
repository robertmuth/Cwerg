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
############################################################
# CodeGen exit
############################################################
# REGSTATS exit                   glo:  0  0  loc:  0  1
# glo_lac     []
# glo_not_lac []
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun exit 16
# live-out sp]
.bbl start 4
    str_imm PuW sp 4 r7
    mov_imm r7 1
    svc 0
    ldr_imm r7 pUw sp 4
    bx lr
.endfun 
############################################################
# CodeGen putchar
############################################################
# REGSTATS putchar                glo:  0  0  loc:  0  2
# glo_lac     []
# glo_not_lac []
# sig: IN: [U8] -> OUT: []  stk_size:16
.fun putchar 16
    sub_imm sp sp 16
# live-out sp]
.bbl start 4
    mov_regimm r1 lsl r0 0
    mov_regimm r0 lsl sp 0
    strb_imm PUw sp 0 r1
    mov_imm r2 1
    mov_regimm r1 lsl r0 0
    mov_imm r0 1
    str_imm PuW sp 4 r7
    mov_imm r7 4
    svc 0
    ldr_imm r7 pUw sp 4
    add_imm sp sp 16
    bx lr
.endfun 
############################################################
# CodeGen writeln
############################################################
# REGSTATS writeln                glo:  0  0  loc:  0  2
# glo_lac     []
# glo_not_lac []
# sig: IN: [A32 U32] -> OUT: []  stk_size:0
.fun writeln 16
    stm PuW sp reglist:0x4000
# live-out sp]
.bbl start 4
    mov_regimm r2 lsl r1 0
    mov_regimm r1 lsl r0 0
    mov_imm r0 1
    str_imm PuW sp 4 r7
    mov_imm r7 4
    svc 0
    ldr_imm r7 pUw sp 4
    mov_imm r0 10
    bl lr expr:call:putchar
    ldm reglist:0x8000 pUW sp
.endfun 
############################################################
# CodeGen print_num
############################################################
# REGSTATS print_num              glo:  1  2  loc:  0  3
# glo_lac     ['rem']
# glo_not_lac ['div', 'sp']
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_num 16
    stm PuW sp reglist:0x4040
# live-out div rem sp]
.bbl start 4
    mov_regimm r1 lsl r0 0
    mov_imm r0 10
    udiv r6 r1 r0
    mov_imm r0 10
    mul r6 r6 r0
    sub_regimm r6 r1 lsl r6 0
    mov_imm r0 10
    udiv lr r1 r0
    cmp_imm lr 0
    b eq expr:jump24:skip
# live-out rem sp]
.bbl ddd 4
    mov_regimm r0 lsl lr 0
    bl lr expr:call:print_num
# live-out sp]
.bbl skip 4
    add_imm r6 r6 0x30
    mov_regimm r0 lsl r6 0
    bl lr expr:call:putchar
    ldm reglist:0x8040 pUW sp
.endfun 
############################################################
# CodeGen print_num_ln
############################################################
# REGSTATS print_num_ln           glo:  0  0  loc:  0  1
# glo_lac     []
# glo_not_lac []
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_num_ln 16
    stm PuW sp reglist:0x4000
# live-out sp]
.bbl start 4
    bl lr expr:call:print_num
    mov_imm r0 10
    bl lr expr:call:putchar
    ldm reglist:0x8000 pUW sp
.endfun 
############################################################
# CodeGen _start
############################################################
# REGSTATS _start                 glo:  0  0  loc:  0  1
# glo_lac     []
# glo_not_lac []
# sig: IN: [] -> OUT: []  stk_size:0
.fun _start 16
    stm PuW sp reglist:0x4000
# live-out sp]
.bbl start 4
    movw r0 expr:movw_abs_nc:string_pointers:0
    movt r0 expr:movt_abs:string_pointers:0
    ldr_imm r0 PUw r0 0
    mov_imm r1 10
    bl lr expr:call:writeln
    movw r0 expr:movw_abs_nc:string_pointers:0
    movt r0 expr:movt_abs:string_pointers:0
    ldr_imm r0 PUw r0 4
    mov_imm r1 10
    bl lr expr:call:writeln
    movw r0 expr:movw_abs_nc:string_pointers:0
    movt r0 expr:movt_abs:string_pointers:0
    ldr_imm r0 PUw r0 8
    mov_imm r1 10
    bl lr expr:call:writeln
    mov_imm r0 0
    bl lr expr:call:exit
    ldm reglist:0x8000 pUW sp
.endfun 
# STATS:
#  canonicalized: 0
#  const_fold: 0
#  const_prop: 5
#  dropped_regs: 6
#  ls_st_simplify: 4
#  move_elim: 0
#  strength_red: 1
#  useless: 0
