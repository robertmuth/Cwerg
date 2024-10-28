/*
 * this file reflects the std_lib
 */
#include "std_types.h"

#define SEEK_END 2
#define SEEK_CUR 1
#define SEEK_SET 0

#define O_RDONLY 0
#define O_WRONLY 1
#define O_RDWR 2
#define O_CREAT 64
#define O_TRUNC 512


extern ssize_t write_s(int fd, const char* s);
extern ssize_t write_x(int fd, uint32_t val);
extern ssize_t write_u(int fd, uint32_t val);
extern ssize_t write_d(int fd, int32_t sval);
extern ssize_t write_c(int fd, uint8_t c);

extern void* memset(void* ptr, int value, size_t n);
extern void* memcpy(void* dst, const void* src, size_t n);

extern void* malloc(size_t size);
extern void free(void* ptr);

extern void abort();

// useful for tests - does not really belong here
extern void print_ln(const char* s, size_t n);
extern void print_s_ln(const char* s);
extern void print_d_ln(int32_t n);
extern void print_u_ln(uint32_t n);
extern void print_x_ln(uint32_t n);
extern void print_c_ln(uint8_t c);
