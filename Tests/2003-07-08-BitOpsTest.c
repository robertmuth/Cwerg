int printf( const char *restrict format, ... );


void test(unsigned int A, unsigned int B, unsigned int C, unsigned int D) {
  printf("%x %x %x %x\n", A, B, C, D);
  unsigned int bxor, bor, band, bandnot, bornot;
  bxor = A ^ B ^ C ^ D;
  bor  = A | B | C | D;
  band = A & B & C & D;
  bandnot = (A & ~B) ^ (C & ~D);
  bornot  = (A | ~B) ^ (C | ~D);
  
  printf("%x %x %x %x %x\n", bxor, bor, band, bandnot, bornot);
}

int main() {
  test(7, 8, (unsigned int)-5, 5);
  return 0;
}
