############################################################
# GlobalRegAlloc arm_syscall_write
############################################################
# REGSTATS arm_syscall_write      all:  0  0  glo:  0  0  loc:  0  0
############################################################
# GlobalRegAlloc arm_syscall_read
############################################################
# REGSTATS arm_syscall_read       all:  0  0  glo:  0  0  loc:  0  0
############################################################
# GlobalRegAlloc arm_syscall_open
############################################################
# REGSTATS arm_syscall_open       all:  0  0  glo:  0  0  loc:  0  0
############################################################
# GlobalRegAlloc arm_syscall_close
############################################################
# REGSTATS arm_syscall_close      all:  0  0  glo:  0  0  loc:  0  0
############################################################
# GlobalRegAlloc arm_syscall_lseek
############################################################
# REGSTATS arm_syscall_lseek      all:  0  0  glo:  0  0  loc:  0  0
############################################################
# GlobalRegAlloc arm_syscall_brk
############################################################
# REGSTATS arm_syscall_brk        all:  0  0  glo:  0  0  loc:  0  0
############################################################
# GlobalRegAlloc arm_syscall_exit
############################################################
# REGSTATS arm_syscall_exit       all:  0  0  glo:  0  0  loc:  0  0
############################################################
# GlobalRegAlloc exit
############################################################
# REGSTATS exit                   all:  0  1  glo:  0  0  loc:  0  1
############################################################
# GlobalRegAlloc brk
############################################################
# REGSTATS brk                    all:  1  0  glo:  0  0  loc:  0  1
############################################################
# GlobalRegAlloc open
############################################################
# REGSTATS open                   all:  1  3  glo:  0  0  loc:  0  3
############################################################
# GlobalRegAlloc close
############################################################
# REGSTATS close                  all:  1  0  glo:  0  0  loc:  0  1
############################################################
# GlobalRegAlloc write
############################################################
# REGSTATS write                  all:  1  2  glo:  0  0  loc:  0  3
############################################################
# GlobalRegAlloc read
############################################################
# REGSTATS read                   all:  1  2  glo:  0  0  loc:  0  3
############################################################
# GlobalRegAlloc lseek
############################################################
# REGSTATS lseek                  all:  1  2  glo:  0  0  loc:  0  3
############################################################
# GlobalRegAlloc putchar
############################################################
# REGSTATS putchar                all:  0  1  glo:  0  0  loc:  0  2
############################################################
# GlobalRegAlloc writeln
############################################################
# REGSTATS writeln                all:  0  2  glo:  0  0  loc:  0  2
############################################################
# GlobalRegAlloc puts
############################################################
# REGSTATS puts                   all:  0  1  glo:  0  2  loc:  0  1
############################################################
# GlobalRegAlloc print_num
############################################################
# REGSTATS print_num              all:  0  1  glo:  1  1  loc:  0  3
############################################################
# GlobalRegAlloc print_num_ln
############################################################
# REGSTATS print_num_ln           all:  0  1  glo:  0  0  loc:  0  1
############################################################
# GlobalRegAlloc print_hex_num
############################################################
# REGSTATS print_hex_num          all:  0  1  glo:  1  1  loc:  0  1
############################################################
# GlobalRegAlloc print_hex_num_ln
############################################################
# REGSTATS print_hex_num_ln       all:  0  1  glo:  0  0  loc:  0  1
############################################################
# GlobalRegAlloc free
############################################################
# REGSTATS free                   all:  0  1  glo:  0  0  loc:  0  1
############################################################
# GlobalRegAlloc malloc
############################################################
# REGSTATS malloc                 all:  0  1  glo:  4  1  loc:  0  2
############################################################
# GlobalRegAlloc dump
############################################################
# REGSTATS dump                   all:  0  0  glo:  2  0  loc:  0  2
############################################################
# GlobalRegAlloc conflict
############################################################
# REGSTATS conflict               all:  0  1  glo:  0  6  loc:  0  1
############################################################
# GlobalRegAlloc solve
############################################################
# REGSTATS solve                  all:  1  0  glo:  3  0  loc:  1  2
############################################################
# GlobalRegAlloc main
############################################################
# REGSTATS main                   all:  0  0  glo:  0  0  loc:  0  1
# size 8
.mem $$malloc_state 4 data
    .data 8 "\x00"
.endmem
# size 41
.mem LINE 4 rodata
    .data 1 "\n========================================"
.endmem
# size 64
.mem BOARD 4 data
    .data 64 " "
