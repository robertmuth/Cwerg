# INT_OP


# ========================================
.fun shr_u32 NORMAL [] = [U32 U32 U32]
  .bbl prolog
    poparg val:U32
    poparg max:U32
    poparg step:U32
    mov n:U32 0
  .bbl loop
    shr r:U32 val n
    conv tmp_op1:U32 val
    conv tmp_op2:U32 n
    conv tmp_out:U32 r

    pusharg tmp_op2
    pusharg tmp_op1
    pusharg tmp_out
    bsr print_x_x_x_ln

    add n n step
    ble  n max loop
    ret


.fun shr_u16 NORMAL [] = [U16 U16 U16]
  .bbl prolog
    poparg val:U16
    poparg max:U16
    poparg step:U16
    mov n:U16 0
  .bbl loop
    shr r:U16 val n
    conv tmp_op1:U32 val
    conv tmp_op2:U32 n
    conv tmp_out:U32 r

    pusharg tmp_op2
    pusharg tmp_op1
    pusharg tmp_out
    bsr print_x_x_x_ln

    add n n step
    ble  n max loop
    ret

.fun shr_u8 NORMAL [] = [U8 U8 U8]
  .bbl prolog
    poparg val:U8
    poparg max:U8
    poparg step:U8
    mov n:U8 0
  .bbl loop
    shr r:U8 val n
    conv tmp_op1:U32  val
    conv tmp_op2:U32  n
    conv tmp_out:U32  r

    pusharg tmp_op2
    pusharg tmp_op1
    pusharg tmp_out
    bsr print_x_x_x_ln

    add n n step
    ble  n max loop
    ret

# ========================================
.fun shl_u32 NORMAL [] = [U32 U32 U32]
  .bbl prolog
    poparg val:U32
    poparg max:U32
    poparg step:U32
    mov n:U32 0
  .bbl loop
    shl r:U32 val n
    conv tmp_op1:U32  val
    conv tmp_op2:U32  n
    conv tmp_out:U32  r
    pusharg tmp_op2
    pusharg tmp_op1
    pusharg tmp_out
    bsr print_x_x_x_ln

    add n n step
    ble  n max loop
    ret


.fun shl_u16 NORMAL [] = [U16 U16 U16]
  .bbl prolog
    poparg val:U16
    poparg max:U16
    poparg step:U16
    mov n:U16 0
  .bbl loop
    shl r:U16 val n
    conv tmp_op1:U32  val
    conv tmp_op2:U32  n
    conv tmp_out:U32  r
    pusharg tmp_op2
    pusharg tmp_op1
    pusharg tmp_out
    bsr print_x_x_x_ln

    add n n step
    ble  n max loop
    ret

.fun shl_u8 NORMAL [] = [U8 U8 U8]
  .bbl prolog
    poparg val:U8
    poparg max:U8
    poparg step:U8
    mov n:U8 0
  .bbl loop
    shl r:U8 val n
    conv tmp_op1:U32  val
    conv tmp_op2:U32  n
    conv tmp_out:U32  r
    pusharg tmp_op2
    pusharg tmp_op1
    pusharg tmp_out
    bsr print_x_x_x_ln

    add n n step
    ble  n max loop
    ret

# ========================================
.fun shr_s32 NORMAL [] = [S32 S32 S32]
  .bbl prolog
    poparg val:S32
    poparg max:S32
    poparg step:S32
    mov n:S32 0
  .bbl loop
    shr r:S32 val n
    conv tmp_op1:U32  val
    conv tmp_op2:U32  n
    conv tmp_out:U32  r
    pusharg tmp_op2
    pusharg tmp_op1
    pusharg tmp_out
    bsr print_x_x_x_ln

    add n n step
    ble  n max loop
    ret


.fun shr_s16 NORMAL [] = [S16 S16 S16]
  .bbl prolog
    poparg val:S16
    poparg max:S16
    poparg step:S16
    mov n:S16 0
  .bbl loop
    shr r:S16 val n
    conv tmp_op1:U32  val
    conv tmp_op2:U32  n
    conv tmp_out:U32  r
    pusharg tmp_op2
    pusharg tmp_op1
    pusharg tmp_out
    bsr print_x_x_x_ln


    add n n step
    ble  n max loop
    ret

.fun shr_s8 NORMAL [] = [S8 S8 S8]
  .bbl prolog
    poparg val:S8
    poparg max:S8
    poparg step:S8
    mov n:S8 0
  .bbl loop
    shr r:S8 val n
    conv tmp_op1:U32  val
    conv tmp_op2:U32  n
    conv tmp_out:U32  r
    pusharg tmp_op2
    pusharg tmp_op1
    pusharg tmp_out
    bsr print_x_x_x_ln

    add n n step
    ble  n max loop
    ret


.fun cntlz_u8 NORMAL [] = [U8 U8 U8]
  .bbl prolog

    poparg val:U8
    poparg max:U8
    poparg step:U8
  .bbl loop
    cntlz r:U8 val
    conv tmp_op:U32  val
    conv tmp_out:U32  r
    pusharg tmp_op
    pusharg tmp_out
    bsr print_x_x_ln

    add val val step
    ble  val max loop
    ret

