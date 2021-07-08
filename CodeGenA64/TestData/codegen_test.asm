
.mem COUNTER 4 RW
.data 4 [0]

.fun TestMoveImmediates NORMAL [] = [A64]
.reg U32 [$r0_U32 $r1_U32 $r2_U32 rem div]
.reg S32 [$r0_S32]
.reg U8 [$r0_U8]
.reg A64 [addr]
.bbl start
.stk buffer 1 16
      conv $r0_U32@w10 $r0_U8@w10
      mov $r0_S32@w11 -100:S32
      mov $r0_U32@w10 525032:U32
      mov addr@x20 0x1234567890123456:A64
      lea addr@x20 = buffer 0:U32
      lea.mem addr@x20 COUNTER 100:S32
      lea.mem addr@x20 COUNTER $r0_U32@w10
      mov $r1_U32@w11 $r0_U32@w10
      mov $r0_U32@w10 10
      div rem@w5 $r1_U32@w11 $r0_U32@w10
      mov $r0_U32@w10 10
      mul rem@w5 rem@w5 $r0_U32@w10
      sub rem@w5 $r1_U32@w11 rem@w5
      mov $r0_U32@w10 10
      bne  $r0_U32@w10 148932 skip
      mov $r0_U32@w10 148932
      div div@w6 $r1_U32@w11 $r0_U32@w10
      beq div@w6 0 skip
.bbl skip
    poparg base:A64
    ld add:A64  base 0:U32
    ret



