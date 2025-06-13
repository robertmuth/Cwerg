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
	cd FE &&  $(MAKE) -f Makefile_cc tests
	cd FE && $(MAKE)  -f Makefile_py-s tests && $(MAKE) -s clean
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


test_setup:
	@which cmake
	@which c++
	@which python3
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


cloc:
	./cloc.sh frontend > FE/CLOC.md
	./cloc.sh backend > BE/CLOC.md


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
