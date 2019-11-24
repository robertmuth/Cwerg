TESTS = Tests/*c

tests:
	./sym_tab.py $(TESTS)
	./type_tab.py $(TESTS)
	echo "OK"
