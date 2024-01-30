(module main [] :
(import test)
(import fmt)

(enum @pub color S32 :
    (entry black 0)
    (entry white 1)
    (entry blue 2)
    (entry green 3)
    (entry red 4))


(fun @polymorphic fmt::SysRender [
        (param v color)
        (param out (slice! u8))
        (param options (ptr! fmt::SysFormatOptions))] uint :
    (return (@polymorphic fmt::SysRender [(unwrap v) out options])))


(defrec @pub ic32 :
    (field real s32)
    (field imag s32))

(fun @polymorphic fmt::SysRender [
        (param v ic32)
        (param s (slice! u8))
        (param opt (ptr! fmt::SysFormatOptions))] uint :
    (let f auto (front! s))
    (let l auto (len s))
    (let! n uint 0)
    (= n (@polymorphic fmt::SysRender [
       (. v real) s opt]))
    (+= n (@polymorphic fmt::SysRender [
        "+"  (slice_val (pinc f n) (- l n)) opt]))
    (+= n (@polymorphic fmt::SysRender [
        (. v imag)  (slice_val (pinc f n) (- l n)) opt]))
    (+= n (@polymorphic fmt::SysRender [
        "i"  (slice_val (pinc f n) (- l n)) opt]))
    (return n))


(global test_string (slice u8) "qwerty_1234")

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (let! @ref opt auto (rec_val fmt::SysFormatOptions []))
    (let! buffer auto (array_val fmt::FORMATED_STRING_MAX_LEN u8))
    (let! @ref s (slice! u8) buffer)
    (let! n uint 0)
    (= n (@polymorphic fmt::SysRender [
            666_uint
            s
            (&! opt)]))
    (test::AssertSliceEq# (slice_val (front s) n) "666")
    (= n (@polymorphic fmt::SysRender [
            true
            s
            (&! opt)]))
    (test::AssertSliceEq# (slice_val (front s) n) "true")
    (= n (@polymorphic fmt::SysRender [
            69_u16
            s
            (&! opt)]))
    (test::AssertSliceEq# (slice_val (front s) n) "69")
    (= n (@polymorphic fmt::SysRender [
            -69_s32
            s
            (&! opt)]))
    (test::AssertSliceEq# (slice_val (front s) n) "-69")
    (= n (@polymorphic fmt::SysRender [
            (wrap 120 fmt::rune)
            s
            (&! opt)]))
    (test::AssertSliceEq# (slice_val (front s) n) "x")
    (= n (@polymorphic fmt::SysRender [
            (wrap 2 fmt::r64_hex)
            s
            (&! opt)]))
    (test::AssertSliceEq# (slice_val (front s) n) "0x1.p1")
    (= n (@polymorphic fmt::SysRender [
            color:blue
            s
            (&! opt)]))
    (test::AssertSliceEq# (slice_val (front s) n) "2")
    (= n (@polymorphic fmt::SysRender [
            (rec_val ic32 [(field_val 111) (field_val 222)])
            s
            (&! opt)]))
    (test::AssertSliceEq# (slice_val (front s) n) "111+222i")
    (= n (@polymorphic fmt::SysRender [
            (wrap test_string fmt::str_hex)
            s
            (&! opt)]))
    (test::AssertSliceEq# (slice_val (front s) n) "7177657274795f31323334")
    @doc "test end"
    (test::Success#)
    (return 0))

)
