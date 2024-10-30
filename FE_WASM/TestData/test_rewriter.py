#!/bin/env python3

"""
This tool helps rewriting wast test for use with Cwerg.

Usage:
./test_rewrite.py < test.wast > test.rewritten.wast

Note: test.rewritten.wast will NOT be a valid wast file
further hand editing is necessary.
"""

import collections
import sys
import re
from typing import List, Dict

RE_EXPORT = re.compile(r'\s*\(func\s\(export\s"([-_.a-zA-Z0-9$]+)"')

RE_ASSERT = re.compile(r'^\((assert_[a-z0-9]+)\s+(.*)$')

RE_INVOKE = re.compile(r'\(invoke\s+"([-_.a-zA-Z0-9]+)"\s*(.*)$')

RE_PARAM = re.compile(r'(\([.0-9a-z]+\s+[-+.0-9xXeEpPa-fA-F]+\))\s*(.*)$')


def Rename(s: str):
    return "$" + s.replace("-", "_").replace(".", "_")


# (assert_return (invoke "nested-block-value" (i32.const 0)) (i32.const 19))
# (call $assert_eq_i32 (i32.const 2800) (call $ge_u (i32.const 1) (i32.const 0)) (i32.const 1))


def ParseAssertReturn(line):
    m = RE_INVOKE.match(line)
    assert m
    params = []
    expected = None
    fun_name = m.group(1)
    rest = m.group(2)
    while rest.startswith("("):
        m = RE_PARAM.match(rest)
        assert m
        params.append(m.group(1))
        rest = m.group(2)
    assert rest.startswith(")")
    rest = rest[1:].strip()
    if rest.startswith("("):
        m = RE_PARAM.match(rest)
        assert m, f"could not parse return {line}"
        expected = m.group(1)
    return Rename(fun_name), params, expected


def main(fin):
    last_fun = None
    method_no = 1000
    test_no = 0
    for line in fin:
        if line.startswith(";;"):
            print(line, end="")
            continue

        m = RE_EXPORT.match(line)
        if m:
            # print(Rename(m.group(1)))
            name = Rename(m.group(1))
            line = line.replace("func ", "func " + name + " ").replace(m.group(1), name[1:])
            print(line, end="")
            continue

        m = RE_ASSERT.match(line)
        if m:
            if m.group(1) != "assert_return":
                continue
            fun_name, params, expected = ParseAssertReturn(m.group(2))
            if fun_name != last_fun:
                method_no += 100
                test_no = 0
                last_fun = fun_name
            test_no += 1
            if not expected:
                print(f"(call {fun_name} {' '.join(params)})")
                continue
            check = f"$assert_eq_{expected[1:4]}"
            no = method_no + test_no
            print(f"(call {check} (i32.const {no}) (call {fun_name} {' '.join(params)}) {expected})")

            continue

        print(line, end="")


if __name__ == "__main__":
    sys.exit(main(sys.stdin))
