/* This file is #included by every code emitted by CodeGenC/codegen.py */

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>

int printf_u(const char* fmt, uint64_t v) { return printf(fmt, v); }
int printf_d(const char* fmt, int64_t v) { return printf(fmt, v); }
int printf_f(const char* fmt, double v) { return printf(fmt, v); }
int printf_c(const char* fmt, char v) { return printf(fmt, v); }
int printf_p(const char* fmt, void* v) { return printf(fmt, v); }
int printf_s(const char* fmt, char* v) { return printf(fmt, v); }

void print_num_ln(uint32_t v) { printf("%d\n", v); }
void print_num(uint32_t v) { printf("%d", v); }

int print(const char* s) { return printf("%s", s); }

void writeln(const char *s, uint32_t len) { 
    write(1, s, len);
    write(1,"\n", 1);
}

