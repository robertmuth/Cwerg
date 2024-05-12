@doc "print command-line args"
(module main [] :
(import fmt)


(fun strlen [(param s (ptr u8))] uint :
    (let! i uint 0)
    @doc "pinc is adds an integer to a pointer it also has an options bound"
    (while (!= (^ (pinc s i)) 0) :
        (+= i 1))
    (return i))


@cdecl (fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (for i 0 (as argc u32) 1 :
        (let s (ptr u8) (^ (pinc argv i)))
        @doc """the print# macro does not supprt zero terminated strings
but it does support slices."""
        (let t auto (slice_val s (strlen [s])))
        (fmt::print# t "\n"))
    (return 0))
)

