# Getting Started

### Setup

For simplicity we assume you are running on an x86-64 system with a recent Debian 
based Linux distributions.

To setup the python environment run this inside the
top level repo directory.
```
# make sure all the packages defined by Cwerg can be imported
export PYTHONPATH=$(pwd)

# confirm python interpreter version, you need at least Python 3.7
python3 -V

# install the c-parser if you want to use the code in FrontEndC/
sudo apt install python3-pycparser
```

To prepare the c++ build (you need at least a C++17 compatible compiler) run his 
inside the top level repo directory. Both Gcc and Clang should work.

```
sudo apt install cmake

mkdir build
cd build
cmake ..
cd ..

# you may need to install the unwind library (used by the ASSERT macro
sudo apt install libunwind-dev

# in order to use the 32bit memory model ("-m32") on x86-64 you need to install

sudo apt install gcc-multilib
```

To set up and an Arm cross-compilation and testing environment please check
[TestQemu/README.md](../TestQemu/README.md)

### Testing

A good way to find yourself around the project is to start with
the top level Makefile. Just running 
```
make
```
will run a battery of self tests and confirm your set up is working properly

We currently use simple recursive Makefiles. The C++ implementation
is built via CMake which works better with IDEs.

The Python implementation contains the authoritative comments.
The C++ implementation re-uses the Python function names as much as possible.
The Python function comments apply to the C++ functions as well in this case.


### Simple Example: Sieve of Eratosthenes

[C Code](../FrontEndC/TestData/sieve.c)
<details>
<summary>Click to expand!</summary>

```
#include "std_lib.h"   // needed because printf may be rewritten to call helpers defined here
  
  
int printf( const char *restrict format, ... );

// computes number of primes between [3 - SIZE]
#define SIZE 1000000

char is_prime[SIZE];

unsigned sieve (unsigned repeats) {
  unsigned num_primes; 

  for (unsigned n = 0; n < repeats; n++) {
    num_primes = 0;
    for (unsigned i = 0; i < SIZE; i++) is_prime[i] = 1;
    for (unsigned i = 0; i < SIZE; i++)
      if (is_prime[i]) {
        unsigned prime = i + i + 3;
        for (unsigned k = i + prime; k < SIZE; k += prime) is_prime[k] = 0;
        num_primes++;
      }
  }
  return num_primes;
}


int main() {
  if (sieve(1U) != 148932) abort();
  return 0;
}
```
</details>

Compile this to 32bit Cwerg IR is accomplished via:
```
FrontEndC/translate.py --mode 32 FrontEndC/TestData/sieve.c --cpp_args=-IStdLib > sieve.asm
```
yielding this (somewhat horrible) code:

<details>
  <summary>Click to expand!</summary>

```
.mem is_prime 1 RW
.data 1000000 [0]


.fun sieve NORMAL [U32] = [U32]
.reg U32 [%out]

.bbl %start
  poparg repeats:U32
  .reg U32 [num_primes]
  .reg U32 [n]
  mov n = 0
  bra for_4_cond

.bbl for_4
  mov num_primes = 0
  .reg U32 [i]
  mov i = 0
  bra for_1_cond

.bbl for_1
  lea %A32_1:A32 = is_prime
  lea %A32_2:A32 = %A32_1 i
  mov %S8_3:S8 = 1
  st %A32_2 0 = %S8_3

.bbl for_1_next
  add %U32_4:U32 = i 1
  mov i = %U32_4

.bbl for_1_cond
  blt i 1000000 for_1
  bra for_1_exit

.bbl for_1_exit
  .reg U32 [__local_10_i]
  mov __local_10_i = 0
  bra for_3_cond

.bbl for_3
  lea %A32_5:A32 = is_prime
  lea %A32_6:A32 = %A32_5 __local_10_i
  ld %S8_7:S8 = %A32_6 0
  conv %S32_8:S32 = %S8_7
  bne %S32_8 0 if_7_true
  bra for_3_next

.bbl if_7_true
  .reg U32 [prime]
  add %U32_9:U32 = __local_10_i __local_10_i
  add %U32_10:U32 = %U32_9 3
  mov prime = %U32_10
  .reg U32 [k]
  add %U32_11:U32 = __local_10_i prime
  mov k = %U32_11
  bra for_2_cond

.bbl for_2
  lea %A32_12:A32 = is_prime
  lea %A32_13:A32 = %A32_12 k
  mov %S8_14:S8 = 0
  st %A32_13 0 = %S8_14

.bbl for_2_next
  add %U32_15:U32 = k prime
  mov k = %U32_15

.bbl for_2_cond
  blt k 1000000 for_2
  bra for_2_exit

.bbl for_2_exit
  add %U32_16:U32 = num_primes 1
  mov num_primes = %U32_16

.bbl for_3_next
  add %U32_17:U32 = __local_10_i 1
  mov __local_10_i = %U32_17

.bbl for_3_cond
  blt __local_10_i 1000000 for_3
  bra for_4_next

.bbl for_4_next
  add %U32_18:U32 = n 1
  mov n = %U32_18

.bbl for_4_cond
  blt n repeats for_4
  bra for_4_exit

.bbl for_4_exit
  mov %out = num_primes
  pusharg %out
  ret


.fun main NORMAL [S32] = []
.reg S32 [%out]

.bbl %start
  mov %U32_2:U32 = 1
  pusharg %U32_2
  bsr sieve
  poparg %U32_1:U32
  bne %U32_1 148932 if_1_true
  bra if_1_end

.bbl if_1_true
  bsr abort

.bbl if_1_end
  mov %out = 0
  pusharg %out
  ret
```
</details>

