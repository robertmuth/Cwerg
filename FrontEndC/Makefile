.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

ALL_TESTS = \
20000523-1.c \
20020129-1.c \
2002-05-02-CastTest.c \
2002-12-13-MishaTest.c \
2003-04-22-Switch.c \
2003-05-14-initialize-string.c \
2003-05-22-LocalTypeTest.c \
2003-07-08-BitOpsTest.c \
2003-10-12-GlobalVarInitializers.c \
2005-05-12-Int64ToFP.c \
2005-05-13-SDivTwo.c \
2005-11-29-LongSwitch.c \
2006-01-29-SimpleIndirectCall.c \
2006-02-04-DivRem.c \
20080424-1.c \
990127-1.c \
arrays_decl_ref.c \
corner_cases.c \
nqueen.c \
pr19606.c \
rename.c \
struct2.c \
sumarray.c \
do_while.c \
sieve.c \
pfannkuchen.c

META_TESTS = \
20000523-1.c \
2002-05-02-CastTest.c \
2002-12-13-MishaTest.c \
2003-04-22-Switch.c \
2003-05-14-initialize-string.c \
2003-05-22-LocalTypeTest.c \
2003-07-08-BitOpsTest.c \
2003-10-12-GlobalVarInitializers.c \
2005-05-12-Int64ToFP.c \
2005-05-13-SDivTwo.c \
2005-11-29-LongSwitch.c \
2006-01-29-SimpleIndirectCall.c \
2006-02-04-DivRem.c \
20080424-1.c \
990127-1.c \
arrays_decl_ref.c \
corner_cases.c \
nqueen.c \
pr19606.c \
rename.c \
struct2.c \
sumarray.c
#20020129-1.c

EASY_TESTS = \
20000523-1.c \
20020129-1.c \
corner_cases.c \
2002-05-02-CastTest.c \
2005-05-13-SDivTwo.c \
nqueen.c \
pr19606.c \
2003-04-22-Switch.c \
sumarray.c \
2003-05-22-LocalTypeTest.c \
20080424-1.c \
2003-07-08-BitOpsTest.c \
do_while.c \
sieve.c \
pfannkuchen.c

# T2006-01-29-SimpleIndirectCall.c
# T2003-05-14-initialize-string.c
# T2005-05-12-Int64ToFP.c

tests: tests_py tests_c
	@echo "[OK FrontEndC]"

tests_py:  meta_tests translate_tests

tests_c: canonicalize_tests $(DIR)/nano32 $(DIR)/nano64

# exercise meta data generation
$(DIR)/%.meta_test : TestData/%.c
	@echo "[meta $@]"
	$(PYPY)	./meta.py --cpp_args=-I../StdLib $< >$@.out


meta_tests:: $(META_TESTS:%.c=$(DIR)/%.meta_test)

# make sure we can translate without crashing
$(DIR)/%.translate_test : TestData/%.c
	@echo "[translate $@]"
	$(PYPY)	./translate.py --mode=32 --cpp_args=-I../StdLib $< >$@.out

translate_tests:: $(EASY_TESTS:%.c=$(DIR)/%.translate_test)

# make sure the canocalized code still compiles
$(DIR)/%.canonicalize_test : TestData/%.c
	@echo "[compile $@]"
	$(PYPY)	./canonicalize.py --cpp_args=-I../StdLib  $< >$@.out.c
	$(CC) -Wno-builtin-declaration-mismatch $@.out.c -o $@.exe
	./$@.exe > $@.run.out
	diff $@.run.out $(basename $<).reference_output

canonicalize_tests: $(ALL_TESTS:%.c=$(DIR)/%.canonicalize_test)

# This uses std lib proto types but no implementation - note the hack around print_s_ln
$(DIR)/nano64: TestData/nanojpeg.c
	@echo "[compile $@]"
	$(PYPY)	./canonicalize.py --cpp_args=-I../StdLib TestData/nanojpeg.c > $@.out.c
	$(CC) -Dprint_s_ln=puts -I ../StdLib -Wno-builtin-declaration-mismatch $@.out.c -m64 -o $@.exe
	./$@.exe TestData/ash_tree.jpg $@.ppm
	cmp  $@.ppm TestData/ash_tree.ppm

# This uses std lib proto types but no implementation - note the hack around print_s_ln
$(DIR)/nano32: TestData/nanojpeg.c
	@echo "[compile $@]"
	$(PYPY)	./canonicalize.py --cpp_args=-I../StdLib TestData/nanojpeg.c > $@.out.c
	$(CC) -Dprint_s_ln=puts -I ../StdLib -Wno-builtin-declaration-mismatch $@.out.c -m32 -o $@.exe
	./$@.exe TestData/ash_tree.jpg $@.ppm
	cmp  $@.ppm TestData/ash_tree.ppm

clean:
	rm -f $(DIR)/*
