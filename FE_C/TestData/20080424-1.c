#include "std_lib.h"   // needed because printf may be rewritten to call helpers defined here

int g[48][3][3];

/* void bar(int [3][3], int[][3]); */
 
void bar (int x[3][3], int y[3][3])
{
  static int i;
  if (x != g[i + 8] || y != g[i])
    abort ();
  i = i + 1;
}

void foo (int x[][3][3])
{
  int i;
  for (i = 0; i < 8; i++)
    {
      int k = i + 8;
      bar (x[k], x[k - 8]);
    }
}

int main ()
{
  foo (g);
  return 0;
}
