(defmod m1 [] [

(defun pub foo1 [(param a (TypeBase S32)) (param b s32) (param c s32)] s32 [
   (Comment "this is a comment with \" with quotes \t ")
   (StmtExpr discard (ExprCall (Id foo1) [0 0 0]))
   (StmtExpr discard (ExprCall foo2 [1 2 3]))
   (return (ValNum 7)) 
])

(let pub v1 auto 7_u64)

(let pub v1a auto (& v1))

(defun foo2 [(param a (TypeBase S32)) (param b s32) (param c s32)] s32 [
   (# "this is a comment with \" with quotes \t ")
    (if (Expr2 LE  a b) 
    [(= (^ v1a) 666)]
    [])
   (if (!(<=  a b)) 
    [(+= v1 666)]
    [])
   (return (ValNum 7)) 
])

(deftype wrapped t1 s32)

(const pub c1 auto 7_s64)


(defrec pub type_rec [
   (# "this is a comment with \" with quotes \t ")
   (field s1 s32 (ValNum 7))
   (field s2 s32 (ValUndef))
   (field s3 s32 (ValUndef))
   (field s3 s32 undef)

   (field b1 bool false)
   (field u1 u64 666)
   (field u2 u64 666_u64)
])


(const c2 auto (offsetof type_rec s1))

(defenum pub type_enum S32 [
   (# "this is a comment with \" with quotes \t ")
   (entry s1 (ValNum 7))
   (entry s2)
   (entry s3 19)
   (entry s4)
])

])

(defmod m2 [] [

(deftype  type_ptr (ptr mut s32))

(deftype pub type_union (TypeSum [s32 void type_ptr]))




(defun foo3 [(param a bool) (param b bool) (param c s32)] bool [
   (# "this is a comment with \" with quotes \t ")
   (if (and a b) 
    [(return a)]
    [(return (xor a b))])
   (if (<=  a b) 
    []
    [])
   (return (== a b)) 
])


(defun foo [(param a s32) (param b s32) (param c s32)] (ptr u8) [
   (# "this is a comment with \" with quotes \t ")
   (let p1 (ptr u8) undef)
   (let p2 (ptr u8) undef)
   (if (== p1 p2) [] [])
   (let p3 auto (? false p1 p2))
   (block my_block [
      (# "this is a comment with \" with quotes \t ")
      (break)
      (continue)
      (break my_block)
      (continue my_block)
    ])
   (return p1) 
])


])