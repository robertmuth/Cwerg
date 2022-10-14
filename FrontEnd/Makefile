
DIR=build

$(info $(shell mkdir -p $(DIR)))

TESTS = print_argv.cw types.cw consts.cw sexpr.cw

TESTS_PARSE = $(TESTS:%.cw=$(DIR)/%.cw.parse)
TESTS_META = $(TESTS:%.cw=$(DIR)/%.cw.meta)

tests_py: $(TESTS_PARSE) $(TESTS_META)

$(DIR)/%.cw.parse: TestData/%.cw
	@echo "[parse $@]"
	./cwast.py < $<

$(DIR)/%.cw.meta: TestData/%.cw
	@echo "[parse $@]"
	./meta.py < $<

clean:
	@rm -f $(DIR)/* 
