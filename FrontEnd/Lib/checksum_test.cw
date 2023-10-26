(module main [] :
(import test)
(import fmt)

(import checksum)

(global @mut Crc32Tab checksum::CrcTab undef)
(global @mut Crc32cTab checksum::CrcTab undef)

(global Data00k auto (array_val 1024 u8 [(index_val 0x00)]))
(global Data55k auto (array_val 1024 u8 [(index_val 0x55)]))
(global DataAAk auto (array_val 1024 u8 [(index_val 0xaa)]))
(global DataFFk auto (array_val 1024 u8 [(index_val 0xff)]))

(global Data00m auto (array_val (* 1024 1024) u8 [(index_val 0x00)]))
(global Data55m auto (array_val (* 1024 1024) u8 [(index_val 0x55)]))
(global DataAAm auto (array_val (* 1024 1024) u8 [(index_val 0xaa)]))
(global DataFFm auto (array_val (* 1024 1024) u8 [(index_val 0xff)]))

(global DataInc auto (array_val 64 u8 [
    (index_val 0)
    (index_val 1)
    (index_val 2)
    (index_val 3)
    (index_val 4)
    (index_val 5)
    (index_val 6)
    (index_val 7)
    (index_val 8)
    (index_val 9)
    (index_val 10)
    (index_val 11)
    (index_val 12)
    (index_val 13)
    (index_val 14)
    (index_val 15)
    (index_val 16)
    (index_val 17)
    (index_val 18)
    (index_val 19)
    (index_val 20)
    (index_val 21)
    (index_val 22)
    (index_val 23)
    (index_val 24)
    (index_val 25)
    (index_val 26)
    (index_val 27)
    (index_val 28)
    (index_val 29)
    (index_val 30)
    (index_val 31)
    (index_val 32)
    (index_val 33)
    (index_val 34)
    (index_val 35)
    (index_val 36)
    (index_val 37)
    (index_val 38)
    (index_val 39)
    (index_val 40)
    (index_val 41)
    (index_val 42)
    (index_val 43)
    (index_val 44)
    (index_val 45)
    (index_val 46)
    (index_val 47)
    (index_val 48)
    (index_val 49)
    (index_val 50)
    (index_val 51)
    (index_val 52)
    (index_val 53)
    (index_val 54)
    (index_val 55)
    (index_val 56)
    (index_val 57)
    (index_val 58)
    (index_val 59)
    (index_val 60)
    (index_val 61)
    (index_val 62)
    (index_val 63)
    ]))

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "init"
    (stmt (checksum::InitCrcTab [checksum::PolyCrc32LE (& @mut Crc32Tab)]))
    (fmt::print! ["\n\n"])
    (stmt (checksum::InitCrcTab [checksum::PolyCrc32cLE (& @mut Crc32cTab)]))

    @doc """crc32
    python3 -c "import zlib; print(zlib.crc32(bytes([0xaa] * 1024)))"
    """
    (test::AssertEq! (checksum::CalcCrc [Data00k 0 (& Crc32Tab)]) 0xefb5af2e_u32)
    (test::AssertEq! (checksum::CalcCrc [Data55k 0 (& Crc32Tab)]) 0x6be062a7_u32)
    (test::AssertEq! (checksum::CalcCrc [DataAAk 0 (& Crc32Tab)]) 0x3c6f327d_u32)
    (test::AssertEq! (checksum::CalcCrc [DataFFk 0 (& Crc32Tab)]) 0xb83afff4_u32)
    (test::AssertEq! (checksum::CalcCrc [DataInc 0 (& Crc32Tab)]) 0x100ece8c_u32)

    @doc """crc32c
    python3 -c "import crc32c; print(crc32c.crc32c(bytes([0xff] * 1024)))"
    """
    (test::AssertEq! (checksum::CalcCrc [Data00k 0 (& Crc32cTab)]) 4004437628_u32)
    (test::AssertEq! (checksum::CalcCrc [Data55k 0 (& Crc32cTab)]) 2308428020_u32)
    (test::AssertEq! (checksum::CalcCrc [DataAAk 0 (& Crc32cTab)]) 551338860_u32)
    (test::AssertEq! (checksum::CalcCrc [DataFFk 0 (& Crc32cTab)]) 1206242788_u32)
    (test::AssertEq! (checksum::CalcCrc [DataInc 0 (& Crc32cTab)]) 0xfb6d36eb_u32)

    @doc """adler32
    python3 -c "import zlib; print(zlib.adler32(bytes([0xff] * 1024)))"
    """
    (test::AssertEq! (checksum::Adler32 [Data00k checksum::Adler32SeedCrc]) 67108865_u32)
    (test::AssertEq! (checksum::Adler32 [Data55k checksum::Adler32SeedCrc]) 3587724304_u32)
    (test::AssertEq! (checksum::Adler32 [DataAAk checksum::Adler32SeedCrc]) 2814355487_u32)
    (test::AssertEq! (checksum::Adler32 [DataFFk checksum::Adler32SeedCrc]) 2040986670_u32)
    (test::AssertEq! (checksum::Adler32 [Data00m checksum::Adler32SeedCrc]) 15728641_u32)
    (test::AssertEq! (checksum::Adler32 [Data55m checksum::Adler32SeedCrc]) 2238926769_u32)
    (test::AssertEq! (checksum::Adler32 [DataAAm checksum::Adler32SeedCrc]) 168140641_u32)
    (test::AssertEq! (checksum::Adler32 [DataFFm checksum::Adler32SeedCrc]) 2391338769_u32)

    @doc "test end"
    (test::Success!)
    (return 0))

)
