@doc "module"
(module [] :

@pub (defrec type_rec2 :
    (field s1 (slice u8))
    @doc "field comment"
    (field s2 s32)
    (field s3 s32))


@doc "global with rec literal"
(global r02 auto (rec_val type_rec2 [
        (field_val 9 s2)
        @doc "field_val comment"
        (field_val 7)]))


@doc "enum decl"
(enum type_enum S32 :
    @doc "enum entry comment"
    (entry e1 7)
    (entry e2)
    (entry e3 19)
    (entry e4))


(global c31 auto (array_val 30 uint [
        10
        @doc "index_val"
        (index_val 20)
        30]))


@doc "fun"
(fun main [
        (param argc s32)
        @doc "param"
        (param argv (ptr (ptr u8)))] s32 :
    (let! loc11 auto (array_val 30 uint [
            10
            @doc "index_val"
            (index_val 20)
            30]))
    (let! loc22 auto (rec_val type_rec2 [
            (field_val 9 s2)
            @doc "field_val comment"
            (field_val 7)]))
    @doc "cond"
    (cond :
        @doc "in block"
        (case (== (% argc 15) 0) :
            @doc "in block"
            (return 1))
        @doc "in another block2"
        (case (== (% argc 3) 0) :
            (return 2))
        (case (== (% argc 5) 0) :
            (return 3))
        (case true :
            (return 4)))
    (return 0))
)
