@doc "hash_test"
(module [] :
(import fmt)

(import test)


(fun hash_32 [(param xx (ptr u32))] u32 :
    (let x u32 (^ xx))
    (return (xor (<< x 16_u32) (* x 123456789))))


(fun eq_32 [(param a (ptr u32)) (param b (ptr u32))] bool :
    (return (== (^ a) (^ b))))

(import hashtab hashtab32_gen [
        u32
        u32
        hash_32
        eq_32])


(global SIZE u32 32)


(global! meta auto (array_val SIZE u8 [0]))


(global! keys auto (array_val SIZE u32 [0]))


(global! vals auto (array_val SIZE u32 [0]))


(global! ht auto (rec_val hashtab::HashTab32 [
        (front! meta)
        (front! keys)
        (front! vals)
        SIZE
        0]))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (@ref let! key u32 6)
    (@ref let! val u32 6)
    (for i 0 (/ SIZE 2) 1 :
        (= key i)
        (= val (! i))
        (let p auto (hashtab::InsertOrUpdate [(&! ht) (& key) (& val)]))
        (fmt::print# "Insert key: " key " val: " val " ->  " p "\n"))
    (do (hashtab::DebugDump [(& ht)]))
    (for i 0 (/ SIZE 2) 1 :
        (= key i)
        (let v_expected auto (! i))
        (trylet pval (ptr! u32) (hashtab::Lookup [(&! ht) (& key)]) err :)
        (test::AssertEq# (^ pval) v_expected))
    @doc """if we delete one element and re-insert, it should
    end up in the same spit
    """
    (= key 6)
    (trylet lookup1 (ptr! u32) (hashtab::Lookup [(&! ht) (& key)]) err :)
    (test::AssertTrue# (hashtab::DeleteIfPresent [(&! ht) (& key)]))
    (test::AssertTrue# (hashtab::InsertOrUpdate [(&! ht) (& key) (& val)]))
    (trylet lookup2 (ptr! u32) (hashtab::Lookup [(&! ht) (& key)]) err :)
    (test::AssertEq# lookup1 lookup2)
    (= key 6)
    (= val 66)
    (test::AssertFalse# (hashtab::InsertOrUpdate [(&! ht) (& key) (& val)]))
    (trylet pval (ptr! u32) (hashtab::Lookup [(&! ht) (& key)]) err :)
    (test::AssertEq# (^ pval) val)
    (test::Success#)
    (return 0))
)
