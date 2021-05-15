
TESTS = TestData/malloc.a32.asm \
        ../TestData/reg_torture_f32.asm \
        ../TestData/reg_torture.asm \
        ../TestData/cmp.asm \
        ../TestData/memaddr.32.asm \
        ../TestData/switch.asm \
        ../TestData/indirect.32.asm \
        ../TestData/fib.asm \
        ../TestData/queens.32.asm \
        ../TestData/stack.asm \
        ../TestData/multiple_results.asm \
        ../TestData/multiple_results_f32.asm \
        ../TestData/multiple_results_f64.asm \
        TestData/linkerdef.a32.asm

TEST_EXES = $(TESTS:.asm=.asm.exe)
TEST_C_EXES = $(TESTS:.asm=.asm.c.exe)

TEST_OPT_EXES = $(TESTS:.asm=.asm.opt.exe)

.SUFFIXES:
.PHONY: $(TESTS) TestData/syscall.a32.asm.exe TestData/cli.asm.a32.exe

tests: tests_py tests_c
	@echo

tests_py:  $(TEST_EXES) ../TestData/queens.32.asm.s.exe TestData/syscall.a32.asm.exe TestData/cli.asm.a32.exe isel_test nanojpeg

tests_c: $(TEST_C_EXES) isel_test isel_test_c codegen_parity nanojpeg_c


STD_LIB = ../StdLib/syscall.a32.asm ../StdLib/std_lib.32.asm

############################################################
# Python
############################################################

# note we sneak in our poor man's std_lib here
%.asm.exe: %.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py binary - $@ >$@.out
	$@ > $<.actual.out
	diff $<.actual.out $<.golden

TestData/syscall.a32.asm.exe: TestData/syscall.a32.asm
	@echo "[integration $@]"
	$(PYPY) ./codegen.py normal $<  $<.s
	$(PYPY)	../CpuA32/assembler_tool.py assemble_raw $<.s $@ > $<.out
	$@ > $<.actual.out
	diff $<.actual.out $<.golden


../TestData/queens.32.asm.s.exe: ../TestData/queens.32.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py normal - $<.s
	$(PYPY)	../CpuA32/assembler_tool.py assemble $<.s $@ > $<.out
	$@ > $<.actual.out
	diff $<.actual.out $<.golden

TestData/cli.asm.a32.exe: TestData/cli.a32.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py binary - $@ > $<.out
	$@ 1 2 3 aa bbb ccc > $<.actual.out
	diff $<.actual.out $<.golden

isel_test:
	@echo "[integration $@]"
	$(PYPY) ./isel_tester.py < TestData/codegen_test.asm  > TestData/codegen_test.asm.actual.out
	diff TestData/codegen_test.asm.actual.out TestData/codegen_test.asm.golden


nanojpeg:
	@echo "[$@]"
	cat $(STD_LIB) ../TestData/nano_jpeg.32.asm  | $(PYPY) ./codegen.py binary - $@.exe >$@.out
	./$@.exe ../TestData/ash_tree.jpg $@.ppm
	md5sum  $@.ppm > $@.actual
	diff $@.actual ../TestData/nano_jpeg.golden

############################################################
# C++
############################################################
BUILD_DIR=../build
CODEGEN_TOOL=$(BUILD_DIR)/a32_codegen_tool.exe

$(CODEGEN_TOOL)::
	@cd $(BUILD_DIR); $(MAKE) -s a32_codegen_tool.exe

%.asm.c.exe: %.asm
	@echo "[integration $@]"
	@cd $(BUILD_DIR); $(MAKE) -s a32_codegen_tool.exe
	cat $(STD_LIB) $< | $(CODEGEN_TOOL) -mode binary - $@ >$@.out
	@chmod a+rx $@
	$@ > $<.actual.out
	diff $<.actual.out $<.golden

isel_gen.cc: isel_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_c <$@ > $@.tmp
	@mv $@.tmp $@

isel_gen.h: isel_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_h <$@ > $@.tmp
	@mv $@.tmp $@

isel_test_c: isel_gen.h isel_gen.cc
	@echo "[integration $@]"
	@cd $(BUILD_DIR); $(MAKE) -s a32_isel_tester.exe
	$(BUILD_DIR)/a32_isel_tester.exe < TestData/codegen_test.asm  > TestData/codegen_test_c.asm.actual.out
	diff TestData/codegen_test_c.asm.actual.out TestData/codegen_test.asm.golden