.fun cntlz_u32 NORMAL [] = [U32 U32 U32]
  .bbl prolog
    poparg val:U32
    poparg max:U32
    poparg step:U32
  .bbl loop
    cntlz r:U32 val
    conv tmp_op:U32  val
    conv tmp_out:U32  r
    pusharg tmp_op
    pusharg tmp_out
    bsr print_x_x_ln

    add val val step
    ble  val max loop
    ret


.fun cnttz_u8 NORMAL [] = [U8 U8 U8]
  .bbl prolog
    poparg val:U8
    poparg max:U8
    poparg step:U8
  .bbl loop
    cnttz r:U8 val
    conv tmp_op:U32  val
    conv tmp_out:U32  r
    pusharg tmp_op
    pusharg tmp_out
    bsr print_x_x_ln

    add val val step
    ble  val max loop
    ret

 .fun cnttz_u32 NORMAL [] = [U32 U32 U32]
  .bbl prolog
    poparg val:U32
    poparg max:U32
    poparg step:U32
  .bbl loop
    cnttz r:U32 val
    conv tmp_op:U32  val
    conv tmp_out:U32  r
    pusharg tmp_op
    pusharg tmp_out
    bsr print_x_x_ln

    add val val step
    ble  val max loop
    ret

# ========================================
.fun cntpop_u32 NORMAL [] = [U32 U32 U32]
  .bbl prolog
    poparg val:U32
    poparg max:U32
    poparg step:U32
  .bbl loop
    cntpop r:U32 val
    conv tmp_op:U32  val
    conv tmp_out:U32  r
    pusharg tmp_op
    pusharg tmp_out
    bsr print_x_x_ln

    add val val step
    ble  val max loop
    ret

# ========================================
.fun main NORMAL [S32] = []
    .reg U32 ru32
    .reg U32 nu32
    .reg U16 ru16
    .reg U16 nu16
    .reg U8 ru8
    .reg U8 nu8
    .reg S32 rs32
    .reg S32 ns32
    .reg S16 rs16
    .reg S16 ns16
    .reg S8 rs8
    .reg S8 ns8

.bbl start
    pusharg 10:U8
    bsr print_c_ln
    pusharg 4:U32
    pusharg 64:U32
    pusharg  0x87654321:U32
    bsr shr_u32

    pusharg 10:U8
    bsr print_c_ln
    pusharg 4:U16
    pusharg 32:U16
    pusharg  0x8765:U16
    bsr shr_u16

    pusharg 10:U8
    bsr print_c_ln
    pusharg 2:U8
    pusharg 16:U8
    pusharg  0x87:U8
    bsr shr_u8

##########
    pusharg 10:U8
    bsr print_c_ln
    pusharg 4:U32
    pusharg 64:U32
    pusharg  0x87654321:U32
    bsr shl_u32

    pusharg 10:U8
    bsr print_c_ln
    pusharg 4:U16
    pusharg 32:U16
    pusharg  0x8765:U16
    bsr shl_u16

    pusharg 10:U8
    bsr print_c_ln
    pusharg 2:U8
    pusharg 16:U8
    pusharg  0x87:U8
    bsr shl_u8

##########
    pusharg 10:U8
    bsr print_c_ln
    pusharg 4:S32
    pusharg 64:S32
    pusharg  -2023406815:S32 # 0x87654321
    bsr shr_s32

    pusharg 10:U8
    bsr print_c_ln
    pusharg 4:S16
    pusharg 32:S16
    pusharg -30875:S16 # 0x8765
    bsr shr_s16

    pusharg 10:U8
    bsr print_c_ln
    pusharg 2:S8
    pusharg 16:S8
    pusharg -121:S8 # 0x87
    bsr shr_s8

##########
    pusharg 10:U8
    bsr print_c_ln
    pusharg 4:S32
    pusharg 64:S32
    pusharg  0x12345678:S32
    bsr shr_s32

    pusharg 10:U8
    bsr print_c_ln
    pusharg 4:S16
    pusharg 32:S16
    pusharg 0x1234:S16
    bsr shr_s16

    pusharg 10:U8
    bsr print_c_ln
    pusharg 2:S8
    pusharg 16:S8
    pusharg 0x12:S8
    bsr shr_s8

##########
    pusharg 10:U8
    bsr print_c_ln
    pusharg 1:U8
    pusharg 16:U8
    pusharg 0x0:U8
    bsr cntlz_u8

    pusharg 10:U8
    bsr print_c_ln
    pusharg 1:U32
    pusharg 16:U32
    pusharg 0x0:U32
    bsr cntlz_u32

##########
    pusharg 10:U8
    bsr print_c_ln
    pusharg 1:U8
    pusharg 16:U8
    pusharg 0x0:U8
    bsr cnttz_u8

    pusharg 10:U8
    bsr print_c_ln
    pusharg 1:U32
    pusharg 16:U32
    pusharg 0x0:U32
    bsr cnttz_u32

##########
    pusharg 10:U8
    bsr print_c_ln
    pusharg 0x10001:U32
    pusharg 0x100010:U32
    pusharg 0x0:U32
    bsr cntpop_u32

##########
    pusharg 0:S32
    ret
