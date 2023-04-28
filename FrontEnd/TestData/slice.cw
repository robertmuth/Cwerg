(module main [] [
(# "slice")

(fun pub extern memcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param size uint)] (ptr mut u8) [])
(fun pub extern write [(param fd s32) (param s (ptr u8)) (param size uint)] sint [])

(fun mymemcpy [(param dst (ptr mut u8)) (param src (ptr u8)) (param size uint)] uint [
   (stmt (call memcpy [dst src size]))
   (return size)
])

(fun pub write_slice [(param fd s32) (param s (slice u8))] sint [
    (return (call write [fd (front s) (len s)]))
])

(global NEWLINE auto "\n")
(global SPACE auto " ")
(global pub NOT_FOUND uint (not 0))

(fun foo [(param a (slice u8))] (slice u8) [
    (return a) 
])

(fun bar [(param a (slice u8))] (slice u8) [
    (return a) 
])

(# "macro for while-loop")
(macro pub while [(macro_param $cond EXPR) 
                  (macro_param $body STMT_LIST)] [] [
    (block _ [
          (if $cond [] [(break)])
          $body
          (continue)
    ])
])   

(fun strlen [(param s (ptr u8))] uint [
      (let mut i uint 0)
      (while (!= (^ (incp s i)) 0) [
        (+= i 1)
      ])
      (return i)
])

(fun find [(param haystack (slice u8)) (param needle (slice u8))] uint [
    (if (== (len needle) 0) [(return 0)] [])
    (if (< (len haystack) (len needle)) [(return NOT_FOUND)] [])
    (# "at this point we know that both slices have len > 0")
    (let len_needle auto (len needle))
    (let last_i auto (- (len haystack) len_needle))
    (let mut curr_i uint 0)
    (block _ [
        (let mut curr_j uint 0)
        (block _ [
            (if (!= (at haystack (+ curr_i curr_j)) 
                    (at needle curr_j)) [(break)] [])
            (+= curr_j 1)
            (if (< curr_j len_needle) [(continue)] [(return curr_i)])
        ])
        (+= curr_i 1)
        (if (<= curr_i last_i) [(continue)] [(return NOT_FOUND)])
    ])
])

(fun u64_to_str [(param val u64) (param base u64) (param buf (ptr mut u8))] uint [
    (let mut v auto val)
    (let mut ref tmp (array 32 u8) undef)
    (let mut pos uint 32)
    (block _ [
        (-= pos 1)
        (let c auto (% v base))
        (let mut c8 auto (as c u8))
        (+= c8 (? (<= c8 9) '0' (- 'a' 10)))
        (= (at tmp pos) c8)
        (/= v base)
        (if (!= v 0) [(continue)] [])
    ])
    (return (call mymemcpy [buf (& (at tmp pos)) (- 32 pos)]))
])

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
    (let mut ref storage (array 1024 u8) undef)
    (let buffer (slice mut u8) storage)
    (let mut curr auto buffer)
    (= curr storage)
    (stmt (call write_slice [1 "haystack: "]))
    (let arg1 auto (^(incp argv 1)))
    (let haystack auto (slice_val arg1 (call strlen [arg1])))
    (stmt (call write_slice [1 haystack]))
    (stmt (call write_slice [1 NEWLINE]))

    (stmt (call write_slice [1 "needle: "]))
    (let arg2 auto (^(incp argv 2)))
    (let needle auto (slice_val arg2 (call strlen [arg2])))
    (stmt (call write_slice [1 needle]))
    (stmt (call write_slice [1 NEWLINE]))
   
    (stmt (call write_slice [1 "match at: "]))
    (let match uint (call find [haystack needle]))
    (let mut ref buf (array 32 u8) undef)
    (let n auto (call u64_to_str [match 10 (front mut buf)]))
    (stmt (call write [1 (front buf) n]))
    (stmt (call write_slice [1 NEWLINE]))
    (return 0)
])

])

