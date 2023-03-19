(module main [] [

(# "library provided puts style function") 
(fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])

(fun pub write_slice [(param fd s32) (param s (slice u8))] sint [
    (return (call write [fd (front s) (len s)]))
])

(defrec pub type_rec1 [
   (# "this is a comment with \" with quotes \t ")
   (field s1 s32)
   (field s2 s32)
   (field s3 s32)
   (field s4 bool)
   (field s5 u64)
   (field s6 u64)
])


(defrec pub type_rec2 [
    (field t1 bool)
    (field t2 u32)
    (field t3 type_rec1)
    (field t4 bool)
])


(defrec pub type_rec3 [
    (field u2 u16)
    (field u3 u64)
    (field u4 type_rec2)
    (field u5 (array 13 u16))
    (field u6 u64)
])

(defrec pub type_rec4 [
    (field t1 u64)
    (field t2 u8)
    (field t3 u16)
    (field t4 u32)
    (field t5 bool)
])

(global u0 u32 0x12345678)

(global g0 type_rec1 undef)

(global g1 (array 5 type_rec1) undef)

(global g2 auto (rec_val type_rec2 [
      (field_val true t1) 
      (field_val u0 t2)
]))

(global g3 auto (rec_val type_rec3 [
    (field_val 0x1234) 
    (field_val 0x4321) 
    (field_val g2) 
    (field_val 
      (array_val 13 u16 [
        (index_val 0x11) 
        (index_val undef)
        (index_val 0x12)]))
]))

(global g4 auto (array_val 4 type_rec2 [(index_val undef) (index_val g2)]))

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
    (let v1 auto (rec_val type_rec3 []))
    (return 0)
])


])