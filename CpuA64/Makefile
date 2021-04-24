
.SUFFIXES:

TESTS = TestData/exit.asm TestData/hello.asm TestData/fib.asm

TEST_INSTRUCTIONS = 0 90000440 9126c000 14014192 97fffcf7 54000140 1e201004 f2c7f84a

.PHONY: $(TESTS)

tests: tests_py tests_c
	@echo


tests_py: disassembler_test objdump_compat_test argv_test  $(TESTS:.asm=.test)


tests_c: opcode_test_c symbolize_parity codegen_parity

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

############################################################
# C++ Port
############################################################
BUILD_DIR=../build

ASSEMBLER_TOOL=$(BUILD_DIR)/a64_assembler_tool.exe
DISASSEMBLER_TOOL=$(BUILD_DIR)/a64_disassembler_tool.exe


opcode_gen.cc: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_c <$@ > $@.tmp
	@mv $@.tmp $@

opcode_gen.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_h <$@ > $@.tmp
	@mv $@.tmp $@

opcode_test_c: opcode_gen.h opcode_gen.cc
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s a64_opcode_test.exe
	$(BUILD_DIR)/a64_opcode_test.exe


symbolize_parity:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s a64_disassembler_tool.exe

	$(DISASSEMBLER_TOOL) $(TEST_INSTRUCTIONS) > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual_c.out $@.actual.out
	#
	$(DISASSEMBLER_TOOL) batch < TestData/a64_test.regular.dis > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py batch < TestData/a64_test.regular.dis  > $@.actual.out
	diff $@.actual_c.out $@.actual.out

codegen_parity: $(ASSEMBLER_TOOL)
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s a64_assembler_tool.exe

clean:
	rm -f  TestData/*.out TestData/*.exe *.exe *.out
