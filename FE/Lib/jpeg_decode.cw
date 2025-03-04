; Simple JPEG Decoder loosely based on
; https://github.com/richgel999/picojpeg
; More on jpeg
; https://github.com/corkami/formats/blob/master/image/jpeg.md
; https://www.youtube.com/watch?v=CPT4FSkFUgs
; More on Huffman codes
; https://www.ece.ucdavis.edu/cerl/wp-content/uploads/sites/14/2015/09/GenHuffCodes.pdf
; on fast idct transforms:
; Feig, E.&& Winograd, S. (September 1992b). "Fast algorithms for the discrete cosine transform".
;                   IEEE Transactions on Signal Processing. 40 (9): 2174–2193
module:

import BS = bytestream

import fmt

; To enable debug logging make sure the next macro is called `debug#`
; To enable debug logging make sure the second macro is called `debug#`
macro xdebug# STMT_LIST ($parts EXPR_LIST_REST) []:
    fmt::print#($parts)

macro debug# STMT_LIST ($parts EXPR_LIST_REST) []:

global WinogradMultipliers = {[64]u8:
                              128, 178, 178, 167, 246, 167, 151, 232, 232, 151,
                              128, 209, 219, 209, 128, 101, 178, 197, 197, 178,
                              101, 69, 139, 167, 177, 167, 139, 69, 35, 96, 131,
                              151, 151, 131, 96, 35, 49, 91, 118, 128, 118, 91,
                              49, 46, 81, 101, 101, 81, 46, 42, 69, 79, 69, 42,
                              35, 54, 54, 35, 28, 37, 28, 19, 19, 10}

macro div_pow2_with_rounding# EXPR ($x EXPR, $d EXPR) []:
    ($x + (1 << ($d - 1))) >> $d

fun ApplyWindogradMulipliers(qt_tab ^![64]s16) void:
    let c s32 = (1 << (10 - 7 - 1))
    for i = 0, len(qt_tab^), 1:
        let! x s32 = as(qt_tab^[i], s32)
        let y = x
        set x *= as(WinogradMultipliers[i], s32)
        ; divide by 2^3 with rouding
        set x = div_pow2_with_rounding#(x, 10 - 7)
        debug#("apply: ", i, " ", y, " ", x, "\n")
        set qt_tab^[i] = as(x, s16)

; multiply helper functions are the 4 types of signed multiplies needed by the Winograd IDCT.
; 1 / cos(4 * pi/16)   362, 256+106
global c_b1_b3 s32 = 362

; 1 / cos(6*pi/16) 669,  256+256+157
global c_b2 s32 = 669

; 1 / cos(2*pi/16)  277, 256+21
global c_b4 s32 = 277

; 1 / (cos(2*pi/16) + cos(6*pi/16))  196, 196
global c_b5 s32 = 196

fun imul(w s16, c s32) s16:
    let x s32 = as(w, s32) * c
    return as(div_pow2_with_rounding#(x, 8), s16)

macro CommonIDCT# STMT_LIST () []:
    let x4 = src4 - src7
    let x7 = src4 + src7
    let x5 = src5 + src6
    let x6 = src5 - src6
    let tmp1 = imul(x4 - x6, c_b5)
    let stg26 = imul(x6, c_b4) - tmp1
    let x24 = tmp1 - imul(x4, c_b2)
    let x15 = x5 - x7
    let x17 = x5 + x7
    let tmp2 = stg26 - x17
    let tmp3 = imul(x15, c_b1_b3) - tmp2
    let x44 = tmp3 + x24
    let x30 = src0 + src1
    let x31 = src0 - src1
    let x12 = src2 - src3
    let x13 = src2 + src3
    let x32 = imul(x12, c_b1_b3) - x13
    let x40 = x30 + x13
    let x43 = x30 - x13
    let x41 = x31 + x32
    let x42 = x31 - x32

; updates blk in place
fun RowIDCT(blk ^![8 * 8]s16) void:
    for o = 0, len(blk^), 8:
        let src0 = blk^[o + 0]
        let src5 = blk^[o + 1]
        let src2 = blk^[o + 2]
        let src7 = blk^[o + 3]
        let src1 = blk^[o + 4]
        let src4 = blk^[o + 5]
        let src3 = blk^[o + 6]
        let src6 = blk^[o + 7]
        if (src1 | src2 | src3 | src4 | src5 | src6 | src7) == 0:
            debug#("idc-row shortcicuit ", src0, "\n")
            for i = 0, 8_uint, 1:
                set blk^[o + i] = src0
            continue
        CommonIDCT#()
        debug#("idc-row out ", x40 + x17, " ", x41 + tmp2, " ", x42 + tmp3, " ",
               x43 - x44, "\n")
        set blk^[o + 0] = x40 + x17
        set blk^[o + 1] = x41 + tmp2
        set blk^[o + 2] = x42 + tmp3
        set blk^[o + 3] = x43 - x44
        set blk^[o + 4] = x43 + x44
        set blk^[o + 5] = x42 - tmp3
        set blk^[o + 6] = x41 - tmp2
        set blk^[o + 7] = x40 - x17

