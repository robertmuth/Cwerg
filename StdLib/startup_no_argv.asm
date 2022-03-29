.fun _start NORMAL [] = []
.bbl entry
  bsr main
  poparg res:S32
  pusharg res
  bsr exit
  ret
