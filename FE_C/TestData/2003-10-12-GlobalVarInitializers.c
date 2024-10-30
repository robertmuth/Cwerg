int printf( const char *restrict format, ... );

union { unsigned __l; float __d; } GlobalUnion = { 0x70c00000U };

int main() {
  union { unsigned __l; float __d; } LocalUnion = { 0x7fc00000U };

  printf("%f %f\n", GlobalUnion.__d, LocalUnion.__d);

  return 0;
}



