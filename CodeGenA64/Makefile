
# no built-in rules please
.SUFFIXES:

DIR=build

$(info $(shell mkdir -p $(DIR)))

TESTS = reg_torture_f32.asm \
        reg_torture.asm \
        cmp.asm \
        memaddr.64.asm \
        switch.asm \
        indirect.64.asm \
        fib.asm \
        queens.64.asm \
        stack.asm \
        multiple_results.asm \
        multiple_results_f32.asm \
        multiple_results_f64.asm

TEST_EXES = $(TESTS:%.asm=$(DIR)/%.asm.exe)

STD_LIB = ../StdLib/syscall.a64.asm ../StdLib/std_lib.64.asm

tests: tests_py tests_c
	@echo "[OK CodeGenA64]"


tests_py: $(TEST_EXES)  $(DIR)/queens.64.asm.s.exe $(DIR)/syscall.a64.asm.exe $(DIR)/cli.a64.asm.exe $(DIR)/nanojpeg $(DIR)/isel_test

tests_c: $(DIR)/isel_test_c $(DIR)/syscall.a64.asm.c.exe

# note we sneak in our poor man's std_lib here
$(DIR)/%.asm.exe: ../TestData/%.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py -mode binary -add_startup_code - $@ >$@.out
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/syscall.a64.asm.exe: TestData/syscall.a64.asm
	@echo "[integration $@]"
	$(PYPY) ./codegen.py -mode binary $<  $@
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/queens.64.asm.s.exe: ../TestData/queens.64.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py -mode binary -add_startup_code - $@
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/cli.a64.asm.exe: TestData/cli.a64.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py -mode binary -add_startup_code - $@ > $@.out
	$@ 1 2 3 aa bbb ccc > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/nanojpeg:
	@echo "[$@]"
	cat $(STD_LIB) ../TestData/nano_jpeg.64.asm  | $(PYPY) ./codegen.py -mode binary  -add_startup_code - $@.exe >$@.out
	./$@.exe ../TestData/ash_tree.jpg $@.ppm
	md5sum  $@.ppm > $@.actual
	diff $@.actual TestData/nano_jpeg.golden

$(DIR)/isel_test:
	@echo "[integration $@]"
	$(PYPY) ./isel_tester.py < TestData/codegen_test.asm  > $@.actual.out
	diff $@.actual.out TestData/codegen_test.asm.golden

############################################################
# C++
############################################################
BUILD_DIR=../build
CODEGEN_TOOL=$(BUILD_DIR)/a64_codegen_tool.exe

$(CODEGEN_TOOL):
	@cd $(BUILD_DIR); $(MAKE) -s a64_codegen_tool.exe

$(DIR)/%.asm.c.exe: ../TestData/%.asm $(CODEGEN_TOOL)
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(CODEGEN_TOOL) -mode binary --add_startup_code - $@ >$@.out
	@chmod a+rx $@
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

# same as above but from local TestData dir
# $(DIR)/%.asm.c.exe: TestData/%.asm  $(CODEGEN_TOOL)
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(CODEGEN_TOOL) --add_startup_code -mode binary - $@ >$@.out
	@chmod a+rx $@
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/syscall.a64.asm.c.exe: TestData/syscall.a64.asm $(CODEGEN_TOOL)
	@echo "[integration $@]"
	$(CODEGEN_TOOL) -mode binary $< $@ >$@.out
	@chmod a+rx $@
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

isel_gen.cc: isel_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_c <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

isel_gen.h: isel_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_h <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

$(DIR)/isel_test_c: isel_gen.h isel_gen.cc
	@echo "[integration $@]"
	@cd $(BUILD_DIR); $(MAKE) -s a64_isel_tester.exe
	$(BUILD_DIR)/a64_isel_tester.exe < TestData/codegen_test.asm  > $@.actual.out
	diff $@.actual.out TestData/codegen_test.asm.golden

clean:
	@rm -f $(DIR)/*
