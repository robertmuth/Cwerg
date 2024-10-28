

#    When Linux transfers control to a binary is does not follow any calling
#    convention so we need this shim.
#    The initial execution env looks like this:
#    0(sp)			    argc
#    8(sp)			    argv[0] # argv start
#    16(sp)               argv[1]
#    ...
#    (8*argc)(sp)        NULL    # argv sentinel
#
#    (8*(argc+1))(sp)    envp[0] # envp start
#    (8*(argc+2))(sp)    envp[1]
#    ...
#                        NULL    # envp sentinel

.fun _start NORMAL [] = []
.bbl entry
  # getfp assumes a return address was pushed onto the stack
  # which is not true at startup so the the fp is off by 8 bytes
  # and points to the beginning of argv
  getfp fp:A64
  ld argc:U64 fp -8
  # the envp starts (argv + 1) pointers after argv
  # shr envp_offset:U64 argc 3
  # add envp_offset 8
  # lea envp:A64 fp envp_offset
  conv argc_short:S32 argc
  # default mxcsr is 0x1f80
  # description: https://wiki.osdev.org/SSE
  # force "rounding down"
  inline "stmxcsr_32_mbis8 rsp noindex 0 -4"
  inline "and_32_mbis8_imm32 rsp noindex 0 -4 0xffff9fff"
  inline "or_32_mbis8_imm32 rsp noindex 0 -4 0x2000"
  inline "ldmxcsr_32_mbis8 rsp noindex 0 -4"
  # [0x0f 0xae 0x5c 0x24 0xfc]                 # stmxcsr -0x4(%rsp)
  # [0x81 0x64 0x24 0xfc 0xff 0x9f 0xff 0xff] 	# andl    $0xffff9fff,-0x4(%rsp)
  # [0x81 0x4c 0x24 0xfc 0x00 0x20 0x00 0x00]	# orl     $0x2000,-0x4(%rsp)
  # [0x0f 0xae 0x54 0x24 0xfc]       	          # ldmxcsr -0x4(%rsp)
  pusharg fp
  pusharg argc_short
  bsr main
  poparg res:S32
  pusharg res
  bsr exit
  ret