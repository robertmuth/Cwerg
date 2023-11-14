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
   (index_val 16)
   (index_val 17)
   (index_val 18)
   (index_val 0)
   (index_val 8)
   (index_val 7)
   (index_val 9)
   (index_val 6)
   (index_val 10)
   (index_val 5)
   (index_val 11)
   (index_val 4)
   (index_val 12)
   (index_val 3)
   (index_val 13)
   (index_val 2)
   (index_val 14)
   (index_val 1)
   (index_val 15)
]))

@doc """

"""
(fun handle_dynamic_huffman [(param bs (ptr @mut bitstream::Stream32))
                      (param dst_buf (slice @mut u8))]
                      (union [uint CorruptionErrorType NoSpaceErrorType]) :
   (let lit_num_syms u32 (+ (bitstream::Stream32GetBits [bs 5]) 257))
	(let dist_num_syms u32 (+ (bitstream::Stream32GetBits [bs 5]) 1))
   (let cl_num_syms u32 (+ (bitstream::Stream32GetBits [bs 4]) 4))

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
   (if (== (huffman::ComputeCountsAndSymbolsFromLengths
                [cl_lengths cl_counts cl_symbols])
           huffman::BAD_TREE_ENCODING) :
      (return CorruptionError)
   :)

   @doc "decode combined lengths for lit + dist"
   (if (> lit_num_syms  286) :
        (return CorruptionError)
   :)
   (if (> dist_num_syms 30) :
        (return CorruptionError)
   :)

   (let @mut lit_dist_lengths (array (+ MAX_DIST_SYMS  MAX_LIT_SYMS) u16))
   (let @mut i u32 0)
   (while (< i (+ lit_num_syms dist_num_syms)) :
      (let sym auto (huffman::NextSymbol [bs cl_counts cl_symbols]))
      (if (== sym huffman::BAD_SYMBOL) :
         (return CorruptionError)
      :)
      (if (bitstream::Stream32Eos [bs]) :
          (return CorruptionError)
      :)
      (cond :
        (case (< sym 16) :
          (=  (at lit_dist_lengths i) sym)
          (+= i 1)
        )
        (case (== sym 16) :

        )
        (case (== sym 17) :

        )
        (case (== sym 18) :

        )
        (case true :
         (return CorruptionError)
        )
      )
   )

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

(macro incs! EXPR [(mparam $slice EXPR) (mparam $length EXPR)] [] :
   (slice_val (incp (front @mut $slice) $length)
              (- (len $slice) $length))
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