.text
.global _start

_start:
    mov r0, #1                  @ stdout
    add r1, pc, #(_msg - . - 8) @ pc-rel by hand
    mov r2, #(_msg_end - _msg)
    mov r7, #4                  @ 'write' syscall
    swi #0                  

    mov r0, #0
    mov r7, #1                  @ 'exit' syscall
    swi #0                  

_msg:
      .asciz "Hello world (asm)\n"
_msg_end:	

	.section ".bss"
	.byte 0, 0, 0, 0
	
	.section ".data"
	.byte 1, 2, 3, 4



	.section ".rodata"
	.byte 0, 0, 0, 0
