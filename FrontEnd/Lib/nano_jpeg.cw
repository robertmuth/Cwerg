@doc """Simple JPEG Decoder loosely based on
https://github.com/richgel999/picojpeg
More on jpeg
https://github.com/corkami/formats/blob/master/image/jpeg.md
https://www.youtube.com/watch?v=CPT4FSkFUgs
More on Huffman codes
https://www.ece.ucdavis.edu/cerl/wp-content/uploads/sites/14/2015/09/GenHuffCodes.pdf
on fast idct transforms:
Feig, E.; Winograd, S. (September 1992b). "Fast algorithms for the discrete cosine transform".
                  IEEE Transactions on Signal Processing. 40 (9): 2174–2193"""
(module [] :
(import BS bytestream)

(import fmt)


@doc """To enable debug logging make sure the next macro is called `debug#`
To enable debug logging make sure the second macro is called `debug#`"""
(macro debug# STMT_LIST [(mparam $parts EXPR_LIST_REST)] [] :
    (fmt::print# $parts))


(macro xdebug# STMT_LIST [(mparam $parts EXPR_LIST_REST)] [] :)


(global WinogradMultipliers auto (array_val 64 u8 [
        128 178 178 167 246 167 151 232 232 151 128 209 219 209 128 101 178 197 197
        178 101 69 139 167 177 167 139 69 35 96 131 151 151 131 96 35 49 91 118 128
        118 91 49 46 81 101 101 81 46 42 69 79 69 42 35 54 54 35 28 37 28 19 19 10]))


(macro div_pow2_with_rounding# EXPR [(mparam $x EXPR) (mparam $d EXPR)] [] :
    (>> (+ $x (paren (<< 1 (- $d 1)))) $d))


(fun ApplyWindogradMulipliers [(param qt_tab (ptr! (array 64 s16)))] void :
    (let c s32 (paren (<< 1 (- (- 10 7) 1))))
    (for i 0 (len (^ qt_tab)) 1 :
        (let! x s32 (as (at (^ qt_tab) i) s32))
        (let y auto x)
        (*= x (as (at WinogradMultipliers i) s32))
        @doc "divide by 2^3 with rouding"
        (= x (div_pow2_with_rounding# x (- 10 7)))
        (debug# "apply: " i " " y " " x "\n")
        (= (at (^ qt_tab) i) (as x s16))))


@doc """multiply helper functions are the 4 types of signed multiplies needed by the Winograd IDCT.
1 / cos(4 * pi/16)   362, 256+106"""
(global c_b1_b3 s32 362)


@doc "1 / cos(6*pi/16) 669,  256+256+157"
(global c_b2 s32 669)


@doc "1 / cos(2*pi/16)  277, 256+21"
(global c_b4 s32 277)


@doc "1 / (cos(2*pi/16) + cos(6*pi/16))  196, 196"
(global c_b5 s32 196)


(fun imul [(param w s16) (param c s32)] s16 :
    (let x s32 (* (as w s32) c))
    (return (as (div_pow2_with_rounding# x 8) s16)))


(macro CommonIDCT# STMT_LIST [] [] :
    (let x4 auto (- src4 src7))
    (let x7 auto (+ src4 src7))
    (let x5 auto (+ src5 src6))
    (let x6 auto (- src5 src6))
    (let tmp1 auto (imul [(- x4 x6) c_b5]))
    (let stg26 auto (- (imul [x6 c_b4]) tmp1))
    (let x24 auto (- tmp1 (imul [x4 c_b2])))
    (let x15 auto (- x5 x7))
    (let x17 auto (+ x5 x7))
    (let tmp2 auto (- stg26 x17))
    (let tmp3 auto (- (imul [x15 c_b1_b3]) tmp2))
    (let x44 auto (+ tmp3 x24))
    (let x30 auto (+ src0 src1))
    (let x31 auto (- src0 src1))
    (let x12 auto (- src2 src3))
    (let x13 auto (+ src2 src3))
    (let x32 auto (- (imul [x12 c_b1_b3]) x13))
    (let x40 auto (+ x30 x13))
    (let x43 auto (- x30 x13))
    (let x41 auto (+ x31 x32))
    (let x42 auto (- x31 x32)))


@doc "updates blk in place"
(fun RowIDCT [(param blk (ptr! (array (* 8 8) s16)))] void :
    (for o 0 (len (^ blk)) 8 :
        (let src0 auto (at (^ blk) (+ o 0)))
        (let src5 auto (at (^ blk) (+ o 1)))
        (let src2 auto (at (^ blk) (+ o 2)))
        (let src7 auto (at (^ blk) (+ o 3)))
        (let src1 auto (at (^ blk) (+ o 4)))
        (let src4 auto (at (^ blk) (+ o 5)))
        (let src3 auto (at (^ blk) (+ o 6)))
        (let src6 auto (at (^ blk) (+ o 7)))
        (if (== (paren (or (or (or (or (or (or src1 src2) src3) src4) src5) src6) src7)) 0) :
            (debug# "idc-row shortcicuit " src0 "\n")
            (for i 0 8_uint 1 :
                (= (at (^ blk) (+ o i)) src0))
            (continue)
         :)
        (CommonIDCT#)
        (debug# "idc-row out " (+ x40 x17) " " (+ x41 tmp2) " " (+ x42 tmp3) " " (- x43 x44) "\n")
        (= (at (^ blk) (+ o 0)) (+ x40 x17))
        (= (at (^ blk) (+ o 1)) (+ x41 tmp2))
        (= (at (^ blk) (+ o 2)) (+ x42 tmp3))
        (= (at (^ blk) (+ o 3)) (- x43 x44))
        (= (at (^ blk) (+ o 4)) (+ x43 x44))
        (= (at (^ blk) (+ o 5)) (- x42 tmp3))
        (= (at (^ blk) (+ o 6)) (- x41 tmp2))
        (= (at (^ blk) (+ o 7)) (- x40 x17))))


@doc "descale and clamp x to [0:255]"
(fun descale_clamp [(param xx s16)] u8 :
    (let x auto (+ (div_pow2_with_rounding# xx 7) 128))
    (cond :
        (case (< x 0) :
            (return 0))
        (case (>= x 0xff) :
            (return 0xff))
        (case true :
            (return (as x u8)))))


(fun ColIDCT [(param blk (ptr (array (* 8 8) s16))) (param out (ptr! (array (* 8 8) u8)))] void :
    (for o 0 8_uint 1 :
        (let src0 auto (at (^ blk) (+ o (* 8 0))))
        (let src5 auto (at (^ blk) (+ o (* 8 1))))
        (let src2 auto (at (^ blk) (+ o (* 8 2))))
        (let src7 auto (at (^ blk) (+ o (* 8 3))))
        (let src1 auto (at (^ blk) (+ o (* 8 4))))
        (let src4 auto (at (^ blk) (+ o (* 8 5))))
        (let src3 auto (at (^ blk) (+ o (* 8 6))))
        (let src6 auto (at (^ blk) (+ o (* 8 7))))
        (if (== (paren (or (or (or (or (or (or src1 src2) src3) src4) src5) src6) src7)) 0) :
            (debug# "idc-col shortcicuit " o " " src0 "\n")
            (let t auto (descale_clamp [src0]))
            (for i 0 (len (^ blk)) 8 :
                (= (at (^ out) (+ o i)) t))
            (continue)
         :)
        (CommonIDCT#)
        (debug# "idc-col out " (+ x40 x17) " " (+ x41 tmp2) " " (+ x42 tmp3) " " (- x43 x44) "\n")
        (= (at (^ out) (+ o (* 8 0))) (descale_clamp [(+ x40 x17)]))
        (= (at (^ out) (+ o (* 8 1))) (descale_clamp [(+ x41 tmp2)]))
        (= (at (^ out) (+ o (* 8 2))) (descale_clamp [(+ x42 tmp3)]))
        (= (at (^ out) (+ o (* 8 3))) (descale_clamp [(- x43 x44)]))
        (= (at (^ out) (+ o (* 8 4))) (descale_clamp [(+ x43 x44)]))
        (= (at (^ out) (+ o (* 8 5))) (descale_clamp [(- x42 tmp3)]))
        (= (at (^ out) (+ o (* 8 6))) (descale_clamp [(- x41 tmp2)]))
        (= (at (^ out) (+ o (* 8 7))) (descale_clamp [(- x40 x17)]))))


@doc "for huffman decoding"
(defrec BitStream :
    (field buf (slice u8))
    (field offset uint)
    @doc """contains the next up to 8 bits from the stream
the exact number is bits_count"""
    (field bits_cache u8)
    (field bits_count u8)
    @doc "end-of-stream flag - once set it will not be cleared"
    (field eos bool))


@pub (fun GetNextBit [(param bs (ptr! BitStream))] u16 :
    (let! bits_count u8 (^. bs bits_count))
    (let! bits_cache u8 (^. bs bits_cache))
    (if (== bits_count 0) :
        (if (== (^. bs offset) (len (^. bs buf))) :
            (= (^. bs eos) true)
            (return 0)
         :)
        (= bits_cache (at (^. bs buf) (^. bs offset)))
        @doc """debug#("new cache: ", wrap_as(bits_cache, fmt::u8_hex), "\n")"""
        (+= (^. bs offset) 1)
        (= bits_count 8)
        (if (== bits_cache 0xff) :
            (if (== (^. bs offset) (len (^. bs buf))) :
                (= (^. bs eos) true)
                (return 0)
             :)
            (let zeros auto (at (^. bs buf) (^. bs offset)))
            (if (!= zeros 0) :
                (= (^. bs eos) true)
                (return 0)
             :)
            (+= (^. bs offset) 1)
         :)
        (= (^. bs bits_cache) bits_cache)
     :)
    (-= bits_count 1)
    (let out auto (as (and (paren (>> bits_cache bits_count)) 1) u16))
    (= (^. bs bits_count) bits_count)
    (return out))


(defrec HuffmanTree :
    (field counts (array 16 u8))
    (field symbols (array 256 u8))
    (field num_symbols u8)
    (field min_code (array 16 u16))
    (field max_code (array 16 u16))
    (field val_ptr (array 16 u8)))


(global BAD_SYMBOL auto 0xffff_u16)


(fun NextSymbol [(param bs (ptr! BitStream)) (param ht (ptr HuffmanTree))] u16 :
    (let! offset u16 (GetNextBit [bs]))
    (for level 0 (len (^. ht counts)) 1 :
        (let mc auto (at (^. ht max_code) level))
        (if (&& (<= offset mc) (!= mc 0xffff)) :
            (+= offset (- (as (at (^. ht val_ptr) level) u16) (at (^. ht min_code) level)))
            (debug# "huffman level=" level " offset=" offset " symbol=" (at (^. ht symbols) offset) "\n")
            (return (as (at (^. ht symbols) offset) u16))
         :)
        (<<= offset 1)
        (+= offset (GetNextBit [bs])))
    (return BAD_SYMBOL))


@doc "not we rely on wrap around arithmetic"
(fun GetVal [(param bs (ptr! BitStream)) (param num_bits u16)] s16 :
    (let bits auto (as num_bits s32))
    (let! out s32 0)
    (for i 0 bits 1 :
        (<<= out 1)
        (or= out (as (GetNextBit [bs]) s32)))
    @doc "note: signed shift"
    (if (< out (<< 1 (- bits 1))) :
        (+= out (+ (paren (<< (paren -1) bits)) 1))
     :)
    (return (as out s16)))


(defrec AppInfo :
    (field version_major u8)
    (field version_minor u8)
    (field units u8)
    (field density_x u16)
    (field density_y u16)
    (field thumbnail_w u8)
    (field thumbnail_h u8))


(defrec Component :
    (field cid u8)
    (field ssx u32)
    (field ssy u32)
    @doc "quantization table index:  0-3"
    (field qt_tab u8)
    @doc "image dimensions in pixels"
    (field width u32)
    (field height u32)
    (field stride u32)
    @doc "huffman table index for dc decoding: 0-1"
    (field dc_tab u8)
    @doc "huffman table index for ac decoding: 0-1"
    (field ac_tab u8))


(defrec FrameInfo :
    (field width u32)
    (field height u32)
    (field ncomp u8)
    @doc "macro block dimensions in pixels (e.g. 8x8)"
    (field mbsizex u32)
    (field mbsizey u32)
    @doc "image dimension measure in macro blocks"
    (field mbwidth u32)
    (field mbheight u32)
    (field comp (array 3 Component)))


@pub (@wrapped type Success void)


@pub (global SuccessVal auto (wrap_as void_val Success))


@pub (@wrapped type CorruptionError void)


@pub (global CorruptionErrorVal auto (wrap_as void_val CorruptionError))


@pub (@wrapped type UnsupportedError void)


@pub (global UnsupportedErrorVal auto (wrap_as void_val UnsupportedError))


(fun div_roundup [(param a u32) (param b u32)] u32 :
    (return (/ (- (+ a b) 1) b)))


(fun DecodeHufmanTable [(param chunk (slice u8)) (param huffman_trees (ptr! (array 2 (array 2 HuffmanTree))))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! data auto chunk)
    (let kind auto (BS::FrontU8Unchecked [(&! data)]))
    (if (!= (and kind 0xec) 0) :
        (return CorruptionErrorVal)
     :)
    (let pos auto (and kind 3))
    (if (> pos 1) :
        (return UnsupportedErrorVal)
     :)
    @doc "0 means dc"
    (let is_ac auto (>> (and kind 0x10) 4))
    (let ht (ptr! HuffmanTree) (&! (at (at (^ huffman_trees) is_ac) pos)))
    (let counts auto (BS::FrontSliceUnchecked [(&! data) 16]))
    (let! total auto 0_uint)
    (for i 0 16_s32 1 :
        (+= total (as (at counts i) uint))
        (= (at (^. ht counts) i) (at counts i)))
    (if (< (len data) total) :
        (return BS::OutOfBoundsErrorVal)
     :)
    (for i 0 total 1 :
        (= (at (^. ht symbols) i) (at data i)))
    (if (> total 255) :
        (return CorruptionErrorVal)
     :)
    (= (^. ht num_symbols) (as total u8))
    (do (BS::SkipUnchecked [(&! data) total]))
    (debug# "Hufman total codes[" is_ac "," pos "]: " total "\n")
    (let! acc u16 0)
    (let! code u16 0)
    (for i 0 16_s32 1 :
        (let num u16 (as (at counts i) u16))
        (if (== num 0) :
            (= (at (^. ht min_code) i) 0)
            (= (at (^. ht max_code) i) 0xffff_u16)
            (= (at (^. ht val_ptr) i) 0)
         :
            (= (at (^. ht min_code) i) code)
            (= (at (^. ht max_code) i) (- (+ code num) 1))
            (= (at (^. ht val_ptr) i) (as acc u8))
            (+= acc num)
            (+= code num))
        (<<= code 1))
    (return SuccessVal))


(fun DecodeQuantizationTable [(param chunk (slice u8)) (param qt_tabs (ptr! (array 4 (array 64 s16))))] (union [
        u8
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! data auto chunk)
    (let! qt_avail u8 0)
    (while (>= (len data) 65) :
        (let t auto (at data 0))
        (if (!= (and t 0xfc) 0) :
            (return CorruptionErrorVal)
         :)
        (debug# "processing qt: " t "\n")
        (or= qt_avail (<< 1 t))
        (let qt_tab auto (&! (at (^ qt_tabs) t)))
        (for i 0 64_u32 1 :
            (= (at (^ qt_tab) i) (as (at data (+ i 1)) s16)))
        (do (ApplyWindogradMulipliers [qt_tab]))
        (do (BS::SkipUnchecked [(&! data) 65])))
    (if (!= (len data) 0) :
        (return CorruptionErrorVal)
     :)
    (return qt_avail))


(fun DecodeRestartInterval [(param chunk (slice u8))] (union [
        u16
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! data auto chunk)
    (trylet interval u16 (BS::FrontBeU16 [(&! data)]) err :
        (return err))
    (debug# "restart interval: " interval "\n")
    (return interval))


(fun DecodeAppInfo [(param chunk (slice u8)) (param app_info (ptr! AppInfo))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! data auto chunk)
    (if (< (len data) 14) :
        (return CorruptionErrorVal)
     :)
    (if (|| (|| (|| (|| (!= (at data 0) 'J') (!= (at data 1) 'F')) (!= (at data 2) 'I')) (!= (at data 3) 'F')) (!= (at data 4) 0)) :
        (return CorruptionErrorVal)
     :)
    (do (BS::SkipUnchecked [(&! data) 5]))
    (= (^. app_info version_major) (BS::FrontU8Unchecked [(&! data)]))
    (= (^. app_info version_minor) (BS::FrontU8Unchecked [(&! data)]))
    (= (^. app_info units) (BS::FrontU8Unchecked [(&! data)]))
    (= (^. app_info density_x) (BS::FrontBeU16Unchecked [(&! data)]))
    (= (^. app_info density_y) (BS::FrontBeU16Unchecked [(&! data)]))
    (= (^. app_info thumbnail_w) (BS::FrontU8Unchecked [(&! data)]))
    (= (^. app_info thumbnail_h) (BS::FrontU8Unchecked [(&! data)]))
    (debug# "AppInfo: " (^. app_info version_major) "." (^. app_info version_minor) "\n")
    (return SuccessVal))


(fun DecodeStartOfFrame [(param chunk (slice u8)) (param out (ptr! FrameInfo))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! data auto chunk)
    (trylet format u8 (BS::FrontU8 [(&! data)]) err :
        (return err))
    (if (!= format 8) :
        (debug# "unsupported format: " format "\n")
        (return UnsupportedErrorVal)
     :)
    (trylet height u16 (BS::FrontBeU16 [(&! data)]) err :
        (return err))
    (= (^. out height) (as height u32))
    (trylet width u16 (BS::FrontBeU16 [(&! data)]) err :
        (return err))
    (= (^. out width) (as width u32))
    (trylet ncomp u8 (BS::FrontU8 [(&! data)]) err :
        (return err))
    (= (^. out ncomp) ncomp)
    (if (&& (!= ncomp 1) (!= ncomp 3)) :
        (debug# "unsupported ncomp: " ncomp "\n")
        (return UnsupportedErrorVal)
     :)
    (debug# "frame: " width "x" height " ncomp: " ncomp "\n")
    (let! ssxmax u32 0)
    (let! ssymax u32 0)
    (for i 0 ncomp 1 :
        (let comp (ptr! Component) (&! (paren (at (^. out comp) i))))
        (tryset (^. comp cid) (BS::FrontU8 [(&! data)]) err :
            (return err))
        (trylet ss u8 (BS::FrontU8 [(&! data)]) err :
            (return err))
        (let ssx auto (as (>> ss 4) u32))
        (let ssy auto (as (and ss 0xf) u32))
        @doc "ssy must be a power of two"
        (if (|| (|| (== ssx 0) (== ssy 0)) (!= (and ssy (- ssy 1)) 0)) :
            (debug# "bad ss: " ssx "x" ssy "\n")
            (return CorruptionErrorVal)
         :)
        (debug# "comp: " i " " (^. comp cid) " " ssx "x" ssy "\n")
        (= (^. comp ssx) ssx)
        (= (^. comp ssy) ssy)
        (max= ssxmax ssx)
        (max= ssymax ssy)
        (trylet! qt_tab u8 (BS::FrontU8 [(&! data)]) err :
            (return err))
        (if (!= (and qt_tab 0xfc) 0) :
            (debug# "bad qt_tab: " qt_tab "\n")
            (return CorruptionErrorVal)
         :)
        (= (^. comp qt_tab) qt_tab))
    (if (== ncomp 1) :
        (= ssxmax 1)
        (= ssymax 1)
        (= (. (at (^. out comp) 0) ssx) 1)
        (= (. (at (^. out comp) 0) ssy) 1)
     :)
    (let mbsizex u32 (* (as ssxmax u32) 8))
    (let mbsizey u32 (* (as ssymax u32) 8))
    (= (^. out mbsizex) mbsizex)
    (= (^. out mbsizey) mbsizey)
    (= (^. out mbwidth) (div_roundup [(^. out width) mbsizex]))
    (= (^. out mbheight) (div_roundup [(^. out height) mbsizey]))
    (debug# "mbsize: " mbsizex "x" mbsizey " mbdim: " (^. out mbwidth) "x" (^. out mbheight) "\n")
    (for i 0 ncomp 1 :
        (let comp (ptr! Component) (&! (paren (at (^. out comp) i))))
        (= (^. comp width) (div_roundup [(* (^. out width) (^. comp ssx)) ssxmax]))
        (= (^. comp height) (div_roundup [(* (^. out height) (^. comp ssy)) ssymax]))
        (= (^. comp stride) (* (* (^. out mbwidth) (^. comp ssx)) 8))
        (if (&& (< (^. comp width) 3) (!= (^. comp ssx) ssxmax)) :
            (debug# "bad width: " (^. comp width) "\n")
            (return CorruptionErrorVal)
         :)
        (if (&& (< (^. comp height) 3) (!= (^. comp ssy) ssymax)) :
            (debug# "bad height: " (^. comp height) "\n")
            (return CorruptionErrorVal)
         :)
        (debug# "comp: " i " " (^. comp width) "x" (^. comp height) " stride:" (^. comp stride) "\n"))
    (return SuccessVal))


(fun DecodeScan [(param chunk (slice u8)) (param frame_info (ptr! FrameInfo))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! data auto chunk)
    (trylet ncomp u8 (BS::FrontU8 [(&! data)]) err :
        (return err))
    (if (!= ncomp (^. frame_info ncomp)) :
        (return UnsupportedErrorVal)
     :)
    (for i 0 ncomp 1 :
        (if (< (len data) 2) :
            (return BS::OutOfBoundsErrorVal)
         :)
        (let comp (ptr! Component) (&! (paren (at (^. frame_info comp) i))))
        (if (!= (at data 0) (^. comp cid)) :
            (return CorruptionErrorVal)
         :)
        (let tabsel auto (at data 1))
        (if (!= (and tabsel 0xee) 0) :
            (return CorruptionErrorVal)
         :)
        (= (^. comp dc_tab) (and (paren (>> tabsel 4)) 1))
        (= (^. comp ac_tab) (and tabsel 1))
        (debug# "tabsel[" (^. comp cid) "]: " (^. comp dc_tab) "." (^. comp ac_tab) "\n")
        (do (BS::SkipUnchecked [(&! data) 2]))
        (if (< (len data) 3) :
            (return BS::OutOfBoundsErrorVal)
         :))
    (if (|| (|| (!= (at data 0) 0) (!= (at data 1) 63)) (!= (at data 2) 0)) :
        (return UnsupportedErrorVal)
     :)
    (do (BS::SkipUnchecked [(&! data) 3]))
    (debug# ">>>>>>> " (at data 0) "\n")
    (return SuccessVal))


(global ZigZagIndex auto (array_val (* 8 8) u8 [
        0 1 8 16 9 2 3 10 17 24 32 25 18 11 4 5 12 19 26 33 40 48 41 34 27 20 13 6
        7 14 21 28 35 42 49 56 57 50 43 36 29 22 15 23 30 37 44 51 58 59 52 45 38
        31 39 46 53 60 61 54 47 55 62 63]))


@doc "returns new dc value on success"
(fun DecodeBlock [
        (param bs (ptr! BitStream))
        (param dc_tab (ptr HuffmanTree))
        (param ac_tab (ptr HuffmanTree))
        (param qt_tab (ptr (array 64 s16)))
        (param out (ptr! (array (* 8 8) s16)))
        (param last_dc s16)] (union [
        s16
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (for i 0 (len (^ out)) 1 :
        (= (at (^ out) i) 0))
    (let dc_code auto (NextSymbol [bs dc_tab]))
    (let dc_val s16 (+ last_dc (GetVal [bs (and dc_code 0xf)])))
    (debug# "dc=" (* dc_val (at (^ qt_tab) 0)) "\n")
    (= (at (^ out) 0) (* dc_val (at (^ qt_tab) 0)))
    (let! coeff u16 0)
    (while true :
        (let ac_code auto (NextSymbol [bs ac_tab]))
        (if (== ac_code 0) :
            (break)
         :)
        (let extra_bits auto (and ac_code 0xf))
        (let skip auto (paren (>> ac_code 4)))
        (if (&& (== extra_bits 0) (!= skip 15)) :
            (return CorruptionErrorVal)
         :)
        (let ac_val auto (GetVal [bs extra_bits]))
        (+= coeff (+ skip 1))
        (debug# "ac=" ac_val " " (at (^ qt_tab) coeff) " " coeff "\n")
        (= (at (^ out) (at ZigZagIndex coeff)) (* ac_val (at (^ qt_tab) coeff)))
        (if (>= coeff 63) :
            (break)
         :))
    (return dc_val))


(fun DecodeMacroBlocksHuffman [
        (param chunk (slice u8))
        (param frame_info (ptr FrameInfo))
        (param huffman_trees (ptr (array 2 (array 2 HuffmanTree))))
        (param quantization_tab (ptr (array 4 (array 64 s16))))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (debug# "Decode blocks\n")
    (@ref let! bs auto (rec_val BitStream [chunk]))
    (let! dc_last auto (array_val 3 s16 [0 0 0]))
    (@ref let! buffer (array (* 8 8) s16) undef)
    (@ref let! buffer2 (array (* 8 8) u8) undef)
    (for m 0 (* (^. frame_info mbwidth) (^. frame_info mbheight)) 1 :
        (for c 0 (^. frame_info ncomp) 1 :
            (let comp (ptr Component) (& (at (^. frame_info comp) c)))
            (let dc_tab (ptr HuffmanTree) (& (at (at (^ huffman_trees) 0) (^. comp dc_tab))))
            (let ac_tab (ptr HuffmanTree) (& (at (at (^ huffman_trees) 1) (^. comp ac_tab))))
            (let qt_tab (ptr (array 64 s16)) (& (at (^ quantization_tab) (^. comp qt_tab))))
            (for y 0 (^. comp ssy) 1 :
                (for x 0 (^. comp ssx) 1 :
                    @doc """debug#("Block: ", m, " comp=", c, " x=", x, " y=", y, "\n")"""
                    (debug# "Block ===================\n")
                    (tryset (at dc_last c) (DecodeBlock [
                            (&! bs)
                            dc_tab
                            ac_tab
                            qt_tab
                            (&! buffer)
                            (at dc_last c)]) err :
                        (return err))
                    (do (RowIDCT [(&! buffer)]))
                    (do (ColIDCT [(& buffer) (&! buffer2)]))
                    (if (== m 1000) :
                        (return UnsupportedErrorVal)
                     :)))))
    (return SuccessVal))


@pub (fun DecodeImage [(param a_data (slice u8))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (debug# "DecodeImage: " (len a_data) "\n")
    (@ref let! app_info AppInfo undef)
    (@ref let! frame_info FrameInfo undef)
    (@ref let! huffman_trees (array 2 (array 2 HuffmanTree)) undef)
    (@ref let! quantization_tab (array 4 (array 64 s16)) undef)
    (let! qt_avail_bits u8 0)
    (let! restart_interval u16 0)
    (@ref let! data auto a_data)
    (trylet magic u16 (BS::FrontBeU16 [(&! data)]) err :
        (return err))
    (if (!= magic 0xffd8) :
        (debug# "bad magic: " (wrap_as magic fmt::u16_hex) "\n")
        (return CorruptionErrorVal)
     :)
    (while true :
        (trylet chunk_kind u16 (BS::FrontBeU16 [(&! data)]) err :
            (return err))
        (trylet chunk_length u16 (BS::FrontBeU16 [(&! data)]) err :
            (return err))
        (debug# "CHUNK: " (wrap_as chunk_kind fmt::u16_hex) " " chunk_length "\n")
        (trylet chunk_slice (slice u8) (BS::FrontSlice [(&! data) (as (- chunk_length 2) uint)]) err :
            (return err))
        (cond :
            (case (== chunk_kind 0xffe0) :
                (trylet dummy Success (DecodeAppInfo [chunk_slice (&! app_info)]) err :
                    (return err)))
            (case (== chunk_kind 0xffc0) :
                (trylet dummy Success (DecodeStartOfFrame [chunk_slice (&! frame_info)]) err :
                    (return err)))
            (case (== chunk_kind 0xffc4) :
                (trylet dummy Success (DecodeHufmanTable [chunk_slice (&! huffman_trees)]) err :
                    (return err)))
            (case (== chunk_kind 0xffdb) :
                (tryset qt_avail_bits (DecodeQuantizationTable [chunk_slice (&! quantization_tab)]) err :
                    (return err)))
            (case (== chunk_kind 0xffdd) :
                (tryset restart_interval (DecodeRestartInterval [chunk_slice]) err :
                    (return err)))
            (case (== chunk_kind 0xffda) :
                @doc "start of scan chunk, huffman encoded image data follows"
                (trylet dummy Success (DecodeScan [chunk_slice (&! frame_info)]) err :
                    (return err))
                (trylet dummy2 Success (DecodeMacroBlocksHuffman [
                        data
                        (& frame_info)
                        (& huffman_trees)
                        (& quantization_tab)]) err :
                    (return err))
                (break))
            (case (== chunk_kind 0xfffe) :
                (debug# "chunk ignored\n"))
            (case (== (and chunk_kind 0xfff0) 0xffe0) :
                (debug# "chunk ignored\n"))
            (case true :
                (return UnsupportedErrorVal))))
    (debug# "DecodeImage complete\n")
    (return SuccessVal))
)

