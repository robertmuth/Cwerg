#!/bin/env python3

"""

"""
from typing import List
import sys

from Util import parse


def EmitString(s: str):
    b = parse.EscapedStringToBytes(t[1:-1])
    t2 = parse.BytesToEscapedString(b)
    print('"' + t2 + '"', end="")


def EmitId(s: str):
    print("{" + t + "}", end="")


if __name__ == '__main__':
    mode = sys.argv[1]
    for line in sys.stdin:
        print()
        line = line[:-1]
        print(line)
        if mode == "lex":
            try:
                token: List[str] = parse.ParseLine(line)
                # print (repr(token))
                sep = ""
                for t in token:
                    print(sep, end="")
                    sep = " "
                    if t.startswith('"'):
                        EmitString(t)
                    else:
                        EmitId(t)

            except Exception as err:
                print("@FAILED@")
            print()
        else:
            assert mode == "num"
            token = line.split()
            assert len(token) == 2
            if token[0] == "uint64":
                val = parse.ParseUint64(token[1])
                if val is None:
                    print(f"[UINT64] @BAD VALUE@")
                else:
                    print(f"[UINT64] {val} {val:x}")
            elif token[0] == "int64":
                val = parse.ParseInt64(token[1])
                if val is None:
                    print(f"[INT64] @BAD VALUE@")
                else:
                    print(f"[INT64] {val} {val & ((1 << 64) - 1):x}")
            elif token[0] == "flt64":
                val = parse.ParseFlt64(token[1])
                if val is None:
                    print(f"[FLT64] @BAD VALUE@")
                else:
                    print(f"[FLT64] {val:g} {parse.Flt64ToBits(val):x}")
            elif token[0] == "char":
                val = parse.ParseChar(token[1])
                if val is None:
                    print(f"[CHAR] @BAD VALUE@")
                else:
                    print(f"[CHAR] {val}")
