# exercises address stored as data
# requires std_lib.asm

.mem LINE 4 RO
.data 10 "="

.mem HASH 4 RO
.data 10 "="

.mem SEMI 4 RO
.data 10 ";"

.mem string_pointers 8 RO
.addr.mem 8  LINE 0
.addr.mem 8  HASH 0
.addr.mem 8  SEMI 0


.fun main NORMAL [S32] = []
.reg A64 [s]
.bbl start
    lea.mem x:A64  string_pointers 0
    ld s x 0
    pusharg 10:U32
    pusharg s
    bsr writeln

    ld s x 8
    pusharg 10:U32
    pusharg s
    bsr writeln

    lea.mem x string_pointers 16
    ld s x 0
    pusharg 10:U32
    pusharg s
    bsr writeln

    pusharg 0:S32
    ret




