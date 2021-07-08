
.mem LINE 4 RO
.data 1 "\n========================================"

.mem BOARD 4 RW
.data 64 [32]    # 32 = space

.mem XCOORDS 4 RW
.data 8 [0]

.mem COUNTER 4 RW
.data 4 [0]

	
.fun exit NORMAL [] = [U32]
# live_out: ['r0']
.reg U32 [$r0_U32 out]
.reg A32 [$sp_A32]
.bbl start
    syscall arm_syscall_exit 1:U32
    ret

.fun brk NORMAL [A32] = [U32]
# live_out: ['r0']
# live_clobber: ['r0']
.reg U32 [$r0_U32 len]
.reg A32 [$r0_A32 $sp_A32 res]
.bbl start  #  live_out[r0]
    syscall arm_syscall_brk 45:U32
    ret

.fun open NORMAL [S32] = [A32 U32 U32]
# live_out: ['r0', 'r1', 'r2']
# live_clobber: ['r0']
.reg S32 [$r0_S32 res]
.reg U32 [$r1_U32 $r2_U32 flags mode]
.reg A32 [$r0_A32 $sp_A32 path]
.bbl start  #  live_out[r0]
    syscall arm_syscall_open 5:U32
    ret

.fun close NORMAL [S32] = [S32]
# live_out: ['r0']
# live_clobber: ['r0']
.reg S32 [$r0_S32 fh res]
.reg A32 [$sp_A32]
.bbl start  #  live_out[r0]
    syscall arm_syscall_close 6:U32
    ret

.fun write NORMAL [S32] = [S32 A32 U32]
# live_out: ['r0', 'r1', 'r2']
# live_clobber: ['r0']
.reg S32 [$r0_S32 fh res]
.reg U32 [$r2_U32 len]
.reg A32 [$r1_A32 $sp_A32 buf]
.bbl start  #  live_out[r0]
    syscall arm_syscall_write 4:U32
    ret

.fun read NORMAL [S32] = [S32 A32 U32]
# live_out: ['r0', 'r1', 'r2']
# live_clobber: ['r0']
.reg S32 [$r0_S32 fh res]
.reg U32 [$r2_U32 len]
.reg A32 [$r1_A32 $sp_A32 buf]
.bbl start  #  live_out[r0]
    syscall arm_syscall_read 3:U32
    ret

.fun putchar NORMAL [] = [U32]
# live_out: ['r0']
.reg S32 [$r0_S32]
.reg U8 [$r1_U8 %ScRaTcH_widening_U8]
.reg U32 [$r0_U32 $r1_U32 $r2_U32 c char]
.reg A32 [$r0_A32 $r1_A32 $sp_A32 buf]
.stk buffer 1 1
.bbl start
    conv $r1_U32@r1 $r0_U32@r0
    mov $r0_A32@r0 $sp_A32@sp
    conv $r1_U8@r1 $r1_U32@r1
    st $sp_A32@sp 0 $r1_U8@r1
    mov $r2_U32@r2 1
    mov $r1_A32@r1 $r0_A32@r0
    mov $r0_S32@r0 1
    syscall arm_syscall_write 4:U32
    ret

.fun writeln NORMAL [] = [A32 U32]
# live_out: ['r0', 'r1']
.reg S32 [$r0_S32]
.reg U32 [$r0_U32 $r1_U32 $r2_U32 len]
.reg A32 [$r0_A32 $r1_A32 $sp_A32 buf]
.bbl start
    mov $r2_U32@r2 $r1_U32@r1
    mov $r1_A32@r1 $r0_A32@r0
    mov $r0_S32@r0 1
    syscall arm_syscall_write 4:U32
    mov $r0_U32@r0 10
    bsr putchar
    ret

.fun print_num NORMAL [] = [U32]
# live_out: ['r0']
.reg U32 [$r0_U32 $r1_U32 %ScRaTcH_elim_imm_U32 div rem x]
.reg A32 [$sp_A32]
.bbl start  #  edge_out[ddd  skip]  live_out[lr  r6]
    mov $r1_U32@r1 $r0_U32@r0
    mov $r0_U32@r0 10
    div rem@r6 $r1_U32@r1 $r0_U32@r0
    mov $r0_U32@r0 10
    mul rem@r6 rem@r6 $r0_U32@r0
    sub rem@r6 $r1_U32@r1 rem@r6
    mov $r0_U32@r0 10
    div div@lr $r1_U32@r1 $r0_U32@r0
    beq div@lr 0 skip
.bbl ddd  #  edge_out[skip]  live_out[r6]
    mov $r0_U32@r0 div@lr
    bsr print_num
.bbl skip
    add rem@r6 rem@r6 48
    mov $r0_U32@r0 rem@r6
    bsr putchar
    ret

.fun print_num_ln NORMAL [] = [U32]
# live_out: ['r0']
.reg U32 [$r0_U32 x]
.reg A32 [$sp_A32]
.bbl start
    bsr print_num
    mov $r0_U32@r0 10
    bsr putchar
    ret

