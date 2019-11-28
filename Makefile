TESTS = Tests/*c

tests: 
	./test_harness.py $(TESTS)

sym_tests:
	./sym_tab.py $(TESTS)

type_tests:
	./type_tab.py $(TESTS)
