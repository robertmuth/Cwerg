.text
.global _start

_start:
	mov x0, #1 	// stdout
	adrp x1, _msg
	add x1, x1, :lo12:_msg
	mov x2, #(_msg_end - _msg)
	mov x8, #64  	// 'write' syscall
	svc #0                  

	mov x0, #0
	mov x8, #93 	// 'exit' syscall
	svc #0                  

_msg:
      .asciz "Hello world (asm)\n"
_msg_end:	

	.section ".bss"
	.byte 0, 0, 0, 0
	
	.section ".data"
	.byte 1, 2, 3, 4



	.section ".rodata"
	.byte 0, 0, 0, 0
