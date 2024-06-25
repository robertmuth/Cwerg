-- heapsort
module($type TYPE, $cmp_lt CONST_EXPR):

@pub fun sort(sdata slice!($type)) void:
    let data ^!$type = front!(sdata)
    let n = len(sdata)
    let! ir = n
    let! l = n >> 1 + 1
    let! rdata $type = undef
    while true:
        if l > 1:
            set l -= 1
            set rdata = pinc(data, l)^
        else:
            set rdata = pinc(data, ir)^
            set pinc(data, ir)^ = pinc(data, 1_uint)^
            set ir -= 1
            if ir == 1:
                set pinc(data, ir)^ = rdata
                return
        let! i = l
        let! j = l << 1
        while j <= ir:
            if j < ir && $cmp_lt(pinc(data, j), pinc(data, j + 1)):
                set j += 1
            if rdata < pinc(data, j)^:
                set pinc(data, i)^ = pinc(data, j)^
                set i = j
                set j += i
            else:
                set j = ir + 1
        set pinc(data, i)^ = rdata
    return
