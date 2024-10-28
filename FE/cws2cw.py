#!/usr/bin/python3
"""Concrete Syntax Pretty printer (PP) for Cwerg AST to concrete syntax

"""


import logging
import sys


from FE import parse_sexpr
from FE import pp

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.WARN)
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    mod = parse_sexpr.ReadModFromStream(sys.stdin, "stdin")
    pp.AddMissingParens(mod)
    pp.PrettyPrint(mod, sys.stdout)
