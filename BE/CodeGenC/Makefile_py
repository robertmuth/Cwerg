

.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

TESTS = fp_op.asm \
        int_op.asm \
        cmp.asm \
        multiple_results.asm \
        multiple_results_f32.asm \
        multiple_results_f64.asm \
        fib.asm \
        queens.64.asm \
        switch.asm \
        indirect.64.asm \
        memaddr.64.asm \
        stack.asm \
        add_const.asm
        # struct.asm

TEST_EXES = $(TESTS:%.asm=$(DIR)/%.asm.exe)
TEST_OPT_EXES = $(TESTS:%.asm=$(DIR)/%.asm.opt.exe)


tests: $(TEST_EXES)  $(TEST_OPT_EXES)
	@echo "[OK CodeGenC]"

CC_FLAGS = -Wall -Wno-unused-result -Wno-unused-label -Wno-unused-variable \
   -Wno-uninitialized -Wno-main -Wno-unused-but-set-variable \
   -Wno-misleading-indentation \
   -Wno-non-literal-null-conversion -I../StdLib

$(DIR)/%.asm.exe : ../TestData/%.asm
	echo "[ir -> c.64 $@]"
	cat ../StdLib/syscall.extern64.asm ../StdLib/std_lib.64.asm $< | $(PYPY) ./codegen.py - > $@.c
	$(CC) $(CC_FLAGS) -O -static -m64 -nostdlib ../StdLib/syscall.c $@.c -lgcc  -o $@
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/%.asm.opt.exe : ../TestData/%.asm
	echo "[ir -> opt -> c.64 $@]"
	cat ../StdLib/syscall.extern64.asm ../StdLib/std_lib.64.asm $< | ${PYPY} ../Base/optimize.py > $@.opt
	$(PYPY) ./codegen.py $@.opt  > $@.opt.c
	$(CC) $(CC_FLAGS) -O -static -m64 -nostdlib ../StdLib/syscall.c $@.opt.c  -lgcc -lm -o $@
	$@ > $@.actual.opt.out
	diff $@.actual.opt.out $<.golden

clean:
	rm -f  $(DIR)/*
