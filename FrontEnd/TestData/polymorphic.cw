(module main [] :
(import test)
(import fmt)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (let @mut @ref opt auto (rec_val fmt::SysFormatOptions []))
    (let @mut buffer auto (array_val fmt::FORMATED_STRING_MAX_LEN u8))
    (let @mut @ref s (slice @mut u8) buffer)
    (let @mut n uint 0)
    (= n (call @polymorphic SysRender [
            666_uint
            s
            (& @mut opt)]))
    (test::AssertSliceEq! (slice_val (front s) n) "666")
    (= n (call @polymorphic SysRender [
            true
            s
            (& @mut opt)]))
    (test::AssertSliceEq! (slice_val (front s) n) "true")
    (= n (call @polymorphic SysRender [
            69_u16
            s
            (& @mut opt)]))
    (test::AssertSliceEq! (slice_val (front s) n) "69")
    (= n (call @polymorphic SysRender [
            -69_s32
            s
            (& @mut opt)]))
    (test::AssertSliceEq! (slice_val (front s) n) "-69")
    (= n (call @polymorphic SysRender [
            (as 120_u8 fmt::rune)
            s
            (& @mut opt)]))
    (test::AssertSliceEq! (slice_val (front s) n) "x")
    (= n (call @polymorphic SysRender [
            (as 2_r64 fmt::r64_hex)
            s
            (& @mut opt)]))
    (test::AssertSliceEq! (slice_val (front s) n) "0x1.p1")
    @doc "test end"
    (test::Success!)
    (return 0))

)
