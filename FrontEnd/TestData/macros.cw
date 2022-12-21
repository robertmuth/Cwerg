(module macro_testing [] [

(# "Macro Examples")

(defrec pub MyRec [
    (field s1 s32 undef)
    (field s2 u32 undef)
])


(fun TestRightArrowMacro [(param pointer (ptr MyRec))] u32 [
    (return (-> pointer s2))
])
  
(fun TestWhileMacro [(param end u32)] u32 [
    (let mut sum u32 0)
    (while (< sum end) [
        (+= sum 1)
    ])
    (return sum)
])


(fun TestAssertMacro [(param xxx u32)] u32 [
    (assert (< xxx 777))
    (return 0)
])

(fun TestForMacro [(param end u32)] u32 [
    (let mut sum u32 0)
    (for i u32 0 end 1 [
        (+= sum i)
    ])
    (return sum)
])

(macro nested0 [] [])
(macro nested1 [] [(nested0)])
(macro nested2 [] [(nested1)])
(macro nested3 [] [(nested2)])
(macro nested4 [] [(nested3)])

(fun TestRecursiveMacro [] u32 [
    (nested3)
    (return 0)
])

(macro product [(macro_param $result ID) (macro_param $factors STMT_LIST)] [
    (macro_for $x $factors [
        (= $result (* $result $x))
    ])
])

(fun TestProductMacro [] u32 [
    (let mut result u32 1)
    (product result [111 (* 2 111) 333 444 555 666])
    (return result)
])


(fun TestForMacroStringify [] (slice u8) [
    (return (stringify TestForMacroStringify))
])

(fun TestForMacroPrint [] void [
    (print [true false]) 
])

])