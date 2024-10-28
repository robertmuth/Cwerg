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
# sig: IN: [S32 U32] -> OUT: [S64]  stk_size:16
.fun write_u 16
    sub_64_mr_imm32 rsp 0x18
.bbl %start 4
    mov_32_r_mr r8d edi
    mov_32_r_mr r10d esi
    mov_64_r_imm64 r9 0x10
.bbl while_1 4
    sub_64_mr_imm32 r9 0x1
    mov_32_r_imm32 ecx 0xa
    mov_32_r_mr eax r10d
    xor_32_r_mr edx edx
    div_32_edx_eax_mr edx eax ecx
    mov_32_r_mr ecx edx
    add_32_mr_imm32 ecx 0x30
    lea_64_r_mbis32 rdx rsp noindex 0 0
    mov_8_mbis8_r rdx r9 0 0 cl
    mov_32_r_imm32 ecx 0xa
    mov_32_r_mr eax r10d
    xor_32_r_mr edx edx
    div_32_edx_eax_mr edx eax ecx
    mov_32_r_mr r10d eax
.bbl while_1_cond 4
    cmp_32_mr_imm32 r10d 0x0
    jne_32 expr:loc_pcrel32:while_1
.bbl while_1_exit 4
    lea_64_r_mbis32 rcx rsp noindex 0 0
    lea_64_r_mbis8 rcx rcx r9 0 0
    mov_64_r_imm64 rdx 0x10
    sub_64_r_mr rdx r9
    mov_64_r_mr rsi rcx
    mov_32_r_mr edi r8d
    call_32 expr:pcrel32:write
    mov_64_r_mr rcx rax
    mov_64_r_mr rax rcx
    add_64_mr_imm32 rsp 0x18
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
# sig: IN: [U32] -> OUT: []  stk_size:0
.fun print_u_ln 16
    sub_64_mr_imm32 rsp 0x8
.bbl %start 4
    mov_32_r_mr ecx edi
    mov_32_r_mr esi ecx
    mov_32_r_imm32 edi 0x1
    call_32 expr:pcrel32:write_u
    mov_64_r_mr rcx rax
    mov_8_r_imm8 sil 0xa
    mov_32_r_imm32 edi 0x1
    call_32 expr:pcrel32:write_c
    mov_64_r_mr rcx rax
    add_64_mr_imm32 rsp 0x8
    ret
.endfun
# sig: IN: [U32] -> OUT: [U32]  stk_size:0
.fun fibonacci 16
    push_64_r rbp
    push_64_r rbx
    sub_64_mr_imm32 rsp 0x8
.bbl start 4
    mov_32_r_mr ebx edi
    cmp_32_mr_imm32 ebx 0x1
    ja_32 expr:loc_pcrel32:difficult
.bbl start_1 4
    mov_32_r_mr eax ebx
    add_64_mr_imm32 rsp 0x8
    pop_64_r rbx
    pop_64_r rbp
    ret
.bbl difficult 4
    mov_32_r_mr ecx ebx
    sub_32_mr_imm32 ecx 0x1
    mov_32_r_mr edi ecx
    call_32 expr:pcrel32:fibonacci
    mov_32_r_mr ecx eax
    mov_32_r_mr ebp ecx
    mov_32_r_mr ecx ebx
    sub_32_mr_imm32 ecx 0x2
    mov_32_r_mr edi ecx
    call_32 expr:pcrel32:fibonacci
    mov_32_r_mr ecx eax
    mov_32_r_mr edx ebp
    add_32_r_mr edx ecx
    mov_32_r_mr ecx edx
    mov_32_r_mr eax ecx
    add_64_mr_imm32 rsp 0x8
    pop_64_r rbx
    pop_64_r rbp
    ret
.endfun
# sig: IN: [] -> OUT: [S32]  stk_size:0
.fun main 16
    sub_64_mr_imm32 rsp 0x8
.bbl start 4
    mov_32_r_imm32 edi 0x7
    call_32 expr:pcrel32:fibonacci
    mov_32_r_mr ecx eax
    mov_32_r_mr edi ecx
    call_32 expr:pcrel32:print_u_ln
    mov_32_r_imm32 eax 0x0
    add_64_mr_imm32 rsp 0x8
    ret
.endfun
