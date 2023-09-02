
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
        import.cw \
        import2.cw \
        sizeof.cw 

TESTS_PARSE = $(TESTS:%.cw=$(DIR)/%.cw.parse)
TESTS_SYMTAB = $(TESTS:%.cw=$(DIR)/%.cw.symtab)
TESTS_META = $(TESTS:%.cw=$(DIR)/%.cw.meta)
TESTS_EVAL = $(TESTS:%.cw=$(DIR)/%.cw.eval)

TESTS_PP = $(TESTS:%.cw=$(DIR)/%.cw.pp) 

tests_py: clean $(TESTS_META) $(TESTS_EVAL) $(TESTS_PP) tests_lang_x64 tests_emit


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

tests_emit: \
    $(DIR)/wordcount.x64.exe \
    $(DIR)/hello_world.x64.exe \
    $(DIR)/fizzbuzz.x64.exe \
    $(DIR)/heapsort.x64.exe \
    $(DIR)/print_argv.x64.exe \
    $(DIR)/sieve.x64.exe \
    $(DIR)/polymorphic.x64.exe \
    $(DIR)/string.x64.exe \
    $(DIR)/trig_test.x64.exe \
    $(DIR)/checksum_test.x64.exe

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


$(DIR)/%.lang.x64.exe: LangTest/%.cw
	@echo "[lang $@]"
	./emit_ir.py Lib/builtin.cw Lib/test.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.lang.a64.exe: LangTest/%.cw
	@echo "[lang $@]"
	./emit_ir.py Lib/builtin.cw Lib/test.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../CodeGenA64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.lang.a32.exe: LangTest/%.cw
	@echo "[lang $@]"
	./emit_ir.py Lib/builtin.cw Lib/test.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A32) $@.asm | $(PYPY) ../CodeGenA32/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/hello_world.x64.exe: TestData/hello_world.cw
	./emit_ir.py Lib/builtin.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 

$(DIR)/sieve.x64.exe: TestData/sieve.cw
	./emit_ir.py Lib/builtin.cw Lib/test.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 

$(DIR)/heapsort.x64.exe: TestData/heapsort.cw
	./emit_ir.py Lib/builtin.cw Lib/random.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 

$(DIR)/print_argv.x64.exe: TestData/print_argv.cw
	./emit_ir.py Lib/builtin.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@  arg1 arg2 argc3

$(DIR)/fizzbuzz.x64.exe: TestData/fizzbuzz.cw
	./emit_ir.py Lib/builtin.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@  


$(DIR)/polymorphic.x64.exe: TestData/polymorphic.cw
	./emit_ir.py Lib/builtin.cw Lib/test.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/wordcount.x64.exe: TestData/wordcount.cw
	cat Lib/os.cw $< | ./typify.py


$(DIR)/string.x64.exe: Lib/string_test.cw
	./emit_ir.py Lib/builtin.cw Lib/test.cw Lib/string.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

## Lib Tests

$(DIR)/trig_test.x64.exe: Lib/trig_test.cw
	./emit_ir.py  Lib/builtin.cw  Lib/test.cw Lib/math.cw Lib/trig.cw  $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/checksum_test.x64.exe: Lib/checksum_test.cw
	./emit_ir.py  Lib/builtin.cw  Lib/test.cw Lib/checksum.cw  $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

## Manual tests

$(DIR)/asciiquarium.x64.exe: TestData/asciiquarium.cw
	./emit_ir.py Lib/builtin.cw  Lib/random.cw Lib/ansi.cw Lib/test.cw $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 128 48

$(DIR)/asciiquarium.a64.exe: TestData/asciiquarium.cw
	./emit_ir.py Lib/builtin.cw  Lib/random.cw Lib/ansi.cw Lib/test.cw $< > $@.asm
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