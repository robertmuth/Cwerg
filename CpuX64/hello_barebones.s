
        .global _start

	.section ".rodata"
_msg:
        .ascii  "Hello, world (asm)\n"
_msg_end:
	
        .text
_start:
        # write(1, _msg, len(_msg))
        mov     $1, %rax          
        mov     $1, %rdi          
        mov     $_msg, %rsi          
        mov     $_msg_end - _msg, %rdx
        syscall                   

        # exit(0)
        mov     $60, %rax         
        xor     %rdi, %rdi        
        syscall


