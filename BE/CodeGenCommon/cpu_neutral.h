
#include <string_view>

#include "BE/Base/ir.h"

namespace cwerg::code_gen_common {

using namespace cwerg;
using namespace cwerg::base;

std::string_view SectionNameForMem(Mem mem);

void JtbCodeGenSimpleText(Jtb jtb, std::ostream* output, int addr_size);

void MemCodeGenText(Mem mem, std::ostream* output);

template <typename UNIT>
void MemCodeGenBinary(Mem mem, int reloc_kind, UNIT* out) {
  std::string_view padding_zero("\0", 1);

  out->MemStart(StrData(Name(mem)), MemAlignment(mem),
                SectionNameForMem(mem), padding_zero, false);
  for (Data data : MemDataIter(mem)) {
    uint32_t size = DataSize(data);
    Handle target = DataTarget(data);
    int32_t extra = DataExtra(data);
    if (base::Kind(target) == RefKind::STR) {
      out->AddData(extra, StrData(Str(target)), size);
    } else if (base::Kind(target) == RefKind::FUN) {
      out->AddFunAddr(size, reloc_kind, StrData(Name(Fun(target))));
    } else {
      ASSERT(base::Kind(target) == RefKind::MEM, "");
      out->AddMemAddr(size, reloc_kind, StrData(Name(Mem(target))), extra);
    }
  }
  out->MemEnd();
}
template <typename UNIT>
void JtbCodeGenSimpleBinary(Jtb jtb, int addr_size, int reloc_kind, UNIT* out) {
  std::string_view padding_zero("\0", 1);

  std::vector<Bbl> table(JtbSize(jtb), JtbDefBbl(jtb));
  for (Jen jen : JtbJenIter(jtb)) {
    table[JenPos(jen)] = JenBbl(jen);
  }
  out->MemStart(StrData(Name(jtb)), addr_size, "rodata", padding_zero, true);
  for (Bbl bbl : table) {
    out->AddBblAddr(addr_size, reloc_kind, StrData(Name(bbl)));
  }
  out->MemEnd();
}

}  // namespace cwerg::code_gen_common