(DefFun foo t (TypeFunSig [(FunArg (TypeBase S32) a) (FunArg s32 b) (FunArg s32 c)] s32) [
   (Comment "this is a comment with \" with quotes \t ")
   (StmtExpr (ExprCall (Id [] foo) []) true)
   (StmtExpr (ExprCall foo []) true)
   (StmtReturn (ValNum 7 S32)) 
])

(DefType cool f t s32)



(DefType cool f t (TypeRec [
   (Comment "this is a comment with \" with quotes \t ")
   (RecField s1 s32 (ValNum 7 S32))
   (RecField s2 s32 (ValUndef S32))
   (RecField s3 s32 (ValUndef S32))
   (RecField s3 s32 undef_s32)

   (RecField b1 bool false)
   (RecField u1 u64 666)
   (RecField u2 u64 666_u64)
]))



