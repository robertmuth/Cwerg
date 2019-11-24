unsigned short
safe_53 (int short ui1, int short ui2)
{
  return ui1 - ui2;
}

int short
safe_60 (int short left, int right)
{
  return right ? 0 : left >> right;
}

struct S0
{
  int f;
};

struct S1
{
  int f3;
};

struct S2
{
  volatile struct S0 f2;
};

struct S3
{
  int f;
};

int short g_8;
int g_20[][1][0];
int g_37;

struct S2 g_6;

struct S3 g_169;

struct S1 g_177;
struct S2 g_1639[];

char func_13 (unsigned, unsigned short, short);

char func_21 (unsigned char, unsigned, int *);

struct S2 func_1 (void)
{
  int l_2 = 1;
  l_2 && func_13 (0, 0, 0), 0;
  return g_1639[0];
}

char func_13 (unsigned p_, unsigned short p_15, short p_1)
{
  int l_346;
  int *l_701 = &g_37;
  for (l_346 = 2; l_346 >= 0; l_346 -= 1)
    {
      for (; g_177.f3; g_177.f3 += 1);
      for (p_15 = 0; p_15 <= 2; p_15 += 1)
	*l_701 = safe_60 (g_6.f2.f, func_21 (g_169.f, 0, 0)) > 0;
    }
  return 0;
}

char
func_21 (unsigned char p_, unsigned p_2, int *p_24)
{
  int *l_30 = &g_20[0][0][1];
  int **l_29 = &l_30;
  **l_29 = safe_53 (*l_30, g_8);
  return **l_29;
}

int main (void)
{
  func_1 ();
  return 0;
}
