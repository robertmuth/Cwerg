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
.PHONY: CLOC.txt

CWERG_LIBS = -lunwind -llzma
CWERG_FLAGS = -DCWERG_ENABLE_UNWIND

tests:
	cd BE && $(MAKE) -f Makefile_py tests
	@echo Build Native Exes
	mkdir -p build && cd build && cmake -DCWERG_FLAGS="$(CWERG_FLAGS)" -DCWERG_LIBS="$(CWERG_LIBS)" .. && $(MAKE) -s
	cd BE &&  $(MAKE) -f Makefile_cc tests
	cd Util && $(MAKE) -s tests && $(MAKE) -s clean
	cd FE && $(MAKE) -s tests_py && $(MAKE) -s clean
	cd FE_WASM && $(MAKE) -s tests && $(MAKE) -s clean

cmake_setup:
	mkdir -p build && cd build && cmake -DCWERG_FLAGS="$(CWERG_FLAGS)" -DCWERG_LIBS="$(CWERG_LIBS)" ..

show_versions:
	@echo Tool Versions
	python3 -V
	gcc -v
	g++ -v
	clang -v
	clang++ -v


test_cross_execution:
	cd TestQemu && $(MAKE) -s tests_cross && $(MAKE)  -s clean


benchmark:
	cd BE/CodeGenA32 && $(MAKE) -f Makefile_cc -s benchmark && $(MAKE)  -f Makefile_cc -s clean

#@ presubmit - tests that should pass before any commit
#@
presubmit: lint tests format


#@ lint - statically check python code for error
#@
lint:
	mypy .


# --by-file
CLOC_FLAGS = -quiet --hide-rate --match-d='Base|CodeGenA32|CodeGen.*|Cpu.*|Elf|Tools|Util'

#@ cloc - print lines of code stats
#@
cloc:
	@echo
	@echo "## Regular Code"
	@echo
	@cloc ${CLOC_FLAGS} '--match-f=[.](py|cc|h)$$' '--not-match-f=(_test|_tab|_gen.*)[.](py|h|cc)$$' .
	@echo
	@echo "## Tables"
	@echo
	@cloc ${CLOC_FLAGS} '--match-f=_tab[.](py|cc|h)$$' .
	@echo
	@echo "## Generated Code"
	@echo
	@cloc ${CLOC_FLAGS} '--match-f=_gen.*[.](py|cc|h)$$' .
	@echo
	@echo "## Testing Code"
	@echo
	@cloc ${CLOC_FLAGS} '--match-f=_test[.](py|cc|h)$$' .
	@echo
	@echo "## Breakdown: Table Files"
	@echo
	@cloc ${CLOC_FLAGS} --by-file  '--match-f=_tab[.](py|cc|h)$$' .
	@echo
	@echo "## Breakdown: Generated Files"
	@echo
	@cloc ${CLOC_FLAGS} --by-file  '--match-f=_gen.*[.](py|cc|h)$$' .
	@echo
	@echo "## Breakdown: Regular Files"
	@echo
	@cloc ${CLOC_FLAGS} --by-file '--match-f=[.](py|cc|h)$$' '--not-match-f=(_tab|_gen.*)[.](py|cc|h)$$' .


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




include_stats:
	grep -h include */*.cc */*.h | sort | uniq -c

clean:
	rm -fr TestData/*.out TestData/*.exe TestData/*.c TestData/*.opt build/

#@ help - Show this messsage
#@
help:
	@egrep "^#@" ${MAKEFILE_LIST} | cut -c 3-
