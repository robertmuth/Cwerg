
.mem COUNTER 4 RW
.data 4 [0]

.fun TestMoveImmediates NORMAL [] = [A64]
  .reg U32 [$r0 $r1 $r2 $r3]
  .reg S32 [$r0_S32]
  .reg S64 [$r10 $r11 $12]
  .reg F32 [$f0 $f1 $f2]
  .reg F64 [$f10 $f11 $f12]

  .reg U8 [$r0_U8]
  .reg A64 [addr]
.bbl int
    add $r10@rax $r10@rax 0x12345678:S64
    and $r1@rdx $r1@rdx 42
    xor $r2@rdx $r2@rdx $r3@rcx
.bbl flt
    add $f1@xmm0 $f1@xmm0 $f2@xmm1

    ret




