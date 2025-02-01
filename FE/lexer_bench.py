#!/bin/env python3

import sys

from FE import lexer


def Run():
    inp = lexer.LexerRaw("stdin", sys.stdin)
    while True:
        tk = inp.next_token()
        kind = tk.kind
        if kind is lexer.TK_KIND.SPECIAL_EOF:
            break
        print (f"{kind.name}")
if __name__ == "__main__":
    Run()