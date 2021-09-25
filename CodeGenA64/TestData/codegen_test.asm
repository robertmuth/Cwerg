
.mem COUNTER 4 RW
.data 4 [0]

.fun TestMoveImmediates NORMAL [] = [A64]
  .reg U32 [$r0_U32 $r1_U32 $r2_U32 rem div]
  .reg S32 [$r0_S32]
  .reg S64 [$r10]
  .reg U8 [$r0_U8]
  .reg A64 [addr]
.bbl start
  .stk buffer 1 16
    mov $r10@x20 0x1234567890123456:S64
    and $r10@x20 $r10@x20 4294705151:S64
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
    ld add:A64@x23  base@x22 0:U32
    ret

.fun TestF64 NORMAL [F64] = [F64 F64]
  .reg F64 [d1 d2 d3]
.bbl start
   cmplt d3@d0 0.0:F64 d1@d1 d2@d2 0.0:F64
.bbl skip
     ret

.fun TestMoveImmediates_gpr_scratch NORMAL [] = [A64]
  .reg S32 [$r0_S32]
  .reg U8 [$r0_U8]
  .reg A64 [addr]
  .reg F32 [flt]
  .reg F64 [dbl]
   .stk buffer 16 16
.bbl start
     copysign flt@s1 flt@s1 0:F32   # abs
     copysign dbl@d2 dbl@d2 0:F64   # abs
     st.stk buffer 0:U32 dbl
     ld.stk flt buffer 0:U32
     beq dbl@d2 0.0 skip
     copysign flt@s1 flt@s1 flt@s1
     copysign dbl@d2 dbl@d2 dbl@d2
.bbl skip
     ret



