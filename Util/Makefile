
tests: tests_py tests_c
	@echo

tests_py:  parse_test


tests_c: parse_test_c handle_test bitvec_test handlevec_test mem_pool_test immutable_test


############################################################
# Python Port
############################################################

parse_test: parse_test.py
	@echo "[$@]"
	$(PYPY) ./parse_test.py < TestData/lines.txt  > $@.actual.out
	diff $@.actual.out TestData/lines.golden

############################################################
# C++ Port
############################################################
BUILD_DIR=../build

parse_test_c:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s parse_test.exe
	$(BUILD_DIR)/parse_test.exe < TestData/lines.txt  > $@.actual.out
	diff $@.actual.out TestData/lines.golden

handle_test:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s handle_test.exe
	$(BUILD_DIR)/handle_test.exe

bitvec_test:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s bitvec_test.exe
	$(BUILD_DIR)/bitvec_test.exe

handlevec_test:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s handlevec_test.exe
	$(BUILD_DIR)/handlevec_test.exe

mem_pool_test:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s mem_pool_test.exe
	$(BUILD_DIR)/mem_pool_test.exe

immutable_test:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s immutable_test.exe
	$(BUILD_DIR)/immutable_test.exe

clean:
	rm -f *.out

