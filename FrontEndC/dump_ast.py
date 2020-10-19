#!/usr/bin/python3

import sys

import pycparser

if __name__ == "__main__":
    ast = pycparser.parse_file(sys.argv[1], use_cpp=True)
    ast.show(showcoord=False)