.fun dump NORMAL [] = []
.reg U32 [$r0_U32 $r1_U32 count i]
.reg A32 [$r0_A32 $sp_A32 %ScRaTcH_base_A32 board line]
.bbl start  #  edge_out[loop]  live_out[r6  r7]
    lea.mem $r0_A32@r0 COUNTER 0
    ld $r0_U32@r0 $r0_A32@r0 0
    add $r1_U32@r1 $r0_U32@r0 1
    lea.mem $r0_A32@r0 COUNTER 0
    st $r0_A32@r0 0 $r1_U32@r1
    lea.mem $r0_A32@r0 LINE 0
    mov $r1_U32@r1 9
    bsr writeln
    lea.mem board@r6 BOARD 0
    lea.mem board@r6 BOARD $r1_U32@r1
    mov i@r7 0
.bbl loop  #  edge_out[loop  loop_1]  live_out[r6  r7]
    mov $r1_U32@r1 8
    mov $r0_A32@r0 board@r6
    bsr writeln
    lea board@r6 board@r6 8
    add i@r7 i@r7 1
    blt i@r7 8 loop
.bbl loop_1
    ret

.fun conflict NORMAL [U32] = [U32]
# live_out: ['r0']
# live_clobber: ['r0']
.reg U8 [$r6_U8 %ScRaTcH_widening_U8]
.reg U32 [$r0_U32 d1 d2 i lastx x y]
.reg A32 [$r6_A32 $sp_A32 %ScRaTcH_base_A32]
.bbl start  #  edge_out[start_1  success]  live_out[r12]
    mov y@r12 $r0_U32@r0
    beq y@r12 0 success
.bbl start_1  #  edge_out[loop]  live_out[r12  r2  r3]
    lea.mem $r6_A32@r6 XCOORDS 0
    ld $r6_U8@r6 $r6_A32@r6 y@r12
    conv lastx@r3 $r6_U8@r6
    mov i@r2 0
.bbl loop  #  edge_out[conflict  loop_1]  live_out[r12  r2  r3  r5]
    lea.mem $r6_A32@r6 XCOORDS 0
    ld $r6_U8@r6 $r6_A32@r6 i@r2
    conv x@r5 $r6_U8@r6
    beq x@r5 lastx@r3 conflict
.bbl loop_1  #  edge_out[loop_2  ok]  live_out[r0  r1  r12  r2  r3  r5]
    sub d1@r0 y@r12 i@r2
    sub d2@r1 lastx@r3 x@r5
    ble x@r5 lastx@r3 ok
.bbl loop_2  #  edge_out[ok]  live_out[r0  r1  r12  r2  r3]
    sub d2@r1 x@r5 lastx@r3
.bbl ok  #  edge_out[conflict  ok_1]  live_out[r12  r2  r3]
    beq d1@r0 d2@r1 conflict
.bbl ok_1  #  edge_out[loop  success]  live_out[r12  r2  r3]
    add i@r2 i@r2 1
    blt i@r2 y@r12 loop
.bbl success  #  live_out[r4]
    mov $r0_U32@r0 0
    ret
.bbl conflict  #  live_out[r4]
    mov $r0_U32@r0 1
    ret

.fun solve NORMAL [] = [U32]
# live_out: ['r0']
.reg U8 [$r0_U8 $r1_U8 %ScRaTcH_elim_imm_U8 %ScRaTcH_widening_U8]
.reg U32 [$r0_U32 i pos res y]
.reg A32 [$r0_A32 $r1_A32 $sp_A32 %ScRaTcH_base_A32]
.bbl start  #  edge_out[cont  start_1]  live_out[r8]
    mov y@r8 $r0_U32@r0
    blt y@r8 8 cont
.bbl start_1
    bsr dump
    ret
.bbl cont  #  edge_out[loop]  live_out[r6  r8]
    mov i@r6 0
.bbl loop  #  edge_out[loop_1  next]  live_out[r6  r7  r8]
    shl pos@r7 y@r8 3
    add pos@r7 pos@r7 i@r6
    lea.mem $r1_A32@r1 BOARD 0
    mov $r0_U8@r0 42
    st $r1_A32@r1 pos@r7 $r0_U8@r0
    conv $r1_U8@r1 i@r6
    lea.mem $r0_A32@r0 XCOORDS 0
    st $r0_A32@r0 y@r8 $r1_U8@r1
    mov $r0_U32@r0 y@r8
    bsr conflict
    beq $r0_U32@r0 1 next
.bbl loop_1  #  edge_out[next]  live_out[r6  r7  r8]
    add y@r8 y@r8 1
    mov $r0_U32@r0 y@r8
    bsr solve
    sub y@r8 y@r8 1
.bbl next  #  edge_out[loop  next_1]  live_out[r6  r8]
    lea.mem $r1_A32@r1 BOARD 0
    mov $r0_U8@r0 32
    st $r1_A32@r1 pos@r7 $r0_U8@r0
    add i@r6 i@r6 1
    blt i@r6 8 loop
