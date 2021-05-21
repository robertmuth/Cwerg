
tests_cross: test_qemu_env_a32 test_qemu_env_a64


CC_FLAGS_CROSS =  -static  -Wl,-z,norelro  -O2 -marm -march=armv7ve

# check if cross-compiler and cross-running works for a32 (see README.md)
test_qemu_env_a32:
	@echo "[$@]"
	arm-linux-gnueabihf-as -mfloat-abi=hard hello_barebones.a32.s -o hello_barebones.a32.o
	arm-linux-gnueabihf-ld hello_barebones.a32.o -o hello_barebones.a32.exe
	qemu-arm-static  ./hello_barebones.a32.exe
	@echo c-hello
	arm-linux-gnueabihf-gcc $(CC_FLAGS_CROSS) hello.c -o hello.a32.exe
	qemu-arm-static  ./hello.a32.exe
	@echo OK

# check if cross-compiler and cross-running works for a64 (see README.md)
test_qemu_env_a64:
	@echo "[$@]"
	aarch64-linux-gnu-as hello_barebones.a64.s -o hello_barebones.a64.o
	aarch64-linux-gnu-ld hello_barebones.a64.o -o hello_barebones.a64.exe
	qemu-aarch64-static  ./hello_barebones.a64.exe
	@echo c-hello
	aarch64-linux-gnu-gcc-8 -static  -Wl,-z,norelro  -O2 hello.c -o hello.a64.exe
	qemu-aarch64-static  ./hello.a64.exe
	@echo OK

clean:
	rm -f *.o *.exe


