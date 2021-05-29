.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

tests_cross:  $(DIR)/jit_cpu_a64.exe $(DIR)/jit_cpu_a32.exe

############################################################
# Cross Compile
############################################################
CC_FLAGS= -Wall -Werror -std=c++17 -fno-exceptions -O2 -I..

A32_LIB_DIS = ../CpuA32/symbolic.cc ../CpuA32/opcode_gen.cc
A64_LIB_DIS = ../CpuA64/symbolic.cc ../CpuA64/opcode_gen.cc
UTIL_LITE_LIB = ../Util/assert.cc ../Util/parse.cc

CC_FLAGS_A32_CROSS =  -static  -Wl,-z,norelro -marm -march=armv7ve $(CC_FLAGS) -DCWERG_DISABLE_UNWIND


$(DIR)/jit_cpu_a32.exe: jit_cpu_a32.cc $(A32_LIB_DIS) $(UTIL_LITE_LIB)
	arm-linux-gnueabihf-g++-9 $(CC_FLAGS_A32_CROSS) $(UTIL_LITE_LIB) $(A32_LIB_DIS) jit_cpu_a32.cc  -o $@.exe
	./$@.exe

CC_FLAGS_A64_CROSS =  -static  -Wl,-z,norelro $(CC_FLAGS) -DCWERG_DISABLE_UNWIND

$(DIR)/jit_cpu_a64.exe: jit_cpu_a32.cc $(A64_LIB_DIS) $(UTIL_LITE_LIB)
	aarch64-linux-gnu-g++-9 $(CC_FLAGS_A64_CROSS) $(UTIL_LITE_LIB) $(A64_LIB_DIS) jit_cpu_a64.cc  -o $@.exe
	./$@.exe