We translate it to Arm32 assembler using
```
cat StdLib/syscall.a32.asm StdLib/std_lib.32.asm sieve.asm | CodeGenA32/codegen.py normal - sieve.a32.s
```
 yielding (only relevant parts shown):

<details>
  <summary>Click to expand!</summary>

```
.mem is_prime 1 data
    .data 1000000 "\x00"
.endmem

...

.fun sieve 16
    stmdb_update al sp reglist:0x4040
    sub_imm al sp sp 8
.bbl %start 4
    mov_regimm al r6 r0 lsl 0
    mov_imm al ip 0
    b al expr:jump24:for_4_cond
.bbl for_4 4
    mov_imm al lr 0
    mov_imm al r4 0
    b al expr:jump24:for_1_cond
.bbl for_1 4
    movw al r0 expr:movw_abs_nc:is_prime
    movt al r0 expr:movt_abs:is_prime
    mov_imm al r1 1
    strb_reg_add al r0 r4 lsl 0 r1
.bbl for_1_next 4
    add_imm al r0 r4 1
    mov_regimm al r4 r0 lsl 0
.bbl for_1_cond 4
    movw al r0 16960
    movt al r0 15
    cmp_regimm al r4 r0 lsl 0
    b cc expr:jump24:for_1
.bbl for_1_exit 4
    mov_imm al r3 0
    b al expr:jump24:for_3_cond
.bbl for_3 4
    movw al r0 expr:movw_abs_nc:is_prime
    movt al r0 expr:movt_abs:is_prime
    ldrsb_reg_add al r0 r0 r3
    sxtb al r0 r0 0
    mov_regimm al r0 r0 lsl 0
    cmp_imm al r0 0
    b eq expr:jump24:for_3_next
.bbl if_7_true 4
    add_regimm al r0 r3 r3 lsl 0
    add_imm al r2 r0 3
    add_regimm al r0 r3 r2 lsl 0
    mov_regimm al r5 r0 lsl 0
    b al expr:jump24:for_2_cond
.bbl for_2 4
    movw al r0 expr:movw_abs_nc:is_prime
    movt al r0 expr:movt_abs:is_prime
    mov_imm al r1 0
    strb_reg_add al r0 r5 lsl 0 r1
.bbl for_2_next 4
    add_regimm al r0 r5 r2 lsl 0
    mov_regimm al r5 r0 lsl 0
.bbl for_2_cond 4
    movw al r0 16960
    movt al r0 15
    cmp_regimm al r5 r0 lsl 0
    b cc expr:jump24:for_2
.bbl for_2_exit 4
    add_imm al r0 lr 1
    mov_regimm al lr r0 lsl 0
.bbl for_3_next 4
    add_imm al r0 r3 1
    mov_regimm al r3 r0 lsl 0
.bbl for_3_cond 4
    movw al r0 16960
    movt al r0 15
    cmp_regimm al r3 r0 lsl 0
    b cc expr:jump24:for_3
.bbl for_4_next 4
    add_imm al r0 ip 1
    mov_regimm al ip r0 lsl 0
.bbl for_4_cond 4
    cmp_regimm al ip r6 lsl 0
    b cc expr:jump24:for_4
.bbl for_4_exit 4
    mov_regimm al r0 lr lsl 0
    add_imm al sp sp 8
    ldmia_update al reglist:0x8040 sp
.endfun
# sig: IN: [] -> OUT: [S32]  stk_size:0
.fun main 16
    stmdb_update al sp reglist:0x4000
    sub_imm al sp sp 12
.bbl %start 4
    mov_imm al r0 1
    bl al expr:call:sieve
    movw al r1 17860
    movt al r1 2
    cmp_regimm al r0 r1 lsl 0
    b eq expr:jump24:if_1_end
.bbl if_1_true 4
    bl al expr:call:abort
.bbl if_1_end 4
    mov_imm al r0 0
    add_imm al sp sp 12
    ldmia_update al reglist:0x8000 sp
.endfun
```
</details>

