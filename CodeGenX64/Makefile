# no built-in rules please
.SUFFIXES:

DIR=build
QEMU=

$(info $(shell mkdir -p $(DIR)))
TESTS = cmp.asm \
        reg_torture.asm \
        reg_torture_f32.asm \
        fp_op.asm \
        multiple_results_f64.asm \
        multiple_results_f32.asm \
        switch.asm indirect.64.asm \
        multiple_results.asm \
        memaddr.64.asm \
        stack.asm \
        int_op.asm \
        queens.64.asm \
        fib.asm \
        stack.asm \
        pfannkuchen.64.asm

TEST_EXES = $(TESTS:%.asm=$(DIR)/%.asm.exe)
TEST_C_EXES = $(TESTS:%.asm=$(DIR)/%.asm.c.exe)

STD_LIB = ../StdLib/syscall.x64.asm ../StdLib/std_lib.64.asm

tests: tests_py tests_c
	@echo "[OK CodeGenX64]"

tests_py: $(DIR)/isel_test $(DIR)/syscall.x64.asm.exe $(DIR)/cli.x64.asm.exe $(TEST_EXES) $(DIR)/nanojpeg

tests_c: $(DIR)/isel_test_c $(DIR)/codegen_parity

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

$(DIR)/nanojpeg:
	@echo "[$@]"
	cat $(STD_LIB) ../TestData/nano_jpeg.64.asm  | $(PYPY) ./codegen.py -mode binary  -add_startup_code - $@.exe >$@.out
	$@.exe ../TestData/ash_tree.jpg $@.ppm
	md5sum  $@.ppm > $@.actual
	diff $@.actual TestData/nano_jpeg.golden

############################################################
# Code Gen
############################################################

isel_gen.cc: isel_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_c <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

isel_gen.h: isel_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_h <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

isel_gen_patterns.h: isel_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_patterns_h >$@

############################################################
# C++
############################################################
BUILD_DIR=../build
CODEGEN_TOOL=$(BUILD_DIR)/x64_codegen_tool.exe

$(CODEGEN_TOOL)::
	@cd $(BUILD_DIR); $(MAKE) -s x64_codegen_tool.exe

$(DIR)/isel_test_c: isel_gen.h isel_gen.cc
	@echo "[integration $@]"
	@cd $(BUILD_DIR); $(MAKE) -s x64_isel_tester.exe
	$(BUILD_DIR)/x64_isel_tester.exe < TestData/codegen_test.asm  > $@.actual.out
	diff $@.actual.out TestData/codegen_test.asm.golden

#TEST_MODE = normal
#TEST_MODE = legalize
TEST_MODE = reg_alloc_global
#TEST_MODE = reg_alloc_local

# ensure identical output when emitting textual assembly between
# python and c++ implementations
$(DIR)/codegen_parity: isel_gen.h isel_gen.cc $(CODEGEN_TOOL)
	@echo "[$@]"
	cat $(STD_LIB) ../TestData/int_op.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/int_op.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/cmp.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/cmp.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/queens.64.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/queens.64.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/fib.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/fib.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/reg_torture.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) -  $@.out
	cat $(STD_LIB) ../TestData/reg_torture.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/multiple_results_f64.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/multiple_results_f64.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/multiple_results_f32.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/multiple_results_f32.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/stack.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/stack.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/switch.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/switch.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/memaddr.64.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/memaddr.64.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/reg_torture_f32.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/reg_torture_f32.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB) ../TestData/nano_jpeg.64.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB) ../TestData/nano_jpeg.64.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out

clean:
	rm -f $(DIR)/*
