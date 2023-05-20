
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

tests_py: clean $(TESTS_META) $(TESTS_EVAL) $(TESTS_PP) test_emit


tests_all_py: $(TESTS_PARSE) $(TESTS_SYMTAB) $(TESTS_META) $(TESTS_EVAL) $(TESTS_PP)

tests_pp_py: $(TESTS_PP)

test_emit: \
    $(DIR)/hello_world.x64.exe \
    $(DIR)/fizzbuzz.x64.exe \
	$(DIR)/heapsort.x64.exe \
	$(DIR)/print_argv.x64.exe \
	$(DIR)/sieve.x64.exe \
	$(DIR)/defer.x64.exe \
	$(DIR)/rec.x64.exe \
	$(DIR)/string.x64.exe \
    $(DIR)/polymorphic.x64.exe

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
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 

$(DIR)/sieve.x64.exe: TestData/sieve.cw
	./emit_ir.py TestData/mod_builtin.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 

$(DIR)/heapsort.x64.exe: TestData/heapsort.cw
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 

$(DIR)/print_argv.x64.exe: TestData/print_argv.cw
	./emit_ir.py TestData/mod_builtin.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@  arg1 arg2 argc3

$(DIR)/fizzbuzz.x64.exe: TestData/fizzbuzz.cw
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@  


$(DIR)/defer.x64.exe: TestData/defer.cw
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/rec.x64.exe: TestData/rec.cw
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/string.x64.exe: TestData/string.cw
	./emit_ir.py TestData/mod_builtin.cw TestData/mod_test.cw TestData/mod_string.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/polymorphic.x64.exe: TestData/polymorphic.cw
	./emit_ir.py TestData/mod_builtin.cw TestData/mod_test.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

clean:
	@rm -f $(DIR)/* 
