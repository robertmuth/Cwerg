    .intel_syntax noprefix

    .global _start

	.section ".rodata"
_msg:
    .ascii  "Hello, world (asm)\n"
_msg_end:
	
    .text
_start:
        # write(1, _msg, len(_msg))
        mov     rax, 1
        mov     rdi, 1
        lea     rsi, _msg
        mov     rdx, _msg_end - _msg
        syscall                   

        # exit(0)
        mov     rax, 60
        xor     rdi, rdi
        syscall


