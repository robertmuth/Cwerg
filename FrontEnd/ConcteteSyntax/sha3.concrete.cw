module sha3:

import fmt

-- variants of sha3-512
-- https://www.cybertest.com/blog/keccak-vs-sha3
-- https://emn178.github.io/online-tools/sha3_512.html
-- 
@pub rec StateKeccak:
    msglen uint
    x[25] u64

global KeccakPadding u8 = 1

global Sha3Padding u8 = 6

global BlockSize512 uint = 72

global BlockSize384 uint = 104

global BlockSize256 uint = 136

global BlockSize224 uint = 144

@pub rec StateKeccak512:
    base StateKeccak
    tail[BlockSize512 / 8] u64

@pub rec StateKeccak384:
    base StateKeccak
    tail[BlockSize384 / 8] u64

@pub rec StateKeccak256:
    base StateKeccak
    tail[BlockSize256 / 8] u64

@pub rec StateKeccak224:
    base StateKeccak
    tail[BlockSize224 / 8] u64

-- only valid len for data are 9, 13, 17, 18
fun AddBlockAlignedLE(state ^!StateKeccak, data slice(u64)) void:
    for i = 0, 9_uint, 1:
        set state ^. x[i] xor= data[i]
    if len(data) == 9:
        return
    for i = 9, 13_uint, 1:
        set state ^. x[i] xor= data[i]
    if len(data) == 13:
        return
    for i = 13, 17_uint, 1:
        set state ^. x[i] xor= data[i]
    if len(data) == 17:
        return
    for i = 17, 18_uint, 1:
        set state ^. x[i] xor= data[i]

global rconst =[24] u64{
    0x0000000000000001, 0x0000000000008082, 0x800000000000808a, 0x8000000080008000, 
    0x000000000000808b, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009, 
    0x000000000000008a, 0x0000000000000088, 0x0000000080008009, 0x000000008000000a, 
    0x000000008000808b, 0x800000000000008b, 0x8000000000008089, 0x8000000000008003, 
    0x8000000000008002, 0x8000000000000080, 0x000000000000800a, 0x800000008000000a, 
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008}

macro XOR_5_EXPR# EXPR($x EXPR, $p1 EXPR, $p2 EXPR, $p3 EXPR, $p4 EXPR, $p5 EXPR)[
]:
    $x^[$p1] xor $x^[$p2] xor $x^[$p3] xor $x^[$p4] xor $x^[$p5]

macro XOR_1# STMT_LIST($x EXPR, $indices EXPR_LIST, $v EXPR)[]:
    mfor $i $indices:
        set $x^[$i] xor= $v

macro UPDATE# STMT_LIST($a EXPR, $b EXPR, $x EXPR, $i EXPR, $bitpos EXPR)[]:
    set $b = $x^[$i]
    set $x^[$i] = $a << $bitpos or $a >> (64 - $bitpos)
    set $a = $b

fun dumpA(tag slice(u8), x ^[25] u64) void:
    fmt::print#(tag, "\n")
    for i = 0, 5_uint, 1:
        for j = 0, 5_uint, 1:
            fmt::print#(" ", wrapas(x^[i + j * 5], fmt::u64_hex))
        fmt::print#("\n")

