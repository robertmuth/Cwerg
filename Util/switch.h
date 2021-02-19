#pragma once
// (c) Robert Muth - see LICENSE for more info
// Trivial library for dealing with command-line flags

#include <cstdint>
#include <iostream>
#include <string>

namespace cwerg {

class SwitchBase {
 public:
  SwitchBase(std::string_view name,
             std::string_view purpose,
             bool has_arg = true)
      : next_(list_), name_(name), purpose_(purpose), has_arg_(has_arg) {
    list_ = this;
  }

  virtual bool Set(std::string_view arg) = 0;
  virtual std::string Get() const = 0;

  static void EmitSummary(std::ostream* output);

  static SwitchBase* Find(std::string_view name);

  // return the number of args consumed or -1 if there was an error
  // in which case an message is emitted to
  static int ParseArgv(int argc, const char* argv[], std::ostream* output);

 private:
  static SwitchBase* list_;

  SwitchBase* const next_;
  const std::string name_;
  const std::string purpose_;
  const bool has_arg_;
};

// Only decimal and hexadecimal notation is supported
class SwitchInt32 : public SwitchBase {
 public:
  SwitchInt32(std::string_view name, std::string_view purpose, int32_t value)
      : SwitchBase(name, purpose), value_(value) {}

  int32_t Value() const { return value_; }

  std::string Get() const override;
  bool Set(std::string_view arg) override;

 private:
  int32_t value_;
};

class SwitchBool : public SwitchBase {
 public:
  SwitchBool(std::string_view name, std::string_view purpose)
      : SwitchBase(name, purpose, false), value_(false) {}

  bool Value() const { return value_; }

  std::string Get() const override { return value_ ? "true" : "false"; }


  bool Set(std::string_view arg) override {
    value_ = true;
    return true;
  }

 private:
  bool value_;
};

class SwitchString : public SwitchBase {
 public:
  SwitchString(std::string_view name,
               std::string_view purpose,
               std::string_view value)
      : SwitchBase(name, purpose), value_(value) {}

  std::string_view Value() const { return value_; }

  std::string Get() const override { return value_; }

  bool Set(std::string_view arg) override {
    value_ = arg;
    return true;
  }

 private:
  std::string value_;
};

}  // namespace cwerg
