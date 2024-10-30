#include "std_lib.h"   // needed because printf may be rewritten to call helpers defined here


int printf( const char *restrict format, ... );

  
int SumArray(int Array[], int Num) {
  unsigned int i, Result = 0;
  Array[34] = 1234;

  for (i = 0; i < Num; ++i) {
    Result += Array[i];
  }

  return Result;
}

int main() {
  printf("sizeof int %u\n", (unsigned)sizeof(int));
  int *Array = (int*)malloc(sizeof(int) * (unsigned long) 100);
  int i;

  for (i = 0; i < 100; i += 2) {
  	Array[i] = i*4;
  }
  for (i = 1; i < 100; i += 2)
    Array[i] = i*2;

  printf("Produced: %d\n", SumArray(Array, 100));
  return 0;
}
