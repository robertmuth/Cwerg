
.SUFFIXES:


tests: tests_py tests_c
	@echo


tests_py: objdump_compat_test


tests_c:

objdump_compat_test:
	@echo "[$@]"
	$(PYPY) ./opcode_test.py TestData/a64_test.regular.dis


clean:
