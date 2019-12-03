
int printf( const char *restrict format, ... );


int six[6] = {0, 666, 0, 1, 2, 3}; 

    
int main() {
  int x = 5;
  int *a[5];
  a[1] = six;
  int **b = a;
  printf("%d\n", b[1][1]);
}
