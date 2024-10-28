#!/usr/bin/python3


import collections
import sys

if __name__ == "__main__":
    seen = set()
    names = collections.defaultdict(int)
    for line in sys.stdin:
        line = line[:-1]
        line  = line.split("<")[0]
        line  = line.split("#")[0]
        try:
            addr_str, data_str, ins_str = line.strip().split("\t")
        except:
            continue
        name = ins_str.split()[0]

        key = data_str
        if name in {"call", "jmp"}:
            # there are just too many
            key  = ins_str
        if key in seen:
            continue
        seen.add(key)

        names[name] += 1
        print (line)

