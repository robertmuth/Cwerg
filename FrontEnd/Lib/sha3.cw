(module sha3 [] :
(import fmt)

@doc "variant of sha3-512 - https://www.cybertest.com/blog/keccak-vs-sha3"

(defrec @pub StateKeccak :
	(field msglen uint)
    (field x (array 25 u64)))

(global BlockSize512 uint 72)

(defrec @pub StateKeccak512 :
	(field base StateKeccak)
	(field tail	(array (/ BlockSize512 8) u64)))

@doc "only valid len for data are 9, 13, 17, 18
(fun AddBlockAlignedLE [(param state (ptr @mut StateKeccak)) (param data (slice u64))] void :
    (for i 0 9_uint 1 :
        (xor= (at (-> state x) i) (at data i)))
    (if (== (len data) 9) : (return) :)
    (for i 9 13_uint 1 :
        (xor= (at (-> state x) i) (at data i)))
    (if (== (len data) 13) : (return) :)
    (for i 13 17_uint 1 :
        (xor= (at (-> state x) i) (at data i)))
    (if (== (len data) 17) : (return) :)
    (for i 17 18_uint 1 :
        (xor= (at (-> state x) i) (at data i)))
)

(global rconst auto (array_val 24 u64 [
	 (index_val 0x0000000000000001) (index_val 0x0000000000008082) (index_val 0x800000000000808a)
	 (index_val 0x8000000080008000) (index_val 0x000000000000808b) (index_val 0x0000000080000001)
	 (index_val 0x8000000080008081) (index_val 0x8000000000008009) (index_val 0x000000000000008a)
	 (index_val 0x0000000000000088) (index_val 0x0000000080008009) (index_val 0x000000008000000a)
	 (index_val 0x000000008000808b) (index_val 0x800000000000008b) (index_val 0x8000000000008089)
	 (index_val 0x8000000000008003) (index_val 0x8000000000008002) (index_val 0x8000000000000080)
	 (index_val 0x000000000000800a) (index_val 0x800000008000000a) (index_val 0x8000000080008081)
	 (index_val 0x8000000000008080) (index_val 0x0000000080000001) (index_val 0x8000000080008008)
]))

(macro XOR_5_EXPR! EXPR  [(mparam $x EXPR)
                         (mparam $p1 EXPR)
                         (mparam $p2 EXPR)
                         (mparam $p3 EXPR)
                         (mparam $p4 EXPR)
                         (mparam $p5 EXPR)] [] :
    (xor (xor (xor (xor (at (^ $x) $p1) (at (^ $x) $p2))
            (at (^ $x) $p3)) (at (^ $x) $p4)) (at (^ $x) $p5))
)

(macro XOR_1! STMT_LIST  [(mparam $x EXPR) (mparam $indices EXPR_LIST) (mparam $v EXPR)] [] :
     (macro_for $i $indices : (xor= (at (^ $x) $i) $v))
)

(macro UPDATE! STMT_LIST [(mparam $a EXPR) (mparam $b EXPR) (mparam $x EXPR) (mparam $i EXPR) (mparam $bitpos EXPR)] [] :
    (= $b (at (^ $x) $i))
    (= (at (^ $x) $i) (or (<< $a $bitpos) (>> $a (- 64 $bitpos))))
    (= $a $b)
)

(fun dumpA [(param tag (slice u8)) (param x (ptr (array 25 u64)))] void :
    (fmt::print! [tag "\n"])
    (for i 0 5_uint 1 :
        (for j 0 5_uint 1 :
            (fmt::print! [" " (wrap (at (^ x) (+ i (* j 5))) fmt::u64_hex)])
        )
        (fmt::print! ["\n"])
    )
)

(fun KeccakF  [(param x (ptr @mut (array 25 u64)))] void :
    @doc """(stmt (dumpA ["KeccakF:" x]))"""

	(for round  0 24_uint 1 :
        @doc "theta(x)"
		(let @mut bc0 auto (XOR_5_EXPR! x 0 5 10 15 20))
  		(let @mut bc1 auto (XOR_5_EXPR! x 1 6 11 16 21))
  		(let @mut bc2 auto (XOR_5_EXPR! x 2 7 12 17 22))
  		(let @mut bc3 auto (XOR_5_EXPR! x 3 8 13 18 23))
  		(let @mut bc4 auto (XOR_5_EXPR! x 4 9 14 19 24))
        @doc ""
		(let @mut t0 auto (xor bc4  (or (<< bc1 1) (>> bc1 63))))
		(let @mut t1 auto (xor bc0  (or (<< bc2 1) (>> bc2 63))))
		(let @mut t2 auto (xor bc1  (or (<< bc3 1) (>> bc3 63))))
		(let @mut t3 auto (xor bc2  (or (<< bc4 1) (>> bc4 63))))
		(let @mut t4 auto (xor bc3  (or (<< bc0 1) (>> bc0 63))))

        (XOR_1! x [0 5 10 15 20] t0)
        (XOR_1! x [1 6 11 16 21] t1)
        (XOR_1! x [2 7 12 17 22] t2)
        (XOR_1! x [3 8 13 18 23] t3)
        (XOR_1! x [4 9 14 19 24] t4)
        @doc """(stmt (dumpA ["theta" x]))"""

        @doc "rho(x)"
        (let @mut a u64 (at (^ x) 1))
        (let @mut b u64)

        (UPDATE! a b x 10 1)
        (UPDATE! a b x 7 3)
        (UPDATE! a b x 11 6)
        (UPDATE! a b x 17 10)
        @doc ""
        (UPDATE! a b x 18 15)
        (UPDATE! a b x 3 21)
        (UPDATE! a b x 5 28)
        (UPDATE! a b x 16 36)
        @doc ""
        (UPDATE! a b x 8 45)
        (UPDATE! a b x 21 55)
        (UPDATE! a b x 24 2)
        (UPDATE! a b x 4 14)
        @doc ""
        (UPDATE! a b x 15 27)
        (UPDATE! a b x 23 41)
        (UPDATE! a b x 19 56)
        (UPDATE! a b x 13 8)
        @doc ""
        (UPDATE! a b x 12 25)
        (UPDATE! a b x 2 43)
        (UPDATE! a b x 20 62)
        (UPDATE! a b x 14 18)
        @doc ""
        (UPDATE! a b x 22 39)
        (UPDATE! a b x 9 61)
        (UPDATE! a b x 6 20)
        (UPDATE! a b x 1 44)


        @doc """(stmt (dumpA ["rho" x]))"""


        @doc "chi"
        (for i  0 25_uint 5 :
            (= bc0 (at (^ x) (+ i 0)))
            (= bc1 (at (^ x) (+ i 1)))
            (= bc2 (at (^ x) (+ i 2)))
            (= bc3 (at (^ x) (+ i 3)))
            (= bc4 (at (^ x) (+ i 4)))

            (xor= (at (^ x) (+ i 0)) (and (! bc1) bc2))
            (xor= (at (^ x) (+ i 1)) (and (! bc2) bc3))
            (xor= (at (^ x) (+ i 2)) (and (! bc3) bc4))
            (xor= (at (^ x) (+ i 3)) (and (! bc4) bc0))
            (xor= (at (^ x) (+ i 4)) (and (! bc0) bc1))
        )

        @doc """(stmt (dumpA ["chi" x]))"""

        @doc "iota"
        (xor= (at (^ x) 0) (at rconst round))
    )
)

(fun @pub KeccakAdd [(param state (ptr @mut  StateKeccak))
                     (param tail (slice @mut u64))
                     (param data (slice u8))] void :
    @doc """(fmt::print! ["KeccakAdd: " (-> state msglen) " "  data "\n"])"""
    (let tail_u8 auto (as (front @mut tail)  (ptr @mut u8)))
    (let block_size uint (* (len tail) 8))
    (let tail_use uint (% (-> state msglen) block_size))

    (let @mut offset uint 0)
    (if (> tail_use 0) :
       (if (< (+ tail_use (len data)) block_size) :
            (for i 0 (len data) 1 :
                (= (^ (incp tail_u8 (+ tail_use i))) (at data i))
            )
            (+= (-> state msglen) (len data))
            (return)
       :
            (= offset (- block_size tail_use))
            (for i 0 offset 1 :
                (= (^ (incp tail_u8 (+ tail_use i))) (at data i))
            )
            (stmt (AddBlockAlignedLE [state  tail]))
            (stmt (KeccakF [(& @mut (-> state x))]))
       )
    :)
    (while  (>= (- (len data) offset) block_size) :
       (for i 0 block_size 1 :
            (= (^ (incp tail_u8 i)) (at data offset))
            (+= offset 1)
        )
        (stmt (AddBlockAlignedLE [state  tail]))
        (stmt (KeccakF [(& @mut (-> state x))]))

    )
    (for i 0 (- (len data) offset) 1 :
        (= (^ (incp tail_u8 i)) (at data offset))
        (+= offset 1)
    )

    (+= (-> state msglen) (len data))
)

(fun @pub KeccakFinalize [(param state (ptr @mut  StateKeccak))
                          (param tail (slice @mut u64))] void :
   (let tail_u8 auto (as (front @mut tail)  (ptr @mut u8)))
   (let block_size auto (* (len tail) 8))

   (let padding_start uint (% (-> state msglen) block_size))
   (for i padding_start block_size 1 :
    (= (^ (incp tail_u8 i)) 0))
   (or= (^ (incp tail_u8 padding_start)) 1)
   (or= (^ (incp tail_u8 (- block_size 1))) 0x80)
   (stmt (AddBlockAlignedLE [state  tail]))
   (stmt (KeccakF [(& @mut (-> state x))]))
)

@doc "returns 512 bit cryptographic hash of data"
(fun @pub Keccak512 [(param data (slice u8))] (array 64 u8) :
  (let @mut @ref state auto (rec_val StateKeccak512 []))
  (stmt (KeccakAdd [(& @mut (. state base)) (. state tail) data]))
  (stmt (KeccakFinalize [(& @mut (. state base)) (. state tail)]))
  (return (^(as (& (. (. state base) x)) (ptr (array 64 u8)))))
)

)