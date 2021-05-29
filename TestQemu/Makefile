.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

tests_cross: test_qemu_env_a32 test_qemu_env_a64

set_up_cross_env_a32:
	sudo apt install gcc-9-multilib-arm-linux-gnueabihf  g++-9-multilib-arm-linux-gnueabihf qemu-user-static

CC_FLAGS_A32_CROSS =  -static  -Wl,-z,norelro  -O2 -marm -march=armv7ve

# check if cross-compiler and cross-running works for a32 (see README.md)
test_qemu_env_a32:
	@echo "[$@]"
	arm-linux-gnueabihf-as -mfloat-abi=hard hello_barebones.a32.s -o hello_barebones.a32.o
	arm-linux-gnueabihf-ld hello_barebones.a32.o -o hello_barebones.a32.exe
	qemu-arm-static  ./hello_barebones.a32.exe
	@echo c-hello
	arm-linux-gnueabihf-gcc-9 $(CC_FLAGS_A32_CROSS) hello.c -o hello.c.a32.exe
	qemu-arm-static  ./hello.c.a32.exe
    #  This does not work - probable because the libraries are compiled for another arch
	# @echo c++-hello
	# arm-linux-gnueabihf-g++-9  $(CC_FLAGS_A32_CROSS)  -O2 hello.cc -o hello.cc.a32.exe
	# qemu-aarch64-static  ./hello.cc.a32.exe
	@echo "[OK $@]"


CC_FLAGS_A64_CROSS =  -static  -Wl,-z,norelro  -O2

set_up_cross_env_a64:
	sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu qemu-user-static


# check if cross-compiler and cross-running works for a64 (see README.md)
test_qemu_env_a64:
	@echo "[$@]"
	aarch64-linux-gnu-as hello_barebones.a64.s -o hello_barebones.a64.o
	aarch64-linux-gnu-ld hello_barebones.a64.o -o hello_barebones.a64.exe
	qemu-aarch64-static  ./hello_barebones.a64.exe
	@echo c-hello
	aarch64-linux-gnu-gcc-9 $(CC_FLAGS_A64_CROSS) hello.c -o $(DIR)/hello.c.a64.exe
	qemu-aarch64-static $(DIR)/hello.c.a64.exe
	@echo c++-hello
	aarch64-linux-gnu-g++-9 $(CC_FLAGS_A64_CROSS) hello.cc -o$(DIR)/hello.cc.a64.exe
	qemu-aarch64-static $(DIR)/hello.cc.a64.exe
	@echo "[OK $@]"


clean:
	rm -f *.o *.exe


