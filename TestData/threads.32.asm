# thread test

.mem gSLEEP_DUR 16 RO
# one sec
.data 1 [2 0 0 0  0 0 0 0   0 0 0 0   0 0 0 0]


.mem gWORKER_SPAWNED_MSG 1 RO
.data 1 "worker_spawned"
.data 1 [0]

.mem gSTACK 16 RW
.data 655360 [0]

.mem gSUM 16 RW
.data 4 [0]


.fun short_sleep NORMAL [] = []
.bbl entry
    lea.mem sleep_dur:A32 gSLEEP_DUR 0
    pusharg 0:A32
    pusharg sleep_dur
    bsr nanosleep
    poparg res:S32
    ret

# ========================================
.fun worker NORMAL [] = [U32]
.bbl entry
    poparg arg:U32
    mov i:U32 100
.bbl loop
    sub i i 1
.bbl cas_loop
    ld.mem old_val:U32 gSUM 0
    add new_val:U32 old_val arg
    cas.mem prev_val:U32 old_val new_val gSUM 0
    #bsr yield
    #poparg res:S32
    bne prev_val old_val cas_loop 

    bne i 0 loop
    ret

# ========================================
.fun main NORMAL [S32] = []
.bbl entry
    mov i:U32 = 100
    lea.mem stk:A32 gSTACK 0
    lea.fun proc:C32 worker

.bbl loop
    sub i i 1
    lea stk stk 4096
    conv user_arg:U32 i

    # CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM
    pusharg 0x50f00:U32
    pusharg user_arg
    pusharg 0:A32  # tls
    pusharg stk
    pusharg proc
    bsr spawn
    poparg x:S32

    bne i 0 loop
    lea msg:A32 gWORKER_SPAWNED_MSG 0
    pusharg msg
    bsr print_s_ln

    bsr short_sleep
    ld.mem sum:U32 gSUM 0
    conv iarg:U32 sum
    pusharg iarg
    bsr print_x_ln

    pusharg 0:S32
    ret




