
DIR=build

$(info $(shell mkdir -p $(DIR)))

TESTS = array.cw print_argv.cw types.cw consts.cw sexpr.cw sum_type.cw cast.cw

TESTS_PARSE = $(TESTS:%.cw=$(DIR)/%.cw.parse)
TESTS_SYMTAB = $(TESTS:%.cw=$(DIR)/%.cw.symtab)
TESTS_META = $(TESTS:%.cw=$(DIR)/%.cw.meta)
TESTS_PP = $(TESTS:%.cw=$(DIR)/%.cw.pp)

tests_py: $(TESTS_PARSE) $(TESTS_SYMTAB) $(TESTS_META) $(TESTS_PP)

$(DIR)/%.cw.parse: TestData/%.cw
	@echo "[parse $@]"
	./cwast.py < $<

$(DIR)/%.cw.meta: TestData/%.cw
	@echo "[parse $@]"
	./meta.py < $<

$(DIR)/%.cw.symtab: TestData/%.cw
	@echo "[parse $@]"
	./symtab.py < $<

$(DIR)/%.cw.pp: TestData/%.cw
	@echo "[parse $@]"
	./pp.py < $<

clean:
	@rm -f $(DIR)/* 
