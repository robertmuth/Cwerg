@doc  "expr"
(module main [] :
(import test)


(fun test_u32 [(param a u32) (param b u32)] void :
    (test::AssertEq (+ a b) 0x99999999_u32)
    (test::AssertEq (- a b) 0x7530eca9_u32)
    (test::AssertEq (or a b) 0x97755779_u32)
    (test::AssertEq (and a b) 0x02244220_u32)
    (test::AssertEq (xor a b) 0x95511559_u32)
    (test::AssertEq (* a b) 0x70b88d78_u32)
    (test::AssertEq (/ a b) 0x7_u32)
    (test::AssertEq (% a b) 0x7f6e5d9_u32)
    (test::AssertEq (not a) 0x789abcde_u32)
    (test::AssertEq (~ a) 0x789abcdf_u32)

)

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (stmt (call test_u32 [0x87654321 0x12345678]))
    @doc "test end"
    (stmt (call SysPrint ["OK\n"]))
    (return 0))


)