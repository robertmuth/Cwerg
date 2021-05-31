
# no built-in rules please
.SUFFIXES:

DIR=build

$(info $(shell mkdir -p $(DIR)))

TESTS =  memaddr.64.asm fib.asm multiple_results.asm cmp.asm

TEST_EXES = $(TESTS:%.asm=$(DIR)/%.asm.exe) $(LOCAL_TESTS:%.asm=$(DIR)/%.asm.exe)

STD_LIB = ../StdLib/syscall.a64.asm ../StdLib/std_lib.64.asm

tests: tests_py tests_c
	@echo "[OK CodeGenA64]"


tests_py: $(TEST_EXES) $(DIR)/syscall.a64.asm.exe

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

clean:
	@rm -f $(DIR)/*