fun clamp8(x s16) s16:
    cond:
        case x < 0:
            return 0
        case x >= 0xff:
            return 0xff
        case true:
            return x

; descale
fun descale(xx s16) s16:
    return div_pow2_with_rounding#(xx, 7) + 128

fun ColIDCT(blk ^![8 * 8]s16) void:
    for o = 0, 8_uint, 1:
        let src0 = blk^[o + 8 * 0]
        let src5 = blk^[o + 8 * 1]
        let src2 = blk^[o + 8 * 2]
        let src7 = blk^[o + 8 * 3]
        let src1 = blk^[o + 8 * 4]
        let src4 = blk^[o + 8 * 5]
        let src3 = blk^[o + 8 * 6]
        let src6 = blk^[o + 8 * 7]
        if (src1 | src2 | src3 | src4 | src5 | src6 | src7) == 0:
            debug#("idc-col shortcicuit ", o, " ", src0, "\n")
            let t = clamp8(descale(src0))
            for i = 0, len(blk^), 8:
                set blk^[o + i] = t
            continue
        CommonIDCT#()
        debug#("idc-col out ", descale(x40 + x17), " ", descale(x41 + tmp2),
               " ", descale(x42 + tmp3), " ", descale(x43 - x44), "\n")
        set blk^[o + 8 * 0] = clamp8(descale(x40 + x17))
        set blk^[o + 8 * 1] = clamp8(descale(x41 + tmp2))
        set blk^[o + 8 * 2] = clamp8(descale(x42 + tmp3))
        set blk^[o + 8 * 3] = clamp8(descale(x43 - x44))
        set blk^[o + 8 * 4] = clamp8(descale(x43 + x44))
        set blk^[o + 8 * 5] = clamp8(descale(x42 - tmp3))
        set blk^[o + 8 * 6] = clamp8(descale(x41 - tmp2))
        set blk^[o + 8 * 7] = clamp8(descale(x40 - x17))

; for huffman decoding
rec BitStream:
    buf span(u8)
    offset uint
    ; contains the next up to 8 bits from the stream
    ; the exact number is bits_count
    bits_cache u8
    bits_count u8
    ; end-of-stream flag - once set it will not be cleared
    eos bool

pub fun GetBytesConsumed(bs ^BitStream) uint:
    return bs^.offset

pub fun GetNextBit(bs ^!BitStream) u16:
    let! bits_count u8 = bs^.bits_count
    let! bits_cache u8 = bs^.bits_cache
    if bits_count == 0:
        if bs^.offset == len(bs^.buf):
            set bs^.eos = true
            return 0
        set bits_cache = bs^.buf[bs^.offset]
        ; debug#("new cache: ", wrap_as(bits_cache, fmt::u8_hex), "\n")
        set bs^.offset += 1
        set bits_count = 8
        if bits_cache == 0xff:
            if bs^.offset == len(bs^.buf):
                set bs^.eos = true
                return 0
            let zeros = bs^.buf[bs^.offset]
            if zeros != 0:
                set bs^.eos = true
                return 0
            set bs^.offset += 1
        set bs^.bits_cache = bits_cache
    set bits_count -= 1
    let out = as((bits_cache >> bits_count) & 1, u16)
    set bs^.bits_count = bits_count
    return out

