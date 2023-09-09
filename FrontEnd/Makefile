
DIR=build
QEMU=

$(info $(shell mkdir -p $(DIR)))

TESTS = macros.cw \
        types.cw \
        consts.cw \
        sexpr.cw \
        cast.cw \
		comment.cw \
        linked_list.cw \
        binary_tree.cw \
        sizeof.cw 

TESTS_PARSE = $(TESTS:%.cw=$(DIR)/%.cw.parse)
TESTS_SYMTAB = $(TESTS:%.cw=$(DIR)/%.cw.symtab)
TESTS_META = $(TESTS:%.cw=$(DIR)/%.cw.meta)
TESTS_EVAL = $(TESTS:%.cw=$(DIR)/%.cw.eval)

TESTS_PP = $(TESTS:%.cw=$(DIR)/%.cw.pp) 

tests_py: clean $(TESTS_META) $(TESTS_EVAL) $(TESTS_PP) \
                tests_lang_x64  \
                tests_lib_x64 tests_lib_a64 \
				tests_emit


tests_all_py: $(TESTS_PARSE) $(TESTS_SYMTAB) $(TESTS_META) $(TESTS_EVAL) $(TESTS_PP)

tests_pp_py: $(TESTS_PP)

STD_LIB_WITH_ARGV_X64 = ../StdLib/startup.x64.asm ../StdLib/syscall.x64.asm ../StdLib/std_lib.64.asm
STD_LIB_WITH_ARGV_A64 = ../StdLib/startup.a64.asm ../StdLib/syscall.a64.asm ../StdLib/std_lib.64.asm
STD_LIB_WITH_ARGV_A32 = ../StdLib/startup.a32.asm ../StdLib/syscall.a32.asm ../StdLib/std_lib.32.asm

# test language features X64
tests_lang_x64: \
    $(DIR)/array_test.lang.x64.exe \
    $(DIR)/assign_test.lang.x64.exe \
    $(DIR)/enum_test.lang.x64.exe \
    $(DIR)/rec_test.lang.x64.exe \
    $(DIR)/expr_sint_test.lang.x64.exe \
    $(DIR)/expr_uint_test.lang.x64.exe \
    $(DIR)/defer_test.lang.x64.exe \
    $(DIR)/sum_untagged_test.lang.x64.exe \
    $(DIR)/sum_tagged_test.lang.x64.exe 

# test language features A64
tests_lang_a64: \
    $(DIR)/array_test.lang.a64.exe \
    $(DIR)/assign_test.lang.a64.exe \
    $(DIR)/enum_test.lang.a64.exe \
    $(DIR)/rec_test.lang.a64.exe \
    $(DIR)/defer_test.lang.a64.exe \
    $(DIR)/sum_untagged_test.lang.a64.exe \
    $(DIR)/sum_tagged_test.lang.a64.exe \
    $(DIR)/expr_uint_test.lang.a64.exe \
    $(DIR)/expr_sint_test.lang.a64.exe

# test language features A32
# TODO: this does not work yet
tests_lang_a32: \
    $(DIR)/array_test.lang.a32.exe \
    $(DIR)/assign_test.lang.a64.exe \
    $(DIR)/enum_test.lang.a64.exe \
    $(DIR)/rec_test.lang.a64.exe \
    $(DIR)/defer_test.lang.a64.exe \
    $(DIR)/sum_untagged_test.lang.a64.exe \
    $(DIR)/sum_tagged_test.lang.a64.exe \
    $(DIR)/expr_uint_test.lang.a64.exe \
    $(DIR)/expr_sint_test.lang.a64.exe

tests_lib_x64: \
	$(DIR)/string_test.lib.x64.exe \
    $(DIR)/trig_test.lib.x64.exe \
    $(DIR)/checksum_test.lib.x64.exe 

tests_lib_a64: \
	$(DIR)/string_test.lib.a64.exe \
    $(DIR)/trig_test.lib.a64.exe \
    $(DIR)/checksum_test.lib.a64.exe 

