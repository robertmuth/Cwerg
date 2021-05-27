MAKEFLAGS = --warn-undefined-variables

export PYTHONPATH =  $(shell pwd)
export COLOR = ON
export VERBOSE = FALSE
export PATH := $(PATH):$(HOME)/.local/bin

# Other optional configs:
# PYPY: arbitrary interpreter, e.g. python3.7 or pypy
# CC: c-compiler

# make sort behave sanely
export LC_ALL=C

.SUFFIXES:

TESTS = TestData/cmp.asm \
        TestData/multiple_results.asm \
        TestData/multiple_results_f32.asm \
        TestData/multiple_results_f64.asm \
        TestData//fib.asm \
        TestData/queens.64.asm \
        TestData/switch.asm \
        TestData/indirect.64.asm \
        TestData/memaddr.64.asm \
        TestData/stack.asm 

# TestData/struct.asm

TEST_EXES = $(TESTS:.asm=.asm.exe)
TEST_OPT_EXES = $(TESTS:.asm=.asm.opt.exe)

.PHONY: $(TESTS) CLOC.txt

CC_FLAGS = -Wall -Wno-unused-result -Wno-unused-label -Wno-unused-variable \
   -Wno-uninitialized -Wno-main -Wno-unused-but-set-variable \
   -Wno-misleading-indentation \
   -Wno-non-literal-null-conversion -IStdLib

%.asm.exe : %.asm
	echo "[ir -> c.64 $@]"
	cat StdLib/syscall.extern64.asm StdLib/std_lib.64.asm $< | $(PYPY) CodeGenC/codegen.py - > $<.c
	$(CC) $(CC_FLAGS) -O -static -m64 -nostdlib StdLib/syscall.c $<.c  -o $@
	$@ > $<.actual.out
	diff $<.actual.out $<.golden

%.asm.opt.exe : %.asm
	echo "[ir -> opt -> c.64 $@]"
	cat StdLib/syscall.extern64.asm StdLib/std_lib.64.asm $< | ${PYPY} Base/optimize.py > $<.opt
	$(PYPY) CodeGenC/codegen.py $<.opt  > $<.opt.c
	$(CC) $(CC_FLAGS) -O -static -m64 -nostdlib StdLib/syscall.c $<.opt.c -lm -o $@
	$@ > $<.actual.opt.out
	diff $<.actual.opt.out $<.golden


tests: 
	$(MAKE) -s $(TEST_EXES)
	@echo
	$(MAKE) -s $(TEST_OPT_EXES)
	$(MAKE) -s clean
	@echo
	mkdir -p build && cd build && cmake .. && $(MAKE) -s
	cd Elf && $(MAKE) -s tests && $(MAKE) -s clean
	cd Base &&   $(MAKE) -s tests && $(MAKE) -s clean
	cd CpuA32 && $(MAKE) -s tests && $(MAKE) -s clean
	cd CpuA64 && $(MAKE) -s tests && $(MAKE) -s clean
	cd CodeGenA32 && $(MAKE) -s tests && $(MAKE) -s clean
	cd Util && $(MAKE) -s tests && $(MAKE) -s clean


tests_github:
	@echo Tool Versions
	python3 -V
	gcc -v
	g++ -v
	clang -v
	clang++ -v
	@echo Build Native Exes
	mkdir -p build && cd build && cmake .. && $(MAKE) -s
	@echo Run Tests
	cd Elf && $(MAKE) -s tests && $(MAKE) -s clean
	cd Base &&   $(MAKE) -s tests && $(MAKE) -s clean
	cd CpuA32 && $(MAKE) -s tests && $(MAKE) -s clean
	cd CpuA64 && $(MAKE) -s tests && $(MAKE) -s clean
	cd CodeGenA32 && $(MAKE) -s tests && $(MAKE) -s clean
	cd CodeGenA64 && $(MAKE) -s tests && $(MAKE) -s clean
	cd Util && $(MAKE) -s tests_py && $(MAKE) -s clean
	cd FrontEndC && $(MAKE) -s tests && $(MAKE) -s clean

integration_tests:
	$(MAKE) -f Makefile.integration -s tests clean


tests_cross:
	cd TestQemu && $(MAKE) -s tests_cross && $(MAKE)  -s clean
	cd CpuA32 && $(MAKE) -s tests_cross && $(MAKE)  -s clean


benchmark:
	cd CodeGenA32 && $(MAKE) -s benchmark && $(MAKE) -s clean

#@ presumit - tests that should pass before any commit
#@
presubmit: lint tests format 


#@ lint - statically check python code for error
#@
lint:
	mypy .


# --by-file
CLOC_FLAGS = -quiet --hide-rate --match-d='Base|CodeGenA32|CodeGenC|CpuA32|CpuA64|Elf|Tools|Util'

#@ cloc - print lines of code stats
#@
cloc:
	@echo
	@echo "## Regular Code"
	@echo
	@cloc ${CLOC_FLAGS} '--match-f=(?<!_test|_tab|_gen)[.](py|h|cc)$$' .
	@echo
	@echo "## Tables"
	@echo
	@cloc ${CLOC_FLAGS} '--match-f=_tab[.](py|cc|h)$$' .
	@echo
	@echo "## Generated Code"
	@echo
	@cloc ${CLOC_FLAGS} '--match-f=_gen[.](py|cc|h)$$' .
	@echo
	@echo "## Testing Code"
	@echo
	@cloc ${CLOC_FLAGS} '--match-f=_test[.](py|cc|h)$$' .
	@echo
	@echo "## Breakdown By File"
	@echo
	@cloc ${CLOC_FLAGS} --by-file '--match-f=[.](py|cc|h)$$' .


#@ CLOC.txt - update line count stats
#@
CLOC.txt:
	make -s cloc | grep -v "github.com" > $@

#@ format - reformat python and c(++) files 
#@
format:
	autopep8 -a -a -a -i */*.py
	clang-format -i --style=Chromium */*.cc */*.h


TestData/nano_jpeg.32.asm::
	$(PYPY) FrontEndC/translate.py  --cpp_args=-IStdLib --mode=32  FrontEndC/TestData/nanojpeg.c > $@

TestData/nano_jpeg.64.asm::
	$(PYPY) FrontEndC/translate.py  --cpp_args=-IStdLib --mode=64  FrontEndC/TestData/nanojpeg.c > $@

#@ opcodes - list opcodes and their fields
#@
opcodes:
	Base/opcode_tab.py


include_stats:
	grep -h include */*.cc */*.h | sort | uniq -c

clean:
	rm -fr TestData/*.out TestData/*.exe TestData/*.c TestData/*.opt build/

#@ help - Show this messsage
#@
help:
	@egrep "^#@" ${MAKEFILE_LIST} | cut -c 3-
