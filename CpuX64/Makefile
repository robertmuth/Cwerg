.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))


TEST_INSTRUCTIONS = ff b5 b8 f9 ff ff,  6a 12,  48 8b 05 a7 40 7f 00 ,  48 89 b4 04 50 01 00 00,  48 89 84 24 f0 00 00 00


tests: objdump_tests $(DIR)/disassembler_test
	@echo "[OK CPUX64]"

hello-x64:
	gcc -static -Wl,-z,norelro -O2 hello.c -o hello-x64 

hello_barebones-x64:
	as hello_barebones.s -o $(DIR)/hello_barebones.o
	ld $(DIR)/hello_barebones.o -o $@

objdump_tests:
	$(PYPY) ./opcode_test.py < TestData/objdump.dis


$(DIR)/disassembler_test:
	@echo "[$@]"
	$(PYPY) ./disassembler_tool.py $(TEST_INSTRUCTIONS) > $@.actual.out
	diff $@.actual.out TestData/disassembler_test.golden

clean:
	rm -f $(DIR)/*
