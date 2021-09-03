# INT_OP

# ========================================
.fun main NORMAL [S32] = []
    .reg U32 [ru32 nu32]
    .reg U16 [ru16 nu16]
    .reg U8 [ru8 nu8]
    .reg S32 [rs32 ns32]
    .reg S16 [rs16 ns16]
    .reg S8 [rs8 ns8]

.bbl start
##########
    pusharg 10:U8
    bsr print_c_ln

    mov nu32 0
  .bbl shr_u32
    shr ru32 0x87654321:U32 nu32
    pusharg nu32
    bsr print_x_ln
    pusharg ru32
    bsr print_x_ln

    add nu32 nu32 4
    ble  nu32 64 shr_u32
##
    mov nu16 0
  .bbl shr_u16
    shr ru16 0x8765:U16 nu16
    conv ru32 nu16
    pusharg ru32
    bsr print_x_ln
    conv ru32 ru16
    pusharg ru32
    bsr print_x_ln

    add nu16 nu16 4
    ble  nu16 32 shr_u16
##
    mov nu8 0
  .bbl shr_u8
    shr ru8 0x87:U8 nu8
    conv ru32 nu8
    pusharg ru32
    bsr print_x_ln
    conv ru32 ru8
    pusharg ru32
    bsr print_x_ln

    add nu8 nu8 1
    ble  nu8 16 shr_u8
##########
    pusharg 10:U8
    bsr print_c_ln

    mov nu32 0
  .bbl shl_u32
    shl ru32 0x87654321:U32 nu32
    pusharg nu32
    bsr print_x_ln
    pusharg ru32
    bsr print_x_ln

    add nu32 nu32 4
    ble  nu32 64 shl_u32
##
    mov nu16 0
  .bbl shl_u16
    shl ru16 0x8765:U16 nu16
    conv ru32 nu16
    pusharg ru32
    bsr print_x_ln
    conv ru32 ru16
    pusharg ru32
    bsr print_x_ln

    add nu16 nu16 4
    ble  nu16 32 shl_u16
##
    mov nu8 0
  .bbl shl_u8
    shl ru8 0x87:U8 nu8
    conv ru32 nu8
    pusharg ru32
    bsr print_x_ln
    conv ru32 ru8
    pusharg ru32
    bsr print_x_ln

    add nu8 nu8 1
    ble  nu8 16 shl_u8
##########
    pusharg 10:U8
    bsr print_c_ln

    mov ns32 0
  .bbl shr_s32
    shr rs32 -2023406815:S32 ns32   # 0x87654321
    conv ru32 ns32
    pusharg ru32
    bsr print_x_ln
    conv ru32 rs32
    pusharg ru32
    bsr print_x_ln

    add ns32 ns32 4
    ble  ns32 64 shr_s32
##
    mov ns16 0
  .bbl shr_s16
    shr rs16 -30875:S16 ns16  # 0x8765
    conv ru32 ns16
    pusharg ru32
    bsr print_x_ln
    conv ru32 rs16
    pusharg ru32
    bsr print_x_ln

    add ns16 ns16 4
    ble  ns16 32 shr_s16
##
    mov ns8 0
  .bbl shr_s8
    shr rs8 -121:S8 ns8  # 0x87
    conv ru32 ns8
    pusharg ru32
    bsr print_x_ln
    conv ru32 rs8
    pusharg ru32
    bsr print_x_ln

    add ns8 ns8 1
    ble  ns8 16 shr_s8
##########
    pusharg 10:U8
    bsr print_c_ln
    
    mov ns32 0
  .bbl shr_s32_2
    shr rs32 0x12345678:S32 ns32   # 0x87654321
    conv ru32 ns32
    pusharg ru32
    bsr print_x_ln
    conv ru32 rs32
    pusharg ru32
    bsr print_x_ln

    add ns32 ns32 4
    ble  ns32 64 shr_s32_2
##
    mov ns16 0
  .bbl shr_s16_2
    shr rs16 0x1234:S16 ns16  # 0x8765
    conv ru32 ns16
    pusharg ru32
    bsr print_x_ln
    conv ru32 rs16
    pusharg ru32
    bsr print_x_ln

    add ns16 ns16 4
    ble  ns16 32 shr_s16_2
##
    mov ns8 0
  .bbl shr_s8_2
    shr rs8 0x12:S8 ns8  # 0x87
    conv ru32 ns8
    pusharg ru32
    bsr print_x_ln
    conv ru32 rs8
    pusharg ru32
    bsr print_x_ln

    add ns8 ns8 4
    ble  ns8 16 shr_s8_2
##########
    pusharg 0:S32
    ret
