.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

tests: objdump_tests
	@echo "[OK CPUX64]"

hello-x64:
	gcc -static -Wl,-z,norelro -O2 hello.c -o hello-x64 

hello_barebones-x64:
	as hello_barebones.s -o $(DIR)/hello_barebones.o
	ld $(DIR)/hello_barebones.o -o $@

objdump_tests:
	$(PYPY) ./opcode_test.py < TestData/objdump.dis


clean:
	rm -f $(DIR)/*
