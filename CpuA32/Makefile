.SUFFIXES:  # no built-in rules
DIR=build
QEMU_A32 = qemu-arm-static

$(info $(shell mkdir -p $(DIR)))

TESTS = memaddr.asm exit.asm hello.asm fib.asm switch.asm


TEST_INSTRUCTIONS = eefdbbc0 e12fff31 924aa001 ebffdc62 e8bd87f0 ecbd8b08 08bd81f0 e1920f9f 015461fa e3c70102 0

tests: tests_py tests_c
	@echo "[OK CpuA32]"

tests_py: objdump_compat_test $(DIR)/disassembler_test \
              $(DIR)/argv_test $(TESTS:%.asm=$(DIR)/%.test)

tests_c: $(DIR)/symbolize_parity $(TESTS:%.asm=$(DIR)/%.test_c) $(DIR)/codegen_parity

############################################################
# Python Port
############################################################
$(DIR)/%.test : TestData/%.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble $< $@.exe > $@.out
	$@.exe > $@.actual.out
	diff $@.actual.out $<.golden


$(DIR)/argv_test: TestData/argv.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble $< $@.exe > $@.out
	$(QEMU_A32) $@.exe argv1 argv2 arvg3 argv4 ... argn > $@.actual.out
	diff $@.actual.out $<.golden

objdump_compat_test:
	@echo "[$@]"
	$(PYPY) ./opcode_test.py TestData/arm_test.dis


$(DIR)/disassembler_test:
	@echo "[$@]"
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual.out TestData/disassembler_test.golden

# dump opcode table
opcodes:
	$(PYPY) ./opcode_tab.py dist

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

ASSEMBLER_TOOL=$(BUILD_DIR)/a32_assembler_tool.exe
DISASSEMBLER_TOOL=$(BUILD_DIR)/a32_disassembler_tool.exe

$(DISASSEMBLER_TOOL):
	@cd $(BUILD_DIR); $(MAKE) -s a32_disassembler_tool.exe

$(ASSEMBLER_TOOL):
	@cd $(BUILD_DIR); $(MAKE) -s a32_assembler_tool.exe

$(DIR)/%.test_c : TestData/%.asm $(ASSEMBLER_TOOL)
	echo "[integration $@]"
	$(ASSEMBLER_TOOL) assemble $< $@.exe > $@.out
	chmod a+x $@.exe
	$(QEMU_A32) $@.exe > $@.actual_c.out
	diff $@.actual_c.out $<.golden

$(DIR)/codegen_parity: $(ASSEMBLER_TOOL)
	@echo "[$@]"
	$(ASSEMBLER_TOOL) assemble TestData/fib.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble TestData/fib.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe
	@echo
	$(ASSEMBLER_TOOL) assemble TestData/switch.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble TestData/switch.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe
	@echo
	$(ASSEMBLER_TOOL) assemble TestData/nanojpeg.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble TestData/nanojpeg.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe

$(DIR)/symbolize_parity: $(DISASSEMBLER_TOOL)
	@echo "[$@]"
	$(DISASSEMBLER_TOOL) $(TEST_INSTRUCTIONS) > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual_c.out $@.actual.out
	#
	$(DISASSEMBLER_TOOL) batch < TestData/arm_test.dis > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py batch < TestData/arm_test.dis  > $@.actual.out
	diff $@.actual_c.out $@.actual.out

############################################################
# Misc
############################################################

clean:
	rm -f  $(DIR)/* $(DISASSEMBLER_TOOL) $(ASSEMBLER_TOOL)



