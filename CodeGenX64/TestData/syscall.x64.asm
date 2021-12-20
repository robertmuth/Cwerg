
.fun x64_syscall_write SIGNATURE [S32] = [S32 A64 U64]
.fun x64_syscall_exit SIGNATURE [] = [S32]

.mem msg 4 RO
.data 1 "hello world\n"


.fun _start NORMAL [] = []
.bbl start
    lea m:A64 = msg
    pusharg 12:U64
    pusharg m
    pusharg 1:S32
    syscall x64_syscall_write 1:U8
    poparg dummy:S32
	
    pusharg 0:S32
    syscall x64_syscall_exit 60:U8
    ret




