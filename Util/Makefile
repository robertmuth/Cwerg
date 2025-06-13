.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

tests: tests_py tests_c
	@echo "[OK Util]"

tests_py:  $(DIR)/parse_test


tests_c:  $(DIR)/parse_test_c handle_test bitvec_test handlevec_test mem_pool_test immutable_test

############################################################
# Python Port
############################################################

 $(DIR)/parse_test: parse_test.py
	@echo "[$@]"
	$(PYPY) ./parse_test.py lex < TestData/lines_lex.txt  > $@.actual_lex.out
	diff $@.actual_lex.out TestData/lines_lex.golden
	$(PYPY) ./parse_test.py num < TestData/lines_num.txt  > $@.actual_num.out
	diff $@.actual_num.out TestData/lines_num.golden
############################################################
# C++ Port
############################################################
BUILD_DIR=../build

 $(DIR)/parse_test_c:
	@echo "[$@]"
	@cd $(BUILD_DIR); $(MAKE) -s parse_test.exe
	$(BUILD_DIR)/parse_test.exe lex < TestData/lines_lex.txt  > $@.actual_lex.out
	diff $@.actual_lex.out TestData/lines_lex.golden
	$(BUILD_DIR)/parse_test.exe num < TestData/lines_num.txt  > $@.actual_num.out
	diff $@.actual_num.out TestData/lines_num.golden

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
	rm -f $(DIR)/*
