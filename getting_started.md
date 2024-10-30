# Getting Started


### Setup

For simplicity we assume you are running on an x86-64 system with a **recent** Debian
based Linux distributions.


First you need to install (cross) tool chains and emulators.

Cwerg requires C++17 compatible compilers and Python 3.10 or higher.
```
sudo apt install cmake
sudo apt install gcc g++
sudo apt install gcc-multilib
sudo apt-get install libunwind-dev gcc-multilib
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
sudo apt install qemu-user-static
```

Run the following command to see if everything is setup properly:
```
make test_setup
```

If the steps do not work, the instructions may be out of date.
Check how the continous integration sets up its enviroment in
[.github/workflows/ci.yml](.github/workflows/ci.yml).


### Orientation

To test everything run
```
make tests
```
This will take several minutes.

The [Makefile](Makefile) target `tests` primarily invokes other nested
Makefiles and is good starting point for exploring the project.

If you want to invoke nested Makefiles directly, always set:
```
export PYTHONPATH=$(pwd)
```
The toplevel Makefile will do this implicitly but the nested Makefiles
do not.

The component that have been ported to C++ use `CMake`
which works better with IDEs. All the build-artifacts are kept
in the toplevel `build/` directory.

The source code is organized into the following directories:
* [BE/](BE/) - the backend Code (Python + C++)
* [FE/](FE/) - the frontend Code (Python only)
* [Util/](Util/) - code shared by frontend and backend (Python + C++)
* [FE_WASM/](FE_WASM/) - a deprecated alternative frontend
  which translates WASM/WASI code to Cwerg IR (Python only)
* [TestQemu/](TestQemu/) - cross compilation and emulation tests


The Python implementation contains the authoritative comments.
The C++ implementation re-uses the Python function names as much as possible.
The Python function comments apply to the C++ functions as well in this case.


### Simple Example: Sieve of Eratosthenes

[Cwerg Code](FE/LangTest/sieve_test.cw)

<details>
<summary>Cwerg code for sieve - click to expand:</summary>

```
-- prime number sieve
  module:

  import test

  global SIZE uint = 1000000

  global EXPECTED uint = 148932

  -- The array is initialized to all true because the explicit
  -- value for the first element is replicated for the
  -- subsequent unspecified ones.
  --
  -- index i reprents number 3 + 2 * i
  global! is_prime = [SIZE]bool{true}

  -- the actual sieve function
  fun sieve() uint:
      -- mutable local variable
      let! count uint = 0
      -- the type of loop variable `i`  is determined by `N`
      for i = 0, SIZE, 1:
          if is_prime[i]:
              set count += 1
              let p uint = i + i + 3
              for k = i + p, SIZE, p:
                  set is_prime[k] = false
      return count

  fun main(argc s32, argv ^^u8) s32:
      test::AssertEq#(sieve(), EXPECTED)
      test::Success#()
      return 0

```
</details>

Compiling this to 32bit Cwerg IR is accomplished via:
```
FE/emit_ir.py -shake_tree -stdlib FE/Lib -arch a32 FE/LangTest/sieve_test.cw > sieve.ir
```

<details>
  <summary>yielding this IR code - click to expand:</summary>

