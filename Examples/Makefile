.SUFFIXES:  # no built-in rules

tests: jit_cpu_a32.test jit_cpu_a64.test jit_ir_a64.test jit_ir_x64.test

# setting these is not strictly necessary because Linux will auto-detect the proper qemu to use
QEMUX64 =
QEMUA64 = qemu-aarch64-static
QEMUA32 = qemu-arm-static

############################################################
# A32
############################################################
DIR_A32=builda32
CXX_A32 = arm-linux-gnueabihf-g++
CC_A32 = arm-linux-gnueabihf-gcc
# https://stackoverflow.com/questions/48149323/what-does-the-gcc-warning-project-parameter-passing-for-x-changed-in-gcc-7-1-m
A32_FLAGS = -DCWERG_DISABLE_UNWIND -Wl,-z,norelro -marm -march=armv7ve -Wno-psabi

setupa32:
	mkdir -p $(DIR_A32) && cd $(DIR_A32) && CC=$(CC_A32) CXX=$(CXX_A32) cmake -DCWERG_FLAGS="$(A32_FLAGS)" -UCWERG_LIBS ../..


jit_cpu_a32.test: setupa32
	cd $(DIR_A32); VERBOSE=1 $(MAKE) -s jit_cpu_a32.exe
	 $(QEMUA32) $(DIR_A32)/jit_cpu_a32.exe > $(DIR_A32)/$@.out
	diff $(DIR_A32)/$@.out TestData/fib.golden

############################################################
# A64
############################################################
DIR_A64=builda64
CXX_A64 = aarch64-linux-gnu-g++
CC_A64 = aarch64-linux-gnu-gcc
A64_FLAGS = -DCWERG_DISABLE_UNWIND -Wl,-z,norelro

setupa64:
	mkdir -p $(DIR_A64) && cd $(DIR_A64) && CC=$(CC_A64) CXX=$(CXX_A64) cmake -DCWERG_FLAGS="$(A64_FLAGS)" -UCWERG_LIBS  ../..

jit_cpu_a64.test: setupa64
	cd $(DIR_A64); VERBOSE=1 $(MAKE) -s jit_cpu_a64.exe
	 $(QEMUA64) $(DIR_A64)/jit_cpu_a64.exe> $(DIR_A64)/$@.out
	diff $(DIR_A64)/$@.out TestData/fib.golden

jit_ir_a64.test: setupa64
	cd $(DIR_A64); VERBOSE=1 $(MAKE) -s jit_ir_a64.exe
	$(QEMUA64) $(DIR_A64)/jit_ir_a64.exe > $(DIR_A64)/$@.out
	diff $(DIR_A64)/$@.out TestData/fib.golden

############################################################
# X64
############################################################
DIR_X64=buildx64
CXX_X64 = g++
CC_X64 = gcc
X64_FLAGS = -DCWERG_DISABLE_UNWIND -Wl,-z,norelro

setupx64:
	mkdir -p $(DIR_X64) && cd $(DIR_X64) && CC=$(CC_X64) CXX=$(CXX_X64) cmake -DCWERG_FLAGS="$(X64_FLAGS)" -UCWERG_LIBS  ../..


jit_ir_x64.test: setupx64
	cd $(DIR_X64); VERBOSE=1 $(MAKE) -s jit_ir_x64.exe
	$(QEMUX64) $(DIR_X64)/jit_ir_x64.exe > $(DIR_X64)/$@.out
	diff $(DIR_X64)/$@.out TestData/fib.golden

clean:
	rm -rf $(DIR_A32) $(DIR_A64) $(DIR_X64)
