
.fun a32_syscall_write SIGNATURE [] = [U32 A32 U32]
.fun a32_syscall_exit SIGNATURE [] = [U32]

.mem msg 4 RO
.data 1 "hello world\n"


.fun _start NORMAL [] = []
.bbl start
    mov len:U32 = 12  # strlen(msg)
    lea m:A32 = msg
    mov fh:U32 = 1   # stdout
    pusharg len
    pusharg m
    pusharg fh
    syscall a32_syscall_write 4:U8

    mov out:U32 = 0
    pusharg out
    syscall a32_syscall_exit 1:U8

    ret




