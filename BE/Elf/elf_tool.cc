#include "BE/Elf/elfhelper.h"
#include "Util/assert.h"

#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <iostream>
#include <string_view>

using namespace cwerg::elf;
using namespace cwerg;

void VerifyChunks(const std::vector<std::string_view>& chunks,
                  std::string_view data) {
  size_t offset = 0;
  for (const auto& chunk : chunks) {
    // std::cout << "Checking " << std::hex << chunk.size() << "\n";
    CHECK(chunk == data.substr(offset, chunk.size()), "");
    offset += chunk.size();
  }
}

int main(int argc, char* argv[]) {
  if (argc <= 1) {
    std::cout << "No file specified\n";
    return 1;
  }
  const int fd = open(argv[1], O_RDONLY);
  if (fd < 0) {
    std::cout << "Cannot open file " << argv[1] << "\n";
    return 1;
  }
  struct stat s;
  if (fstat(fd, &s) < 0) {
    std::cout << "Cannot stat file " << argv[1] << "\n";
    return 1;
  }

  const void* mapped = mmap(nullptr, s.st_size, PROT_READ, MAP_PRIVATE, fd, 0);

  std::string_view data((const char*)mapped, s.st_size);
  EI_CLASS cls = ElfDetermineClass(data);
  std::cout << "class is " << EnumToString(cls) << "\n";
  if (cls == EI_CLASS::X_64) {
    Executable<uint64_t> exe;
    if (!exe.Load(data)) {
      std::cout << "cannot load " << argv[1] << "\n";
      return 1;
    }
    const uint64_t header_size = CombinedElfHeaderSize<uint64_t>(exe.segments);
    const uint64_t section_header_offset =
        exe.VerifyVaddrsAndOffsets(header_size, exe.start_vaddr);
    CHECK(exe.ehdr.e_shoff == section_header_offset, "");
    CHECK(exe.ehdr.e_phoff == sizeof(exe.ident) + sizeof(exe.ehdr), "");
    exe.ehdr.e_shoff = exe.UpdateVaddrsAndOffsets(header_size, exe.start_vaddr);
    exe.ehdr.e_phoff = sizeof(exe.ident) + sizeof(exe.ehdr);


    std::vector<std::string_view> chunks = exe.Save();
    VerifyChunks(chunks, data);
    // std::cout << exe;
  } else if (cls == EI_CLASS::X_32) {
    Executable<uint32_t> exe;
    if (!exe.Load(data)) {
      std::cout << "cannot load " << argv[1] << "\n";
      return 1;
    }
    const uint32_t header_size = CombinedElfHeaderSize<uint32_t>(exe.segments);
    const uint32_t section_header_offset =
        exe.VerifyVaddrsAndOffsets(header_size, exe.start_vaddr);
    CHECK(exe.ehdr.e_shoff == section_header_offset, "");
    CHECK(exe.ehdr.e_phoff == sizeof(exe.ident) + sizeof(exe.ehdr), "");
    exe.UpdateVaddrsAndOffsets(header_size, exe.start_vaddr);
    std::vector<std::string_view> chunks = exe.Save();
    VerifyChunks(chunks, data);
    // std::cout << exe;
  } else {
    std::cout << "unsupported EI_CLASS in " << argv[1] << "\n";
    return 1;
  }
  return 0;
}
