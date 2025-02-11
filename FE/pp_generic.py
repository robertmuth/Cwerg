"""Pretty Priting References

Original Paper [Derek Oppen]: https://www.cs.tufts.edu/~nr/cs257/archive/derek-oppen/prettyprinting.pdf
Wadler's Functional Version: https://homepages.inf.ed.ac.uk/wadler/papers/prettier/prettier.pdf
JEAN-PHILIPPE BERNARDY: https://jyp.github.io/pdf/Prettiest.pdf

Nice historical summary:
https://observablehq.com/@freedmand/pretty-printing

Code:
Wadler/Leijen Pretty Printer: https://hackage.haskell.org/package/wl-pprint
Another Wadler/Leijen PP: https://github.com/quchen/prettyprinter/
Jean-Philippe Bernardy Prettiest: https://github.com/jyp/prettiest

Reddit Thread:
https://www.reddit.com/r/ProgrammingLanguages/comments/vzp7td/pretty_printing_which_paper/
https://www.reddit.com/r/haskell/comments/6e62i5/ann_prettyprinter_10_ending_the_wadlerleijen_zoo/
"""
import sys
import dataclasses
import logging

from typing import Optional, Union

@dataclasses.dataclass()
class EOL:
    """Forced Line Break"""
    pass

@dataclasses.dataclass()
class WS:
    """Whitespace (Breakable)"""
    pass


@dataclasses.dataclass()
class Text:
    """Text Snippet"""
    text: str


@dataclasses.dataclass()
class TextMultiLine:
    """Text Snippet"""
    text: str


@dataclasses.dataclass()
class Doc:
    """"Introduces a new ident level"""
    indent: int
    children: list


@dataclasses.dataclass()
class Group:
    beg: str
    end: str
    children: list
