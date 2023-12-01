@doc "flate https://www.w3.org/TR/PNG-Compression.html"
(module flate [] :

(import bitstream)
(import fmt)
(import huffman)

(type @pub @wrapped CorruptionError void)
(global @pub CorruptionErrorVal auto (wrap void_val CorruptionError))

(type @pub @wrapped TruncationError void)
(global @pub TruncationErrorVal auto (wrap void_val TruncationError))

(type @pub @wrapped NoSpaceError void)
(global @pub NoSpaceErrorVal auto (wrap void_val NoSpaceError))

(type @pub @wrapped Success void)
(global @pub SuccessVal auto (wrap void_val Success))

(global MAX_HUFFMAN_BITS u16 15)
(global MAX_LIT_SYMS u16 288)
(global MAX_DIST_SYMS u16 32)
(global NUM_CODE_LEN_SYMS u16 19)


(global CodeLenCodeIndex auto (array_val 19 u8 [
   16 17 18 0 8 7 9 6 10 5 11 4 12 3 13 2 14 1 15
]))


@doc "read length for the combined literal and distance huffman costs"
(fun read_lit_dist_lengths [(param bs (ptr @mut bitstream::Stream32))
                            (param cl_counts (slice u16))
                            (param cl_symbols (slice u16))
                            (param lengths (slice @mut u16))]
                           (union [Success CorruptionError TruncationError]) :
   (let @mut i uint 0)
   (while (< i (len lengths)) :
      (let sym auto (huffman::NextSymbol [bs cl_counts cl_symbols]))
      (if (== sym huffman::BAD_SYMBOL) :
         (return CorruptionErrorVal)
      :)
      (if (bitstream::Stream32Eos [bs]) :
          (return TruncationErrorVal)
      :)
      (cond :
        (case (< sym 16) :
          (=  (at lengths i) sym)
          (+= i 1)
        )
        (case (== sym 16) :
            (if (== i 0) : (return CorruptionErrorVal)  :)
            (let prev auto (at lengths (- i 1)))
            (let @mut n auto (+ (bitstream::Stream32GetBits [bs 2]) 3))
            (while (> n 0) :
               (-= n 1)
               (= (at lengths i) prev)
               (+= i 1)
            )
        )
        (case (== sym 17) :
            (let @mut n auto (+ (bitstream::Stream32GetBits [bs 3]) 3))
            (if (> (+ i (as n uint)) (len lengths)) : (return CorruptionErrorVal) :)
            (block _ :
               (-= n 1)
               (= (at lengths i) 0)
               (+= i 1)
               (if (!= n 0) : (continue) :)
            )
        )
        (case (== sym 18) :
            (let @mut n auto (+ (bitstream::Stream32GetBits [bs 7]) 11))
            (if (> (+ i (as n uint)) (len lengths)) : (return CorruptionErrorVal) :)
            (block _ :
               (-= n 1)
               (= (at lengths i) 0)
               (+= i 1)
               (if (!= n 0) : (continue) :)
            )
        )
        (case true :
         (return CorruptionErrorVal)
        )
      )
   )
   (return SuccessVal)
)

(macro incs! EXPR [(mparam $slice EXPR) (mparam $length EXPR)] [] :
   (slice_val (incp (front @mut $slice) $length)
              (- (len $slice) $length))
)

(global width_bits_lookup auto (array_val 29 u8 [
		0 0 0 0 0 0 0 0 1 1
		1 1 2 2 2 2 3 3 3 3
		4 4 4 4 5 5 5 5 0
]))

(global width_base_lookup auto (array_val 29 u16 [
		 3  4  5   6   7   8   9  10  11  13
		15 17 19  23  27  31  35  43  51  59
		67 83 99 115 131 163 195 227 258
]))

(global dist_bits_lookup auto (array_val 30 u8 [
		0 0  0  0  1  1  2  2  3  3
		4 4  5  5  6  6  7  7  8  8
		9 9 10 10 11 11 12 12 13 13
]))

(global dist_base_lookup auto (array_val 30 u16 [
		   1    2    3    4    5    7    9    13    17    25
		  33   49   65   97  129  193  257   385   513   769
		1025 1537 2049 3073 4097 6145 8193 12289 16385 24577
]))


@doc "common part for handing both dynamic and fixed hufman"
(fun handle_huffman_common [
   (param bs (ptr @mut bitstream::Stream32))
   (param lit_counts (slice u16))
   (param lit_symbols (slice u16))
   (param dist_counts (slice u16))
   (param dist_symbols (slice u16))
   (param pos uint)
   (param dst (slice @mut u8)) ]
 (union [uint CorruptionError NoSpaceError TruncationError]) :
   (let @mut i uint pos)
   (while true :
     (let sym auto (huffman::NextSymbol [bs lit_counts lit_symbols]))
     (if (bitstream::Stream32Eos [bs]) : (return TruncationErrorVal) :)
     (if (== sym huffman::BAD_TREE_ENCODING) :
      (return CorruptionErrorVal)
     :)
     (cond :
        (case (== sym 256) :
         (return i)
        )
        (case (< sym 256) :
          (=  (at dst i) (as sym u8))
          (+= i 1)
        )
        (case  (< sym (+ (as (len width_bits_lookup) u16) 257)) :
            (let sym_width auto (- sym 257))
            (let width u32 (+ (bitstream::Stream32GetBits [bs (at width_bits_lookup sym_width)])
                              (as (at width_base_lookup sym_width) u32)))
            (let sym_dist auto (huffman::NextSymbol [bs dist_counts dist_symbols]))
            (if (bitstream::Stream32Eos [bs]) : (return TruncationErrorVal) :)
            (if (> sym_dist (as (len dist_bits_lookup) u16)) : (return CorruptionErrorVal) :)
            (let distance u32 (+ (bitstream::Stream32GetBits [bs (at dist_bits_lookup sym_dist)])
                             (as (at dist_base_lookup sym_dist) u32)))
            (if (bitstream::Stream32Eos [bs]) : (return TruncationErrorVal) :)
            (if (> (as distance uint) i) : (return CorruptionErrorVal) :)
            (if (> (+ i (as width uint)) (len dst)) : (return NoSpaceErrorVal) :)
            (for x 0 width 1 :
               (= (at dst i) (at dst (- i (as distance uint))))
               (+= i 1)
            )

        )
        (case true : (return CorruptionErrorVal))
     )
   )
   (return i)
)

@doc "handle 0b10 section"
(fun handle_dynamic_huffman [(param bs (ptr @mut bitstream::Stream32))
                      (param pos uint)
                      (param dst (slice @mut u8))]
                      (union [uint CorruptionError NoSpaceError TruncationError]) :
   (let lit_num_syms uint (as (+ (bitstream::Stream32GetBits [bs 5]) 257) uint))
	(let dist_num_syms uint (as (+ (bitstream::Stream32GetBits [bs 5]) 1) uint))
   (let cl_num_syms uint (as (+ (bitstream::Stream32GetBits [bs 4]) 4) uint))

   @doc "build the code_len auxiliary huffman tree"
   (let @mut cl_lengths (array NUM_CODE_LEN_SYMS u16))
   (let @mut cl_symbols (array NUM_CODE_LEN_SYMS u16))
   (let @mut cl_counts (array (+ MAX_HUFFMAN_BITS 1) u16))

   (for i 0 (len cl_lengths) 1 :
      (= (at cl_lengths i) 0)
   )
   (for i 0 cl_num_syms 1 :
      (= (at cl_lengths (at CodeLenCodeIndex i))
         (as (bitstream::Stream32GetBits [bs 3]) u16))
   )
   (let cl_last_symbol u16 (huffman::ComputeCountsAndSymbolsFromLengths
                [cl_lengths cl_counts cl_symbols]))
   (if (== cl_last_symbol huffman::BAD_TREE_ENCODING) :
      (return CorruptionErrorVal)
   :)

   @doc "decode combined lengths for lit + dist"
   (if (> lit_num_syms  286) : (return CorruptionErrorVal) :)
   (if (> dist_num_syms 30) : (return CorruptionErrorVal) :)

   (let @mut @ref lit_dist_lengths (array (+ MAX_DIST_SYMS  MAX_LIT_SYMS) u16))
   (let lit_dist_slice auto (slice_val (front @mut lit_dist_lengths) (+ lit_num_syms dist_num_syms)))
   (try x Success (read_lit_dist_lengths [bs cl_counts cl_symbols
                                 lit_dist_slice]) err :
                                             (return err))
   @doc "literal tree"
   (let lit_lengths auto (slice_val (incp (front @mut lit_dist_lengths) dist_num_syms) lit_num_syms))
   (let @mut lit_symbols (array MAX_LIT_SYMS u16))
   (let @mut lit_counts (array (+ MAX_HUFFMAN_BITS 1) u16))
   (let lit_last_symbol u16 (huffman::ComputeCountsAndSymbolsFromLengths
                [lit_lengths lit_counts lit_symbols]))

   (if (== lit_last_symbol huffman::BAD_TREE_ENCODING) :
      (return CorruptionErrorVal)
   :)

   @doc "distance tree"
   (let dist_lengths auto (slice_val (incp (front @mut lit_dist_lengths) lit_num_syms) dist_num_syms))
   (let @mut dist_symbols (array MAX_DIST_SYMS u16))
   (let @mut dist_counts (array (+ MAX_HUFFMAN_BITS 1) u16))

   (let dist_last_symbol u16 (huffman::ComputeCountsAndSymbolsFromLengths
                [dist_lengths dist_counts dist_symbols]))

   (if (== dist_last_symbol huffman::BAD_TREE_ENCODING) :
      (return CorruptionErrorVal)
   :)

   (return (handle_huffman_common [
         bs
         lit_counts
         (slice_val (front lit_symbols) lit_num_syms)
         dist_counts
         (slice_val (front dist_symbols) dist_num_syms)
         pos
         dst
      ]))
)

@doc "handle 0b00 section"
(fun handle_uncompressed [
    (param bs (ptr @mut bitstream::Stream32))
    (param pos uint)
    (param dst (slice @mut u8))
   ] (union [uint CorruptionError NoSpaceError TruncationError]) :
   (stmt (bitstream::Stream32SkipToNextByte [bs]))
   (let length u32 (bitstream::Stream32GetBits [bs 16]))
   (let inv_length u32 (bitstream::Stream32GetBits [bs 16]))
   (if (bitstream::Stream32Eos [bs]) : (return TruncationErrorVal) :)
   (if (!= length (and (! inv_length) 0xffff)) :
      (return CorruptionErrorVal)
   :)
   (fmt::print! ["uncompressed " length "\n"])

   (let src auto (bitstream::Stream32GetByteSlice [bs (as length uint)]))

   (if (bitstream::Stream32Eos [bs]) : (return CorruptionErrorVal) :)

   (if (< (len dst) (as length uint)) : (return NoSpaceErrorVal) :)
   (for i 0 (len src) 1 :
      (= (at dst (+ pos i)) (at src i))
   )
   (return (+ pos (len src)))
)



(fun @pub uncompress [
   (param bs (ptr @mut bitstream::Stream32))
   (param dst (slice @mut u8))
   ] (union [uint CorruptionError NoSpaceError TruncationError]) :
   (fmt::print! ["FlateUncompress\n"])
   (let @mut pos uint 0)
   (let @mut seen_last bool false)
   (while (! seen_last) :
     (= seen_last (bitstream::Stream32GetBool [bs]))
     (let kind u32 (bitstream::Stream32GetBits [bs 2]))
     (if (bitstream::Stream32Eos [bs]) :
          (return TruncationErrorVal)
     :)
     (fmt::print! ["new round " seen_last " " kind "\n"])
     (cond :
       (case (== kind 0) :
         (try new_pos uint (handle_uncompressed [bs pos dst]) err :
            (return err))

         (= pos new_pos)
       )
       @doc "fixed huffman"
       (case (== kind 1) :
         (trap)
       )
       (case (== kind 2) :
         (try new_pos uint (handle_dynamic_huffman [bs pos dst]) err :
            (return err))

         (+= pos new_pos)
       )
       @doc "reserved"
       (case true :
         (return CorruptionErrorVal)
       )
     )
   )
   (return pos)
)

)