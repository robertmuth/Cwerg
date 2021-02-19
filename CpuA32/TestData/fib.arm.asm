.fun fibonacci 16
     stm  al PuW sp reglist:16576
.bbl start 0
     mov_regimm al r6 lsl r0 #0
     cmp_imm al r6 #1
     b  hi expr:b.pcrel:difficult

.bbl start_2 0 
     mov_regimm al r0 lsl r6 #0
     ldm  al reglist:32960 pUW sp

.bbl difficult 0
     sub_imm al r0 r6 #1
     bl  al lr expr:bl.pcrel:fibonacci
     add_imm al r7 r0 #0
     sub_imm al r0 r6 #2
     bl  al lr expr:bl.pcrel:fibonacci
     add_regimm al r0 r7 lsl r0 #0
     ldm  al reglist:32960 pUW sp
.endfun

.mem fmt 4 rodata
  .data 1 "%d\n\0"
.endmem
	
.fun main 16
     stm  al PuW sp reglist:16384

.bbl start 0
     mov_imm al r0 #7
     bl  al lr expr:bl.pcrel:fibonacci
     mov_regimm al r1 lsl r0 #0
     movw  al r0 expr:movw.lower16:fmt:0
     movt  al r0 expr:movt.uppper16:fmt:0
     bl  al lr expr:bl.pcrel:printf_u
     mov_imm al r0 #0
     ldm  al reglist:32768 pUW sp
.endfun
