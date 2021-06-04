
 #include "std_lib.h"   // needed because printf may be rewritten to call helpers defined here
  
  
int printf( const char *restrict format, ... );

// computes number of primes between [3 - SIZE]
#define SIZE 1000000

char is_prime[SIZE];

unsigned sieve (int repeats) {
  unsigned num_primes; 

  for (unsigned n = 0; n < repeats; n++) {
    num_primes = 0;
    for (int i = 0; i < SIZE; i++) is_prime[i] = 1;
    for (int i = 0; i < SIZE; i++)
      if (is_prime[i]) {
        unsigned prime = i + i + 3;
        for (unsigned k = i + prime; k < SIZE; k += prime) is_prime[k] = 0;
        num_primes++;
      }
  }
  return num_primes;
}


int main() {
  if (sieve(1) != 148932) abort();
  return 0;
}
