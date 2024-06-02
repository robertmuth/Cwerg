(module m1 [] :

@pub (fun foo1 [
        (param a s32)
        (param b s32)
        (param c s32)] s32 :
    (shed (foo1 [0 0 0]))
    (shed (foo2 [1 2 3]))
    (return 7))


@pub (global! v1 auto 7_u64)


@pub (global v1a auto (&! v1))


(fun foo2 [
        (param a s32)
        (param b s32)
        (param c s32)] s32 :
    (if (<= a b) :
        (= (^ v1a) 666)
     :)
    (if (! (<= a b)) :
        (+= v1 666)
     :)
    (return 7))


(@wrapped type t1 s32)


@pub (global c1 auto 7_s64)


@pub (defrec type_rec :
    (field s1 s32)
    (field s2 s32)
    (field s3 s32)
    (field s4 s32)
    (field b1 bool)
    (field u1 u64)
    (field u2 u64))


@pub (defrec one_field_rec :
    (field the_field r32))


@pub (defrec one_one_field_rec :
    (field the_field one_field_rec))


(global c2 auto (offsetof type_rec s1))


@pub (enum type_enum S32 :
    (entry s1 7)
    (entry s2)
    (entry s3 19)
    (entry s4))


(type type_ptr (ptr! s32))


@pub (type type_union (union [s32 void type_ptr]))


(fun foo3 [
        (param a bool)
        (param b bool)
        (param c s32)] bool :
    (if (and a b) :
        (return a)
     :
        (return (xor a b)))
    (if (<= a b) :
     :)
    (return (== a b)))


(fun foo4 [
        (param a s32)
        (param b s32)
        (param c s32)] (ptr u8) :
    (let p1 (ptr u8) undef)
    (let p2 (ptr u8) undef)
    (if (== p1 p2) :
     :)
    (let p3 auto (? false p1 p2))
    (block my_block :
        (break)
        (continue)
        (break)
        (continue))
    (return p1))


(fun foo5 [(param c s32)] bool :
    (return (< c (expr :
        (return 6)))))


(fun foo6 [(param c s32)] s32 :
    (return (* 55_s32 (+ c 44))))


(fun square [(param c s32)] s32 :
    (return (* c c)))


(fun double [(param c s32)] s32 :
    (return (+ c c)))


(fun square_or_double [(param use_square bool) (param c s32)] s32 :
    (let foo auto (? use_square square double))
    (return (foo [c])))
)

