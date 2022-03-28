

#    When Linux transfers control to a binary is does not follow any calling
#    convention so we need this shim.
#    The initial execution env looks like this:
#    0(sp)			         argc
#    8(sp)			         argv[0] # argv start
#    16(sp)              argv[1]
#    ...
#    (8*argc)(sp)        NULL    # argv sentinel
#
#    (8*(argc+1))(sp)    envp[0] # envp start
#    (8*(argc+2))(sp)    envp[1]
#    ...
#                        NULL    # envp sentinel

.fun _start NORMAL [] = []
.bbl entry
  getfp fp:A64
  ld argc:U64 fp 0
  lea argv:A64 fp 8
  # the envp starts (argv + 1) pointers after argv
  # shr envp_offset:U64 argc 3
  # add envp_offset 16
  # lea envp:A64 fp envp_offset
  conv argc_short:S32 argc
  pusharg argv
  pusharg argc_short
  bsr main
  poparg res:S32
  pusharg res
  bsr exit
  ret