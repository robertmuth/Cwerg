#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <sstream>

class AssertHelper {
 public:
  AssertHelper(int line, const char* file)
      : line_(line), file_(file) {}

  ~AssertHelper();

  template <typename T>
  AssertHelper& operator<<(const T& value) {
    ss_ << value;
    return *this;
  }

  void Abort();

  const int line_;
  const char* const file_;
  std::stringstream ss_;
};

typedef void (*AbortHandlerFun)();

void SetAbortHandler(AbortHandlerFun handler);

#if defined(NDEBUG)
#define ASSERT(x, m)
#else
#define ASSERT(x, m) do { if (!(x)) AssertHelper(__LINE__, __FILE__) << m; } while(0)
#endif

#define CHECK(x, m) do { if (!(x)) AssertHelper(__LINE__, __FILE__) << m; } while(0)
