# Cross Testing  with QEMU

(see https://gist.github.com/luk6xff/9f8d2520530a823944355e59343eadc1)

## A32 aka Arm32

Set up env for Ubuntu 

```
sudo apt-get install gcc-arm-linux-gnueabihf libc6-dev-armhf-cross qemu-user-static
```

For C++ support:
```
 sudo apt-get install g++-arm-linux-gnueabihff libunwind-dev-armhf-cross
```

Now you can run

```
arm-linux-gnueabihf-gcc -static  -O2 -marm -march=armv7ve  hello.c -o hello-a32
arm-linux-gnueabihf-objdump -d hello-a32   # optional
qemu-arm-static  ./hello-a32

arm-linux-gnueabihf-as hello_barebones.a32.s -o hello_barebones.a32.o
arm-linux-gnueabihf-objdump -d hello_barebones.a32.o
arm-linux-gnueabihf-ld hello_barebones.a32.o -o hello_barebones-a32
arm-linux-gnueabihf-objdump -d hello_barebones-a32
qemu-arm-static  ./hello_barebones-a32 
```

or equivalently

`make test_qemu_env_a32`
  
## A64 aka Aarch64

Set up env for Ubuntu 

```
sudo apt-get install gcc-aarch64-linux-gnu lqemu-user-static
```
Now you can run

```
aarch64-linux-gnu-gcc -static  -O2  hello.c -o hello-a64
aarch64-linux-gnu-objdump -d hello-a64   # optional
qemu-arm-static  ./hello-a64

aarch64-linux-gnu-as hello_barebones.a64.s -o hello_barebones.a64.o
aarch64-linux-gnu-objdump -d hello_barebones.a64.o
aarch64-linux-gnu-ld hello_barebones.a64.o -o hello_barebones-a64
aarch64-linux-gnu-objdump -d hello_barebones-a64
qemu-arm-static  ./hello_barebones-a64
```

or equivalently

`make test_qemu_env_a64`