rec HuffmanTree:
    counts [16]u8
    symbols [256]u8
    num_symbols u8
    min_code [16]u16
    max_code [16]u16
    val_ptr [16]u8

global BAD_SYMBOL = 0xffff_u16

fun NextSymbol(bs ^!BitStream, ht ^HuffmanTree) u16:
    let! offset u16 = GetNextBit(bs)
    for level = 0, len(ht^.counts), 1:
        let mc = ht^.max_code[level]
        if offset <= mc && mc != 0xffff:
            set offset += as(ht^.val_ptr[level], u16) - ht^.min_code[level]
            debug#("huffman level=", level, " offset=", offset, " symbol=",
                   ht^.symbols[offset], "\n")
            return as(ht^.symbols[offset], u16)
        set offset <<= 1
        set offset += GetNextBit(bs)
    return BAD_SYMBOL

; not we rely on wrap around arithmetic
fun GetVal(bs ^!BitStream, num_bits u16) s16:
    let bits = as(num_bits, s32)
    let! out s32 = 0
    for i = 0, bits, 1:
        set out <<= 1
        set out |= as(GetNextBit(bs), s32)
    ; note: signed shift
    if out < 1 << (bits - 1):
        set out += ((-1) << bits) + 1
    return as(out, s16)

rec AppInfo:
    version_major u8
    version_minor u8
    units u8
    density_x u16
    density_y u16
    thumbnail_w u8
    thumbnail_h u8

pub rec Component:
    cid u8
    ssx u32
    ssy u32
    ; quantization table index:  0-3
    qt_tab u8
    ; image dimensions in pixels
    width u32
    height u32
    stride u32
    ; huffman table index for dc decoding: 0-1
    dc_tab u8
    ; huffman table index for ac decoding: 0-1
    ac_tab u8

pub rec FrameInfo:
    width u32
    height u32
    ncomp u8
    format u8
    ; macro block dimensions in pixels (e.g. 8x8)
    mbsizex u32
    mbsizey u32
    ; image dimension measure in macro blocks
    mbwidth u32
    mbheight u32
    comp [3]Component

pub wrapped type Success = void

pub global SuccessVal = wrap_as(void_val, Success)

pub wrapped type CorruptionError = void

pub global CorruptionErrorVal = wrap_as(void_val, CorruptionError)

pub wrapped type UnsupportedError = void

pub global UnsupportedErrorVal = wrap_as(void_val, UnsupportedError)

fun div_roundup(a u32, b u32) u32:
    return (a + b - 1) / b

