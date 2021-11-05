#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <condition_variable>
#include <iostream>
#include <mutex>
#include <vector>
#include "Util/webserver.h"

namespace cwerg {

// see https://gcc.gnu.org/bugzilla/show_bug.cgi?id=58909
#define BUGGY_LIBC 1
#if BUGGY_LIBC
extern "C" unsigned int sleep(unsigned int seconds);
#endif

// Software Breakpoints
class BreakPoint {
 public:
  BreakPoint(std::string_view name) : next_(head), name_(name) { head = this; }

  std::string_view name() const { return name_; }
  bool ready() const { return ready_; }  // benign race
  static bool HaveBreakPoints() { return head != nullptr; }

  void Break() {
    std::unique_lock<std::mutex> lock(mutex_);
    std::cerr << "break point hit [" << name_ << "]\n";
    ready_ = false;

    while (!ready_) {
#if BUGGY_LIBC
      lock.unlock();
      sleep(1);
#else
      cv_.wait(lock);
#endif
    }
  }

  void Resume() {
    {
      std::lock_guard<std::mutex> lock(mutex_);
      std::cerr << "resume break point [" << name_ << "]\n";
      ready_ = true;
    }
#if BUGGY_LIBC
#else
    cv_.notify_all();
#endif
  }

  static bool ResumeByName(std::string_view name) {
    for (BreakPoint* w = head; w != nullptr; w = w->next_) {
      if (name == w->name_) {
        w->Resume();
        return true;
      }
    }
    std::cerr << "Unknown breakpoint " << name << "\n";
    return false;
  }

  static std::vector<const BreakPoint*> GetAll() {
    std::vector<const BreakPoint*> out;
    for (BreakPoint* w = head; w != nullptr; w = w->next_) out.push_back(w);
    return out;
  }

 private:
  BreakPoint* const next_;
  const std::string name_;
#if BUGGY_LIBC
#else
  std::condition_variable cv_;
#endif
  std::mutex mutex_;
  bool ready_ = true;

  static BreakPoint* head;
};

// This must be registered with the webserver to handle break points like so
// webserver->handler.push_back(WebHandler{"/resume/", "GET", ResumeHandler});
extern WebResponse ResumeBreakpointHandler(const WebRequest& request);

// Renders the breakpoint overview
extern void RenderBreakPointHTML(std::ostream* out);

}  // namespace cwerg
