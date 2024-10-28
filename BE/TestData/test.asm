# comment
;;;  comment

.num four pos 4
.num pointone flt .1111
    
    
.mem global1 four ro
	.data 16 [0 0 1 1 2 2 3 3]
	.data 1 "hello world\0"
    
.mem global2 four rw
    
.fun fun1 normal [s32 rout1 u8 rout2] = [s8 rin1 u8 rin2]
    .stk slot1 4 8
    .num minus_one neg -1	
    .num plus_one pos 1	
    .reg [r01 r02 r03] s8
    .reg [r11 r12 r13] s32
    .reg [r21 r22 r23] a32
    .reg [r31 r32 r33] f32
    .reg [r41] a32
    .reg [r91] c32

.bbl start
    xor rout2 rin2 rin2
    add r01 = r02 r03
    add r11 = r12 r13
    add r31 = r32 r33
    add.i r01 = r01 minus_one
    mov.stk r41 = slot1
    mov.mem r41 = global1
    mov r02 = r03
    bra start
    
.bbl loop
    beq start r22 r32
    beq next r22 r32

.bbl next
    mov.fun r91 = fun1
    add r21 = r21 r11
    sub r11 r21 r22
    bsr fun2 [rout1 rout2] = [rin1 rin2]
    ret 
	
.fun fun2 normal [s32 rout1 u8 rout2] = [s8 rin1 u8 rin2]
    .reg [r01 r02 r03] s8
