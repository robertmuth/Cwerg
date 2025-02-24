#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/lexer.h"
#include "FE/parse.h"
#include "Util/assert.h"
#include "Util/pretty.h"
#include "Util/switch.h"

using namespace cwerg::fe;
using namespace cwerg;

SwitchInt32 sw_multiplier("multiplier", "adjust multiplies for item pool sizes",
                          4);

std::vector<char> SlurpDataFromStream(std::istream* fin) {
  size_t num_bytes_per_read = 1024 * 1024;
  size_t current_offset = 0U;
  std::vector<char> out(num_bytes_per_read);
  auto rdbuf = fin->rdbuf();
  while (true) {
    size_t count =
        rdbuf->sgetn(out.data() + current_offset, num_bytes_per_read);
    if (count == 0) break;
    current_offset += count;
    out.resize(current_offset + num_bytes_per_read);
  }
  out.resize(current_offset);
  return out;
}

void MaybeEmitDoc(std::vector<PP::Token>* out, Node node) {
  Str doc = Node_comment(node);
  if (doc == StrInvalid) return;
  const char* data = StrData(doc);
  size_t start = 0;
  size_t end = 0;
  while (data[start] != '\0') {
    for (end = start; data[end] != '\n'; ++end);
    out->push_back(PP::Str(std::string_view(data + start, end - start)));
    out->push_back(PP ::LineBreak());
    start = end + 1;
  }
}
void EmitTokensTopLevel(std::vector<PP::Token>* out, Node node) {
  MaybeEmitDoc(out, node);
  out->push_back(PP::Beg(PP::BreakType::INCONSISTENT, 2));
  switch (Node_kind(node)) {
    case NT::DefGlobal:
      break;

    case NT::Import:
      out->push_back(PP::Str("import"));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(NameData(Node_name(node))));
      if (Node_path(node) != StrInvalid) {
        ASSERT(false, "");
      }
      if (Node_args_mod(node) != HandleInvalid) {
        ASSERT(false, "");
      }
      break;
    case NT::DefRec:
      out->push_back(PP::Str("rec"));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(NameData(Node_name(node))));
      out->push_back(PP::Brk(0));
      out->push_back(PP::Str(":"));
      break;
    default:
      break;
  }
  out->push_back(PP::End());
}

void EmitTokensModule(std::vector<PP::Token>* out, Node node) {
  ASSERT(Node_kind(node) == NT::DefMod, "");
  MaybeEmitDoc(out, node);
  out->push_back(PP::Beg(PP::BreakType::INCONSISTENT, 2));
  out->push_back(PP::Str("module"));
  //
  if (Node_params_mod(node) != HandleInvalid) {
    ASSERT(false, "");
  }
  //
  out->push_back(PP::Brk(0));
  out->push_back(PP::Str(":"));
  out->push_back(PP::End());
  if (Node_body_mod(node) != HandleInvalid) {
    out->push_back(PP::Beg(PP::BreakType::FORCE_LINE_BREAK, 0));
    bool emit_break = false;
    for (Node child = Node_body_mod(node); child != HandleInvalid;
         child = Node_next(child)) {
      out->push_back(PP::LineBreak());
      if (emit_break) {
        out->push_back(PP::LineBreak());
      }
      emit_break = true;
      EmitTokensTopLevel(out, child);
    }
    out->push_back(PP::End());
  }
}

void Prettify(Node mod) {
  std::vector<PP::Token> tokens;
  tokens.push_back(PP::Beg(PP::BreakType::CONSISTENT, 0));
  EmitTokensModule(&tokens, mod);
  tokens.push_back(PP::End());
  std::cout << PP::PrettyPrint(tokens, 80);
}

int main(int argc, const char* argv[]) {
  InitLexer();
  InitStripes(sw_multiplier.Value());
  InitParser();

  // If the synchronization is turned off, the C++ standard streams are allowed
  // to buffer their I/O independently from their stdio counterparts, which may
  // be considerably faster in some cases.
  // std::ios_base::sync_with_stdio(false);
  std::istream* fin = &std::cin;

  std::vector<char> data = SlurpDataFromStream(fin);
  Lexer lexer(
      std::string_view(reinterpret_cast<char*>(data.data()), data.size()), 555);
  // std::cout << "loaded " << data.size() << " bytes\n";

  Node mod = ParseDefMod(&lexer);
  Prettify(mod);
  return 0;
}