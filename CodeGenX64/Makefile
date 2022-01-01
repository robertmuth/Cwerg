# no built-in rules please
.SUFFIXES:

DIR=build
QEMU=

$(info $(shell mkdir -p $(DIR)))
TESTS =  multiple_results.asm memaddr.64.asm stack.asm int_op.asm queens.64.asm fib.asm stack.asm pfannkuchen.64.asm

TESTS2 = fp_op.asm \
        reg_torture_f32.asm \
        reg_torture.asm \
        cmp.asm \
        multiple_results_f32.asm \
        multiple_results_f64.asm \
        switch.asm \
        indirect.64.asm

TEST_EXES = $(TESTS:%.asm=$(DIR)/%.asm.exe)
TEST_C_EXES = $(TESTS:%.asm=$(DIR)/%.asm.c.exe)

STD_LIB = ../StdLib/syscall.x64.asm ../StdLib/std_lib.64.asm

tests: tests_py tests_c
	@echo "[OK CodeGenX64]"

tests_py:  $(DIR)/isel_test $(DIR)/syscall.x64.asm.exe $(DIR)/cli.x64.asm.exe $(TEST_EXES)

tests_c:

# note we sneak in our poor man's std_lib here
$(DIR)/%.asm.exe: ../TestData/%.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py -mode binary -add_startup_code - $@ >$@.out
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden


$(DIR)/isel_test:
	@echo "[integration $@]"
	$(PYPY) ./isel_tester.py < TestData/codegen_test.asm  > $@.actual.out
	diff $@.actual.out TestData/codegen_test.asm.golden

$(DIR)/syscall.x64.asm.exe: TestData/syscall.x64.asm
	@echo "[integration $@]"
	$(PYPY) ./codegen.py -mode binary $<  $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden


$(DIR)/cli.x64.asm.exe: TestData/cli.x64.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py -mode binary -add_startup_code - $@ > $@.out
	${QEMU} $@ 1 2 3 aa bbb ccc > $@.actual.out
	diff $@.actual.out $<.golden


clean:
	rm -f $(DIR)/*
