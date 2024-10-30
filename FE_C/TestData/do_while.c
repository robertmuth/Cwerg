
long write(int fd, char* buf, unsigned long len);

long write_uu(int fd, unsigned val) {
  char buffer[16];
  unsigned long pos = sizeof(buffer);
  do {
    --pos;
    buffer[pos] = '0' + val % 10;
    val /= 10;
  } while (val != 0);

  return write(fd, &buffer[pos], sizeof(buffer) - pos);
}


long write_dd(int fd, int sval) {
  if (sval >= 0) {
    return write_uu(fd, (unsigned)sval);
  }

  unsigned val = (unsigned)-sval;
  char buffer[16];
  unsigned long pos = sizeof(buffer);
  do {
    --pos;
    buffer[pos] = '0' + val % 10;
    val /= 10;
  } while (val != 0);

  --pos;
  buffer[pos] = '-';
  return write(fd, &buffer[pos], sizeof(buffer) - pos);
}


int main() {
  write_dd(1, 1);
  write(1, "\n", 1);
  write_dd(1, -1);
  write(1, "\n", 1);
  write_dd(1, 101);
  write(1, "\n", 1);
  write_dd(1, -101);
  write(1, "\n", 1);
  write_dd(1, 1001);
  write(1, "\n", 1);
  write_dd(1, -1001);
  write(1, "\n", 1);
  return 0;
}
