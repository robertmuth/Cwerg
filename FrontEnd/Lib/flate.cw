@doc "flate https://www.w3.org/TR/PNG-Compression.html"
(module flate [] :

(import bitstream)
(import fmt)
(import huffman)

(macro xdebug! STMT_LIST [(mparam $parts EXPR_LIST)] [] :
   (fmt::print! [ $parts ])
)

(macro debug! STMT_LIST [(mparam $parts EXPR_LIST)] [] :)

(macro xdump_slice! STMT_LIST [
   (mparam $prefix EXPR) (mparam $slice EXPR)] [$s_eval $i] :
   (macro_let $s_eval auto $slice)
   (for $i 0 (len $s_eval) 1 :
       (fmt::print! [$prefix $i " -> " (at $s_eval $i) "\n"]))
)

(macro dump_slice! STMT_LIST [
   (mparam $prefix EXPR) (mparam $slice EXPR)] [$s $i] :)

@doc "the input bitstream was corrupted"
(type @pub @wrapped CorruptionError void)
(global @pub CorruptionErrorVal auto (wrap void_val CorruptionError))

@doc "the input bitstream was truncated"
(type @pub @wrapped TruncationError void)
(global @pub TruncationErrorVal auto (wrap void_val TruncationError))

@doc "the provided output buffer was not large enough"
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
          (debug! ["tree decoding num=" i  " sym=" sym " len=1"  "\n"])
          (=  (at lengths i) sym)
          (+= i 1)
        )
        (case (== sym 16) :
            (if (== i 0) : (return CorruptionErrorVal)  :)
            (let prev auto (at lengths (- i 1)))
            (let @mut n auto (+ (bitstream::Stream32GetBits [bs 2]) 3))
            (debug! ["tree decoding num=" i  " sym=" sym " len=" n "\n"])
            (while (> n 0) :
               (-= n 1)
               (= (at lengths i) prev)
               (+= i 1)
            )
        )
        (case (== sym 17) :
            (let @mut n auto (+ (bitstream::Stream32GetBits [bs 3]) 3))
            (if (> (+ i (as n uint)) (len lengths)) : (return CorruptionErrorVal) :)
            (debug! ["tree decoding num=" i  " sym=" sym " len=" n "\n"])
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
            (debug! ["tree decoding num=" i  " sym=0" " len=" n "\n"])
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

@doc "amount of bytes to copy: fixed base"
(global width_base_lookup auto (array_val 29 u16 [
		 3  4  5   6   7   8   9  10  11  13
		15 17 19  23  27  31  35  43  51  59
		67 83 99 115 131 163 195 227 258
]))

@doc "amount of bytes to copy: bit count of variable part"
(global width_bits_lookup auto (array_val 29 u8 [
		0 0 0 0 0 0 0 0 1 1
		1 1 2 2 2 2 3 3 3 3
		4 4 4 4 5 5 5 5 0
]))


@doc "distance to the bytes to copy: fixed base"
(global dist_base_lookup auto (array_val 30 u16 [
		   1    2    3    4    5    7    9    13    17    25
		  33   49   65   97  129  193  257   385   513   769
		1025 1537 2049 3073 4097 6145 8193 12289 16385 24577
]))

@doc "distance to the bytes to copy: bit count of variable part"
(global dist_bits_lookup auto (array_val 30 u8 [
		0 0  0  0  1  1  2  2  3  3
		4 4  5  5  6  6  7  7  8  8
		9 9 10 10 11 11 12 12 13 13
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
   (debug! ["handle_huffman_common " pos "\n"])
   (let @mut i uint pos)
   (while true :
     (let sym auto (huffman::NextSymbol [bs lit_counts lit_symbols]))
     (debug! ["["  i "]  symbol " sym "\n"])

     (if (bitstream::Stream32Eos [bs]) :
        (debug! ["  eos\n" ])
        (return TruncationErrorVal)
     :)
     (if (== sym huffman::BAD_TREE_ENCODING) :
      (return CorruptionErrorVal)
     :)
     (cond :
        @doc "end of huffman code"
        (case (== sym 256) :
         (return i)
        )
        @doc "huffman symbol is decoded symbol"
        (case (< sym 256) :
          (=  (at dst i) (as sym u8))
          (+= i 1)
        )
        @doc """copy data that was previously decompressed

        The amount of data to be copied, `width`, is computed from the symbol and some extra
        bits from the stream.

        The backward distance is computed by reading another symbol using the `dist` tree.
        """
        (case  (< sym (+ (as (len width_bits_lookup) u16) 257)) :
            (let sym_width auto (- sym 257))
            (let width u32 (+
                (as (at width_base_lookup sym_width) u32)
                (bitstream::Stream32GetBits [bs (at width_bits_lookup sym_width)])))
            (let sym_dist auto (huffman::NextSymbol [bs dist_counts dist_symbols]))
            (if (bitstream::Stream32Eos [bs]) :
                (return TruncationErrorVal) :)
            (if (> sym_dist (as (len dist_bits_lookup) u16)) :
                (return CorruptionErrorVal) :)
            (let distance u32 (+ (bitstream::Stream32GetBits [bs (at dist_bits_lookup sym_dist)])
                             (as (at dist_base_lookup sym_dist) u32)))
            (if (bitstream::Stream32Eos [bs]) :
                (return TruncationErrorVal) :)
            (if (> (as distance uint) i) :
                (return CorruptionErrorVal) :)
            (if (> (+ i (as width uint)) (len dst)) :
                (return NoSpaceErrorVal) :)
            (debug! [ "copy " width " " distance "\n"])
            (for x 0 width 1 :
               (= (at dst i) (at dst (- i (as distance uint))))
               (+= i 1)
            )

        )
        (case true : (return CorruptionErrorVal))
     )
   )
   @doc "unreachable"
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
   (debug! ["handle_dynamic_huffman lit_num_syms="  lit_num_syms
                 " dist_num_syms=" dist_num_syms  " cl_num_syms=" cl_num_syms "\n"])

   @doc ""
   (let @mut @ref lit_dist_lengths (array (+ MAX_DIST_SYMS  MAX_LIT_SYMS) u16))
   (block _ :
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
         (debug! ["sym length " i ": "  (at cl_lengths (at CodeLenCodeIndex i)) "\n"])
      )
      (let cl_last_symbol u16 (huffman::ComputeCountsAndSymbolsFromLengths
                  [cl_lengths cl_counts cl_symbols]))
      (if (== cl_last_symbol huffman::BAD_TREE_ENCODING) :
         (return CorruptionErrorVal)
      :)

      (debug! [ "decode combined lengths for lit + dist\n"])
      (if (> lit_num_syms  286) : (return CorruptionErrorVal) :)
      (if (> dist_num_syms 30) : (return CorruptionErrorVal) :)

      (let lit_dist_slice auto (slice_val (front @mut lit_dist_lengths) (+ lit_num_syms dist_num_syms)))
      (try x Success (read_lit_dist_lengths [bs cl_counts cl_symbols
                                    lit_dist_slice]) err :
                                                (return err))
   )
   (dump_slice! "combo: "
                 (slice_val (front lit_dist_lengths)
                            (+ lit_num_syms dist_num_syms))
   )


   (let @mut lit_symbols (array MAX_LIT_SYMS u16))
   (let @mut lit_counts (array (+ MAX_HUFFMAN_BITS 1) u16))
   (block _ :
      (let lit_lengths auto (slice_val (front @mut lit_dist_lengths)  lit_num_syms))
      (let lit_last_symbol u16 (huffman::ComputeCountsAndSymbolsFromLengths
                  [lit_lengths lit_counts lit_symbols]))
      (if (== lit_last_symbol huffman::BAD_TREE_ENCODING) :
         (return CorruptionErrorVal)
      :)
      (debug! ["computed literal tree. last=" lit_last_symbol "\n"])
   )


   (let @mut dist_symbols (array MAX_DIST_SYMS u16))
   (let @mut dist_counts (array (+ MAX_HUFFMAN_BITS 1) u16))
   (block _ :
      (let dist_lengths auto (slice_val (incp (front @mut lit_dist_lengths) lit_num_syms) dist_num_syms))
      (let dist_last_symbol u16 (huffman::ComputeCountsAndSymbolsFromLengths
                  [dist_lengths dist_counts dist_symbols]))

      (if (== dist_last_symbol huffman::BAD_TREE_ENCODING) :
          (debug! ["BAD ENCODING\n"])
          (return CorruptionErrorVal)
      :)
      (debug! ["computed distance tree. last=" dist_last_symbol "\n"])
   )


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

@doc """fixed lit:

 24 (width=7):   256-279
144 (width=8):     0-143
  8 (width=8):   280-287
112 (width=9):   144-255

last symbol: 285
"""
(global fixed_lit_counts auto (array_val 10 u16 [
   0 0 0 0 0 0 0 24 152 112
]))


(global fixed_lit_symbols auto (array_val 288 u16 [
   256 257 258 259  260 261 262 263
   264 265 266 267  268 269 270 271
   272 273 274 275  276 277 278 279
     0   1   2   3    4   5   6   7
     8   9  10  11   12  13  14  15
    16  17  18  19   20  21  22  23
    24  25  26  27   28  29  30  31
    32  33  34  35   36  37  38  39
    40  41  42  43   44  45  46  47
    48  49  50  51   52  53  54  55
    56  57  58  59   60  61  62  63
    64  65  66  67   68  69  70  71
    72  73  74  75   76  77  78  79
    80  81  82  83   84  85  86  87
    88  89  90  91   92  93  94  95
    96  97  98  99  100 101 102 103
   104 105 106 107  108 109 110 111
   112 113 114 115  116 117 118 119
   120 121 122 123  124 125 126 127
   128 129 130 131  132 133 134 135
   136 137 138 139  140 141 142 143
   280 281 282 283  284 285 286 287
   144 145 146 147  148 149 150 151
   152 153 154 155  156 157 158 159
   160 161 162 163  164 165 166 167
   168 169 170 171  172 173 174 175
   176 177 178 179  180 181 182 183
   184 185 186 187  188 189 190 191
   192 193 194 195  196 197 198 199
   200 201 202 203  204 205 206 207
   208 209 210 211  212 213 214 215
   216 217 218 219  220 221 222 223
   224 225 226 227  228 229 230 231
   232 233 234 235  236 237 238 239
   240 241 242 243  244 245 246 247
   248 249 250 251  252 253 254 255
]))


@doc """fixed dist:

 32 (width=5):   0-31

last symbol: 29
"""
(global fixed_dist_counts auto (array_val 6 u16 [
   0 0 0 0 0 32
]))

(global fixed_dist_symbols auto (array_val 32 u16 [
     0   1   2   3    4   5   6   7
     8   9  10  11   12  13  14  15
    16  17  18  19   20  21  22  23
    24  25  26  27   28  29  30  31
]))

@doc "handle 0b01 section"
(fun handle_fixed_huffman [(param bs (ptr @mut bitstream::Stream32))
                      (param pos uint)
                      (param dst (slice @mut u8))]
                      (union [uint CorruptionError NoSpaceError TruncationError]) :
   (debug! ["handle_fixed_huffman\n"])
   (return (handle_huffman_common [
         bs
         fixed_lit_counts
         fixed_lit_symbols
         fixed_dist_counts
         fixed_dist_symbols
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
   (debug! ["handle_uncompressed\n"])
   (stmt (bitstream::Stream32SkipToNextByte [bs]))
   (let length u32 (bitstream::Stream32GetBits [bs 16]))
   (let inv_length u32 (bitstream::Stream32GetBits [bs 16]))
   (if (bitstream::Stream32Eos [bs]) : (return TruncationErrorVal) :)
   (if (!= length (and (! inv_length) 0xffff)) :
      (return CorruptionErrorVal)
   :)
   (debug! ["uncompressed " length "\n"])

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
   (debug! ["FlateUncompress\n"])
   @doc "next position within dst to write"
   (let @mut pos uint 0)
   (let @mut seen_last bool false)
   (while (! seen_last) :
     (= seen_last (bitstream::Stream32GetBool [bs]))
     (let kind u32 (bitstream::Stream32GetBits [bs 2]))
     (if (bitstream::Stream32Eos [bs]) :
          (return TruncationErrorVal)
     :)
     (debug! ["new round last=" seen_last "\n"])
     (cond :
       (case (== kind 0) :
         (try new_pos uint (handle_uncompressed [bs pos dst]) err :
            (return err))

         (= pos new_pos)
       )
       @doc "fixed huffman"
       (case (== kind 1) :
         (try new_pos uint (handle_fixed_huffman [bs pos dst]) err :
            (return err))

         (= pos new_pos)
       )
       (case (== kind 2) :
         (try new_pos uint (handle_dynamic_huffman [bs pos dst]) err :
            (return err))

         (= pos new_pos)
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