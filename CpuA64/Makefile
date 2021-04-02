
.SUFFIXES:

TESTS = TestData/exit.asm TestData/hello.asm TestData/fib.asm

TEST_INSTRUCTIONS = 0 90000440 9126c000 14014192 97fffcf7 54000140

.PHONY: $(TESTS)

tests: tests_py tests_c
	@echo


tests_py: objdump_compat_test argv_test disassembler_test  $(TESTS:.asm=.test)


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

argv_test: TestData/argv.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble $< TestData/$@.exe > $<.out
	TestData/$@.exe argv1 argv2 arvg3 argv4 ... argn > $<.actual.out
	diff $<.actual.out $<.golden

disassembler_test:
	@echo "[$@]"
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual.out TestData/$@.golden

clean:
