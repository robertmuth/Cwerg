/*
    This test should be more or less identical to arm_test.py
    except that it is written in C.
    It checks that we can assemble and disassemble all the instructions
    found in `arm_test.dis`
*/

// #include "Cpu64/disassembler.h"
#include "CpuA64/opcode_gen.h"
#include "CpuA64/symbolic.h"
#include "Util/assert.h"
#include "Util/parse.h"

#include <cstdint>
#include <iomanip>
#include <iostream>
#include <set>
#include <string_view>
#include <vector>

namespace {
using namespace cwerg;

const int kMaxLineLen = 256;

const std::set<std::pair<std::string_view, std::string_view>> SIMPLE_ALIASES = {
    // official name, cwerg name without variant
    {"asr", "asrv"},
    {"lsr", "lsrv"},
    {"lsl", "lslv"},
    {"ror", "rorv"},

    // will be handled by OperandsMatch(
    {"mov", "movn"},
    {"mov", "movz"},

    //  cwerg specific aliases
    {"ldr", "fldr"},
    {"str", "fstr"},
    {"ldur", "fldur"},
    {"stur", "fstur"},
    {"ldp", "fldp"},
    {"stp", "fstp"},
    //
    {"ldrh", "ldr"},
    {"strh", "str"},
    {"ldurh", "ldur"},

    {"sturh", "stur"},
    {"ldpsw", "ldp"},
    {"ldarh", "ldar"},
    {"stlrh", "stlr"},
    {"ldaxrh", "ldaxr"},
    {"ldxrh", "ldxr"},
    {"stlxrh", "stlxr"},
    {"ldrb", "ldr"},
    {"strb", "str"},
    {"stxrh", "stxr"},
    {"ldurb", "ldur"},
    {"sturb", "stur"},
    {"ldarb", "ldar"},
    {"stlrb", "stlr"},
    {"ldaxrb", "ldaxr"},
    {"ldxrb", "ldxr"},
    {"stxrb", "stxr"},
    {"stlxrb", "stlxr"},
};

const std::set<std::pair<std::string_view, std::string_view>> COMPLEX_ALIASES =
    {
        {"cmn", "adds"},
        {"cmp", "subs"},
        {"neg", "sub"},
        {"negs", "subs"},
        {"ngcs", "sbcs"},
        {"cneg", "csneg"},
        {"cinc", "csinc"},
        {"cset", "csinc"},
        {"cinv", "csinv"},
        {"csetm", "csinv"},
        //
        {"tst", "ands"},
        {"mov", "orr"},
        {"mov", "add"},
        {"mvn", "orn"},
        {"mul", "madd"},
        {"mneg", "msub"},
        //
        {"lsl", "ubfm"},
        {"lsr", "ubfm"},
        {"asr", "sbfm"},
        {"ror", "extr"},
        {"ubfiz", "ubfm"},
        {"ubfx", "ubfm"},
        {"sbfx", "sbfm"},
        {"sxtb", "sbfm"},
        {"sxth", "sbfm"},
        {"sxtw", "sbfm"},
        {"sbfiz", "sbfm"},
        {"bfxil", "bfm"},
        {"bfi", "bfm"},
        {"bfc", "bfm"},
        //
        {"smull", "smaddl"},
        {"umull", "umaddl"},
};

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

void HandleAliasMassaging(std::string_view short_name,
                          const a64::Ins& ins,
                          std::vector<std::string_view>* token) {}

void MassageOperandsAndCheckName(std::string_view line,
                                 uint32_t data,
                                 const a64::Ins& ins,
                                 std::vector<std::string_view>* token) {
  size_t pos = ins.opcode->name.find('_');
  std::string_view actual_name = (*token)[1];
  std::string_view short_name = ins.opcode->name.substr(0, pos);
  if (short_name != actual_name) {
    if (SIMPLE_ALIASES.find({actual_name, short_name}) !=
        SIMPLE_ALIASES.end()) {
      short_name = actual_name;
    } else if (COMPLEX_ALIASES.find({actual_name, short_name}) !=
               COMPLEX_ALIASES.end()) {
      // HandleAliasMassaging(short_name, ins, token);
      short_name = actual_name;
    } else if (short_name == "b" &&
               ins.opcode->name.substr(2) == actual_name.substr(2)) {
      short_name = actual_name;
    }
  }

  if (short_name != actual_name) {
    std::cout << "name mismatch: " << actual_name << " vs " << short_name
              << "\n";
  }
}

// bool OperandsMatch(const a64::Ins& ins,
//                   std::vector<std::string_view>* token) {}

int HandleOneInstruction(std::string_view line,
                         uint32_t data,
                         std::vector<std::string_view>* token) {
  // token[0] data
  // token[1] mnemonic
  // token[2] operand1
  // token[3] operand2
  // token[4] ...

  a64::Ins ins;
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

  MassageOperandsAndCheckName(line, data, ins, token);

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
    if (token.size() <= 1) continue;
    const uint32_t data = strtoul(token[0].data(), nullptr, 16);
    errors += HandleOneInstruction(line, data, &token);
  }

  fclose(fp);
  return errors;
}

void CheckEncodeDecode() {
  uint32_t count = 0;
  uint32_t sm = 0;
  for (uint32_t size = 64; size >= 2; size >>= 1) {
    for (uint32_t ones = 1; ones < size; ++ones) {
      for (uint32_t r = 0; r < size; ++r) {
        ++count;
        const uint32_t n = size == 64;
        const uint32_t s = sm | (ones - 1);
        const uint32_t i = (n << 12) | (r << 6) | s;
        uint64_t x = a64::Decode_10_15_16_22_X(i);
        // std::cout << std::hex << n << " " << r << " " << s << " pattern " <<
        // x
        //          << "\n";
        uint32_t j = a64::Encode_10_15_16_22_X(x);
        ASSERT(i == j, "bad logic imm " << i << " vs " << j);
      }
    }

    if (size <= 32) {
      sm += size;
    }
  }

  ASSERT(count == 5334, "total number of codes is not 5334: " << count);
}

void CheckEncodeDecodeFloat() {
  for (uint32_t i = 0; i < 256; ++i) {
    const double d = a64::Decode8BitFlt(i);
     // std::cout << std::hex << i << " " << d << "\n";
     uint32_t j = a64::Encode8BitFlt(d);
     ASSERT(i == j, "bad flt imm " << i << " vs " << j << "  val " << d);
  }
}

}  // namespace

int main(int argc, char* argv[]) {
  CheckEncodeDecode();
  CheckEncodeDecodeFloat();
  int failures = 0;
  for (int i = 1; i < argc; ++i) {
    failures += Process(argv[i]);
  }
  if (failures > 0) {
    std::cout << "Failures: " << failures << "\n";
  }
  return failures > 0;
}
