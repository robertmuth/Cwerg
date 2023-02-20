(module main [] [
(# "slice")

(global NEWLINE auto "\n")
(global SPACE auto " ")
(global pub NOT_FOUND uint (not 0))

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 [
   (let mut ref storage (array 1024 u8) undef)
   (let buffer (slice mut u8) storage)
   (let mut curr auto buffer)
   (= curr storage)
   (return 0)
])

])