fun KeccakF(x ^![25] u64) void:
    -- (shed (dumpA ["KeccakF:" x]))
    for round = 0, 24_uint, 1:
        -- theta(x)
        let! bc0 = XOR_5_EXPR#(x, 0, 5, 10, 15, 20)
        let! bc1 = XOR_5_EXPR#(x, 1, 6, 11, 16, 21)
        let! bc2 = XOR_5_EXPR#(x, 2, 7, 12, 17, 22)
        let! bc3 = XOR_5_EXPR#(x, 3, 8, 13, 18, 23)
        let! bc4 = XOR_5_EXPR#(x, 4, 9, 14, 19, 24)
        -- 
        let! t0 = bc4 xor (bc1 << 1 or bc1 >> 63)
        let! t1 = bc0 xor (bc2 << 1 or bc2 >> 63)
        let! t2 = bc1 xor (bc3 << 1 or bc3 >> 63)
        let! t3 = bc2 xor (bc4 << 1 or bc4 >> 63)
        let! t4 = bc3 xor (bc0 << 1 or bc0 >> 63)
        XOR_1#(x,{0, 5, 10, 15, 20}, t0)
        XOR_1#(x,{1, 6, 11, 16, 21}, t1)
        XOR_1#(x,{2, 7, 12, 17, 22}, t2)
        XOR_1#(x,{3, 8, 13, 18, 23}, t3)
        XOR_1#(x,{4, 9, 14, 19, 24}, t4)
        -- rho(x)
        let! a u64 = x^[1]
        let! b u64
        UPDATE#(a, b, x, 10, 1)
        UPDATE#(a, b, x, 7, 3)
        UPDATE#(a, b, x, 11, 6)
        UPDATE#(a, b, x, 17, 10)
        -- 
        UPDATE#(a, b, x, 18, 15)
        UPDATE#(a, b, x, 3, 21)
        UPDATE#(a, b, x, 5, 28)
        UPDATE#(a, b, x, 16, 36)
        -- 
        UPDATE#(a, b, x, 8, 45)
        UPDATE#(a, b, x, 21, 55)
        UPDATE#(a, b, x, 24, 2)
        UPDATE#(a, b, x, 4, 14)
        -- 
        UPDATE#(a, b, x, 15, 27)
        UPDATE#(a, b, x, 23, 41)
        UPDATE#(a, b, x, 19, 56)
        UPDATE#(a, b, x, 13, 8)
        -- 
        UPDATE#(a, b, x, 12, 25)
        UPDATE#(a, b, x, 2, 43)
        UPDATE#(a, b, x, 20, 62)
        UPDATE#(a, b, x, 14, 18)
        -- 
        UPDATE#(a, b, x, 22, 39)
        UPDATE#(a, b, x, 9, 61)
        UPDATE#(a, b, x, 6, 20)
        UPDATE#(a, b, x, 1, 44)
        -- chi
        for i = 0, 25_uint, 5:
            set bc0 = x^[i + 0]
            set bc1 = x^[i + 1]
            set bc2 = x^[i + 2]
            set bc3 = x^[i + 3]
            set bc4 = x^[i + 4]
            set x^[i + 0] xor= !bc1 and bc2
            set x^[i + 1] xor= !bc2 and bc3
            set x^[i + 2] xor= !bc3 and bc4
            set x^[i + 3] xor= !bc4 and bc0
            set x^[i + 4] xor= !bc0 and bc1
        -- iota
        set x^[0] xor= rconst[round]

@pub fun KeccakAdd(state ^!StateKeccak, tail slice!(u64), data slice(u8)) void:
    -- (fmt::print# "KeccakAdd: " (-> state msglen) " "  data "\n")
    let tail_u8 = as(front!(tail), ^!u8)
    let block_size uint = len(tail) * 8
    let tail_use uint = state ^. msglen % block_size
    let! offset uint = 0
    if tail_use > 0:
        if tail_use + len(data) < block_size:
            for i = 0, len(data), 1:
                set pinc(tail_u8, tail_use + i)^= data[i]
            set state ^. msglen += len(data)
            return
        else:
            set offset = block_size - tail_use
            for i = 0, offset, 1:
                set pinc(tail_u8, tail_use + i)^= data[i]
            shed AddBlockAlignedLE(state, tail)
            shed KeccakF(&!state ^. x)
    while len(data) - offset >= block_size:
        for i = 0, block_size, 1:
            set pinc(tail_u8, i)^= data[offset]
            set offset += 1
        shed AddBlockAlignedLE(state, tail)
        shed KeccakF(&!state ^. x)
    for i = 0, len(data) - offset, 1:
        set pinc(tail_u8, i)^= data[offset]
        set offset += 1
    set state ^. msglen += len(data)

@pub fun KeccakFinalize(state ^!StateKeccak, tail slice!(u64), padding u8) void:
    let tail_u8 = as(front!(tail), ^!u8)
    let block_size = len(tail) * 8
    let padding_start uint = state ^. msglen % block_size
    for i = padding_start, block_size, 1:
        set pinc(tail_u8, i)^= 0
    set pinc(tail_u8, padding_start)^or= padding
    set pinc(tail_u8, block_size - 1)^or= 0x80
    shed AddBlockAlignedLE(state, tail)
    shed KeccakF(&!state ^. x)

-- returns 512 bit cryptographic hash of data
@pub fun Keccak512(data slice(u8))[64] u8:
    @ref let! state = StateKeccak512{}
    shed KeccakAdd(&!state.base, state.tail, data)
    shed KeccakFinalize(&!state.base, state.tail, KeccakPadding)
    return as(&state.base.x, ^[64] u8)^

-- returns 512 bit cryptographic hash of data
@pub fun Sha3512(data slice(u8))[64] u8:
    @ref let! state = StateKeccak512{}
    shed KeccakAdd(&!state.base, state.tail, data)
    shed KeccakFinalize(&!state.base, state.tail, Sha3Padding)
    return as(&state.base.x, ^[64] u8)^

