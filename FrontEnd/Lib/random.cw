@doc "random"
(module random [] :
(global IM u32 139968)


(global IA u32 3877)


(global IC u32 29573)


(global @mut LAST u32 42)


(fun @pub get_random [(param max r64)] r64 :
    (= LAST (% (+ (* LAST IA) IC) IM))
    (return (/ (* max (as LAST r64)) (as IM r64))))


@doc "see https://www.pcg-random.org/download.html"
(defrec Pcg32State :
    (field state u64)
    (field inc u64))


(global @pub Pcg32StateDefault auto (rec_val Pcg32State [(field_val 0x853c49e6748fea9b_u64) (field_val 0xda3e39cb94b95bdb_u64)]))


@doc "Generate a uniformly distributed 32-bit random number"
(fun Pcg32GetRandom [(param state (ptr @mut Pcg32State))] u32 :
    (let oldstate u64 (-> state state))
    (= (-> state state) (+ (* oldstate 6364136223846793005_u64) (-> state inc)))
    (let xorshifted u32 (as (>> (xor (>> oldstate 18) oldstate) 27) u32))
    (let rot u32 (as (>> oldstate 59) u32))
    (return (or (>> xorshifted rot) (<< xorshifted (and (- 0 rot) 31)))))

)


