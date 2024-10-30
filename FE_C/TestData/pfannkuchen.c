/* The Computer Language Benchmarks Game
 * https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
 *
 * contributed by Ledrug Katz
 *
 */

#include "std_lib.h"
// needed because printf may be rewritten to call helpers defined here

int printf( const char *restrict format, ... );
void abort();

/* this depends highly on the platform.  It might be faster to use
   char type on 32-bit systems; it might be faster to use unsigned. */

#define elem int

elem s[16], t[16];

int maxflips = 0;
int max_n;
int odd = 0;
int checksum = 0;

int flip(elem *s, elem* t)
{
   register int i;
   register elem *x, *y, c;

   for (x = t, y = s, i = max_n; i > 0; i--) {
     *x = *y;
     x += 1;
     y += 1;
   }
   i = 1;
   do {
      for (x = t, y = t + t[0]; x < y; ) {
       c = *x;
       *x = *y;
       x += 1;
       *y = c;
       y -= 1;
     }
     i++;
   } while (t[t[0]]);
   return i;
}

void rotate(int n, elem* s)
{
   elem c;
   register int i;
   c = s[0];
   for (i = 1; i <= n; i++) s[i-1] = s[i];
   s[n] = c;
}

/* Tompkin-Paige iterative perm generation */
void tk(int n, elem* s, elem* t)
{
   int i = 0, f;
   elem c[16];
   for (int x = 0; x < 16; x++) {
     c[x] = 0;
   }

   while (i < n) {
      rotate(i, s);
      if (c[i] >= i) {
         c[i] = 0;
         i += 1;
         continue;
      }

      c[i] = c[i] + 1;
      i = 1;
      odd = ~odd;
      if (s[0] != 0) {
        if ( s[s[0]]  != 0) {
          f = flip(s, t);
        } else {
          f = 1;
        }
         if (f > maxflips) maxflips = f;
         if (odd != 0) {
           checksum = checksum - f;
         } else {
            checksum = checksum + f;
         }
      }
   }
}

int main(int argc, char **v)
{
   int i;

   max_n = 11;

   for (i = 0; i < max_n; i++) s[i] = i;
   tk(max_n, s, t);
   printf("max_n: %d crc: %d  flips: %d\n", max_n, checksum,maxflips);
   if (checksum != 556355) abort();
   if (maxflips != 51) abort();

   return 0;
}
