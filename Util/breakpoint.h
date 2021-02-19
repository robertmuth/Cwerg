#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <condition_variable>
#include <iostream>
#include <mutex>
#include <vector>

namespace cwerg {

// Software Breakpoints
class BreakPoint {
 public:
  BreakPoint(std::string_view name) : next_(head), name_(name) { head = this; }

  std::string_view name() const { return name_; }
  bool ready() const { return ready_; }  // benign race

  void Break() {
    std::unique_lock<std::mutex> lock(mutex_);
    std::cerr << "break point hit [" << name_ << "]\n";
    ready_ = false;
    while (!ready_) {
      cv_.wait(lock);
    }
  }

  void Resume() {
    {
      std::lock_guard<std::mutex> lock(mutex_);
      std::cerr << "resume break point [" << name_ << "]\n";
      ready_ = true;
    }
    cv_.notify_all();
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
  std::condition_variable cv_;
  std::mutex mutex_;
  bool ready_ = true;

  static BreakPoint* head;
};

}  // namespace cwerg
