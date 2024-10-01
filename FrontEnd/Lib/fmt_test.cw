(module [] :
(import test)

(import fmt)


@pub (enum color S32 :
    (entry black 0)
    (entry white 1)
    (entry blue 2)
    (entry green 3)
    (entry red 4))


(fun fmt::SysRender@ [
        (param v color)
        (param out (slice! u8))
        (param options (ptr! fmt::SysFormatOptions))] uint :
    (return (fmt::SysRender@ [(unwrap v) out options])))


@pub (defrec ic32 :
    (field real s32)
    (field imag s32))


(fun fmt::SysRender@ [
        (param v ic32)
        (param s (slice! u8))
        (param opt (ptr! fmt::SysFormatOptions))] uint :
    (let f auto (front! s))
    (let l auto (len s))
    (let! n uint 0)
    (= n (fmt::SysRender@ [(. v real) s opt]))
    (+= n (fmt::SysRender@ ["+" (span_val (pinc f n) (- l n)) opt]))
    (+= n (fmt::SysRender@ [(. v imag) (span_val (pinc f n) (- l n)) opt]))
    (+= n (fmt::SysRender@ ["i" (span_val (pinc f n) (- l n)) opt]))
    (return n))


(global test_string (slice u8) "qwerty_1234")


(fun test_custom [] void :
    (@ref let! opt auto (rec_val fmt::SysFormatOptions []))
    (let! buffer auto (vec_val fmt::FORMATED_STRING_MAX_LEN u8))
    (@ref let! s (slice! u8) buffer)
    (let! n uint 0)
    @doc "complex"
    (= n (fmt::SysRender@ [
            (rec_val ic32 [111 222])
            s
            (&! opt)]))
    (test::AssertSliceEq# (span_val (front s) n) "111+222i")
    @doc "enum"
    (= n (fmt::SysRender@ [color:blue s (&! opt)]))
    (test::AssertSliceEq# (span_val (front s) n) "2")
)

(fun test_int [] void :
    (@ref let! opt auto (rec_val fmt::SysFormatOptions []))
    (let! buffer auto (vec_val fmt::FORMATED_STRING_MAX_LEN u8))
    (@ref let! s (slice! u8) buffer)
    (let! n uint 0)
    (= n (fmt::SysRender@ [666_uint s (&! opt)]))
    (test::AssertSliceEq# (span_val (front s) n) "666")
    (= n (fmt::SysRender@ [69_u16 s (&! opt)]))
    (test::AssertSliceEq# (span_val (front s) n) "69")
    (= n (fmt::SysRender@ [-69_s32 s (&! opt)]))
    (test::AssertSliceEq# (span_val (front s) n) "-69")
)

(fun test_real [] void :
    (@ref let! opt auto (rec_val fmt::SysFormatOptions []))
    (let! buffer auto (vec_val fmt::FORMATED_STRING_MAX_LEN u8))
    (@ref let! s (slice! u8) buffer)
    (let! n uint 0)
    (= n (fmt::SysRender@ [(wrap_as 2 fmt::r64_hex) s (&! opt)]))
    @doc """(fmt::print# s " \n")"""
    (test::AssertSliceEq# (span_val (front s) n) "0x1.p+1")

    (= n (fmt::SysRender@ [666e+20_r64 s (&! opt)]))
    (test::AssertSliceEq# (span_val (front s) n) "6.660000e+22")
)

(fun test_misc [] void :
    (@ref let! opt auto (rec_val fmt::SysFormatOptions []))
    (let! buffer auto (vec_val fmt::FORMATED_STRING_MAX_LEN u8))
    (@ref let! s (slice! u8) buffer)
    (let! n uint 0)
    (= n (fmt::SysRender@ [true s (&! opt)]))
    (test::AssertSliceEq# (span_val (front s) n) "true")

    (= n (fmt::SysRender@ [(wrap_as 120 fmt::rune) s (&! opt)]))
    (test::AssertSliceEq# (span_val (front s) n) "x")

    (= n (fmt::SysRender@ [(wrap_as test_string fmt::str_hex) s (&! opt)]))
    (test::AssertSliceEq# (span_val (front s) n) "7177657274795f31323334")
)

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (do (test_int []))
    (do (test_misc []))
    (do (test_custom []))
    (do (test_real []))
    @doc "test end"
    (test::Success#)
    (return 0))
)
