@doc """hashtab32

32 refers to width of the integer returned by the hash function.
This also limits the max table size to (2^32 - 1).

$ktype:
$vtype:
$khash:
$keq:
"""
(module hashtab32 [
  @doc "the key type"
  (modparam $ktype TYPE)
  @doc "the value type"
  (modparam $vtype TYPE)
  @doc "the hash function: ptr($ktype) -> u32
  (modparam $khash CONST_EXPR)
  @doc "the key equality checker: ptr($ktype) X ptr($ktype) -> bool
  (modparam $keq CONST_EXPR)] :

(global FreeEntry u8 0x00)
(global DeletedEntry u8 0x01)
(global UsedEntryMark u8 0x80)

@doc """
The Hashtable contains pointers to 3 arrays of size `size`:
* meta: u8 entries with the following meaning:
  - FreeEntry (0):              entry is unused
  - DeletedEntry (1):           tombstone for deleted FreeEntry
  - Highbit (UsedEntryMark) set: entry is used and low 7 bit of
                                key hash matches
* keys: the keys
* vals: the value

"""
@pub (defrec HashTab32 :
  (field meta (ptr! u8))
	(field keys	(ptr! $ktype))
	(field vals	(ptr! $vtype))
  (field size u32)
  (field used u32)
)

(global NotFound u32 0xffffffff)

@pub (fun Lookup [
    (param ht (ptr HashTab32))
    (param key (ptr $ktype))] (union [void (ptr! $vtype)]) :
  (let h u32 (call $khash [key]))
  (let filter u8 (or (as h u8) UsedEntryMark))

  (let meta auto (-> ht meta))
  (let keys auto (-> ht keys))
  (let size auto (-> ht size))
  (let! i auto (% h size))

  (while true :
    (let m auto (^ (pinc meta i)))
    (if (== m FreeEntry) :
        (return void_val)
    :)
    (if (&& (== m filter) (call $keq [key (pinc keys i)])) :
        (return (pinc (pinc (-> ht vals) i) i))
    :)
    (+= i 1)
    (if (>= i size) : (-= i size) :)
  )
)

@pub (fun InsertOrUpdate [
    (param ht (ptr! HashTab32))
    (param key (ptr $ktype))
    (param val (ptr $vtype))] bool :
  (let h u32 (call $khash [key]))
  (let filter u8 (or (as h u8) UsedEntryMark))

  (let meta auto (-> ht meta))
  (let keys auto (-> ht keys))
  (let size auto (-> ht size))
  (let! i auto (% h size))
  (let! seen_deleted auto false)
  (let! first_deleted u32 0)

  (while true :
    (let m auto (^ (pinc meta i)))
    (if (== m FreeEntry) :
         (if (! seen_deleted) :
            (= first_deleted i)
         :)
         (= (^ (pinc (-> ht vals) first_deleted)) (^ val) )
         (+= (-> ht used) 1)
         (return true)
    :)
    (if (&& (== m filter) (call $keq [key (pinc keys i)])) :
        (= (^ (pinc (-> ht vals) i)) (^ val) )
        (return false)
    :)
    (if (&& (! seen_deleted) (== m DeletedEntry)) :
        (= seen_deleted true)
        (= first_deleted i)
    :)
    (+= i 1)
    (if (>= i size) : (-= i size) :)
  )
)

@pub (fun DeleteIfPresent [
    (param ht (ptr! HashTab32))
    (param key (ptr $ktype))] bool :
  (let h u32 (call $khash [key]))
  (let filter u8 (or (as h u8) UsedEntryMark))

  (let meta auto (-> ht meta))
  (let keys auto (-> ht keys))
  (let size auto (-> ht size))
  (let! i auto (% h size))

  (while true :
    (let m auto (^ (pinc meta i)))
    (if (== m FreeEntry) :
        (return false)
    :)
    (if (&& (== m filter) (call $keq [key (pinc keys i)])) :
        (= (^ (pinc meta i)) DeletedEntry)
        (-= (-> ht used) 1)
        (return true)
    :)
    (+= i 1)
    (if (>= i size) : (-= i size) :)
  )
)

)