.bbl next_1
    ret

.fun _start NORMAL [] = []
.reg U32 [$r0_U32 count]
.reg A32 [$r0_A32 $sp_A32 %ScRaTcH_base_A32]
.bbl start
    mov $r0_U32@r0 0
    bsr solve
    lea.mem $r0_A32@r0 COUNTER 0
    ld $r0_U32@r0 $r0_A32@r0 0
    bsr print_num
    mov $r0_U32@r0 10
    bsr putchar
    mov $r0_U32@r0 0
    bsr exit
    ret

.fun TestMoveImmediates NORMAL [] = []
.reg S32 [x]
.bbl start
    mov x@r0 66
    mov x@r0 -66
    mov x@r0 26112 # 0x6600
    mov x@r0 -26112
    mov x@r0 666
    mov x@r0 -666
    mov x@r0 66666
    mov x@r0 -66666
    ret

.fun TestLdStImmediates NORMAL [] = []
.reg S32 [x]
.reg U32 [y]
.reg A32 [base]
.reg U8 [ua]
.reg U16 [ub]
.reg S8 [sa]
.reg S16 [sb]

.bbl start
    ld ua@r6 base@r6 66:S32
    ld ua@r6 base@r6 -66:S32
    ld sa@r6 base@r6 66:S32
    ld sa@r6 base@r6 -66:S32
    ld ua@r6 base@r6 666:S32
    ld ua@r6 base@r6 -666:S32
    ld sa@r6 base@r6 666:S32   # out of bounds
    ld sa@r6 base@r6 -666:S32  # outo of bounds

    #
    st base@r6 66:S32 ua@r6
    st base@r6 -66:S32 sa@r6
    st base@r6 66:S32 ua@r6
    st base@r6 -66:S32 sa@r6
    st base@r6 666:S32 ua@r6
    st base@r6 -666:S32 sa@r6
    st base@r6 666:S32 ua@r6
    st base@r6 -666:S32 sa@r6

    #
    ld ub@r6 base@r6 66:S32
    ld ub@r6 base@r6 -66:S32
    ld sb@r6 base@r6 66:S32
    ld sb@r6 base@r6 -66:S32
    ld ub@r6 base@r6 666:S32 # out of bounds
    ld ub@r6 base@r6 -666:S32 # out of bounds
    ld sb@r6 base@r6 666:S32   # out of bounds
    ld sb@r6 base@r6 -666:S32  # outo of bounds

    #
    st base@r6 66:S32 ub@r6
    st base@r6 -66:S32 sb@r6
    st base@r6 66:S32 ub@r6
    st base@r6 -66:S32 sb@r6
    st base@r6 666:S32 ub@r6 # out of bounds
    st base@r6 -666:S32 sb@r6 # out of bounds
    st base@r6 666:S32 ub@r6 # out of bounds
    st base@r6 -666:S32 sb@r6 # out of bounds
    mov x@r1 454
    mov y@r1 0xfffffff0
    and y@r1 y@r1 0xfffffff0
    ret

.fun TestLea NORMAL [] = []
.reg S32 [x]
.reg A32 [base]

.bbl start
    lea base@r6 base@r6 66:S32
    lea base@r6 base@r6 -66:S32
    ret

# TODO: add flt ld/st tests
.fun TestStk_gpr_scratch NORMAL [] = []
.reg S32 [x]
.reg S16 [y]
.stk buffer 4 1000004

.bbl start
    st.stk buffer 0:U32 66:S32
    st.stk buffer 0:U32 x@r1
    st.stk buffer 0:U32 y@r2
    ld.stk x buffer 0:U32
    ld.stk y buffer 0:U32


    st.stk buffer 10:U32  66:S32
    st.stk buffer 10:U32  x@r1
    st.stk buffer 10:U32  y@r2
    ld.stk x buffer 10:U32
    ld.stk y buffer 10:U32


    st.stk buffer 100:U32  66:S32
    st.stk buffer 100:U32  x@r1
    st.stk buffer 100:U32  y@r2
    ld.stk x buffer 100:U32
    ld.stk y buffer 100:U32


    st.stk buffer 1000:U32  66:S32
    st.stk buffer 1000:U32  x@r1
    st.stk buffer 1000:U32  y@r2
    ld.stk x buffer 1000:U32
    ld.stk y buffer 1000:U32

    st.stk buffer 100000:U32  66:S32
    st.stk buffer 100000:U32  x@r1
    st.stk buffer 100000:U32  y@r2
    ld.stk x buffer 100000:U32
    ld.stk y buffer 100000:U32

    st.stk buffer 1000000:U32  66:S32
    st.stk buffer 1000000:U32  x@r1
    st.stk buffer 1000000:U32  y@r2
    ld.stk x buffer 1000000:U32
    ld.stk y buffer 1000000:U32
    ret
