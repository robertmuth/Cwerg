
.SUFFIXES:

TESTS = TestData/exit.asm TestData/hello.asm TestData/fib.asm


.PHONY: $(TESTS)

tests: tests_py tests_c
	@echo


tests_py: objdump_compat_test $(TESTS:.asm=.test)


tests_c:

objdump_compat_test:
	@echo "[$@]"
	$(PYPY) ./opcode_test.py TestData/a64_test.regular.dis

############################################################
# Python Port
############################################################
%.test : %.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble_raw $< $@.exe > $<.out
	$@.exe > $<.actual.out
	diff $<.actual.out $<.golden


clean:
