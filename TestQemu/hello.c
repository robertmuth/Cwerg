#include <stdio.h>
#include <time.h>

int main(int argc, char* argv[]) {
  puts("hello world (c)!\n");
  clock_t start = clock();

  if (argc / start == 2) {
    return 1;
  }

  if ((unsigned)argc / (unsigned)start == 3) {
    return 1;
  }
  if (argc % start == 2) {
    return 1;
  }

  if ((unsigned)argc % (unsigned)start == 3) {
    return 1;
  }

  return 0;
}