fun DecodeHufmanTable(chunk span(u8), huffman_trees ^![2][2]HuffmanTree)
  union(Success, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    ref let! data = chunk
    let kind = BS::FrontU8Unchecked(@!data)
    if kind & 0xec != 0:
        return CorruptionErrorVal
    let pos = kind & 3
    if pos > 1:
        return UnsupportedErrorVal
    ; 0 means dc
    let is_ac = (kind & 0x10) >> 4
    let ht ^!HuffmanTree = @!huffman_trees^[is_ac][pos]
    let counts = BS::FrontSliceUnchecked(@!data, 16)
    let! total = 0_uint
    for i = 0, 16_s32, 1:
        set total += as(counts[i], uint)
        set ht^.counts[i] = counts[i]
    if len(data) < total:
        return BS::OutOfBoundsErrorVal
    for i = 0, total, 1:
        set ht^.symbols[i] = data[i]
    if total > 255:
        return CorruptionErrorVal
    set ht^.num_symbols = as(total, u8)
    do BS::SkipUnchecked(@!data, total)
    debug#("Hufman total codes[", is_ac, ",", pos, "]: ", total, "\n")
    let! acc u16 = 0
    let! code u16 = 0
    for i = 0, 16_s32, 1:
        let num u16 = as(counts[i], u16)
        if num == 0:
            set ht^.min_code[i] = 0
            set ht^.max_code[i] = 0xffff_u16
            set ht^.val_ptr[i] = 0
        else:
            set ht^.min_code[i] = code
            set ht^.max_code[i] = code + num - 1
            set ht^.val_ptr[i] = as(acc, u8)
            set acc += num
            set code += num
        set code <<= 1
    return SuccessVal

fun DecodeQuantizationTable(chunk span(u8), qt_tabs ^![4][64]s16)
  union(u8, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    ref let! data = chunk
    let! qt_avail u8 = 0
    while len(data) >= 65:
        let t = data[0]
        if t & 0xfc != 0:
            return CorruptionErrorVal
        debug#("processing qt: ", t, "\n")
        set qt_avail |= 1 << t
        let qt_tab = @!qt_tabs^[t]
        for i = 0, 64_u32, 1:
            set qt_tab^[i] = as(data[i + 1], s16)
        do ApplyWindogradMulipliers(qt_tab)
        do BS::SkipUnchecked(@!data, 65)
    if len(data) != 0:
        return CorruptionErrorVal
    return qt_avail

fun DecodeRestartInterval(chunk span(u8))
  union(u16, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    ref let! data = chunk
    trylet interval u16 = BS::FrontBeU16(@!data), err:
        return err
    debug#("restart interval: ", interval, "\n")
    return interval

fun DecodeAppInfo(chunk span(u8), app_info ^!AppInfo)
  union(Success, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    ref let! data = chunk
    if len(data) < 14:
        return CorruptionErrorVal
    if data[0] != 'J' || data[1] != 'F' || data[2] != 'I' || data[3] != 'F' ||
      data[4] != 0:
        return CorruptionErrorVal
    do BS::SkipUnchecked(@!data, 5)
    set app_info^.version_major = BS::FrontU8Unchecked(@!data)
    set app_info^.version_minor = BS::FrontU8Unchecked(@!data)
    set app_info^.units = BS::FrontU8Unchecked(@!data)
    set app_info^.density_x = BS::FrontBeU16Unchecked(@!data)
    set app_info^.density_y = BS::FrontBeU16Unchecked(@!data)
    set app_info^.thumbnail_w = BS::FrontU8Unchecked(@!data)
    set app_info^.thumbnail_h = BS::FrontU8Unchecked(@!data)
    debug#("AppInfo: ", app_info^.version_major, ".", app_info^.version_minor,
           "\n")
    return SuccessVal

fun DecodeStartOfFrame(chunk span(u8), out ^!FrameInfo)
  union(Success, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    ref let! data = chunk
    trylet format u8 = BS::FrontU8(@!data), err:
        return err
    if format != 8:
        debug#("unsupported format: ", format, "\n")
        return UnsupportedErrorVal
    set out^.format = format
    trylet height u16 = BS::FrontBeU16(@!data), err:
        return err
    set out^.height = as(height, u32)
    trylet width u16 = BS::FrontBeU16(@!data), err:
        return err
    set out^.width = as(width, u32)
    trylet ncomp u8 = BS::FrontU8(@!data), err:
        return err
    set out^.ncomp = ncomp
    if ncomp != 1 && ncomp != 3:
        debug#("unsupported ncomp: ", ncomp, "\n")
        return UnsupportedErrorVal
    ; debug#("frame: ", width, "x", height, " ncomp: ", ncomp, "\n")
    let! ssxmax u32 = 0
    let! ssymax u32 = 0
    for i = 0, ncomp, 1:
        let comp ^!Component = @!(out^.comp[i])
        tryset comp^.cid = BS::FrontU8(@!data), err:
            return err
        trylet ss u8 = BS::FrontU8(@!data), err:
            return err
        let ssx = as(ss >> 4, u32)
        let ssy = as(ss & 0xf, u32)
        ; ssy must be a power of two
        if ssx == 0 || ssy == 0 || ssy & (ssy - 1) != 0:
            debug#("bad ss: ", ssx, "x", ssy, "\n")
            return CorruptionErrorVal
        ; for now we only support YH1V1
        if ssx != 1 || ssy != 1:
            return UnsupportedErrorVal
        ; debug#("comp: ", i, " ", comp^.cid, " ", ssx, "x", ssy, "\n")
        set comp^.ssx = ssx
        set comp^.ssy = ssy
        set ssxmax max= ssx
        set ssymax max= ssy
        trylet! qt_tab u8 = BS::FrontU8(@!data), err:
            return err
        if qt_tab & 0xfc != 0:
            debug#("bad qt_tab: ", qt_tab, "\n")
            return CorruptionErrorVal
        set comp^.qt_tab = qt_tab
    if ncomp == 1:
        set ssxmax = 1
        set ssymax = 1
        set out^.comp[0].ssx = 1
        set out^.comp[0].ssy = 1
    let mbsizex u32 = as(ssxmax, u32) * 8
    let mbsizey u32 = as(ssymax, u32) * 8
    set out^.mbsizex = mbsizex
    set out^.mbsizey = mbsizey
    set out^.mbwidth = div_roundup(out^.width, mbsizex)
    set out^.mbheight = div_roundup(out^.height, mbsizey)
    ; debug#("mbsize: ", mbsizex, "x", mbsizey,  " mbdim: ", out^.mbwidth, "x", out^.mbheight, "\n")
    for i = 0, ncomp, 1:
        let comp ^!Component = @!(out^.comp[i])
        set comp^.width = div_roundup(out^.width * comp^.ssx, ssxmax)
        set comp^.height = div_roundup(out^.height * comp^.ssy, ssymax)
        set comp^.stride = out^.mbwidth * comp^.ssx * 8
        if comp^.width < 3 && comp^.ssx != ssxmax:
            debug#("bad width: ", comp^.width, "\n")
            return CorruptionErrorVal
        if comp^.height < 3 && comp^.ssy != ssymax:
            debug#("bad height: ", comp^.height, "\n")
            return CorruptionErrorVal
    ; debug#("comp: ", i, " ", comp^.width, "x", comp^.height, " stride:", comp^.stride, "\n")
    return SuccessVal

fun DecodeScan(chunk span(u8), frame_info ^!FrameInfo)
  union(Success, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    ref let! data = chunk
    trylet ncomp u8 = BS::FrontU8(@!data), err:
        return err
    if ncomp != frame_info^.ncomp:
        return UnsupportedErrorVal
    for i = 0, ncomp, 1:
        if len(data) < 2:
            return BS::OutOfBoundsErrorVal
        let comp ^!Component = @!(frame_info^.comp[i])
        if data[0] != comp^.cid:
            return CorruptionErrorVal
        let tabsel = data[1]
        if tabsel & 0xee != 0:
            return CorruptionErrorVal
        set comp^.dc_tab = (tabsel >> 4) & 1
        set comp^.ac_tab = tabsel & 1
        debug#("tabsel[", comp^.cid, "]: ", comp^.dc_tab, ".", comp^.ac_tab,
               "\n")
        do BS::SkipUnchecked(@!data, 2)
        if len(data) < 3:
            return BS::OutOfBoundsErrorVal
    if data[0] != 0 || data[1] != 63 || data[2] != 0:
        return UnsupportedErrorVal
    do BS::SkipUnchecked(@!data, 3)
    debug#(">>>>>>> ", data[0], "\n")
    return SuccessVal

global ZigZagIndex = {[8 * 8]u8:
                      0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
                      12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21,
                      28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30,
                      37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61,
                      54, 47, 55, 62, 63}

; returns new dc value on success
fun DecodeBlock(bs ^!BitStream, dc_tab ^HuffmanTree, ac_tab ^HuffmanTree,
                qt_tab ^[64]s16, out ^![8 * 8]s16, last_dc s16)
  union(s16, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    for i = 0, len(out^), 1:
        set out^[i] = 0
    let dc_code = NextSymbol(bs, dc_tab)
    let dc_val s16 = last_dc + GetVal(bs, dc_code & 0xf)
    debug#("dc=", dc_val * qt_tab^[0], "\n")
    set out^[0] = dc_val * qt_tab^[0]
    let! coeff u16 = 0
    while true:
        let ac_code = NextSymbol(bs, ac_tab)
        if ac_code == 0:
            break
        let extra_bits = ac_code & 0xf
        let skip = (ac_code >> 4)
        if extra_bits == 0 && skip != 15:
            return CorruptionErrorVal
        let ac_val = GetVal(bs, extra_bits)
        set coeff += skip + 1
        debug#("ac=", ac_val, " ", qt_tab^[coeff], " ", coeff, "\n")
        set out^[ZigZagIndex[coeff]] = ac_val * qt_tab^[coeff]
        if coeff >= 63:
            break
    return dc_val

fun DecodeMacroBlocksHuffman(chunk span(u8), fi ^FrameInfo,
                             huffman_trees ^[2][2]HuffmanTree,
                             quantization_tab ^[4][64]s16, out span!(u8))
  union(uint, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    debug#("Decode blocks\n")
    ref let! bs = {BitStream: chunk}
    let! dc_last = {[3]s16: 0, 0, 0}
    ref let! buffer [8 * 8]s16 = undef
    let ncomp u32 = as(fi^.ncomp, u32)
    ; we assume ssx/ssy are 1
    let byte_stride = fi^.mbwidth * 8 * ncomp
    for my = 0, fi^.mbheight * 8, 8:
        for mx = 0, fi^.mbwidth * 8, 8:
            for c = 0, ncomp, 1:
                let comp ^Component = @fi^.comp[c]
                let dc_tab ^HuffmanTree = @huffman_trees^[0][comp^.dc_tab]
                let ac_tab ^HuffmanTree = @huffman_trees^[1][comp^.ac_tab]
                let qt_tab ^[64]s16 = @quantization_tab^[comp^.qt_tab]
                ; debug#("Block: ", m, " comp=", c, " x=", x, " y=", y, "\n")
                debug#("Block ===================\n")
                tryset dc_last[c] =
                  DecodeBlock(@!bs, dc_tab, ac_tab, qt_tab, @!buffer, dc_last[c]
                    ), err:
                    return err
                do RowIDCT(@!buffer)
                do ColIDCT(@!buffer)
                let! i u32 = 0
                for y = my, my + 8, 1:
                    let o = y * byte_stride + c
                    for x = mx, mx + 8, 1:
                        set out[o + x * ncomp] = as(buffer[i], u8)
                        set i += 1
    return GetBytesConsumed(@bs)

pub fun DecodeFrameInfo(a_data span(u8))
  union(FrameInfo, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    ref let! fi FrameInfo = undef
    ref let! data = a_data
    trylet magic u16 = BS::FrontBeU16(@!data), err:
        return err
    if magic != 0xffd8:
        return CorruptionErrorVal
    while true:
        trylet chunk_kind u16 = BS::FrontBeU16(@!data), err:
            return err
        trylet chunk_length u16 = BS::FrontBeU16(@!data), err:
            return err
        trylet chunk_slice span(u8) =
          BS::FrontSlice(@!data, as(chunk_length - 2, uint)), err:
            return err
        if chunk_kind == 0xffc0:
            trylet dummy Success = DecodeStartOfFrame(chunk_slice, @!fi), err:
                return err
            return fi
    return CorruptionErrorVal

fun clamp8b(x s32) s32:
    cond:
        case x < 0:
            return 0
        case x >= 0xff:
            return 0xff
        case true:
            return x

pub fun ConvertYH1V1ToRGB(out span!(u8)) void:
    for i = 0, len(out), 3:
        let Y = as(out[i], s32)
        let Cb = as(out[i + 1], s32)
        let Cr = as(out[i + 2], s32)
        ;  R = Y + 1.402 (Cr-128)
        ; 0.402 = 103/256
        let crR = Cr + ((Cr * 103) >> 8) - 179
        set out[i] = as(clamp8b(Y + crR), u8)
        ; G = Y - 0.34414 (Cb-128) - 0.71414 (Cr-128)
        ; 0.344 = 88/256
        ; 0.714 = 183/256
        let cbG = ((Cb * 88) >> 8) - 44
        let crG = ((Cr * 183) >> 8) - 91
        set out[i + 1] = as(clamp8b(clamp8b(Y - cbG) - crG), u8)
        ; B = Y + 1.772 (Cb-128)
        ; 0.772 = 198/256
        let cbB = Cb + ((Cb * 198) >> 8) - 227
        set out[i + 2] = as(clamp8b(Y + cbB), u8)

pub fun DecodeImage(a_data span(u8), out span!(u8))
  union(Success, CorruptionError, UnsupportedError, BS::OutOfBoundsError):
    debug#("DecodeImage: ", len(a_data), "\n")
    ref let! app_info AppInfo = undef
    ref let! frame_info FrameInfo = undef
    ref let! huffman_trees [2][2]HuffmanTree = undef
    ref let! quantization_tab [4][64]s16 = undef
    let! qt_avail_bits u8 = 0
    let! restart_interval u16 = 0
    ref let! data = a_data
    trylet magic u16 = BS::FrontBeU16(@!data), err:
        return err
    if magic != 0xffd8:
        debug#("bad magic: ", wrap_as(magic, fmt::u16_hex), "\n")
        return CorruptionErrorVal
    while true:
        trylet chunk_kind u16 = BS::FrontBeU16(@!data), err:
            return err
        if chunk_kind == 0xffd9:
            break
        trylet chunk_length u16 = BS::FrontBeU16(@!data), err:
            return err
        debug#("CHUNK: ", wrap_as(chunk_kind, fmt::u16_hex), " ", chunk_length,
               "\n")
        trylet chunk_slice span(u8) =
          BS::FrontSlice(@!data, as(chunk_length - 2, uint)), err:
            return err
        cond:
            case chunk_kind == 0xffe0:
                trylet dummy Success = DecodeAppInfo(chunk_slice, @!app_info),
                  err:
                    return err
            case chunk_kind == 0xffc0:
                trylet dummy Success =
                  DecodeStartOfFrame(chunk_slice, @!frame_info), err:
                    return err
            case chunk_kind == 0xffc4:
                trylet dummy Success =
                  DecodeHufmanTable(chunk_slice, @!huffman_trees), err:
                    return err
            case chunk_kind == 0xffdb:
                tryset qt_avail_bits =
                  DecodeQuantizationTable(chunk_slice, @!quantization_tab), err:
                    return err
            case chunk_kind == 0xffdd:
                ; tryset restart_interval = DecodeRestartInterval(chunk_slice), err:
                ;    return err
                return UnsupportedErrorVal
            case chunk_kind == 0xffda:
                ; start of scan chunk, huffman encoded image data follows
                trylet dummy Success = DecodeScan(chunk_slice, @!frame_info),
                  err:
                    return err
                trylet bytes_consumed uint =
                  DecodeMacroBlocksHuffman(data, @frame_info, @huffman_trees,
                    @quantization_tab, out), err:
                    return err
                do BS::SkipUnchecked(@!data, bytes_consumed)
            case chunk_kind == 0xfffe:
                debug#("chunk ignored\n")
            case chunk_kind & 0xfff0 == 0xffe0:
                debug#("chunk ignored\n")
            case true:
                return UnsupportedErrorVal
    debug#("DecodeImage complete ", len(data), "\n")
    return SuccessVal
