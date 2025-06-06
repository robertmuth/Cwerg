module:

static_assert 3_s32 + 4 == 7

global a1 u32 = 7

static_assert a1 == 7

global a2 u32

static_assert a2 == 0

global a3 s32 = -1

static_assert a3 == -1

global a4 s32

static_assert a4 == 0

global a5 r32 = 1.0_r32

static_assert a5 == 1.0_r32

global a6 r32

static_assert a6 == 0.0_r32

global a7 bool = true

static_assert a7 == true

global a8 bool

static_assert a8 == false

global c0 void = void_val

global c1 = 7_u32

ref global c2 u32 = 7

global c3 = 7.0_r32

global c4 = "axxxxb"

global c4_span span(u8) = c4
static_assert len(c4) == 6
; static_assert len(c4_span) == 6
; static_assert len(c4_span) == len(c4)

static_assert c4[0] == 'a'
static_assert size_of(type_of(c4)) == 6
static_assert c4[size_of(type_of(c4)) - 1] == 'b'

ref global c10 = c2

pub rec type_rec:
    s1 s32
    s2 s32
    s3 s32
    s4 s32
    b1 bool
    u1 u64
    u2 u64

; rec literal with explicit field name
ref global c32 = {type_rec: 7, 9, 7}

static_assert c32.s1 == 7

static_assert c32.s2 == 9

static_assert c32.s3 == 7

static_assert c32.s4 == 0

static_assert c32.b1 == false

static_assert @c32 == @c32

static_assert @c2 != @c10

pub enum type_enum s32:
    e1 7
    e2 auto_val
    e3 19
    e4 auto_val

global c20 = type_enum:e3

static_assert unwrap(c20) == 19

global c41 = c32.s1

static_assert c41 == 7

; array literal with explicit indices
global c30 = {[30]uint: 1 = 0, 2 = 10, 3 = 20}

global c40 = c30[1]

static_assert c40 == 0

; array literal
global c31 = {[30]uint: 10, 20, 30}

; rec literal
global c33 = {type_rec: 7, 9, 7}

static_assert c33.s1 == 7

pub rec type_rec2:
    s1 span(u8)
    s2 s32
    s3 s32

; rec literal
global r01 = {type_rec2: "aaa", 9, 7}

; rec literal
global r02 = {type_rec2: s2 = 9, 7}

static_assert len(r02.s1) == 0

global auto1 s32

static_assert auto1 == 0

global auto2 bool

static_assert auto2 == false

global auto3 r64

static_assert auto3 == 0.0

global auto4 type_rec2

static_assert is(auto4, type_rec2) == true

static_assert is(auto4, s32) != true

static_assert is(a8, s32) != true

static_assert is(a8, bool) == true

ref global! Real r32

global p1 ^r32 = @Real

global p2 ^!r32 = @!Real

static_assert is(p1, bool) == false

static_assert is(p1, ^!r32) == false

static_assert is(p1, ^r32) == true

fun foo(x u16) u16:
    return x

static_assert foo == foo

static_assert @Real == @Real

; just a compilation test
fun main(argc s32, argv ^^u8) s32:
    return 0
