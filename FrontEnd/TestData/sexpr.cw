(DefFun foo t (TypeFunSig [(FunArg (TypeBase S32) a) (FunArg s32 b) (FunArg s32 c)] s32) [
   (Comment "this is a comment with \" with quotes \t ")
   (StmtExpr (ExprCall (Id [] foo) []) true)
   (StmtExpr (ExprCall foo []) true)
   (StmtReturn (ValNum 7 S32)) 
])

(DefType cool f t s32)



(DefType cool f t (TypeRec [
   (Comment "this is a comment with \" with quotes \t ")
   (RecField f1 s32 (ValNum 7 S32))
   (RecField f2 s32 (ValUndef S32))
]))