```
.fun $sig/S32_S32_A32_U32 SIGNATURE [S32] = [S32 A32 U32]


.fun $sig/U32_void SIGNATURE [U32] = []


.fun $sig/S32_S32_A32 SIGNATURE [S32] = [S32 A32]

.mem $generated/global_val%0 1 RO
# array: array<u8,17>
.data 1 "AssertEq failed: "  # 0 array<u8,17>

.mem $generated/global_val%1 1 RO
# array: array<u8,17>
.data 1 "[call] [id] sieve"  # 0 array<u8,17>

.mem $generated/global_val%2 1 RO
# array: array<u8,4>
.data 1 " VS "  # 0 array<u8,4>

.mem $generated/global_val%3 1 RO
# array: array<u8,13>
.data 1 "[id] EXPECTED"  # 0 array<u8,13>

.mem $generated/global_val%4 1 RO
# array: array<u8,1>
.data 1 [10]  # 0 array<u8,1>

.mem $generated/global_val%5 1 RO
# array: array<u8,3>
.data 1 "OK\n"  # 0 array<u8,3>

.mem os/Stdin 4 RO
.data 4 [0]  # 0 s32

.mem os/Stdout 4 RO
.data 1 "\x01\x00\x00\x00"  # 0 s32

.mem os/Stderr 4 RO
.data 1 "\x02\x00\x00\x00"  # 0 s32

.mem sieve_test/SIZE 4 RO
.data 1 "@B\x0f\x00"  # 0 u32

.mem sieve_test/EXPECTED 4 RO
.data 1 "\xc4E\x02\x00"  # 0 u32

.mem sieve_test/is_prime 1 RW
# array: array<bool,1000000>
.data 1000000 [1]  # array<bool,1000000>


.fun sieve_test/sieve NORMAL [U32] = []
.bbl entry
  mov count:U32 = 0:U32
  mov end_eval$5:U32 = 1000000:U32
  mov step_eval$6:U32 = 1:U32
  mov it$7:U32 = 0:U32
.bbl _  # block start
  blt it$7 1000000:U32 br_join.1  # GE([id] it$7, [ValNum] 1000000)
  bra _.1  # break
.bbl br_join.1
  bra br_join
.bbl br_f
  blt 1000000:U32 it$7 br_join.2  # LE([id] it$7, [ValNum] 1000000)
  bra _.1  # break
.bbl br_join.2
.bbl br_join
  mov i:U32 = it$7
  add expr2:U32 = it$7 1:U32
  mov it$7 = expr2  # [=] [id] it$7 = ADD([id] it$7, [ValNum] 1)
  lea.mem lhsaddr_sieve_test/is_prime:A32 = sieve_test/is_prime 0
  lea expr2.1:A32 = lhsaddr_sieve_test/is_prime i
  ld deref:U8 = expr2.1 0
  beq deref 0 br_join.3
  add expr2.2:U32 = count 1:U32
  mov count = expr2.2  # [=] [id] count = ADD([id] count, [ValNum] 1)
  add expr2.3:U32 = i i
  add expr2.4:U32 = expr2.3 3:U32
  mov p:U32 = expr2.4
  mov end_eval$2:U32 = 1000000:U32
  mov step_eval$3:U32 = p
  add expr2.5:U32 = i p
  mov it$4:U32 = expr2.5
.bbl _.2  # block start
  blt step_eval$3 0:U32 br_f.4  # GE([id] step_eval$3, [ValNum] 0)
  blt it$4 1000000:U32 br_join.5  # GE([id] it$4, [ValNum] 1000000)
  bra _.3  # break
.bbl br_join.5
  bra br_join.4
.bbl br_f.4
  blt 1000000:U32 it$4 br_join.6  # LE([id] it$4, [ValNum] 1000000)
  bra _.3  # break
.bbl br_join.6
.bbl br_join.4
  mov k:U32 = it$4
  add expr2.6:U32 = it$4 step_eval$3
  mov it$4 = expr2.6  # [=] [id] it$4 = ADD([id] it$4, [id] step_eval$3)
  lea.mem lhsaddr_sieve_test/is_prime.1:A32 = sieve_test/is_prime 0
  lea expr2.7:A32 = lhsaddr_sieve_test/is_prime.1 k
  st expr2.7 0 = 0:U8
  bra _.2  # continue
.bbl _.3  # block end
.bbl br_join.3
  bra _  # continue
.bbl _.1  # block end
  pusharg count
  ret


.fun main NORMAL [S32] = [S32 A32]
.bbl entry
  poparg argc:S32
  poparg argv:A32
  bsr sieve_test/sieve
  poparg call:U32
  mov e_val$2:U32 = call
  mov a_val$3:U32 = 148932:U32
  beq e_val$2 148932:U32 br_join  # NE([id] e_val$2, [ValNum] 148932)
  .stk msg_eval$4 4 8
  lea.stk init_base:A32 msg_eval$4 0
  lea.mem lhsaddr_$generated/global_val%0:A32 = $generated/global_val%0 0
  st init_base 0 = lhsaddr_$generated/global_val%0
  st init_base 4 = 17:U32
  lea.stk lhsaddr_msg_eval$4:A32 = msg_eval$4 0
  ld field_pointer:A32 = lhsaddr_msg_eval$4 0
  pusharg 17:U32
  pusharg field_pointer
  pusharg 1:S32
  bsr write
  poparg call.1:S32
  .stk msg_eval$5 4 8
  lea.stk init_base.1:A32 msg_eval$5 0
  lea.mem lhsaddr_$generated/global_val%1:A32 = $generated/global_val%1 0
  st init_base.1 0 = lhsaddr_$generated/global_val%1
  st init_base.1 4 = 17:U32
  lea.stk lhsaddr_msg_eval$5:A32 = msg_eval$5 0
  ld field_pointer.1:A32 = lhsaddr_msg_eval$5 0
  pusharg 17:U32
  pusharg field_pointer.1
  pusharg 1:S32
  bsr write
  poparg call.2:S32
  .stk msg_eval$6 4 8
  lea.stk init_base.2:A32 msg_eval$6 0
  lea.mem lhsaddr_$generated/global_val%2:A32 = $generated/global_val%2 0
  st init_base.2 0 = lhsaddr_$generated/global_val%2
  st init_base.2 4 = 4:U32
  lea.stk lhsaddr_msg_eval$6:A32 = msg_eval$6 0
  ld field_pointer.2:A32 = lhsaddr_msg_eval$6 0
  pusharg 4:U32
  pusharg field_pointer.2
  pusharg 1:S32
  bsr write
  poparg call.3:S32
  .stk msg_eval$7 4 8
  lea.stk init_base.3:A32 msg_eval$7 0
  lea.mem lhsaddr_$generated/global_val%3:A32 = $generated/global_val%3 0
  st init_base.3 0 = lhsaddr_$generated/global_val%3
  st init_base.3 4 = 13:U32
  lea.stk lhsaddr_msg_eval$7:A32 = msg_eval$7 0
  ld field_pointer.3:A32 = lhsaddr_msg_eval$7 0
  pusharg 13:U32
  pusharg field_pointer.3
  pusharg 1:S32
  bsr write
  poparg call.4:S32
  .stk msg_eval$8 4 8
  lea.stk init_base.4:A32 msg_eval$8 0
  lea.mem lhsaddr_$generated/global_val%4:A32 = $generated/global_val%4 0
  st init_base.4 0 = lhsaddr_$generated/global_val%4
  st init_base.4 4 = 1:U32
  lea.stk lhsaddr_msg_eval$8:A32 = msg_eval$8 0
  ld field_pointer.4:A32 = lhsaddr_msg_eval$8 0
  pusharg 1:U32
  pusharg field_pointer.4
  pusharg 1:S32
  bsr write
  poparg call.5:S32
  trap
.bbl br_join
  .stk msg_eval$9 4 8
  lea.stk init_base.5:A32 msg_eval$9 0
  lea.mem lhsaddr_$generated/global_val%5:A32 = $generated/global_val%5 0
  st init_base.5 0 = lhsaddr_$generated/global_val%5
  st init_base.5 4 = 3:U32
  lea.stk lhsaddr_msg_eval$9:A32 = msg_eval$9 0
  ld field_pointer.5:A32 = lhsaddr_msg_eval$9 0
  pusharg 3:U32
  pusharg field_pointer.5
  pusharg 1:S32
  bsr write
  poparg call.6:S32
  pusharg 0:S32
  ret
```
</details>

