# demonstrates use of switch instruction for computed jumps
# requires std_lib.asm

# ========================================
.fun main NORMAL [S32] = []
    .reg U32 [size i]

.jtb switch_tab 5 labelD [1 labelA 2 labelB 4 labelC]

.bbl start
    mov i 0

.bbl loop
    switch i switch_tab

.bbl labelA
    pusharg 65:U8  # 'A'
    bsr print_c_ln
    bra tail

.bbl labelB
    pusharg 66:U8 # 'B'
    bsr print_c_ln
    bra tail

.bbl labelC
    pusharg 67:U8 # 'C'
    bsr print_c_ln
    bra tail

.bbl labelD
    pusharg 68:U8  # 'D'
    bsr print_c_ln
    bra tail

.bbl tail
    add i = i 1
    blt i 5 loop

    pusharg 0:S32
    ret
