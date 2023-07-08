(module mod1 [] :
(global pub var u32 1)

)


(module mod2 [] :
(global pub var u32 2)

)


(module mod3 [] :
(global pub var u32 3)

)


(module mod4 [] :
(global pub var u32 4)

)


(module mod5 [] :
(global pub var u32 5)

)


(module mod11 [] :
(import mod1)

(global var auto (+ mod1::var 11))

)


(module mod12 [] :
(import mod1)

(import mod2)

(global var auto (+ mod1::var mod2::var))

)


(module mod13 [] :
(import mod2 mod102)

(import mod1)

(global var auto (+ mod1::var mod102::var))

)


(module mod14 [] :
(import mod1)

(global var auto (+ mod1::var 14))

)


(module mod15 [] :
(import mod1)

(global var auto (+ mod1::var 15))

)


(module mod16 [] :
(import mod2)

(import mod1 mod101)

(global var auto (+ mod101::var mod2::var))

)


