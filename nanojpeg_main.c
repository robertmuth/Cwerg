

#include "nanojpeg.c"

int printf( const char *restrict format, ... );
void* malloc(unsigned long size);
char*  itoa (int value, char* str, int base);



#define FILE void

FILE* fopen(const char *pathname, const char *mode);
int fclose(FILE* stream);
int fseek(FILE* stream, long offset, int whence);
long ftell(FILE* stream);

unsigned long fread(void *ptr, unsigned long size, unsigned long nmemb, FILE* stream);
unsigned long fwrite(void *ptr, unsigned long size, unsigned long nmemb, FILE* stream);
int fputs(const char *restrict s, FILE *stream);

const int SEEK_END = 2;
const int SEEK_SET = 0;

void fwrite_d(FILE* f, int a) {
  char buf[64];
  int i = 63;
  buf[i] = 0;
  --i;

  // assume only pos a for now
  do {
        buf[i] = '0' + a % 10;
        --i;
        a /= 10;
  } while (a != 0);
  fputs(&buf[i+1], f);
}

int main(int argc, char* argv[]) {
    int size;
    char *buf;
    FILE *f;

    if (argc < 2) {
        printf("Usage: %s <input.jpg> [<output.ppm>]\n", argv[0]);
        return 2;
    }
    f = fopen(argv[1], "rb");
    if (!f) {
        printf("Error opening the input file.\n");
        return 1;
    }
    fseek(f, 0, SEEK_END);
    size = (int) ftell(f);
    buf = (char*) malloc(size);
    fseek(f, 0, SEEK_SET);
    size = (int) fread(buf, 1, size, f);
    fclose(f);

    njInit();
    if (njDecode(buf, size)) {
        free((void*)buf);
        printf("Error decoding the input file.\n");
        return 1;
    }
    free((void*)buf);

    f = fopen((argc > 2) ? argv[2] : (njIsColor() ? "nanojpeg_out.ppm" : "nanojpeg_out.pgm"), "wb");
    if (!f) {
        printf("Error opening the output file.\n");
        return 1;
    }
    fputs(njIsColor() ? "P6\n" : "P5\n", f);
    fwrite_d(f, njGetWidth());
    fputs(" ", f);
    fwrite_d(f, njGetHeight());
    fputs("\n", f);
    fputs("255\n", f);

    fwrite(njGetImage(), 1, njGetImageSize(), f);
    fclose(f);
    njDone();
    return 0;
}
