.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

tests_cross: test_qemu_env_a32 test_qemu_env_a64


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

############################################################
# Python
############################################################
python_version_check:
	@echo "Python Version Check (3.10 or higher required)"
	@python3 -V
	@python3 -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10 or higher is required'"
	@echo "Python version is sufficient"

############################################################
# Host C++
############################################################
host_cxx_version_check:
	@echo "Host C++ Compiler Version Check (should support C++20)"
	@$(CXX) --version | head -n 1
	@$(CXX) hello.cc -std=c++20 -o $(DIR)/hello.cc.host.exe
	@$(DIR)/hello.cc.host.exe > $(DIR)/hello.cc.host.out
	@echo "hello world (cc)!" | diff - $(DIR)/hello.cc.host.out
	@echo "Host C++ compiler is sufficient"

############################################################
# A32
############################################################
# on debian systems you will need to install the following packages to get the cross-compiler and qemu for a32:
#	sudo apt install gcc-arm-linux-gnueabihf  g++-arm-linux-gnueabihf qemu-user-static

# https://gcc.gnu.org/onlinedocs/gcc/ARM-Options.html
CC_A32_FLAGS = -static  -Wl,-z,norelro  -O2 -marm -march=armv7ve+simd
CXX_A32 = arm-linux-gnueabihf-g++
CC_A32 = arm-linux-gnueabihf-gcc
AS_A32 = arm-linux-gnueabihf-as
LD_A32 = arm-linux-gnueabihf-ld
QEMU_A32 = qemu-arm-static

# check if cross-compiler and cross-running works for a32 (see README.md)
cross_toolchain_a32_check:
	@echo "[$@]"
	$(AS_A32) -mfloat-abi=hard hello_barebones.a32.s -o $(DIR)/hello_barebones.a32.o
	$(LD_A32) $(DIR)/hello_barebones.a32.o -o $(DIR)/hello_barebones.a32.exe
	$(QEMU_A32)  $(DIR)/hello_barebones.a32.exe
	@echo c-hello
	$(CC_A32) $(CC_A32_FLAGS) hello.c -o $(DIR)/hello.c.a32.exe
	$(QEMU_A32)  $(DIR)/hello.c.a32.exe > $(DIR)/hello.c.a32.out
	@echo "hello world (c)!" | diff - $(DIR)/hello.c.a32.out
	@echo c++-hello
	$(CXX_A32)  $(CC_A32_FLAGS) -std=c++20 -O2 hello.cc -o $(DIR)/hello.cc.a32.exe
	$(QEMU_A32)  $(DIR)/hello.cc.a32.exe > $(DIR)/hello.cc.a32.out
	@echo "hello world (cc)!" | diff - $(DIR)/hello.cc.a32.out
	@echo "[OK $@]"
	@echo

############################################################
# A64
############################################################
# on debian systems you will need to install the following packages to get the cross-compiler and qemu for a64:
#	sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu qemu-user-static

CC_A64_FLAGS = -static  -Wl,-z,norelro  -O2
CXX_A64 = aarch64-linux-gnu-g++
CC_A64 = aarch64-linux-gnu-gcc
AS_A64 = aarch64-linux-gnu-as
LD_A64 = aarch64-linux-gnu-ld
QEMU_A64 = qemu-aarch64-static


cross_toolchain_a64_check:
	@echo "[$@]"
	$(AS_A64) hello_barebones.a64.s -o $(DIR)/hello_barebones.a64.o
	$(LD_A64) $(DIR)/hello_barebones.a64.o -o $(DIR)/hello_barebones.a64.exe
	$(QEMU_A64) $(DIR)/hello_barebones.a64.exe
	@echo c-hello
	$(CC_A64) $(CC_A64_FLAGS) hello.c -o $(DIR)/hello.c.a64.exe
	$(QEMU_A64) $(DIR)/hello.c.a64.exe > $(DIR)/hello.c.a64.out
	@echo "hello world (c)!" | diff - $(DIR)/hello.c.a64.out
	@echo c++-hello
	$(CXX_A64) $(CC_A64_FLAGS) -std=c++20 -O2 hello.cc -o$(DIR)/hello.cc.a64.exe
	$(QEMU_A64) $(DIR)/hello.cc.a64.exe > $(DIR)/hello.cc.a64.out
	@echo "hello world (cc)!" | diff - $(DIR)/hello.cc.a64.out
	@echo "[OK $@]"

############################################################
# X64
############################################################
# on debian systems you will need to install the following packages to get the cross-compiler and qemu for a64:
#	sudo apt install x86_64-linux-gnu-gcc x86_64-linux-gnu-g++ qemu-user-static
# TODO

clean:
	rm -f $(DIR)
