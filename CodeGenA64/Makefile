
# no built-in rules please
.SUFFIXES:

DIR=build

QEMU = qemu-aarch64-static

$(info $(shell mkdir -p $(DIR)))

TESTS = fp_op.asm \
        int_op.asm \
        reg_torture_f32.asm \
        reg_torture.asm \
        cmp.asm \
        fib.asm \
        stack.asm \
        multiple_results.asm \
        multiple_results_f32.asm \
        multiple_results_f64.asm \
        memaddr.64.asm \
        switch.asm \
        indirect.64.asm \
        queens.64.asm \
        pfannkuchen.64.asm

TEST_EXES = $(TESTS:%.asm=$(DIR)/%.asm.exe)
TEST_C_EXES = $(TESTS:%.asm=$(DIR)/%.asm.c.exe)

STD_LIB_NO_ARGV = ../StdLib/startup_no_argv.asm ../StdLib/syscall.a64.asm ../StdLib/std_lib.64.asm
STD_LIB_WITH_ARGV = ../StdLib/startup.a64.asm ../StdLib/syscall.a64.asm ../StdLib/std_lib.64.asm

tests: tests_py tests_c
	@echo "[OK CodeGenA64]"


tests_py: $(TEST_EXES) $(DIR)/syscall.a64.asm.exe $(DIR)/cli.a64.asm.exe $(DIR)/nanojpeg $(DIR)/isel_test

tests_c: $(DIR)/isel_test_c $(DIR)/syscall.a64.asm.c.exe $(TEST_C_EXES) $(DIR)/nanojpeg_c $(DIR)/codegen_parity

# note we sneak in our poor man's std_lib here
$(DIR)/%.asm.exe: ../TestData/%.asm
	@echo "[integration $@]"
	cat $(STD_LIB_NO_ARGV) $< | $(PYPY) ./codegen.py -mode binary - $@ >$@.out
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/syscall.a64.asm.exe: TestData/syscall.a64.asm
	@echo "[integration $@]"
	$(PYPY) ./codegen.py -mode binary $<  $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/cli.a64.asm.exe: TestData/cli.a64.asm
	@echo "[integration $@]"
	cat $(STD_LIB_WITH_ARGV) $< | $(PYPY) ./codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 1 2 3 aa bbb ccc > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/threads.a64.asm.exe: ../TestData/threads.64.asm
	@echo "[integration $@]"
	cat $(STD_LIB_NO_ARGV) $< | $(PYPY) ./codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/nanojpeg:
	@echo "[$@]"
	cat $(STD_LIB_WITH_ARGV) ../TestData/nano_jpeg.64.asm  | $(PYPY) ./codegen.py -mode binary - $@.exe >$@.out
	${QEMU} $@.exe ../TestData/ash_tree.jpg $@.ppm
	md5sum  $@.ppm > $@.actual
	diff $@.actual TestData/nano_jpeg.golden

$(DIR)/isel_test:
	@echo "[integration $@]"
	$(PYPY) ./isel_tester.py < TestData/codegen_test.asm  > $@.actual.out
	diff $@.actual.out TestData/codegen_test.asm.golden

############################################################
# Code Gen
############################################################

isel_gen.cc: isel_tab.py ../Base/opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_c <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

isel_gen.h: isel_tab.py ../Base/opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_h <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

############################################################
# C++
############################################################
BUILD_DIR=../build
CODEGEN_TOOL=$(BUILD_DIR)/a64_codegen_tool.exe

$(CODEGEN_TOOL)::
	@cd $(BUILD_DIR); $(MAKE) -s a64_codegen_tool.exe

$(DIR)/%.asm.c.exe: ../TestData/%.asm $(CODEGEN_TOOL)
	@echo "[integration $@]"
	cat $(STD_LIB_NO_ARGV) $< | $(CODEGEN_TOOL) -mode binary - $@ >$@.out
	@chmod a+rx $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

# same as above but from local TestData dir
# $(DIR)/%.asm.c.exe: TestData/%.asm  $(CODEGEN_TOOL)
	@echo "[integration $@]"
	cat $(STD_LIB_NO_ARGV) $< | $(CODEGEN_TOOL) -mode binary - $@ >$@.out
	@chmod a+rx $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/syscall.a64.asm.c.exe: TestData/syscall.a64.asm $(CODEGEN_TOOL)
	@echo "[integration $@]"
	$(CODEGEN_TOOL) -mode binary $< $@ >$@.out
	@chmod a+rx $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden


$(DIR)/isel_test_c: isel_gen.h isel_gen.cc
	@echo "[integration $@]"
	@cd $(BUILD_DIR); $(MAKE) -s a64_isel_tester.exe
	$(BUILD_DIR)/a64_isel_tester.exe < TestData/codegen_test.asm  > $@.actual.out
	diff $@.actual.out TestData/codegen_test.asm.golden

$(DIR)/nanojpeg_c: $(CODEGEN_TOOL)
	@echo "[$@]"
	cat $(STD_LIB_WITH_ARGV) ../TestData/nano_jpeg.64.asm | $(CODEGEN_TOOL) -mode binary - $@.exe >$@.out
	@chmod a+rx $@.exe
	${QEMU} $@.exe ../TestData/ash_tree.jpg $@.ppm
	md5sum  $@.ppm | sed -e "s|$@.ppm|nanojpeg.ppm|" > $@.actual
	diff $@.actual ../TestData/nano_jpeg.golden

TEST_MODE = normal
#TEST_MODE = reg_alloc_local
#TEST_MODE = reg_alloc_global

# ensure identical output when emitting textual assembly between
# python and c++ implementations
$(DIR)/codegen_parity: isel_gen.h isel_gen.cc $(CODEGEN_TOOL)
	@echo "[$@]"
	cat $(STD_LIB_NO_ARGV) ../TestData/threads.64.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/threads.64.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/int_op.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/int_op.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/cmp.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/cmp.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/queens.64.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/queens.64.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/fib.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/fib.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/reg_torture.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) -  $@.out
	cat $(STD_LIB_NO_ARGV) ../TestData/reg_torture.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/multiple_results_f64.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/multiple_results_f64.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/multiple_results_f32.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/multiple_results_f32.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/stack.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/stack.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/switch.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/switch.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/memaddr.64.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/memaddr.64.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/reg_torture_f32.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/reg_torture_f32.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_WITH_ARGV) ../TestData/nano_jpeg.64.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_WITH_ARGV) ../TestData/nano_jpeg.64.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out


clean:
	@rm -f $(DIR)/* $(CODEGEN_TOOL)
