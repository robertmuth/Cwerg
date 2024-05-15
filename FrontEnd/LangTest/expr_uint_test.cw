@doc "expr"
(module main [] :
(import test)


(fun test_u64 [(param a u64) (param b u64)] void :
    (test::AssertEq# (+ a b) 0x9999999999999999_u64)
    (test::AssertEq# (- a b) 0x7530eca97530eca9_u64)
    (test::AssertEq# (max a b) 0x8765432187654321_u64)
    (test::AssertEq# (min a b) 0x1234567812345678_u64)
    (test::AssertEq# (or a b) 0x9775577997755779_u64)
    (test::AssertEq# (and a b) 0x0224422002244220_u64)
    (test::AssertEq# (xor a b) 0x9551155995511559_u64)
    (test::AssertEq# (* a b) 0xeb11e7f570b88d78_u64)
    (test::AssertEq# (/ a b) 0x7_u64)
    (test::AssertEq# (% a b) 0x7f6e5d907f6e5d9_u64)
    @doc ""
    (test::AssertEq# (<< a 0) 0x8765432187654321_u64)
    (test::AssertEq# (<< a 32) 0x8765432100000000_u64)
    (test::AssertEq# (<< a 64) 0x8765432187654321_u64)
    @doc ""
    (test::AssertEq# (>> a 0) 0x8765432187654321_u64)
    (test::AssertEq# (>> a 32) 0x87654321_u64)
    (test::AssertEq# (>> a 64) 0x8765432187654321_u64)
    @doc ""
    (test::AssertEq# (< a b) false)
    (test::AssertEq# (<= a b) false)
    (test::AssertEq# (> a b) true)
    (test::AssertEq# (>= a b) true)
    (test::AssertEq# (== a b) false)
    (test::AssertEq# (!= a b) true)
    @doc ""
    (test::AssertEq# (< a a) false)
    (test::AssertEq# (<= a a) true)
    (test::AssertEq# (> a a) false)
    (test::AssertEq# (>= a a) true)
    (test::AssertEq# (== a a) true)
    (test::AssertEq# (!= a a) false))


(fun test_u32 [(param a u32) (param b u32)] void :
    (test::AssertEq# (+ a b) 0x99999999_u32)
    (test::AssertEq# (- a b) 0x7530eca9_u32)
    (test::AssertEq# (max a b) 0x87654321_u32)
    (test::AssertEq# (min a b) 0x12345678_u32)
    (test::AssertEq# (or a b) 0x97755779_u32)
    (test::AssertEq# (and a b) 0x02244220_u32)
    (test::AssertEq# (xor a b) 0x95511559_u32)
    (test::AssertEq# (* a b) 0x70b88d78_u32)
    (test::AssertEq# (/ a b) 0x7_u32)
    (test::AssertEq# (% a b) 0x7f6e5d9_u32)
    @doc ""
    (test::AssertEq# (! a) 0x789abcde_u32)
    (test::AssertEq# (~ a) 0x789abcdf_u32)
    @doc ""
    (test::AssertEq# (<< a 0) 0x87654321_u32)
    (test::AssertEq# (<< a 16) 0x43210000_u32)
    (test::AssertEq# (<< a 32) 0x87654321_u32)
    @doc ""
    (test::AssertEq# (>> a 0) 0x87654321_u32)
    (test::AssertEq# (>> a 16) 0x8765_u32)
    (test::AssertEq# (>> a 32) 0x87654321_u32)
    @doc ""
    (test::AssertEq# (< a b) false)
    (test::AssertEq# (<= a b) false)
    (test::AssertEq# (> a b) true)
    (test::AssertEq# (>= a b) true)
    (test::AssertEq# (== a b) false)
    (test::AssertEq# (!= a b) true)
    @doc ""
    (test::AssertEq# (< a a) false)
    (test::AssertEq# (<= a a) true)
    (test::AssertEq# (> a a) false)
    (test::AssertEq# (>= a a) true)
    (test::AssertEq# (== a a) true)
    (test::AssertEq# (!= a a) false))


(fun test_u16 [(param a u16) (param b u16)] void :
    (test::AssertEq# (+ a b) 0x5555_u16)
    (test::AssertEq# (- a b) 0x30ed_u16)
    (test::AssertEq# (max a b) 0x4321_u16)
    (test::AssertEq# (min a b) 0x1234_u16)
    (test::AssertEq# (or a b) 0x5335_u16)
    (test::AssertEq# (and a b) 0x0220_u16)
    (test::AssertEq# (xor a b) 0x5115_u16)
    (test::AssertEq# (* a b) 0xf4b4_u16)
    (test::AssertEq# (/ a b) 0x3_u16)
    (test::AssertEq# (% a b) 0xc85_u16)
    @doc ""
    (test::AssertEq# (! a) 0xbcde_u16)
    (test::AssertEq# (~ a) 0xbcdf_u16)
    @doc ""
    (test::AssertEq# (<< a 0) 0x4321_u16)
    (test::AssertEq# (<< a 8) 0x2100_u16)
    (test::AssertEq# (<< a 16) 0x4321_u16)
    @doc ""
    (test::AssertEq# (>> a 0) 0x4321_u16)
    (test::AssertEq# (>> a 8) 0x43_u16)
    (test::AssertEq# (>> a 16) 0x4321_u16)
    @doc ""
    (test::AssertEq# (< a b) false)
    (test::AssertEq# (<= a b) false)
    (test::AssertEq# (> a b) true)
    (test::AssertEq# (>= a b) true)
    (test::AssertEq# (== a b) false)
    (test::AssertEq# (!= a b) true)
    @doc ""
    (test::AssertEq# (< a a) false)
    (test::AssertEq# (<= a a) true)
    (test::AssertEq# (> a a) false)
    (test::AssertEq# (>= a a) true)
    (test::AssertEq# (== a a) true)
    (test::AssertEq# (!= a a) false))


(fun test_u8 [(param a u8) (param b u8)] void :
    (test::AssertEq# (+ a b) 0xff_u8)
    (test::AssertEq# (- a b) 0xf_u8)
    (test::AssertEq# (max a b) 0x87_u8)
    (test::AssertEq# (min a b) 0x78_u8)
    (test::AssertEq# (or a b) 0xff_u8)
    (test::AssertEq# (and a b) 0x0_u8)
    (test::AssertEq# (xor a b) 0xff_u8)
    @doc """ needs backend fixes (test::AssertEq# (* a b) 0x48_u8) """
    (test::AssertEq# (/ a b) 0x1_u8)
    (test::AssertEq# (% a b) 0xf_u8)
    @doc ""
    (test::AssertEq# (! a) 0x78_u8)
    (test::AssertEq# (~ a) 0x79_u8)
    @doc ""
    (test::AssertEq# (<< a 0) 0x87_u8)
    (test::AssertEq# (<< a 32) 0x87_u8)
    (test::AssertEq# (<< a 64) 0x87_u8)
    @doc ""
    (test::AssertEq# (>> a 0) 0x87_u8)
    (test::AssertEq# (>> a 32) 0x87_u8)
    (test::AssertEq# (>> a 64) 0x87_u8)
    @doc ""
    (test::AssertEq# (< a b) false)
    (test::AssertEq# (<= a b) false)
    (test::AssertEq# (> a b) true)
    (test::AssertEq# (>= a b) true)
    (test::AssertEq# (== a b) false)
    (test::AssertEq# (!= a b) true)
    @doc ""
    (test::AssertEq# (< a a) false)
    (test::AssertEq# (<= a a) true)
    (test::AssertEq# (> a a) false)
    (test::AssertEq# (>= a a) true)
    (test::AssertEq# (== a a) true)
    (test::AssertEq# (!= a a) false))


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (shed (test_u64 [0x8765432187654321 0x1234567812345678]))
    (shed (test_u32 [0x87654321 0x12345678]))
    (shed (test_u16 [0x4321 0x1234]))
    (shed (test_u8 [0x87 0x78]))
    @doc "test end"
    (test::Success#)
    (return 0))
)

