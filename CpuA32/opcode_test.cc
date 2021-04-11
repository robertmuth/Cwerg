/*
    This test should be more or less identical to arm_test.py
    except that it is written in C.
    It checks that we can assemble and disassemble all the instructions
    found in `arm_test.dis`
*/

#include "CpuA32/opcode_gen.h"
#include "CpuA32/symbolic.h"
#include "Util/assert.h"
#include "Util/parse.h"

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
  int nesting_level = 0;
  int token_start = -1;
  for (int i = 0; buffer[i] != 0 && i < buffer.size(); ++i) {
    const char c = buffer[i];
    if (nesting_level == 0 && (c == ',' || c == ' ' || c == '\t' || c == '\n' ||
                               c == '[' || c == ']' || c == '!')) {
      if (token_start >= 0) {
        tokens->emplace_back(
            std::string_view(&buffer[token_start], i - token_start));
        token_start = -1;
      }
    } else {
      if (c == '{')
        ++nesting_level;
      else if (c == '}')
        --nesting_level;
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

bool has_prefix(std::string_view name, std::string_view prefix) {
  return name.substr(0, prefix.size()) == prefix;
}

bool has_suffix(std::string_view name, std::string_view suffix) {
  if (name.size() < suffix.size()) return false;
  return name.substr(name.size() - suffix.size()) == suffix;
}

std::string FixupAliases(const a32::Opcode& opcode,
                         const std::vector<std::string_view>& token,
                         std::vector<std::string>* actual_ops) {
  std::string_view name = token[1];
  for (unsigned i = 2; i < token.size(); ++i) {
    actual_ops->push_back(std::string(token[i]));
  }

  auto three = name.substr(0, 3);
  if (three == "lsl" || three == "lsr" || three == "asr" || three == "ror") {
    actual_ops->insert(actual_ops->end() - 1, std::string(three));
    return "mov" + std::string(name.substr(3));
  }

  if (opcode.classes & a32::OPC_FLAG::MULTIPLE) {
    if (has_prefix(name, "push")) {
      actual_ops->insert(actual_ops->begin(), "sp");
      return "stmdb" + std::string(name.substr(4));
    } else if (has_prefix(name, "vpush")) {
      actual_ops->insert(actual_ops->begin(), "sp");
      return "vstmdb" + std::string(name.substr(5));
    } else if (has_prefix(name, "pop")) {
      actual_ops->push_back("sp");
      return "ldmia" + std::string(name.substr(3));
    } else if (has_prefix(name, "vpop")) {
      actual_ops->push_back("sp");
      return "vldmia" + std::string(name.substr(4));
    }

    if (has_prefix(name, "vldm") || has_prefix(name, "ldm")) {
      actual_ops->push_back((*actual_ops)[0]);
      actual_ops->erase(actual_ops->begin());
    }

    bool is_vfp = name[0] == 'v';
    auto two = name.substr(is_vfp ? 4 : 3, 2);
    if (two != "ia" && two != "ib" && two != "da" && two != "db") {
      return std::string(name.substr(0, is_vfp ? 4 : 3)) + "ia" +
             std::string(name.substr(is_vfp ? 4 : 3));
    }
  }

  if (has_prefix(name, "strex")) {
    actual_ops->push_back((*actual_ops)[1]);
    actual_ops->erase(actual_ops->begin() + 1);
    return std::string(name);
  }

  if (has_prefix(name, "str") || has_prefix(name, "vstr")) {
    actual_ops->push_back((*actual_ops)[0]);
    actual_ops->erase(actual_ops->begin());
  }

  return std::string(name);
}

// assumes  {d8-d10} or  {d1}
std::string_view range_first_reg(std::string_view range) {
  for (unsigned i = 1; i < range.size(); ++i) {
    if (range[i] == '-' || range[i] == '}') {
      return range.substr(1, i - 1);
    }
  }
  return "";
}

unsigned range_width(std::string_view range) {
  auto start_reg = range_first_reg(range);
  if (start_reg.size() + 2 == range.size()) return 1;
  auto end_reg = range_first_reg(range.substr(1 + start_reg.size()));
  auto r1 = ParseInt<unsigned>(start_reg.substr(1));
  auto r2 = ParseInt<unsigned>(end_reg.substr(1));
  if (r1 && r2) {
    return 1 + r2.value() - r1.value();
  }
  return 0;
}

std::string reg_list(std::string_view std_op) {
  if (has_prefix(std_op, "reglist:")) std_op.remove_prefix(8);
  const uint32_t mask = ParseInt<unsigned>(std_op).value();
  return a32::SymbolizeRegListMask(mask);
}

bool OperandsMatch(const a32::Opcode& opcode,
                   std::string_view actual_name,
                   const std::vector<std::string>& objdump_ops,
                   const std::vector<std::string>& std_ops) {
  ASSERT(opcode.num_fields == std_ops.size(), "");
  unsigned j = 0;  // index into objdump_ops
  for (unsigned i = 0; i < opcode.num_fields; ++i) {
    const a32::OK ok = opcode.fields[i];
    std::string_view std_op = std_ops[i];
    std::string_view objdump_op;
    if (j < objdump_ops.size()) objdump_op = objdump_ops[j];
    if (has_prefix(objdump_op, "#")) objdump_op.remove_prefix(1);

    if (has_prefix(objdump_op, "-") && a32::OPC_FLAG::ADDR_DEC & opcode.classes) {
      ASSERT(ok == a32::OK::REG_0_3 || ok == a32::OK::IMM_0_7_TIMES_4 ||
             ok == a32::OK::IMM_0_11 || ok == a32::OK::IMM_0_3_8_11 , "");
      objdump_op.remove_prefix(1);
    }

    if (std_op == objdump_op) {
      ++j;
    } else if (opcode.fields[i] == a32::OK::PRED_28_31 &&
               (std_op == "al" || has_suffix(actual_name, std_op))) {
      // pass
    } else if (std_op == "0" &&
               (ok == a32::OK::IMM_10_11_TIMES_8 ||
                ok == a32::OK::IMM_0_7_TIMES_4 || ok == a32::OK::IMM_7_11 ||
                ok == a32::OK::IMM_0_11 || ok == a32::OK::IMM_0_3_8_11)) {
      // pass
    } else if (std_op == "lsl" && ok == a32::OK::SHIFT_MODE_5_6) {
      // pass
    } else if (a32::OPC_FLAG::MULTIPLE & opcode.classes) {
      if (ok == a32::OK::DREG_12_15_22 || ok == a32::OK::SREG_12_15_22) {
        if (range_first_reg(objdump_op) == std_op) continue;
      } else if (ok == a32::OK::REG_RANGE_0_7 ||
                 ok == a32::OK::REG_RANGE_1_7) {
        if (has_prefix(std_op, "regrange:")) std_op.remove_prefix(9);
        auto w = ParseInt<unsigned>(std_op);
        if (w.value() == range_width(objdump_op)) {
          ++j;
          continue;
        }
      } else if (ok == a32::OK::REGLIST_0_15) {
        if (reg_list(std_op) == objdump_op) {
          ++j;
          continue;
        }
      }
      return false;
    } else {
      return false;
    }
  }
  return true;
}

int HandleOneInstruction(std::string_view line,
                         uint32_t data,
                         const std::vector<std::string_view>& token) {
  // printf("%s\n", line);
  a32::Ins ins;
  if (!Disassemble(&ins, data)) {
    std::cout << "could not find opcode for: " << std::hex << data << std::dec
              << " -- [" << line << "]\n";
    return 1;
  }

  uint32_t data_expected = Assemble(ins);
  if (data != data_expected) {
    std::cout << "assembler mismatch " << std::hex << data << " vs "
              << data_expected << std::dec << " in: " << line;
    return 1;
  }

  std::vector<std::string> actual_ops;
  const std::string actual_name = FixupAliases(*ins.opcode, token, &actual_ops);
  if (!has_prefix(actual_name, ins.opcode->name)) {
    std::cout << "name mismatch: [" << ins.opcode->name << "] [" << actual_name
              << "] in: " << line;
  }

  std::vector<std::string> std_ops;
  InsSymbolize(ins, &std_ops);
  std::vector<std::string_view> std_ops_view;
  std_ops_view.emplace_back(ins.opcode->enum_name);
  for (const std::string& op : std_ops)  std_ops_view.emplace_back(op);
  a32::Ins ins2;
  a32::InsFromSymbolized(std_ops_view, &ins2);

  if (!OperandsMatch(*ins.opcode, actual_name, actual_ops, std_ops)) {
    std::cout << "operand mismatch: std:[";
    std::string_view sep = "";
    for (auto& op : std_ops) {
      std::cout << sep << op;
      sep = " ";
    }
    std::cout << "] vs  objdump:[";
    sep = "";
    for (auto& op : actual_ops) {
      std::cout << sep << op;
      sep = " ";
    }
    std::cout << "] in: " << line;
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
    errors += HandleOneInstruction(line, data, token);
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
