# INT_OP

# ========================================
.fun shr_u32 NORMAL [] = [U32 U32 U32]
  .reg U32 [n r val max step]
  .reg U32 [tmp]
  .bbl prolog
    poparg val
    poparg max
    poparg step
    mov n 0
  .bbl loop
    shr r val n
    conv tmp n
    pusharg tmp
    bsr print_x_ln
    conv tmp r
    pusharg tmp
    bsr print_x_ln

    add n n step
    ble  n max loop
    ret


.fun shr_u16 NORMAL [] = [U16 U16 U16]
  .reg U16 [n r val max step]
  .reg U32 [tmp]
    .bbl prolog
    poparg val
    poparg max
    poparg step
    mov n 0
  .bbl loop
    shr r val n
    conv tmp n
    pusharg tmp
    bsr print_x_ln
    conv tmp r
    pusharg tmp
    bsr print_x_ln

    add n n step
    ble  n max loop
    ret

.fun shr_u8 NORMAL [] = [U8 U8 U8]
  .reg U8 [n r val max step]
  .reg U32 [tmp]
    .bbl prolog

    poparg val
    poparg max
    poparg step
    mov n 0
  .bbl loop
    shr r val n
    conv tmp n
    pusharg tmp
    bsr print_x_ln
    conv tmp r
    pusharg tmp
    bsr print_x_ln

    add n n step
    ble  n max loop
    ret

# ========================================
.fun shl_u32 NORMAL [] = [U32 U32 U32]
  .reg U32 [n r val max step]
  .reg U32 [tmp]
    .bbl prolog

    poparg val
    poparg max
    poparg step
    mov n 0
  .bbl loop
    shl r val n
    conv tmp n
    pusharg tmp
    bsr print_x_ln
    conv tmp r
    pusharg tmp
    bsr print_x_ln

    add n n step
    ble  n max loop
    ret


.fun shl_u16 NORMAL [] = [U16 U16 U16]
  .reg U16 [n r val max step]
  .reg U32 [tmp]
    .bbl prolog

    poparg val
    poparg max
    poparg step
    mov n 0
  .bbl loop
    shl r val n
    conv tmp n
    pusharg tmp
    bsr print_x_ln
    conv tmp r
    pusharg tmp
    bsr print_x_ln

    add n n step
    ble  n max loop
    ret

.fun shl_u8 NORMAL [] = [U8 U8 U8]
  .reg U8 [n r val max step]
  .reg U32 [tmp]
    .bbl prolog

    poparg val
    poparg max
    poparg step
    mov n 0
  .bbl loop
    shl r val n
    conv tmp n
    pusharg tmp
    bsr print_x_ln
    conv tmp r
    pusharg tmp
    bsr print_x_ln

    add n n step
    ble  n max loop
    ret

# ========================================
.fun shr_s32 NORMAL [] = [S32 S32 S32]
  .reg S32 [n r val max step]
  .reg U32 [tmp]
  .bbl prolog
    poparg val
    poparg max
    poparg step
    mov n 0
  .bbl loop
    shr r val n
    conv tmp n
    pusharg tmp
    bsr print_x_ln
    conv tmp r
    pusharg tmp
    bsr print_x_ln

    add n n step
    ble  n max loop
    ret


.fun shr_s16 NORMAL [] = [S16 S16 S16]
  .reg S16 [n r val max step]
  .reg U32 [tmp]
  .bbl prolog
    poparg val
    poparg max
    poparg step
    mov n 0
  .bbl loop
    shr r val n
    conv tmp n
    pusharg tmp
    bsr print_x_ln
    conv tmp r
    pusharg tmp
    bsr print_x_ln

    add n n step
    ble  n max loop
    ret

.fun shr_s8 NORMAL [] = [S8 S8 S8]
  .reg S8 [n r val max step]
  .reg U32 [tmp]
  .bbl prolog
    poparg val
    poparg max
    poparg step
    mov n 0
  .bbl loop
    shr r val n
    conv tmp n
    pusharg tmp
    bsr print_x_ln
    conv tmp r
    pusharg tmp
    bsr print_x_ln

    add n n step
    ble  n max loop
    ret

# ========================================
.fun main NORMAL [S32] = []
    .reg U32 [ru32 nu32]
    .reg U16 [ru16 nu16]
    .reg U8 [ru8 nu8]
    .reg S32 [rs32 ns32]
    .reg S16 [rs16 ns16]
    .reg S8 [rs8 ns8]

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

    pusharg 0:S32
    ret
