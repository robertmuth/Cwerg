

.fun const_1 NORMAL [S32] = []
.bbl start
	pusharg 1:S32
	ret

.fun const_2 NORMAL [S32] = []
.bbl start
	pusharg 2:S32
	ret

	
	
.fun add_them  NORMAL [S32] = [S32 S32]
.bbl start
	poparg dummy2:S32
	poparg dummy3:S32
	add res:S32 dummy2 dummy3
	pusharg res
	ret

	
.fun compute  NORMAL [S32] = []
.reg S32 tmp
.bbl start
	bsr const_1
	poparg tmp
	mov op1:S32 tmp
	bsr const_2
	poparg tmp
	mov op2:S32 tmp
	pusharg op2
	pusharg op1
	bsr add_them
	poparg tmp
	pusharg tmp
	ret
	
.fun main  NORMAL [S32] = []
.bbl start
	bsr compute
	poparg x:S32
	pusharg x
	bsr print_d_ln
	pusharg 0:S32
	ret
