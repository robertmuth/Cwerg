(module
  (import "wasi" "print_i32_ln" (func $wasi$print_i32_ln (param i32)))
  (memory 0)
  (func $size (export "size") (result i32) (memory.size))
  (func $grow (export "grow") (param i32) (result i32) (memory.grow (local.get 0)))


(func $assert_eq_i32 (param $line i32) (param $x i32) (param $y i32)
       (if (i32.ne (local.get 1) (local.get 2))
           (then
	       (call $wasi$print_i32_ln  (local.get 0))
	       (call $wasi$print_i32_ln  (local.get 1))
	       (call $wasi$print_i32_ln  (local.get 2))
	       (unreachable))
       )
)
 
(func $main (export "_start")
  (call $assert_eq_i32 (i32.const 1101) (call $grow (i32.const 0)) (i32.const 0))
  (call $assert_eq_i32 (i32.const 1201) (call $size ) (i32.const 0))
  (call $assert_eq_i32 (i32.const 1301) (call $grow (i32.const 1)) (i32.const 0))
  (call $assert_eq_i32 (i32.const 1401) (call $size ) (i32.const 1))
  (call $assert_eq_i32 (i32.const 1501) (call $grow (i32.const 1)) (i32.const 1))
  (call $assert_eq_i32 (i32.const 1601) (call $size ) (i32.const 2))
  (call $assert_eq_i32 (i32.const 1701) (call $grow (i32.const 2)) (i32.const 2))
  (call $assert_eq_i32 (i32.const 1801) (call $size ) (i32.const 4))
  (call $assert_eq_i32 (i32.const 1901) (call $grow (i32.const 6)) (i32.const 4))
  (call $assert_eq_i32 (i32.const 2001) (call $size ) (i32.const 10))
  (call $assert_eq_i32 (i32.const 2101) (call $grow (i32.const 0)) (i32.const 10))
  (call $wasi$print_i32_ln  (i32.const 666))
)

)
