
# no built-in rules please
.SUFFIXES:

tests: tests_py tests_c
	@echo

tests_py:  TestData/syscall.a64.asm.exe

tests_c:

TestData/syscall.a64.asm.exe: TestData/syscall.a64.asm
	@echo "[integration $@]"
	$(PYPY) ./codegen.py normal $<  $<.s
	$(PYPY)	../CpuA64/assembler_tool.py assemble_raw $<.s $@ > $<.out
	$@ > $<.actual.out
	diff $<.actual.out $<.golden



clean:
	@rm -f TestData/*.exe TestData/*.out TestData/*.s
