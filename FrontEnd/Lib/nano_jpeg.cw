@doc """Simple JPEG Decoder loosely based on
https://keyj.emphy.de/nanojpeg/
More Info
https://github.com/corkami/formats/blob/master/image/jpeg.md
For Huffman codes
https://www.ece.ucdavis.edu/cerl/wp-content/uploads/sites/14/2015/09/GenHuffCodes.pdf
https://www.youtube.com/watch?v=CPT4FSkFUgs"""
(module [] :
(import BS bytestream)

(import fmt)


@doc """To enable debug logging make sure the next macro is called `debug#`
To enable debug logging make sure the second macro is called `debug#`"""
(macro debug# STMT_LIST [(mparam $parts EXPR_LIST_REST)] [] :
    (fmt::print# $parts))


(macro xdebug# STMT_LIST [(mparam $parts EXPR_LIST_REST)] [] :)


(global W1 s32 2841)


(global W2 s32 2676)


(global W3 s32 2408)


(global W5 s32 1609)


(global W6 s32 1108)


(global W7 s32 565)


@doc "updates blk in place"
(fun RowIDCT [(param blk (ptr! (array 8 s32)))] void :
    (let! x1 auto (<< (at (^ blk) 4) 11))
    (let! x2 auto (at (^ blk) 6))
    (let! x3 auto (at (^ blk) 2))
    (let! x4 auto (at (^ blk) 1))
    (let! x5 auto (at (^ blk) 7))
    (let! x6 auto (at (^ blk) 5))
    (let! x7 auto (at (^ blk) 3))
    (if (== (paren (or (or (or (or (or (or x1 x2) x3) x4) x5) x6) x7)) 0) :
        (let t auto (<< (at (^ blk) 0) 3))
        (for i 0 8_u32 1 :
            (= (at (^ blk) i) t))
        (return)
     :)
    (let! x0 auto (+ (paren (<< (at (^ blk) 0) 11)) 128))
    (let! x8 auto (* (+ x4 x5) W7))
    (= x4 (+ x8 (* x4 (- W1 W7))))
    (= x5 (- x8 (* x5 (+ W1 W7))))
    (= x8 (* (+ x6 x7) W3))
    (= x6 (- x8 (* x6 (- W3 W5))))
    (= x7 (- x8 (* x7 (+ W3 W5))))
    (= x8 (+ x0 x1))
    (-= x0 x1)
    (= x1 (* (+ x3 x2) W6))
    (= x2 (- x1 (* x2 (+ W2 W6))))
    (= x3 (+ x1 (* x3 (- W2 W6))))
    (= x1 (+ x4 x6))
    (-= x4 x6)
    (= x6 (+ x5 x7))
    (-= x5 x7)
    (= x7 (+ x8 x3))
    (-= x8 x3)
    (= x3 (+ x0 x2))
    (-= x0 x2)
    (= x2 (>> (+ (* (+ x4 x5) 181) 128) 8))
    (= x4 (>> (+ (* (- x4 x5) 181) 128) 8))
    (= (at (^ blk) 0) (>> (+ x7 x1) 8))
    (= (at (^ blk) 1) (>> (+ x3 x2) 8))
    (= (at (^ blk) 2) (>> (+ x0 x4) 8))
    (= (at (^ blk) 3) (>> (+ x8 x6) 8))
    (= (at (^ blk) 4) (>> (- x8 x6) 8))
    (= (at (^ blk) 5) (>> (- x0 x4) 8))
    (= (at (^ blk) 6) (>> (- x3 x2) 8))
    (= (at (^ blk) 7) (>> (- x7 x1) 8)))


@doc "clamp x to [0:255]"
(fun ClampU8 [(param x s32)] u8 :
    (cond :
        (case (< x 0) :
            (return 0))
        (case (>= x 0xff) :
            (return 0xff))
        (case true :
            (return (as x u8)))))


(fun ColIDCT [
        (param blk (ptr (array (* 8 8) s32)))
        (param out (slice! u8))
        (param stride uint)] void :
    (let! x1 auto (<< (at (^ blk) (* 8 4)) 8))
    (let! x2 auto (at (^ blk) (* 8 6)))
    (let! x3 auto (at (^ blk) (* 8 2)))
    (let! x4 auto (at (^ blk) (* 8 1)))
    (let! x5 auto (at (^ blk) (* 8 7)))
    (let! x6 auto (at (^ blk) (* 8 5)))
    (let! x7 auto (at (^ blk) (* 8 3)))
    (if (== (paren (or (or (or (or (or (or x1 x2) x3) x4) x5) x6) x7)) 0) :
        (let t auto (ClampU8 [(+ (paren (>> (+ (at (^ blk) 0) 32) 6)) 128)]))
        (for i 0 8_u32 1 :
            (= (at out (* i 8)) t))
        (return)
     :)
    (let! x0 auto (+ (paren (<< (at (^ blk) 0) 8)) 8192))
    (let! x8 auto (+ (* (+ x4 x5) W7) 4))
    (= x4 (>> (+ x8 (* x4 (- W1 W7))) 3))
    (= x5 (>> (- x8 (* x5 (+ W1 W7))) 3))
    (= x8 (+ (* (+ x6 x7) W3) 4))
    (= x6 (>> (- x8 (* x6 (- W3 W5))) 3))
    (= x7 (>> (- x8 (* x7 (+ W3 W5))) 3))
    (= x8 (+ x0 x1))
    (-= x0 x1)
    (= x1 (+ (* (+ x3 x2) W6) 4))
    (= x2 (>> (- x1 (* x2 (+ W2 W6))) 3))
    (= x3 (>> (+ x1 (* x3 (- W2 W6))) 3))
    (= x1 (+ x4 x6))
    (-= x4 x6)
    (= x6 (+ x5 x7))
    (-= x5 x7)
    (= x7 (+ x8 x3))
    (-= x8 x3)
    (= x3 (+ x0 x2))
    (-= x0 x2)
    (= x2 (>> (+ (* (+ x4 x5) 181) 128) 8))
    (= x4 (>> (+ (* (- x4 x5) 181) 128) 8))
    (= (at out (* 0 stride)) (ClampU8 [(+ (paren (>> (+ x7 x1) 14)) 128)]))
    (= (at out (* 1 stride)) (ClampU8 [(+ (paren (>> (+ x3 x2) 14)) 128)]))
    (= (at out (* 2 stride)) (ClampU8 [(+ (paren (>> (+ x0 x4) 14)) 128)]))
    (= (at out (* 3 stride)) (ClampU8 [(+ (paren (>> (+ x8 x6) 14)) 128)]))
    (= (at out (* 4 stride)) (ClampU8 [(+ (paren (>> (- x8 x6) 14)) 128)]))
    (= (at out (* 5 stride)) (ClampU8 [(+ (paren (>> (- x0 x4) 14)) 128)]))
    (= (at out (* 6 stride)) (ClampU8 [(+ (paren (>> (- x3 x2) 14)) 128)]))
    (= (at out (* 7 stride)) (ClampU8 [(+ (paren (>> (- x7 x1) 14)) 128)])))


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
    (field qtsel u8)
    @doc "image dimensions in pixels"
    (field width u32)
    (field height u32)
    (field stride u32)
    (field dctabsel u8)
    (field actabsel u8))


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


(fun DecodeQuantizationTable [(param chunk (slice u8)) (param qtab (ptr! (array 4 (array 64 u8))))] (union [
        u8
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (@ref let! data auto chunk)
    (let! qtavail u8 0)
    (while (>= (len data) 65) :
        (let t auto (at data 0))
        (if (!= (and t 0xfc) 0) :
            (return CorruptionErrorVal)
         :)
        (debug# "processing qt: " t "\n")
        (or= qtavail (<< 1 t))
        (for i 0 64_u32 1 :
            (= (at (at (^ qtab) t) i) (at data (+ i 1))))
        (do (BS::SkipUnchecked [(&! data) 65])))
    (if (!= (len data) 0) :
        (return CorruptionErrorVal)
     :)
    (return qtavail))


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
        (trylet! qtsel u8 (BS::FrontU8 [(&! data)]) err :
            (return err))
        (if (!= (and qtsel 0xfc) 0) :
            (debug# "bad qtsel: " qtsel "\n")
            (return CorruptionErrorVal)
         :)
        (= (^. comp qtsel) qtsel))
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
        (= (^. comp dctabsel) (and (paren (>> tabsel 4)) 1))
        (= (^. comp actabsel) (and tabsel 1))
        (debug# "tabsel[" (^. comp cid) "]: " (^. comp dctabsel) "." (^. comp actabsel) "\n")
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


@doc "returns new dc value on success"
(fun DecodeBlock [
        (param bs (ptr! BitStream))
        (param dc_tab (ptr HuffmanTree))
        (param ac_tab (ptr HuffmanTree))
        (param last_dc s16)] (union [
        s16
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (let dc_code auto (NextSymbol [bs dc_tab]))
    (let dc_val s16 (GetVal [bs (and dc_code 0xf)]))
    (debug# "dc=" (+ dc_val last_dc) "\n")
    (let! coeff u16 1)
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
        (debug# "ac=" ac_val " " (- coeff 1) "\n")
        (if (> coeff 63) :
            (break)
         :))
    (return (+ last_dc dc_val)))


(fun DecodeMacroBlocksHuffman [
        (param chunk (slice u8))
        (param frame_info (ptr FrameInfo))
        (param huffman_trees (ptr (array 2 (array 2 HuffmanTree))))] (union [
        Success
        CorruptionError
        UnsupportedError
        BS::OutOfBoundsError]) :
    (debug# "Decode blocks\n")
    (@ref let! bs auto (rec_val BitStream [chunk]))
    (let! dc_last auto (array_val 3 s16 [0 0 0]))
    (for m 0 (* (^. frame_info mbwidth) (^. frame_info mbheight)) 1 :
        (for c 0 (^. frame_info ncomp) 1 :
            (let comp (ptr Component) (& (at (^. frame_info comp) c)))
            (let dc_tab (ptr HuffmanTree) (& (at (at (^ huffman_trees) 0) (^. comp dctabsel))))
            (let ac_tab (ptr HuffmanTree) (& (at (at (^ huffman_trees) 1) (^. comp actabsel))))
            (for y 0 (^. comp ssy) 1 :
                (for x 0 (^. comp ssx) 1 :
                    @doc """debug#("Block: ", m, " comp=", c, " x=", x, " y=", y, "\n")"""
                    (debug# "Block ===================\n")
                    (tryset (at dc_last c) (DecodeBlock [
                            (&! bs)
                            dc_tab
                            ac_tab
                            (at dc_last c)]) err :
                        (return err))
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
    (@ref let! quantization_tab (array 4 (array 64 u8)) undef)
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
                (trylet dummy2 Success (DecodeMacroBlocksHuffman [data (& frame_info) (& huffman_trees)]) err :
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