Translating it to Arm32 assembler is accomplished via:
```
cat BE/StdLib/syscall.a32.asm BE/StdLib/syscall.a32.asm BE/StdLib/std_lib.32.asm sieve.ir | BE/CodeGenA32/codegen.py -mode normal - sieve.a32.s
```
<details>
  <summary>yielding this (Cwerg flavored) assembly code - click to expand:</summary>

```
.fun $sig/S32_S32_A32_U32 SIGNATURE [S32] = [S32 A32 U32]


.fun $sig/U32_void SIGNATURE [U32] = []


.fun $sig/S32_S32_A32 SIGNATURE [S32] = [S32 A32]

.mem $generated/global_val%0 1 RO
# array: array<u8,17>
.data 1 "AssertEq failed: "  # 0 array<u8,17>

.mem $generated/global_val%1 1 RO
# array: array<u8,17>
.data 1 "[call] [id] sieve"  # 0 array<u8,17>

.mem $generated/global_val%2 1 RO
# array: array<u8,4>
.data 1 " VS "  # 0 array<u8,4>

.mem $generated/global_val%3 1 RO
# array: array<u8,13>
.data 1 "[id] EXPECTED"  # 0 array<u8,13>

.mem $generated/global_val%4 1 RO
# array: array<u8,1>
.data 1 [10]  # 0 array<u8,1>

.mem $generated/global_val%5 1 RO
# array: array<u8,3>
.data 1 "OK\n"  # 0 array<u8,3>

.mem os/Stdin 4 RO
.data 4 [0]  # 0 s32

.mem os/Stdout 4 RO
.data 1 "\x01\x00\x00\x00"  # 0 s32

.mem os/Stderr 4 RO
.data 1 "\x02\x00\x00\x00"  # 0 s32

.mem sieve_test/SIZE 4 RO
.data 1 "@B\x0f\x00"  # 0 u32

.mem sieve_test/EXPECTED 4 RO
.data 1 "\xc4E\x02\x00"  # 0 u32

.mem sieve_test/is_prime 1 RW
# array: array<bool,1000000>
.data 1000000 [1]  # array<bool,1000000>


.fun sieve_test/sieve NORMAL [U32] = []
.bbl entry
  mov count:U32 = 0:U32
  mov end_eval$5:U32 = 1000000:U32
  mov step_eval$6:U32 = 1:U32
  mov it$7:U32 = 0:U32
.bbl _  # block start
  blt it$7 1000000:U32 br_join.1  # GE([id] it$7, [ValNum] 1000000)
  bra _.1  # break
.bbl br_join.1
  bra br_join
.bbl br_f
  blt 1000000:U32 it$7 br_join.2  # LE([id] it$7, [ValNum] 1000000)
  bra _.1  # break
.bbl br_join.2
.bbl br_join
  mov i:U32 = it$7
  add expr2:U32 = it$7 1:U32
  mov it$7 = expr2  # [=] [id] it$7 = ADD([id] it$7, [ValNum] 1)
  lea.mem lhsaddr_sieve_test/is_prime:A32 = sieve_test/is_prime 0
  lea expr2.1:A32 = lhsaddr_sieve_test/is_prime i
  ld deref:U8 = expr2.1 0
  beq deref 0 br_join.3
  add expr2.2:U32 = count 1:U32
  mov count = expr2.2  # [=] [id] count = ADD([id] count, [ValNum] 1)
  add expr2.3:U32 = i i
  add expr2.4:U32 = expr2.3 3:U32
  mov p:U32 = expr2.4
  mov end_eval$2:U32 = 1000000:U32
  mov step_eval$3:U32 = p
  add expr2.5:U32 = i p
  mov it$4:U32 = expr2.5
.bbl _.2  # block start
  blt step_eval$3 0:U32 br_f.4  # GE([id] step_eval$3, [ValNum] 0)
  blt it$4 1000000:U32 br_join.5  # GE([id] it$4, [ValNum] 1000000)
  bra _.3  # break
.bbl br_join.5
  bra br_join.4
.bbl br_f.4
  blt 1000000:U32 it$4 br_join.6  # LE([id] it$4, [ValNum] 1000000)
  bra _.3  # break
.bbl br_join.6
.bbl br_join.4
  mov k:U32 = it$4
  add expr2.6:U32 = it$4 step_eval$3
  mov it$4 = expr2.6  # [=] [id] it$4 = ADD([id] it$4, [id] step_eval$3)
  lea.mem lhsaddr_sieve_test/is_prime.1:A32 = sieve_test/is_prime 0
  lea expr2.7:A32 = lhsaddr_sieve_test/is_prime.1 k
  st expr2.7 0 = 0:U8
  bra _.2  # continue
.bbl _.3  # block end
.bbl br_join.3
  bra _  # continue
.bbl _.1  # block end
  pusharg count
  ret


.fun main NORMAL [S32] = [S32 A32]
.bbl entry
  poparg argc:S32
  poparg argv:A32
  bsr sieve_test/sieve
  poparg call:U32
  mov e_val$2:U32 = call
  mov a_val$3:U32 = 148932:U32
  beq e_val$2 148932:U32 br_join  # NE([id] e_val$2, [ValNum] 148932)
  .stk msg_eval$4 4 8
  lea.stk init_base:A32 msg_eval$4 0
  lea.mem lhsaddr_$generated/global_val%0:A32 = $generated/global_val%0 0
  st init_base 0 = lhsaddr_$generated/global_val%0
  st init_base 4 = 17:U32
  lea.stk lhsaddr_msg_eval$4:A32 = msg_eval$4 0
  ld field_pointer:A32 = lhsaddr_msg_eval$4 0
  pusharg 17:U32
  pusharg field_pointer
  pusharg 1:S32
  bsr write
  poparg call.1:S32
  .stk msg_eval$5 4 8
  lea.stk init_base.1:A32 msg_eval$5 0
  lea.mem lhsaddr_$generated/global_val%1:A32 = $generated/global_val%1 0
  st init_base.1 0 = lhsaddr_$generated/global_val%1
  st init_base.1 4 = 17:U32
  lea.stk lhsaddr_msg_eval$5:A32 = msg_eval$5 0
  ld field_pointer.1:A32 = lhsaddr_msg_eval$5 0
  pusharg 17:U32
  pusharg field_pointer.1
  pusharg 1:S32
  bsr write
  poparg call.2:S32
  .stk msg_eval$6 4 8
  lea.stk init_base.2:A32 msg_eval$6 0
  lea.mem lhsaddr_$generated/global_val%2:A32 = $generated/global_val%2 0
  st init_base.2 0 = lhsaddr_$generated/global_val%2
  st init_base.2 4 = 4:U32
  lea.stk lhsaddr_msg_eval$6:A32 = msg_eval$6 0
  ld field_pointer.2:A32 = lhsaddr_msg_eval$6 0
  pusharg 4:U32
  pusharg field_pointer.2
  pusharg 1:S32
  bsr write
  poparg call.3:S32
  .stk msg_eval$7 4 8
  lea.stk init_base.3:A32 msg_eval$7 0
  lea.mem lhsaddr_$generated/global_val%3:A32 = $generated/global_val%3 0
  st init_base.3 0 = lhsaddr_$generated/global_val%3
  st init_base.3 4 = 13:U32
  lea.stk lhsaddr_msg_eval$7:A32 = msg_eval$7 0
  ld field_pointer.3:A32 = lhsaddr_msg_eval$7 0
  pusharg 13:U32
  pusharg field_pointer.3
  pusharg 1:S32
  bsr write
  poparg call.4:S32
  .stk msg_eval$8 4 8
  lea.stk init_base.4:A32 msg_eval$8 0
  lea.mem lhsaddr_$generated/global_val%4:A32 = $generated/global_val%4 0
  st init_base.4 0 = lhsaddr_$generated/global_val%4
  st init_base.4 4 = 1:U32
  lea.stk lhsaddr_msg_eval$8:A32 = msg_eval$8 0
  ld field_pointer.4:A32 = lhsaddr_msg_eval$8 0
  pusharg 1:U32
  pusharg field_pointer.4
  pusharg 1:S32
  bsr write
  poparg call.5:S32
  trap
.bbl br_join
  .stk msg_eval$9 4 8
  lea.stk init_base.5:A32 msg_eval$9 0
  lea.mem lhsaddr_$generated/global_val%5:A32 = $generated/global_val%5 0
  st init_base.5 0 = lhsaddr_$generated/global_val%5
  st init_base.5 4 = 3:U32
  lea.stk lhsaddr_msg_eval$9:A32 = msg_eval$9 0
  ld field_pointer.5:A32 = lhsaddr_msg_eval$9 0
  pusharg 3:U32
  pusharg field_pointer.5
  pusharg 1:S32
  bsr write
  poparg call.6:S32
  pusharg 0:S32
  ret

```
</details>

