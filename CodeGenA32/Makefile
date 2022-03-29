.SUFFIXES:  # no built-in rules
DIR=build

QEMU = qemu-arm-static

$(info $(shell mkdir -p $(DIR)))

LOCAL_TESTS = malloc.a32.asm  linkerdef.a32.asm

TESTS = int_op.asm \
        reg_torture_f32.asm \
        reg_torture.asm \
        cmp.asm \
        memaddr.32.asm \
        switch.asm \
        indirect.32.asm \
        fib.asm \
        queens.32.asm \
        stack.asm \
        multiple_results.asm \
        multiple_results_f32.asm \
        multiple_results_f64.asm \
        pfannkuchen.32.asm

TEST_EXES = $(TESTS:%.asm=$(DIR)/%.asm.exe) $(LOCAL_TESTS:%.asm=$(DIR)/%.asm.exe)
TEST_C_EXES = $(TESTS:%.asm=$(DIR)/%.asm.c.exe) $(LOCAL_TESTS:%.asm=$(DIR)/%.asm.c.exe)


tests: tests_py tests_c
	@echo "[OK CodeGenA32]"

tests_py: $(TEST_EXES) $(DIR)/queens.32.asm.s.exe $(DIR)/syscall.a32.asm.exe $(DIR)/cli.a32.asm.exe $(DIR)/isel_test $(DIR)/nanojpeg

tests_c: $(TEST_C_EXES) $(DIR)/isel_test_c $(DIR)/codegen_parity $(DIR)/nanojpeg_c

STD_LIB_NO_ARGV = ../StdLib/startup_no_argv.a32.asm ../StdLib/syscall.a32.asm ../StdLib/std_lib.32.asm
STD_LIB_WITH_ARGV = ../StdLib/startup.a32.asm ../StdLib/syscall.a32.asm ../StdLib/std_lib.32.asm

############################################################
# Python
############################################################

# note we sneak in our poor man's std_lib here
$(DIR)/%.asm.exe: ../TestData/%.asm
	@echo "[integration $@]"
	cat $(STD_LIB_NO_ARGV) $< | $(PYPY) ./codegen.py -mode binary - $@ >$@.out
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

# sames as above but local TestData dir
$(DIR)/%.asm.exe: TestData/%.asm
	@echo "[integration $@]"
	cat $(STD_LIB_NO_ARGV) $< | $(PYPY) ./codegen.py -mode binary - $@ >$@.out
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/syscall.a32.asm.exe: TestData/syscall.a32.asm
	@echo "[integration $@]"
	$(PYPY) ./codegen.py -mode binary $<  $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden


$(DIR)/queens.32.asm.s.exe: ../TestData/queens.32.asm
	@echo "[integration $@]"
	cat $(STD_LIB_NO_ARGV) $< | $(PYPY) ./codegen.py -mode normal - $@.s
	$(PYPY)	../CpuA32/assembler_tool.py assemble $@.s $@ > $@.out
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/cli.a32.asm.exe: TestData/cli.a32.asm
	@echo "[integration $@]"
	cat $(STD_LIB_WITH_ARGV) $< | $(PYPY) ./codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 1 2 3 aa bbb ccc > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/isel_test:
	@echo "[integration $@]"
	$(PYPY) ./isel_tester.py < TestData/codegen_test.asm  > $@.actual.out
	diff $@.actual.out TestData/codegen_test.asm.golden

$(DIR)/nanojpeg:
	@echo "[$@]"
	cat $(STD_LIB_WITH_ARGV) ../TestData/nano_jpeg.32.asm  | $(PYPY) ./codegen.py -mode binary - $@.exe >$@.out
	${QEMU} $@.exe ../TestData/ash_tree.jpg $@.ppm
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

############################################################
# C++
############################################################
BUILD_DIR=../build
CODEGEN_TOOL=$(BUILD_DIR)/a32_codegen_tool.exe

$(CODEGEN_TOOL):
	@cd $(BUILD_DIR); $(MAKE) -s a32_codegen_tool.exe

$(DIR)/%.asm.c.exe: ../TestData/%.asm $(CODEGEN_TOOL)
	@echo "[integration $@]"
	cat $(STD_LIB_NO_ARGV) $< | $(CODEGEN_TOOL) -mode binary - $@ >$@.out
	@chmod a+rx $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