We can also generate an executable directly with:

```
cat StdLib/syscall.a32.asm StdLib/std_lib.32.asm sieve.asm | CodeGenA32/codegen.py binary - sieve.a32.exe
```

And, assuming you have installed qemu or run on an Arm system, you can run this executable like so
`./sieve.a32.exe`

Disassembling the executable provides more standard Arm32 instructions via:
```
arm-linux-gnueabihf-objdump -d ./sieve.a32.exe
```
yielding:
<details>
  <summary>Click to expand!</summary>
  
```
  000206f0 <sieve>:
   206f0:	e92d4040 	push	{r6, lr}
   206f4:	e24dd008 	sub	sp, sp, #8

000206f8 <%start>:
   206f8:	e1a06000 	mov	r6, r0
   206fc:	e3a0c000 	mov	ip, #0
   20700:	ea00002e 	b	207c0 <for_4_cond>

00020704 <for_4>:
   20704:	e3a0e000 	mov	lr, #0
   20708:	e3a04000 	mov	r4, #0
   2070c:	ea000005 	b	20728 <for_1_cond>

00020710 <for_1>:
   20710:	e3000838 	movw	r0, #2104	; 0x838
   20714:	e3400003 	movt	r0, #3
   20718:	e3a01001 	mov	r1, #1
   2071c:	e7c01004 	strb	r1, [r0, r4]

00020720 <for_1_next>:
   20720:	e2840001 	add	r0, r4, #1
   20724:	e1a04000 	mov	r4, r0

00020728 <for_1_cond>:
   20728:	e3040240 	movw	r0, #16960	; 0x4240
   2072c:	e340000f 	movt	r0, #15
   20730:	e1540000 	cmp	r4, r0
   20734:	3afffff5 	bcc	20710 <for_1>

00020738 <for_1_exit>:
   20738:	e3a03000 	mov	r3, #0
   2073c:	ea000019 	b	207a8 <for_3_cond>

00020740 <for_3>:
   20740:	e3000838 	movw	r0, #2104	; 0x838
   20744:	e3400003 	movt	r0, #3
   20748:	e19000d3 	ldrsb	r0, [r0, r3]
   2074c:	e6af0070 	sxtb	r0, r0
   20750:	e1a00000 	nop			; (mov r0, r0)
   20754:	e3500000 	cmp	r0, #0
   20758:	0a000010 	beq	207a0 <for_3_next>

0002075c <if_7_true>:
   2075c:	e0830003 	add	r0, r3, r3
   20760:	e2802003 	add	r2, r0, #3
   20764:	e0830002 	add	r0, r3, r2
   20768:	e1a05000 	mov	r5, r0
   2076c:	ea000005 	b	20788 <for_2_cond>

00020770 <for_2>:
   20770:	e3000838 	movw	r0, #2104	; 0x838
   20774:	e3400003 	movt	r0, #3
   20778:	e3a01000 	mov	r1, #0
   2077c:	e7c01005 	strb	r1, [r0, r5]

00020780 <for_2_next>:
   20780:	e0850002 	add	r0, r5, r2
   20784:	e1a05000 	mov	r5, r0

00020788 <for_2_cond>:
   20788:	e3040240 	movw	r0, #16960	; 0x4240
   2078c:	e340000f 	movt	r0, #15
   20790:	e1550000 	cmp	r5, r0
   20794:	3afffff5 	bcc	20770 <for_2>

00020798 <for_2_exit>:
   20798:	e28e0001 	add	r0, lr, #1
   2079c:	e1a0e000 	mov	lr, r0

000207a0 <for_3_next>:
   207a0:	e2830001 	add	r0, r3, #1
   207a4:	e1a03000 	mov	r3, r0

000207a8 <for_3_cond>:
   207a8:	e3040240 	movw	r0, #16960	; 0x4240
   207ac:	e340000f 	movt	r0, #15
   207b0:	e1530000 	cmp	r3, r0
   207b4:	3affffe1 	bcc	20740 <for_3>

000207b8 <for_4_next>:
   207b8:	e28c0001 	add	r0, ip, #1
   207bc:	e1a0c000 	mov	ip, r0

000207c0 <for_4_cond>:
   207c0:	e15c0006 	cmp	ip, r6
   207c4:	3affffce 	bcc	20704 <for_4>

000207c8 <for_4_exit>:
   207c8:	e1a0000e 	mov	r0, lr
   207cc:	e28dd008 	add	sp, sp, #8
   207d0:	e8bd8040 	pop	{r6, pc}
   207d4:	e320f000 	nop	{0}
   207d8:	e320f000 	nop	{0}
   207dc:	e320f000 	nop	{0}

000207e0 <main>:
   207e0:	e92d4000 	stmfd	sp!, {lr}
   207e4:	e24dd00c 	sub	sp, sp, #12

000207e8 <%start>:
   207e8:	e3a00001 	mov	r0, #1
   207ec:	ebffffbf 	bl	206f0 <sieve>
   207f0:	e30415c4 	movw	r1, #17860	; 0x45c4
   207f4:	e3401002 	movt	r1, #2
   207f8:	e1500001 	cmp	r0, r1
   207fc:	0a000000 	beq	20804 <if_1_end>

00020800 <if_1_true>:
   20800:	ebffff6a 	bl	205b0 <abort>

00020804 <if_1_end>:
   20804:	e3a00000 	mov	r0, #0
   20808:	e28dd00c 	add	sp, sp, #12
   2080c:	e8bd8000 	ldmfd	sp!, {pc}

00020810 <_start>:
   20810:	e59d0000 	ldr	r0, [sp]
   20814:	e28d1004 	add	r1, sp, #4
   20818:	ebfffff0 	bl	207e0 <main>
   2081c:	e3007001 	movw	r7, #1
   20820:	ef000000 	svc	0x00000000
   20824:	e7f000f0 	udf	#0
```
</details>
### Directory Organization

