(module main [] [
(# "slice")

(global NEWLINE auto "\n")
(global SPACE auto " ")
(global pub NOT_FOUND uint (not 0))

(fun foo [(param a (slice u8))] (slice u8) [
    (return a) 
])

(fun bar [(param a (slice u8))] (slice u8) [
    (return a) 
])

(fun find [(param haystack (slice u8)) (param needle (slice u8))] uint [
    (if (== (len needle) 0) [(return 0)] [])
    (if (< (len haystack) (len needle)) [(return NOT_FOUND)] [])
    (# "at this point we know that both slices have len > 0")
    (let last_j auto (len needle))
    (let last_i auto (- (len haystack) last_j))
    (let mut curr_i uint 0)
    (block _ [
        (let mut curr_j uint 0)
        (block _ [
            (if (!= (at haystack (+ curr_i curr_j)) 
                    (at needle curr_j)) [(break)] [])
            (+= curr_j 1)
            (if (< curr_j last_j) [(continue)] [(return curr_i)])
        ])
        (+= curr_i 1)
        (if (< curr_i last_i) [(continue)] [(return NOT_FOUND)])
    ])
])


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
   (let mut ref storage (array 1024 u8) undef)
   (let buffer (slice mut u8) storage)
   (let mut curr auto buffer)
   (= curr storage)
   (return 0)
])

])
