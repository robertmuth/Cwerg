/*
    This test should be more or less identical to arm_test.py
    except that it is written in C.
    It checks that we can assemble and disassemble all the instructions
    found in `arm_test.dis`
*/

#include "CpuA32/disassembler.h"
#include "CpuA32/opcode_gen.h"

#include <cstdint>

#include <iomanip>
#include <iostream>
#include <string_view>
#include <vector>

namespace {
using namespace cwerg;

const int kMaxLineLen = 256;

// Splits at whitespace and comma
void SplitLine(std::string_view buffer, std::vector<std::string_view>* tokens) {
  tokens->clear();
  int token_start = -1;
  for (int i = 0; buffer[i] != 0 && i < buffer.size(); ++i) {
    const char c = buffer[i];
    if (c == ',' || c == ' ' || c == '\t' || c == '\n') {
      if (token_start >= 0) {
        tokens->emplace_back(
            std::string_view(&buffer[token_start], i - token_start));
        token_start = -1;
      }
    } else {
      if (token_start < 0) {
        token_start = i;
      }
    }
  }
  if (token_start >= 0) {
    tokens->emplace_back(
        std::string_view(&buffer[token_start], buffer.size() - token_start));
  }
}

// We rename (v)stmiaXX  -> (v)stmXX
const std::string_view kMultiRewrites[] = {  //
    "stmia", "stm", "vstmia", "vstm",        //
    "stmib", "stm", "vstmib", "vstm",        //
    "stmdb", "stm", "vstmdb", "vstm",        //
    "ldmia", "ldm", "vldmia", "vldm",        //
    "ldmib", "ldm", "vldmib", "vldm",        //
    "ldmdb", "ldm", "vldmdb", "vldm",        //
    "push",  "stm", "vpush",  "vstm",        //
    "pop",   "ldm", "vpop",   "vldm",        //
    "",      ""};

std::string_view replace_prefix(char buffer[128],
                                std::string_view name,
                                std::string_view src,
                                std::string_view dst) {
  dst.copy(buffer, dst.size());
  name.remove_prefix(src.size());
  name.copy(buffer + dst.size(), name.size());
  return std::string_view(buffer, dst.size() + name.size());
}

bool has_prefix(std::string_view name, std::string_view prefix) {
  return name.substr(0, prefix.size()) == prefix;
}

void MassageInput(std::vector<std::string_view>* token,
                  char buffer[128],
                  bool is_multiple) {
  auto name = (*token)[1];
  if (is_multiple) {
    for (unsigned i = 0; !kMultiRewrites[i].empty(); i += 2) {
      auto& src = kMultiRewrites[i];
      auto& dst = kMultiRewrites[i + 1];
      if (has_prefix(name, src)) {
        (*token)[1] = replace_prefix(buffer, name, src, dst);
        break;
      }
    }
  } else if (has_prefix(name, "vcmp") && (*token)[3] == "#0.0") {
    (*token)[3] = "#0";
  } else {
    //   lslXX     r3, r9, #2 -> movXX   r3, r9, lsl #2

    auto name3 = name.substr(0, 3);
    if (name3 == "lsl" || name3 == "lsr" || name3 == "asr" || name3 == "ror") {
      token->push_back(token->back());
      (*token)[token->size() - 2] = name3;
      (*token)[1] = replace_prefix(buffer, name, name3, "mov");
    }
  }
}

int HandleOneInstruction(std::string_view line,
                         uint32_t data,
                         std::vector<std::string_view>* actual) {
  // printf("%s\n", line);
  a32::Ins ins;
  if (!DecodeIns(&ins, data)) {
    std::cout << "could not find opcode for: " << std::hex << data << std::dec
              << " -- [" << line << "]\n";
    return 1;
  }
  auto& name = (*actual)[1];
  // we need to test push/pop BEFORE it is rewritten by  MassageInput
  int is_push_pop = has_prefix(name, "push") || has_prefix(name, "vpush") ||
                    has_prefix(name, "pop") || has_prefix(name, "vpop");
  char buffer_name[128];
  MassageInput(actual, buffer_name, ins.opcode->classes & a32::MULTIPLE);

  char buffer[128];
  a32::RenderInsStd(ins, buffer);

  std::vector<std::string_view> expected;
  SplitLine(buffer, &expected);
  if (expected[0] != (*actual)[1]) {
    std::cout << "name mismatch: [" << line << "] [" << buffer << "\n";
    return 1;
  }
  int operand_start_actual = 2;
  // for push/pop actual is missing the address operand "sp!"
  int operand_start_expected = 1 + is_push_pop;
  if (actual->size() - operand_start_actual !=
      expected.size() - operand_start_expected) {
    std::cout << "operand count mismatch: [" << line << "] [" << buffer << "\n";
    return 1;
  }
  for (int i = operand_start_actual; i < actual->size(); ++i) {
    int j = i - operand_start_actual + operand_start_expected;
    if ((*actual)[i] != expected[j]) {
      std::cout << "operand mismatch: [" << line << "] [" << buffer << "\n";
      return 1;
    }
  }

  uint32_t data_expected = EncodeIns(ins);
  if (data != data_expected) {
    std::cout << "assembler mismatch " << std::hex << data << " vs "
              << data_expected << std::dec << " [" << line << "] [" << buffer
              << "\n";
    return 1;
  }
  return 0;
}

int Process(const char* filename) {
  int errors = 0;
  // printf("processing %s\n", filename);
  FILE* fp = fopen(filename, "r");
  if (!fp) return 1;

  std::vector<std::string_view> token;
  char line[kMaxLineLen];
  while (fgets(line, sizeof line, fp)) {
    SplitLine(line, &token);
    if (token.size() <= 2) continue;
    const uint32_t data = strtoul(token[0].data(), nullptr, 16);
    errors += HandleOneInstruction(line, data, &token);
  }

  fclose(fp);
  return errors;
}

}  // namespace

int main(int argc, char* argv[]) {
  int failures = 0;
  for (int i = 1; i < argc; ++i) {
    failures += Process(argv[i]);
  }
  if (failures > 0) {
    std::cout << "Failures: " << failures << "\n";
  }
  return failures > 0;
}
