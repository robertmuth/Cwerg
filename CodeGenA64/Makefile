
# no built-in rules please
.SUFFIXES:

DIR=build

$(info $(shell mkdir -p $(DIR)))

tests: tests_py tests_c
	@echo "[OK CodeGenA64]"


tests_py: $(DIR)/syscall.a64.asm.exe

tests_c:

$(DIR)/syscall.a64.asm.exe: TestData/syscall.a64.asm
	@echo "[integration $@]"
	$(PYPY) ./codegen.py normal $<  $@.s
	$(PYPY)	../CpuA64/assembler_tool.py assemble_raw $@.s $@ > $@.out
	$@ > $@.actual.out
	diff $@.actual.out $<.golden

clean:
	@rm -f $(DIR)/*
