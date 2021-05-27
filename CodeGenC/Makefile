

.SUFFIXES:  # no built-in rules

TESTS = ../TestData/cmp.asm \
        ../TestData/multiple_results.asm \
        ../TestData/multiple_results_f32.asm \
        ../TestData/multiple_results_f64.asm \
        ../TestData//fib.asm \
        ../TestData/queens.64.asm \
        ../TestData/switch.asm \
        ../TestData/indirect.64.asm \
        ../TestData/memaddr.64.asm \
        ../TestData/stack.asm

        # TestData/struct.asm

TEST_EXES = $(TESTS:.asm=.asm.exe)
TEST_OPT_EXES = $(TESTS:.asm=.asm.opt.exe)


tests: $(TEST_EXES)  $(TEST_OPT_EXES)
	@echo OK

CC_FLAGS = -Wall -Wno-unused-result -Wno-unused-label -Wno-unused-variable \
   -Wno-uninitialized -Wno-main -Wno-unused-but-set-variable \
   -Wno-misleading-indentation \
   -Wno-non-literal-null-conversion -I../StdLib

%.asm.exe : %.asm
	echo "[ir -> c.64 $@]"
	cat ../StdLib/syscall.extern64.asm ../StdLib/std_lib.64.asm $< | $(PYPY) ./codegen.py - > $<.c
	$(CC) $(CC_FLAGS) -O -static -m64 -nostdlib ../StdLib/syscall.c $<.c  -o $@
	$@ > $<.actual.out
	diff $<.actual.out $<.golden

%.asm.opt.exe : %.asm
	echo "[ir -> opt -> c.64 $@]"
	cat ../StdLib/syscall.extern64.asm ../StdLib/std_lib.64.asm $< | ${PYPY} ../Base/optimize.py > $<.opt
	$(PYPY) ./codegen.py $<.opt  > $<.opt.c
	$(CC) $(CC_FLAGS) -O -static -m64 -nostdlib ../StdLib/syscall.c $<.opt.c -lm -o $@
	$@ > $<.actual.opt.out
	diff $<.actual.opt.out $<.golden

clean:
	rm -f  ../TestData/*.out ../TestData/*.exe ../TestData/*.c ../TestData/*.opt
