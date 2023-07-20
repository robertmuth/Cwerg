(module m1 [] :

(defrec @pub type_rec2 :
      (field s1 (slice u8))
      (# "field comment")
      (field s2 s32)
      (field s3 s32))


    
  (# "rec literal")
  (global r02 auto (rec_val type_rec2 [
    (field_val 9 s2) 
    (# "field_val comment")
    (field_val 7)]))

(enum @pub type_enum S32 :
      (# "enum_entry")
      (entry e1 7)
      (entry e2)
      (entry e3 19)
      (entry e4))



(global c31 auto (array_val 30 uint [
          (index_val 10)
          (# "index_val")
          (index_val 20)
          (index_val 30)]))


  
  
  (fun main [(param argc s32) 
             (# "param")
             (param argv (ptr (ptr u8)))] s32 :
    (# "in fun")
    (cond :
        (# "in block")
        (case (== (% argc 15) 0) :
            (# "in block")

            (return 1)
            (# "in block2"))
        (case (== (% argc 3) 0) :
            (return 2))
        (case (== (% argc 5) 0) :
            (return 3))
        (case true :
            (return 4)))
      (return 0))

(# "eom"))