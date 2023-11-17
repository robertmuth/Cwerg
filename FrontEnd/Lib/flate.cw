@doc "flate https://www.w3.org/TR/PNG-Compression.html"
(module flate [] :

(import bitstream)
(import fmt)
(import huffman)


(type @pub @wrapped CorruptionErrorType void)
(global @pub CorruptionError auto (wrap void_val CorruptionErrorType))

(type @pub @wrapped NoSpaceErrorType void)
(global @pub NoSpaceError auto (wrap void_val NoSpaceErrorType))

(type @pub @wrapped SuccessType void)
(global @pub Success auto (wrap void_val SuccessType))

(global MAX_HUFFMAN_BITS u16 15)
(global MAX_LIT_SYMS u16 288)
(global MAX_DIST_SYMS u16 32)
(global NUM_CODE_LEN_SYMS u16 19)


(global CodeLenCodeIndex auto (array_val 19 u8 [
   @doc ""
   16
   17
   18
   0
   8
   7
   9
   6
   10
   5
   11
   4
   12
   3
   13
   2
   14
   1
   15
]))


@doc "read length for the combined literal and distance huffman costs"
(fun read_lit_dist_lengths [(param bs (ptr @mut bitstream::Stream32))
                            (param cl_counts (slice u16))
                            (param cl_symbols (slice u16))
                            (param lengths (slice @mut u16))]
                           (union [SuccessType CorruptionErrorType]) :
   (let @mut i uint 0)
   (while (< i (len lengths)) :
      (let sym auto (huffman::NextSymbol [bs cl_counts cl_symbols]))
      (if (== sym huffman::BAD_SYMBOL) :
         (return CorruptionError)
      :)
      (if (bitstream::Stream32Eos [bs]) :
          (return CorruptionError)
      :)
      (cond :
        (case (< sym 16) :
          (=  (at lengths i) sym)
          (+= i 1)
        )
        (case (== sym 16) :
            (if (== i 0) : (return CorruptionError)  :)
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
            (if (> (+ i (as n uint)) (len lengths)) : (return CorruptionError) :)
            (block _ :
               (-= n 1)
               (= (at lengths i) 0)
               (+= i 1)
               (if (!= n 0) : (continue) :)

            )
        )
        (case (== sym 18) :
            (let @mut n auto (+ (bitstream::Stream32GetBits [bs 7]) 11))
            (if (> (+ i (as n uint)) (len lengths)) : (return CorruptionError) :)
            (block _ :
               (-= n 1)
               (= (at lengths i) 0)
               (+= i 1)
               (if (!= n 0) : (continue) :)
            )
        )
        (case true :
         (return CorruptionError)
        )
      )
   )
   (return Success)
)

(macro incs! EXPR [(mparam $slice EXPR) (mparam $length EXPR)] [] :
   (slice_val (incp (front @mut $slice) $length)
              (- (len $slice) $length))
)

@doc """

"""
(fun handle_dynamic_huffman [(param bs (ptr @mut bitstream::Stream32))
                      (param dst_buf (slice @mut u8))]
                      (union [uint CorruptionErrorType NoSpaceErrorType]) :
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
      (return CorruptionError)
   :)

   @doc "decode combined lengths for lit + dist"
   (if (> lit_num_syms  286) :
        (return CorruptionError)
   :)
   (if (> dist_num_syms 30) :
        (return CorruptionError)
   :)

   (let @mut @ref lit_dist_lengths (array (+ MAX_DIST_SYMS  MAX_LIT_SYMS) u16))
   (let lit_dist_slice auto (slice_val (front @mut lit_dist_lengths) (+ lit_num_syms dist_num_syms)))
   (try x SuccessType (read_lit_dist_lengths [bs cl_counts cl_symbols
                                 lit_dist_slice]) err :
                                             (return err))
   @doc "literal tree"
   (let @mut lit_lengths (array MAX_LIT_SYMS u16))
   (let @mut lit_symbols (array MAX_LIT_SYMS u16))
   (let @mut lit_counts (array (+ MAX_HUFFMAN_BITS 1) u16))
   (let lit_slice auto (slice_val (incp (front @mut lit_lengths) dist_num_syms) lit_num_syms))
   (let lit_last_symbol u16 (huffman::ComputeCountsAndSymbolsFromLengths
                [lit_slice lit_counts lit_symbols]))

   (if (== lit_last_symbol huffman::BAD_TREE_ENCODING) :
      (return CorruptionError)
   :)

   @doc "distance tree"
   (let @mut dist_lengths (array MAX_DIST_SYMS u16))
   (let @mut dist_symbols (array MAX_DIST_SYMS u16))
   (let @mut dist_counts (array (+ MAX_HUFFMAN_BITS 1) u16))
   (let dist_slice auto (slice_val (front @mut dist_lengths) dist_num_syms))

   (let dist_last_symbol u16 (huffman::ComputeCountsAndSymbolsFromLengths
                [dist_slice dist_counts dist_symbols]))

   (if (== dist_last_symbol huffman::BAD_TREE_ENCODING) :
      (return CorruptionError)
   :)
)


(fun handle_uncompressed [(param bs (ptr @mut bitstream::Stream32))
                      (param dst_buf (slice @mut u8))]
                      (union [uint CorruptionErrorType NoSpaceErrorType]) :
   (let length u32 (bitstream::Stream32GetBits [bs 16]))
   (let inv_length u32 (bitstream::Stream32GetBits [bs 16]))
   (if (!= length (and (! inv_length) 0xffff)) :
      (return CorruptionError)
   :)
   (stmt (bitstream::Stream32SkipToNextByte [bs]))
   (let copy_src auto (bitstream::Stream32GetByteSlice [bs (as length uint)]))

   (if (bitstream::Stream32Eos [bs]) :
      (return CorruptionError)
   :)

   (if (< (len dst_buf) (as length uint)) :
      (return NoSpaceError)
   :)

   (return (len copy_src))
)



(fun @pub uncompress [(param bs (ptr @mut bitstream::Stream32))
                      (param dst (slice @mut u8))]
                      (union [uint CorruptionErrorType NoSpaceErrorType]) :
   (let @mut dst_buf auto dst)
   (let @mut seen_last bool false)
   (while (! seen_last) :
     (= seen_last (bitstream::Stream32GetBool [bs]))
     (let kind u32 (bitstream::Stream32GetBits [bs 2]))
     (cond :
       (case (== kind 0) :
         (try written_bytes uint (handle_uncompressed [bs dst_buf]) err :
            (return err))

         (= dst_buf (incs! dst_buf written_bytes))
       )
       @doc "fixed huffman"
       (case (== kind 1) :

       )
       (case (== kind 2) :
         (try written_bytes uint (handle_dynamic_huffman [bs dst_buf]) err :
            (return err))

         (= dst_buf (incs! dst_buf written_bytes))
       )
       @doc "reserved"
       (case true :
         (return CorruptionError)
       )
     )
   )
   (return (- (len dst) (len dst_buf)))
)

)