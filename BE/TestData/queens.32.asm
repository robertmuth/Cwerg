# classic n-queens puzzle
# requires std_lib.asm

.mem LINE 4 RO
.data 1 "\n========================================"

.mem BOARD 4 RW
.data 64 [32]    # 32 = space

.mem XCOORDS 4 RW
.data 8 [0]

.mem COUNTER 4 RW
.data 4 [0]

# ========================================
.fun dump NORMAL [] = []
.bbl start
     # inc counter
     lea counter:A32 = COUNTER
     ld count:U32 = counter 0
     add count = count 1
     st counter 0 = count

     mov len:U32 9
     lea line:A32 = LINE
     pusharg len
     pusharg line
     bsr print_ln

     lea board:A32 = BOARD
     mov dim:U32 = 8
     mov i:U32 = 0
.bbl loop
     pusharg dim
     pusharg board
     bsr print_ln
     lea board = board dim
     add i = i 1
     blt i 8 loop
     ret

# ========================================
.fun conflict NORMAL [U8] = [U8]
.bbl start
    poparg y:U8
    beq y 0 success
    lea xcoords:A32 = XCOORDS
    ld lastx:U8 = xcoords  y
    mov i:U8 = 0
.bbl loop
    ld x:U8 = xcoords  i
    beq x lastx conflict
    sub d1:U8 = y i
    sub d2:U8 = lastx x
    ble x lastx ok
    sub d2 = x lastx
.bbl ok
    beq d1 d2 conflict
    add i = i 1
    blt i y loop
.bbl success
    mov res:U8 0
    pusharg res
    ret
.bbl conflict
    mov res 1
    pusharg res
    ret

# ========================================
.fun solve NORMAL [] = [U8]
.bbl start
    poparg y:U8
    blt y 8 cont
    bsr dump
    ret
 .bbl cont
    mov empty:U8 = 32
    mov queen:U8 = 42
    lea xcoords:A32 = XCOORDS
    lea board:A32 = BOARD
    mov i:U8 = 0
 .bbl loop
    mul pos:U8 = y 8
    add pos = pos i
    st board pos = queen
    #bsr dump [] = []
    st xcoords y = i
    pusharg y
    bsr conflict
    poparg res:U8
    beq res 1 next
    add y = y 1
    pusharg y
    bsr solve
    sub y = y 1
 .bbl next
    st board pos = empty
    add i = i 1
    blt i 8 loop
    ret



# ========================================
.fun main NORMAL [S32] = []
.bbl start
    pusharg 0:U8
    bsr solve

    lea counter:A32 = COUNTER
    ld count:U32 = counter 0
    pusharg count
    bsr print_u_ln

    pusharg 0:S32
    ret
