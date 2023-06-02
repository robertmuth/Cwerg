(module random [] [
(# "random")


(global IM u32 139968)
(global IA u32 3877)
(global IC u32 29573)
(global mut LAST u32 42)

(fun pub get_random [(param max r64)] r64 [
   (= LAST (% (+ (* LAST IA) IC) IM))
   (return (/ (* max (as LAST r64)) (as IM r64)))
])

])