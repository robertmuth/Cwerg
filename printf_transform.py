#!/usr/bin/python3

import re

PRINTF_OPTION = re.compile(r"%([-+ 0]*)([0-9]*)([.][0-9]+)?([lqh]+)?([cduoxefgsp])")

LENGTH_TRANSLATION = {
    None: "",
    "l": "l",
    "ll": "q",
    "q": "q",
    "h": "h",
}


class FormatOptions:

    def __init__(self, s: str):
        m = PRINTF_OPTION.match(s)
        assert m
        flags, width, precision, length, kind = m.groups()
        self.kind = kind
        self.length = LENGTH_TRANSLATION.get(length, "")
        self.precision = int(precision[1:]) if precision else -1
        self.width = int(width) if width else -1
        self.show_sign = "+" in flags
        self.adjust_left = "-" in flags
        self.pad_with_zero = "0" in flags
        self.space_for_plus = " " in flags

    def __str__(self):
        f = []
        if self.show_sign: f.append("+")
        if self.adjust_left: f.append("-")
        if self.pad_with_zero: f.append("0")
        if self.space_for_plus: f.append(" ")
        return "[FormatOptions (%s) %d %d %s %s]" % ("".join(f), self.width, self.precision, self.length, self.kind)


def TokenizeFormatString(s: str):
    out = []
    last = 0

    def add_plain(start, end):
        if start != end:
            plain = s[start: end]
            out.append(plain if plain != "%%" else "%")

    for m in PRINTF_OPTION.finditer(s):
        start, end = m.span()
        add_plain(last, start)
        last = end
        out.append(m.group(0))
    add_plain(last, len(s))
    return out


if __name__ == "__main__":
    import sys

    for a in sys.argv[1:]:
        print([str(x) for x in TokenizeFormatString(a)])
