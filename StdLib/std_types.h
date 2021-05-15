/* This file is #included by every code emitted by CodeGenC/codegen.py
   I represents a very poor man's libc.
   The intention is to get simple programs to work not to be pretty or complete.
 */

// We basically assume ilp32 or lp64
// see https://en.wikipedia.org/wiki/64-bit_computing#64-bit_data_models
// Note: dump predefined symbols like so: gcc -dM -m32 -E - < /dev/null

#if __SIZEOF_LONG_LONG__ != 8
#error "unexpected long long size"
#endif

#if __SIZEOF_INT__ != 4
#error "unexpected int size"
#endif

#if __SIZEOF_SHORT__ != 2
#error "unexpected int size"
#endif

#if __SIZEOF_LONG__ != __SIZEOF_POINTER__
#error "unexpected long vs pointer size"
#endif

// Wouldn't it be nice to have typedefs
#define uint8_t unsigned char
#define uint16_t unsigned short
#define uint32_t unsigned int
#define uint64_t unsigned long long

#define int8_t signed char
#define int16_t signed short
#define int32_t signed int
#define int64_t signed long long

#define size_t unsigned long
#define ssize_t signed long

// syscalls
extern int64_t lseek64(int fd, int64_t offset, int whence);
extern ssize_t lseek(int fd, size_t offset, int whence);
extern int32_t open(const char* path, int oflag, int mode);
extern int32_t close(int fd);
extern ssize_t read(int fd, void* buf, size_t n);
extern ssize_t write(int fd, const void* buf, size_t n);

extern char* xbrk(char* addr);  // maps to linux brk (which differs from posix brk)
extern void exit(int status);
extern int32_t kill(int pid, int signal);
extern int32_t getpid();
