cmake_minimum_required(VERSION 3.10)
project(Cwerg)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-fno-exceptions -O3 -g")
set(CMAKE_EXE_LINKER_FLAGS "-static")
# The "whole-archive" dance is necessary for using std::condition_variable
# with static linking, see
# https://gcc.gnu.org/bugzilla/show_bug.cgi?id=58909
set(CMAKE_CXX_STANDARD_LIBRARIES "-lunwind -llzma  -Wl,--whole-archive -lpthread -Wl,--no-whole-archive")

include_directories(./)

add_library(UTIL_LIB OBJECT
        Util/assert.cc
        Util/assert.h
        Util/breakpoint.cc
        Util/breakpoint.h
        Util/bitvec.cc
        Util/bitvec.h
        Util/bst.cc
        Util/bst.h
        Util/handle.h
        Util/handlevec.cc
        Util/handlevec.h
        Util/immutable.cc
        Util/immutable.h
        Util/list.h
        Util/mem_pool.h
        Util/parse.cc
        Util/parse.h
        Util/stripe.cc
        Util/stripe.h
        Util/switch.cc
        Util/switch.h
        Util/webserver.cc
        Util/webserver.h
        )

add_executable(immutable_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/immutable_test.cc
        )

add_executable(bitvec_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/bitvec_test.cc
        )

add_executable(handle_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/handle_test.cc
        )

add_executable(handlevec_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/handlevec_test.cc
        )

add_executable(parse_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/parse_test.cc
        )

add_executable(mem_pool_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        Util/mem_pool_test.cc
        )

add_library(CPUA32_LIB OBJECT
        CpuA32/symbolic.cc
        CpuA32/symbolic.h
        CpuA32/assembler.cc
        CpuA32/assembler.h
        CpuA32/opcode_gen.cc
        CpuA32/opcode_gen.h
        )

add_library(CPUA32_LITE_LIB OBJECT
        CpuA32/symbolic.cc
        CpuA32/symbolic.h
        CpuA32/opcode_gen.cc
        CpuA32/opcode_gen.h
        )

add_executable(a32_opcode_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LITE_LIB>
        CpuA32/opcode_test.cc
        )

add_executable(a32_jit_example.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LITE_LIB>
        CpuA32/jit_example.cc
        )


add_library(CPUA64_LITE_LIB OBJECT
        CpuA64/symbolic.cc
        CpuA64/symbolic.h
        CpuA64/opcode_gen.cc
        CpuA64/opcode_gen.h
        )

add_executable(a64_opcode_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA64_LITE_LIB>
        CpuA64/opcode_test.cc
        )

add_executable(a64_disassembler_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA64_LITE_LIB>
        CpuA64/disassembler_tool.cc
        )

add_library(ELF_LIB OBJECT
        Elf/enum_gen.cc
        Elf/enum_gen.h
        Elf/elfhelper.cc
        Elf/elfhelper.h
        )

add_library(BASE_LIB OBJECT
        Base/canonicalize.cc
        Base/canonicalize.h
        Base/cfg.cc
        Base/cfg.h
        Base/ir.cc
        Base/ir.h
        Base/liveness.cc
        Base/liveness.h
        Base/lowering.cc
        Base/lowering.h
        Base/opcode_gen.cc
        Base/opcode_gen.h
        Base/sanity.cc
        Base/sanity.h
        Base/serialize.cc
        Base/serialize.h
        Base/reaching_defs.cc
        Base/reaching_defs.h
        Base/reg_stats.cc
        Base/reg_stats.h
        Base/reg_alloc.cc
        Base/reg_alloc.h
        Base/optimize.cc
        Base/optimize.h
        )

add_executable(optimize_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        Base/optimize_tool.cc
        )

add_executable(elf_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        Elf/elf_tool.cc
        )

add_executable(gen_elf_test.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        Elf/gen_elf_test.cc
        )

add_executable(a32_assembler_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        CpuA32/assembler_tool.cc
        )

add_executable(a32_disassembler_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        CpuA32/disassembler_tool.cc
        )

add_library(CODEGENA32_LIB OBJECT
        CodeGenA32/isel_gen.cc
        CodeGenA32/isel_gen.h
        CodeGenA32/codegen.cc
        CodeGenA32/codegen.h
        CodeGenA32/legalize.cc
        CodeGenA32/legalize.h
        CodeGenA32/regs.cc
        CodeGenA32/regs.h
        )

add_executable(a32_isel_tester.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CODEGENA32_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        ${CODEGENA32_LIB}
        CodeGenA32/isel_tester.cc
        )


add_executable(a32_codegen_tool.exe
        $<TARGET_OBJECTS:UTIL_LIB>
        $<TARGET_OBJECTS:CPUA32_LIB>
        $<TARGET_OBJECTS:ELF_LIB>
        $<TARGET_OBJECTS:CODEGENA32_LIB>
        $<TARGET_OBJECTS:BASE_LIB>
        CodeGenA32/codegen_tool.cc
        )

