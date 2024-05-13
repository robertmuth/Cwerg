
DIR=build
QEMU=


TESTS = $(wildcard TestData/*cw)
LANG_TESTS = $(wildcard LangTest/*cw)
LIB_TESTS = $(wildcard Lib/*_test.cw)

tests_py: clean \
          tests_meta_py \
          tests_eval_py \
		  tests_pp_py \
          tests_lang_x64 \
          tests_lang_a64 \
          tests_lib_x64 \
          tests_lib_a64 \
          tests_emit_x64 \
          tests_emit_a64

tests_parse_py: $(TESTS:%.cw=$(DIR)/%.cw.parse)
tests_meta_py: $(TESTS:%.cw=$(DIR)/%.cw.meta)
tests_eval_py: $(TESTS:%.cw=$(DIR)/%.cw.eval)
tests_symtab_py: $(TESTS:%.cw=$(DIR)/%.cw.symtab)
tests_pp_py: $(TESTS:%.cw=$(DIR)/%.cw.pp)



tests_all_py: tests_parse_py tests_symtab_py tests_meta_py tests_eval_py tests_pp_py

STD_LIB_WITH_ARGV_X64 = ../StdLib/startup.x64.asm ../StdLib/syscall.x64.asm ../StdLib/std_lib.64.asm
STD_LIB_WITH_ARGV_A64 = ../StdLib/startup.a64.asm ../StdLib/syscall.a64.asm ../StdLib/std_lib.64.asm
STD_LIB_WITH_ARGV_A32 = ../StdLib/startup.a32.asm ../StdLib/syscall.a32.asm ../StdLib/std_lib.32.asm

# test language
tests_lang_x64: $(LANG_TESTS:%.cw=$(DIR)/%.x64.exe)
tests_lib_x64: $(LIB_TESTS:%.cw=$(DIR)/%.x64.exe)
#
tests_lang_a64: $(LANG_TESTS:%.cw=$(DIR)/%.a64.exe)
tests_lib_a64: $(LIB_TESTS:%.cw=$(DIR)/%.a64.exe)

# TODO: broken
tests_lang_a32: $(LANG_TESTS:%.cw=$(DIR)/%.a32.exe)
tests_lang_a32: $(LIB_TESTS:%.cw=$(DIR)/%.a32.exe)


tests_emit_x64: \
    $(DIR)/hash_test.run.x64.exe \
    $(DIR)/sort.run.x64.exe \
    $(DIR)/linked_list.run.x64.exe \
    $(DIR)/hello_world.run.x64.exe \
    $(DIR)/fizzbuzz.run.x64.exe \
    $(DIR)/sieve.run.x64.exe \
    $(DIR)/heapsort.run.x64.exe \
	$(DIR)/fibonacci.run.x64.exe \
	$(DIR)/print_argv.x64.test \
    $(DIR)/wordcount.x64.test

tests_emit_a64: \
    $(DIR)/hash_test.run.x64.exe \
    $(DIR)/sort.run.a64.exe \
    $(DIR)/linked_list.run.a64.exe \
    $(DIR)/hello_world.run.a64.exe \
    $(DIR)/fizzbuzz.run.a64.exe \
    $(DIR)/sieve.run.a64.exe \
    $(DIR)/heapsort.run.a64.exe \
	$(DIR)/fibonacci.run.x64.exe \
    $(DIR)/print_argv.a64.test \
    $(DIR)/wordcount.a64.test

$(DIR)/%.cw.parse: %.cw
	@echo "[parse $@]"
	./parse_sexpr.py $<

$(DIR)/%.cw.meta: %.cw
	@echo "[typify $@]"
	./typify.py $<

$(DIR)/%.cw.eval: %.cw
	@echo "[eval $@]"
	./eval.py $<

$(DIR)/%.cw.symtab: %.cw
	@echo "[symbolize $@]"
	./symbolize.py $<

$(DIR)/%.cw.pp: %.cw
	@echo "[prettyprint $@]"
	./pp_sexpr.py $< >$@.tmp.cw
	./pp_sexpr.py $@.tmp.cw >$@
	diff $@.tmp.cw $@

## Exe Tests

$(DIR)/%.x64.exe: %.cw
	@echo "[lang $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.a64.exe: %.cw
	@echo "[lang $@]"
	./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../CodeGenA64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

# TODO: broken
$(DIR)/%.a32.exe: %.cw
	@echo "[lang $@]"
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
	@echo cleaning and setting up build dirs
	@rm -rf $(DIR)/*
	@mkdir -p  $(DIR)
	@mkdir -p  $(DIR)/Lib
	@mkdir -p  $(DIR)/TestData
	@mkdir -p  $(DIR)/LangTest

pp_test:
	./pp.py TestData/*.cw  Lib/*.cw  LangTest/*.cw

concrete_test:
	for cw in LangTest/*.cw ; do \
      echo "\n" $$cw ; \
	  ./pp.py $$cw > $$cw.concrete ; \
      ./parse.py < $$cw.concrete ; \
      rm  $$cw.concrete ; \
    done

reformat:
	for f in TestData/*.cw ; do \
		echo $$f ; ./pp_sexpr.py < $$f  >$$f.pp; mv $$f.pp $$f ; \
	done

reformat_lib:
	for f in Lib/*.cw ; do \
		echo $$f ; ./pp_sexpr.py < $$f  >$$f.pp; mv $$f.pp $$f ; \
	done