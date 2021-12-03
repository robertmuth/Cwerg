
.mem fmt 4 rodata
    .data 1 "hello, world (x64)\n"
.endmem

.fun _start 16
    mov_64_mr_imm32 rdi 1      # stdout
    mov_64_mr_imm32 rdx 0x13   # size of string
    lea_64_r_mpc32  rsi rip expr:pcrel32:fmt:-4
    mov_64_mr_imm32 rax 1      # sycall write
    syscall

    xor_64_mr_r     rdi rdi
    mov_64_mr_imm32 rax 0x3c  # syscall exit
    syscall
.endfun

