// Check that signed divide by a power of two works for small types

int printf( const char *restrict format, ... );

int main() {
  int i;
  for (i = 0; i != 258; ++i) {
    printf("%d\n", ((signed char)i) / (signed char)2);
  }
  return 0;
}
