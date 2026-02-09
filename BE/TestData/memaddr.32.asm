# exercises address stored as data
# requires std_lib.asm

.mem LINE 4 RO
.data 10 "="

.mem HASH 4 RO
.data 10 "="

.mem SEMI 4 RO
.data 10 ";"

.mem string_pointers 8 RO
.addr.mem 4  LINE 0
.addr.mem 4  HASH 0
.addr.mem 4  SEMI 0


.fun main NORMAL [S32] = []
.reg A32 s
.bbl start
    lea.mem x:A32  string_pointers 0
    ld s x 0
    pusharg 10:U32
    pusharg s
    bsr print_ln

    ld s x 4
    pusharg 10:U32
    pusharg s
    bsr print_ln

    lea.mem x string_pointers 8
    ld s x 0
    pusharg 10:U32
    pusharg s
    bsr print_ln

    pusharg 0:S32
    ret