nanojpeg_c: $(CODEGEN_TOOL)
	@echo "[$@]"
	cat $(STD_LIB) ../TestData/nano_jpeg.32.asm  |  $(CODEGEN_TOOL) -mode binary  - $@.exe >$@.out
	@chmod a+rx $@.exe
	./$@.exe ../TestData/ash_tree.jpg $@.ppm
	md5sum  $@.ppm | sed -e "s/$@.ppm/nanojpeg.ppm/" > $@.actual
	diff $@.actual ../TestData/nano_jpeg.golden

benchmark: $(CODEGEN_TOOL)
	@echo "[$@]"
	time $(CODEGEN_TOOL) -mode binary TestData/benchmark.asm $@.exe >$@.out

TEST_MODE = normal
#TEST_MODE = reg_alloc_local
#TEST_MODE = reg_alloc_global

# ensure identical output when emitting textual assembly between
# python and c++ implementations
codegen_parity: isel_gen.h isel_gen.cc $(CODEGEN_TOOL)
	@echo "[$@]"
	@echo
	cat $(STD_LIB) ../TestData/reg_torture.asm | $(PYPY) ./codegen.py $(TEST_MODE) -  TestData/$@.out
	cat $(STD_LIB) ../TestData/reg_torture.asm  |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) TestData/linkerdef.a32.asm  |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	cat $(STD_LIB) TestData/linkerdef.a32.asm | $(PYPY) ./codegen.py $(TEST_MODE) -  TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) ../TestData/multiple_results_f64.asm  |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	cat $(STD_LIB) ../TestData/multiple_results_f64.asm | $(PYPY) ./codegen.py $(TEST_MODE) -  TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) ../TestData/multiple_results_f32.asm  |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	cat $(STD_LIB) ../TestData/multiple_results_f32.asm | $(PYPY) ./codegen.py $(TEST_MODE) -  TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) ../TestData/fib.asm |  $(CODEGEN_TOOL) -mode $(TEST_MODE)  - TestData/$@_c.out
	cat $(STD_LIB) ../TestData/fib.asm | $(PYPY) ./codegen.py $(TEST_MODE) - TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) ../TestData/queens.32.asm |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	cat $(STD_LIB) ../TestData/queens.32.asm | $(PYPY) ./codegen.py $(TEST_MODE) - TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) ../TestData/reg_torture_f32.asm |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	cat $(STD_LIB) ../TestData/reg_torture_f32.asm | $(PYPY) ./codegen.py $(TEST_MODE) - TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) ../TestData/stack.asm |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	cat $(STD_LIB) ../TestData/stack.asm | $(PYPY) ./codegen.py $(TEST_MODE) - TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) ../TestData/switch.asm |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	cat $(STD_LIB) ../TestData/switch.asm | $(PYPY) ./codegen.py $(TEST_MODE) - TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) ../TestData/memaddr.32.asm |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	cat $(STD_LIB) ../TestData/memaddr.32.asm | $(PYPY) ./codegen.py $(TEST_MODE) - TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out
	@echo
	cat $(STD_LIB) ../TestData/nano_jpeg.32.asm |  $(CODEGEN_TOOL) -mode $(TEST_MODE) - TestData/$@_c.out
	cat $(STD_LIB) ../TestData/nano_jpeg.32.asm | $(PYPY) ./codegen.py $(TEST_MODE) - TestData/$@.out
	diff TestData/$@_c.out   TestData/$@.out


regenerate_cpua32_tests:
	#cat $(STD_LIB) ../TestData/memaddr.32.asm |  $(CODEGEN_TOOL) -mode normal - ../CpuA32/TestData/memaddr.asm
	#cat $(STD_LIB) ../TestData/fib.asm |  $(CODEGEN_TOOL) -mode normal - ../CpuA32/TestData/fib.asm
	cat $(STD_LIB) ../TestData/nano_jpeg.32.asm |  $(CODEGEN_TOOL) -mode normal - ../CpuA32/TestData/nanojpeg.asm
	#cat $(STD_LIB) ../TestData/switch.asm |  $(CODEGEN_TOOL) -mode normal - ../CpuA32/TestData/switch.asm
############################################################
# Misc
############################################################

clean:
	rm -fr TestData/*.out TestData/*.exe TestData/*.s *.exe *.out *.actual *.ppm

