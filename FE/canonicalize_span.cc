
#include "FE/canonicalize_span.h"

#include <array>

#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "FE/typify.h"
#include "Util/parse.h"

namespace cwerg::fe {

Node MakeSpanReplacementStruct(CanonType span_ct, TypeCorpus* tc) {
  std::array<NameAndType, 2> fields = {{
      NameAndType{NameNew("pointer"), tc->InsertPtrFromSpan(span_ct)},
      NameAndType{NameNew("length"), tc->get_uint_canon_type()},
  }};
  std::string name = "xtuple_";
  name += NameData(CanonType_name(span_ct));
  return MakeDefRec(NameNew(name), fields, tc);
}

NodeChain MakeAndRegisterSpanTypeReplacements(TypeCorpus* tc) {
  NodeChain out;
  tc->ClearReplacementInfo();
  CanonType new_ct;
  for (CanonType ct : tc->InTopoOrder()) {
    if (CanonType_is_span(ct)) {
      Node rec = MakeSpanReplacementStruct(ct, tc);
      out.Append(rec);
      new_ct = Node_x_type(rec);
    } else {
      new_ct = tc->MaybeGetReplacementType(ct);
      if (new_ct.isnull()) {
        continue;
      }
    }
    CanonTypeLinkReplacementType(ct, new_ct);
  }
  return out;
}

void ReplaceSpans(Node mod) {}

}  // namespace cwerg::fe