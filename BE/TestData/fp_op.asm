


.fun mul_f32 NORMAL [] = [S32 R32 R32 R32]
  .reg U32 [tmp]
  .reg R32 [dst expected src1 src2]
  .bbl prolog
    poparg testno:S32
    poparg expected
    poparg src1
    poparg src2
    mul dst src1 src2
    beq dst expected ok
    pusharg testno
    bsr print_d_ln
    bitcast tmp expected
    pusharg tmp
    bsr print_x_ln
    bitcast tmp dst
    pusharg tmp
    bsr print_x_ln
  .bbl ok
    ret

.fun copysign_f32 NORMAL [] = [S32 R32 R32 R32]
  .reg U32 [tmp]
  .reg R32 [dst expected src1 src2]
  .bbl prolog
    poparg testno:S32
    poparg expected
    poparg src1
    poparg src2
    copysign dst src1 src2
    beq dst expected ok
    pusharg testno
    bsr print_d_ln
    bitcast tmp expected
    pusharg tmp
    bsr print_x_ln
    bitcast tmp dst
    pusharg tmp
    bsr print_x_ln
    trap
  .bbl ok
    ret

.fun abs_f32 NORMAL [] = [S32 R32 R32]
  .reg U32 [tmp]
  .reg R32 [dst expected src]
  .bbl prolog
    poparg testno:S32
    poparg expected
    poparg src
    copysign dst src 0.0
    beq dst expected ok
    pusharg testno
    bsr print_d_ln
    bitcast tmp expected
    pusharg tmp
    bsr print_x_ln
    bitcast tmp dst
    pusharg tmp
    bsr print_x_ln
    trap
  .bbl ok
    ret

# ========================================
.fun main NORMAL [S32] = []
  .bbl prolog
    pusharg 0.4:R32
    pusharg 0.0:R32
    pusharg 0.0:R32
    pusharg 101:S32
    bsr mul_f32

    pusharg -4.0:R32
    pusharg -4.0:R32
    pusharg 16.0:R32
    pusharg 102:S32
    bsr mul_f32
##########
    pusharg 0.0:R32
    pusharg 0.0:R32
    pusharg 0.0:R32
    pusharg 201:S32
    bsr copysign_f32

    pusharg 0.0:R32
    pusharg -6.0:R32
    pusharg 6.0:R32
    pusharg 202:S32
    bsr copysign_f32

    pusharg 0.0:R32
    pusharg 6.0:R32
    pusharg 6.0:R32
    pusharg 203:S32
    bsr copysign_f32
##########
    pusharg -66.0:R32
    pusharg 66.0:R32
    pusharg 301:S32
    bsr abs_f32

    pusharg 66.0:R32
    pusharg 66.0:R32
    pusharg 302:S32
    bsr abs_f32

    pusharg 666:S32
    bsr print_d_ln
    pusharg 0:S32
    ret
