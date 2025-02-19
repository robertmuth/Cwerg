"""
Generic Pretty Printer based on:

Pretty Priting
Derek C. Oppen, 1979
https://www.cs.tufts.edu/~nr/cs257/archive/derek-oppen/prettyprinting.pdf


This version does away with all the space optimizations and
offline concerns of the paper resulting in a drastically
simpler algorithm.

The API consists of a single function `PrettyPrint`.
Which takes list of Tokens and returns a string with
formatted text.

A token may be one of:
* String
* Break
* Begin
* End

Enhancements to Oppen:
* a new BreakType, FORCE_LINE_BREAK, makes nesting easier
* a week annotation to Break helps with formatting Lisp like code

For usage see `tests.py`


Copyright 2025 Robert Muth <robert@muth.org>
See LICENSE for more details.
"""
from typing import Union

import enum
import dataclasses

_INFINITY = 1000000


class BreakType(enum.Enum):
    # No breaks are needed (the block fits on the line).
    # This will be automatically selected.
    FITS = 1
    # Fill line as much as possible then issue a line break and
    # continue in the same fashion on the next line
    INCONSISTENT = 2
    # If a block does not fit on a line, put each subblock
    # on a new line.
    CONSISTENT = 3
    # NOTE: THIS IS AN ADDITION TO THE ORIGINAL PAPER
    # Put each subblock on a new line
    # The `offset` applies even to the first line.
    # So this can be used as a nesting construct.
    FORCE_LINE_BREAK = 4


@dataclasses.dataclass()
class String:
    string: str


@dataclasses.dataclass()
class Break:
    """
    Either a space of widths `num_spaces` or a line break with additional
    `offset` relative to the indentation of the enclosing block
    """
    # Number of spaces if no overflow. Besides 1 the primary other values
    # are 0 and infinity (for LineBreak)
    num_spaces: int = 1
    # indent for overﬂow lines
    offset: int = 0
    # NOTE: THIS IS AN ADDITION TO THE ORIGINAL PAPER
    # This is useful with BreakType CONSISTENT to not automatically
    # force line breaks at the beginning of a group
    weak: bool = False


def LineBreak(offset=0):
    # Break which is guaranteed to overflow and hence forces a line break
    return Break(num_spaces=_INFINITY, offset=offset)


def WeakBreak(num_spaces):
    return Break(num_spaces, 0, True)


@dataclasses.dataclass()
class Begin:
    # how to handle Breaks nested between this `Begin`` and `End``
    break_type: BreakType
    # additional indent
    offset: int


@dataclasses.dataclass()
class End:
    pass


Token = Union[String, Break, Begin, End]


def _ComputeSizes(tokens: list[Token]):
    # Stack invariants:
    # only Begin and Break tokens can be on the stack
    # there are never two consecutive Break Tokens on the Stack
    # So the top of the stack is eiher [... Begin] or
    # [... Begin Break]
    scan_stack = []
    sizes = []
    total = 0  # corresponds to `rightotal` in the paper
    for n, token in enumerate(tokens):
        if isinstance(token, Begin):
            scan_stack.append(n)
            sizes.append(-total)
        elif isinstance(token, End):
            sizes.append(1)
            x = scan_stack.pop(-1)
            sizes[x] += total
            if isinstance(tokens[x], Break):
                x = scan_stack.pop(-1)
                sizes[x] += total
        elif isinstance(token, Break):
            # "close out" the last Break if there is one
            sizes.append(-total)
            z = scan_stack[-1]
            if isinstance(tokens[z], Break):
                z = scan_stack.pop()
                sizes[z] += total
            scan_stack.append(n)
            total += token.num_spaces
        elif isinstance(token, String):
            sizes.append(len(token.string))
            total += len(token.string)
        else:
            assert False, f"unknown token {token}"
    assert len(tokens) == len(sizes), f"{len(tokens)} {len(sizes)}"
    return sizes


