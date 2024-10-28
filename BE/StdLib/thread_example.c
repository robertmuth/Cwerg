// Compile like so:
// gcc thread_example.c -Wall -O3 -static -g -nostdlib  -mfsgsbase 
// aarch64-linux-gnu-gcc thread_example.c  -Wall -O3 -static -g -nostdli
// arm-linux-gnueabihf-gcc thread_example.c  -Wall -O3 -static -g -nostdlib
#include <stdint.h>

#include "syscall.c"

// From /usr/include/linux/sched.h
#define CSIGNAL 0x000000ff     /* signal mask to be sent at exit */
#define CLONE_VM 0x00000100    /* set if VM shared between processes */
#define CLONE_FS 0x00000200    /* set if fs info shared between processes */
#define CLONE_FILES 0x00000400 /* set if open files shared between processes \
                                */
#define CLONE_SIGHAND \
  0x00000800 /* set if signal handlers and blocked signals shared */
#define CLONE_PIDFD 0x00001000 /* set if a pidfd should be placed in parent */
#define CLONE_PTRACE \
  0x00002000 /* set if we want to let tracing continue on the child too */
#define CLONE_VFORK                                                           \
  0x00004000 /* set if the parent wants the child to wake it up on mm_release \
              */
#define CLONE_PARENT \
  0x00008000 /* set if we want to have the same parent as the cloner */
#define CLONE_THREAD 0x00010000         /* Same thread group? */
#define CLONE_NEWNS 0x00020000          /* New mount namespace group */
#define CLONE_SYSVSEM 0x00040000        /* share system V SEM_UNDO semantics */
#define CLONE_SETTLS 0x00080000         /* create a new TLS for the child */
#define CLONE_PARENT_SETTID 0x00100000  /* set the TID in the parent */
#define CLONE_CHILD_CLEARTID 0x00200000 /* clear the TID in the child */
#define CLONE_DETACHED 0x00400000       /* Unused, ignored */
#define CLONE_UNTRACED                                                      \
  0x00800000 /* set if the tracing process can't force CLONE_PTRACE on this \
                clone */
#define CLONE_CHILD_SETTID 0x01000000 /* set the TID in the child */
#define CLONE_NEWCGROUP 0x02000000    /* New cgroup namespace */
#define CLONE_NEWUTS 0x04000000       /* New utsname namespace */
#define CLONE_NEWIPC 0x08000000       /* New ipc namespace */
#define CLONE_NEWUSER 0x10000000      /* New user namespace */
#define CLONE_NEWPID 0x20000000       /* New pid namespace */
#define CLONE_NEWNET 0x40000000       /* New network namespace */
#define CLONE_IO 0x80000000           /* Clone io context */

#define NUM_THREADS 10
#define STACK_SIZE 65536
#define TLS_SIZE 65536

// This collection of flags was taken from the qemu-linux-user source code:
// https://github.com/qemu/qemu/blob/9c721291506c037d934900a6167dc3bf4a8f51a6/linux-user/syscall.c#L159
// Other combination of flags will result in a EINVAL (-22)
#define CLONE_FLAGS                                                   \
  (CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND | CLONE_THREAD | \
   CLONE_SYSVSEM | CLONE_SETTLS)
//#define CLONE_FLAGS 0x111

uint8_t stacks[STACK_SIZE * NUM_THREADS] __attribute__((aligned(256)));

uint8_t tlss[TLS_SIZE * NUM_THREADS] __attribute__((aligned(256)));

int pids[NUM_THREADS];

unsigned results[NUM_THREADS];

struct timespec {
  uint64_t tv_sec; /* seconds */
  long tv_nsec;    /* nanoseconds */
};

int sleep(int secs) {
  struct timespec ts = {secs, 0};
  return nanosleep(&ts, 0);
}

void print(char* buffer) {
  int size = 0;
  while (buffer[size]) ++size;
  write(1, buffer, size);
}

void printx(unsigned long x) {
  char buffer[64];
  int i = 63;
  buffer[i] = 0;
  --i;
  do {
    int c = x & 0xf;
    buffer[i] = c > 9 ? (c - 10 + 'a') : (c + '0');
    --i;
    x >>= 4;
  } while (x);
  print(buffer + i + 1);
}

void report(char* tag, unsigned i, unsigned id) {
  print(tag);
  print(" [");
  printx(i);
  print("] ");
  printx(id);
  print("\n");
}

int childFunc(int i) {
  sleep(1);
  long tls = -1;
#if __x86_64__
  tls = __builtin_ia32_rdfsbase64();
#endif
  int pid = getpid();
  report("child", i, pid);
  printx((long) tls);
  print ("\n");
  results[i] = i;
  return 0;
}

void spawn(int i) {
  uint8_t* new_stack = &stacks[(i + 1) * STACK_SIZE] - 256;
  void* new_tls = &tlss[i * TLS_SIZE];  
  print("spawning ");
  printx((long) new_stack);
  print (" ");
  printx((long) new_tls);
  print ("\n");

  report("clone-flags and stack", CLONE_FLAGS, (long)new_stack);
  int ret = clone(CLONE_FLAGS, new_stack, 0, 0, new_tls);
  // Note, we want i to end up in a register here. If it is on the stack
  // it may get overridden by the next round of spawning.
  // So this works best with higher optimization levels.
  if (ret == 0) {
    childFunc(i);
    exit(0);
  } else {
    pids[i] = ret;
  }
  report("cloned", i, pids[i]);
}

int main(int argc, char* argv[]) {
  report("flags",CLONE_FLAGS   ,  CLONE_FLAGS   );
  for (int i = 0; i < NUM_THREADS; i++) {
    spawn(i);
  }

  sleep(2);
  report("cloning done", 0, 0);
  sleep(1);

  for (int i = 0; i < NUM_THREADS; i++) {
    report("wait", i, results[i]);
    wait4(pids[i], 0, 0, 0);
  }

  return 0;
}
