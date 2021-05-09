#include "std_lib.h"   // needed because printf may be rewritten to call helpers defined here

int printf( const char *restrict format, ... );

struct nj_code {
    unsigned char bits, code;
};

struct nj_component {
    int cid;
    int ssx, ssy;
    int width, height;
    int stride;
    int qtsel;
    int actabsel, dctabsel;
    int dcpred;
    const char *pixels;
};

struct nj_ctx {
    const unsigned char *pos;
    int error;
    int ncomp;
    struct nj_component comp[3];
    int qtused, qtavail;
    unsigned char qtab[4][64];
    struct nj_code vlctab[4][65536];
    int buf, bufbits;
    int block[64];
    int rstinterval;
    const char *rgb;
};

struct nj_ctx nj;

const char* njGetImage(void) {
  if (nj.ncomp == 0)
    return nj.comp[0].pixels;
  else
    return nj.rgb;
}

int main () {
  nj.comp[0].pixels = "hello";
  nj.comp[1].pixels = "world";

  const char* p = njGetImage();

  printf("%s %s!\n", p, nj.comp[1].pixels);
  
  return 0;
}
  
