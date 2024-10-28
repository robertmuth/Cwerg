# size 8
.mem __static_2__malloc_end 8 data
    .data 8 "\x00"
.endmem
# size 8
.mem __static_1__malloc_start 8 data
    .data 8 "\x00"
.endmem
# sig: IN: [] -> OUT: []  stk_size:0
.fun _start 16
    sub_64_mr_imm32 rsp 0x8
.bbl entry 4
    stmxcsr_32_mbis8 rsp noindex 0 -4
    and_32_mbis8_imm32 rsp noindex 0 -4 0xffff9fff
    or_32_mbis8_imm32 rsp noindex 0 -4 0x2000
    ldmxcsr_32_mbis8 rsp noindex 0 -4
    call_32 expr:pcrel32:main
    mov_32_r_mr ecx eax
    mov_32_r_mr edi ecx
    call_32 expr:pcrel32:exit
    add_64_mr_imm32 rsp 0x8
    ret
.endfun
# sig: IN: [S32] -> OUT: []  stk_size:0
.fun exit 16
.bbl start 4
    mov_32_r_mr ecx edi
    mov_32_r_mr edi ecx
    push_64_mr rcx
    push_64_mr r11
    mov_64_mr_imm32 rax 0x3c
    mov_64_r_mr r10 rcx
    syscall
    pop_64_mr r11
    pop_64_mr rcx
    int3
.endfun
# sig: IN: [S32 A64 U64] -> OUT: [S64]  stk_size:0
.fun write 16
.bbl start 4
    mov_32_r_mr ecx edi
    mov_32_r_mr edi ecx
    push_64_mr rcx
    push_64_mr r11
    mov_64_mr_imm32 rax 0x1
    mov_64_r_mr r10 rcx
    syscall
    pop_64_mr r11
    pop_64_mr rcx
    mov_64_r_mr rcx rax
    mov_64_r_mr rax rcx
    ret
.endfun
# sig: IN: [S32 U8] -> OUT: [S64]  stk_size:16
.fun write_c 16
    sub_64_mr_imm32 rsp 0x18
.bbl %start 4
    mov_32_r_mr ecx edi
    mov_8_r_mr dl sil
    mov_8_mbis32_r rsp noindex 0 0 dl
    lea_64_r_mbis32 rsi rsp noindex 0 0
    mov_64_r_imm64 rdx 0x1
    mov_32_r_mr edi ecx
    call_32 expr:pcrel32:write
    mov_64_r_mr rcx rax
    mov_32_r_mr ecx ecx
    movsxd_64_r_mr rcx ecx
    mov_64_r_mr rax rcx
    add_64_mr_imm32 rsp 0x18
    ret
.endfun
# sig: IN: [U8] -> OUT: []  stk_size:0
.fun print_c_ln 16
    sub_64_mr_imm32 rsp 0x8
.bbl %start 4
    mov_8_r_mr cl dil
    mov_8_r_mr sil cl
    mov_32_r_imm32 edi 0x1
    call_32 expr:pcrel32:write_c
    mov_64_r_mr rcx rax
    mov_8_r_imm8 sil 0xa
    mov_32_r_imm32 edi 0x1
    call_32 expr:pcrel32:write_c
    mov_64_r_mr rcx rax
    add_64_mr_imm32 rsp 0x8
    ret
.endfun
# sig: IN: [] -> OUT: [S32]  stk_size:0
.fun main 16
.localmem switch_tab 8 rodata
    .addr.bbl 8 labelD
    .addr.bbl 8 labelA
    .addr.bbl 8 labelB
    .addr.bbl 8 labelD
    .addr.bbl 8 labelC
.endmem
    push_64_r rbx
.bbl start 4
    mov_32_r_imm32 ebx 0x0
.bbl loop 4
    mov_32_r_mr ecx ebx
    lea_64_r_mpc32 rax rip expr:loc_pcrel32:switch_tab
    jmp_64_mbis8 rax rcx 3 0
.bbl labelA 4
    mov_8_r_imm8 dil 0x41
    call_32 expr:pcrel32:print_c_ln
    jmp_32 expr:loc_pcrel32:tail
.bbl labelB 4
    mov_8_r_imm8 dil 0x42
    call_32 expr:pcrel32:print_c_ln
    jmp_32 expr:loc_pcrel32:tail
.bbl labelC 4
    mov_8_r_imm8 dil 0x43
    call_32 expr:pcrel32:print_c_ln
    jmp_32 expr:loc_pcrel32:tail
.bbl labelD 4
    mov_8_r_imm8 dil 0x44
    call_32 expr:pcrel32:print_c_ln
.bbl tail 4
    add_32_mr_imm32 ebx 0x1
    cmp_32_mr_imm32 ebx 0x5
    jb_32 expr:loc_pcrel32:loop
.bbl tail_1 4
    mov_32_r_imm32 eax 0x0
    pop_64_r rbx
    ret
.endfun
