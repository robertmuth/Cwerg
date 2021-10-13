.SUFFIXES:  # no built-in rules

tests: jit_cpu_a32.test jit_cpu_a64.test jit_ir_a64.test

DIR_A32=build32
CXX_A32 = arm-linux-gnueabihf-g++
CC_A32 = arm-linux-gnueabihf-gcc
# https://stackoverflow.com/questions/48149323/what-does-the-gcc-warning-project-parameter-passing-for-x-changed-in-gcc-7-1-m
A32_FLAGS = -DCWERG_DISABLE_UNWIND -Wl,-z,norelro -marm -march=armv7ve -Wno-psabi

DIR_A64=build64
CXX_A64 = aarch64-linux-gnu-g++
CC_A64 = aarch64-linux-gnu-gcc
A64_FLAGS = -DCWERG_DISABLE_UNWIND -Wl,-z,norelro

setup32:
	mkdir -p $(DIR_A32) && cd $(DIR_A32) && CC=$(CC_A32) CXX=$(CXX_A32) cmake -DCWERG_FLAGS="$(A32_FLAGS)" -UCWERG_LIBS ../..

jit_cpu_a32.test: setup32
	cd $(DIR_A32); VERBOSE=1 $(MAKE) -s jit_cpu_a32.exe
	$(DIR_A32)/jit_cpu_a32.exe > $(DIR_A32)/$@.out
	diff $(DIR_A32)/$@.out TestData/fib.golden

setup64:
	mkdir -p $(DIR_A64) && cd $(DIR_A64) && CC=$(CC_A64) CXX=$(CXX_A64) cmake -DCWERG_FLAGS="$(A64_FLAGS)" -UCWERG_LIBS  ../..

jit_cpu_a64.test: setup64
	cd $(DIR_A64); VERBOSE=1 $(MAKE) -s jit_cpu_a64.exe
	$(DIR_A64)/jit_cpu_a64.exe> $(DIR_A64)/$@.out
	diff $(DIR_A64)/$@.out TestData/fib.golden

jit_ir_a64.test: setup64
	cd $(DIR_A64); VERBOSE=1 $(MAKE) -s jit_ir_a64.exe
	$(DIR_A64)/jit_ir_a64.exe > $(DIR_A64)/$@.out
	diff $(DIR_A64)/$@.out TestData/fib.golden

clean:
	rm -rf $(DIR_A32) $(DIR_A64)
