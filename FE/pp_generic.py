#!/usr/bin/python3
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

from typing import Optional, Any


@dataclasses.dataclass()
class Line:
    """Whitespace (Breakable)"""
    alt: str = " "


@dataclasses.dataclass()
class Text:
    """Text Snippet"""
    text: str


@dataclasses.dataclass()
class TextMultiLine:
    """Text Snippet"""
    text: str


@dataclasses.dataclass()
class Nest:
    """"Introduces a new ident level"""
    indent: int
    doc: Any


@dataclasses.dataclass()
class Concat:
    """"Introduces a new ident level"""
    docs: list[Any]


@dataclasses.dataclass()
class LazyUnion:

    a_lazy: Any
    b: Any

    @staticmethod
    def Make(doc):
        return LazyUnion(None, doc)

    def a(self):
        if self.a_lazy is None:
            self.a_lazy = Flatten(self.b)
        return self.a_lazy


def Flatten(doc: Any) -> Any:
    while isinstance(doc, LazyUnion):
        doc = doc.a()
    if isinstance(doc, Concat):
        return Concat([Flatten(d) for d in doc.docs])
    elif isinstance(doc, Nest):
        return Nest(doc.indent, Flatten(doc.doc))
    elif isinstance(doc, Line):
        return Text(doc.alt)
    else:
        return doc


def Size(doc: Any, cutoff: int) -> int:
    if isinstance(doc, LazyUnion):
        return Size(doc.b, cutoff)
    if isinstance(doc, Concat):
        total = 0
        for d in doc.docs:
            total += Size(d, cutoff - total)
            if total > cutoff:
                break
        return total
    elif isinstance(doc, Nest):
        return Size(doc.doc, cutoff)
    elif isinstance(doc, Line):
        return len(doc.alt)
    elif isinstance(doc, Text):
        return len(doc.text)
    else:
        assert False


def Best(pairs: list[tuple[int, Any]], max_line_width, current_width):
    print("@@BEST[", current_width, "]", pairs)
    for indent, doc in pairs:
        # print("@@LOOP[", current_width, "]", pairs)

        if doc is None:
            pass
        elif isinstance(doc, Concat):
            for x in Best([(indent, d) for d in doc.docs], max_line_width, current_width):
                yield x
        elif isinstance(doc, Nest):
            for x in Best([(indent + doc.indent, doc.doc)], max_line_width, current_width):
                yield x
        elif isinstance(doc, Text):
            yield doc.text
            current_width += len(doc.text)
        elif isinstance(doc, Line):
            yield "\n" + " " * indent
            current_width = indent
        elif isinstance(doc, LazyUnion):
            cutoff = max_line_width - current_width
            if Size(doc.b, cutoff) <= cutoff:
                a  = Flatten(doc.b)
                for x in Best([(indent, a)], max_line_width, current_width):
                    yield x
            else:
                for x in Best([(indent, doc.b)], max_line_width, current_width):
                    yield x
        else:
            assert False


def Test1():
    c = Nest(4, Concat([Line()] + [Text(x) for x in "0123456789"]))
    for x in Best([(0, c)], 20, 0):
        print(x, end="")
    print()

def Test2():

    c = []
    for x in "0123456789abcde":
        c.append(Text(x))
        c.append(Line())
    d = LazyUnion.Make(Concat(c))
    for x in Best([(0, d)], 40, 0):
        print(x, end="")
    print()



if __name__ == "__main__":
    Test2()
