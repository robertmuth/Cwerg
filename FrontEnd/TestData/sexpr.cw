(fun pub foo (TypeFunSig [(FunArg (TypeBase S32) a) (FunArg s32 b) (FunArg s32 c)] s32) [
   (Comment "this is a comment with \" with quotes \t ")
   (StmtExpr (ExprCall (Id [] foo) []))
   (StmtExpr discard (ExprCall foo []))
   (return (ValNum 7 S32)) 
])

(type wrapped cool s32)



(type pub type_rec (TypeRec [
   (# "this is a comment with \" with quotes \t ")
   (field s1 s32 (ValNum 7 S32))
   (field s2 s32 (ValUndef S32))
   (field s3 s32 (ValUndef S32))
   (field s3 s32 undef_s32)

   (field b1 bool false)
   (field u1 u64 666)
   (field u2 u64 666_u64)
]))


(type  type_ptr (ptr mut s32))

(type pub type_union (TypeSum [s32 void type_ptr]))


(fun foo (TypeFunSig [(FunArg (TypeBase S32) a) (FunArg s32 b) (FunArg s32 c)] s32) [
   (# "this is a comment with \" with quotes \t ")
    (if (Expr2 LE  a b) 
    []
    [])
   (if (<=  a b) 
    []
    [])
   (return (ValNum 7 S32)) 
])