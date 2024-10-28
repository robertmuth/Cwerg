.fun _start NORMAL [] = []
.bbl entry
  # set rounding mode 
  inline "stmxcsr_32_mbis8 rsp noindex 0 -4"
  inline "and_32_mbis8_imm32 rsp noindex 0 -4 0xffff9fff"
  inline "or_32_mbis8_imm32 rsp noindex 0 -4 0x2000"
  inline "ldmxcsr_32_mbis8 rsp noindex 0 -4"
  bsr main
  poparg res:S32
  pusharg res
  bsr exit
  ret
