# based on
# https://github.com/bytecodealliance/wasmtime/blob/main/docs/WASI-tutorial.md

.fun fd_write NORMAL [S32] = [A32 S32 S32 S32 S32]

  .bbl %start
    poparg mem_base:A32
    poparg fd:S32
    poparg array_offset:S32
    poparg array_size:S32
    poparg result_offset:S32

    lea array:A32 mem_base array_offset
    lea result:A32 mem_base result_offset
    mov count:S32 0:S32
    mov errno:S32 0:S32
    bra check

  .bbl loop
    ld buf:A32 array 0:U32
    ld len:U32 array 4:U32
    lea array array 8:U32
    sub array_size array_size 1
    pusharg len
    pusharg buf
    pusharg fd
    bsr write
    poparg errno
    blt errno 0 epilog
    add count count errno
  .bbl check
    blt 0:U32 array_size loop
  .bbl epilog
    st result 0:U32 count
    pusharg errno
    ret


