extern int printf(const char *str, ...);

int main() {
  char title[] = "foo and stuff\n";
  printf("%s", title);
  return 0;
}