.endmem
# size 8
.mem XCOORDS 4 data
    .data 8 "\x00"
.endmem
# size 4
.mem COUNTER 4 data
    .data 4 "\x00"
.endmem
# sig: IN: [S32 A32 U32] -> OUT: [S32]  stk_size:0
.fun arm_syscall_write 16
.endfun
# sig: IN: [S32 A32 U32] -> OUT: [S32]  stk_size:0
.fun arm_syscall_read 16
.endfun
# sig: IN: [A32 S32 S32] -> OUT: [S32]  stk_size:0
.fun arm_syscall_open 16
.endfun
# sig: IN: [S32] -> OUT: [S32]  stk_size:0
.fun arm_syscall_close 16
.endfun
# sig: IN: [S32 S32 S32] -> OUT: [S32]  stk_size:0
.fun arm_syscall_lseek 16
.endfun
# sig: IN: [A32] -> OUT: [A32]  stk_size:0
.fun arm_syscall_brk 16
.endfun
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun arm_syscall_exit 16
.endfun
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun exit 16
.bbl start 4
    str_imm_sub_pre al sp 4 r7
    movw al r7 1
    svc al 0
    ldr_imm_add_post al r7 sp 4
    ud2 al
.endfun
# sig: IN: [A32] -> OUT: [A32]  stk_size:0
.fun brk 16
.bbl start 4
    str_imm_sub_pre al sp 4 r7
    movw al r7 45
    svc al 0
    ldr_imm_add_post al r7 sp 4
    bx al lr
.endfun
# sig: IN: [A32 S32 S32] -> OUT: [S32]  stk_size:0
.fun open 16
.bbl start 4
    str_imm_sub_pre al sp 4 r7
    movw al r7 5
    svc al 0
    ldr_imm_add_post al r7 sp 4
    bx al lr
.endfun
# sig: IN: [S32] -> OUT: [S32]  stk_size:0
.fun close 16
.bbl start 4
    str_imm_sub_pre al sp 4 r7
    movw al r7 6
    svc al 0
    ldr_imm_add_post al r7 sp 4
    bx al lr
.endfun
# sig: IN: [S32 A32 U32] -> OUT: [S32]  stk_size:0
.fun write 16
.bbl start 4
    str_imm_sub_pre al sp 4 r7
    movw al r7 4
    svc al 0
    ldr_imm_add_post al r7 sp 4
    bx al lr
.endfun
# sig: IN: [S32 A32 U32] -> OUT: [S32]  stk_size:0
.fun read 16
.bbl start 4
    str_imm_sub_pre al sp 4 r7
    movw al r7 3
    svc al 0
    ldr_imm_add_post al r7 sp 4
    bx al lr
.endfun
# sig: IN: [S32 S32 S32] -> OUT: [S32]  stk_size:0
.fun lseek 16
.bbl start 4
    str_imm_sub_pre al sp 4 r7
    movw al r7 19
    svc al 0
    ldr_imm_add_post al r7 sp 4
    bx al lr
.endfun
# sig: IN: [U32] -> OUT: []  stk_size:1
.fun putchar 16
    sub_imm al sp sp 16
.bbl start 4
    add_imm al r1 sp 0
    mov_regimm al r0 lsl r0 0
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
    mov_regimm al r2 lsl r1 0
    mov_regimm al r1 lsl r0 0
    mov_imm al r0 1
    str_imm_sub_pre al sp 4 r7
    movw al r7 4
    svc al 0
    ldr_imm_add_post al r7 sp 4
    mov_regimm al r1 lsl r0 0
    mov_imm al r0 10
    bl al lr expr:call:putchar
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun
# sig: IN: [A32] -> OUT: []  stk_size:0
.fun puts 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl start 4
    mov_regimm al r2 lsl r0 0
    mov_imm al r3 0
    b al expr:jump24:check
.bbl loop 4
    add_imm al r3 r3 1
.bbl check 4
    ldrb_reg_add al r0 r2 lsl r3 0
    uxtb al r0 ror_rrx r0 0
    cmp_imm al r0 0
    b ne expr:jump24:loop
.bbl check_1 4
    mov_regimm al r1 lsl r3 0
    mov_regimm al r0 lsl r2 0
    bl al lr expr:call:writeln
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
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
    sub_regimm al r6 r0 lsl r1 0
    mov_imm al r1 10
    udiv al r4 r0 r1
    cmp_imm al r4 0
    b eq expr:jump24:skip
