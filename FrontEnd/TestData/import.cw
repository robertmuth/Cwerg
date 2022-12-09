(defmod std [] [
    (# "File StdLib bindings")

    (type pub wrapped errorOpen void)
    (type pub wrapped errorClose void)
    (type pub wrapped errorRead void)
    (type pub wrapped errorWrite void)
    (type pub errorIO (union [errorOpen errorClose errorRead errorWrite]))
 
    (defenum pub Mode U32 [
        (entry r 1)
        (entry w 2)
        (entry rw 3)])

    (type pub fileHandle s32)
    
    (const pub stdin fileHandle 0)
    (const pub stdout fileHandle 1)
    (const pub stderr fileHandle 2)


    (fun pub extern open 
        [(param fname (slice u8)) (param mode Mode)] (union [fileHandle errorOpen]) [])
    (fun pub extern read 
        [(param fp fileHandle) (param buffer (slice mut u8))] (union [u64 errorRead]) [])
    (fun pub extern write
        [(param fp fileHandle) (param buffer (slice u8))] (union [u64 errorWrite]) [])
    (fun pub extern close 
        [(param fp fileHandle)] (union [void errorClose]) [])
])


(defmod main [] [
    (import std)
    (fun main [(param argc u32) (param argv (ptr (ptr u8)))] s32 [
        (stmt discard (call std/write [std/stdout "hello world\n"]))
        (return 0)
    ])
])