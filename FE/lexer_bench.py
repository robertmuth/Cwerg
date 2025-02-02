#!/bin/env python3

import sys

from FE import lexer_tab as lexer


def Run():
    inp = lexer.LexerRaw("stdin", sys.stdin)
    while True:
        tk = inp.next_token()
        kind = tk.kind
        if kind is lexer.TK_KIND.SPECIAL_EOF:
            break
        print(f"{kind.name} {tk.srcloc.lineno} {tk.column} {tk.text}")


if __name__ == "__main__":
    if 0:
        from cProfile import Profile
        from pstats import SortKey, Stats
        with Profile() as profile:
            ret = Run()
            Stats(profile).strip_dirs().sort_stats(SortKey.CALLS).print_stats()
            exit(ret)
    else:
        Run()
