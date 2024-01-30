@doc "Macro Examples"
(module macro_testing [] :

(defrec @pub MyRec :
    (field s1 s32)
    (field s2 u32))


(fun TestRightArrowMacro [(param pointer (ptr MyRec))] u32 :
    (return (-> pointer s2)))


(fun TestWhileMacro [(param end u32)] u32 :
    (let! sum u32 0)
    (while (< sum end) :
        (+= sum 1))
    (return sum))





(fun TestForMacro! [(param end u32)] u32 :
    (let! sum u32 0)
    (for i 0 end 1 :
        (+= sum i))
    (return sum))


(macro nested0# STMT_LIST [] [] :)


(macro nested1# STMT_LIST [] [] :
    (nested0#))


(macro nested2# STMT_LIST [] [] :
    (nested1#))


(macro nested3# STMT_LIST [] [] :
    (nested2#))


(macro nested4# STMT_LIST [] [] :
    (nested3#))


(fun TestRecursiveMacro [] u32 :
    (nested3#)
    (return 0))


(macro product# STMT_LIST [(mparam $result ID) (mparam $factors STMT_LIST)] [] :
    ($for $x $factors :
        (= $result (* $result $x))))


(fun TestProductMacro [] u32 :
    (let! result u32 1)
    (product# result [
            111
            (* 2 111)
            333
            444
            555
            666])
    (return result))


(fun TestForMacroStringify [] (slice u8) :
    (return (stringify TestForMacroStringify)))


(fun TestSwap [(param vec (slice! u8))] void :
    (swap (at vec 1) (at vec 2)))


)
