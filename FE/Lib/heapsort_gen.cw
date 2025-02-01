; heapsort
module($type TYPE, $cmp_lt CONST_EXPR):

pub fun sort(sdata span!($type)) void:
    let data ^!$type = front!(sdata)
    let n = len(sdata)
    let! ir = n
    let! l = n >> 1 + 1
    let! rdata $type = undef
    while true:
        if l > 1:
            set l -= 1
            set rdata = ptr_inc(data, l)^
        else:
            set rdata = ptr_inc(data, ir)^
            set ptr_inc(data, ir)^ = ptr_inc(data, 1_uint)^
            set ir -= 1
            if ir == 1:
                set ptr_inc(data, ir)^ = rdata
                return
        let! i = l
        let! j = l << 1
        while j <= ir:
            if j < ir && $cmp_lt(ptr_inc(data, j), ptr_inc(data, j + 1)):
                set j += 1
            if rdata < ptr_inc(data, j)^:
                set ptr_inc(data, i)^ = ptr_inc(data, j)^
                set i = j
                set j += i
            else:
                set j = ir + 1
        set ptr_inc(data, i)^ = rdata
    return
