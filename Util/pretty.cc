// (c) Robert Muth - see LICENSE for more info

#include "pretty.h"

#include <cassert>
#include <iostream>

namespace PP {

std::ostream& operator<<(std::ostream& out, BreakType bt) {
  switch (bt) {
    case BreakType::INVALID:
      out << "INVALID";
      break;
    case BreakType::FITS:
      out << "FITS";
      break;
    case BreakType::INCONSISTENT:
      out << "INCONSISTENT";
      break;
    case BreakType::CONSISTENT:
      out << "CONSISTENT";
      break;
    case BreakType::FORCE_LINE_BREAK:
      out << "FORCE_LINE_BREAK";
      break;
  }
  return out;
}

std::ostream& operator<<(std::ostream& out, const Token& t) {
  switch (t.type) {
    case TokenType::BEG:
      out << "Beg(break_type=" << t.beg.break_type
          << ", offset=" << t.beg.offset << ")";
      break;
    case TokenType::END:
      out << "End()";
      break;
    case TokenType::BRK:
      out << "Brk(num_spaces=" << t.brk.num_spaces
          << ", offset=" << t.brk.offset << ", nobreak=" << t.brk.nobreak
          << ")";
      break;
    case TokenType::STR:
      out << "Str(\"" << t.str << "\")";
      break;
    case TokenType::INVALID:
      out << "INVALID";
      break;
  }
  return out;
}

template <typename T>
T PopStack(std::vector<T>& stack) {
  T top = stack.back();
  stack.pop_back();
  return top;
}

std::vector<ssize_t> ComputeSizes(const std::vector<Token>& tokens) {
  std::vector<ssize_t> sizes;
  sizes.reserve(tokens.size());
  ssize_t total = 0;
  std::vector<size_t> scan_stack;
  size_t x;

  for (size_t n = 0; n < tokens.size(); n++) {
    const Token& token = tokens[n];
    switch (token.type) {
      case TokenType::BEG:
        sizes.push_back(-total);
        scan_stack.push_back(n);
        break;
      case TokenType::END:
        sizes.push_back(1);
        x = PopStack(scan_stack);
        sizes[x] += total;
        if (tokens[x].type == TokenType::BRK) {
          x = PopStack(scan_stack);
          sizes[x] += total;
        }
        break;
      case TokenType::BRK:
        sizes.push_back(-total);
        // maybe close sizes a preceeding BRK
        x = scan_stack.back();
        if (tokens[x].type == TokenType::BRK) {
          scan_stack.pop_back();
          sizes[x] += total;
        }
        scan_stack.push_back(n);
        total += token.brk.num_spaces;
        break;
      case TokenType::STR:
        sizes.push_back(token.str.size());
        total += token.str.size();
        break;
      default:
        assert(false);  // unreachable
        break;
    }
  }
  return sizes;
}

void UpdatesSizesForNoBreaks(const std::vector<Token>& tokens,
                             std::vector<ssize_t>& sizes) {
  ssize_t total = INFINITE_WIDTH;
  for (size_t j = 0; j < tokens.size(); j++) {
    size_t i = tokens.size() - 1 - j;
    const Token& token = tokens[i];
    switch (token.type) {
      case TokenType::BEG:
        if (token.beg.break_type == BreakType::FORCE_LINE_BREAK) {
          total = INFINITE_WIDTH;
        }
        break;
      case TokenType::END:
        total = INFINITE_WIDTH;
        break;
      case TokenType::BRK:
        if (token.brk.nobreak) {
          if (total < sizes[i]) {
            sizes[i] = total;
            total += token.brk.num_spaces;
          } else {
            total = sizes[i];
          }
        } else {
          total = 0;
        }
        break;
      case TokenType::STR:
        total += token.str.size();
        break;
      case TokenType::INVALID:
        assert(false);  // unreachable
        break;
    }
  }
  //
  total = 0;
  for (size_t j = 0; j < tokens.size(); j++) {
    size_t i = tokens.size() - 1 - j;
    const Token& token = tokens[i];
    switch (token.type) {
      case TokenType::BEG:
        if (token.beg.break_type == BreakType::FORCE_LINE_BREAK) {
          total = 0;
        }
        break;
      case TokenType::END:
        break;
      case TokenType::BRK:
        total += token.brk.num_spaces;
        if (!token.brk.nobreak) {
          if (total > sizes[i]) {
            sizes[i] = total;
          }
          total = 0;
        }
        break;
      case TokenType::STR:
        total += token.str.size();
        break;
      case TokenType::INVALID:
        assert(false);  // unreachable
        break;
    }
  }
}

class Output {
 public:
  Output(size_t line_width, size_t approx_output_length)
      : line_width_(line_width), remaining_(line_width) {
    buffer_.reserve(approx_output_length);
  }

