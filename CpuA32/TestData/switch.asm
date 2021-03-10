############################################################
# CodeGen exit
############################################################
# REGSTATS exit                   glo:  0  0  loc:  0  1
# glo_lac     []
# glo_not _lac []
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun exit 16
# live-out sp]
.bbl start 4
    str_imm_sub_pre sp 4 r7
    mov_imm r7 1
    svc 0
    ldr_imm_add_post r7 sp 4
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
    strb_imm_add sp 0 r1
    mov_imm r2 1
    mov_regimm r1 lsl r0 0
    mov_imm r0 1
    str_imm_sub_pre sp 4 r7
    mov_imm r7 4
    svc 0
    ldr_imm_add_post r7 sp 4
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
    stmdb_update sp reglist:0x4000
# live-out sp]
.bbl start 4
    mov_regimm r2 lsl r1 0
    mov_regimm r1 lsl r0 0
    mov_imm r0 1
    str_imm_sub_pre sp 4 r7
    mov_imm r7 4
    svc 0
    ldr_imm_add_post r7 sp 4
    mov_imm r0 10
    bl lr expr:call:putchar
    ldmia_update reglist:0x8000 sp
.endfun 
############################################################
# CodeGen print_num
############################################################
# REGSTATS print_num              glo:  1  2  loc:  0  3
# glo_lac     ['rem']
# glo_not_lac ['div', 'sp']
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_num 16
    stmdb_update sp reglist:0x4040
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
    ldmia_update reglist:0x8040 sp
.endfun 
############################################################
# CodeGen print_num_ln
############################################################
# REGSTATS print_num_ln           glo:  0  0  loc:  0  1
# glo_lac     []
# glo_not_lac []
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_num_ln 16
    stmdb_update sp reglist:0x4000
# live-out sp]
.bbl start 4
    bl lr expr:call:print_num
    mov_imm r0 10
    bl lr expr:call:putchar
    ldmia_update reglist:0x8000 sp
.endfun 
############################################################
# CodeGen _start
############################################################
# REGSTATS _start                 glo:  1  1  loc:  0  1
# glo_lac     ['i']
# glo_not_lac ['sp']
# sig: IN: [] -> OUT: []  stk_size:0
.fun _start 16
.mem switch_tab 4 rodata
.addr.bbl 4 labelD
.addr.bbl 4 labelA
.addr.bbl 4 labelB
.addr.bbl 4 labelD
.addr.bbl 4 labelC
.endmem 
    stmdb_update sp reglist:0x4040
# live-out i sp]
.bbl start 4
    mov_imm r6 0
# live-out i sp]
.bbl loop 4
    movw r0 expr:movw_abs_nc:switch_tab
    movt r0 expr:movt_abs:switch_tab
    ldr_reg_add pc r0 lsl r6 2
# live-out i sp]
.bbl labelA 4
    mov_imm r0 0x41
    bl lr expr:call:putchar
    mov_imm r0 10
    bl lr expr:call:putchar
    b expr:jump24:tail
# live-out i sp]
.bbl labelB 4
    mov_imm r0 0x42
    bl lr expr:call:putchar
    mov_imm r0 10
    bl lr expr:call:putchar
    b expr:jump24:tail
# live-out i sp]
.bbl labelC 4
    mov_imm r0 0x43
    bl lr expr:call:putchar
    mov_imm r0 10
    bl lr expr:call:putchar
    b expr:jump24:tail
# live-out i sp]
.bbl labelD 4
    mov_imm r0 0x44
    bl lr expr:call:putchar
    mov_imm r0 10
    bl lr expr:call:putchar
# live-out i sp]
.bbl tail 4
    add_imm r6 r6 1
    cmp_imm r6 5
    b cc expr:jump24:loop
# live-out sp]
.bbl tail_1 4
    mov_imm r0 0
    bl lr expr:call:exit
    ldmia_update reglist:0x8040 sp
.endfun 
# STATS:
#  canonicalized: 0
#  const_fold: 0
#  const_prop: 14
#  dropped_regs: 8
#  ls_st_simplify: 1
#  move_elim: 0
#  strength_red: 1
#  useless: 0
