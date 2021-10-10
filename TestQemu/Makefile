.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

tests_cross: test_qemu_env_a32 test_qemu_env_a64

############################################################
# A32
############################################################
set_up_cross_env_a32:
	sudo apt install gcc-multilib-arm-linux-gnueabihf  g++-multilib-arm-linux-gnueabihf qemu-user-static

# https://gcc.gnu.org/onlinedocs/gcc/ARM-Options.html
CC_A32_FLAGS = -static  -Wl,-z,norelro  -O2 -marm -march=armv7ve+simd
CXX_A32 = arm-linux-gnueabihf-g++
CC_A32 = arm-linux-gnueabihf-gcc
AS_A32 = arm-linux-gnueabihf-as
LD_A32 = arm-linux-gnueabihf-ld
QEMU_A32 = qemu-arm-static

# check if cross-compiler and cross-running works for a32 (see README.md)
test_qemu_env_a32:
	@echo "[$@]"
	$(AS_A32) -mfloat-abi=hard hello_barebones.a32.s -o hello_barebones.a32.o
	$(LD_A32) hello_barebones.a32.o -o hello_barebones.a32.exe
	$(QEMU_A32)  ./hello_barebones.a32.exe
	@echo c-hello
	$(CC_A32) $(CC_A32_FLAGS) hello.c -o hello.c.a32.exe
	$(QEMU_A32)  ./hello.c.a32.exe
	@echo c++-hello
	$(CXX_A32)  $(CC_A32_FLAGS)  -O2 hello.cc -o hello.cc.a32.exe
	$(QEMU_A32)  ./hello.cc.a32.exe
	@echo "[OK $@]"
	@echo

############################################################
# A64
############################################################

CC_A64_FLAGS = -static  -Wl,-z,norelro  -O2
CXX_A64 = aarch64-linux-gnu-g++
CC_A64 = aarch64-linux-gnu-gcc
AS_A64 = aarch64-linux-gnu-as
LD_A64 = aarch64-linux-gnu-ld
QEMU_A64 = qemu-aarch64-static

set_up_cross_env_a64:
	sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu qemu-user-static

# check if cross-compiler and cross-running works for a64 (see README.md)
test_qemu_env_a64:
	@echo "[$@]"
	$(AS_A64) hello_barebones.a64.s -o hello_barebones.a64.o
	$(LD_A64) hello_barebones.a64.o -o hello_barebones.a64.exe
	$(QEMU_A64) ./hello_barebones.a64.exe
	@echo c-hello
	$(CC_A64) $(CC_A64_FLAGS) hello.c -o $(DIR)/hello.c.a64.exe
	$(QEMU_A64) $(DIR)/hello.c.a64.exe
	@echo c++-hello
	$(CXX_A64) $(CC_A64_FLAGS) hello.cc -o$(DIR)/hello.cc.a64.exe
	$(QEMU_A64) $(DIR)/hello.cc.a64.exe
	@echo "[OK $@]"


clean:
	rm -f *.o *.exe


