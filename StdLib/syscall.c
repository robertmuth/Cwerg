/*
 * Bindings for testing CodeGenC in -nostdlib mode
 * https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md
 *
 * Built-in defines can be dumped via
 * gcc -m32 -dM -E - < /dev/null
 * gcc -dM -E - < /dev/null
 * arm-linux-gnueabihf-gcc-9 -dM -E - < /dev/null
 *
 * This file can be tested like so
 * gcc -nostdlib -static -D__test_main__=1 -m32 syscall.c
 * ./a.out
 * gcc -nostdlib -static -D__test_main__=1 syscall.c
 * ./a.out
 * aarch64-linux-gnu-gcc-8 -nostdlib  -static -D__test_main__=1 syscall.c
 * ./a.out
 * arm-linux-gnueabihf-gcc-9 -nostdlib  -static -D__test_main__=1 -marm
 * -march=armv7ve syscall.c
 * ./a.our
 */

#if !__linux__
#error "only linux supported"
#endif

extern int main(int argc, char** argv);

/* ============================================================ */
#if __x86_64__
/* ============================================================ */
long _x64_syscall0(long n) {
  long ret;
  __asm__ __volatile__("syscall" : "=a"(ret) : "a"(n) : "rcx", "r11", "memory");
  return ret;
}

long _x64_syscall1(long n, long a1) {
  long ret;
  __asm__ __volatile__("syscall"
                       : "=a"(ret)
                       : "a"(n), "D"(a1)
                       : "rcx", "r11", "memory");
  return ret;
}

long _x64_syscall2(long n, long a1, long a2) {
  long ret;
  __asm__ __volatile__("syscall"
                       : "=a"(ret)
                       : "a"(n), "D"(a1), "S"(a2)
                       : "rcx", "r11", "memory");
  return ret;
}

long _x64_syscall3(long n, long a1, long a2, long a3) {
  long ret;
  __asm__ __volatile__("syscall"
                       : "=a"(ret)
                       : "a"(n), "D"(a1), "S"(a2), "d"(a3)
                       : "rcx", "r11", "memory");
  return ret;
}

long _x64_syscall4(long n, long a1, long a2, long a3, long a4) {
  long ret;
  register long r10 __asm__("r10") = a4;
  __asm__ __volatile__("syscall"
                       : "=a"(ret)
                       : "a"(n), "D"(a1), "S"(a2), "d"(a3), "r"(r10)
                       : "rcx", "r11", "memory");
  return ret;
}

long _x64_syscall5(long n, long a1, long a2, long a3, long a4, long a5) {
  long ret;
  register long r10 __asm__("r10") = a4;
  register long r8 __asm__("r8") = a5;
  __asm__ __volatile__("syscall"
                       : "=a"(ret)
                       : "a"(n), "D"(a1), "S"(a2), "d"(a3), "r"(r10), "r"(r8)
                       : "rcx", "r11", "memory");
  return ret;
}

long _x64_syscall6(long n,
                   long a1,
                   long a2,
                   long a3,
                   long a4,
                   long a5,
                   long a6) {
  long ret;
  register long r10 __asm__("r10") = a4;
  register long r8 __asm__("r8") = a5;
  register long r9 __asm__("r9") = a6;
  __asm__ __volatile__("syscall"
                       : "=a"(ret)
                       : "a"(n), "D"(a1), "S"(a2), "d"(a3), "r"(r10), "r"(r8),
                         "r"(r9)
                       : "rcx", "r11", "memory");
  return ret;
}

int clock_gettime(int  clk_id, void* timespec) {
   return _x64_syscall2(0x107, clk_id, timespec);
}

int close(int fd) { return _x64_syscall1(3, fd); }

void exit(int status) {
  _x64_syscall1(60, status);
  while (1)
    ;
}

int getpid() { return _x64_syscall0(39); }

int kill(int pid, int sig) { return _x64_syscall2(62, pid, sig); }

long lseek(int fd, unsigned long offset, int whence) {
  return _x64_syscall3(8, fd, offset, whence);
}

int open(const char* path, int oflag, int mode) {
  return _x64_syscall3(2, (long)path, oflag, mode);
}

long read(int fd, void* buf, unsigned long n) {
  return _x64_syscall3(0, fd, (long)buf, n);
}

long write(int fd, const void* buf, unsigned long n) {
  return _x64_syscall3(1, fd, (long)buf, n);
}

void* xbrk(void* addr) { return (void*)_x64_syscall1(12, (long)addr); }