We can also generate an executable directly with:

```
cat BE/StdLib/startup.a32.asm BE/StdLib/syscall.a32.asm BE/StdLib/std_lib.32.asm sieve.ir | BE/CodeGenA32/codegen.py -mode binary - sieve.a32.exe
```

And, assuming you have installed qemu or run on an Arm system, you can run this executable like so
`./sieve.a32.exe`

Disassembling the executable provides more standard Arm32 assembler via:
```
arm-linux-gnueabihf-objdump -d ./sieve.a32.exe
```
<details>
  <summary>yielding this listing - click to expand:</summary>

```
sieve.a32.exe:     file format elf32-littlearm


Disassembly of section .text:

000200a0 <_start>:
   200a0:	e92d4000 	stmfd	sp!, {lr}
   200a4:	e24dd00c 	sub	sp, sp, #12

000200a8 <entry>:
   200a8:	e3000010 	movw	r0, #16
   200ac:	e08d0000 	add	r0, sp, r0
   200b0:	e5902000 	ldr	r2, [r0]
   200b4:	e2800004 	add	r0, r0, #4
   200b8:	e1a01000 	mov	r1, r0
   200bc:	e1a00002 	mov	r0, r2
   200c0:	eb00003e 	bl	201c0 <main>
   200c4:	eb000001 	bl	200d0 <a32_syscall_exit>
   200c8:	e28dd00c 	add	sp, sp, #12
   200cc:	e8bd8000 	ldmfd	sp!, {pc}

000200d0 <a32_syscall_exit>:
   200d0:	e52d7004 	push	{r7}		@ (str r7, [sp, #-4]!)
   200d4:	e52d7004 	push	{r7}		@ (str r7, [sp, #-4]!)
   200d8:	e3007001 	movw	r7, #1
   200dc:	ef000000 	svc	0x00000000
   200e0:	e49d7004 	pop	{r7}		@ (ldr r7, [sp], #4)
   200e4:	e49d7004 	pop	{r7}		@ (ldr r7, [sp], #4)
   200e8:	e7f000f0 	udf	#0
   200ec:	e320f000 	nop	{0}

000200f0 <write>:
   200f0:	e52d7004 	push	{r7}		@ (str r7, [sp, #-4]!)
   200f4:	e52d7004 	push	{r7}		@ (str r7, [sp, #-4]!)
   200f8:	e3007004 	movw	r7, #4
   200fc:	ef000000 	svc	0x00000000
   20100:	e49d7004 	pop	{r7}		@ (ldr r7, [sp], #4)
   20104:	e49d7004 	pop	{r7}		@ (ldr r7, [sp], #4)
   20108:	e12fff1e 	bx	lr
   2010c:	e320f000 	nop	{0}

00020110 <sieve_test/sieve>:
   20110:	e92d4000 	stmfd	sp!, {lr}
   20114:	e24dd00c 	sub	sp, sp, #12

00020118 <entry>:
   20118:	e3a03000 	mov	r3, #0
   2011c:	e3a0c000 	mov	ip, #0

00020120 <_>:
   20120:	e3040240 	movw	r0, #16960	@ 0x4240
   20124:	e340000f 	movt	r0, #15
   20128:	e150000c 	cmp	r0, ip
   2012c:	9a00001f 	bls	201b0 <_.1>

00020130 <br_join>:
   20130:	e1a0400c 	mov	r4, ip
   20134:	e28cc001 	add	ip, ip, #1
   20138:	e3000348 	movw	r0, #840	@ 0x348
   2013c:	e3400004 	movt	r0, #4
   20140:	e7d00004 	ldrb	r0, [r0, r4]
   20144:	e6ef0070 	uxtb	r0, r0
   20148:	e1a00000 	nop			@ (mov r0, r0)
   2014c:	e6ef0070 	uxtb	r0, r0
   20150:	e3500000 	cmp	r0, #0
   20154:	0afffff1 	beq	20120 <_>

00020158 <br_join_1>:
   20158:	e2833001 	add	r3, r3, #1
   2015c:	e0840004 	add	r0, r4, r4
   20160:	e280e003 	add	lr, r0, #3
   20164:	e084500e 	add	r5, r4, lr

00020168 <_.2>:
   20168:	e35e0000 	cmp	lr, #0
   2016c:	3a000004 	bcc	20184 <br_f.4>

00020170 <_.2_1>:
   20170:	e3040240 	movw	r0, #16960	@ 0x4240
   20174:	e340000f 	movt	r0, #15
   20178:	e1550000 	cmp	r5, r0
   2017c:	3a000004 	bcc	20194 <br_join.4>

00020180 <_.2_1bra1>:
   20180:	eaffffe6 	b	20120 <_>

00020184 <br_f.4>:
   20184:	e3040240 	movw	r0, #16960	@ 0x4240
   20188:	e340000f 	movt	r0, #15
   2018c:	e1550000 	cmp	r5, r0
   20190:	9affffe2 	bls	20120 <_>

00020194 <br_join.4>:
   20194:	e1a00005 	mov	r0, r5
   20198:	e085500e 	add	r5, r5, lr
   2019c:	e3001348 	movw	r1, #840	@ 0x348
   201a0:	e3401004 	movt	r1, #4
   201a4:	e3a02000 	mov	r2, #0
   201a8:	e7c12000 	strb	r2, [r1, r0]
   201ac:	eaffffed 	b	20168 <_.2>

000201b0 <_.1>:
   201b0:	e1a00003 	mov	r0, r3
   201b4:	e28dd00c 	add	sp, sp, #12
   201b8:	e8bd8000 	ldmfd	sp!, {pc}
   201bc:	e320f000 	nop	{0}

000201c0 <main>:
   201c0:	e92d4000 	stmfd	sp!, {lr}
   201c4:	e24dd03c 	sub	sp, sp, #60	@ 0x3c

000201c8 <entry>:
   201c8:	e1a02000 	mov	r2, r0
   201cc:	ebffffcf 	bl	20110 <sieve_test/sieve>
   201d0:	e30415c4 	movw	r1, #17860	@ 0x45c4
   201d4:	e3401002 	movt	r1, #2
   201d8:	e1500001 	cmp	r0, r1
   201dc:	0a000036 	beq	202bc <br_join>

000201e0 <entry_1>:
   201e0:	e30002f4 	movw	r0, #756	@ 0x2f4
   201e4:	e3400003 	movt	r0, #3
   201e8:	e58d0000 	str	r0, [sp]
   201ec:	e3a00011 	mov	r0, #17
   201f0:	e58d0004 	str	r0, [sp, #4]
   201f4:	e59d0000 	ldr	r0, [sp]
   201f8:	e3a02011 	mov	r2, #17
   201fc:	e1a01000 	mov	r1, r0
   20200:	e3a00001 	mov	r0, #1
   20204:	ebffffb9 	bl	200f0 <write>
   20208:	e1a03000 	mov	r3, r0
   2020c:	e3000305 	movw	r0, #773	@ 0x305
   20210:	e3400003 	movt	r0, #3
   20214:	e58d0008 	str	r0, [sp, #8]
   20218:	e3a00011 	mov	r0, #17
   2021c:	e58d000c 	str	r0, [sp, #12]
   20220:	e59d0008 	ldr	r0, [sp, #8]
   20224:	e3a02011 	mov	r2, #17
   20228:	e1a01000 	mov	r1, r0
   2022c:	e3a00001 	mov	r0, #1
   20230:	ebffffae 	bl	200f0 <write>
   20234:	e1a03000 	mov	r3, r0
   20238:	e3000316 	movw	r0, #790	@ 0x316
   2023c:	e3400003 	movt	r0, #3
   20240:	e58d0010 	str	r0, [sp, #16]
   20244:	e3a00004 	mov	r0, #4
   20248:	e58d0014 	str	r0, [sp, #20]
   2024c:	e59d0010 	ldr	r0, [sp, #16]
   20250:	e3a02004 	mov	r2, #4
   20254:	e1a01000 	mov	r1, r0
   20258:	e3a00001 	mov	r0, #1
   2025c:	ebffffa3 	bl	200f0 <write>
   20260:	e1a03000 	mov	r3, r0
   20264:	e300031a 	movw	r0, #794	@ 0x31a
   20268:	e3400003 	movt	r0, #3
   2026c:	e58d0018 	str	r0, [sp, #24]
   20270:	e3a0000d 	mov	r0, #13
   20274:	e58d001c 	str	r0, [sp, #28]
   20278:	e59d0018 	ldr	r0, [sp, #24]
   2027c:	e3a0200d 	mov	r2, #13
   20280:	e1a01000 	mov	r1, r0
   20284:	e3a00001 	mov	r0, #1
   20288:	ebffff98 	bl	200f0 <write>
   2028c:	e1a03000 	mov	r3, r0
   20290:	e3000327 	movw	r0, #807	@ 0x327
   20294:	e3400003 	movt	r0, #3
   20298:	e58d0020 	str	r0, [sp, #32]
   2029c:	e3a00001 	mov	r0, #1
   202a0:	e58d0024 	str	r0, [sp, #36]	@ 0x24
   202a4:	e59d0020 	ldr	r0, [sp, #32]
   202a8:	e3a02001 	mov	r2, #1
   202ac:	e1a01000 	mov	r1, r0
   202b0:	e3a00001 	mov	r0, #1
   202b4:	ebffff8d 	bl	200f0 <write>
   202b8:	e7f000f0 	udf	#0

000202bc <br_join>:
   202bc:	e3000328 	movw	r0, #808	@ 0x328
   202c0:	e3400003 	movt	r0, #3
   202c4:	e58d0028 	str	r0, [sp, #40]	@ 0x28
   202c8:	e3a00003 	mov	r0, #3
   202cc:	e58d002c 	str	r0, [sp, #44]	@ 0x2c
   202d0:	e59d0028 	ldr	r0, [sp, #40]	@ 0x28
   202d4:	e3a02003 	mov	r2, #3
   202d8:	e1a01000 	mov	r1, r0
   202dc:	e3a00001 	mov	r0, #1
   202e0:	ebffff82 	bl	200f0 <write>
   202e4:	e1a01000 	mov	r1, r0
   202e8:	e3a00000 	mov	r0, #0
   202ec:	e28dd03c 	add	sp, sp, #60	@ 0x3c
   202f0:	e8bd8000 	ldmfd	sp!, {pc}
```
</details>

