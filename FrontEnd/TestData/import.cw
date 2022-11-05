(defmod std [] [
    (# "File StdLib bindings")

    (deftype pub wrapped errorOpen void)
    (deftype pub wrapped errorClose void)
    (deftype pub wrapped errorRead void)
    (deftype pub wrapped errorWrite void)
    (deftype pub errorIO (union [errorOpen errorClose errorRead errorWrite]))
 
    (defenum pub Mode U32 [
        (entry r 1)
        (entry w 2)
        (entry rw 3)])

    (deftype pub fileHandle s32)
    
    (const stdin fileHandle 0)
    (const stdout fileHandle 1)
    (const stderr fileHandle 2)


    (defun pub extern open 
        [(param fname (slice u8)) (param mode Mode)] (union [fileHandle errorOpen]) [])
    (defun pub extern read 
        [(param fp fileHandle) (param buffer (slice mut u8))] (union [u64 errorRead]) [])
    (defun pub extern write
        [(param fp fileHandle) (param buffer (slice u8))] (union [u64 errorWrite]) [])
    (defun pub extern close 
        [(param fp fileHandle)] (union [void errorClose]) [])
])


(defmod main [] [
    (import std)
    (defun main [(param argc u32) (param argv (ptr (ptr u8)))] s32 [
        (expr discard (call std/write [std/stdout "hello world\n"]))
        (return 0)
    ])
])