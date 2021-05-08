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
extern size_t lseek(int fd, size_t offset, int whence);
extern int open(const char* path, int oflag, int mode);
extern int close(int fd);
extern ssize_t read(int fd, void* buf, size_t n);
extern ssize_t write(int fd, const void* buf, size_t n);
extern void* sbrk(size_t increment);
extern void exit(int status);
extern int raise(int signal);

#define SEEK_END 2
#define SEEK_CUR 1
#define SEEK_SET 0

#define O_RDONLY 0
#define O_WRONLY 1
#define O_RDWR 2
#define O_CREAT 64
#define O_TRUNC 512

int write_s(int fd, const char* s) {
  size_t len = 0;
  while (s[len] != 0) len += 1;
  return write(fd, s, len);
}

int write_x(int fd, uint32_t val) {
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

int write_u(int fd, uint32_t val) {
  char buffer[16];
  size_t pos = sizeof(buffer);
  do {
    --pos;
    buffer[pos] = '0' + val % 10;
    val /= 10;
  } while (val != 0);

  return write(fd, &buffer[pos], sizeof(buffer) - pos);
}

int write_d(int fd, int32_t sval) {
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

int write_c(int fd, char c) {
  char buffer[16];
  buffer[0] = c;
  return (int)write(fd, buffer, (size_t)1);
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

// extern void* malloc(size_t size);

// TODO: very poor error checking
void* malloc(size_t size) {
  // obviously not thread-safe
  static char* _malloc_start;
  static char* _malloc_end;
  const size_t page_size = 1 << 20;  // 1Mi

  if (_malloc_start == 0) {
    // Note: we could call this with 0 but since we may co-exist with libc
    // this could result in us stepping on libc so we waste a bit of memory
    // to avoid this.
    _malloc_start = (char*) sbrk(page_size);  // we assume this will be nicely aligned
    _malloc_end = _malloc_start;
  }

  size_t rounded_size = (size + 15) / 16 * 16;
  if (_malloc_start + rounded_size > _malloc_end) {
    size_t increment = (rounded_size + page_size - 1) / page_size * page_size;
    _malloc_end = (char*)sbrk(increment);
  }

  void* result = _malloc_start;
  _malloc_start += rounded_size;
  return result;
}

void free(void* ptr) {
  // do nothing - hack
}


void abort() {
  raise(3);
  exit(1);
}

void print_ln(const char* s, uint32_t n) {
  write(1, s, n);
  write_s(1, "\n");
}

void print_s_ln(const char* s) {
  write_s(1, s);
  write_s(1, "\n");
}

void print_d_ln(int32_t n) {
  write_d(1, n);
  write_s(1, "\n");
}

void print_u_ln(uint32_t n) {
  write_u(1, n);
  write_s(1, "\n");
}

void print_x_ln(uint32_t n) {
  write_x(1, n);
  write_s(1, "\n");
}

void print_c_ln(uint8_t c) {
  write_c(1, c);
  write_s(1, "\n");
}


