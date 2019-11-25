TESTS = Tests/*c

tests: sym_tests type_tests
	#./sym_tab.py $(TESTS)
	#./type_tab.py $(TESTS)
	echo "OK"

sym_tests:
	./sym_tab.py $(TESTS)

type_tests:
	./type_tab.py $(TESTS)
