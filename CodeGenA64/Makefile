
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


tests_py: $(TEST_EXES)  $(DIR)/queens.64.asm.s.exe $(DIR)/syscall.a64.asm.exe $(DIR)/cli.a64.asm.exe $(DIR)/nanojpeg

tests_c:

# note we sneak in our poor man's std_lib here
$(DIR)/%.asm.exe: ../TestData/%.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py binary - $@ >$@.out
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/syscall.a64.asm.exe: TestData/syscall.a64.asm
	@echo "[integration $@]"
	$(PYPY) ./codegen.py normal $<  $@.s
	$(PYPY)	../CpuA64/assembler_tool.py assemble_raw $@.s $@ > $@.out
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/queens.64.asm.s.exe: ../TestData/queens.64.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py normal - $@.s
	$(PYPY)	../CpuA64/assembler_tool.py assemble $@.s $@ > $@.out
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/cli.a64.asm.exe: TestData/cli.a64.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py binary - $@ > $@.out
	$@ 1 2 3 aa bbb ccc > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/nanojpeg:
	@echo "[$@]"
	cat $(STD_LIB) ../TestData/nano_jpeg.64.asm  | $(PYPY) ./codegen.py binary - $@.exe >$@.out
	./$@.exe ../TestData/ash_tree.jpg $@.ppm
	md5sum  $@.ppm > $@.actual
	diff $@.actual TestData/nano_jpeg.golden

isel_gen.cc: isel_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_c <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

isel_gen.h: isel_tab.py
	@echo "[$@]"
	$(PYPY) ./isel_tab.py gen_h <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

clean:
	@rm -f $(DIR)/*
