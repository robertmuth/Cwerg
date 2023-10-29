(module bitstream [] :


@doc """supports retrieval of bitfields up to 32 bit wide from underlying slice

not thread-safe"""
(defrec @pub Stream32 :
    (field buf (slice u8))
    (field offset uint)
    (field bits_cache u32)
    (field bits_count u32)
    (field eos bool))


@doc """ n must be from [0, 32]
may set eos
"""

(fun @pub Stream32GetBits [(param bs (ptr @mut Stream32))
                            (param n u32)] u32 :
   (let @mut new_bits u32)
   (let @mut bits_count u32 (-> bs bits_count))
   (let @mut bits_cache u32 (-> bs bits_cache))

   @doc """when the while loop exits and bits_count > 32, new_bits contains
   (bits_count - 32) bits we still need to put into the cache"""
   (while (< bits_count n) :
      (if (== (-> bs offset) (len (-> bs buf))) :
        (= (-> bs eos) true)
        (return 0)
      :)
      (= new_bits  (as (at (-> bs buf) (-> bs offset)) u32))
      (+= (-> bs offset) 1)
      (or= bits_cache (<< new_bits bits_count))
      (+= bits_count 8)
   )

    (let @mut out u32)
    (if (< n 32) :
       (= out (and bits_cache (- (<< 1_u32 n) 1)))
       (>>= bits_cache n)
    :
      (= out bits_cache)
      (= bits_cache 0)
    )

    (if (>= bits_count 32) :
       (>>= new_bits (- 40_u32 bits_count))
       (<<= new_bits (- 32_u32 n))
       (or= bits_cache new_bits)
   :)

   (-= bits_count n)
   (= (-> bs bits_count) bits_count)
   (= (-> bs bits_cache) bits_cache)

   (return out)
)

(fun @pub Stream32SkipToNextByte [(param bs (ptr @mut Stream32))] void :
   (= (-> bs bits_count) 0)
)

(fun @pub Stream32GetBool [(param bs (ptr @mut Stream32))] bool :
    (return (as (Stream32GetBits [bs 1]) bool))
)

@doc "may set eos bit"
(fun @pub Stream32GetByteSlice [(param bs (ptr @mut Stream32))
                                (param n uint)] (slice u8) :
   (let @mut l uint (len (-> bs buf)))
   (let @mut f auto (front (-> bs buf)))
   (let offset uint (-> bs offset))

   (if (> n (- l  offset)) :
    (= (-> bs eos) true)
    (return (slice_val f 0))
   :
    (= (-> bs offset) (+ offset n))
    (return (slice_val (incp f offset) n))
   )

)

@doc "rounds down - bits_cache treated as consumed/empty"
(fun @pub Stream32BytesLeft [(param bs (ptr Stream32))] uint :
   (return (- (len (-> bs buf)) (-> bs offset)))
)

@doc "rounds up - bits_cache treated as consumed/empty"
(fun @pub Stream32BytesConsumed [(param bs (ptr Stream32))] uint :
   (return (-> bs offset))
)

(fun @pub Stream32Eos [(param bs (ptr Stream32))] bool :
   (return (-> bs eos))
)
)