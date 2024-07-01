# Cross Testing Cross-tool-chains and QEMU

This more or less assumes Ubuntu (22.04) running on x86-64.

(see https://gist.github.com/luk6xff/9f8d2520530a823944355e59343eadc1)


Note that once the package `qemu-user-static` is installed, you can
run arm32 and aarch64 executables directly as if they were native executable.
So instead of `qemu-aarch64-static hello.aarch64.exe` you can just run `./hello.aarch64.exe`.

## A32 aka Arm32


Install the cross toolchain:

```
sudo apt-get install gcc-arm-linux-gnueabihf  g++-arm-linux-gnueabihf
```


Set up cross compilers and QEMU via

```
make set_up_cross_env_a32
```

note, this runs sudo so it may prompt for a password

Now check the setup with

```
make test_qemu_env_a32
```

Here is a barebones example

```
arm-linux-gnueabihf-as hello_barebones.a32.s -o hello_barebones.a32.o
arm-linux-gnueabihf-objdump -d hello_barebones.a32.o
arm-linux-gnueabihf-ld hello_barebones.a32.o -o hello_barebones-a32
arm-linux-gnueabihf-objdump -d hello_barebones-a32
qemu-arm-static  ./hello_barebones-a32
```


## A64 aka Aarch64


Install the cross toolchain:

```
sudo apt-get install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
```

Set up cross compilers and QEMU via

```
make set_up_cross_env_a64
```

note, this runs sudo so it may prompt for a password

Now check the setup with

```
make test_qemu_env_a64
```

Here is a barebones example

```
aarch64-linux-gnu-as hello_barebones.a64.s -o hello_barebones.a64.o
aarch64-linux-gnu-objdump -d hello_barebones.a64.o
aarch64-linux-gnu-ld hello_barebones.a64.o -o hello_barebones-a64
aarch64-linux-gnu-objdump -d hello_barebones-a64
qemu-arm-static  ./hello_barebones-a64
```

Often it useful to see how a compiler translates a certain C expression.
Assuming `test.c` contains code with that expression. Run
```
aarch64-linux-gnu-gcc-8 test.c -c -O3  -o xxx.o ; aarch64-linux-gnu-objdump -D xxx.o
```
to see the result.

Qemu can also used to generated traces which can be useful for debugging:

General purpose reg contents only
```
qemu-aarch64-static -singlestep -d nochain,cpu  test.exe 2> trace.txt
```

General purpose + FP reg contents and instruction:

```
qemu-aarch64-static -singlestep -d nochain,cpu,fpu,in_asm  test.exe 2> trace.txt
```
