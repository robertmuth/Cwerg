@doc "String Library"
(module [] :

@pub (global NOT_FOUND uint (! 0))


(fun are_two_non_empty_strings_the_same [
        (param s1 (ptr u8))
        (param s2 (ptr u8))
        (param n uint)] bool :
    (let! i uint 0)
    (block _ :
        (let c1 u8 (^ (pinc s1 i)))
        (let c2 u8 (^ (pinc s2 i)))
        (if (!= c1 c2) :
            (return false)
         :)
        (+= i 1)
        (if (< i n) :
            (continue)
         :
            (return true))))


@pub (fun find [(param haystack (slice u8)) (param needle (slice u8))] uint :
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== nlen 0) :
        (return 0)
     :)
    (if (< hlen nlen) :
        (return NOT_FOUND)
     :)
    @doc "at this point we know that both slices have len > 0"
    (let hptr (ptr u8) (front haystack))
    (let nptr (ptr u8) (front needle))
    (let n uint (- hlen nlen))
    (let! i uint 0)
    (block _ :
        (if (are_two_non_empty_strings_the_same [(pinc hptr i) nptr nlen]) :
            (return i)
         :)
        (+= i 1)
        (if (<= i n) :
            (continue)
         :
            (return NOT_FOUND))))


@pub (fun rfind [(param haystack (slice u8)) (param needle (slice u8))] uint :
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== nlen 0) :
        (return 0)
     :)
    (if (< hlen nlen) :
        (return NOT_FOUND)
     :)
    @doc "at this point we know that both slices have len > 0"
    (let hptr (ptr u8) (front haystack))
    (let nptr (ptr u8) (front needle))
    (let! i uint (- hlen nlen))
    (block _ :
        (if (are_two_non_empty_strings_the_same [(pinc hptr i) nptr nlen]) :
            (return i)
         :)
        (if (== i 0) :
            (return NOT_FOUND)
         :)
        (-= i 1)
        (continue)))


@pub (fun starts_with [(param haystack (slice u8)) (param needle (slice u8))] bool :
    (let hlen uint (len haystack))
    (let nlen uint (len needle))
    (if (== nlen 0) :
        (return true)
     :)
    (if (< hlen nlen) :
        (return false)
     :)
    @doc "at this point we know that both slices have len > 0"
    (return (are_two_non_empty_strings_the_same [(front haystack) (front needle) nlen])))


@pub (fun ends_with [(param haystack (slice u8)) (param needle (slice u8))] bool :
    (let hlen uint (len haystack))
    (let nlen uint (len needle))
    (if (== nlen 0) :
        (return true)
     :)
    (if (< hlen nlen) :
        (return false)
     :)
    @doc "at this point we know that both slices have len > 0"
    (return (are_two_non_empty_strings_the_same [(pinc (front haystack) (- hlen nlen)) (front needle) nlen])))


@pub (fun cmp [(param aslice (slice u8)) (param bslice (slice u8))] sint :
    (let alen uint (len aslice))
    (let blen uint (len bslice))
    (let n uint (min alen blen))
    (let aptr (ptr u8) (front aslice))
    (let bptr (ptr u8) (front bslice))
    (let! i uint 0)
    (block _ :
        (if (< i n) :
         :
            (break))
        (let a u8 (^ (pinc aptr i)))
        (let b u8 (^ (pinc bptr i)))
        (cond :
            (case (== a b) :)
            (case (< a b) :
                (return -1))
            (case true :
                (return 1)))
        (+= i 1)
        (continue))
    @doc "the common prefix is the same"
    (cond :
        (case (== alen blen) :
            (return 0))
        (case (< alen blen) :
            (return -1))
        (case true :
            (return 1))))


(fun contains_char [(param haystack (slice u8)) (param needle u8)] bool :
    @doc "assumes that haystack is not empty"
    (let n uint (len haystack))
    (let hptr (ptr u8) (front haystack))
    (let! i uint 0)
    (block _ :
        (if (== needle (^ (pinc hptr i))) :
            (return true)
         :)
        (+= i 1)
        (if (< i n) :
            (continue)
         :
            (return false))))


@pub (fun find_first_of [(param haystack (slice u8)) (param needle (slice u8))] uint :
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== hlen 0) :
        (return NOT_FOUND)
     :)
    (if (== nlen 0) :
        (return NOT_FOUND)
     :)
    @doc "at this point we know that both slices have len > 0"
    (let hptr (ptr u8) (front haystack))
    (let! i uint 0)
    (block _ :
        (if (contains_char [needle (^ (pinc hptr i))]) :
            (return i)
         :)
        (+= i 1)
        (if (< i hlen) :
            (continue)
         :
            (return NOT_FOUND))))


@pub (fun find_first_not_of [(param haystack (slice u8)) (param needle (slice u8))] uint :
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== hlen 0) :
        (return NOT_FOUND)
     :)
    (if (== nlen 0) :
        (return 0)
     :)
    @doc "at this point we know that both slices have len > 0"
    (let hptr (ptr u8) (front haystack))
    (let! i uint 0)
    (block _ :
        (if (contains_char [needle (^ (pinc hptr i))]) :
         :
            (return i))
        (+= i 1)
        (if (< i hlen) :
            (continue)
         :
            (return NOT_FOUND))))


@pub (fun find_last_of [(param haystack (slice u8)) (param needle (slice u8))] uint :
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== hlen 0) :
        (return NOT_FOUND)
     :)
    (if (== nlen 0) :
        (return NOT_FOUND)
     :)
    @doc "at this point we know that both slices have len > 0"
    (let hptr (ptr u8) (front haystack))
    (let! i uint hlen)
    (block _ :
        (-= i 1)
        (if (contains_char [needle (^ (pinc hptr i))]) :
            (return i)
         :)
        (if (== i 0) :
            (return NOT_FOUND)
         :)
        (continue)))


@pub (fun find_last_not_of [(param haystack (slice u8)) (param needle (slice u8))] uint :
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== hlen 0) :
        (return NOT_FOUND)
     :)
    (if (== nlen 0) :
        (return (- hlen 1))
     :)
    @doc "at this point we know that both slices have len > 0"
    (let hptr (ptr u8) (front haystack))
    (let! i uint hlen)
    (block _ :
        (-= i 1)
        (if (contains_char [needle (^ (pinc hptr i))]) :
         :
            (return i))
        (if (== i 0) :
            (return NOT_FOUND)
         :)
        (continue)))
)

