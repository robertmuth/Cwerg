

/* -*- mode: c -*-
 * $Id: heapsort.gcc,v 1.10 2001/05/08 02:46:59 doug Exp $
 * http://www.bagley.org/~doug/shootout/
 */

//#include <stdlib.h>
//#include <stdio.h>

extern void* malloc(unsigned long size);
extern void free(void* ptr);

extern void abort();

#define IM 139968
#define IA   3877
#define IC  29573

double
gen_random(double max) {
    static long last = 42;
    last = (last * IA + IC) % IM;
    return max * last / IM;
}

void
heap_sort(int n, double *ra) {
    int i, j;
    int ir = n;
    int l = (n >> 1) + 1;
    double rra;

    for (;;) {
    if (l > 1) {
      --l;
        rra = ra[l];
    } else {
        rra = ra[ir];
        ra[ir] = ra[1];
	--ir;
	if (ir == 1) {
	  ra[1] = rra;
	  return;
        }
    }
    i = l;
    j = l << 1;
    while (j <= ir) {
        if (j < ir && ra[j] < ra[j+1]) {
	  ++j;
	}
        if (rra < ra[j]) {
	  ra[i] = ra[j];
	  i = j;
	  j += i;
        } else {
	  j = ir + 1;
        }
    }
    ra[i] = rra;
    }
}

// #define N  20000000
#define N  20
int
main(int argc, char *argv[]) {

    double* ary = (double *)malloc((N) * sizeof(double));
    for (int i=1; i<N+1; i++) {
      ary[i] = gen_random(1);
    }

    heap_sort(N, ary);
    for (int i=1; i<N; i++) {
      if (ary[i] > ary[i+1]) {
	// printf("mismatch at %d\n", i);
	abort();
      }
    }

    // if (ary[N] != 0x1.ffff10454bf81p-1) { abort(); }
    // printf("%a\n", ary[N]);

    free(ary);
    return(0);
}
