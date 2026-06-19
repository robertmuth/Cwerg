#include "BE/CodeGenCommon/cpu_neutral.h"

#include "BE/Base/serialize.h"
#include "Util/parse.h"

namespace cwerg::code_gen_common {

using namespace cwerg;
using namespace cwerg::base;

std::string_view MemKindToSectionName(MEM_KIND kind) {
  switch (kind) {
    case MEM_KIND::RO:
      return "rodata";
    case MEM_KIND::RW:
      return "data";
    default:
      ASSERT(false, "");
      return "";
  }
}

void JtbCodeGenSimpleText(Jtb jtb, std::ostream* output, int addr_size) {
  std::vector<Bbl> table(JtbSize(jtb), JtbDefBbl(jtb));
  for (Jen jen : JtbJenIter(jtb)) {
    table[JenPos(jen)] = JenBbl(jen);
  }
  *output << ".localmem " << Name(jtb) << " " << addr_size << " rodata\n";
  for (Bbl bbl : table) {
    *output << "    .addr.bbl " << addr_size << " " << Name(bbl) << "\n";
  }
  *output << ".endmem\n";
}

void MemCodeGenText(Mem mem, std::ostream* output) {
  *output << "# size " << MemSize(mem) << "\n"
          << ".mem " << Name(mem) << " " << MemAlignment(mem) << " "
          << MemKindToSectionName(MemKind(mem)) << "\n";
  for (Data data : MemDataIter(mem)) {
    uint32_t size = DataSize(data);
    Handle target = DataTarget(data);
    int32_t extra = DataExtra(data);
    if (Kind(target) == RefKind::STR) {
      size_t len = size;
      char buffer[4096];
      if (len > 0) {
        len = BytesToEscapedString({StrData(Str(target)), len}, buffer);
      }
      buffer[len] = 0;
      *output << "    .data " << extra << " \"" << buffer << "\"\n";
    } else if (Kind(target) == RefKind::FUN) {
      *output << "    .addr.fun " << size << " " << Name(Fun(target)) << "\n";
    } else {
      ASSERT(Kind(target) == RefKind::MEM, "");
      *output << "    .addr.mem " << size << " " << Name(Mem(target))
              << std::hex << " 0x" << extra << std::dec << "\n";
    }
  }

  *output << ".endmem\n";
}



}  // namespace cwerg::code_gen_common