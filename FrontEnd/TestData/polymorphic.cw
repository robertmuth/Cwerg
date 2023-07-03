(module main [] :
(import test )

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (let mut ref opt auto (rec_val SysFormatOptions []))
    (let mut buffer auto (array_val FORMATED_STRING_MAX_LEN u8 []))
    (let mut ref s (slice mut u8) buffer)
    (let mut n uint 0)
    (= n (call polymorphic SysRender [
            666_uint
            s
            (& mut opt)]))
    (test::AssertSliceEq (slice_val (front s) n) "666")
    (= n (call polymorphic SysRender [
            true
            s
            (& mut opt)]))
    (test::AssertSliceEq (slice_val (front s) n) "true")
    (= n (call polymorphic SysRender [
            69_u16
            s
            (& mut opt)]))
    (test::AssertSliceEq (slice_val (front s) n) "69")
    (print ["OK\n"])
    (return 0))

)


