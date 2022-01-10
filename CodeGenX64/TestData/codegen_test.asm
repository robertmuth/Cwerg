
.mem COUNTER 4 RW
.data 4 [0]

.fun TestMoveImmediates NORMAL [] = [A64]
  .reg U32 [$r0 $r1 $r2 $r3 bitu]
  .reg S32 [$r0_S32 bits]
  .reg S64 [$r10 $r11 $12]
  .reg F32 [$f0 $f1 $f2]
  .reg F64 [$f10 $f11 $f12]
  .reg U8 [$r0_U8 %U8_857]
  .reg A64 [addr1 addr2]
.bbl int
    add $r10@rax $r10@rax 0x12345678:S64
    and $r1@rdx $r1@rdx 42
    xor $r2@rdx $r2@rdx $r3@rcx
    ld  $r2@rdx addr1@rdx 0x20:S32
    ld  $r2@rdx addr1@rdx $r0_U8@rdx
    lea addr1@rdx addr1@rdx $r0_U8@rdx
    conv bits@STK %U8_857@rcx
    conv bitu@STK %U8_857@rcx

.bbl flt
    add $f1@xmm0 $f1@xmm0 $f2@xmm1

    ret




