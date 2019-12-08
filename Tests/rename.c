int printf( const char *restrict format, ... );


int test() {
  printf("regular");
  int a = 6;
  {
    int a = 7;
    {
      int a = 8;
      a += 1;
      printf ("%d\n", a);
    }
    a += 1;
    printf ("%d\n", a);
  }
  a += 1;
  printf ("%d\n", a); 
  {
    int a = 9;
    {
      int a = 10;
      a += 1;
      printf ("%d\n", a);
    }
    a += 1;
    printf ("%d\n", a);
  }
  a += 1;
  printf ("%d\n", a);

  printf ("static\n");
  int static as = 6;
  {
    int static as = 7;
    {
      int static as = 8;
      as += 1;
      printf ("%d\n", as);
    }
    as += 1;
    printf ("%d\n", as);
  }
  as += 1;
  printf ("%d\n", as); 
  {
    int static as = 9;
    {
      int static as = 10;
      as += 1;
      printf ("%d\n", as);
    }
    as += 1;
    printf ("%d\n", as);
  }
  as += 1;
  printf ("%d\n", as);
}

int main() {
  test();
  test();
}