The directory organization reflects the architecture of the Cwerg:

#### [Base/](../Base) 

contains the [IR](opcodes.md) definitions, (de-)serialization code, 
transformation and optimization passes.

Implementations: Python, C++ 
 
#### [CodeGenA32/](../CodeGenA32)

contains the Arm 32-bit backends which converts the IR to Arm32 machine Code.

Implementations: Python, C++ 

#### [CodeGenA64/](../CodeGenA64)

contains the Arm 64-bit backends which converts the IR to Arm64 machine Code.

Implementations: Python, C++ 

#### [CodeGenC/](../CodeGenC)
 
contains the C backend which converts the IR to equivalent C code
 
Implementations: Python
 
#### [CpuA32/](../CpuA32)

contains the (dis-)assemblers for the Arm 32-bit ISA. They are based
on a tabular description of the ISA which is also used by 
and may be useful for other projects as well.

Implementations: Python, C++ 

#### [CpuA64/](../CpuA64)

contains the (dis-)assemblers for the Arm 64-bit ISA. They are based
on a tabular description of the ISA which is also used by 
and may be useful for other projects as well.

Implementations: Python, C++ 

#### [Elf/](../Elf)

contains the (dis-)assemblers for the Elf object code format.
Currently, only basic features necessary to deal with static executables
are supported but it is more or less "standalone" and may be useful for
 other projects as well
 
Implementations: Python, C++ 

#### [Elf/](../Elf)

Examples illustrating the use of Cwerg.

#### [FrontEndC/](../FrontEndC)
 
contains a C frontend that translates a subset of the C language to the IR.
 
Implementations: Python
 

#### [TestQemu/](../TestQemu)

tests the cross development environment setup. 

#### [Tools/](../Tools)

misc tools

Implementations: Python

#### [Util](../Util)

contains basic helpers for parsing and elementary datastructures

Implementations: Python, C++

## Vaporware

#### [CpuX64/](../CpuX64)

future home of the  (dis-)assemblers for X86-64 ISA


#### [FrontEndLLVM/](../FrontEndLLVM)

future home of a LLVM to IR translator.


#### [FrontEndWASM/](../FrontEndWASM)

future home of a WASM to IR translator.

