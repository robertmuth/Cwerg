

#include "nanojpeg.c"

#include <stdio.h>



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
    fprintf(f, "P%d\n%d %d\n255\n", njIsColor() ? 6 : 5, njGetWidth(), njGetHeight());
    fwrite(njGetImage(), 1, njGetImageSize(), f);
    fclose(f);
    njDone();
    return 0;
}
