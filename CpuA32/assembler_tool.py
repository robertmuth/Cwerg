#!/usr/bin/python3
"""
Assembler produces A32 ELF executables
"""
import CpuA32.assembler as asm

import argparse
import os
import stat
import sys


def lint(input):
    src = sys.stdin if input == "-" else open(input)
    print("UNIT", asm.UnitParse(src))


def assemble_common(input, output, add_startup_code):
    src = sys.stdin if input == "-" else open(input)
    dst = sys.stdout if output == "-" else open(output, "wb")
    unit = asm.UnitParse(src, add_startup_code)
    for sym in unit.symbols:
        assert sym.section, f"undefined symbol: {sym}"

    #print(unit)
    exe = asm.Assemble(unit, True)
    #for phdr in exe.segments:
    #    print(phdr)
    #    for sec in phdr.sections:
    #        print(sec)
    print("WRITING EXE")
    exe.save(dst)
    if output != "-":
        os.chmod(output, stat.S_IREAD | stat.S_IEXEC | stat.S_IWRITE)


def assemble_raw(input, output):
    assemble_common(input, output, False)


def assemble(input, output):
    assemble_common(input, output, True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='assembler_tool')
    subparsers = parser.add_subparsers(dest='subparser')

    parser_lint = subparsers.add_parser('lint', description='just parse the input and print result')
    parser_lint.add_argument('input', type=str, help='input file')

    parser_assemble = subparsers.add_parser('assemble_raw', description='parse and emit elf exe')
    parser_assemble.add_argument('input', type=str, help='input file')
    parser_assemble.add_argument('output', type=str, help='output file')

    parser_assemble = subparsers.add_parser(
        'assemble',
        description='parse and emit elf exe. Also add _start entry point calling main')
    parser_assemble.add_argument('input', type=str, help='input file')
    parser_assemble.add_argument('output', type=str, help='output file')

    args = parser.parse_args()

    kwargs = vars(parser.parse_args())
    globals()[kwargs.pop('subparser')](**kwargs)
