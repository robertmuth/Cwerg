MAKEFLAGS = --warn-undefined-variables

# Run `make help` for help

#@ Note exports can easily be overwritten via command line
#@ e.g.: make COLOR=OFF PYPY= ...
#@
#@ Other optional configs:
#@
#@ CC: c-compiler (e.g. clang)
#@ PYPY: prefix used for invoking python programs (e.g. python3.7 or pypy)
#@ QEMU_A32: prefix used for invoking programs compiled for a32 (e.g. qemu-arm-static)
#@ QEMU_A64: prefix used for invoking programs compiled for a64 (e.g. qemu-aarch64-static)
#@ QEMU_X64: prefix used for invoking programs compiled for x64 (e.g. qemu-x86_64-static)
#@
#@ Make targets:
#@
export PYTHONPATH := $(shell pwd)
export COLOR := ON
export VERBOSE := FALSE
export PATH := $(PATH):$(HOME)/.local/bin
# make sort behave sanely
export LC_ALL := C

.SUFFIXES:
.PHONY: CLOC.txt

CWERG_LIBS := -lunwind -llzma
CWERG_FLAGS := -DCWERG_ENABLE_UNWIND

#@ tests (default) - run BE and FE tests
#@
tests: cmake_setup
	@echo Python Tests
	cd BE && $(MAKE) -f Makefile_py tests
	cd FE && $(MAKE) -f Makefile_py -s tests && $(MAKE) -f Makefile_py -s clean
	@echo C++ Tests
	cd BE && $(MAKE) -f Makefile_cc tests
	cd Util && $(MAKE) -s tests && $(MAKE) -s clean
	cd FE &&  $(MAKE) -f Makefile_cc clean && $(MAKE) -f Makefile_cc tests

#@ cmake_setup - process the CMake config file and set up directories for building C++ frontend/backends
#@
cmake_setup:
	mkdir -p build && cd build && cmake -DCWERG_FLAGS="$(CWERG_FLAGS)" -DCWERG_LIBS="$(CWERG_LIBS)" ..

#@ build_compiler - build c++ versions of frontend and backends
#@
build_compiler: cmake_setup
	cd build && $(MAKE) -s -j compiler.exe x64_codegen_tool.exe a64_codegen_tool.exe a32_codegen_tool.exe

#@ show_versions - show version of development tools Cwerg depends on
#@
show_versions:
	@echo Tool Versions
	-python3 -V
	-gcc -v
	-g++ -v
	-clang -v
	-clang++ -v
	-qemu-aarch64-static -version
	-qemu-arm-static -version
	-qemu-x86_64-static -version
	-cloc -version

test_setup:
	@which cmake
	@which c++
	@which python3
	cd TestQemu && $(MAKE) -s tests_cross && $(MAKE)  -s clean


benchmark:
	cd BE/CodeGenA32 && $(MAKE) -f Makefile_cc -s benchmark && $(MAKE)  -f Makefile_cc -s clean

## Work in progress
##@ presubmit - tests that should pass before any commit
##@
## Work in progress
presubmit: lint tests format


#@ lint - statically check python code for error
#@
lint:
	mypy .

#@ cloc - update line number statistics
#@
cloc:
	./cloc.sh FE > FE/CLOC.md
	./cloc.sh BE > BE/CLOC.md
	./cloc.sh IR > IR/CLOC.md


#@ format - reformat python and c(++) files
#@
format:
	autopep8 -a -a -a -i */*.py
	clang-format -i --style=Chromium */*.cc */*.h


include_stats:
	grep -h include */*.cc */*.h | sort | uniq -c

clean:
	rm -fr TestData/*.out TestData/*.exe TestData/*.c TestData/*.opt build/

#@ help - Show this messsage
#@
help:
	@egrep "^#@" ${MAKEFILE_LIST} | cut -c 3-
