(defmod mod1 [] [    
    (let var u32 1)
])


(defmod mod2 [] [    
    (let var u32 2)
])

(defmod mod3 [] [    
    (let var u32 3)
])

(defmod mod4 [] [    
    (let var u32 4)
])

(defmod mod5 [] [    
    (let var u32 5)
])



(defmod mod11 [] [    
    (import mod1)
    (let var auto (+ mod1/var 11))
])

(defmod mod12 [] [    
    (import mod1)
    (import mod2)
    (let var auto (+ mod1/var mod2/var))
])

(defmod mod13 [] [    
    (import mod2 mod102)
    (import mod1)
    (let var auto (+ mod1/var mod102/var))
])

(defmod mod14 [] [    
    (import mod1)
    (let var auto (+ mod1/var 14))
])

(defmod mod15 [] [    
    (import mod1)
    (let var auto (+ mod1/var 15))
])

(defmod mod16 [] [    
    (import mod2)
    (import mod1 mod101)
    (let var auto (+ mod101/var mod2/var))
])