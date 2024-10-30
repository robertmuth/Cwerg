#include "std_lib.h"   // needed because printf may be rewritten to call helpers defined here


int
main (void)
{
  long long   x;
  int         n;

  // requires 64bit
  //if (sizeof (long long) < 8)
  //  return (0);

  n = 9;
  x = (((long long) n) << 55) / 0xff;

  if (x == 0)
    abort ();

  x = (((long long) 9) << 55) / 0xff;

  if (x == 0)
    abort ();

  return 0;
}
