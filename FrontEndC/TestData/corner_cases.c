int printf( const char *restrict format, ... );

int main() {
  int a = 6;
  int c = 3;
  int b = c += a;
  a += 1;
  for (int x = 0; ++c, x < 10; ++x) {
    printf("%d\n", x);
  }
  label:
  b += 5;
  c += 6;
  {
  other:
    ;
  }
  int x;
  for (; ; ) {
    break;
  }
  printf("result: %d\n", b + c);
  return 0;
}


