
.SUFFIXES:
DIR=build
QEMU = qemu-aarch64-static

$(info $(shell mkdir -p $(DIR)))

TESTS = exit.asm hello.asm fib.asm

TEST_INSTRUCTIONS = 0 90000440 9126c000 14014192 97fffcf7 54000140 1e201004 f2c7f84a \
                    f2c0000a f280000a 6ee0fb39 2ea41c20 6f02e6b0 1e602008 \
					9e670100 1e260000 e205800 2e303800 ee2e062 4ee3e282
      

tests: tests_py tests_c
	@echo "[OK CpuA64]"


tests_py: $(DIR)/disassembler_test objdump_compat_test $(DIR)/argv_test  $(TESTS:%.asm=$(DIR)/%.test)


tests_c: opcode_test_c $(DIR)/symbolize_parity $(DIR)/codegen_parity

objdump_compat_test:
	@echo "[$@]"
	$(PYPY) ./opcode_test.py TestData/a64_test.vector.supported.dis
	$(PYPY) ./opcode_test.py TestData/a64_test.regular.dis

############################################################
# Python Port
############################################################
$(DIR)/%.test : TestData/%.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble $< $@.exe > $@.out
	${QEMU} $@.exe > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/argv_test: TestData/argv.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble $< $@.exe > $@.out
	${QEMU} $@.exe argv1 argv2 arvg3 argv4 ... argn > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/disassembler_test:
	@echo "[$@]"
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual.out TestData/disassembler_test.golden

############################################################
# Code Gen
############################################################

opcode_gen.cc: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_c <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

opcode_gen.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_h <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

############################################################
# C++ Port
############################################################
BUILD_DIR=../build

ASSEMBLER_TOOL=$(BUILD_DIR)/a64_assembler_tool.exe
DISASSEMBLER_TOOL=$(BUILD_DIR)/a64_disassembler_tool.exe

$(ASSEMBLER_TOOL):
	@cd $(BUILD_DIR); $(MAKE) -s a64_assembler_tool.exe

$(DISASSEMBLER_TOOL):
	@cd $(BUILD_DIR); $(MAKE) -s a64_disassembler_tool.exe

opcode_test_c: opcode_gen.h opcode_gen.cc
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s a64_opcode_test.exe
	$(BUILD_DIR)/a64_opcode_test.exe


$(DIR)/symbolize_parity:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s a64_disassembler_tool.exe

	$(DISASSEMBLER_TOOL) $(TEST_INSTRUCTIONS) > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual_c.out $@.actual.out
	#
	$(DISASSEMBLER_TOOL) batch < TestData/a64_test.regular.dis > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py batch < TestData/a64_test.regular.dis  > $@.actual.out
	diff $@.actual_c.out $@.actual.out

$(DIR)/codegen_parity:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s a64_assembler_tool.exe
	@echo
	$(ASSEMBLER_TOOL) assemble TestData/exit.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble TestData/exit.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe
	@echo
	$(ASSEMBLER_TOOL) assemble TestData/hello.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble TestData/hello.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe
	@echo
	$(ASSEMBLER_TOOL) assemble TestData/fib.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble TestData/fib.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe

clean:
	rm -f $(DIR)/* $(DISASSEMBLER_TOOL) $(ASSEMBLER_TOOL)
