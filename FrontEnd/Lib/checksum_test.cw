(module main [] :
(import test)
(import fmt)

(import checksum)

(global! Crc32Tab checksum::CrcTab undef)
(global! Crc32cTab checksum::CrcTab undef)

(global Data00k auto (array_val 1024 u8 [ 0x00 ]))
(global Data55k auto (array_val 1024 u8 [ 0x55 ]))
(global DataAAk auto (array_val 1024 u8 [ 0xaa ]))
(global DataFFk auto (array_val 1024 u8 [ 0xff ]))

(global Data00m auto (array_val (* 1024 1024) u8 [ 0x00 ]))
(global Data55m auto (array_val (* 1024 1024) u8 [ 0x55 ]))
(global DataAAm auto (array_val (* 1024 1024) u8 [ 0xaa ]))
(global DataFFm auto (array_val (* 1024 1024) u8 [ 0xff ]))

(global DataInc auto (array_val 64 u8 [
    0
    1
    2
    3
    4
    5
    6
    7
    8
    9
    10
    11
    12
    13
    14
    15
    16
    17
    18
    19
    20
    21
    22
    23
    24
    25
    26
    27
    28
    29
    30
    31
    32
    33
    34
    35
    36
    37
    38
    39
    40
    41
    42
    43
    44
    45
    46
    47
    48
    49
    50
    51
    52
    53
    54
    55
    56
    57
    58
    59
    60
    61
    62
    63
    ]))

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "init"
    (shed (checksum::InitCrcTab [checksum::PolyCrc32LE (&! Crc32Tab)]))
    (fmt::print# ["\n\n"])
    (shed (checksum::InitCrcTab [checksum::PolyCrc32cLE (&! Crc32cTab)]))

    @doc """crc32
    python3 -c "import zlib; print(zlib.crc32(bytes([0xaa] * 1024)))"
    """
    (test::AssertEq# (checksum::CalcCrc [Data00k 0 (& Crc32Tab)]) 0xefb5af2e_u32)
    (test::AssertEq# (checksum::CalcCrc [Data55k 0 (& Crc32Tab)]) 0x6be062a7_u32)
    (test::AssertEq# (checksum::CalcCrc [DataAAk 0 (& Crc32Tab)]) 0x3c6f327d_u32)
    (test::AssertEq# (checksum::CalcCrc [DataFFk 0 (& Crc32Tab)]) 0xb83afff4_u32)
    (test::AssertEq# (checksum::CalcCrc [DataInc 0 (& Crc32Tab)]) 0x100ece8c_u32)

    @doc """crc32c
    python3 -c "import crc32c; print(crc32c.crc32c(bytes([0xff] * 1024)))"
    """
    (test::AssertEq# (checksum::CalcCrc [Data00k 0 (& Crc32cTab)]) 4004437628_u32)
    (test::AssertEq# (checksum::CalcCrc [Data55k 0 (& Crc32cTab)]) 2308428020_u32)
    (test::AssertEq# (checksum::CalcCrc [DataAAk 0 (& Crc32cTab)]) 551338860_u32)
    (test::AssertEq# (checksum::CalcCrc [DataFFk 0 (& Crc32cTab)]) 1206242788_u32)
    (test::AssertEq# (checksum::CalcCrc [DataInc 0 (& Crc32cTab)]) 0xfb6d36eb_u32)

    @doc """adler32
    python3 -c "import zlib; print(zlib.adler32(bytes([0xff] * 1024)))"
    """
    (test::AssertEq# (checksum::Adler32 [Data00k checksum::Adler32SeedCrc]) 67108865_u32)
    (test::AssertEq# (checksum::Adler32 [Data55k checksum::Adler32SeedCrc]) 3587724304_u32)
    (test::AssertEq# (checksum::Adler32 [DataAAk checksum::Adler32SeedCrc]) 2814355487_u32)
    (test::AssertEq# (checksum::Adler32 [DataFFk checksum::Adler32SeedCrc]) 2040986670_u32)
    (test::AssertEq# (checksum::Adler32 [Data00m checksum::Adler32SeedCrc]) 15728641_u32)
    (test::AssertEq# (checksum::Adler32 [Data55m checksum::Adler32SeedCrc]) 2238926769_u32)
    (test::AssertEq# (checksum::Adler32 [DataAAm checksum::Adler32SeedCrc]) 168140641_u32)
    (test::AssertEq# (checksum::Adler32 [DataFFm checksum::Adler32SeedCrc]) 2391338769_u32)

    @doc "test end"
    (test::Success#)
    (return 0))

)
