(module $builtin [] [

(fun pub extern memcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param size uint)] (ptr mut u8) [])
(fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])
(fun pub extern SysErrorPrint [(param buffer (slice u8))] void [])
(fun pub SysPrint [(param buffer (slice u8))] void [
     (stmt (call write [1_s32 (front buffer) (len buffer)]))
])


])


(module string [] [
(# "String Library")

(global pub NOT_FOUND uint (not 0))

(fun are_two_non_empty_strings_the_same [
    (param s1 (ptr u8)) (param s2 (ptr u8)) (param n uint)] bool [
    (let mut i uint 0)
    (block _ [
        (let c1 u8 (^ (incp s1 i)))
        (let c2 u8 (^ (incp s2 i)))
        (if (!= c1 c2) [(return false)] [])
        (+= i 1)
        (if (< i n) [(continue)] [(return true)])
    ])
])

(fun pub find [(param haystack (slice u8)) 
               (param needle (slice u8))] uint [
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== nlen 0) [(return 0)] [])
    (if (< hlen nlen) [(return NOT_FOUND)] [])
    (# "at this point we know that both slices have len > 0")
    (let hptr (ptr u8) (front haystack))
    (let nptr (ptr u8) (front needle))
    (let n uint (- hlen nlen))
    (let mut i uint 0)
    (block _ [
        (if (call are_two_non_empty_strings_the_same [
          (incp hptr i) nptr nlen]) [(return i)] [])
        (+= i 1)
        (if (<= i n) [(continue)] [(return NOT_FOUND)])
    ])
])

(fun pub rfind [(param haystack (slice u8)) 
                (param needle (slice u8))] uint [
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== nlen 0) [(return 0)] [])
    (if (< hlen nlen) [(return NOT_FOUND)] [])
    (# "at this point we know that both slices have len > 0")
    (let hptr (ptr u8) (front haystack))
    (let nptr (ptr u8) (front needle))
    (let mut i uint (- hlen nlen))
    (block _ [
        (if (call are_two_non_empty_strings_the_same [
          (incp hptr i) nptr nlen]) [(return i)] [])
        (if (== i 0) [(return NOT_FOUND)] [])
        (-= i 1)
        (continue)
    ])
])

(fun pub starts_with [(param haystack (slice u8)) 
                      (param needle (slice u8))] bool [
    (let hlen uint (len haystack))
    (let nlen uint (len needle))
    (if (== nlen 0) [(return true)] [])
    (if (< hlen nlen) [(return false)] [])
    (# "at this point we know that both slices have len > 0")
    (return (call are_two_non_empty_strings_the_same [
        (front haystack) (front needle) nlen]))
])

(fun pub ends_with [(param haystack (slice u8)) 
                    (param needle (slice u8))] bool [
    (let hlen uint (len haystack))
    (let nlen uint (len needle))
    (if (== nlen 0) [(return true)] [])
    (if (< hlen nlen) [(return false)] [])
    (# "at this point we know that both slices have len > 0")
    (return (call are_two_non_empty_strings_the_same [
        (incp (front haystack) (- hlen nlen)) (front needle) nlen]))
])

(fun pub cmp [(param aslice (slice u8)) (param bslice (slice u8))] sint [
    (let alen uint (len aslice))
    (let blen uint (len bslice))
    (let n uint (min alen blen))
    (let aptr (ptr u8) (front aslice))
    (let bptr (ptr u8) (front bslice))

    (let mut i uint 0)
    (block _ [
        (if (< i n) [] [(break)])
        (let a u8 (^ (incp aptr i)))
        (let b u8 (^ (incp bptr i)))
        (cond [
            (case (== a b) [(continue)])
            (case (< a b) [(return 1)])
            (case (true) [(return -1)])
        ])
        (+= i 1)
        (continue)
    ])
    (# "the common prefix is the same")
    (cond [
        (case (== alen blen) [(return 0)])
        (case (< alen blen) [(return 1)])
        (case (true) [(return -1)])
    ])
])

(fun contains_char [
    (param haystack (slice u8)) (param needle u8)] bool [
    (# "assumes that haystack is not empty")
    (let n uint (len haystack))
    (let hptr (ptr u8) (front haystack))
    (let mut i uint 0)
    (block _ [
        (if (== needle (^ (incp hptr i))) [(return true)] [])
        (+= i 1)
        (if (< i n) [(continue)] [(return false)])
    ])
])

(fun pub find_first_of [(param haystack (slice u8)) 
                        (param needle (slice u8))] uint [
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== hlen 0) [(return NOT_FOUND)] [])
    (if (== nlen 0) [(return NOT_FOUND)] [])
    (# "at this point we know that both slices have len > 0")
    (let hptr (ptr u8) (front haystack))
    (let mut i uint 0)
    (block _ [
        (if (call contains_char [needle (^ (incp hptr i))]) [(return i)] []) 
        (+= i 1)
        (if (< i hlen) [(continue)] [(return NOT_FOUND)])
    ])
])
 
(fun pub find_first_not_of [(param haystack (slice u8)) 
                            (param needle (slice u8))] uint [
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== hlen 0) [(return NOT_FOUND)] [])
    (if (== nlen 0) [(return 0)] [])
    (# "at this point we know that both slices have len > 0")
    (let hptr (ptr u8) (front haystack))
    (let mut i uint 0)
    (block _ [
        (if (call contains_char [needle (^ (incp hptr i))]) [] [(return i)]) 
        (+= i 1)
        (if (< i hlen) [(continue)] [(return NOT_FOUND)])
    ])
])

(fun pub find_last_of [(param haystack (slice u8)) 
                       (param needle (slice u8))] uint [
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== hlen 0) [(return NOT_FOUND)] [])
    (if (== nlen 0) [(return NOT_FOUND)] [])
    (# "at this point we know that both slices have len > 0")
    (let hptr (ptr u8) (front haystack))
    (let mut i uint hlen)
    (block _ [
        (if (call contains_char [needle (^ (incp hptr i))]) [(return i)] []) 
        (if (== i 0) [(return NOT_FOUND)] [])
        (-= i 1)
        (continue)
    ])
])

(fun pub find_last_not_of [(param haystack (slice u8)) 
                           (param needle (slice u8))] uint [
    (let nlen uint (len needle))
    (let hlen uint (len haystack))
    (if (== hlen 0) [(return NOT_FOUND)] [])
    (if (== nlen 0) [(return NOT_FOUND)] [])
    (# "at this point we know that both slices have len > 0")
    (let hptr (ptr u8) (front haystack))
    (let mut i uint hlen)
    (block _ [
        (if (call contains_char [needle (^ (incp hptr i))]) [] [(return i)]) 
        (if (== i 0) [(return NOT_FOUND)] [])
        (continue)
        (-= i 1)
    ])
])

])




(module test [] [

(# "The two arguments must type derivable")
(macro pub AssertEq [(macro_param $e_expr EXPR) 
                     (macro_param $a_expr EXPR)] [$e_val $a_val] [
    (macro_let $e_val auto $e_expr) 
    (macro_let $a_val auto $a_expr) 
    (if (!= $e_val $a_val) [
        (stmt (call SysPrint ["CheckEq failed: "]))
        (stmt (call SysPrint [(stringify $a_expr)]))
        (stmt (call SysPrint ["\n"]))
        (trap)
    ] []) 
])

])

(module main [] [
(import test)
(import string)

(global STR_ABC auto "ABC")
(global STR_ABCD auto "ABCD")
(global STR_CD auto "CD")
(global STR_XYZ auto "XYZ")
(global STR_VXYZ auto "VXYZ")

(global STR_TEST auto "TEST\n")

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
    (test/AssertEq string/NOT_FOUND (call string/find [STR_ABC STR_ABCD]))
    (test/AssertEq 0_uint (call string/find [STR_ABCD STR_ABC]))
    (test/AssertEq 1_uint (call string/find [STR_VXYZ STR_XYZ]))
    (test/AssertEq 2_uint (call string/find [STR_ABCD STR_CD]))
    (test/AssertEq string/NOT_FOUND (call string/find [STR_XYZ STR_VXYZ]))
    
    (test/AssertEq string/NOT_FOUND (call string/rfind [STR_ABC STR_ABCD]))
    (test/AssertEq 0_uint (call string/rfind [STR_ABCD STR_ABC]))
    (test/AssertEq 1_uint (call string/rfind [STR_VXYZ STR_XYZ]))
    (test/AssertEq 2_uint (call string/rfind [STR_ABCD STR_CD]))
    (test/AssertEq string/NOT_FOUND (call string/find [STR_ABC STR_ABCD]))

    (stmt (call SysPrint ["OK\n"]))
    (return 0)
])


])