void _x64_main(long* args) { exit(main(args[0], (char**)&args[1])); }

/* linux has uses a non standard ABI when it starts a program */
__asm__(
    ".text\n"
    ".global _start\n"
    "_start:\n"
    "	xor %rbp,%rbp\n"
    "	mov %rsp,%rdi\n"
    "	andq $-16,%rsp\n"
    "	call _x64_main\n");

/* ============================================================ */
#elif __i386__
/* ============================================================ */

long _x32_syscall0(long n) {
  long ret;
  __asm__ __volatile__("int $0x80" : "=a"(ret) : "a"(n) : "memory");
  return ret;
}

long _x32_syscall1(long n, long a1) {
  long ret;
  __asm__ __volatile__("int $0x80" : "=a"(ret) : "a"(n), "b"(a1) : "memory");
  return ret;
}

long _x32_syscall2(long n, long a1, long a2) {
  long ret;
  __asm__ __volatile__("int $0x80"
                       : "=a"(ret)
                       : "a"(n), "b"(a1), "c"(a2)
                       : "memory");
  return ret;
}

long _x32_syscall3(long n, long a1, long a2, long a3) {
  long ret;
  __asm__ __volatile__("int $0x80"
                       : "=a"(ret)
                       : "a"(n), "b"(a1), "c"(a2), "d"(a3)
                       : "memory");

  return ret;
}

long _x32_syscall4(long n, long a1, long a2, long a3, long a4) {
  long ret;
  __asm__ __volatile__("int $0x80"
                       : "=a"(ret)
                       : "a"(n), "b"(a1), "c"(a2), "d"(a3), "S"(a4)
                       : "memory");
  return ret;
}

long _x32_syscall5(long n, long a1, long a2, long a3, long a4, long a5) {
  long ret;
  __asm__ __volatile__("int $0x80"
                       : "=a"(ret)
                       : "a"(n), "b"(a1), "c"(a2), "d"(a3), "S"(a4), "D"(a5)
                       : "memory");

  return ret;
}

long _x32_syscall6(long n,
                   long a1,
                   long a2,
                   long a3,
                   long a4,
                   long a5,
                   long a6) {
  long ret;
  __asm__ __volatile__(
      "pushl %7;"
      "push %%ebp;"
      "mov 4(%%esp),%%ebp;"
      "int $0x80;"
      "pop %%ebp; "
      "add $4,%%esp"
      : "=a"(ret)
      : "a"(n), "b"(a1), "c"(a2), "d"(a3), "S"(a4), "D"(a5), "g"(a6)
      : "memory");
  return ret;
}

int clock_gettime(int  clk_id, void* timespec) {
   return _x32_syscall2(0x109, clk_id, timespec);
}

int close(int fd) { return _x32_syscall1(6, fd); }

void exit(int status) {
  _x32_syscall1(1, status);
  while (1)
    ;
}

int getpid() { return _x32_syscall0(20); }

int kill(int pid, int sig) { return _x32_syscall2(37, pid, sig); }

long lseek(int fd, unsigned long offset, int whence) {
  return _x32_syscall3(19, fd, offset, whence);
}

int open(const char* path, int oflag, int mode) {
  return _x32_syscall3(5, (long)path, oflag, mode);
}

long read(int fd, void* buf, unsigned long n) {
  return _x32_syscall3(3, fd, (long)buf, n);
}

long write(int fd, const void* buf, unsigned long n) {
  return _x32_syscall3(4, fd, (long)buf, n);
}

void* xbrk(void* addr) { return (void*)_x32_syscall1(45, (long)addr); }

void _x32_main(long* args) { exit(main(args[0], (char**)&args[1])); }

/* linux has uses a non standard ABI when it starts a program */
__asm__(
    ".text\n"
    ".global _start\n"
    "_start:\n"
    "	xor %ebp,%ebp \n"
    "	mov %esp,%eax \n"
    "	and $-16,%esp \n"
    "	push %eax \n"
    "	call _x32_main\n");

/* ============================================================ */
#elif __aarch64__
/* ============================================================ */

long _a64_syscall0(long n) {
  register long x8 __asm__("x8") = n;
  register long x0 __asm__("x0");
  __asm__ __volatile__("svc 0" : "=r"(x0) : "r"(x8) : "memory", "cc");
  return x0;
}

long _a64_syscall1(long n, long a) {
  register long x8 __asm__("x8") = n;
  register long x0 __asm__("x0") = a;
  __asm__ __volatile__("svc 0" : "=r"(x0) : "r"(x8), "0"(x0) : "memory", "cc");
}

