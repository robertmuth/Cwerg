int printf( const char *restrict format, ... );

void test(unsigned X, unsigned Y) {
  printf("%u %u %u %u\n", X, Y, X / (8 << (Y&15)), X % (8 << (Y&15)));
}

int i;
int main(void) {
  long long l;

  for(i=10; i<139045193; i*=-3) {
    test(i, i^12345);
    i++;
  }

  return(0);
}

