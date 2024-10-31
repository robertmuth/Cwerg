
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
    conv $r0_U32@x10 $r0_U8@x10
    mov $r0_S32@x11 -100:S32
    mov $r0_U32@x10 525032:U32
    mov addr@x20 0x1234567890123456:A64
    lea addr@x20 = buffer 0:U32
    lea.mem addr@x20 COUNTER 100:S32
    lea.mem addr@x20 COUNTER $r0_U32@x10
    mov $r1_U32@x11 $r0_U32@x10
    mov $r0_U32@x10 10
    div rem@x5 $r1_U32@x11 $r0_U32@x10
    mov $r0_U32@x10 10
    mul rem@x5 rem@x5 $r0_U32@x10
    sub rem@x5 $r1_U32@x11 rem@x5
    mov $r0_U32@x10 10
    bne  $r0_U32@x10 148932 skip
    mov $r0_U32@x10 148932
    div div@x6 $r1_U32@x11 $r0_U32@x10
    beq div@x6 0 skip

.bbl skip
    poparg base:A64
    ld add:A64@x23  base@x22 0:U32
    ret

.fun TestR64 NORMAL [R64] = [R64 R64]
  .reg R64 [d1 d2 d3]
.bbl start
   cmplt d3@d0 0.0:R64 d1@d1 d2@d2 0.0:R64
.bbl skip
     ret

.fun TestMoveImmediates_gpr_scratch NORMAL [] = [A64]
  .reg S32 [$r0_S32]
  .reg U8 [$r0_U8]
  .reg A64 [addr]
  .reg R32 [flt]
  .reg R64 [dbl]
   .stk buffer 16 16
.bbl start
     copysign flt@d1 flt@d1 0:R32   # abs
     copysign dbl@d2 dbl@d2 0:R64   # abs
     st.stk buffer 0:U32 dbl
     ld.stk flt buffer 0:U32
     beq dbl@d2 0.0 skip
     copysign flt@d1 flt@d1 flt@d1
     copysign dbl@d2 dbl@d2 dbl@d2
.bbl skip
     ret

.fun TestLea NORMAL [] = []
  .reg A64 [fp argv]
  .bbl entry
#  TODO: try negative offsets
#  lea argv@x1 fp@x2 -8:S64

  lea argv@x1 fp@x2 8:U64
  ret
