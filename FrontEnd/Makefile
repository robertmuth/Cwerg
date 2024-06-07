
DIR=build
QEMU=


TESTS = $(wildcard TestData/*cw)
LANG_TESTS = $(wildcard LangTest/*cw)
LIB_TESTS = $(wildcard Lib/*_test.cw)
TEST_TESTS = \
	TestData/fibonacci.cw \
    TestData/fizzbuzz.cw \
	TestData/hash_test.cw \
    TestData/heapsort.cw \
    TestData/hello_world.cw \
    TestData/linked_list.cw \
    TestData/sieve.cw \
    TestData/sort.cw

TESTS_A32 = \
    TestData/fibonacci.cw \
	TestData/fizzbuzz.cw \
    TestData/hello_world.cw \
	TestData/linked_list.cw \
    TestData/sieve.cw \
    Lib/bitstream_test.cw \
    Lib/bytestream_test.cw \
    Lib/checksum_test.cw \
    Lib/huffman_test.cw \
    Lib/string_test.cw \
    Lib/trig_test.cw

TESTS_CONCRETE = $(LANG_TESTS) $(TESTS) \
    Lib/ansi.cw \
    Lib/bitstream.cw \
    Lib/bitstream_test.cw \
    Lib/bytestream.cw \
    Lib/bytestream_test.cw \
    Lib/checksum.cw \
    Lib/checksum_test.cw \
    Lib/fmt.cw \
    Lib/fmt_test.cw \
    Lib/hashtab32.cw \
    Lib/heapsort.cw \
    Lib/huffman.cw \
    Lib/huffman_test.cw \
    Lib/math.cw \
    Lib/os.cw \
    Lib/random.cw \
    Lib/sha3.cw \
    Lib/sha3_test.cw \
    Lib/string.cw \
    Lib/string_test.cw \
    Lib/trig.cw \
    Lib/trig_test.cw

#	Lib/flate.cw   ***
#	Lib/flate_test.cw


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
    tests_concrete_py

tests_parse_py: $(TESTS:%.cw=$(DIR)/%.cw.parse)
tests_meta_py: $(TESTS:%.cw=$(DIR)/%.cw.meta)
tests_eval_py: $(TESTS:%.cw=$(DIR)/%.cw.eval)
tests_symtab_py: $(TESTS:%.cw=$(DIR)/%.cw.symtab)
tests_pp_py: $(TESTS:%.cw=$(DIR)/%.cw.pp)

tests_concrete_py:  $(TESTS_CONCRETE:%.cw=$(DIR)/%.concrete)


tests_all_py: tests_parse_py tests_symtab_py tests_meta_py tests_eval_py tests_pp_py

STD_LIB_WITH_ARGV_X64 = ../StdLib/startup.x64.asm ../StdLib/syscall.x64.asm ../StdLib/std_lib.64.asm
STD_LIB_WITH_ARGV_A64 = ../StdLib/startup.a64.asm ../StdLib/syscall.a64.asm ../StdLib/std_lib.64.asm
STD_LIB_WITH_ARGV_A32 = ../StdLib/startup.a32.asm ../StdLib/syscall.a32.asm ../StdLib/std_lib.32.asm

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

$(DIR)/%.a32.exe: %.cw
	@echo "[lang $@]"
	./emit_ir.py -shake_tree -arch a32 $< > $@.asm
	cat $(STD_LIB_WITH_ARGV_A32) $@.asm | $(PYPY) ../CodeGenA32/codegen.py -mode binary - $@ > $@.out
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

# concrete
$(DIR)/%.concrete: %.cw
	@echo "[concrete $@]"
	./pp.py $< > $@
	./parse.py < $@ > $@.pp
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


reformat:
	for f in TestData/*.cw ; do \
		echo $$f ; ./pp_sexpr.py < $$f  >$$f.pp; mv $$f.pp $$f ; \
	done

update_concrete_syntax:
	for f in $(TESTS_CONCRETE) ; do  \
	  ./pp.py  $$f > ConcreteSyntax/$$f ; \
	done

reformat_lib:
	for f in Lib/*.cw ; do \
		echo $$f ; ./pp_sexpr.py < $$f  >$$f.pp; mv $$f.pp $$f ; \
	done