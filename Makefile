TESTS = Tests/*c

tests: 
	./test_harness.py $(TESTS)

meta_tests:
	./meta.py $(TESTS)

