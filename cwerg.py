#!/bin/env python3
"""
A simple compiler driver for Cwerg
"""

import argparse
import os
import platform
import sys
from typing import Any


def get_cwerg_root_directory():
    script_path = os.path.realpath(__file__)
    return os.path.dirname(script_path)


ROOT_DIR = get_cwerg_root_directory()


LINES = "=" * 80


def is_exe(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


# maps deom platform.machine() to Cwerg name
ARCH_MAP: dict[str, str] = {
    'x86_64': 'x64',
    'aarch64': 'a64',
    'armv7l': 'a32',
}

SUPPORTED_ARCHS: set[str] = set(ARCH_MAP.values())


FE_MAP: dict[str, str] = {
    "py": ROOT_DIR + "/FE/compiler.py",
    "cxx": ROOT_DIR + "/build/compiler.exe",
}


def GetFeCommand(fe_tag: str, input: str, output: str) -> str:
    fe = FE_MAP.get(fe_tag)
    if fe is None:
        print(f"Unknown frontend {fe_tag}")
        exit(1)
    if not is_exe(fe):
        print(f"Frontend executable not found {fe}")
        if fe_tag.startswith("cxx_"):
            print(f"""
You may need to build the excutable first like so:

cd ${ROOT_DIR}
make build_compiler
""")

        exit(1)
    return f"{fe} {input} > {output}"


def get_backend(prefix: str) -> str:
    arch: str = ARCH_MAP.get(platform.machine(), platform.machine())
    if arch is None:
        print(f"Cannot find backend for arch {platform.machine()}")
        exit(1)
    return BE_MAP.get(prefix + arch)


BE_MAP: dict[str, Any] = {
    "py_x64": ("x64", ROOT_DIR + "/BE/CodeGenX64/codegen.py"),
    "py_a64": ("a64", ROOT_DIR + "/BE/CodeGenA64/codegen.py"),
    "py_a32": ("a32", ROOT_DIR + "/BE/CodeGenA32/codegen.py"),
    "py_auto": lambda: get_backend("py_"),
    "cxx_x64": ("x64", ROOT_DIR + "/build/x64_codegen_tool.exe"),
    "cxx_a64": ("a64", ROOT_DIR + "/build/a64_codegen_tool.exe"),
    "cxx_a32": ("a32", ROOT_DIR + "/build/a32_codegen_tool.exe"),
    "cxx_auto": lambda: get_backend("cxx_"),
}


SYSLIB_MAP: dict[str, str] = {
    "x64": (ROOT_DIR + "/BE/StdLib/startup.x64.asm", ROOT_DIR + "/BE/StdLib/syscall.x64.asm"),
    "a64": (ROOT_DIR + "/BE/StdLib/startup.a64.asm", ROOT_DIR + "/BE/StdLib/syscall.a64.asm"),
    "a32": (ROOT_DIR + "/BE/StdLib/startup.a32.asm", ROOT_DIR + "/BE/StdLib/syscall.a32.asm"),
}


def GetBeCommand(be_tag: str, input: str, output: str) -> str:
    be = BE_MAP.get(be_tag)
    if be is None:
        print(f"Unknown backend {be_tag}")
        exit(1)
    if callable(be):
        be = be()
    if not is_exe(be[1]):
        print(f"Backend executable not found: {be}")
        if be_tag.startswith("cxx_"):
            print(f"""
You may need to build the excutable first like so:

cd ${ROOT_DIR}
make build_compiler
""")
        exit(1)
    syslibs = SYSLIB_MAP[be[0]]
    return f"{be[1]} -mode binary {' '.join(syslibs)} {input} {output}"


def Diagnostics():
    print(LINES)
    print("Diagnostics")
    print(LINES)

    print(f"Cwerg root directory: {ROOT_DIR}")
    print(f"StdLib: {ROOT_DIR}/FE/Lib")

    print()
    print(LINES)
    print("Frontends (py = Python implementation, cxx = C++ implementation):")
    print(LINES)
    for name, path in sorted(FE_MAP.items()):
        if callable(path):
            path = path()
        print(f"{name:10} {path} {'✓' if is_exe(path) else '✗'}")

    print()
    print(LINES)
    print("Backends (py_ = Python implementation, cxx_ = C++ implementation):")
    print(LINES)
    for name, (arch, path) in sorted(BE_MAP.items()):
        if callable(path):
            path = path()
        print(f"{name:10} {arch:4} {path} {'✓' if is_exe(path) else '✗'}")

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

    parser = argparse.ArgumentParser(description='Cwerg compiler driver',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog="More info at http://cwerg.org")
    # replicated args here so it appears in the help text
    parser.add_argument('-diag', help='show diagnostics and exit',
                        action='store_true')
    #
    parser.add_argument('-fe', help=f"frontend to use",
                        default="cxx", choices=FE_MAP.keys())
    parser.add_argument('-be', help=f"backend to use",
                        default="cxx_auto",  choices=BE_MAP.keys())
    parser.add_argument('-v', help='switch verbose mode on',
                        action='store_true')
    parser.add_argument('-dry_run', help='show but do not execute commands',
                        action='store_true')
    # parser.add_argument('-tmp', help='directry for temp files', default="/tmp")

    parser.add_argument('input', metavar='input-src', type=str,
                        help='the input source file')
    parser.add_argument('output', metavar='output-exe', type=str,
                        help='the output executable')
    args = parser.parse_args(remainder)

    intermeditate_file = args.output + ".ir"

    fe_cmd = GetFeCommand(args.fe, args.input, intermeditate_file)
    if args.v or args.dry_run:
        print(fe_cmd)
    if not args.dry_run:
        if 0 != os.system(fe_cmd):
            return 1

    be_cmd = GetBeCommand(args.be, intermeditate_file, args.output)
    if args.v or args.dry_run:
        print(be_cmd)
    if not args.dry_run:
        if 0 != os.system(be_cmd):
            return 1

    rm_cmd = f"chmod a+x {args.output} ; rm -f {intermeditate_file}"
    if args.v or args.dry_run:
        print(rm_cmd)
    if not args.dry_run:
        if 0 != os.system(rm_cmd):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
