int printf( const char *restrict format, ... );

int main() {
  unsigned long long NX = 124, X;

  do {
    X = NX;
    printf("%llu = %f  %lld = %f\n", X, (double)X, X, (double)(signed long long)X);
    NX += 1ULL << 60;
  } while (X < NX);

  return 0;
}
