// (c) Robert Muth - see LICENSE for more info

#include "Util/assert.h"

#include <iostream>

static AbortHandlerFun MyAbortHandler = &abort;

void SetAbortHandler(AbortHandlerFun handler) {
  MyAbortHandler = handler;
}

#ifdef CWERG_ENABLE_UNWIND

#define UNW_LOCAL_ONLY
#include <libunwind.h>
#include <iomanip>
#include <iostream>

void AssertHelper::Abort() {
  unw_cursor_t cursor;
  unw_context_t context;

  // Init
  unw_getcontext(&context);
  unw_init_local(&cursor, &context);

  // Unwind
  while (unw_step(&cursor) > 0) {
    unw_word_t offset, pc;
    unw_get_reg(&cursor, UNW_REG_IP, &pc);
    if (pc == 0) break;

    char sym[1024];
    if (unw_get_proc_name(&cursor, sym, sizeof(sym), &offset) == 0) {
      std::cerr << std::hex << "0x" << pc << ": " << sym << " (+0x" << offset
                << ")\n";
    } else {
      std::cerr << std::hex << "0x" << pc << ": -- no symbol info\n";
    }
  }
  std::cerr << "to unmangle append ` |& c++filt ` to command\n";
  MyAbortHandler();
}

#else

#include <execinfo.h>

void AssertHelper::Abort() {
  void* buffer[1024];
  int count = backtrace(buffer, 1024);
  backtrace_symbols_fd(buffer, count, 2);
  MyAbortHandler();
}
#endif

AssertHelper::~AssertHelper() {
  std::cerr << "Failure at " << file_ << "::" << std::dec << line_ << ": "
            << ss_.str() << "\n";

  Abort();
}


