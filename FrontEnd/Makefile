
DIR=build
QEMU=

$(info $(shell mkdir -p $(DIR)))

TESTS = macros.cw \
        array.cw \
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

tests_py: clean $(TESTS_META) $(TESTS_EVAL) $(TESTS_PP) \
    $(DIR)/hello_world.x64.exe \
    $(DIR)/fizzbuzz.x64.exe \
	$(DIR)/heapsort.exe \
	$(DIR)/sieve.exe 

tests_all_py: $(TESTS_PARSE) $(TESTS_SYMTAB) $(TESTS_META) $(TESTS_EVAL) $(TESTS_PP)

tests_pp_py: $(TESTS_PP)

BUILTINS = TestData/builtin.cw 

$(DIR)/%.cw.parse: TestData/%.cw
	@echo "[parse $@]"
	cat $(BUILTINS) $< | ./parse.py 

$(DIR)/%.cw.meta: TestData/%.cw
	@echo "[typify $@]"
	cat $(BUILTINS) $< |./typify.py 

$(DIR)/%.cw.eval: TestData/%.cw
	@echo "[eval $@]"
	cat $(BUILTINS) $< |./eval.py 

$(DIR)/%.cw.symtab: TestData/%.cw
	@echo "[symbolize $@]"
	cat $(BUILTINS) $< |./symbolize.py 

$(DIR)/%.cw.pp: TestData/%.cw
	@echo "[prettyprint $@]"
	cat $(BUILTINS) $< | ./pp.py >$@.tmp
	./pp.py < $@.tmp >$@
	diff $@.tmp $@

STD_LIB_WITH_ARGV = ../StdLib/startup.x64.asm ../StdLib/syscall.x64.asm ../StdLib/std_lib.64.asm


$(DIR)/hello_world.x64.exe: TestData/hello_world.cw
	cat $< |  $(PYPY)  ./emit_ir.py > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 

$(DIR)/sieve.exe: TestData/sieve.cw
	cat $< |  $(PYPY)  ./emit_ir.py > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 

$(DIR)/heapsort.exe: TestData/heapsort.cw
	cat $< |  $(PYPY)  ./emit_ir.py > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 

$(DIR)/print_argv.x64.exe: TestData/print_argv.cw
	cat TestData/builtin.cw $< |  $(PYPY)  ./emit_ir.py > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@  arg1 arg2 argc3

$(DIR)/fizzbuzz.x64.exe: TestData/fizzbuzz.cw
	cat $< |  $(PYPY)  ./emit_ir.py > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@  arg1 arg2 argc3

clean:
	@rm -f $(DIR)/* 
