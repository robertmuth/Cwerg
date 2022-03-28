#   When Linux transfers control to a new A32 program is does not follow any calling
#    convention so we need this shim.
#    The initial execution env looks like this:
#    0(sp)			argc
#
#    4(sp)			    argv[0] # argv start
#    8(sp)              argv[1]
#    ...
#    (4*argc)(sp)       NULL    # argv sentinel

#    (4*(argc+1))(sp)   envp[0] # envp start
#    (4*(argc+2))(sp)   envp[1]
#    ...
#                       NULL    # envp sentinel

.fun _start NORMAL [] = []
.bbl entry
  getfp fp:A32
  ld argc:S32 fp 0
  lea argv:A32 fp 4
  # the envp starts (argv + 1) pointers after argv
  # shr envp_offset:U32 argc 2
  # add envp_offset 8
  # lea envp:A32 fp envp_offset
  pusharg argv
  pusharg argc
  bsr main
  poparg res:S32
  pusharg res
  bsr exit
  ret