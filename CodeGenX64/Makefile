# no built-in rules please
.SUFFIXES:

DIR=build

$(info $(shell mkdir -p $(DIR)))

tests: tests_py tests_c
	@echo "[OK CodeGenX64]"

tests_py:  $(DIR)/isel_test $(DIR)/syscall.x64.asm.exe

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

clean:
	rm -f $(DIR)/*
