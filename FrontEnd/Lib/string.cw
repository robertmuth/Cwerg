@doc "String Library"
(module string [] :

(global @pub NOT_FOUND uint (! 0))


(fun are_two_non_empty_strings_the_same [
        (param s1 (ptr u8))
        (param s2 (ptr u8))
        (param n uint)] bool :
    (let @mut i uint 0)
    (block _ :
        (let c1 u8 (^ (&+ s1 i)))
        (let c2 u8 (^ (&+ s2 i)))
        (if (!= c1 c2) :
            (return false)
            :)
        (+= i 1)
        (if (< i n) :
            (continue)
            :
            (return true))))


(fun @pub find [(param haystack (slice u8)) (param needle (slice u8))] uint :
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
    (let @mut i uint 0)
    (block _ :
        (if (are_two_non_empty_strings_the_same [
                (&+ hptr i)
                nptr
                nlen]) :
            (return i)
            :)
        (+= i 1)
        (if (<= i n) :
            (continue)
            :
            (return NOT_FOUND))))


(fun @pub rfind [(param haystack (slice u8)) (param needle (slice u8))] uint :
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
    (let @mut i uint (- hlen nlen))
    (block _ :
        (if (are_two_non_empty_strings_the_same [
                (&+ hptr i)
                nptr
                nlen]) :
            (return i)
            :)
        (if (== i 0) :
            (return NOT_FOUND)
            :)
        (-= i 1)
        (continue)))


(fun @pub starts_with [(param haystack (slice u8)) (param needle (slice u8))] bool :
    (let hlen uint (len haystack))
    (let nlen uint (len needle))
    (if (== nlen 0) :
        (return true)
        :)
    (if (< hlen nlen) :
        (return false)
        :)
    @doc "at this point we know that both slices have len > 0"
    (return (are_two_non_empty_strings_the_same [
            (front haystack)
            (front needle)
            nlen])))


(fun @pub ends_with [(param haystack (slice u8)) (param needle (slice u8))] bool :
    (let hlen uint (len haystack))
    (let nlen uint (len needle))
    (if (== nlen 0) :
        (return true)
        :)
    (if (< hlen nlen) :
        (return false)
        :)
    @doc "at this point we know that both slices have len > 0"
    (return (are_two_non_empty_strings_the_same [
            (&+ (front haystack) (- hlen nlen))
            (front needle)
            nlen])))


(fun @pub cmp [(param aslice (slice u8)) (param bslice (slice u8))] sint :
    (let alen uint (len aslice))
    (let blen uint (len bslice))
    (let n uint (min alen blen))
    (let aptr (ptr u8) (front aslice))
    (let bptr (ptr u8) (front bslice))
    (let @mut i uint 0)
    (block _ :
        (if (< i n) :
            :
            (break))
        (let a u8 (^ (&+ aptr i)))
        (let b u8 (^ (&+ bptr i)))
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
    (let @mut i uint 0)
    (block _ :
        (if (== needle (^ (&+ hptr i))) :
            (return true)
            :)
        (+= i 1)
        (if (< i n) :
            (continue)
            :
            (return false))))


(fun @pub find_first_of [(param haystack (slice u8)) (param needle (slice u8))] uint :
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
    (let @mut i uint 0)
    (block _ :
        (if (contains_char [needle (^ (&+ hptr i))]) :
            (return i)
            :)
        (+= i 1)
        (if (< i hlen) :
            (continue)
            :
            (return NOT_FOUND))))


(fun @pub find_first_not_of [(param haystack (slice u8)) (param needle (slice u8))] uint :
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
    (let @mut i uint 0)
    (block _ :
        (if (contains_char [needle (^ (&+ hptr i))]) :
            :
            (return i))
        (+= i 1)
        (if (< i hlen) :
            (continue)
            :
            (return NOT_FOUND))))


(fun @pub find_last_of [(param haystack (slice u8)) (param needle (slice u8))] uint :
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
    (let @mut i uint hlen)
    (block _ :
        (-= i 1)
        (if (contains_char [needle (^ (&+ hptr i))]) :
            (return i)
            :)
        (if (== i 0) :
            (return NOT_FOUND)
            :)
        (continue)))


(fun @pub find_last_not_of [(param haystack (slice u8)) (param needle (slice u8))] uint :
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
    (let @mut i uint hlen)
    (block _ :
        (-= i 1)
        (if (contains_char [needle (^ (&+ hptr i))]) :
            :
            (return i))
        (if (== i 0) :
            (return NOT_FOUND)
            :)
        (continue)))
)

