module:

@pub rec MyRec:
    s1 s32
    s2 u32
    s3 u32

fun foo(p1 u8, p2 MyRec, p3 bool, p4 MyRec) MyRec:
    return p3 ? p2 : p4

fun bar(p1 bool, p2 MyRec, p3 MyRec) MyRec:
    return foo('c', p2, p1, p3)