.bbl ddd 4
    mov_regimm al r0 lsl r4 0
    bl al lr expr:call:print_num
.bbl skip 4
    add_imm al r6 r6 48
    mov_regimm al r0 lsl r6 0
    bl al lr expr:call:putchar
    add_imm al sp sp 8
    ldmia_update al reglist:0x8040 sp
.endfun
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_num_ln 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl start 4
    bl al lr expr:call:print_num
    mov_imm al r0 10
    bl al lr expr:call:putchar
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_hex_num 16
    stmdb_update al sp reglist:0x4040
    sub_imm al sp sp 8
.bbl start 4
    and_imm al r6 r0 15
    mov_regimm al r2 lsr r0 4
    cmp_imm al r2 0
    b eq expr:jump24:skip
.bbl ddd 4
    mov_regimm al r0 lsl r2 0
    bl al lr expr:call:print_hex_num
.bbl skip 4
    cmp_imm al r6 10
    movw cc r0 48
    movw cs r0 55
    add_regimm al r6 r6 lsl r0 0
    mov_regimm al r0 lsl r6 0
    bl al lr expr:call:putchar
    add_imm al sp sp 8
    ldmia_update al reglist:0x8040 sp
.endfun
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_hex_num_ln 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl start 4
    bl al lr expr:call:print_hex_num
    mov_imm al r0 10
    bl al lr expr:call:putchar
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun
# sig: IN: [A32] -> OUT: []  stk_size:0
.fun free 16
.bbl start 4
    bx al lr
.endfun
# sig: IN: [U32] -> OUT: [A32]  stk_size:0
.fun malloc 16
    stmdb_update al sp reglist:0x43c0
    sub_imm al sp sp 12
.bbl start 4
    mov_regimm al r8 lsl r0 0
    add_imm al r8 r8 15
    bic_imm al r8 r8 15
    movw al r0 expr:movw_abs_nc:$$malloc_state
    movt al r0 expr:movt_abs:$$malloc_state
    ldr_imm_add al r9 r0 0
    movw al r0 expr:movw_abs_nc:$$malloc_state:4
    movt al r0 expr:movt_abs:$$malloc_state:4
    ldr_imm_add al r3 r0 0
    cmp_imm al r9 0
    b ne expr:jump24:normal
.bbl init 4
    mov_imm al r0 0
    bl al lr expr:call:brk
    mov_regimm al r9 lsl r0 0
    mov_regimm al r3 lsl r9 0
    movw al r0 expr:movw_abs_nc:$$malloc_state
    movt al r0 expr:movt_abs:$$malloc_state
    str_imm_add al r0 0 r9
    movw al r0 expr:movw_abs_nc:$$malloc_state:4
    movt al r0 expr:movt_abs:$$malloc_state:4
    str_imm_add al r0 0 r9
.bbl normal 4
    add_regimm al r7 r9 lsl r8 0
    cmp_regimm al r7 lsl r3 0
    b ls expr:jump24:done
.bbl normal_1 4
    add_imm al r6 r3 2097152
    mov_regimm al r0 lsl r6 0
    movw al r1 0
    movt al r1 65520
    and_regimm al r0 r0 lsl r1 0
    mov_regimm al r6 lsl r0 0
    mov_regimm al r0 lsl r6 0
    bl al lr expr:call:brk
    cmp_regimm al r0 lsl r6 0
    b eq expr:jump24:done_after_brk
.bbl normal_2 4
    mov_imm al r0 0
    add_imm al sp sp 12
    ldmia_update al reglist:0x83c0 sp
.bbl done_after_brk 4
    movw al r0 expr:movw_abs_nc:$$malloc_state:4
    movt al r0 expr:movt_abs:$$malloc_state:4
    str_imm_add al r0 0 r6
.bbl done 4
    movw al r0 expr:movw_abs_nc:$$malloc_state
    movt al r0 expr:movt_abs:$$malloc_state
    str_imm_add al r0 0 r7
    mov_regimm al r0 lsl r9 0
    add_imm al sp sp 12
    ldmia_update al reglist:0x83c0 sp
.endfun
# sig: IN: [] -> OUT: []  stk_size:0
.fun dump 16
    stmdb_update al sp reglist:0x40c0
    sub_imm al sp sp 4
