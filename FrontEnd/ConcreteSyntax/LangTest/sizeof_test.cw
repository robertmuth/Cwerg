module:

static_assert sizeof(u8) == 1_uint

static_assert sizeof(s16) == 2

static_assert sizeof(r32) == 4

static_assert sizeof(r64) == 8

-- assuming 64 bit pointers
static_assert sizeof(^u8) == 8

static_assert sizeof(^r64) == 8

static_assert sizeof(^^s64) == 8

static_assert sizeof([20]r64) == 160

static_assert sizeof(slice(r64)) == 16

@pub rec type_rec:
    s1 s32
    s2 s32
    s3 s32
    s4 s32
    b1 bool
    u1 u64
    u2 u64

static_assert sizeof(type_rec) == 40

static_assert offsetof(type_rec, s1) == 0

static_assert offsetof(type_rec, b1) == 16

static_assert offsetof(type_rec, u1) == 24

@pub enum type_enum s32:
    e1 7
    e2 auto
    e3 19
    e4 auto

static_assert sizeof(type_enum) == 4

@wrapped type w1 = s32

@wrapped type w2 = void

@wrapped type w3 = void

type ptr1 = ^!s32

@pub type sum1 = union(bool, u8)

static_assert sizeof(sum1) == 3

@pub type sum2 = union(bool, s32, s64)

static_assert sizeof(sum2) == 16

@pub type sum3 = union(bool, w3)

static_assert sizeof(sum3) == 3

@pub type sum4 = union(ptr1, w3)

-- 8 with union optimization
static_assert sizeof(sum4) == 16

@pub type sum5 = union(ptr1, w2, w3)

-- 8 with union optimization
static_assert sizeof(sum5) == 16

@pub type sum6 = union(ptr1, w1, w2, w3)

static_assert sizeof(sum6) == 16

-- just a compilation test
@cdecl fun main(argc s32, argv ^^u8) s32:
    return 0
