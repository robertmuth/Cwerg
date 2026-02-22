#!/bin/env python3
"""
A simple compiler driver for Cwerg
"""

import argparse
import os
import platform
import sys


def get_cwerg_root_directory():
    script_path = os.path.realpath(__file__)
    return os.path.dirname(script_path)


ROOT_DIR = get_cwerg_root_directory()

PY_FE = ROOT_DIR + "/FE/compiler.py"

PY_BE = {
    "x64": ROOT_DIR + "/BE/CodeGenX64/codegen.py",
    "a64": ROOT_DIR + "/BE/CodeGenA64/codegen.py",
    "a32": ROOT_DIR + "/BE/CodeGenA32/codegen.py",
}

CXX_FE = ROOT_DIR + "/build/compiler.exe"

CXX_BE = {
    "x64": ROOT_DIR + "/build/x64_codegen_tool.exe",
    "a64": ROOT_DIR + "/build/a64_codegen_tool.exe",
    "a32": ROOT_DIR + "/build/a32_codegen_tool.exe",
}

LINES = "=" * 80


def is_exe(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


ARCH_MAP = {
    'x86_64': 'x64',
    'aarch64': 'a64',
    'armv7l': 'a32',
}

SUPPORTED_ARCHS = set(ARCH_MAP.values())


def Diagnostics():
    print(LINES)
    print("Diagnostics")
    print(LINES)

    print(f"Cwerg root directory: {ROOT_DIR}")
    print(f"StdLib: {ROOT_DIR}/FE/Lib")
    print()
    print(f"Frontend PY: {PY_FE} {'✓' if is_exe(PY_FE) else '✗'}")
    for target, path in sorted(PY_BE.items()):
        print(f"Backend PY {target}: {path} {'✓' if is_exe(path) else '✗'}")

    print()
    print(f"Frontend C++: {CXX_FE} {'✓' if is_exe(PY_FE) else '✗'}")
    for target, path in sorted(CXX_BE.items()):
        print(f"Backend C++ {target}: {path} {'✓' if is_exe(path) else '✗'}")

    print()
    print(
        f"To rebuild the C++ components run: cd {ROOT_DIR} ; make build_compiler")
    print()


def main():
    if sys.version_info[0] != 3 or sys.version_info[1] < 12:
        print("Cwerg requires Python 3.12 or higher")
        return 1
    if not platform.platform().startswith("Linux"):
        print("Cwerg currently requires Linux")
        return 1

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-diag', help='show diagnostics and exit',
                        action='store_true')

    args, remainder = parser.parse_known_args()
    if args.diag:
        Diagnostics()
        return 0

    parser = argparse.ArgumentParser(description='cwerg compiler driver',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog="More info at http://cwerg.org")
    # replicated here so it appears in the help text
    parser.add_argument('-diag', help='show diagnostics and exit',
                        action='store_true')
    parser.add_argument('-arch', help='arch to generated code for',
                        default="auto")
    parser.add_argument('-v', help='switch verbose mode on',
                        action='store_true')
    # parser.add_argument('-tmp', help='directry for temp files', default="/tmp")

    parser.add_argument('input', metavar='input-src', type=str,
                        help='the input source file')
    parser.add_argument('output', metavar='output-exe', type=str,
                        help='the output executable')
    args = parser.parse_args(remainder)

    arch = args.arch
    if arch == "auto":
        arch = ARCH_MAP.get(platform.machine(), platform.machine())
    if arch not in SUPPORTED_ARCHS:
        print(
            f"Unsuppported arch {arch}. Cwerg currently targets only: x64 (X86_64/AMD64), a64 (Aarch64), a32 (ARMv7l)")
        return 1

    intermeditate_file = args.output + ".ir"
    fe_cmd = f"{CXX_FE} {args.input} {intermeditate_file}"
    if (args.v):
        print(fe_cmd)
    if 0 != os.system(fe_cmd):
        return 1

    be_cmd = f"{CXX_BE[arch]} {intermeditate_file} {args.output}"
    if (args.v):
        print(be_cmd)
    if 0 != os.system(be_cmd):
        return 1
    os.remove(intermeditate_file)
    print(arch)
    print(args.input)
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
