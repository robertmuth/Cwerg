int printf( const char *restrict format, ... );


int main(int argc, char** argv)
{
  char  c1 = 100;  /* 100 = 'd' */
  short s1 = -769; /* 0xfcff = -769 */
  
  unsigned char ubc0 = (unsigned char) c1;      /* 100 = 'd' */
  unsigned char ubs0 = (unsigned char) s1;                     /* 0xff = 255 */
  unsigned char ubs1 = ubs0+1;                         /* ((uint8) 0xff) + 1) = 0 */

  signed char  bs0  = (unsigned char) ubs0;                    /* (int8) 0xff = -1 */
  signed char  bs1  = (unsigned char) (ubs0 + 1U);             /* (int8) (0xff + 0x1) = 0 */

  unsigned char  uc2 = (unsigned char) c1;      /* 100 = 'd' */
  unsigned short us2 = (unsigned short) s1;     /* 0xfcff = 64767 */

  int ic3 = (int) c1;                           /* 100 = 'd' */
  int is3 = (int) s1;                           /* 0xfffffcff = -769 */
  int is4 = ((int) ubs0) + 1;                   /* ((int) 0xff) + 1 = 256 */
  int is5 = ((int)  bs0) + 1;                   /* ((int) -1)   + 1 = 0 */

  unsigned int uic4 = (unsigned int) c1;        /*  100 = 'd' */
  unsigned int uis4 = (unsigned int) s1;        /* 0xfffff7ff = 4294966527 */
  
  printf("ubc0 = '%c'\t   [0x%x]\n", ubc0, ubc0);
  printf("ubs0 = %u\t   [0x%x]\n",   ubs0, ubs0);
  printf("ubs1 = %u\t   [0x%x]\n",   ubs1, ubs1);
  printf("bs0  = %d\t   [0x%x]\n",   bs0,  bs0);
  printf("bs1  = %d\t   [0x%x]\n",   bs1,  bs1);
  printf("c1   = '%c'\t   [0x%x]\n", c1,   c1);
  printf("s1   = %d\t   [0x%x]\n",   s1,   s1);
  printf("uc2  = '%c'\t   [0x%x]\n", uc2,  uc2);
  printf("us2  = %u\t   [0x%x]\n",   us2,  us2);
  printf("ic3  = '%c'\t   [0x%x]\n", ic3,  ic3);
  printf("is3  = %d\t   [0x%x]\n",   is3,  is3);
  printf("is4  = %d\t   [0x%x]\n",   is4,  is4);
  printf("is5  = %d\t   [0x%x]\n",   is5,  is5);
  printf("uic4 = '%c'\t   [0x%x]\n", uic4, uic4);
  printf("uis4 = %u  [0x%x]\n",   uis4, uis4);
  
  return 0;
}
