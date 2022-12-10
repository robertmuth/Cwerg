
DIR=build

$(info $(shell mkdir -p $(DIR)))

TESTS = array.cw \
        print_argv.cw \
        types.cw \
        consts.cw \
        sexpr.cw \
        sum_type.cw \
        cast.cw \
        wordcount.cw \
        linked_list.cw \
        binary_tree.cw \
        import.cw \
        import2.cw \
        sizeof.cw

TESTS_PARSE = $(TESTS:%.cw=$(DIR)/%.cw.parse)
TESTS_SYMTAB = $(TESTS:%.cw=$(DIR)/%.cw.symtab)
TESTS_META = $(TESTS:%.cw=$(DIR)/%.cw.meta)
TESTS_EVAL = $(TESTS:%.cw=$(DIR)/%.cw.eval)

TESTS_PP = $(TESTS:%.cw=$(DIR)/%.cw.pp)

tests_py: $(TESTS_META) $(TESTS_EVAL) $(TESTS_PP)
tests_all_py: $(TESTS_PARSE) $(TESTS_SYMTAB) $(TESTS_META) $(TESTS_EVAL) $(TESTS_PP)

BUILTINS = TestData/builtin.cw 

$(DIR)/%.cw.parse: TestData/%.cw
	@echo "[parse $@]"
	cat $(BUILTINS) $< | ./cwast.py 

$(DIR)/%.cw.meta: TestData/%.cw
	@echo "[meta $@]"
	cat $(BUILTINS) $< |./meta.py 

$(DIR)/%.cw.eval: TestData/%.cw
	@echo "[eval $@]"
	cat $(BUILTINS) $< |./eval.py 

$(DIR)/%.cw.symtab: TestData/%.cw
	@echo "[symtab $@]"
	cat $(BUILTINS) $< |./symtab.py 

$(DIR)/%.cw.pp: TestData/%.cw
	@echo "[prettyprint $@]"
	./pp.py < $< >$@.tmp
	./pp.py < $@.tmp >$@
	diff $@.tmp $@

clean:
	@rm -f $(DIR)/* 
