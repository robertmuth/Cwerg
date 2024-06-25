@doc "expr"
(module [] :

(fun assoc1 [
        (param a u32)
        (param b u32)
        (param c u32)
        (param d u32)] u32 :
    (return (+ (- (+ a b) c) d)))


(fun assoc2 [
        (param a u32)
        (param b u32)
        (param c u32)
        (param d u32)] u32 :
    (return (* (+ a b) (+ c d))))


(fun assoc3 [
        (param a u32)
        (param b u32)
        (param c u32)
        (param d u32)] u32 :
    (return (max (min a b) (min c d))))


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (return 0))
)

