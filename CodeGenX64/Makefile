# no built-in rules please
.SUFFIXES:

DIR=build
QEMU=

$(info $(shell mkdir -p $(DIR)))

STD_LIB = ../StdLib/syscall.x64.asm ../StdLib/std_lib.64.asm

tests: tests_py tests_c
	@echo "[OK CodeGenX64]"

tests_py:  $(DIR)/isel_test $(DIR)/syscall.x64.asm.exe $(DIR)/cli.x64.asm.exe

tests_c:


$(DIR)/isel_test:
	@echo "[integration $@]"
	$(PYPY) ./isel_tester.py < TestData/codegen_test.asm  > $@.actual.out
	diff $@.actual.out TestData/codegen_test.asm.golden

$(DIR)/syscall.x64.asm.exe: TestData/syscall.x64.asm
	@echo "[integration $@]"
	$(PYPY) ./codegen.py -mode binary $<  $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/queens.64.asm.s.exe: ../TestData/queens.64.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py -mode binary -add_startup_code - $@
	${QEMU} $@ > $@.actual.out
	diff $@.actual.out $<.golden

$(DIR)/cli.x64.asm.exe: TestData/cli.x64.asm
	@echo "[integration $@]"
	cat $(STD_LIB) $< | $(PYPY) ./codegen.py -mode binary -add_startup_code - $@ > $@.out
	${QEMU} $@ 1 2 3 aa bbb ccc > $@.actual.out
	diff $@.actual.out $<.golden


clean:
	rm -f $(DIR)/*