tests_emit: \
    $(DIR)/hello_world.run.x64.exe \
    $(DIR)/hello_world.run.a64.exe \
    $(DIR)/fizzbuzz.run.x64.exe \
    $(DIR)/fizzbuzz.run.a64.exe \
    $(DIR)/sieve.run.x64.exe \
    $(DIR)/sieve.run.a64.exe \
    $(DIR)/polymorphic.run.x64.exe \
    $(DIR)/polymorphic.run.a64.exe \
    $(DIR)/heapsort.run.x64.exe \
    $(DIR)/heapsort.run.a64.exe \
	$(DIR)/print_argv.x64.test \
    $(DIR)/print_argv.a64.test \
    $(DIR)/wordcount.x64.test \
    $(DIR)/wordcount.a64.test 

$(DIR)/%.cw.parse: TestData/%.cw
	@echo "[parse $@]"
	cat $(BUILTINS) $< | ./parse.py 

$(DIR)/%.cw.meta: TestData/%.cw
	@echo "[typify $@]"
	./typify.py $< 

$(DIR)/%.cw.eval: TestData/%.cw
	@echo "[eval $@]"
	./eval.py $< 

$(DIR)/%.cw.symtab: TestData/%.cw
	@echo "[symbolize $@]"
	./symbolize.py $< 

$(DIR)/%.cw.pp: TestData/%.cw
	@echo "[prettyprint $@]"
	cat $(BUILTINS) $< | ./pp.py >$@.tmp
	./pp.py < $@.tmp >$@
	diff $@.tmp $@

## Language Tests

$(DIR)/%.lang.x64.exe: LangTest/%.cw
	@echo "[lang $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.lang.a64.exe: LangTest/%.cw
	@echo "[lang $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../CodeGenA64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.lang.a32.exe: LangTest/%.cw
	@echo "[lang $@]"
	./emit_ir.py Lib/os.cw  Lib/builtin.cw Lib/test.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A32) $@.asm | $(PYPY) ../CodeGenA32/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

## Library Tests

$(DIR)/%.lib.x64.exe: Lib/%.cw
	@echo "[lib $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.lib.a64.exe: Lib/%.cw
	@echo "[lib $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../CodeGenA64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.lib.a32.exe: Lib/%.cw
	@echo "[lib $@]"
	./emit_ir.py Lib/os.cw  Lib/builtin.cw Lib/test.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A32) $@.asm | $(PYPY) ../CodeGenA32/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

## Misc Tests

$(DIR)/%.run.x64.exe: TestData/%.cw
	@echo "[run $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.run.a64.exe: TestData/%.cw
	@echo "[run $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../CodeGenA64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

## Compile only Tests

$(DIR)/%.compile.x64.exe: TestData/%.cw
	@echo "[run $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out

$(DIR)/%.compile.a64.exe: TestData/%.cw
	@echo "[run $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../CodeGenA64/codegen.py -mode binary - $@ > $@.out

$(DIR)/wordcount.x64.test: build/wordcount.compile.x64.exe
	echo "hello world\na b c d " | ${QEMU} $<

$(DIR)/wordcount.a64.test: build/wordcount.compile.a64.exe
	echo "hello world\na b c d " | ${QEMU} $<


$(DIR)/print_argv.x64.test: build/print_argv.compile.x64.exe
	${QEMU} $< arg1 arg2 argc3

$(DIR)/print_argv.a64.test: build/print_argv.compile.a64.exe
	${QEMU} $< arg1 arg2 argc3


## Manual tests

$(DIR)/asciiquarium.x64.exe: TestData/asciiquarium.cw
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 128 48

$(DIR)/asciiquarium.a64.exe: TestData/asciiquarium.cw
	./emit_ir.py  $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../CodeGenA64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 128 48

clean:
	@rm -f $(DIR)/* 


reformat:
	for f in TestData/*.cw ; do \
		echo $$f ; ./pp.py < $$f  >$$f.pp; mv $$f.pp $$f ; \
	done

reformat_lib:
	for f in Lib/*.cw ; do \
		echo $$f ; ./pp.py < $$f  >$$f.pp; mv $$f.pp $$f ; \
	done