(module main [] :
(import test)

(enum @pub enum8 U8 :
    (entry e1 7)
    (entry e2)
    (entry e3 19)
    (entry e4))

(enum @pub enum16 U16 :
    (entry e1 70)
    (entry e2)
    (entry e3 190)
    (entry e4))

(enum @pub enum32 U32 :
    (entry e1 700)
    (entry e2)
    (entry e3 1900)
    (entry e4))

@doc "GLOBAL"
(global @mut g1 auto enum8::e1)
(global @mut g2 auto enum16::e2)
(global @mut g3 auto enum32::e3)


(defrec @pub rec1 :
    @doc "this is a comment with \" with quotes \t "
    (field s1 s32)
    (field s2 s32)
    (field s3 s32)
    (field s4 bool)
    (field s5 enum8)
    (field s6 enum16)
    (field s7 enum32)
    (field s8 u64)
    (field s9 u64))

(global @mut gr1 rec1 undef)

(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "LOCAL"
    (let @mut v1 auto enum8::e2)
    (let @mut v2 auto enum16::e3)
    (let @mut v3 auto enum32::e4)
    
    (test::AssertEq! g1 enum8::e1)
    (test::AssertEq! g2 enum16::e2)
    (test::AssertEq! g3 enum32::e3)

    (= g1 v1)
    (= g2 v2)
    (= g3 v3)

    (test::AssertEq! g1 enum8::e2)
    (test::AssertEq! g2 enum16::e3)
    (test::AssertEq! g3 enum32::e4)
    
    (= v1 enum8::e3)
    (= v2 enum16::e4)
    (= v3 enum32::e1)

    (test::AssertEq! v1 enum8::e3)
    (test::AssertEq! v2 enum16::e4)
    (test::AssertEq! v3 enum32::e1)

    (= (. gr1 s5) enum8::e3)
    (= (. gr1 s6) enum16::e4)
    (= (. gr1 s7) enum32::e1)
    
    (test::AssertEq! (. gr1 s5) enum8::e3)
    (test::AssertEq! (. gr1 s6) enum16::e4)
    (test::AssertEq! (. gr1 s7) enum32::e1)

    @doc "test end"
    (test::Success!)
    (return 0))

)