  void Append(std::string_view str) { buffer_ += str; }

  void AppendWithSpaceUpdate(std::string_view str) {
    buffer_ += str;
    remaining_ -= str.size();
  }

  void IndentWithSpaceUpdate(size_t num_spaces) {
    for (size_t i = 0; i < num_spaces; i++) {
      buffer_ += ' ';
    }
    remaining_ -= num_spaces;
  }

  size_t LineWidth() { return line_width_; }

  size_t Remaining() { return remaining_; }

  bool FitsInCurrentLine(size_t size) { return size <= remaining_; }

  std::string Get() { return buffer_; }

  void SetOffsetAndLineBreak(size_t offset) {
    remaining_ = offset;
    buffer_ += '\n';
    size_t ci = line_width_ - remaining_;
    for (size_t i = 0; i < ci; i++) {
      buffer_ += ' ';
    }
  }

 private:
  size_t line_width_;
  size_t remaining_;
  std::string buffer_;
};

struct Entry {
  size_t offset;
  BreakType break_type;
};

void Render(const std::vector<Token>& tokens, const std::vector<ssize_t>& sizes,
            Output* output) {
  std::vector<Entry> stack;
  for (size_t i = 0; i < tokens.size(); i++) {
    const Token& token = tokens[i];
    const size_t size = sizes[i];
    switch (token.type) {
      case TokenType::BEG: {
        Entry entry;
        if (token.beg.break_type == BreakType::FORCE_LINE_BREAK) {
          size_t offset;
          if (!stack.empty()) {
            offset = stack.back().offset;
            output->SetOffsetAndLineBreak(offset - token.beg.offset);
          } else {
            offset = output->LineWidth();
          }
          entry = {output->Remaining(), token.beg.break_type};
        } else if (output->FitsInCurrentLine(size)) {
          entry = {0, BreakType::FITS};
        } else {
          entry = {
              output->Remaining() - token.beg.offset,
              token.beg.break_type == BreakType::CONSISTENT
                  ? BreakType::CONSISTENT
                  : BreakType::INCONSISTENT,
          };
        }
        stack.push_back(entry);
      } break;
      case TokenType::END:
        stack.pop_back();
        break;
      case TokenType::BRK: {
        const Entry& top = stack.back();
        BreakType break_type = top.break_type;
        size_t offset = top.offset;
        if ((token.brk.nobreak && output->FitsInCurrentLine(size)) ||
            break_type == BreakType::FITS) {
          output->IndentWithSpaceUpdate(token.brk.num_spaces);
        } else if (top.break_type == BreakType::CONSISTENT ||
                   top.break_type == BreakType::FORCE_LINE_BREAK) {
          output->SetOffsetAndLineBreak(offset - token.brk.offset);
        } else if (top.break_type == BreakType::INCONSISTENT) {
          if (output->FitsInCurrentLine(size)) {
            output->IndentWithSpaceUpdate(token.brk.num_spaces);
          } else {
            output->SetOffsetAndLineBreak(offset - token.brk.offset);
          }
        }
      } break;

      case TokenType::STR:
        output->AppendWithSpaceUpdate(token.str);
        break;
      case TokenType::INVALID:
        assert(false);  // unreachable
        break;
    }
  }
}

size_t ApproxOutputLength(const std::vector<Token>& tokens) {
  size_t total = 0;
  for (const Token& token : tokens) {
    switch (token.type) {
      case TokenType::BEG:
      case TokenType::END:
        break;
      case TokenType::STR:
        total += token.str.size();
        break;
      case TokenType::BRK:
        total += token.brk.num_spaces;
        break;
      default:
        assert(false);  // unreachable
        break;
    }
  }
  return total;
}

std::string PrettyPrint(const std::vector<Token>& tokens, size_t line_width) {
  std::vector<ssize_t> sizes = ComputeSizes(tokens);
  assert(sizes.size() == tokens.size());
  UpdatesSizesForNoBreaks(tokens, sizes);
#if 0
  for (size_t i = 0; i < tokens.size(); i++) {
    std::cout << tokens[i] << " " << sizes[i] << std::endl;
  }
#endif
  Output output(line_width, ApproxOutputLength(tokens));
  Render(tokens, sizes, &output);
  return output.Get();
}

}  // namespace PP
