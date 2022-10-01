(fun foo t (TypeFunSig [(FunArg (TypeBase S32) a) (FunArg s32 b) (FunArg s32 c)] s32) [
   (Comment "this is a comment with \" with quotes \t ")
   (StmtExpr (ExprCall (Id [] foo) []) true)
   (StmtExpr (ExprCall foo []) true)
   (return (ValNum 7 S32)) 
])

(type cool s32 f t)



(type type_rec (TypeRec [
   (# "this is a comment with \" with quotes \t ")
   (RecField s1 s32 (ValNum 7 S32))
   (RecField s2 s32 (ValUndef S32))
   (RecField s3 s32 (ValUndef S32))
   (RecField s3 s32 undef_s32)

   (RecField b1 bool false)
   (RecField u1 u64 666)
   (RecField u2 u64 666_u64)
]) f t)


(type  type_ptr (TypePtr s32 t) f t)

(type type_union (TypeSum [s32 void type_ptr]) f t)


(DefFun foo t (TypeFunSig [(FunArg (TypeBase S32) a) (FunArg s32 b) (FunArg s32 c)] s32) [
   (# "this is a comment with \" with quotes \t ")
    (if (Expr2 LE  a b) 
    []
    [])
   (if (<=  a b) 
    []
    [])
   (return (ValNum 7 S32)) 
])