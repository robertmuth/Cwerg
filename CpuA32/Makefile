
.SUFFIXES:

TESTS = TestData/memaddr.asm \
    TestData/exit.asm \
	TestData/hello.asm \
	TestData/fib.asm \
	TestData/switch.asm

.PHONY: $(TESTS)

TEST_INSTRUCTIONS = eefdbbc0 e12fff31 924aa001 ebffdc62 e8bd87f0 ecbd8b08 08bd81f0 e1920f9f 015461fa 0

tests: tests_py tests_c
	@echo


tests_py: objdump_compat_test disassembler_test disassembler_test jit_test \
          $(TESTS:.asm=.test)

tests_c: objdump_compat_test_c disassembler_test_c build_test_c \
         $(TESTS:.asm=.test_c) codegen_parity

tests_cross: jit_example_cross
############################################################
# Python Port
############################################################
%.test : %.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble_raw $< $@.exe > $<.out
	$@.exe > $<.actual.out
	diff $<.actual.out $<.golden


objdump_compat_test:
	@echo "[$@]"
	$(PYPY) ./opcode_test.py TestData/arm_test.dis

jit_test:
	@echo "[$@]"
	$(PYPY) ./jit.py > $@.actual.out
	diff $@.actual.out TestData/$@.golden


disassembler_test:
	@echo "[$@]"
	$(PYPY) ./disassembler.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual.out TestData/$@.golden

# dump opcode table
opcodes:
	$(PYPY) ./opcode_tab.py dist

############################################################
# C++ Port
############################################################
BUILD_DIR=../build

ASSEMBLER_TOOL=$(BUILD_DIR)/a32_assembler_tool.exe
DISASSEMBLER_TOOL=$(BUILD_DIR)/a32_disassembler_tool.exe

$(DISSEMBLER_TOOL)::
	@cd $(BUILD_DIR); $(MAKE) -s a32_disassembler_tool.exe


%.test_c : %.asm
	echo "[integration $@]"
	@cd $(BUILD_DIR); $(MAKE) -s a32_assembler_tool.exe
	$(ASSEMBLER_TOOL) assemble_raw $< $@.exe > $<.out
	chmod a+x $@.exe
	$@.exe > $<.actual_c.out
	diff $<.actual_c.out $<.golden


opcode_gen.cc: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_c <$@ > $@.tmp
	@mv $@.tmp $@

opcode_gen.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_h <$@ > $@.tmp
	@mv $@.tmp $@

objdump_compat_test_c: TestData/arm_test.dis opcode_gen.h opcode_gen.cc
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s a32_opcode_test.exe
	$(BUILD_DIR)/a32_opcode_test.exe TestData/arm_test.dis

disassembler_test_c: opcode_gen.h opcode_gen.cc $(DISASSEMBLER_TOOL)
	@echo "[$@]"
	$(DISASSEMBLER_TOOL) disass $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual.out TestData/$@.golden

build_test_c:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s  a32_assembler_tool.exe a32_jit_example.exe


codegen_parity: $(ASSEMBLER_TOOL)
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
	rm -f  TestData/*.out TestData/*.exe *.exe *.out