long _a64_syscall2(long n, long a, long b) {
  register long x8 __asm__("x8") = n;
  register long x0 __asm__("x0") = a;
  register long x1 __asm__("x1") = b;
  __asm__ __volatile__("svc 0"
                       : "=r"(x0)
                       : "r"(x8), "0"(x0), "r"(x1)
                       : "memory", "cc");
}

long _a64_syscall3(long n, long a, long b, long c) {
  register long x8 __asm__("x8") = n;
  register long x0 __asm__("x0") = a;
  register long x1 __asm__("x1") = b;
  register long x2 __asm__("x2") = c;
  __asm__ __volatile__("svc 0"
                       : "=r"(x0)
                       : "r"(x8), "0"(x0), "r"(x1), "r"(x2)
                       : "memory", "cc");
}

long _a64_syscall4(long n, long a, long b, long c, long d) {
  register long x8 __asm__("x8") = n;
  register long x0 __asm__("x0") = a;
  register long x1 __asm__("x1") = b;
  register long x2 __asm__("x2") = c;
  register long x3 __asm__("x3") = d;
  __asm__ __volatile__("svc 0"
                       : "=r"(x0)
                       : "r"(x8), "0"(x0), "r"(x1), "r"(x2), "r"(x3)
                       : "memory", "cc");
}

long _a64_syscall5(long n, long a, long b, long c, long d, long e) {
  register long x8 __asm__("x8") = n;
  register long x0 __asm__("x0") = a;
  register long x1 __asm__("x1") = b;
  register long x2 __asm__("x2") = c;
  register long x3 __asm__("x3") = d;
  register long x4 __asm__("x4") = e;
  __asm__ __volatile__("svc 0"
                       : "=r"(x0)
                       : "r"(x8), "0"(x0), "r"(x1), "r"(x2), "r"(x3), "r"(x4)
                       : "memory", "cc");
}

long _a64_syscall6(long n, long a, long b, long c, long d, long e, long f) {
  register long x8 __asm__("x8") = n;
  register long x0 __asm__("x0") = a;
  register long x1 __asm__("x1") = b;
  register long x2 __asm__("x2") = c;
  register long x3 __asm__("x3") = d;
  register long x4 __asm__("x4") = e;
  register long x5 __asm__("x5") = f;
  __asm__ __volatile__("svc 0"
                       : "=r"(x0)
                       : "r"(x8), "0"(x0), "r"(x1), "r"(x2), "r"(x3), "r"(x4),
                         "r"(x5)
                       : "memory", "cc");
}

int clock_gettime(int  clk_id, void* timespec) {
   return _a64_syscall2(0x71, clk_id, timespec);
}

int close(int fd) { return _a64_syscall1(57, fd); }

void exit(int status) {
  _a64_syscall1(93, status);
  while (1)
    ;
}

int getpid() { return _a64_syscall0(172); }

int kill(int pid, int sig) { return _a64_syscall2(129, pid, sig); }

long lseek(int fd, unsigned long offset, int whence) {
  return _a64_syscall3(62, fd, offset, whence);
}

int openat(const char* path, int oflag, int mode) {
  return _a64_syscall4(5, -100 /* AT_FDCWD */, (long)path, oflag, mode);
}

long read(int fd, void* buf, unsigned long n) {
  return _a64_syscall3(63, fd, (long)buf, n);
}

long write(int fd, const void* buf, unsigned long n) {
  return _a64_syscall3(64, fd, (long)buf, n);
}

void* xbrk(void* addr) { return (void*)_a64_syscall1(214, (long)addr); }

void _a64_main(long* args) { exit(main(args[0], (char**)&args[1])); }

/* linux has uses a non standard ABI when it starts a program */
__asm__(
    ".text\n"
    ".global _start\n"
    ".type _start, %function\n"
    "_start:\n"
    "	mov x29, #0\n"
    "	mov x30, #0\n"
    "	mov x0, sp\n"
    "	and sp, x0, #-16\n"
    "	b _a64_main\n");

/* ============================================================ */
#elif __arm__
/* ============================================================ */

long _a32_syscall0(long n) {
  register long r7 __asm__("r7") = n;
  register long r0 __asm__("r0");
  __asm__ __volatile__("svc 0" : "=r"(r0) : "r"(r7) : "memory");
  return r0;
}

long _a32_syscall1(long n, long a) {
  register long r7 __asm__("r7") = n;
  register long r0 __asm__("r0") = a;
  __asm__ __volatile__("svc 0" : "=r"(r0) : "r"(r7), "0"(r0) : "memory");
  return r0;
}

