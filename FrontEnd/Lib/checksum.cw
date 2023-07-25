@doc "Checksums"
(module checksum [] :

(type @pub CrcTab (array 256 u32))

@doc "0xedb88320 is reversed 0x04c11db7"
(global @pub PolyCrc32LE u32 0xedb88320)

@doc "0x82f63b78 is reversed 0x1EDC6F41"
(global @pub PolyCrc32cLE u32 0x82f63b78)

(fun @pub InitCrcTab [(param poly u32) (param tab (ptr @mut CrcTab))] void :
    (for i u32 0 256 1 :
        (let @mut crc u32 i)
        (for j u32 0 8 1 :
            (if (== (and crc 1) 0) :
                (= crc (>> crc 1))
            :
                (= crc (>> crc 1))
                (= crc (xor crc poly)))
        )
        (= (at (^ tab) i)  crc)
    )
)

(fun @pub CalcCrc [(param buf (slice u8)) 
                   (param start_crc u32) 
                   (param tab (ptr CrcTab))] u32 :
    (let @mut crc u32 (xor start_crc 0xffffffff))
    (for i uint 0 (len buf) 1 :
        (let index u8 (xor (as (and crc 0xff) u8) (at buf i)))
        (= crc (xor (at (^ tab) (as index u32)) (>> crc 8)))
    )
    (return (xor crc 0xffffffff)))
)