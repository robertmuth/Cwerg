int printf( const char *restrict format, ... );
void* malloc(unsigned long size);
  
int SumArray(int Array[], int Num) {
  unsigned int i, Result = 0;
  Array[34] = 1234;

  for (i = 0; i < Num; ++i) {
    Result += Array[i];
  }

  return Result;
}

int main() {
  printf("sizeof int %lu\n", sizeof(int));
  int *Array = (int*)malloc(sizeof(int) * 100);
  int i;

  for (i = 0; i < 100; i += 2) {
  	Array[i] = i*4;
  }
  for (i = 1; i < 100; i += 2)
    Array[i] = i*2;

  printf("Produced: %d\n", SumArray(Array, 100));
  return 0;
}
