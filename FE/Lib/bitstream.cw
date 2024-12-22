module:

-- supports retrieval of bitfields up to 32 bit wide from underlying slice
--
-- Bits will be streamed in a little endian fashion:
-- Suppose the stream consists of 3 bytes [0b10101010, 0b11001100, 0b1111000]
-- These will be treated like this bit stream:
-- 0x11110000_11001100_10101010
-- where bits are taken from the bottom/least signficant bits
-- This is different from a jpeg bitstream is uses a big-endian flavor.
--
-- Not thread-safe
pub rec Stream32:
    buf span(u8)
    offset uint
    -- contains the next up to 8 bits from the stream
    -- the exact number is bits_count
    bits_cache u8
    bits_count u8
    -- end-of-stream flag - once set it will not be cleared
    eos bool

-- n must be from [0, 32]
-- may set eos
--
pub fun Stream32GetBits(bs ^!Stream32, bits_requested u8) u32:
    let! new_bits u32
    let! bits_count u8 = bs^.bits_count
    let! bits_cache u32 = as(bs^.bits_cache, u32)
    -- when the while loop exits and bits_count > 32, new_bits contains
    --    (bits_count - 32) bits we still need to put into the cache
    while bits_count < bits_requested:
        if bs^.offset == len(bs^.buf):
            set bs^.eos = true
            return 0
        set new_bits = as(bs^.buf[bs^.offset], u32)
        set bs^.offset += 1
        set bits_cache |= new_bits << as(bits_count, u32)
        set bits_count += 8
    let! out u32
    if bits_requested < 32:
        set out = bits_cache & (1_u32 << as(bits_requested, u32) - 1)
        set bits_cache >>= as(bits_requested, u32)
    else:
        -- bits_requested == 32
        set out = bits_cache
        set bits_cache = 0
    if bits_count >= 32:
        set new_bits >>= 40_u32 - as(bits_count, u32)
        set new_bits <<= 32_u32 - as(bits_requested, u32)
        set bits_cache |= new_bits
    set bits_count -= bits_requested
    set bs^.bits_count = bits_count
    set bs^.bits_cache = as(bits_cache, u8)
    return out

-- Resume bit retrieval at the next byte boundary
pub fun Stream32SkipToNextByte(bs ^!Stream32) void:
    -- If there are any bits in the cache throw them away
    set bs^.bits_count = 0

pub fun Stream32GetBool(bs ^!Stream32) bool:
    return as(Stream32GetBits(bs, 1), bool)

-- may set eos bit
pub fun Stream32GetByteSlice(bs ^!Stream32, n uint) span(u8):
    let! l uint = len(bs^.buf)
    let! f = front(bs^.buf)
    let offset uint = bs^.offset
    if n > l - offset:
        set bs^.eos = true
        return make_span(f, 0)
    else:
        set bs^.offset = offset + n
        return make_span(ptr_inc(f, offset), n)

-- rounds down - bits_cache treated as consumed/empty
pub fun Stream32BytesLeft(bs ^Stream32) uint:
    return len(bs^.buf) - bs^.offset

-- rounds up - bits_cache treated as consumed/empty
pub fun Stream32BytesConsumed(bs ^Stream32) uint:
    return bs^.offset

pub fun Stream32Eos(bs ^Stream32) bool:
    return bs^.eos