# same as above but from local TestData dir
$(DIR)/%.asm.c.exe: TestData/%.asm  $(CODEGEN_TOOL)
	@echo "[integration $@]"
	cat $(STD_LIB_NO_ARGV) $< | $(CODEGEN_TOOL) -mode binary - $@ >$@.out
	@chmod a+rx $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/isel_test_c: isel_gen.h isel_gen.cc
	@echo "[integration $@]"
	@cd $(BUILD_DIR); $(MAKE) -s a32_isel_tester.exe
	$(BUILD_DIR)/a32_isel_tester.exe < TestData/codegen_test.asm  > $@.actual.out
	diff $@.actual.out TestData/codegen_test.asm.golden

$(DIR)/nanojpeg_c: $(CODEGEN_TOOL)
	@echo "[$@]"
	cat $(STD_LIB_WITH_ARGV) ../TestData/nano_jpeg.32.asm | $(CODEGEN_TOOL) -mode binary - $@.exe >$@.out
	@chmod a+rx $@.exe
	${QEMU} $@.exe ../TestData/ash_tree.jpg $@.ppm
	md5sum  $@.ppm | sed -e "s|$@.ppm|nanojpeg.ppm|" > $@.actual
	diff $@.actual ../TestData/nano_jpeg.golden

# called from toplevel
benchmark: $(CODEGEN_TOOL)
	@echo "[$@]"
	time $(CODEGEN_TOOL) -mode binary -add_startup_code TestData/benchmark.asm $(DIR)/$@.exe > $(DIR)/$@.out

TEST_MODE = normal
#TEST_MODE = reg_alloc_local
#TEST_MODE = reg_alloc_global

# ensure identical output when emitting textual assembly between
# python and c++ implementations
$(DIR)/codegen_parity: isel_gen.h isel_gen.cc $(CODEGEN_TOOL)
	@echo "[$@]"
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/int_op.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) -  $@.out
	cat $(STD_LIB_NO_ARGV) ../TestData/int_op.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/cmp.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) -  $@.out
	cat $(STD_LIB_NO_ARGV) ../TestData/cmp.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/reg_torture.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) -  $@.out
	cat $(STD_LIB_NO_ARGV) ../TestData/reg_torture.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) TestData/linkerdef.a32.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) TestData/linkerdef.a32.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) -  $@.out
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
	cat $(STD_LIB_NO_ARGV) ../TestData/fib.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/fib.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/queens.32.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/queens.32.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_NO_ARGV) ../TestData/reg_torture_f32.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/reg_torture_f32.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
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
	cat $(STD_LIB_NO_ARGV) ../TestData/memaddr.32.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_NO_ARGV) ../TestData/memaddr.32.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out
	@echo
	cat $(STD_LIB_WITH_ARGV) ../TestData/nano_jpeg.32.asm | $(CODEGEN_TOOL) -mode $(TEST_MODE) - $@_c.out
	cat $(STD_LIB_WITH_ARGV) ../TestData/nano_jpeg.32.asm | $(PYPY) ./codegen.py -mode $(TEST_MODE) - $@.out
	diff $@_c.out $@.out


regenerate_cpua32_tests:
	#cat $(STD_LIB_NO_ARGV) ../TestData/memaddr.32.asm |  $(CODEGEN_TOOL) -mode normal - ../CpuA32/TestData/memaddr.asm
	#cat $(STD_LIB_NO_ARGV) ../TestData/fib.asm |  $(CODEGEN_TOOL) -mode normal - ../CpuA32/TestData/fib.asm
	cat $(STD_LIB_NO_ARGV) ../TestData/nano_jpeg.32.asm |  $(CODEGEN_TOOL) -mode normal - ../CpuA32/TestData/nanojpeg.asm
	#cat $(STD_LIB_NO_ARGV) ../TestData/switch.asm |  $(CODEGEN_TOOL) -mode normal - ../CpuA32/TestData/switch.asm
############################################################
# Misc
############################################################

clean:
	rm -f $(DIR)/* $(CODEGEN_TOOL)

bug:
	cat $(STD_LIB) TestData/reg_test1.asm | $(PYPY) ./codegen.py normal - -
