@doc """canonical huffman trees

https://datatracker.ietf.org/doc/html/rfc1951 Section 3.2
https://en.wikipedia.org/wiki/Canonical_Huffman_code

"""
(module huffman [] :

(import bitstream)

(global BAD_SYMBOL u16 0xffff)

@doc """Decode the next symbol from a bitstream

This function has two failure modes:
* the bitstream may run out of bits
  This must be checked by the caller
* the retrieved bits are out of range
  This will result in BAD_SYMBOL to be returned

  Note counts[0] is not used
"""
(fun NextSymbol [(param bs (ptr @mut bitstream::Stream32))
                 (param counts (slice u16))
                 (param symbols (slice u16))] u16 :
   (let @mut offset u32 0)
   (let @mut base u32 0)

   (for level 1 (len counts) 1 :
      (<<= offset 1)
      (+= offset (bitstream::Stream32GetBits [bs 1]))
      (let count u32 (as (at counts level) u32))
      (if (< offset count) :
          (+= base offset)
          (return (at symbols base))
      :)
      (+= base count)
      (-= offset count)
   )
   (return BAD_SYMBOL)
)


(global BAD_TREE_ENCODING u16 0xffff)
(global MAX_SYMBOLS uint 0xff00)


@doc """Check that symbol count at a level can be encoded

"""
(fun CountsAreFeasible [(param counts (slice u16))] bool :
    (let @mut available u16 2)
    (for level 1 (len counts) 1 :
        (let used auto (at counts level))
        (if (> used available) :
            (return false)
        :
            (= available (* (- available used) 2))
        )
    )
    (return (== available 0))
)


@doc """
Returns highest symbol encountered. Usually that value is
(len lengths) - 1

Note counts[0] is always 0
"""
(fun @pub ComputeCountsAndSymbolsFromLengths [
       (param lengths (slice u16))
       (param counts (slice @mut u16))
       (param symbols (slice @mut u16))] u16 :
    (if (> (len lengths) MAX_SYMBOLS) : (return BAD_TREE_ENCODING) :)
    (if (< (len lengths) 2) : (return BAD_TREE_ENCODING) :)

    (for level 0 (len counts) 1 :
        (= (at counts level) 0))
    (let @mut last u16 0)
    (for i 0 (len lengths) 1 :
        (let bits auto (at lengths i))
        (if (!= bits 0) :
        (= last (as i u16))
        (+= (at counts bits) 1)
        :)
    )
    (if (! (CountsAreFeasible [counts])) :
        (return BAD_TREE_ENCODING)
    :)

    @doc "accumulate counts to get offsets"
    (let @mut n u16 0)
    (for i 1 (len counts) 1 :
        (+= n (at counts i))
        (= (at counts i) n)
    )

    @doc "fill in symbols"
    (for i 0 (len lengths) 1 :
        (let bits auto (at lengths i))
        (if (!= bits 0) :
            (let offset auto (at counts (- bits 1)))
            (= (at symbols offset) (as i u16))
            (+= (at counts (- bits 1)) 1)
        :)
    )

    @doc """de-accumulate to get back original count
    n0 is the original value of the element at index i-2
    n1 is the original value of the element at index i-1"""
    (let @mut n0 u16 0)
    (let @mut n1 u16 0)
    (for i 0 (len counts) 1 :
        (let d auto(- n1 n0))
        (= n0 n1)
        (= n1 (at counts i))
        (= (at counts i) d)
    )
    (return last)
)

)