-- Checksums
module checksum:

@pub type CrcTab = [256]u32

-- 0xedb88320 is reversed 0x04c11db7
@pub global PolyCrc32LE u32 = 0xedb88320

-- 0x82f63b78 is reversed 0x1EDC6F41
@pub global PolyCrc32cLE u32 = 0x82f63b78

@pub fun InitCrcTab(poly u32, tab ^!CrcTab) void:
    for i = 0, 256_u32, 1:
        let! crc u32 = i
        for j = 0, 8_u32, 1:
            if crc and 1 == 0:
                set crc = crc >> 1
            else:
                set crc = crc >> 1
                set crc = crc xor poly
        set tab^[i] = crc

-- start crc is 0
@pub fun CalcCrc(buf slice(u8), start_crc u32, tab ^CrcTab) u32:
    let! crc u32 = start_crc xor 0xffffffff
    for i = 0, len(buf), 1:
        let index u8 = as(crc and 0xff, u8) xor buf[i]
        set crc = tab^[index] xor crc >> 8
    return crc xor 0xffffffff

global Adler32Mod u32 = 65521

-- largest n before we have to do a modulo operation on b
global Adler32MaxLen uint = 5552

-- only use expensive modulo when absolutely needed
@pub fun Adler32ShortSliceHelper(buf slice(u8), start_crc u32) u32:
    let! a u32 = start_crc and 0xffff
    let! b u32 = start_crc >> 16 and 0xffff
    for i = 0, len(buf), 1:
        set a += as(buf[i], u32)
        set b += a
    set a %= Adler32Mod
    set b %= Adler32Mod
    return a or b << 16

-- crc to be passed to Adler32 for the first invocation
@pub global Adler32SeedCrc u32 = 1

-- start crc is 1
@pub fun Adler32(buf slice(u8), start_crc u32) u32:
    let! crc u32 = start_crc
    let! start uint = 0
    while start < len(buf):
        let end = start + Adler32MaxLen min len(buf)
        set crc = Adler32ShortSliceHelper(
                slice(pinc(front(buf), start), end - start), crc)
        set start = end
    return crc
