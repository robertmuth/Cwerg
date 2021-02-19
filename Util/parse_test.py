#!/usr/bin/python3

"""

"""
from typing import List
import sys
import re

from Util import parse


def EmitString(s: str):
    b = parse.EscapedStringToBytes(t[1:-1])
    t2 = parse.BytesToEscapedString(b)
    print('"' + t2 + '"', end="")


def EmitId(s: str):
    print("{" + t + "}", end="")


def EmitNum(s: str):
    if parse.IsInt(s):
        x = int(s)
        if x < 0:
            print(parse.NegToHexString(-x) + "#", end="")
        else:
            print(parse.PosToHexString(x) + "#", end="")
    else:
        x = float(s)
        print(parse.FltToHexString(x) + "#", end="")


if __name__ == '__main__':
    for line in sys.stdin:
        print()
        line = line[:-1]
        print(line)
        try:
            token: List[str] = parse.ParseLine(line)
            # print (repr(token))
            sep = ""
            for t in token:
                print(sep, end="")
                sep = " "
                if t.startswith('"'):
                    EmitString(t)
                elif parse.IsNum(t):
                    EmitNum(t)
                else:
                    EmitId(t)
            print()
        except Exception as err:
            print("@FAILED@")