def _UpdateSizeOfWeakBreaks(tokens: list[Token], sizes: list[int]):
    # Update chains of WeakBreaks from the right to have smaller sizes
    # This will result in WeakBreak to more likely fit in the current line
    total = _INFINITY
    for i in reversed(range(len(tokens))):
        token: Token = tokens[i]
        if isinstance(token, Begin):
            pass
        elif isinstance(token, End):
            total = _INFINITY
        elif isinstance(token, String):
            total += sizes[i]
        elif isinstance(token, Break):
            if token.weak:
                if total < sizes[i]:
                    sizes[i] = total
                    total += token.num_spaces
                else:
                    total = sizes[i]
            else:
                total = 0
    # Add to the break preceding a sequence of WeakBreaks
    # this should prevent breaking at WeakBreaks because
    # we break earlier at the preceding Break
    total = 0
    for i in reversed(range(len(tokens))):

        token: Token = tokens[i]
        if isinstance(token, Begin):
            pass
        elif isinstance(token, End):
            pass
        elif isinstance(token, String):
            total += sizes[i]
        elif isinstance(token, Break):
            total += token.num_spaces
            if not token.weak:
                if total > sizes[i]:
                    sizes[i] = total
                total = 0

class _Output:

    def __init__(self: "_Output", line_width: int):
        self.buffer: list[str] = []
        self.remaining = line_width  # how much space is left in current line
        self.line_width = line_width  # constant

    def append(self, s):
        self.buffer.append(s)

    def get_string(self):
        return "".join(self.buffer)

    def append_with_space_update(self, s):
        self.buffer.append(s)
        self.remaining -= len(s)

    def current_indent(self):
        return self.line_width - self.remaining

    def fits_in_current_line(self, size: int) -> bool:
        return size <= self.remaining

    def set_offset(self, offset: int):
        self.remaining = offset

    def line_break(self):
        self.buffer.append("\n")
        self.buffer.append(" " * self.current_indent())


@dataclasses.dataclass()
class _Entry:
    offset: int  # same measurement as `remaining`, i.e.`offset`== margin means zero indent
    break_type: BreakType


def _Render(tokens, sizes, output: _Output):
    print_stack: list[_Entry] = []

    for token, size in zip(tokens, sizes):
        if isinstance(token, Begin):
            if token.break_type == BreakType.FORCE_LINE_BREAK:
                if print_stack:
                    offset = print_stack[-1].offset
                    output.set_offset(offset - token.offset)
                    output.line_break()
                else:
                    offset = output.line_width
                entry = _Entry(
                    output.remaining, token.break_type)
            elif output.fits_in_current_line(size):
                entry = _Entry(0, BreakType.FITS)
            else:
                bt = (BreakType.CONSISTENT
                      if token.break_type == BreakType.CONSISTENT
                      else BreakType.INCONSISTENT)
                entry = _Entry(
                    output.remaining - token.offset, bt)
            print_stack.append(entry)
        elif isinstance(token, End):
            print_stack.pop()
            # Note, not resetting the offset right away in the
            # non-FORCE_LINE_BREAK case is responsible for the
            # behavior characterized in the paper as:
            # "In particular, it effectively changes (dynamically)
            # each occurrence of ] (string) into (string) ]."
        elif isinstance(token, Break):
            top = print_stack[-1]

            if token.weak and output.fits_in_current_line(size):
                output.append_with_space_update(
                    " " * token.num_spaces)  # indent
            elif top.break_type == BreakType.FITS:
                output.append_with_space_update(
                    " " * token.num_spaces)  # indent
            elif top.break_type in (BreakType.CONSISTENT, BreakType.FORCE_LINE_BREAK):
                output.set_offset(top.offset - token.offset)
                output.line_break()
            elif top.break_type == BreakType.INCONSISTENT:
                if output.fits_in_current_line(size):
                    output.append_with_space_update(
                        " " * token.num_spaces)  # indent
                else:
                    output.set_offset(top.offset - token.offset)
                    output.line_break()

        elif isinstance(token, String):
            # TODO: handle long/multiline strings
            assert size == len(token.string)
            output.append_with_space_update(token.string)
        else:
            assert False, f"Unsupported token {token}"


def PrettyPrint(tokens: list[Token], line_width: int) -> str:
    # print(tokens)
    output = _Output(line_width)
    sizes: list[int] = _ComputeSizes(tokens)
    _UpdateSizeOfWeakBreaks(tokens, sizes)
    #for t, s in zip(tokens, sizes):
    #    print (t, s)
    _Render(tokens, sizes, output)
    return output.get_string()
