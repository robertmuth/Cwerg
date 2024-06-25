(module [] :

(import test)

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

(fun sign1 [(param x s32)] s32 :
  (cond :
    (case (== x 0) : (return 0_s32))
    (case (< x 0) : (return -1_s32))
    (case true : (return 1_s32))))

(fun sign2 [(param x s32)] s32 :
 (let out s32  (expr :
                  (cond :
                    (case (== x 0) : (return 0_s32))
                    (case (< x 0) : (return -1_s32))
                    (case true : (return 1_s32)))))
 (return out))

 (fun sign3 [(param x s32)] s32 :
   (return  (expr :
                  (cond :
                    (case (== x 0) : (return 0_s32))
                    (case (< x 0) : (return -1_s32))
                    (case true : (return 1_s32))))))

@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
  (test::AssertEq# (assoc3 [5 7 1 2]) 5_u32)
   @doc ""
   (test::AssertEq# (sign1 [20]) 1_s32)
   (test::AssertEq# (sign2 [20]) 1_s32)
   (test::AssertEq# (sign3 [20]) 1_s32)
   @doc ""
   (test::AssertEq# (sign1 [0]) 0_s32)
   (test::AssertEq# (sign2 [0]) 0_s32)
   (test::AssertEq# (sign3 [0]) 0_s32)
   @doc ""
   (test::AssertEq# (sign1 [-20]) -1_s32)
   (test::AssertEq# (sign2 [-20]) -1_s32)
   (test::AssertEq# (sign3 [-20]) -1_s32)
    @doc "test end"
    (test::Success#)
    (return 0))
)
