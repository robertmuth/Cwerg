
DIR := build
QEMU :=

TEST_SOURCES := $(wildcard TestData/*.cw)
TEST_SOURCES_NO_GENERIC :=  $(filter-out $(wildcard TestData/*gen.cw), $(wildcard TestData/*.cws))

LANG_TESTS := $(wildcard LangTest/*_test.cw)
LANG_SOURCES := $(wildcard LangTest/*.cw)

LIB_TESTS := $(wildcard Lib/*_test.cw)
LIB_SOURCES :=  $(wildcard Lib/*.cw)
LIB_SOURCES_NO_GENERIC := $(filter-out Lib/builtin.cw $(wildcard Lib/*gen.cw), $(wildcard Lib/*.cw))

TEST_TESTS := \
	TestData/binary_tree_test.cw \
	TestData/fibonacci.cw \
    TestData/fizzbuzz.cw \
    TestData/hello_world.cw \
    TestData/nqueens.cw

# excludes 64bit tests
TESTS_A32 := \
    LangTest/consts_test.cw \
	LangTest/array_test.cw \
    LangTest/cast_test.cw \
    LangTest/defer_test.cw \
    LangTest/enum_test.cw \
    LangTest/expr_test.cw \
	LangTest/linked_list_test.cw \
	LangTest/sieve_test.cw \
    LangTest/types_test.cw \
    TestData/fibonacci.cw \
	TestData/fizzbuzz.cw \
	TestData/nqueens.cw \
    TestData/hello_world.cw \
    Lib/bitstream_test.cw \
    Lib/bytestream_test.cw \
    Lib/checksum_test.cw \
    Lib/huffman_test.cw \
    Lib/string_test.cw

ALL_SOURCES := $(LANG_SOURCES) $(TEST_SOURCES) $(LIB_SOURCES)
ALL_SOURCES_NO_GENERIC := $(LANG_SOURCES) $(TEST_SOURCES_NO_GENERIC) $(LIB_SOURCES_NO_GENERIC)


# not the clean part will be run out of order but the early targets are not
# relying on the cleaning so things work out with "make -j"
tests_py: \
    clean \
    tests_meta_py \
    tests_eval_py \
    tests_pp_py \
    tests_x64 \
    tests_a64 \
    tests_a32 \
    misc_test_x64 \
    misc_test_a64 \
    # tests_concrete_py
	@echo "PASSED $@"

tests_parse_py: $(ALL_SOURCES:%.cw=$(DIR)/%.cw.parse)
	@echo "PASSED $@"

tests_meta_py: $(ALL_SOURCES_NO_GENERIC:%.cw=$(DIR)/%.cw.meta)
	@echo "PASSED $@"

tests_eval_py: $(ALL_SOURCES_NO_GENERIC:%.cw=$(DIR)/%.cw.eval)
	@echo "PASSED $@"

tests_symtab_py: $(ALL_SOURCES_NO_GENERIC:%.cw=$(DIR)/%.cw.symtab)
	@echo "PASSED $@"

tests_pp_py: $(ALL_SOURCES:%.cws=$(DIR)/%.cw.pp)
	@echo "PASSED $@"

tests_concrete_py:  $(ALL_SOURCES:%.cw=$(DIR)/%.concrete)
	@echo "PASSED $@"

tests_all_py: tests_parse_py tests_symtab_py tests_meta_py tests_eval_py tests_pp_py

STD_LIB_WITH_ARGV_X64 = ../BE/StdLib/startup.x64.asm ../BE/StdLib/syscall.x64.asm ../BE/StdLib/std_lib.64.asm
STD_LIB_WITH_ARGV_A64 = ../BE/StdLib/startup.a64.asm ../BE/StdLib/syscall.a64.asm ../BE/StdLib/std_lib.64.asm
STD_LIB_WITH_ARGV_A32 = ../BE/StdLib/startup.a32.asm ../BE/StdLib/syscall.a32.asm ../BE/StdLib/std_lib.32.asm

# test language
tests_x64: $(LANG_TESTS:%.cw=$(DIR)/%.x64.exe) $(LIB_TESTS:%.cw=$(DIR)/%.x64.exe) $(TEST_TESTS:%.cw=$(DIR)/%.x64.exe)
tests_a64: $(LANG_TESTS:%.cw=$(DIR)/%.a64.exe) $(LIB_TESTS:%.cw=$(DIR)/%.a64.exe) $(TEST_TESTS:%.cw=$(DIR)/%.a64.exe)
tests_a32: $(TESTS_A32:%.cw=$(DIR)/%.a32.exe)


# Special due to commandline args
misc_test_x64:  $(DIR)/print_argv.x64.test $(DIR)/wordcount.x64.test
misc_test_a64:  $(DIR)/print_argv.a64.test $(DIR)/wordcount.a64.test


$(DIR)/%.cw.parse: %.cw
	@echo "[parse $@]"
	./parse_sexpr.py $<

$(DIR)/%.cw.meta: %.cw
	@echo "[typify $@]"
	$(PYPY) ./typify.py $<

$(DIR)/%.cw.eval: %.cw
	@echo "[eval $@]"
	$(PYPY) ./eval.py $<

$(DIR)/%.cw.symtab: %.cw
	@echo "[symbolize $@]"
	$(PYPY) ./symbolize.py $<


$(DIR)/%.cws.pp: %.cws
	@echo "[prettyprint $@]"
	$(PYPY) ./pp_sexpr.py $< >$@.tmp.cws
	$(PYPY) ./pp_sexpr.py $@.tmp.cws >$@
	diff $@.tmp.cws $@

## Exe Tests

$(DIR)/%.x64.exe: %.cw
	@echo "[lang $@]"
	$(PYPY) ./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../BE/CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.a64.exe: %.cw
	@echo "[lang $@]"
	$(PYPY) ./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../BE/CodeGenA64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@

$(DIR)/%.a32.exe: %.cw
	@echo "[lang $@]"
	$(PYPY) ./emit_ir.py -shake_tree -arch a32 $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A32) $@.asm | $(PYPY) ../BE/CodeGenA32/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@
## Compile only Tests

$(DIR)/%.compile.x64.exe: TestData/%.cw
	@echo "[run $@]"
	$(PYPY) ./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../BE/CodeGenX64/codegen.py -mode binary - $@ > $@.out

$(DIR)/%.compile.a64.exe: TestData/%.cw
	@echo "[run $@]"
	$(PYPY) ./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../BE/CodeGenA64/codegen.py -mode binary - $@ > $@.out

# concrete
$(DIR)/%.concrete: %.cws
	@echo "[concrete $@]"
	$(PYPY) ./pp.py $< > $@
	$(PYPY) ./parse.py < $@ > $@.pp
	diff -bB $@.pp $<

# Misc Tests

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
	$(PYPY) ./emit_ir.py $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_X64) $@.asm | $(PYPY) ../BE/CodeGenX64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 128 48

$(DIR)/asciiquarium.a64.exe: TestData/asciiquarium.cw
	$(PYPY) ./emit_ir.py  $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A64) $@.asm | $(PYPY) ../BE/CodeGenA64/codegen.py -mode binary - $@ > $@.out
	${QEMU} $@ 128 48




clean:
	@echo cleaning and setting up build dirs
	@rm -rf $(DIR)/*
	@mkdir -p  $(DIR)
	@mkdir -p  $(DIR)/Lib
	@mkdir -p  $(DIR)/TestData
	@mkdir -p  $(DIR)/LangTest

pp_test:
	$(PYPY) ./pp.py TestData/*.cw  Lib/*.cw  LangTest/*.cw

cloc:
	@cloc ${CLOC_FLAGS} --by-file '--match-f=[.](py|cc|h)$$' .

update_concrete_syntax:
	for f in $(ALL_SOURCES) ; do  \
	  $(PYPY) ./pp.py  $$f > ConcreteSyntax/$$f ; \
	done

# concrete
$(DIR)/%.concrete: %.cws
	@echo "[concrete $@]"
	$(PYPY) ./pp.py $< > $@
	$(PYPY) ./parse.py < $@ > $@.pp
	diff -bB $@.pp $<

check_conv_sexpr:
	for f in */*.cws ; do \
		echo $$f ; ./cws2cw.py < $$f | ./cw2cws.py > xxx; diff -w  $$f xxx ; \
	done

check_conv:
	for f in */*.cw ; do \
		echo $$f ; ./cw2cws.py < $$f | ./cws2cw.py > xxx; diff -w  $$f xxx ; \
	done

reformat:
	for f in */*.cw ; do \
		echo $$f ; ./pp.py < $$f  >$$f.pp; mv $$f.pp $$f ; \
	done