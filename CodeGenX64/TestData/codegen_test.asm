
.mem COUNTER 4 RW
.data 4 [0]

.fun TestMoveImmediates NORMAL [] = [A64]
  .reg U32 [$r0 $r1 $r2 $r3]
  .reg S32 [$r0_S32]
  .reg S64 [$r10 $r11 $12]
  .reg U8 [$r0_U8]
  .reg A64 [addr]
.bbl start
    add $r10@rax $r10@rax 0x12345678:S64
    and $r1@rdx $r1@rdx 42
    xor $r2@rdx $r2@rdx $r3@rcx
    ret




