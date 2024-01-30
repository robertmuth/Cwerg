@doc "Checksums"
(module checksum [] :

(type @pub CrcTab (array 256 u32))

@doc "0xedb88320 is reversed 0x04c11db7"
(global @pub PolyCrc32LE u32 0xedb88320)

@doc "0x82f63b78 is reversed 0x1EDC6F41"
(global @pub PolyCrc32cLE u32 0x82f63b78)

(fun @pub InitCrcTab [(param poly u32) (param tab (ptr! CrcTab))] void :
    (for i 0 256_u32 1 :
        (let! crc u32 i)
        (for j 0 8_u32 1 :
            (if (== (and crc 1) 0) :
                (= crc (>> crc 1))
            :
                (= crc (>> crc 1))
                (= crc (xor crc poly)))
        )
        (= (at (^ tab) i)  crc)
    )
)

@doc "start crc is 0"
(fun @pub CalcCrc [(param buf (slice u8))
                   (param start_crc u32)
                   (param tab (ptr CrcTab))] u32 :
    (let! crc u32 (xor start_crc 0xffffffff))
    (for i 0 (len buf) 1 :
        (let index u8 (xor (as (and crc 0xff) u8) (at buf i)))
        (= crc (xor (at (^ tab) index) (>> crc 8)))
    )
    (return (xor crc 0xffffffff)))

(global Adler32Mod u32 65521)

@doc "largest n before we have to do a modulo operation on b"
(global Adler32MaxLen uint 5552)

@doc "only use expensive modulo when absolutely needed"
(fun @pub Adler32ShortSliceHelper [(param buf (slice u8))
                        (param start_crc u32)] u32 :
    (let! a u32 (and start_crc 0xffff))
    (let! b u32 (and (>> start_crc 16) 0xffff))
    (for i 0 (len buf) 1 :
        (+= a (as (at buf i) u32))
        (+= b a)
    )
    (mod= a Adler32Mod)
    (mod= b Adler32Mod)
    (return (or a (<< b 16)))
)

@doc "crc to be passed to Adler32 for the first invocation"
(global @pub Adler32SeedCrc u32 1)

@doc "start crc is 1"
(fun @pub Adler32 [(param buf (slice u8))
                    (param start_crc u32)] u32 :

    (let! crc u32 start_crc)
    (let! start uint 0)
    (while (< start (len buf)) :
        (let end auto (min (+ start Adler32MaxLen) (len buf)))
        (= crc (Adler32ShortSliceHelper [(slice_val (pinc (front buf) start) (- end start))
                                        crc]))
        (= start end)
    )
    (return crc))

)