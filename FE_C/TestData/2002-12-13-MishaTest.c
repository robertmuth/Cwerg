int printf( const char *restrict format, ... );

void sum(short* to, short* from, short count) {
  int i;
  for (i = 0; i != count; ++i)
    *to += *from++;
}


int main() {
  short Array[2];
  short Sum = 0;
  int i;

  for (i = 0; i != 2; ++i)
    Array[i] = i;

  sum(&Sum, Array, 2);

  printf("Sum is %d\n", Sum);
  return 0;
}
