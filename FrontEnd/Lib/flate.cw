@doc "flate https://www.w3.org/TR/PNG-Compression.html"
(module flate [] :

(import bitstream)
(import fmt)


(type @pub @wrapped CorruptionErrorType void)
(global @pub CorruptionError auto (wrap void_val CorruptionErrorType))

(type @pub @wrapped NoSpaceErrorType void)
(global @pub NoSpaceError auto (wrap void_val NoSpaceErrorType))

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
       @doc "uncompressed block"
       (case (== kind 0) :
         (try written_bytes uint (handle_uncompressed [bs dst_buf]) err :
            (return err))

         (= dst_buf (slice_val (incp (front @mut dst_buf) written_bytes)
                               (- (len dst_buf) written_bytes)))
       )
       @doc "fixed huffman"
       (case (== kind 1) :

       )
       @doc "dynamic huffman"
       (case (== kind 2) :

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