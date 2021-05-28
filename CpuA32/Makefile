.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

TESTS = memaddr.asm exit.asm hello.asm fib.asm switch.asm


TEST_INSTRUCTIONS = eefdbbc0 e12fff31 924aa001 ebffdc62 e8bd87f0 ecbd8b08 08bd81f0 e1920f9f 015461fa e3c70102 0

tests: tests_py tests_c
	@echo "[OK CpuA32]"

tests_py: objdump_compat_test $(DIR)/disassembler_test $(DIR)/jit_test \
              $(DIR)/argv_test $(TESTS:%.asm=$(DIR)/%.test)

tests_c: $(DIR)/symbolize_parity build_test_c $(TESTS:%.asm=$(DIR)/%.test_c) $(DIR)/codegen_parity

tests_cross: jit_example_cross
############################################################
# Python Port
############################################################
$(DIR)/%.test : TestData/%.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble_raw $< $@.exe > $@.out
	$@.exe > $@.actual.out
	diff $@.actual.out $<.golden


$(DIR)/argv_test: TestData/argv.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble $< $@.exe > $@.out
	$@.exe argv1 argv2 arvg3 argv4 ... argn > $@.actual.out
	diff $@.actual.out $<.golden

objdump_compat_test:
	@echo "[$@]"
	$(PYPY) ./opcode_test.py TestData/arm_test.dis

$(DIR)/jit_test:
	@echo "[$@]"
	$(PYPY) ./jit.py > $@.actual.out
	diff $@.actual.out TestData/jit_test.golden


$(DIR)/disassembler_test:
	@echo "[$@]"
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual.out TestData/disassembler_test.golden

# dump opcode table
opcodes:
	$(PYPY) ./opcode_tab.py dist

############################################################
# C++ Port
############################################################
BUILD_DIR=../build

ASSEMBLER_TOOL=$(BUILD_DIR)/a32_assembler_tool.exe
DISASSEMBLER_TOOL=$(BUILD_DIR)/a32_disassembler_tool.exe

$(DISASSEMBLER_TOOL)::
	@cd $(BUILD_DIR); $(MAKE) -s a32_disassembler_tool.exe


$(DIR)/%.test_c : TestData/%.asm
	echo "[integration $@]"
	@cd $(BUILD_DIR); $(MAKE) -s a32_assembler_tool.exe
	$(ASSEMBLER_TOOL) assemble_raw $< $@.exe > $@.out
	chmod a+x $@.exe
	$@.exe > $@.actual_c.out
	diff $@.actual_c.out $<.golden


opcode_gen.cc: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_c <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

opcode_gen.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_h <$@ > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

build_test_c:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s  a32_assembler_tool.exe a32_jit_example.exe


$(DIR)/codegen_parity: $(ASSEMBLER_TOOL)
	@echo "[$@]"
	$(ASSEMBLER_TOOL) assemble_raw TestData/fib.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble_raw  TestData/fib.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe
	@echo
	$(ASSEMBLER_TOOL) assemble_raw TestData/switch.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble_raw  TestData/switch.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe
	@echo
	$(ASSEMBLER_TOOL) assemble TestData/nanojpeg.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble  TestData/nanojpeg.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe

$(DIR)/symbolize_parity:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s a32_disassembler_tool.exe
	#
	$(DISASSEMBLER_TOOL) $(TEST_INSTRUCTIONS) > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual_c.out $@.actual.out
	#
	$(DISASSEMBLER_TOOL) batch < TestData/arm_test.dis > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py batch < TestData/arm_test.dis  > $@.actual.out
	diff $@.actual_c.out $@.actual.out

############################################################
# Cross Compile
############################################################

CC_FLAGS_CROSS =  -static  -Wl,-z,norelro -marm -march=armv7ve $(CC_FLAGS) -DCWERG_DISABLE_UNWIND
A32_LIB_DIS = opcode_gen.cc disassembler.cc
UTIL_LITE_LIB = ../Util/assert.cc ../Util/parse.cc

jit_example_cross: $(A32_LIB_DIS) jit_example.cc
	arm-linux-gnueabihf-g++ $(CC_FLAGS_CROSS) $(UTIL_LITE_LIB) $(A32_LIB_DIS) jit_example.cc  -o $@.exe
	./$@.exe

############################################################
# Misc
############################################################

clean:
	rm -f  $(DIR)/*