.bbl start 4
    movw al r0 expr:movw_abs_nc:COUNTER
    movt al r0 expr:movt_abs:COUNTER
    ldr_imm_add al r0 r0 0
    add_imm al r0 r0 1
    movw al r1 expr:movw_abs_nc:COUNTER
    movt al r1 expr:movt_abs:COUNTER
    str_imm_add al r1 0 r0
    movw al r0 expr:movw_abs_nc:LINE
    movt al r0 expr:movt_abs:LINE
    mov_imm al r1 9
    bl al lr expr:call:writeln
    movw al r6 expr:movw_abs_nc:BOARD
    movt al r6 expr:movt_abs:BOARD
    mov_imm al r7 0
.bbl loop 4
    mov_imm al r1 8
    mov_regimm al r0 lsl r6 0
    bl al lr expr:call:writeln
    add_imm al r6 r6 8
    add_imm al r7 r7 1
    cmp_imm al r7 8
    b cc expr:jump24:loop
.bbl loop_1 4
    add_imm al sp sp 4
    ldmia_update al reglist:0x80c0 sp
.endfun
# sig: IN: [U32] -> OUT: [U32]  stk_size:0
.fun conflict 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl start 4
    mov_regimm al lr lsl r0 0
    cmp_imm al lr 0
    b eq expr:jump24:success
.bbl start_1 4
    movw al r0 expr:movw_abs_nc:XCOORDS
    movt al r0 expr:movt_abs:XCOORDS
    ldrb_reg_add al r0 r0 lsl lr 0
    uxtb al r5 ror_rrx r0 0
    mov_imm al r4 0
.bbl loop 4
    movw al r0 expr:movw_abs_nc:XCOORDS
    movt al r0 expr:movt_abs:XCOORDS
    ldrb_reg_add al r0 r0 lsl r4 0
    uxtb al ip ror_rrx r0 0
    cmp_regimm al ip lsl r5 0
    b eq expr:jump24:conflict
.bbl loop_1 4
    sub_regimm al r2 lr lsl r4 0
    sub_regimm al r3 r5 lsl ip 0
    cmp_regimm al ip lsl r5 0
    b ls expr:jump24:ok
.bbl loop_2 4
    sub_regimm al r3 ip lsl r5 0
.bbl ok 4
    cmp_regimm al r2 lsl r3 0
    b eq expr:jump24:conflict
.bbl ok_1 4
    add_imm al r4 r4 1
    cmp_regimm al r4 lsl lr 0
    b cc expr:jump24:loop
.bbl success 4
    mov_imm al r0 0
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.bbl conflict 4
    mov_imm al r0 1
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun solve 16
    stmdb_update al sp reglist:0x41c0
.bbl start 4
    mov_regimm al r8 lsl r0 0
    cmp_imm al r8 8
    b cc expr:jump24:cont
.bbl start_1 4
    bl al lr expr:call:dump
    ldmia_update al reglist:0x81c0 sp
.bbl cont 4
    mov_imm al r6 0
.bbl loop 4
    mov_regimm al r7 lsl r8 3
    add_regimm al r7 r7 lsl r6 0
    movw al r0 expr:movw_abs_nc:BOARD
    movt al r0 expr:movt_abs:BOARD
    mov_imm al r1 42
    strb_reg_add al r0 lsl r7 0 r1
    mov_regimm al r0 lsl r6 0
    movw al r1 expr:movw_abs_nc:XCOORDS
    movt al r1 expr:movt_abs:XCOORDS
    strb_reg_add al r1 lsl r8 0 r0
    mov_regimm al r0 lsl r8 0
    bl al lr expr:call:conflict
    cmp_imm al r0 1
    b eq expr:jump24:next
.bbl loop_1 4
    add_imm al r8 r8 1
    mov_regimm al r0 lsl r8 0
    bl al lr expr:call:solve
    sub_imm al r8 r8 1
.bbl next 4
    movw al r0 expr:movw_abs_nc:BOARD
    movt al r0 expr:movt_abs:BOARD
    mov_imm al r1 32
    strb_reg_add al r0 lsl r7 0 r1
    add_imm al r6 r6 1
    cmp_imm al r6 8
    b cc expr:jump24:loop
.bbl next_1 4
    ldmia_update al reglist:0x81c0 sp
.endfun
# sig: IN: [] -> OUT: [S32]  stk_size:0
.fun main 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl start 4
    mov_imm al r0 0
    bl al lr expr:call:solve
    movw al r0 expr:movw_abs_nc:COUNTER
    movt al r0 expr:movt_abs:COUNTER
    ldr_imm_add al r0 r0 0
    bl al lr expr:call:print_num_ln
    mov_imm al r0 0
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun
