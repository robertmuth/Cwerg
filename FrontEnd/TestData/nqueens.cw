@doc "nqueens"
(module [] :
(import fmt)

(import test)


(global DIM auto 10_s32)


(type Board (array DIM (array DIM bool)))


(fun DumpBoard [(param board (ptr Board))] void :
    (for i 0 DIM 1 :
        (for j 0 DIM 1 :
            (fmt::print# (? (at (at (^ board) i) j) "Q" ".")))
        (fmt::print# "\n"))
    (fmt::print# "\n"))


(fun HasConflict [
        (param board (ptr Board))
        (param row s32)
        (param col s32)] bool :
    (for i 0 row 1 :
        (if (at (at (^ board) i) col) :
            (return true)
         :)
        (let j auto (- row i))
        (if (&& (> (+ (- col j) 1) 0) (at (at (^ board) i) (- col j))) :
            (return true)
         :)
        (if (&& (< (+ col j) DIM) (at (at (^ board) i) (+ col j))) :
            (return true)
         :))
    (return false))


(fun Solve [(param board (ptr! Board)) (param row s32)] uint :
    (if (>= row DIM) :
        @doc "(do (DumpBoard [board]))"
        (return 1)
     :)
    (let! n auto 0_uint)
    (for i 0 DIM 1 :
        (if (! (HasConflict [board row i])) :
            (= (at (at (^ board) row) i) true)
            (+= n (Solve [board (+ row 1)]))
            (=  (at (at (^ board) row) i) false)
         :))
    (return n))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc "initialized to false"
    (@ref let! board auto (vec_val DIM (array DIM bool)))
    (let n auto (Solve [(&! board) 0]))
    (fmt::print# n "\n")
    (test::AssertEq# n 724_uint)
    (test::Success#)
    (return 0))
)
