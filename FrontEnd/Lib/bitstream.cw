(module bitstream [] :


@doc """supports retrieval of bitfields up to 32 bit wide from underlying slice

not thread-safe"""
@pub (defrec Stream32 :
    (field buf (slice u8))
    (field offset uint)
    (field bits_cache u32)
    (field bits_count u8)
    (field eos bool))


@doc """ n must be from [0, 32]
may set eos
"""

@pub (fun Stream32GetBits [(param bs (ptr! Stream32))
                            (param n u8)] u32 :
   (let! new_bits u32)
   (let! bits_count u8 (-> bs bits_count))
   (let! bits_cache u32 (-> bs bits_cache))

   @doc """when the while loop exits and bits_count > 32, new_bits contains
   (bits_count - 32) bits we still need to put into the cache"""
   (while (< bits_count n) :
      (if (== (-> bs offset) (len (-> bs buf))) :
        (= (-> bs eos) true)
        (return 0)
      :)
      (= new_bits  (as (at (-> bs buf) (-> bs offset)) u32))
      (+= (-> bs offset) 1)
      (or= bits_cache (<< new_bits (as bits_count u32)))
      (+= bits_count 8)
   )

    (let! out u32)
    (if (< n 32) :
       (= out (and bits_cache (- (<< 1_u32 (as n u32)) 1)))
       (>>= bits_cache (as n u32))
    :
      (= out bits_cache)
      (= bits_cache 0)
    )

    (if (>= bits_count 32) :
       (>>= new_bits (- 40_u32 (as bits_count u32)))
       (<<= new_bits (- 32_u32 (as n u32)))
       (or= bits_cache new_bits)
   :)

   (-= bits_count n)
   (= (-> bs bits_count) bits_count)
   (= (-> bs bits_cache) bits_cache)

   (return out)
)

@pub (fun Stream32SkipToNextByte [(param bs (ptr! Stream32))] void :
   (= (-> bs bits_count) 0)
)

@pub (fun Stream32GetBool [(param bs (ptr! Stream32))] bool :
    (return (as (Stream32GetBits [bs 1]) bool))
)

@doc "may set eos bit"
@pub (fun Stream32GetByteSlice [(param bs (ptr! Stream32))
                                (param n uint)] (slice u8) :
   (let! l uint (len (-> bs buf)))
   (let! f auto (front (-> bs buf)))
   (let offset uint (-> bs offset))

   (if (> n (- l  offset)) :
    (= (-> bs eos) true)
    (return (slice_val f 0))
   :
    (= (-> bs offset) (+ offset n))
    (return (slice_val (pinc f offset) n))
   )

)

@doc "rounds down - bits_cache treated as consumed/empty"
@pub (fun Stream32BytesLeft [(param bs (ptr Stream32))] uint :
   (return (- (len (-> bs buf)) (-> bs offset)))
)

@doc "rounds up - bits_cache treated as consumed/empty"
@pub (fun Stream32BytesConsumed [(param bs (ptr Stream32))] uint :
   (return (-> bs offset))
)

@pub (fun Stream32Eos [(param bs (ptr Stream32))] bool :
   (return (-> bs eos))
)
)