long _a32_syscall2(long n, long a, long b) {
  register long r7 __asm__("r7") = n;
  register long r0 __asm__("r0") = a;
  register long r1 __asm__("r1") = b;
  __asm__ __volatile__("svc 0"
                       : "=r"(r0)
                       : "r"(r7), "0"(r0), "r"(r1)
                       : "memory");
  return r0;
}

long _a32_syscall3(long n, long a, long b, long c) {
  register long r7 __asm__("r7") = n;
  register long r0 __asm__("r0") = a;
  register long r1 __asm__("r1") = b;
  register long r2 __asm__("r2") = c;
  __asm__ __volatile__("svc 0"
                       : "=r"(r0)
                       : "r"(r7), "0"(r0), "r"(r1), "r"(r2)
                       : "memory");
  return r0;
}

long _a32_syscall4(long n, long a, long b, long c, long d) {
  register long r7 __asm__("r7") = n;
  register long r0 __asm__("r0") = a;
  register long r1 __asm__("r1") = b;
  register long r2 __asm__("r2") = c;
  register long r3 __asm__("r3") = d;
  __asm__ __volatile__("svc 0"
                       : "=r"(r0)
                       : "r"(r7), "0"(r0), "r"(r1), "r"(r2), "r"(r3)
                       : "memory");
  return r0;
}

long _a32_syscall5(long n, long a, long b, long c, long d, long e) {
  register long r7 __asm__("r7") = n;
  register long r0 __asm__("r0") = a;
  register long r1 __asm__("r1") = b;
  register long r2 __asm__("r2") = c;
  register long r3 __asm__("r3") = d;
  register long r4 __asm__("r4") = e;
  __asm__ __volatile__("svc 0"
                       : "=r"(r0)
                       : "r"(r7), "0"(r0), "r"(r1), "r"(r2), "r"(r3), "r"(r4)
                       : "memory");
  return r0;
}

long _a32_syscall6(long n, long a, long b, long c, long d, long e, long f) {
  register long r7 __asm__("r7") = n;
  register long r0 __asm__("r0") = a;
  register long r1 __asm__("r1") = b;
  register long r2 __asm__("r2") = c;
  register long r3 __asm__("r3") = d;
  register long r4 __asm__("r4") = e;
  register long r5 __asm__("r5") = f;
  __asm__ __volatile__("svc 0"
                       : "=r"(r0)
                       : "r"(r7), "0"(r0), "r"(r1), "r"(r2), "r"(r3), "r"(r4),
                         "r"(r5)
                       : "memory");
  return r0;
}

int clock_gettime(int  clk_id, void* timespec) {
   return _a32_syscall2(0xe4, clk_id, timespec);
}

int close(int fd) { return _a32_syscall1(6, fd); }

void exit(int status) {
  _a32_syscall1(1, status);
  while (1)
    ;
}

int getpid() { return _a32_syscall0(20); }

int kill(int pid, int sig) { return _a32_syscall2(37, pid, sig); }

long lseek(int fd, unsigned long offset, int whence) {
  return _a32_syscall3(19, fd, offset, whence);
}

int open(const char* path, int oflag, int mode) {
  return _a32_syscall3(5, (long)path, oflag, mode);
}

long read(int fd, void* buf, unsigned long n) {
  return _a32_syscall3(3, fd, (long)buf, n);
}

long write(int fd, const void* buf, unsigned long n) {
  return _a32_syscall3(4, fd, (long)buf, n);
}

void* xbrk(void* addr) { return (void*)_a32_syscall1(45, (long)addr); }

void _a32_main(long* args) { exit(main(args[0], (char**)&args[1])); }

/* linux has uses a non standard ABI when it starts a program */
__asm__(
    ".text\n"
    ".global _start\n"
    ".type _start, %function\n"
    "_start:\n"
    "	mov fp, #0 \n"
    "	mov lr, #0 \n"
    "	mov a1, sp \n"
    "   and sp, a1, #-16 \n"
    "	bl _a32_main\n");
#else
#error "unsupported architecture"
#endif

#if __test_main__
int main(int argc, char** argv) {
  write(1, "hello world\n", 12);
  for (int i = 0; i < argc; ++i) {
    char* s = argv[i];
    int len = 0;
    while (s[len] != 0) ++len;
    write(1, s, len);
    write(1, "\n", 1);
  }
  return 0;
}
#endif
