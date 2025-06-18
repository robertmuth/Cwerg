// (c) Robert Muth - see LICENSE for more info

#include "Util/switch.h"
#include <charconv>
#include <iomanip>

namespace cwerg {

SwitchBase* SwitchBase::list_ = nullptr;

SwitchBase* SwitchBase::Find(std::string_view name) {
  for (SwitchBase* sw = list_; sw; sw = sw->next_) {
    if (sw->name_ == name) return sw;
  }
  return nullptr;
}

void SwitchBase::EmitSummary(std::ostream* output) {
  for (const SwitchBase* sw = list_; sw != nullptr; sw = sw->next_) {
    *output << std::setw(-20) << sw->name_ << " value: " << sw->Get() << "\n\n"
            << sw->purpose_ << "\n\n\n";
  }
}

int SwitchBase::ParseArgv(int argc, const char* argv[], std::ostream* output) {
  for (int i = 1; i < argc; ++i) {
    const char* arg = argv[i];

    if (arg[0] != '-' || arg[1] == 0) return i;
    SwitchBase* sw = Find(arg + 1);
    if (sw == nullptr) {
      *output << "unknown flag: [" << arg << "]\n";
      EmitSummary(output);
      return -1;
    }

    if (sw->has_arg_) {
      ++i;
      if (i >= argc) {
        *output << "missing arg for: [" << arg << "]\n";
        return -1;
      }
      if (!sw->Set(argv[i])) {
        *output << "cannot parse arg for: [" << arg << "]: [" << argv[i]
                << "]\n";
        return -1;
      }
    } else {
      sw->Set("");
    }
  }
  return argc;
}

std::string SwitchInt32::Get() const {
  std::ostringstream s;
  s << value_;
  return s.str();
}

bool SwitchInt32::Set(std::string_view arg) {
  int base = 10;
  if (arg.size() > 2 && arg[0] == '0' && (arg[1] == 'x' || arg[1] == 'X')) {
    base = 16;
    arg.remove_prefix(2);
  }
  auto result =
      std::from_chars(arg.data(), arg.data() + arg.size(), value_, base);
  return result.ptr == arg.data() + arg.size() || result.ec == std::errc();
}

}  // namespace cwerg
