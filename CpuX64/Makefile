.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

TESTS = hello.asm

TEST_INSTRUCTIONS = "ff b5 b8 f9 ff ff" \
                    "6a 12" \
                    "48 8b 05 a7 40 7f 00" \
                    "48 89 b4 04 50 01 00 00" \
                    "48 89 84 24 f0 00 00 00" \
                    "f3 66 41 0f bd cc" \
                    "41 f7 b8 80 23 03 00" \
                    "48 83 7e 78 01" \
                    "f3 0f 11 0c c1" \
                    "c7 85 dc 00 00 00 00 00 70 c2" \
                    "48 8d 04 ad 00 00 00 00" \
                    "49 6b cd fc" \
                    "48 b8 00 00 00 00 00 00 01 f4" \
                    "0f b1 15 92 0e 02 00"

tests: $(DIR)/disassembler_test $(DIR)/symbolize_parity $(DIR)/codegen_parity $(TESTS:%.asm=$(DIR)/%.test) objdump_tests
	@echo "[OK CPUX64]"

hello-x64:
	gcc -static -Wl,-z,norelro -O2 hello.c -o hello-x64 

hello_barebones-x64:
	as hello_barebones.s -o $(DIR)/hello_barebones.o
	ld $(DIR)/hello_barebones.o --emit-relocs -o $@

objdump_tests:
	$(PYPY) ./opcode_test.py < TestData/objdump.dis


$(DIR)/disassembler_test:
	@echo "[$@]"
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual.out TestData/disassembler_test.golden

$(DIR)/%.test : TestData/%.asm
	echo "[integration $@]"
	$(PYPY)	./assembler_tool.py assemble $< $@.exe > $@.out
	$@.exe > $@.actual.out
	diff $@.actual.out $<.golden

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

opcode_gen_encodings.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_encodings >$@

opcode_gen_names.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_names >$@

opcode_gen_enum.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_enum >$@

opcode_gen_collisions.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_collisions >$@


GENERATED = opcode_gen.cc opcode_gen.h opcode_gen_encodings.h opcode_gen_names.h \
            opcode_gen_enum.h opcode_gen_collisions.h
############################################################
# C++ Port
############################################################
BUILD_DIR=../build

ASSEMBLER_TOOL=$(BUILD_DIR)/x64_assembler_tool.exe
DISASSEMBLER_TOOL=$(BUILD_DIR)/x64_disassembler_tool.exe

$(ASSEMBLER_TOOL): $(GENERATED)
	@cd $(BUILD_DIR); $(MAKE) -s x64_assembler_tool.exe

$(DISASSEMBLER_TOOL): $(GENERATED)
	@cd $(BUILD_DIR); $(MAKE) -s x64_disassembler_tool.exe



$(DIR)/symbolize_parity:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s x64_disassembler_tool.exe

	$(DISASSEMBLER_TOOL) $(TEST_INSTRUCTIONS) > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual_c.out $@.actual.out
	#
	$(DISASSEMBLER_TOOL) batch < TestData/x64_test.regular.dis > $@.actual_c.out
	$(PYPY) ./disassembler_tool.py batch < TestData/x64_test.regular.dis  > $@.actual.out
	diff $@.actual_c.out $@.actual.out

$(DIR)/codegen_parity:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s x64_assembler_tool.exe
	@echo
	$(ASSEMBLER_TOOL) assemble TestData/hello.asm $@_c.exe > $@_c.exe.out
	$(PYPY)	./assembler_tool.py assemble TestData/hello.asm $@.exe > $@.exe.out
	cmp -l  $@_c.exe $@.exe
	@echo


clean:
	rm -f $(DIR)/*
