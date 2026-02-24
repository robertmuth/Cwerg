; canonical huffman tree decoder
;
; https://datatracker.ietf.org/doc/html/rfc1951 Section 3.2
; https://en.wikipedia.org/wiki/Canonical_Huffman_code
;
;
; Usage:
;
; Assumptions:
; * encoded was as set symbols numbered 0-MAX_SYMBOLS
; * for each symbol the width of the associated huffman code was recorded in a length slice
; * unused symbols have a widths of 0
; * we do not need to know the actual code for a symbol because we use canonical codes
;
module:

import bitstream

pub global BAD_SYMBOL u16 = 0xffff

pub global BAD_TREE_ENCODING u16 = 0xffff

global MAX_SYMBOLS uint = 0xff00

; Decode the next symbol from a bitstream
;
; This function has two failure modes:
; * the bitstream may run out of bits
;   This must be checked by the caller
; * the retrieved bits are out of range
;   This will result in BAD_SYMBOL to be returned
;
;   counts[i] contains the number of huffman code of 2^i
;   Note counts[0] is not used
;
pub fun NextSymbol(bs ^!bitstream\Stream32, counts span(u16), symbols span(u16)
                   ) u16:
    let! offset u32 = 0
    let! base u32 = 0
    for level = 1, len(counts), 1:
        set offset <<= 1
        set offset += bitstream\Stream32GetBits(bs, 1)
        let count u32 = as(counts[level], u32)
        if offset < count:
            set base += offset
            return symbols[base]
        set base += count
        set offset -= count
    return BAD_SYMBOL

; Check that symbol count at a level can be encoded
;
;
fun CountsAreFeasible(counts span(u16)) bool:
    let! available u16 = 2
    for level = 1, len(counts), 1:
        let used = counts[level]
        if used > available:
            return false
        else:
            set available = (available - used) * 2
    return available == 0

;
; Popoulates the counts and sybols from lengths
;
; lengths[sym] contains the bitwidth of synbol sym.
;
; Returns the number of elements in symbols populated which is usally
; the number of nonzero entries in lengths.
;
; If lengths has exactly one non-zero elemenmt an extra dummy element
; will be inserted into symbols and 2 will be returned.
;
; counts[width] contains the number of elments in lengths having value width.
; Note counts[0] is always 0
;
;
pub fun ComputeCountsAndSymbolsFromLengths(lengths span(u16), counts span!(u16),
                                           symbols span!(u16)) u16:
    if len(lengths) > MAX_SYMBOLS:
        return BAD_TREE_ENCODING
    for level = 0, len(counts), 1:
        set counts[level] = 0
    let! last u16 = 0
    for i = 0, len(lengths), 1:
        let bits = lengths[i]
        if bits != 0:
            set last = as(i, u16)
            if as(bits, uint) >= len(counts):
                return BAD_TREE_ENCODING
            set counts[bits] += 1
    let! n u16 = 0
    for i = 1, len(counts), 1:
        set n += counts[i]
    cond:
        case n == 0:
            ; this is odd but some tests rely on it
            return 0_u16
        case n == 1:
            ; also see below for more special handling
            if counts[1] != 1:
                return BAD_TREE_ENCODING
        case true:
            if !CountsAreFeasible(counts):
                return BAD_TREE_ENCODING
    ; accumulate counts to get offsets
    ;     counts[i] := sum(0<= x <= i, counts[x])
    ;     
    set n = 0
    for i = 1, len(counts), 1:
        set n += counts[i]
        set counts[i] = n
    ; fill in symbols grouped by bit-width preserving ordered for same width symbols
    for i = 0, len(symbols), 1:
        set symbols[i] = BAD_SYMBOL
    for i = 0, len(lengths), 1:
        let bits = lengths[i]
        if bits != 0:
            let offset = counts[bits - 1]
            set symbols[offset] = as(i, u16)
            set counts[bits - 1] += 1
    ; de-accumulate to get back original count
    ;
    ;     at this point we have: counts_now[i] == sum(0<= x <= i + 1, counts_orig[x])
    ;     we compute:  counts_orig[i] := counts_now[i - 1] -   counts_now[i - 2]
    ;
    ;     n0 is the original value of the element at index i-2
    ;     n1 is the original value of the element at index i-1
    let! n0 u16 = 0
    let! n1 u16 = 0
    for i = 0, len(counts), 1:
        let d = n1 - n0
        set n0 = n1
        set n1 = counts[i]
        set counts[i] = d
    ; weird case
    if n == 1:
        set counts[1] = 2
        set symbols[1] = BAD_SYMBOL
        set n += 1
    return n
