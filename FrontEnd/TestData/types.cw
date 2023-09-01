(module m1 [] :
(type @wrapped t1 s32)


(type @wrapped t2 void)


(type @wrapped t3 void)


(defrec @pub type_rec :
    @doc "this is a comment with \" with quotes \t"
    (field s1 s32)
    (field s2 s32)
    (field s3 s32)
    (field s4 s32)
    (field b1 bool)
    (field u1 u64)
    (field u2 u64))


(defrec @pub linked_list :
    @doc "this is a comment with \" with quotes \t "
    (field s1 (union [void (ptr linked_list)])))


(enum @pub type_enum S32 :
    @doc "this is a comment with \" with quotes \t "
    (entry s1)
    (entry s2)
    (entry s3)
    (entry s4))


(type type_array (array 3 bool))


(type type_slice (slice type_rec))


(type type_ptr (ptr @mut s32))


(type @pub type_union (union [
        s32
        void
        type_ptr]))


(type @pub type_union2 (union [
        s32
        void
        (union [type_union u8])]))


(type type_fun (sig [
        (param a bool)
        (param b bool)
        (param c s32)] s32))


(fun funx [(param a type_union)] s32 :
    (return (as a (sumdelta type_union (union [void type_ptr])))))

)