### Summary Of Commands For Generating an Executable

#### X64 (X86-64)

```
FE/emit_ir.py -shake_tree -stdlib FE/Lib -arch x64 FE/LangTest/sieve_test.cw > sieve.ir
cat BE/StdLib/startup.x64.asm BE/StdLib/syscall.x64.asm BE/StdLib/std_lib.64.asm sieve.ir | BE/CodeGenX64/codegen.py -mode binary - sieve.x64.exe

./sieve.x64.exe

objdump -d sieve.x64.exe
```

#### A32 (Arm32)

```
FE/emit_ir.py -shake_tree -stdlib FE/Lib -arch a32 FE/LangTest/sieve_test.cw > sieve.ir
cat BE/StdLib/startup.a32.asm BE/StdLib/syscall.a32.asm BE/StdLib/std_lib.32.asm sieve.ir | BE/CodeGenA32/codegen.py -mode binary - sieve.a32.exe

./sieve.a32.exe

arm-linux-gnueabihf-objdump -d sieve.a32.exe
```

#### A64 (Aarch64))

```
FE/emit_ir.py -shake_tree -stdlib FE/Lib -arch a64 FE/LangTest/sieve_test.cw > sieve.ir
cat BE/StdLib/startup.a64.asm BE/StdLib/syscall.a64.asm BE/StdLib/std_lib.64.asm sieve.ir | BE/CodeGenA64/codegen.py -mode binary - sieve.a64.exe


./sieve.a64.exe

aarch64-linux-gnu-objdump -d sieve.a64.exe
```
