/* This file is #included by every code emitted by CodeGenC/codegen.py
   I represents a very poor man's libc.
   The intention is to get simple programs to work not to be pretty or complete.
 */

// We basically assume ilp32 or lp64
// see https://en.wikipedia.org/wiki/64-bit_computing#64-bit_data_models
// Note: dump predefined symbols like so: gcc -dM -m32 -E - < /dev/null

#include "std_lib.h"

ssize_t write_s(int fd, const char* s) {
  size_t len = 0;
  while (s[len] != 0) len += 1;
  return write(fd, s, len);
}

ssize_t write_x(int fd, uint32_t val) {
  char buffer[16];
  size_t pos = sizeof(buffer);
  do {
    --pos;
    unsigned digit = val % 16;
    if (digit <= 9) {
      buffer[pos] = '0' + digit;
    } else {
      buffer[pos] = 'a' - 10 + digit;
    }
    val /= 16;
  } while (val != 0);

  return write(fd, &buffer[pos], sizeof(buffer) - pos);
}

ssize_t write_u(int fd, uint32_t val) {
  char buffer[16];
  size_t pos = sizeof(buffer);
  do {
    --pos;
    buffer[pos] = '0' + val % 10;
    val /= 10;
  } while (val != 0);

  return write(fd, &buffer[pos], sizeof(buffer) - pos);
}

ssize_t write_d(int fd, int32_t sval) {
  if (sval >= 0) {
    return write_u(fd, (unsigned)sval);
  }

  unsigned val = (unsigned)-sval;
  char buffer[16];
  size_t pos = sizeof(buffer);
  do {
    --pos;
    buffer[pos] = '0' + val % 10;
    val /= 10;
  } while (val != 0);

  --pos;
  buffer[pos] = '-';
  return write(fd, &buffer[pos], sizeof(buffer) - pos);
}

ssize_t write_c(int fd, uint8_t c) {
  char buffer[16];
  buffer[0] = c;
  return (int)write(fd, buffer, (size_t)1);
}

void print_ln(const char* s, size_t n) {
  write(1, s, n);
  write_c(1, (uint8_t)'\n');
}

void print_s_ln(const char* s) {
  write_s(1, s);
  write_c(1, (uint8_t)'\n');
}

void print_d_ln(int32_t n) {
  write_d(1, n);
  write_c(1, (uint8_t)'\n');
}

void print_u_ln(uint32_t n) {
  write_u(1, n);
  write_c(1, (uint8_t)'\n');
}

void print_x_ln(uint32_t n) {
  write_x(1, n);
  write_c(1, (uint8_t)'\n');
}

void print_c_ln(uint8_t c) {
  write_c(1, c);
  write_c(1, (uint8_t)'\n');
}

void* memset(void* ptr, int value, size_t n) {
  for (int i = 0; i < n; i += 1) {
    ((char*)ptr)[i] = value;
  }
  return ptr;
}

void* memcpy(void* dst, const void* src, size_t n) {
  for (int i = 0; i < n; i += 1) {
    ((char*)dst)[i] = ((char*)src)[i];
  }
  return dst;
}

void abort() {
  kill(getpid(), 3);
  exit(1);
}

// extern void* malloc(size_t size);

// TODO: very poor error checking
void* malloc(size_t size) {
  // obviously not thread-safe, zero initialized
  static char* _malloc_start;
  static char* _malloc_end;
  const size_t page_size = 1 << 20;  // 1Mi

  if (_malloc_start == 0) {
    // Note: we could call this with 0 but since we may co-exist with libc
    // this could result in us stepping on libc so we waste a bit of memory
    // to avoid this.
    _malloc_start = xbrk((char*)0);
    _malloc_end = _malloc_start;
  }

  size_t rounded_size = (size + 15) / 16 * 16;
  if (_malloc_start + rounded_size > _malloc_end) {
    size_t increment = (rounded_size + page_size - 1) / page_size * page_size;
    char* new_end = _malloc_end + increment;
    _malloc_end = xbrk(new_end);
    if (_malloc_end != new_end) {
      // TODO: Make some noise
      abort();
    }
  }

  void* result = _malloc_start;
  _malloc_start = _malloc_start + rounded_size;
  return result;
}

void free(void* ptr) {
  // do nothing - hack
}



